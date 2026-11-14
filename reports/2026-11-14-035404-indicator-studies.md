# Indicator studies, 2026-11-14

Code 2e4c9b0; research-app data fingerprint 4e1f98996cd13f8f; 90 tests (90 with enough signals).

Holdout: 0 results read from `holdout_ledger.jsonl`, 60 evaluated for the first time in this run and stored. Each study version gets one look.

**How to read this.** Each row asks: after the signal (known at that day's close), how did the index do over the next *h* sessions compared with all days in the same period? *Excess* is that difference in basis points (100 bp = 1%). *p* is the chance of an excess this large from a randomly shifted copy of the same signal pattern; *q* corrects p for every test in this run. *Holdout* re-checks the same rule on 1993-2009 data that played no part in choosing it. *Next-open* is the excess if you buy at the next morning's open instead of the close.

Costs: ETF round trip 2 bp (used for verdicts); Kalshi perps 24 bp as taker or 4 bp as maker. A candidate must clear the ETF cost.

## rsi2_below_10 (v1)

RSI(2) closes below 10 (short-term oversold).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 395 (395) | +18.9 | 58% vs 55% | 0.001 | 0.031 | 412 | +29.2 | 0.001 | +6.8 | Candidate |
| SPY | 5 | 395 (200) | +44.6 | 65% vs 61% | 0.003 | 0.031 | 412 | +62.3 | 0.002 | +32.7 | Candidate |
| SPY | 10 | 394 (164) | +28.2 | 60% vs 64% | 0.193 | 0.364 | 412 | +67.9 | 0.003 | +16.0 | No evidence |
| QQQ | 1 | 412 (412) | +14.9 | 55% vs 56% | 0.009 | 0.074 | 294 | +50.3 | 0.001 | +5.6 | Candidate |
| QQQ | 5 | 412 (203) | +31.7 | 61% vs 60% | 0.049 | 0.194 | 294 | +85.5 | 0.007 | +22.5 | No evidence |
| QQQ | 10 | 410 (166) | +31.2 | 60% vs 63% | 0.198 | 0.364 | 294 | +77.0 | 0.053 | +22.3 | No evidence |
| IWM | 1 | 437 (437) | +14.5 | 55% vs 53% | 0.024 | 0.135 | no data | – | – | +9.9 | No evidence |
| IWM | 5 | 437 (215) | +29.5 | 61% vs 56% | 0.129 | 0.317 | no data | – | – | +25.2 | No evidence |
| IWM | 10 | 437 (172) | +15.3 | 57% vs 57% | 0.568 | 0.698 | no data | – | – | +11.0 | No evidence |

## rsi14_below_30 (v1)

RSI(14) closes below 30 (classic oversold).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 58 (58) | +94.3 | 57% vs 55% | 0.003 | 0.031 | 61 | +61.0 | 0.001 | +57.0 | Candidate |
| SPY | 5 | 58 (25) | +206.2 | 84% vs 61% | 0.003 | 0.031 | 61 | +122.7 | 0.014 | +170.7 | Candidate |
| SPY | 10 | 58 (22) | +108.0 | 69% vs 64% | 0.089 | 0.263 | 61 | +161.2 | 0.026 | +70.1 | No evidence |
| QQQ | 1 | 48 (48) | +147.0 | 71% vs 56% | 0.001 | 0.031 | 58 | +132.0 | 0.001 | +89.6 | Candidate |
| QQQ | 5 | 48 (25) | +280.2 | 88% vs 60% | 0.002 | 0.031 | 58 | +145.5 | 0.113 | +224.5 | Failed holdout |
| QQQ | 10 | 47 (23) | +229.0 | 72% vs 63% | 0.013 | 0.097 | 58 | +254.9 | 0.095 | +173.1 | Candidate |
| IWM | 1 | 107 (107) | -22.3 | 50% vs 53% | 0.091 | 0.263 | no data | – | – | -9.4 | No evidence |
| IWM | 5 | 107 (38) | -14.6 | 56% vs 56% | 0.754 | 0.828 | no data | – | – | -2.1 | No evidence |
| IWM | 10 | 107 (30) | -72.2 | 57% vs 57% | 0.360 | 0.514 | no data | – | – | -59.5 | No evidence |

## ema21_touch_uptrend (v1)

Low touches the 21-day EMA and the close holds above it, in an uptrend (close above the 200-day SMA).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 381 (381) | -9.6 | 52% vs 55% | 0.064 | 0.230 | 361 | +7.3 | 0.253 | -9.1 | No evidence |
| SPY | 5 | 380 (214) | -20.7 | 56% vs 61% | 0.096 | 0.263 | 361 | +16.1 | 0.301 | -20.4 | No evidence |
| SPY | 10 | 379 (162) | -16.7 | 59% vs 64% | 0.390 | 0.534 | 361 | +16.6 | 0.477 | -16.5 | No evidence |
| QQQ | 1 | 370 (370) | -9.1 | 55% vs 56% | 0.159 | 0.349 | 197 | -1.0 | 0.942 | -6.5 | No evidence |
| QQQ | 5 | 370 (221) | -17.1 | 58% vs 60% | 0.291 | 0.452 | 197 | +45.8 | 0.248 | -14.5 | No evidence |
| QQQ | 10 | 370 (162) | -31.2 | 61% vs 63% | 0.194 | 0.364 | 197 | +68.4 | 0.269 | -28.6 | No evidence |
| IWM | 1 | 428 (428) | +0.7 | 53% vs 53% | 0.909 | 0.932 | no data | – | – | +0.3 | No evidence |
| IWM | 5 | 426 (223) | -1.9 | 55% vs 56% | 0.916 | 0.932 | no data | – | – | -2.4 | No evidence |
| IWM | 10 | 425 (165) | -6.3 | 54% vs 57% | 0.805 | 0.873 | no data | – | – | -6.7 | No evidence |

## ema50_touch_uptrend (v1)

Low touches the 50-day EMA and the close holds above it, in an uptrend (close above the 200-day SMA).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 219 (219) | +6.2 | 58% vs 55% | 0.383 | 0.534 | 211 | +3.5 | 0.665 | +8.1 | No evidence |
| SPY | 5 | 219 (141) | -1.4 | 60% vs 61% | 0.934 | 0.934 | 211 | +10.7 | 0.624 | +0.6 | No evidence |
| SPY | 10 | 218 (105) | -16.7 | 58% vs 64% | 0.526 | 0.666 | 211 | +25.5 | 0.451 | -14.9 | No evidence |
| QQQ | 1 | 214 (214) | -12.2 | 54% vs 56% | 0.155 | 0.349 | 104 | -5.8 | 0.778 | -15.1 | No evidence |
| QQQ | 5 | 214 (136) | -36.3 | 56% vs 60% | 0.089 | 0.263 | 104 | +33.3 | 0.543 | -39.2 | No evidence |
| QQQ | 10 | 214 (104) | -41.4 | 60% vs 63% | 0.172 | 0.357 | 104 | +46.4 | 0.623 | -44.2 | No evidence |
| IWM | 1 | 233 (233) | -1.3 | 53% vs 53% | 0.885 | 0.926 | no data | – | – | +1.4 | No evidence |
| IWM | 5 | 231 (138) | +33.9 | 60% vs 56% | 0.155 | 0.349 | no data | – | – | +35.6 | No evidence |
| IWM | 10 | 230 (108) | +54.4 | 65% vs 57% | 0.130 | 0.317 | no data | – | – | +55.9 | No evidence |

## macd_cross_up (v1)

MACD(12,26) crosses above its 9-day signal line.

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 179 (179) | +8.5 | 56% vs 55% | 0.291 | 0.452 | 180 | +12.4 | 0.166 | +4.1 | No evidence |
| SPY | 5 | 179 (171) | +18.6 | 63% vs 61% | 0.219 | 0.386 | 180 | -20.8 | 0.219 | +14.2 | No evidence |
| SPY | 10 | 179 (155) | +24.7 | 66% vs 64% | 0.174 | 0.357 | 180 | -36.2 | 0.074 | +20.5 | No evidence |
| QQQ | 1 | 165 (165) | +12.9 | 62% vs 56% | 0.194 | 0.364 | 115 | +30.6 | 0.141 | +2.2 | No evidence |
| QQQ | 5 | 165 (163) | -1.7 | 63% vs 60% | 0.922 | 0.932 | 115 | -7.1 | 0.857 | -12.3 | No evidence |
| QQQ | 10 | 165 (149) | +12.4 | 64% vs 63% | 0.597 | 0.698 | 115 | +1.2 | 0.983 | +1.7 | No evidence |
| IWM | 1 | 166 (166) | -4.3 | 54% vs 53% | 0.667 | 0.759 | no data | – | – | -0.2 | No evidence |
| IWM | 5 | 166 (160) | +7.1 | 57% vs 56% | 0.729 | 0.810 | no data | – | – | +11.2 | No evidence |
| IWM | 10 | 166 (143) | +24.2 | 63% vs 57% | 0.357 | 0.514 | no data | – | – | +28.6 | No evidence |

## macd_cross_up_below_zero (v1)

MACD crosses above its signal line while still below zero.

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 64 (64) | +1.9 | 53% vs 55% | 0.878 | 0.926 | 77 | +17.7 | 0.209 | +0.5 | No evidence |
| SPY | 5 | 64 (63) | +37.7 | 66% vs 61% | 0.146 | 0.346 | 77 | -19.0 | 0.473 | +36.3 | No evidence |
| SPY | 10 | 64 (58) | +77.5 | 67% vs 64% | 0.026 | 0.135 | 77 | -44.2 | 0.231 | +76.6 | No evidence |
| QQQ | 1 | 66 (66) | +16.5 | 59% vs 56% | 0.288 | 0.452 | 59 | +19.1 | 0.505 | +5.2 | No evidence |
| QQQ | 5 | 66 (65) | +45.5 | 68% vs 60% | 0.163 | 0.350 | 59 | -53.6 | 0.324 | +34.4 | No evidence |
| QQQ | 10 | 66 (59) | +99.0 | 67% vs 63% | 0.044 | 0.191 | 59 | +0.9 | 0.993 | +88.1 | No evidence |
| IWM | 1 | 77 (77) | -8.0 | 53% vs 53% | 0.606 | 0.699 | no data | – | – | +6.0 | No evidence |
| IWM | 5 | 77 (75) | +50.4 | 65% vs 56% | 0.125 | 0.317 | no data | – | – | +64.6 | No evidence |
| IWM | 10 | 77 (68) | +97.2 | 69% vs 57% | 0.041 | 0.184 | no data | – | – | +112.1 | No evidence |

## bollinger_lower_close (v1)

Close below the lower Bollinger band (20 days, 2 standard deviations).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 222 (222) | +30.7 | 60% vs 55% | 0.001 | 0.031 | 213 | +24.3 | 0.005 | +15.1 | Candidate |
| SPY | 5 | 222 (107) | +74.2 | 67% vs 61% | 0.003 | 0.031 | 213 | +39.1 | 0.088 | +59.4 | Candidate |
| SPY | 10 | 219 (87) | +71.7 | 65% vs 64% | 0.022 | 0.135 | 213 | -14.0 | 0.634 | +56.5 | No evidence |
| QQQ | 1 | 211 (211) | +37.7 | 60% vs 56% | 0.001 | 0.031 | 135 | +36.8 | 0.037 | +20.1 | Candidate |
| QQQ | 5 | 211 (104) | +85.5 | 65% vs 60% | 0.003 | 0.031 | 135 | +72.3 | 0.167 | +68.9 | Failed holdout |
| QQQ | 10 | 208 (81) | +91.6 | 63% vs 63% | 0.031 | 0.147 | 135 | +87.5 | 0.233 | +75.3 | No evidence |
| IWM | 1 | 254 (254) | +13.8 | 55% vs 53% | 0.101 | 0.267 | no data | – | – | +8.9 | No evidence |
| IWM | 5 | 254 (119) | +34.0 | 61% vs 56% | 0.208 | 0.375 | no data | – | – | +29.4 | No evidence |
| IWM | 10 | 254 (96) | +22.1 | 59% vs 57% | 0.589 | 0.698 | no data | – | – | +17.2 | No evidence |

## new_20d_high (v1)

Close above the highest close of the previous 20 days (breakout).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 978 (978) | -0.5 | 54% vs 55% | 0.854 | 0.915 | 734 | -7.6 | 0.058 | +1.8 | No evidence |
| SPY | 5 | 978 (354) | -9.8 | 60% vs 61% | 0.279 | 0.452 | 734 | -17.8 | 0.130 | -7.5 | No evidence |
| SPY | 10 | 978 (222) | -13.0 | 67% vs 64% | 0.392 | 0.534 | 734 | -8.9 | 0.631 | -10.7 | No evidence |
| QQQ | 1 | 959 (959) | +2.4 | 58% vs 56% | 0.505 | 0.649 | 441 | -12.9 | 0.156 | +1.3 | No evidence |
| QQQ | 5 | 959 (338) | -7.8 | 61% vs 60% | 0.479 | 0.634 | 441 | -27.6 | 0.306 | -8.9 | No evidence |
| QQQ | 10 | 959 (222) | -6.3 | 68% vs 63% | 0.722 | 0.810 | 441 | +2.5 | 0.956 | -7.4 | No evidence |
| IWM | 1 | 716 (716) | -2.6 | 53% vs 53% | 0.590 | 0.698 | no data | – | – | -2.0 | No evidence |
| IWM | 5 | 716 (271) | -17.3 | 54% vs 56% | 0.261 | 0.444 | no data | – | – | -16.6 | No evidence |
| IWM | 10 | 715 (184) | -17.7 | 56% vs 57% | 0.500 | 0.649 | no data | – | – | -17.2 | No evidence |

## volume_spike_down_day (v1)

Down day on at least 2x the previous 20-day average volume (capitulation).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 82 (82) | +28.7 | 54% vs 55% | 0.020 | 0.135 | 94 | +23.5 | 0.054 | +1.9 | No evidence |
| SPY | 5 | 82 (53) | +54.9 | 65% vs 61% | 0.078 | 0.260 | 94 | +9.5 | 0.713 | +30.4 | No evidence |
| SPY | 10 | 81 (48) | -55.8 | 63% vs 64% | 0.246 | 0.426 | 94 | +13.8 | 0.738 | -81.7 | No evidence |
| QQQ | 1 | 83 (83) | -17.7 | 54% vs 56% | 0.188 | 0.364 | 20 | +15.0 | 0.741 | -3.7 | No evidence |
| QQQ | 5 | 83 (57) | +35.0 | 61% vs 60% | 0.324 | 0.495 | 20 | +50.3 | 0.608 | +50.2 | No evidence |
| QQQ | 10 | 82 (49) | -53.8 | 60% vs 63% | 0.351 | 0.514 | 20 | -148.7 | 0.342 | -37.5 | No evidence |
| IWM | 1 | 58 (58) | +9.7 | 53% vs 53% | 0.594 | 0.698 | no data | – | – | -8.9 | No evidence |
| IWM | 5 | 58 (41) | +94.5 | 67% vs 56% | 0.048 | 0.194 | no data | – | – | +77.4 | No evidence |
| IWM | 10 | 57 (38) | -76.3 | 61% vs 57% | 0.269 | 0.448 | no data | – | – | -95.5 | No evidence |

## above_sma200 (v1)

Close above the 200-day SMA (a trend-filter state, not an entry).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 3579 (3579) | -1.1 | 55% vs 55% | 0.055 | 0.208 | 2854 | +0.9 | 0.552 | -1.4 | No evidence |
| SPY | 5 | 3575 (729) | -6.2 | 61% vs 61% | 0.027 | 0.135 | 2854 | +7.4 | 0.270 | -6.5 | No evidence |
| SPY | 10 | 3570 (373) | -12.7 | 64% vs 64% | 0.021 | 0.135 | 2854 | +18.9 | 0.171 | -12.9 | No evidence |
| QQQ | 1 | 3604 (3604) | -1.5 | 56% vs 56% | 0.067 | 0.234 | 1403 | -0.7 | 0.826 | -2.1 | No evidence |
| QQQ | 5 | 3602 (738) | -6.2 | 60% vs 60% | 0.094 | 0.263 | 1403 | +4.0 | 0.823 | -6.9 | No evidence |
| QQQ | 10 | 3599 (377) | -12.6 | 63% vs 63% | 0.084 | 0.263 | 1403 | +13.0 | 0.696 | -13.4 | No evidence |
| IWM | 1 | 2942 (2942) | -1.2 | 53% vs 53% | 0.349 | 0.514 | no data | – | – | -1.4 | No evidence |
| IWM | 5 | 2938 (610) | -3.1 | 55% vs 56% | 0.596 | 0.698 | no data | – | – | -3.3 | No evidence |
| IWM | 10 | 2935 (310) | -9.3 | 56% vs 57% | 0.425 | 0.571 | no data | – | – | -9.6 | No evidence |

## Summary

- No evidence: 78
- Candidate: 10
- Failed holdout: 2

These are historical event studies on adjusted daily ETF prices, not trades: no stops, sizing or slippage beyond the stated cost. Overlapping multi-day windows make each signal less independent than the count suggests; the trades column counts non-overlapping ones. A candidate is a lead for a fuller test, not an edge.
