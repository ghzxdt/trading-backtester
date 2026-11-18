"""Run the registered filter tests (backtester/splits.py) and write a report.

    ..\\trading-research\\.venv\\Scripts\\python.exe -B run_splits.py

For four registered strategy-entries (the two QQQ next-open Leads, the same Bollinger rule on SPY, and QQQ RSI(2) at
the close), asks whether the trades did better or worse when a condition held at the signal: a gap up at the next open
(idea 7), SPY below its 200-day average and the VIX level (idea 8), an inverted VIX curve, a scheduled release within 5
sessions; and whether each strategy beats trades started on days with the same VIX level (volatility-matched baseline).
Development window: Lead v3's (2010-01-01 to 2026-11-13). 1993-2009 is evaluated once per test version and stored in
holdout_ledger.jsonl. Writes reports/<date-time>-filter-tests.md and .html, exports/filter_tests.json and
exports/evidence.json, and appends the run to trials.jsonl. Other settings are a partial run: no labels, no 1993-2009.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from backtester import data, evidence, lead_v3, lock, registry, runlog, splits
from backtester.ledger import HoldoutLedger, holdout_result, rng_for
from backtester.report_html import render
from backtester.study import bh_qvalues
from run_studies import METHOD, PARTIAL, code_version, period_mask

HERE = Path(__file__).resolve().parent
REPORTS = HERE / "reports"
EXPORTS = HERE / "exports"
TRIALS = HERE / "trials.jsonl"
LEDGER = HERE / "holdout_ledger.jsonl"
MODE_LABELS = {"etf_close": "close", "etf_next_open": "next open"}


def is_registered(resamples: int, seed: int) -> bool:
    return (resamples, seed) == (splits.RESAMPLES, splits.SEED)


def run(resamples: int, seed: int, cfg=None, root=None, ledger: HoldoutLedger | None = None) -> list[dict]:
    """`ledger=None` computes 1993-2009 in memory and stores nothing (tests and rebuild checks)."""
    cfg = cfg or data.config()
    root = root or data.research_root(cfg)
    registered = is_registered(resamples, seed)
    context = data.load_context(root)
    spy = data.load("SPY", root)
    frames, rows = {}, []
    for strategy in splits.STRATEGIES:
        symbol, signal, exit_name, mode = strategy
        if symbol not in frames:
            frames[symbol] = data.load(symbol, root)
        frame = frames[symbol]
        vix = frame["vix"] if "vix" in frame else pd.Series(float("nan"), index=frame.index)
        ctx = {"vix": vix, "vix3m": context["vix3m"], "spy_close": spy["close"], "events": context["events"]}
        dev, hold = lead_v3.development_mask(frame.index, cfg), period_mask(frame.index, cfg["holdout"])
        key = splits.strategy_key(strategy)
        dev_trades = splits.strategy_trades(frame, strategy, dev, cfg)
        hold_trades = splits.strategy_trades(frame, strategy, hold, cfg) if hold.any() else None
        base = {"strategy": key, "symbol": symbol, "signal": signal, "exit": exit_name, "mode": mode,
                "strategy_trades": len(dev_trades)}
        for split in splits.SPLITS:
            if mode not in split.entries:
                continue
            values = split.value(frame, ctx)
            who = (split.name, split.version, key)
            dev_result = splits.contrast(dev_trades, values, split, rng_for(seed, *who, "development"), resamples)
            hold_result, source = holdout_result(
                ledger, registered, f"filter|{split.name}@{split.version}|{key}", bool(split.before_2010 and hold.any()),
                lambda v=values, w=who: splits.contrast(hold_trades, v, split, rng_for(seed, *w, "holdout"), resamples))
            rows.append({**base, "kind": "split", "test": split.name, "version": split.version,
                         "description": split.description, "group_label": split.group_label,
                         "rest_label": split.rest_label, "dev": dev_result, "holdout": hold_result, "holdout_source": source})
        test = splits.VOL_TEST
        who = (test["name"], test["version"], key)
        dev_result = splits.volatility_test(frame, dev, dev_trades, mode, vix, rng_for(seed, *who, "development"), resamples)
        hold_result, source = holdout_result(
            ledger, registered, f"filter|{test['name']}@{test['version']}|{key}", bool(hold.any() and vix[hold].notna().any()),
            lambda: splits.volatility_test(frame, hold, hold_trades, mode, vix, rng_for(seed, *who, "holdout"), resamples))
        rows.append({**base, "kind": "baseline", "test": test["name"], "version": test["version"],
                     "description": test["description"], "group_label": None, "rest_label": None,
                     "dev": dev_result, "holdout": hold_result, "holdout_source": source})
    judge(rows, registered)
    return rows


def judge(rows: list[dict], registered: bool) -> None:
    if not registered:
        for row in rows:
            row["q"], row["label"] = None, PARTIAL
        return
    family = [r for r in rows if r["dev"].get("status") == "ok"]
    for row, q in zip(family, bh_qvalues([r["dev"]["p"] for r in family])):
        row["q"] = q
    for row in rows:
        row.setdefault("q", None)
        label = splits.contrast_label if row["kind"] == "split" else splits.volatility_label
        row["label"] = label(row["dev"], row["holdout"], row["q"])


def bp(x) -> str:
    return "–" if x is None or x != x else f"{x * 1e4:+.0f}"


def interval(pair) -> str:
    return "–" if not pair else f"{pair[0] * 1e4:+.0f} to {pair[1] * 1e4:+.0f}"


def p_text(x) -> str:
    return "–" if x is None else f"{x:.3f}"


def report(rows, cfg, fingerprint, version, started, resamples) -> str:
    start, end = cfg["development"]["start"], lead_v3.DEV_END
    lines = [f"# Filter tests, {started:%Y-%m-%d}", "",
             f"Code {version}; research-app data fingerprint {fingerprint}; {len(rows)} tests; {resamples:,} resamples each.", "",
             "**What this asks.** Did a registered strategy do better or worse when a condition held at the signal? "
             "Each trade's *excess* is its gross return minus the mean of every trade of the same length and entry in the "
             f"window ({start} to {end}, Lead v3's development window). The *difference* is the mean excess of the trades "
             "where the condition held minus the rest, in basis points per trade, with a 90% interval and a two-sided p "
             "from resampling calendar quarters of trades. q corrects for every test in this run. 1993-2009 is computed "
             "once per test version and then read from `holdout_ledger.jsonl`, where the condition can be measured there.", "",
             "**Registered 2026-11-18 before any was run** (`backtester/splits.py`): ideas 7 (a gap up at the next open uses "
             "up the bounce) and 8 (trend and volatility) from the research app's idea ledger, plus the VIX curve, a release "
             "inside the trade, and a volatility-matched baseline from the 2026-11-17 audit.", "",
             "**How to read the labels.** *Supported difference* needs development p < 0.05, q < 0.10 and the same sign in "
             "1993-2009 with p < 0.10. *No meaningful difference*: the interval rules out a difference as large as the "
             "strategy's own mean excess. *Insufficient evidence*: the interval is too wide to say. Few trades make most "
             "splits wide: with about 100 trades a difference has to be well over 1 point per trade to show. None of these "
             "labels changes a trade verdict; a filter worth using becomes a new registered strategy version.", ""]
    if rows and rows[0]["label"] == PARTIAL:
        lines += ["**Partial run.** These are not the registered settings, so there are no q-values or labels and "
                  "1993-2009 was not evaluated (stored results are shown where they exist).", ""]
    lines += ["## Summary", "", "| Test | Strategy | Entry | Condition (trades) vs rest (trades) | Difference bp per trade (90% interval) "
              "| p | q | 1993-2009 difference bp (p) | Label |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] != "split":
            continue
        d, h = r["dev"], r["holdout"] or {}
        held = "no data" if r["holdout"] is None else ("too few" if h.get("status") != "ok" else f"{bp(h.get('diff'))} ({p_text(h.get('p'))})")
        lines.append(f"| {r['test']} | {r['symbol']} {r['signal']} | {MODE_LABELS[r['mode']]} | {r['group_label']} ({d.get('group', 0)}) "
                     f"vs {r['rest_label']} ({d.get('rest', 0)}) | {bp(d.get('diff'))} ({interval(d.get('ci90'))}) | "
                     f"{p_text(d.get('p'))} | {p_text(r['q'])} | {held} | {r['label']} |")
    lines += ["", "## Volatility-matched baseline", "",
              "Excess over trades of the same length and entry that started on a day in the same VIX bucket (below 15, 15-20, "
              "20-30, 30 and up), against the usual excess over all same-length trades. If the edge were only the higher "
              "returns of volatile markets, the matched excess would be near zero.", "",
              "| Strategy | Entry | Trades | Usual excess bp | Volatility-matched excess bp (90% interval) | p | q | 1993-2009 bp (p) | Label |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] != "baseline":
            continue
        d, h = r["dev"], r["holdout"] or {}
        held = "no data" if r["holdout"] is None else ("too few" if h.get("status") != "ok" else f"{bp(h.get('mean_excess'))} ({p_text(h.get('p'))})")
        lines.append(f"| {r['symbol']} {r['signal']} | {MODE_LABELS[r['mode']]} | {d.get('measured', d.get('trades', 0))} | "
                     f"{bp(d.get('v2_mean_excess'))} | {bp(d.get('mean_excess'))} ({interval(d.get('ci90'))}) | {p_text(d.get('p'))} | "
                     f"{p_text(r['q'])} | {held} | {r['label']} |")
    lines += ["", "## By bucket (development, descriptive)", ""]
    for r in rows:
        buckets = r["dev"].get("buckets") or []
        if r["kind"] != "split" or not buckets:
            continue
        lines += [f"**{r['test']}, {r['symbol']} {r['signal']} ({MODE_LABELS[r['mode']]})**", "",
                  "| Bucket | Trades | Mean excess bp |", "|---|---|---|"]
        lines += [f"| {b['label']} | {b['trades']} | {bp(b['mean_excess'])} |" for b in buckets] + [""]
    tally = pd.Series([r["label"] for r in rows]).value_counts()
    lines += ["## Tally", ""] + [f"- {k}: {v}" for k, v in tally.items()] + [
        "", "Limits: the four strategies share many signal days (most QQQ RSI(14) days are also Bollinger days), so their "
        "results are not independent. A split describes the past; acting on one needs a new registered strategy version, "
        "checked forward."]
    return "\n".join(lines) + "\n"


def export(rows, fingerprint, version, started, report_name, cfg) -> dict:
    return {"kind": "filter_tests", "schema": 1, "generated_at": started.isoformat(timespec="seconds"), "code": version,
            "data_fingerprint": fingerprint, "report": report_name,
            "development": {"start": cfg["development"]["start"], "end": lead_v3.DEV_END}, "parameters": splits.PARAMS,
            "tests": [{"test": r["test"], "version": r["version"], "kind": r["kind"], "strategy": r["strategy"],
                       "symbol": r["symbol"], "mode": r["mode"], "group_label": r["group_label"],
                       "group": r["dev"].get("group"), "rest": r["dev"].get("rest"),
                       "diff": r["dev"].get("diff", r["dev"].get("mean_excess")), "ci90": r["dev"].get("ci90"),
                       "p": r["dev"].get("p"), "q": r["q"], "label": r["label"],
                       "holdout": r["holdout"], "holdout_source": r["holdout_source"]} for r in rows]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resamples", type=int, default=splits.RESAMPLES)
    ap.add_argument("--seed", type=int, default=splits.SEED)
    args = ap.parse_args(argv)
    started = datetime.now(timezone.utc)
    cfg = data.config()
    registry.read(TRIALS)  # refuse to start on a broken record
    rules = lock.check()   # ... or on a rule changed under a recorded version
    ledger = HoldoutLedger(LEDGER)
    root, fingerprint = data.snapshot(data.research_root(cfg))
    version = code_version()
    rows = run(args.resamples, args.seed, cfg, root, ledger=ledger)
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / f"{runlog.report_stem('filter-tests', started)}.md"
    text = report(rows, cfg, fingerprint, version, started, args.resamples)
    registry.append(TRIALS, {"kind": "filter_tests", "run_at": started.isoformat(timespec="seconds"), "code": version,
                             "data": fingerprint, "settings": runlog.settings(cfg), "method": METHOD,
                             "rules": {k: v for k, v in rules.items() if k.startswith(("split:", "filters:"))},
                             "family": "registered" if is_registered(args.resamples, args.seed) else "partial",
                             "seed": args.seed, "resamples": args.resamples, "development_end": lead_v3.DEV_END,
                             "report": path.name,
                             "tests": [{"study": r["test"], "version": r["version"], "kind": r["kind"],
                                        "symbol": r["symbol"], "strategy": r["strategy"], "mode": r["mode"],
                                        "verdict": r["label"], "q": r["q"], "dev_p": r["dev"].get("p"),
                                        "dev_diff": r["dev"].get("diff", r["dev"].get("mean_excess")),
                                        "dev_ci90": r["dev"].get("ci90"), "dev_group": r["dev"].get("group"),
                                        "dev_rest": r["dev"].get("rest"),
                                        "holdout_diff": (r["holdout"] or {}).get("diff", (r["holdout"] or {}).get("mean_excess")),
                                        "holdout_p": (r["holdout"] or {}).get("p"), "holdout_source": r["holdout_source"]}
                                       for r in rows]})
    ledger.commit(started.isoformat(timespec="seconds"), version, fingerprint, args.seed, args.resamples)
    path.write_text(text, encoding="utf-8")
    path.with_suffix(".html").write_text(render(text, path.stem), encoding="utf-8")
    EXPORTS.mkdir(exist_ok=True)
    target = EXPORTS / "filter_tests.json"
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(export(rows, fingerprint, version, started, path.name, cfg), indent=1,
                              default=lambda x: x.item() if hasattr(x, "item") else str(x)), encoding="utf-8")
    tmp.replace(target)
    evidence.write(EXPORTS, data.research_root(cfg))
    print(f"Wrote {path} and exports/filter_tests.json ({len(rows)} tests; {registry.total_tests(TRIALS)} recorded in total).")
    for r in rows:
        if r["label"] in ("Supported difference", "Edge beyond volatility"):
            print(f"  {r['label']}: {r['test']} on {r['strategy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
