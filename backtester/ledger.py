"""Two guards on how results are produced: one random stream per test, and the holdout checked once.

Seeds. Every test draws its random numbers from its own generator, seeded from the run seed and the test's
identity. A test's p-value therefore does not depend on which other tests ran before it, or in what order.

Holdout ledger. The first registered run that evaluates a rule on 1993-2009 stores the result in
holdout_ledger.jsonl (append-only, hash-chained like trials.jsonl). Every later run reads that stored result
instead of computing it again, so the holdout cannot be consulted repeatedly while a rule is being developed.
A changed rule needs a new version, and a new version gets its own single look.

History the ledger cannot show: before it existed (2026-11-13) the 1993-2009 period was evaluated in six
recorded runs of the unchanged v1 rules (see trials.jsonl). Those were repeats, not rule changes.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from . import registry


def rng_for(seed: int, *identity) -> np.random.Generator:
    """A generator that belongs to one test: same seed and identity, same draws, whatever else ran."""
    text = "|".join(str(part) for part in (seed, *identity))
    return np.random.default_rng(int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big"))


def plain(value):
    """JSON-safe copy (numpy numbers become Python numbers)."""
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


class HoldoutLedger:
    """Stored holdout results by test key. `path=None` keeps nothing (tests and rebuild checks)."""

    def __init__(self, path: Path | None):
        self.path, self.stored, self.pending = path, {}, {}
        for row in registry.read(path) if path else []:
            for key, result in row["entries"].items():
                self.stored.setdefault(key, {"result": result, "first_run_at": row["run_at"],
                                             "code": row["code"], "data": row["data"]})

    def get(self, key: str) -> dict | None:
        entry = self.stored.get(key)
        return None if entry is None else entry["result"]

    def source(self, key: str) -> str | None:
        entry = self.stored.get(key)
        return None if entry is None else f"ledger, first computed {entry['first_run_at'][:10]}"

    def add(self, key: str, result: dict) -> None:
        if key not in self.stored:
            self.pending[key] = plain(result)

    def commit(self, run_at: str, code: str, data: str, seed: int, draws: int) -> int:
        """Append this run's first looks. Returns how many were added."""
        if not self.path or not self.pending:
            return 0
        registry.append(self.path, {"run_at": run_at, "code": code, "data": data, "seed": seed, "draws": draws,
                                    "entries": self.pending})
        added, self.pending = len(self.pending), {}
        return added


def holdout_result(ledger: HoldoutLedger | None, registered: bool, key: str, has_data: bool, compute):
    """(result, where it came from). The only place a runner may evaluate the holdout.

    - no ledger (tests, rebuild checks): computed in memory, stored nowhere;
    - already in the ledger: the stored first look, never recomputed;
    - not yet in the ledger: computed and stored, but only by a run with the registered settings."""
    if not has_data:
        return None, None
    if ledger is None:
        return compute(), "computed, not stored"
    stored = ledger.get(key)
    if stored is not None:
        return stored, ledger.source(key)
    if not registered:
        return None, "not checked (only a run with the registered settings may look at the holdout)"
    result = plain(compute())
    ledger.add(key, result)
    return result, "first look, stored in the ledger"
