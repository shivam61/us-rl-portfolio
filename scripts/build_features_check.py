"""Feature check for ingested Tier B names (on-the-fly features, nothing persisted for them).

Features are not cached per name: scripts/build_features.py writes data/features/*.parquet for
the sp500_dynamic universe only, and load_inputs in run_phase_a7_trend_overlay.py regenerates
features from the price cache. This script does the same regeneration with:
  - an extended universe copy (runs_ingest/feature_check/universe_extended.yaml, Tier B names
    added with sector 'Unknown'),
  - a merged cache of symlinks (data/raw + data/raw_tierB/raw) under runs_ingest/, so nothing is
    written into data/raw.
and a baseline run on the unextended universe over the same cache minus Tier B.

Checks:
  1. feature columns identical between baseline and extended runs (feature count equal);
  2. baseline names' feature values unchanged when Tier B names are added;
  3. every Tier B name has non-null features after warm-up (252 trading days from its first row);
  4. the volatility score frame has values for each Tier B name on membership control dates.

Usage: .venv/bin/python scripts/build_features_check.py [--tiers runs_ingest/tiers.csv]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.alpha.volatility_score import compute_volatility_score_frame  # noqa: E402
from src.config.loader import load_config  # noqa: E402
from src.data.ingestion import DataIngestion  # noqa: E402
from src.features.stock_features import StockFeatureGenerator  # noqa: E402

WARMUP_ROWS = 252


def _main_data_root() -> Path:
    """data/ lives in the main checkout; the worktree links it (see docs/runbooks)."""
    return REPO / "data"


def write_universes(base_universe: Path, out_dir: Path, extra: list[str], drop: list[str]) -> tuple[Path, Path]:
    cfg = yaml.safe_load(base_universe.read_text())
    cfg["tickers"] = {t: s for t, s in cfg["tickers"].items() if t not in drop}
    base_out = out_dir / "universe_baseline.yaml"
    ext = dict(cfg)
    ext["name"] = f"{cfg['name']}_tierB"
    ext["description"] = cfg.get("description", "") + " + Tier B free-source names (sector Unknown)"
    ext["tickers"] = {**cfg["tickers"], **{t: "Unknown" for t in extra}}
    ext_out = out_dir / "universe_extended.yaml"
    base_out.write_text(yaml.safe_dump(cfg, sort_keys=False))
    ext_out.write_text(yaml.safe_dump(ext, sort_keys=False))
    return base_out, ext_out


def build_cache(cache_root: Path, tickers: list[str], sources: list[Path]) -> None:
    raw = cache_root / "raw"
    if raw.exists():
        shutil.rmtree(raw)
    raw.mkdir(parents=True)
    missing = []
    for t in tickers:
        for src in sources:
            p = src / f"{t}.parquet"
            if p.exists():
                (raw / f"{t}.parquet").symlink_to(p.resolve())
                break
        else:
            missing.append(t)
    if missing:
        raise SystemExit(f"no cache file for {len(missing)} tickers, e.g. {missing[:5]}")


def generate(universe_path: Path, cache_root: Path, base_config) -> dict:
    _, uni = load_config(str(base_config), str(universe_path))
    ingestion = DataIngestion(cache_dir=str(cache_root), force_download=False,
                              fundamental_provider="simulated")
    tickers = sorted(set(list(uni.tickers.keys()) + uni.sector_etfs + uni.macro_etfs
                         + [uni.benchmark, uni.vix_proxy]))
    data_dict = ingestion.fetch_universe_data(tickers=tickers, start_date=base_config_start(base_config))
    feats = StockFeatureGenerator(data_dict, benchmark_ticker=uni.benchmark,
                                  sector_mapping=dict(uni.tickers)).generate()
    return {"features": feats, "universe": uni, "n_tickers": len(tickers)}


def base_config_start(base_config: Path) -> str:
    cfg, _ = load_config(str(base_config), str(REPO / "config" / "universes" / "sp500.yaml"))
    return cfg.backtest.start_date


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tiers", type=Path, default=REPO / "runs_ingest" / "tiers.csv")
    ap.add_argument("--tierb-raw", type=Path, default=_main_data_root() / "raw_tierB" / "raw")
    ap.add_argument("--main-raw", type=Path, default=_main_data_root() / "raw")
    ap.add_argument("--membership-mask", type=Path,
                    default=_main_data_root() / "artifacts" / "sp500_pit_membership_mask.parquet")
    ap.add_argument("--base-config", type=Path, default=REPO / "config" / "base.yaml")
    ap.add_argument("--universe", type=Path, default=REPO / "config" / "universes" / "sp500.yaml")
    ap.add_argument("--work", type=Path, default=REPO / "runs_ingest" / "feature_check")
    args = ap.parse_args()

    work = args.work
    work.mkdir(parents=True, exist_ok=True)
    tiers = pd.read_csv(args.tiers)
    tier_b = sorted(tiers.loc[tiers.tier == "B", "ticker"].tolist())
    src_cfg = yaml.safe_load(args.universe.read_text())
    all_base = sorted(set(list(src_cfg["tickers"].keys()) + src_cfg["sector_etfs"] + src_cfg["macro_etfs"]
                          + [src_cfg["benchmark"], src_cfg["vix_proxy"]]))
    # Universe names without a price file in the cache cannot be regenerated offline; drop them
    # from both runs so the comparison stays like-for-like (they would otherwise be downloaded).
    drop = [t for t in all_base if not (args.main_raw / f"{t}.parquet").exists()]
    base_uni, ext_uni = write_universes(args.universe, work, tier_b, drop)
    base_names = sorted(t for t in all_base if t not in drop)
    print(f"dropped universe names without cache file: {drop}")

    base_cache = work / "cache_baseline"
    ext_cache = work / "cache_extended"
    build_cache(base_cache, base_names, [args.main_raw])
    build_cache(ext_cache, sorted(set(base_names + tier_b)), [args.main_raw, args.tierb_raw])

    print(f"baseline universe: {len(base_names)} tickers; Tier B names: {len(tier_b)}")
    base_run = generate(base_uni, base_cache, args.base_config)
    base_feats = base_run["features"]
    ext_run = generate(ext_uni, ext_cache, args.base_config)
    ext_feats = ext_run["features"]

    checks = {}
    checks["feature_count_baseline"] = int(base_feats.shape[1])
    checks["feature_count_extended"] = int(ext_feats.shape[1])
    checks["feature_columns_equal"] = list(base_feats.columns) == list(ext_feats.columns)

    base_tick = base_feats.index.get_level_values("ticker").unique()
    same_base = ext_feats.loc[ext_feats.index.get_level_values("ticker").isin(base_tick)]
    common_idx = base_feats.index.intersection(same_base.index)
    a = base_feats.loc[common_idx]
    b = same_base.loc[common_idx, base_feats.columns]
    # liquidity_rank is a per-date percentile across the whole universe, so adding names moves it
    # by design. Every other column is per-name or grouped by sector ('Unknown' is its own group).
    cross_sectional = {"liquidity_rank"}
    changed = {}
    changed_by_year: dict[str, dict[str, int]] = {}
    years = common_idx.get_level_values("date").year
    for col in base_feats.columns:
        x = a[col].to_numpy(dtype=float)
        y = b[col].to_numpy(dtype=float)
        same = np.isclose(x, y, rtol=1e-9, atol=1e-12, equal_nan=True)
        if not same.all():
            changed[col] = int((~same).sum())
            changed_by_year[col] = {str(int(yr)): int(n) for yr, n in
                                    pd.Series(~same).groupby(np.asarray(years)).sum().items() if n}
    checks["baseline_columns_changed"] = changed
    checks["baseline_columns_changed_by_year"] = changed_by_year
    checks["baseline_calendar_start"] = str(base_feats.index.get_level_values("date").min().date())
    checks["extended_calendar_start"] = str(ext_feats.index.get_level_values("date").min().date())
    late = years >= 2010
    checks["baseline_changed_rows_2010_on_excl_cross_sectional"] = {
        col: int((~np.isclose(a[col].to_numpy(dtype=float)[late], b[col].to_numpy(dtype=float)[late],
                              rtol=1e-9, atol=1e-12, equal_nan=True)).sum())
        for col in base_feats.columns if col not in cross_sectional
    }
    checks["baseline_values_unchanged_excl_cross_sectional"] = not (set(changed) - cross_sectional)
    # Tier B names start in 1990, so the panel calendar (and row-based warm-up) moves for 2006-2007.
    # Strict test from 2008 on, after the extended calendar's warm-up window has passed.
    late08 = years >= 2008
    checks["baseline_values_unchanged_from_2008_excl_cross_sectional"] = all(
        int((~np.isclose(a[c].to_numpy(dtype=float)[late08], b[c].to_numpy(dtype=float)[late08],
                         rtol=1e-9, atol=1e-12, equal_nan=True)).sum()) == 0
        for c in base_feats.columns if c not in cross_sectional)
    checks["baseline_rows_compared"] = int(len(common_idx))
    checks["dropped_universe_names_no_cache"] = drop

    per_name = []
    ext_tick = ext_feats.index.get_level_values("ticker")
    for t in tier_b:
        sub = ext_feats.loc[ext_tick == t]
        if sub.empty:
            per_name.append({"ticker": t, "rows": 0, "features_ok": False})
            continue
        dates = sub.index.get_level_values("date")
        first_row = dates.min()
        post = sub[dates >= sub.index.get_level_values("date").sort_values()[min(WARMUP_ROWS, len(sub) - 1)]]
        nonnull = post.notna().all(axis=1) if post.shape[1] else pd.Series(dtype=bool)
        feat_dates = post.index.get_level_values("date")[post.notna().any(axis=1).to_numpy()]
        per_name.append({
            "ticker": t, "rows": int(len(sub)), "first_row": str(first_row.date()),
            "features_nonnull_after_warmup": bool(post.notna().any(axis=1).any()) if len(post) else False,
            "fully_nonnull_share_after_warmup": round(float(nonnull.mean()), 4) if len(nonnull) else 0.0,
            "feature_first": str(feat_dates.min().date()) if len(feat_dates) else None,
            "feature_last": str(feat_dates.max().date()) if len(feat_dates) else None,
        })
    checks["tierb_names_with_features"] = int(sum(1 for r in per_name if r.get("features_nonnull_after_warmup")))
    firsts = [r["feature_first"] for r in per_name if r.get("feature_first")]
    lasts = [r["feature_last"] for r in per_name if r.get("feature_last")]
    checks["tierb_feature_date_range"] = [min(firsts), max(lasts)] if firsts else None

    vol = compute_volatility_score_frame(ext_feats)
    mask = pd.read_parquet(args.membership_mask)
    mask.index = pd.DatetimeIndex(mask.index)
    month_ends = mask.groupby(mask.index.to_period("M")).tail(1).index
    vol_ticker = vol.index.get_level_values("ticker")
    vol_date = vol.index.get_level_values("date")
    vol_rows = []
    for t in tier_b:
        member_dates = mask.index[mask[t].fillna(False).astype(bool).to_numpy()] if t in mask.columns else pd.DatetimeIndex([])
        control = [d for d in month_ends if d in set(member_dates) and d.year >= 2008]
        sel = vol.loc[(vol_ticker == t) & vol_date.isin(control)]
        has = sel["volatility_score"].notna()
        vol_rows.append({"ticker": t, "control_dates": len(control),
                         "control_dates_with_vol_score": int(has.sum()) if len(sel) else 0})
    names_with_vol = sum(1 for r in vol_rows if r["control_dates_with_vol_score"] > 0)
    checks["tierb_names_with_vol_score_on_control_dates"] = names_with_vol
    checks["tierb_names_total"] = len(tier_b)

    out = {"checks": checks, "per_name_features": per_name, "per_name_vol": vol_rows}
    (work / "feature_check.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(checks, indent=1))
    bad = [r["ticker"] for r in per_name if not r.get("features_nonnull_after_warmup")]
    print("tier B names without features after warm-up:", bad)


if __name__ == "__main__":
    main()
