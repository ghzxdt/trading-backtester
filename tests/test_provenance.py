"""A recorded run can be rebuilt: its inputs are kept, its record comes first, its files are its own."""
import json, sys, tempfile, unittest
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_studies, run_trades  # noqa: E402
from backtester import catalog, data, lock, registry, runlog  # noqa: E402
from backtester.ledger import HoldoutLedger, rng_for  # noqa: E402

CFG = {"research_app": "unused", "development": {"start": "2010-01-01", "end": None},
       "holdout": {"start": "1993-01-01", "end": "2009-12-31"},
       "costs_round_trip_bps": {"etf": 2, "kalshi_taker": 24, "kalshi_maker": 4}, "funding_bps_per_day": 1.37,
       "verdict_cost": "etf"}


def research_app(folder: Path, symbols=("SPY",), last="2012-12-31") -> Path:
    """A stand-in research app with one long price file."""
    days = pd.bdate_range("2004-01-02", last)
    tables = []
    for k, symbol in enumerate(symbols):
        r = np.random.default_rng(4 + k).normal(0.0003, 0.012, len(days))
        close = 100 * np.cumprod(1 + r)
        tables.append(pd.DataFrame({"date": days, "ticker": symbol, "open": np.r_[100, close[:-1]],
                                    "high": close * 1.01, "low": close * 0.99, "close": close, "volume": 1e6}))
    raw = folder / "data" / "raw"
    raw.mkdir(parents=True)
    pd.concat(tables).to_csv(raw / "etfs_long.csv", index=False)
    return folder


def sandbox(stack: ExitStack, tmp: Path, module) -> Path:
    """Point one runner at a temporary folder so main() writes nothing real. Returns the stand-in research app."""
    app = research_app(tmp / "research", symbols=("SPY", "QQQ", "IWM"))
    for name, value in (("REPORTS", tmp / "reports"), ("TRIALS", tmp / "trials.jsonl"), ("EXPORTS", tmp / "exports"),
                        ("LEDGER", tmp / "holdout_ledger.jsonl"), ("HERE", tmp)):
        if hasattr(module, name):
            stack.enter_context(mock.patch.object(module, name, value))
    stack.enter_context(mock.patch.object(data, "SNAPSHOTS", tmp / "snapshots"))
    stack.enter_context(mock.patch.object(data, "config", lambda: {**CFG, "research_app": str(app)}))
    stack.enter_context(mock.patch("builtins.print"))
    return app


class SnapshotTests(unittest.TestCase):
    def test_snapshot_keeps_the_inputs_and_loads_the_same_prices(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = research_app(Path(tmp) / "research")
            folder, mark = data.snapshot(app, Path(tmp) / "snapshots")
            self.assertEqual(mark, data.fingerprint(app))
            self.assertEqual(mark, data.fingerprint(folder))
            self.assertEqual(folder.name, mark)
            pd.testing.assert_frame_equal(data.load("SPY", folder), data.load("SPY", app))
            (app / "data" / "raw" / "etfs_long.csv").write_text("date,ticker,open,high,low,close,volume\n")
            self.assertEqual(len(data.load("SPY", folder)), len(pd.bdate_range("2004-01-02", "2012-12-31")))
            self.assertNotEqual(data.fingerprint(app), mark)  # the research app moved on; the snapshot did not

    def test_a_damaged_snapshot_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = research_app(Path(tmp) / "research")
            folder, _ = data.snapshot(app, Path(tmp) / "snapshots")
            import gzip
            (folder / "data" / "raw" / "etfs_long.csv.gz").write_bytes(gzip.compress(b"date,ticker\n"))
            with self.assertRaises(ValueError):
                data.snapshot(app, Path(tmp) / "snapshots")

    def test_a_stale_long_history_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = research_app(Path(tmp) / "research")
            raw = app / "data" / "raw"
            recent = pd.read_csv(raw / "etfs_long.csv").tail(50).copy()
            recent["date"] = pd.bdate_range("2013-01-02", periods=50).strftime("%Y-%m-%d")
            recent.to_csv(raw / "etfs.csv", index=False)
            with self.assertRaises(ValueError):
                data.load("SPY", app)


class RunRecordTests(unittest.TestCase):
    def test_names_and_versions(self):
        a = runlog.report_stem("trade-simulation", datetime(2026, 11, 13, 5, 2, 9, tzinfo=timezone.utc))
        b = runlog.report_stem("trade-simulation", datetime(2026, 11, 13, 19, 40, 27, tzinfo=timezone.utc))
        self.assertEqual(a, "2026-11-13-050209-trade-simulation")
        self.assertNotEqual(a, b)  # two runs on one day keep separate reports
        self.assertNotIn("research_app", runlog.settings(CFG))
        self.assertEqual(runlog.settings(CFG)["holdout"], CFG["holdout"])
        with mock.patch.object(runlog, "_git", side_effect=lambda *a: "abc1234" if a[0] == "rev-parse" else " M config.json"):
            self.assertEqual(runlog.code_version(), "abc1234+dirty")
        with mock.patch.object(runlog, "_git", side_effect=lambda *a: "abc1234" if a[0] == "rev-parse" else ""):
            self.assertEqual(runlog.code_version(), "abc1234")

    def test_trade_run_writes_its_record_list_and_export_and_can_be_rebuilt(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            tmp = Path(tmp)
            sandbox(stack, tmp, run_trades)
            self.assertEqual(run_trades.main([]), 0)  # the registered settings
            record = registry.read(tmp / "trials.jsonl")[-1]
            self.assertEqual(record["settings"]["costs_round_trip_bps"]["etf"], 2)
            self.assertEqual((record["family"], record["method"]), ("registered", 2))
            self.assertEqual(record["rules"], lock.marks())
            self.assertTrue((tmp / "reports" / record["report"]).exists())
            trades = pd.read_csv(tmp / record["trade_list"])
            self.assertGreater(len(trades), 0)
            self.assertEqual(set(trades["period"]), {"development", "holdout"})
            export = json.loads((tmp / "exports" / "trade_simulation.json").read_text(encoding="utf-8"))
            self.assertEqual((export["seed"], export["draws"], export["trade_list"]), (11, 2000, record["trade_list"]))
            self.assertEqual(export["data_fingerprint"], record["data"])
            self.assertTrue(all(t["holdout_source"].startswith("first look") for t in record["tests"]))
            # Rebuild from the kept inputs and the ledger alone: same numbers as the record.
            folder = tmp / "snapshots" / record["data"]
            rows, *_ = run_trades.run(2000, 11, CFG, folder, ledger=HoldoutLedger(tmp / "holdout_ledger.jsonl"))
            self.assertEqual([r["dev"]["random_percentile"] for r in rows],
                             [t["dev_random_percentile"] for t in record["tests"]])
            self.assertEqual([r["holdout"]["random_percentile"] for r in rows],
                             [t["holdout_random_percentile"] for t in record["tests"]])
            self.assertEqual([r["verdict"] for r in rows], [t["verdict"] for t in record["tests"]])
            # A second run reads every holdout result from the ledger and adds nothing to it.
            self.assertEqual(run_trades.main([]), 0)
            again = registry.read(tmp / "trials.jsonl")[-1]
            self.assertTrue(all(t["holdout_source"].startswith("ledger") for t in again["tests"]))
            self.assertEqual([t["holdout_random_percentile"] for t in again["tests"]],
                             [t["holdout_random_percentile"] for t in record["tests"]])
            self.assertEqual(len(registry.read(tmp / "holdout_ledger.jsonl")), 1)
            # Other settings never look at the holdout: with an empty ledger there is nothing to show.
            (tmp / "holdout_ledger.jsonl").unlink()
            self.assertEqual(run_trades.main(["--draws", "50"]), 0)
            other = registry.read(tmp / "trials.jsonl")[-1]
            self.assertEqual(other["family"], "unregistered settings")
            self.assertTrue(all(t["holdout_random_percentile"] is None for t in other["tests"]))
            self.assertFalse((tmp / "holdout_ledger.jsonl").exists())

    def test_no_report_or_export_without_a_record(self):
        for module in (run_trades, run_studies):
            with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
                tmp = Path(tmp)
                sandbox(stack, tmp, module)
                (tmp / "trials.jsonl").write_text('{"hash": "not a chain"}\n', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "hash chain"):
                    module.main(["--draws", "20"])
                self.assertFalse((tmp / "reports").exists() and any((tmp / "reports").iterdir()))
                self.assertFalse((tmp / "exports" / "trade_simulation.json").exists())


class SeedAndLedgerTests(unittest.TestCase):
    def test_each_test_has_its_own_random_stream(self):
        a, b = rng_for(7, "rsi2_below_10", "v1", "SPY", 5, "development"), rng_for(7, "rsi2_below_10", "v1", "SPY", 5, "development")
        self.assertEqual(a.integers(0, 10**9, 5).tolist(), b.integers(0, 10**9, 5).tolist())
        other = rng_for(7, "rsi2_below_10", "v1", "SPY", 5, "holdout")
        self.assertNotEqual(rng_for(7, "rsi2_below_10", "v1", "SPY", 5, "development").integers(0, 10**9, 5).tolist(),
                            other.integers(0, 10**9, 5).tolist())

    def test_p_values_do_not_depend_on_order_or_subset_and_partial_runs_give_no_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = research_app(Path(tmp) / "research", symbols=("SPY", "QQQ", "IWM"))
            def p_values(rows):
                return {(r["study"], r["symbol"], r["horizon"]): (r["dev"].get("p"), (r["holdout"] or {}).get("p")) for r in rows}
            full = run_studies.run(list(catalog.SYMBOLS), list(catalog.HORIZONS), 200, catalog.SEED, CFG, app)
            reverse = run_studies.run(["IWM", "QQQ", "SPY"], [10, 5, 1], 200, catalog.SEED, CFG, app)
            subset = run_studies.run(["QQQ"], [5], 200, catalog.SEED, CFG, app)
            self.assertEqual(p_values(full), p_values(reverse))
            self.assertTrue(all(p_values(full)[k] == v for k, v in p_values(subset).items()))
            self.assertEqual(len(subset), len(catalog.STUDIES))
            self.assertTrue(all(r["verdict"] == run_studies.PARTIAL and "q" not in r for r in subset))
            self.assertIn("**Partial run.**", run_studies.report(subset, CFG, "fp", "abc", datetime(2026, 11, 13)))

    def test_holdout_is_evaluated_once_and_then_read_from_the_ledger(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            tmp = Path(tmp)
            sandbox(stack, tmp, run_studies)
            calls = []
            real = run_studies.evaluate
            def counting(signal, forward, mask, horizon, draws=2000, rng=None):
                calls.append(str(mask.index[mask.to_numpy()][0].year))  # first year of the period evaluated
                return real(signal, forward, mask, horizon, draws, rng)
            stack.enter_context(mock.patch.object(run_studies, "evaluate", counting))
            self.assertEqual(run_studies.main(["--symbols", "SPY", "--horizons", "5"]), 0)   # partial: no look
            self.assertNotIn("2004", calls)
            self.assertFalse((tmp / "holdout_ledger.jsonl").exists())
            self.assertEqual(run_studies.main([]), 0)                                         # registered: first look
            first_looks = calls.count("2004")
            self.assertEqual(first_looks, 90)
            self.assertEqual(run_studies.main([]), 0)                                         # again: ledger only
            self.assertEqual(calls.count("2004"), first_looks)
            one, two = registry.read(tmp / "trials.jsonl")[-2:]
            self.assertTrue(all(t["holdout_source"].startswith("first look") for t in one["tests"]))
            self.assertTrue(all(t["holdout_source"].startswith("ledger") for t in two["tests"]))
            self.assertEqual([(t["holdout_p"], t["verdict"]) for t in one["tests"]],
                             [(t["holdout_p"], t["verdict"]) for t in two["tests"]])
            self.assertEqual((one["family"], registry.read(tmp / "trials.jsonl")[0]["family"]), ("registered", "partial"))
            text = (tmp / "reports" / two["report"]).read_text(encoding="utf-8")
            self.assertIn("90 results read from `holdout_ledger.jsonl`", text)

    def test_a_rule_changed_under_its_version_stops_the_run(self):
        self.assertEqual(lock.check(), lock.marks())  # the code matches rule_lock.json
        changed = [catalog.Study("rsi2_below_10", "v1", "edited in place", lambda d: lock.ind.rsi(d["close"], 2) < 12)
                   if s.name == "rsi2_below_10" else s for s in catalog.STUDIES]
        with mock.patch.object(catalog, "STUDIES", changed):
            with self.assertRaisesRegex(ValueError, "changed under a recorded version.*rsi2_below_10@v1"):
                lock.check()
        added = catalog.STUDIES + [catalog.Study("rsi2_below_10", "v2", "a new version", lambda d: lock.ind.rsi(d["close"], 2) < 12)]
        with mock.patch.object(catalog, "STUDIES", added), tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "not registered yet.*rsi2_below_10@v2"):
                lock.check()
            copy = Path(tmp) / "rule_lock.json"
            copy.write_text(lock.LOCK.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual(lock.add(copy), ["study:rsi2_below_10@v2"])
            self.assertEqual(lock.add(copy), [])  # never replaces what is recorded
            lock.check(copy)
        with mock.patch.object(catalog, "STUDIES", catalog.STUDIES[1:]):
            with self.assertRaisesRegex(ValueError, "no longer in the code"):
                lock.check()


if __name__ == "__main__":
    unittest.main()
