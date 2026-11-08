"""Append-only, hash-chained record of every study run, including the ideas that failed.

Counting every test is what keeps a lucky backtest from looking like an edge. Never edit trials.jsonl by
hand; a broken chain is reported on the next read.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _digest(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows, previous = [], ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        body = {k: v for k, v in row.items() if k != "hash"}
        if row.get("previous_hash") != previous or row.get("hash") != _digest(body):
            raise ValueError(f"{path.name} hash chain is broken; do not overwrite it")
        previous = row["hash"]
        rows.append(row)
    return rows


def append(path: Path, record: dict) -> dict:
    rows = read(path)
    body = {**record, "previous_hash": rows[-1]["hash"] if rows else ""}
    row = {**body, "hash": _digest(body)}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def total_tests(path: Path) -> int:
    return sum(len(r.get("tests", [])) for r in read(path))
