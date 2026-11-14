"""Registered trade rules for the simulator, fixed before any simulation was run (2026-11-08).

Signals are the three oversold studies that were candidates in the 2026-11-08 indicator run. Exits are two
common, simple rules; nothing is tuned. A changed rule gets a new version, never an edit.

Execution models (the same trades, priced different ways):
- etf_close:      buy the ETF at the signal day's close (a market-on-close order), sell at the exit close.
- etf_next_open:  buy the ETF at the next morning's open, sell at the exit close.
- perp_maker / perp_taker: the Kalshi perp entered just after the close (~4:05 PM ET, priced at the ETF close
  as a proxy), exited just before a later 4 PM close, paying Kalshi's maker or taker fee on both sides and
  the daily 4 PM funding for every 4 PM it is held through.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from . import indicators as ind
from .catalog import STUDIES

SIGNALS = ("rsi2_below_10", "rsi14_below_30", "bollinger_lower_close")
SYMBOLS = ("SPY", "QQQ")
MODES = ("etf_close", "etf_next_open", "perp_maker", "perp_taker")
DRAWS, SEED = 2000, 11  # the registered run; other settings get no holdout look


@dataclass(frozen=True)
class Exit:
    name: str
    version: str
    description: str
    # (frame, signal position) -> exit position (a session index, exited at that day's close)
    rule: Callable[[pd.DataFrame, np.ndarray], np.ndarray]


def _hold(n: int):
    return lambda frame, pos: pos + n


def _close_above_sma5(frame: pd.DataFrame, pos: np.ndarray) -> np.ndarray:
    above = (frame["close"] > ind.sma(frame["close"], 5)).to_numpy()
    out = []
    for p in pos:
        window = above[p + 1:p + 11]
        hits = np.flatnonzero(window)
        out.append(p + 1 + hits[0] if len(hits) else p + 10)
    return np.asarray(out, dtype=int)


EXITS = [
    Exit("hold_5", "v1", "Exit at the close five sessions after the signal", _hold(5)),
    Exit("close_above_sma5", "v1", "Exit at the first close above the 5-day SMA, at most ten sessions after the signal",
         _close_above_sma5),
]


def signal_rule(name: str):
    for study in STUDIES:
        if study.name == name:
            return study
    raise KeyError(name)
