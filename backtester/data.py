"""Read-only access to the trading-research app's saved market data.

The backtester never writes into the research app. It reads the app's download caches:
  data/raw/etfs_long.csv   SPY since 1993 and QQQ since 1999 (daily OHLCV, split/dividend adjusted)
  data/raw/etfs.csv        SPY, QQQ, IWM, DIA, RSP, TQQQ, SQQQ, UPRO, SPXU since 2010 (daily OHLCV)
  data/raw/VIX.csv         Cboe VIX daily history
Prices are adjusted, so returns include dividends; they are research prices, not executable quotes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
CONFIG = HERE / "config.json"
COLUMNS = ["open", "high", "low", "close", "volume"]


def config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def research_root(cfg: dict | None = None) -> Path:
    root = Path((cfg or config())["research_app"])
    if not (root / "data" / "raw").is_dir():
        raise FileNotFoundError(f"Research app data not found under {root}")
    return root


def _etf_file(path: Path, symbol: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=COLUMNS)
    frame = pd.read_csv(path, parse_dates=["date"])
    frame = frame[frame["ticker"] == symbol]
    return frame.set_index("date")[COLUMNS].astype(float).sort_index()


def load(symbol: str, root: Path | None = None) -> pd.DataFrame:
    """Daily OHLCV for one ETF plus that day's VIX close, longest history available."""
    root = Path(root) if root else research_root()
    raw = root / "data" / "raw"
    symbol = symbol.upper()
    long, short = _etf_file(raw / "etfs_long.csv", symbol), _etf_file(raw / "etfs.csv", symbol)
    frame = long if len(long) >= len(short) else short
    if frame.empty:
        raise ValueError(f"No saved daily history for {symbol}")
    if not frame.index.is_unique or not frame.index.is_monotonic_increasing:
        raise ValueError(f"{symbol} history has duplicate or unordered dates")
    if (frame[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError(f"{symbol} history has non-positive prices")
    vix_path = raw / "VIX.csv"
    if vix_path.exists():
        vix = pd.read_csv(vix_path)
        vix.columns = [c.strip().upper() for c in vix.columns]
        vix = pd.Series(vix["CLOSE"].astype(float).to_numpy(), index=pd.to_datetime(vix["DATE"], format="%m/%d/%Y"))
        frame["vix"] = vix.reindex(frame.index)
    return frame


def fingerprint(root: Path | None = None) -> str:
    """Hash of the input files, so every recorded result names the exact data it used."""
    root = Path(root) if root else research_root()
    digest = hashlib.sha256()
    for name in ("etfs_long.csv", "etfs.csv", "VIX.csv"):
        path = root / "data" / "raw" / name
        if path.exists():
            digest.update(name.encode() + hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()[:16]
