# Trading backtester log

## Pick up here (next session)

**In progress: the trade simulator for the oversold candidates.** The rules are registered in
`backtester/strategies.py` (committed 2026-11-08 before any simulation ran, so the commit date proves they
weren't tuned on results). Nothing has been simulated yet. Build next:

1. `backtester/simulate.py`
   - Trades: for each signal day t (study rule true at t's close), enter per execution mode, exit at the close of
     the session the exit rule returns (`hold_5`: t+5; `close_above_sma5`: first close above the 5-day SMA in
     t+1..t+10, else t+10). One position at a time; the next signal must come after the exit day.
     A trade counts in a period only if both its signal day and exit day fall inside that period.
   - Entry price: `etf_close` and both perp modes use close[t]; `etf_next_open` uses open[t+1].
   - Costs per round trip (config.json): ETF 2 bp; perp maker 4 bp or taker 24 bp, plus funding of
     `funding_bps_per_day` (add 1.37 to config.json; the measured US500 mean per daily record, zeros included) for
     every 4 PM crossed while held: (exit date - entry date in calendar days) - 1, since entry is just after a 4 PM
     and exit just before one. Proxy prices: adjusted SPY/QQQ (US500 seemed to track a total-return index over
     24 days; unconfirmed).
   - Daily marked equity at 1x: in-market days earn the instrument's return (next-open entry: first day is
     close/open - 1), costs deducted on the exit day, cash days earn 0. Report CAGR, max drawdown, exposure (share
     of days in the market), CAGR / max drawdown (the user's "return per unit of risk").
   - Benchmarks: (a) exposure-matched buy-and-hold: daily return = exposure x close-to-close return (for perp
     modes also minus exposure x funding per calendar day); (b) random entries: 2,000 draws of the same number of
     trades with the same holding lengths at random valid entry days in the period, and the percentile of the
     strategy's mean gross trade return.
2. `run_trades.py`: SYMBOLS x SIGNALS x EXITS = 12 strategies, each on development (2010 on) and holdout
   (1993-2009; QQQ from 1999), all four execution modes as columns. Write `reports/<date>-trade-simulation.md` and
   `.html`, and append to `trials.jsonl` (kind `trade_simulation`).
3. Verdict per strategy and mode, using these registered rules: **Lead** if random-entry percentile >= 95% in
   development and >= 90% in the holdout, and net CAGR beats exposure-matched buy-and-hold in both periods.
   **Timing edge only** if it beats random entries but not matched buy-and-hold. **Failed holdout**, or
   **No edge** if development fails the random-entry test.
4. Tests (mechanics: entry/exit indices, no overlap, funding crossings, cost deduction, matched benchmark,
   planted-edge percentile), a "Run trade simulation" button in `backtester_app.pyw`, then commit and push.

Daily data can't model stops honestly (no intraday path), so v1 has no stops; say so in the report.

## 2026-11-08
- Started the app: causal indicators, event studies with circular-shift p-values, BH correction, the 1993-2009
  holdout, and a hash-chained trial record. First run: 90 tests. Oversold mean reversion (RSI(2) < 10, RSI(14) < 30,
  close below the lower Bollinger band) were candidates on SPY/QQQ. Trend and momentum signals showed no evidence.
- Desktop app (`backtester_app.pyw`, "Trading Backtester" shortcut) with HTML reports. Private repo
  https://github.com/ghzxdt/trading-backtester.
- Registered the trade-simulation rules (`backtester/strategies.py`); simulator not built yet.
