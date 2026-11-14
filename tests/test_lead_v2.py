"""Lead verdict v2: exact baseline, a test that uses the rule's own spread, a risk-matched benchmark, the labels."""
import sys, unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backtester import lead_v2, simulate  # noqa: E402

CFG = {"costs_round_trip_bps": {"etf": 2, "kalshi_taker": 24, "kalshi_maker": 4}, "funding_bps_per_day": 1.37}


def hold(n):
    return lambda f, pos: pos + n


def stormy_history(seed, days=3000):
    """Calm most of the time, with a 40-day stormy stretch about once a year. The signal fires only in the storms
    and carries no information: every day has the same expected return."""
    rng = np.random.default_rng(seed)
    vol = np.full(days, 0.007)
    start = 0
    while start < days:
        start += int(rng.integers(150, 350))
        vol[start:start + 40] = 0.025
    close = 100 * np.cumprod(1 + rng.normal(0.0003, vol))
    frame = pd.DataFrame({"open": np.r_[100, close[:-1]], "high": close * 1.01, "low": close * 0.99, "close": close},
                         index=pd.bdate_range("2010-01-04", periods=days))
    storm = np.flatnonzero(vol > 0.02)
    signal = pd.Series(False, index=frame.index)
    signal.iloc[rng.choice(storm[storm < days - 20], size=min(60, len(storm) // 3), replace=False)] = True
    return frame, signal


class LeadV2Tests(unittest.TestCase):
    def test_baseline_is_the_average_of_every_possible_trade(self):
        f = pd.DataFrame({"open": [10.0, 10, 11, 12, 13, 14], "close": [10.0, 11, 12, 13, 14, 15]},
                         index=pd.bdate_range("2020-01-01", periods=6))
        mask = pd.Series([False, True, True, True, True, True], index=f.index)
        base = lead_v2.baseline(f, mask, np.array([2, 1]), "etf_close")
        self.assertAlmostEqual(base[0], np.mean([13 / 11 - 1, 14 / 12 - 1, 15 / 13 - 1]))  # exits stay inside the period
        self.assertAlmostEqual(base[1], np.mean([12 / 11 - 1, 13 / 12 - 1, 14 / 13 - 1, 15 / 14 - 1]))
        nxt = lead_v2.baseline(f, mask, np.array([2]), "etf_next_open")
        self.assertAlmostEqual(nxt[0], np.mean([13 / 11 - 1, 14 / 12 - 1, 15 / 13 - 1]))  # bought at the next open

    def test_zero_edge_rule_that_trades_in_storms_is_not_passed_more_often_than_chance(self):
        """The reason for v2. v1's random-entry percentile passes such a rule far more than 5% of the time."""
        runs, v1, v2 = 120, 0, 0
        for seed in range(runs):
            frame, signal = stormy_history(seed)
            mask = pd.Series(True, index=frame.index)
            trades = simulate.find_trades(frame, signal, hold(5), mask)
            priced = simulate.price_trades(frame, trades, "etf_close", CFG)
            v1 += simulate.random_percentile(frame, mask, priced, "etf_close", 400, np.random.default_rng(seed)) >= 95
            test = lead_v2.excess_test(priced, lead_v2.baseline(frame, mask, priced["sessions"].to_numpy(int), "etf_close"),
                                       np.random.default_rng(seed), 600)
            v2 += test["p"] < lead_v2.DEV_P and test["mean_excess"] > 0
        self.assertGreater(v1 / runs, 0.12)
        self.assertLess(v2 / runs, 0.09)

    def test_a_planted_edge_is_found(self):
        frame, signal = stormy_history(3)
        close = frame["close"].to_numpy().copy()
        for p in np.flatnonzero(signal.to_numpy()):
            close[p + 1:] *= 1.02
        frame["close"] = close
        mask = pd.Series(True, index=frame.index)
        trades = simulate.find_trades(frame, signal, hold(5), mask)
        priced = simulate.price_trades(frame, trades, "etf_close", CFG)
        out = lead_v2.evaluate(frame, trades, priced, mask, "etf_close", CFG, np.random.default_rng(1), 2000)
        self.assertLess(out["v2"]["p"], 0.01)
        self.assertGreater(out["v2"]["mean_excess"], 0.01)
        self.assertGreaterEqual(out["v2"]["quarters"], lead_v2.MIN_QUARTERS)

    def test_risk_matched_benchmark_scales_with_in_trade_volatility(self):
        frame, signal = stormy_history(5)
        mask = pd.Series(True, index=frame.index)
        trades = simulate.find_trades(frame, signal, hold(5), mask)
        priced = simulate.price_trades(frame, trades, "etf_close", CFG)
        returns, exposure = simulate.daily_returns(frame, trades, "etf_close", CFG, mask)
        fraction = lead_v2.risk_fraction(frame, trades, returns, exposure, mask)
        self.assertGreater(fraction, 1.5 * exposure)  # the rule holds through storms, so the benchmark holds more
        out = lead_v2.evaluate(frame, trades, priced, mask, "etf_close", CFG, np.random.default_rng(1), 200)
        self.assertAlmostEqual(out["risk_fraction"], fraction)
        expected = simulate.summary(simulate.matched_buy_and_hold(frame, mask, fraction, "etf_close", CFG))
        self.assertEqual(out["risk_matched"], expected)
        calm = pd.Series(False, index=frame.index)
        calm.iloc[::40] = True  # spread evenly: in-trade volatility is about the same as every day's
        even = simulate.find_trades(frame, calm, hold(5), mask)
        r, e = simulate.daily_returns(frame, even, "etf_close", CFG, mask)
        self.assertAlmostEqual(lead_v2.risk_fraction(frame, even, r, e, mask) / e, 1.0, delta=0.25)

    def test_verdicts(self):
        def result(trades, excess, p, cagr, matched, quarters=12):
            return {"trades": trades, "strategy": {"cagr": cagr}, "risk_matched": {"cagr": matched},
                    "v2": {"mean_excess": excess, "p": p, "quarters": quarters}}
        good = result(60, 0.004, 0.01, 0.05, 0.03)
        self.assertEqual(lead_v2.verdict(good, good, 0.05), "Lead")
        self.assertEqual(lead_v2.verdict(good, good, 0.20), "No edge")           # fails the correction for 24 tests
        self.assertEqual(lead_v2.verdict(good, good, None), "No edge")
        self.assertEqual(lead_v2.verdict(result(60, 0.004, 0.06, 0.05, 0.03), good, 0.05), "No edge")
        self.assertEqual(lead_v2.verdict(result(60, -0.004, 0.01, 0.05, 0.03), good, 0.05), "No edge")
        self.assertEqual(lead_v2.verdict(result(15, 0.004, 0.01, 0.05, 0.03), good, 0.05), "Too few trades")
        self.assertEqual(lead_v2.verdict(result(60, 0.004, 0.01, 0.05, 0.03, quarters=5), good, 0.05), "Too few trades")
        self.assertEqual(lead_v2.verdict(good, None, 0.05), "Development only (no holdout)")
        self.assertEqual(lead_v2.verdict(good, result(10, 0.004, 0.01, 0.05, 0.03), 0.05), "Development only (no holdout)")
        self.assertEqual(lead_v2.verdict(good, result(60, 0.004, 0.2, 0.05, 0.03), 0.05), "Failed holdout")
        self.assertEqual(lead_v2.verdict(good, result(60, -0.001, 0.05, 0.05, 0.03), 0.05), "Failed holdout")
        self.assertEqual(lead_v2.verdict(good, result(60, 0.004, 0.05, 0.02, 0.03), 0.05), "Timing edge only")
        self.assertEqual(lead_v2.verdict(result(60, 0.004, 0.01, 0.02, 0.03), good, 0.05), "Timing edge only")


if __name__ == "__main__":
    unittest.main()
