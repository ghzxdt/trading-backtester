# App review, 2026-11-18, built on the Codex review of 2026-11-14

The user asked for another review of the apps based on the Codex review package at
`C:\Users\timothy\Documents\Codex\2026-11-14\https-github-com-ghzxdt-trading-backtester-3\outputs\`: nine reports
(executive summary, application audit, user manual, data reference, integration, edge catalog, thesis playbook,
validation roadmap, improvement roadmap) and an evidence folder, written on 2026-11-14 against data through 2026-11-13.

That package was the "completed research application review" the 2026-11-17 brief asked for; the 2026-11-17 audit
(`BACKTESTER_AUDIT_2026-11-17.md`) was written without it. This review does three things:
1. checks every Codex finding that touches the backtester against the app as it is now (code 40ad5e1, runs of
   2026-11-18, after the fixes in `docs/CHANGES_2026-11-18.md`), by running code, not by reading;
2. checks the Codex research-app findings that can be checked read-only, and lists the rest for that app's chat;
3. merges both reviews into one priority list.

Nothing in either app was changed for this review. Checks ran from a scratch folder; the scripts are in section 7.

## Bottom line

- **The two reviews agree on the core.** The arithmetic reproduces (Codex: all 24 ETF rows to 1e-12; mine: every
  study number and trade). The evidence is one QQQ oversold family, counted several times. Leads are provisional,
  1993-2009 is a reused period, forward evidence is empty, same-close execution is an assumption, tails are hidden
  behind win rates, and the research app's prospective records are almost unused.
- **Codex's sharpest backtester point stands and I reproduced it exactly:** at the same total volatility, simply
  holding QQQ beat every Lead's CAGR in 2010-2026 (QQQ Bollinger at the next open: +4.77% a year against +9.17%,
  with a similar worst drawdown, -17.4% against -18.1%). The Leads are timing signals, not better allocations of a
  fixed risk budget. My overlay check adds the useful nuance: as an add-on to a held QQQ position, RSI(14) raised
  return per unit of risk in 2010-2026 and Bollinger did not.
- **Codex found three backtester problems my audit missed, all confirmed today:**
  1. the one-look 1993-2009 cache is keyed by rule names only, so a changed cost or setting silently reuses old
     statistics (shown in a sandbox: costs moved from 2 to 50 bp; development recomputed at 50 bp; 1993-2009 kept the
     2 bp numbers while the export header said 50 bp). This now also covers Lead v3 and the new filter tests;
  2. the weekly script commits everything already staged, not only its own files, and pushes without checking the
     branch;
  3. study windows at the end of 2009 run into 2010 prices (one SPY signal, 2009-12-31, plus the baseline's last days).
- **Of Codex's backtester findings, the 2026-11-18 fixes closed or largely closed five** (risk inside trades,
  leveraged pricing, regime and gap tests, a separate forward record, use of the VIX). **Open:** the three above, the
  whole-volatility and cash benchmarks, a registered causal exit, episode-level counting, and some smaller items
  (section 2.8).
- **Research app, still true on the 2026-11-17 build:** the "Intraday collection" card shows OK while the last run
  got minute bars for 0 of 16 tickers; every one of 120,705 minute-bar events is labelled `retrieved_archive`, so the
  intraday paper engine (which requires `observed_live`) can never produce eligible forward evidence. And, new today:
  the minute-bar archive has not grown since 2026-11-14, so the intraday history the ORB research waits for is not
  accumulating.

## 1. Where the two reviews agree and differ

| Topic | Codex (2026-11-14) | Audit (2026-11-17) | Now |
|---|---|---|---|
| Reproducibility | 24 ETF rows reproduced to 1e-12 | All studies and 24 development pricings reproduced independently; records rebuild exactly | Agree. Still true after the fixes (0 differences) |
| What the evidence is | One related QQQ oversold family; RSI(14) overlaps Bollinger 37/48 days | Same; 77% overlap, 90% with RSI(2) or Bollinger | Agree |
| Benchmark | Risk-matched benchmark is narrow; equal-whole-volatility index beats all six Leads | Risk-matched benchmark is a low bar; overlay view: RSI(14) adds, Bollinger does not | Both hold; see 2.1 |
| Same-close execution | Unresolved at entry and at the SMA5 exit; next-open exit sensitivity does not collapse | Same; exit moved to next open changes means by -7 to +7 bp | Agree; a registered causal exit is still missing |
| 1993-2009 | Reused stress period, not confirmation | Same | Agree |
| Forward evidence | Zero completed trades after 2026-11-08 | Same | Still zero; now tracked separately by Lead v3 |
| Tails | No MAE/MFE, expected shortfall, time under water | Worst intra-trade -11.7% to -22.9% at 1x | MAE, worst and median trades now reported; shortfall and time under water not |
| p-value calibration | Not examined | Near nominal; 1.5-1.8x lenient for rare signals | Mine only |
| Open development window | Not raised as such | Weekly runs could flip verdicts silently | Fixed (Lead v3, studies method 3) |
| Holdout identity | Keys omit costs, periods, statistic; future v3 needs a namespace | Missed | Confirmed, open (2.4) |
| Holdout boundary | 2009 windows run into 2010 | Missed | Confirmed, open (2.5) |
| Weekly script | Commits anything staged; no branch check | Missed | Confirmed, open (2.8) |
| Research app collection | Green status with 0/16; archive-only minute bars | Daytime jobs never ran; did not check the minute-bar label | Both still true (section 3) |
| GEX | Matched-regime size ratio 1.18, interval 0.90-1.43: not shown beyond volatility | Placed GEX among verified size effects | Codex is more careful; I move GEX down (3.3) |

## 2. Backtester findings, re-checked against the current app

### 2.1 B1. The benchmark answers a narrower question than "better use of risk" - open

Codex's point: Lead v2 (and v3) compare with buy-and-hold scaled to time in the market x in-trade volatility. An
index allocation with the same *whole-strategy* volatility (idle days included) is far larger, because volatility
scales with the square root of exposure, not with exposure.

[Verified] Recomputed with the current code on the 2026-11-13 snapshot (development 2010-01-01 to 2026-11-13, 2 bp):

| Lead (5-day-average exit unless stated) | Entry | Trades | Strategy CAGR | QQQ at the same total volatility | Index fraction | Max drawdown, strategy / index |
|---|---|---|---|---|---|---|
| QQQ RSI(2) < 10 | close | 192 | +6.69% | +10.57% | 0.56x | -18.9% / -20.8% |
| QQQ RSI(14) < 30, hold 5 | close | 25 | +4.62% | +6.80% | 0.36x | -12.0% / -13.6% |
| QQQ RSI(14) < 30 | close | 26 | +4.58% | +6.56% | 0.35x | -12.0% / -13.1% |
| QQQ RSI(14) < 30 | next open | 26 | +4.30% | +6.16% | 0.33x | -12.0% / -12.3% |
| QQQ Bollinger | close | 104 | +5.13% | +9.31% | 0.50x | -17.1% / -18.4% |
| QQQ Bollinger | next open | 104 | +4.77% | +9.17% | 0.49x | -17.4% / -18.1% |

Codex's figures match to 0.01 points (its QQQ RSI(2) strategy CAGR, 6.67%, differs by the knife-edge exit that flips
between Yahoo downloads; see `CHANGES_2026-11-18.md`). Caveats both reviews share: the scaling uses the whole period's
realised volatility (not knowable in advance) and cash earns zero in both legs.

What it means for decisions: as a standalone use of a fixed risk budget, none of the Leads beat holding less QQQ.
The case for them is as timing on top of a position, which is the overlay view: holding QQQ and adding 1x during
RSI(14) trades raised return per unit of risk (0.99 against 0.92 at the same average exposure) and lowered the
worst drawdown; doing the same with Bollinger added return but not return per unit of risk (audit, part 1, 1.8).
The reports should say both things. **Still open:** an equal-whole-volatility column, a cash-yield column, an
implementable version scaled by trailing volatility, and the overlay comparison, all descriptive beside v3.

### 2.2 B2. Same-close execution at entry and exit - partly addressed

- Entry: unchanged and correctly labelled; the research app acts only on next-open Leads; the pre-close route still
  has no recorded data.
- Exit: the trade reports and evidence cards now show the mean if the 5-day-average exit is taken at the next open
  (descriptive, same trades): QQQ Bollinger +0.81% either way. Codex's version, which keeps the position one more
  session and re-runs the trade sequence, gave +0.81% net (102 trades) for Bollinger and +2.93% net (25 trades) for
  RSI(14), against about +2.75% net on the same 26 trades in mine. Both are exploratory and both say the result does
  not collapse.
- **Open:** a registered exit version that decides on a known close and sells at the next open, judged by v3.

### 2.3 B3. 1993-2009 is reused; no forward trades - structurally addressed, evidence still empty

Lead v3 now keeps trades signalled after 2026-11-13 apart, with a band set in advance, and the studies list forward
signals separately. As of the 2026-11-18 runs: zero forward trades; three forward study signals (SPY and IWM RSI(2) on
2026-11-16). Nothing to confirm or reject yet.

### 2.4 B4. The one-look cache does not know which settings produced it - open, confirmed

[Verified] The holdout ledger keys are `trade|signal@v+exit@v|symbol|mode`, `study|name@v|symbol|h<h>` and (new)
`filter|split@v|strategy`. None includes the costs, the period definitions or the statistic. A sandbox run with
made-up prices, ETF cost 2 bp, then again at 50 bp with the same rules and seed:

| | Run 1 | Run 2 |
|---|---|---|
| Record settings | 2 bp | 50 bp |
| Development mean net per trade (SPY RSI(2), hold 5) | -0.21% | -0.69% (recomputed) |
| 1993-2009 source | first look | "ledger, first computed ..." (reused) |
| Export cost header / implied 1993-2009 cost | - | 50 bp / 2.0 bp |

So a changed setting would mix new development numbers with old 1993-2009 numbers under a header that names only
the new setting. Nothing recorded so far is affected: `config.json`'s settings have not changed since 2026-11-08 (its
only later change, 2026-11-12, was the research app's folder, which is not a setting), and every ledger entry dates
from 2026-11-14 or 2026-11-18. Lead v3 reuses v2's 1993-2009 statistics deliberately (the test is identical), but
nothing *checks* that; Codex predicted exactly this for "a future v3".

**Fix (first in section 4):** store a hash of the settings and method (costs, funding, periods, statistic version and
parameters, draws/resamples) with every ledger entry and every record; when a stored entry's identity differs from the
run's, stop with a message to register a new version. Entries made before the guard map to the current settings.

### 2.5 B5. 1993-2009 study windows run into 2010 - open (development side fixed)

[Verified] In the indicator studies, the 1993-2009 statistics use forward returns computed on the full history.
One signal crosses: SPY RSI(2) < 10 on 2009-12-31 (its 1-, 5- and 10-session returns end in January 2010), and the
1993-2009 all-days baseline also includes the last h days of 2009. Small. The trade simulator was never affected
(trades must exit inside their period). Method 3 already stops development returns at 2026-11-13; the 2009 boundary
needs the same treatment, which is a new 1993-2009 computation and therefore a new holdout namespace (do it together
with 2.4).

### 2.6 B6. Overlapping rules counted as several results - open as a reporting gap

The overlap numbers agree (Codex: 37 of 48 RSI(14) days are Bollinger days; audit: 77%). The 14 Leads are pricings
of about one bet. The evidence cards now note limitations per rule but not the overlap. **Open:** an episode view that
counts distinct sell-off episodes across the three signals, and a note on each card naming the overlapping rules.

### 2.7 B7. Tails and sparse episodes - largely fixed

Reports and evidence cards now show the worst point inside trades, worst and median trades, the mean without the best
three, best-5 share and a cost line (QQQ RSI(14) next open: worst intra-trade -11.7% although no closed trade lost more
than 1.6%; in TQQQ, Bollinger's worst trade -47.6%). **Open:** expected shortfall, time under water, and the overnight
gap loss inside trades.

### 2.8 Other Codex items

| Item | Status now | Evidence |
|---|---|---|
| VIX loaded but unused | Fixed | Filter tests use VIX level, VIX/VIX3M and a VIX-matched baseline |
| ATR implemented, unused | Open (no question needs it yet) | `indicators.atr` |
| Sector, breadth, intermarket tests | Open | No sector ETF data; RSP/SPY not used by any test |
| Net confidence intervals | Partly | 90% intervals on excess; none on net CAGR or benchmark differences |
| Cash earns zero | Open | Both strategy and benchmark |
| Leveraged-ETF realism | Partly | TQQQ/UPRO repricing reported (2.4-2.7x the 1x mean; worst trades -42% to -59%); no registered verdict |
| Weekly script commits anything staged; pushes without a branch check | **Open, confirmed** | `run_weekly.ps1` stages its paths, then `git commit -m` with no path list, and `git push origin main` with no branch check |
| "Open latest report" picks by file time across report types | Open, now three types | `backtester_app.pyw` `latest_report` |
| Snapshots not on GitHub | Open (covered by the manual backup of `C:\Claude`) | `.gitignore` |

## 3. Research-app findings (read-only check, for that app's chat)

### 3.1 Checked today

| Codex finding | Status on the 2026-11-17 build | Evidence |
|---|---|---|
| F2: collection status green while data failed | **Still true** | System status: "Intraday collection: ok, 2026-11-17 20:10 ET, Minute bars for 0 of 16 tickers in the last run" |
| Intraday dead end: archive-labelled bars can never qualify | **Still true** | 120,705 minute-bar events, all `retrieved_archive` (`intraday_collect.py:51`); eligibility needs `observed_live` (`intraday/features.py:157`, `intraday/paper.py:48`) |
| F1: prospective records unused | Still true | 0 calls, 0 journal notes, 0 pre-close records, 8 stance records; paper decisions missed 2026-11-09/10/11/16 |
| GEX stale and not shown beyond volatility | Consistent with Codex | GEX copy ends 2026-11-05 (manual download) |
| **New: the minute-bar archive is not growing** | Found today | Sessions 2026-11-02 to 2026-11-14 only; the last run retrieved 0 of 16; Yahoo keeps about 5 days, so missed days are lost |

### 3.2 Not re-checked here (Codex's findings stand as written; for the research chat)

F3 (0DTE outcome compares raw strikes with adjusted closes), F4 (macro replay picks values by date only, so an 08:30
release can appear at 08:00), F5 (pre-close window hard-coded 15:30-16:00, no quote age, no evidence check), F6 (one
hypothesis, several outcome views without a shared id), F7 (recorded invalidation is never applied), F8 (OCC volume
halving unverified), F9 (horizon mixing), F10 (small timing inconsistencies), the VIX/sqrt(252) label, and the naming
clashes ("Backtests", "Paper", two "Today" headings).

### 3.3 Change to the information hierarchy (audit part 7)

The audit placed "GEX below zero" with the verified size effects (tier 3). Codex's matched-regime check (ratio 1.18,
calendar-year interval 0.90 to 1.43) shows the size effect is not established beyond the VIX regime. Move GEX to
tier 4 (context, insufficient evidence) until a registered test against VIX and realised-volatility baselines says
otherwise. The other tier-3 size effects (event days, weekend and holiday gaps) were matched or controlled differently
and stay.

## 4. Combined priority list

| # | App | Work | Why now | Size |
|---|---|---|---|---|
| 1 | Backtester | Settings-and-method identity on every ledger entry and record; refuse mismatched reuse | Any future cost or period change would silently mix numbers; v3 and the filter tests already rely on reuse | Small-medium |
| 2 | Backtester | Weekly script: commit only its own paths, refuse other staged files, check the branch | It runs unattended and pushes | Small |
| 3 | Research | Collection health = data delivered, per symbol; find why minute bars returned 0 of 16 | Intraday history is being lost now (Yahoo keeps about 5 days) | Small |
| 4 | Research | A receipt-timed live observation path for minute bars | Without it the ORB rule can never produce eligible forward evidence | Medium |
| 5 | Backtester | Equal-whole-volatility, trailing-volatility, cash and overlay comparisons beside v3 (descriptive) | Answers "is this a better use of risk?" honestly | Small-medium |
| 6 | Research | The six follow-ups sent 2026-11-18 (v3 caution, evidence cards, Forward below band, archive, cross-check tolerance, keep the laptop asleep) | Already handed over | Mixed |
| 7 | Backtester | Registered next-open exit version; 2009 boundary purge in a new holdout namespace (with #1) | Execution honesty; clean split | Small |
| 8 | Both | One opportunity id across stance, paper book, calls and journal; record abstentions and vetoes | Lets discretionary choices be compared with the frozen rule | Medium |
| 9 | Backtester | Episode view across the overlapping rules; expected shortfall and time under water | Stops counting one bet several times | Small |

Not recommended now (both reviews agree): combined probability scores, sentiment models, machine learning, more
indicators, broker integration, sizing.

## 5. Where I would qualify Codex

- **Benchmark framing.** Agreed that the Lead label is narrow. The more useful question for this user is the overlay
  one (what adding the rule to a held position does), where RSI(14) helped and Bollinger did not; report both.
- **Exit sensitivity.** Its next-open exit variant re-runs the trade sequence; mine keeps the trades fixed. They differ
  by about 18 bp per trade for RSI(14) and agree that the result holds. Neither is registered.
- **Calibration.** Codex did not test the p-value methods; the audit's simulation (lenient by 1.5-1.8x for rare
  signals) belongs beside its findings.
- **Scope.** Codex weighted the research app; for the backtester its findings are fewer but precise, and three of them
  were real gaps in my audit.

## 6. Status of the earlier documents

`BACKTESTER_AUDIT_2026-11-17.md` remains the full audit; read it with `docs/CHANGES_2026-11-18.md` (what has been
fixed) and this review (what Codex added). The Codex package itself stays where it is, outside `C:\Claude`.

## 7. How this was checked

All on 2026-11-18, from `scratchpad\checks\codex_recheck.py` and inline scripts, using the research app's Python:
- B1: `simulate.daily_returns` over v3's development window on snapshot `c4713b15d633ad4c`; index fraction = standard
  deviation of the strategy's daily returns (idle days included) / the index's; CAGR and drawdown by `simulate.summary`.
- B5: signal days in the 1993-2009 mask whose forward window ends after 2009-12-31, per study and horizon.
- B4: a sandbox research app (made-up prices) through `run_trades.main` twice, with `data.config` patched from 2 to 50
  bp; compared records and the export.
- Weekly script and app: read `run_weekly.ps1` and `backtester_app.pyw`; `config.json` history from `git log`.
- Research app, read-only: `data/intraday/v1/bars.jsonl` availability labels; `output/thesis_state.json` System status
  rows; `intraday_collect.py`, `intraday/features.py`, `intraday/paper.py` (eligibility lines).
Not checked: the Codex research-app findings in 3.2, its screenshots and its UI inventory.
