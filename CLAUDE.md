# Trading backtester

Separate app that tests indicator and setup ideas on data collected by the research app
(`C:\Users\gzdt\trading-research`, see its CLAUDE.md and LOG.md for context). The user develops a thesis there and
charts with indicators; this app measures which indicators actually carried information.

## Rules
- Read the research app's files only; never write into that folder.
- Never fabricate data. Unknown stays unknown.
- Studies are registered before they run (`backtester/catalog.py`). Never edit a study that has been run; add a new
  version. Never edit `trials.jsonl` by hand (append-only, hash-chained).
- Development period 2010 on; 1993-2009 is the holdout, checked once per study version. Report every test,
  including failures, and the multiple-testing correction.
- Indicators must be causal (a value at day t uses data up to t only); the tests check this.
- After every change: run the tests, commit with a clear message, push `main` to the private GitHub repo
  https://github.com/ghzxdt/trading-backtester.
- Uses the research app's Python: `..\trading-research\.venv\Scripts\python.exe`.

## How to run
- Desktop shortcut **Trading Backtester** opens `backtester_app.pyw` (Tk) with the research app's `pythonw.exe`.
- Next session: read `LOG.md` ("Pick up here") first.
- Studies: `..\trading-research\.venv\Scripts\python.exe -B run_studies.py` (or `run.cmd`); about 10 seconds.
- Tests: `..\trading-research\.venv\Scripts\python.exe -B -m unittest discover -s tests`.
