"""Registered filter tests: does a registered strategy do better or worse when a condition holds?

Registered 2026-11-18, before any of them was run on real prices. Sources: the research app's idea ledger (idea 7: a
large gap up at the next open uses up the bounce; idea 8: the oversold rules depend on trend and volatility) and the
2026-11-17 audit (docs/reviews/BACKTESTER_AUDIT_2026-11-17.md: the VIX term structure, a scheduled release inside the
trade, and a volatility-matched baseline).

What is compared. The trades of four registered strategy-entries (STRATEGIES: the two QQQ next-open Leads, the same
Bollinger rule on SPY, and QQQ RSI(2) at the close), in v3's development window (2010-01-01 to 2026-11-13). Each trade's
excess is its gross return minus the mean of every trade of the same length and entry in the window (Lead v2/v3's
baseline). A split divides the trades by a condition known before the entry. The statistic is the difference in mean
excess, condition group minus the rest, with a 90% interval and a two-sided p from resampling calendar quarters of
trades RESAMPLES times (trades from one sell-off stay together). q corrects for every test in this family.
1993-2009 is evaluated once per test version through the holdout ledger, where the condition can be measured there
(gap, trend and VIX level; not VIX3M, which starts in 2009, nor the release calendar, which starts in 2010).

Labels (none changes a trade verdict):
- Supported difference: development p < 0.05 and q < 0.10, and 1993-2009 has the same sign with p < 0.10.
- Development only (...): passes in development; 1993-2009 has no data for it, or too few trades.
- Not confirmed in 1993-2009: passes in development; 1993-2009 has the other sign or p >= 0.10.
- No meaningful difference: fails in development, and the 90% interval excludes any difference as large as the
  strategy's own mean excess, either way.
- Insufficient evidence: fails in development, and the interval is too wide to say.
- Too few trades: fewer than MIN_GROUP trades on either side.

The volatility-matched baseline test asks whether a strategy's trades beat trades of the same length and entry that
started on days in the same VIX bucket (the research app's buckets, declared 2026-11-08), one-sided like Lead v2.
It separates timing from the higher returns volatile markets may pay anyway. Labels: Edge beyond volatility;
Development only (...); Not confirmed in 1993-2009; Not shown beyond volatility; Too few trades.

Splits divide few trades, so most results will be "Insufficient evidence": with about 100 trades a difference has to
be well over 1 percentage point per trade to show. That is a finding too: the condition has not earned a place in the
decision.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from . import lead_v2, simulate, strategies

VERSION = "v1"
RESAMPLES, SEED = 10000, 13  # the registered run; other settings are partial (no labels, no 1993-2009 look)
DEV_P, DEV_Q, HOLDOUT_P = 0.05, 0.10, 0.10
MIN_GROUP = 8
COVERAGE = 0.9  # share of a period's trades the condition must be measurable for
STRATEGIES = (("QQQ", "bollinger_lower_close", "close_above_sma5", "etf_next_open"),
              ("SPY", "bollinger_lower_close", "close_above_sma5", "etf_next_open"),
              ("QQQ", "rsi14_below_30", "close_above_sma5", "etf_next_open"),
              ("QQQ", "rsi2_below_10", "close_above_sma5", "etf_close"))
VIX_BUCKETS = ((0.0, 15.0, "VIX below 15"), (15.0, 20.0, "VIX 15-20"), (20.0, 30.0, "VIX 20-30"),
               (30.0, np.inf, "VIX 30 and up"))  # the research app's buckets (thesis/regime.py, 2026-11-08)
GAP_BUCKETS = ((-np.inf, -0.005, "gap down more than 0.5%"), (-0.005, 0.005, "within 0.5%"),
               (0.005, 0.015, "gap up 0.5% to 1.5%"), (0.015, np.inf, "gap up 1.5% or more"))


def _gap(frame: pd.DataFrame, ctx: dict) -> pd.Series:
    """The next session's open against the signal close. Known at that open; a premarket quote approximates it."""
    return frame["open"].shift(-1) / frame["close"] - 1


def _spy_trend(frame: pd.DataFrame, ctx: dict) -> pd.Series:
    spy = ctx["spy_close"]
    return (spy / spy.rolling(200, min_periods=200).mean() - 1).reindex(frame.index)


def _vix(frame: pd.DataFrame, ctx: dict) -> pd.Series:
    return ctx["vix"].reindex(frame.index)


def _vix_curve(frame: pd.DataFrame, ctx: dict) -> pd.Series:
    return (ctx["vix"] / ctx["vix3m"].reindex(ctx["vix"].index)).reindex(frame.index)


def _release_ahead(frame: pd.DataFrame, ctx: dict, sessions: int = 5) -> pd.Series:
    """How many scheduled CPI, jobs or Fed dates fall in the `sessions` sessions after each day (dates are known ahead).
    Blank where the calendar does not cover the whole window."""
    events = ctx["events"]
    days = pd.DatetimeIndex(pd.to_datetime(events.loc[events["scheduled"].astype(bool), "date"])) if len(events) else []
    out = np.full(len(frame), np.nan)
    if len(days) == 0:
        return pd.Series(out, index=frame.index)
    flags = np.asarray(frame.index.isin(days), float)
    running = np.concatenate([[0.0], np.cumsum(flags)])
    ahead = running[np.minimum(np.arange(len(frame)) + sessions + 1, len(frame))] - running[np.arange(len(frame)) + 1]
    complete = np.arange(len(frame)) + sessions < len(frame)
    covered = (frame.index >= days.min()) & (frame.index <= days.max())
    out[complete & covered] = ahead[complete & covered]
    return pd.Series(out, index=frame.index)


@dataclass(frozen=True)
class Split:
    name: str
    version: str
    description: str
    value: Callable[[pd.DataFrame, dict], pd.Series]
    in_group: Callable[[np.ndarray], np.ndarray]
    group_label: str
    rest_label: str
    buckets: tuple = ()
    entries: tuple = ("etf_next_open", "etf_close")
    before_2010: bool = True

    def declared(self) -> dict:
        return {"name": self.name, "version": self.version, "description": self.description,
                "group": self.group_label, "rest": self.rest_label, "entries": list(self.entries),
                "before_2010": self.before_2010, "buckets": [label for _, _, label in self.buckets]}


SPLITS = [
    Split("gap_at_next_open", "v1", "The next open's gap from the signal close (idea 7)", _gap,
          lambda v: v >= 0.005, "gap up 0.5% or more", "smaller gap, or a gap down", GAP_BUCKETS,
          entries=("etf_next_open",)),
    Split("spy_200d_trend", "v1", "SPY's close against its 200-day average at the signal close (idea 8)", _spy_trend,
          lambda v: v < 0, "SPY below its 200-day average", "SPY above it"),
    Split("vix_level", "v1", "The VIX close on the signal day (idea 8)", _vix,
          lambda v: v >= 20, "VIX 20 or higher", "VIX below 20", VIX_BUCKETS),
    Split("vix_term_structure", "v1", "VIX above VIX3M on the signal day: an inverted curve, a stress reading", _vix_curve,
          lambda v: v > 1, "VIX above VIX3M", "VIX at or below VIX3M", before_2010=False),
    Split("release_within_5_sessions", "v1", "A scheduled CPI, jobs or Fed release in the five sessions after the signal",
          _release_ahead, lambda v: v > 0, "a release within 5 sessions", "no release", before_2010=False),
]
VOL_TEST = {"name": "volatility_matched_baseline", "version": "v1",
            "description": "Excess over every same-length trade that started on a day in the same VIX bucket",
            "buckets": [label for _, _, label in VIX_BUCKETS]}
PARAMS = {"version": VERSION, "registered": "2026-11-18", "resamples": RESAMPLES, "dev_p": DEV_P, "dev_q": DEV_Q,
          "holdout_p": HOLDOUT_P, "min_group": MIN_GROUP, "coverage": COVERAGE,
          "strategies": [list(s) for s in STRATEGIES], "splits": [s.declared() for s in SPLITS], "volatility_test": VOL_TEST,
          "window": "lead_v3 development window", "statistic": "difference in mean excess, quarter-cluster resampling",
          "family": "every split and volatility test of a registered run"}


def strategy_key(strategy) -> str:
    symbol, signal, exit_name, mode = strategy
    return f"{symbol}:{signal}+{exit_name}|{mode}"


def strategy_trades(frame: pd.DataFrame, strategy, mask: pd.Series, cfg: dict) -> pd.DataFrame:
    """The strategy's trades in `mask`, with each trade's signal position and its excess over same-length trades."""
    _, signal_name, exit_name, mode = strategy
    signal = strategies.signal_rule(signal_name).rule(frame).fillna(False).astype(bool)
    exit_rule = {e.name: e for e in strategies.EXITS}[exit_name].rule
    trades = simulate.find_trades(frame, signal, exit_rule, mask)
    priced = simulate.price_trades(frame, trades, mode, cfg)
    if priced.empty:
        return priced.assign(position=pd.Series(dtype=int), excess=pd.Series(dtype=float))
    base = lead_v2.baseline(frame, mask, priced["sessions"].to_numpy(int), mode)
    return priced.assign(position=[p for p, _ in trades], excess=priced["gross"].to_numpy(float) - base)


def _quarters(days) -> np.ndarray:
    _, which = np.unique(pd.PeriodIndex(pd.DatetimeIndex(days), freq="Q").asi8, return_inverse=True)
    return which


def contrast(priced: pd.DataFrame | None, values: pd.Series, split: Split, rng: np.random.Generator,
             resamples: int = RESAMPLES) -> dict:
    if priced is None or priced.empty:
        return {"status": "too few", "trades": 0}
    v = values.to_numpy(float)[priced["position"].to_numpy(int)]
    x = priced["excess"].to_numpy(float)
    defined = np.isfinite(v)
    group = np.zeros(len(v), bool)
    group[defined] = split.in_group(v[defined])
    rest = defined & ~group
    mean = lambda sel: float(x[sel].mean()) if sel.any() else None  # noqa: E731
    out = {"trades": int(len(v)), "measured": int(defined.sum()), "group": int(group.sum()), "rest": int(rest.sum()),
           "group_mean": mean(group), "rest_mean": mean(rest), "strategy_mean": mean(defined),
           "buckets": [{"label": label, "trades": int((defined & (v >= lo) & (v < hi)).sum()),
                        "mean_excess": mean(defined & (v >= lo) & (v < hi))} for lo, hi, label in split.buckets]}
    if defined.sum() < COVERAGE * len(v):
        return {**out, "status": "no data"}
    if group.sum() < MIN_GROUP or rest.sum() < MIN_GROUP:
        return {**out, "status": "too few"}
    which = _quarters(priced["signal_day"].to_numpy()[defined])
    xs, gs = x[defined], group[defined]
    count = int(which.max()) + 1
    sa = np.bincount(which, weights=np.where(gs, xs, 0.0), minlength=count)
    na = np.bincount(which, weights=gs.astype(float), minlength=count)
    sb = np.bincount(which, weights=np.where(gs, 0.0, xs), minlength=count)
    nb = np.bincount(which, weights=(~gs).astype(float), minlength=count)
    draw = rng.integers(0, count, size=(resamples, count))
    n_a, n_b = na[draw].sum(axis=1), nb[draw].sum(axis=1)
    ok = (n_a > 0) & (n_b > 0)
    diffs = sa[draw].sum(axis=1)[ok] / n_a[ok] - sb[draw].sum(axis=1)[ok] / n_b[ok]
    if len(diffs) < resamples // 2:  # the two sides share too few quarters to resample them together
        return {**out, "status": "too few", "quarters": count}
    tail = min(int((diffs <= 0).sum()), int((diffs >= 0).sum()))
    return {**out, "status": "ok", "quarters": count, "diff": out["group_mean"] - out["rest_mean"],
            "ci90": [float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))],
            "p": float(min(1.0, 2 * (tail + 1) / (len(diffs) + 1)))}


def vix_bucket_codes(vix: pd.Series) -> np.ndarray:
    v = vix.to_numpy(float)
    codes = np.full(len(v), -1)
    for k, (lo, hi, _) in enumerate(VIX_BUCKETS):
        codes[(v >= lo) & (v < hi)] = k
    return codes


def volatility_test(frame: pd.DataFrame, mask: pd.Series, priced: pd.DataFrame | None, mode: str, vix: pd.Series,
                    rng: np.random.Generator, resamples: int = RESAMPLES) -> dict:
    if priced is None or priced.empty:
        return {"status": "too few", "trades": 0}
    codes = vix_bucket_codes(vix.reindex(frame.index))
    close, open_ = frame["close"].to_numpy(float), frame["open"].to_numpy(float)
    inside = np.flatnonzero(mask.to_numpy(bool))
    cache, base = {}, []
    for p, length in zip(priced["position"].to_numpy(int), priced["sessions"].to_numpy(int)):
        bucket = codes[p]
        if bucket < 0:
            base.append(np.nan)
            continue
        if (length, bucket) not in cache:
            starts = inside[inside + length <= inside.max()]
            starts = starts[codes[starts] == bucket]
            entry = open_[starts + 1] if mode == "etf_next_open" else close[starts]
            cache[(length, bucket)] = float((close[starts + length] / entry - 1).mean()) if len(starts) else np.nan
        base.append(cache[(length, bucket)])
    x = priced["gross"].to_numpy(float) - np.asarray(base, float)
    ok = np.isfinite(x)
    out = {"trades": int(len(x)), "measured": int(ok.sum()), "v2_mean_excess": float(priced["excess"].mean()),
           "mean_excess": float(x[ok].mean()) if ok.any() else None}
    if ok.sum() < COVERAGE * len(x):
        return {**out, "status": "no data"}
    which = _quarters(priced["signal_day"].to_numpy()[ok])
    count = int(which.max()) + 1
    if ok.sum() < lead_v2.MIN_TRADES or count < lead_v2.MIN_QUARTERS:
        return {**out, "status": "too few", "quarters": count}
    sums = np.bincount(which, weights=x[ok], minlength=count)
    sizes = np.bincount(which, minlength=count)
    draw = rng.integers(0, count, size=(resamples, count))
    means = sums[draw].sum(axis=1) / sizes[draw].sum(axis=1)
    return {**out, "status": "ok", "quarters": count, "ci90": [float(np.percentile(means, 5)), float(np.percentile(means, 95))],
            "p": float((np.sum(means <= 0) + 1) / (resamples + 1))}


def contrast_label(dev: dict, hold: dict | None, q: float | None) -> str:
    if dev.get("status") != "ok":
        return "Too few trades" if dev.get("status") == "too few" else "No data"
    if dev["p"] < DEV_P and q is not None and q < DEV_Q:
        if hold is None:
            return "Development only (no 1993-2009 data)"
        if hold.get("status") != "ok":
            return "Development only (too few 1993-2009 trades)"
        same = np.sign(hold["diff"]) == np.sign(dev["diff"])
        return "Supported difference" if same and hold["p"] < HOLDOUT_P else "Not confirmed in 1993-2009"
    edge = abs(dev.get("strategy_mean") or 0.0)
    lo, hi = dev["ci90"]
    return "No meaningful difference" if edge > 0 and -edge < lo and hi < edge else "Insufficient evidence"


def volatility_label(dev: dict, hold: dict | None, q: float | None) -> str:
    if dev.get("status") != "ok":
        return "Too few trades" if dev.get("status") == "too few" else "No data"
    if dev["mean_excess"] > 0 and dev["p"] < DEV_P and q is not None and q < DEV_Q:
        if hold is None:
            return "Development only (no 1993-2009 data)"
        if hold.get("status") != "ok":
            return "Development only (too few 1993-2009 trades)"
        return "Edge beyond volatility" if hold["mean_excess"] > 0 and hold["p"] < HOLDOUT_P else "Not confirmed in 1993-2009"
    return "Not shown beyond volatility"


def reference_context(frame: pd.DataFrame) -> dict:
    """A made-up context for the rule lock: a VIX-like series from the reference prices' own volatility, a slower
    VIX3M, the prices as SPY, and a release every 21 sessions."""
    vix = (frame["close"].pct_change().rolling(21, min_periods=21).std() * np.sqrt(252) * 100).round(6)
    return {"vix": vix, "vix3m": vix.rolling(63, min_periods=21).mean().round(6), "spy_close": frame["close"],
            "events": pd.DataFrame({"date": frame.index[5::21], "event": "cpi", "scheduled": True})}


def fingerprint(split: Split, frame: pd.DataFrame, ctx: dict) -> str:
    """What a split does on the reference history (group membership and buckets), plus its declared settings."""
    v = split.value(frame, ctx).to_numpy(float)
    defined = np.isfinite(v)
    group = np.full(len(v), -1)
    group[defined] = split.in_group(v[defined]).astype(int)
    buckets = np.full(len(v), -1)
    for k, (lo, hi, _) in enumerate(split.buckets):
        buckets[defined & (v >= lo) & (v < hi)] = k
    digest = hashlib.sha256(json.dumps(split.declared(), sort_keys=True).encode())
    digest.update(np.ascontiguousarray(group).astype("<i8").tobytes() + np.ascontiguousarray(buckets).astype("<i8").tobytes())
    return digest.hexdigest()[:16]


def volatility_fingerprint(ctx: dict) -> str:
    digest = hashlib.sha256(json.dumps(VOL_TEST, sort_keys=True).encode())
    digest.update(np.ascontiguousarray(vix_bucket_codes(ctx["vix"])).astype("<i8").tobytes())
    return digest.hexdigest()[:16]
