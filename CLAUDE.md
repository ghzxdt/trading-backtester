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
- The trade simulator's verdict is Lead v2 (`backtester/lead_v2.py`). v1 (`simulate.verdict`) stays as it was and is
  reported beside it. A changed verdict is a new version, registered and committed before it runs on real prices.
- The research app reads `exports/trade_simulation.json` (schema 1). Keep every field it reads; add, don't rename.
- Indicators must be causal (a value at day t uses data up to t only); the tests check this.
- After every change: run the tests, commit with a clear message, push `main` to the private GitHub repo
  https://github.com/ghzxdt/trading-backtester.
- Uses the research app's Python: `..\trading-research\.venv\Scripts\python.exe`.

## How to run
- Desktop shortcut **Trading Backtester** opens `backtester_app.pyw` (Tk) with the research app's `pythonw.exe`.
- Next session: read `LOG.md` ("Pick up here") first.
- Studies: `..\trading-research\.venv\Scripts\python.exe -B run_studies.py` (or `run.cmd`); about 10 seconds.
- Trade simulation: `..\trading-research\.venv\Scripts\python.exe -B run_trades.py`; about 30 seconds. Also writes
  the list of every simulated trade to `exports/trades/<run>.csv` (the app's "Open trade list" button).
- Commit code before a real run, so the record names a clean commit (otherwise it says "+dirty").
- Tests: `..\trading-research\.venv\Scripts\python.exe -B -m unittest discover -s tests`.
