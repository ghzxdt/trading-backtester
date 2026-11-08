# Trading backtester log

## Pick up here (next session)

**Trade simulator done (2026-11-08).** `run_trades.py` (or the app's "Run trade simulation" button) prices the
registered rules four ways and writes `reports/<date>-trade-simulation.md/.html`, `exports/trade_simulation.json`
(ETF pricing only, read by the research app's Daily thesis tab; the user decided on 2026-11-08 that the thesis
shows no Kalshi) and a `trials.jsonl` record.

First run (code 0fb0521, 48 results): 24 Leads under the registered verdict, all but one on the
`close_above_sma5` exit or on QQQ. But the descriptive return-per-drawdown table matters more for the user's goal:
in development (2010 on) every strategy had a lower CAGR per unit of max drawdown than buy-and-hold at the same
time in the market (for example SPY RSI(2) hold 5: 0.20 vs 0.39). In the 1993-2009 holdout, which had two crashes,
most strategies beat it (SPY RSI(2) hold 5: 0.52 vs 0.13). So these are timing edges whose value depends on the
regime, not a free lunch. Trades fully invested during a crash produce the -20% to -30% drawdowns at 1x.

Next ideas (each a new registered version, never an edit): a trend or volatility filter (registered before
testing), stops once intraday bars exist, and leverage scaling for the risk view.

## 2026-11-08
- Started the app: causal indicators, event studies with circular-shift p-values, BH correction, the 1993-2009
  holdout, and a hash-chained trial record. First run: 90 tests. Oversold mean reversion (RSI(2) < 10, RSI(14) < 30,
  close below the lower Bollinger band) were candidates on SPY/QQQ. Trend and momentum signals showed no evidence.
- Desktop app (`backtester_app.pyw`, "Trading Backtester" shortcut) with HTML reports. Private repo
  https://github.com/ghzxdt/trading-backtester.
- Registered the trade-simulation rules (`backtester/strategies.py`); simulator not built yet.
