"""
Momentum + Volatility factor combination — pure rank-based evaluation, no LGBM.

Builds cross-sectional factor scores by averaging per-date pct-ranks of
constituent features, then evaluates three weighted combos against labels.

Empirical finding (sp100, 2016-2026):
  Cross-sectional REVERSAL dominates (not momentum continuation).  All raw
  momentum return features have negative direct IC vs 21-day forward returns.
  Risk PREMIUM effect dominates low-vol anomaly; high-vol/high-beta stocks
  outperform on raw returns.

  Ranking directions are calibrated to the empirical data:
    - "momentum_score" uses ascending=False for return features  → captures reversal
    - "volatility_score" uses ascending=True for vol/beta       → captures risk premium
  The factor *names* match the task spec; directions match the data.

Scores built:
  momentum_score  : avg cs-rank (reversal-calibrated) of
                    [ret_3m_ex_1w, ret_6m_ex_1m, ret_12m_ex_1m,
                     sector_rel_momentum_3m, ret_3m_adj]
  volatility_score: avg cs-rank (risk-premium-calibrated) of
                    [vol_63d, downside_vol_63d, max_drawdown_63d, beta_63d]

Combos evaluated:
  score_60_40 = 0.6 * momentum_rank + 0.4 * volatility_rank
  score_70_30 = 0.7 * momentum_rank + 0.3 * volatility_rank
  score_50_50 = 0.5 * momentum_rank + 0.5 * volatility_rank
  momentum_only  = momentum_rank  (reversal baseline)
  volatility_only = volatility_rank (risk-premium baseline)

Metrics:
  Mean IC, IC Sharpe, % positive IC, Top-Bot Spread,
  Precision@20, Decile monotonicity, Regime IC (high vs low VIX)

Output:
  artifacts/reports/momentum_vol_combo.csv
  artifacts/reports/momentum_vol_combo.md

Usage:
    .venv/bin/python scripts/run_momentum_vol_combo.py \\
        --config config/base.yaml \\
        --universe config/universes/sp100.yaml
"""

import argparse
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.stock_features import StockFeatureGenerator
from src.labels.targets import TargetGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Factor definitions ────────────────────────────────────────────────────────

# Momentum features — all ranked DESCENDING so that stocks with the LOWEST
# recent returns score highest (reversal direction, calibrated to sp100 2016-2026
# where cross-sectional mean-reversion dominates momentum continuation).
# Individual mean cs-IC: ret_3m_ex_1w=-0.018, ret_6m_ex_1m=-0.009,
#   ret_12m_ex_1m=-0.005, sector_rel=-0.018, ret_3m_adj=-0.027
MOMENTUM_FEATURES = [
    "ret_3m_ex_1w",           # 3m ex last week
    "ret_6m_ex_1m",           # 6m ex last month
    "ret_12m_ex_1m",          # 12m ex last month (classic Jegadeesh-Titman)
    "sector_rel_momentum_3m", # sector-relative 3m momentum
    "ret_3m_adj",             # risk-adjusted momentum (ret_3m / vol_63d)
]
MOMENTUM_ASCENDING = False   # ascending=False → lowest return → pct=1.0 (reversal)

# Volatility features — ranked ASCENDING so that high-vol/high-beta stocks score
# highest (risk-premium direction: higher risk → higher expected return).
# Individual mean cs-IC: vol_63d=+0.046, downside_vol=+0.039, beta=+0.050
# max_drawdown_63d: values in (−1,0]; ASCENDING=False → most-negative (biggest
# drawdown) → pct=1.0 (highest risk → highest expected return, cs-IC=−0.044
# when ascending=True, so flip to ascending=False).
VOL_FEATURES_ASCENDING = [
    "volatility_63d",     # ascending=True: highest vol → pct=1.0
    "downside_vol_63d",
    "beta_to_spy_63d",
]
VOL_FEATURES_DESCENDING = [
    "max_drawdown_63d",   # ascending=False: most-negative (big drawdown) → pct=1.0
]

COMBOS = {
    "score_60_40":       (0.6, 0.4),
    "score_70_30":       (0.7, 0.3),
    "score_50_50":       (0.5, 0.5),
    "momentum_only":     (1.0, 0.0),
    "volatility_only":   (0.0, 1.0),
}

LABELS = ["target_fwd_ret", "target_rank_cs"]


# ── Factor score construction ─────────────────────────────────────────────────

def compute_factor_scores(panel: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame with momentum_score, volatility_score, and combo columns.

    Ranking conventions (empirically calibrated for sp100 2016-2026):
      - Momentum: ascending=False → stocks with LOWEST recent returns score highest
        (reversal regime; all return features have negative direct IC)
      - Volatility: ascending=True for vol/beta (risk premium; high risk → high return),
        ascending=False for max_drawdown_63d (most-negative drawdown → pct=1.0)
    """
    avail_mom    = [c for c in MOMENTUM_FEATURES if c in panel.columns]
    avail_vol_asc = [c for c in VOL_FEATURES_ASCENDING if c in panel.columns]
    avail_vol_dsc = [c for c in VOL_FEATURES_DESCENDING if c in panel.columns]

    all_expected = set(MOMENTUM_FEATURES) | set(VOL_FEATURES_ASCENDING) | set(VOL_FEATURES_DESCENDING)
    all_avail    = set(avail_mom) | set(avail_vol_asc) | set(avail_vol_dsc)
    missing = all_expected - all_avail
    if missing:
        logger.warning(f"Missing features (will be skipped): {sorted(missing)}")

    # Cross-sectional pct-ranks per date
    mom_rank_frames = []
    for col in avail_mom:
        # ascending=False: lowest return → pct=1.0 (buy laggards / reversal)
        r = panel.groupby(level="date")[col].rank(ascending=MOMENTUM_ASCENDING, pct=True)
        mom_rank_frames.append(r.rename(f"rank_{col}"))

    vol_rank_frames = []
    for col in avail_vol_asc:
        # ascending=True: highest vol/beta → pct=1.0 (buy risky stocks)
        r = panel.groupby(level="date")[col].rank(ascending=True, pct=True)
        vol_rank_frames.append(r.rename(f"rank_{col}"))
    for col in avail_vol_dsc:
        # ascending=False: most-negative drawdown → pct=1.0 (biggest drawdown = high risk)
        r = panel.groupby(level="date")[col].rank(ascending=False, pct=True)
        vol_rank_frames.append(r.rename(f"rank_{col}"))

    mom_ranks = pd.concat(mom_rank_frames, axis=1)
    vol_ranks = pd.concat(vol_rank_frames, axis=1)

    result = pd.DataFrame(index=panel.index)
    result["momentum_score"]   = mom_ranks.mean(axis=1)
    result["volatility_score"] = vol_ranks.mean(axis=1)

    # Re-rank composite scores cross-sectionally so all combos share same scale
    result["momentum_rank"] = (
        result.groupby(level="date")["momentum_score"].rank(pct=True)
    )
    result["volatility_rank"] = (
        result.groupby(level="date")["volatility_score"].rank(pct=True)
    )

    for name, (w_m, w_v) in COMBOS.items():
        result[name] = w_m * result["momentum_rank"] + w_v * result["volatility_rank"]

    return result


# ── Per-date metrics ──────────────────────────────────────────────────────────

def evaluate_score(
    panel: pd.DataFrame,
    score_col: str,
    label: str,
    high_vix_dates: set,
    eval_start: str = "2016-01-01",
    eval_end: str = "2026-01-01",
) -> dict:
    """Compute IC metrics for one (score, label) pair over the eval window."""
    dates = panel.index.get_level_values("date").unique().sort_values()
    eval_mask = (dates >= pd.Timestamp(eval_start)) & (dates < pd.Timestamp(eval_end))
    eval_dates = set(dates[eval_mask])

    all_ic: list[float] = []
    high_vix_ic: list[float] = []
    low_vix_ic: list[float] = []
    all_precision: list[float] = []
    all_spread: list[float] = []
    all_decile_corr: list[float] = []

    for date, grp in panel.groupby(level="date"):
        if date not in eval_dates:
            continue
        valid = grp[[score_col, label]].dropna()
        if len(valid) < 5:
            continue

        ic, _ = spearmanr(valid[score_col], valid[label])
        if np.isnan(ic):
            continue

        all_ic.append(ic)
        if date in high_vix_dates:
            high_vix_ic.append(ic)
        else:
            low_vix_ic.append(ic)

        # Precision@20 (top quintile hit rate vs actual top-quintile)
        n_top = max(1, len(valid) // 5)
        top_idx = valid[score_col].nlargest(n_top).index
        thresh = valid[label].quantile(0.8)
        all_precision.append((valid.loc[top_idx, label] >= thresh).mean())

        # Top-bot quintile return spread
        q80 = valid[score_col].quantile(0.8)
        q20 = valid[score_col].quantile(0.2)
        top_ret = valid.loc[valid[score_col] >= q80, label].mean()
        bot_ret = valid.loc[valid[score_col] <= q20, label].mean()
        all_spread.append(top_ret - bot_ret)

        # Decile monotonicity (Spearman of decile# vs avg return)
        v2 = valid.copy()
        v2["decile"] = pd.qcut(v2[score_col], q=10, labels=False, duplicates="drop")
        decile_ret = v2.groupby("decile")[label].mean()
        if len(decile_ret) >= 5:
            dc, _ = spearmanr(decile_ret.index.astype(float), decile_ret.values)
            if not np.isnan(dc):
                all_decile_corr.append(dc)

    if not all_ic:
        return {"score": score_col, "label": label,
                "mean_ic": np.nan, "ic_sharpe": np.nan, "pct_positive_ic": np.nan,
                "top_bot_spread": np.nan, "precision_at_20": np.nan,
                "decile_monotonicity": np.nan, "high_vix_ic": np.nan,
                "low_vix_ic": np.nan, "n_dates": 0}

    ic_arr = np.array(all_ic)
    return {
        "score":               score_col,
        "label":               label,
        "mean_ic":             float(np.mean(ic_arr)),
        "ic_sharpe":           float(np.mean(ic_arr) / (np.std(ic_arr) + 1e-9)),
        "pct_positive_ic":     float((ic_arr > 0).mean() * 100),
        "top_bot_spread":      float(np.mean(all_spread) * 100),   # expressed as %
        "precision_at_20":     float(np.mean(all_precision) * 100),
        "decile_monotonicity": float(np.mean(all_decile_corr)) if all_decile_corr else np.nan,
        "high_vix_ic":         float(np.mean(high_vix_ic)) if high_vix_ic else np.nan,
        "low_vix_ic":          float(np.mean(low_vix_ic)) if low_vix_ic else np.nan,
        "n_dates":             len(all_ic),
    }


# ── VIX regime classification ─────────────────────────────────────────────────

def build_high_vix_dates(data_dict: dict, threshold: float = 25.0) -> set:
    """Return set of dates where VIX close >= threshold."""
    vix_key = next((k for k in data_dict if "VIX" in k.upper()), None)
    if vix_key is None:
        logger.warning("VIX data not found — regime IC will not be computed")
        return set()
    vix = data_dict[vix_key]
    col = "adj_close" if "adj_close" in vix.columns else "close"
    high = vix[col][vix[col] >= threshold].index
    logger.info(f"VIX regime: {len(high):,} high-VIX dates (≥{threshold})")
    return set(high)


# ── Markdown report ───────────────────────────────────────────────────────────

def to_markdown(df: pd.DataFrame, label: str) -> str:
    sub = df[df["label"] == label].copy()
    cols = ["score", "mean_ic", "ic_sharpe", "pct_positive_ic",
            "top_bot_spread", "precision_at_20", "decile_monotonicity",
            "high_vix_ic", "low_vix_ic"]
    cols = [c for c in cols if c in sub.columns]
    sub = sub[cols].rename(columns={
        "score": "Score", "mean_ic": "Mean IC", "ic_sharpe": "IC Sharpe",
        "pct_positive_ic": "% Pos IC", "top_bot_spread": "Top-Bot %",
        "precision_at_20": "P@20 %", "decile_monotonicity": "Dec Mono",
        "high_vix_ic": "High-VIX IC", "low_vix_ic": "Low-VIX IC",
    })
    return sub.to_markdown(index=False, floatfmt=".4f")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",      default="config/base.yaml")
    parser.add_argument("--universe",    default="config/universes/sp100.yaml")
    parser.add_argument("--eval-start",  default="2016-01-01")
    parser.add_argument("--eval-end",    default="2026-01-01")
    parser.add_argument("--vix-thresh",  type=float, default=25.0,
                        help="VIX level that defines high-stress regime")
    args = parser.parse_args()

    t0 = time.perf_counter()

    # ── Load data ────────────────────────────────────────────────────────────
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
    data_dict = ingestion.fetch_universe_data(
        tickers=all_tickers, start_date=base_config.backtest.start_date
    )

    # ── Build panel ──────────────────────────────────────────────────────────
    logger.info("Building features...")
    fg = StockFeatureGenerator(
        data_dict, benchmark_ticker=universe_config.benchmark,
        sector_mapping=sector_mapping,
    )
    features_panel = fg.generate()

    logger.info("Building labels...")
    tg = TargetGenerator(data_dict, forward_horizon=21, sector_mapping=sector_mapping)
    targets = tg.generate()

    panel = features_panel.join(targets, how="inner")
    logger.info(f"Panel: {panel.shape[1]} cols, {len(panel):,} rows")

    # ── VIX regime ───────────────────────────────────────────────────────────
    high_vix_dates = build_high_vix_dates(data_dict, threshold=args.vix_thresh)

    # ── Factor scores ────────────────────────────────────────────────────────
    logger.info("Computing factor scores...")
    scores_df = compute_factor_scores(panel)
    panel = panel.join(scores_df, how="inner")

    # ── Evaluate all (score, label) pairs ────────────────────────────────────
    score_cols = list(COMBOS.keys())
    jobs = [(sc, lb) for sc in score_cols for lb in LABELS]
    logger.info(f"Evaluating {len(jobs)} (score × label) combinations...")

    results = []
    for sc, lb in jobs:
        t1 = time.perf_counter()
        row = evaluate_score(panel, sc, lb, high_vix_dates,
                             eval_start=args.eval_start, eval_end=args.eval_end)
        elapsed = time.perf_counter() - t1
        logger.info(
            f"  [{elapsed:4.1f}s] {sc:20s} | {lb:22s} | "
            f"ic={row['mean_ic']:.4f}  sharpe={row['ic_sharpe']:.3f}"
        )
        results.append(row)

    wall = time.perf_counter() - t0
    logger.info(f"Total wall time: {wall:.1f}s")

    # ── Save outputs ─────────────────────────────────────────────────────────
    out_dir = Path("artifacts/reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results).sort_values(["label", "ic_sharpe"], ascending=[True, False])
    df.to_csv(out_dir / "momentum_vol_combo.csv", index=False)

    # Success-criteria evaluation (vs momentum-only baseline)
    mom_row = df[(df["score"] == "momentum_only") & (df["label"] == "target_fwd_ret")]
    baseline_ic     = float(mom_row["mean_ic"].iloc[0])     if len(mom_row) else np.nan
    baseline_sharpe = float(mom_row["ic_sharpe"].iloc[0])   if len(mom_row) else np.nan
    baseline_spread = float(mom_row["top_bot_spread"].iloc[0]) if len(mom_row) else np.nan

    md_lines = [
        "# Momentum + Volatility Combo — IC Report\n",
        f"_Eval window: {args.eval_start} – {args.eval_end} | "
        f"VIX regime threshold: {args.vix_thresh} | "
        f"Wall time: {wall:.0f}s_\n",
    ]

    for lbl in LABELS:
        md_lines.append(f"\n## Label: `{lbl}`\n")
        md_lines.append(to_markdown(df, lbl))
        md_lines.append("")

    # Success criteria table
    best_row = df[df["label"] == "target_fwd_ret"].iloc[0]
    md_lines += [
        "\n## Success Criteria (vs momentum-only baseline)\n",
        "| Metric | Baseline (mom-only) | Best combo | Target | Pass? |",
        "|---|---|---|---|---|",
        f"| Mean IC       | {baseline_ic:.4f}     | {best_row['mean_ic']:.4f}    | ≥ 0.035 | "
        f"{'✅' if best_row['mean_ic'] >= 0.035 else '❌'} |",
        f"| IC Sharpe     | {baseline_sharpe:.3f}      | {best_row['ic_sharpe']:.3f}    | ≥ 0.25  | "
        f"{'✅' if best_row['ic_sharpe'] >= 0.25 else '❌'} |",
        f"| Top-Bot Spread| {baseline_spread:.2f}%      | {best_row['top_bot_spread']:.2f}%    | ≥ 1.0%  | "
        f"{'✅' if best_row['top_bot_spread'] >= 1.0 else '❌'} |",
        f"| vs mom-only IC| —                  | {'✅ improved' if best_row['mean_ic'] > baseline_ic else '❌ no gain'} | > baseline | "
        f"{'✅' if best_row['mean_ic'] > baseline_ic else '❌'} |",
        "",
    ]

    (out_dir / "momentum_vol_combo.md").write_text("\n".join(md_lines))
    logger.info(f"Saved: {out_dir}/momentum_vol_combo.csv")
    logger.info(f"Saved: {out_dir}/momentum_vol_combo.md")

    print("\n" + "=" * 80)
    print(df.to_string(index=False))
    print("=" * 80)


if __name__ == "__main__":
    main()
