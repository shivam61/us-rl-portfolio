"""
Walk-forward IC evaluation for each feature family.

Thread budget:  joblib_jobs × lgbm_threads <= total_cpus (32)
  sp100 default:  jobs=15, lgbm_threads=2  → 30 cores
  sp500 default:  jobs=4,  lgbm_threads=8  → 32 cores

Usage:
    .venv/bin/python scripts/run_alpha_research.py \
        --config config/base.yaml \
        --universe config/universes/sp100.yaml

    # override thread budget explicitly:
    .venv/bin/python scripts/run_alpha_research.py \
        --joblib-jobs 8 --lgbm-threads 4

    # benchmark three configs and compare runtimes:
    .venv/bin/python scripts/run_alpha_research.py --benchmark

Output:
    artifacts/reports/feature_family_ic.csv
    artifacts/reports/feature_family_ic.md
"""
# ── Thread env vars must be set before numpy / lightgbm are imported ─────────
import os
import sys

# Resolved after arg parsing in main(); placeholder keeps linters happy.
# Workers inherit these from the parent process (loky uses spawn).
def _apply_thread_env(n: int) -> None:
    for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[var] = str(n)
    os.environ["LGBM_N_JOBS"] = str(n)

# ─────────────────────────────────────────────────────────────────────────────
import argparse
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import spearmanr
import lightgbm as lgb

from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.stock_features import StockFeatureGenerator
from src.labels.targets import TargetGenerator
from src.utils.threading import TOTAL_CPUS, compute_thread_budget

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Feature families ──────────────────────────────────────────────────────────

FEATURE_FAMILIES = {
    "baseline": [
        "ret_1m", "ret_3m", "ret_6m", "ret_12m", "ret_12m_ex_1m",
        "above_50dma", "above_200dma", "ma_50_200_ratio", "price_to_52w_high",
        "volatility_21d", "volatility_63d", "downside_vol_63d",
        "max_drawdown_63d", "avg_dollar_volume_63d", "beta_to_spy_63d",
        "relative_strength_vs_spy_63d", "liquidity_rank",
    ],
    "reversal": [
        "ret_1w", "ret_2w", "ret_zscore_21d", "overextension_20dma",
        "rsi_proxy", "gap_overnight",
    ],
    "momentum": [
        "ret_3m_ex_1w", "ret_6m_ex_1m", "ret_3m_adj", "ret_6m_adj",
        "mom_stability_3m", "trend_consistency", "sector_rel_momentum_3m",
    ],
    "volatility": [
        "volatility_21d", "volatility_63d", "downside_vol_63d",
        "max_drawdown_63d", "beta_to_spy_63d",
    ],
    "all_new": [
        "ret_1w", "ret_2w", "ret_zscore_21d", "overextension_20dma",
        "rsi_proxy", "gap_overnight",
        "ret_3m_ex_1w", "ret_6m_ex_1m", "ret_3m_adj", "ret_6m_adj",
        "mom_stability_3m", "trend_consistency", "sector_rel_momentum_3m",
    ],
}

LABEL_COLS = ["target_fwd_ret", "target_rank_cs", "target_fwd_ret_sector_rel"]


# ── Walk-forward IC evaluation ────────────────────────────────────────────────

def _eval_family(
    panel: pd.DataFrame,
    features: list[str],
    label: str,
    lgbm_threads: int,
    train_years: int = 3,
    eval_start: str = "2016-01-01",
    eval_end: str = "2026-01-01",
) -> dict:
    available = [f for f in features if f in panel.columns]
    if not available or label not in panel.columns:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "precision_at_20": np.nan, "top_bot_spread": np.nan}

    dates = panel.index.get_level_values("date").unique().sort_values()
    eval_years = sorted({d.year for d in dates[(dates >= eval_start) & (dates < eval_end)]})

    all_ic: list[float] = []
    all_precision: list[float] = []
    all_spread: list[float] = []

    for year in eval_years:
        year_start  = pd.Timestamp(f"{year}-01-01")
        year_end    = pd.Timestamp(f"{year+1}-01-01")
        train_start = pd.Timestamp(f"{year - train_years}-01-01")

        train_dates   = dates[(dates >= train_start) & (dates < year_start)]
        eval_dates_yr = dates[(dates >= year_start)  & (dates < year_end)]

        if len(train_dates) < 50 or len(eval_dates_yr) < 10:
            continue

        train_panel = panel.loc[panel.index.get_level_values("date").isin(train_dates)]
        eval_panel  = panel.loc[panel.index.get_level_values("date").isin(eval_dates_yr)]

        X_train = train_panel[available].fillna(0)
        y_train = train_panel[label].fillna(0)
        X_eval  = eval_panel[available].fillna(0)
        y_eval  = eval_panel[label]

        mask_train = y_train.notna() & X_train.notna().all(axis=1)
        mask_eval  = y_eval.notna()  & X_eval.notna().all(axis=1)
        if mask_train.sum() < 30 or mask_eval.sum() < 10:
            continue

        model = lgb.LGBMRegressor(
            n_estimators=50, num_leaves=31,
            n_jobs=lgbm_threads,
            random_state=42, verbosity=-1,
        )
        model.fit(X_train[mask_train], y_train[mask_train])
        preds = model.predict(X_eval[mask_eval])

        eval_masked = eval_panel[mask_eval].copy()
        eval_masked["pred"] = preds

        for _, grp in eval_masked.groupby(level="date"):
            if len(grp) < 5:
                continue
            ic, _ = spearmanr(grp["pred"], grp[label])
            if not np.isnan(ic):
                all_ic.append(ic)

            n = max(1, len(grp) // 5)
            top_pred  = grp["pred"].nlargest(n).index
            thresh    = grp[label].quantile(0.8)
            all_precision.append((grp.loc[top_pred, label] >= thresh).mean())

            top_ret = grp.loc[grp["pred"] >= grp["pred"].quantile(0.8), label].mean()
            bot_ret = grp.loc[grp["pred"] <= grp["pred"].quantile(0.2), label].mean()
            all_spread.append(top_ret - bot_ret)

    if not all_ic:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "precision_at_20": np.nan, "top_bot_spread": np.nan}

    ic_arr = np.array(all_ic)
    return {
        "mean_ic":         float(np.mean(ic_arr)),
        "ic_sharpe":       float(np.mean(ic_arr) / (np.std(ic_arr) + 1e-9)),
        "precision_at_20": float(np.mean(all_precision)),
        "top_bot_spread":  float(np.mean(all_spread)),
        "n_dates":         len(all_ic),
    }


def _eval_job(
    family: str, features: list[str], label: str,
    panel: pd.DataFrame, lgbm_threads: int,
) -> dict:
    t0 = time.perf_counter()
    metrics = _eval_family(panel, features, label, lgbm_threads)
    elapsed = time.perf_counter() - t0
    logger.info(f"  [{elapsed:5.1f}s] family={family} label={label} ic={metrics.get('mean_ic', float('nan')):.4f}")
    return {"family": family, "label": label, **metrics}


# ── Benchmarking ──────────────────────────────────────────────────────────────

def _run_benchmark(panel: pd.DataFrame) -> None:
    """Compare three thread budget configs on a single (baseline, target_fwd_ret) job."""
    configs = [
        ("15j × 2t", 15, 2),
        (" 8j × 4t",  8, 4),
        (" 4j × 8t",  4, 8),
    ]
    print(f"\n{'Config':<12} {'wall_sec':>10} {'load_after':>12}")
    print("-" * 38)
    for label, jobs, threads in configs:
        _apply_thread_env(threads)
        t0 = time.perf_counter()
        Parallel(n_jobs=jobs, backend="loky")(
            delayed(_eval_job)("baseline", FEATURE_FAMILIES["baseline"], "target_fwd_ret", panel, threads)
            for _ in range(jobs)
        )
        elapsed = time.perf_counter() - t0
        load = os.getloadavg()[0]
        print(f"{label:<12} {elapsed:>10.1f} {load:>12.1f}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",       default="config/base.yaml")
    parser.add_argument("--universe",     default="config/universes/sp100.yaml")
    parser.add_argument("--eval-start",   default="2016-01-01")
    parser.add_argument("--eval-end",     default="2026-01-01")
    parser.add_argument("--train-years",  type=int, default=3)
    parser.add_argument("--joblib-jobs",  type=int, default=0,
                        help="Outer parallel jobs (0 = auto)")
    parser.add_argument("--lgbm-threads", type=int, default=0,
                        help="LightGBM threads per job (0 = auto)")
    parser.add_argument("--benchmark",    action="store_true",
                        help="Compare thread configs and exit")
    args = parser.parse_args()

    n_jobs = len(FEATURE_FAMILIES) * len(LABEL_COLS)  # 15

    # ── Resolve thread budget ────────────────────────────────────────────────
    if args.joblib_jobs and args.lgbm_threads:
        joblib_jobs   = args.joblib_jobs
        lgbm_threads  = args.lgbm_threads
    elif args.joblib_jobs:
        joblib_jobs   = args.joblib_jobs
        lgbm_threads  = max(1, TOTAL_CPUS // joblib_jobs)
    elif args.lgbm_threads:
        lgbm_threads  = args.lgbm_threads
        joblib_jobs   = max(1, TOTAL_CPUS // lgbm_threads)
    else:
        # Auto: prefer running all jobs simultaneously on small data
        joblib_jobs, lgbm_threads = compute_thread_budget(n_jobs, TOTAL_CPUS)

    product = joblib_jobs * lgbm_threads
    logger.info(
        f"Thread budget: {joblib_jobs} joblib jobs × {lgbm_threads} lgbm threads "
        f"= {product} / {TOTAL_CPUS} cores"
    )
    if product > TOTAL_CPUS:
        logger.warning(f"Budget {product} exceeds {TOTAL_CPUS} CPUs — consider reducing --joblib-jobs or --lgbm-threads")

    # Apply env vars before any parallel dispatch so loky workers inherit them
    _apply_thread_env(lgbm_threads)

    # ── Load data + build panel ──────────────────────────────────────────────
    base_config, universe_config = load_config(args.config, args.universe)
    sector_mapping = dict(universe_config.tickers)

    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(set(
        list(universe_config.tickers.keys())
        + universe_config.sector_etfs
        + universe_config.macro_etfs
        + [universe_config.benchmark, universe_config.vix_proxy]
    ))
    logger.info(f"Loading data for {len(all_tickers)} tickers...")
    data_dict = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)

    logger.info("Building features...")
    fg = StockFeatureGenerator(data_dict, benchmark_ticker=universe_config.benchmark, sector_mapping=sector_mapping)
    features_panel = fg.generate()

    logger.info("Building labels...")
    tg = TargetGenerator(data_dict, forward_horizon=21, sector_mapping=sector_mapping)
    targets = tg.generate()

    panel = features_panel.join(targets, how="inner")
    logger.info(f"Panel: {panel.shape[1]} columns, {len(panel):,} rows")

    if args.benchmark:
        _run_benchmark(panel)
        return

    # ── Parallel IC evaluation ───────────────────────────────────────────────
    jobs = [
        (family, features, label)
        for family, features in FEATURE_FAMILIES.items()
        for label in LABEL_COLS
    ]
    logger.info(f"Running {len(jobs)} IC evaluations (joblib_jobs={joblib_jobs}, lgbm_threads={lgbm_threads})...")

    t_start = time.perf_counter()
    results = Parallel(n_jobs=joblib_jobs, backend="loky")(
        delayed(_eval_job)(family, features, label, panel, lgbm_threads)
        for family, features, label in jobs
    )
    wall = time.perf_counter() - t_start
    logger.info(f"IC eval complete in {wall:.1f}s (load avg: {os.getloadavg()[0]:.1f})")

    # ── Save outputs ─────────────────────────────────────────────────────────
    out_dir = Path("artifacts/reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results).sort_values(["label", "ic_sharpe"], ascending=[True, False])
    df.to_csv(out_dir / "feature_family_ic.csv", index=False)

    md_lines = ["# Feature Family IC Report\n"]
    for lbl in LABEL_COLS:
        md_lines.append(f"## Label: `{lbl}`\n")
        sub = df[df["label"] == lbl][["family", "mean_ic", "ic_sharpe", "precision_at_20", "top_bot_spread"]].copy()
        sub.columns = ["Family", "Mean IC", "IC Sharpe", "Precision@20", "Top-Bot Spread"]
        md_lines.append(sub.to_markdown(index=False, floatfmt=".4f"))
        md_lines.append("")

    md_lines += [
        "\n## Success Criteria\n",
        "| Metric | Current | Phase A target |",
        "|---|---|---|",
        "| Mean Rank IC | 0.033 | ≥ 0.040 |",
        "| IC Sharpe | 0.086 | ≥ 0.30 |",
        "| Top-bot spread | 0.19% | ≥ 0.40% |",
        "| Precision@20 | ~10% | ≥ 15% |",
        f"\n_Run: {len(jobs)} jobs, {joblib_jobs}×{lgbm_threads} thread budget, {wall:.0f}s wall time_",
    ]

    (out_dir / "feature_family_ic.md").write_text("\n".join(md_lines))
    logger.info(f"Saved: {out_dir}/feature_family_ic.csv")
    logger.info(f"Saved: {out_dir}/feature_family_ic.md")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
