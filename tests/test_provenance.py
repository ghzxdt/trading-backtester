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
from backtester import data, registry, runlog  # noqa: E402

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
            self.assertEqual(run_trades.main(["--draws", "50", "--seed", "3"]), 0)
            record = registry.read(tmp / "trials.jsonl")[-1]
            self.assertEqual(record["settings"]["costs_round_trip_bps"]["etf"], 2)
            self.assertTrue((tmp / "reports" / record["report"]).exists())
            trades = pd.read_csv(tmp / record["trade_list"])
            self.assertGreater(len(trades), 0)
            self.assertEqual(set(trades["period"]), {"development", "holdout"})
            export = json.loads((tmp / "exports" / "trade_simulation.json").read_text(encoding="utf-8"))
            self.assertEqual((export["seed"], export["draws"], export["trade_list"]), (3, 50, record["trade_list"]))
            self.assertEqual(export["data_fingerprint"], record["data"])
            # Rebuild from the kept inputs alone: same numbers as the record.
            folder = tmp / "snapshots" / record["data"]
            rows, *_ = run_trades.run(50, 3, CFG, folder, **self.rebuild_arguments(tmp))
            self.assertEqual([r["dev"]["random_percentile"] for r in rows],
                             [t["dev_random_percentile"] for t in record["tests"]])
            self.assertEqual([r["verdict"] for r in rows], [t["verdict"] for t in record["tests"]])

    def rebuild_arguments(self, tmp: Path) -> dict:
        return {}

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


if __name__ == "__main__":
    unittest.main()
