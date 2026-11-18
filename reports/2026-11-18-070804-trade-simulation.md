# Trade simulation, 2026-11-18

Code 43f0869; research-app data fingerprint d09e16aa32e780ea; 48 strategy x pricing results; 2000 random-entry draws each.

**What this is.** The oversold signals that were candidates in the indicator studies, turned into trades with fixed exits that were registered before this simulator existed (`backtester/strategies.py`). One position at a time, fully invested (1x) while in a trade, cash earns nothing in between. No stops: daily bars can't show whether a stop would have filled.

**Pricing.** *ETF at close*: buy at the signal day's close. *ETF next open*: buy at the next morning's open. Both pay 2 bp per round trip. *Perp* columns price the same trades as a Kalshi perp bought just after the close: 4 bp (maker) or 24 bp (taker) per round trip plus 1.37 bp of funding for every calendar day held through a 4 PM funding time. The perp columns use the ETF's adjusted price as a stand-in for the perp's price.

**The test (verdict v3, registered 2026-11-18).** v2's test, unchanged, on a development window fixed at 2010-01-01 to 2026-11-13, so a verdict no longer moves as data is added. *Excess* is the average trade minus the average of every possible trade of the same length in the period, with a 90% interval. Its p-value comes from resampling the rule's own trades by calendar quarter 10,000 times, so the spread is the rule's own and trades from one sell-off stay together. q corrects the development p-values for every strategy and entry price in the run (the three close-entry pricings are one test).

**Forward record.** Trades signalled after 2026-11-13 are untouched evidence, kept apart and compared with the development result: each trade's excess uses the development mean of trades of its length. From 5 forward trades, a forward mean below the development mean minus 2 standard errors is *below band*, and a Lead becomes *Forward below band*. The band is wide: it catches a large break, it cannot confirm an edge.

**Benchmarks.** *Risk-matched buy-and-hold* holds the same instrument every day at a fraction equal to the strategy's time in the market times (its volatility while in a trade / the instrument's on all days). Beating it means more return per unit of risk while in a trade than the instrument usually gives. *Return per unit of volatility* compares the whole strategy, idle days included, with simply owning the instrument; it is shown for information and is not part of the verdict.

**Verdicts.** *Lead* = positive excess with p < 0.05 and q < 0.1 in development, positive excess with p < 0.1 in 1993-2009, a higher CAGR than risk-matched buy-and-hold in both, and no forward record below its band. *Forward below band* = a Lead whose forward record fell below its band. *Timing edge only* = passes the tests but not the benchmark. *Failed holdout* = passes development only. *No edge* = fails in development. *Too few trades* = under 20 trades or under 8 quarters with trades.

**1993-2009 is a reused period.** The three signals were chosen on 2026-11-08 partly because they passed it in the indicator studies, so it can remove a Lead but cannot confirm one. Its statistics are computed once and then read from `holdout_ledger.jsonl`; measures added later (the interval, the risk inside trades) are not computed for it.

**v1 and v2 beside v3.** v1 (2026-11-08) and v2 (2026-11-13) are still computed, on v2's development window, which runs from 2010-01-01 to the latest data.

## Changed since the last registered run

No verdict changed (that run used verdict v2; this one uses v3).

## Verdicts (v3)

| Strategy | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| SPY rsi2_below_10, hold_5 | No edge | No edge | No edge | No edge |
| SPY rsi2_below_10, close_above_sma5 | No edge | No edge | No edge | No edge |
| SPY rsi14_below_30, hold_5 | Failed holdout | No edge | Failed holdout | Failed holdout |
| SPY rsi14_below_30, close_above_sma5 | No edge | No edge | No edge | No edge |
| SPY bollinger_lower_close, hold_5 | No edge | No edge | No edge | No edge |
| SPY bollinger_lower_close, close_above_sma5 | No edge | No edge | No edge | No edge |
| QQQ rsi2_below_10, hold_5 | No edge | No edge | No edge | No edge |
| QQQ rsi2_below_10, close_above_sma5 | Lead | No edge | Lead | Lead |
| QQQ rsi14_below_30, hold_5 | Lead | Failed holdout | Lead | Lead |
| QQQ rsi14_below_30, close_above_sma5 | Lead | Lead | Lead | Lead |
| QQQ bollinger_lower_close, hold_5 | No edge | No edge | No edge | No edge |
| QQQ bollinger_lower_close, close_above_sma5 | Lead | Lead | Lead | Lead |

### Development test behind each verdict (ETF pricings)

Development 2010-01-01 to 2026-11-13. v2 and v1 are on v2's window to date and are superseded.

| Strategy | Entry | Trades | Excess bp (90% interval) | p | q | 1993-2009 excess bp | p | v2 (to date) | v1 |
|---|---|---|---|---|---|---|---|---|---|
| SPY rsi2_below_10, hold_5 | ETF at close | 192 | +30.3 (-5 to +63) | 0.077 | 0.165 | +68.5 | 0.001 | No edge | Lead |
| SPY rsi2_below_10, hold_5 | ETF next open | 192 | +14.8 (-19 to +47) | 0.224 | 0.268 | +53.6 | 0.005 | No edge | No edge |
| SPY rsi2_below_10, close_above_sma5 | ETF at close | 188 | +21.6 (-10 to +50) | 0.121 | 0.213 | +58.3 | 0.000 | No edge | No edge |
| SPY rsi2_below_10, close_above_sma5 | ETF next open | 188 | +14.0 (-19 to +42) | 0.215 | 0.268 | +44.3 | 0.002 | No edge | No edge |
| SPY rsi14_below_30, hold_5 | ETF at close | 24 | +116.8 (+38 to +203) | 0.009 | 0.032 | +34.8 | 0.246 | Failed holdout | Failed holdout |
| SPY rsi14_below_30, hold_5 | ETF next open | 24 | +114.8 (-11 to +253) | 0.067 | 0.160 | +46.8 | 0.220 | No edge | Failed holdout |
| SPY rsi14_below_30, close_above_sma5 | ETF at close | 24 | +44.9 (-136 to +189) | 0.288 | 0.314 | +88.4 | 0.090 | No edge | No edge |
| SPY rsi14_below_30, close_above_sma5 | ETF next open | 24 | +63.3 (-142 to +248) | 0.274 | 0.313 | +79.2 | 0.123 | No edge | Lead |
| SPY bollinger_lower_close, hold_5 | ETF at close | 96 | +28.0 (-23 to +75) | 0.172 | 0.258 | +75.5 | 0.005 | No edge | No edge |
| SPY bollinger_lower_close, hold_5 | ETF next open | 96 | +24.8 (-31 to +76) | 0.216 | 0.268 | +70.6 | 0.012 | No edge | No edge |
| SPY bollinger_lower_close, close_above_sma5 | ETF at close | 99 | +37.9 (-8 to +75) | 0.082 | 0.165 | +59.3 | 0.008 | No edge | Lead |
| SPY bollinger_lower_close, close_above_sma5 | ETF next open | 99 | +33.1 (-19 to +74) | 0.124 | 0.213 | +48.4 | 0.035 | No edge | Lead |
| QQQ rsi2_below_10, hold_5 | ETF at close | 193 | -4.9 (-43 to +32) | 0.583 | 0.609 | +56.9 | 0.052 | No edge | No edge |
| QQQ rsi2_below_10, hold_5 | ETF next open | 193 | -15.0 (-52 to +20) | 0.753 | 0.753 | +57.0 | 0.054 | No edge | No edge |
| QQQ rsi2_below_10, close_above_sma5 | ETF at close | 192 | +33.7 (+11 to +55) | 0.008 | 0.032 | +89.3 | 0.002 | Lead | Lead |
| QQQ rsi2_below_10, close_above_sma5 | ETF next open | 192 | +26.4 (+1 to +49) | 0.042 | 0.111 | +90.6 | 0.001 | No edge | Lead |
| QQQ rsi14_below_30, hold_5 | ETF at close | 25 | +276.6 (+198 to +362) | 0.000 | 0.001 | +149.5 | 0.073 | Lead | Lead |
| QQQ rsi14_below_30, hold_5 | ETF next open | 25 | +267.2 (+155 to +389) | 0.000 | 0.001 | +117.6 | 0.140 | Failed holdout | Lead |
| QQQ rsi14_below_30, close_above_sma5 | ETF at close | 26 | +277.8 (+209 to +352) | 0.000 | 0.001 | +264.1 | 0.017 | Lead | Lead |
| QQQ rsi14_below_30, close_above_sma5 | ETF next open | 26 | +267.9 (+185 to +370) | 0.000 | 0.001 | +233.7 | 0.035 | Lead | Lead |
| QQQ bollinger_lower_close, hold_5 | ETF at close | 97 | +27.5 (-22 to +73) | 0.172 | 0.258 | +91.7 | 0.055 | No edge | No edge |
| QQQ bollinger_lower_close, hold_5 | ETF next open | 97 | +25.9 (-29 to +73) | 0.207 | 0.268 | +97.4 | 0.039 | No edge | No edge |
| QQQ bollinger_lower_close, close_above_sma5 | ETF at close | 104 | +59.4 (+26 to +88) | 0.004 | 0.021 | +146.3 | 0.001 | Lead | Lead |
| QQQ bollinger_lower_close, close_above_sma5 | ETF next open | 104 | +59.6 (+20 to +92) | 0.011 | 0.032 | +144.1 | 0.001 | Lead | Lead |

## Forward record (signals after 2026-11-13)

Each forward trade's excess is its gross return minus the development mean of trades of its length. The band applies from 5 trades.

| Strategy | Entry | Forward trades | Mean excess bp | Band lower edge bp | Status |
|---|---|---|---|---|---|
| SPY rsi2_below_10, hold_5 | ETF at close | 0 | – | – | none yet |
| SPY rsi2_below_10, hold_5 | ETF next open | 0 | – | – | none yet |
| SPY rsi2_below_10, close_above_sma5 | ETF at close | 0 | – | – | none yet |
| SPY rsi2_below_10, close_above_sma5 | ETF next open | 0 | – | – | none yet |
| SPY rsi14_below_30, hold_5 | ETF at close | 0 | – | – | none yet |
| SPY rsi14_below_30, hold_5 | ETF next open | 0 | – | – | none yet |
| SPY rsi14_below_30, close_above_sma5 | ETF at close | 0 | – | – | none yet |
| SPY rsi14_below_30, close_above_sma5 | ETF next open | 0 | – | – | none yet |
| SPY bollinger_lower_close, hold_5 | ETF at close | 0 | – | – | none yet |
| SPY bollinger_lower_close, hold_5 | ETF next open | 0 | – | – | none yet |
| SPY bollinger_lower_close, close_above_sma5 | ETF at close | 0 | – | – | none yet |
| SPY bollinger_lower_close, close_above_sma5 | ETF next open | 0 | – | – | none yet |
| QQQ rsi2_below_10, hold_5 | ETF at close | 0 | – | – | none yet |
| QQQ rsi2_below_10, hold_5 | ETF next open | 0 | – | – | none yet |
| QQQ rsi2_below_10, close_above_sma5 | ETF at close | 0 | – | – | none yet |
| QQQ rsi2_below_10, close_above_sma5 | ETF next open | 0 | – | – | none yet |
| QQQ rsi14_below_30, hold_5 | ETF at close | 0 | – | – | none yet |
| QQQ rsi14_below_30, hold_5 | ETF next open | 0 | – | – | none yet |
| QQQ rsi14_below_30, close_above_sma5 | ETF at close | 0 | – | – | none yet |
| QQQ rsi14_below_30, close_above_sma5 | ETF next open | 0 | – | – | none yet |
| QQQ bollinger_lower_close, hold_5 | ETF at close | 0 | – | – | none yet |
| QQQ bollinger_lower_close, hold_5 | ETF next open | 0 | – | – | none yet |
| QQQ bollinger_lower_close, close_above_sma5 | ETF at close | 0 | – | – | none yet |
| QQQ bollinger_lower_close, close_above_sma5 | ETF next open | 0 | – | – | none yet |

## Risk inside trades (development, ETF pricings)

What win rates and averages hide. *MAE* is the worst point a trade reached from its entry, from daily lows (the day's high and low are not ordered). *Without best 3*: the mean net trade if the three best trades are removed. *Costs*: the mean net trade at 2 / 5 / 10 / 20 bp round trip. *Sold next open*: the mean gross trade if the exit is taken at the next morning's open instead of at the close the exit rule looks at.

| Strategy | Entry | Median / worst trade | MAE median / 10th pct / worst | Trades with MAE below -5% / -10% | Without best 3 | Costs 2 / 5 / 10 / 20 bp | Sold next open |
|---|---|---|---|---|---|---|---|
| SPY rsi2_below_10, hold_5 | ETF at close | +0.54% / -12.6% | -1.2% / -4.4% / -13.4% | 16 / 3 | +39.9 | +56.6 / +53.5 / +48.5 / +38.5 | +73.0 |
| SPY rsi2_below_10, hold_5 | ETF next open | +0.53% / -15.8% | -1.3% / -4.2% / -16.6% | 16 / 2 | +23.0 | +37.5 / +34.4 / +29.4 / +19.4 | +53.8 |
| SPY rsi2_below_10, close_above_sma5 | ETF at close | +0.82% / -18.2% | -1.0% / -4.5% / -19.9% | 16 / 5 | +33.2 | +39.5 / +36.5 / +31.5 / +21.4 | +48.6 |
| SPY rsi2_below_10, close_above_sma5 | ETF next open | +0.65% / -21.2% | -1.1% / -4.2% / -22.9% | 15 / 3 | +20.0 | +28.3 / +25.3 / +20.2 / +10.2 | +37.2 |
| SPY rsi14_below_30, hold_5 | ETF at close | +1.29% / -12.6% | -2.0% / -8.2% / -13.4% | 5 / 1 | +26.4 | +143.1 / +140.1 / +135.0 / +124.9 | +190.5 |
| SPY rsi14_below_30, hold_5 | ETF next open | +1.63% / -15.8% | -2.0% / -8.2% / -16.6% | 4 / 1 | +28.6 | +137.5 / +134.4 / +129.4 / +119.2 | +184.8 |
| SPY rsi14_below_30, close_above_sma5 | ETF at close | +0.99% / -18.2% | -1.9% / -8.2% / -19.9% | 5 / 1 | +0.3 | +62.5 / +59.5 / +54.4 / +44.4 | +60.3 |
| SPY rsi14_below_30, close_above_sma5 | ETF next open | +1.54% / -21.2% | -1.6% / -8.2% / -22.9% | 4 / 1 | -13.2 | +77.3 / +74.3 / +69.2 / +59.2 | +73.7 |
| SPY bollinger_lower_close, hold_5 | ETF at close | +0.70% / -12.6% | -1.3% / -4.3% / -13.4% | 9 / 5 | +33.7 | +54.3 / +51.3 / +46.3 / +36.2 | +81.0 |
| SPY bollinger_lower_close, hold_5 | ETF next open | +0.58% / -15.8% | -1.2% / -4.1% / -16.6% | 8 / 2 | +24.8 | +47.5 / +44.5 / +39.5 / +29.4 | +74.0 |
| SPY bollinger_lower_close, close_above_sma5 | ETF at close | +0.95% / -18.2% | -1.2% / -5.6% / -19.9% | 11 / 5 | +45.4 | +56.1 / +53.1 / +48.0 / +38.0 | +60.0 |
| SPY bollinger_lower_close, close_above_sma5 | ETF next open | +0.81% / -21.2% | -1.1% / -4.9% / -22.9% | 10 / 2 | +31.6 | +47.7 / +44.7 / +39.6 / +29.6 | +51.2 |
| QQQ rsi2_below_10, hold_5 | ETF at close | +0.60% / -12.6% | -1.4% / -4.9% / -20.9% | 19 / 4 | +18.1 | +30.3 / +27.3 / +22.3 / +12.2 | +56.1 |
| QQQ rsi2_below_10, hold_5 | ETF next open | +0.26% / -15.8% | -1.5% / -4.8% / -19.7% | 18 / 4 | +4.9 | +15.2 / +12.2 / +7.1 / -2.9 | +40.9 |
| QQQ rsi2_below_10, close_above_sma5 | ETF at close | +1.09% / -11.8% | -1.2% / -5.2% / -20.9% | 20 / 5 | +53.2 | +58.9 / +55.8 / +50.8 / +40.7 | +63.8 |
| QQQ rsi2_below_10, close_above_sma5 | ETF next open | +0.82% / -15.1% | -1.3% / -4.8% / -19.7% | 19 / 4 | +39.7 | +46.5 / +43.5 / +38.4 / +28.4 | +51.3 |
| QQQ rsi14_below_30, hold_5 | ETF at close | +3.12% / -1.8% | -1.4% / -4.9% / -17.2% | 2 / 1 | +251.7 | +311.7 / +308.6 / +303.5 / +293.2 | +322.5 |
| QQQ rsi14_below_30, hold_5 | ETF next open | +3.26% / -5.0% | -1.5% / -4.7% / -10.8% | 2 / 2 | +202.4 | +297.3 / +294.2 / +289.1 / +278.8 | +307.1 |
| QQQ rsi14_below_30, close_above_sma5 | ETF at close | +2.59% / +0.0% | -1.3% / -4.9% / -17.2% | 2 / 1 | +245.4 | +296.4 / +293.3 / +288.1 / +277.8 | +291.7 |
| QQQ rsi14_below_30, close_above_sma5 | ETF next open | +1.70% / -1.6% | -1.5% / -4.0% / -11.6% | 2 / 2 | +177.9 | +281.5 / +278.4 / +273.2 / +263.0 | +277.0 |
| QQQ bollinger_lower_close, hold_5 | ETF at close | +0.58% / -12.6% | -2.0% / -5.6% / -20.9% | 12 / 5 | +38.9 | +62.6 / +59.6 / +54.6 / +44.5 | +86.5 |
| QQQ bollinger_lower_close, hold_5 | ETF next open | +0.73% / -15.8% | -1.9% / -5.8% / -19.7% | 12 / 4 | +29.6 | +56.0 / +53.0 / +48.0 / +37.9 | +79.6 |
| QQQ bollinger_lower_close, close_above_sma5 | ETF at close | +1.23% / -11.8% | -1.7% / -5.4% / -20.9% | 14 / 5 | +74.8 | +83.7 / +80.7 / +75.6 / +65.5 | +85.9 |
| QQQ bollinger_lower_close, close_above_sma5 | ETF next open | +1.13% / -15.1% | -1.4% / -5.5% / -19.7% | 13 / 4 | +62.6 | +78.9 / +75.9 / +70.8 / +60.7 | +80.9 |

## Leveraged-ETF version of the same trades (development, descriptive)

The development trades priced in TQQQ (for QQQ) and UPRO (for SPY), using those funds' own prices from 2010 on, with the same 2 bp cost. No test and no verdict: it shows what the instrument would have done. *x 1x* is the leveraged mean gross trade divided by the 1x mean gross trade on the same trades.

| Strategy | Entry | ETF | Trades | Mean / median net | Win rate | Worst trade | MAE median / worst | x 1x |
|---|---|---|---|---|---|---|---|---|
| SPY rsi2_below_10, hold_5 | ETF at close | UPRO | 192 | +1.57% / +1.35% | 62% | -41.8% | -3.7% / -42.4% | 2.71 |
| SPY rsi2_below_10, hold_5 | ETF next open | UPRO | 192 | +1.02% / +1.45% | 58% | -47.7% | -3.9% / -48.3% | 2.64 |
| SPY rsi2_below_10, close_above_sma5 | ETF at close | UPRO | 188 | +1.02% / +2.35% | 71% | -53.9% | -3.3% / -56.6% | 2.51 |
| SPY rsi2_below_10, close_above_sma5 | ETF next open | UPRO | 188 | +0.75% / +1.86% | 72% | -58.6% | -3.1% / -61.1% | 2.56 |
| SPY rsi14_below_30, hold_5 | ETF at close | UPRO | 24 | +3.78% / +3.71% | 75% | -41.8% | -5.9% / -42.4% | 2.62 |
| SPY rsi14_below_30, hold_5 | ETF next open | UPRO | 24 | +3.90% / +4.52% | 71% | -47.7% | -5.8% / -48.3% | 2.81 |
| SPY rsi14_below_30, close_above_sma5 | ETF at close | UPRO | 24 | +1.27% / +2.94% | 79% | -53.9% | -5.5% / -56.6% | 2.01 |
| SPY rsi14_below_30, close_above_sma5 | ETF next open | UPRO | 24 | +2.22% / +4.52% | 79% | -58.6% | -4.8% / -61.1% | 2.82 |
| SPY bollinger_lower_close, hold_5 | ETF at close | UPRO | 96 | +1.41% / +1.81% | 59% | -41.8% | -4.1% / -42.4% | 2.55 |
| SPY bollinger_lower_close, hold_5 | ETF next open | UPRO | 96 | +1.33% / +1.62% | 58% | -47.7% | -3.5% / -48.3% | 2.73 |
| SPY bollinger_lower_close, close_above_sma5 | ETF at close | UPRO | 99 | +1.40% / +2.62% | 71% | -53.9% | -3.8% / -56.6% | 2.45 |
| SPY bollinger_lower_close, close_above_sma5 | ETF next open | UPRO | 99 | +1.28% / +2.40% | 69% | -58.6% | -3.4% / -61.1% | 2.62 |
| QQQ rsi2_below_10, hold_5 | ETF at close | TQQQ | 192 | +0.78% / +1.59% | 57% | -39.2% | -4.4% / -39.6% | 2.36 |
| QQQ rsi2_below_10, hold_5 | ETF next open | TQQQ | 192 | +0.40% / +0.86% | 54% | -45.2% | -4.5% / -45.6% | 2.19 |
| QQQ rsi2_below_10, close_above_sma5 | ETF at close | TQQQ | 190 | +1.39% / +3.14% | 68% | -41.8% | -3.8% / -47.3% | 2.36 |
| QQQ rsi2_below_10, close_above_sma5 | ETF next open | TQQQ | 190 | +1.12% / +2.30% | 68% | -47.6% | -4.0% / -52.5% | 2.39 |
| QQQ rsi14_below_30, hold_5 | ETF at close | TQQQ | 25 | +8.28% / +7.21% | 80% | -10.2% | -4.6% / -29.0% | 2.64 |
| QQQ rsi14_below_30, hold_5 | ETF next open | TQQQ | 25 | +8.15% / +9.70% | 80% | -23.0% | -4.8% / -37.3% | 2.73 |
| QQQ rsi14_below_30, close_above_sma5 | ETF at close | TQQQ | 26 | +7.81% / +7.03% | 88% | -2.7% | -4.2% / -29.0% | 2.62 |
| QQQ rsi14_below_30, close_above_sma5 | ETF next open | TQQQ | 26 | +7.63% / +5.09% | 92% | -16.6% | -4.5% / -38.2% | 2.70 |
| QQQ bollinger_lower_close, hold_5 | ETF at close | TQQQ | 96 | +1.65% / +1.53% | 56% | -39.2% | -6.0% / -39.6% | 2.43 |
| QQQ bollinger_lower_close, hold_5 | ETF next open | TQQQ | 96 | +1.64% / +1.79% | 57% | -45.2% | -6.0% / -45.6% | 2.65 |
| QQQ bollinger_lower_close, close_above_sma5 | ETF at close | TQQQ | 102 | +2.04% / +3.55% | 76% | -41.8% | -5.1% / -47.3% | 2.39 |
| QQQ bollinger_lower_close, close_above_sma5 | ETF next open | TQQQ | 102 | +2.10% / +3.08% | 75% | -47.6% | -4.2% / -52.5% | 2.57 |

## Return per unit of drawdown (descriptive, not part of the verdict)

CAGR divided by the worst peak-to-trough loss, for the strategy versus exposure-matched buy-and-hold, ETF at the close. A strategy that is fully invested during its trades can earn more per year than the matched benchmark yet still have deeper drawdowns, because the benchmark spreads its smaller exposure over every day. The higher figure is named in brackets.

| Strategy | Development | Holdout |
|---|---|---|
| SPY rsi2_below_10, hold_5 | 0.20 vs 0.39 (buy-and-hold) | 0.52 vs 0.13 (strategy) |
| SPY rsi2_below_10, close_above_sma5 | 0.15 vs 0.39 (buy-and-hold) | 0.36 vs 0.13 (strategy) |
| SPY rsi14_below_30, hold_5 | 0.11 vs 0.38 (buy-and-hold) | 0.04 vs 0.13 (buy-and-hold) |
| SPY rsi14_below_30, close_above_sma5 | 0.03 vs 0.38 (buy-and-hold) | 0.09 vs 0.13 (buy-and-hold) |
| SPY bollinger_lower_close, hold_5 | 0.14 vs 0.39 (buy-and-hold) | 0.25 vs 0.13 (strategy) |
| SPY bollinger_lower_close, close_above_sma5 | 0.14 vs 0.38 (buy-and-hold) | 0.16 vs 0.13 (strategy) |
| QQQ rsi2_below_10, hold_5 | 0.10 vs 0.50 (buy-and-hold) | 0.20 vs 0.03 (strategy) |
| QQQ rsi2_below_10, close_above_sma5 | 0.35 vs 0.49 (buy-and-hold) | 0.35 vs 0.03 (strategy) |
| QQQ rsi14_below_30, hold_5 | 0.39 vs 0.49 (buy-and-hold) | 0.21 vs 0.03 (strategy) |
| QQQ rsi14_below_30, close_above_sma5 | 0.38 vs 0.49 (buy-and-hold) | 0.25 vs 0.04 (strategy) |
| QQQ bollinger_lower_close, hold_5 | 0.17 vs 0.49 (buy-and-hold) | 0.26 vs 0.03 (strategy) |
| QQQ bollinger_lower_close, close_above_sma5 | 0.30 vs 0.49 (buy-and-hold) | 0.45 vs 0.03 (strategy) |

Full-time buy-and-hold at 1x, for reference:

| Symbol | Development CAGR | Max drawdown | CAGR per drawdown | Holdout CAGR | Max drawdown | CAGR per drawdown |
|---|---|---|---|---|---|---|
| SPY | +14.01% | -33.7% | 0.42 | +7.59% | -55.2% | 0.14 |
| QQQ | +18.39% | -35.1% | 0.52 | -0.75% | -83.0% | -0.01 |

## SPY: rsi2_below_10 (v1), exit hold_5 (v1)

Signal: RSI(2) closes below 10 (short-term oversold). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 192 | 192 | 192 | 192 |
| Time in market | 23% | 23% | 23% | 23% |
| Win rate (after costs) | 64% | 58% | 61% | 56% |
| Mean per trade, gross / net bp | +58.6 / +56.6 | +39.5 / +37.5 | +58.6 / +46.1 | +58.6 / +26.0 |
| Median / worst trade, net | +0.54% / -12.55% | +0.53% / -15.75% | +0.44% / -12.64% | +0.24% / -12.82% |
| Average win / loss | +2.08% / -2.08% | +2.01% / -1.91% | +2.06% / -2.04% | +2.04% / -1.98% |
| Worst point inside a trade (MAE): median / worst | -1.2% / -13.4% | -1.3% / -16.6% | -1.2% / -13.4% | -1.2% / -13.4% |
| Excess over same-length trades, bp (p) | +30.3 (0.077) | +14.8 (0.224) | +30.3 (0.077) | +30.3 (0.077) |
| Excess, 90% interval, bp | -5 to +63 | -19 to +47 | -5 to +63 | -5 to +63 |
| Quarters with trades | 67 | 67 | 67 | 67 |
| Share of gross profit from the best 5 trades | 41% | 53% | 41% | 41% |
| CAGR: strategy / risk-matched buy-and-hold | +6.11% / +4.45% | +3.88% / +4.31% | +4.86% / +2.84% | +2.49% / +2.85% |
| Return per unit of volatility: strategy / index | 0.59 / 0.85 | 0.41 / 0.85 | 0.48 / 0.85 | 0.28 / 0.85 |
| v1 random-entry percentile | 97 | 84 | 97 | 97 |
| CAGR: strategy / time-matched buy-and-hold | +6.11% / +3.27% | +3.88% / +3.27% | +4.86% / +2.11% | +2.49% / +2.11% |
| Max drawdown: strategy / matched | -30.7% / -8.4% | -34.1% / -8.4% | -32.4% / -8.5% | -37.5% / -8.5% |
| CAGR per unit of drawdown: strategy / matched | 0.20 / 0.39 | 0.11 / 0.39 | 0.15 / 0.25 | 0.07 / 0.25 |
| **Holdout (1993-2009)** | | | | |
| Trades | 218 | 218 | 218 | 218 |
| Time in market | 26% | 26% | 26% | 26% |
| Win rate (after costs) | 64% | 63% | 62% | 59% |
| Mean per trade, gross / net bp | +86.2 / +84.2 | +66.9 / +64.9 | +86.2 / +73.5 | +86.2 / +53.3 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +2.39% / -1.94% | +2.21% / -1.99% | +2.35% / -1.94% | +2.29% / -1.96% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +68.5 (0.001) | +53.6 (0.005) | +68.5 (0.001) | +68.5 (0.001) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 68 | 68 | 68 | 68 |
| Share of gross profit from the best 5 trades | 33% | 39% | 33% | 33% |
| CAGR: strategy / risk-matched buy-and-hold | +10.74% / +2.70% | +8.10% / +2.63% | +9.23% / +1.14% | +6.45% / +1.14% |
| Return per unit of volatility: strategy / index | 0.90 / 0.47 | 0.72 / 0.47 | 0.79 / 0.47 | 0.57 / 0.47 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +10.74% / +2.27% | +8.10% / +2.27% | +9.23% / +0.97% | +6.45% / +0.97% |
| Max drawdown: strategy / matched | -20.6% / -16.9% | -22.8% / -16.9% | -21.7% / -21.5% | -23.7% / -21.5% |
| CAGR per unit of drawdown: strategy / matched | 0.52 / 0.13 | 0.36 / 0.13 | 0.43 / 0.05 | 0.27 / 0.05 |
| **Verdict (v3)** | No edge | No edge | No edge | No edge |

## SPY: rsi2_below_10 (v1), exit close_above_sma5 (v1)

Signal: RSI(2) closes below 10 (short-term oversold). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 188 | 188 | 188 | 188 |
| Time in market | 16% | 16% | 16% | 16% |
| Win rate (after costs) | 72% | 72% | 71% | 66% |
| Mean per trade, gross / net bp | +41.5 / +39.5 | +30.3 / +28.3 | +41.5 / +32.0 | +41.5 / +11.9 |
| Median / worst trade, net | +0.82% / -18.24% | +0.65% / -21.23% | +0.77% / -18.40% | +0.57% / -18.56% |
| Average win / loss | +1.30% / -1.97% | +1.16% / -2.02% | +1.26% / -2.02% | +1.14% / -1.91% |
| Worst point inside a trade (MAE): median / worst | -1.0% / -19.9% | -1.1% / -22.9% | -1.0% / -19.9% | -1.0% / -19.9% |
| Excess over same-length trades, bp (p) | +21.6 (0.121) | +14.0 (0.215) | +21.6 (0.121) | +21.6 (0.121) |
| Excess, 90% interval, bp | -10 to +50 | -19 to +42 | -10 to +50 | -10 to +50 |
| Quarters with trades | 67 | 67 | 67 | 67 |
| Share of gross profit from the best 5 trades | 25% | 39% | 25% | 25% |
| CAGR: strategy / risk-matched buy-and-hold | +4.16% / +3.32% | +2.83% / +3.22% | +3.28% / +2.12% | +1.00% / +2.07% |
| Return per unit of volatility: strategy / index | 0.46 / 0.85 | 0.34 / 0.85 | 0.38 / 0.85 | 0.15 / 0.85 |
| v1 random-entry percentile | 95 | 86 | 95 | 95 |
| CAGR: strategy / time-matched buy-and-hold | +4.16% / +2.25% | +2.83% / +2.25% | +3.28% / +1.46% | +1.00% / +1.46% |
| Max drawdown: strategy / matched | -27.1% / -5.8% | -30.1% / -5.8% | -28.7% / -5.9% | -34.9% / -5.9% |
| CAGR per unit of drawdown: strategy / matched | 0.15 / 0.39 | 0.09 / 0.39 | 0.11 / 0.25 | 0.03 / 0.25 |
| **Holdout (1993-2009)** | | | | |
| Trades | 212 | 212 | 212 | 212 |
| Time in market | 18% | 18% | 18% | 18% |
| Win rate (after costs) | 75% | 74% | 75% | 69% |
| Mean per trade, gross / net bp | +71.1 / +69.1 | +52.7 / +50.7 | +71.1 / +61.4 | +71.1 / +41.2 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +1.59% / -2.08% | +1.40% / -2.05% | +1.54% / -2.17% | +1.47% / -1.92% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +58.3 (0.000) | +44.3 (0.002) | +58.3 (0.000) | +58.3 (0.000) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 68 | 68 | 68 | 68 |
| Share of gross profit from the best 5 trades | 27% | 33% | 27% | 27% |
| CAGR: strategy / risk-matched buy-and-hold | +8.60% / +2.14% | +6.17% / +2.09% | +7.55% / +0.91% | +4.88% / +0.89% |
| Return per unit of volatility: strategy / index | 0.78 / 0.47 | 0.60 / 0.47 | 0.70 / 0.47 | 0.49 / 0.47 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +8.60% / +1.61% | +6.17% / +1.61% | +7.55% / +0.70% | +4.88% / +0.70% |
| Max drawdown: strategy / matched | -23.7% / -12.0% | -23.7% / -12.0% | -23.7% / -15.3% | -23.7% / -15.3% |
| CAGR per unit of drawdown: strategy / matched | 0.36 / 0.13 | 0.26 / 0.13 | 0.32 / 0.05 | 0.21 / 0.05 |
| **Verdict (v3)** | No edge | No edge | No edge | No edge |

## SPY: rsi14_below_30 (v1), exit hold_5 (v1)

Signal: RSI(14) closes below 30 (classic oversold). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 24 | 24 | 24 | 24 |
| Time in market | 3% | 3% | 3% | 3% |
| Win rate (after costs) | 75% | 71% | 75% | 75% |
| Mean per trade, gross / net bp | +145.2 / +143.1 | +139.5 / +137.5 | +145.2 / +132.5 | +145.2 / +112.2 |
| Median / worst trade, net | +1.29% / -12.55% | +1.63% / -15.75% | +1.18% / -12.64% | +0.98% / -12.82% |
| Average win / loss | +3.29% / -4.14% | +3.68% / -4.21% | +3.18% / -4.24% | +2.97% / -4.43% |
| Worst point inside a trade (MAE): median / worst | -2.0% / -13.4% | -2.0% / -16.6% | -2.0% / -13.4% | -2.0% / -13.4% |
| Excess over same-length trades, bp (p) | +116.8 (0.009) | +114.8 (0.067) | +116.8 (0.009) | +116.8 (0.009) |
| Excess, 90% interval, bp | +38 to +203 | -11 to +253 | +38 to +203 | +38 to +203 |
| Quarters with trades | 17 | 17 | 17 | 17 |
| Share of gross profit from the best 5 trades | 105% | 112% | 105% | 105% |
| CAGR: strategy / risk-matched buy-and-hold | +1.87% / +1.09% | +1.77% / +1.04% | +1.72% / +0.71% | +1.43% / +0.72% |
| Return per unit of volatility: strategy / index | 0.28 / 0.85 | 0.28 / 0.85 | 0.26 / 0.85 | 0.22 / 0.85 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +1.87% / +0.41% | +1.77% / +0.41% | +1.72% / +0.27% | +1.43% / +0.27% |
| Max drawdown: strategy / matched | -17.6% / -1.1% | -21.0% / -1.1% | -17.9% / -1.1% | -18.4% / -1.1% |
| CAGR per unit of drawdown: strategy / matched | 0.11 / 0.38 | 0.08 / 0.38 | 0.10 / 0.25 | 0.08 / 0.25 |
| **Holdout (1993-2009)** | | | | |
| Trades | 27 | 27 | 27 | 27 |
| Time in market | 3% | 3% | 3% | 3% |
| Win rate (after costs) | 48% | 48% | 48% | 41% |
| Mean per trade, gross / net bp | +52.5 / +50.5 | +60.1 / +58.1 | +52.5 / +39.8 | +52.5 / +19.7 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +3.34% / -2.13% | +3.75% / -2.36% | +3.23% / -2.23% | +3.59% / -2.14% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +34.8 (0.246) | +46.8 (0.220) | +34.8 (0.246) | +34.8 (0.246) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 20 | 20 | 20 | 20 |
| Share of gross profit from the best 5 trades | 206% | 221% | 206% | 206% |
| CAGR: strategy / risk-matched buy-and-hold | +0.71% / +0.58% | +0.80% / +0.58% | +0.53% / +0.26% | +0.21% / +0.26% |
| Return per unit of volatility: strategy / index | 0.13 / 0.47 | 0.15 / 0.47 | 0.11 / 0.47 | 0.06 / 0.47 |
| v1 random-entry percentile | 77 | 84 | 77 | 77 |
| CAGR: strategy / time-matched buy-and-hold | +0.71% / +0.29% | +0.80% / +0.29% | +0.53% / +0.13% | +0.21% / +0.13% |
| Max drawdown: strategy / matched | -18.9% / -2.2% | -15.5% / -2.2% | -19.7% / -2.8% | -22.3% / -2.8% |
| CAGR per unit of drawdown: strategy / matched | 0.04 / 0.13 | 0.05 / 0.13 | 0.03 / 0.05 | 0.01 / 0.05 |
| **Verdict (v3)** | Failed holdout | No edge | Failed holdout | Failed holdout |

## SPY: rsi14_below_30 (v1), exit close_above_sma5 (v1)

Signal: RSI(14) closes below 30 (classic oversold). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 24 | 24 | 24 | 24 |
| Time in market | 2% | 2% | 2% | 2% |
| Win rate (after costs) | 79% | 79% | 79% | 79% |
| Mean per trade, gross / net bp | +64.5 / +62.5 | +79.3 / +77.3 | +64.5 / +54.9 | +64.5 / +34.7 |
| Median / worst trade, net | +0.99% / -18.24% | +1.54% / -21.23% | +0.93% / -18.40% | +0.72% / -18.56% |
| Average win / loss | +2.02% / -4.67% | +2.45% / -5.60% | +1.95% / -4.77% | +1.75% / -4.97% |
| Worst point inside a trade (MAE): median / worst | -1.9% / -19.9% | -1.6% / -22.9% | -1.9% / -19.9% | -1.9% / -19.9% |
| Excess over same-length trades, bp (p) | +44.9 (0.288) | +63.3 (0.274) | +44.9 (0.288) | +44.9 (0.288) |
| Excess, 90% interval, bp | -136 to +189 | -142 to +248 | -136 to +189 | -136 to +189 |
| Quarters with trades | 17 | 17 | 17 | 17 |
| Share of gross profit from the best 5 trades | 131% | 141% | 131% | 131% |
| CAGR: strategy / risk-matched buy-and-hold | +0.74% / +0.86% | +0.88% / +0.84% | +0.63% / +0.56% | +0.34% / +0.55% |
| Return per unit of volatility: strategy / index | 0.14 / 0.85 | 0.16 / 0.85 | 0.12 / 0.85 | 0.08 / 0.85 |
| v1 random-entry percentile | 88 | 97 | 88 | 88 |
| CAGR: strategy / time-matched buy-and-hold | +0.74% / +0.28% | +0.88% / +0.28% | +0.63% / +0.19% | +0.34% / +0.19% |
| Max drawdown: strategy / matched | -23.5% / -0.7% | -22.7% / -0.7% | -23.6% / -0.8% | -23.8% / -0.8% |
| CAGR per unit of drawdown: strategy / matched | 0.03 / 0.38 | 0.04 / 0.38 | 0.03 / 0.25 | 0.01 / 0.25 |
| **Holdout (1993-2009)** | | | | |
| Trades | 24 | 24 | 24 | 24 |
| Time in market | 2% | 2% | 2% | 2% |
| Win rate (after costs) | 75% | 62% | 75% | 67% |
| Mean per trade, gross / net bp | +101.7 / +99.7 | +88.2 / +86.1 | +101.7 / +91.5 | +101.7 / +71.3 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +2.25% / -2.76% | +2.63% / -2.08% | +2.19% / -2.90% | +2.25% / -2.37% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +88.4 (0.090) | +79.2 (0.123) | +88.4 (0.090) | +88.4 (0.090) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 20 | 20 | 20 | 20 |
| Share of gross profit from the best 5 trades | 99% | 133% | 99% | 99% |
| CAGR: strategy / risk-matched buy-and-hold | +1.35% / +0.43% | +1.14% / +0.44% | +1.23% / +0.19% | +0.94% / +0.19% |
| Return per unit of volatility: strategy / index | 0.24 / 0.47 | 0.21 / 0.47 | 0.22 / 0.47 | 0.18 / 0.47 |
| v1 random-entry percentile | 98 | 96 | 98 | 98 |
| CAGR: strategy / time-matched buy-and-hold | +1.35% / +0.20% | +1.14% / +0.20% | +1.23% / +0.09% | +0.94% / +0.09% |
| Max drawdown: strategy / matched | -15.7% / -1.5% | -16.0% / -1.5% | -16.5% / -1.9% | -18.9% / -1.9% |
| CAGR per unit of drawdown: strategy / matched | 0.09 / 0.13 | 0.07 / 0.13 | 0.07 / 0.05 | 0.05 / 0.05 |
| **Verdict (v3)** | No edge | No edge | No edge | No edge |

## SPY: bollinger_lower_close (v1), exit hold_5 (v1)

Signal: Close below the lower Bollinger band (20 days, 2 standard deviations). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 96 | 96 | 96 | 96 |
| Time in market | 11% | 11% | 11% | 11% |
| Win rate (after costs) | 59% | 59% | 59% | 56% |
| Mean per trade, gross / net bp | +56.4 / +54.3 | +49.5 / +47.5 | +56.4 / +43.9 | +56.4 / +23.7 |
| Median / worst trade, net | +0.70% / -12.55% | +0.58% / -15.75% | +0.60% / -12.64% | +0.40% / -12.82% |
| Average win / loss | +2.44% / -2.22% | +2.35% / -2.26% | +2.33% / -2.32% | +2.24% / -2.34% |
| Worst point inside a trade (MAE): median / worst | -1.3% / -13.4% | -1.2% / -16.6% | -1.3% / -13.4% | -1.3% / -13.4% |
| Excess over same-length trades, bp (p) | +28.0 (0.172) | +24.8 (0.216) | +28.0 (0.172) | +28.0 (0.172) |
| Excess, 90% interval, bp | -23 to +75 | -31 to +76 | -23 to +75 | -23 to +75 |
| Quarters with trades | 57 | 57 | 57 | 57 |
| Share of gross profit from the best 5 trades | 58% | 70% | 58% | 58% |
| CAGR: strategy / risk-matched buy-and-hold | +2.86% / +2.60% | +2.42% / +2.55% | +2.25% / +1.68% | +1.09% / +1.69% |
| Return per unit of volatility: strategy / index | 0.36 / 0.85 | 0.31 / 0.85 | 0.29 / 0.85 | 0.16 / 0.85 |
| v1 random-entry percentile | 90 | 88 | 90 | 90 |
| CAGR: strategy / time-matched buy-and-hold | +2.86% / +1.64% | +2.42% / +1.64% | +2.25% / +1.07% | +1.09% / +1.07% |
| Max drawdown: strategy / matched | -19.9% / -4.3% | -23.4% / -4.3% | -20.5% / -4.3% | -23.0% / -4.3% |
| CAGR per unit of drawdown: strategy / matched | 0.14 / 0.39 | 0.10 / 0.39 | 0.11 / 0.25 | 0.05 / 0.25 |
| **Holdout (1993-2009)** | | | | |
| Trades | 97 | 97 | 97 | 97 |
| Time in market | 11% | 11% | 11% | 11% |
| Win rate (after costs) | 62% | 62% | 59% | 56% |
| Mean per trade, gross / net bp | +93.1 / +91.1 | +83.9 / +81.8 | +93.1 / +80.4 | +93.1 / +60.2 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +2.54% / -1.73% | +2.52% / -1.94% | +2.56% / -1.70% | +2.50% / -1.78% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +75.5 (0.005) | +70.6 (0.012) | +75.5 (0.005) | +75.5 (0.005) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 52 | 52 | 52 | 52 |
| Share of gross profit from the best 5 trades | 50% | 57% | 50% | 50% |
| CAGR: strategy / risk-matched buy-and-hold | +5.06% / +1.40% | +4.49% / +1.41% | +4.42% / +0.62% | +3.22% / +0.62% |
| Return per unit of volatility: strategy / index | 0.58 / 0.47 | 0.52 / 0.47 | 0.52 / 0.47 | 0.39 / 0.47 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +5.06% / +1.04% | +4.49% / +1.04% | +4.42% / +0.46% | +3.22% / +0.46% |
| Max drawdown: strategy / matched | -20.2% / -7.8% | -18.2% / -7.8% | -20.3% / -9.9% | -20.4% / -9.9% |
| CAGR per unit of drawdown: strategy / matched | 0.25 / 0.13 | 0.25 / 0.13 | 0.22 / 0.05 | 0.16 / 0.05 |
| **Verdict (v3)** | No edge | No edge | No edge | No edge |

## SPY: bollinger_lower_close (v1), exit close_above_sma5 (v1)

Signal: Close below the lower Bollinger band (20 days, 2 standard deviations). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 99 | 99 | 99 | 99 |
| Time in market | 8% | 8% | 8% | 8% |
| Win rate (after costs) | 73% | 70% | 70% | 69% |
| Mean per trade, gross / net bp | +58.1 / +56.1 | +49.7 / +47.7 | +58.1 / +48.4 | +58.1 / +28.3 |
| Median / worst trade, net | +0.95% / -18.24% | +0.81% / -21.23% | +0.87% / -18.40% | +0.67% / -18.56% |
| Average win / loss | +1.50% / -1.94% | +1.50% / -1.88% | +1.50% / -1.85% | +1.32% / -1.99% |
| Worst point inside a trade (MAE): median / worst | -1.2% / -19.9% | -1.1% / -22.9% | -1.2% / -19.9% | -1.2% / -19.9% |
| Excess over same-length trades, bp (p) | +37.9 (0.082) | +33.1 (0.124) | +37.9 (0.082) | +37.9 (0.082) |
| Excess, 90% interval, bp | -8 to +75 | -19 to +74 | -8 to +75 | -8 to +75 |
| Quarters with trades | 57 | 57 | 57 | 57 |
| Share of gross profit from the best 5 trades | 31% | 52% | 31% | 31% |
| CAGR: strategy / risk-matched buy-and-hold | +3.14% / +2.17% | +2.57% / +2.14% | +2.67% / +1.40% | +1.47% / +1.37% |
| Return per unit of volatility: strategy / index | 0.39 / 0.85 | 0.33 / 0.85 | 0.34 / 0.85 | 0.21 / 0.85 |
| v1 random-entry percentile | 98 | 97 | 98 | 98 |
| CAGR: strategy / time-matched buy-and-hold | +3.14% / +1.21% | +2.57% / +1.21% | +2.67% / +0.79% | +1.47% / +0.79% |
| Max drawdown: strategy / matched | -22.3% / -3.1% | -22.7% / -3.1% | -22.4% / -3.2% | -22.6% / -3.2% |
| CAGR per unit of drawdown: strategy / matched | 0.14 / 0.38 | 0.11 / 0.38 | 0.12 / 0.25 | 0.07 / 0.25 |
| **Holdout (1993-2009)** | | | | |
| Trades | 96 | 96 | 96 | 96 |
| Time in market | 9% | 9% | 9% | 9% |
| Win rate (after costs) | 72% | 67% | 70% | 62% |
| Mean per trade, gross / net bp | +73.4 / +71.4 | +58.1 / +56.1 | +73.4 / +62.6 | +73.4 / +42.5 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +1.83% / -2.14% | +1.90% / -2.12% | +1.81% / -2.11% | +1.81% / -1.89% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +59.3 (0.008) | +48.4 (0.035) | +59.3 (0.008) | +59.3 (0.008) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 52 | 52 | 52 | 52 |
| Share of gross profit from the best 5 trades | 44% | 63% | 44% | 44% |
| CAGR: strategy / risk-matched buy-and-hold | +3.87% / +1.25% | +2.96% / +1.26% | +3.36% / +0.55% | +2.19% / +0.54% |
| Return per unit of volatility: strategy / index | 0.46 / 0.47 | 0.36 / 0.47 | 0.41 / 0.47 | 0.29 / 0.47 |
| v1 random-entry percentile | 100 | 98 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +3.87% / +0.82% | +2.96% / +0.82% | +3.36% / +0.37% | +2.19% / +0.37% |
| Max drawdown: strategy / matched | -23.7% / -6.2% | -23.7% / -6.2% | -23.7% / -7.8% | -23.7% / -7.8% |
| CAGR per unit of drawdown: strategy / matched | 0.16 / 0.13 | 0.12 / 0.13 | 0.14 / 0.05 | 0.09 / 0.05 |
| **Verdict (v3)** | No edge | No edge | No edge | No edge |

## QQQ: rsi2_below_10 (v1), exit hold_5 (v1)

Signal: RSI(2) closes below 10 (short-term oversold). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 193 | 193 | 193 | 193 |
| Time in market | 23% | 23% | 23% | 23% |
| Win rate (after costs) | 59% | 58% | 57% | 54% |
| Mean per trade, gross / net bp | +32.3 / +30.3 | +17.2 / +15.2 | +32.3 / +19.8 | +32.3 / -0.2 |
| Median / worst trade, net | +0.60% / -12.56% | +0.26% / -15.83% | +0.50% / -12.64% | +0.30% / -12.82% |
| Average win / loss | +2.25% / -2.44% | +2.00% / -2.40% | +2.20% / -2.45% | +2.12% / -2.48% |
| Worst point inside a trade (MAE): median / worst | -1.4% / -20.9% | -1.5% / -19.7% | -1.4% / -20.9% | -1.4% / -20.9% |
| Excess over same-length trades, bp (p) | -4.9 (0.583) | -15.0 (0.753) | -4.9 (0.583) | -4.9 (0.583) |
| Excess, 90% interval, bp | -43 to +32 | -52 to +20 | -43 to +32 | -43 to +32 |
| Quarters with trades | 67 | 67 | 67 | 67 |
| Share of gross profit from the best 5 trades | 58% | 93% | 58% | 58% |
| CAGR: strategy / risk-matched buy-and-hold | +2.93% / +5.36% | +1.20% / +5.19% | +1.71% / +3.88% | -0.60% / +3.89% |
| Return per unit of volatility: strategy / index | 0.30 / 0.92 | 0.16 / 0.92 | 0.20 / 0.92 | 0.01 / 0.92 |
| v1 random-entry percentile | 42 | 21 | 42 | 42 |
| CAGR: strategy / time-matched buy-and-hold | +2.93% / +4.31% | +1.20% / +4.31% | +1.71% / +3.13% | -0.60% / +3.13% |
| Max drawdown: strategy / matched | -30.4% / -8.7% | -40.4% / -8.7% | -33.7% / -9.6% | -40.4% / -9.6% |
| CAGR per unit of drawdown: strategy / matched | 0.10 / 0.50 | 0.03 / 0.50 | 0.05 / 0.32 | -0.01 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 145 | 145 | 145 | 145 |
| Time in market | 27% | 27% | 27% | 27% |
| Win rate (after costs) | 54% | 54% | 54% | 51% |
| Mean per trade, gross / net bp | +65.2 / +63.2 | +59.2 / +57.2 | +65.2 / +52.6 | +65.2 / +32.4 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +3.82% / -3.18% | +3.64% / -3.10% | +3.76% / -3.23% | +3.75% / -3.24% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +56.9 (0.052) | +57.0 (0.054) | +56.9 (0.052) | +56.9 (0.052) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 44 | 44 | 44 | 44 |
| Share of gross profit from the best 5 trades | 69% | 70% | 69% | 69% |
| CAGR: strategy / risk-matched buy-and-hold | +7.34% / +1.04% | +6.60% / +1.04% | +5.84% / -0.55% | +3.03% / -0.55% |
| Return per unit of volatility: strategy / index | 0.44 / 0.15 | 0.41 / 0.15 | 0.37 / 0.15 | 0.25 / 0.15 |
| v1 random-entry percentile | 94 | 94 | 94 | 94 |
| CAGR: strategy / time-matched buy-and-hold | +7.34% / +0.95% | +6.60% / +0.95% | +5.84% / -0.39% | +3.03% / -0.39% |
| Max drawdown: strategy / matched | -36.2% / -33.2% | -32.8% / -33.2% | -37.6% / -35.4% | -40.3% / -35.4% |
| CAGR per unit of drawdown: strategy / matched | 0.20 / 0.03 | 0.20 / 0.03 | 0.16 / -0.01 | 0.08 / -0.01 |
| **Verdict (v3)** | No edge | No edge | No edge | No edge |

## QQQ: rsi2_below_10 (v1), exit close_above_sma5 (v1)

Signal: RSI(2) closes below 10 (short-term oversold). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 192 | 192 | 192 | 192 |
| Time in market | 17% | 17% | 17% | 17% |
| Win rate (after costs) | 70% | 70% | 68% | 65% |
| Mean per trade, gross / net bp | +60.9 / +58.9 | +48.5 / +46.5 | +60.9 / +50.9 | +60.9 / +30.8 |
| Median / worst trade, net | +1.09% / -11.77% | +0.82% / -15.08% | +1.02% / -11.94% | +0.82% / -12.12% |
| Average win / loss | +1.54% / -1.65% | +1.38% / -1.65% | +1.52% / -1.66% | +1.38% / -1.70% |
| Worst point inside a trade (MAE): median / worst | -1.2% / -20.9% | -1.3% / -19.7% | -1.2% / -20.9% | -1.2% / -20.9% |
| Excess over same-length trades, bp (p) | +33.7 (0.008) | +26.4 (0.042) | +33.7 (0.008) | +33.7 (0.008) |
| Excess, 90% interval, bp | +11 to +55 | +1 to +49 | +11 to +55 | +11 to +55 |
| Quarters with trades | 67 | 67 | 67 | 67 |
| Share of gross profit from the best 5 trades | 16% | 23% | 16% | 16% |
| CAGR: strategy / risk-matched buy-and-hold | +6.67% / +4.32% | +5.17% / +4.15% | +5.71% / +3.11% | +3.32% / +3.03% |
| Return per unit of volatility: strategy / index | 0.61 / 0.92 | 0.51 / 0.92 | 0.54 / 0.92 | 0.35 / 0.92 |
| v1 random-entry percentile | 98 | 96 | 98 | 98 |
| CAGR: strategy / time-matched buy-and-hold | +6.67% / +3.13% | +5.17% / +3.13% | +5.71% / +2.28% | +3.32% / +2.28% |
| Max drawdown: strategy / matched | -18.9% / -6.3% | -22.2% / -6.3% | -19.3% / -7.0% | -20.1% / -7.0% |
| CAGR per unit of drawdown: strategy / matched | 0.35 / 0.49 | 0.23 / 0.49 | 0.30 / 0.32 | 0.17 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 143 | 143 | 143 | 143 |
| Time in market | 20% | 20% | 20% | 20% |
| Win rate (after costs) | 71% | 73% | 70% | 67% |
| Mean per trade, gross / net bp | +95.8 / +93.7 | +90.9 / +88.9 | +95.8 / +85.6 | +95.8 / +65.4 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +2.59% / -3.03% | +2.35% / -3.00% | +2.55% / -3.09% | +2.45% / -3.01% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +89.3 (0.002) | +90.6 (0.001) | +89.3 (0.002) | +89.3 (0.002) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 44 | 44 | 44 | 44 |
| Share of gross profit from the best 5 trades | 40% | 42% | 40% | 40% |
| CAGR: strategy / risk-matched buy-and-hold | +12.02% / +0.92% | +11.36% / +0.91% | +10.81% / -0.34% | +7.91% / -0.33% |
| Return per unit of volatility: strategy / index | 0.68 / 0.15 | 0.66 / 0.15 | 0.63 / 0.15 | 0.50 / 0.15 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +12.02% / +0.80% | +11.36% / +0.80% | +10.81% / -0.21% | +7.91% / -0.21% |
| Max drawdown: strategy / matched | -34.2% / -26.0% | -34.8% / -26.0% | -35.2% / -27.8% | -36.7% / -27.8% |
| CAGR per unit of drawdown: strategy / matched | 0.35 / 0.03 | 0.33 / 0.03 | 0.31 / -0.01 | 0.22 / -0.01 |
| **Verdict (v3)** | Lead | No edge | Lead | Lead |

## QQQ: rsi14_below_30 (v1), exit hold_5 (v1)

Signal: RSI(14) closes below 30 (classic oversold). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 25 | 25 | 25 | 25 |
| Time in market | 3% | 3% | 3% | 3% |
| Win rate (after costs) | 88% | 80% | 84% | 80% |
| Mean per trade, gross / net bp | +313.8 / +311.7 | +299.4 / +297.3 | +313.8 / +300.7 | +313.8 / +280.1 |
| Median / worst trade, net | +3.12% / -1.81% | +3.26% / -5.05% | +3.02% / -1.91% | +2.81% / -2.11% |
| Average win / loss | +3.67% / -0.97% | +4.27% / -2.21% | +3.74% / -0.83% | +3.71% / -0.85% |
| Worst point inside a trade (MAE): median / worst | -1.4% / -17.2% | -1.5% / -10.8% | -1.4% / -17.2% | -1.4% / -17.2% |
| Excess over same-length trades, bp (p) | +276.6 (0.000) | +267.2 (0.000) | +276.6 (0.000) | +276.6 (0.000) |
| Excess, 90% interval, bp | +198 to +362 | +155 to +389 | +198 to +362 | +198 to +362 |
| Quarters with trades | 21 | 21 | 21 | 21 |
| Share of gross profit from the best 5 trades | 44% | 57% | 44% | 44% |
| CAGR: strategy / risk-matched buy-and-hold | +4.61% / +1.14% | +4.34% / +1.08% | +4.45% / +0.84% | +4.14% / +0.84% |
| Return per unit of volatility: strategy / index | 0.64 / 0.92 | 0.64 / 0.92 | 0.62 / 0.92 | 0.58 / 0.92 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +4.61% / +0.56% | +4.34% / +0.56% | +4.45% / +0.41% | +4.14% / +0.41% |
| Max drawdown: strategy / matched | -12.0% / -1.1% | -12.3% / -1.1% | -12.0% / -1.3% | -12.0% / -1.3% |
| CAGR per unit of drawdown: strategy / matched | 0.39 / 0.49 | 0.35 / 0.49 | 0.37 / 0.32 | 0.35 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 26 | 26 | 26 | 26 |
| Time in market | 5% | 5% | 5% | 5% |
| Win rate (after costs) | 69% | 50% | 65% | 65% |
| Mean per trade, gross / net bp | +157.8 / +155.8 | +119.8 / +117.8 | +157.8 / +144.8 | +157.8 / +124.5 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +3.98% / -3.89% | +5.13% / -2.78% | +4.10% / -3.56% | +3.89% / -3.75% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +149.5 (0.073) | +117.6 (0.140) | +149.5 (0.073) | +149.5 (0.073) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 15 | 15 | 15 | 15 |
| Share of gross profit from the best 5 trades | 126% | 161% | 126% | 126% |
| CAGR: strategy / risk-matched buy-and-hold | +3.38% / +0.36% | +2.46% / +0.36% | +3.11% / -0.03% | +2.62% / -0.03% |
| Return per unit of volatility: strategy / index | 0.33 / 0.15 | 0.26 / 0.15 | 0.31 / 0.15 | 0.27 / 0.15 |
| v1 random-entry percentile | 96 | 92 | 96 | 96 |
| CAGR: strategy / time-matched buy-and-hold | +3.38% / +0.23% | +2.46% / +0.23% | +3.11% / -0.01% | +2.62% / -0.01% |
| Max drawdown: strategy / matched | -15.8% / -6.6% | -16.8% / -6.6% | -16.7% / -7.2% | -18.9% / -7.2% |
| CAGR per unit of drawdown: strategy / matched | 0.21 / 0.03 | 0.15 / 0.03 | 0.19 / -0.00 | 0.14 / -0.00 |
| **Verdict (v3)** | Lead | Failed holdout | Lead | Lead |

## QQQ: rsi14_below_30 (v1), exit close_above_sma5 (v1)

Signal: RSI(14) closes below 30 (classic oversold). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 26 | 26 | 26 | 26 |
| Time in market | 2% | 2% | 2% | 2% |
| Win rate (after costs) | 100% | 92% | 96% | 96% |
| Mean per trade, gross / net bp | +298.4 / +296.4 | +283.5 / +281.5 | +298.4 / +289.8 | +298.4 / +269.2 |
| Median / worst trade, net | +2.59% / +0.01% | +1.70% / -1.63% | +2.51% / -0.09% | +2.30% / -0.29% |
| Average win / loss | +2.96% / – | +3.12% / -0.87% | +3.02% / -0.09% | +2.81% / -0.29% |
| Worst point inside a trade (MAE): median / worst | -1.3% / -17.2% | -1.5% / -11.6% | -1.3% / -17.2% | -1.3% / -17.2% |
| Excess over same-length trades, bp (p) | +277.8 (0.000) | +267.9 (0.000) | +277.8 (0.000) | +277.8 (0.000) |
| Excess, 90% interval, bp | +209 to +352 | +185 to +370 | +209 to +352 | +209 to +352 |
| Quarters with trades | 21 | 21 | 21 | 21 |
| Share of gross profit from the best 5 trades | 39% | 55% | 39% | 39% |
| CAGR: strategy / risk-matched buy-and-hold | +4.58% / +0.82% | +4.30% / +0.77% | +4.48% / +0.60% | +4.16% / +0.59% |
| Return per unit of volatility: strategy / index | 0.66 / 0.92 | 0.66 / 0.92 | 0.65 / 0.92 | 0.62 / 0.92 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +4.58% / +0.32% | +4.30% / +0.32% | +4.48% / +0.24% | +4.16% / +0.24% |
| Max drawdown: strategy / matched | -12.0% / -0.7% | -12.0% / -0.7% | -12.0% / -0.7% | -12.0% / -0.7% |
| CAGR per unit of drawdown: strategy / matched | 0.38 / 0.49 | 0.36 / 0.49 | 0.37 / 0.32 | 0.35 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 23 | 23 | 23 | 23 |
| Time in market | 3% | 3% | 3% | 3% |
| Win rate (after costs) | 83% | 78% | 83% | 83% |
| Mean per trade, gross / net bp | +270.3 / +268.2 | +233.7 / +231.7 | +270.3 / +260.3 | +270.3 / +239.8 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +4.49% / -5.89% | +4.25% / -4.65% | +4.42% / -6.04% | +4.21% / -6.23% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +264.1 (0.017) | +233.7 (0.035) | +264.1 (0.017) | +264.1 (0.017) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 14 | 14 | 14 | 14 |
| Share of gross profit from the best 5 trades | 78% | 89% | 78% | 78% |
| CAGR: strategy / risk-matched buy-and-hold | +5.48% / +0.26% | +4.69% / +0.26% | +5.30% / -0.01% | +4.86% / -0.01% |
| Return per unit of volatility: strategy / index | 0.55 / 0.15 | 0.47 / 0.15 | 0.54 / 0.15 | 0.50 / 0.15 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +5.48% / +0.15% | +4.69% / +0.15% | +5.30% / -0.00% | +4.86% / -0.00% |
| Max drawdown: strategy / matched | -22.1% / -4.3% | -23.3% / -4.3% | -22.4% / -4.6% | -22.7% / -4.6% |
| CAGR per unit of drawdown: strategy / matched | 0.25 / 0.04 | 0.20 / 0.04 | 0.24 / -0.00 | 0.21 / -0.00 |
| **Verdict (v3)** | Lead | Lead | Lead | Lead |

## QQQ: bollinger_lower_close (v1), exit hold_5 (v1)

Signal: Close below the lower Bollinger band (20 days, 2 standard deviations). Exit: Exit at the close five sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 97 | 97 | 97 | 97 |
| Time in market | 11% | 11% | 11% | 11% |
| Win rate (after costs) | 57% | 59% | 56% | 55% |
| Mean per trade, gross / net bp | +64.6 / +62.6 | +58.0 / +56.0 | +64.6 / +52.1 | +64.6 / +32.0 |
| Median / worst trade, net | +0.58% / -12.56% | +0.73% / -15.83% | +0.48% / -12.64% | +0.28% / -12.82% |
| Average win / loss | +2.88% / -2.33% | +2.81% / -2.65% | +2.82% / -2.37% | +2.67% / -2.51% |
| Worst point inside a trade (MAE): median / worst | -2.0% / -20.9% | -1.9% / -19.7% | -2.0% / -20.9% | -2.0% / -20.9% |
| Excess over same-length trades, bp (p) | +27.5 (0.172) | +25.9 (0.207) | +27.5 (0.172) | +27.5 (0.172) |
| Excess, 90% interval, bp | -22 to +73 | -29 to +73 | -22 to +73 | -22 to +73 |
| Quarters with trades | 49 | 49 | 49 | 49 |
| Share of gross profit from the best 5 trades | 58% | 70% | 58% | 58% |
| CAGR: strategy / risk-matched buy-and-hold | +3.33% / +3.34% | +2.89% / +3.27% | +2.71% / +2.43% | +1.53% / +2.43% |
| Return per unit of volatility: strategy / index | 0.36 / 0.92 | 0.32 / 0.92 | 0.30 / 0.92 | 0.19 / 0.92 |
| v1 random-entry percentile | 84 | 84 | 84 | 84 |
| CAGR: strategy / time-matched buy-and-hold | +3.33% / +2.17% | +2.89% / +2.17% | +2.71% / +1.59% | +1.53% / +1.59% |
| Max drawdown: strategy / matched | -19.2% / -4.4% | -23.7% / -4.4% | -21.5% / -4.9% | -25.8% / -4.9% |
| CAGR per unit of drawdown: strategy / matched | 0.17 / 0.49 | 0.12 / 0.49 | 0.13 / 0.32 | 0.06 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 66 | 66 | 66 | 66 |
| Time in market | 12% | 12% | 12% | 12% |
| Win rate (after costs) | 61% | 62% | 61% | 58% |
| Mean per trade, gross / net bp | +100.1 / +98.1 | +99.6 / +97.6 | +100.1 / +87.3 | +100.1 / +67.1 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +3.61% / -3.06% | +3.49% / -3.15% | +3.50% / -3.17% | +3.47% / -3.13% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +91.7 (0.055) | +97.4 (0.039) | +91.7 (0.055) | +91.7 (0.055) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 32 | 32 | 32 | 32 |
| Share of gross profit from the best 5 trades | 85% | 78% | 85% | 85% |
| CAGR: strategy / risk-matched buy-and-hold | +5.51% / +0.66% | +5.50% / +0.65% | +4.82% / -0.13% | +3.55% / -0.13% |
| Return per unit of volatility: strategy / index | 0.42 / 0.15 | 0.43 / 0.15 | 0.38 / 0.15 | 0.30 / 0.15 |
| v1 random-entry percentile | 95 | 96 | 95 | 95 |
| CAGR: strategy / time-matched buy-and-hold | +5.51% / +0.54% | +5.50% / +0.54% | +4.82% / -0.07% | +3.55% / -0.07% |
| Max drawdown: strategy / matched | -20.8% / -16.3% | -19.0% / -16.3% | -22.8% / -17.6% | -27.2% / -17.6% |
| CAGR per unit of drawdown: strategy / matched | 0.26 / 0.03 | 0.29 / 0.03 | 0.21 / -0.00 | 0.13 / -0.00 |
| **Verdict (v3)** | No edge | No edge | No edge | No edge |

## QQQ: bollinger_lower_close (v1), exit close_above_sma5 (v1)

Signal: Close below the lower Bollinger band (20 days, 2 standard deviations). Exit: Exit at the first close above the 5-day SMA, at most ten sessions after the signal.

| | ETF at close | ETF next open | Perp, maker | Perp, taker |
|---|---|---|---|---|
| **Development (2010-01-01 to 2026-11-13)** | | | | |
| Trades | 104 | 104 | 104 | 104 |
| Time in market | 9% | 9% | 9% | 9% |
| Win rate (after costs) | 80% | 74% | 78% | 74% |
| Mean per trade, gross / net bp | +85.7 / +83.7 | +80.9 / +78.9 | +85.7 / +76.0 | +85.7 / +55.8 |
| Median / worst trade, net | +1.23% / -11.77% | +1.13% / -15.08% | +1.16% / -11.94% | +0.96% / -12.12% |
| Average win / loss | +1.63% / -2.30% | +1.73% / -1.90% | +1.60% / -2.21% | +1.48% / -2.06% |
| Worst point inside a trade (MAE): median / worst | -1.7% / -20.9% | -1.4% / -19.7% | -1.7% / -20.9% | -1.7% / -20.9% |
| Excess over same-length trades, bp (p) | +59.4 (0.004) | +59.6 (0.011) | +59.4 (0.004) | +59.4 (0.004) |
| Excess, 90% interval, bp | +26 to +88 | +20 to +92 | +26 to +88 | +26 to +88 |
| Quarters with trades | 49 | 49 | 49 | 49 |
| Share of gross profit from the best 5 trades | 21% | 32% | 21% | 21% |
| CAGR: strategy / risk-matched buy-and-hold | +5.13% / +2.75% | +4.77% / +2.71% | +4.63% / +1.99% | +3.34% / +1.95% |
| Return per unit of volatility: strategy / index | 0.54 / 0.92 | 0.51 / 0.92 | 0.50 / 0.92 | 0.38 / 0.92 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +5.13% / +1.65% | +4.77% / +1.65% | +4.63% / +1.21% | +3.34% / +1.21% |
| Max drawdown: strategy / matched | -17.1% / -3.4% | -17.4% / -3.4% | -17.2% / -3.7% | -17.4% / -3.7% |
| CAGR per unit of drawdown: strategy / matched | 0.30 / 0.49 | 0.27 / 0.49 | 0.27 / 0.32 | 0.19 / 0.32 |
| **Holdout (1993-2009)** | | | | |
| Trades | 63 | 63 | 63 | 63 |
| Time in market | 9% | 9% | 9% | 9% |
| Win rate (after costs) | 73% | 73% | 73% | 71% |
| Mean per trade, gross / net bp | +153.1 / +151.1 | +144.7 / +142.7 | +153.1 / +142.4 | +153.1 / +122.1 |
| Median / worst trade, net | – / – | – / – | – / – | – / – |
| Average win / loss | +3.07% / -2.70% | +2.85% / -2.43% | +3.00% / -2.83% | +2.86% / -2.87% |
| Worst point inside a trade (MAE): median / worst | – / – | – / – | – / – | – / – |
| Excess over same-length trades, bp (p) | +146.3 (0.001) | +144.1 (0.001) | +146.3 (0.001) | +146.3 (0.001) |
| Excess, 90% interval, bp | – | – | – | – |
| Quarters with trades | 32 | 32 | 32 | 32 |
| Share of gross profit from the best 5 trades | 47% | 50% | 47% | 47% |
| CAGR: strategy / risk-matched buy-and-hold | +8.68% / +0.55% | +8.21% / +0.53% | +8.14% / -0.07% | +6.88% / -0.07% |
| Return per unit of volatility: strategy / index | 0.66 / 0.15 | 0.64 / 0.15 | 0.63 / 0.15 | 0.55 / 0.15 |
| v1 random-entry percentile | 100 | 100 | 100 | 100 |
| CAGR: strategy / time-matched buy-and-hold | +8.68% / +0.43% | +8.21% / +0.43% | +8.14% / -0.04% | +6.88% / -0.04% |
| Max drawdown: strategy / matched | -19.5% / -12.7% | -19.5% / -12.7% | -19.5% / -13.7% | -19.5% / -13.7% |
| CAGR per unit of drawdown: strategy / matched | 0.45 / 0.03 | 0.42 / 0.03 | 0.42 / -0.00 | 0.35 / -0.00 |
| **Verdict (v3)** | Lead | Lead | Lead | Lead |

## Summary

- No edge: 30
- Lead: 14
- Failed holdout: 4

Limits: adjusted daily prices (dividends included), no slippage beyond the stated costs, no stops, no taxes, 1x only. A Lead is a rule worth watching forward, not proof of an edge; results at higher leverage scale both the gains and the drawdowns, and the leveraged-ETF table shows by how much.

Every simulated trade is listed in `exports/trades/2026-11-18-070804-trade-simulation.csv` (one row per trade and pricing; adjusted prices, returns as fractions).
