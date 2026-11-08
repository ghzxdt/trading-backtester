# Trade simulation, 2026-11-08

Code 0fb0521; research-app data fingerprint b63e9f180f1e0ab0; 48 strategy x pricing results; 2000 random-entry draws each.

**What this is.** The oversold signals that were candidates in the indicator studies, turned into trades with fixed exits that were registered before this simulator existed (`backtester/strategies.py`). One position at a time, fully invested (1x) while in a trade, cash earns nothing in between. No stops: daily bars can't show whether a stop would have filled.

**Pricing.** *ETF at close*: buy at the signal day's close. *ETF next open*: buy at the next morning's open. Both pay 2 bp per round trip. *Perp* columns price the same trades as a Kalshi perp bought just after the close: 4 bp (maker) or 24 bp (taker) per round trip plus 1.37 bp of funding for every calendar day held through a 4 PM funding time. The perp columns use the ETF's adjusted price as a stand-in for the perp's price.

**Benchmarks.** *Matched buy-and-hold* holds the same instrument every day at a fraction equal to the strategy's time in the market, so the comparison isn't flattered by holding less risk. *Random-entry percentile*: the strategy's average gross trade against 2,000 sets of random entry days with the same number of trades and the same holding lengths (95 means it beat 95% of them).

**Verdicts** (registered 2026-11-08): *Lead* = random-entry percentile at least 95 in development and 90 in the holdout, and a higher CAGR than matched buy-and-hold in both. *Timing edge only* = beats random entries in both periods, but not matched buy-and-hold. *Failed holdout* = passes development only. *No edge* = fails the random-entry test in development. *Too few trades* = under 20.

## Verdicts

| Strategy | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| SPY rsi2_below_10, hold_5 | Lead | No edge | Lead | Lead |
| SPY rsi2_below_10, close_above_sma5 | No edge | No edge | No edge | No edge |
| SPY rsi14_below_30, hold_5 | Failed holdout | Failed holdout | Failed holdout | Failed holdout |
| SPY rsi14_below_30, close_above_sma5 | No edge | Lead | No edge | No edge |
| SPY bollinger_lower_close, hold_5 | No edge | No edge | No edge | No edge |
| SPY bollinger_lower_close, close_above_sma5 | Lead | Lead | Lead | Lead |
| QQQ rsi2_below_10, hold_5 | No edge | No edge | No edge | No edge |
| QQQ rsi2_below_10, close_above_sma5 | Lead | Lead | Lead | Lead |
| QQQ rsi14_below_30, hold_5 | Lead | Lead | Lead | Lead |
| QQQ rsi14_below_30, close_above_sma5 | Lead | Lead | Lead | Lead |
| QQQ bollinger_lower_close, hold_5 | No edge | No edge | No edge | No edge |
| QQQ bollinger_lower_close, close_above_sma5 | Lead | Lead | Lead | Lead |

## Return per unit of drawdown (descriptive, not part of the verdict)

CAGR divided by the worst peak-to-trough loss, for the strategy versus exposure-matched buy-and-hold, ETF at the close. A strategy that is fully invested during its trades can earn more per year than the matched benchmark yet still have deeper drawdowns, because the benchmark spreads its smaller exposure over every day. The higher figure is named in brackets.

| Strategy | Development | Holdout |
|---|---|---|
| SPY rsi2_below_10, hold_5 | 0.20 vs 0.39 (buy-and-hold) | 0.52 vs 0.13 (strategy) |
| SPY rsi2_below_10, close_above_sma5 | 0.15 vs 0.38 (buy-and-hold) | 0.36 vs 0.13 (strategy) |
| SPY rsi14_below_30, hold_5 | 0.11 vs 0.38 (buy-and-hold) | 0.04 vs 0.13 (buy-and-hold) |
| SPY rsi14_below_30, close_above_sma5 | 0.03 vs 0.38 (buy-and-hold) | 0.09 vs 0.13 (buy-and-hold) |
| SPY bollinger_lower_close, hold_5 | 0.14 vs 0.38 (buy-and-hold) | 0.25 vs 0.13 (strategy) |
| SPY bollinger_lower_close, close_above_sma5 | 0.13 vs 0.38 (buy-and-hold) | 0.16 vs 0.13 (strategy) |
| QQQ rsi2_below_10, hold_5 | 0.10 vs 0.49 (buy-and-hold) | 0.20 vs 0.03 (strategy) |
| QQQ rsi2_below_10, close_above_sma5 | 0.36 vs 0.49 (buy-and-hold) | 0.35 vs 0.03 (strategy) |
| QQQ rsi14_below_30, hold_5 | 0.35 vs 0.48 (buy-and-hold) | 0.21 vs 0.03 (strategy) |
| QQQ rsi14_below_30, close_above_sma5 | 0.36 vs 0.48 (buy-and-hold) | 0.25 vs 0.04 (strategy) |
| QQQ bollinger_lower_close, hold_5 | 0.17 vs 0.49 (buy-and-hold) | 0.26 vs 0.03 (strategy) |
| QQQ bollinger_lower_close, close_above_sma5 | 0.30 vs 0.49 (buy-and-hold) | 0.45 vs 0.03 (strategy) |

Full-time buy-and-hold at 1x, for reference:

| Symbol | Development CAGR | Max drawdown | CAGR per drawdown | Holdout CAGR | Max drawdown | CAGR per drawdown |
|---|---|---|---|---|---|---|
| SPY | +13.85% | -33.7% | 0.41 | +7.59% | -55.2% | 0.14 |
| QQQ | +18.16% | -35.1% | 0.52 | -0.75% | -83.0% | -0.01 |

## SPY: rsi2_below_10 (v1), exit hold_5 (v1)

Signal: RSI(2) closes below 10 (short-term oversold). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 192 | 192 | 192 | 192 |
| Time in market | 23% | 23% | 23% | 23% |
| Win rate (after costs) | 64% | 58% | 61% | 56% |
| Mean per trade, gross / net bp | +58.6 / +56.6 | +39.5 / +37.5 | +58.6 / +46.1 | +58.6 / +26.1 |
| Average win / loss | +2.08% / -2.08% | +2.01% / -1.91% | +2.06% / -2.04% | +2.05% / -1.98% |
| Random-entry percentile | 97 | 83 | 97 | 97 |
| CAGR: strategy / matched buy-and-hold | +6.12% / +3.25% | +3.88% / +3.25% | +4.86% / +2.08% | +2.49% / +2.08% |
| Max drawdown: strategy / matched | -30.7% / -8.4% | -34.1% / -8.4% | -32.4% / -8.5% | -37.5% / -8.5% |
| CAGR per unit of drawdown: strategy / matched | 0.20 / 0.39 | 0.11 / 0.39 | 0.15 / 0.24 | 0.07 / 0.24 |
| **Holdout (1993-2009)** | | | | |
| Trades | 218 | 218 | 218 | 218 |
| Time in market | 26% | 26% | 26% | 26% |
| Win rate (after costs) | 64% | 63% | 62% | 59% |
| Mean per trade, gross / net bp | +86.2 / +84.2 | +66.9 / +64.9 | +86.2 / +73.6 | +86.2 / +53.6 |
| Average win / loss | +2.39% / -1.94% | +2.21% / -1.99% | +2.35% / -1.95% | +2.29% / -1.96% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +10.74% / +2.27% | +8.10% / +2.27% | +9.23% / +0.97% | +6.45% / +0.97% |
| Max drawdown: strategy / matched | -20.6% / -16.9% | -22.8% / -16.9% | -21.7% / -21.5% | -23.7% / -21.5% |
| CAGR per unit of drawdown: strategy / matched | 0.52 / 0.13 | 0.36 / 0.13 | 0.43 / 0.05 | 0.27 / 0.05 |
| **Verdict** | Lead | No edge | Lead | Lead |

## SPY: rsi2_below_10 (v1), exit close_above_sma5 (v1)

Signal: RSI(2) closes below 10 (short-term oversold). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 188 | 188 | 188 | 188 |
| Time in market | 16% | 16% | 16% | 16% |
| Win rate (after costs) | 72% | 72% | 71% | 66% |
| Mean per trade, gross / net bp | +41.5 / +39.5 | +30.3 / +28.3 | +41.5 / +31.9 | +41.5 / +11.9 |
| Average win / loss | +1.30% / -1.97% | +1.16% / -2.02% | +1.26% / -2.02% | +1.15% / -1.92% |
| Random-entry percentile | 94 | 87 | 94 | 94 |
| CAGR: strategy / matched buy-and-hold | +4.17% / +2.23% | +2.83% / +2.23% | +3.29% / +1.44% | +1.00% / +1.44% |
| Max drawdown: strategy / matched | -27.1% / -5.8% | -30.1% / -5.8% | -28.7% / -5.9% | -34.9% / -5.9% |
| CAGR per unit of drawdown: strategy / matched | 0.15 / 0.38 | 0.09 / 0.38 | 0.11 / 0.24 | 0.03 / 0.24 |
| **Holdout (1993-2009)** | | | | |
| Trades | 212 | 212 | 212 | 212 |
| Time in market | 18% | 18% | 18% | 18% |
| Win rate (after costs) | 75% | 74% | 75% | 69% |
| Mean per trade, gross / net bp | +71.1 / +69.1 | +52.7 / +50.7 | +71.1 / +61.4 | +71.1 / +41.4 |
| Average win / loss | +1.59% / -2.09% | +1.40% / -2.05% | +1.54% / -2.17% | +1.47% / -1.93% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +8.60% / +1.61% | +6.17% / +1.61% | +7.55% / +0.70% | +4.88% / +0.70% |
| Max drawdown: strategy / matched | -23.7% / -12.0% | -23.7% / -12.0% | -23.7% / -15.3% | -23.7% / -15.3% |
| CAGR per unit of drawdown: strategy / matched | 0.36 / 0.13 | 0.26 / 0.13 | 0.32 / 0.05 | 0.21 / 0.05 |
| **Verdict** | No edge | No edge | No edge | No edge |

## SPY: rsi14_below_30 (v1), exit hold_5 (v1)

Signal: RSI(14) closes below 30 (classic oversold). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 24 | 24 | 24 | 24 |
| Time in market | 3% | 3% | 3% | 3% |
| Win rate (after costs) | 75% | 71% | 75% | 75% |
| Mean per trade, gross / net bp | +145.2 / +143.2 | +139.5 / +137.5 | +145.2 / +132.7 | +145.2 / +112.7 |
| Average win / loss | +3.29% / -4.14% | +3.68% / -4.22% | +3.18% / -4.24% | +2.98% / -4.44% |
| Random-entry percentile | 99 | 100 | 99 | 99 |
| CAGR: strategy / matched buy-and-hold | +1.87% / +0.41% | +1.77% / +0.41% | +1.72% / +0.27% | +1.43% / +0.27% |
| Max drawdown: strategy / matched | -17.6% / -1.1% | -21.0% / -1.1% | -17.9% / -1.1% | -18.4% / -1.1% |
| CAGR per unit of drawdown: strategy / matched | 0.11 / 0.38 | 0.08 / 0.38 | 0.10 / 0.24 | 0.08 / 0.24 |
| **Holdout (1993-2009)** | | | | |
| Trades | 27 | 27 | 27 | 27 |
| Time in market | 3% | 3% | 3% | 3% |
| Win rate (after costs) | 48% | 48% | 48% | 41% |
| Mean per trade, gross / net bp | +52.5 / +50.5 | +60.1 / +58.1 | +52.5 / +39.8 | +52.5 / +19.8 |
| Average win / loss | +3.34% / -2.13% | +3.75% / -2.36% | +3.24% / -2.24% | +3.60% / -2.14% |
| Random-entry percentile | 75 | 82 | 75 | 75 |
| CAGR: strategy / matched buy-and-hold | +0.71% / +0.29% | +0.80% / +0.29% | +0.53% / +0.13% | +0.21% / +0.13% |
| Max drawdown: strategy / matched | -18.9% / -2.2% | -15.5% / -2.2% | -19.7% / -2.8% | -22.3% / -2.8% |
| CAGR per unit of drawdown: strategy / matched | 0.04 / 0.13 | 0.05 / 0.13 | 0.03 / 0.05 | 0.01 / 0.05 |
| **Verdict** | Failed holdout | Failed holdout | Failed holdout | Failed holdout |

## SPY: rsi14_below_30 (v1), exit close_above_sma5 (v1)

Signal: RSI(14) closes below 30 (classic oversold). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 24 | 24 | 24 | 24 |
| Time in market | 2% | 2% | 2% | 2% |
| Win rate (after costs) | 79% | 79% | 79% | 79% |
| Mean per trade, gross / net bp | +64.5 / +62.5 | +79.3 / +77.3 | +64.5 / +54.8 | +64.5 / +34.8 |
| Average win / loss | +2.02% / -4.67% | +2.45% / -5.61% | +1.95% / -4.78% | +1.75% / -4.98% |
| Random-entry percentile | 87 | 96 | 87 | 87 |
| CAGR: strategy / matched buy-and-hold | +0.74% / +0.28% | +0.88% / +0.28% | +0.63% / +0.18% | +0.34% / +0.18% |
| Max drawdown: strategy / matched | -23.5% / -0.7% | -22.7% / -0.7% | -23.6% / -0.8% | -23.8% / -0.8% |
| CAGR per unit of drawdown: strategy / matched | 0.03 / 0.38 | 0.04 / 0.38 | 0.03 / 0.24 | 0.01 / 0.24 |
| **Holdout (1993-2009)** | | | | |
| Trades | 24 | 24 | 24 | 24 |
| Time in market | 2% | 2% | 2% | 2% |
| Win rate (after costs) | 75% | 62% | 75% | 67% |
| Mean per trade, gross / net bp | +101.7 / +99.7 | +88.2 / +86.2 | +101.7 / +91.5 | +101.7 / +71.5 |
| Average win / loss | +2.25% / -2.77% | +2.63% / -2.08% | +2.19% / -2.91% | +2.26% / -2.38% |
| Random-entry percentile | 98 | 97 | 98 | 98 |
| CAGR: strategy / matched buy-and-hold | +1.35% / +0.20% | +1.14% / +0.20% | +1.23% / +0.09% | +0.94% / +0.09% |
| Max drawdown: strategy / matched | -15.7% / -1.5% | -16.0% / -1.5% | -16.5% / -1.9% | -18.9% / -1.9% |
| CAGR per unit of drawdown: strategy / matched | 0.09 / 0.13 | 0.07 / 0.13 | 0.07 / 0.05 | 0.05 / 0.05 |
| **Verdict** | No edge | Lead | No edge | No edge |

## SPY: bollinger_lower_close (v1), exit hold_5 (v1)

Signal: Close below the lower Bollinger band (20 days, 2 standard deviations). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 96 | 96 | 96 | 96 |
| Time in market | 11% | 11% | 11% | 11% |
| Win rate (after costs) | 59% | 59% | 59% | 56% |
| Mean per trade, gross / net bp | +56.4 / +54.4 | +49.5 / +47.5 | +56.4 / +43.9 | +56.4 / +23.9 |
| Average win / loss | +2.44% / -2.22% | +2.35% / -2.26% | +2.33% / -2.33% | +2.25% / -2.35% |
| Random-entry percentile | 89 | 88 | 89 | 89 |
| CAGR: strategy / matched buy-and-hold | +2.86% / +1.63% | +2.42% / +1.63% | +2.25% / +1.05% | +1.09% / +1.05% |
| Max drawdown: strategy / matched | -19.9% / -4.3% | -23.4% / -4.3% | -20.5% / -4.3% | -23.0% / -4.3% |
| CAGR per unit of drawdown: strategy / matched | 0.14 / 0.38 | 0.10 / 0.38 | 0.11 / 0.24 | 0.05 / 0.24 |
| **Holdout (1993-2009)** | | | | |
| Trades | 97 | 97 | 97 | 97 |
| Time in market | 11% | 11% | 11% | 11% |
| Win rate (after costs) | 62% | 62% | 59% | 56% |
| Mean per trade, gross / net bp | +93.1 / +91.1 | +83.9 / +81.9 | +93.1 / +80.5 | +93.1 / +60.5 |
| Average win / loss | +2.54% / -1.73% | +2.52% / -1.94% | +2.57% / -1.70% | +2.50% / -1.78% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +5.06% / +1.04% | +4.49% / +1.04% | +4.42% / +0.46% | +3.22% / +0.46% |
| Max drawdown: strategy / matched | -20.2% / -7.8% | -18.2% / -7.8% | -20.3% / -9.9% | -20.4% / -9.9% |
| CAGR per unit of drawdown: strategy / matched | 0.25 / 0.13 | 0.25 / 0.13 | 0.22 / 0.05 | 0.16 / 0.05 |
| **Verdict** | No edge | No edge | No edge | No edge |

## SPY: bollinger_lower_close (v1), exit close_above_sma5 (v1)

Signal: Close below the lower Bollinger band (20 days, 2 standard deviations). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 98 | 98 | 98 | 98 |
| Time in market | 8% | 8% | 8% | 8% |
| Win rate (after costs) | 72% | 69% | 69% | 68% |
| Mean per trade, gross / net bp | +55.9 / +53.9 | +47.7 / +45.7 | +55.9 / +46.3 | +55.9 / +26.3 |
| Average win / loss | +1.48% / -1.94% | +1.49% / -1.88% | +1.49% / -1.86% | +1.31% / -1.99% |
| Random-entry percentile | 97 | 96 | 97 | 97 |
| CAGR: strategy / matched buy-and-hold | +2.98% / +1.19% | +2.43% / +1.19% | +2.52% / +0.77% | +1.33% / +0.77% |
| Max drawdown: strategy / matched | -22.3% / -3.1% | -22.7% / -3.1% | -22.4% / -3.2% | -22.6% / -3.2% |
| CAGR per unit of drawdown: strategy / matched | 0.13 / 0.38 | 0.11 / 0.38 | 0.11 / 0.24 | 0.06 / 0.24 |
| **Holdout (1993-2009)** | | | | |
| Trades | 96 | 96 | 96 | 96 |
| Time in market | 9% | 9% | 9% | 9% |
| Win rate (after costs) | 72% | 67% | 70% | 62% |
| Mean per trade, gross / net bp | +73.4 / +71.4 | +58.1 / +56.1 | +73.4 / +62.6 | +73.4 / +42.6 |
| Average win / loss | +1.83% / -2.14% | +1.90% / -2.12% | +1.81% / -2.12% | +1.82% / -1.89% |
| Random-entry percentile | 99 | 99 | 99 | 99 |
| CAGR: strategy / matched buy-and-hold | +3.87% / +0.82% | +2.96% / +0.82% | +3.36% / +0.37% | +2.19% / +0.37% |
| Max drawdown: strategy / matched | -23.7% / -6.2% | -23.7% / -6.2% | -23.7% / -7.8% | -23.7% / -7.8% |
| CAGR per unit of drawdown: strategy / matched | 0.16 / 0.13 | 0.12 / 0.13 | 0.14 / 0.05 | 0.09 / 0.05 |
| **Verdict** | Lead | Lead | Lead | Lead |

## QQQ: rsi2_below_10 (v1), exit hold_5 (v1)

Signal: RSI(2) closes below 10 (short-term oversold). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 193 | 193 | 193 | 193 |
| Time in market | 23% | 23% | 23% | 23% |
| Win rate (after costs) | 59% | 58% | 57% | 54% |
| Mean per trade, gross / net bp | +32.3 / +30.3 | +17.2 / +15.2 | +32.3 / +19.9 | +32.3 / -0.1 |
| Average win / loss | +2.25% / -2.44% | +2.00% / -2.40% | +2.20% / -2.46% | +2.12% / -2.48% |
| Random-entry percentile | 41 | 22 | 41 | 41 |
| CAGR: strategy / matched buy-and-hold | +2.93% / +4.27% | +1.20% / +4.27% | +1.71% / +3.08% | -0.60% / +3.08% |
| Max drawdown: strategy / matched | -30.4% / -8.7% | -40.4% / -8.7% | -33.7% / -9.6% | -40.4% / -9.6% |
| CAGR per unit of drawdown: strategy / matched | 0.10 / 0.49 | 0.03 / 0.49 | 0.05 / 0.32 | -0.01 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 145 | 145 | 145 | 145 |
| Time in market | 27% | 27% | 27% | 27% |
| Win rate (after costs) | 54% | 54% | 54% | 51% |
| Mean per trade, gross / net bp | +65.2 / +63.2 | +59.2 / +57.2 | +65.2 / +52.7 | +65.2 / +32.7 |
| Average win / loss | +3.82% / -3.18% | +3.64% / -3.10% | +3.76% / -3.24% | +3.76% / -3.25% |
| Random-entry percentile | 94 | 95 | 94 | 94 |
| CAGR: strategy / matched buy-and-hold | +7.34% / +0.95% | +6.60% / +0.95% | +5.84% / -0.39% | +3.03% / -0.39% |
| Max drawdown: strategy / matched | -36.2% / -33.2% | -32.8% / -33.2% | -37.6% / -35.4% | -40.3% / -35.4% |
| CAGR per unit of drawdown: strategy / matched | 0.20 / 0.03 | 0.20 / 0.03 | 0.16 / -0.01 | 0.08 / -0.01 |
| **Verdict** | No edge | No edge | No edge | No edge |

## QQQ: rsi2_below_10 (v1), exit close_above_sma5 (v1)

Signal: RSI(2) closes below 10 (short-term oversold). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 191 | 191 | 191 | 191 |
| Time in market | 16% | 16% | 16% | 16% |
| Win rate (after costs) | 71% | 70% | 69% | 65% |
| Mean per trade, gross / net bp | +62.0 / +60.0 | +49.9 / +47.9 | +62.0 / +52.1 | +62.0 / +32.1 |
| Average win / loss | +1.54% / -1.66% | +1.38% / -1.63% | +1.52% / -1.66% | +1.39% / -1.70% |
| Random-entry percentile | 98 | 96 | 98 | 98 |
| CAGR: strategy / matched buy-and-hold | +6.79% / +3.08% | +5.32% / +3.08% | +5.83% / +2.23% | +3.45% / +2.23% |
| Max drawdown: strategy / matched | -18.9% / -6.3% | -22.2% / -6.3% | -19.3% / -7.0% | -20.1% / -7.0% |
| CAGR per unit of drawdown: strategy / matched | 0.36 / 0.49 | 0.24 / 0.49 | 0.30 / 0.32 | 0.17 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 143 | 143 | 143 | 143 |
| Time in market | 20% | 20% | 20% | 20% |
| Win rate (after costs) | 71% | 73% | 70% | 67% |
| Mean per trade, gross / net bp | +95.8 / +93.8 | +90.9 / +88.9 | +95.8 / +85.6 | +95.8 / +65.6 |
| Average win / loss | +2.59% / -3.03% | +2.35% / -3.00% | +2.56% / -3.10% | +2.46% / -3.02% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +12.02% / +0.80% | +11.36% / +0.80% | +10.81% / -0.21% | +7.91% / -0.21% |
| Max drawdown: strategy / matched | -34.2% / -26.0% | -34.8% / -26.0% | -35.2% / -27.8% | -36.7% / -27.8% |
| CAGR per unit of drawdown: strategy / matched | 0.35 / 0.03 | 0.33 / 0.03 | 0.31 / -0.01 | 0.22 / -0.01 |
| **Verdict** | Lead | Lead | Lead | Lead |

## QQQ: rsi14_below_30 (v1), exit hold_5 (v1)

Signal: RSI(14) closes below 30 (classic oversold). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 24 | 24 | 24 | 24 |
| Time in market | 3% | 3% | 3% | 3% |
| Win rate (after costs) | 88% | 79% | 83% | 79% |
| Mean per trade, gross / net bp | +300.4 / +298.4 | +293.0 / +291.0 | +300.4 / +287.7 | +300.4 / +267.7 |
| Average win / loss | +3.55% / -0.97% | +4.26% / -2.21% | +3.62% / -0.83% | +3.61% / -0.85% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +4.24% / +0.53% | +4.07% / +0.53% | +4.08% / +0.39% | +3.78% / +0.39% |
| Max drawdown: strategy / matched | -12.0% / -1.1% | -12.3% / -1.1% | -12.0% / -1.2% | -12.0% / -1.2% |
| CAGR per unit of drawdown: strategy / matched | 0.35 / 0.48 | 0.33 / 0.48 | 0.34 / 0.32 | 0.32 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 26 | 26 | 26 | 26 |
| Time in market | 5% | 5% | 5% | 5% |
| Win rate (after costs) | 69% | 50% | 65% | 65% |
| Mean per trade, gross / net bp | +157.8 / +155.8 | +119.8 / +117.8 | +157.8 / +145.0 | +157.8 / +125.0 |
| Average win / loss | +3.98% / -3.89% | +5.14% / -2.78% | +4.11% / -3.57% | +3.91% / -3.77% |
| Random-entry percentile | 96 | 92 | 96 | 96 |
| CAGR: strategy / matched buy-and-hold | +3.38% / +0.23% | +2.46% / +0.23% | +3.11% / -0.01% | +2.62% / -0.01% |
| Max drawdown: strategy / matched | -15.8% / -6.6% | -16.8% / -6.6% | -16.7% / -7.2% | -18.9% / -7.2% |
| CAGR per unit of drawdown: strategy / matched | 0.21 / 0.03 | 0.15 / 0.03 | 0.19 / -0.00 | 0.14 / -0.00 |
| **Verdict** | Lead | Lead | Lead | Lead |

## QQQ: rsi14_below_30 (v1), exit close_above_sma5 (v1)

Signal: RSI(14) closes below 30 (classic oversold). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 25 | 25 | 25 | 25 |
| Time in market | 2% | 2% | 2% | 2% |
| Win rate (after costs) | 100% | 92% | 96% | 96% |
| Mean per trade, gross / net bp | +290.4 / +288.4 | +282.1 / +280.1 | +290.4 / +282.0 | +290.4 / +262.0 |
| Average win / loss | +2.88% / – | +3.12% / -0.87% | +2.94% / -0.09% | +2.74% / -0.29% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +4.29% / +0.31% | +4.12% / +0.31% | +4.19% / +0.23% | +3.88% / +0.23% |
| Max drawdown: strategy / matched | -12.0% / -0.6% | -12.0% / -0.6% | -12.0% / -0.7% | -12.0% / -0.7% |
| CAGR per unit of drawdown: strategy / matched | 0.36 / 0.48 | 0.34 / 0.48 | 0.35 / 0.32 | 0.32 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 23 | 23 | 23 | 23 |
| Time in market | 3% | 3% | 3% | 3% |
| Win rate (after costs) | 83% | 78% | 83% | 83% |
| Mean per trade, gross / net bp | +270.3 / +268.3 | +233.7 / +231.7 | +270.3 / +260.4 | +270.3 / +240.4 |
| Average win / loss | +4.49% / -5.89% | +4.25% / -4.65% | +4.43% / -6.05% | +4.23% / -6.25% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +5.48% / +0.15% | +4.69% / +0.15% | +5.30% / -0.00% | +4.86% / -0.00% |
| Max drawdown: strategy / matched | -22.1% / -4.3% | -23.3% / -4.3% | -22.4% / -4.6% | -22.7% / -4.6% |
| CAGR per unit of drawdown: strategy / matched | 0.25 / 0.04 | 0.20 / 0.04 | 0.24 / -0.00 | 0.21 / -0.00 |
| **Verdict** | Lead | Lead | Lead | Lead |

## QQQ: bollinger_lower_close (v1), exit hold_5 (v1)

Signal: Close below the lower Bollinger band (20 days, 2 standard deviations). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 96 | 96 | 96 | 96 |
| Time in market | 11% | 11% | 11% | 11% |
| Win rate (after costs) | 57% | 59% | 56% | 55% |
| Mean per trade, gross / net bp | +65.6 / +63.6 | +59.4 / +57.4 | +65.6 / +53.1 | +65.6 / +33.1 |
| Average win / loss | +2.88% / -2.38% | +2.81% / -2.70% | +2.83% / -2.42% | +2.68% / -2.56% |
| Random-entry percentile | 85 | 84 | 85 | 85 |
| CAGR: strategy / matched buy-and-hold | +3.35% / +2.13% | +2.94% / +2.13% | +2.74% / +1.55% | +1.57% / +1.55% |
| Max drawdown: strategy / matched | -19.2% / -4.4% | -23.7% / -4.4% | -21.5% / -4.9% | -25.8% / -4.9% |
| CAGR per unit of drawdown: strategy / matched | 0.17 / 0.49 | 0.12 / 0.49 | 0.13 / 0.32 | 0.06 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 66 | 66 | 66 | 66 |
| Time in market | 12% | 12% | 12% | 12% |
| Win rate (after costs) | 61% | 62% | 61% | 58% |
| Mean per trade, gross / net bp | +100.1 / +98.1 | +99.6 / +97.6 | +100.1 / +87.4 | +100.1 / +67.4 |
| Average win / loss | +3.61% / -3.06% | +3.49% / -3.15% | +3.50% / -3.17% | +3.48% / -3.14% |
| Random-entry percentile | 96 | 97 | 96 | 96 |
| CAGR: strategy / matched buy-and-hold | +5.51% / +0.54% | +5.50% / +0.54% | +4.82% / -0.07% | +3.55% / -0.07% |
| Max drawdown: strategy / matched | -20.8% / -16.3% | -19.0% / -16.3% | -22.8% / -17.6% | -27.2% / -17.6% |
| CAGR per unit of drawdown: strategy / matched | 0.26 / 0.03 | 0.29 / 0.03 | 0.21 / -0.00 | 0.13 / -0.00 |
| **Verdict** | No edge | No edge | No edge | No edge |

## QQQ: bollinger_lower_close (v1), exit close_above_sma5 (v1)

Signal: Close below the lower Bollinger band (20 days, 2 standard deviations). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010 on)** | | | | |
| Trades | 103 | 103 | 103 | 103 |
| Time in market | 9% | 9% | 9% | 9% |
| Win rate (after costs) | 81% | 75% | 79% | 75% |
| Mean per trade, gross / net bp | +86.8 / +84.8 | +82.4 / +80.4 | +86.8 / +77.1 | +86.8 / +57.1 |
| Average win / loss | +1.63% / -2.40% | +1.73% / -1.95% | +1.60% / -2.30% | +1.48% / -2.13% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +5.15% / +1.61% | +4.82% / +1.61% | +4.66% / +1.18% | +3.38% / +1.18% |
| Max drawdown: strategy / matched | -17.1% / -3.3% | -17.4% / -3.3% | -17.2% / -3.7% | -17.4% / -3.7% |
| CAGR per unit of drawdown: strategy / matched | 0.30 / 0.49 | 0.28 / 0.49 | 0.27 / 0.32 | 0.19 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 63 | 63 | 63 | 63 |
| Time in market | 9% | 9% | 9% | 9% |
| Win rate (after costs) | 73% | 73% | 73% | 71% |
| Mean per trade, gross / net bp | +153.1 / +151.1 | +144.7 / +142.7 | +153.1 / +142.5 | +153.1 / +122.5 |
| Average win / loss | +3.07% / -2.70% | +2.85% / -2.43% | +3.00% / -2.84% | +2.87% / -2.88% |
| Random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / matched buy-and-hold | +8.68% / +0.43% | +8.20% / +0.43% | +8.14% / -0.04% | +6.88% / -0.04% |
| Max drawdown: strategy / matched | -19.5% / -12.7% | -19.5% / -12.7% | -19.5% / -13.7% | -19.5% / -13.7% |
| CAGR per unit of drawdown: strategy / matched | 0.45 / 0.03 | 0.42 / 0.03 | 0.42 / -0.00 | 0.35 / -0.00 |
| **Verdict** | Lead | Lead | Lead | Lead |

## Summary

- Lead: 24
- No edge: 20
- Failed holdout: 4

Limits: adjusted daily prices (dividends included), no slippage beyond the stated costs, no stops, no taxes, 1x only. A Lead is a rule worth watching forward, not proof of an edge; results at higher leverage scale both the gains and the drawdowns.
