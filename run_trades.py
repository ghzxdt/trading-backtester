"""Simulate the registered trade rules (backtester/strategies.py) and compare them with two benchmarks.

    ..\\trading-research\\.venv\\Scripts\\python.exe -B run_trades.py

12 strategies (SPY/QQQ x 3 oversold signals x 2 exits), each priced four ways (ETF at the close, ETF at the next
open, Kalshi perp as maker or taker using the ETF as the price proxy), on the development period (2010 on) and the
1993-2009 holdout. Writes reports/<date-time>-trade-simulation.md and .html, exports/trade_simulation.json
(read by the research app's Daily thesis tab; ETF modes only), the list of every simulated trade
(exports/trades/<date-time>-trade-simulation.csv), and appends the run to trials.jsonl.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from backtester import data, lock, registry, runlog, simulate, strategies
from backtester.ledger import HoldoutLedger, holdout_result, rng_for
from backtester.report_html import render
from backtester.strategies import EXITS, MODES, SIGNALS, SYMBOLS, signal_rule
from run_studies import METHOD, code_version, period_mask

HERE = Path(__file__).resolve().parent
REPORTS = HERE / "reports"
EXPORTS = HERE / "exports"
TRIALS = HERE / "trials.jsonl"
LEDGER = HERE / "holdout_ledger.jsonl"
MODE_LABELS = {"etf_close": "ETF at close", "etf_next_open": "ETF next open",
               "perp_maker": "Perp, maker", "perp_taker": "Perp, taker"}
THESIS_MODES = ("etf_close", "etf_next_open")  # user, 2026-11-08: the thesis shows ETFs only, no Kalshi


def buy_and_hold(frame, mask) -> dict:
    return simulate.summary(frame["close"].pct_change().fillna(0.0)[mask.to_numpy(bool)])


def is_registered(symbols, draws, seed) -> bool:
    return (tuple(symbols), draws, seed) == (SYMBOLS, strategies.DRAWS, strategies.SEED)


def run(draws: int, seed: int, cfg=None, root=None, symbols=SYMBOLS,
        ledger: HoldoutLedger | None = None) -> tuple[list[dict], dict, dict, pd.DataFrame]:
    """`ledger=None` computes the holdout in memory and stores nothing (tests and rebuild checks)."""
    cfg = cfg or data.config()
    root = root or data.research_root(cfg)
    registered = is_registered(symbols, draws, seed)
    rows, signal_days, full, lists = [], {}, {}, []
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
                    # One random stream per test. The three close-entry modes are the same test of the same
                    # gross trades, so they share a stream; the next-open entry has its own.
                    entry = "next_open" if mode == "etf_next_open" else "close"
                    who = (name, study.version, ex.name, ex.version, symbol, entry)
                    result, source = {}, None
                    for period, mask in (("development", dev), ("holdout", hold)):
                        if not mask.any():
                            result[period] = None
                            continue
                        # The trade list is rebuilt every run (it involves no test); only the holdout's
                        # statistics are read from the ledger.
                        trades = simulate.find_trades(frame, signal, ex.rule, mask)
                        priced = simulate.price_trades(frame, trades, mode, cfg)
                        lists.append(priced.assign(symbol=symbol, signal=name, signal_version=study.version,
                                                   exit=ex.name, exit_version=ex.version, pricing=mode, period=period))

                        def compute(mask=mask, period=period, trades=trades, priced=priced):
                            return simulate.evaluate(frame, signal, ex.rule, mask, mode, cfg, draws,
                                                     rng_for(seed, *who, period), trades, priced)
                        if period == "development":
                            result[period] = compute()
                        else:
                            key = f"trade|{name}@{study.version}+{ex.name}@{ex.version}|{symbol}|{mode}"
                            result[period], source = holdout_result(ledger, registered, key, True, compute)
                    dev_result, hold_result = result["development"], result["holdout"]
                    rows.append({"symbol": symbol, "signal": name, "signal_version": study.version,
                                 "signal_description": study.description, "exit": ex.name,
                                 "exit_version": ex.version, "exit_description": ex.description, "mode": mode,
                                 "dev": dev_result, "holdout": hold_result, "holdout_source": source,
                                 "verdict": simulate.verdict(dev_result, hold_result)})
    return rows, signal_days, full, trade_list(lists)


TRADE_COLUMNS = ["symbol", "signal", "signal_version", "exit", "exit_version", "pricing", "period", "signal_day",
                 "entry_day", "entry_price", "exit_day", "exit_price", "sessions", "gross", "cost", "net"]


def trade_list(lists: list[pd.DataFrame]) -> pd.DataFrame:
    """Every simulated trade, one row each. Prices are the adjusted prices the simulation used (dividends
    included), so they differ from the prices quoted on the day; returns are fractions (0.01 = 1%)."""
    if not lists:
        return pd.DataFrame(columns=TRADE_COLUMNS)
    table = pd.concat(lists, ignore_index=True)[TRADE_COLUMNS]
    for column in ("signal_day", "entry_day", "exit_day"):
        table[column] = pd.to_datetime(table[column]).dt.strftime("%Y-%m-%d")
    return table.round({"entry_price": 4, "exit_price": 4, "gross": 6, "cost": 6, "net": 6})


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


def report(rows, cfg, fingerprint, version, started, draws, full, trades_file: str | None = None) -> str:
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
    if trades_file:
        lines += ["", f"Every simulated trade is listed in `{trades_file}` (one row per trade and pricing; adjusted "
                  "prices, returns as fractions)."]
    return "\n".join(lines) + "\n"


def compact(result: dict | None) -> dict | None:
    if result is None:
        return None
    keep = ("trades", "exposure", "win_rate", "mean_gross", "mean_net", "avg_win", "avg_loss", "mean_sessions",
            "random_percentile")
    return {**{k: result.get(k) for k in keep}, "strategy": result["strategy"], "matched": result["matched"]}


VERDICT_DEFINITION = ("v1, registered 2026-11-08. Lead: the mean gross trade beats at least 95% of random same-length "
                      "entries in development and 90% in the 1993-2009 period, and CAGR is above buy-and-hold held at "
                      "the strategy's time in the market in both. The 1993-2009 period also helped choose these "
                      "signals, so it is not independent confirmation.")


def export(rows, signal_days, cfg, fingerprint, version, started, report_name, full, run_info: dict | None = None) -> dict:
    """Evidence for the research app's Daily thesis tab: ETF pricing only (no Kalshi in the thesis).

    Schema 1 is unchanged for the reader; the fields from "verdict_definition" down were added 2026-11-13."""
    return {"kind": "trade_simulation", "schema": 1, "generated_at": started.isoformat(timespec="seconds"),
            "code": version, "data_fingerprint": fingerprint, "report": report_name,
            "verdict_definition": VERDICT_DEFINITION,
            "data_through": {key.split(":")[0]: value["last_date"] for key, value in signal_days.items()},
            "entry_notes": {"etf_close": "Needs the order in before the close, on an estimate of that close's signal.",
                            "etf_next_open": "Signal known after the close; bought at the next session's open."},
            **(run_info or {}),
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
    ap.add_argument("--draws", type=int, default=strategies.DRAWS)
    ap.add_argument("--seed", type=int, default=strategies.SEED)
    args = ap.parse_args(argv)
    started = datetime.now(timezone.utc)
    cfg = data.config()
    registry.read(TRIALS)  # refuse to start on a broken record
    rules = lock.check()   # ... or on a rule changed under a recorded version
    ledger = HoldoutLedger(LEDGER)
    root, fingerprint = data.snapshot(data.research_root(cfg))  # the run reads this copy, which stays on disk
    version = code_version()
    rows, signal_days, full, trades = run(args.draws, args.seed, cfg, root, ledger=ledger)
    REPORTS.mkdir(exist_ok=True)
    stem = runlog.report_stem("trade-simulation", started)
    path, trades_path = REPORTS / f"{stem}.md", EXPORTS / "trades" / f"{stem}.csv"
    trades_name = trades_path.relative_to(HERE).as_posix()
    text = report(rows, cfg, fingerprint, version, started, args.draws, full, trades_name)
    # The record goes first: if it can't be written (a broken chain), no report or export appears without one.
    registry.append(TRIALS, {"kind": "trade_simulation", "run_at": started.isoformat(timespec="seconds"),
                             "code": version, "data": fingerprint, "settings": runlog.settings(cfg),
                             "method": METHOD, "rules": rules,
                             "family": "registered" if is_registered(SYMBOLS, args.draws, args.seed) else "unregistered settings",
                             "seed": args.seed, "draws": args.draws,
                             "report": path.name, "trade_list": trades_name,
                             "tests": [{"study": f"{r['signal']}+{r['exit']}", "version": f"{r['signal_version']}/{r['exit_version']}",
                                        "symbol": r["symbol"], "mode": r["mode"], "verdict": r["verdict"],
                                        "holdout_source": r.get("holdout_source"),
                                        "dev_trades": r["dev"]["trades"], "dev_mean_net": r["dev"].get("mean_net"),
                                        "dev_random_percentile": r["dev"].get("random_percentile"),
                                        "dev_cagr": r["dev"]["strategy"]["cagr"], "dev_matched_cagr": r["dev"]["matched"]["cagr"],
                                        "holdout_trades": (r["holdout"] or {}).get("trades"),
                                        "holdout_random_percentile": (r["holdout"] or {}).get("random_percentile")}
                                       for r in rows]})
    ledger.commit(started.isoformat(timespec="seconds"), version, fingerprint, args.seed, args.draws)
    path.write_text(text, encoding="utf-8")
    path.with_suffix(".html").write_text(render(text, path.stem), encoding="utf-8")
    trades_path.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(trades_path, index=False, lineterminator="\n")
    write_json(EXPORTS / "trade_simulation.json",
               export(rows, signal_days, cfg, fingerprint, version, started, path.name, full,
                      {"seed": args.seed, "draws": args.draws, "settings": runlog.settings(cfg),
                       "trade_list": trades_name}))
    print(f"Wrote {path}, {trades_name} ({len(trades)} trades) and exports/trade_simulation.json ({len(rows)} results; "
          f"{registry.total_tests(TRIALS)} tests recorded in total).")
    for r in rows:
        if r["verdict"] == "Lead":
            print(f"  Lead: {r['symbol']} {r['signal']} + {r['exit']} ({MODE_LABELS[r['mode']]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
