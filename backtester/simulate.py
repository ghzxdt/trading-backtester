"""Trade simulation for registered strategies (backtester/strategies.py), with two benchmarks.

Daily data only: no stops (there is no honest intraday path to fill them), one position at a time, 1x notional.
Prices are adjusted ETF prices; for the perp modes they stand in for the Kalshi perp, whose fees and 4 PM funding
are charged explicitly.

Benchmarks:
- Exposure-matched buy-and-hold: hold the same instrument every day at a constant fraction equal to the
  strategy's time in the market (perp modes also pay funding on that fraction every calendar day).
- Random entries: the same number of trades with the same holding lengths at random entry days in the period;
  the strategy's mean gross trade return is ranked against 2,000 such draws (percentile).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def find_trades(frame: pd.DataFrame, signal: pd.Series, exit_rule, mask: pd.Series) -> list[tuple[int, int]]:
    """(signal position, exit position) pairs, one position at a time, both days inside the period."""
    flags = signal.reindex(frame.index).fillna(False).to_numpy(bool) & mask.to_numpy(bool)
    inside = mask.to_numpy(bool)
    trades, busy_until = [], -1
    for p in np.flatnonzero(flags):
        if p <= busy_until:
            continue
        e = int(exit_rule(frame, np.array([p]))[0])
        if e >= len(frame) or not inside[e]:
            continue
        trades.append((int(p), e))
        busy_until = e
    return trades


def costs_for(mode: str, cfg: dict, entry_day: pd.Timestamp, exit_day: pd.Timestamp) -> float:
    """Round-trip cost as a fraction of notional."""
    fees = cfg["costs_round_trip_bps"]
    if mode.startswith("etf"):
        return fees["etf"] / 1e4
    crossings = max((exit_day - entry_day).days - 1, 0)  # 4 PM fundings between a ~4:05 PM entry and a pre-4 PM exit
    return (fees["kalshi_maker" if mode == "perp_maker" else "kalshi_taker"] + cfg["funding_bps_per_day"] * crossings) / 1e4


def price_trades(frame: pd.DataFrame, trades, mode: str, cfg: dict) -> pd.DataFrame:
    close, open_ = frame["close"].to_numpy(), frame["open"].to_numpy()
    rows = []
    for p, e in trades:
        entry = open_[p + 1] if mode == "etf_next_open" else close[p]
        gross = close[e] / entry - 1
        cost = costs_for(mode, cfg, frame.index[p], frame.index[e])
        rows.append({"signal_day": frame.index[p], "exit_day": frame.index[e], "sessions": e - p,
                     "gross": gross, "cost": cost, "net": gross - cost})
    return pd.DataFrame(rows, columns=["signal_day", "exit_day", "sessions", "gross", "cost", "net"])


def daily_returns(frame: pd.DataFrame, trades, mode: str, cfg: dict, mask: pd.Series) -> tuple[pd.Series, float]:
    """Daily marked returns inside the period (cash earns 0) and the share of period days in the market."""
    close, open_ = frame["close"].to_numpy(), frame["open"].to_numpy()
    out = np.zeros(len(frame))
    held = np.zeros(len(frame), bool)
    for p, e in trades:
        for d in range(p + 1, e + 1):
            if d == p + 1 and mode == "etf_next_open":
                out[d] = close[d] / open_[d] - 1
            else:
                out[d] = close[d] / close[d - 1] - 1
            held[d] = True
        cost = costs_for(mode, cfg, frame.index[p], frame.index[e])
        out[e] = (1 + out[e]) * (1 - cost) - 1
    inside = mask.to_numpy(bool)
    series = pd.Series(out, index=frame.index)[inside]
    return series, float(held[inside].mean()) if inside.any() else 0.0


def matched_buy_and_hold(frame: pd.DataFrame, mask: pd.Series, exposure: float, mode: str, cfg: dict) -> pd.Series:
    r = frame["close"].pct_change().fillna(0.0)
    if mode.startswith("perp"):
        gap = pd.Series(frame.index, index=frame.index).diff().dt.days.fillna(1)
        r = r - cfg["funding_bps_per_day"] / 1e4 * gap
    return (exposure * r)[mask.to_numpy(bool)]


def summary(returns: pd.Series) -> dict:
    if returns.empty:
        return {"cagr": None, "max_drawdown": None, "return_per_drawdown": None}
    equity = (1 + returns).cumprod()
    years = len(returns) / TRADING_DAYS
    cagr = float(equity.iloc[-1] ** (1 / years) - 1) if years > 0 and equity.iloc[-1] > 0 else -1.0
    drawdown = float((equity / equity.cummax() - 1).min())
    return {"cagr": cagr, "max_drawdown": drawdown,
            "return_per_drawdown": cagr / abs(drawdown) if drawdown < 0 else None}


def random_percentile(frame: pd.DataFrame, mask: pd.Series, priced: pd.DataFrame, mode: str,
                      draws: int = 2000, rng: np.random.Generator | None = None) -> float | None:
    """Percentile of the strategy's mean gross trade return among random same-length entries."""
    if priced.empty:
        return None
    rng = rng if rng is not None else np.random.default_rng(7)
    close, open_ = frame["close"].to_numpy(), frame["open"].to_numpy()
    lengths = priced["sessions"].to_numpy(int)
    inside = np.flatnonzero(mask.to_numpy(bool))
    candidates = inside[inside + lengths.max() <= inside.max()]
    if len(candidates) == 0:
        return None
    starts = rng.choice(candidates, size=(draws, len(lengths)))
    ends = starts + lengths
    entry = open_[starts + 1] if mode == "etf_next_open" else close[starts]
    means = (close[ends] / entry - 1).mean(axis=1)
    return float((means < priced["gross"].mean()).mean() * 100)


def evaluate(frame, signal, exit_rule, mask, mode, cfg, draws=2000, rng=None) -> dict:
    trades = find_trades(frame, signal, exit_rule, mask)
    priced = price_trades(frame, trades, mode, cfg)
    returns, exposure = daily_returns(frame, trades, mode, cfg, mask)
    out = {"trades": len(priced), "exposure": exposure, "strategy": summary(returns),
           "matched": summary(matched_buy_and_hold(frame, mask, exposure, mode, cfg))}
    if len(priced):
        wins, losses = priced.loc[priced["net"] > 0, "net"], priced.loc[priced["net"] <= 0, "net"]
        out.update(win_rate=float((priced["net"] > 0).mean()), mean_net=float(priced["net"].mean()),
                   mean_gross=float(priced["gross"].mean()), avg_win=float(wins.mean()) if len(wins) else None,
                   avg_loss=float(losses.mean()) if len(losses) else None,
                   mean_sessions=float(priced["sessions"].mean()),
                   random_percentile=random_percentile(frame, mask, priced, mode, draws, rng))
    return out


def verdict(dev: dict, holdout: dict | None, min_trades: int = 20) -> str:
    """Registered 2026-11-08: Lead needs the random-entry test (>= 95th percentile in development, >= 90th in the
    holdout) and a higher CAGR than exposure-matched buy-and-hold in both periods."""
    def beats(r):
        s, m = r["strategy"]["cagr"], r["matched"]["cagr"]
        return s is not None and m is not None and s > m
    if dev["trades"] < min_trades:
        return "Too few trades"
    if (dev.get("random_percentile") or 0) < 95:
        return "No edge"
    if holdout is None or holdout["trades"] < min_trades:
        return "Development only (no holdout)"
    if (holdout.get("random_percentile") or 0) < 90:
        return "Failed holdout"
    return "Lead" if beats(dev) and beats(holdout) else "Timing edge only"


def finite(x):
    return x is not None and not (isinstance(x, float) and math.isnan(x))
