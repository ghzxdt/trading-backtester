# Trading backtester log

## Pick up here (next session)

**Where it stands (2026-11-14).** A review on 2026-11-13 found the trade simulator's Lead verdict claimed more
than its evidence. Three fixes are in and pushed: every run keeps its inputs and can be rebuilt, the 1993-2009
period is looked at once and stored, and the verdict is now Lead v2 (`backtester/lead_v2.py`).

Latest trade simulation (code 213f39e, data 4e1f98996cd13f8f, report `2026-11-14-084052-trade-simulation`):
14 Leads of 48 under v2, against 24 under v1. All 14 are on QQQ; SPY has none. In the export the research app
reads (ETF pricing): 6 Leads of 24, and only 2 at the next-open entry, QQQ RSI(14) < 30 and QQQ close below the
lower Bollinger band, both with the `close_above_sma5` exit. QQQ RSI(14) rests on 25-26 trades, so its p-value
is rougher than it looks.

Open items:
- The research app's Daily thesis will now show fewer long setups (no SPY rule is a Lead; QQQ RSI(2) is a Lead
  only at the close). Its idea ledger still quotes the v1 result ("6 of 12 next-open pricings rated Lead"). That
  wording is the research chat's to update; a hand-over note is in the shared notes folder.
- Not verified: whether a Kalshi perp can be bought near the ETF close at 4:05 PM (no perp prices inspected).
- `snapshots/` is on this machine only. It is inside `C:\Claude`, so the manual backup covers it.

Next ideas (each a new registered version, never an edit): score trades after 2026-11-08 as the only untouched
evidence, a trend or volatility filter, stops once intraday bars exist, and leverage scaling for the risk view.

## 2026-11-13 and 2026-11-14
- Review of the whole app at 80c4f2a (in this project's chat). Main findings: the simulator re-tested signals on
  the two periods that had selected them; its random-entry percentile was too lenient for rules that trade in
  sell-offs; some Leads existed only at the closing price; the time-matched benchmark carried about a third of the
  rule's risk; the holdout "once" rule and rule versions were not enforced; inputs were not kept.
- Provenance (2c79930): runs read from `snapshots/<fingerprint>/`; the trial record is written before the report
  and export; records carry the settings and "+dirty"; reports are named by UTC date and time; the export states
  the verdict definition, seed, draws and data-through date. New: `exports/trades/<run>.csv` lists every simulated
  trade, with an "Open trade list" button in the app.
- Arithmetic fixes in the simulator: a trade's net return now compounds its cost like the equity curve (it was
  gross minus cost; at most 0.24 bp different for ETFs), and a first-day loss counts as a drawdown.
- Seeds, ledger, lock (2e4c9b0): one random stream per test (method 2), `holdout_ledger.jsonl`, `rule_lock.json`,
  partial runs get no verdicts. First method-2 study run (2a30d23): the same 10 Candidates, 78 No evidence and
  2 Failed holdout as before; 60 holdout results stored. Before the ledger existed, 1993-2009 had been evaluated
  in six recorded runs of the unchanged v1 rules.
- Lead v2 registered (25350c7) before running: excess over every possible same-length trade, p from resampling the
  rule's own trades by calendar quarter, Benjamini-Hochberg across the 24 strategy-and-entry tests, and a
  buy-and-hold benchmark scaled to time in the market x in-trade volatility (the user chose this benchmark on
  2026-11-13 over a whole-strategy Sharpe comparison and over keeping v1's). On made-up prices a zero-edge rule
  that trades only in volatile stretches passes v1's percentile 19% of the time and v2's test 6%.
- v2 was designed after seeing development-period diagnostics for these 12 strategies (not 1993-2009 results for
  the new statistic), and the signals were selected on both periods, so a v2 Lead is still provisional.
- First v2 run (213f39e): v2 14 Lead, 30 No edge, 4 Failed holdout; v1 on the same run 24 Lead, 20 No edge,
  4 Failed holdout. The benchmark step removed nothing (no "Timing edge only"). 48 trade holdout results stored.
  Both new records rebuild exactly from the snapshot and the ledger. 36 tests pass.

## 2026-11-12
- Laptop reset: the project moved to `C:\Claude\trading-backtester`, and `config.json` now points to
  `C:/Claude/trading-research`. Committed the 2026-11-09 study and trade-simulation runs that were left
  uncommitted before the reset (3 trial records).
- Re-ran `run_studies.py` on the new laptop (report `2026-11-13-indicator-studies`, named by UTC date). Data
  fingerprint 3af56709652ae7c6 and all 90 results are identical to the 2026-11-09 run; 456 tests recorded in total.
- Recreated the "Trading Backtester" desktop shortcut (research app's `pythonw.exe`, `assets\backtester.ico`);
  the app opens from it.

## 2026-11-08
- Started the app: causal indicators, event studies with circular-shift p-values, BH correction, the 1993-2009
  holdout, and a hash-chained trial record. First run: 90 tests. Oversold mean reversion (RSI(2) < 10, RSI(14) < 30,
  close below the lower Bollinger band) were candidates on SPY/QQQ. Trend and momentum signals showed no evidence.
- Desktop app (`backtester_app.pyw`, "Trading Backtester" shortcut) with HTML reports. Private repo
  https://github.com/ghzxdt/trading-backtester.
- Registered the trade-simulation rules (`backtester/strategies.py`); simulator not built yet.
