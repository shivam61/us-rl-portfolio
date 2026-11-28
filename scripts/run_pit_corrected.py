"""Corrected-mask rerun of the B.5 picks test (membership-only mask, vol_top_20, equal weight, no costs).

Steps (run from the worktree root, in order):
    python scripts/run_pit_corrected.py make-configs
    python scripts/run_pit_corrected.py run --load 503        # variant A
    python scripts/run_pit_corrected.py run --load B          # variants B and D
    python scripts/run_pit_corrected.py run --load C          # variant C
    python scripts/run_pit_corrected.py run --load legacy     # sanity S0 (old run) and S1
    python scripts/run_pit_corrected.py run --load unconv     # sanity: B with unconverted Tier B
    python scripts/run_pit_corrected.py report

Each load is a separate feature build because the volatility score is ranked cross-sectionally over the
loaded universe. Holdout 2019-01-01..2026-04-24; training window 2008-01-01..2018-12-31.
Nothing is written under data/. The sealed 2026-05..11 rows are never used for selection or metrics
(base configs cap backtest.end_date at 2026-04-24).
"""
import argparse
import importlib.util
import json
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from run_phase_a7_trend_overlay import load_inputs  # noqa: E402
from run_phase_b2_turnover_control import build_vol_path_fast  # noqa: E402
from src.reporting.metrics import calculate_metrics  # noqa: E402

_spec = importlib.util.spec_from_file_location("build_sp500_pit_membership", ROOT / "scripts" / "build_sp500_pit_membership.py")
pit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pit)

FINAL = ROOT / "runs_final"
CFG = FINAL / "configs"
OUT = FINAL / "out"
LEGACY_DIR = Path("/Users/shivamgupta/github/us-rl-portfolio/.claude/worktrees/agent-ab416871969d08121/runs_pit")
COMP = Path("/private/tmp/claude-501/-Users-shivamgupta-github-us-rl-portfolio/5058cb96-5758-4d0d-bf44-39a776434699/scratchpad/membership/components_updated.csv")
WINDOWS = Path("/Users/shivamgupta/github/us-rl-portfolio/artifacts/reports/tierb_usable_windows.csv")
TIER_A = ["BF.B", "VEEV", "FDXF", "FLEX", "HONA"]
EXCLUDE_C = ["BWA", "BBWI", "JEF"]
# No cached price in either cache; the earlier run also got no data for them. Dropped so the loader never downloads.
NO_PRICE = ["BK", "CTRA"]
SEALED_CAP = "2026-04-24"
HOLD = (pd.Timestamp("2019-01-01"), pd.Timestamp("2026-04-24"))
TRAIN = (pd.Timestamp("2008-01-01"), pd.Timestamp("2018-12-31"))
SPY = "SPY"
TRADE_ETFS = ["SPY", "TLT", "GLD", "UUP"]


def tier_b_tickers() -> list[str]:
    w = pd.read_csv(WINDOWS, dtype=str).dropna(subset=["usable_start", "usable_end"])
    tickers = sorted(set(w["ticker"].str.strip()))
    files = sorted(p.stem for p in (ROOT / "data" / "raw_tierB" / "raw").glob("*.parquet"))
    assert tickers == files, f"windows tickers and Tier B files differ: {set(tickers) ^ set(files)}"
    return tickers


def make_configs() -> None:
    CFG.mkdir(parents=True, exist_ok=True)
    base = yaml.safe_load((LEGACY_DIR / "base_extended.yaml").read_text())
    base["backtest"]["end_date"] = SEALED_CAP
    variants = {
        "base_merged": "runs_final/merged_cache",
        "base_unconv": "runs_final/merged_cache_unconv",
        "base_legacy": str(LEGACY_DIR / "raw_extended"),
    }
    for name, cache in variants.items():
        cfg = yaml.safe_load(yaml.safe_dump(base))
        cfg["data"]["cache_dir"] = cache
        (CFG / f"{name}.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))

    u503 = yaml.safe_load((LEGACY_DIR / "sp500_baseline.yaml").read_text())
    u503["name"] = "sp500_503_final"
    for t in NO_PRICE:
        u503["tickers"].pop(t)
    (CFG / "universe_503.yaml").write_text(yaml.safe_dump(u503, sort_keys=False))

    tb = tier_b_tickers()
    uB = yaml.safe_load(yaml.safe_dump(u503))
    uB["name"] = "extended_B_final"
    for t in TIER_A + tb:
        uB["tickers"][t] = "Unknown"
    (CFG / "universe_B.yaml").write_text(yaml.safe_dump(uB, sort_keys=False))

    uC = yaml.safe_load(yaml.safe_dump(uB))
    uC["name"] = "extended_C_final"
    for t in EXCLUDE_C:
        uC["tickers"].pop(t)
    (CFG / "universe_C.yaml").write_text(yaml.safe_dump(uC, sort_keys=False))

    leg = yaml.safe_load((LEGACY_DIR / "sp500_extended.yaml").read_text())
    leg["name"] = "legacy_596"
    for t in NO_PRICE:
        leg["tickers"].pop(t, None)
    (CFG / "universe_legacy.yaml").write_text(yaml.safe_dump(leg, sort_keys=False))

    # Every ticker the loader needs must already be cached, so nothing downloads.
    for base_name, uni in [("base_merged", uB), ("base_unconv", uB), ("base_legacy", leg)]:
        cache = Path(variants[base_name]) if Path(variants[base_name]).is_absolute() else ROOT / variants[base_name]
        need = set(uni["tickers"]) | set(uni["sector_etfs"]) | set(uni["macro_etfs"]) | {uni["benchmark"], uni["vix_proxy"]}
        missing = sorted(t for t in need if not (cache / "raw" / f"{t}.parquet").exists())
        print(f"{base_name}: {len(need)} tickers needed, missing {missing[:10]} ({len(missing)})")
    print(f"Tier B tickers: {len(tb)}; universe_B {len(uB['tickers'])}; universe_C {len(uC['tickers'])}")


def _px_mask(mask_gated: pd.DataFrame, index: pd.DatetimeIndex, columns, universe: set) -> pd.DataFrame:
    m = mask_gated.reindex(index=index, method="ffill").reindex(columns=columns, fill_value=False).fillna(False).astype(bool)
    outside = [c for c in columns if c not in universe]
    m.loc[:, outside] = False
    return m


def _snapshot_legacy_mask(index: pd.DatetimeIndex, columns) -> pd.DataFrame:
    snaps = pit.load_snapshots(COMP)
    return pit.build_mask(snaps, index, columns)


def window_metrics(sel: dict, px: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    ds = sorted(d for d in sel if start <= d <= end)
    spy = px[SPY]
    rets, spy_rets, overlaps = [], [], []
    for d0, d1 in zip(ds[:-1], ds[1:]):
        held = sel[d0]
        r = (px.loc[d1, held] / px.loc[d0, held] - 1).replace([np.inf, -np.inf], np.nan)
        rets.append(r.mean())
        spy_rets.append(spy.loc[d1] / spy.loc[d0] - 1)
        overlaps.append(len(set(sel[d0]) & set(sel[d1])))
    rets = pd.Series(rets, index=ds[1:], dtype=float)
    spy_rets = pd.Series(spy_rets, index=ds[1:], dtype=float)
    nav = pd.Series(np.r_[1.0, (1 + rets).cumprod().to_numpy()], index=ds)
    spy_nav = pd.Series(np.r_[1.0, (1 + spy_rets).cumprod().to_numpy()], index=ds)
    years = (ds[-1] - ds[0]).days / 365.25
    ppy = len(rets) / years
    m = calculate_metrics(nav, periods_per_year=ppy)
    ms = calculate_metrics(spy_nav, periods_per_year=ppy)
    return dict(
        start=str(start.date()),
        end=str(end.date()),
        first_control=str(ds[0].date()),
        last_control=str(ds[-1].date()),
        control_dates=len(ds),
        years=round(years, 3),
        mean_names_held=round(float(np.mean([len(sel[d]) for d in ds])), 2),
        mean_overlap_names=round(float(np.mean(overlaps)), 2),
        cum_return=round(float(m["Total Return"]), 4),
        cagr=round(float(m["CAGR"]), 4),
        vol=round(float(m["Volatility"]), 4),
        sharpe=round(float(m["Sharpe"]), 3),
        max_drawdown=round(float(m["Max Drawdown"]), 4),
        spy_cum_return=round(float(ms["Total Return"]), 4),
        spy_cagr=round(float(ms["CAGR"]), 4),
        spy_vol=round(float(ms["Volatility"]), 4),
        spy_sharpe=round(float(ms["Sharpe"]), 3),
        spy_max_drawdown=round(float(ms["Max Drawdown"]), 4),
    )


def run_variant(name: str, inputs: dict, mask: pd.DataFrame, px: pd.DataFrame, universe: set) -> dict:
    inputs["pit_mask"] = mask
    sel = build_vol_path_fast(inputs, None)["selected"]
    with open(OUT / f"{name}_sel.pkl", "wb") as fh:
        pickle.dump(sel, fh)
    res = dict(
        variant=name,
        universe_size=len(universe),
        holdout=window_metrics(sel, px, *HOLD),
        train=window_metrics(sel, px, *TRAIN),
    )
    picks_all = [t for d in sel for t in sel[d]]
    res["distinct_names_picked"] = len(set(picks_all))
    print(name, json.dumps({k: v for k, v in res.items() if k in ("holdout", "train")}, default=str)[:600])
    return res


def load_universe(base_name: str, universe_name: str):
    base = str(CFG / f"{base_name}.yaml")
    uni = str(CFG / f"{universe_name}.yaml")
    inputs = load_inputs(base, uni, TRADE_ETFS)
    px = inputs["prices"].astype(float)
    universe = set(inputs["universe_config"].tickers.keys())
    return inputs, px, universe


def run_load(load: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gated = pd.read_parquet(FINAL / "pit_mask_corrected.parquet")
    tb = tier_b_tickers()
    results = {}
    if load == "503":
        inputs, px, uni = load_universe("base_merged", "universe_503")
        m = _px_mask(gated, px.index, px.columns, uni)
        results["A"] = run_variant("A", inputs, m, px, uni)
    elif load == "B":
        inputs, px, uni = load_universe("base_merged", "universe_B")
        m = _px_mask(gated, px.index, px.columns, uni)
        results["B"] = run_variant("B", inputs, m, px, uni)
        m_d = m.copy()
        pre = m_d.index < pd.Timestamp("2019-01-01")
        cols = [t for t in tb if t in m_d.columns]
        m_d.loc[pre, cols] = False
        results["D"] = run_variant("D", inputs, m_d, px, uni)
        # Rank-pool control: same 501-name mask as A, but the B universe is loaded, so Tier A/B names
        # still enter the cross-sectional percentile ranks. A_pool minus A isolates the pool effect.
        base503 = set(yaml.safe_load((CFG / "universe_503.yaml").read_text())["tickers"])
        m_a = m.copy()
        m_a.loc[:, [c for c in m_a.columns if c not in base503]] = False
        results["A_pool"] = run_variant("A_pool", inputs, m_a, px, uni)
    elif load == "C":
        inputs, px, uni = load_universe("base_merged", "universe_C")
        m = _px_mask(gated, px.index, px.columns, uni)
        results["C"] = run_variant("C", inputs, m, px, uni)
    elif load == "legacy":
        inputs, px, uni = load_universe("base_legacy", "universe_legacy")
        legacy_m = _snapshot_legacy_mask(px.index, px.columns)
        legacy_m.loc[:, [c for c in px.columns if c not in uni]] = False
        results["S0"] = run_variant("S0_legacy_old_mask", inputs, legacy_m, px, uni)
        m = _px_mask(gated, px.index, px.columns, uni)
        results["S1"] = run_variant("S1_legacy_corrected_mask", inputs, m, px, uni)
    elif load == "unconv":
        inputs, px, uni = load_universe("base_unconv", "universe_B")
        m = _px_mask(gated, px.index, px.columns, uni)
        results["Sunc"] = run_variant("Sunc_B_unconverted", inputs, m, px, uni)
    else:
        raise SystemExit(f"unknown load {load}")
    (OUT / f"results_{load}.json").write_text(json.dumps(results, indent=1, default=str))


def picks_and_checks(sel: dict, windows: pd.DataFrame, tier_b: list[str]) -> dict:
    allowed = {}
    for ticker, grp in windows.groupby("ticker"):
        allowed[ticker] = list(zip(grp["window_start"], grp["window_end"]))
    violations = []
    counts_all, counts_hold = {}, {}
    for d, names in sel.items():
        for t in names:
            if t in allowed:
                counts_all[t] = counts_all.get(t, 0) + 1
                if HOLD[0] <= d <= HOLD[1]:
                    counts_hold[t] = counts_hold.get(t, 0) + 1
                if not any(a <= d <= b for a, b in allowed[t]):
                    violations.append((str(d.date()), t))
    top_all = sorted(counts_all.items(), key=lambda x: (-x[1], x[0]))[:10]
    top_hold = sorted(counts_hold.items(), key=lambda x: (-x[1], x[0]))[:10]
    return dict(
        tierb_names_picked_all=len(counts_all),
        tierb_pick_count_all=sum(counts_all.values()),
        tierb_pick_count_holdout=sum(counts_hold.values()),
        top10_all=top_all,
        top10_holdout=top_hold,
        violations_outside_window=violations,
    )


def report() -> None:
    results = {}
    for f in sorted(OUT.glob("results_*.json")):
        results.update(json.loads(f.read_text()))
    windows = pit.load_tierb_windows(WINDOWS)
    tb = tier_b_tickers()
    rows = []
    for k, v in results.items():
        for period in ("holdout", "train"):
            r = v[period]
            rows.append(dict(variant=k, period=period, universe=v["universe_size"], **{kk: vv for kk, vv in r.items()}))
    table = pd.DataFrame(rows)
    table.to_csv(FINAL / "variant_metrics.csv", index=False)
    pd.set_option("display.width", 250)
    print(table[["variant", "period", "universe", "first_control", "last_control", "control_dates", "mean_names_held",
                 "mean_overlap_names", "cum_return", "cagr", "sharpe", "max_drawdown", "spy_cum_return", "spy_cagr",
                 "spy_sharpe", "spy_max_drawdown"]].to_string(index=False))

    picks = {}
    for name in ["A", "A_pool", "B", "C", "D", "S0_legacy_old_mask", "S1_legacy_corrected_mask", "Sunc_B_unconverted"]:
        p = OUT / f"{name}_sel.pkl"
        if not p.exists():
            continue
        sel = pickle.loads(p.read_bytes())
        picks[name] = picks_and_checks(sel, windows, tb)
    (FINAL / "picks_summary.json").write_text(json.dumps(picks, indent=1, default=str))
    for name, info in picks.items():
        print(name, "tierB picks:", info["tierb_pick_count_all"], "names:", info["tierb_names_picked_all"],
              "violations:", len(info["violations_outside_window"]))
        print("  top10 all:", info["top10_all"])
        print("  top10 holdout:", info["top10_holdout"])

    # coverage by year on the corrected (ungated) mask, plus snapshot-only legacy figures from the builder run
    ung = pd.read_parquet(FINAL / "pit_mask_ungated.parquet")
    pres = pd.read_parquet(FINAL / "pit_price_presence.parquet").reindex(index=ung.index, columns=ung.columns, fill_value=False)
    cov = []
    for y in (2008, 2012, 2016, 2020, 2024):
        d = ung.index[ung.index.year == y][-1]
        members = int(ung.loc[d].sum())
        priced = int((ung.loc[d] & pres.loc[d]).sum())
        cov.append(dict(year=y, date=str(d.date()), members=members, priced=priced, coverage=round(priced / members, 3)))
    cov = pd.DataFrame(cov)
    cov.to_csv(FINAL / "coverage_by_year.csv", index=False)
    print(cov.to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("make-configs")
    r = sub.add_parser("run")
    r.add_argument("--load", required=True)
    sub.add_parser("report")
    args = ap.parse_args()
    if args.cmd == "make-configs":
        make_configs()
    elif args.cmd == "run":
        run_load(args.load)
    else:
        report()


if __name__ == "__main__":
    main()
