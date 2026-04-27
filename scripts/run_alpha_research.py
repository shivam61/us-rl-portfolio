"""
Walk-forward IC evaluation for each feature family.

Usage:
    .venv/bin/python scripts/run_alpha_research.py \
        --config config/base.yaml \
        --universe config/universes/sp100.yaml

Output:
    artifacts/reports/feature_family_ic.csv
    artifacts/reports/feature_family_ic.md
"""
import argparse
import logging
import json
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Feature families ─────────────────────────────────────────────────────────

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
    train_years: int = 3,
    eval_start: str = "2016-01-01",
    eval_end: str = "2026-01-01",
) -> dict:
    """
    Annual walk-forward: train on `train_years` of data, predict on next year,
    compute Spearman IC per date, then aggregate.
    """
    available = [f for f in features if f in panel.columns]
    if not available:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "precision_at_20": np.nan, "top_bot_spread": np.nan}

    if label not in panel.columns:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "precision_at_20": np.nan, "top_bot_spread": np.nan}

    dates = panel.index.get_level_values("date").unique().sort_values()
    eval_dates = dates[(dates >= eval_start) & (dates < eval_end)]
    eval_years = sorted(set(d.year for d in eval_dates))

    all_ic: list[float] = []
    all_precision: list[float] = []
    all_spread: list[float] = []

    for year in eval_years:
        year_start = pd.Timestamp(f"{year}-01-01")
        year_end   = pd.Timestamp(f"{year+1}-01-01")
        train_start = pd.Timestamp(f"{year - train_years}-01-01")

        train_idx = (dates >= train_start) & (dates < year_start)
        eval_idx  = (dates >= year_start)  & (dates < year_end)

        train_dates = dates[train_idx]
        eval_dates_yr = dates[eval_idx]

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

        model = lgb.LGBMRegressor(n_estimators=50, num_leaves=31, n_jobs=-1, random_state=42, verbosity=-1)
        model.fit(X_train[mask_train], y_train[mask_train])
        preds = model.predict(X_eval[mask_eval])

        pred_series = pd.Series(preds, index=eval_panel[mask_eval].index, name="pred")
        actual = y_eval[mask_eval]

        # Per-date IC
        eval_panel_masked = eval_panel[mask_eval].copy()
        eval_panel_masked["pred"] = preds

        for date, grp in eval_panel_masked.groupby(level="date"):
            if len(grp) < 5:
                continue
            ic, _ = spearmanr(grp["pred"], grp[label])
            if not np.isnan(ic):
                all_ic.append(ic)

            # Precision@20: fraction of top-20 predicted that are in top quintile actual
            n = max(1, len(grp) // 5)
            top_pred = grp["pred"].nlargest(n).index
            top_actual_thresh = grp[label].quantile(0.8)
            precision = (grp.loc[top_pred, label] >= top_actual_thresh).mean()
            all_precision.append(precision)

            # Top-minus-bottom spread
            top_ret  = grp.loc[grp["pred"] >= grp["pred"].quantile(0.8), label].mean()
            bot_ret  = grp.loc[grp["pred"] <= grp["pred"].quantile(0.2), label].mean()
            all_spread.append(top_ret - bot_ret)

    if not all_ic:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "precision_at_20": np.nan, "top_bot_spread": np.nan}

    ic_arr = np.array(all_ic)
    return {
        "mean_ic":        float(np.mean(ic_arr)),
        "ic_sharpe":      float(np.mean(ic_arr) / (np.std(ic_arr) + 1e-9)),
        "precision_at_20": float(np.mean(all_precision)),
        "top_bot_spread": float(np.mean(all_spread)),
        "n_dates":        len(all_ic),
    }


def _eval_job(family: str, features: list[str], label: str, panel: pd.DataFrame) -> dict:
    logger.info(f"Evaluating family={family} label={label}")
    metrics = _eval_family(panel, features, label)
    return {"family": family, "label": label, **metrics}


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",   default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp100.yaml")
    parser.add_argument("--eval-start", default="2016-01-01")
    parser.add_argument("--eval-end",   default="2026-01-01")
    parser.add_argument("--train-years", type=int, default=3)
    args = parser.parse_args()

    base_config, universe_config = load_config(args.config, args.universe)
    sector_mapping = dict(universe_config.tickers)

    # ── Load data ────────────────────────────────────────────────────────────
    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = (
        list(universe_config.tickers.keys())
        + universe_config.sector_etfs
        + universe_config.macro_etfs
        + [universe_config.benchmark, universe_config.vix_proxy]
    )
    all_tickers = list(set(all_tickers))
    logger.info(f"Loading data for {len(all_tickers)} tickers...")
    data_dict = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)

    # ── Build features ───────────────────────────────────────────────────────
    logger.info("Building features...")
    fg = StockFeatureGenerator(data_dict, benchmark_ticker=universe_config.benchmark, sector_mapping=sector_mapping)
    features_panel = fg.generate()

    logger.info("Building labels...")
    tg = TargetGenerator(data_dict, forward_horizon=21, sector_mapping=sector_mapping)
    targets = tg.generate()

    panel = features_panel.join(targets, how="inner")
    logger.info(f"Panel: {panel.shape[1]} columns, {len(panel)} rows")

    # ── Parallel IC evaluation ───────────────────────────────────────────────
    jobs = [
        (family, features, label)
        for family, features in FEATURE_FAMILIES.items()
        for label in LABEL_COLS
    ]
    logger.info(f"Running {len(jobs)} IC evaluations in parallel...")
    results = Parallel(n_jobs=-1, backend="loky")(
        delayed(_eval_job)(family, features, label, panel)
        for family, features, label in jobs
    )

    # ── Save outputs ─────────────────────────────────────────────────────────
    out_dir = Path("artifacts/reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results).sort_values(["label", "ic_sharpe"], ascending=[True, False])
    df.to_csv(out_dir / "feature_family_ic.csv", index=False)

    # Markdown summary
    md_lines = ["# Feature Family IC Report\n"]
    for label in LABEL_COLS:
        md_lines.append(f"## Label: `{label}`\n")
        sub = df[df["label"] == label][["family", "mean_ic", "ic_sharpe", "precision_at_20", "top_bot_spread"]].copy()
        sub.columns = ["Family", "Mean IC", "IC Sharpe", "Precision@20", "Top-Bot Spread"]
        md_lines.append(sub.to_markdown(index=False, floatfmt=".4f"))
        md_lines.append("")

    md_lines.append("\n## Success Criteria\n")
    md_lines.append("| Metric | Current | Phase A target |")
    md_lines.append("|---|---|---|")
    md_lines.append("| Mean Rank IC | 0.033 | ≥ 0.040 |")
    md_lines.append("| IC Sharpe | 0.086 | ≥ 0.30 |")
    md_lines.append("| Top-bot spread | 0.19% | ≥ 0.40% |")
    md_lines.append("| Precision@20 | ~10% | ≥ 15% |")

    (out_dir / "feature_family_ic.md").write_text("\n".join(md_lines))

    logger.info(f"Saved: {out_dir}/feature_family_ic.csv")
    logger.info(f"Saved: {out_dir}/feature_family_ic.md")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
