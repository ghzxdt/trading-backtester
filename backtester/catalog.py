"""Registered indicator studies. Each is fixed before it is run; a changed rule gets a new version.

All are long-side hypotheses ("after this, the index tends to do better than usual"). Every signal is
known at that day's close. Add new studies at the end with version v1; never edit a recorded one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from . import indicators as ind


# The registered run: these symbols and horizons form the family the multiple-testing correction covers, with
# this seed and number of draws. A run with anything else is partial: it gets no verdicts and no holdout look.
SYMBOLS = ("SPY", "QQQ", "IWM")
HORIZONS = (1, 5, 10)
DRAWS, SEED = 2000, 7


@dataclass(frozen=True)
class Study:
    name: str
    version: str
    description: str
    rule: Callable[[pd.DataFrame], pd.Series]
    needs_volume: bool = False


def _ema_touch(n: int):
    def rule(d: pd.DataFrame) -> pd.Series:
        e = ind.ema(d["close"], n)
        return (d["low"] <= e) & (d["close"] >= e) & (d["close"] > ind.sma(d["close"], 200))
    return rule


def _macd_cross(below_zero: bool):
    def rule(d: pd.DataFrame) -> pd.Series:
        m = ind.macd(d["close"])
        cross = ind.crossed_above(m["macd"], m["signal"])
        return cross & (m["macd"] < 0) if below_zero else cross
    return rule


STUDIES = [
    Study("rsi2_below_10", "v1", "RSI(2) closes below 10 (short-term oversold)",
          lambda d: ind.rsi(d["close"], 2) < 10),
    Study("rsi14_below_30", "v1", "RSI(14) closes below 30 (classic oversold)",
          lambda d: ind.rsi(d["close"], 14) < 30),
    Study("ema21_touch_uptrend", "v1", "Low touches the 21-day EMA and the close holds above it, in an uptrend (close above the 200-day SMA)",
          _ema_touch(21)),
    Study("ema50_touch_uptrend", "v1", "Low touches the 50-day EMA and the close holds above it, in an uptrend (close above the 200-day SMA)",
          _ema_touch(50)),
    Study("macd_cross_up", "v1", "MACD(12,26) crosses above its 9-day signal line", _macd_cross(False)),
    Study("macd_cross_up_below_zero", "v1", "MACD crosses above its signal line while still below zero", _macd_cross(True)),
    Study("bollinger_lower_close", "v1", "Close below the lower Bollinger band (20 days, 2 standard deviations)",
          lambda d: d["close"] < ind.bollinger(d["close"])["lower"]),
    Study("new_20d_high", "v1", "Close above the highest close of the previous 20 days (breakout)",
          lambda d: d["close"] > d["close"].shift(1).rolling(20, min_periods=20).max()),
    Study("volume_spike_down_day", "v1", "Down day on at least 2x the previous 20-day average volume (capitulation)",
          lambda d: (ind.relative_volume(d["volume"]) >= 2) & (d["close"] < d["close"].shift(1)), needs_volume=True),
    Study("above_sma200", "v1", "Close above the 200-day SMA (a trend-filter state, not an entry)",
          lambda d: d["close"] > ind.sma(d["close"], 200)),
]
