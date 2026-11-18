"""Lead verdict v3 for the trade simulator, registered 2026-11-18 before it was run on real prices.

v3 asks exactly v2's questions (lead_v2.py: excess over every same-length trade judged by resampling calendar
quarters, q across the run's 24 strategy-and-entry tests, 1993-2009 p < 0.10, CAGR above the risk-matched
benchmark, at least 20 trades from 8 quarters) with two changes, both from the 2026-11-17 audit
(docs/reviews/BACKTESTER_AUDIT_2026-11-17.md, part 1 section 1.6):

1. A fixed development window. v2's window had no end, so every weekly run folded the newest trades into
   "development" and could move a verdict across a threshold without anyone noticing, while the research app acted
   on it. v3's development window ends on DEV_END, 2026-11-13: the day v2 was registered and the last day its
   design could have seen. Development results no longer change when data is added.
2. A forward record. A trade whose signal day is after DEV_END is untouched evidence. Its excess is its gross return
   minus the development-window mean of every trade of the same length and entry. After n forward trades with mean
   excess f, against the development trades' mean excess m and standard deviation s:
     "none yet" (n = 0); "too few" (n < MIN_FORWARD);
     "consistent" while f >= m - BAND_SE * s / sqrt(n);
     "below band" when f < m - BAND_SE * s / sqrt(n);
     "failed" when, in addition, f + 1.645 * s / sqrt(n) < 0 (a forward 90% interval wholly below zero).
   A development Lead whose forward status is "below band" or "failed" is labelled DEMOTED instead of "Lead". The
   research app acts only on "Lead", so it stops treating that rule as a setup until a person has reviewed it.

The band is wide on purpose. At the historical rates, confirming these edges statistically would take years
(QQQ Bollinger about 19 years); the band's job is to catch a large break early, not to prove the edge.
v1 (simulate.verdict) and v2 (lead_v2.verdict, on v2's open window) are still computed and reported beside v3.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import lead_v2, simulate

VERSION = "v3"
DEV_END = "2026-11-13"
MIN_FORWARD = 5
BAND_SE = 2.0
DEMOTED = "Forward below band"
PARAMS = {"version": VERSION, "registered": "2026-11-18", "tests": "lead_v2, unchanged", "lead_v2": lead_v2.PARAMS,
          "development_end": DEV_END, "forward": "signal day after development_end",
          "forward_baseline": "development-window mean gross of every trade of the same length and entry",
          "min_forward": MIN_FORWARD, "band": f"m - {BAND_SE} * s / sqrt(n)", "failed": "f + 1.645 * s / sqrt(n) < 0",
          "demoted_label": DEMOTED}
DEFINITION = (
    "v3, registered 2026-11-18: v2's tests and thresholds on a development window fixed at 2010-01-01 to "
    f"{DEV_END}, so a verdict no longer moves as data is added. Lead: the average trade beats the average of every "
    "possible trade of the same length (development p < 0.05 by resampling the rule's trades by calendar quarter, "
    "q < 0.10 across the run's strategy-and-entry tests; 1993-2009 p < 0.10), and CAGR is above buy-and-hold scaled to "
    "the same time in the market and volatility in a trade, in both periods. Trades signalled after "
    f"{DEV_END} are kept apart as the forward record; from {MIN_FORWARD} forward trades, a Lead whose forward mean "
    f"excess falls below its development mean minus {BAND_SE:g} standard errors is labelled '{DEMOTED}'. "
    "1993-2009 also helped choose these signals, so it can remove a Lead but not confirm one.")


def development_mask(index: pd.DatetimeIndex, cfg: dict) -> pd.Series:
    """v3's development window: the configured start to DEV_END."""
    spec = cfg["development"]
    start = pd.Timestamp(spec["start"]) if spec.get("start") else index.min()
    return pd.Series((index >= start) & (index <= pd.Timestamp(DEV_END)), index=index)


def forward_mask(index: pd.DatetimeIndex) -> pd.Series:
    return pd.Series(index > pd.Timestamp(DEV_END), index=index)


def forward_status(n: int, f: float | None, m: float | None, s: float | None) -> tuple[str, float | None]:
    """(status, lower edge of the band) for n forward trades with mean excess f, given development m and s."""
    if n == 0:
        return "none yet", None
    if m is None or s is None or not np.isfinite(s) or s <= 0:
        return "no development band", None
    band = m - BAND_SE * s / np.sqrt(n)
    if n < MIN_FORWARD:
        return "too few", float(band)
    if f + 1.645 * s / np.sqrt(n) < 0:
        return "failed", float(band)
    if f < band:
        return "below band", float(band)
    return "consistent", float(band)


def development_excess(frame: pd.DataFrame, dev_mask: pd.Series, priced: pd.DataFrame, mode: str) -> np.ndarray:
    if priced.empty:
        return np.array([])
    return priced["gross"].to_numpy(float) - lead_v2.baseline(frame, dev_mask, priced["sessions"].to_numpy(int), mode)


def forward_record(frame: pd.DataFrame, signal: pd.Series, exit_rule, mode: str, cfg: dict, dev_mask: pd.Series,
                   dev_excess: np.ndarray) -> tuple[dict, pd.DataFrame]:
    """The forward block for one strategy and pricing, and its priced trades."""
    trades = simulate.find_trades(frame, signal, exit_rule, forward_mask(frame.index))
    priced = simulate.price_trades(frame, trades, mode, cfg)
    m = float(np.mean(dev_excess)) if len(dev_excess) else None
    s = float(np.std(dev_excess, ddof=1)) if len(dev_excess) > 1 else None
    f = None
    if len(priced):
        base = lead_v2.baseline(frame, dev_mask, priced["sessions"].to_numpy(int), mode)
        f = float((priced["gross"].to_numpy(float) - base).mean())
    status, band = forward_status(len(priced), f, m, s)
    return ({"since": DEV_END, "trades": len(priced), "mean_excess": f, "mean_net": float(priced["net"].mean()) if len(priced) else None,
             "band_lower": band, "status": status, "development_mean_excess": m, "development_sd": s,
             "last_signal": f"{priced['signal_day'].iloc[-1]:%Y-%m-%d}" if len(priced) else None}, priced)


def verdict(dev: dict, holdout: dict | None, q: float | None, forward: dict | None) -> str:
    label = lead_v2.verdict(dev, holdout, q)
    if label == "Lead" and (forward or {}).get("status") in ("below band", "failed"):
        return DEMOTED
    return label
