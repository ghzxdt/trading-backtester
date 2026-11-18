# Trading backtester

Separate app that tests indicator and setup ideas on data collected by the research app
(`C:\Claude\trading-research`, see its CLAUDE.md and LOG.md for context). The user develops a thesis there and
charts with indicators; this app measures which indicators actually carried information.

## Rules
- Read the research app's files only; never write into that folder.
- Never fabricate data. Unknown stays unknown.
- Studies are registered before they run (`backtester/catalog.py`). Never edit a study that has been run; add a new
  version. Never edit `trials.jsonl` by hand (append-only, hash-chained).
- Development period 2010 on; 1993-2009 is the holdout, checked once per study version. Report every test,
  including failures, and the multiple-testing correction.
- These rules are enforced in code (2026-11-13), not only written here:
  - `rule_lock.json` fingerprints every registered signal, exit and verdict; a rule edited under its version stops
    the run. Register a new version with `-m backtester.lock --add`.
  - `holdout_ledger.jsonl` stores each version's 1993-2009 result the first time a registered run computes it; later
    runs read it. Never edit it by hand (append-only, hash-chained). Other symbols, horizons, seed or draws make a
    run partial: no verdicts, no holdout look.
  - Each run reads its prices from `snapshots/<fingerprint>/` (gzipped copies, this machine only, not on GitHub),
    so any record can be rebuilt. Don't delete that folder.
- The trade simulator's verdict is Lead v3 (`backtester/lead_v3.py`, registered 2026-11-18): v2's tests on a
  development window fixed at 2010-01-01 to 2026-11-13, so verdicts no longer drift as data is added, plus a forward
  record of trades signalled after it (from 5 forward trades, a Lead below its band is labelled "Forward below band").
  v1 (`simulate.verdict`) and v2 (`lead_v2.py`, on v2's window to date) stay as they were and are reported beside it.
  A changed verdict is a new version, registered and committed before it runs on real prices.
- Filter tests (`backtester/splits.py`, `run_splits.py`, registered 2026-11-18) follow the same rules: a changed split
  is a new version, and 1993-2009 is looked at once per split version through the holdout ledger.
- The research app reads `exports/trade_simulation.json` (schema 1). Keep every field it reads; add, don't rename.
  `exports/evidence.json` (one evidence card per strategy and ETF entry) is for a later version of its Daily thesis.
- Indicators must be causal (a value at day t uses data up to t only); the tests check this.
- After every change: run the tests, commit with a clear message, push `main` to the private GitHub repo
  https://github.com/ghzxdt/trading-backtester.
- Uses the research app's Python: `..\trading-research\.venv\Scripts\python.exe`.

## How to run
- Desktop shortcut **Trading Backtester** opens `backtester_app.pyw` (Tk) with the research app's `pythonw.exe`.
- Next session: read `LOG.md` ("Pick up here") first.
- Studies: `..\trading-research\.venv\Scripts\python.exe -B run_studies.py` (or `run.cmd`); about 10 seconds.
- Trade simulation: `..\trading-research\.venv\Scripts\python.exe -B run_trades.py`; about 30 seconds. Also writes
  the list of every simulated trade to `exports/trades/<run>.csv` (the app's "Open trade list" button) and
  `exports/evidence.json`. Its report starts with the verdicts that changed since the last registered run.
- Filter tests: `..\trading-research\.venv\Scripts\python.exe -B run_splits.py` (the app's "Run filter tests");
  about 20 seconds. Writes `reports/<run>-filter-tests.md`, `exports/filter_tests.json` and refreshes the evidence file.
- Commit code before a real run, so the record names a clean commit (otherwise it says "+dirty").
- Weekly: the Windows scheduled task **Trading Backtester Weekly Run** (Saturdays 10:00 AM, or at the next sign-in
  if missed) runs `run_weekly.ps1`: the trade simulation, then a commit of only the files it writes and a push.
  Log: `work\weekly_run.log`. Since 2026-11-15 it wakes the laptop from sleep to run (wake timers are allowed on
  mains and battery); it cannot wake it from a shutdown, and runs only while the user is signed in. It keeps the export fresh for the research app (caution after 10 days, unused after 45).
- Tests: `..\trading-research\.venv\Scripts\python.exe -B -m unittest discover -s tests`.
