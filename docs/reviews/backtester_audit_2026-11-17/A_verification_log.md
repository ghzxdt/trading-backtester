# Appendix A. Verification log

Part of the [backtester audit of 2026-11-17](../BACKTESTER_AUDIT_2026-11-17.md). How every verified statement in
this review was checked, so each can be repeated.

## A.1 Environment and isolation

- Checks run on 2026-11-18 (early morning, Central time) with the research app's Python 3.12
  (`C:\Claude\trading-research\.venv\Scripts\python.exe -B`).
- Code under test: the tracked files of `C:\Claude\trading-backtester` at 407cd65, copied with `git ls-files` into a
  scratch folder (`bt_copy`), plus copies of `trials.jsonl` and `holdout_ledger.jsonl`. (Commit 28ce2c8, made by
  another session during this review, added only the 2026-11-17 run outputs; the code is identical.)
- Data: the kept snapshot `snapshots/c4713b15d633ad4c` (research-app files as of 2026-11-17 18:26 CT, prices through
  2026-11-13), read in place, read-only. The earlier snapshot `4e1f98996cd13f8f` for the drift comparison.
- Research app: read-only file reads and GET requests to the local dashboard (`http://127.0.0.1:8766/thesis.html`);
  its build state `output/thesis_state.json` (built 2026-11-17 21:39 ET); its data folders for coverage counts.
- Nothing was written into either project except this review and the LOG entry. No study or trade simulation was
  run in the project folder (the app's buttons append to `trials.jsonl`), so the Tk window was read from code, not
  launched.
- 1993-2009 was not evaluated for any new rule or variant. The only 1993-2009 numbers quoted are ones already in the
  holdout ledger.

## A.2 Checks and results

| # | Check | Method | Sample and parameters | Result |
|---|---|---|---|---|
| 1 | Unit tests | `-m unittest discover -s tests` in the scratch copy | 36 tests | OK (22 s) |
| 2 | Exact rebuild of the latest records | `rebuild_check.py`: `run_studies.run` and `run_trades.run` on the snapshot with a copy of the ledger; compare 6 study fields x 90 tests and 11 trade fields x 48 results with `trials.jsonl` | Records of 2026-11-18 00:26:54 and 00:27:51 UTC; seeds 7 and 11; 2,000 draws | 0 differing values |
| 3 | Data integrity | `data_check.py` | All symbols in the snapshot | OHLC consistent; adjusted consistently; no duplicates; gaps only at real closures; files agree within 1.8e-6; SQQQ 29 zero-volume days |
| 4 | Download drift | `snap_diff.py` | Snapshots of 2026-11-14 and 2026-11-17, both ending 2026-11-13 | Up to 1.6e-6 relative change in about 60% of rows; no new or missing rows; VIX unchanged |
| 5 | Independent study reproduction | `independent.py` part 1: own Wilder RSI and Bollinger, own forward returns and excess | SPY, QQQ, IWM x 3 oversold studies x h 1, 5, 10; development 2010-01-01..2026-11-13 | 24 of 27 exact; IWM RSI(14) differs (7 early-2010 days; RSI seed) by up to 15 bp |
| 6 | RSI seed difference | Inline script (A.4) | IWM, 2010 on | First RSI(14) values 27.82 (backtester) vs 37.05 (Wilder); max gap 9.2 points on 2010-01-25; below 0.005 after 2010-06-01 |
| 7 | Independent trade reproduction | `independent.py` part 2 vs `exports/trades/2026-11-18-002751-trade-simulation.csv` | 24 development strategy-pricings (ETF) | Same signal and exit days for all; gross within 5e-7 (CSV rounding) |
| 8 | Exit timing | `independent.py` part 3: `close_above_sma5` exit moved to the next open | 12 strategy-pricings, development | Mean changes -6.8 to +7.1 bp |
| 9 | Cost sensitivity | `independent.py` part 4 | 4 strategy-pricings at 2/5/10/20 bp | Leads positive at 20 bp |
| 10 | Concentration and overlap | `independent.py` parts 5-6 | QQQ next-open Leads, development | See [01 section 1.9](01_technical_accuracy_audit.md) |
| 11 | Parameter neighbourhood | `sensitivity.py` (unregistered variants, development only) | QQQ and SPY, listed variants | See [01 section 1.6](01_technical_accuracy_audit.md) |
| 12 | Calibration of the two tests | `calibration.py 500`: the backtester's own `study.evaluate` and `lead_v2.excess_test` on synthetic zero-edge histories | 500 x 4,250-day histories per world type; constant volatility and GARCH(1,1) 0.10/0.88 with t(6) shocks; study test 500 shifts; v2 1,000 resamples | Rejection rates in [01 section 1.7](01_technical_accuracy_audit.md); Monte Carlo error about +/-1 point |
| 13 | Forward power and overlay | `forward_power.py` | QQQ Leads, development | See [06 section 6.3](06_validation_framework.md), [01 section 1.8](01_technical_accuracy_audit.md) |
| 14 | Intra-trade excursions | `excursions.py` | 4 strategy-pricings, development | See [01 section 1.8](01_technical_accuracy_audit.md) |
| 15 | Research app consumption | Read `output/thesis_state.json` | Build of 2026-11-17 21:39 ET | Export of 2026-11-18 00:27:51 UTC read; 807 dates cross-checked, match; evidence age 4 days |
| 16 | Research app records | Counted lines in `data/thesis/*`, `data/monitor/paper_events.jsonl`, `data/intraday/v1/bars.jsonl`, `data/intraday_hourly/*`, `data/news_history/headlines-v1.jsonl` | As of 2026-11-18 | 8 stance records; 0 calls, journal notes, pre-close records; 16 paper decisions and 8 outcomes; minute bars for 12 sessions (2026-11-02..14); hourly bars from 2023-12-18; 333 headlines first seen 2026-11-08..17; no futures, nowcast or same-day option files |

**Limits of these checks.** Prices were not compared with a second vendor. The perp assumptions were not tested.
The Tk window was not opened. Calibration used one family of synthetic worlds; real markets may be more extreme. The
sensitivity probe is exploratory and on the development period only. Nothing after the 2026-11-13 close (data) or the
2026-11-17 close (research app state) was observed.

## A.3 Scripts

All scripts sit beside a scratch copy of the backtester (`bt_copy/`) and read the real snapshot read-only. `lib.py` is
the part of `independent.py` above the line `report = {}` (the helper functions), saved separately so the other
scripts can import it without printing. Run each with `python -B <script>` from the scripts' folder.

### rebuild_check.py

```python
"""Rebuild the two latest recorded runs (2026-11-18 studies and trade simulation) from their kept snapshot and the
holdout ledger, using a scratch copy of the code, and compare every number with the trial record. Read-only:
the ledger is read, never committed; the snapshot is read from the real repo's snapshots folder."""
import json
import sys
from pathlib import Path

SCR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCR / "bt_copy"))
import run_studies, run_trades  # noqa: E402
from backtester import catalog, data, strategies  # noqa: E402
from backtester.ledger import HoldoutLedger  # noqa: E402

REPO = Path(r"C:\Claude\trading-backtester")
records = [json.loads(l) for l in (REPO / "trials.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
cfg = json.loads((REPO / "config.json").read_text(encoding="utf-8"))
ledger = HoldoutLedger(SCR / "bt_copy" / "holdout_ledger.jsonl")  # a copy; commit() is never called


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str):
        return a == b
    return abs(a - b) <= 1e-12 * max(1, abs(a), abs(b))


for rec in records[-2:]:
    folder = REPO / "snapshots" / rec["data"]
    assert data.fingerprint(folder) == rec["data"], "snapshot fingerprint mismatch"
    if rec.get("kind") == "trade_simulation":
        rows, *_ = run_trades.run(rec["draws"], rec["seed"], cfg, folder, ledger=ledger)
        fields = [("verdict", lambda r: r["verdict"]), ("verdict_v1", lambda r: r["verdict_v1"]), ("q", lambda r: r.get("q")),
                  ("dev_excess", lambda r: (r["dev"].get("v2") or {}).get("mean_excess")),
                  ("dev_p", lambda r: (r["dev"].get("v2") or {}).get("p")),
                  ("dev_trades", lambda r: r["dev"]["trades"]), ("dev_mean_net", lambda r: r["dev"].get("mean_net")),
                  ("dev_cagr", lambda r: r["dev"]["strategy"]["cagr"]),
                  ("dev_risk_matched_cagr", lambda r: (r["dev"].get("risk_matched") or {}).get("cagr")),
                  ("holdout_p", lambda r: ((r["holdout"] or {}).get("v2") or {}).get("p")),
                  ("dev_random_percentile", lambda r: r["dev"].get("random_percentile"))]
    else:
        rows = run_studies.run(list(catalog.SYMBOLS), list(catalog.HORIZONS), rec["draws"], rec["seed"], cfg, folder, ledger=ledger)
        fields = [("verdict", lambda r: r["verdict"]), ("q", lambda r: r.get("q")), ("dev_excess", lambda r: r["dev"].get("excess")),
                  ("dev_p", lambda r: r["dev"].get("p")), ("holdout_excess", lambda r: (r["holdout"] or {}).get("excess")),
                  ("holdout_p", lambda r: (r["holdout"] or {}).get("p"))]
    bad = 0
    for row, test in zip(rows, rec["tests"]):
        for name, get in fields:
            if not same(get(row), test.get(name)):
                bad += 1
                if bad <= 5:
                    print("  differs:", name, get(row), test.get(name))
    print(f"{rec.get('kind', 'studies')} {rec['run_at']} data {rec['data']}: {len(rows)} rows vs {len(rec['tests'])} recorded, "
          f"{bad} differing values across {len(fields)} fields")
```

### data_check.py

```python
"""Independent data checks on the latest kept snapshot (read-only). No backtester code is imported."""
import gzip
import io
from pathlib import Path

import numpy as np
import pandas as pd

SNAP = Path(r"C:\Claude\trading-backtester\snapshots\c4713b15d633ad4c\data\raw")


def read(name):
    return pd.read_csv(io.BytesIO(gzip.decompress((SNAP / f"{name}.gz").read_bytes())))


long, short, vix = read("etfs_long.csv"), read("etfs.csv"), read("VIX.csv")
print("etfs_long columns", list(long.columns), "tickers", sorted(long["ticker"].unique()))
print("etfs columns", list(short.columns), "tickers", sorted(short["ticker"].unique()))
for name, table in (("long", long), ("short", short)):
    for sym, g in table.groupby("ticker"):
        g = g.assign(date=pd.to_datetime(g["date"])).set_index("date").sort_index()
        o, h, l, c = (g[k] for k in ("open", "high", "low", "close"))
        bad_hl = int(((h < np.maximum(o, c) * (1 - 1e-6)) | (l > np.minimum(o, c) * (1 + 1e-6))).sum())
        gaps = g.index.to_series().diff().dt.days
        per_year = g.groupby(g.index.year).size()
        thin = {int(y): int(n) for y, n in per_year.items() if n < 245 and y not in (g.index[0].year, g.index[-1].year)}
        dup = int(g.index.duplicated().sum())
        zero_vol = int((g["volume"] <= 0).sum())
        overnight = (o / c.shift(1) - 1).abs()
        print(f"{name:5} {sym:5} {g.index[0]:%Y-%m-%d}..{g.index[-1]:%Y-%m-%d} rows {len(g)} dup {dup} "
              f"OHLC-inconsistent {bad_hl} gaps>4d {int((gaps > 4).sum())} thin-years {thin} zero-vol {zero_vol} "
              f"max |open/prev close-1| {overnight.max():.3f} on {overnight.idxmax():%Y-%m-%d}")
# Do the two files agree where they overlap (SPY, QQQ since 2010)?
for sym in ("SPY", "QQQ"):
    a = long[long.ticker == sym].assign(date=lambda d: pd.to_datetime(d["date"])).set_index("date")
    b = short[short.ticker == sym].assign(date=lambda d: pd.to_datetime(d["date"])).set_index("date")
    common = a.index.intersection(b.index)
    ra, rb = a.loc[common, "close"].pct_change(), b.loc[common, "close"].pct_change()
    oa, ob = (a.loc[common, "open"] / a.loc[common, "close"]), (b.loc[common, "open"] / b.loc[common, "close"])
    print(f"{sym}: {len(common)} common days; max |return diff| {np.nanmax(np.abs(ra - rb)):.2e}; "
          f"max |open/close ratio diff| {np.nanmax(np.abs(oa - ob)):.2e}; price level ratio {a.loc[common, 'close'].iloc[-1] / b.loc[common, 'close'].iloc[-1]:.6f}")
# The earliest SPY rows: adjusted (a raw 1993 SPY traded near $44)
first = long[long.ticker == "SPY"].head(3)
print(first.to_string(index=False))
print(long[long.ticker == "SPY"].tail(4).to_string(index=False))
print(short[short.ticker == "QQQ"].tail(3).to_string(index=False))
vix.columns = [c.strip().upper() for c in vix.columns]
print("VIX rows", len(vix), vix.iloc[0].to_dict(), vix.iloc[-1].to_dict())
```

### snap_diff.py

```python
"""Compare the two kept snapshots (Nov 14 run vs Nov 17 run): what changed in the research app's files between them."""
import gzip, io
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(r"C:\Claude\trading-backtester\snapshots")
def read(fp, name):
    return pd.read_csv(io.BytesIO(gzip.decompress((ROOT / fp / "data" / "raw" / f"{name}.gz").read_bytes())))
for name in ("etfs_long.csv", "etfs.csv", "VIX.csv"):
    a, b = read("4e1f98996cd13f8f", name), read("c4713b15d633ad4c", name)
    print(name, "rows", len(a), "->", len(b))
    if name == "VIX.csv":
        a.columns = b.columns = [c.strip().upper() for c in a.columns]
        m = a.merge(b, on="DATE", how="outer", suffixes=("_a", "_b"), indicator=True)
        print("  only in one:", m["_merge"].value_counts().to_dict())
        diff = m[(m["_merge"] == "both") & (np.abs(m["CLOSE_a"] - m["CLOSE_b"]) > 1e-9)]
        print("  changed closes:", len(diff), diff.tail(3).to_string(index=False) if len(diff) else "")
        continue
    key = ["date", "ticker"]
    m = a.merge(b, on=key, how="outer", suffixes=("_a", "_b"), indicator=True)
    print("  only in one:", m["_merge"].value_counts().to_dict())
    both = m[m["_merge"] == "both"]
    for col in ("open", "high", "low", "close", "volume"):
        rel = np.abs(both[f"{col}_b"] / both[f"{col}_a"] - 1)
        n = int((rel > 1e-7).sum())
        if n:
            w = both.loc[rel.idxmax()]
            print(f"  {col}: {n} rows changed, largest relative change {rel.max():.2e} ({w['ticker']} {w['date']})")
            if col == "close":
                ch = both[rel > 1e-7]
                print("   changed rows by ticker:", ch.groupby("ticker").size().to_dict(), "date range", ch["date"].min(), ch["date"].max())
                # Is it a uniform rescale (dividend adjustment) per ticker?
                for t, g in ch.groupby("ticker"):
                    r = (g["close_b"] / g["close_a"])
                    print(f"   {t}: ratio min {r.min():.8f} max {r.max():.8f}")
```

### independent.py

```python
"""Independent re-implementation (no backtester imports) of the indicators, event-study excess and the trade
rules, checked against the 2026-11-18 recorded runs; then exit-timing, cost and parameter-sensitivity probes.

Read-only. Data: the kept snapshot c4713b15d633ad4c (data through 2026-11-13). Development period only
(2010-01-01 on) for every probe that is not a reproduction of an already recorded number. 1993-2009 is not
looked at for any new variant.
"""
import gzip
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Claude\trading-backtester")
SNAP = REPO / "snapshots" / "c4713b15d633ad4c" / "data" / "raw"
DEV_START = pd.Timestamp("2010-01-01")


def load(symbol):
    t = pd.read_csv(io.BytesIO(gzip.decompress((SNAP / "etfs_long.csv.gz").read_bytes())), parse_dates=["date"])
    if symbol not in set(t["ticker"]):
        t = pd.read_csv(io.BytesIO(gzip.decompress((SNAP / "etfs.csv.gz").read_bytes())), parse_dates=["date"])
    return t[t.ticker == symbol].set_index("date")[["open", "high", "low", "close", "volume"]].astype(float).sort_index()


def wilder_rsi(close, n):
    """Classic Wilder RSI: seed with the simple mean of the first n changes, then recursive smoothing."""
    c = close.to_numpy()
    out = np.full(len(c), np.nan)
    ch = np.diff(c)
    if len(ch) < n:
        return pd.Series(out, index=close.index)
    g, l = np.clip(ch, 0, None), np.clip(-ch, 0, None)
    ag, al = g[:n].mean(), l[:n].mean()
    out[n] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n, len(ch)):
        ag = (ag * (n - 1) + g[i]) / n
        al = (al * (n - 1) + l[i]) / n
        out[i + 1] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return pd.Series(out, index=close.index)


def boll_lower(close, n=20, k=2.0):
    m = close.rolling(n).mean()
    s = close.rolling(n).apply(lambda x: np.sqrt(np.mean((x - x.mean()) ** 2)), raw=True)
    return m - k * s


def signal(frame, name, **kw):
    c = frame["close"]
    if name == "rsi2_below_10":
        return wilder_rsi(c, 2) < kw.get("level", 10)
    if name == "rsi14_below_30":
        return wilder_rsi(c, kw.get("n", 14)) < kw.get("level", 30)
    if name == "bollinger_lower_close":
        return c < boll_lower(c, kw.get("n", 20), kw.get("k", 2.0))
    raise KeyError(name)


def exit_pos(frame, p, rule, sma_n=5, cap=10, hold=5):
    c = frame["close"].to_numpy()
    if rule == "hold_5":
        return p + hold
    sma = pd.Series(c).rolling(sma_n).mean().to_numpy()
    for d in range(p + 1, min(p + cap, len(c) - 1) + 1):
        if c[d] > sma[d]:
            return d
    return p + cap


def trades(frame, sig, rule, start=DEV_START, **kw):
    inside = (frame.index >= start)
    flags = sig.fillna(False).to_numpy(bool) & inside
    out, busy = [], -1
    for p in np.flatnonzero(flags):
        if p <= busy:
            continue
        e = exit_pos(frame, p, rule, **kw)
        if e >= len(frame) or not inside[e]:
            continue
        out.append((p, e))
        busy = e
    return out


def price(frame, tr, entry="close", exit_at="close"):
    o, c = frame["open"].to_numpy(), frame["close"].to_numpy()
    rows = []
    for p, e in tr:
        ep = o[p + 1] if entry == "next_open" else c[p]
        if exit_at == "next_open":  # sell at the open after the exit-signal close (no same-close decision)
            if e + 1 >= len(c):
                continue
            xp = o[e + 1]
        else:
            xp = c[e]
        rows.append({"signal_day": frame.index[p], "exit_day": frame.index[e], "sessions": e - p, "entry_price": ep,
                     "exit_price": xp, "gross": xp / ep - 1})
    return pd.DataFrame(rows)


def baseline(frame, lengths, entry="close", start=DEV_START):
    """Mean gross return of every possible same-length trade inside the period (as Lead v2 defines it)."""
    o, c = frame["open"].to_numpy(), frame["close"].to_numpy()
    inside = np.flatnonzero(frame.index >= start)
    out = {}
    for L in np.unique(lengths):
        s = inside[inside + L <= inside.max()]
        ep = o[s + 1] if entry == "next_open" else c[s]
        out[L] = float((c[s + L] / ep - 1).mean())
    return np.array([out[L] for L in lengths])


report = {}
# 1. Reproduce study numbers (development) for the oversold family.
recs = [json.loads(l) for l in (REPO / "trials.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
studies_rec = [r for r in recs if r.get("kind") != "trade_simulation"][-1]
print("== Study reproduction (development, close entry): mine vs recorded excess, bp")
worst = 0.0
for sym in ("SPY", "QQQ", "IWM"):
    f = load(sym)
    for name in ("rsi2_below_10", "rsi14_below_30", "bollinger_lower_close"):
        sig = signal(f, name)
        for h in (1, 5, 10):
            fwd = f["close"].shift(-h) / f["close"] - 1
            valid = (f.index >= DEV_START) & fwd.notna().to_numpy()
            s = sig.fillna(False).to_numpy(bool) & valid
            excess = fwd[s].mean() - fwd[valid].mean()
            rec = next(t for t in studies_rec["tests"] if t["study"] == name and t["symbol"] == sym and t["horizon"] == h)
            worst = max(worst, abs(excess - rec["dev_excess"]) * 1e4)
            print(f"  {sym} {name:22} h{h:<2} n={int(s.sum()):4}  {excess * 1e4:+8.2f}  vs {rec['dev_excess'] * 1e4:+8.2f}")
print(f"  largest difference: {worst:.4f} bp")

# 2. Reproduce the trade list (development, all 12 strategies x 2 ETF entries) against the recorded CSV.
csv = pd.read_csv(REPO / "exports" / "trades" / "2026-11-18-002751-trade-simulation.csv", parse_dates=["signal_day", "entry_day", "exit_day"])
print("\n== Trade-list reproduction (development): trades, mean gross; mine vs CSV")
mismatch = 0
for sym in ("SPY", "QQQ"):
    f = load(sym)
    for name in ("rsi2_below_10", "rsi14_below_30", "bollinger_lower_close"):
        sig = signal(f, name)
        for rule in ("hold_5", "close_above_sma5"):
            tr = trades(f, sig, rule)
            for entry, mode in (("close", "etf_close"), ("next_open", "etf_next_open")):
                mine = price(f, tr, entry)
                theirs = csv[(csv.symbol == sym) & (csv.signal == name) & (csv.exit == rule) & (csv.pricing == mode) & (csv.period == "development")]
                same_days = (len(mine) == len(theirs) and (mine["signal_day"].to_numpy() == theirs["signal_day"].to_numpy()).all()
                             and (mine["exit_day"].to_numpy() == theirs["exit_day"].to_numpy()).all())
                diff = np.abs(mine["gross"].to_numpy() - theirs["gross"].to_numpy()).max() if same_days else np.nan
                mismatch += (not same_days) or diff > 2e-6
                print(f"  {sym} {name:22} {rule:16} {mode:13} {len(mine):4} vs {len(theirs):4}  "
                      f"{mine['gross'].mean() * 1e4:+7.1f} vs {theirs['gross'].mean() * 1e4:+7.1f} bp  same days: {same_days}  max |diff| {diff:.1e}")
print(f"  strategy-pricings that differ: {mismatch}")

# 3. Exit timing: the close_above_sma5 exit decides at a close and sells at that same close.
print("\n== Exit timing for close_above_sma5 (development): sell at the exit-signal close vs the next open")
timing = []
for sym in ("SPY", "QQQ"):
    f = load(sym)
    for name in ("rsi2_below_10", "rsi14_below_30", "bollinger_lower_close"):
        tr = trades(f, signal(f, name), "close_above_sma5")
        for entry in ("close", "next_open"):
            a, b = price(f, tr, entry, "close"), price(f, tr, entry, "next_open")
            base = baseline(f, a["sessions"].to_numpy(int), entry).mean()
            timing.append((sym, name, entry, len(a), a["gross"].mean(), b["gross"].mean()))
            print(f"  {sym} {name:22} entry {entry:9} n={len(a):3} exit at close {a['gross'].mean() * 1e4:+7.1f} bp, "
                  f"exit next open {b['gross'].mean() * 1e4:+7.1f} bp (difference {(b['gross'].mean() - a['gross'].mean()) * 1e4:+6.1f}); "
                  f"win rate {(a['gross'] > 0).mean():.0%} -> {(b['gross'] > 0).mean():.0%}")

# 4. Cost sensitivity for the two next-open Leads and the close-only QQQ RSI(2) Lead (development).
print("\n== Cost sensitivity (development, mean net per trade, bp, at round-trip costs of 2 / 5 / 10 / 20 bp)")
for sym, name, rule, entry in (("QQQ", "bollinger_lower_close", "close_above_sma5", "next_open"),
                               ("QQQ", "rsi14_below_30", "close_above_sma5", "next_open"),
                               ("QQQ", "rsi2_below_10", "close_above_sma5", "close"),
                               ("QQQ", "rsi2_below_10", "close_above_sma5", "next_open")):
    f = load(sym)
    pr = price(f, trades(f, signal(f, name), rule), entry)
    base = baseline(f, pr["sessions"].to_numpy(int), entry)
    nets = [((1 + pr["gross"]) * (1 - c / 1e4) - 1).mean() * 1e4 for c in (2, 5, 10, 20)]
    print(f"  {sym} {name:22} {rule} {entry:9} n={len(pr)}  net " + " / ".join(f"{x:+.1f}" for x in nets)
          + f"   (same-length baseline {base.mean() * 1e4:+.1f} bp)")

# 5. Year-by-year concentration for the two next-open Leads (development; from data the trade list already shows).
print("\n== By year (development, next-open entry, close_above_sma5 exit): trades and mean gross bp")
for name in ("bollinger_lower_close", "rsi14_below_30"):
    f = load("QQQ")
    pr = price(f, trades(f, signal(f, name), "close_above_sma5"), "next_open")
    by = pr.groupby(pr["signal_day"].dt.year)["gross"].agg(["count", "mean", "sum"])
    total = pr["gross"].sum()
    print(f"  QQQ {name}: " + ", ".join(f"{y}: {int(r['count'])} / {r['mean'] * 1e4:+.0f}" for y, r in by.iterrows()))
    top_years = (by["sum"] / total).sort_values(ascending=False).head(3)
    print("    share of summed gross from the best three years: " + ", ".join(f"{y} {s:.0%}" for y, s in top_years.items()))
    srt = np.sort(pr["gross"].to_numpy())[::-1]
    print(f"    without the best 3 trades: mean {srt[3:].mean() * 1e4:+.1f} bp (all {srt.mean() * 1e4:+.1f}); "
          f"median {np.median(srt) * 1e4:+.1f} bp; worst trade {srt[-1] * 1e4:+.0f} bp")

# 6. Overlap of the QQQ signals (development).
f = load("QQQ")
days = {n: set(f.index[(signal(f, n).fillna(False).to_numpy(bool)) & (f.index >= DEV_START)]) for n in
        ("rsi2_below_10", "rsi14_below_30", "bollinger_lower_close")}
print("\n== Signal-day overlap, QQQ development")
for a in days:
    for b in days:
        if a < b:
            inter = len(days[a] & days[b])
            print(f"  {a} & {b}: {inter} common days; {inter / len(days[a]):.0%} of {a} ({len(days[a])}), {inter / len(days[b]):.0%} of {b} ({len(days[b])})")
rs = days["rsi14_below_30"]
print(f"  RSI(14)<30 days that are also below the lower band or RSI(2)<10: {len(rs & (days['bollinger_lower_close'] | days['rsi2_below_10'])) / len(rs):.0%}")
```

### sensitivity.py

```python
"""Parameter-neighbourhood probe, DEVELOPMENT PERIOD ONLY (2010-01-01 to 2026-11-13). Exploratory: these variants are
not registered, must not be used to pick a new parameter, and 1993-2009 was not looked at for any of them.
Excess = mean gross minus the mean of every possible same-length trade in the period (Lead v2's baseline).
t = excess / (sd of per-trade excess / sqrt(n)), a rough guide only (trades cluster in sell-offs)."""
import numpy as np, pandas as pd
from lib import load, signal, trades, price, baseline, wilder_rsi, boll_lower, DEV_START

def row(f, sig, rule, entry, label, **kw):
    pr = price(f, trades(f, sig, rule, **kw), entry)
    if len(pr) < 5:
        return f"  {label:44} n={len(pr):3} (too few)"
    ex = pr["gross"].to_numpy() - baseline(f, pr["sessions"].to_numpy(int), entry)
    t = ex.mean() / (ex.std(ddof=1) / np.sqrt(len(ex)))
    return (f"  {label:44} n={len(pr):3}  mean {pr['gross'].mean()*1e4:+6.1f}  excess {ex.mean()*1e4:+6.1f} bp  t {t:4.1f}  "
            f"win {(pr['gross']>0).mean():.0%}  worst {pr['gross'].min()*1e4:+6.0f}")

q = load("QQQ"); s = load("SPY"); c = q["close"]
print("QQQ RSI(14) < level, close_above_sma5 exit, next-open entry")
for lv in (25, 27.5, 30, 32.5, 35):
    print(row(q, wilder_rsi(c, 14) < lv, "close_above_sma5", "next_open", f"RSI(14) < {lv}"))
for n in (10, 20):
    print(row(q, wilder_rsi(c, n) < 30, "close_above_sma5", "next_open", f"RSI({n}) < 30"))
print("QQQ close below the lower band (n, k), close_above_sma5 exit, next-open entry")
for n, k in ((20, 1.5), (20, 2.0), (20, 2.5), (15, 2.0), (30, 2.0)):
    print(row(q, c < boll_lower(c, n, k), "close_above_sma5", "next_open", f"Bollinger({n}, {k})"))
print("QQQ RSI(2) < level, close_above_sma5 exit, close entry")
for lv in (5, 10, 15, 20):
    print(row(q, wilder_rsi(c, 2) < lv, "close_above_sma5", "close", f"RSI(2) < {lv}"))
print("Exit neighbourhood for QQQ Bollinger(20, 2), next-open entry")
sig = c < boll_lower(c, 20, 2.0)
for sma_n, cap in ((3, 10), (5, 10), (10, 10), (5, 5), (5, 15)):
    print(row(q, sig, "close_above_sma5", "next_open", f"first close above SMA{sma_n}, cap {cap}", sma_n=sma_n, cap=cap))
for hold in (1, 3, 5, 10):
    print(row(q, sig, "hold_5", "next_open", f"hold {hold} sessions", hold=hold))
print("Same Bollinger(20, 2) rule and exit on SPY, next-open entry (the registered SPY row is 'No edge')")
print(row(s, s["close"] < boll_lower(s["close"], 20, 2.0), "close_above_sma5", "next_open", "SPY Bollinger(20, 2)"))
print(row(s, wilder_rsi(s["close"], 14) < 30, "close_above_sma5", "next_open", "SPY RSI(14) < 30"))
```

### calibration.py

```python
"""How often do the backtester's two tests pass a rule that has NO edge, on made-up prices whose volatility clusters
like an index's? Synthetic data only, so nothing real is looked at.

World: daily returns r_t = mu + sigma_t * z_t with GARCH(1,1) volatility (persistence ~0.98, the usual index fit),
constant mean, so no signal can predict returns. Signals are the real rules (RSI(2) < 10, RSI(14) < 30, close below
the lower Bollinger band), which fire mostly in volatile stretches.

1. Indicator-study test (study.evaluate): circular-shift p, two-sided; count p < 0.05 at h = 1 and h = 5.
2. Lead v2 test (lead_v2.excess_test): quarter-resampled p, one-sided; count p < 0.05 with positive excess,
   for the close_above_sma5 exit at the close.
Both are imported from the scratch copy of the backtester, unchanged.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCR / "bt_copy"))
from backtester import catalog, lead_v2, simulate, strategies, study  # noqa: E402

RULES = {s.name: s for s in catalog.STUDIES if s.name in ("rsi2_below_10", "rsi14_below_30", "bollinger_lower_close")}
EXIT = {e.name: e for e in strategies.EXITS}["close_above_sma5"]
CFG = {"costs_round_trip_bps": {"etf": 2, "kalshi_taker": 24, "kalshi_maker": 4}, "funding_bps_per_day": 1.37}


def garch_history(seed, days=4250, mu=0.0004, omega=2.0e-6, alpha=0.10, beta=0.88):
    rng = np.random.default_rng(seed)
    z = rng.standard_t(6, days) / np.sqrt(6 / 4)  # fat tails, unit variance
    var = omega / (1 - alpha - beta)
    r = np.empty(days)
    for t in range(days):
        r[t] = mu + np.sqrt(var) * z[t]
        var = omega + alpha * (r[t] - mu) ** 2 + beta * var
    close = 100 * np.cumprod(1 + r)
    opens = np.r_[100, close[:-1]] * (1 + rng.normal(0, 0.002, days))
    idx = pd.bdate_range("2010-01-04", periods=days)
    return pd.DataFrame({"open": opens, "high": np.maximum(opens, close) * 1.004, "low": np.minimum(opens, close) * 0.996,
                         "close": close, "volume": 1e6}, index=idx)


def homoskedastic_history(seed, days=4250, mu=0.0004, sd=0.011):
    rng = np.random.default_rng(seed)
    r = mu + sd * rng.standard_t(6, days) / np.sqrt(6 / 4)
    close = 100 * np.cumprod(1 + r)
    opens = np.r_[100, close[:-1]] * (1 + rng.normal(0, 0.002, days))
    return pd.DataFrame({"open": opens, "high": np.maximum(opens, close) * 1.004, "low": np.minimum(opens, close) * 0.996,
                         "close": close, "volume": 1e6}, index=pd.bdate_range("2010-01-04", periods=days))


def run(maker, worlds, label):
    hits = {(name, h): 0 for name in RULES for h in (1, 5)}
    v2_hits = {name: 0 for name in RULES}
    v2_judged = {name: 0 for name in RULES}
    for seed in range(worlds):
        frame = maker(seed)
        mask = pd.Series(frame.index >= frame.index[260], index=frame.index)  # skip the warm-up year
        for name, s in RULES.items():
            sig = s.rule(frame).fillna(False).astype(bool)
            for h in (1, 5):
                out = study.evaluate(sig, study.forward_return(frame, h), mask, h, 500, np.random.default_rng(seed * 7 + h))
                hits[(name, h)] += out.get("status") == "ok" and out["p"] < 0.05
            trades = simulate.find_trades(frame, sig, EXIT.rule, mask)
            priced = simulate.price_trades(frame, trades, "etf_close", CFG)
            if len(priced) >= 20:
                base = lead_v2.baseline(frame, mask, priced["sessions"].to_numpy(int), "etf_close")
                t = lead_v2.excess_test(priced, base, np.random.default_rng(seed), 1000)
                if t["quarters"] >= 8:
                    v2_judged[name] += 1
                    v2_hits[name] += t["p"] < 0.05 and t["mean_excess"] > 0
    print(f"\n{label}: {worlds} zero-edge histories of about 17 years")
    for (name, h), k in hits.items():
        print(f"  study test  {name:22} h={h}: p < 0.05 in {k / worlds:.1%} (two-sided; 5% expected)")
    for name in RULES:
        j = v2_judged[name]
        print(f"  Lead v2 test {name:22} close_above_sma5: p < 0.05 and excess > 0 in {v2_hits[name] / max(j, 1):.1%} of {j} judged "
              f"(one-sided; 5% expected)")


if __name__ == "__main__":
    worlds = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    run(homoskedastic_history, worlds, "Constant volatility (control)")
    run(garch_history, worlds, "Clustered volatility (GARCH 0.10/0.88, t(6) shocks)")
```

### forward_power.py

```python
"""(1) How many forward trades would it take to tell the Leads' development edge from zero? (2) The Leads as an
overlay on a held QQQ position versus simply holding more QQQ. Development period only (2010-01-01 to 2026-11-13)."""
import numpy as np, pandas as pd
from lib import load, signal, trades, price, baseline, DEV_START
q = load("QQQ")
years = (q.index[-1] - DEV_START).days / 365.25
for name, rule, entry in (("bollinger_lower_close", "close_above_sma5", "next_open"), ("rsi14_below_30", "close_above_sma5", "next_open"),
                          ("rsi2_below_10", "close_above_sma5", "close")):
    tr = trades(q, signal(q, name), rule)
    pr = price(q, tr, entry)
    ex = pr["gross"].to_numpy() - baseline(q, pr["sessions"].to_numpy(int), entry)
    m, sd = ex.mean(), ex.std(ddof=1)
    per_year = len(pr) / years
    # trades needed for a one-sided 5% test with 80% power if the true edge equals the development mean
    n80 = ((1.645 + 0.842) * sd / m) ** 2
    # trades needed before a mean excess of zero or worse would sit 2 standard errors below the development mean
    n_reject = (2 * sd / m) ** 2
    print(f"QQQ {name:22} {entry:9}: {len(pr)} trades ({per_year:.1f}/yr); mean excess {m*1e4:+.0f} bp, sd {sd*1e4:.0f} bp; "
          f"80% power needs ~{n80:.0f} trades (~{n80/per_year:.0f} years); a zero-edge forward record sits 2 se below "
          f"the development mean after ~{n_reject:.0f} trades (~{n_reject/per_year:.0f} years)")
# Overlay: hold QQQ 1x always, add 1x more while a rule's trade is open (cash/borrowing at 0).
r = q["close"].pct_change().fillna(0.0)
dev = q.index >= DEV_START
def stats(x):
    x = x[dev]
    eq = (1 + x).cumprod(); dd = (eq / eq.cummax().clip(lower=1) - 1).min()
    yrs = len(x) / 252; cagr = eq.iloc[-1] ** (1 / yrs) - 1
    return f"CAGR {cagr:+.2%}, vol {x.std()*np.sqrt(252):.1%}, Sharpe(rf=0) {x.mean()/x.std()*np.sqrt(252):.2f}, max DD {dd:.1%}"
print("\nQQQ held 1x:                    ", stats(r))
for name in ("bollinger_lower_close", "rsi14_below_30"):
    tr = trades(q, signal(q, name), "close_above_sma5")
    extra = np.zeros(len(q))
    o, c = q["open"].to_numpy(), q["close"].to_numpy()
    for p, e in tr:
        for d in range(p + 1, e + 1):
            extra[d] = c[d] / o[d] - 1 if d == p + 1 else c[d] / c[d - 1] - 1  # next-open entry
    extra = pd.Series(extra, index=q.index)
    held = (extra != 0)[dev].mean()
    print(f"QQQ 1x + 1x more during {name:22}", stats(r + extra), f"(average exposure {1 + held:.3f}x)")
    print(f"QQQ held at that average exposure  ", stats(r * (1 + held)))
```

### excursions.py

```python
"""Maximum adverse and favourable excursion per trade from daily highs and lows (development, 2010 on).
Next-open entry: the entry day's whole range comes after the open, so it counts. Close entry: from the next day.
The exit day counts up to its close (its high and low may come before the close, which is when the trade is
still open)."""
import numpy as np, pandas as pd
from lib import load, signal, trades
q, s = load("QQQ"), load("SPY")
for sym, f, name, entry in (("QQQ", q, "bollinger_lower_close", "next_open"), ("QQQ", q, "rsi14_below_30", "next_open"),
                            ("QQQ", q, "rsi2_below_10", "close"), ("SPY", s, "bollinger_lower_close", "next_open")):
    o, h, l, c = (f[k].to_numpy() for k in ("open", "high", "low", "close"))
    mae, mfe, gross = [], [], []
    for p, e in trades(f, signal(f, name), "close_above_sma5"):
        ep = o[p + 1] if entry == "next_open" else c[p]
        first = p + 1
        mae.append(l[first:e + 1].min() / ep - 1)
        mfe.append(h[first:e + 1].max() / ep - 1)
        gross.append(c[e] / ep - 1)
    mae, mfe, gross = map(np.array, (mae, mfe, gross))
    pct = lambda x, k: np.percentile(x, k) * 100
    print(f"{sym} {name:22} {entry:9} n={len(mae):3}  MAE median {pct(mae,50):+.2f}%  10th pct {pct(mae,10):+.2f}%  worst {mae.min()*100:+.2f}%  "
          f"| MFE median {pct(mfe,50):+.2f}%  | trades whose MAE < -5%: {(mae < -0.05).sum()}, < -10%: {(mae < -0.10).sum()}  "
          f"| winners that were first down >2%: {((gross > 0) & (mae < -0.02)).sum()}")
```

## A.4 RSI seed check (inline)

```python
import gzip, io
from pathlib import Path
import numpy as np, pandas as pd
SNAP = Path(r"C:\Claude\trading-backtester\snapshots\c4713b15d633ad4c\data\raw")
t = pd.read_csv(io.BytesIO(gzip.decompress((SNAP / "etfs.csv.gz").read_bytes())), parse_dates=["date"])
c = t[t.ticker == "IWM"].set_index("date")["close"].sort_index()
ch = c.diff(); n = 14  # the backtester's definition
g = ch.clip(lower=0).ewm(alpha=1/n, adjust=False, min_periods=n).mean()
l = (-ch.clip(upper=0)).ewm(alpha=1/n, adjust=False, min_periods=n).mean()
bt = (100 - 100/(1+g/l)).where(l != 0, 100.0).where(g.notna())
x = c.to_numpy(); d = np.diff(x); gg, ll = np.clip(d, 0, None), np.clip(-d, 0, None)  # classic Wilder
w = np.full(len(x), np.nan); ag, al = gg[:n].mean(), ll[:n].mean(); w[n] = 100-100/(1+ag/al)
for i in range(n, len(d)):
    ag = (ag*(n-1)+gg[i])/n; al = (al*(n-1)+ll[i])/n; w[i+1] = 100-100/(1+ag/al)
w = pd.Series(w, index=c.index)
a, b = bt < 30, w < 30
print([f"{x:%Y-%m-%d}" for x in a.index[(a != b) & bt.notna()]])
```
