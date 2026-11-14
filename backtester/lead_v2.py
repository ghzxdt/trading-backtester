"""Lead verdict v2 for the trade simulator, registered 2026-11-13 before it was run on real prices.

Why v1 (simulate.verdict, registered 2026-11-08) was replaced. A review on 2026-11-13 found that v1's
random-entry percentile compares the rule with entries on ordinary days, although these rules trade in
sell-offs, when returns swing about a third more than usual, so it overstated how sure the result was; that
its benchmark matched time in the market but carried about a third of the rule's risk; and that nothing
corrected for testing 24 strategy-and-entry combinations. v1 stays in the code and is still reported, unchanged.

What v2 asks, for each strategy and entry price (the three close-entry pricings are one test):

1. Excess. Each trade's gross return minus the average gross return of every possible trade of the same length
   and entry type in the period. This baseline is exact; nothing is drawn at random.
2. Is the average excess above zero, judged by the rule's own trades? Whole calendar quarters of trades are
   resampled with replacement RESAMPLES times, so trades from one sell-off stay together and the spread is the
   rule's own, not that of ordinary days. p = share of resamples whose average excess is zero or less.
3. Development (2010 on): p below DEV_P and, after Benjamini-Hochberg across the 24 development tests of a
   registered run, q below DEV_Q, with a positive average excess.
4. 1993-2009: positive average excess with p below HOLDOUT_P, looked at once and stored in the holdout ledger.
   This period is reused, not independent: the three signals were chosen on 2026-11-08 partly because they
   passed it in the indicator studies. It can remove a Lead; it cannot confirm one.
5. Benchmark (chosen by the user, 2026-11-13): buy-and-hold of the same instrument at a constant fraction equal
   to time in the market x (volatility of the rule's daily returns while in a trade / volatility of the
   instrument on all days). Beating it means the rule earned more per unit of risk while in a trade than the
   instrument usually does. Required in both periods.
6. At least MIN_TRADES trades from at least MIN_QUARTERS different quarters in a period, or it is not judged.

Labels are v1's, so the research app reads them unchanged: Lead, Timing edge only (passes 3 and 4, not 5),
Failed holdout, No edge, Too few trades, Development only (no holdout).

Limits to keep in view. The design was written after seeing development-period diagnostics for these twelve
strategies (not 1993-2009 results for the new statistic), and the signals themselves were selected on both
periods. A v2 Lead is therefore still provisional; only trades after 2026-11-08 are untouched evidence. With
few quarters the resampling is rougher than its p-value suggests.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import simulate

VERSION = "v2"
RESAMPLES = 10000
DEV_P, DEV_Q, HOLDOUT_P = 0.05, 0.10, 0.10
MIN_TRADES, MIN_QUARTERS = 20, 8
PARAMS = {"version": VERSION, "registered": "2026-11-13", "resamples": RESAMPLES, "cluster": "calendar quarter of the signal day",
          "dev_p": DEV_P, "dev_q": DEV_Q, "holdout_p": HOLDOUT_P, "min_trades": MIN_TRADES, "min_quarters": MIN_QUARTERS,
          "family": "strategies x entry prices (close, next open) of a registered run",
          "benchmark": "buy-and-hold at exposure x (in-trade volatility / all-days volatility)"}
DEFINITION = (
    "v2, registered 2026-11-13. Lead: the average trade beats the average of every possible trade of the same length "
    f"in the period, judged by resampling the rule's own trades by calendar quarter (development p < {DEV_P} and "
    f"q < {DEV_Q} across the run's strategy-and-entry tests; 1993-2009 p < {HOLDOUT_P}), and CAGR is above "
    "buy-and-hold scaled to the same time in the market and the same volatility while in a trade, in both periods. "
    "The 1993-2009 period also helped choose these signals, so it is not independent confirmation; a Lead is "
    "provisional until trades after 2026-11-08 support it.")


def baseline(frame: pd.DataFrame, mask: pd.Series, lengths: np.ndarray, mode: str) -> np.ndarray:
    """For each holding length: the mean gross return of every possible trade of that length inside the period."""
    close, open_ = frame["close"].to_numpy(), frame["open"].to_numpy()
    inside = np.flatnonzero(mask.to_numpy(bool))
    means = {}
    for length in np.unique(lengths):
        starts = inside[inside + length <= inside.max()]
        if len(starts) == 0:
            means[length] = np.nan
            continue
        entry = open_[starts + 1] if mode == "etf_next_open" else close[starts]
        means[length] = float((close[starts + length] / entry - 1).mean())
    return np.array([means[length] for length in lengths], dtype=float)


def excess_test(priced: pd.DataFrame, base: np.ndarray, rng: np.random.Generator, resamples: int = RESAMPLES) -> dict:
    """Average excess over the baseline, and how often it is zero or less when quarters of trades are resampled."""
    gross = priced["gross"].to_numpy(float)
    excess = gross - base
    quarters = pd.PeriodIndex(pd.DatetimeIndex(priced["signal_day"]), freq="Q")
    _, which = np.unique(quarters.asi8, return_inverse=True)
    count = int(which.max()) + 1
    sums, sizes = np.bincount(which, weights=excess, minlength=count), np.bincount(which, minlength=count)
    draw = rng.integers(0, count, size=(resamples, count))
    means = sums[draw].sum(axis=1) / sizes[draw].sum(axis=1)
    best = np.sort(gross)[::-1][:5]
    return {"mean_excess": float(excess.mean()), "baseline": float(base.mean()),
            "p": float((np.sum(means <= 0) + 1) / (resamples + 1)), "quarters": count,
            "top5_share": float(best.sum() / gross.sum()) if gross.sum() > 0 else None}


def risk_fraction(frame: pd.DataFrame, trades, returns: pd.Series, exposure: float, mask: pd.Series) -> float | None:
    """Exposure x (volatility of the rule's daily returns while in a trade / the instrument's on all days)."""
    held = np.zeros(len(frame), bool)
    for p, e in trades:
        held[p + 1:e + 1] = True
    inside = mask.to_numpy(bool)
    in_trade = returns.to_numpy()[held[inside]]
    every_day = frame["close"].pct_change().to_numpy()[inside]
    every_day = every_day[np.isfinite(every_day)]
    if len(in_trade) < 2 or len(every_day) < 2 or every_day.std() == 0:
        return None
    return float(exposure * in_trade.std() / every_day.std())


def per_volatility(returns: pd.Series) -> float | None:
    """Annualised mean over annualised volatility of daily returns (cash earns 0)."""
    spread = returns.std()
    return None if not spread or not np.isfinite(spread) else float(returns.mean() / spread * np.sqrt(simulate.TRADING_DAYS))


def evaluate(frame: pd.DataFrame, trades, priced: pd.DataFrame, mask: pd.Series, mode: str, cfg: dict,
             rng: np.random.Generator, resamples: int = RESAMPLES) -> dict:
    """The v2 fields for one strategy, pricing and period, to sit beside simulate.evaluate's."""
    if priced.empty:
        return {"v2": None, "risk_matched": None, "risk_fraction": None, "per_volatility": None, "index_per_volatility": None}
    returns, exposure = simulate.daily_returns(frame, trades, mode, cfg, mask)
    fraction = risk_fraction(frame, trades, returns, exposure, mask)
    index = frame["close"].pct_change().fillna(0.0)[mask.to_numpy(bool)]
    matched = None if fraction is None else simulate.summary(simulate.matched_buy_and_hold(frame, mask, fraction, mode, cfg))
    return {"v2": excess_test(priced, baseline(frame, mask, priced["sessions"].to_numpy(int), mode), rng, resamples),
            "risk_matched": matched, "risk_fraction": fraction,
            "per_volatility": per_volatility(returns), "index_per_volatility": per_volatility(index)}


def judged(result: dict | None) -> bool:
    return bool(result and result.get("v2") and result["trades"] >= MIN_TRADES and result["v2"]["quarters"] >= MIN_QUARTERS)


def verdict(dev: dict, holdout: dict | None, q: float | None) -> str:
    def beats(r):
        s, m = r["strategy"]["cagr"], (r.get("risk_matched") or {}).get("cagr")
        return s is not None and m is not None and s > m
    if not judged(dev):
        return "Too few trades"
    test = dev["v2"]
    if not (test["mean_excess"] > 0 and test["p"] < DEV_P and q is not None and q < DEV_Q):
        return "No edge"
    if not judged(holdout):
        return "Development only (no holdout)"
    if not (holdout["v2"]["mean_excess"] > 0 and holdout["v2"]["p"] < HOLDOUT_P):
        return "Failed holdout"
    return "Lead" if beats(dev) and beats(holdout) else "Timing edge only"
