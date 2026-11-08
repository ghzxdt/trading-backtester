"""Indicators are causal and match their definitions; studies, verdicts and the trial record behave."""
import json, sys, tempfile, unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backtester import catalog, indicators as ind, registry, study  # noqa: E402

DAYS = pd.bdate_range("2000-01-03", periods=900)


def prices(seed=1):
    r = np.random.default_rng(seed).normal(0.0004, 0.012, len(DAYS))
    close = pd.Series(100 * np.cumprod(1 + r), index=DAYS)
    spread = close * 0.006
    return pd.DataFrame({"open": close.shift(1).fillna(100), "high": close + spread, "low": close - spread,
                         "close": close, "volume": np.random.default_rng(seed + 1).integers(1e6, 3e6, len(DAYS)).astype(float)})


class IndicatorTests(unittest.TestCase):
    def test_every_indicator_is_causal(self):
        """Values up to day t must not change when later days are added."""
        full, cut = prices(), prices().iloc[:600]
        series = {
            "ema": lambda d: ind.ema(d["close"], 21), "sma": lambda d: ind.sma(d["close"], 200),
            "rsi": lambda d: ind.rsi(d["close"], 14), "macd": lambda d: ind.macd(d["close"])["signal"],
            "atr": lambda d: ind.atr(d["high"], d["low"], d["close"]), "bb": lambda d: ind.bollinger(d["close"])["lower"],
            "relvol": lambda d: ind.relative_volume(d["volume"])}
        for name, f in series.items():
            pd.testing.assert_series_equal(f(full).iloc[:600], f(cut), check_names=False, obj=name)
        for s in catalog.STUDIES:
            pd.testing.assert_series_equal(s.rule(full).iloc[:600], s.rule(cut), check_names=False, obj=s.name)

    def test_definitions(self):
        up = pd.Series(np.arange(1.0, 40.0))
        self.assertEqual(ind.rsi(up, 14).dropna().iloc[-1], 100.0)
        self.assertTrue(ind.rsi(up, 14).iloc[:14].isna().all())
        s = pd.Series([1.0, 2.0, 3.0, 4.0])
        self.assertAlmostEqual(ind.ema(s, 3).iloc[-1], ((1 * .5 + 2 * .5) * .5 + 3 * .5) * .5 + 4 * .5)
        self.assertEqual(ind.relative_volume(pd.Series([1.0] * 20 + [3.0]), 20).iloc[-1], 3.0)
        a, b = pd.Series([1.0, 1.0, 3.0, 3.0]), pd.Series([2.0, 2.0, 2.0, 2.0])
        self.assertEqual(ind.crossed_above(a, b).tolist(), [False, False, True, False])


class StudyTests(unittest.TestCase):
    def test_forward_returns_line_up(self):
        d = pd.DataFrame({"open": [10.0, 11, 12, 13], "close": [10.0, 12, 14, 16]})
        self.assertAlmostEqual(study.forward_return(d, 1)[0], 0.2)
        self.assertAlmostEqual(study.forward_return(d, 2, "next_open")[0], 14 / 11 - 1)
        self.assertTrue(np.isnan(study.forward_return(d, 1)[3]))

    def test_non_overlapping_count(self):
        self.assertEqual(study.non_overlapping(np.array([0, 1, 2, 5, 6, 10]), 5), 3)

    def test_signal_on_every_day_has_no_excess(self):
        fwd = study.forward_return(prices(), 5)
        mask = pd.Series(True, index=DAYS)
        out = study.evaluate(pd.Series(True, index=DAYS), fwd, mask, 5, 200)
        self.assertAlmostEqual(out["excess"], 0.0)
        self.assertGreater(out["p"], 0.5)

    def test_planted_effect_is_found_and_noise_is_not(self):
        d = prices(3)
        fwd = study.forward_return(d, 1)
        mask = pd.Series(True, index=DAYS)
        signal = pd.Series(False, index=DAYS)
        signal.iloc[::15] = True
        planted = fwd.copy()
        planted[signal] += 0.01
        self.assertLess(study.evaluate(signal, planted, mask, 1, 500)["p"], 0.01)
        self.assertGreater(study.evaluate(signal, fwd, mask, 1, 500)["p"], 0.05)

    def test_too_few_signals(self):
        signal = pd.Series(False, index=DAYS)
        signal.iloc[:5] = True
        out = study.evaluate(signal, study.forward_return(prices(), 1), pd.Series(True, index=DAYS), 1, 50)
        self.assertNotEqual(out["status"], "ok")

    def test_bh_qvalues(self):
        self.assertEqual([round(q, 3) for q in study.bh_qvalues([0.01, 0.04, 0.03, 0.5])], [0.04, 0.053, 0.053, 0.5])

    def test_verdicts(self):
        ok = {"status": "ok", "excess": 0.002, "p": 0.01}
        self.assertEqual(study.verdict(ok, ok, 0.05, 0.0002), "Candidate")
        self.assertEqual(study.verdict(ok, {**ok, "excess": -0.001}, 0.05, 0.0002), "Failed holdout")
        self.assertEqual(study.verdict(ok, None, 0.05, 0.0002), "Development only (no holdout data)")
        self.assertEqual(study.verdict(ok, ok, 0.2, 0.0002), "No evidence")  # fails the multiple-testing check
        self.assertEqual(study.verdict({**ok, "excess": 0.0001}, ok, 0.05, 0.0002), "Real but smaller than costs")
        self.assertEqual(study.verdict({**ok, "excess": -0.002}, ok, 0.05, 0.0002), "Opposite effect (weaker than normal)")


class RegistryTests(unittest.TestCase):
    def test_chain_appends_and_detects_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trials.jsonl"
            registry.append(path, {"tests": [1, 2]})
            registry.append(path, {"tests": [3]})
            self.assertEqual(registry.total_tests(path), 3)
            lines = path.read_text(encoding="utf-8").splitlines()
            first = json.loads(lines[0])
            first["tests"] = [9]
            path.write_text(json.dumps(first) + "\n" + lines[1] + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                registry.read(path)


if __name__ == "__main__":
    unittest.main()
