# 6. Edge validation framework

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Brief section 8; deliverable 7.

The aim is not the most profitable configuration. It is to decide whether a relationship is robust enough to use
in future decisions, and to notice when it stops being so.

## 6.1 The fifteen steps, mapped to what exists

| # | Step | Where it happens | Supported today? | Gap | Class |
|---|---|---|---|---|---|
| 1 | Record the observation and reasoning | Research app: Journal note, then Idea ledger (title, claim, route) | Yes | Journal is empty; ideas are entered by hand | - |
| 2 | Make it measurable | Idea ledger "how to test it"; backtester `Study`/`Exit` code | Yes | No structured rule format shared by both apps | Integration |
| 3 | Expected outcome and holding period | Idea ledger text; exit rule in code | Partly | No field for the expected size or the horizon | Integration |
| 4 | Benchmark | Fixed in code (all days; same-length trades; risk-matched) | Partly | No volatility-matched baseline; no cash yield; no overlay view | High value |
| 5 | Signal conditions before results | `catalog.py`/`strategies.py` + `rule_lock.json` | **Yes, enforced** | - | - |
| 6 | Information available at decision time | Causality tests; entry modes; research app's "known at" tags | Partly | No per-rule decision timestamp; close entries and the close-decided exit need a pre-close estimate | High value |
| 7 | Initial exploratory test | Indicator studies; partial runs | Yes | Means and p only, no distribution or interval | High value |
| 8 | Sensitivity to parameters | Nothing (my check was a scratch script) | **No** | A labelled neighbourhood report | High value |
| 9 | Regimes and tickers | Tickers: SPY/QQQ (trades), +IWM (studies). Regimes: none | **No** for regimes | A registered split/filter with a nested comparison | **Critical** |
| 10 | Realistic costs | 2 bp ETF; perps modelled | Yes for SPY/QQQ | Leveraged ETFs not priced; no cost-sensitivity line | High value |
| 11 | Out-of-sample / walk-forward | 1993-2009 once (reused for selection); no forward column | Partly | Development window open-ended; forward trades mixed in | **Critical** |
| 12 | Repeated testing and selection bias | BH within a run; trial record counts every run | Partly | No cumulative family across runs, versions and the research app's 33 tests | Optional |
| 13 | Decide on forward testing | Idea ledger stage "forward"; research app stance | Yes (by hand) | No forward band set in advance | **Critical** |
| 14 | Monitor real-time behaviour | Research app: stance log, paper book, pre-close check | Partly | Stance scored over 5 sessions, not the rule's exit; pre-close never recorded; no deterioration status | **Critical** |
| 15 | Reassess | Weekly run (refresh only) | **No** | No scheduled review, no verdict-change report | **Critical** |

## 6.2 The procedure

### Before any number is seen (steps 1-6)
1. **Journal the observation** on the Daily thesis ("Journal": the note saves what the page showed). Say what you saw,
   on which day, and why you think it matters.
2. **Create an idea** in the Idea ledger: title, claim (a sentence that can be wrong), how to test it, route.
3. **Write the rule** precisely: instrument; the condition and its parameters; the decision time (close, 3:50 PM
   estimate, next open); entry price; exit rule; holding cap; costs; side.
4. **State the expected outcome:** sign, rough size per trade, horizon, and what result would make you drop it. Write
   it into the idea's "how to test it" until the ledger has fields for it.
5. **Pick the benchmark:** for an entry rule, every same-length trade (the v2 baseline); for a filter, the unfiltered
   rule; for an overlay, holding the index at the same average exposure.
6. **Check availability:** every input must be known before the decision time. The VIX close, GEX/DIX and FRED
   series are published after 4 PM; a rule that uses them can only be traded at the next open (or later). Macro values
   need first-release vintages (ALFRED), not today's revised numbers.
7. **Register** in the backtester (`catalog.py` or `strategies.py`, `-m backtester.lock --add`), commit, then set the
   idea to "registered" with the commit hash.

### First look (step 7)
8. Run the registered studies or trade simulation. Read the six dimensions in [05 section 5.4](05_interpretation_guide.md).
9. If nothing is there on SPY and QQQ at any horizon, drop it now and say so in the ledger. That is a useful result.

### Robustness (steps 8-10)
10. **Neighbourhood:** run the pre-declared neighbours (for example the threshold +/- one step, the band width +/- 0.5,
    the exit average 3/5/10), development period only, labelled exploratory. Accept smooth behaviour; distrust a
    single good setting surrounded by poor ones. Never promote a neighbour to the rule without a new version.
11. **Regimes and instruments:** run the registered split (for example trend x VIX, the research app's buckets) and
    the same rule on the other index. A rule that works in one cell only is a filter hypothesis, to be registered and
    tested as such.
12. **Costs:** read the result at 2, 5, 10 and 20 bp round trip, and in the instrument you would trade (TQQQ or UPRO
    if that is the plan).
13. **Risk shape:** MAE distribution and the worst trade at the intended leverage. Decide whether you could hold
    through the worst historical path. If not, the rule is not for that instrument.

### Independent evidence (steps 11-12)
14. **1993-2009:** read once from the ledger. If the rule was chosen after seeing it, it can only remove the rule.
15. **Forward:** from the registration date on, every signal is logged before entry (the research app's stance log and
    paper book already do this for the oversold rules), and the backtester reports post-registration trades in a
    separate column, never mixed into "development".
16. **Selection:** write next to the result how many related ideas were tried (trial record runs, ledger ideas,
    research-app tests), and whether this rule was chosen from a larger set.

### Forward decision and monitoring (steps 13-15)
17. **Forward band, set before the first forward trade.** From the development trades: mean excess m and per-trade
    standard deviation s. After n forward trades with mean excess f:
    - *Consistent* while f >= m - 2 s / sqrt(n);
    - *Deteriorating* when f < m - 2 s / sqrt(n);
    - *Failed* when the forward 90% interval lies entirely below zero.
    Implementation check, every trade: the paper trade must equal the backtest trade for the same day (the research
    app's paper book already rebuilds the backtester's trades to within 0.005 bp).
18. **Monitor** in the research app: the stance, the paper ticket, the paper book, the pre-close log. Score each
    forward trade by the rule's own exit, not only by a fixed 5 sessions.
19. **Reassess** quarterly and after any verdict change: re-read the registry entry, the forward band, the regime the
    market is in, and whether the mechanism still makes sense. A changed rule is a new version with a new band.

## 6.3 What forward testing can and cannot do here

[Verified, development statistics] How many forward trades it would take to tell each Lead's development edge from
zero (one-sided 5% test, 80% power, if the true edge equals the development mean):

| Rule | Trades a year | Mean excess / sd per trade | Trades needed | Years at the historical rate |
|---|---|---|---|---|
| QQQ Bollinger, next open | 6.2 | +60 bp / 256 bp | about 114 | about 19 |
| QQQ RSI(14) < 30, next open | 1.5 | +268 bp / 330 bp | about 9 | about 6 |
| QQQ RSI(2) < 10, close entry | 11.4 | +34 bp / 211 bp | about 241 | about 21 |

So forward testing will not *confirm* the Bollinger or RSI(2) rules within a trading career, and RSI(14) needs years.
Its realistic jobs are: catching implementation errors at once (paper vs backtest), detecting large failures (the band
above), and building the user's own record of acting on the evidence. Decisions in the meantime rest on the
historical evidence and its stated uncertainty. This argues for modest size and against leverage, not for waiting.

## 6.4 Critical missing functionality versus optional

**Critical (the process cannot be completed without these):**
1. Frozen development window per verdict version, and a separate forward column in reports and the export.
2. A verdict-change list in every run's record, export and the weekly log.
3. A registered split / filter capability with a nested comparison (rule vs rule + filter), for regimes, gap size,
   events and context data.
4. Forward bands stored with each rule and a forward status (consistent, deteriorating, failed) in the export.
5. Intra-trade risk: MAE and worst trade per strategy; leveraged-ETF pricing before any leveraged use.

**High value:**
6. Confidence intervals for every excess.
7. Neighbourhood (sensitivity) report, labelled exploratory, development only.
8. Cost-sensitivity line (2/5/10/20 bp) per strategy.
9. Exit decided on information available before it: a next-open variant of `close_above_sma5`, or a 3:50 PM estimate.
10. A volatility-matched baseline, registered as a new benchmark version.

**Optional:**
11. A combined count of all ideas tried across both apps.
12. Walk-forward re-estimation (low value while rules have no fitted parameters).
13. A query form for one-off descriptive studies.
