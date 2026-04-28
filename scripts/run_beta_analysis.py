"""
Beta decomposition for momentum+vol factor scores.

For each score (volatility_only, score_50_50, momentum_only), this script:

  1. Forms long-only (top quintile) and long-short (top minus bottom quintile)
     portfolios at monthly frequency (non-overlapping 21-day periods).

  2. Regresses portfolio returns against SPY returns to extract:
       alpha (Jensen's alpha), beta, R², t-stats

  3. Computes:
       - average beta of selected stocks (from beta_to_spy_63d feature)
       - rolling 12-month beta and alpha (12-period windows of monthly data)
       - beta vs return scatter data

  4. Answers: "Is the signal just loading on market beta?"

Output:
    artifacts/reports/beta_analysis.md
    artifacts/reports/beta_vs_return.csv

Usage:
    .venv/bin/python scripts/run_beta_analysis.py \\
        --config config/base.yaml \\
        --universe config/universes/sp100.yaml
"""

import argparse
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.stock_features import StockFeatureGenerator
from src.labels.targets import TargetGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Factor definitions (mirrored from run_momentum_vol_combo.py) ──────────────

MOMENTUM_FEATURES = [
    "ret_3m_ex_1w", "ret_6m_ex_1m", "ret_12m_ex_1m",
    "sector_rel_momentum_3m", "ret_3m_adj",
]
MOMENTUM_ASCENDING = False  # reversal-calibrated

VOL_FEATURES_ASCENDING  = ["volatility_63d", "downside_vol_63d", "beta_to_spy_63d"]
VOL_FEATURES_DESCENDING = ["max_drawdown_63d"]

COMBOS = {
    "score_50_50":     (0.5, 0.5),
    "momentum_only":   (1.0, 0.0),
    "volatility_only": (0.0, 1.0),
}

SCORES = list(COMBOS.keys())


# ── OLS helpers (no statsmodels dependency) ───────────────────────────────────

def _ols(y: np.ndarray, x: np.ndarray) -> dict:
    """OLS of y on [1, x]. Returns alpha, beta, R², t-stats, annualised alpha."""
    mask = ~(np.isnan(y) | np.isnan(x))
    y, x = y[mask], x[mask]
    n = len(y)
    if n < 6:
        nan = float("nan")
        return dict(alpha=nan, beta=nan, r2=nan, t_alpha=nan, t_beta=nan,
                    alpha_ann=nan, n=n)

    X = np.column_stack([np.ones(n), x])
    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    alpha, beta = coeffs

    y_hat = X @ coeffs
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    mse = ss_res / max(n - 2, 1)
    cov_inv = np.linalg.inv(X.T @ X) if np.linalg.det(X.T @ X) != 0 else None
    if cov_inv is not None:
        se = np.sqrt(mse * np.diag(cov_inv))
        t_alpha = alpha / se[0] if se[0] > 0 else float("nan")
        t_beta  = beta  / se[1] if se[1] > 0 else float("nan")
    else:
        t_alpha = t_beta = float("nan")

    # Annualise: each period is 21 trading days ≈ 1 month
    alpha_ann = alpha * (252 / 21)

    return dict(alpha=alpha, beta=beta, r2=r2,
                t_alpha=t_alpha, t_beta=t_beta,
                alpha_ann=alpha_ann, n=n)


# ── Factor score construction (same logic as run_momentum_vol_combo.py) ───────

def compute_factor_scores(panel: pd.DataFrame) -> pd.DataFrame:
    avail_mom     = [c for c in MOMENTUM_FEATURES if c in panel.columns]
    avail_vol_asc = [c for c in VOL_FEATURES_ASCENDING if c in panel.columns]
    avail_vol_dsc = [c for c in VOL_FEATURES_DESCENDING if c in panel.columns]

    mom_frames = [
        panel.groupby(level="date")[c].rank(ascending=MOMENTUM_ASCENDING, pct=True).rename(f"r_{c}")
        for c in avail_mom
    ]
    vol_frames = [
        panel.groupby(level="date")[c].rank(ascending=True,  pct=True).rename(f"r_{c}")
        for c in avail_vol_asc
    ] + [
        panel.groupby(level="date")[c].rank(ascending=False, pct=True).rename(f"r_{c}")
        for c in avail_vol_dsc
    ]

    result = pd.DataFrame(index=panel.index)
    result["momentum_score"]   = pd.concat(mom_frames, axis=1).mean(axis=1)
    result["volatility_score"] = pd.concat(vol_frames, axis=1).mean(axis=1)

    result["momentum_rank"]  = result.groupby(level="date")["momentum_score"].rank(pct=True)
    result["volatility_rank"] = result.groupby(level="date")["volatility_score"].rank(pct=True)

    for name, (wm, wv) in COMBOS.items():
        result[name] = wm * result["momentum_rank"] + wv * result["volatility_rank"]

    return result


# ── SPY forward return helper ─────────────────────────────────────────────────

def build_spy_fwd_ret(data_dict: dict, horizon: int = 21) -> pd.Series:
    """Series of SPY horizon-day forward returns indexed by date."""
    spy_key = next((k for k in data_dict if k in ("SPY", "spy")), None)
    if spy_key is None:
        logger.warning("SPY not found in data_dict")
        return pd.Series(dtype=float)
    close = data_dict[spy_key]["adj_close"]
    return (close.shift(-horizon) / close - 1.0).rename("spy_fwd_ret")


# ── Portfolio construction ────────────────────────────────────────────────────

def build_portfolio_series(
    panel: pd.DataFrame,
    score_col: str,
    spy_fwd: pd.Series,
    eval_start: str,
    eval_end: str,
    rebal_every: int = 21,   # non-overlapping periods
    q_high: float = 0.8,
    q_low:  float = 0.2,
) -> pd.DataFrame:
    """
    Monthly (non-overlapping) portfolio returns.

    Returns DataFrame indexed by date with columns:
      long_ret, short_ret, ls_ret, spy_ret,
      long_beta, short_beta, ls_beta,
      long_alpha, ls_alpha, n_long, n_short
    """
    dates = panel.index.get_level_values("date").unique().sort_values()
    eval_mask = (dates >= pd.Timestamp(eval_start)) & (dates < pd.Timestamp(eval_end))
    eval_dates = dates[eval_mask]

    # Sample every rebal_every trading days for non-overlapping periods
    rebal_dates = eval_dates[::rebal_every]

    rows = []
    for date in rebal_dates:
        try:
            grp = panel.xs(date, level="date")
        except KeyError:
            continue

        cols_needed = [score_col, "target_fwd_ret", "beta_to_spy_63d"]
        valid = grp[cols_needed].dropna()
        if len(valid) < 8:
            continue

        q80 = valid[score_col].quantile(q_high)
        q20 = valid[score_col].quantile(q_low)
        long_s  = valid[valid[score_col] >= q80]
        short_s = valid[valid[score_col] <= q20]

        long_ret  = float(long_s["target_fwd_ret"].mean())
        short_ret = float(short_s["target_fwd_ret"].mean())
        spy_ret   = float(spy_fwd.get(date, np.nan))

        long_beta  = float(long_s["beta_to_spy_63d"].mean())
        short_beta = float(short_s["beta_to_spy_63d"].mean())

        long_alpha = long_ret - long_beta * spy_ret if not np.isnan(spy_ret) else np.nan
        ls_ret     = long_ret - short_ret
        ls_beta    = long_beta - short_beta
        ls_alpha   = ls_ret - ls_beta * spy_ret if not np.isnan(spy_ret) else np.nan

        rows.append(dict(
            date=date,
            long_ret=long_ret, short_ret=short_ret,
            ls_ret=ls_ret, spy_ret=spy_ret,
            long_beta=long_beta, short_beta=short_beta, ls_beta=ls_beta,
            long_alpha=long_alpha, ls_alpha=ls_alpha,
            n_long=len(long_s), n_short=len(short_s),
        ))

    df = pd.DataFrame(rows).set_index("date")
    logger.info(f"  {score_col}: {len(df)} monthly observations")
    return df


# ── Rolling beta/alpha ────────────────────────────────────────────────────────

def add_rolling_stats(port: pd.DataFrame, window: int = 12) -> pd.DataFrame:
    """Append rolling-window OLS beta and alpha columns."""
    roll_betas, roll_alphas = [], []
    for i in range(len(port)):
        start = max(0, i - window + 1)
        sub = port.iloc[start : i + 1].dropna(subset=["ls_ret", "spy_ret"])
        if len(sub) < max(4, window // 2):
            roll_betas.append(np.nan)
            roll_alphas.append(np.nan)
        else:
            res = _ols(sub["ls_ret"].values, sub["spy_ret"].values)
            roll_betas.append(res["beta"])
            roll_alphas.append(res["alpha_ann"])
    port[f"roll_{window}m_beta"]  = roll_betas
    port[f"roll_{window}m_alpha"] = roll_alphas
    return port


# ── Markdown helpers ──────────────────────────────────────────────────────────

def _fmt(v, fmt=".4f"):
    return f"{v:{fmt}}" if not np.isnan(v) else "—"


def regression_table(results: dict) -> str:
    """Single summary table for all score × portfolio_type combinations."""
    headers = ["Score", "Portfolio", "Alpha (ann%)", "Beta", "R²",
               "t(α)", "t(β)", "Avg Long β", "N"]
    rows = []
    for sc, d in results.items():
        for ptype in ("long_only", "long_short"):
            r = d[ptype]
            avg_beta = d.get("long_avg_beta" if ptype == "long_only" else "ls_avg_beta", np.nan)
            rows.append([
                sc, ptype.replace("_", "-"),
                f"{r['alpha_ann']*100:.2f}%",
                _fmt(r["beta"], ".3f"),
                _fmt(r["r2"], ".3f"),
                _fmt(r["t_alpha"], ".2f"),
                _fmt(r["t_beta"], ".2f"),
                _fmt(avg_beta, ".3f"),
                str(r["n"]),
            ])

    col_w = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
    sep = "|" + "|".join("-" * (w + 2) for w in col_w) + "|"
    hdr = "|" + "|".join(f" {h:{w}s} " for h, w in zip(headers, col_w)) + "|"
    lines = [hdr, sep]
    for row in rows:
        lines.append("|" + "|".join(f" {v:{w}s} " for v, w in zip(row, col_w)) + "|")
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",     default="config/base.yaml")
    parser.add_argument("--universe",   default="config/universes/sp100.yaml")
    parser.add_argument("--eval-start", default="2016-01-01")
    parser.add_argument("--eval-end",   default="2026-01-01")
    args = parser.parse_args()

    t0 = time.perf_counter()

    # ── Load data ────────────────────────────────────────────────────────────
    base_config, universe_config = load_config(args.config, args.universe)
    sector_mapping = dict(universe_config.tickers)

    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(set(
        list(universe_config.tickers.keys())
        + universe_config.sector_etfs + universe_config.macro_etfs
        + [universe_config.benchmark, universe_config.vix_proxy]
    ))
    data_dict = ingestion.fetch_universe_data(
        tickers=all_tickers, start_date=base_config.backtest.start_date
    )

    fg = StockFeatureGenerator(
        data_dict, benchmark_ticker=universe_config.benchmark,
        sector_mapping=sector_mapping,
    )
    features_panel = fg.generate()
    tg = TargetGenerator(data_dict, forward_horizon=21, sector_mapping=sector_mapping)
    targets = tg.generate()
    panel = features_panel.join(targets, how="inner")
    logger.info(f"Panel: {panel.shape[1]} cols, {len(panel):,} rows")

    spy_fwd = build_spy_fwd_ret(data_dict, horizon=21)
    scores_df = compute_factor_scores(panel)
    panel = panel.join(scores_df, how="inner")

    # ── Per-score analysis ───────────────────────────────────────────────────
    reg_results: dict = {}
    all_port_dfs: dict = {}

    for score_col in SCORES:
        logger.info(f"Building portfolio series for {score_col}...")
        port = build_portfolio_series(
            panel, score_col, spy_fwd,
            eval_start=args.eval_start, eval_end=args.eval_end,
        )
        port = add_rolling_stats(port, window=12)
        port = add_rolling_stats(port, window=6)
        all_port_dfs[score_col] = port

        valid = port.dropna(subset=["spy_ret"])

        lo_reg = _ols(valid["long_ret"].values, valid["spy_ret"].values)
        ls_reg = _ols(valid["ls_ret"].values,   valid["spy_ret"].values)

        long_avg_beta  = float(valid["long_beta"].mean())
        short_avg_beta = float(valid["short_beta"].mean())
        reg_results[score_col] = {
            "long_only":    lo_reg,
            "long_short":   ls_reg,
            "long_avg_beta":  long_avg_beta,
            "short_avg_beta": short_avg_beta,
            "ls_avg_beta":    long_avg_beta - short_avg_beta,
            "long_ann_ret":   float(valid["long_ret"].mean() * 252 / 21),
            "spy_ann_ret":    float(valid["spy_ret"].mean()  * 252 / 21),
            "ls_ann_ret":     float(valid["ls_ret"].mean()   * 252 / 21),
            "long_ann_alpha": float(valid["long_alpha"].mean() * 252 / 21),
            "ls_ann_alpha":   float(valid["ls_alpha"].mean()  * 252 / 21),
        }

        r = reg_results[score_col]
        lo = r["long_only"]
        ls = r["long_short"]
        logger.info(
            f"  {score_col}: "
            f"long α_ann={lo['alpha_ann']*100:.2f}% β={lo['beta']:.3f} R²={lo['r2']:.3f} "
            f"| LS α_ann={ls['alpha_ann']*100:.2f}% β={ls['beta']:.3f} R²={ls['r2']:.3f}"
        )

    wall = time.perf_counter() - t0

    # ── Save CSV ─────────────────────────────────────────────────────────────
    out_dir = Path("artifacts/reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_parts = []
    for sc, port in all_port_dfs.items():
        p = port.copy()
        p.insert(0, "score", sc)
        csv_parts.append(p.reset_index())
    csv_df = pd.concat(csv_parts, ignore_index=True)
    csv_df.to_csv(out_dir / "beta_vs_return.csv", index=False)

    # ── Build markdown ───────────────────────────────────────────────────────

    # Per-score narrative rows
    score_rows = []
    for sc in SCORES:
        r = reg_results[sc]
        lo = r["long_only"]
        ls = r["long_short"]
        score_rows.append(
            f"| {sc} | {r['long_avg_beta']:.3f} | "
            f"{lo['beta']:.3f} | {lo['alpha_ann']*100:.2f}% | {lo['t_alpha']:.2f} | "
            f"{lo['r2']:.3f} | {ls['beta']:.3f} | {ls['alpha_ann']*100:.2f}% | {ls['t_alpha']:.2f} |"
        )

    # Determine verdict for each score
    verdicts = {}
    for sc in SCORES:
        r = reg_results[sc]
        lo = r["long_only"]
        ls = r["long_short"]
        alpha_sig_95 = abs(lo["t_alpha"]) > 1.96
        alpha_sig_90 = abs(lo["t_alpha"]) > 1.64
        ls_alpha_sig  = abs(ls["t_alpha"]) > 1.64
        beta_near_mkt = 0.8 < lo["beta"] < 1.2   # within ±20% of market

        if alpha_sig_95 and ls_alpha_sig:
            verdicts[sc] = (
                f"NOT just beta — statistically significant alpha at 95% "
                f"(long t={lo['t_alpha']:.2f}, LS t={ls['t_alpha']:.2f})"
            )
        elif alpha_sig_90 and not ls_alpha_sig:
            verdicts[sc] = (
                f"Partial alpha — long portfolio alpha significant at 90% "
                f"(t={lo['t_alpha']:.2f}), but LS spread alpha weak (t={ls['t_alpha']:.2f})"
            )
        elif beta_near_mkt and not alpha_sig_90:
            verdicts[sc] = (
                f"Beta-plus-noise — market-like β={lo['beta']:.3f} with no significant alpha "
                f"(t={lo['t_alpha']:.2f})"
            )
        else:
            verdicts[sc] = (
                f"Weak / mixed — β={lo['beta']:.3f}, alpha t={lo['t_alpha']:.2f}"
            )

    md = [
        "# Beta Decomposition — Momentum + Vol Factor Scores",
        "",
        f"_Eval: {args.eval_start} – {args.eval_end} | sp100 (44 tickers) | "
        f"Monthly rebalancing (non-overlapping 21-day) | Wall time: {wall:.0f}s_",
        "",
        "## Methodology",
        "",
        "For each date in the eval window (sampled every 21 trading days):",
        "- **Long portfolio** = equal-weight top-quintile stocks by score",
        "- **Short portfolio** = equal-weight bottom-quintile stocks by score",
        "- **Long-short (LS)** = long return − short return",
        "- **SPY return** = 21-day forward return from same date",
        "",
        "OLS regression: `portfolio_return ~ α + β · SPY_return`",
        "- α (Jensen's alpha) = return unexplained by market exposure",
        "- β = portfolio market loading",
        "- Annualised: multiply by 252/21 ≈ 12×",
        "",
        "---",
        "",
        "## Regression Results",
        "",
        "| Score | Avg long β | Long β | Long α (ann%) | t(α) | Long R² | LS β | LS α (ann%) | t(α) |",
        "|---|---|---|---|---|---|---|---|---|",
    ] + score_rows + [
        "",
        "> β = portfolio OLS beta vs SPY. α = annualised Jensen's alpha. "
        "t(α) > 1.96 → significant at 95%. LS = long-short (top20% − bottom20%).",
        "",
        "---",
        "",
        "## Avg beta of selected stocks (from `beta_to_spy_63d` feature)",
        "",
        "| Score | Avg beta of long stocks | Avg beta of short stocks | L-S beta spread |",
        "|---|---|---|---|",
    ] + [
        f"| {sc} | {reg_results[sc]['long_avg_beta']:.3f} | "
        f"{reg_results[sc]['short_avg_beta']:.3f} | "
        f"{reg_results[sc]['ls_avg_beta']:.3f} |"
        for sc in SCORES
    ] + [
        "",
        "_Avg beta of long stocks comes directly from the `beta_to_spy_63d` feature — "
        "reflects the stocks' realised rolling beta at the time of selection._",
        "",
        "---",
        "",
        "## Rolling 12-month beta (long-short portfolio)",
        "",
    ]

    # Rolling stats summary
    for sc in SCORES:
        port = all_port_dfs[sc]
        roll = port["roll_12m_beta"].dropna()
        if len(roll) > 0:
            md.append(
                f"- **{sc}**: mean {roll.mean():.3f}, "
                f"min {roll.min():.3f}, max {roll.max():.3f}, "
                f"std {roll.std():.3f} (n={len(roll)} 12m windows)"
            )

    md += [
        "",
        "---",
        "",
        "## Conclusion — Is the signal just beta exposure?",
        "",
    ]

    for sc in SCORES:
        r = reg_results[sc]
        lo = r["long_only"]
        ls = r["long_short"]
        md.append(f"### {sc}")
        md.append("")
        md.append(
            f"- Long portfolio beta = **{lo['beta']:.3f}** (avg selected stock β = {r['long_avg_beta']:.3f})"
        )
        md.append(
            f"- Long-short beta = **{ls['beta']:.3f}** — "
            + ("significant market loading in the spread" if abs(ls["beta"]) > 0.3
               else "near-zero market loading in the spread")
        )
        md.append(
            f"- Long annualised alpha = **{lo['alpha_ann']*100:.2f}%** (t = {lo['t_alpha']:.2f})"
        )
        md.append(
            f"- Long-short annualised alpha = **{ls['alpha_ann']*100:.2f}%** (t = {ls['t_alpha']:.2f})"
        )
        md.append(f"- **Verdict: {verdicts[sc]}**")
        md.append("")

    (out_dir / "beta_analysis.md").write_text("\n".join(md))
    logger.info(f"Saved: {out_dir}/beta_analysis.md")
    logger.info(f"Saved: {out_dir}/beta_vs_return.csv")

    print("\n" + "=" * 80)
    for sc in SCORES:
        r = reg_results[sc]
        lo = r["long_only"]
        ls = r["long_short"]
        print(
            f"{sc:20s}  "
            f"long: β={lo['beta']:.3f} α_ann={lo['alpha_ann']*100:.1f}% t(α)={lo['t_alpha']:.2f}  |  "
            f"LS:   β={ls['beta']:.3f} α_ann={ls['alpha_ann']*100:.1f}% t(α)={ls['t_alpha']:.2f}"
        )
    print("=" * 80)


if __name__ == "__main__":
    main()
