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
..\trading-research\.venv\Scripts\python.exe -B -m unittest discover -s tests
```

`run.cmd` does the first of these. Each run writes `reports/<date>-indicator-studies.md` (plus an `.html` page)
and appends every test to `trials.jsonl`. `run_trades.py` (the app's "Run trade simulation") writes
`reports/<date>-trade-simulation.md` and `exports/trade_simulation.json`, which the research app's Daily thesis tab
reads if it exists (ETF pricing only).

## What a study measures

A study is one rule known at a day's close (e.g. "RSI(2) below 10"). For each symbol and horizon *h* (1, 5, 10
sessions) it reports:

- **Excess**: the average return over the next *h* sessions after the signal, minus the average over all days in
  the same period. Ordinary market drift is not counted as an edge.
- **p**: how often a randomly shifted copy of the same signal pattern does as well (keeps its count and clustering).
- **q**: p corrected for every test in the run (Benjamini-Hochberg).
- **Holdout**: the same rule on 1993-2009 data that played no part in choosing it (SPY and QQQ only; IWM's saved
  history starts in 2010).
- **Next-open**: the excess if you buy at the next morning's open rather than the close (perps trade at ~4:05 PM).
- **Verdict**: *Candidate* only if the development result survives q < 0.10, beats the ETF round-trip cost, and the
  holdout agrees (same direction, p < 0.10). Otherwise *No evidence*, *Failed holdout*, *Development only*,
  *Real but smaller than costs*, or *Opposite effect*.

## Data (read-only, from the research app)

- `data/raw/etfs_long.csv`: SPY since 1993, QQQ since 1999 (adjusted daily OHLCV)
- `data/raw/etfs.csv`: SPY, QQQ, IWM, DIA, RSP, TQQQ, SQQQ, UPRO, SPXU since 2010
- `data/raw/VIX.csv`: Cboe VIX
- Later: `data/intraday/v1/` minute bars, which the research app now collects every weekday

## Results so far

See `reports/`. First run (2026-11-08, 90 tests): oversold mean-reversion rules on SPY and QQQ (RSI(2) < 10,
RSI(14) < 30, close below the lower Bollinger band) were candidates, confirmed on the 1993-2009 holdout. EMA
touches, MACD crosses, 20-day breakouts, volume spikes and the 200-day trend state showed no evidence. Candidates
are leads for a full trade simulation, not proven edges.

## Adding a study

Add a `Study` at the end of `backtester/catalog.py` with version `v1`. Never edit a study that has been run;
change it by adding `v2`. Every run stays in `trials.jsonl`, failures included, so the number of ideas tried is
always visible.

## Next steps

1. Trade simulator: done 2026-11-08 (no stops yet: daily bars can't show whether a stop would fill). See LOG.md
   for the first results.
2. Regime splits for the candidates (VIX level, trend, credit), declared before looking.
3. Intraday studies (VWAP, opening range, relative volume by time of day) once the research app's minute history
   has a few months of sessions.
4. Feed results back into the research app's Today page as "what happened after similar setups".
