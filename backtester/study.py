"""Event studies: what happened after a signal, compared with all days in the same period.

For a signal known at day t's close, the forward return runs from t's close (the price a Kalshi perp
can be traded near at ~4:05 PM) or from t+1's open (an ETF bought the next morning) to the close
h sessions later. Each signal is judged against every day in the same period ("excess"), so normal
market drift is not mistaken for an edge.

The null model shifts the whole signal pattern by a random number of days within the period
(a circular shift). That keeps the number of signals and how they cluster, which matters because
multi-day forward windows overlap. p = (hits + 1) / (draws + 1), two-sided.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MIN_SIGNALS = 20


def forward_return(frame: pd.DataFrame, horizon: int, entry: str = "close") -> pd.Series:
    exit_price = frame["close"].shift(-horizon)
    if entry == "close":
        return exit_price / frame["close"] - 1
    if entry == "next_open":
        return exit_price / frame["open"].shift(-1) - 1
    raise ValueError(f"Unknown entry {entry!r}")


def non_overlapping(positions: np.ndarray, horizon: int) -> int:
    """How many signals remain if a new one is taken only after the previous window ends."""
    count, free_from = 0, -1
    for p in positions:
        if p >= free_from:
            count += 1
            free_from = p + horizon
    return count


def evaluate(signal: pd.Series, forward: pd.Series, mask: pd.Series, horizon: int,
             draws: int = 2000, rng: np.random.Generator | None = None) -> dict:
    rng = rng if rng is not None else np.random.default_rng(7)
    valid = mask & forward.notna()
    flags = signal.reindex(forward.index).fillna(False).astype(bool)[valid].to_numpy()
    values = forward[valid].to_numpy()
    n, m = int(flags.sum()), len(values)
    out = {"signals": n, "days": m}
    if m == 0:
        return {**out, "status": "no data"}
    base = float(values.mean())
    out.update(base_mean=base, base_hit=float((values > 0).mean()))
    if n < MIN_SIGNALS:
        return {**out, "status": f"fewer than {MIN_SIGNALS} signals"}
    chosen = values[flags]
    excess = float(chosen.mean() - base)
    p = None
    if draws:
        shifts = rng.integers(1, m, size=draws)
        null = np.fromiter((values[np.roll(flags, k)].mean() - base for k in shifts), float, draws)
        p = float((np.sum(np.abs(null) >= abs(excess)) + 1) / (draws + 1))
    out.update(status="ok", mean=float(chosen.mean()), excess=excess, hit=float((chosen > 0).mean()), p=p,
               trades=non_overlapping(np.flatnonzero(flags), horizon))
    return out


def bh_qvalues(pvalues: list[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p-values (false discovery rate) for every test in a run."""
    p = np.asarray(pvalues, float)
    if p.size == 0:
        return []
    order = np.argsort(p)
    ranked = p[order] * p.size / np.arange(1, p.size + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q = np.empty_like(p)
    q[order] = np.minimum(ranked, 1.0)
    return q.tolist()


def verdict(dev: dict, holdout: dict | None, q: float | None, cost: float) -> str:
    """Plain label. 'Candidate' needs a development result that survives the multiple-testing
    correction and covers costs, confirmed in the same direction on the untouched holdout."""
    if dev.get("status") != "ok":
        return "Too few signals"
    significant = dev["p"] < 0.05 and q is not None and q < 0.10
    if not significant:
        return "No evidence"
    if dev["excess"] < 0:
        return "Opposite effect (weaker than normal)"
    if holdout is None or holdout.get("status") != "ok":
        return "Development only (no holdout data)"
    if holdout["excess"] <= 0 or holdout["p"] >= 0.10:
        return "Failed holdout"
    if dev["excess"] <= cost:
        return "Real but smaller than costs"
    return "Candidate"
