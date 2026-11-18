# 9. Case studies: both applications working together

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Brief section 13; deliverable 12.

Real figures come from the research app's Daily thesis built at 9:39 PM ET on 2026-11-17 (latest close 2026-11-17)
and from the backtester's 2026-11-17 runs (data through 2026-11-13). Anything marked **[Hypothetical]** is an
illustration; no new test was run for it, and no outcome after 2026-11-17 is known.

**The real situation on the evening of 2026-11-17:**
- QQQ closed at 656.95: -8.5% over 20 sessions, below its 50- and 200-day averages. SPY 732.44, still above its
  200-day average. IWM below both.
- Equal weight (RSP) has beaten SPY by 4.7% over 20 sessions: a sell-off led by large technology stocks.
- VIX 25.5, above VIX3M 25.0 (inverted term structure, a stress reading).
- RSI(2) < 10 fired at the close on SPY, QQQ and IWM; IWM also closed below its lower Bollinger band.
- Nvidia (also Home Depot and Disney) reported after the close.
- The page's stance: **flat** ("a rule fired at the 2026-11-17 close, but its tested entry has passed"): QQQ RSI(2)
  < 10 is a Lead only when bought at the signal close.
- Triggers for the next close: QQQ RSI(14) < 30 at a close of 627.00 or lower (-4.6%); QQQ below its lower band at
  637.06 or lower (-3.0%).
- Evidence status: usable, 4 days old, dates cross-checked (match).
- No futures or nowcast snapshot, no pre-close record and no same-day option data exist yet (daytime jobs have not run).

---

## Scenario A. A research-generated opportunity

*The research app shows something unusual: a tech-led sell-off (QQQ -8.5% in 20 sessions while equal weight leads),
with the largest index holding reporting after the close.*

1. **Is it material?** Check it against history before forming a view. The desk already shows the parts (20-day
   returns, breadth, VIX bucket). Ask how often QQQ has been this far below its 20-day level while RSP led SPY; the
   research app's "breakaway" test found only a hint for "QQQ much weaker than usual vs SPY" (p = 0.053), so this is a
   question, not a known effect.
2. **Form a testable hypothesis** [Hypothetical]: "After QQQ's 20-day return is at or below -8% while RSP's 20-day
   return beats SPY's by at least 3 points, QQQ's next 5 and 10 sessions beat all days." Sign, horizon, condition
   and benchmark are written before any number is seen.
3. **Comparable conditions:** the lab needs a two-symbol study for this (not available today; [11](11_roadmap_and_developer_handoff.md)
   item H3). Until then, the trade list and the indicator studies give partial analogues: the QQQ RSI(14) and Bollinger
   rules capture "QQQ sold off hard" without the breadth part.
4. **Perform the test:** register the study (idea ledger, then `catalog.py` and the lock), run the registered studies;
   because it overlaps the oversold family, also report its trades' overlap with RSI(14) and Bollinger days.
5. **Interpret:** read excess, interval, trades, and how much it adds beyond the existing oversold rules. The saved RSP
   history starts in 2010, so the breadth condition has no 1993-2009 check: say so, and plan a forward record instead.
6. **Return evidence:** an evidence card with occurrence frequency, interval, worst case and status
   ("historical testing").
7. **Construct the thesis:** a bounce thesis would rest on the registered Leads first; the new study, if supportive,
   is tier 2 until it has a forward record.
8. **Confirmation, invalidation, no-trade:** confirmation = a registered rule fires (for example QQQ closes at or below
   637.06); invalidation = the registered exit, or a close below the worst historical MAE you can hold; no-trade =
   evidence status not "ok", an event inside the window you are not willing to carry (the Nvidia reaction is the
   next session itself), or the instrument you would use is leveraged and untested.

## Scenario B. A backtester-generated opportunity

*The lab rates QQQ "close below the lower Bollinger band, exit at the first close above the 5-day average" a Lead at
the next open.*

1. **Robust?** From [01](01_technical_accuracy_audit.md): smooth across band widths and lengths; profit not from a
   few trades (best-5 share 32%); 2020 lost 4.9% per trade on 3 trades; worst intra-trade -19.7%; SPY points the same
   way more weakly; 77% of RSI(14) days are also Bollinger days. Robust enough to watch, not to lever.
2. **Observable conditions:** the close relative to the lower band, known at 4:00 PM. The desk computes the exact
   trigger close for tomorrow (637.06 on the evening of 2026-11-17) and the 5-day-average exit level for an open trade.
3. **Configure the desk:** already done: "Registered signals at the latest close" shows the trigger, the pre-close
   check compares the 3:50 PM price with it, and the paper ticket and paper book follow a logged long to its exit.
4. **Detect it developing:** the trigger distance shrinking (-3.0% on 2026-11-17). Write the level down for the next
   day's 3:50 PM check.
5. **Current context:** event risk (Nvidia's reaction session), an inverted VIX curve, QQQ below its 200-day average.
   None is part of the rule, and whether any changes the rule's results is untested (ideas 7 and 8). They are tier 3:
   they can reduce size or defer, not reverse the rule.
6. **Still relevant?** Yes while the evidence status is "ok", the dates cross-check, the verdict has not changed,
   and the forward record is inside its band. Re-read the card when any of those changes.

## Scenario C. Conflicting evidence

*The user's reading is bearish (QQQ below both averages, inverted VIX curve, narrow leadership breaking), while the
lab's evidence for the next few sessions after a deep oversold reading is bullish.*

1. **Same question?** Usually not. The lab's evidence is about the next 1-10 sessions after a specific close. A
   bear-market view is about weeks or months. Both can be right.
2. **What is tested?** The bullish side has a registered, provisional Lead. The bearish side has no tested short rule:
   all three rally shorts failed 1993-2009, and the 200-day state showed no evidence as a signal.
3. **Decide by a rule written in advance, not on the day:** tested evidence sets direction; untested context can only
   reduce size, shorten the hold or skip. Write this rule into your process once.
4. **Do not resolve by searching.** Re-running variants until one agrees with the view (a different band, a trend
   filter tried after looking) is cherry-picking; the lab's lock and record are there to make that visible.
5. **Turn the conflict into a test:** "oversold bounces below the 200-day average are weaker" is idea 8; register it
   and live with whatever it says.
6. **Record both:** your call with "leans on: regime" and the stance; in a year the scoreboard shows which helped.

## Scenario D. A novel catalyst with little history

*[Hypothetical] An unexpected policy announcement during the session hits semiconductor stocks; QQQ falls sharply
intraday. Nothing like it is in the event calendar.*

1. **Analogues by market state, not by story.** The lab cannot search narratives. Describe the state with observable
   variables (size of the QQQ drop, gap or intraday range, VIX change, whether an oversold rule fired) and use those
   to pull comparable days and the trades that followed from the trade list.
2. **Know the limits:** few analogues, chosen from memory (the vivid ones), in different macro conditions. Each is an
   anecdote. Show the spread of what followed, not an average with false precision.
3. **Evaluate without manufacturing confidence:** let the registered rules speak only if one actually fires; treat the
   catalyst as tier 3 (size and timing), and prefer smaller size or no trade over a confident call.
4. **Record it for future research:** a journal note the same day (the note keeps a snapshot of the page and later
   shows what followed), an idea in the ledger at stage "observation", and a line in a catalyst log (forward), so in
   a few years such days can be studied as a set.

## Scenario E. Evening preparation and the next day (real state of 2026-11-17)

**Evening (after the refresh, 9:39 PM ET):**
1. Daily thesis: flat, close-only setup (QQQ RSI(2)). Evidence usable, 4 days old.
2. Note the triggers for 2026-11-18: QQQ Bollinger at 637.06 or lower, RSI(14) at 627.00 or lower.
3. Events: Nvidia reported after the close; the next session is its reaction day. Next scheduled jobs report
   2026-12-04, CPI 2026-12-10 (per the desk's calendar check).
4. Context: inverted VIX curve; QQQ below both averages; equal weight leading.
5. Record a call (it costs a minute and the call log is still empty): for example "flat QQQ; would buy at the open
   only after a next-open Lead fires; invalid if ...".
6. Do not consult the lab for a new test tonight: the registered evidence answers tonight's question.

**Overnight:** the Nvidia reaction moves futures. The desk's futures card is empty (no snapshot has ever been taken),
so this has to be read elsewhere. Note the overnight move; it does not change the stance (already flat).

**Before the open (8:00-9:25 AM ET):** re-read the page's morning view and news. Question: has anything made the
registered levels irrelevant today (a halt, a gap so large the bounce happened overnight)? If QQQ is set to open far
above the close, the RSI(2) bounce is partly taken already; idea 7 would measure that, untested today.

**After the open:** no registered intraday rule; the Intraday tab is observation only. Do not trade the open on the
daily rule's behalf.

**3:50 PM ET:** the decisive moment for the close route. Is QQQ at or below 637.06? If so, the Bollinger rule is
likely to fire at the close, and its closing-price pricing is a Lead: a market-on-close order on that estimate is the
only way to use the stronger close-entry evidence. The pre-close check logs this before the close. If QQQ is far above
the trigger, nothing to do.

**After the close:** the evening refresh decides. If a next-open Lead fired, the stance is long and the paper ticket
shows the exit rule; if not, flat. Either way, record the call.

## Scenario F. Eliminating information overload

*[Hypothetical design; not run] Does the "VIX term structure inverted" reading deserve a place in the daily routine?*

1. **Decision it should improve:** take or skip a QQQ Bollinger trade; or expect bigger moves.
2. **Two registered tests, written now:**
   - Unconditional: SPY and QQQ next 5 sessions (mean and absolute move) after days with VIX > VIX3M against other
     days, 2010 on. VIX3M starts in 2009, so there is no 1993-2009 check; the out-of-sample part is forward.
   - Conditional: QQQ Bollinger trades split by inversion at the signal close.
3. **Power, before running:** the conditional split can detect only about 1.4 points per trade; the unconditional
   test can detect about 0.8 points over 5 sessions in the mean and much smaller differences in move size.
4. **Decision rules, written now:**
   - size effect, no direction: tier 3 (risk), shown when a position is live;
   - neither, with narrow intervals: tier 5, removed from the daily view;
   - wide intervals: tier 4 (context), no daily attention, re-test after more data;
   - a direction effect in the unconditional test that also shows in the split's sign: tier 2, candidate filter,
     registered as a new strategy version.
5. **Record** the outcome in the idea ledger whatever it is. A "no" removes a card from your attention for good reason.

## Scenario G. Edge deterioration

*[Hypothetical numbers] The QQQ Bollinger rule after 20 forward trades.*

1. **Band, set at registration from development trades:** mean excess m = +60 bp, per-trade standard deviation
   s = 256 bp. Lower edge after n forward trades: m - 2 s / sqrt(n): n = 5: -169 bp; n = 10: -102 bp; n = 20: -54 bp;
   n = 40: -21 bp.
2. **[Hypothetical]** After 20 forward trades (about three years at 6 a year) the forward mean excess is -80 bp: below
   -54 bp, so the status becomes **deteriorating**.
3. **Lab:** writes the status into the evidence card and the weekly log; does not re-fit the rule.
4. **Checks before concluding:** were the paper trades identical to the backtest's (implementation)? Did costs or
   execution change (costs)? Did the market spend the period in conditions the rule never saw (regime: idea 8)? Is
   one crash trade responsible (MAE, best and worst trades)?
5. **Desk:** shows the status beside the stance. With today's stance rules the page would still call "long" on a fired
   Lead; a stance-rules version that refuses deteriorating rules (or halves their weight in the user's own sizing) is
   the change to make in advance, not after a loss.
6. **User:** decide retire or keep monitoring, and write the reason. A modified rule (a filter, a new exit) is a new
   version with its own band and a fresh forward start; the old one stays in the registry as retired.
