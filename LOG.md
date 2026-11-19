# Trading backtester log

## Pick up here (next session)

**Where it stands (2026-11-18).** The 2026-11-17 audit's fixes are in (`docs/CHANGES_2026-11-18.md`): the verdict is
now Lead v3 (`backtester/lead_v3.py`): v2's tests on a development window fixed at 2010-01-01 to 2026-11-13, plus a
forward record of trades signalled after it. The indicator studies use the same fixed window (method 3). Reports now
show intervals, the worst point inside trades (MAE), a cost line, the leveraged-ETF version of each trade, and the
verdicts that changed since the last registered run. Registered filter tests (`run_splits.py`) test trend, VIX, the VIX
curve, release days, the overnight gap and a volatility-matched baseline. `exports/evidence.json` holds one evidence
card per strategy for the research app.

Latest runs (code 43f0869/40ad5e1, data d09e16aa32e780ea through 2026-11-17): studies 10 Candidates (report
`2026-11-18-071234-indicator-studies`); trade simulation 14 Leads of 48, all QQQ, no verdict changed from v2
(`2026-11-18-070804-trade-simulation`); next-open Leads QQQ Bollinger (+0.60% excess, 90% interval +0.20% to +0.92%)
and QQQ RSI(14) (+2.68%, +1.85% to +3.70%), both with the 5-day-average exit. In TQQQ the same Bollinger trades
averaged +2.10% but the worst lost 47.6%. Filter tests (`2026-11-18-070830-filter-tests`): no condition earned a
place yet; the gap-up effect (idea 7) points the same way on all three next-open strategies in 2010-2026 (q 0.108)
but not in 1993-2009; QQQ RSI(14) is an edge beyond volatility. No forward trades yet.

Open items:
- The research app reads the export (schema 1, now verdict v3; checked with its own reader on 2026-11-18: ok, 6 of 6
  date cross-checks match). Its paper book reads `verdict_v1` and the page reads `risk_matched`: keep both in every
  export, or tell the research chat before dropping either (a test checks they are there). Its "provisional Lead"
  caution checks `verdict_version == "v2"` and no longer shows; the research chat should accept "v3" (see the
  change log's last section for its other tasks).
- The research page cautions when the export is over 10 days old and stops using it after 45. Since 2026-11-14
  the scheduled task "Trading Backtester Weekly Run" re-runs the trade simulation every Saturday at 10:00 AM and
  commits and pushes the results (`run_weekly.ps1`, log in `work\weekly_run.log`). If the export ever goes stale,
  check that log first. Since 2026-11-15 the task wakes the laptop from sleep (not from a shutdown); a timer wake
  has not yet been seen on this laptop (the System log showed only power-button and USB wakes).
- Not verified: whether a Kalshi perp can be bought near the ETF close at 4:05 PM (no perp prices inspected).
- `snapshots/` is on this machine only. It is inside `C:\Claude`, so the manual backup covers it.
- Full audit of 2026-11-17: `docs/reviews/BACKTESTER_AUDIT_2026-11-17.md`. What is left, merged with the Codex review
  of 2026-11-14: `docs/reviews/APP_REVIEW_2026-11-18.md`, section 4. Top two (backtester): a settings-and-method
  identity on every holdout-ledger entry, and the weekly script committing only its own files.
- Known residual: each Yahoo re-download moves adjusted prices by about 1e-6 and flips two knife-edge exits (QQQ
  2013-12-12, SPY 1993-07-22), so QQQ RSI(2)'s p moves by about 0.0005 between downloads. Visible in the
  verdict-change list; a tolerance would need a new exit version.

Next ideas (each a new registered version, never an edit): watch the forward record and the gap-up effect forward;
a credit-spread split; a leveraged-ETF verdict once a loss limit is set; stops once intraday bars exist.

## 2026-11-19: Kalshi and perpetuals removed (user decision)
- User: "as for anything kalshi or perpetual information weve been tracking i want that gone ... no more tracking
  that." Backtester: the perp_maker and perp_taker pricings are gone (strategies.MODES is ETF at the close and at the
  next open), `config.json` no longer holds Kalshi fees or funding, reports and docs no longer mention perps, and
  `simulate.costs_for` refuses a non-ETF pricing. Perps were never in a verdict's test family, so no verdict, p or q
  changes; trial records and reports before today keep their perp rows. CLAUDE.md records the rule.
- The research chat was asked the same day to remove its Kalshi collection, the Leverage tab and perp readings,
  archive (not delete) the collected Kalshi files, and leave the frozen four-rule experiment as recorded.
- Note for the planned settings guard on the holdout ledger: the recorded settings lost the Kalshi keys today; they
  never affected an ETF statistic, so the guard should hash only settings that do (ETF cost, periods, statistics).

## 2026-11-18 (afternoon): IWM history from 2000 in the research app's data
- The research chat (5fc6bec) added IWM to `data/raw/etfs_long.csv` from 2000-05-26 (6,659 sessions). Checked here:
  `data.load("IWM")` now starts 2000-05-26, SPY and QQQ are unchanged apart from the usual 1e-6 re-download drift,
  53 tests pass, the rule lock is fine; the data fingerprint changes (was d09e16aa32e780ea).
- Effect: only the indicator studies use IWM. The next registered study run takes IWM's first and only 1993-2009
  look (2000-05-26 to 2009-12-31) and stores it; IWM's 2010-on numbers shift slightly (indicators now warm up before
  2010, and the 200-day average exists from January 2010); every q moves a little with them. The trade simulation,
  filter tests and the weekly run use SPY and QQQ only and are unaffected.
- Opportunity: IWM 2000-2009 played no part in choosing the oversold rules (they were chosen on SPY and QQQ). Testing
  the two QQQ next-open Leads on it, registered before running, is the one untouched historical check these rules
  can still get. Not done yet.
- The research chat's other changes the same day: evidence cards from `exports/evidence.json` beside fired or
  near-trigger rules (it checks same_run against trade_simulation.json), a daily archive, stances scored to the
  rule's own exit, and a date cross-check that tolerates a flip within 10 ppm of the day's close.

## 2026-11-18 (later): review built on the Codex review of 2026-11-14
- User asked for another app review based on the Codex package in
  `C:\Users\timothy\Documents\Codex\2026-11-14\https-github-com-ghzxdt-trading-backtester-3\outputs\`. Result:
  `docs/reviews/APP_REVIEW_2026-11-18.md`. Read-only; nothing in either app changed.
- Reproduced Codex's benchmark finding exactly: at the same total volatility, QQQ held beat every Lead's CAGR in
  2010-2026 (QQQ Bollinger next open +4.77% against +9.17%, similar drawdown). The Leads are timing on top of a
  position, not better allocations.
- Confirmed three backtester problems the 2026-11-17 audit missed: the holdout ledger reuses 1993-2009 statistics
  after a settings change (sandbox: 2 -> 50 bp, old 2 bp numbers kept under a 50 bp header; nothing recorded is
  affected, settings unchanged since 2026-11-08); `run_weekly.ps1` commits anything staged and pushes without a branch
  check; 2009 study windows run into 2010 (one SPY signal). All open; first two are top of the merged list.
- Research app (read-only): System status still shows intraday collection OK with 0 of 16 minute-bar tickers; all
  120,705 minute bars are `retrieved_archive`, so intraday paper evidence can never qualify; the minute archive has
  not grown since 2026-11-14. For the research chat.
- Pick up here: section 4 of that review (combined priorities) supersedes the order in the audit's part 11.

## 2026-11-18: audit fixes (Lead v3, filter tests, risk and evidence cards)
- User asked to order the audit's fixes, act on them and give a before/after change log: `docs/CHANGES_2026-11-18.md`.
- Order: descriptive fixes first (verdict-change list, MAE and risk profile, intervals; verified to leave every
  recorded number unchanged), then Lead v3 and the filter tests, registered in `rule_lock.json` and committed
  (43f0869) before any run on real prices, then leveraged pricing and `exports/evidence.json`.
- First runs (data through 2026-11-17): v3 kept the 14 Leads; filter tests stored 15 first looks at 1993-2009.
- Found while running: the studies' open window turned 2 of 10 Candidates into No evidence with unchanged excess
  (two more days re-randomised the shift test: QQQ RSI(2) h1 p 0.009 -> 0.021). Fixed with the same window
  (method 3, 40ad5e1); re-run reproduces the 2026-11-13 record (10 Candidates).
- The research app's reader accepts the v3 export unchanged. Its own follow-ups are in the change log. 53 tests.

## 2026-11-17 and 2026-11-18: full audit (read-only)
- The user's brief (backtester audit, edge validation, research-app integration), run in a session started from this
  project's chat. Nothing in either app was changed; checks ran from a scratch copy. Review:
  `docs/reviews/BACKTESTER_AUDIT_2026-11-17.md` (index and executive assessment) and 13 parts in
  `docs/reviews/backtester_audit_2026-11-17/`, including the verification scripts (appendix A).
- Verified: 36 tests pass; the 2026-11-17 runs (committed in 28ce2c8) rebuild with zero differences; an independent
  re-implementation reproduces every SPY/QQQ study number and all 24 development ETF strategy-pricings. No
  calculation error found.
- Findings to act on: (1) the open-ended development window lets weekly runs mix post-registration trades into
  "development" and flip verdicts silently (QQQ RSI(2) next open is at q 0.110); (2) reports hide intra-trade risk:
  worst intra-trade lows at 1x were -11.7% (QQQ RSI(14)), -19.7% (QQQ Bollinger), -22.9% (SPY), so no leveraged use
  until MAE and TQQQ/UPRO pricing exist; (3) both p-value methods are near nominal but about 1.5-1.8x lenient for rare
  signals (synthetic test); (4) the 5-day-average exit decides at the close it sells at (moving it to the next open
  changes means by -7 to +7 bp); (5) Yahoo's 1e-6 re-adjustments flipped two knife-edge exits between snapshots
  (round to the cent); (6) the VIX is loaded but unused, so no regime test exists. Regime splits were deliberately
  not computed, to keep the research app's idea 8 blind; 1993-2009 was not looked at for any new variant.

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
