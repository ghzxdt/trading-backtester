# 3. Feature-by-feature operating manuals

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Deliverable 4.

The backtester has no tabs. Its window is one row of seven buttons over a log pane; its real "tabs" are the two
reports those buttons produce, the trade list, the export that appears inside the research app, and four
command-line or scheduled functions. Each gets the same treatment below: functionality, strategic use, operating
instructions, a short guide and an importance rank (1 = most important to the research process).

| Rank | Feature | Where |
|---|---|---|
| 1 | Trade-simulation report | "Run trade simulation" button, `reports/*-trade-simulation.html` |
| 2 | Backtester evidence inside the research app | Daily thesis tab: registered signals, paper ticket, paper book, pre-close check, stance |
| 3 | Indicator-studies report | "Run indicator studies" button, `reports/*-indicator-studies.html` |
| 4 | Registering a study or version | `backtester/catalog.py`, `strategies.py`, `-m backtester.lock --add` |
| 5 | Trade list | "Open trade list" button, `exports/trades/*.csv` |
| 6 | Weekly scheduled run | Task "Trading Backtester Weekly Run", `run_weekly.ps1` |
| 7 | Partial runs | Command line `--symbols --horizons --draws --seed` |
| 8 | Run tests | "Run tests" button |
| 9 | Report archive | "Open latest report", "Open reports folder" |
| 10 | Status line | Top of the window |
| 11 | Open research app | Button |

---

## 3.1 Trade-simulation report (rank 1)

### Functionality
- **Accomplishes:** turns the three oversold signals into actual trades with two registered exits on SPY and QQQ and
  judges each strategy and entry price with Lead v2. The only place in either app where a rule's trades, costs,
  equity curve and benchmark meet.
- **Inputs:** the snapshot of the research app's daily files; `config.json` costs and periods; the registered rules.
  No user settings.
- **Outputs:** verdict grid (12 strategies x 4 pricings); development test table (excess, p, q, holdout excess and
  p, v1 verdict); return per unit of drawdown table; full buy-and-hold reference; one detail block per strategy with
  development and 1993-2009 rows; the export and trade list.
- **Calculations:** see [02 section 2.9](02_application_breakdown.md).
- **Questions it answers:** Did buying after this oversold reading beat buying at random for the same length? Does it
  survive costs? Is the bounce partly overnight (close vs next open)? How much time in the market, how deep the equity
  drawdown, how concentrated the profit? Did it also hold in 1993-2009?

### Strategic application
- **Discovering edges:** it does not discover; it validates the three registered signals. New edges reach it only
  through registration (3.4).
- **Investigating an observation** ("QQQ always bounces after a flush"): find the closest registered strategy, read
  its development and 1993-2009 rows, then look at the trade list for the trades that resemble the observation.
- **Confirming or challenging a thesis:** a bullish bounce thesis on QQQ after a deep sell-off is supported by a Lead
  at the entry you can still use (next open). It is challenged when the relevant row is "No edge" at that entry, when
  excess is small against its spread, or when the per-strategy block shows the gains come from a few trades.
- **Most important information, in order:** (1) verdict at the entry you can actually take; (2) excess over
  same-length trades and its p and q; (3) number of trades and quarters; (4) share of profit from the best 5 trades;
  (5) 1993-2009 excess and p; (6) CAGR versus risk-matched buy-and-hold; (7) maximum drawdown.
- **Easily misread:**
  - "Lead" in the `etf_close` or perp columns: those entries are not available from the evening page (close) or not
    verified at all (perps).
  - Win rate: QQQ RSI(14)'s 100% (close entry) and 92% (next open) hide how deep trades went first: with the
    next-open entry, two of the 26 were more than 10% down at their worst.
  - "CAGR vs risk-matched buy-and-hold": for the Leads the benchmark holds a constant 4-23% of the index (4% for QQQ
    RSI(14), 14% for QQQ Bollinger), so beating it is easy for any rule with an edge; it is not a claim that the rule
    beats owning QQQ. The "return per unit of volatility" row (0.66 against 0.92 for QQQ RSI(14)) answers that
    question, and the answer is no as a standalone strategy.
  - The 1993-2009 row: it can remove a Lead, it cannot confirm one (the signals were chosen on it).
  - A SPY "No edge" next to a QQQ "Lead" for the same rule is mostly threshold noise between two very similar
    instruments.
- **Most useful configuration:** the registered one; there are no settings. Read the `ETF next open` column first.
- **Valuable when:** a registered oversold signal has fired or is close to firing (the research app shows the
  trigger levels), and before changing how a Lead is acted on.
- **Unreliable or irrelevant when:** the setup differs from the rule (an intraday flush that recovers by the close,
  a single-stock shock, an instrument other than SPY or QQQ), or the position will be leveraged.

### Operating instructions
1. Start at **Verdicts**, row of the ETF and rule that fired, column **ETF next open**.
2. Go to **Development test behind each verdict**: note excess, p, q and trades. Treat q within a factor of two of
   0.10 as borderline.
3. Open the strategy's detail block: check trades, quarters, best-5 share, average loss, maximum drawdown.
4. Compare with the same rule's `ETF at close` column: the difference is roughly the overnight part of the bounce.
5. Open the trade list (3.5) and look at the worst trades and the trades from similar markets.
- **Prioritise:** excess with its p and q; trades; best-5 share; drawdown.
- **Warrants more investigation:** a Lead whose best-5 share is above about 50%; a verdict that changed since last
  week; a large gap between close and next-open results; an open setup during an event or earnings window.
- **Justifies rejecting** (for that entry and exit): "No edge" at the entry you can take; or a Lead whose excess is
  not clearly above its spread once the best trades are removed; or forward trades that fall below a band registered
  in advance (see [06](06_validation_framework.md)).
- **Complementary research-app features:** Registered signals and "what would change the call" levels, pre-close check,
  paper book, regime card, events and earnings, expressions and risk by leverage.
- **Next:** record the conclusion in the research app's idea ledger (stage and evidence reference); if a new question
  arose (gap size, regime, leveraged ETF), write it as an idea, not as an edit to an existing rule.

**Guide:** read next-open verdict, then excess/p/q/trades, then the best-5 share and worst trades; never act on a
close or perp column from the evening page; never infer leverage safety. **Importance: 1.**

---

## 3.2 Backtester evidence inside the research app (rank 2)

### Functionality
- **Accomplishes:** the research app's Daily thesis recomputes the three rules on its own data, checks every fired
  date against the export (807 dates matched in the 2026-11-17 build), and uses the export's verdicts for its stance
  ("long" only when a rule fired whose next-open pricing is a Lead), the paper ticket, the paper book, the pre-close
  check and "what would change the call" levels.
- **Inputs:** `exports/trade_simulation.json` (age caution after 10 days, unused after 45).
- **Outputs:** stance (long, flat or no call); evidence rows per rule; trigger closes for the next session; paper
  trades from logged stances to the rule's own exit; pre-close comparison (none recorded yet).
- **Questions:** Did a Lead rule fire at today's close? What close tomorrow would make one fire? What do the paper
  trades say against the backtest?

### Strategic application
- The only place the backtester's evidence becomes a daily decision, so it is where misreading costs most.
- **Confirming a thesis:** "Long" means exactly one thing: a QQQ (today) next-open Lead fired. It does not mean the
  regime, news or events agree. Read the cautions beside it.
- **Easily misread:** "Flat" with the status "close-only setup" (as on the 2026-11-17 close, when QQQ RSI(2) < 10
  fired) means the evidence exists only for the closing price that has passed, not that the rule failed.
- **Valuable:** every evening after the refresh. **Unreliable:** when the export is older than 10 days, when the
  cross-check says mismatch, or right after a weekly run changed a verdict (nothing tells you; see 3.6).

### Operating instructions
1. Read the headline and the evidence status (usable, age, checked through).
2. Read "Registered signals at the latest close": which rule fired, its value, the trigger close for tomorrow.
3. For a long: open the paper ticket; note the registered exit and the 5-day-average level to watch.
4. For a near-trigger: write the trigger levels down for the 3:50 PM check next day.
- **Reject** acting when the evidence status is not "ok", or a cross-check mismatch is shown.
- **Next:** record your call (with what would invalidate it) in "Your calls"; the stance is logged automatically.

**Guide:** stance first, status second, trigger levels third, paper ticket for the exit. **Importance: 2.**

---

## 3.3 Indicator-studies report (rank 3)

### Functionality
- **Accomplishes:** screens the 10 registered daily rules on SPY, QQQ and IWM at 1, 5 and 10 sessions against all days
  in the period, with a correction for 90 tests and the one-look 1993-2009 holdout.
- **Inputs:** snapshot; registered studies. **Outputs:** one table per study (signals, non-overlapping count,
  excess, hit rate against all days, p, q, holdout signals, excess, p, next-open excess, verdict) and a tally.
- **Questions:** After condition X at the close, did the index do better than usual over the next 1, 5 or 10
  sessions? Was it real in 1993-2009 too? Is the bounce mostly from the close or still there from the next open?

### Strategic application
- **Discovering edges:** the closest the backtester gets to discovery, in a controlled way: each new daily price
  condition can be registered as a study and screened against the whole family.
- **Investigating an observation:** "after a big down-volume day the market bounces" is `volume_spike_down_day`:
  the report says No evidence on all nine tests.
- **Challenging a thesis:** it is the record of what did not work (EMA touches, MACD, breakouts, 200-day state,
  volume spikes). Before building a thesis on one of those, read its row.
- **Most important:** excess with q; holdout direction; next-open excess (the executable version); signal counts.
- **Easily misread:** the hit rate (a 5-day hit rate of 84% vs 61% sounds decisive on 58 overlapping signals); the
  signals column (overlapping windows; the trades number in brackets is the honest count); the holdout "agreeing"
  (the holdout is a filter, and IWM has none); excess is before costs and against an all-days mean, not a trade.
- **Valuable:** for deciding whether a price-pattern idea is worth a trade simulation. **Unreliable:** for rare
  signals (p about 1.5x lenient in my calibration), and as anything more than a screen.

### Operating instructions
1. Find the study that matches your idea; if none matches, register one (3.4) before looking at any number.
2. Read the development excess and q at each horizon; check the next-open column for the executable version.
3. Read the holdout columns: same sign and p < 0.10 needed.
4. If a Candidate: it is a lead for a trade simulation, not a trade. If No evidence across symbols and horizons:
   record the idea as dropped in the research app's idea ledger.
- **Reject** an idea when it shows No evidence on SPY and QQQ at every horizon, or when the holdout has the opposite
  sign.
- **Next:** for a Candidate, write the trade rule (entry, exit, pricing) and register it in `strategies.py` before
  running the simulation.

**Guide:** match idea to row; excess with q; holdout sign; next-open excess; Candidate means "simulate", not
"trade". **Importance: 3.**

---

## 3.4 Registering a study or a new version (rank 4)

### Functionality
- **Accomplishes:** the only way a new hypothesis enters the backtester. A `Study` (or an `Exit`, or a verdict
  version) is added with version v1 at the end of `catalog.py` or `strategies.py`, then
  `..\trading-research\.venv\Scripts\python.exe -B -m backtester.lock --add` fingerprints it in `rule_lock.json`.
  A changed rule must become v2; the lock refuses an edit.
- **Inputs:** a written rule (a function of the daily OHLCV and VIX frame). **Outputs:** a new fingerprint; from the
  next registered run, the rule is in the family, gets its one holdout look, and appears in reports and the record.
- **Questions:** none by itself; it fixes the question before the answer is seen.

### Strategic application
- This is the backtester's main defence against fitting to history. Use it for every idea from the research app.
- **Easily misread:** registering after running a partial run on the same rule defeats the purpose; the record would
  not show it. Adding a study also changes the family size, so every q in the next run moves slightly.
- **Valuable:** always. **Unreliable:** only if bypassed.

### Operating instructions
1. Write the idea in the research app's idea ledger first (title, claim, how to test it, route).
2. Write the rule in code with a description that a reader could re-implement; commit it.
3. Run `-m backtester.lock --add`, commit `rule_lock.json` with the rule ("Register ... before running").
4. Run the studies (and later the trade simulation) with the registered settings.
5. Update the idea ledger with the result and the report name.

**Guide:** idea ledger, code, lock, commit, run, record. Never edit a run rule. **Importance: 4.**

---

## 3.5 Trade list (rank 5)

### Functionality
- **Accomplishes:** every simulated trade of the latest run (9,600 rows: 12 strategies x 4 pricings x 2 periods),
  with signal day, entry and exit day and price (adjusted), sessions held, gross, cost and net.
- **Questions:** Which trades made the result? What happened in 2020, 2022, April 2025? How long are trades held?
  What did trades look like when the market looked like today?

### Strategic application
- The tool for checking concentration, regime clustering and analogues by hand until the backtester reports them.
- **Easily misread:** prices are adjusted (they differ from the prices printed on the day); the same trades appear
  four times (one per pricing); development and holdout are mixed (filter `period`).
- **Valuable:** before trusting a Lead; when the current market resembles a past episode.

### Operating instructions
1. Filter `symbol`, `signal`, `exit`, `pricing = etf_next_open`, `period = development`.
2. Sort by `net`: read the five best and five worst trades and their dates.
3. Group by year (a pivot) to see whether one episode carries the result.
4. For the current setup, find trades from similar markets (for example the same month after a large drop) and read
   them as anecdotes, not as a sample.
- **Warrants more work:** one year or one episode supplying most of the profit; a worst trade much larger than the
  average loss.

**Guide:** filter to the strategy and entry you would trade, sort by net, pivot by year. **Importance: 5.**

---

## 3.6 Weekly scheduled run (rank 6)

### Functionality
- **Accomplishes:** every Saturday 10:00 AM (or the next sign-in), `run_weekly.ps1` runs the trade simulation with the
  registered settings, commits only the files a run writes and pushes. Keeps the export inside the research app's
  10-day caution window. Log: `work\weekly_run.log`.

### Strategic application
- Freshness, not new evidence. Each run re-estimates the open-ended development window, so verdicts can change
  without anyone being told (see [01 section 1.6](01_technical_accuracy_audit.md)).
- **Unreliable** as a monitoring tool until verdict changes are reported and forward trades are kept apart.

### Operating instructions
1. Monday: open `work\weekly_run.log`; check "Committed and pushed" and the list of Leads.
2. Compare the Lead list with last week's (by eye today; the log prints Leads only).
3. If a Lead appeared or disappeared, read the report before the next evening's stance.

**Guide:** check the log weekly; treat a changed Lead list as an event to read, not as news. **Importance: 6.**

---

## 3.7 Partial runs from the command line (rank 7)

### Functionality
- `run_studies.py --symbols DIA RSP --horizons 3` and similar; `run_trades.py --draws 500 --seed 1`. Partial runs
  report numbers but give no verdicts and never look at 1993-2009; they are recorded in `trials.jsonl` as "partial".
- **Questions:** How does a registered rule behave on another of the nine ETFs or at another horizon?

### Strategic application
- Useful for descriptive questions on the other ETFs (DIA, RSP) and the 3x funds (TQQQ, UPRO), which the registered
  family excludes. Still recorded, so a later registration can be checked against it.
- **Easily misread:** a partial run's p-values are uncorrected; "no verdict" is not "no evidence".
- **Not for:** trying variants of a rule until one looks good. That is what registration prevents.

**Guide:** use for description on other ETFs; anything that might drive a decision gets registered.
**Importance: 7.**

---

## 3.8 Run tests (rank 8)

- Runs the 36 tests (about 20 seconds). They check that indicators are causal, statistics find planted effects and
  ignore noise, trade mechanics, costs, the record chain, snapshots, the ledger and the lock.
- **When:** after any code change and before any run you intend to rely on. A failure means do not run.
- **Guide:** green before every recorded run. **Importance: 8.**

## 3.9 Report archive: "Open latest report" and "Open reports folder" (rank 9)

- Opens the most recently written report (by file time, either kind) or the folder of all reports (Markdown and
  HTML, named by UTC date and time).
- **Use:** to compare this week with earlier weeks, by eye. There is no diff tool. The trial record holds every
  number for a scripted comparison.
- **Guide:** keep the latest trade-simulation report open while reading the Daily thesis. **Importance: 9.**

## 3.10 Status line (rank 10)

- Shows the research data's latest date (last line of `etfs.csv`), the number of recorded runs (not ideas) and the
  latest report name.
- **Use:** a quick check that the data is current before a run. A data date older than the last session means the
  research app has not refreshed; run nothing until it has.
- **Importance: 10.**

## 3.11 Open research app (rank 11)

- Starts the research app's control panel (`desktop_app.pyw`) with that app's Python. Convenience only.
- **Importance: 11.**
