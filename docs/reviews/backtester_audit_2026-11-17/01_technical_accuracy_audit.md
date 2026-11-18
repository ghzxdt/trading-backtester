# 1. Technical accuracy audit

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). Deliverable 2: findings that affect
whether the backtester's historical results can be trusted, and the independent checks behind them.

Scope: code at commit 407cd65 (unchanged in 28ce2c8, which only added run results), the recorded runs in
`trials.jsonl`, the kept snapshot `snapshots/c4713b15d633ad4c` (research-app data through 2026-11-13), and the
research app's consumption of the export. Every check ran from a scratch copy or a separate read-only script; nothing
in either app was changed. Methods, parameters and the scripts are in [A_verification_log.md](A_verification_log.md).

Labels used throughout: **[Verified]** checked by running code or recomputing it independently on 2026-11-18;
**[Verified historical finding]** a result about past prices that I reproduced; **[Reasonable hypothesis]**;
**[Unvalidated assumption]**; **[Missing data]**; **[Technical limitation]**; **[Recommendation]**.

---

## 1.1 Bottom line

- **The engine computes what it says it computes.** [Verified] All 36 unit tests pass. Both latest recorded runs
  (studies and trade simulation, 2026-11-18 00:26-00:27 UTC) rebuild from their snapshot and the holdout ledger with
  zero differing values. My own code, written without importing the backtester, reproduces every SPY and QQQ study
  number exactly and every development trade (same signal day, exit day and return) for all 24 ETF strategy-pricings.
- **No critical correctness blocker was found in the calculations.** The two most important qualifications are about
  use, not arithmetic: (1) the evidence covers 1x SPY/QQQ only and the reports hide intra-trade losses that reached
  -11.7% to -22.9% at 1x, so nothing here supports leveraged use yet; (2) the development window is open-ended, so
  each weekly run folds post-registration trades into "development" and can flip a verdict that the research app
  turns into a stance, without anyone being told.
- **Statistical tests are roughly calibrated, slightly lenient for rare signals.** [Verified on synthetic data] On
  500 made-up zero-edge price histories with clustered volatility, the study test passed RSI(14) < 30 at a nominal
  5% level 7-8% of the time and Lead v2's test passed it 9% of the time. Frequent signals stayed near 5-7%.
- **Results are as reliable as they are narrow.** Two QQQ rules carry all next-open Leads, they share most of their
  signal days, the RSI(14) one rests on 26 trades, and the 1993-2009 period helped choose them.

| Area | Verdict | Why |
|---|---|---|
| Signal causality, look-ahead in indicators | Trust | Tested by truncation in the suite; reproduced independently |
| Entry at the signal close (`etf_close`, perp modes) | Caution | Needs a pre-close decision on an unfinished bar; flip rate unmeasured |
| Entry at the next open (`etf_next_open`) | Trust | Realistic for a market-on-open order; 2 bp round trip is adequate for SPY/QQQ |
| Exit `close_above_sma5` at the exit-signal close | Caution (minor) | Same-bar decision; moving it to the next open changes means by -7 to +7 bp |
| Exit `hold_5` | Trust | Time-based; no decision on the exit bar |
| Adjusted prices, dividends, splits | Trust | OHLC adjusted consistently; total-return basis |
| Survivorship | Trust | Index ETFs; no constituent selection |
| Cost model, ETFs | Trust | Leads survive 20 bp round trips |
| Cost and price model, Kalshi perps | Disregard for decisions | ETF price as proxy, funding from 33 records, 4:05 PM entry never verified |
| Study p-values (circular shift) | Trust with caution | Near nominal; 1.5x lenient for rare signals under clustered volatility |
| Lead v2 p-values (quarter resampling) | Trust with caution | Near nominal for frequent signals; about 1.8x lenient at ~25 trades |
| Multiple-testing correction | Trust within a run | Covers the run's family only, not the history of choices |
| 1993-2009 holdout | Caution | One look is enforced, but the signals were chosen partly on it |
| Development window | Caution, needs a fix | Open-ended; absorbs forward trades; verdicts can drift weekly |
| Tail risk and drawdown reporting | Incomplete | No MAE, no worst-trade, no per-trade distribution in reports |
| Leveraged ETF results | Not available | Never simulated |
| Regime dependence | Unknown | Not testable in the current code (VIX is loaded but unused) |

---

## 1.2 Reproducibility and record-keeping

**[Verified] Unit tests.** `python -B -m unittest discover -s tests` in a scratch copy of the tracked files: 36 tests,
OK, 22 s. The suite covers indicator causality (values up to day t unchanged when later days are added), definitions,
forward-return alignment, a planted-effect and a noise test for both statistics, the BH correction, verdict labels,
trade mechanics, costs and funding, benchmarks, snapshot integrity, the hash chains, the one-look holdout, per-test
random streams and the rule lock.

**[Verified] Exact rebuild.** `rebuild_check.py` (appendix) re-ran the 2026-11-18 study run (90 tests) and trade run
(48 results) from `snapshots/c4713b15d633ad4c` with a copy of `holdout_ledger.jsonl`, then compared verdicts, q, p,
excess, CAGR, risk-matched CAGR, trade counts and the v1 percentile with `trials.jsonl`: 0 differences. The
provenance design (snapshot, ledger, lock, per-test seeds, record written before report) works as documented.

**[Verified] Data drift between downloads.** Between the 2026-11-14 snapshot (`4e1f98996cd13f8f`) and the
2026-11-17 one (`c4713b15d633ad4c`), both ending on 2026-11-13, Yahoo's re-download changed 9,812 of 15,472
long-history rows and 20,019 of 38,133 recent rows, every one by at most 1.6 parts per million (a re-computed
adjustment factor). Every verdict was identical, but that noise was enough to flip two knife-edge "close above the
5-day average" comparisons: one QQQ RSI(2) trade now exits on 2013-12-16 instead of 12-17 and one SPY 1993 trade on
07-26 instead of 07-23. QQQ RSI(2)'s development p moved from 0.0084 to 0.0081 and its next-open q from 0.111 to
0.110. (The stored 1993-2009 statistics stay those of the first look, by design, so the trade list's holdout rows and
the ledger now differ by that one SPY trade.) [Recommendation] Compare prices rounded to the cent in both apps, so
vendor noise cannot move a signal or an exit; otherwise a re-adjustment could also flip a fired date and make the
research app's date cross-check report a mismatch. The fingerprint changes on almost every run, creating a new
2.3 MB snapshot; storage is not a concern at one run a week (about 120 MB a year).

**[Verified] Record counts.** `trials.jsonl`: 11 runs, 780 test rows (6 study runs x 90, 5 trade runs x 48). Distinct
hypotheses behind them: 90 study tests and 24 strategy-entry tests (48 pricings). `holdout_ledger.jsonl`: two
entries, 60 study results and 48 trade results, first computed 2026-11-14. Before the ledger existed the 1993-2009
period was evaluated in six recorded runs of unchanged rules (repeats, so no extra information leaked; noted in
`backtester/ledger.py`).

**Gaps.**
- [Technical limitation] A run with a dirty tree records `+dirty` but not the diff, so a dirty-tree result cannot be
  rebuilt exactly. The first recorded run (2026-11-08 06:14 UTC) says `uncommitted`.
- [Technical limitation] Nothing compares a run's verdicts with the previous run's. A verdict that changes is
  committed silently by `run_weekly.ps1` and read by the research app the same evening (see 1.6).
- [Recommendation] Keep a `verdict_changes` list in each trade-run record and export, and print it in the weekly log.

## 1.3 Data integrity

[Verified] on snapshot `c4713b15d633ad4c` with `data_check.py`:

| Check | Result |
|---|---|
| Coverage | SPY 1993-01-29 to 2026-11-13 (8,507 sessions); QQQ 1999-03-10 to 2026-11-13 (6,965); DIA, IWM, RSP, SPY, QQQ, UPRO, SPXU 2010-01-04 on (4,243); TQQQ, SQQQ 2010-02-11 on (4,216); VIX 1990-01-02 on |
| Duplicate dates, unordered dates | None |
| OHLC consistency (high >= max(open, close), low <= min(open, close)) | 0 violations in any symbol |
| Adjustment basis | Open, high, low and close share one adjustment factor (SPY's first open is 24.07, against about $44 as traded in 1993), so next-open entries and overnight gaps are not distorted |
| Gaps over 4 calendar days | Only real closures (September 2001, Hurricane Sandy 2012, and a holiday combination) |
| Sessions per year | No thin years |
| `etfs.csv` vs `etfs_long.csv` (SPY, QQQ, 4,243 common days) | Returns agree within 1.8e-6; identical open/close ratios |
| Zero-volume days | SQQQ has 29 (not used by the backtester) |

- [Verified] **Dividends and splits** are in the prices (Yahoo adjusted), so returns are total returns. Trade-list
  prices are adjusted, not the prices printed on the day; `run_trades.trade_list` says so.
- [Unvalidated assumption] **Vendor accuracy.** Prices come from Yahoo only. The research app cross-checks SPY and
  QQQ daily returns against FRED's S&P 500 and Nasdaq-100 over the latest 60 sessions; there is no independent check
  of opens, of IWM, or of the 1993-2009 history.
- [Verified] **Stale inputs, not partial bars.** The 2026-11-17 18:26 CT runs used data through 2026-11-13: the
  laptop was shut down from the evening of 15 November to the afternoon of 17 November and the research app's evening
  refresh ran only later that evening. The status line shows the data date; check it before a run. (The research
  app's log says it drops a session whose close is missing, so a partial day should not be saved; not tested here.)
- **Historical revisions.** Price data is not revised in substance; adjustment factors are recomputed (above). The
  macro series the research app holds (NFCI, payrolls, CPI) are revised and would need vintages (ALFRED) before any
  backtest uses them; credit spreads, VIX and Treasury yields are market data and are not revised.

## 1.4 Look-ahead, signal availability and execution timing

**Indicators.** [Verified] Every indicator uses data up to and including its own bar (`tests/test_backtester.py`
truncation test, and my independent implementation). One definitional difference:

- [Verified] The backtester's RSI is a pandas exponential average seeded with the first change, not Wilder's
  classic seed (the mean of the first n changes). The two agree to within 0.005 points after five months of history.
  They disagree only at the start of a series: IWM's history starts on 2010-01-04, so 7 of its RSI(14) < 30 days in
  January-February 2010 differ and its study excess differs by up to 15 bp. SPY and QQQ are unaffected (history from
  1993 and 1999). A charting package that uses Wilder's seed will show slightly different RSI values for IWM in early
  2010 only. The research app uses the identical code, so the two apps agree with each other.

**Entries.**
- `etf_close`: buys at the close of the signal day, which is only known at that close. The export says so ("Needs
  the order in before the close, on an estimate of that close's signal"), and the research app's stance rules v2
  refuse to call a close-only Lead a setup. [Missing data] How often a rule that looks fired at 3:50 PM ET is still
  fired at 4:00 PM (the flip rate) has never been measured: the pre-close check exists in the research app but has
  recorded nothing, because no daytime job has yet run on this laptop.
- `etf_next_open`: buys at the next session's opening price, after the signal is known. Realistic for a market-on-open
  order in SPY or QQQ.
- `perp_maker`, `perp_taker`: enter "about 4:05 PM" at the ETF's 4:00 PM adjusted close. [Unvalidated assumption]
  No perp price was ever compared with the ETF close at 4:05 PM; the backtester's own LOG lists this as not verified.

**Exits.**
- `hold_5` exits at the close five sessions after the signal: a time exit, so a market-on-close order works.
- `close_above_sma5` decides at a close ("is this close above the 5-day average?") and sells at that same close.
  [Verified] I re-priced every development trade with the exit moved to the next morning's open (a decision made only
  after the close is known). Mean per trade changed by -6.8 to +7.1 bp across the 12 strategy-pricings; for the Leads:
  QQQ Bollinger +0.0 / +0.2 bp, QQQ RSI(14) -6.6 / -6.8 bp, QQQ RSI(2) +2.7 / +2.9 bp. QQQ RSI(14)'s 100% win rate
  (close entry) becomes 96% and the next-open 92% becomes 85%. Verdict-relevant? No. Worth modelling honestly? Yes,
  because the user executes this exit by hand: a pre-close estimate at 3:50 PM, or the next open, are the two real
  options, and the research app's paper book assumes the same-close exit.

**Intraday ambiguity.** Daily bars cannot say whether a day's high came before its low, so the simulator has no stops
(stated in every report). This is honest, but it means intra-trade risk is invisible (section 1.8).

**Time zones and sessions.** Daily bars are dated by exchange date; no time-zone handling is needed for daily
studies. Early-close days are treated as full sessions; holidays shorten nothing because horizons count sessions.
[Technical limitation] The research app's hourly bars and live quotes are *as traded* (not adjusted) while daily bars
are adjusted. On a quarterly ex-dividend day the live price drops by the dividend (about 0.25-0.3% for SPY, less for
QQQ) relative to an adjusted history downloaded the night before; the pre-close check could see a slightly deeper
drop than the adjusted series will record. Not measured; four days a year per ETF.

## 1.5 Survivorship, data leakage, corporate actions

- [Verified] **Survivorship bias**: not material. SPY, QQQ and IWM are funds whose index membership is decided in real
  time; no stock universe is selected with hindsight. The choice of QQQ as the instrument is the user's, not a
  result of searching instruments for the best backtest.
- **Leakage across periods**: the 1993-2009 holdout is read once per rule version (enforced by the ledger), but it
  is not independent evidence for the trade simulator, because the three signals were chosen on 2026-11-08 partly
  because they passed it in the indicator studies. The backtester states this in every report. Treat 1993-2009 as a
  filter that can remove a rule, not one that confirms it.
- **Leakage across apps**: the research app recomputes the rules on its own copy of the same Yahoo files and checks
  every fired date against the export (807 dates matched in the 2026-11-17 build). A definition change in one app
  shows up as a mismatch and blocks the stance. Good.
- Corporate actions: handled by adjusted prices (QQQ's 2000 split, dividends).

## 1.6 Overfitting, data snooping and repeated testing

What the code enforces well:
- Rules are fingerprinted (`rule_lock.json`, 13 entries); an edited rule stops every run.
- Each test has its own random stream, so a p-value does not depend on what else ran.
- BH correction over the registered family (90 study tests; 24 strategy-entry tests).
- Partial runs (other symbols, horizons, seed or draws) get no verdict and no holdout look.
- Every run is appended to a hash-chained record, failures included.

What it does not cover:
- **The history of choices.** The family correction covers one run. It does not cover the choices made between
  runs: the three signals were picked from 90 studies, two exits were picked before the simulator existed, and the
  v2 verdict was designed after seeing development-period diagnostics for these 12 strategies (documented in
  `lead_v2.py`). The trade simulation's q-values are therefore conditional on a selection that already favoured
  these rules. [Reasonable hypothesis] The real false-discovery rate for the Leads is higher than q suggests,
  by an amount that cannot be computed from the record.
- **The research app's own tests.** The research app keeps a separate registry of 33 "luck tests" (10 rated edge,
  6 hint, 17 none in the 2026-11-17 build), plus its frozen four-rule paper experiment and an intraday trial
  registry. These are not counted in the backtester's family. A shared count would show the true number of ideas tried.
- **Development window (important).** `config.json` sets the development period to start 2010-01-01 with no end, so
  every run re-estimates "development" on all data to date. Trades after the registration date (2026-11-08 for the
  rules, 2026-11-13 for v2) are the only untouched evidence, yet each weekly run mixes them into the development
  statistics and can flip a verdict across a hard threshold. Example of how close that is today: QQQ RSI(2) < 10
  with the 5-day-average exit, next-open entry, has q = 0.110 against a 0.10 threshold. One good bounce could make it
  a Lead; the research app would then log "long" whenever QQQ's RSI(2) fires (32 times in the last year, against 2
  for RSI(14)), with no human decision and no record that the evidence changed. [Recommendation, critical for forward validation] Freeze each verdict version's development end at its
  registration date; report post-registration trades as a separate forward column; report verdict changes.

**Parameter sensitivity.** [Verified, development period only; 1993-2009 not looked at] A neighbourhood of
unregistered variants around the Leads (appendix, `sensitivity.py`):

| Variant (QQQ, next-open entry, 5-day-average exit unless stated) | Trades | Mean per trade | Excess over same-length trades | Rough t |
|---|---|---|---|---|
| RSI(14) < 25 / 27.5 / **30** / 32.5 / 35 | 6 / 11 / **26** / 44 / 64 | +537 / +496 / **+284** / +171 / +97 bp | +521 / +481 / **+268** / +152 / +76 bp | 2.4 / 3.9 / **4.1** / 2.8 / 2.1 |
| Bollinger (20, 1.5) / **(20, 2)** / (20, 2.5) / (15, 2) / (30, 2) | 156 / **104** / 39 / 110 / 81 | +62 / **+81** / +156 / +91 / +86 bp | +40 / **+60** / +138 / +70 / +64 bp | 2.1 / **2.4** / 3.9 / 3.9 / 1.8 |
| RSI(2) < 5 / **10** / 15 / 20 (close entry) | 104 / **192** / 271 / 330 | +90 / **+61** / +59 / +50 bp | +65 / **+34** / +33 / +24 bp | 3.0 / **2.2** / 2.5 / 2.0 |
| Bollinger (20, 2), exit first close above SMA3 / **SMA5** / SMA10 | 114 / **104** / 90 | +75 / **+81** / +103 bp | +62 / **+60** / +65 bp | 3.6 / **2.4** / 1.9 |
| Bollinger (20, 2), exit after 1 / 3 / 5 / 10 sessions | 149 / 112 / 97 / 80 | +8 / +12 / +58 / +124 bp | +5 / -5 / +26 / +55 bp | 0.4 / -0.2 / 0.7 / 1.2 |
| Same Bollinger rule on SPY / RSI(14) < 30 on SPY | 99 / 24 | +50 / +79 bp | +33 / +63 bp | 1.1 / 0.6 |

What this says:
- The registered parameters are not a knife edge: deeper oversold readings give larger and rarer bounces, a smooth
  dose-response, which is what a real effect would look like.
- The exit carries much of the result. The same Bollinger entries held for a fixed 1-5 sessions show little or no
  excess; exiting at the first close above a short average shows +60 bp. That is consistent with a fast bounce that
  fades, but it also means the evidence is about one exit family, and the choice of that family was made before the
  simulator existed, not tuned.
- The QQQ-only Leads should not be read as "works on QQQ, not on SPY". The same rules on SPY point the same way with
  weaker statistics and a deeper worst case. With two instruments this correlated, a threshold landing on one side for
  QQQ and the other for SPY is weak evidence of a real difference.
- These variants are unregistered. They must not be used to pick a new parameter.

## 1.7 Statistical method calibration

[Verified on synthetic data] `calibration.py` (appendix) ran the backtester's own test functions, unchanged, on 500
made-up 17-year price histories with **no edge** (constant expected return), with the real rules as signals:

| Rule | Study test, h=1 | Study test, h=5 | Lead v2 test (5-day-average exit) |
|---|---|---|---|
| Constant volatility: RSI(2) < 10 | 5.0% | 5.0% | 4.8% |
| Constant volatility: RSI(14) < 30 | 3.2% | 5.6% | 6.2% |
| Constant volatility: Bollinger | 4.6% | 3.8% | 7.0% |
| Clustered volatility (GARCH): RSI(2) < 10 | 6.0% | 4.4% | 5.2% |
| Clustered volatility (GARCH): RSI(14) < 30 | **8.2%** | **7.4%** | **9.0%** |
| Clustered volatility (GARCH): Bollinger | 7.2% | 6.8% | 6.4% |

Share of zero-edge histories passing at the nominal 5% level (study test two-sided p < 0.05; v2 one-sided p < 0.05
with positive excess). Monte Carlo error is about +/-1 point.

- Both tests behave well for frequent signals. For rare signals in volatile stretches both are lenient by roughly
  1.5-1.8x: the circular shift moves the signal pattern into mostly calm days, and quarter resampling with about 20
  quarters is rough (the module says so).
- Effect on today's verdicts: none of the Leads sits near the edge on this account. QQQ RSI(14) has development
  p = 0.0001 (the floor for 10,000 resamples: no resample was at or below zero); QQQ Bollinger next-open p = 0.011.
  The borderline case is QQQ RSI(2) next-open (p = 0.041, q = 0.110), already a "No edge". The 1993-2009 p-values
  behind the Leads run from 0.0006 to 0.073 against a 0.10 threshold; the 0.073 one (QQQ RSI(14), hold 5 sessions,
  close entry) would not survive a 1.8x correction. The two next-open Leads (0.0006 and 0.035) would.
- Effect on the indicator studies: the "Candidate" layer is somewhat more generous than labelled for RSI(14), so
  candidates should be treated as leads only, which is how the app describes them.
- [Technical limitation] The study report gives no confidence interval for any excess; the trade report gives none
  either. A p-value alone does not say how large the effect plausibly is.
- [Technical limitation] Real markets cluster more than this GARCH (2008, 2020), so the real leniency could be larger.

## 1.8 Costs, liquidity, tail risk and benchmarks

**Costs.** [Verified] ETF round trip 2 bp. For SPY and QQQ a 1-cent spread is well under 1 bp at current prices and
commissions are zero, so 2 bp is reasonable for market-on-open and market-on-close orders at retail size. The Leads
are not cost-sensitive:

| QQQ rule (development, 5-day-average exit) | Net mean per trade at 2 / 5 / 10 / 20 bp round trip | Same-length baseline |
|---|---|---|
| Bollinger, next open (104 trades) | +78.9 / +75.9 / +70.8 / +60.7 bp | +21.3 bp |
| RSI(14) < 30, next open (26) | +281.5 / +278.4 / +273.2 / +263.0 bp | +15.6 bp |
| RSI(2) < 10, close (192) | +59.0 / +55.9 / +50.9 / +40.8 bp | +27.1 bp |

[Unvalidated assumption] Kalshi perp costs (4 / 24 bp round trip plus 1.37 bp a day of funding) rest on a fee page
read on 2026-11-07 and 33 daily funding records; weekend funding, the perp's own price at 4:05 PM and its spread at
that time are not verified. The research app's user decision of 2026-11-08 keeps perps out of the thesis, so the perp
columns should be read as information only.

**Liquidity.** At retail size SPY and QQQ have no meaningful capacity limit. TQQQ, SQQQ, UPRO and SPXU have wider
spreads and no simulated history in the backtester.

**Tail risk.** [Verified] Maximum adverse excursion per trade, from daily lows and highs (development, 1x; appendix
`excursions.py`):

| Rule | Trades | Median MAE | 10th percentile MAE | Worst MAE | Trades worse than -5% / -10% | Worst closed trade |
|---|---|---|---|---|---|---|
| QQQ Bollinger, next open | 104 | -1.43% | -5.50% | -19.73% | 13 / 4 | -15.06% |
| QQQ RSI(14) < 30, next open | 26 | -1.46% | -4.03% | -11.65% | 2 / 2 | -1.61% |
| QQQ RSI(2) < 10, close | 192 | -1.18% | -5.16% | -20.86% | 20 / 5 | -11.75% |
| SPY Bollinger, next open | 99 | -1.13% | -4.86% | -22.87% | 10 / 2 | -21.21% |

- The QQQ RSI(14) rule's trades all closed between -1.6% and large gains, but at their worst point two of them were
  down more than 10%. The reports show win rate, average win and loss and maximum drawdown of the equity curve, which
  hide this.
- [Reasonable hypothesis] In a 3x daily-reset ETF these paths would have meant losses of roughly a third to over half
  of the position before any recovery, before the extra decay of a volatile path. Nothing in either app has tested
  that. [Critical for leveraged use] Do not size a leveraged position on these Leads until MAE and leveraged-ETF
  pricing are in the backtester.

**Benchmarks.** The reports compare with four baselines: all days in the period (studies); every same-length trade
(v2); buy-and-hold scaled to time in market (v1); buy-and-hold scaled to time in market x in-trade volatility (v2).
These are sound for "is this better than random timing". Missing:
- A volatility-matched baseline (same-VIX days). Oversold signals fire when volatility is high, when expected returns
  are also thought to be higher. Without it, "excess" cannot separate a timing skill from a reward for bearing
  volatility. [Recommendation] Register it as a v3 benchmark before looking.
- A cash yield. Cash earns 0% in the simulator. Each next-open Lead adds roughly 4% a year of excess (QQQ Bollinger
  6.2 trades a year x 0.60%; RSI(14) 1.5 x 2.68%), so in years when bills pay 4-5%, interest on the idle 90-98% of the
  money is as large as the rule's own contribution. Ignoring it understates a low-exposure rule against buy-and-hold.
- An overlay view. [Verified, development only] Holding QQQ 1x and adding 1x more during each RSI(14) trade gave a
  Sharpe ratio (cash at 0) of 0.99 against 0.92 for QQQ held at the same average exposure, with a smaller maximum
  drawdown (-32.6% vs -35.6%). The same overlay on the Bollinger rule added return (CAGR +22.9% vs +19.9%) but not
  return per unit of risk (Sharpe 0.90 vs 0.92; drawdown -42.5% vs -37.8%). This matches the 2026-11-07 quant
  review's advice to treat the oversold rules as an exposure overlay, and it is the honest frame for the user's
  question "does this improve what I already hold?".

## 1.9 Sample size, regime dependency and time stability

- [Verified historical finding] QQQ RSI(14) < 30 next-open: 26 development trades over 14 calendar years. Removing the
  best 3 trades lowers the mean from +2.84% to +1.80%. QQQ Bollinger next-open: 104 trades; without the best 3,
  +0.81% becomes +0.65%; median +1.15%; the worst year (2020: 3 trades, mean -4.86%) is one crash.
- [Verified historical finding] No single year dominates: the best three years supply 41% (Bollinger) and 46%
  (RSI(14)) of summed gross return.
- [Verified historical finding] Overlap: 90% of QQQ RSI(14) < 30 days are also below the lower Bollinger band or have
  RSI(2) < 10, and 77% are Bollinger days. The two next-open Leads are largely one bet on deep oversold readings.
- [Missing data] Regime dependence is untested. The backtester loads the VIX but no study or strategy uses it, and
  no trend or volatility split exists. I deliberately did not compute regime splits for these rules: the research
  app's idea ledger plans a registered trend-and-volatility test (idea 8), and looking first would spoil it.

## 1.10 What to trust, treat cautiously, or disregard

**Trust (as computed):**
- The indicator-study table for SPY and QQQ, as a description of 2010-2026 history.
- The trade lists and the next-open pricing of each trade.
- "No evidence" for the trend, momentum and volume studies (EMA touches, MACD, 20-day breakout, 200-day state,
  volume spikes): none of 63 tests passed, with no positive 1993-2009 result except one near miss (SPY volume-spike
  down day, next session from the close: +23.5 bp, p 0.054; almost nothing from the next open).
- The provenance: any recorded number can be rebuilt.

**Treat with caution:**
- Every Lead. Provisional by the app's own definition; small samples; chosen partly on the holdout; one exit family;
  one instrument family.
- The SPY-versus-QQQ split in verdicts.
- Any Lead or Candidate whose q or p is within a factor of two of its threshold.
- Close-entry evidence until the pre-close flip rate is measured.
- Weekly-refreshed verdicts as "forward" evidence until the development window is frozen.

**Disregard until corrected or tested:**
- The perp columns, for any decision.
- Any extrapolation of these results to TQQQ, UPRO, SQQQ, SPXU, NVDL, TSLL or other leveraged products.
- Any reading of win rate as risk (MAE shows the risk).
- IWM, which has no trade simulation and no holdout.
