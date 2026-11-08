"""Chart indicators, each computed only from data up to and including its own bar (no look-ahead).

Conventions match common charting packages: EMA uses span n (alpha = 2/(n+1)); RSI and ATR use Wilder
smoothing (alpha = 1/n); MACD is EMA(12) - EMA(26) with a 9-period EMA signal line; Bollinger bands use
a population standard deviation. Every series is blank until it has its full lookback.
"""
from __future__ import annotations

import pandas as pd


def sma(series: pd.Series, n: int) -> pd.Series:
    return series.rolling(n, min_periods=n).mean()


def ema(series: pd.Series, n: int) -> pd.Series:
    return series.ewm(span=n, adjust=False, min_periods=n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    change = close.diff()
    gain = change.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    loss = (-change.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    out = 100 - 100 / (1 + gain / loss)
    return out.where(loss != 0, 100.0).where(gain.notna())


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    line = ema(close, fast) - ema(close, slow)
    sig = line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})


def atr(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 14) -> pd.Series:
    prior = close.shift(1)
    true_range = pd.concat([high - low, (high - prior).abs(), (low - prior).abs()], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def bollinger(close: pd.Series, n: int = 20, width: float = 2.0) -> pd.DataFrame:
    mid = sma(close, n)
    spread = close.rolling(n, min_periods=n).std(ddof=0) * width
    return pd.DataFrame({"mid": mid, "upper": mid + spread, "lower": mid - spread})


def relative_volume(volume: pd.Series, n: int = 20) -> pd.Series:
    """Today's volume over the average of the previous n days (today excluded from its own baseline)."""
    return volume / volume.shift(1).rolling(n, min_periods=n).mean()


def crossed_above(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a > b) & (a.shift(1) <= b.shift(1))
