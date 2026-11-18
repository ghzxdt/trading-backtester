# 5. Backtest interpretation guide

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Brief section 7; deliverable 6.

## 5.1 Which metrics exist, and what each is good for

| Metric | In the backtester? | Use | Misleading when |
|---|---|---|---|
| Trade count / sample size | Yes (trades, non-overlapping count, quarters) | The first number to read; sets how much anything else can mean | Overlapping windows inflate "signals" (studies) |
| Win rate | Yes (after costs) | Describes the payoff shape | Read alone: a rule that wins small and loses big can win 90% and lose money; it says nothing about risk |
| Average and median return | Average yes; median **no** | Average is what compounds; the median shows whether a few trades carry it | Average alone with skewed trades (best-5 share above 50%) |
| Average win / average loss | Yes | Payoff ratio | Ignores frequency and path |
| Expectancy | Yes, as mean net per trade | Per-trade edge after costs | Without the baseline it includes plain market drift |
| Excess over a baseline | Yes (all days; same-length trades) | The real "edge" measure | Baseline choice matters: unconditional baselines do not remove a volatility premium |
| Profit factor | **No** | Gross wins over gross losses | Unstable with few losses (QQQ RSI(14) close entry has none) |
| Maximum drawdown | Yes (equity, strategy and benchmarks) | Pain of the equity curve | For a rule in the market 2% of the time it measures one or two trades |
| Risk-adjusted return | Partly (CAGR per drawdown; return per volatility, cash at 0) | Compares with holding the index | No cash yield; per-drawdown ratios are dominated by one episode |
| Maximum adverse excursion (MAE) | **No** | How far a trade goes against you before the exit | n/a: missing. [01 section 1.8](01_technical_accuracy_audit.md) shows it is large |
| Maximum favourable excursion (MFE) | **No** | Whether exits leave money behind | n/a |
| Holding period | Yes (mean sessions) | Exposure and overnight count | Mean hides the 10-session cap trades, which are the losers |
| Return distribution, tail risk | **No** (trade list allows it by hand) | Shape, fat tails, worst cases | n/a |
| Exposure-adjusted performance | Yes (time in market, risk-matched benchmark) | Separates timing from exposure | The risk-matched benchmark is small; beating it is a low bar |
| Performance by regime | **No** | When the rule works | n/a |
| Performance by ticker | Yes (SPY, QQQ) | Robustness across instruments | Two highly correlated instruments; a split verdict is weak evidence |
| Performance over time | **No** (trade list by hand) | Stability, decay | n/a |
| Confidence intervals | **No** (p and q only) | How big the effect plausibly is | A p-value is not an effect size |
| Out-of-sample results | 1993-2009 (reused for selection); no forward column | The strongest evidence | A reused period passing is not confirmation |

## 5.2 Concentration: is it a few trades, a few periods, one ticker, or one setting?

Run these four checks on any result before believing it. Current numbers for the two next-open Leads (development):

| Check | How | QQQ Bollinger (104 trades) | QQQ RSI(14) < 30 (26 trades) |
|---|---|---|---|
| A few trades? | Best-5 share (report); mean without the best 3; median vs mean | Best-5 share 32%; +0.81% falls to +0.65% without the best 3; median +1.15% | Best-5 share 55%; +2.84% falls to +1.80%; median +1.72% |
| A few periods? | Trade list pivoted by year; share from the best three years | Best three years 41% of summed gross; 2020 (3 trades) -4.9% mean | Best three years 46%; 26 trades spread over 14 years |
| One ticker? | Same rule on SPY | SPY: same direction, t about 1.1 | SPY: same direction, t about 0.6 |
| Narrow settings? | Neighbouring parameters ([01 section 1.6](01_technical_accuracy_audit.md)) | Smooth across band widths and lengths; exit family matters a lot | Smooth dose-response across thresholds |
| Worst case | MAE from the daily lows | -19.7% intra-trade; -15.1% closed | -11.7% intra-trade; -1.6% closed |

Reading: the Bollinger result is broad but modest and carries one crash-sized loss; the RSI(14) result is large but
rests on few trades, half of whose profit comes from five of them.

## 5.3 Six levels of evidence

| Level | What it means | What must be true | Backtester label today |
|---|---|---|---|
| 1. Promising observation | Something looked different after a condition | An excess in one period, any p | (nothing; partial runs) |
| 2. Statistically supported relationship | Unlikely to be luck within its test family | Registered; development p and q pass; sign holds out of sample | Study "Candidate"; trade "Failed holdout" means level 2 in development only |
| 3. Economically meaningful after costs | Big enough to trade | Excess clearly above realistic costs and spread at the executable entry; survives removing the best trades | Trade-simulation excess at `etf_next_open` |
| 4. Robust strategy | Not an artefact of one setting, period or instrument | Neighbouring settings agree; years agree; similar instruments agree; worst case known and tolerable at the intended size | Not reported (needs sensitivity, by-year, MAE) |
| 5. Ready for forward testing | Worth a forward record | Levels 2-4, a written exit and invalidation, a forward band set before the first trade | "Lead" is the app's nearest label; it skips most of level 4 |
| 6. Rejected | Not worth attention | Fails level 2 or 3 on a registered test, or forward trades fall below their band | "No edge", "No evidence", "Failed holdout" (for that rule version) |

Where the QQQ Leads stand: level 3 reached for the next-open entry; level 4 partly (parameter neighbourhood and years
look fine; instrument agreement weak; worst case known only from my check and large); level 5 reached informally
(stance and paper book log forward), without a pre-registered forward band.

## 5.4 An acceptance framework without arbitrary thresholds

The app's verdicts use fixed cut-offs (p < 0.05, q < 0.10, holdout p < 0.10). They are useful as a common language, but
evidence is continuous, and a rule at q = 0.098 is not different from one at q = 0.110. Read every result along six
dimensions and write a one-line judgement for each:

1. **Size with uncertainty.** The excess and a 90% interval (by quarter-cluster resampling, which the code already
   does for p). Accept when the interval's lower end is above the realistic cost at the size traded; doubt when it
   straddles zero; reject when the upper end is below the cost.
2. **Breadth.** Trades and distinct episodes (quarters). Fewer than about 10 episodes: anecdote. Ten to thirty:
   suggestive. Thirty and up: a pattern.
3. **Consistency.** Same sign across sub-periods (for example 2010-14, 2015-19, 2020-22, 2023 on, which the
   research app already uses), across SPY and QQQ, and across neighbouring parameters. A result that needs one
   period, one ticker or one setting is fragile.
4. **Mechanism.** A plausible reason that predicts the shape of the result (deeper oversold, bigger bounce; bounce
   fades after a few days). A result with no mechanism, or with a shape the mechanism does not predict, needs more
   evidence, not less.
5. **Risk shape.** MAE distribution and worst trade at the intended instrument and leverage. A positive mean with a
   worst case that would end the account is not acceptable at that leverage, whatever the p-value.
6. **Independence of the evidence.** Was the period used to choose the rule? How many related ideas were tried
   (the trial record count, plus the research app's)? Forward evidence counts more than reused history.

Decide with all six in view:
- **Act (forward-test at small size):** 1 above costs, 2 at least suggestive, 3 consistent, 4 present, 5 tolerable
  at the intended size, 6 honest about selection.
- **Watch only:** any one of 1-3 doubtful, or 5 unknown.
- **Reject for now:** 1 below costs or the sign flips across periods or instruments; record why, so it is not
  re-tested casually.

This is a judgement with stated reasons, not a score, and the reasons go into the registry entry
([08](08_integration_and_registry.md)).

## 5.5 Common misreadings in this app's reports

- "Lead" means provisional by the app's own definition. It is a reason to watch a rule forward, not proof.
- A Lead in the `ETF at close` column cannot be used from the evening page. Only `ETF next open` can, or the
  pre-close route at 3:50 PM.
- Perp columns are the ETF priced with perp costs. They say nothing about a perp's own prices.
- 100% win rate (QQQ RSI(14), close entry): 26 trades, two of which were more than 10% down at some point.
- "CAGR above risk-matched buy-and-hold" is a low bar for a rule in the market 2-9% of the time; "return per unit of
  volatility" against the index is the question "is it better than owning QQQ", and the answer is no as a
  standalone strategy. As an overlay on a held position, RSI(14) improved return per unit of risk in 2010-2026 and
  Bollinger did not ([01 section 1.8](01_technical_accuracy_audit.md)).
- The 1993-2009 column passing does not confirm a rule chosen partly because it passed 1993-2009.
- Hit rate "84% vs 61%" in the study report counts overlapping 5-day windows.
- A verdict that changes between weekly runs: the development window grew; check whether the change is from new
  trades, and treat any change near a threshold as noise until the window is frozen.
- IWM rows: no trade simulation and no holdout; every IWM verdict is No evidence or Development only by construction.
