# 10. Combined operating manual: using both applications through the week

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Brief section 14; deliverable 13.

Times are Eastern (the laptop's clock is Central, one hour earlier). The research app is "the desk", the backtester
"the lab". The routine is built so that the lab is consulted rarely and deliberately: the desk already carries the
lab's evidence every evening.

## 10.1 The abbreviated daily routine (about 15 minutes in total)

| When | Open | Do | Record |
|---|---|---|---|
| Evening, after the refresh (from about 9:30 PM; the desk waits for Cboe's VIX close) | Desk: Daily thesis | Stance; evidence status; fired rules; tomorrow's trigger levels; events and earnings in the next 5 sessions | Your call (direction, ETF, horizon, invalidation, "leans on"); trigger levels for tomorrow |
| Morning, 8:00-9:25 AM | Desk: Daily thesis (morning view) | Overnight move and news; anything that makes the levels irrelevant | Nothing unless the plan changes (a journal note if it does) |
| 3:50 PM, only if a trigger is within reach | Desk: pre-close check (or any live quote) | Is the close-route rule about to fire? Decide the market-on-close order | The pre-close check logs itself; note your decision |
| Weekend, 10 minutes | Lab: `work\weekly_run.log`; desk: scoreboards | Did the weekly run succeed? Did any Lead change? | Ledger update if a verdict changed |

Skip the lab on ordinary days. Its evidence is already on the page.

## 10.2 Workflows

### Weekend strategy research (60-120 minutes, not every weekend)
- **Open first:** the desk's Idea ledger, then the lab's latest trade-simulation report.
- **Review:** ideas at "idea" or "registered"; the weekly run's log; the paper book and stance scoreboards.
- **Attention:** whether any registered test is due (a split, a new pricing), and whether last week produced a forward
  trade to compare with its band.
- **Questions:** Which single open question would most change how I act on the current Leads? Is it already written
  as an idea?
- **Consult the lab:** to register and run one test at a time (3.4 in [03](03_tab_operating_manuals.md)).
- **Existing evidence is enough when:** the question is already answered by a registered result, including a "no".
- **New investigation is justified when:** it would change a decision you actually make (enter, skip, size, exit), and
  it can be written as a rule known before the decision time.
- **Stop when:** one test is registered and run, or after the time box. Never run variants of a result you just saw.
- **Outputs:** idea ledger updates (stage, evidence reference, result); commits in the lab.

### Evening market analysis (10 minutes)
- **Open first:** desk, Daily thesis.
- **Review, in order:** headline and stance; evidence status (usable? age? cross-check?); registered signals (fired,
  values, trigger closes); paper ticket and open paper trades (exit level); events and earnings in the window;
  regime (trend, VIX and curve, breadth) as context.
- **Questions:** Is there a registered next-open setup? Is any open paper trade at its exit level tomorrow? Is there a
  reason in tier 3 (event, earnings, weekend, extreme VIX) to reduce size or skip?
- **Consult the lab:** no, unless the evidence status is not "ok" (then run the trade simulation) or a verdict changed.
- **Stop when:** your call is recorded.
- **Outputs:** your call; tomorrow's trigger levels; a journal note for anything unusual.

### Premarket preparation (5-10 minutes)
- **Open first:** desk, Daily thesis (morning view), then news.
- **Attention:** the overnight move against the evening's plan; scheduled releases at 8:30 AM; earnings reactions
  in large holdings.
- **Questions:** Has the expected bounce already happened overnight (a big gap up after a signal)? Is today an event
  day that makes the daily rules mean less?
- **Consult the lab:** no.
- **Stop when:** you know whether the evening plan stands.
- **Outputs:** a journal note only if the plan changes, with the reason.

### Market-open confirmation (first 30 minutes)
- **Open first:** desk, Intraday tab, as observation only.
- **Attention:** whether a next-open entry filled as planned (paper ticket price vs the actual open).
- **Consult the lab:** no. No intraday rule has evidence yet.
- **Stop when:** the entry is done or the decision is made not to act.
- **Outputs:** the fill against the open (for your own record of slippage).

### Intraday opportunity evaluation
- **Default:** none. The desk's intraday tools are for collecting and describing until the opening-range rule has its
  20 sampled sessions and a registered test passes.
- **Exception:** the 3:50 PM pre-close decision for a close-route rule, using levels prepared the evening before.
- **Stop rule:** if you find yourself reading charts to justify a trade the registered rules do not give, stop and
  write the idea in the ledger instead.

### Post-market review (5 minutes, after the refresh)
- Merged into the evening analysis: the refresh scores the stance and calls, and the paper book moves open trades.
- **Attention:** any paper trade that closed; how it compares with the backtest's average and its band.
- **Outputs:** nothing new unless a trade closed outside its usual range (journal note).

### Weekly edge evaluation (15 minutes, Saturday after 10:00 AM)
- **Open first:** lab, `work\weekly_run.log` ("Committed and pushed", the Lead list).
- **Then:** the trade-simulation report: compare the Lead list and the development q of borderline rules (for example
  QQQ RSI(2) next open, q 0.110) with last week.
- **Then:** desk, stance and paper-book scoreboards; System status card (missed days).
- **Questions:** Did any verdict change? Did a forward trade close outside its band? Were any days lost (laptop off)?
- **Consult the lab further:** only if a verdict changed: read why (new trades in the open-ended window).
- **Outputs:** an idea-ledger update for any change; a note of lost days.

### Periodic strategy reassessment (quarterly, 1-2 hours)
- **Open first:** the idea ledger, filtered to forward testing, monitoring and deteriorating.
- **For each:** registry entry, evidence card (or report), forward trades against the band, the mechanism, the regime
  the market has been in.
- **Decide:** keep monitoring, deteriorating, retire; or register a new version. Record the decision and the reason.
- **Also:** count the ideas tried this quarter (both apps) and write it beside the results.
- **Stop when:** every forward and monitored idea has a recorded decision.

## 10.3 The comprehensive strategy-development routine (one idea, start to finish)

1. **Observe** (desk): journal note with the page snapshot.
2. **Hypothesis** (desk): idea ledger entry: claim, mechanism, expected sign and size, horizon, benchmark, invalidation.
3. **Specify** (lab): rule in code, decision time, entry and exit, costs; commit.
4. **Register** (lab): `-m backtester.lock --add`; commit; ledger stage "registered" with the commit.
5. **First look** (lab): registered study run. Drop now if nothing is there (ledger "dropped", with the report).
6. **Trade simulation** (lab): register the trade rule and exits; run; Lead or not.
7. **Robustness** (lab): neighbourhood, split by regime and instrument, costs, MAE at the intended instrument.
8. **Decide on forward testing** (both): band from the development trades; desk shows the rule's levels and logs its
   signals before entry; ledger stage "forward".
9. **Monitor** (desk daily, lab weekly): stance, paper book, forward band.
10. **Reassess** (quarterly): keep, deteriorating, retire, or a new version.

A typical idea should take one weekend for steps 1-6 and another for step 7. Steps 8-10 take years for rare signals
([06 section 6.3](06_validation_framework.md)), which is why few ideas should reach them.

## 10.4 What should never happen in the routine

- Backtesting each headline. Headlines are tier 6 until a registered test with forward data exists.
- Running the trade simulation during the session to "check" a live trade.
- Changing a registered rule after seeing its result (a new version instead).
- Treating the 1993-2009 column as confirmation of a rule chosen on it.
- Sizing a leveraged position from 1x evidence.
- Spending the session researching. Research is a weekend activity; the week is for executing what is prepared.
