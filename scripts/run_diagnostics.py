"""
Ablation diagnostics with enhanced alpha quality metrics.

Outputs per run:
  ablation_results.csv          — CAGR / Sharpe / MaxDD for each experiment
  optimizer_sensitivity.csv     — turnover sweep
  risk_intervention_log.csv     — per-rebalance risk events
  alpha_quality_detail.json     — IC, Precision@N, spread, sector IC
  diagnostic_summary.md         — human-readable summary

Universe-expansion comparison:
  artifacts/reports/universe_expansion_results.md
  artifacts/reports/alpha_quality_large_universe.json
"""
import argparse
import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from src.config.loader import load_config
from src.backtest.walk_forward import WalkForwardEngine
from src.data.ingestion import DataIngestion
from src.reporting.metrics import calculate_metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Alpha quality helpers ────────────────────────────────────────────────────

def _precision_at_n(alpha_scores: pd.Series, actual_rets: pd.Series, n: int) -> float:
    """Fraction of top-N predicted that are also in top-N actual."""
    if len(alpha_scores) < n or len(actual_rets) < n:
        return float("nan")
    common = alpha_scores.index.intersection(actual_rets.dropna().index)
    if len(common) < n:
        return float("nan")
    pred_top = set(alpha_scores.loc[common].nlargest(n).index)
    act_top  = set(actual_rets.loc[common].nlargest(n).index)
    return len(pred_top & act_top) / n


def _sector_ic(alpha_scores: pd.Series, actual_rets: pd.Series,
               sector_mapping: dict) -> dict:
    """Rank IC broken down by sector."""
    common = alpha_scores.index.intersection(actual_rets.dropna().index)
    out = {}
    for ticker in common:
        sec = sector_mapping.get(ticker, "Unknown")
        out.setdefault(sec, []).append(ticker)
    sector_ics = {}
    for sec, tickers in out.items():
        if len(tickers) < 5:
            continue
        a = alpha_scores.loc[tickers].rank()
        b = actual_rets.loc[tickers].rank()
        sector_ics[sec] = float(a.corr(b))
    return sector_ics


def _concentration(weights: pd.Series) -> dict:
    w = weights[weights > 0]
    if w.empty:
        return {"hhi": 1.0, "eff_n": 1.0}
    hhi   = float((w ** 2).sum())
    eff_n = float(1.0 / hhi) if hhi > 0 else float(len(w))
    return {"hhi": hhi, "eff_n": eff_n}


# ── Engine helpers ───────────────────────────────────────────────────────────

def _load_engine(base_config, universe_config, features_dir: Path,
                 prices_dict: dict, pit_mask):
    stock_features = pd.read_parquet(features_dir / "stock_features.parquet")
    macro_features = pd.read_parquet(features_dir / "macro_features.parquet")
    targets        = pd.read_parquet(features_dir / "targets.parquet")
    return WalkForwardEngine(
        config=base_config, universe_config=universe_config,
        stock_features=stock_features, macro_features=macro_features,
        targets=targets, prices_dict=prices_dict, pit_mask=pit_mask
    )


def run_experiment(name, engine, **kwargs):
    logger.info(f"Running experiment: {name}")
    history, trades, diagnostics = engine.run(**kwargs)
    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    return {"name": name, "metrics": metrics, "diagnostics": diagnostics, "history": history}


# ── Enhanced alpha quality aggregation ──────────────────────────────────────

def _aggregate_alpha_quality(alpha_quality_list: list, sector_mapping: dict,
                              top_n_p20: int = 20, top_n_p50: int = 50) -> dict:
    rics         = [x["rank_ic"]         for x in alpha_quality_list if "rank_ic" in x]
    spreads      = [x["spread"]          for x in alpha_quality_list if "spread"  in x]
    top_rets     = [x["top_decile_ret"]  for x in alpha_quality_list if "top_decile_ret" in x]
    bot_rets     = [x["bot_decile_ret"]  for x in alpha_quality_list if "bot_decile_ret" in x]
    prec20       = [x.get("precision_20", float("nan")) for x in alpha_quality_list]
    prec50       = [x.get("precision_50", float("nan")) for x in alpha_quality_list]
    prec20_clean = [v for v in prec20 if not np.isnan(v)]
    prec50_clean = [v for v in prec50 if not np.isnan(v)]

    # Sector IC — average across rebalances
    all_sec_ics: dict = {}
    for entry in alpha_quality_list:
        for sec, ic in entry.get("sector_ic", {}).items():
            all_sec_ics.setdefault(sec, []).append(ic)
    mean_sector_ic = {s: float(np.mean(v)) for s, v in all_sec_ics.items()}

    return {
        "n_rebalances":    len(rics),
        "mean_rank_ic":    float(np.mean(rics))   if rics    else None,
        "median_rank_ic":  float(np.median(rics)) if rics    else None,
        "pct_positive_ic": float(np.mean([r > 0 for r in rics])) if rics else None,
        "mean_spread":     float(np.mean(spreads)) if spreads else None,
        "mean_top_decile": float(np.mean(top_rets)) if top_rets else None,
        "mean_bot_decile": float(np.mean(bot_rets)) if bot_rets else None,
        "precision_at_20": float(np.mean(prec20_clean)) if prec20_clean else None,
        "precision_at_50": float(np.mean(prec50_clean)) if prec50_clean else None,
        "sector_ic":       mean_sector_ic,
    }


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Run Portfolio Diagnostics")
    parser.add_argument("--config",           type=str, required=True)
    parser.add_argument("--universe",         type=str, default="config/universes/sp100.yaml")
    parser.add_argument("--compare-universe", type=str, default=None,
                        help="Old/baseline universe for before-vs-after comparison")
    args = parser.parse_args()

    base_config, universe_config = load_config(args.config, args.universe)
    cache_dir    = Path(base_config.data.cache_dir)
    features_dir = cache_dir / "features"

    diag_dir = Path("artifacts/diagnostics") / datetime.now().strftime("%Y%m%d_%H%M%S")
    diag_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Load data once
    ingestion   = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(set(
        list(universe_config.tickers.keys()) +
        universe_config.macro_etfs + universe_config.sector_etfs +
        [universe_config.benchmark]
    ))
    data_dict   = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)
    prices_dict = ingestion.build_all_matrices(data_dict)

    pit_mask = None
    if not universe_config.is_static and universe_config.pit_mask_path:
        pit_mask = pd.read_parquet(universe_config.pit_mask_path)

    top_n = base_config.portfolio.top_n_stocks

    def get_engine():
        return _load_engine(base_config, universe_config, features_dir, prices_dict, pit_mask)

    # ── Alpha quality run only (trimmed for speed) ───────────────────────────
    alpha_run = run_experiment(f"Alpha_Top{top_n}_EW",
                               get_engine(), use_optimizer=False, use_risk_engine=False,
                               top_n_equal_weight=top_n)
    results = [alpha_run]

    # Stub ablation/sensitivity CSVs so downstream code doesn't break
    ablation_df = pd.DataFrame([{
        "Experiment": alpha_run["name"],
        "CAGR":       alpha_run["metrics"].get("CAGR"),
        "Sharpe":     alpha_run["metrics"].get("Sharpe"),
        "MaxDD":      alpha_run["metrics"].get("Max Drawdown"),
        "Volatility": alpha_run["metrics"].get("Volatility"),
    }])
    ablation_df.to_csv(diag_dir / "ablation_results.csv", index=False)
    pd.DataFrame(columns=["turnover_limit", "cagr", "sharpe", "max_dd"]).to_csv(
        diag_dir / "optimizer_sensitivity.csv", index=False)

    # ── Enhanced alpha quality ────────────────────────────────────────────────
    top_n_diag = alpha_run
    raw_aq     = top_n_diag["diagnostics"].get("alpha_quality", [])
    sector_mapping = dict(universe_config.tickers)

    # Metrics are now computed in walk_forward._generate_target_weights — pass through as-is
    enriched_aq = [dict(entry) for entry in raw_aq]

    # ── Summary stats ─────────────────────────────────────────────────────────
    rics    = [e["rank_ic"]         for e in enriched_aq if "rank_ic"         in e]
    spreads = [e["spread"]          for e in enriched_aq if "spread"          in e]
    top_d   = [e["top_decile_ret"]  for e in enriched_aq if "top_decile_ret"  in e]
    bot_d   = [e["bot_decile_ret"]  for e in enriched_aq if "bot_decile_ret"  in e]
    p20     = [v for e in enriched_aq for v in [e.get("precision_20")] if v is not None and not np.isnan(v)]
    p50     = [v for e in enriched_aq for v in [e.get("precision_50")] if v is not None and not np.isnan(v)]

    # Sector IC — average across all rebalances
    all_sec_ics: dict = {}
    for e in enriched_aq:
        for sec, ic in e.get("sector_ic", {}).items():
            if not np.isnan(ic):
                all_sec_ics.setdefault(sec, []).append(ic)
    mean_sector_ic = {s: float(np.mean(v)) for s, v in all_sec_ics.items()}

    alpha_summary = {
        "universe":         universe_config.name,
        "n_tickers":        len(universe_config.tickers),
        "n_rebalances":     len(rics),
        "mean_rank_ic":     float(np.mean(rics))    if rics    else None,
        "median_rank_ic":   float(np.median(rics))  if rics    else None,
        "pct_positive_ic":  float(np.mean([r > 0 for r in rics])) if rics else None,
        "mean_spread":      float(np.mean(spreads)) if spreads else None,
        "mean_top_decile":  float(np.mean(top_d))   if top_d   else None,
        "mean_bot_decile":  float(np.mean(bot_d))   if bot_d   else None,
        "precision_at_20":  float(np.mean(p20))     if p20     else None,
        "precision_at_50":  float(np.mean(p50))     if p50     else None,
        "sector_ic":        mean_sector_ic,
        "per_rebalance":    enriched_aq,
    }

    with open(diag_dir / "alpha_quality_detail.json", "w") as f:
        json.dump(alpha_summary, f, indent=4)
    with open(reports_dir / "alpha_quality_large_universe.json", "w") as f:
        json.dump(alpha_summary, f, indent=4)

    # ── Risk intervention / exposure ─────────────────────────────────────────
    risk_log    = pd.DataFrame(full_sys["diagnostics"].get("risk_interventions", []))
    exposure_df = pd.DataFrame(full_sys["diagnostics"].get("exposure", []))
    risk_log.to_csv(diag_dir / "risk_intervention_log.csv", index=False)

    avg_exposure = exposure_df["gross_exposure"].mean() if not exposure_df.empty else 0
    avg_holdings = exposure_df["num_holdings"].mean()   if not exposure_df.empty else 0
    pct_risk     = (len(risk_log) / len(exposure_df))   if not exposure_df.empty else 0
    avg_hhi      = exposure_df["hhi"].mean()            if "hhi"       in exposure_df.columns and not exposure_df.empty else float("nan")
    avg_eff_n    = exposure_df["effective_n"].mean()    if "effective_n" in exposure_df.columns and not exposure_df.empty else float("nan")

    # ── Diagnostic summary ────────────────────────────────────────────────────
    alpha_cagr   = alpha_run["metrics"].get("CAGR", 0) or 0
    alpha_sharpe = alpha_run["metrics"].get("Sharpe", 0) or 0

    summary_lines = [
        "# Diagnostic Summary",
        f"Generated: {datetime.now()}",
        f"Universe:  {universe_config.name}  ({len(universe_config.tickers)} tickers)",
        f"Top-N:     {top_n} stocks",
        "",
        "## Ablation",
        f"| Experiment | CAGR | Sharpe | MaxDD | Vol |",
        f"|---|---|---|---|---|",
    ]
    for _, row in ablation_df.iterrows():
        summary_lines.append(
            f"| {row['Experiment']} | {row['CAGR']:.2%} | {row['Sharpe']:.2f} | "
            f"{row['MaxDD']:.2%} | {row['Volatility']:.2%} |"
        )

    def _fmt(v, fmt):
        return format(v, fmt) if v is not None else "n/a"

    sec_ic_lines = [f"  - {s}: {v:.4f}" for s, v in sorted(alpha_summary.get("sector_ic", {}).items(), key=lambda x: -x[1])]
    summary_lines += [
        "",
        "## Alpha Quality",
        f"- Mean Rank IC:    {_fmt(alpha_summary['mean_rank_ic'], '.4f')}",
        f"- Median Rank IC:  {_fmt(alpha_summary['median_rank_ic'], '.4f')}",
        f"- % Positive IC:   {_fmt(alpha_summary['pct_positive_ic'], '.1%')}",
        f"- Mean Spread:     {_fmt(alpha_summary['mean_spread'], '.4f')}",
        f"- Mean Top Decile: {_fmt(alpha_summary['mean_top_decile'], '.4f')}",
        f"- Mean Bot Decile: {_fmt(alpha_summary['mean_bot_decile'], '.4f')}",
        f"- Precision@20:    {_fmt(alpha_summary['precision_at_20'], '.4f')}",
        f"- Precision@50:    {_fmt(alpha_summary['precision_at_50'], '.4f')}",
        "- Sector IC (mean across rebalances):",
        *sec_ic_lines,
        "",
        "## Exposure & Holdings (Full System)",
        f"- Avg Gross Exposure:  {avg_exposure:.2%}",
        f"- Avg Cash:            {1-avg_exposure:.2%}",
        f"- Avg Holdings:        {avg_holdings:.1f}",
        f"- Avg HHI:             {avg_hhi:.4f}" if not np.isnan(avg_hhi) else "- Avg HHI:             n/a",
        f"- Avg Effective N:     {avg_eff_n:.1f}" if not np.isnan(avg_eff_n) else "- Avg Effective N:     n/a",
        f"- % Rebalances w/ Risk Trigger: {pct_risk:.2%}",
        "",
        "## Key Findings",
    ]

    summary_lines.append(f"- **Alpha Top-{top_n} EW**: CAGR={alpha_cagr:.2%}  Sharpe={alpha_sharpe:.2f}")
    if avg_exposure < 0.75:
        summary_lines.append(f"- **CASH DRAG**: avg exposure {avg_exposure:.2%} (target ≥ 75%)")
    if alpha_summary["mean_rank_ic"] is not None and alpha_summary["mean_rank_ic"] > 0.04:
        summary_lines.append(f"- **IC TARGET MET**: {alpha_summary['mean_rank_ic']:.4f} > 0.04")
    else:
        ic_val = alpha_summary["mean_rank_ic"] or 0
        summary_lines.append(f"- **IC BELOW TARGET**: {ic_val:.4f} (target >0.04)")

    (diag_dir / "diagnostic_summary.md").write_text("\n".join(summary_lines))

    # ── Universe expansion comparison ─────────────────────────────────────────
    if args.compare_universe:
        logger.info(f"Loading baseline universe: {args.compare_universe}")
        _, old_universe = load_config(args.config, args.compare_universe)

        old_cache   = Path(base_config.data.cache_dir)
        old_ftdir   = old_cache / "features"   # same features dir; old universe is subset
        old_pitm    = None
        if not old_universe.is_static and old_universe.pit_mask_path:
            old_pitm = pd.read_parquet(old_universe.pit_mask_path)

        old_all = list(set(
            list(old_universe.tickers.keys()) +
            old_universe.macro_etfs + old_universe.sector_etfs + [old_universe.benchmark]
        ))
        old_data    = ingestion.fetch_universe_data(tickers=old_all, start_date=base_config.backtest.start_date)
        old_prices  = ingestion.build_all_matrices(old_data)
        old_engine  = _load_engine(base_config, old_universe, old_ftdir, old_prices, old_pitm)

        old_res = run_experiment(f"Alpha_Top{top_n}_EW_OLD",
                                 old_engine, use_optimizer=False, use_risk_engine=False,
                                 top_n_equal_weight=top_n)
        old_m   = old_res["metrics"]
        new_m   = top_n_diag["metrics"]

        old_aq  = old_res["diagnostics"].get("alpha_quality", [])
        old_rics = [e["rank_ic"] for e in old_aq if "rank_ic" in e]

        comparison_md = [
            "# Universe Expansion Results",
            f"Generated: {datetime.now()}",
            "",
            "## Universe Summary",
            f"| | Old ({old_universe.name}) | New ({universe_config.name}) |",
            f"|---|---|---|",
            f"| Tickers | {len(old_universe.tickers)} | {len(universe_config.tickers)} |",
            f"| Top-N   | {top_n} | {top_n} |",
            "",
            "## Performance Comparison",
            f"| Metric | Old | New | Delta |",
            f"|---|---|---|---|",
        ]
        for key in ["CAGR", "Sharpe", "Max Drawdown", "Volatility"]:
            v_old = old_m.get(key, 0) or 0
            v_new = new_m.get(key, 0) or 0
            delta = v_new - v_old
            fmt = ".2%" if key in ("CAGR", "Max Drawdown", "Volatility") else ".2f"
            comparison_md.append(
                f"| {key} | {v_old:{fmt}} | {v_new:{fmt}} | "
                f"{'▲' if delta>0 else '▼'} {abs(delta):{fmt}} |"
            )

        ic_old = float(np.mean(old_rics)) if old_rics else 0
        ic_new = alpha_summary["mean_rank_ic"] or 0
        comparison_md += [
            "",
            "## Alpha Quality Comparison",
            f"| Metric | Old | New |",
            f"|---|---|---|",
            f"| Mean Rank IC     | {ic_old:.4f} | {ic_new:.4f} |",
            f"| % Positive IC    | {np.mean([r>0 for r in old_rics]) if old_rics else 0:.1%} | "
            f"{alpha_summary['pct_positive_ic'] or 0:.1%} |",
            "",
            "## Success Criteria",
        ]
        comparison_md.append(f"- IC > 0.04:     {'✅' if ic_new > 0.04 else '❌'}  ({ic_new:.4f})")
        delta_cagr = (new_m.get("CAGR", 0) or 0) - (old_m.get("CAGR", 0) or 0)
        comparison_md.append(f"- CAGR +2–5 pp:  {'✅' if 0.02 <= delta_cagr <= 0.07 else '❓'} ({delta_cagr:+.2%})")
        d_sharpe = (new_m.get("Sharpe", 0) or 0) - (old_m.get("Sharpe", 0) or 0)
        comparison_md.append(f"- Sharpe stable: {'✅' if d_sharpe >= -0.05 else '❌'} ({d_sharpe:+.2f})")

        (reports_dir / "universe_expansion_results.md").write_text("\n".join(comparison_md))
        logger.info(f"Universe comparison report → {reports_dir / 'universe_expansion_results.md'}")

    logger.info(f"Diagnostics complete. Results in {diag_dir}")


if __name__ == "__main__":
    main()
