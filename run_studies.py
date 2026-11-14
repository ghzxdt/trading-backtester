"""Run the registered indicator studies on the research app's daily data and write a report.

    ..\\trading-research\\.venv\\Scripts\\python.exe -B run_studies.py
    ..\\trading-research\\.venv\\Scripts\\python.exe -B run_studies.py --symbols SPY --horizons 5

Each run tests every study x symbol x horizon on the development period (2010 on). The 1993-2009 holdout is
evaluated once per study version, by the first registered run, and stored in holdout_ledger.jsonl; later runs
read the stored result. Results go to reports/ and every test is appended to trials.jsonl, so failed ideas stay
on the record. A run with other symbols, horizons, seed or draws is partial: no verdicts, no holdout look.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from backtester import catalog, data, lock, registry, runlog
from backtester.catalog import STUDIES
from backtester.ledger import HoldoutLedger, holdout_result, rng_for
from backtester.report_html import render
from backtester.study import bh_qvalues, evaluate, forward_return, verdict

HERE = Path(__file__).resolve().parent
REPORTS = HERE / "reports"
TRIALS = HERE / "trials.jsonl"
LEDGER = HERE / "holdout_ledger.jsonl"
METHOD = 2  # 2 (2026-11-13): one random stream per test, holdout read from the ledger. 1: one shared stream.
PARTIAL = "Partial run (no verdict)"


def period_mask(index: pd.DatetimeIndex, spec: dict) -> pd.Series:
    start = pd.Timestamp(spec["start"]) if spec.get("start") else index.min()
    end = pd.Timestamp(spec["end"]) if spec.get("end") else index.max()
    return pd.Series((index >= start) & (index <= end), index=index)


code_version = runlog.code_version  # kept under its old name for run_trades.py


def is_registered(symbols, horizons, draws, seed) -> bool:
    return (tuple(symbols), tuple(horizons), draws, seed) == (catalog.SYMBOLS, catalog.HORIZONS, catalog.DRAWS, catalog.SEED)


def run(symbols, horizons, draws, seed, cfg=None, root=None, ledger: HoldoutLedger | None = None) -> list[dict]:
    """`ledger=None` computes the holdout in memory and stores nothing (tests and rebuild checks)."""
    cfg = cfg or data.config()
    root = root or data.research_root(cfg)
    registered = is_registered(symbols, horizons, draws, seed)
    cost = cfg["costs_round_trip_bps"][cfg.get("verdict_cost", "etf")] / 1e4
    rows = []
    for symbol in symbols:
        frame = data.load(symbol, root)
        dev_mask, hold_mask = period_mask(frame.index, cfg["development"]), period_mask(frame.index, cfg["holdout"])
        for study in STUDIES:
            if study.needs_volume and frame["volume"].isna().all():
                continue
            signal = study.rule(frame).fillna(False).astype(bool)
            for h in horizons:
                who = (study.name, study.version, symbol, h)  # each test draws from its own random stream
                close_fwd = forward_return(frame, h, "close")
                holdout, source = holdout_result(
                    ledger, registered, f"study|{study.name}@{study.version}|{symbol}|h{h}", bool(hold_mask.any()),
                    lambda: evaluate(signal, close_fwd, hold_mask, h, draws, rng_for(seed, *who, "holdout")))
                rows.append({"study": study.name, "version": study.version, "description": study.description,
                             "symbol": symbol, "horizon": h,
                             "dev": evaluate(signal, close_fwd, dev_mask, h, draws, rng_for(seed, *who, "development")),
                             "holdout": holdout, "holdout_source": source,
                             "next_open": evaluate(signal, forward_return(frame, h, "next_open"), dev_mask, h, 0)})
    if not registered:  # the correction needs the whole registered family, so a partial run gives no verdicts
        for row in rows:
            row["verdict"] = PARTIAL
        return rows
    tested = [r for r in rows if r["dev"].get("status") == "ok"]
    for row, q in zip(tested, bh_qvalues([r["dev"]["p"] for r in tested])):
        row["q"] = q
    for row in rows:
        row["verdict"] = verdict(row["dev"], row["holdout"], row.get("q"), cost)
    return rows


def bp(value) -> str:
    return "–" if value is None or (isinstance(value, float) and np.isnan(value)) else f"{value * 1e4:+.1f}"


def holdout_note(rows) -> list[str]:
    """Say where the holdout figures came from, and flag a partial run."""
    sources = [r.get("holdout_source") or "" for r in rows if r.get("holdout") is not None]
    first, stored = sum(s.startswith("first look") for s in sources), sum(s.startswith("ledger") for s in sources)
    lines = []
    if rows and rows[0].get("verdict") == PARTIAL:
        lines += ["**Partial run.** This is not the registered set of symbols, horizons, seed and draws, so there are "
                  "no q-values or verdicts, and the holdout was not evaluated (stored results are shown where they "
                  "exist).", ""]
    if first or stored:
        dates = sorted({s.split("first computed ")[1] for s in sources if "first computed " in s})
        lines += [f"Holdout: {stored} results read from `holdout_ledger.jsonl`"
                  + (f" (first computed {', '.join(dates)})" if dates else "")
                  + f", {first} evaluated for the first time in this run and stored. Each study version gets one look.", ""]
    return lines


def report(rows, cfg, fingerprint, version, started) -> str:
    costs = cfg["costs_round_trip_bps"]
    lines = [f"# Indicator studies, {started:%Y-%m-%d}", "",
             f"Code {version}; research-app data fingerprint {fingerprint}; {len(rows)} tests "
             f"({sum(1 for r in rows if r['dev'].get('status') == 'ok')} with enough signals).", "",
             *holdout_note(rows),
             "**How to read this.** Each row asks: after the signal (known at that day's close), how did the index do "
             "over the next *h* sessions compared with all days in the same period? *Excess* is that difference in "
             "basis points (100 bp = 1%). *p* is the chance of an excess this large from a randomly shifted copy of "
             "the same signal pattern; *q* corrects p for every test in this run. *Holdout* re-checks the same rule on "
             "1993-2009 data that played no part in choosing it. *Next-open* is the excess if you buy at the next "
             "morning's open instead of the close.", "",
             f"Costs: ETF round trip {costs['etf']} bp (used for verdicts); Kalshi perps {costs['kalshi_taker']} bp as "
             f"taker or {costs['kalshi_maker']} bp as maker. A candidate must clear the ETF cost.", ""]
    for name in dict.fromkeys(r["study"] for r in rows):
        group = [r for r in rows if r["study"] == name]
        lines += [f"## {name} ({group[0]['version']})", "", group[0]["description"] + ".", "",
                  "| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in group:
            d, h, n = r["dev"], r["holdout"] or {}, r["next_open"]
            ok = d.get("status") == "ok"
            hold_ok = h.get("status") == "ok"
            lines.append("| " + " | ".join([
                r["symbol"], str(r["horizon"]),
                f"{d['signals']} ({d.get('trades', '–')})",
                bp(d.get("excess")) if ok else "–",
                f"{d['hit']:.0%} vs {d['base_hit']:.0%}" if ok else "–",
                f"{d['p']:.3f}" if ok else "–",
                f"{r['q']:.3f}" if "q" in r else "–",
                str(h.get("signals", "–")) if r["holdout"] else "no data",
                bp(h.get("excess")) if hold_ok else "–",
                f"{h['p']:.3f}" if hold_ok else "–",
                bp(n.get("excess")) if n.get("status") == "ok" else "–",
                r["verdict"]]) + " |")
        lines.append("")
    tally = pd.Series([r["verdict"] for r in rows]).value_counts()
    lines += ["## Summary", ""] + [f"- {k}: {v}" for k, v in tally.items()] + [
        "", "These are historical event studies on adjusted daily ETF prices, not trades: no stops, sizing or "
        "slippage beyond the stated cost. Overlapping multi-day windows make each signal less independent than the "
        "count suggests; the trades column counts non-overlapping ones. A candidate is a lead for a fuller test, "
        "not an edge."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbols", nargs="+", default=list(catalog.SYMBOLS))
    ap.add_argument("--horizons", nargs="+", type=int, default=list(catalog.HORIZONS))
    ap.add_argument("--draws", type=int, default=catalog.DRAWS)
    ap.add_argument("--seed", type=int, default=catalog.SEED)
    args = ap.parse_args(argv)
    started = datetime.now(timezone.utc)
    cfg = data.config()
    registry.read(TRIALS)  # refuse to start on a broken record
    rules = lock.check()   # ... or on a rule changed under a recorded version
    ledger = HoldoutLedger(LEDGER)
    root, fingerprint = data.snapshot(data.research_root(cfg))  # the run reads this copy, which stays on disk
    version = code_version()
    symbols = [s.upper() for s in args.symbols]
    rows = run(symbols, args.horizons, args.draws, args.seed, cfg, root, ledger)
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / f"{runlog.report_stem('indicator-studies', started)}.md"
    text = report(rows, cfg, fingerprint, version, started)
    # The record goes first: if it can't be written (a broken chain), no report appears without one.
    registry.append(TRIALS, {"run_at": started.isoformat(timespec="seconds"), "code": version, "data": fingerprint,
                             "settings": runlog.settings(cfg), "method": METHOD,
                             "family": "registered" if is_registered(symbols, args.horizons, args.draws, args.seed) else "partial",
                             "rules": {k: v for k, v in rules.items() if k.startswith("study:")},
                             "seed": args.seed, "draws": args.draws, "report": path.name,
                             "tests": [{"study": r["study"], "version": r["version"], "symbol": r["symbol"],
                                        "holdout_source": r.get("holdout_source"),
                                        "horizon": r["horizon"], "verdict": r["verdict"],
                                        "dev_excess": r["dev"].get("excess"), "dev_p": r["dev"].get("p"),
                                        "q": r.get("q"), "holdout_excess": (r["holdout"] or {}).get("excess"),
                                        "holdout_p": (r["holdout"] or {}).get("p")} for r in rows]})
    ledger.commit(started.isoformat(timespec="seconds"), version, fingerprint, args.seed, args.draws)
    path.write_text(text, encoding="utf-8")
    path.with_suffix(".html").write_text(render(text, path.stem), encoding="utf-8")
    print(f"Wrote {path} ({len(rows)} tests; {registry.total_tests(TRIALS)} recorded in total).")
    for r in rows:
        if r["verdict"] == "Candidate":
            print(f"  Candidate: {r['study']} {r['symbol']} h={r['horizon']} excess {bp(r['dev']['excess'])} bp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
