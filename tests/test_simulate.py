"""Trade simulation mechanics: entries and exits, no overlap, costs and funding, benchmarks, verdicts."""
import sys, unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backtester import simulate  # noqa: E402
from backtester.strategies import EXITS  # noqa: E402

CFG = {"costs_round_trip_bps": {"etf": 2, "kalshi_taker": 24, "kalshi_maker": 4}, "funding_bps_per_day": 1.37}
DAYS = pd.bdate_range("2011-01-03", periods=1500)


def frame(seed=3, n=len(DAYS)):
    r = np.random.default_rng(seed).normal(0.0003, 0.011, n)
    close = pd.Series(100 * np.cumprod(1 + r), index=DAYS[:n])
    opens = close.shift(1).fillna(100) * (1 + np.random.default_rng(seed + 9).normal(0, 0.002, n))
    return pd.DataFrame({"open": opens, "high": close * 1.01, "low": close * 0.99, "close": close})


def hold(n):
    return lambda f, pos: pos + n


def everywhere(f):
    return pd.Series(True, index=f.index)


class TradeTests(unittest.TestCase):
    def test_one_position_at_a_time_and_both_days_inside(self):
        f = frame()
        signal = pd.Series(False, index=f.index)
        signal.iloc[[10, 12, 15, 16, 40, len(f) - 3]] = True
        mask = everywhere(f)
        trades = simulate.find_trades(f, signal, hold(5), mask)
        self.assertEqual(trades, [(10, 15), (16, 21), (40, 45)])  # 12 and 15 overlap; the last runs past the data
        mask.iloc[44:] = False
        self.assertEqual(simulate.find_trades(f, signal, hold(5), mask), [(10, 15), (16, 21)])

    def test_close_above_sma5_exit_is_bounded(self):
        f = frame()
        rule = {e.name: e for e in EXITS}["close_above_sma5"].rule
        exits = rule(f, np.arange(20, 200))
        self.assertTrue(((exits > np.arange(20, 200)) & (exits <= np.arange(20, 200) + 10)).all())

    def test_costs_and_funding_crossings(self):
        mon, tue, fri, next_mon = (pd.Timestamp(d) for d in ("2026-11-02", "2026-11-03", "2026-11-06", "2026-11-09"))
        self.assertAlmostEqual(simulate.costs_for("etf_close", CFG, mon, fri), 2e-4)
        self.assertAlmostEqual(simulate.costs_for("perp_taker", CFG, mon, tue), 24e-4)  # no 4 PM crossed
        self.assertAlmostEqual(simulate.costs_for("perp_maker", CFG, fri, next_mon), (4 + 2 * 1.37) * 1e-4)
        self.assertAlmostEqual(simulate.costs_for("perp_maker", CFG, mon, next_mon), (4 + 6 * 1.37) * 1e-4)

    def test_entry_prices_by_mode(self):
        f = frame()
        trades = [(30, 35)]
        close = simulate.price_trades(f, trades, "etf_close", CFG).iloc[0]
        nxt = simulate.price_trades(f, trades, "etf_next_open", CFG).iloc[0]
        self.assertAlmostEqual(close["gross"], f["close"].iloc[35] / f["close"].iloc[30] - 1)
        self.assertAlmostEqual(nxt["gross"], f["close"].iloc[35] / f["open"].iloc[31] - 1)
        self.assertAlmostEqual(close["net"], (1 + close["gross"]) * (1 - 2e-4) - 1)  # as the equity curve compounds it
        self.assertEqual(close["entry_day"], f.index[30])
        self.assertEqual(nxt["entry_day"], f.index[31])
        self.assertAlmostEqual(nxt["entry_price"], f["open"].iloc[31])
        self.assertAlmostEqual(close["exit_price"], f["close"].iloc[35])

    def test_daily_equity_compounds_to_the_trade_result(self):
        f = frame()
        trades = [(30, 35), (50, 58)]
        mask = everywhere(f)
        for mode in ("etf_close", "etf_next_open", "perp_taker"):
            returns, exposure = simulate.daily_returns(f, trades, mode, CFG, mask)
            priced = simulate.price_trades(f, trades, mode, CFG)
            expected = np.prod(1 + priced["net"])  # the trade list and the equity curve agree
            self.assertAlmostEqual(float((1 + returns).prod()), float(expected), places=10)
            self.assertAlmostEqual(exposure, 13 / len(f))
            self.assertEqual(returns.iloc[:31].abs().sum(), 0.0)  # cash before the first trade

    def test_matched_buy_and_hold(self):
        f = frame()
        mask = everywhere(f)
        full = simulate.matched_buy_and_hold(f, mask, 1.0, "etf_close", CFG)
        pd.testing.assert_series_equal(full, f["close"].pct_change().fillna(0.0), check_names=False)
        self.assertEqual(simulate.matched_buy_and_hold(f, mask, 0.0, "perp_taker", CFG).abs().sum(), 0.0)
        half = simulate.matched_buy_and_hold(f, mask, 0.5, "perp_maker", CFG)
        self.assertLess(half.sum(), (0.5 * full).sum())  # funding is charged

    def test_planted_edge_ranks_high_and_noise_does_not(self):
        f = frame(seed=5)
        rng = np.random.default_rng(1)
        signal = pd.Series(False, index=f.index)
        signal.iloc[rng.choice(np.arange(30, len(f) - 20), 120, replace=False)] = True
        mask = everywhere(f)
        noise = simulate.evaluate(f, signal, hold(5), mask, "etf_close", CFG, 2000, np.random.default_rng(2))
        self.assertTrue(10 < noise["random_percentile"] < 90)
        planted = f.copy()
        close = planted["close"].to_numpy().copy()
        for p in np.flatnonzero(signal.to_numpy()):
            close[p + 1:] *= 1.004  # each signal is followed by a +0.4% day
        planted["close"] = close
        edge = simulate.evaluate(planted, signal, hold(5), mask, "etf_close", CFG, 2000, np.random.default_rng(2))
        self.assertGreater(edge["random_percentile"], 97)

    def test_verdicts(self):
        def result(trades, pct, cagr, matched):
            return {"trades": trades, "random_percentile": pct, "strategy": {"cagr": cagr}, "matched": {"cagr": matched}}
        good = result(60, 99, 0.05, 0.03)
        self.assertEqual(simulate.verdict(good, good), "Lead")
        self.assertEqual(simulate.verdict(good, result(40, 92, 0.01, 0.02)), "Timing edge only")
        self.assertEqual(simulate.verdict(good, result(40, 60, 0.05, 0.01)), "Failed holdout")
        self.assertEqual(simulate.verdict(result(60, 80, 0.05, 0.01), good), "No edge")
        self.assertEqual(simulate.verdict(result(10, 99, 0.05, 0.01), good), "Too few trades")
        self.assertEqual(simulate.verdict(good, None), "Development only (no holdout)")

    def test_summary(self):
        flat = simulate.summary(pd.Series(0.0, index=DAYS[:252]))
        self.assertAlmostEqual(flat["cagr"], 0.0)
        self.assertEqual(flat["max_drawdown"], 0.0)
        r = pd.Series([0.1, -0.5, 0.2], index=DAYS[:3])
        self.assertAlmostEqual(simulate.summary(r)["max_drawdown"], -0.5)
        early_loss = pd.Series([-0.05, 0.01, 0.01], index=DAYS[:3])  # a loss on day one is a drawdown from the start
        self.assertAlmostEqual(simulate.summary(early_loss)["max_drawdown"], -0.05)


class RunTradesTests(unittest.TestCase):
    def test_full_run_report_and_export_on_synthetic_history(self):
        import tempfile
        import run_trades
        days = pd.bdate_range("2004-01-02", "2012-12-31")
        r = np.random.default_rng(4).normal(0.0003, 0.012, len(days))
        close = 100 * np.cumprod(1 + r)
        table = pd.DataFrame({"date": days, "ticker": "SPY", "open": np.r_[100, close[:-1]], "high": close * 1.01,
                              "low": close * 0.99, "close": close, "volume": 1e6})
        cfg = {**CFG, "development": {"start": "2010-01-01", "end": None},
               "holdout": {"start": "1993-01-01", "end": "2009-12-31"}}
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "data" / "raw"
            raw.mkdir(parents=True)
            table.to_csv(raw / "etfs_long.csv", index=False)
            rows, signal_days, full, trades = run_trades.run(50, 1, cfg, Path(tmp), symbols=("SPY",))
        self.assertEqual(len(rows), 3 * 2 * 4)
        self.assertNotIn("priced", rows[0]["dev"])  # the trade list is not left inside a result
        self.assertEqual(len(trades), sum(r["dev"]["trades"] + r["holdout"]["trades"] for r in rows))
        self.assertEqual(list(trades.columns), run_trades.TRADE_COLUMNS)
        one = trades[(trades["pricing"] == "etf_next_open") & (trades["period"] == "development")].iloc[0]
        self.assertGreater(one["entry_day"], one["signal_day"])  # bought the morning after the signal
        self.assertAlmostEqual(one["net"], (one["exit_price"] / one["entry_price"]) * (1 - one["cost"]) - 1, places=4)
        text = run_trades.report(rows, cfg, "fp", "abc123", pd.Timestamp("2026-11-08"), 50, full)
        self.assertIn("## Verdicts", text)
        self.assertIn("Return per unit of drawdown", text)
        out = run_trades.export(rows, signal_days, cfg, "fp", "abc123", pd.Timestamp("2026-11-08"), "r.md", full)
        self.assertEqual({s["mode"] for s in out["strategies"]}, {"etf_close", "etf_next_open"})  # no Kalshi in the thesis
        self.assertEqual(len(out["strategies"]), 12)
        self.assertEqual(out["schema"], 1)  # the research app reads schema 1
        self.assertEqual(out["data_through"], {"SPY": "2012-12-31"})
        self.assertIn("Lead", out["verdict_definition"])
        self.assertEqual(signal_days["SPY:rsi2_below_10"]["last_date"], "2012-12-31")


if __name__ == "__main__":
    unittest.main()
