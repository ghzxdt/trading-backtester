# 11. Prioritised roadmap and developer hand-off

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Brief section 15; deliverables 14
and 15. Each recommendation answers a limitation found in this review; none is proposed for sophistication's sake.

## 11.1 Recommendations by class

### Critical correctness fixes

**C1. Freeze the development window per verdict version, and report forward trades separately.**
- *Benefit:* verdicts stop drifting with each weekly run; post-registration trades become clean forward evidence;
  deterioration becomes measurable. *Data:* none new. *Depends on:* nothing.
- *Complexity:* low-medium (a new verdict version, Lead v3: v2's statistics with the development end fixed at
  2026-11-13, plus a forward block). Must be registered and committed before it runs on real prices (project rule).
- *Limits:* forward samples stay small for years ([06 section 6.3](06_validation_framework.md)).
- *Objective:* the only route to "monitoring whether edges deteriorate".

**C2. Report verdict changes.**
- *Benefit:* a Lead appearing or disappearing becomes visible before the desk acts on it. *Data:* the trial record.
- *Complexity:* low. *Limits:* none. *Objective:* trust in the hand-off.

**C3. Report intra-trade risk (MAE, worst trade, median, profit factor, mean without the best three, by-year table).**
- *Benefit:* replaces the misleading picture given by win rate and equity drawdown (QQQ RSI(14): 26 closed trades no
  worse than -1.6%, intra-trade lows down to -11.7%). *Data:* daily highs and lows, already held.
- *Complexity:* low; descriptive only, so no verdict version is needed. *Limits:* daily bars do not order the high
  and low within a day. *Objective:* risk evaluation; a prerequisite for any leveraged use.

### High-value improvements to existing functionality

| ID | Recommendation | Benefit | Data | Depends on | Complexity | Limits |
|---|---|---|---|---|---|---|
| H1 | Confidence intervals for every excess (cluster resampling) and the per-trade distribution | Effect sizes with uncertainty instead of p alone | None new | - | Low | Rough with few clusters |
| H2 | Registered splits and filters with a nested comparison (rule vs rule + filter) | Tests ideas 7 and 8, information value, "when does the setup fail" | VIX (held); VIX3M, credit, events (H3) | H1, H3 | Medium | Small samples on rare rules |
| H3 | Read more of the desk's files: VIX3M, VIX9D, Baa-10y, events calendar, FRED market series; multi-symbol conditions (RSP, SPY, QQQ, IWM together) | Lets the lab test the desk's regime, breadth, event and credit information | Desk files, read-only, in the snapshot | - | Medium | FRED dates need a one-day lag; revised series need vintages |
| H4 | Leveraged-ETF pricing (QQQ signals traded in TQQQ, SPY in UPRO) with MAE | The instrument actually used for leverage; prerequisite for any leveraged decision | TQQQ, UPRO daily since 2010 (held) | C3 | Low-medium | No 1993-2009 history |
| H5 | Exit decided only on information available before it: a next-open variant of the 5-day-average exit (new exit version) | Honest execution; measured impact small (-7 to +7 bp) | None | - | Low | - |
| H6 | Cost-sensitivity line (2/5/10/20 bp) per strategy | Shows how much cost the edge can carry | None | - | Low | - |
| H7 | Volatility-matched baseline (same-VIX-bucket days), registered as a benchmark version | Separates timing from a volatility premium; answers "beyond what price action reveals" | VIX (held) | H2 | Low-medium | Must be registered before looking |
| H8 | Neighbourhood report: pre-declared parameter neighbours, development only, labelled exploratory, recorded as partial | Shows whether a result is a knife edge | None | - | Low | Must never be used to pick a new parameter |
| H9 | IWM history from 2000 in the desk's download (desk change) | Gives IWM a 1993-2009-style check | Yahoo | Desk chat | Low | Desk-side change |

### Essential integration requirements

| ID | Requirement | Benefit | Complexity | Notes |
|---|---|---|---|---|
| I1 | `exports/evidence.json`: one evidence card per registered rule (occurrence, interval, distribution, MAE, holdout, forward status and band, cost line, limitations, freshness, links) | The desk can show what the evidence is, not just a label | Medium | Schema in [08 section 8.4](08_integration_and_registry.md); keep `trade_simulation.json` schema 1 untouched |
| I2 | Structured idea fields in the desk's Idea ledger (schema 2) and an idea reader in the lab; `idea_id` recorded with every registered rule and run | One registry, linked tests | Medium (both apps) | The lab reads the ledger read-only |
| I3 | Desk shows evidence cards and forward status beside the stance; stance rules v3 that refuse a rule whose forward status is failed or deteriorating | Deterioration changes behaviour automatically | Medium (desk) | A registered stance-rules version |
| I4 | Daily hash-chained feature archive in the desk (one row per session of every card's key values) | Point-in-time record so tier-6 information can be tested later | Low-medium (desk) | Today `thesis_state.json` is overwritten |
| I5 | Score each stance by the rule's own exit as well as 5 sessions (desk gap 11) | The scoreboard measures the same trade as the evidence | Low (desk) | - |
| I6 | Declarative rule specs written by the lab and evaluated by the desk (keep the date cross-check) | Rules written once; new rules reach the desk without code | Medium-high | Later phase |
| I7 | One count of ideas tried across both apps, shown with results | Honest multiple-testing context | Low | - |

### Optional enhancements

| ID | Enhancement | Why optional |
|---|---|---|
| O1 | Walk-forward (rolling) evaluation | Rules have no fitted parameters; C1's forward block covers the need |
| O2 | A form or notebook for one-off descriptive studies | Convenience; registration discipline must stay |
| O3 | Cash yield (FRED 3-month bill) in strategy equity | Small, known bias against low-exposure rules |
| O4 | Run-to-run comparison page | C2 covers the important part |
| O5 | Minute-bar history from a free API (Alpaca, if the user chooses) | Unlocks intraday studies years earlier; user decision |
| O6 | Sector ETF daily data in the desk | Only if sector questions become central |
| O7 | Forward sentiment labels on headlines (fixed rule, written now) | Cheap to start; useful only after years |
| O8 | Analogue finder by market state (nearest past days on a few registered variables) | Useful for Scenario D; risk of story-telling, so descriptive only |

### Unnecessary features (would add complexity without fixing a real limitation)

| Feature | Why not |
|---|---|
| Parameter optimisation or grid-search tools | The problem is false discovery, not too few variants; the neighbourhood report (H8) is enough |
| Machine-learning or multi-factor models | 26-104 trades per rule cannot support them; they would fit noise |
| More indicators (stochastics, Ichimoku, etc.) | 63 tests of seven trend, momentum and volume studies already showed no evidence |
| A shared database, a unified app, a validation service or an API between the apps | The file contract works, keeps the desk's records safe and survives the laptop sleeping |
| Fully automatic research-to-backtester runs | Would bypass registration, the lab's main safeguard |
| Paid historical news, sentiment or catalyst archives | No evidence yet that news improves decisions; licensing and cost; collect forward first |
| Broker or paper-trading API integration | Against the desk's rules; the paper book already records the trades |
| Alerts and push notifications | The desk's evening page and 3:50 PM check cover the two decision moments |
| Intraday event studies before the data exist | 12 sessions of minute bars |

## 11.2 Sequence

| Phase | Work | Size | Unblocks |
|---|---|---|---|
| 0. Now, no code | Keep the laptop asleep (not shut down) on market days so the desk's daytime jobs run; record a call each evening; decide that no leveraged position rests on these rules until H4 and C3 exist | - | Forward data (pre-close, options, futures), the call scoreboard |
| 1. Lab, 1-2 days | C2 verdict changes; C3 risk metrics; H6 cost line; H1 intervals | Small | Honest reading of current results |
| 2. Lab, 2-3 days | C1 Lead v3 (frozen development end, forward block), registered first; H5 next-open exit version | Small-medium | Deterioration monitoring |
| 3. Lab, 3-5 days | H3 more inputs; H2 split engine; register and run ideas 7 and 8 and the VIX-curve split; H4 leveraged pricing; H7 volatility-matched baseline (registered before looking) | Medium | Regime and information-value answers; leveraged decisions |
| 4. Both apps, 3-5 days | I1 evidence file; I2 structured ideas and the lab's reader; I3 cards and stance rules v3; I4 feature archive; I5 rule-exit scoring | Medium | The integrated loop |
| 5. Later | I6 declarative rules; intraday studies once 60+ sampled sessions or a minute history exist; same-day options description after 60 sessions | Medium-large | New routes (B, D, E) |

## 11.3 Developer hand-off (for Codex or another coding agent)

### Ground rules for whoever implements this
- Two repositories: `C:\Claude\trading-backtester` (the lab; this hand-off) and `C:\Claude\trading-research` (the desk;
  its tasks go to that project's own session). The lab reads the desk's files and never writes into that folder. The
  desk must never need the lab to run.
- Python: `..\trading-research\.venv\Scripts\python.exe -B`. Tests: `-m unittest discover -s tests` (36 today); every
  change adds tests; all must pass.
- A study, exit, pricing or verdict that has been run is never edited: add a version, register it with
  `-m backtester.lock --add`, commit before running it on real prices. `trials.jsonl` and `holdout_ledger.jsonl` are
  append-only; never edit them.
- `exports/trade_simulation.json` schema 1: keep every field the desk reads (including `verdict_v1`, `risk_matched`,
  `signal_days`, `strategies[].development/holdout.trades/strategy/matched`); add fields, never rename or remove.
- 1993-2009 is looked at once per version through `ledger.holdout_result`; descriptive add-ons must not call the holdout
  outside it.
- After a change: tests, commit with a clear message, push `main`.

### T1. Verdict changes in every trade run (C2)
- **Where:** `run_trades.py` (`main`, after `run`).
- **Do:** read the last record in `trials.jsonl` with `kind == "trade_simulation"`, `family == "registered"` and the
  same `verdict_version`; build `{(symbol, study, mode): verdict}`; compare with this run; produce
  `[{"symbol", "strategy", "mode", "from", "to"}]`.
- **Write to:** the new record (`verdict_changes`), the export (top-level `verdict_changes`), the report (a section
  "Changed since the last run", or "No verdict changed"), and the console (so `work\weekly_run.log` shows it).
- **Tests:** a sandboxed run twice with a monkey-patched verdict → one change reported; identical runs → empty list;
  a partial run → no comparison.
- **Accept when:** the weekly log line lists changes; the export validates in the desk (`signals.validate_export`).

### T2. Intra-trade risk metrics (C3, H6)
- **Where:** `backtester/simulate.py` (new `excursions(frame, trades, mode)`), `price_trades` (add `mae`, `mfe`
  columns), `evaluate` (new keys), `run_trades.period_lines`, `compact`, `TRADE_COLUMNS` (append at the end).
- **Definition:** next-open entry: lows and highs from the entry day (p+1) through the exit day; close entry: from
  p+1 through the exit day; MAE = min(low)/entry - 1, MFE = max(high)/entry - 1.
- **New keys per period:** `median_net`, `profit_factor` (None when no losses), `worst_net`, `best_net`,
  `mean_without_best3`, `mae_median`, `mae_p10`, `mae_worst`, `trades_mae_below_5pct`, `trades_mae_below_10pct`,
  `net_at_cost_bp` ({2,5,10,20}: mean net at that round-trip cost), `by_year` ({year: [trades, mean_net]}).
- **Tests:** a hand-made frame with known lows/highs; profit factor with no losses; by-year sums equal totals.
- **Accept when:** a rebuild of the 2026-11-17 trade run gives the same verdicts and p-values as recorded (the new keys
  are descriptive), and the QQQ RSI(14) next-open block shows MAE worst about -11.65%.

### T3. Lead v3: frozen development window and forward block (C1)
- **Where:** new `backtester/lead_v3.py` (reuse `lead_v2` functions), `run_trades.py`, `lock.py` (register
  `verdict:lead@v3`), README, CLAUDE.md, LOG.md.
- **Definition:** identical tests and thresholds to v2, with `DEV_END = "2026-11-13"` (v2's registration date) in
  `PARAMS`. Development statistics, q and the benchmark use 2010-01-01..DEV_END only. Forward = trades whose signal
  day is after DEV_END (and, for the original rules, flag those after 2026-11-08 too). For each strategy-entry:
  `forward = {"since", "trades", "mean_excess", "band_lower", "status"}` where excess uses the development baseline
  for the same length, `band_lower = m - 2 * s / sqrt(n)` from development excess (m, s), status in
  {"none yet", "consistent", "deteriorating", "failed"} (failed: forward 90% interval below zero by quarter resampling).
- **Export:** `verdict_version: "v3"`, new `verdict_definition`, keep `verdict_v1`, add `verdict_v2` per row and a
  per-row `forward` object (a new key beside `development` and `holdout`).
- **Process:** register and commit v3 before the first real run; tell the desk's session (fields added, `verdict`
  now v3).
- **Tests:** synthetic history where forward trades are bad → status deteriorating/failed while development stats are
  unchanged; development stats identical whatever happens after DEV_END; v2 output unchanged.
- **Accept when:** two runs a week apart give identical development verdicts; the forward block grows.

### T4. Confidence intervals (H1)
- **Where:** `lead_v2.excess_test` produces `means`; add a separate helper that returns the 5th and 95th percentiles of
  the same resample without changing `p` (verify by rebuild), or compute them in `lead_v3`. Studies: a new
  quarter-cluster bootstrap of (forward return - period mean) over signal days, with its own random stream
  (`rng_for(seed, *who, "ci")`), reported beside excess; no change to the study p or verdict.
- **Accept when:** rebuilt records match exactly; reports show "excess (90% interval)".

### T5. More inputs and multi-symbol conditions (H3)
- **Where:** `backtester/data.py`.
- **Do:** add optional files with their paths relative to the desk's `data/` folder: `raw/VIX3M.csv`, `raw/VIX9D.csv`,
  `raw/credit/BAA10Y.csv`, `events/events.csv`, `raw/fred/T10Y3M.csv` (extend the snapshot layout to keep relative
  paths). Keep `_fingerprint` unchanged for runs without the new files (it already skips absent files). FRED-style
  series are joined with a one-session lag (the desk's `thesis/data.fred` rule). Provide
  `load_context(root) -> DataFrame` by date, and let a `Study` declare `needs=("RSP", "VIX3M", ...)`; its rule receives
  `(frame, context)`.
- **Tests:** causality (truncation) for every context column; old snapshots still load and fingerprint identically.

### T6. Split engine (H2, H7)
- **Where:** new `backtester/splits.py`, a runner `run_splits.py`, a section in reports.
- **Model:** `Split(name, version, description, variable(frame, context) -> Series known at the decision time,
  edges: list[float] | labels, applies_to: list of "symbol:signal@v+exit@v")`. For each registered split and
  strategy-entry: per bucket trades, mean excess, interval; difference "bucket vs rest" with an interval; q across the
  registered split family; 1993-2009 once via the ledger where the variable exists.
- **First registrations (before any run):** idea 7 (next-open gap from the signal close: < -0.5%, -0.5..+0.5%,
  +0.5..+1.5%, > +1.5%); idea 8 (SPY above/below its 200-day average x VIX < 20, 20-30, >= 30 at the signal close);
  VIX/VIX3M > 1 at the signal close; an event (CPI, jobs, Fed) inside the holding window. Volatility-matched baseline
  as a benchmark version: excess against same-length trades starting on days in the same VIX bucket.
- **Tests:** planted bucket effect found; no effect → q high; causality of every variable.

### T7. Leveraged pricing (H4)
- **Where:** `strategies.py` (new pricing set version), `simulate.price_trades`, `daily_returns`.
- **Do:** `lev_next_open`: signal and exit days from the 1x index (QQQ, SPY); prices from TQQQ (QQQ) or UPRO (SPY)
  own OHLC (entry at its open after the signal, exit at its close on the exit day); MAE from its own lows. Development
  only (TQQQ from 2010-02-11). Verdict: none ("display only") until a registered verdict version covers it.
- **Accept when:** the report shows each strategy's 1x and 3x results side by side with MAE.

### T8. Exit at the next open (H5)
- **Where:** `strategies.py`: `Exit("close_above_sma5_next_open", "v1", ...)` returns the decision day; pricing sells at
  the next open. Needs `price_trades` to accept an exit price type per exit. Register with the lock.

### T9. Evidence file (I1)
- **Where:** `run_trades.py` (and later `run_splits.py`): write `exports/evidence.json` atomically (like `write_json`).
- **Schema:** [08 section 8.4](08_integration_and_registry.md). Include `idea_id` when T10 exists.
- **Tests:** schema fields present; values equal the report's; JSON loads in a clean interpreter.

### T10. Idea link (I2, lab side)
- **Where:** `catalog.Study`, `strategies.Exit` (optional `idea_id`), records and exports. A read-only reader of
  `<research>/data/thesis/ideas.jsonl` (verify its hash chain like `registry.read`) that lists ideas at stage
  "registered" with no matching rule, shown in the app's log pane on start.

### Desk-side tasks (to hand to the research app's own session)
- D1. Idea ledger schema 2 fields (observation, mechanism, instruments, rule, decision_time, horizon, expected,
  benchmark, confirm, invalidate, monitor); old events stay valid.
- D2. Read `exports/evidence.json` when present; show a compact card beside each fired or near-trigger rule
  (occurrence, interval, MAE worst, forward status, limitations, age); keep working without it.
- D3. Stance rules v3: a fired next-open Lead counts only if its forward status is not "failed" or "deteriorating";
  record `stance_rules: 3`.
- D4. Daily feature archive: append-only, hash-chained, one row per session from the build state.
- D5. Score stances and paper trades by the rule's own exit beside the 5-session score.
- D6. Download IWM from 2000 into `etfs_long.csv` (H9).
- D7. Operations: the daytime jobs need the laptop asleep or on; no code change.
