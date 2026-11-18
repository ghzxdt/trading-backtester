"""Evidence cards for the research app: exports/evidence.json (added 2026-11-18).

One card per registered strategy and ETF entry, built from the latest trade-simulation export and, when present, the
latest filter-test export. A card says what the evidence is, not only its label: how often the rule fires, the excess
with its 90% interval, the trade distribution, the worst point inside trades, cost sensitivity, 1993-2009, the forward
record, the leveraged-ETF version, the filter tests, and the known limits.

The research app does not need this file: its Daily thesis reads exports/trade_simulation.json (schema 1, unchanged).
This is the file a later version of that page can show beside each rule.

Ideas: the research app's idea ledger (data/thesis/ideas.jsonl) is read, never written, to show each linked idea's title
and current stage. The links are kept here because the ledger has no structured rule fields yet.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from . import lead_v3, splits

SCHEMA = 1
# Research-app idea id -> what in this app tests it.
IDEA_LINKS = {1: "next-open pricing of the oversold rules", 2: "closing-price pricing of the oversold rules",
              7: "filter test gap_at_next_open", 8: "filter tests spy_200d_trend and vix_level",
              11: "leveraged-ETF pricing (TQQQ, UPRO)"}


def read_ideas(research_root: Path | None) -> dict[int, dict]:
    """Title and latest stage of each idea in the research app's ledger, replayed from its events (read-only)."""
    path = Path(research_root) / "data" / "thesis" / "ideas.jsonl" if research_root else None
    if path is None or not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
            idea = int(event.get("idea"))
        except (ValueError, TypeError):
            continue
        if event.get("type") == "create":
            out[idea] = {"title": event.get("title"), "stage": event.get("stage"), "updated": event.get("recorded_et")}
        elif event.get("type") == "update" and idea in out:
            if event.get("stage"):
                out[idea]["stage"] = event["stage"]
            out[idea]["updated"] = event.get("recorded_et")
    return out


def _limitations(row: dict) -> list[str]:
    dev = row.get("development") or {}
    risk, v2 = dev.get("risk") or {}, dev.get("v2") or {}
    out = ["1993-2009 helped choose this signal (2026-11-08), so it can remove a Lead but cannot confirm one.",
           "Daily bars: no stops are simulated, and a day's high and low are not ordered."]
    if dev.get("trades") is not None and dev["trades"] < 30:
        out.append(f"Only {dev['trades']} development trades.")
    if (v2.get("top5_share") or 0) > 0.5:
        out.append("More than half of the gross profit came from 5 trades.")
    if risk.get("mae_worst") is not None and risk["mae_worst"] < -0.10:
        out.append(f"Worst point inside a trade: {risk['mae_worst']:.1%} at 1x.")
    if row["mode"] == "etf_close":
        out.append("Needs a market-on-close order placed on an estimate of the close (about 3:50 PM ET).")
    if row["exit"] == "close_above_sma5":
        out.append("The exit decides at a close and sells at that close; the card shows the result if sold at the next "
                   "open instead.")
    if (row.get("forward") or {}).get("status") in (None, "none yet", "too few"):
        out.append("No forward evidence yet (trades signalled after the development window).")
    return out


def build(trades: dict, filters: dict | None, ideas: dict[int, dict]) -> dict:
    start = pd.Timestamp(trades["periods"]["development"]["start"])
    end = pd.Timestamp(trades.get("development_end") or lead_v3.DEV_END)
    years = max((end - start).days / 365.25, 1e-9)
    filter_tests = (filters or {}).get("tests") or []
    cards = []
    for row in trades["strategies"]:
        dev, hold = row.get("development") or {}, row.get("holdout") or {}
        v2, risk, hold_v2 = dev.get("v2") or {}, dev.get("risk") or {}, hold.get("v2") or {}
        dates = pd.to_datetime((trades["signal_days"].get(f"{row['symbol']}:{row['signal']}") or {}).get("dates", []))
        key = splits.strategy_key((row["symbol"], row["signal"], row["exit"], row["mode"]))
        linked = [1 if row["mode"] == "etf_next_open" else 2, 11]
        mine = [t for t in filter_tests if t.get("strategy") == key]
        linked += [7, 8] if mine else []
        cards.append({
            "strategy": key, "symbol": row["symbol"], "signal": f"{row['signal']}@{row['signal_version']}",
            "exit": f"{row['exit']}@{row['exit_version']}", "entry": row["mode"],
            "description": f"{row['signal_description']}. Exit: {row['exit_description']}.",
            "verdict": row["verdict"], "verdict_version": trades.get("verdict_version"),
            "verdict_v2_to_date": row.get("verdict_v2"), "verdict_v1": row.get("verdict_v1"),
            "development": {"start": f"{start:%Y-%m-%d}", "end": f"{end:%Y-%m-%d}"},
            "occurrence": {"signal_days_per_year": round(int(((dates >= start) & (dates <= end)).sum()) / years, 2),
                           "trades_per_year": round((dev.get("trades") or 0) / years, 2),
                           "last_fired": f"{dates.max():%Y-%m-%d}" if len(dates) else None},
            "trades": dev.get("trades"), "quarters": v2.get("quarters"), "win_rate": dev.get("win_rate"),
            "mean_net": dev.get("mean_net"), "excess": v2.get("mean_excess"), "excess_ci90": v2.get("ci90"),
            "p": v2.get("p"), "q": row.get("q"), "best5_share": v2.get("top5_share"),
            "net_distribution": {k: risk.get(k) for k in ("net_p10", "median_net", "net_p90", "worst_net", "best_net")},
            "inside_trades": {k: risk.get(k) for k in ("mae_median", "mae_p10", "mae_worst", "trades_mae_below_5pct",
                                                       "trades_mae_below_10pct", "mfe_median")},
            "mean_net_without_best3": risk.get("mean_net_without_best3"), "profit_factor": risk.get("profit_factor"),
            "mean_net_at_cost_bp": risk.get("mean_net_at_cost_bp"),
            "mean_gross_if_sold_next_open": risk.get("mean_gross_exit_next_open"),
            "holdout": {"trades": hold.get("trades"), "excess": hold_v2.get("mean_excess"), "p": hold_v2.get("p"),
                        "independent": False} if hold else None,
            "forward": row.get("forward"), "leveraged": row.get("leveraged"),
            "filters": [{k: t.get(k) for k in ("test", "label", "group_label", "group", "rest", "diff", "ci90", "p", "q")}
                        for t in mine],
            "ideas": [{"id": i, "tests": IDEA_LINKS.get(i), **(ideas.get(i) or {})} for i in sorted(set(linked))],
            "limitations": _limitations(row),
        })
    return {"kind": "evidence", "schema": SCHEMA, "generated_from": {
                "trade_simulation": {"generated_at": trades.get("generated_at"), "report": trades.get("report"),
                                     "code": trades.get("code"), "data_fingerprint": trades.get("data_fingerprint")},
                "filter_tests": None if not filters else {"generated_at": filters.get("generated_at"),
                                                          "report": filters.get("report"), "code": filters.get("code")}},
            "data_through": trades.get("data_through"), "trade_list": trades.get("trade_list"),
            "wording": "Historical tendencies with their sample sizes and intervals, not probabilities of success.",
            "cards": cards}


def write(exports: Path, research_root: Path | None) -> Path | None:
    """Rebuild exports/evidence.json from the exports on disk. Returns its path, or None without a trade export."""
    exports = Path(exports)
    source = exports / "trade_simulation.json"
    if not source.exists():
        return None
    trades = json.loads(source.read_text(encoding="utf-8"))
    if trades.get("verdict_version") != lead_v3.VERSION:
        return None  # an export from before v3 lacks the fields a card needs
    filters_path = exports / "filter_tests.json"
    filters = json.loads(filters_path.read_text(encoding="utf-8")) if filters_path.exists() else None
    payload = build(trades, filters, read_ideas(research_root))
    target = exports / "evidence.json"
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x)),
                   encoding="utf-8")
    tmp.replace(target)
    return target
