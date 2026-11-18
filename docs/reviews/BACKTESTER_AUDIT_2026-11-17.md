# Backtester audit, trading-edge validation and research-app integration (2026-11-17)

> **Update 2026-11-18.** The backtester-side fixes from this review are done; see `docs/CHANGES_2026-11-18.md` for
> what changed, before and after. This review describes the app as it was at 407cd65.

A read-only review of the trading backtester (`C:\Claude\trading-backtester`, code 407cd65, results through the
2026-11-17 runs) and of how it works with the research app (`C:\Claude\trading-research`), written to the user's brief
of 2026-11-17. Checks ran on 2026-11-18 from a scratch copy; neither app's code, data or settings were changed.

## Executive assessment (deliverable 1)

**What it is.** A small, strict lab: 10 registered daily indicator studies on SPY, QQQ and IWM, and a trade simulator
for three oversold rules on SPY and QQQ, judged against random timing, buy-and-hold and a once-only 1993-2009 check.
Its strength is honesty machinery: rules are registered and fingerprinted, every run is kept in a hash-chained record,
1993-2009 is looked at once per rule version, and each run's input prices are kept, so any result can be rebuilt.

**Can it be trusted?** For what it computes, yes. All 36 tests pass; both latest recorded runs rebuild with zero
differences; my own independent code reproduces every SPY and QQQ study number and every development trade (same
days, same returns). Its statistical tests are close to their stated error rates, a little lenient for rare signals
(a nominal 5% behaved like 7-9% for RSI(14) < 30 in synthetic markets with clustered volatility). Costs are not a
concern for SPY and QQQ: the Leads keep their edge at ten times the assumed 2 bp.

**What it has found.** One family of evidence: deep short-term oversold readings in QQQ have been followed by
above-normal bounces over a few sessions. At the entry still available after the evening page (next open) two rules
qualify as provisional Leads: QQQ closing below its lower Bollinger band (104 trades since 2010, +0.81% per trade
against +0.21% for any same-length trade) and QQQ RSI(14) < 30 (26 trades, +2.84%), both sold at the first close
above the 5-day average. They are largely one bet (77% of RSI(14) days are also Bollinger days); results vary smoothly
with the parameters; the same rules on SPY point the same way more weakly; trend, momentum and volume rules showed
nothing (none of 63 tests passed). No edge is validated forward: one forward signal day exists, and a forward record that could
confirm the Bollinger rule statistically would take well over a decade at its trading rate.

**Main limitations.** Daily bars only; long-only; three tickers (two for trades); no regime, event, breadth or credit
conditioning (the VIX is loaded but unused); no confidence intervals; no intra-trade risk reporting; no leveraged-ETF
pricing; the development window is open-ended, so weekly runs mix new trades into "development" and can flip a
verdict that the research app turns into a stance, without notice; the 1993-2009 check is not independent for rules
chosen on it.

**Strategic potential.** High as the validation half of the system, if three things are added: a frozen development
window with a separate forward record, a registered split/filter engine that can read the research app's regime,
event and credit data, and per-rule evidence cards for the research app. It should stay a separate lab: the file
contract between the apps is sound and should be extended, not replaced.

### Critical correctness blockers
- **In the calculations: none found.** Every recorded number checked was reproduced independently.
- **Blocks one use: leverage.** The evidence is for 1x SPY/QQQ. At 1x, the Leads' trades fell as far as -11.7% (QQQ
  RSI(14)) and -19.7% (QQQ Bollinger) before recovering or exiting, and -22.9% on SPY; the reports show win rates and
  equity drawdown, which hide this. No leveraged ETF was ever simulated. Do not size a leveraged position on these
  rules until intra-trade risk and TQQQ/UPRO pricing are in the lab.
- **Blocks one use: weekly verdicts as forward evidence.** Until the development window is frozen per verdict version
  and verdict changes are reported, a weekly-refreshed verdict is not forward confirmation and can change silently
  (QQQ RSI(2) at the next open sits at q = 0.110 against a 0.10 threshold today).

### The five most valuable next steps
1. Lab: report verdict changes and intra-trade risk (MAE, worst trade, median, cost line). Small.
2. Lab: Lead v3, the same tests on a development window frozen at 2026-11-13, plus a forward block with a band set in
   advance. Registered before it runs.
3. Lab: a registered split engine reading the research app's VIX3M, credit and event data; run ideas 7 (overnight
   gap) and 8 (trend x VIX) and a leveraged pricing mode.
4. Both apps: an evidence file with one card per rule, structured fields in the research app's Idea ledger, and
   stance rules that respect forward status.
5. Operations: keep the laptop asleep (not shut down) on market days so the research app's pre-close, futures and
   option collection finally run; record a call every evening.

## Status of the earlier research-app reviews

No full review of the current research app exists; this one leans on the documents below and on direct inspection
(its code for the hand-off, its data folders, its 2026-11-17 Daily thesis build).

| Document | Date | Still accurate? |
|---|---|---|
| `docs/THESIS_PLAYBOOK.pdf` (source `docs/thesis_playbook_source.html`) | 2026-11-13, updated 11-14 | Most current. Gaps 1-6 and 8 built; gaps 7, 10, 12 are lab work still open (covered here) |
| Research `LOG.md`, "two-app review" | 2026-11-15 | Yes: keep both apps, put new testing in the lab |
| `docs/QUANT_REVIEW_2026-11-07.md` | 2026-11-07 | Yes for the frozen four-rule experiment and Kalshi facts; Kalshi fees since measured |
| `docs/UPGRADE_AUDIT_2026-11-07.md`, `docs/OPTIONS_AUDIT_NOTES.md` | 2026-11-07 | Code descriptions accurate; folder paths are the old laptop's; almost no intraday or option data collected since |
| `docs/quant_audit_2026-11-06.md` | 2026-11-06 | Historical: the pre-repair build; many items since fixed |
| `APP_GUIDE.md`, `STAGE1_REVIEW.md` | Data through 2026-11-05 | Stale on structure (4 tabs on port 8765 then; 12 tabs on 8766 now, Daily thesis first); stage-1 study descriptions still useful; its test registry now holds 33 tests |
| `DATA_INPUTS.md` | Undated (by 2026-11-07) | Partly superseded by the BLS API and ALFRED first-release values |

## How to read this review

Findings are labelled **[Verified]** (checked by running code or recomputing independently), **[Verified historical
finding]**, **[Reasonable hypothesis]**, **[Unvalidated assumption]**, **[Missing data]**, **[Technical limitation]**
and **[Recommendation]**. Examples marked **[Hypothetical]** are illustrations, not results. All historical figures
are from the 2026-11-17 runs (prices through 2026-11-13), development period 2010 on, after 2 bp ETF costs, unless
stated. 1993-2009 was not examined for any new rule.

## Contents

| Part | Deliverable | File |
|---|---|---|
| 1 | Executive assessment | this page |
| 2 | Technical accuracy audit | [01_technical_accuracy_audit.md](backtester_audit_2026-11-17/01_technical_accuracy_audit.md) |
| 3 | Complete application breakdown | [02_application_breakdown.md](backtester_audit_2026-11-17/02_application_breakdown.md) |
| 4 | Feature-by-feature operating manuals | [03_tab_operating_manuals.md](backtester_audit_2026-11-17/03_tab_operating_manuals.md) |
| 5 | Edge discovery vs validation; edge research inventory | [04_edge_discovery_and_inventory.md](backtester_audit_2026-11-17/04_edge_discovery_and_inventory.md) |
| 6 | Backtest interpretation guide | [05_interpretation_guide.md](backtester_audit_2026-11-17/05_interpretation_guide.md) |
| 7 | Edge validation framework | [06_validation_framework.md](backtester_audit_2026-11-17/06_validation_framework.md) |
| 8 | Research information effectiveness | [07_information_effectiveness.md](backtester_audit_2026-11-17/07_information_effectiveness.md) |
| 9-11 | Capability matrix, integration proposal, shared registry | [08_integration_and_registry.md](backtester_audit_2026-11-17/08_integration_and_registry.md) |
| 12 | Case studies (scenarios A-G) | [09_case_studies.md](backtester_audit_2026-11-17/09_case_studies.md) |
| 13 | Combined daily operating manual | [10_operating_manual.md](backtester_audit_2026-11-17/10_operating_manual.md) |
| 14-15 | Roadmap and developer hand-off | [11_roadmap_and_developer_handoff.md](backtester_audit_2026-11-17/11_roadmap_and_developer_handoff.md) |
| 16 | One-page cheat sheet | [12_cheat_sheet.md](backtester_audit_2026-11-17/12_cheat_sheet.md) |
| - | Verification log and scripts | [A_verification_log.md](backtester_audit_2026-11-17/A_verification_log.md) |

Not personal investment advice. Nothing here recommends a position size; the apps never place orders.
