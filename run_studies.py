"""Run the registered indicator studies on the research app's daily data and write a report.

    ..\\trading-research\\.venv\\Scripts\\python.exe -B run_studies.py
    ..\\trading-research\\.venv\\Scripts\\python.exe -B run_studies.py --symbols SPY --horizons 5

Each run tests every study x symbol x horizon on the development period (2010 on), then checks the same
rule once on the untouched 1993-2009 holdout where history exists. Results go to reports/ and every
test is appended to trials.jsonl, so failed ideas stay on the record.
"""
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from backtester import data, registry
from backtester.catalog import STUDIES
from backtester.study import bh_qvalues, evaluate, forward_return, verdict

HERE = Path(__file__).resolve().parent
REPORTS = HERE / "reports"
TRIALS = HERE / "trials.jsonl"


def period_mask(index: pd.DatetimeIndex, spec: dict) -> pd.Series:
    start = pd.Timestamp(spec["start"]) if spec.get("start") else index.min()
    end = pd.Timestamp(spec["end"]) if spec.get("end") else index.max()
    return pd.Series((index >= start) & (index <= end), index=index)


def code_version() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE, capture_output=True,
                              text=True, timeout=10).stdout.strip() or "uncommitted"
    except OSError:
        return "unknown"


def run(symbols, horizons, draws, seed, cfg=None, root=None) -> list[dict]:
    cfg = cfg or data.config()
    root = root or data.research_root(cfg)
    rng = np.random.default_rng(seed)
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
                close_fwd = forward_return(frame, h, "close")
                rows.append({"study": study.name, "version": study.version, "description": study.description,
                             "symbol": symbol, "horizon": h,
                             "dev": evaluate(signal, close_fwd, dev_mask, h, draws, rng),
                             "holdout": evaluate(signal, close_fwd, hold_mask, h, draws, rng) if hold_mask.any() else None,
                             "next_open": evaluate(signal, forward_return(frame, h, "next_open"), dev_mask, h, 0, rng)})
    tested = [r for r in rows if r["dev"].get("status") == "ok"]
    for row, q in zip(tested, bh_qvalues([r["dev"]["p"] for r in tested])):
        row["q"] = q
    for row in rows:
        row["verdict"] = verdict(row["dev"], row["holdout"], row.get("q"), cost)
    return rows


def bp(value) -> str:
    return "–" if value is None or (isinstance(value, float) and np.isnan(value)) else f"{value * 1e4:+.1f}"


def report(rows, cfg, fingerprint, version, started) -> str:
    costs = cfg["costs_round_trip_bps"]
    lines = [f"# Indicator studies, {started:%Y-%m-%d}", "",
             f"Code {version}; research-app data fingerprint {fingerprint}; {len(rows)} tests "
             f"({sum(1 for r in rows if 'q' in r)} with enough signals).", "",
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
    ap.add_argument("--symbols", nargs="+", default=["SPY", "QQQ", "IWM"])
    ap.add_argument("--horizons", nargs="+", type=int, default=[1, 5, 10])
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)
    started = datetime.now(timezone.utc)
    cfg = data.config()
    root = data.research_root(cfg)
    rows = run([s.upper() for s in args.symbols], args.horizons, args.draws, args.seed, cfg, root)
    fingerprint, version = data.fingerprint(root), code_version()
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / f"{started:%Y-%m-%d}-indicator-studies.md"
    path.write_text(report(rows, cfg, fingerprint, version, started), encoding="utf-8")
    registry.append(TRIALS, {"run_at": started.isoformat(timespec="seconds"), "code": version, "data": fingerprint,
                             "seed": args.seed, "draws": args.draws, "report": path.name,
                             "tests": [{"study": r["study"], "version": r["version"], "symbol": r["symbol"],
                                        "horizon": r["horizon"], "verdict": r["verdict"],
                                        "dev_excess": r["dev"].get("excess"), "dev_p": r["dev"].get("p"),
                                        "q": r.get("q"), "holdout_excess": (r["holdout"] or {}).get("excess"),
                                        "holdout_p": (r["holdout"] or {}).get("p")} for r in rows]})
    print(f"Wrote {path} ({len(rows)} tests; {registry.total_tests(TRIALS)} recorded in total).")
    for r in rows:
        if r["verdict"] == "Candidate":
            print(f"  Candidate: {r['study']} {r['symbol']} h={r['horizon']} excess {bp(r['dev']['excess'])} bp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
