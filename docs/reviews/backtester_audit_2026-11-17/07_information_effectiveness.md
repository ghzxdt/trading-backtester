# 7. Research information effectiveness: what deserves attention

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Brief section 9; deliverable 8.

## 7.1 The question, and what history can settle

The research app shows a lot: 12 tabs, and on the Daily thesis alone 22 cards. The question is which of them change
outcomes. History can answer it only for information that (a) has a long, point-in-time record and (b) can be
expressed as a condition known before a decision. For everything else the honest answer is "cannot be evaluated
yet", and the right response is to collect it forward in a form that can be tested later, not to guess.

Two facts set the limits:
- **The decision-relevant rules are rare.** QQQ's two next-open Leads produce about 6 and 1.5 trades a year. A filter
  that splits 104 Bollinger trades into two halves can only show a difference of about 1.4 percentage points per
  trade with 80% power (per-trade standard deviation 2.56%); for the 26 RSI(14) trades, about 3.6 points. Almost any
  realistic filter on these rules will come back "insufficient evidence". [Calculation from the development
  statistics; not a historical finding about any filter.]
- **Unconditional questions have more data.** "Does variable X shift SPY's next 5 sessions?" uses about 850
  non-overlapping 5-day windows since 2010 (about 1,700 since 1993 for SPY). A condition true on 10% of days can show a
  difference of roughly 0.8 points over 5 sessions (5-day standard deviation about 2.5%). This is where history can
  sort context from noise.

So the hierarchy below separates three kinds of verdict that the brief asks to keep apart: **demonstrated value**,
**demonstrated lack of value**, and **insufficient evidence**.

## 7.2 Inventory of the research app's information

Depth and point-in-time status as found on 2026-11-18.

| Information (tab / card) | History held | Point in time? | Backtester can test it |
|---|---|---|---|
| Oversold rules and trigger levels (Daily thesis) | 1993/1999 on | Yes (close) | Yes, today |
| Trend vs 50/200-day (Regime) | 1993 on | Yes | Yes, today (price) |
| VIX level, implied daily move (Regime, risk card) | 1990 on | Yes (close published after 4 PM) | Yes, today (VIX in frame, unused) |
| VIX term structure VIX/VIX3M (Regime) | 2009 on | Yes | After adding VIX3M |
| VIX9D, VVIX, VIX1D | 2011 / 2006 / 2022 on | Yes | After adding the files |
| Credit spreads: Baa-10y; HY, CCC (Regime) | 1986 on; 3 years | Yes (market data) | After adding the file |
| Breadth: RSP vs SPY (Regime) | 2010 on | Yes | After multi-symbol conditions |
| Rates: 2y, 10y, 10y-3m, breakeven (Regime, Macro) | Decades | Yes (market data; FRED dates +1 day) | After adding the files |
| "What happened after days like today" (trend x VIX buckets) | 1993 on | Yes | Descriptive already, in the research app |
| Events: CPI, jobs, Fed (Events) | 2010 on (575) | Scheduled dates yes; emergency actions need care | After reading `events.csv` |
| Release values, first releases, revisions (Macro) | ALFRED vintages since 2015 | First-release yes | After vintage handling; few events |
| Fed funds, NFCI, St. Louis stress, Sahm (Macro) | Long | NFCI and stress are revised; Sahm real-time is not | Only with vintages (NFCI) |
| Mega-cap earnings dates (Events) | About 4 years | Dates yes; times partly | After an earnings event source |
| Movers in the top ten holdings | About 65 days | Yes | No (too short) |
| News since the last close (headlines) | First seen since 2026-11-08 | First-seen time, not publication | No: forward only |
| Futures since 4 PM, Cleveland Fed nowcast (morning card) | None collected yet | Would be | No: forward only |
| Intraday base rates (hourly bars) | Since 2023-12-18 (about 730 sessions) | As traded, not adjusted | No intraday data in the backtester |
| Same-day options (0DTE) | None collected yet | Would be | No: forward only |
| Expressions and risk by leverage | Price history | Yes | Partly (no leveraged pricing) |
| Your calls, "leans on" tags | 0 calls | Yes | Forward only |
| Stance log, paper book | 8 stances, 2 paper trades | Yes | Forward only |
| Indexes tab: day types, overnight vs day, event days, gaps, adverse moves | 2010 on / 1993 on | Yes | Day types reproducible |
| Tickers tab: order-flow stand-ins (volume ratio, close location, up-volume share, A/D line) | 2010 on | Yes (daily) | Yes, today (price and volume) |
| Leverage (Kalshi perps), Kalshi event markets | Weeks | Snapshots | No |
| GEX / DIX | 2011 on (manual) | Published after the close | After adding the file |
| Intraday tab: minute bars, VWAP, opening range, levels, options context | 12 sessions | Receipt times kept | No |

## 7.3 How to test whether a piece of information earns its place

Use one procedure for every item, registered before looking:

1. **Name the decision it is supposed to improve.** For example "take the QQQ Bollinger trade or not", "hold over the
   weekend or not", "expect a bigger or smaller day".
2. **Baseline:** the decision without it (the registered rule alone, or the unconditional base rate).
3. **Nested comparison:** the same trades or days split by the information, with the split fixed in advance. Report the
   difference in mean excess (or in move size) with a 90% interval, and the counts.
4. **Out of sample:** fix the split on 2010 on; check the effect's sign on data the choice did not see (1993-2009
   where it exists and has not been used for this idea; otherwise forward).
5. **Count it** in the family with every other filter tried.
6. **Classify:**
   - *Adds value:* interval above zero in development, same sign out of sample, mechanism makes sense.
   - *Demonstrated lack of incremental value:* enough data that the interval is narrow and includes zero (for
     example a difference within +/- 0.3 points per 5 sessions on thousands of days).
   - *Insufficient evidence:* the interval is wide. Most filters on the oversold rules will land here; that is a
     reason to keep them out of the decision, not proof that they are useless.

For direction claims use mean excess; for risk claims use move size (absolute return, range, MAE), where the
samples are larger and the research app's size effects already show real differences.

## 7.4 The information hierarchy (evidence as of 2026-11-18)

### Tier 1. Validated decision-driving information
None meets the bar of a forward-confirmed edge. **Provisionally decision-driving** (the research app already acts on
them and the evidence is the strongest held): the QQQ next-open oversold Leads (close below the lower Bollinger
band; RSI(14) < 30) with their exit, and the evidence status that gates them (export age, date cross-check). Also the
next session's trigger levels for those rules. Attention: every evening.

### Tier 2. Promising but unvalidated
| Item | Evidence | What would move it |
|---|---|---|
| Closing-price entry for the same rules (pre-close route); QQQ RSI(2) < 10 at the close | Lead at the close only; flip rate unmeasured | Pre-close records showing a low flip rate and forward trades in line |
| SPY oversold rules | Same direction as QQQ, weaker statistics | A registered pooled test or forward record |
| Overnight gap after a signal (idea 7) | Plausible; untested | Registered split |
| Trend and volatility regime (idea 8); VIX term structure; credit widening | Plausible; untested | Registered splits on the Bollinger trades; unconditional tests on all days |
| Normal drop, long 5 sessions (frozen paper experiment) | Survives 1993-2009, mostly drift | Forward record |
Attention: read when a setup is live; do not let them override tier 1 until tested.

### Tier 3. Conditional confirmation (risk and applicability, not direction)
| Item | Evidence | Use |
|---|---|---|
| Event inside the holding window (CPI, jobs, Fed) | Verified size effects (jobs gaps about 1.2x, Fed afternoons 1.29x); no direction | Smaller size or skip; never a reason to flip direction |
| Mega-cap earnings inside the window (e.g. Nvidia after the 2026-11-17 close) | Larger QQQ reaction sessions (research app's earnings table); no direction test | Same as events |
| Weekend and holiday holds | Verified: gaps 1.14x and 1.50x weeknights | Same |
| GEX below zero | Verified size effect (1.31x after VIX) | Same; manual data |
| VIX level and implied move; loss scenarios by leverage | Descriptive, long history | Sizing guardrail |
| Intraday gap-fill base rates | Descriptive, about 730 sessions | Morning context for the open |
Attention: whenever a position or setup is live; they decide "how much" and "whether now", not "which way".

### Tier 4. Contextual
Trend states, breadth, rates and curve, credit levels, the Macro tab (fed funds, NFCI, stress index, Sahm rule,
breakevens), first-release values and revisions, "what happened after days like today", news headlines, movers,
Tickers-tab statistics, futures and nowcast (once collected). These describe the market. None has a tested link to
outcomes in either app. Attention: weekly, or when something is extreme (a percentile near 0 or 100), and as input
to registered tests, not to the daily call.

### Tier 5. Redundant or low value (demonstrated)
| Item | Demonstrated | Caveat |
|---|---|---|
| Trend and momentum entries: EMA(21)/EMA(50) touches in an uptrend, MACD crosses, 20-day breakouts, the 200-day state as an entry; down-volume spikes | None of the 63 registered tests of these seven studies passed (SPY, QQQ, IWM at 1, 5 and 10 sessions); no positive 1993-2009 result except one near miss (SPY volume spike, next session from the close only) | Demonstrated lack of *standalone* value at these horizons; their value as filters is untested |
| Direction on event days | Jobs p = 0.69, CPI p = 0.99, Fed p = 0.98 (research app) | Size effects remain useful (tier 3) |
| Rally shorts | Failed 1993-2009 (all three) | Retired |
| Watching DIA, RSP, SPY and QQQ as separate views | Research app: "basically one bet", QQQ about 1.13x SPY | Breadth (RSP vs SPY) remains context, not a separate thesis |
| Kalshi perp tables for the daily thesis | User decision 2026-11-08: ETFs only | Collection continues for later |
| "Original vs fixed", frozen backtests tabs | Historical records | Audit trail, not daily information |
Attention: none day to day. Keep them in the record so they are not re-tested casually.

### Tier 6. Cannot yet be evaluated
News (first-seen archive since 2026-11-08), same-day options, futures and nowcast snapshots, macro surprises (no
expectation history), Kalshi event and perp markets, the pre-close flip rate, intraday opening-range and VWAP rules
(12 sessions), liquidity samples, option strike concentrations, the user's calls and their "leans on" tags.
Attention: none for decisions; keep collecting (7.6).

## 7.5 The brief's examples, answered for these apps

- **Does a volatility filter improve a price-based strategy?** Not yet known. Testable now with data on hand: register
  the Bollinger trades split by VIX bucket (and by VIX/VIX3M > 1), development first, 1993-2009 once for the VIX split
  (VIX3M does not reach back). Expect "insufficient evidence" unless the difference is above about 1.4 points per
  trade; in parallel run the unconditional version (VIX bucket and next 5 sessions on all days), which has the data
  to say something.
- **Does sentiment improve outcomes beyond momentum?** Cannot be evaluated: no sentiment history exists, and momentum
  itself showed no standalone value. Forward: classify each day's headlines with a fixed rule written now, store the
  label daily, test after about two years.
- **Does sector confirmation improve a directional thesis?** Missing data: no sector ETFs are collected. Free daily
  sector ETF history (Yahoo) would make a registered test possible; until then, no.
- **Does another index add information?** For direction, SPY, QQQ, DIA and RSP are one bet (tier 5). Relative strength
  (QQQ vs SPY, RSP vs SPY, IWM vs SPY) is a separate question: the research app found only a hint (p = 0.053 for "QQQ
  much weaker than usual vs SPY"). Testable in the backtester once a study can use two symbols.
- **Does a news signal predict anything after the market's first reaction?** Not with current data. It needs prices at
  the moment the headline was first seen (minute bars are kept only since 2026-11-02 and Yahoo serves only 5 days), so
  the measurement starts from the first-seen time forward. Collect now; test after a year of events.

## 7.6 Forward collection, so tier 6 can be tested later

1. **Freeze a daily feature row.** Each evening the research app already builds `thesis_state.json` with every card.
   Append a compact, hash-chained row per session (regime bucket, VIX, VIX/VIX3M, credit change, breadth, events and
   earnings in the next 5 sessions, news count and tag, futures move when collected, rule states and trigger
   distances). This is the point-in-time record the backtester will need; today the state file is overwritten.
2. **Register the questions now.** Write in the idea ledger which features will be tested, against which outcome
   (next 5 sessions; rule trades), with which split, and when (for example after 250 sessions). Data collected
   forward is only clean if the test is fixed before it accumulates.
3. **Tag your own calls.** The "leans on" field (signal, regime, event, news, levels, other) turns the call log into a
   test of which information helps *your* decisions; it is empty today.
4. **Keep the daytime jobs running.** The pre-close check, same-day options, futures and liquidity samples have never
   recorded because the laptop was off during market hours; nothing in tier 6 accumulates until it is asleep or on.
5. **Read at fixed dates, not when something looks interesting.** Descriptive reads after 60 sessions; direction tests
   after enough events (about 100) or a year.

## 7.7 A smaller daily screen

| Show by default | One click away | Hidden from the daily routine | Collecting silently |
|---|---|---|---|
| Tier 1: stance, evidence status, fired rules, trigger levels, open paper trades and their exit level | Tier 4 context (regime details, macro, breadth, news list) | Tier 5 | Tier 6 |
| Tier 3: events and earnings in the next 5 sessions, weekend/holiday, VIX and implied move, loss at the intended leverage | Tier 2 items for a live setup | | |

The aim is that the evening read takes ten minutes and ends in a recorded call, and that every other card waits for
a registered test to earn its way up.
