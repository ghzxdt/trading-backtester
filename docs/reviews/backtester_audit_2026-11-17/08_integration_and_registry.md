# 8. How the two applications should work together

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Brief sections 10, 11 and 12;
deliverables 9 (capability matrix), 10 (technical integration proposal) and 11 (shared registry).

## 8.1 Cross-application capability matrix

| Capability | Research app ("the desk") | Backtester ("the lab") | Gap |
|---|---|---|---|
| Data collection | Yahoo daily and hourly bars, minute bars, Cboe VIX family, FRED, BLS, ALFRED, credit, earnings calendars, headlines, Kalshi, Cboe 0DTE, OCC volume | None; reads three of the desk's files | Lab cannot see most of what the desk holds |
| Point-in-time discipline | "Known at" tags, first-seen news, first-release macro, append-only logs | Snapshots, causal indicators, registration | Desk's state file is overwritten daily (no daily feature archive) |
| Descriptive history | Indexes tab studies (33 luck tests), regime base rates, hourly base rates | Event studies (90 tests) | Two engines, two methods, two test counts |
| Hypothesis testing with controls | Partial (luck tests, frozen paper experiment) | Strong (registration, holdout ledger, BH, v2) | Desk ideas reach the lab only by hand |
| Trade simulation | Frozen 4-rule experiment; intraday ORB baseline | 12 strategies x 4 pricings | Leveraged ETFs and the desk's day types not in the lab |
| Regime conditioning | Descriptive buckets declared 2026-11-08 | None | Lab cannot test the desk's regime claims |
| Event and catalyst data | Calendar since 2010, earnings, headlines | None | Event studies impossible in the lab today |
| Live monitoring | Daily thesis, trigger levels, pre-close check, paper book, stance log | None | - (correct split of roles) |
| Forward records | Stance log, paper events, calls, journal, ideas, pre-close | Trial record (backtests only) | Lab does not report forward trades separately |
| Idea registry | Idea ledger (11 ideas, stages) | Catalog + lock + trial record | Two registries, linked only by free-text references |
| Risk view | Loss scenarios by leverage, adverse-move tables | Equity drawdown | No per-trade MAE anywhere; no leveraged pricing in the lab |
| Evidence hand-off | Reads `exports/trade_simulation.json` (schema 1), validates it, cross-checks fired dates | Writes it | One file, three rules; no per-hypothesis evidence card |

## 8.2 Technical findings that shape the integration

| Topic | Finding |
|---|---|
| Stacks | Both Python 3.12 + pandas/numpy, one virtual environment (the desk's). Desk: local HTTP server on 127.0.0.1:8766 with static pages filled from JSON state, Tk control panel. Lab: Tk window, scripts |
| Storage | CSV caches and JSONL logs, several hash-chained. No database in either app |
| APIs | Desk: `/api/v1/...` for thesis notes, calls, ideas, live refresh (localhost only, write routes require an `X-Hub` header). Lab: none |
| Ingestion | Desk downloads on schedule (evening refresh, intraday collection, snapshots) when the laptop is awake; lab reads the desk's files and snapshots them |
| Identifiers | Plain tickers in both; desk's universe is wider (16 intraday instruments; Kalshi tickers) |
| Timestamps | Daily bars by exchange date; desk logs carry UTC and ET; hourly bars ET with offset; minute bars with receipt times. The computer's clock is Central |
| Frequency | Lab daily only; desk daily, hourly, minute, snapshots |
| Indicator definitions | RSI and the lower band are written twice, identically; the desk checks every fired date against the export (807 matched on 2026-11-17). Exits are also written twice (paper book) |
| Price basis | Daily bars adjusted (both); hourly bars and live quotes as traded. Mixed bases matter on ex-dividend days |
| Licensing | Yahoo (personal research use), Cboe public files, FRED (terms accepted by the user; key in `.secrets`), BLS API, SqueezeMetrics GEX/DIX (manual download only, their terms bar automated retrieval), Kalshi public endpoints. Nothing redistributes data |
| Rate limits and retention | Yahoo minute bars kept 5 days and hourly about 730 days by the source, so the desk's own archive is the only history; Cboe posts the VIX close late in the evening; Kalshi serves no historical spreads |
| Local vs cloud | Both local, both pushed to private GitHub repos; data caches and snapshots are not on GitHub; backups by hand |
| Security | Desk binds to localhost; FRED key outside `data/` and git; no broker integration; no trading endpoints |
| Operations | Daytime jobs depend on the laptop being asleep or on; 4 paper-decision days were missed (Nov 9-11, 16) |

## 8.3 Architecture options compared

| Option | Complexity | Reliability | Maintainability | Cost | Reproducibility | Fits today's apps | Research value |
|---|---|---|---|---|---|---|---|
| A. Manual export/import (today) | None | Good | Good | 0 | Good | Yes | Low: one export, three rules |
| B. **Standardised files, both directions** (hypothesis requests from the desk's idea ledger; evidence cards from the lab) | Low-medium | High | High | 0 | High | Yes: extends the existing file contract | **High** |
| C. Shared database | Medium | Medium (one store, locking, migrations) | Medium | 0 | Lower unless versioned | Breaks the append-only, hash-chained logs and the read-only rule | Medium |
| D. Shared market-data layer (one module both import) | Medium | Medium | Medium | 0 | Good | Couples release cycles; the desk's frozen experiments forbid casual changes | Medium |
| E. API between the apps | Medium | Lower (lab would need a server; laptop sleeps) | Medium | 0 | Medium | No: the desk must never depend on the lab | Low extra |
| F. Common signal engine (declarative rule specs) | Medium | High | High | 0 | High | Yes, if introduced as a new file schema | High: ends the double coding |
| G. Separate validation service | High | Medium | Low | Hosting | Medium | No | Low extra |
| H. Merge into one app | High | Lower for the desk's records | Low | 0 | Risky | No: every experiment would touch the app holding the frozen logs | Negative |

**Recommendation: B, then F.** Keep two apps and the current direction rules (the lab reads the desk's files; the desk
reads the lab's export and never needs the lab to run). Extend the file contract both ways, then make rule
definitions declarative so a rule is written once.

## 8.4 The proposed information exchange

### Desk to lab: hypothesis requests
The desk already has the right place: the Idea ledger (`data/thesis/ideas.jsonl`, append-only, hash-chained, with
stages). Add structured fields to its "create" and "update" events (new schema version; old events stay valid):

```json
{
  "schema": 2, "type": "create", "id": 17,
  "title": "Oversold bounce after a large gap up does worse",
  "claim": "...", "route": "A",
  "observation": {"date": "2026-11-17", "journal_note": 3, "snapshot_sha256": "..."},
  "instruments": ["QQQ"], "direction": "long",
  "rule": {"kind": "split", "base": "bollinger_lower_close@v1+close_above_sma5@v1",
           "by": "gap_next_open", "buckets": [-0.005, 0.005, 0.015]},
  "decision_time": "next_open", "horizon_sessions": [1, 10],
  "expected": {"sign": "lower excess in the top bucket", "size_bp": 50},
  "benchmark": "unsplit rule",
  "confirm": "...", "invalidate": "...",
  "data_needed": ["etfs_long.csv"]
}
```

The lab reads `ideas.jsonl` read-only, lists ideas at stage "registered" whose rule it does not yet have, and prints
them in its app ("Ideas waiting for registration"). A human still writes the code and the lock entry; the lab records
`idea_id` with every registered study, strategy and run.

### Lab to desk: evidence cards
Keep `exports/trade_simulation.json` schema 1 exactly (the desk reads it), and add a second file,
`exports/evidence.json` (schema 1 of a new kind), one card per registered rule or split:

```json
{
  "kind": "evidence", "schema": 1, "generated_at": "...", "code": "...", "data_fingerprint": "...",
  "cards": [{
    "idea_id": 1, "rule": "QQQ bollinger_lower_close@v1 + close_above_sma5@v1", "entry": "etf_next_open",
    "verdict": "Lead", "verdict_version": "v2", "verdict_changed_since": null,
    "registered": "2026-11-08", "development": {"start": "2010-01-01", "end": "2026-11-08"},
    "occurrence": {"signals_per_year": 12.5, "trades_per_year": 6.2, "last_fired": "2026-11-06"},
    "trades": 104, "quarters": 49,
    "excess_bp": {"mean": 59.6, "ci90": [null, null]}, "p": 0.011, "q": 0.032,
    "distribution_bp": {"p10": null, "median": null, "p90": null},
    "mae_pct": {"median": -1.43, "p10": -5.50, "worst": -19.73},
    "holdout": {"excess_bp": 144.1, "p": 0.0006, "independent": false},
    "forward": {"since": "2026-11-08", "trades": 0, "mean_excess_bp": null, "band": {"lower_bp_at_n": "m - 2 s / sqrt(n)"},
                "status": "no forward trades yet"},
    "regimes": "not tested", "conditions_failed_in": "not tested",
    "costs_bp_at": {"2": 78.9, "5": 75.9, "10": 70.8, "20": 60.7},
    "limitations": ["chosen partly on 1993-2009", "77% of RSI(14) days overlap", "no stops; 1x only"],
    "report": "reports/....md", "trade_list": "exports/trades/....csv", "evidence_age_days": 0
  }]
}
```
(Values shown are today's development figures where known; nulls are fields the lab does not compute yet.)

The desk shows a card's occurrence, interval, worst case, forward status and limitations beside the stance, and
caps how the card can be worded: "historical tendency, n trades, interval", never "probability of success".

### What can be done by hand today
- Desk to lab: write the idea in the ledger; register the rule in the lab; quote the commit in a ledger update.
- Lab to desk: the trade report, the trade list and the export; the ledger's "evidence reference" field.
- Rule changes: by version in the lab; the desk's date cross-check catches drift for the three registered rules only.

### What needs code
Structured idea fields (desk); an idea reader (lab); the evidence file (lab); evidence cards on the Daily thesis
(desk); declarative rules (both, option F); a daily feature archive (desk).

## 8.5 A shared hypothesis and edge registry

### Where it lives
In the desk's Idea ledger, extended, because it is already append-only, hash-chained, visible on the Daily thesis
and owned by the user's daily process. The lab keeps its own record of *how* each test was run (catalog, lock, trial
record, holdout ledger) and links to ideas by `idea_id`. One registry of ideas, one record of tests: no shared
database, no shared writer.

### Entry fields (the brief's list, mapped)

| Field | Where it lives |
|---|---|
| Unique identifier; date created | Ledger `id`, `recorded_utc` (exists) |
| Original observation | Ledger `observation` (new): date, journal note id, page snapshot hash |
| Reasoning | Ledger `claim` (exists) plus `mechanism` (new) |
| Applicable tickers; data sources | `instruments`, `data_needed` (new) |
| Required market conditions; exact signal | `rule` (new, structured; later a declarative spec) |
| Expected outcome; time horizon | `expected`, `horizon_sessions`, `decision_time` (new) |
| Backtest configuration; dataset and strategy versions | Lab trial record: code, data fingerprint, rule fingerprints, seed, draws; cited in an update event |
| Historical results; out-of-sample results | Evidence card (lab) cited by an update event |
| Forward-testing results | Desk stance log, paper book, pre-close log; summarised in the card's `forward` block |
| Known limitations | Card `limitations`; ledger `result` text |
| Confirmation requirements; invalidation criteria | `confirm`, `invalidate` (new) |
| Validation status; date last evaluated | Ledger `stage` (extended, below); latest update's date |
| Research-app monitoring requirements | `monitor` (new): which levels or conditions the desk should watch and show |

### Lifecycle
The ledger's stages today: idea, registered, backtested, forward, kept, dropped. Proposed, keeping the old names valid:

| Stage | Entry condition | Who moves it | Exit |
|---|---|---|---|
| Observation | A journal note or a seen pattern | User | Written as a falsifiable claim |
| Hypothesis | Claim, mechanism, expected outcome, invalidation written | User | Rule written precisely |
| Initial investigation | Registered in the lab; first study run | Lab run + user | Drop if nothing in development; else simulate |
| Historical testing | Registered trade simulation; verdict | Lab | Lead or not |
| Robustness testing | Neighbourhood, regimes, instruments, costs, MAE | Lab | Robust enough to forward test, or drop |
| Forward testing | Forward band set; signals logged before entry | Desk logs, lab cards | Consistent after the planned number of trades |
| Evidence-supported monitoring | Forward consistent; used in decisions | Both | Deteriorating |
| Deteriorating evidence | Forward below its band, or the mechanism changed | Lab flags, user confirms | Back to monitoring, or retired |
| Rejected / retired | Failed a registered test, or retired after deterioration | User | Stays in the registry permanently |

Rejected and retired ideas never leave the ledger. Before testing a new idea, search the ledger for the same claim;
the ledger's count of tested ideas sits beside every result.

### Monitoring and reassessment
- **Desk, daily:** for each idea in forward testing or monitoring, show its live condition (fired, trigger distance,
  open trade and exit level), and log signals before entry.
- **Lab, weekly:** recompute cards with the development window frozen; add forward trades to the forward block;
  report any verdict or forward-status change in the weekly log and in the evidence file.
- **User, quarterly:** read every card in forward testing, monitoring or deteriorating; decide moves; record them.
