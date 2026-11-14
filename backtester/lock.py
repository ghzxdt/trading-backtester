"""Registered rules cannot change under a recorded version.

rule_lock.json holds a fingerprint of what each registered signal and exit *does*: the days it fires (or the
exits it picks) on a fixed made-up price history. A rule edited in place, or an indicator changed underneath it,
gives a different fingerprint and every run refuses to start. The fix is a new version, never an edit.

Register a new rule or version after adding it to catalog.py or strategies.py:
    ..\\trading-research\\.venv\\Scripts\\python.exe -B -m backtester.lock --add
`--add` only adds keys that are missing; it never replaces a recorded fingerprint.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import catalog, indicators as ind  # noqa: F401 (ind: handy for registering a new rule)

LOCK = Path(__file__).resolve().parent.parent / "rule_lock.json"
DAYS = 2000


def reference_frame() -> pd.DataFrame:
    """A fixed price history from integer arithmetic only, so it is the same on every machine and library version.
    It has calm, falling and volatile stretches and volume spikes, so every registered rule fires on it."""
    state = 20261108

    def uniform() -> float:
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return (state >> 11) / float(1 << 53)

    rows, close = [], 100.0
    for day in range(DAYS):
        phase = (day // 250) % 4  # up, down, choppy, up
        drift = (0.0008, -0.0012, 0.0, 0.0006)[phase]
        scale = (0.008, 0.016, 0.022, 0.010)[phase]
        change = drift + scale * (uniform() + uniform() + uniform() + uniform() - 2.0)
        open_ = close * (1 + 0.003 * (uniform() - 0.5))
        close = close * (1 + change)
        high = max(open_, close) * (1 + 0.006 * uniform())
        low = min(open_, close) * (1 - 0.006 * uniform())
        volume = 1e6 * (1 + uniform()) * (3.5 if uniform() < 0.06 else 1.0)
        rows.append((open_, high, low, close, volume))
    return pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"],
                        index=pd.bdate_range("2001-01-01", periods=DAYS))


def _mark(values: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(values).astype("<i8").tobytes()).hexdigest()[:16]


def marks() -> dict[str, str]:
    """Fingerprint of every rule in the code as it stands now."""
    from .strategies import EXITS
    frame = reference_frame()
    out = {}
    for study in catalog.STUDIES:
        fired = study.rule(frame).fillna(False).to_numpy(bool)
        if not fired.any():
            raise ValueError(f"{study.name} never fires on the reference history, so it cannot be fingerprinted")
        out[f"study:{study.name}@{study.version}"] = _mark(fired)
    positions = np.arange(30, DAYS - 15)
    for ex in EXITS:
        out[f"exit:{ex.name}@{ex.version}"] = _mark(ex.rule(frame, positions))
    from . import lead_v2  # a verdict's thresholds are registered too (its code is covered by the tests)
    out[f"verdict:lead@{lead_v2.VERSION}"] = hashlib.sha256(json.dumps(lead_v2.PARAMS, sort_keys=True).encode()).hexdigest()[:16]
    return out


def check(path: Path = LOCK) -> dict[str, str]:
    """Return the current fingerprints, or raise if they disagree with what was registered."""
    now = marks()
    locked = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    changed = sorted(k for k in now if k in locked and locked[k] != now[k])
    missing = sorted(k for k in locked if k not in now)
    new = sorted(k for k in now if k not in locked)
    problems = []
    if changed:
        problems.append("changed under a recorded version (add a new version instead): " + ", ".join(changed))
    if missing:
        problems.append("recorded but no longer in the code: " + ", ".join(missing))
    if new:
        problems.append("not registered yet (run `-m backtester.lock --add`): " + ", ".join(new))
    if problems:
        raise ValueError("Rule lock: " + "; ".join(problems))
    return now


def add(path: Path = LOCK) -> list[str]:
    now = marks()
    locked = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    new = sorted(k for k in now if k not in locked)
    if new:
        locked.update({k: now[k] for k in new})
        path.write_text(json.dumps(locked, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return new


if __name__ == "__main__":
    if "--add" in sys.argv[1:]:
        added = add()
        print("Registered: " + ", ".join(added) if added else "Nothing new to register.")
    check()
    print(f"Rule lock OK ({len(marks())} rules).")
