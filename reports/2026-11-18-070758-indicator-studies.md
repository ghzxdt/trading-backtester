# Indicator studies, 2026-11-18

Code 43f0869; research-app data fingerprint d09e16aa32e780ea; 90 tests (90 with enough signals).

Holdout: 60 results read from `holdout_ledger.jsonl` (first computed 2026-11-14), 0 evaluated for the first time in this run and stored. Each study version gets one look.

**How to read this.** Each row asks: after the signal (known at that day's close), how did the index do over the next *h* sessions compared with all days in the same period? *Excess* is that difference in basis points (100 bp = 1%), with a 90% interval in brackets (calendar quarters of signals resampled, so signals from one sell-off stay together). *p* is the chance of an excess this large from a randomly shifted copy of the same signal pattern; *q* corrects p for every test in this run. *Holdout* re-checks the same rule on 1993-2009 data that played no part in choosing it. *Next-open* is the excess if you buy at the next morning's open instead of the close.

Costs: ETF round trip 2 bp (used for verdicts); Kalshi perps 24 bp as taker or 4 bp as maker. A candidate must clear the ETF cost.

## rsi2_below_10 (v1)

RSI(2) closes below 10 (short-term oversold).

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 396 (396) | +18.7 (+7 to +32) | 58% vs 55% | 0.001 | 0.031 | 412 | +29.2 | 0.001 | +6.7 | Candidate |
| SPY | 5 | 395 (200) | +44.7 (+14 to +77) | 65% vs 61% | 0.003 | 0.031 | 412 | +62.3 | 0.002 | +32.8 | Candidate |
| SPY | 10 | 395 (164) | +27.7 (-19 to +77) | 60% vs 64% | 0.195 | 0.374 | 412 | +67.9 | 0.003 | +15.5 | No evidence |
| QQQ | 1 | 412 (412) | +15.0 (+6 to +25) | 55% vs 56% | 0.020 | 0.138 | 294 | +50.3 | 0.001 | +5.7 | No evidence |
| QQQ | 5 | 412 (203) | +31.8 (-2 to +67) | 61% vs 60% | 0.053 | 0.201 | 294 | +85.5 | 0.007 | +22.6 | No evidence |
| QQQ | 10 | 411 (166) | +30.5 (-22 to +83) | 60% vs 63% | 0.190 | 0.372 | 294 | +77.0 | 0.053 | +21.5 | No evidence |
| IWM | 1 | 438 (438) | +14.2 (+3 to +26) | 55% vs 53% | 0.027 | 0.140 | no data | – | – | +9.7 | No evidence |
| IWM | 5 | 437 (215) | +29.7 (-8 to +72) | 61% vs 56% | 0.120 | 0.308 | no data | – | – | +25.4 | No evidence |
| IWM | 10 | 437 (172) | +15.4 (-53 to +83) | 57% vs 57% | 0.582 | 0.690 | no data | – | – | +11.2 | No evidence |

## rsi14_below_30 (v1)

RSI(14) closes below 30 (classic oversold).

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 58 (58) | +94.3 (+46 to +154) | 57% vs 55% | 0.003 | 0.031 | 61 | +61.0 | 0.001 | +57.0 | Candidate |
| SPY | 5 | 58 (25) | +206.3 (+139 to +287) | 84% vs 61% | 0.003 | 0.031 | 61 | +122.7 | 0.014 | +170.8 | Candidate |
| SPY | 10 | 58 (22) | +108.1 (-52 to +276) | 69% vs 64% | 0.085 | 0.252 | 61 | +161.2 | 0.026 | +70.3 | No evidence |
| QQQ | 1 | 48 (48) | +147.1 (+96 to +208) | 71% vs 56% | 0.001 | 0.031 | 58 | +132.0 | 0.001 | +89.7 | Candidate |
| QQQ | 5 | 48 (25) | +280.4 (+176 to +386) | 88% vs 60% | 0.002 | 0.031 | 58 | +145.5 | 0.113 | +224.7 | Failed holdout |
| QQQ | 10 | 47 (23) | +229.2 (+83 to +372) | 72% vs 63% | 0.014 | 0.119 | 58 | +254.9 | 0.095 | +173.3 | No evidence |
| IWM | 1 | 107 (107) | -22.3 (-56 to +19) | 50% vs 53% | 0.087 | 0.252 | no data | – | – | -9.3 | No evidence |
| IWM | 5 | 107 (38) | -14.5 (-125 to +132) | 56% vs 56% | 0.770 | 0.845 | no data | – | – | -1.9 | No evidence |
| IWM | 10 | 107 (30) | -72.0 (-285 to +130) | 57% vs 57% | 0.359 | 0.522 | no data | – | – | -59.3 | No evidence |

## ema21_touch_uptrend (v1)

Low touches the 21-day EMA and the close holds above it, in an uptrend (close above the 200-day SMA).

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 381 (381) | -9.5 (-18 to -2) | 52% vs 55% | 0.070 | 0.252 | 361 | +7.3 | 0.253 | -9.0 | No evidence |
| SPY | 5 | 380 (214) | -20.6 (-41 to -2) | 56% vs 61% | 0.103 | 0.274 | 361 | +16.1 | 0.301 | -20.3 | No evidence |
| SPY | 10 | 379 (162) | -16.5 (-48 to +14) | 59% vs 64% | 0.385 | 0.539 | 361 | +16.6 | 0.477 | -16.3 | No evidence |
| QQQ | 1 | 370 (370) | -9.0 (-20 to +1) | 55% vs 56% | 0.161 | 0.363 | 197 | -1.0 | 0.942 | -6.5 | No evidence |
| QQQ | 5 | 370 (221) | -16.9 (-47 to +12) | 58% vs 60% | 0.300 | 0.465 | 197 | +45.8 | 0.248 | -14.3 | No evidence |
| QQQ | 10 | 370 (162) | -31.0 (-75 to +11) | 61% vs 63% | 0.211 | 0.380 | 197 | +68.4 | 0.269 | -28.4 | No evidence |
| IWM | 1 | 428 (428) | +0.8 (-8 to +10) | 53% vs 53% | 0.903 | 0.930 | no data | – | – | +0.4 | No evidence |
| IWM | 5 | 428 (224) | -3.6 (-30 to +24) | 54% vs 56% | 0.836 | 0.895 | no data | – | – | -4.0 | No evidence |
| IWM | 10 | 426 (165) | -6.8 (-47 to +36) | 54% vs 57% | 0.799 | 0.866 | no data | – | – | -7.2 | No evidence |

## ema50_touch_uptrend (v1)

Low touches the 50-day EMA and the close holds above it, in an uptrend (close above the 200-day SMA).

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 219 (219) | +6.3 (-5 to +18) | 58% vs 55% | 0.351 | 0.518 | 211 | +3.5 | 0.665 | +8.2 | No evidence |
| SPY | 5 | 219 (141) | -1.3 (-35 to +33) | 60% vs 61% | 0.936 | 0.936 | 211 | +10.7 | 0.624 | +0.7 | No evidence |
| SPY | 10 | 218 (105) | -16.5 (-71 to +37) | 58% vs 64% | 0.536 | 0.680 | 211 | +25.5 | 0.451 | -14.7 | No evidence |
| QQQ | 1 | 214 (214) | -12.1 (-28 to +4) | 54% vs 56% | 0.169 | 0.363 | 104 | -5.8 | 0.778 | -15.0 | No evidence |
| QQQ | 5 | 214 (136) | -36.1 (-82 to +7) | 56% vs 60% | 0.086 | 0.252 | 104 | +33.3 | 0.543 | -39.0 | No evidence |
| QQQ | 10 | 214 (104) | -41.2 (-100 to +15) | 60% vs 63% | 0.177 | 0.363 | 104 | +46.4 | 0.623 | -44.0 | No evidence |
| IWM | 1 | 233 (233) | -1.2 (-14 to +12) | 53% vs 53% | 0.917 | 0.930 | no data | – | – | +1.4 | No evidence |
| IWM | 5 | 232 (139) | +32.4 (-8 to +78) | 60% vs 56% | 0.170 | 0.363 | no data | – | – | +34.5 | No evidence |
| IWM | 10 | 230 (108) | +54.5 (+2 to +110) | 65% vs 57% | 0.131 | 0.327 | no data | – | – | +56.1 | No evidence |

## macd_cross_up (v1)

MACD(12,26) crosses above its 9-day signal line.

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 179 (179) | +8.6 (-2 to +19) | 56% vs 55% | 0.266 | 0.444 | 180 | +12.4 | 0.166 | +4.2 | No evidence |
| SPY | 5 | 179 (171) | +18.7 (-1 to +38) | 63% vs 61% | 0.224 | 0.396 | 180 | -20.8 | 0.219 | +14.3 | No evidence |
| SPY | 10 | 179 (155) | +24.9 (-5 to +55) | 66% vs 64% | 0.175 | 0.363 | 180 | -36.2 | 0.074 | +20.7 | No evidence |
| QQQ | 1 | 165 (165) | +13.0 (+1 to +25) | 62% vs 56% | 0.200 | 0.376 | 115 | +30.6 | 0.141 | +2.3 | No evidence |
| QQQ | 5 | 165 (163) | -1.6 (-24 to +22) | 63% vs 60% | 0.920 | 0.930 | 115 | -7.1 | 0.857 | -12.2 | No evidence |
| QQQ | 10 | 165 (149) | +12.6 (-25 to +52) | 64% vs 63% | 0.593 | 0.690 | 115 | +1.2 | 0.983 | +2.0 | No evidence |
| IWM | 1 | 166 (166) | -4.2 (-19 to +11) | 54% vs 53% | 0.702 | 0.799 | no data | – | – | -0.2 | No evidence |
| IWM | 5 | 166 (160) | +7.3 (-28 to +40) | 57% vs 56% | 0.739 | 0.821 | no data | – | – | +11.4 | No evidence |
| IWM | 10 | 166 (143) | +24.4 (-18 to +72) | 63% vs 57% | 0.366 | 0.523 | no data | – | – | +28.8 | No evidence |

## macd_cross_up_below_zero (v1)

MACD crosses above its signal line while still below zero.

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 64 (64) | +2.0 (-24 to +28) | 53% vs 55% | 0.881 | 0.930 | 77 | +17.7 | 0.209 | +0.6 | No evidence |
| SPY | 5 | 64 (63) | +37.8 (-8 to +81) | 66% vs 61% | 0.149 | 0.354 | 77 | -19.0 | 0.473 | +36.5 | No evidence |
| SPY | 10 | 64 (58) | +77.6 (+13 to +143) | 67% vs 64% | 0.027 | 0.140 | 77 | -44.2 | 0.231 | +76.8 | No evidence |
| QQQ | 1 | 66 (66) | +16.6 (-10 to +44) | 59% vs 56% | 0.304 | 0.465 | 59 | +19.1 | 0.505 | +5.3 | No evidence |
| QQQ | 5 | 66 (65) | +45.6 (+2 to +93) | 68% vs 60% | 0.157 | 0.363 | 59 | -53.6 | 0.324 | +34.6 | No evidence |
| QQQ | 10 | 66 (59) | +99.2 (+34 to +172) | 67% vs 63% | 0.044 | 0.182 | 59 | +0.9 | 0.993 | +88.3 | No evidence |
| IWM | 1 | 77 (77) | -8.0 (-36 to +21) | 53% vs 53% | 0.598 | 0.690 | no data | – | – | +6.0 | No evidence |
| IWM | 5 | 77 (75) | +50.6 (-4 to +107) | 65% vs 56% | 0.135 | 0.328 | no data | – | – | +64.7 | No evidence |
| IWM | 10 | 77 (68) | +97.4 (+27 to +168) | 69% vs 57% | 0.044 | 0.182 | no data | – | – | +112.3 | No evidence |

## bollinger_lower_close (v1)

Close below the lower Bollinger band (20 days, 2 standard deviations).

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 222 (222) | +30.8 (+17 to +48) | 60% vs 55% | 0.001 | 0.031 | 213 | +24.3 | 0.005 | +15.1 | Candidate |
| SPY | 5 | 222 (107) | +74.3 (+31 to +121) | 67% vs 61% | 0.003 | 0.031 | 213 | +39.1 | 0.088 | +59.5 | Candidate |
| SPY | 10 | 220 (87) | +70.5 (+4 to +139) | 65% vs 64% | 0.028 | 0.140 | 213 | -14.0 | 0.634 | +55.4 | No evidence |
| QQQ | 1 | 211 (211) | +37.8 (+18 to +63) | 60% vs 56% | 0.001 | 0.031 | 135 | +36.8 | 0.037 | +20.1 | Candidate |
| QQQ | 5 | 211 (104) | +85.7 (+38 to +130) | 65% vs 60% | 0.003 | 0.031 | 135 | +72.3 | 0.167 | +69.1 | Failed holdout |
| QQQ | 10 | 209 (82) | +89.7 (+30 to +152) | 63% vs 63% | 0.030 | 0.144 | 135 | +87.5 | 0.233 | +73.3 | No evidence |
| IWM | 1 | 254 (254) | +13.9 (+2 to +27) | 55% vs 53% | 0.103 | 0.274 | no data | – | – | +8.9 | No evidence |
| IWM | 5 | 254 (119) | +34.2 (-33 to +103) | 61% vs 56% | 0.206 | 0.378 | no data | – | – | +29.6 | No evidence |
| IWM | 10 | 254 (96) | +22.3 (-79 to +122) | 59% vs 57% | 0.584 | 0.690 | no data | – | – | +17.4 | No evidence |

## new_20d_high (v1)

Close above the highest close of the previous 20 days (breakout).

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 978 (978) | -0.4 (-3 to +2) | 54% vs 55% | 0.894 | 0.930 | 734 | -7.6 | 0.058 | +1.9 | No evidence |
| SPY | 5 | 978 (354) | -9.7 (-18 to -2) | 60% vs 61% | 0.283 | 0.455 | 734 | -17.8 | 0.130 | -7.3 | No evidence |
| SPY | 10 | 978 (222) | -12.9 (-32 to +4) | 67% vs 64% | 0.399 | 0.545 | 734 | -8.9 | 0.631 | -10.5 | No evidence |
| QQQ | 1 | 959 (959) | +2.5 (-1 to +6) | 58% vs 56% | 0.488 | 0.637 | 441 | -12.9 | 0.156 | +1.4 | No evidence |
| QQQ | 5 | 959 (338) | -7.6 (-25 to +7) | 61% vs 60% | 0.488 | 0.637 | 441 | -27.6 | 0.306 | -8.7 | No evidence |
| QQQ | 10 | 959 (222) | -6.1 (-39 to +23) | 68% vs 63% | 0.736 | 0.821 | 441 | +2.5 | 0.956 | -7.2 | No evidence |
| IWM | 1 | 716 (716) | -2.5 (-8 to +3) | 53% vs 53% | 0.588 | 0.690 | no data | – | – | -2.0 | No evidence |
| IWM | 5 | 716 (271) | -17.1 (-39 to +2) | 54% vs 56% | 0.266 | 0.444 | no data | – | – | -16.4 | No evidence |
| IWM | 10 | 715 (184) | -17.5 (-52 to +14) | 56% vs 57% | 0.514 | 0.661 | no data | – | – | -17.0 | No evidence |

## volume_spike_down_day (v1)

Down day on at least 2x the previous 20-day average volume (capitulation).

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 82 (82) | +28.8 (-4 to +59) | 54% vs 55% | 0.021 | 0.138 | 94 | +23.5 | 0.054 | +1.9 | No evidence |
| SPY | 5 | 82 (53) | +55.0 (-23 to +132) | 65% vs 61% | 0.078 | 0.252 | 94 | +9.5 | 0.713 | +30.5 | No evidence |
| SPY | 10 | 81 (48) | -55.7 (-254 to +119) | 63% vs 64% | 0.251 | 0.435 | 94 | +13.8 | 0.738 | -81.5 | No evidence |
| QQQ | 1 | 83 (83) | -17.6 (-45 to +11) | 54% vs 56% | 0.183 | 0.367 | 20 | +15.0 | 0.741 | -3.7 | No evidence |
| QQQ | 5 | 83 (57) | +35.2 (-28 to +100) | 61% vs 60% | 0.305 | 0.465 | 20 | +50.3 | 0.608 | +50.3 | No evidence |
| QQQ | 10 | 82 (49) | -53.6 (-195 to +70) | 60% vs 63% | 0.333 | 0.500 | 20 | -148.7 | 0.342 | -37.3 | No evidence |
| IWM | 1 | 58 (58) | +9.8 (-27 to +48) | 53% vs 53% | 0.598 | 0.690 | no data | – | – | -8.8 | No evidence |
| IWM | 5 | 58 (41) | +94.6 (+7 to +186) | 67% vs 56% | 0.042 | 0.182 | no data | – | – | +77.5 | No evidence |
| IWM | 10 | 57 (38) | -76.1 (-296 to +114) | 61% vs 57% | 0.272 | 0.445 | no data | – | – | -95.3 | No evidence |

## above_sma200 (v1)

Close above the 200-day SMA (a trend-filter state, not an entry).

| Symbol | h | Signals (trades) | Excess bp (90% interval) | Hit rate vs all days | p | q | Holdout signals | Holdout excess bp | Holdout p | Next-open excess bp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 1 | 3581 (3581) | -1.2 (-3 to +1) | 55% vs 55% | 0.051 | 0.201 | 2854 | +0.9 | 0.552 | -1.4 | No evidence |
| SPY | 5 | 3577 (730) | -6.2 (-17 to +4) | 61% vs 61% | 0.028 | 0.140 | 2854 | +7.4 | 0.270 | -6.5 | No evidence |
| SPY | 10 | 3572 (373) | -12.7 (-33 to +7) | 64% vs 64% | 0.021 | 0.138 | 2854 | +18.9 | 0.171 | -12.9 | No evidence |
| QQQ | 1 | 3604 (3604) | -1.4 (-5 to +2) | 56% vs 56% | 0.083 | 0.252 | 1403 | -0.7 | 0.826 | -2.0 | No evidence |
| QQQ | 5 | 3602 (738) | -6.1 (-20 to +7) | 60% vs 60% | 0.096 | 0.271 | 1403 | +4.0 | 0.823 | -6.8 | No evidence |
| QQQ | 10 | 3601 (377) | -12.7 (-42 to +15) | 63% vs 63% | 0.085 | 0.252 | 1403 | +13.0 | 0.696 | -13.4 | No evidence |
| IWM | 1 | 2942 (2942) | -1.1 (-4 to +2) | 53% vs 53% | 0.389 | 0.539 | no data | – | – | -1.3 | No evidence |
| IWM | 5 | 2940 (611) | -3.2 (-17 to +11) | 55% vs 56% | 0.589 | 0.690 | no data | – | – | -3.4 | No evidence |
| IWM | 10 | 2937 (310) | -9.4 (-39 to +18) | 56% vs 57% | 0.422 | 0.567 | no data | – | – | -9.7 | No evidence |

## Summary

- No evidence: 80
- Candidate: 8
- Failed holdout: 2

These are historical event studies on adjusted daily ETF prices, not trades: no stops, sizing or slippage beyond the stated cost. Overlapping multi-day windows make each signal less independent than the count suggests; the trades column counts non-overlapping ones. A candidate is a lead for a fuller test, not an edge.
