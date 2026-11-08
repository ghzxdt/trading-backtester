"""Simulate the registered trade rules (backtester/strategies.py) and compare them with two benchmarks.

    ..\\trading-research\\.venv\\Scripts\\python.exe -B run_trades.py

12 strategies (SPY/QQQ x 3 oversold signals x 2 exits), each priced four ways (ETF at the close, ETF at the next
open, Kalshi perp as maker or taker using the ETF as the price proxy), on the development period (2010 on) and the
untouched 1993-2009 holdout. Writes reports/<date>-trade-simulation.md and .html, exports/trade_simulation.json
(read by the research app's Daily thesis tab; ETF modes only), and appends the run to trials.jsonl.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from backtester import data, registry, simulate
from backtester.report_html import render
from backtester.strategies import EXITS, MODES, SIGNALS, SYMBOLS, signal_rule
from run_studies import code_version, period_mask

HERE = Path(__file__).resolve().parent
REPORTS = HERE / "reports"
EXPORTS = HERE / "exports"
TRIALS = HERE / "trials.jsonl"
MODE_LABELS = {"etf_close": "ETF at close", "etf_next_open": "ETF next open",
               "perp_maker": "Perp, maker", "perp_taker": "Perp, taker"}
THESIS_MODES = ("etf_close", "etf_next_open")  # user, 2026-11-08: the thesis shows ETFs only, no Kalshi


def buy_and_hold(frame, mask) -> dict:
    return simulate.summary(frame["close"].pct_change().fillna(0.0)[mask.to_numpy(bool)])


def run(draws: int, seed: int, cfg=None, root=None, symbols=SYMBOLS) -> tuple[list[dict], dict, dict]:
    cfg = cfg or data.config()
    root = root or data.research_root(cfg)
    rows, signal_days, full = [], {}, {}
    for symbol in symbols:
        frame = data.load(symbol, root)
        dev, hold = period_mask(frame.index, cfg["development"]), period_mask(frame.index, cfg["holdout"])
        full[symbol] = {"development": buy_and_hold(frame, dev),
                        "holdout": buy_and_hold(frame, hold) if hold.any() else None,
                        "holdout_start": f"{frame.index[hold.to_numpy()][0]:%Y-%m-%d}" if hold.any() else None}
        for name in SIGNALS:
            study = signal_rule(name)
            signal = study.rule(frame).fillna(False).astype(bool)
            signal_days[f"{symbol}:{name}"] = {"version": study.version, "description": study.description,
                                               "last_date": f"{frame.index[-1]:%Y-%m-%d}",
                                               "dates": [f"{d:%Y-%m-%d}" for d in frame.index[signal.to_numpy()]]}
            for ex in EXITS:
                for mode in MODES:
                    # one fresh generator per strategy: the three close-entry modes then share their random draws
                    dev_result = simulate.evaluate(frame, signal, ex.rule, dev, mode, cfg, draws,
                                                   np.random.default_rng(seed))
                    hold_result = (simulate.evaluate(frame, signal, ex.rule, hold, mode, cfg, draws,
                                                     np.random.default_rng(seed + 1)) if hold.any() else None)
                    rows.append({"symbol": symbol, "signal": name, "signal_version": study.version,
                                 "signal_description": study.description, "exit": ex.name,
                                 "exit_version": ex.version, "exit_description": ex.description, "mode": mode,
                                 "dev": dev_result, "holdout": hold_result,
                                 "verdict": simulate.verdict(dev_result, hold_result)})
    return rows, signal_days, full


def per_drawdown_note(result: dict | None) -> str:
    if result is None:
        return "no data"
    s, m = result["strategy"]["return_per_drawdown"], result["matched"]["return_per_drawdown"]
    if not (simulate.finite(s) and simulate.finite(m)):
        return "–"
    return f"{s:.2f} vs {m:.2f} ({'strategy' if s > m else 'buy-and-hold'})"


def pct(x, digits=1, sign=False):
    if not simulate.finite(x):
        return "–"
    return f"{x * 100:+.{digits}f}%" if sign else f"{x * 100:.{digits}f}%"


def bp(x):
    return "–" if not simulate.finite(x) else f"{x * 1e4:+.1f}"


def ratio(x):
    return "–" if not simulate.finite(x) else f"{x:.2f}"


def period_lines(label: str, results: list[dict | None]) -> list[str]:
    def cell(r, fn):
        return "no data" if r is None else fn(r)
    rows = [
        ("Trades", lambda r: str(r["trades"])),
        ("Time in market", lambda r: pct(r["exposure"], 0)),
        ("Win rate (after costs)", lambda r: pct(r.get("win_rate"), 0)),
        ("Mean per trade, gross / net bp", lambda r: f"{bp(r.get('mean_gross'))} / {bp(r.get('mean_net'))}"),
        ("Average win / loss", lambda r: f"{pct(r.get('avg_win'), 2, True)} / {pct(r.get('avg_loss'), 2, True)}"),
        ("Random-entry percentile", lambda r: "–" if r.get("random_percentile") is None else f"{r['random_percentile']:.0f}"),
        ("CAGR: strategy / matched buy-and-hold", lambda r: f"{pct(r['strategy']['cagr'], 2, True)} / {pct(r['matched']['cagr'], 2, True)}"),
        ("Max drawdown: strategy / matched", lambda r: f"{pct(r['strategy']['max_drawdown'], 1)} / {pct(r['matched']['max_drawdown'], 1)}"),
        ("CAGR per unit of drawdown: strategy / matched", lambda r: f"{ratio(r['strategy']['return_per_drawdown'])} / {ratio(r['matched']['return_per_drawdown'])}"),
    ]
    return [f"| **{label}** |" + " |" * len(results)] + [
        f"| {name} | " + " | ".join(cell(r, fn) for r in results) + " |" for name, fn in rows]


def report(rows, cfg, fingerprint, version, started, draws, full) -> str:
    fees = cfg["costs_round_trip_bps"]
    lines = [f"# Trade simulation, {started:%Y-%m-%d}", "",
             f"Code {version}; research-app data fingerprint {fingerprint}; {len(rows)} strategy x pricing results; "
             f"{draws} random-entry draws each.", "",
             "**What this is.** The oversold signals that were candidates in the indicator studies, turned into trades "
             "with fixed exits that were registered before this simulator existed (`backtester/strategies.py`). One "
             "position at a time, fully invested (1x) while in a trade, cash earns nothing in between. No stops: "
             "daily bars can't show whether a stop would have filled.", "",
             "**Pricing.** *ETF at close*: buy at the signal day's close. *ETF next open*: buy at the next morning's "
             f"open. Both pay {fees['etf']} bp per round trip. *Perp* columns price the same trades as a Kalshi perp "
             f"bought just after the close: {fees['kalshi_maker']} bp (maker) or {fees['kalshi_taker']} bp (taker) per "
             f"round trip plus {cfg['funding_bps_per_day']} bp of funding for every calendar day held through a 4 PM "
             "funding time. The perp columns use the ETF's adjusted price as a stand-in for the perp's price.", "",
             "**Benchmarks.** *Matched buy-and-hold* holds the same instrument every day at a fraction equal to the "
             "strategy's time in the market, so the comparison isn't flattered by holding less risk. *Random-entry "
             "percentile*: the strategy's average gross trade against 2,000 sets of random entry days with the same "
             "number of trades and the same holding lengths (95 means it beat 95% of them).", "",
             "**Verdicts** (registered 2026-11-08): *Lead* = random-entry percentile at least 95 in development and "
             "90 in the holdout, and a higher CAGR than matched buy-and-hold in both. *Timing edge only* = beats "
             "random entries in both periods, but not matched buy-and-hold. *Failed holdout* = passes development "
             "only. *No edge* = fails the random-entry test in development. *Too few trades* = under 20.", ""]
    order = list(MODES)
    lines += ["## Verdicts", "", "| Strategy | " + " | ".join(MODE_LABELS[m] for m in order) + " |",
              "|---|" + "---|" * len(order)]
    keys = list(dict.fromkeys((r["symbol"], r["signal"], r["exit"]) for r in rows))
    by_key = {(r["symbol"], r["signal"], r["exit"], r["mode"]): r for r in rows}
    for key in keys:
        lines.append(f"| {key[0]} {key[1]}, {key[2]} | " +
                     " | ".join(by_key[(*key, m)]["verdict"] for m in order) + " |")
    lines += ["", "## Return per unit of drawdown (descriptive, not part of the verdict)", "",
              "CAGR divided by the worst peak-to-trough loss, for the strategy versus exposure-matched buy-and-hold, "
              "ETF at the close. A strategy that is fully invested during its trades can earn more per year than the "
              "matched benchmark yet still have deeper drawdowns, because the benchmark spreads its smaller exposure "
              "over every day. The higher figure is named in brackets.", "",
              "| Strategy | Development | Holdout |", "|---|---|---|"]
    for key in keys:
        r = by_key[(*key, "etf_close")]
        lines.append(f"| {key[0]} {key[1]}, {key[2]} | {per_drawdown_note(r['dev'])} | {per_drawdown_note(r['holdout'])} |")
    lines += ["", "Full-time buy-and-hold at 1x, for reference:", "",
              "| Symbol | Development CAGR | Max drawdown | CAGR per drawdown | Holdout CAGR | Max drawdown | CAGR per drawdown |",
              "|---|---|---|---|---|---|---|"]
    for symbol, f in full.items():
        d, h = f["development"], f["holdout"] or {}
        lines.append(f"| {symbol} | {pct(d['cagr'], 2, True)} | {pct(d['max_drawdown'])} | {ratio(d['return_per_drawdown'])} | "
                     f"{pct(h.get('cagr'), 2, True)} | {pct(h.get('max_drawdown'))} | {ratio(h.get('return_per_drawdown'))} |")
    lines.append("")
    for key in keys:
        group = [by_key[(*key, m)] for m in order]
        first = group[0]
        lines += [f"## {key[0]}: {key[1]} ({first['signal_version']}), exit {key[2]} ({first['exit_version']})", "",
                  f"Signal: {first['signal_description']}. Exit: {first['exit_description']}.", "",
                  "| | " + " | ".join(MODE_LABELS[m] for m in order) + " |", "|---|" + "---|" * len(order)]
        lines += period_lines("Development (2010 on)", [r["dev"] for r in group])
        lines += period_lines("Holdout (1993-2009)", [r["holdout"] for r in group])
        lines += ["| **Verdict** | " + " | ".join(r["verdict"] for r in group) + " |", ""]
    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    lines += ["## Summary", ""] + [f"- {k}: {v}" for k, v in sorted(tally.items(), key=lambda kv: -kv[1])] + [
        "", "Limits: adjusted daily prices (dividends included), no slippage beyond the stated costs, no stops, no "
        "taxes, 1x only. A Lead is a rule worth watching forward, not proof of an edge; results at higher leverage "
        "scale both the gains and the drawdowns."]
    return "\n".join(lines) + "\n"


def compact(result: dict | None) -> dict | None:
    if result is None:
        return None
    keep = ("trades", "exposure", "win_rate", "mean_gross", "mean_net", "avg_win", "avg_loss", "mean_sessions",
            "random_percentile")
    return {**{k: result.get(k) for k in keep}, "strategy": result["strategy"], "matched": result["matched"]}


def export(rows, signal_days, cfg, fingerprint, version, started, report_name, full) -> dict:
    """Evidence for the research app's Daily thesis tab: ETF pricing only (no Kalshi in the thesis)."""
    return {"kind": "trade_simulation", "schema": 1, "generated_at": started.isoformat(timespec="seconds"),
            "code": version, "data_fingerprint": fingerprint, "report": report_name,
            "periods": {"development": cfg["development"], "holdout": cfg["holdout"]},
            "buy_and_hold": full,
            "costs_round_trip_bps": {"etf": cfg["costs_round_trip_bps"]["etf"]},
            "modes": list(THESIS_MODES),
            "strategies": [{"symbol": r["symbol"], "signal": r["signal"], "signal_version": r["signal_version"],
                            "signal_description": r["signal_description"], "exit": r["exit"],
                            "exit_version": r["exit_version"], "exit_description": r["exit_description"],
                            "mode": r["mode"], "verdict": r["verdict"], "development": compact(r["dev"]),
                            "holdout": compact(r["holdout"])} for r in rows if r["mode"] in THESIS_MODES],
            "signal_days": signal_days}


def write_json(path: Path, payload: dict):
    path.parent.mkdir(exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x)),
                   encoding="utf-8")
    tmp.replace(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args(argv)
    started = datetime.now(timezone.utc)
    cfg = data.config()
    root = data.research_root(cfg)
    rows, signal_days, full = run(args.draws, args.seed, cfg, root)
    fingerprint, version = data.fingerprint(root), code_version()
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / f"{started:%Y-%m-%d}-trade-simulation.md"
    text = report(rows, cfg, fingerprint, version, started, args.draws, full)
    path.write_text(text, encoding="utf-8")
    path.with_suffix(".html").write_text(render(text, path.stem), encoding="utf-8")
    write_json(EXPORTS / "trade_simulation.json",
               export(rows, signal_days, cfg, fingerprint, version, started, path.name, full))
    registry.append(TRIALS, {"kind": "trade_simulation", "run_at": started.isoformat(timespec="seconds"),
                             "code": version, "data": fingerprint, "seed": args.seed, "draws": args.draws,
                             "report": path.name,
                             "tests": [{"study": f"{r['signal']}+{r['exit']}", "version": f"{r['signal_version']}/{r['exit_version']}",
                                        "symbol": r["symbol"], "mode": r["mode"], "verdict": r["verdict"],
                                        "dev_trades": r["dev"]["trades"], "dev_mean_net": r["dev"].get("mean_net"),
                                        "dev_random_percentile": r["dev"].get("random_percentile"),
                                        "dev_cagr": r["dev"]["strategy"]["cagr"], "dev_matched_cagr": r["dev"]["matched"]["cagr"],
                                        "holdout_trades": (r["holdout"] or {}).get("trades"),
                                        "holdout_random_percentile": (r["holdout"] or {}).get("random_percentile")}
                                       for r in rows]})
    print(f"Wrote {path} and exports/trade_simulation.json ({len(rows)} results; "
          f"{registry.total_tests(TRIALS)} tests recorded in total).")
    for r in rows:
        if r["verdict"] == "Lead":
            print(f"  Lead: {r['symbol']} {r['signal']} + {r['exit']} ({MODE_LABELS[r['mode']]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
