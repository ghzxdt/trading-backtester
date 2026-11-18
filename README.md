# Trading backtester

A separate app that tests chart-indicator ideas (EMA touches, RSI, MACD, Bollinger bands, volume, and later VWAP and
opening ranges) on the data the **trading-research** app collects. It reads that app's files and never writes to
them. The point is to turn "I think this indicator helps" into a number before you rely on it while charting.

## Run it

Double-click **Trading Backtester** on the desktop. The app runs the studies (about 10 seconds) and opens the
report in your browser, runs the tests, and opens the research app. From a terminal instead, using the research
app's Python (nothing to install):

```
..\trading-research\.venv\Scripts\python.exe -B run_studies.py
..\trading-research\.venv\Scripts\python.exe -B run_studies.py --symbols SPY QQQ --horizons 1 5
..\trading-research\.venv\Scripts\python.exe -B run_trades.py
..\trading-research\.venv\Scripts\python.exe -B run_splits.py
..\trading-research\.venv\Scripts\python.exe -B -m unittest discover -s tests
```

`run.cmd` does the first of these. Each run writes `reports/<date-time>-indicator-studies.md` (plus an `.html`
page; the time is UTC) and appends every test to `trials.jsonl`. `run_trades.py` (the app's "Run trade
simulation") writes `reports/<date-time>-trade-simulation.md`, `exports/trade_simulation.json`, which the research
app's Daily thesis tab reads if it exists (ETF pricing only), and `exports/trades/<date-time>-trade-simulation.csv`,
a list of every simulated trade with its entry and exit day and price (the app's "Open trade list" button), plus
`exports/evidence.json`, one evidence card per strategy and ETF entry. `run_splits.py` (the app's "Run filter tests")
writes `reports/<date-time>-filter-tests.md` and `exports/filter_tests.json`.

The trade simulation also runs by itself every Saturday at 10:00 AM (Windows scheduled task **Trading Backtester
Weekly Run**, script `run_weekly.ps1`), then commits and pushes its results; its log is `work\weekly_run.log`.
The task wakes the laptop from sleep to run, but not from a shutdown: leave it asleep or on, signed in.

A run with other symbols, horizons, seed or draws than the registered ones is a partial run: it reports the numbers
but gives no verdicts and does not look at 1993-2009.

## What keeps a result honest

- **Inputs are kept.** Each run copies the research app's price files into `snapshots/<fingerprint>/` and reads
  from the copy, so any recorded result can be rebuilt later.
- **One look at 1993-2009.** The first registered run stores each rule version's result in `holdout_ledger.jsonl`;
  later runs read it instead of computing it again.
- **Rules can't change quietly.** `rule_lock.json` fingerprints what each registered rule does; an edited rule
  stops the run until it is added as a new version.
- **Each test has its own random numbers**, so a p-value doesn't depend on what else ran.
- **Verdicts don't drift** (2026-11-18). The trade verdict is judged on a development window fixed at 2010-01-01 to
  2026-11-13; trades signalled after it are a separate forward record, and each report lists the verdicts that
  changed since the last registered run.

## What a study measures

A study is one rule known at a day's close (e.g. "RSI(2) below 10"). For each symbol and horizon *h* (1, 5, 10
sessions) it reports:

- **Excess**: the average return over the next *h* sessions after the signal, minus the average over all days in
  the same period, with a 90% interval (calendar quarters of signals resampled). Ordinary market drift is not counted
  as an edge.
- **p**: how often a randomly shifted copy of the same signal pattern does as well (keeps its count and clustering).
- **q**: p corrected for every test in the run (Benjamini-Hochberg).
- **Holdout**: the same rule on 1993-2009 data that played no part in choosing it (SPY and QQQ; IWM from 2000-05-26
  once the research app saved its longer history on 2026-11-18; its first look comes with the next registered run).
  Looked at once per rule version.
- **Next-open**: the excess if you buy at the next morning's open rather than the close (perps trade at ~4:05 PM).
- **Verdict**: *Candidate* only if the development result survives q < 0.10, beats the ETF round-trip cost, and the
  holdout agrees (same direction, p < 0.10). Otherwise *No evidence*, *Failed holdout*, *Development only*,
  *Real but smaller than costs*, or *Opposite effect*.

## What the trade simulation measures

The three oversold signals that were Candidates, turned into trades with two fixed exits on SPY and QQQ (12
strategies), each priced four ways. The verdict is **Lead v3** (`backtester/lead_v3.py`, registered 2026-11-18): the
tests of Lead v2 (`backtester/lead_v2.py`, registered 2026-11-13) on a development window fixed at 2010-01-01 to
2026-11-13, so a verdict no longer moves as data is added.

- **Excess**: the average trade minus the average of every possible trade of the same length in the period, with a
  90% interval.
- **p**: from resampling the rule's own trades by calendar quarter, so the spread is the rule's own (these rules
  trade in sell-offs, when prices swing more than usual). **q** corrects for the 24 strategy-and-entry tests.
- **Risk-matched buy-and-hold**: the index held for the same share of days, scaled to the volatility the rule
  carries while in a trade.
- *Lead* needs p < 0.05 and q < 0.10 from 2010 on, p < 0.10 in 1993-2009, and a higher CAGR than the risk-matched
  benchmark in both. 1993-2009 helped choose these signals, so it can remove a Lead but not confirm one.
- **Forward record**: trades signalled after 2026-11-13, each compared with the development mean of trades of its
  length. From 5 forward trades, a forward mean below the development mean minus 2 standard errors is *below band*,
  and a Lead becomes *Forward below band* (the research app acts only on "Lead"). The band catches a large break; it
  cannot confirm an edge, which at these rules' trading rates would take years.
- **Risk inside trades** (descriptive): the worst point each trade reached from daily lows (MAE), median and worst
  trades, the mean without the best three, results at 2/5/10/20 bp of cost, and the result if the exit were taken at
  the next open.
- **Leveraged-ETF version** (descriptive): the same trades priced in TQQQ and UPRO, 2010 on.

The earlier verdicts are still computed and shown beside v3: v1 (2026-11-08) compared the rule with entries on
ordinary days and with a benchmark carrying about a third of the rule's risk, which overstated the evidence; v2
(2026-11-13) is v3's test on a development window that kept growing with every run.

## What the filter tests measure

`backtester/splits.py`, registered 2026-11-18 before any was run. For four strategy-entries (QQQ Bollinger and QQQ
RSI(14) at the next open, SPY Bollinger at the next open, QQQ RSI(2) at the close): did the trades do better or worse
when a condition held at the signal? Conditions: a gap up of 0.5% or more at the next open (idea 7), SPY below its
200-day average and VIX 20 or higher (idea 8), VIX above VIX3M, a scheduled CPI, jobs or Fed release within 5
sessions. Each gives the difference in mean excess per trade with a 90% interval, p and q, and 1993-2009 once where
the condition can be measured there. A volatility-matched baseline asks whether each strategy beats trades started on
days with the same VIX level. A filter worth using becomes a new registered strategy version; no label here changes a
trade verdict.

## Data (read-only, from the research app)

- `data/raw/etfs_long.csv`: SPY since 1993, QQQ since 1999, IWM since 2000 (added 2026-11-18) (adjusted daily OHLCV)
- `data/raw/etfs.csv`: SPY, QQQ, IWM, DIA, RSP, TQQQ, SQQQ, UPRO, SPXU since 2010
- `data/raw/VIX.csv`: Cboe VIX
- `data/raw/VIX3M.csv`: Cboe three-month VIX (since 2009), and `data/events/events.csv`: the CPI, jobs and Fed
  calendar (since 2010), for the filter tests (2026-11-18)
- Later: `data/intraday/v1/` minute bars, which the research app now collects every weekday

## Results so far

See `reports/`. First run (2026-11-08, 90 tests): oversold mean-reversion rules on SPY and QQQ (RSI(2) < 10,
RSI(14) < 30, close below the lower Bollinger band) were candidates, confirmed on the 1993-2009 holdout. EMA
touches, MACD crosses, 20-day breakouts, volume spikes and the 200-day trend state showed no evidence. Candidates
are leads for a full trade simulation, not proven edges.

## Adding a study

Add a `Study` at the end of `backtester/catalog.py` with version `v1`, then register it:
`..\trading-research\.venv\Scripts\python.exe -B -m backtester.lock --add`. Never edit a study that has been
run; change it by adding `v2` (the rule lock refuses an edit). Every run stays in `trials.jsonl`, failures
included, so the number of ideas tried is always visible.

## Next steps

1. Trade simulator: done 2026-11-08, verdict v2 on 2026-11-13 (no stops yet: daily bars can't show whether a
   stop would fill). See LOG.md for the results.
2. Regime splits for the candidates: trend, VIX level, VIX curve and release days registered 2026-11-18 (filter
   tests); credit spreads not yet.
3. Intraday studies (VWAP, opening range, relative volume by time of day) once the research app's minute history
   has a few months of sessions.
4. Feed results back into the research app's Today page as "what happened after similar setups": the evidence
   cards (`exports/evidence.json`, 2026-11-18) are ready for it; the research app does not show them yet.
5. The full list, in order, is part 11 of `docs/reviews/BACKTESTER_AUDIT_2026-11-17.md`.
