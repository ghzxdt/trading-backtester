# Indicator studies, 2026-11-13

Code cbe1f64; research-app data fingerprint 3af56709652ae7c6; 90 tests (90 with enough signals).

**How to read this.** Each row asks: after the signal (known at that day's close), how did the index do over the next *h* sessions compared with all days in the same period? *Excess* is that difference in basis points (100 bp = 1%). *p* is the chance of an excess this large from a randomly shifted copy of the same signal pattern; *q* corrects p for every test in this run. *Holdout* re-checks the same rule on 1993-2009 data that played no part in choosing it. *Next-open* is the excess if you buy at the next morning's open instead of the close.

Costs: ETF round trip 2 bp (used for verdicts); Kalshi perps 24 bp as taker or 4 bp as maker. A candidate must clear the ETF cost.

## rsi2_below_10 (v1)

RSI(2) closes below 10 (short-term oversold).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 395 (395) | +19.0 | 58% vs 55% | 0.001 | 0.034 | 412 | +29.2 | 0.001 | +6.9 | Candidate |
| SPY | 5 | 394 (200) | +44.8 | 65% vs 61% | 0.005 | 0.049 | 412 | +62.3 | 0.003 | +32.9 | Candidate |
| SPY | 10 | 393 (163) | +28.2 | 60% vs 64% | 0.205 | 0.395 | 412 | +67.9 | 0.002 | +16.1 | No evidence |
| QQQ | 1 | 412 (412) | +15.0 | 55% vs 56% | 0.008 | 0.070 | 294 | +50.3 | 0.002 | +5.7 | Candidate |
| QQQ | 5 | 410 (203) | +30.7 | 61% vs 60% | 0.064 | 0.237 | 294 | +85.5 | 0.009 | +21.9 | No evidence |
| QQQ | 10 | 409 (165) | +31.3 | 61% vs 63% | 0.232 | 0.415 | 294 | +77.0 | 0.054 | +22.5 | No evidence |
| IWM | 1 | 437 (437) | +14.5 | 55% vs 54% | 0.028 | 0.151 | no data | – | – | +9.9 | No evidence |
| IWM | 5 | 437 (215) | +29.6 | 61% vs 56% | 0.096 | 0.288 | no data | – | – | +25.3 | No evidence |
| IWM | 10 | 437 (172) | +15.2 | 57% vs 57% | 0.557 | 0.706 | no data | – | – | +11.0 | No evidence |

## rsi14_below_30 (v1)

RSI(14) closes below 30 (classic oversold).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 58 (58) | +94.3 | 57% vs 55% | 0.001 | 0.034 | 61 | +61.0 | 0.004 | +57.0 | Candidate |
| SPY | 5 | 58 (25) | +206.3 | 84% vs 61% | 0.003 | 0.039 | 61 | +122.7 | 0.008 | +170.8 | Candidate |
| SPY | 10 | 58 (22) | +107.7 | 69% vs 64% | 0.102 | 0.297 | 61 | +161.2 | 0.028 | +69.9 | No evidence |
| QQQ | 1 | 48 (48) | +147.1 | 71% vs 56% | 0.000 | 0.034 | 58 | +132.0 | 0.001 | +89.7 | Candidate |
| QQQ | 5 | 47 (24) | +273.6 | 87% vs 60% | 0.001 | 0.034 | 58 | +145.5 | 0.104 | +220.5 | Failed holdout |
| QQQ | 10 | 47 (23) | +228.4 | 72% vs 63% | 0.012 | 0.090 | 58 | +254.9 | 0.088 | +172.6 | Candidate |
| IWM | 1 | 107 (107) | -22.3 | 50% vs 54% | 0.082 | 0.268 | no data | – | – | -9.4 | No evidence |
| IWM | 5 | 107 (38) | -14.6 | 56% vs 56% | 0.757 | 0.830 | no data | – | – | -2.0 | No evidence |
| IWM | 10 | 107 (30) | -72.2 | 57% vs 57% | 0.361 | 0.524 | no data | – | – | -59.6 | No evidence |

## ema21_touch_uptrend (v1)

Low touches the 21-day EMA and the close holds above it, in an uptrend (close above the 200-day SMA).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 380 (380) | -9.5 | 52% vs 55% | 0.062 | 0.237 | 361 | +7.3 | 0.233 | -9.2 | No evidence |
| SPY | 5 | 379 (213) | -20.4 | 56% vs 61% | 0.114 | 0.301 | 361 | +16.1 | 0.329 | -20.2 | No evidence |
| SPY | 10 | 377 (161) | -15.6 | 59% vs 64% | 0.426 | 0.581 | 361 | +16.6 | 0.479 | -15.6 | No evidence |
| QQQ | 1 | 370 (370) | -9.0 | 55% vs 56% | 0.178 | 0.381 | 197 | -1.0 | 0.931 | -6.4 | No evidence |
| QQQ | 5 | 370 (221) | -16.9 | 58% vs 60% | 0.294 | 0.458 | 197 | +45.8 | 0.259 | -14.4 | No evidence |
| QQQ | 10 | 369 (161) | -30.4 | 61% vs 63% | 0.213 | 0.395 | 197 | +68.4 | 0.275 | -28.1 | No evidence |
| IWM | 1 | 426 (426) | +0.7 | 53% vs 54% | 0.907 | 0.943 | no data | – | – | +0.3 | No evidence |
| IWM | 5 | 425 (223) | -2.1 | 55% vs 56% | 0.912 | 0.943 | no data | – | – | -2.6 | No evidence |
| IWM | 10 | 423 (164) | -6.0 | 54% vs 57% | 0.823 | 0.893 | no data | – | – | -6.3 | No evidence |

## ema50_touch_uptrend (v1)

Low touches the 50-day EMA and the close holds above it, in an uptrend (close above the 200-day SMA).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 219 (219) | +6.2 | 58% vs 55% | 0.388 | 0.546 | 211 | +3.5 | 0.673 | +8.2 | No evidence |
| SPY | 5 | 218 (140) | -0.8 | 61% vs 61% | 0.961 | 0.971 | 211 | +10.7 | 0.617 | +1.1 | No evidence |
| SPY | 10 | 216 (105) | -14.6 | 59% vs 64% | 0.579 | 0.714 | 211 | +25.5 | 0.456 | -12.6 | No evidence |
| QQQ | 1 | 214 (214) | -12.1 | 54% vs 56% | 0.152 | 0.361 | 104 | -5.8 | 0.784 | -15.0 | No evidence |
| QQQ | 5 | 214 (136) | -36.1 | 56% vs 60% | 0.077 | 0.266 | 104 | +33.3 | 0.546 | -39.1 | No evidence |
| QQQ | 10 | 213 (103) | -39.5 | 60% vs 63% | 0.213 | 0.395 | 104 | +46.4 | 0.611 | -42.9 | No evidence |
| IWM | 1 | 231 (231) | -0.2 | 54% vs 54% | 0.980 | 0.980 | no data | – | – | +1.8 | No evidence |
| IWM | 5 | 230 (138) | +34.4 | 60% vs 56% | 0.161 | 0.362 | no data | – | – | +35.9 | No evidence |
| IWM | 10 | 229 (107) | +55.6 | 65% vs 57% | 0.122 | 0.301 | no data | – | – | +56.8 | No evidence |

## macd_cross_up (v1)

MACD(12,26) crosses above its 9-day signal line.

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 179 (179) | +8.6 | 56% vs 55% | 0.294 | 0.458 | 180 | +12.4 | 0.159 | +4.2 | No evidence |
| SPY | 5 | 179 (171) | +18.7 | 63% vs 61% | 0.211 | 0.395 | 180 | -20.8 | 0.193 | +14.2 | No evidence |
| SPY | 10 | 179 (155) | +24.5 | 66% vs 64% | 0.215 | 0.395 | 180 | -36.2 | 0.093 | +20.3 | No evidence |
| QQQ | 1 | 165 (165) | +13.0 | 62% vs 56% | 0.203 | 0.395 | 115 | +30.6 | 0.124 | +2.3 | No evidence |
| QQQ | 5 | 165 (163) | -1.5 | 63% vs 60% | 0.938 | 0.959 | 115 | -7.1 | 0.849 | -12.2 | No evidence |
| QQQ | 10 | 165 (149) | +11.8 | 64% vs 63% | 0.622 | 0.717 | 115 | +1.2 | 0.982 | +1.2 | No evidence |
| IWM | 1 | 166 (166) | -4.3 | 54% vs 54% | 0.703 | 0.798 | no data | – | – | -0.2 | No evidence |
| IWM | 5 | 166 (160) | +7.2 | 57% vs 56% | 0.723 | 0.803 | no data | – | – | +11.2 | No evidence |
| IWM | 10 | 166 (143) | +24.2 | 63% vs 57% | 0.353 | 0.524 | no data | – | – | +28.5 | No evidence |

## macd_cross_up_below_zero (v1)

MACD crosses above its signal line while still below zero.

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 64 (64) | +2.0 | 53% vs 55% | 0.869 | 0.931 | 77 | +17.7 | 0.195 | +0.6 | No evidence |
| SPY | 5 | 64 (63) | +37.8 | 66% vs 61% | 0.158 | 0.362 | 77 | -19.0 | 0.484 | +36.4 | No evidence |
| SPY | 10 | 64 (58) | +77.2 | 67% vs 64% | 0.043 | 0.191 | 77 | -44.2 | 0.242 | +76.4 | No evidence |
| QQQ | 1 | 66 (66) | +16.6 | 59% vs 56% | 0.295 | 0.458 | 59 | +19.1 | 0.480 | +5.3 | No evidence |
| QQQ | 5 | 66 (65) | +45.6 | 68% vs 60% | 0.169 | 0.372 | 59 | -53.6 | 0.307 | +34.5 | No evidence |
| QQQ | 10 | 66 (59) | +98.4 | 67% vs 63% | 0.044 | 0.191 | 59 | +0.9 | 0.995 | +87.6 | No evidence |
| IWM | 1 | 77 (77) | -8.0 | 53% vs 54% | 0.609 | 0.714 | no data | – | – | +6.0 | No evidence |
| IWM | 5 | 77 (75) | +50.5 | 65% vs 56% | 0.124 | 0.301 | no data | – | – | +64.6 | No evidence |
| IWM | 10 | 77 (68) | +97.2 | 69% vs 57% | 0.037 | 0.175 | no data | – | – | +112.0 | No evidence |

## bollinger_lower_close (v1)

Close below the lower Bollinger band (20 days, 2 standard deviations).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 221 (221) | +29.9 | 60% vs 55% | 0.003 | 0.039 | 213 | +24.3 | 0.005 | +14.6 | Candidate |
| SPY | 5 | 219 (106) | +72.9 | 67% vs 61% | 0.003 | 0.039 | 213 | +39.1 | 0.080 | +58.4 | Candidate |
| SPY | 10 | 218 (86) | +72.1 | 66% vs 64% | 0.027 | 0.151 | 213 | -14.0 | 0.650 | +57.0 | No evidence |
| QQQ | 1 | 210 (210) | +36.3 | 60% vs 56% | 0.002 | 0.039 | 135 | +36.8 | 0.034 | +19.1 | Candidate |
| QQQ | 5 | 208 (103) | +82.8 | 65% vs 60% | 0.005 | 0.049 | 135 | +72.3 | 0.168 | +67.4 | Failed holdout |
| QQQ | 10 | 208 (81) | +91.1 | 63% vs 63% | 0.036 | 0.175 | 135 | +87.5 | 0.254 | +74.8 | No evidence |
| IWM | 1 | 254 (254) | +13.8 | 55% vs 54% | 0.108 | 0.301 | no data | – | – | +8.9 | No evidence |
| IWM | 5 | 254 (119) | +34.1 | 61% vs 56% | 0.235 | 0.415 | no data | – | – | +29.4 | No evidence |
| IWM | 10 | 254 (96) | +22.0 | 59% vs 57% | 0.593 | 0.714 | no data | – | – | +17.1 | No evidence |

## new_20d_high (v1)

Close above the highest close of the previous 20 days (breakout).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 978 (978) | -0.5 | 54% vs 55% | 0.891 | 0.943 | 734 | -7.6 | 0.066 | +1.9 | No evidence |
| SPY | 5 | 978 (354) | -9.7 | 60% vs 61% | 0.288 | 0.458 | 734 | -17.8 | 0.122 | -7.4 | No evidence |
| SPY | 10 | 978 (222) | -13.3 | 67% vs 64% | 0.352 | 0.524 | 734 | -8.9 | 0.645 | -10.9 | No evidence |
| QQQ | 1 | 959 (959) | +2.5 | 58% vs 56% | 0.477 | 0.622 | 441 | -12.9 | 0.161 | +1.4 | No evidence |
| QQQ | 5 | 959 (338) | -7.6 | 61% vs 60% | 0.493 | 0.634 | 441 | -27.6 | 0.300 | -8.8 | No evidence |
| QQQ | 10 | 959 (222) | -6.9 | 68% vs 63% | 0.709 | 0.798 | 441 | +2.5 | 0.953 | -8.0 | No evidence |
| IWM | 1 | 716 (716) | -2.6 | 53% vs 54% | 0.604 | 0.714 | no data | – | – | -2.0 | No evidence |
| IWM | 5 | 715 (271) | -17.1 | 54% vs 56% | 0.294 | 0.458 | no data | – | – | -16.6 | No evidence |
| IWM | 10 | 714 (183) | -17.4 | 56% vs 57% | 0.474 | 0.622 | no data | – | – | -17.0 | No evidence |

## volume_spike_down_day (v1)

Down day on at least 2x the previous 20-day average volume (capitulation).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 82 (82) | +28.7 | 54% vs 55% | 0.020 | 0.142 | 94 | +23.5 | 0.061 | +1.9 | No evidence |
| SPY | 5 | 81 (53) | +51.9 | 64% vs 61% | 0.115 | 0.301 | 94 | +9.5 | 0.720 | +27.3 | No evidence |
| SPY | 10 | 80 (47) | -55.8 | 64% vs 64% | 0.248 | 0.429 | 94 | +13.8 | 0.728 | -81.4 | No evidence |
| QQQ | 1 | 83 (83) | -17.6 | 54% vs 56% | 0.202 | 0.395 | 20 | +15.0 | 0.746 | -3.6 | No evidence |
| QQQ | 5 | 82 (57) | +28.3 | 61% vs 60% | 0.442 | 0.593 | 20 | +50.3 | 0.599 | +45.7 | No evidence |
| QQQ | 10 | 81 (48) | -52.3 | 60% vs 63% | 0.359 | 0.524 | 20 | -148.7 | 0.355 | -34.9 | No evidence |
| IWM | 1 | 58 (58) | +9.7 | 53% vs 54% | 0.590 | 0.714 | no data | – | – | -8.9 | No evidence |
| IWM | 5 | 57 (40) | +91.8 | 67% vs 56% | 0.066 | 0.237 | no data | – | – | +74.9 | No evidence |
| IWM | 10 | 57 (38) | -76.3 | 61% vs 57% | 0.254 | 0.432 | no data | – | – | -95.6 | No evidence |

## above_sma200 (v1)

Close above the 200-day SMA (a trend-filter state, not an entry).

| Symbol | h | Signals (trades) | Excess bp | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 3574 (3574) | -1.2 | 55% vs 55% | 0.049 | 0.202 | 2854 | +0.9 | 0.557 | -1.4 | No evidence |
| SPY | 5 | 3570 (728) | -6.2 | 61% vs 61% | 0.027 | 0.151 | 2854 | +7.4 | 0.281 | -6.5 | No evidence |
| SPY | 10 | 3565 (372) | -12.6 | 64% vs 64% | 0.022 | 0.145 | 2854 | +18.9 | 0.151 | -12.9 | No evidence |
| QQQ | 1 | 3602 (3602) | -1.4 | 56% vs 56% | 0.083 | 0.268 | 1403 | -0.7 | 0.851 | -2.0 | No evidence |
| QQQ | 5 | 3599 (737) | -6.0 | 60% vs 60% | 0.118 | 0.301 | 1403 | +4.0 | 0.823 | -6.8 | No evidence |
| QQQ | 10 | 3594 (376) | -12.6 | 63% vs 63% | 0.088 | 0.275 | 1403 | +13.0 | 0.709 | -13.3 | No evidence |
| IWM | 1 | 2938 (2938) | -1.1 | 53% vs 54% | 0.375 | 0.536 | no data | – | – | -1.3 | No evidence |
| IWM | 5 | 2935 (609) | -3.0 | 55% vs 56% | 0.611 | 0.714 | no data | – | – | -3.3 | No evidence |
| IWM | 10 | 2931 (309) | -9.3 | 56% vs 57% | 0.420 | 0.581 | no data | – | – | -9.5 | No evidence |

## Summary

- No evidence: 78
- Candidate: 10
- Failed holdout: 2

These are historical event studies on adjusted daily ETF prices, not trades: no stops, sizing or slippage beyond the stated cost. Overlapping multi-day windows make each signal less independent than the count suggests; the trades column counts non-overlapping ones. A candidate is a lead for a fuller test, not an edge.
