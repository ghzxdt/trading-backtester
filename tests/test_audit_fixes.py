"""Fixes from the 2026-11-17 audit: risk inside trades, intervals, Lead v3's fixed window and forward record, verdict
changes, context files, filter tests, leveraged pricing, evidence cards and their registration."""
import gzip, hashlib, json, sys, tempfile, unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_splits, run_trades  # noqa: E402
from backtester import data, evidence, lead_v2, lead_v3, lock, registry, simulate, splits, study  # noqa: E402

CFG = {"research_app": "unused", "development": {"start": "2010-01-01", "end": None},
       "holdout": {"start": "1993-01-01", "end": "2009-12-31"},
       "costs_round_trip_bps": {"etf": 2, "kalshi_taker": 24, "kalshi_maker": 4}, "funding_bps_per_day": 1.37,
       "verdict_cost": "etf"}


def stormy_returns(days, seed):
    """Calm stretches at 0.8% a day and stormy ones at 2%, so oversold rules fire and VIX-like levels vary."""
    rng = np.random.default_rng(seed)
    vol = np.full(len(days), 0.008)
    start = 0
    while start < len(days):
        start += int(rng.integers(120, 300))
        vol[start:start + 50] = 0.02
    return rng.normal(0.0004, vol)


def make_app(folder: Path, symbols=("SPY", "QQQ", "IWM"), last="2012-12-31", context=True, seed=4) -> Path:
    """A stand-in research app. Prices are drawn through 2013 and cut at `last`, so two apps that end on different days
    share every price up to the earlier end."""
    every = pd.bdate_range("2004-01-02", "2013-12-31")
    days = every[every <= pd.Timestamp(last)]
    tables = []
    for k, symbol in enumerate(symbols):
        close = (100 * np.cumprod(1 + stormy_returns(every, seed + k)))[:len(days)]
        opens = (np.r_[100, close[:-1]] * (1 + np.random.default_rng(seed + 50 + k).normal(0, 0.002, len(every))[:len(days)]))
        tables.append(pd.DataFrame({"date": days, "ticker": symbol, "open": opens, "high": np.maximum(opens, close) * 1.006,
                                    "low": np.minimum(opens, close) * 0.994, "close": close, "volume": 1e6}))
    raw = folder / "data" / "raw"
    raw.mkdir(parents=True)
    pd.concat(tables).to_csv(raw / "etfs_long.csv", index=False)
    if context:
        spy = tables[0].set_index("date")["close"]
        vix = (spy.pct_change().rolling(21).std() * np.sqrt(252) * 100).bfill()
        for name, series in (("VIX.csv", vix), ("VIX3M.csv", vix.rolling(63, min_periods=1).mean())):
            pd.DataFrame({"DATE": series.index.strftime("%m/%d/%Y"), "OPEN": series, "HIGH": series, "LOW": series,
                          "CLOSE": series}).to_csv(raw / name, index=False)
        (folder / "data" / "events").mkdir(parents=True)
        pd.DataFrame({"date": days[days >= "2010-01-08"][::12].strftime("%Y-%m-%d"), "event": "cpi", "time_et": "08:30",
                      "note": "made up", "scheduled": "true"}).to_csv(folder / "data" / "events" / "events.csv", index=False)
    return folder


def sandbox(stack: ExitStack, tmp: Path, *modules) -> Path:
    """Point the runners at a temporary folder so main() writes nothing real."""
    app = make_app(tmp / "research")
    for module in modules:
        for name, value in (("REPORTS", tmp / "reports"), ("TRIALS", tmp / "trials.jsonl"), ("EXPORTS", tmp / "exports"),
                            ("LEDGER", tmp / "holdout_ledger.jsonl"), ("HERE", tmp)):
            if hasattr(module, name):
                stack.enter_context(mock.patch.object(module, name, value))
    stack.enter_context(mock.patch.object(data, "SNAPSHOTS", tmp / "snapshots"))
    stack.enter_context(mock.patch.object(data, "config", lambda: {**CFG, "research_app": str(app)}))
    stack.enter_context(mock.patch("builtins.print"))
    return app


def frame_from(close, opens=None, spread=0.01):
    close = np.asarray(close, float)
    opens = np.r_[close[0], close[:-1]] if opens is None else np.asarray(opens, float)
    return pd.DataFrame({"open": opens, "high": np.maximum(opens, close) * (1 + spread),
                         "low": np.minimum(opens, close) * (1 - spread), "close": close},
                        index=pd.bdate_range("2015-01-05", periods=len(close)))


class RiskInsideTradesTests(unittest.TestCase):
    def test_excursions_on_a_known_path(self):
        f = pd.DataFrame({"open": [100, 101, 99, 97, 104, 106.0], "high": [101, 102, 100, 99, 106, 107.0],
                          "low": [99, 98, 95, 94, 103, 105.0], "close": [100, 100, 96, 98, 105, 106.0]},
                         index=pd.bdate_range("2020-01-06", periods=6))
        nxt = simulate.price_trades(f, [(1, 4)], "etf_next_open", CFG).iloc[0]
        self.assertAlmostEqual(nxt["entry_price"], 99)        # the open after the signal day
        self.assertAlmostEqual(nxt["mae"], 94 / 99 - 1)       # lows from the entry day to the exit day
        self.assertAlmostEqual(nxt["mfe"], 106 / 99 - 1)
        self.assertAlmostEqual(nxt["exit_next_open"], 106)    # the open after the exit day
        close = simulate.price_trades(f, [(1, 4)], "etf_close", CFG).iloc[0]
        self.assertAlmostEqual(close["mae"], 94 / 100 - 1)    # from the day after the signal close
        last = simulate.price_trades(f, [(1, 5)], "etf_close", CFG).iloc[0]
        self.assertTrue(np.isnan(last["exit_next_open"]))     # no session after the data's end

    def test_risk_profile(self):
        priced = pd.DataFrame({"signal_day": pd.to_datetime(["2019-03-01", "2019-06-03", "2020-01-02", "2020-05-04", "2021-02-01"]),
                               "entry_price": 100.0, "gross": [0.0302, -0.0098, 0.0202, 0.0502, -0.0398],
                               "net": [0.03, -0.01, 0.02, 0.05, -0.04], "mae": [-0.01, -0.03, -0.02, -0.12, -0.06],
                               "mfe": [0.04, 0.01, 0.03, 0.06, 0.0], "exit_next_open": [104, 99, 102, 105, 96.0]})
        r = simulate.risk_profile(priced)
        self.assertAlmostEqual(r["profit_factor"], 0.10 / 0.05)
        self.assertAlmostEqual(r["mean_net_without_best3"], (-0.01 - 0.04) / 2)
        self.assertEqual((r["trades_mae_below_5pct"], r["trades_mae_below_10pct"]), (2, 1))
        self.assertAlmostEqual(r["mae_worst"], -0.12)
        self.assertEqual(r["by_year"]["2020"][0], 2)
        costs = [r["mean_net_at_cost_bp"][c] for c in ("2", "5", "10", "20")]
        self.assertEqual(costs, sorted(costs, reverse=True))
        self.assertAlmostEqual(r["mean_gross_exit_next_open"], np.mean([0.04, -0.01, 0.02, 0.05, -0.04]))
        self.assertIsNone(simulate.risk_profile(priced.assign(net=[0.01] * 5))["profit_factor"])  # no losses


class IntervalTests(unittest.TestCase):
    def test_v2_interval_comes_from_the_same_draws_as_p(self):
        days = pd.to_datetime(pd.date_range("2011-01-03", periods=60, freq="21D"))
        priced = pd.DataFrame({"signal_day": days, "gross": np.random.default_rng(3).normal(0.004, 0.02, 60)})
        base = np.full(60, 0.001)
        out = lead_v2.excess_test(priced, base, np.random.default_rng(9), 4000)
        excess = priced["gross"].to_numpy() - base
        _, which = np.unique(pd.PeriodIndex(days, freq="Q").asi8, return_inverse=True)
        count = which.max() + 1
        draw = np.random.default_rng(9).integers(0, count, size=(4000, count))
        means = np.bincount(which, weights=excess, minlength=count)[draw].sum(1) / np.bincount(which, minlength=count)[draw].sum(1)
        self.assertAlmostEqual(out["p"], (np.sum(means <= 0) + 1) / 4001)  # p as before the interval was added
        self.assertAlmostEqual(out["ci90"][0], np.percentile(means, 5))
        self.assertLess(out["ci90"][0], out["mean_excess"])
        self.assertGreater(out["ci90"][1], out["mean_excess"])

    def test_study_interval(self):
        days = pd.bdate_range("2010-01-04", periods=1500)
        fwd = pd.Series(np.random.default_rng(1).normal(0.0005, 0.01, len(days)), index=days)
        signal = pd.Series(False, index=days)
        signal.iloc[::25] = True
        mask = pd.Series(True, index=days)
        lo, hi = study.excess_interval(signal, fwd, mask, np.random.default_rng(2))
        excess = study.evaluate(signal, fwd, mask, 1, 0)["excess"]
        self.assertLess(lo, excess)
        self.assertGreater(hi, excess)
        few = pd.Series(False, index=days)
        few.iloc[:5] = True
        self.assertIsNone(study.excess_interval(few, fwd, mask, np.random.default_rng(2)))


class LeadV3Tests(unittest.TestCase):
    def test_forward_status(self):
        m, s = 0.006, 0.025
        self.assertEqual(lead_v3.forward_status(0, None, m, s)[0], "none yet")
        self.assertEqual(lead_v3.forward_status(3, -0.05, m, s)[0], "too few")
        self.assertEqual(lead_v3.forward_status(10, 0.004, m, s)[0], "consistent")
        status, band = lead_v3.forward_status(10, -0.012, m, s)
        self.assertEqual(status, "below band")
        self.assertAlmostEqual(band, m - 2 * s / np.sqrt(10))
        self.assertEqual(lead_v3.forward_status(10, -0.02, m, s)[0], "failed")

    def test_only_a_lead_is_demoted(self):
        good = {"trades": 60, "strategy": {"cagr": 0.05}, "risk_matched": {"cagr": 0.03},
                "v2": {"mean_excess": 0.004, "p": 0.01, "quarters": 12}}
        self.assertEqual(lead_v3.verdict(good, good, 0.05, {"status": "consistent"}), "Lead")
        self.assertEqual(lead_v3.verdict(good, good, 0.05, {"status": "too few"}), "Lead")
        self.assertEqual(lead_v3.verdict(good, good, 0.05, {"status": "below band"}), lead_v3.DEMOTED)
        self.assertEqual(lead_v3.verdict(good, good, 0.05, {"status": "failed"}), lead_v3.DEMOTED)
        weak = {**good, "v2": {"mean_excess": 0.004, "p": 0.2, "quarters": 12}}
        self.assertEqual(lead_v3.verdict(weak, good, 0.3, {"status": "failed"}), "No edge")

    def test_development_results_do_not_move_when_data_is_added(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(lead_v3, "DEV_END", "2011-12-30"):
            short = make_app(Path(tmp) / "short", symbols=("SPY", "QQQ"), last="2011-12-30", context=False)
            long_ = make_app(Path(tmp) / "long", symbols=("SPY", "QQQ"), last="2013-06-28", context=False)
            a, *_ = run_trades.run(50, 11, CFG, short)
            b, _, _, trades = run_trades.run(50, 11, CFG, long_)
        for x, y in zip(a, b):
            self.assertEqual((x["dev"]["trades"], x["dev"]["v2"]["p"], x["dev"]["v2"]["mean_excess"]),
                             (y["dev"]["trades"], y["dev"]["v2"]["p"], y["dev"]["v2"]["mean_excess"]))
            self.assertEqual(x["forward"]["trades"], 0)
        self.assertTrue(any(y["forward"]["trades"] > 0 for y in b))
        self.assertTrue(any(y["dev_to_date"]["trades"] > y["dev"]["trades"] for y in b))  # v2's window kept growing
        forward = trades[trades["period"] == "forward"]
        self.assertGreater(len(forward), 0)
        self.assertTrue((pd.to_datetime(forward["signal_day"]) > pd.Timestamp("2011-12-30")).all())

    def test_verdict_changes(self):
        previous = {"verdict_version": "v2", "tests": [{"symbol": "QQQ", "study": "a+b", "mode": "etf_close", "verdict": "Lead"},
                                                       {"symbol": "SPY", "study": "a+b", "mode": "etf_close", "verdict": "No edge"}]}
        rows = [{"symbol": "QQQ", "signal": "a", "exit": "b", "mode": "etf_close", "verdict": lead_v3.DEMOTED},
                {"symbol": "SPY", "signal": "a", "exit": "b", "mode": "etf_close", "verdict": "No edge"}]
        self.assertEqual(run_trades.verdict_changes(previous, rows),
                         [{"symbol": "QQQ", "strategy": "a+b", "mode": "etf_close", "from": "Lead", "to": lead_v3.DEMOTED}])
        self.assertIsNone(run_trades.verdict_changes(None, rows))
        self.assertIsNone(run_trades.verdict_changes(previous, [{**rows[0], "verdict": run_trades.PARTIAL}]))


class StudyWindowTests(unittest.TestCase):
    def test_study_results_do_not_move_when_data_is_added(self):
        import run_studies
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(lead_v3, "DEV_END", "2011-12-30"):
            short = make_app(Path(tmp) / "short", last="2011-12-30", context=False)
            long_ = make_app(Path(tmp) / "long", last="2012-06-29", context=False)
            a = run_studies.run(["SPY", "QQQ", "IWM"], [1, 5], 200, 7, CFG, short)
            b = run_studies.run(["SPY", "QQQ", "IWM"], [1, 5], 200, 7, CFG, long_)

        def key(r):
            return r["dev"].get("signals"), r["dev"].get("excess"), r["dev"].get("p"), r.get("dev_ci90")
        self.assertEqual([key(r) for r in a], [key(r) for r in b])  # the outcome of a late signal waits for the forward record
        self.assertTrue(all(r["forward"]["signals"] == 0 for r in a))
        self.assertTrue(any(r["forward"]["signals"] > 0 for r in b))


class ContextFileTests(unittest.TestCase):
    def test_old_fingerprints_and_context_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            bare = make_app(Path(tmp) / "bare", context=False)
            raw = (bare / "data" / "raw" / "etfs_long.csv").read_bytes()
            old_way = hashlib.sha256()
            old_way.update(b"etfs_long.csv" + hashlib.sha256(raw).digest())
            self.assertEqual(data.fingerprint(bare), old_way.hexdigest()[:16])  # unchanged without context files
            full = make_app(Path(tmp) / "full")
            folder, mark = data.snapshot(full, Path(tmp) / "snapshots")
            self.assertTrue((folder / "data" / "raw" / "VIX3M.csv.gz").exists())
            self.assertTrue((folder / "data" / "events" / "events.csv.gz").exists())
            self.assertEqual(data.fingerprint(folder), mark)
            ctx = data.load_context(folder)
            self.assertGreater(len(ctx["vix3m"]), 1000)
            self.assertTrue(ctx["events"]["scheduled"].all())
            self.assertEqual(data.load_context(bare)["vix3m"].size, 0)


class SplitTests(unittest.TestCase):
    def context(self, frame):
        return {"vix": (frame["close"].pct_change().rolling(21).std() * np.sqrt(252) * 100),
                "vix3m": frame["close"].pct_change().rolling(63).std() * np.sqrt(252) * 100,
                "spy_close": frame["close"],
                "events": pd.DataFrame({"date": frame.index[3::9], "event": "cpi", "scheduled": True})}

    def test_conditions_use_only_what_is_known_at_the_decision(self):
        days = pd.bdate_range("2012-01-02", periods=700)
        close = 100 * np.cumprod(1 + stormy_returns(days, 8))
        full = frame_from(close)
        cut = full.iloc[:500]
        for split in splits.SPLITS:
            a = split.value(full, self.context(full))
            ctx = self.context(cut)
            ctx["events"] = self.context(full)["events"]  # scheduled dates are known ahead
            b = split.value(cut, ctx)
            keep = 499 if split.name == "gap_at_next_open" else 500  # the gap needs the next open
            if split.name == "release_within_5_sessions":
                keep = 495  # needs the next five sessions of the calendar, all scheduled in advance
            pd.testing.assert_series_equal(a.iloc[:keep], b.iloc[:keep], check_names=False, obj=split.name)

    def test_a_planted_difference_is_found_and_noise_is_not(self):
        rng = np.random.default_rng(5)
        n = 160
        days = pd.to_datetime(pd.date_range("2010-02-01", periods=n, freq="16D"))
        group = rng.random(n) < 0.4
        values = pd.Series(np.where(group, 1.0, 0.0))
        split = splits.Split("t", "v1", "test", lambda f, c: values, lambda v: v > 0.5, "g", "r")
        noise = rng.normal(0, 0.02, n)
        priced = pd.DataFrame({"signal_day": days, "position": np.arange(n), "excess": noise + np.where(group, 0.015, 0.0)})
        found = splits.contrast(priced, values, split, np.random.default_rng(1), 3000)
        self.assertLess(found["p"], 0.01)
        self.assertGreater(found["ci90"][0], 0)
        plain = splits.contrast(priced.assign(excess=noise), values, split, np.random.default_rng(1), 3000)
        self.assertGreater(plain["p"], 0.05)
        few = splits.contrast(priced.iloc[:10], values, split, np.random.default_rng(1), 300)
        self.assertEqual(few["status"], "too few")

    def test_volatility_matched_baseline_removes_a_pure_volatility_premium(self):
        days = pd.bdate_range("2010-01-04", periods=3000)
        rng = np.random.default_rng(11)
        stormy = np.zeros(len(days), bool)
        start = 0
        while start < len(days):
            start += int(rng.integers(100, 250))
            stormy[start:start + 60] = True
        r = np.where(stormy, rng.normal(0.006, 0.01, len(days)), rng.normal(0.0002, 0.007, len(days)))
        frame = frame_from(100 * np.cumprod(1 + r))
        vix = pd.Series(np.where(stormy, 35.0, 12.0), index=frame.index)
        signal = pd.Series(False, index=frame.index)
        signal.iloc[rng.choice(np.flatnonzero(stormy[:-20]), 150, replace=False)] = True
        mask = pd.Series(True, index=frame.index)
        trades = simulate.find_trades(frame, signal, lambda f, p: p + 3, mask)
        priced = simulate.price_trades(frame, trades, "etf_close", CFG)
        priced = priced.assign(position=[p for p, _ in trades],
                               excess=priced["gross"] - lead_v2.baseline(frame, mask, priced["sessions"].to_numpy(int), "etf_close"))
        out = splits.volatility_test(frame, mask, priced, "etf_close", vix, np.random.default_rng(3), 3000)
        self.assertGreater(out["v2_mean_excess"], 0.005)            # the usual baseline counts the premium as edge
        self.assertLess(abs(out["mean_excess"]), out["v2_mean_excess"] / 3)  # the matched baseline mostly removes it

    def test_labels(self):
        dev = {"status": "ok", "diff": 0.01, "p": 0.01, "ci90": [0.004, 0.016], "strategy_mean": 0.006}
        self.assertEqual(splits.contrast_label(dev, {"status": "ok", "diff": 0.008, "p": 0.04}, 0.05), "Supported difference")
        self.assertEqual(splits.contrast_label(dev, {"status": "ok", "diff": -0.008, "p": 0.04}, 0.05), "Not confirmed in 1993-2009")
        self.assertEqual(splits.contrast_label(dev, None, 0.05), "Development only (no 1993-2009 data)")
        self.assertEqual(splits.contrast_label(dev, None, 0.2), "Insufficient evidence")
        narrow = {**dev, "p": 0.6, "ci90": [-0.003, 0.004]}
        self.assertEqual(splits.contrast_label(narrow, None, 0.7), "No meaningful difference")
        self.assertEqual(splits.contrast_label({"status": "too few"}, None, None), "Too few trades")
        vol = {"status": "ok", "mean_excess": 0.005, "p": 0.01}
        self.assertEqual(splits.volatility_label(vol, {"status": "ok", "mean_excess": 0.003, "p": 0.02}, 0.03), "Edge beyond volatility")
        self.assertEqual(splits.volatility_label({**vol, "p": 0.3}, None, 0.4), "Not shown beyond volatility")


class LeveragedPricingTests(unittest.TestCase):
    def test_same_days_priced_in_the_leveraged_fund(self):
        r = np.random.default_rng(2).normal(0.0005, 0.01, 60)
        base = frame_from(100 * np.cumprod(1 + r))
        lev = frame_from(50 * np.cumprod(1 + 3 * r))
        out = run_trades.leveraged_pricing(base, lev, "TQQQ", [(10, 13)], "etf_next_open", CFG)
        entry, exit_ = lev["open"].iloc[11], lev["close"].iloc[13]
        self.assertEqual((out["instrument"], out["trades"]), ("TQQQ", 1))
        self.assertAlmostEqual(out["mean_gross"], exit_ / entry - 1)
        self.assertAlmostEqual(out["mae_worst"], lev["low"].iloc[11:14].min() / entry - 1)
        self.assertAlmostEqual(out["mean_net"], (exit_ / entry) * (1 - 2e-4) - 1)
        self.assertIsNone(run_trades.leveraged_pricing(base, None, "TQQQ", [(10, 13)], "etf_next_open", CFG))
        self.assertIsNone(run_trades.leveraged_pricing(base, lev, "TQQQ", [(10, 13)], "perp_taker", CFG))


class RegistrationTests(unittest.TestCase):
    def test_new_rules_are_fingerprinted(self):
        marks = lock.marks()
        for key in ["verdict:lead@v3", "filters:family@v1", "split:volatility_matched_baseline@v1",
                    *(f"split:{s.name}@{s.version}" for s in splits.SPLITS)]:
            self.assertIn(key, marks)
        changed = [splits.Split(s.name, s.version, s.description, s.value, (lambda v: v >= 25), s.group_label,
                                s.rest_label, s.buckets, s.entries, s.before_2010) if s.name == "vix_level" else s
                   for s in splits.SPLITS]
        with mock.patch.object(splits, "SPLITS", changed):
            self.assertNotEqual(lock.marks()["split:vix_level@v1"], marks["split:vix_level@v1"])
        with mock.patch.object(lead_v3, "DEV_END", "2026-12-31"), \
                mock.patch.object(lead_v3, "PARAMS", {**lead_v3.PARAMS, "development_end": "2026-12-31"}):
            self.assertNotEqual(lock.marks()["verdict:lead@v3"], marks["verdict:lead@v3"])


class RunnerTests(unittest.TestCase):
    def test_filter_tests_look_at_1993_2009_once_and_cards_are_written(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            tmp = Path(tmp)
            sandbox(stack, tmp, run_trades, run_splits)
            self.assertEqual(run_trades.main([]), 0)
            self.assertEqual(run_splits.main([]), 0)
            record = registry.read(tmp / "trials.jsonl")[-1]
            self.assertEqual((record["kind"], record["family"]), ("filter_tests", "registered"))
            by_test = {(t["study"], t["strategy"]): t for t in record["tests"]}
            for (name, _), t in by_test.items():
                before_2010 = name not in ("vix_term_structure", "release_within_5_sessions")
                self.assertEqual(t["holdout_source"] is not None, before_2010, name)
            self.assertNotIn(("gap_at_next_open", "QQQ:rsi2_below_10+close_above_sma5|etf_close"), by_test)  # next open only
            stored = len(registry.read(tmp / "holdout_ledger.jsonl"))
            self.assertEqual(run_splits.main([]), 0)                       # again: read from the ledger
            again = registry.read(tmp / "trials.jsonl")[-1]
            self.assertTrue(all(t["holdout_source"] is None or t["holdout_source"].startswith("ledger") for t in again["tests"]))
            self.assertEqual([t["holdout_p"] for t in again["tests"]], [t["holdout_p"] for t in record["tests"]])
            self.assertEqual(len(registry.read(tmp / "holdout_ledger.jsonl")), stored)
            self.assertEqual(run_splits.main(["--resamples", "200"]), 0)  # partial: no labels, nothing stored
            partial = registry.read(tmp / "trials.jsonl")[-1]
            self.assertEqual(partial["family"], "partial")
            self.assertTrue(all(t["verdict"] == run_trades.PARTIAL for t in partial["tests"]))
            self.assertEqual(len(registry.read(tmp / "holdout_ledger.jsonl")), stored)
            cards = json.loads((tmp / "exports" / "evidence.json").read_text(encoding="utf-8"))["cards"]
            self.assertEqual(len(cards), 24)
            card = next(c for c in cards if c["strategy"] == "QQQ:bollinger_lower_close+close_above_sma5|etf_next_open")
            self.assertEqual(len(card["filters"]), len(splits.SPLITS) + 1)
            for field in ("excess_ci90", "inside_trades", "forward", "occurrence", "limitations", "mean_net_at_cost_bp"):
                self.assertIn(field, card)
            export = json.loads((tmp / "exports" / "trade_simulation.json").read_text(encoding="utf-8"))
            self.assertIsNone(export["verdict_changes"])                   # the first registered run in the sandbox


if __name__ == "__main__":
    unittest.main()
