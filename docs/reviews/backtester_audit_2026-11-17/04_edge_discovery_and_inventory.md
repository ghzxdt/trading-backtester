# 4. Edge discovery versus validation, and the trading-edge research inventory

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Brief sections 5 and 6;
deliverable 5.

## 4.1 What the backtester is best suited for

| Activity | Fit today | Why |
|---|---|---|
| Testing existing hypotheses | **Strong** | Registration, one-look holdout, correction, kept inputs, exact rebuild |
| Comparing strategies | Good, narrow | Same costs, periods and benchmarks for all 12; no cross-run comparison |
| Studying market behaviour after a daily price condition | Good, narrow | Event-study engine with a sound null; one condition at a time, price data only |
| Evaluating risk | Weak | Equity drawdown only; no MAE, worst-trade, tail or leveraged view |
| Identifying favourable conditions (regimes) | **Not supported** | No regime split; VIX loaded but unused |
| Monitoring edge deterioration | **Not supported** | No forward slice, no rolling view, no alert on a changed verdict |
| Optimising execution | Not supported | Daily bars; two entry prices only |
| Discovering unknown relationships | Deliberately limited | No search or screen; every question is registered first |

**How each should be approached differently.**
- *Validation* (the backtester's job): one rule, written before results, judged once on fixed periods with a
  correction for the family it belongs to. Output: a verdict and an evidence card.
- *Comparison*: only between rules registered in the same family and run on the same snapshot; differences smaller
  than the rules' own uncertainty are not differences.
- *Market-behaviour study* (descriptive): no verdict needed; report the distribution, sample size and an interval,
  and label it "description". The research app already does this for regimes and hourly gaps.
- *Risk evaluation*: about the worst paths, not the average; needs MAE, worst trades, and the instrument actually
  traded (3x ETFs reset daily).
- *Condition finding (regimes)*: a filter is a new rule; it must be registered and must beat the unfiltered rule
  out of sample, not just look better in-sample.
- *Deterioration monitoring*: compare forward trades with a band set in advance; never re-fit the rule.
- *Discovery*: if done at all, in a separate, labelled exploratory mode on the development period only, with every
  variant counted, and with any finding re-registered and confirmed on data the search never saw (forward data, or
  a held-back period). The 1993-2009 holdout must not be used for discovery.

## 4.2 Can it act as an exploratory market-research tool?

Partly. The event-study engine is a general "what happens after condition X" machine for any condition computable
from daily OHLCV (and the VIX column) of the nine ETFs, with a null that respects clustering and a family-wide
correction. What stops it being an exploration tool today:
1. Every question needs Python code and registration; there is no query form.
2. It conditions on price only. Events, macro data, credit, breadth, GEX/DIX and news are in the research app and
   not read.
3. It reports means and p-values only: no distribution, quantiles, interval, or occurrence frequency.
4. No conditioning on two things at once (signal x regime) and no comparison of "signal alone vs signal + filter".
5. Daily horizons from the close or next open only; no overnight-only or intraday horizons.

## 4.3 Example questions: answerable today?

| Question | Today | How, or what is missing |
|---|---|---|
| What typically happens after a particular market condition? | **Yes, for daily price conditions** | Register a `Study`; read excess at 1/5/10 sessions. Missing: distributions and intervals |
| How does the next session behave after a significant sell-off? | **Partly** | RSI(2) < 10 and Bollinger studies at h = 1 cover it from the close; "big drop" by size of move is a new study. Next-session open-to-close or overnight split needs a new horizon type |
| Does a relationship between indices have predictive value? | **No (research app: partly)** | Studies see one symbol at a time. Needs multi-symbol conditions (e.g. QQQ minus SPY 20-day return). The research app's "breakaway" tests looked at this descriptively |
| How do volatility changes alter subsequent behaviour? | **No** | VIX is in the frame but no study uses it; VIX3M, VIX9D, VVIX not loaded. Needs registered VIX conditions and splits |
| Does a premarket move continue or reverse? | **No** | No premarket data. Partial proxy: the open-to-close return after an overnight gap (daily open vs previous close) is computable from daily bars; the research app's hourly base rates describe gap fills since Dec 2023 |
| What conditions make a successful setup fail? | **No** | Needs failure analysis: split a rule's trades by pre-declared conditions (gap size, trend, VIX, events) |
| Does combining two signals beat either alone? | **No** | Needs a combined rule plus a nested comparison against each component, with the same exit and family correction |
| Does a signal add information beyond price action? | **No** | Needs a baseline model of price-only expectations (e.g. same-volatility days) and an incremental test |

## 4.4 The inventory

Each card has the 14 fields the brief asks for, abbreviated: **Hyp** hypothesis; **Why** economic or behavioural
reasoning; **Tickers**; **Info** required; **Signal** precise conditions; **Expect** expected outcome; **Horizon**;
**Bench** benchmark; **Method** testing method; **Risks**; **Invalid** what would invalidate it; **Research app**
relevant features; **Support** whether the backtester supports the test today; **Status**. Statuses use the
brief's categories: validated (none qualify yet), insufficient evidence, untested, rejected.

Statistics quoted are from the 2026-11-17 runs (data through 2026-11-13), development period 2010 on, ETF pricing
after 2 bp, unless stated. Signals marked "proposed" are my suggestions for registration; none has been run.

### E1. Deep-oversold bounce in QQQ (registered)
- **Hyp:** after a deep short-term sell-off, QQQ recovers part of it within days.
- **Why:** forced and emotional selling overshoots; liquidity providers are paid to absorb it; short-term reversal
  in index returns is a long-documented pattern.
- **Tickers:** QQQ (registered); TQQQ as an expression (untested).
- **Info:** daily closes.
- **Signal:** close below the lower Bollinger band (20, 2), or RSI(14) < 30; buy at the next open; exit at the first
  close above the 5-day average, at most 10 sessions.
- **Expect:** Bollinger +0.81% per trade (104 trades, 74% wins); RSI(14) +2.84% (26 trades, 92% wins).
- **Horizon:** 1-10 sessions (mean about 3-4).
- **Bench:** every same-length trade (+0.21% / +0.16%); risk-matched buy-and-hold; QQQ held.
- **Method:** registered Lead v2; then forward trades against a pre-registered band.
- **Risks:** crash continuation (worst intra-trade -19.7% Bollinger, -11.7% RSI(14)); event inside the hold; the
  two rules are largely one bet (77% of RSI(14) days are Bollinger days).
- **Invalid:** forward mean excess below the band in [06](06_validation_framework.md); a registered regime test
  showing the edge exists only in conditions that no longer occur.
- **Research app:** registered signals and trigger levels, paper ticket and book, regime, events and earnings,
  risk by leverage.
- **Support:** yes.
- **Status:** insufficient evidence for a validated edge: provisional Lead (historical). Forward record: one signal
  day, the 2026-11-06 close, logged as a stance before the next open; the research app's paper book shows two trades
  from it (SPY and QQQ), both gains, mean +1.96% net. One episode says nothing yet. Not validated.

### E2. The same bounce in SPY (registered)
- **Hyp / Why / Signal:** as E1, on SPY.
- **Expect:** Bollinger next-open +0.50% (99 trades); RSI(14) next-open +0.79% (24).
- **Status:** insufficient evidence ("No edge" at next open; RSI(14) hold-5 close entry "Failed holdout"). The same
  direction as QQQ with weaker statistics and a worse worst case (-22.9% intra-trade). Do not read as "QQQ works,
  SPY doesn't"; read as "the evidence is thinner than it looks for both".
- **Support:** yes.

### E3. The overnight part of the bounce (close entry beats next open) (registered as pricings)
- **Hyp:** part of the bounce happens between the signal close and the next open.
- **Why:** sellers exhaust into the close; overnight risk premium; next-day buyers arrive at the open.
- **Tickers:** SPY, QQQ.
- **Signal:** the E1/E2 rules bought at the signal close.
- **Expect:** QQQ RSI(2) < 10 with the 5-day-average exit: +0.61% at the close vs +0.49% at the next open (192 trades);
  a Lead only at the close.
- **Horizon:** overnight plus the hold. **Bench:** the next-open pricing of the same trades.
- **Method:** pre-close decision at about 3:50 PM ET, logged before the close; measure the flip rate.
- **Risks:** the 3:50 PM price is not the close; the flip rate is unknown.
- **Invalid:** a high flip rate, or forward close-entry trades no better than next-open ones.
- **Research app:** pre-close check (built, never recorded yet), idea 9 in the ledger.
- **Support:** historical yes; forward requires the research app's daytime job to run.
- **Status:** untested forward.

### E4. A large overnight gap uses up the bounce (idea 7)
- **Hyp:** next-open oversold trades do worse when the open gaps up strongly from the signal close.
- **Why:** the gap captures the reversal before an open buyer can.
- **Tickers:** SPY, QQQ.
- **Info:** daily open and close (available).
- **Signal (proposed):** E1 trades split by the next open's gap from the signal close into buckets fixed in advance
  (for example below -0.5%, -0.5% to +0.5%, +0.5% to +1.5%, above +1.5%).
- **Expect:** lower excess in the gap-up buckets. **Horizon:** the E1 hold.
- **Bench:** the unsplit rule; same-length trades.
- **Method:** registered split; development only first; if adopted as a filter, judged as a new version.
- **Risks:** small buckets (26 RSI(14) trades cannot be split four ways meaningfully).
- **Invalid:** no monotone pattern across buckets.
- **Research app:** "Overnight and inflation" card (futures since 4 PM, once snapshots run), idea 7.
- **Support:** data yes; needs a split feature (small code change).
- **Status:** untested.

### E5. Oversold rules depend on the regime (idea 8)
- **Hyp:** the bounce is larger (or only exists) in some trend or volatility states.
- **Why:** in a bear market, oversold can stay oversold; in high volatility the payoff to supplying liquidity is larger.
- **Tickers:** SPY, QQQ. **Info:** VIX (in the frame), 200-day average, optionally credit spreads (Baa-10y since 1986).
- **Signal (proposed):** E1 trades split by SPY above/below its 200-day average x VIX below 20 / 20-30 / 30 and up,
  the buckets the research app already declared on 2026-11-08.
- **Expect:** unknown in direction; that is the point of registering first.
- **Bench:** the unsplit rule. **Method:** registered split; a filter adopted only as a new version.
- **Risks:** six cells from 26 trades is too few for RSI(14); Bollinger (104) can bear it.
- **Invalid:** no difference beyond what the cells' sample sizes allow.
- **Research app:** regime card, "what happened after days like today".
- **Support:** data yes; split feature missing.
- **Status:** untested. (I deliberately did not look; see [01 section 1.9](01_technical_accuracy_audit.md).)

### E6. Leveraged-ETF expression (idea 11)
- **Hyp:** the E1 trades keep their edge in TQQQ (or UPRO for SPY), net of daily-reset effects.
- **Why:** 3x exposure over a short hold mostly scales the move; path effects are second-order over 3-4 sessions,
  except in crashes.
- **Tickers:** TQQQ, UPRO (2010 on; no 1993-2009). **Info:** their daily OHLCV (available).
- **Signal:** E1 signals on QQQ; trade TQQQ at the next open; same exit dates.
- **Expect:** about 3x the QQQ mean with more than 3x the worst losses.
- **Bench:** 3x the QQQ result; TQQQ same-length trades.
- **Method:** pricing mode `tqqq_next_open` (new version); report MAE.
- **Risks:** the -19.7% QQQ intra-trade low becomes roughly -50% or worse.
- **Invalid:** realised TQQQ results materially below 3x QQQ, or MAE that would breach any loss limit.
- **Research app:** expressions and risk by leverage; idea 11.
- **Support:** data yes; pricing mode missing.
- **Status:** untested. A prerequisite before any leveraged use.

### E7. Rally fade (big up day, then weak)
- **Hyp:** after a big up day the index underperforms the next day or week.
- **Why:** short-covering exhaustion. **Tickers:** SPY.
- **Signal:** the research app's day type "big rise" (SPY move > 1 expected move).
- **Status:** **rejected as a short** (all three rally shorts failed the 1993-2009 holdout, QUANT_REVIEW 2026-11-07;
  idea 4 dropped). A "be less long" reading remains plausible but has not been registered.
- **Support:** day types are not in the backtester; reproducible from daily data.

### E8. Normal drop, long five sessions (frozen paper experiment)
- **Status:** insufficient evidence: survives the holdout but is mostly market drift (+0.34% per trade gross against
  +0.25% for random entries in the same windows, QUANT_REVIEW 2026-11-07); in the research app's frozen forward
  experiment. Weaker cousin of E1.

### E9. Momentum and trend rules (registered, failed)
- EMA(21)/EMA(50) touches in an uptrend, MACD crosses, 20-day breakouts, the 200-day state, volume-spike down days.
- **Status:** **rejected**: none of the 63 tests of these seven studies (SPY, QQQ, IWM; 1, 5 and 10 sessions) passed.
  Keep them in the registry so they are not re-tested casually. One near miss belongs to the oversold family rather
  than to trend: SPY's down day on twice normal volume, next session from the close: +28.7 bp (p 0.020, q 0.135),
  1993-2009 +23.5 bp (p 0.054), but only +1.9 bp from the next open. Like E3, it is an overnight effect that the
  evening page cannot use.

### E10. Event-day volatility (CPI, jobs, Fed)
- **Hyp:** event days move more than normal days; direction is not predictable.
- **Why:** information arrives at a known time.
- **Info:** the research app's event calendar (575 events since 2010).
- **Status:** **verified size effect, no direction** in the research app (jobs-morning gaps about 1.2x, Fed
  afternoons 1.29x; direction p = 0.69 for jobs). Useful for risk (an event inside a hold window), not as an entry.
- **Support:** the backtester cannot read the calendar yet; a registered "event inside the hold" split of E1 is the
  useful test.

### E11. Weekend and holiday gaps are larger
- **Status:** **verified size effect** in the research app (weekend 1.14x, holiday 1.50x weeknights). Risk input for
  holding E1 trades over weekends and holidays. Not a direction signal.

### E12. Post-earnings behaviour of QQQ after mega-cap reports
- **Hyp:** QQQ's reaction session after a top-10 holding reports is larger, and its direction after the first hour
  carries information.
- **Info:** earnings dates (research app: about 4 years from Yahoo, current calendar from Nasdaq), hourly bars since
  Dec 2023.
- **Status:** untested. **Support:** no (needs the earnings dates as an event source; hourly direction tests need
  the hourly bars).
- **Note:** small sample (10 companies x 4 a year x about 3 years with hourly bars), so a size study is feasible,
  a direction study is not.

### E13. Breadth divergence (equal weight against cap weight)
- **Hyp:** when RSP lags SPY sharply, the index's next weeks are weaker (narrow leadership).
- **Info:** RSP and SPY since 2010.
- **Status:** insufficient evidence: the research app's "breakaway" tests found nothing for RSP (p 0.47, 0.76) and a
  hint for "QQQ much weaker than usual against SPY" (p 0.053). **Support:** needs multi-symbol conditions.

### E14. Volatility term-structure inversion as context for the bounce
- **Hyp:** when VIX is above VIX3M (stress), oversold bounces are larger but riskier.
- **Info:** VIX3M since 2009 (research app). **Signal (proposed):** E1 trades split by VIX/VIX3M > 1 at the signal.
- **Status:** untested. **Support:** needs VIX3M in the backtester's data and a split. Live today: the 2026-11-17
  close shows the curve inverted (25.5 against 25.0).

### E15. Credit stress filter
- **Hyp:** oversold bounces fail more often when credit spreads are widening.
- **Info:** Baa-10y since 1986 (market data, not revised), HY spreads 3 years.
- **Status:** untested. **Support:** needs the credit file in the backtester; a registered split.

### E16. GEX below zero means bigger next-day moves
- **Status:** **verified size effect** in the research app (1.31x after adjusting for VIX), direction none. Manual
  data, published after the close. Context for sizing risk, not for entries.

### E17. Gap fill and first-hour behaviour (intraday base rates)
- **Hyp / finding:** gaps over 0.5% filled the same day only 27-37% of the time; 0.2-0.5% gaps 53-72%; after 10:30
  the day kept the first hour's direction 49-59% of the time (research app, hourly bars, first look 2026-11-14).
- **Status:** descriptive history only (about 730 sessions); not a tested edge. **Support:** no (no intraday data in
  the backtester).

### E18. Opening-range break with VWAP (orb-continuation-v1)
- **Status:** registered in the research app, 5 prototype trades, blocked until 20 sampled liquidity days exist.
  12 sessions of minute bars so far. Untested.

### E19. 3:50 PM signal holds to the close (idea 9)
- **Status:** untested; forward-only measurement (pre-close check); no record yet.

### E20. Same-day options: implied against realised move (idea 10)
- **Status:** untested; no snapshot taken yet (needs a daytime run). Forward-only data.

### E21. Macro surprise (CPI or payrolls against the Cleveland Fed nowcast or Kalshi odds)
- **Status:** untested; forward-only (no free history of expectations). The research app stores first-release
  values (ALFRED) but no expectation history.

### E22. Sector rotation, correlation breakdowns, single-stock catalysts
- **Status:** missing data. No sector ETFs or constituent prices are collected (only ten mega-cap closes for the
  movers flag, about 65 days). Out of scope until the user adds data.

### E23. Time-of-day effects
- **Status:** coarse description possible from hourly bars (research app); a real test needs minute history
  (Alpaca's free tier since 2016, if the user chooses).

## 4.5 Summary of the inventory

| Status | Hypotheses |
|---|---|
| Validated (forward-confirmed edge) | None |
| Insufficient evidence (historical support, unconfirmed) | E1 (provisional Lead), E2, E3, E8, E13 |
| Verified size effects, no direction (risk inputs) | E10, E11, E16 |
| Untested, testable on data already held | E4, E5, E6, E14, E15, E12 (size) |
| Untested, forward collection needed | E3 (forward), E17-E21 |
| Rejected | E7 (as a short), E9 |
| Missing data | E22, E23 (minute history) |

The most valuable next tests are E6 (before any leveraged use), E4 and E5 (they decide when E1 should be ignored),
and E14 or E15 as a single registered context filter.
