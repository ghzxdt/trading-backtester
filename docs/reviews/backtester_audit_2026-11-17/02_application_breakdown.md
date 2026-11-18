# 2. Complete application breakdown

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Deliverable 3: what the backtester
actually does, as found in the code at 407cd65/28ce2c8 and in its records, not as its documents intend.

## 2.1 In one paragraph

A small, deliberately strict Python lab (about 2,400 lines including tests) that reads the research app's saved
daily ETF prices, tests a fixed catalogue of chart-indicator rules as event studies, simulates three oversold rules
as trades, and writes reports, an append-only trial record and one JSON export that the research app's Daily thesis
reads. It is built around preventing self-deception (registration, one look at 1993-2009, rule fingerprints, kept
inputs) rather than around flexible exploration. It has no parameter search, no screen, no regime split and no
intraday data, by design or not yet.

## 2.2 Architecture

| File | Lines | Role |
|---|---|---|
| `backtester_app.pyw` | 180 | Tk window: 7 buttons, a status line and a log pane. Runs the scripts below with the research app's Python. |
| `run_studies.py` | 192 | Indicator studies: every study x symbol x horizon; report, trial record, holdout ledger |
| `run_trades.py` | 383 | Trade simulation: 12 strategies x 4 pricings x 2 periods; report, record, ledger, export, trade list |
| `run_weekly.ps1` | 51 | Scheduled Saturday run of `run_trades.py`, then commit and push of its outputs only |
| `backtester/data.py` | 125 | Read-only loader of the research app's files; snapshot and fingerprint |
| `backtester/indicators.py` | 52 | SMA, EMA, RSI, MACD, ATR, Bollinger, relative volume, cross-above |
| `backtester/catalog.py` | 66 | The 10 registered studies; the registered symbols, horizons, draws and seed |
| `backtester/study.py` | 94 | Forward returns, circular-shift p, BH q, study verdicts |
| `backtester/strategies.py` | 64 | The 3 trade signals, 2 exits, 2 symbols, 4 pricings; draws and seed |
| `backtester/simulate.py` | 154 | Trade finding, pricing, costs, daily equity, benchmarks, v1 verdict |
| `backtester/lead_v2.py` | 141 | The v2 test, risk-matched benchmark and verdict |
| `backtester/ledger.py` | 90 | Per-test random streams; the one-look holdout ledger |
| `backtester/lock.py` | 109 | Rule fingerprints on a fixed synthetic price history |
| `backtester/registry.py` | 44 | Hash-chained JSONL append and read |
| `backtester/runlog.py` | 42 | Commit hash with `+dirty`, settings, report names |
| `backtester/report_html.py` | 59 | Markdown-to-HTML for reports |
| `tests/` (4 files) | 633 | 36 tests |

Stack: Python 3.12, pandas, numpy, Tkinter, from the research app's virtual environment (no packages of its own).
Storage: CSV and JSONL files; no database, no server, no network access (git aside). Everything runs locally.

## 2.3 Tickers and asset classes

| Use | Symbols | Notes |
|---|---|---|
| Registered indicator studies | SPY, QQQ, IWM | The family the correction covers |
| Partial study runs (command line) | Any symbol in the research app's daily files: DIA, RSP, TQQQ, SQQQ, UPRO, SPXU as well | No verdicts, no holdout look |
| Trade simulation | SPY, QQQ | The command line exposes only `--draws` and `--seed`; other symbols need code |
| Kalshi perps | None directly | "Perp" pricings use the ETF's price as a stand-in |
| VIX | Loaded beside every symbol as `vix` | Not used by any study or strategy |

Asset class: US equity index ETFs (1x, and 3x/-3x available but unused). No single stocks, futures, options,
crypto, rates or FX.

## 2.4 Data sources, coverage and granularity

| File (research app `data/raw/`) | Content | Coverage (snapshot of 2026-11-13) |
|---|---|---|
| `etfs_long.csv` | SPY, QQQ daily OHLCV, split- and dividend-adjusted (Yahoo) | SPY 1993-01-29 on, QQQ 1999-03-10 on |
| `etfs.csv` | SPY, QQQ, IWM, DIA, RSP, TQQQ, SQQQ, UPRO, SPXU daily OHLCV, adjusted (Yahoo) | 2010-01-04 on (TQQQ, SQQQ 2010-02-11) |
| `VIX.csv` | Cboe VIX daily | 1990-01-02 on |

Granularity: one bar per session. No intraday, no quotes, no volume by time. The loader takes the longer of the two
files per symbol and refuses a long file that ends before the recent one, duplicate or unordered dates, or
non-positive prices. Each run first copies the three files (gzipped) into `snapshots/<fingerprint>/` and reads only
the copy.

Data the research app holds that the backtester does not read (see [07](07_information_effectiveness.md)): minute
bars (12 sessions), Yahoo hourly bars (since 2023-12-18), VIX9D, VIX3M, VVIX, VIX1D, Treasury yields, FRED macro
and stress series, credit spreads (Baa-10y since 1986), the CPI/jobs/Fed calendar since 2010 (575 events), GEX/DIX
since 2011, earnings dates, headlines (first seen since 2026-11-08), Kalshi snapshots, and the forward logs.

## 2.5 Periods

- Development: 2010-01-01 to the latest saved session (open-ended; see [01 section 1.6](01_technical_accuracy_audit.md)).
- Holdout: 1993-01-01 to 2009-12-31; exists for SPY and QQQ only (QQQ from March 1999). Evaluated once per rule
  version by the first registered run and stored in `holdout_ledger.jsonl`.
- No walk-forward, rolling or expanding windows; no sub-period reports.

## 2.6 Indicators

| Indicator | Definition in code | Matches common charting? |
|---|---|---|
| SMA(n) | Rolling mean, blank until n bars | Yes |
| EMA(n) | `ewm(span=n, adjust=False)`, blank until n bars | Yes after warm-up |
| RSI(n) | Wilder smoothing via `ewm(alpha=1/n, adjust=False)` seeded with the first change | Yes after a few months; differs at a series' start (IWM, early 2010) |
| MACD | EMA(12) - EMA(26), 9-period EMA signal | Yes |
| ATR(14) | Wilder-smoothed true range | Yes (unused by any study) |
| Bollinger (20, 2) | SMA(20) +/- 2 x population standard deviation | Yes (population standard deviation, like most charting tools) |
| Relative volume | Volume / mean of the previous 20 days' volume (today excluded) | Common variant |
| Crossed above | a > b today and a <= b yesterday | Yes |

All are causal (tested).

## 2.7 The registered studies (all v1, all long-side, all known at the day's close)

| Study | Rule | Latest result (2026-11-17 run; development 2010 on) |
|---|---|---|
| `rsi2_below_10` | RSI(2) < 10 | Candidate SPY h1, h5 and QQQ h1 |
| `rsi14_below_30` | RSI(14) < 30 | Candidate SPY h1, h5, QQQ h1, h10; Failed holdout QQQ h5 |
| `ema21_touch_uptrend` | Low <= EMA(21) <= close, close > SMA(200) | No evidence |
| `ema50_touch_uptrend` | Low <= EMA(50) <= close, close > SMA(200) | No evidence |
| `macd_cross_up` | MACD crosses above its signal | No evidence |
| `macd_cross_up_below_zero` | Same, with MACD < 0 | No evidence |
| `bollinger_lower_close` | Close < lower band (20, 2) | Candidate SPY h1, h5, QQQ h1; Failed holdout QQQ h5 |
| `new_20d_high` | Close > highest close of the previous 20 days | No evidence |
| `volume_spike_down_day` | Down day on >= 2x the previous 20-day average volume | No evidence |
| `above_sma200` | Close > SMA(200) (a state, not an entry) | No evidence |

Totals: 90 tests; 10 Candidate, 78 No evidence, 2 Failed holdout. IWM is never a Candidate (it has no holdout, so its
best possible verdict is "Development only").

## 2.8 How the event study works

For each study, symbol and horizon h in {1, 5, 10} sessions:
1. Signal: the rule evaluated on the day's bar (true/false per day).
2. Forward return from the signal close to the close h sessions later; also from the next open to that close.
3. **Excess** = mean forward return on signal days minus mean on all valid days in the same period.
4. **p**: the signal pattern is shifted by a random number of days (circular shift, 2,000 draws); p is the share of
   shifts with an absolute excess at least as large, plus one, over draws plus one (two-sided).
5. **Trades** column: how many signals remain if overlapping windows are skipped.
6. **q**: Benjamini-Hochberg over all 90 development p-values of a registered run.
7. Holdout: the same excess and p on 1993-2009, read from the ledger after the first look.
8. Next-open excess: computed for the development period only, without a p-value; not part of the verdict.
9. **Verdict**: Candidate if development p < 0.05 and q < 0.10, excess positive, holdout excess positive with
   holdout p < 0.10, and development excess above the 2 bp ETF cost; otherwise No evidence, Opposite effect,
   Development only, Failed holdout, Real but smaller than costs, or Too few signals (under 20).

## 2.9 How the trade simulator works

Strategies: signals {RSI(2) < 10, RSI(14) < 30, close below the lower band} x exits {hold 5 sessions; first close
above the 5-day SMA within 10 sessions, else the 10th} x symbols {SPY, QQQ} = 12. Each priced four ways:
`etf_close`, `etf_next_open`, `perp_maker`, `perp_taker`.

- **Trades**: walk the signal days in order; skip any signal on or before the current trade's exit day (one position
  at a time); drop a trade whose exit falls outside the period or the data.
- **Prices**: entry at the signal close (or next open); exit at the exit day's close. Adjusted prices.
- **Costs**: ETF 2 bp round trip; perps 4 or 24 bp plus 1.37 bp per calendar day held through a 4 PM funding time.
  Net = (1 + gross) x (1 - cost) - 1.
- **Daily equity**: marked to close each day in a trade, cash at 0% otherwise; exposure = share of period days held.
- **Metrics per period**: trades, exposure, win rate after costs, mean gross and net, average win and loss, mean
  sessions held, CAGR, maximum drawdown, CAGR per unit of drawdown, return per unit of volatility (annualised,
  cash at 0) for the strategy and the index, v1 random-entry percentile, v2 excess with p and number of quarters,
  share of gross profit from the best 5 trades.
- **Benchmarks**: buy-and-hold at the strategy's exposure (v1); buy-and-hold at exposure x in-trade/all-day
  volatility (v2, "risk-matched"); full buy-and-hold at 1x (reference table).
- **Verdict v2** (registered 2026-11-13): Lead if development mean excess over all same-length trades is positive with
  p < 0.05 (quarter-cluster resampling, 10,000 draws) and q < 0.10 (BH across the 24 strategy-entry tests; the three
  close-entry pricings share one test), and 1993-2009 excess positive with p < 0.10, and CAGR above the risk-matched
  benchmark in both periods; at least 20 trades from at least 8 quarters per period. Labels: Lead, Timing edge only,
  Failed holdout, No edge, Too few trades, Development only.
- **Verdict v1** (2026-11-08) is still computed and exported as `verdict_v1` because the research app's paper book
  reads it for stances logged before 2026-11-13.

Latest result (2026-11-17 run): 14 Lead, 30 No edge, 4 Failed holdout. All Leads are QQQ. Next-open Leads: QQQ
Bollinger and QQQ RSI(14), both with the 5-day-average exit.

## 2.10 Governance machinery

| Mechanism | File | What it guarantees |
|---|---|---|
| Trial record | `trials.jsonl` | Every run and test appended, failures included; hash chain refuses edits; record written before the report |
| Holdout ledger | `holdout_ledger.jsonl` | 1993-2009 computed once per rule version, then read |
| Rule lock | `rule_lock.json` | A rule changed under its version stops every run; new versions are registered with `-m backtester.lock --add` |
| Snapshots | `snapshots/<fingerprint>/` | Inputs of every run kept on this machine (not on GitHub; 2.3 MB each) |
| Code version | trial record `code` | Commit hash, `+dirty` if code or `config.json` differ |
| Registered family | `catalog.py`, `strategies.py` | Only the registered symbols, horizons, seed and draws get verdicts |
| Per-test random streams | `ledger.rng_for` | p-values independent of run order and of what else ran |

## 2.11 Outputs

- `reports/<UTC date-time>-indicator-studies.md` and `.html`; `reports/<UTC date-time>-trade-simulation.md` and
  `.html`. Older reports keep date-only names.
- `exports/trade_simulation.json`, schema 1: kind, schema, generated_at, code, data_fingerprint, report,
  verdict_definition, verdict_version, verdict_parameters, data_through, entry_notes, seed, draws, settings,
  trade_list, periods, buy_and_hold, costs, modes (ETF only), strategies (24 rows: symbol, signal and version and
  description, exit and version and description, mode, verdict, verdict_v1, q, holdout_source, development and
  holdout results), signal_days (every fired date per symbol and signal). The research app relies on these fields.
- `exports/trades/<run>.csv`: 9,600 rows per run, one per trade and pricing and period (symbol, signal, versions, exit,
  pricing, period, signal day, entry day and price, exit day and price, sessions, gross, cost, net).
- Console lines for each Candidate or Lead.

## 2.12 Configurable parameters

| Where | Parameter | Effect | Safe to change? |
|---|---|---|---|
| `config.json` | `research_app` | Folder read for data | Yes (machine setting, not recorded) |
| `config.json` | development and holdout dates | Periods | No: changes every verdict; needs a new version |
| `config.json` | `costs_round_trip_bps` (etf 2, kalshi taker 24, maker 4) | Costs and the study cost hurdle | No without a version note; recorded in each run |
| `config.json` | `funding_bps_per_day` 1.37 | Perp funding | Information only |
| `config.json` | `verdict_cost` | Which cost the study verdict uses | No |
| `catalog.py` | SYMBOLS, HORIZONS, DRAWS 2000, SEED 7 | The study family | No |
| `strategies.py` | SIGNALS, SYMBOLS, MODES, DRAWS 2000, SEED 11 | The trade family | No |
| `lead_v2.py` | RESAMPLES 10,000, DEV_P, DEV_Q, HOLDOUT_P, MIN_TRADES, MIN_QUARTERS | Verdict | No (fingerprinted) |
| `study.py` | MIN_SIGNALS 20 | Study eligibility | No |
| Command line | `--symbols`, `--horizons`, `--draws`, `--seed` (studies); `--draws`, `--seed` (trades) | A partial run | Yes: partial runs give numbers only |

There is no user-facing setting for rules, thresholds, exits, holding periods or filters. New rules mean code and a
registered version.

## 2.13 Answers to the capability questions

| Question | Answer |
|---|---|
| Multiple tickers? | Yes for studies (registered three, any of nine by partial run); SPY and QQQ for trades |
| Multiple timeframes? | Daily bars only; horizons 1, 5, 10 sessions (studies); 1-10 sessions (trades) |
| Market regimes? | No. No split by VIX, trend, period or event; the VIX is loaded but unused |
| Export results? | Yes: Markdown/HTML reports, JSON export, CSV trade list |
| Reproduce results? | Yes, exactly (verified): snapshot + ledger + per-test seeds + commit hash |
| Compare results? | Only by reading reports side by side; no run-to-run diff, no comparison table across versions |
| Conditional outcomes beyond strategy backtesting? | Partly. The event-study engine answers "what happened over the next h sessions after condition X" for any daily rule written as a `Study`, with a sound null and a correction. It cannot condition on non-price data (events, macro, news), cannot split by regime, gives no distribution or interval, and every new question needs code and registration |
| Intraday, premarket, overnight-only questions? | Overnight only indirectly (close entry minus next-open entry). No premarket or intraday |
| Short side? | No. Every study and strategy is long-only |
| Stops, targets, position sizing, leverage? | No |
| Walk-forward, rolling-window or out-of-sample beyond 1993-2009? | No |

## 2.14 Actual versus described capabilities

- README "Run it" can be read as if the app runs studies on opening; it does not. Each button runs its job; opening
  the app runs nothing.
- README data list mentions minute bars "later": not used.
- README next steps 2-4 (regime splits, intraday studies, feeding results to the Today page as "what happened after
  similar setups") are not built; the research app has its own regime base rates and hourly base rates instead.
- The app's start-up text says the trade simulation takes "about 15" seconds and CLAUDE.md says about 30; the weekly
  log shows 4 seconds. Harmless.
- The study verdict's label "Development only (no holdout data)" applies to every IWM test; IWM can never be a
  Candidate in the current design. Partly a data choice: the research app saves IWM only from 2010 although it
  started trading in 2000.
