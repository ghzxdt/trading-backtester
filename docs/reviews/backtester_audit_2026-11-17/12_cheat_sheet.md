# 12. One-page operating cheat sheet

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Deliverable 16.

**The desk (research app)** says what is happening and whether a registered setup exists. **The lab (backtester)**
says whether an idea has historical merit. The desk carries the lab's evidence every evening; open the lab on
weekends, when a verdict changes, or when an idea is ready to be registered.

## Every evening (10 minutes, after the refresh, from about 9:30 PM ET)
1. Desk, Daily thesis: **stance** (long / flat / no call) and **evidence status** (usable, age, dates match).
2. **Fired rules** and tomorrow's **trigger closes** (on 2026-11-17: QQQ Bollinger at 637.06, RSI(14) at 627.00).
3. **Events and earnings** in the next 5 sessions; weekend or holiday ahead; VIX and curve.
4. **Record your call** with what would invalidate it and what it leans on.

## Before the open (5 minutes)
Overnight move and news. Only question: has something made tonight's plan irrelevant? Otherwise do nothing.

## 3:50 PM ET (only when a trigger is within reach)
Price vs the trigger written down last night. The closing-price entry is the stronger evidence and can only be
used now, on an estimate.

## Weekly (Saturday)
`work\weekly_run.log`: committed? Leads changed? Desk scoreboards and missed days. Any change: read the report.

## What the labels mean
| Label | Means | Do |
|---|---|---|
| Lead (next open) | Passed v2 in 2010 on and was not contradicted in 1993-2009; provisional | Act at small size, 1x, with the registered exit |
| Lead (close only) | Same, only for buying at the signal close | Only via the 3:50 PM route |
| No edge / No evidence | Did not pass | Not a setup |
| Failed holdout | Passed 2010 on, not 1993-2009 | Not a setup |
| Candidate (studies) | Worth a trade simulation | Not a trade |
| Perp columns | ETF prices with perp costs | Ignore for decisions |

## Read results in this order
Entry you can actually take -> excess and its uncertainty -> trades and quarters -> best-5 share and worst trade
(MAE) -> 1993-2009 sign -> costs. Win rate last.

## Hard rules
- Tested evidence sets direction; untested context only reduces size, shortens the hold or skips.
- Never change a rule after seeing its result: write a new version.
- Never size leverage on 1x evidence: worst intra-trade losses at 1x were -11.7% (QQQ RSI(14)) to -22.9% (SPY).
- Never use 1993-2009 to confirm a rule it helped choose.
- New idea: Journal note -> Idea ledger -> code -> lock -> commit -> run -> record the result, including "no".
- Stop researching when the call is recorded. Research is a weekend job.

## Where the current evidence stands (runs of 2026-11-17, data through 2026-11-13)
- Next-open Leads: **QQQ close below the lower Bollinger band** (104 trades, +0.81% per trade, excess +0.60%) and
  **QQQ RSI(14) < 30** (26 trades, +2.84%, excess +2.68%), both exiting at the first close above the 5-day average.
  Largely the same bet.
- Close-only Leads: QQQ RSI(2) < 10 with the same exit; QQQ RSI(14) < 30 held 5 sessions.
- SPY: no Lead at the next open. IWM: never simulated.
- Forward record: one signal day (2026-11-06), two paper trades, both gains. Years are needed to confirm anything.
