"""Read-only access to the trading-research app's saved market data.

The backtester never writes into the research app. It reads the app's download caches:
  data/raw/etfs_long.csv   SPY since 1993 and QQQ since 1999 (daily OHLCV, split/dividend adjusted)
  data/raw/etfs.csv        SPY, QQQ, IWM, DIA, RSP, TQQQ, SQQQ, UPRO, SPXU since 2010 (daily OHLCV)
  data/raw/VIX.csv         Cboe VIX daily history
Prices are adjusted, so returns include dividends; they are research prices, not executable quotes.

Every recorded run first copies these files into snapshots/<fingerprint>/ and reads from the copy, so the
inputs behind a result stay on disk after the research app refreshes its data.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
CONFIG = HERE / "config.json"
COLUMNS = ["open", "high", "low", "close", "volume"]
FILES = ("etfs_long.csv", "etfs.csv", "VIX.csv")
SNAPSHOTS = HERE / "snapshots"  # kept on this machine only (.gitignore): the inputs behind every recorded run


def config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def research_root(cfg: dict | None = None) -> Path:
    root = Path((cfg or config())["research_app"])
    if not (root / "data" / "raw").is_dir():
        raise FileNotFoundError(f"Research app data not found under {root}")
    return root


def _existing(raw: Path, name: str) -> Path | None:
    """The saved file, or its gzip copy (a snapshot folder holds .gz files)."""
    for path in (raw / name, raw / (name + ".gz")):
        if path.exists():
            return path
    return None


def _bytes(raw: Path, name: str) -> bytes | None:
    path = _existing(raw, name)
    if path is None:
        return None
    return gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()


def _etf_file(path: Path | None, symbol: str) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame(columns=COLUMNS)
    frame = pd.read_csv(path, parse_dates=["date"])
    frame = frame[frame["ticker"] == symbol]
    return frame.set_index("date")[COLUMNS].astype(float).sort_index()


def load(symbol: str, root: Path | None = None) -> pd.DataFrame:
    """Daily OHLCV for one ETF plus that day's VIX close, longest history available."""
    root = Path(root) if root else research_root()
    raw = root / "data" / "raw"
    symbol = symbol.upper()
    long, short = _etf_file(_existing(raw, "etfs_long.csv"), symbol), _etf_file(_existing(raw, "etfs.csv"), symbol)
    frame = long if len(long) >= len(short) else short
    if frame.empty:
        raise ValueError(f"No saved daily history for {symbol}")
    if not short.empty and frame.index[-1] < short.index[-1]:
        raise ValueError(f"{symbol}: the long history ends {frame.index[-1]:%Y-%m-%d}, before the recent file "
                         f"({short.index[-1]:%Y-%m-%d}); refresh the research app's data")
    if not frame.index.is_unique or not frame.index.is_monotonic_increasing:
        raise ValueError(f"{symbol} history has duplicate or unordered dates")
    if (frame[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError(f"{symbol} history has non-positive prices")
    vix_path = _existing(raw, "VIX.csv")
    if vix_path is not None:
        vix = pd.read_csv(vix_path)
        vix.columns = [c.strip().upper() for c in vix.columns]
        vix = pd.Series(vix["CLOSE"].astype(float).to_numpy(), index=pd.to_datetime(vix["DATE"], format="%m/%d/%Y"))
        frame["vix"] = vix.reindex(frame.index)
    return frame


def _fingerprint(contents: dict[str, bytes | None]) -> str:
    digest = hashlib.sha256()
    for name in FILES:
        if contents.get(name) is not None:
            digest.update(name.encode() + hashlib.sha256(contents[name]).digest())
    return digest.hexdigest()[:16]


def fingerprint(root: Path | None = None) -> str:
    """Hash of the input files, so every recorded result names the exact data it used."""
    root = Path(root) if root else research_root()
    return _fingerprint({name: _bytes(root / "data" / "raw", name) for name in FILES})


def snapshot(root: Path | None = None, dest: Path | None = None) -> tuple[Path, str]:
    """Copy the input files (gzipped) into snapshots/<fingerprint>/; return that folder and the fingerprint.

    A run reads its prices from the returned folder, never from the research app directly, so the recorded
    fingerprint always names files that are still on disk and a refresh in the middle of a run can't mix data.
    The folder has the research app's layout, so `load(symbol, folder)` rebuilds any recorded run.
    """
    root = Path(root) if root else research_root()
    contents = {name: _bytes(root / "data" / "raw", name) for name in FILES}
    mark = _fingerprint(contents)
    folder = Path(dest or SNAPSHOTS) / mark
    raw = folder / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for name, content in contents.items():
        target = raw / (name + ".gz")
        if content is None or target.exists():
            continue
        tmp = target.with_suffix(".tmp")
        with tmp.open("wb") as stream, gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as packed:
            packed.write(content)
        os.replace(tmp, target)
    if fingerprint(folder) != mark:
        raise ValueError(f"Snapshot {folder} does not match its fingerprint; do not use it")
    return folder, mark
