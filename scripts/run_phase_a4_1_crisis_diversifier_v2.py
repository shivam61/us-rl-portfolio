import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_phase_a4_defensive_sleeve import (
    active_tickers,
    backtest_weight_path,
    benchmark_rows,
    beta_target_weights,
    combine_weight_paths,
    equal_weights,
    latest_feature,
    latest_scores,
    load_inputs,
    rebalance_dates,
    select_sector_balanced,
    select_top,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

VOL_SPECS = [("vol_top_10", 10), ("vol_top_20", 20)]
DIVERSIFIER_SPECS = [
    ("crisis_diversifier_top_10_equal_weight", 10, None),
    ("crisis_diversifier_top_20_equal_weight", 20, None),
    ("crisis_diversifier_top_30_equal_weight", 30, None),
    ("crisis_diversifier_top_10_beta_0_6", 10, 0.6),
    ("crisis_diversifier_top_20_beta_0_6", 20, 0.6),
    ("crisis_diversifier_top_30_beta_0_6", 30, 0.6),
    ("crisis_diversifier_top_10_beta_0_8", 10, 0.8),
    ("crisis_diversifier_top_20_beta_0_8", 20, 0.8),
    ("crisis_diversifier_top_30_beta_0_8", 30, 0.8),
]
BLEND_WEIGHTS = [(0.6, 0.4), (0.5, 0.5)]


def clean_series(panel: pd.DataFrame, col: str, lower: float | None = None, upper: float | None = None) -> pd.Series:
    if col not in panel.columns:
        return pd.Series(np.nan, index=panel.index)
    values = panel[col].astype(float).replace([np.inf, -np.inf], np.nan)
    return values.clip(lower=lower, upper=upper)


def rolling_stability(series: pd.Series, window: int = 252, min_periods: int = 63) -> pd.Series:
    return -series.groupby(level="ticker").rolling(window, min_periods=min_periods).std().droplevel(0)


def cross_sectional_rank(series: pd.Series) -> pd.Series:
    return series.replace([np.inf, -np.inf], np.nan).groupby(level="date").rank(pct=True)


def component_score(parts: list[pd.Series]) -> pd.Series:
    if not parts:
        return pd.Series(dtype=float)
    ranked = [cross_sectional_rank(part) for part in parts]
    return pd.concat(ranked, axis=1).mean(axis=1, skipna=True)


def compute_crisis_diversifier_score_frame(panel: pd.DataFrame) -> pd.DataFrame:
    """Fundamental-only crisis diversifier score.

    Excludes returns, volatility, drawdown, momentum, and beta from alpha scoring.
    Beta is applied later only as a sleeve construction control.
    """
    debt_to_assets = clean_series(panel, "debt_to_assets", lower=-1.0, upper=3.0)
    debt_to_equity = clean_series(panel, "debt_to_equity", lower=-5.0, upper=10.0)
    interest_coverage = clean_series(panel, "interest_coverage", lower=0.0, upper=100.0)
    balance_strength = component_score(
        [
            -debt_to_assets,
            -debt_to_equity,
            np.log1p(interest_coverage),
        ]
    )

    ocf_to_net_income = clean_series(panel, "ocf_to_net_income", lower=-5.0, upper=5.0)
    accruals = clean_series(panel, "accruals_proxy", lower=-2.0, upper=2.0)
    cashflow_quality = component_score(
        [
            ocf_to_net_income,
            -accruals.abs(),
        ]
    )

    roe = clean_series(panel, "roe", lower=-1.0, upper=1.0)
    gross_margin = clean_series(panel, "gross_margin", lower=-1.0, upper=1.0)
    eps_growth = clean_series(panel, "eps_growth_yoy", lower=-5.0, upper=5.0)
    profitability_stability = component_score(
        [
            rolling_stability(roe),
            rolling_stability(gross_margin),
            rolling_stability(eps_growth),
            -roe.clip(upper=0.0).abs(),
        ]
    )

    pe = clean_series(panel, "pe_ratio", lower=0.0, upper=100.0)
    pb = clean_series(panel, "pb_ratio", lower=0.0, upper=50.0)
    valuation_buffer = component_score(
        [
            -np.log1p(pe),
            -np.log1p(pb),
        ]
    )

    result = pd.DataFrame(index=panel.index)
    result["balance_strength"] = balance_strength
    result["cashflow_quality"] = cashflow_quality
    result["profitability_stability"] = profitability_stability
    result["valuation_buffer"] = valuation_buffer
    result["crisis_diversifier_score"] = result[
        ["balance_strength", "cashflow_quality", "profitability_stability", "valuation_buffer"]
    ].mean(axis=1, skipna=True)
    result["crisis_diversifier_score_rank"] = result.groupby(level="date")["crisis_diversifier_score"].rank(pct=True)
    return result


def audit_fundamental_features(panel: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    fields = [
        "debt_to_assets",
        "debt_to_equity",
        "interest_coverage",
        "ocf_to_net_income",
        "accruals_proxy",
        "roe",
        "gross_margin",
        "eps_growth_yoy",
        "pe_ratio",
        "pb_ratio",
    ]
    rows = []
    ticker_set = set(tickers)
    scoped = panel[panel.index.get_level_values("ticker").isin(ticker_set)]
    for field in fields:
        if field not in scoped.columns:
            rows.append({"feature": field, "coverage_pct": 0.0, "ticker_coverage_pct": 0.0})
            continue
        values = scoped[field].replace([np.inf, -np.inf], np.nan)
        rows.append(
            {
                "feature": field,
                "coverage_pct": float(values.notna().mean()),
                "ticker_coverage_pct": float(values.dropna().index.get_level_values("ticker").nunique() / max(len(tickers), 1)),
            }
        )
    return pd.DataFrame(rows)


def build_weight_paths(inputs: dict, diversifier_scores: pd.DataFrame) -> dict[str, dict]:
    config = inputs["base_config"]
    rebalances = rebalance_dates(config, inputs["prices"])
    sector_mapping = inputs["sector_mapping"]
    paths: dict[str, dict] = {}

    for name, n in VOL_SPECS:
        weights_by_date = {}
        selected_by_date = {}
        realized_beta_by_date = {}
        for date in rebalances:
            candidates = active_tickers(inputs, date)
            scores = latest_scores(inputs["vol_scores"], date, "volatility_score").reindex(candidates)
            selected = select_top(scores, n)
            weights = equal_weights(selected)
            betas = latest_feature(inputs["stock_features"], date, "beta_to_spy_63d")
            weights_by_date[date] = weights
            selected_by_date[date] = selected
            realized_beta_by_date[date] = float((weights * betas.reindex(weights.index).fillna(1.0)).sum()) if not weights.empty else np.nan
        paths[name] = {
            "weights": weights_by_date,
            "selected": selected_by_date,
            "realized_beta": realized_beta_by_date,
            "sleeve_type": "volatility",
        }

    for name, n, beta_target in DIVERSIFIER_SPECS:
        weights_by_date = {}
        selected_by_date = {}
        realized_beta_by_date = {}
        for date in rebalances:
            candidates = active_tickers(inputs, date)
            scores = latest_scores(diversifier_scores, date, "crisis_diversifier_score").reindex(candidates)
            selected = select_sector_balanced(scores, min(n, len(candidates)), sector_mapping)
            betas = latest_feature(inputs["stock_features"], date, "beta_to_spy_63d").reindex(selected)
            weights = equal_weights(selected) if beta_target is None else beta_target_weights(selected, betas, beta_target)
            weights_by_date[date] = weights
            selected_by_date[date] = selected
            realized_beta_by_date[date] = float((weights * betas.reindex(weights.index).fillna(1.0)).sum()) if not weights.empty else np.nan
        paths[name] = {
            "weights": weights_by_date,
            "selected": selected_by_date,
            "realized_beta": realized_beta_by_date,
            "target_beta": beta_target,
            "sleeve_type": "diversifier",
        }

    return paths


def overlap_rows(inputs: dict, paths: dict[str, dict]) -> list[dict]:
    rows = []
    sector_mapping = inputs["sector_mapping"]
    vol_names = [n for n, p in paths.items() if p["sleeve_type"] == "volatility"]
    div_names = [n for n, p in paths.items() if p["sleeve_type"] == "diversifier"]
    for vol_name in vol_names:
        for div_name in div_names:
            ticker_overlaps = []
            sector_overlaps = []
            dates = sorted(set(paths[vol_name]["selected"]).intersection(paths[div_name]["selected"]))
            for date in dates:
                vol_sel = set(paths[vol_name]["selected"][date])
                div_sel = set(paths[div_name]["selected"][date])
                if vol_sel and div_sel:
                    ticker_overlaps.append(len(vol_sel & div_sel) / min(len(vol_sel), len(div_sel)))
                vol_sec = {sector_mapping.get(t, "_other") for t in vol_sel}
                div_sec = {sector_mapping.get(t, "_other") for t in div_sel}
                if vol_sec and div_sec:
                    sector_overlaps.append(len(vol_sec & div_sec) / min(len(vol_sec), len(div_sec)))
            rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "diversifier_sleeve": div_name,
                    "ticker_overlap_pct": float(pd.Series(ticker_overlaps).mean()) if ticker_overlaps else np.nan,
                    "sector_overlap_pct": float(pd.Series(sector_overlaps).mean()) if sector_overlaps else np.nan,
                    "n_rebalances": len(dates),
                }
            )
    return rows


def correlation_rows(inputs: dict, returns_by_name: dict[str, pd.Series]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    names = sorted(returns_by_name)
    aligned = pd.concat({name: returns_by_name[name] for name in names}, axis=1).dropna(how="all").fillna(0.0)
    prices = inputs["prices"]
    benchmark = inputs["universe_config"].benchmark
    drawdown = prices[benchmark] / prices[benchmark].expanding().max() - 1.0
    crisis_dates = drawdown[drawdown <= -0.15].index

    full_rows = []
    crisis_rows = []
    rolling_rows = []
    for vol_name in [n for n in names if n.startswith("vol_")]:
        for div_name in [n for n in names if n.startswith("crisis_diversifier_")]:
            pair = aligned[[vol_name, div_name]].dropna()
            rolling = pair[vol_name].rolling(252, min_periods=63).corr(pair[div_name])
            crisis_pair = pair.loc[pair.index.intersection(crisis_dates)]
            full_corr = float(pair[vol_name].corr(pair[div_name])) if len(pair) > 2 else np.nan
            crisis_corr = float(crisis_pair[vol_name].corr(crisis_pair[div_name])) if len(crisis_pair) > 2 else np.nan
            full_rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "diversifier_sleeve": div_name,
                    "full_correlation": full_corr,
                    "avg_rolling_252d_correlation": float(rolling.mean()) if not rolling.dropna().empty else np.nan,
                }
            )
            crisis_rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "diversifier_sleeve": div_name,
                    "crisis_correlation": crisis_corr,
                    "crisis_observations": len(crisis_pair),
                }
            )
            rolling_rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "vol_sleeve": vol_name,
                    "diversifier_sleeve": div_name,
                    "rolling_corr_min": float(rolling.min()) if not rolling.dropna().empty else np.nan,
                    "rolling_corr_median": float(rolling.median()) if not rolling.dropna().empty else np.nan,
                    "rolling_corr_max": float(rolling.max()) if not rolling.dropna().empty else np.nan,
                }
            )
    return pd.DataFrame(full_rows), pd.DataFrame(crisis_rows), pd.DataFrame(rolling_rows)


def gate_rows(metrics: pd.DataFrame, corr: pd.DataFrame, crisis_corr: pd.DataFrame) -> pd.DataFrame:
    rows = []
    diversifier_metrics = metrics[metrics["sleeve_type"] == "diversifier"]
    for _, metric in diversifier_metrics.iterrows():
        sleeve = metric["sleeve"]
        full_min = corr.loc[corr["diversifier_sleeve"] == sleeve, "full_correlation"].min()
        crisis_min = crisis_corr.loc[crisis_corr["diversifier_sleeve"] == sleeve, "crisis_correlation"].min()
        rows.append(
            {
                "universe": metric["universe"],
                "sleeve": sleeve,
                "sharpe": metric["sharpe"],
                "max_dd": metric["max_dd"],
                "min_full_corr_vs_vol": full_min,
                "min_crisis_corr_vs_vol": crisis_min,
                "passes_hard_gate": bool(
                    metric["sharpe"] >= 0.7
                    and full_min <= 0.6
                    and crisis_min <= 0.65
                ),
            }
        )
    return pd.DataFrame(rows)


def render_report(
    metrics: pd.DataFrame,
    blend_metrics: pd.DataFrame,
    corr: pd.DataFrame,
    crisis_corr: pd.DataFrame,
    rolling_corr: pd.DataFrame,
    overlaps: pd.DataFrame,
    benchmarks: pd.DataFrame,
    gates: pd.DataFrame,
    data_audit: pd.DataFrame,
) -> str:
    pass_rows = gates[gates["passes_hard_gate"]] if not gates.empty else pd.DataFrame()
    lines = [
        "# Phase A.4.1 Crisis Diversifier v2 Results",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Objective: build a truly orthogonal Sleeve 2 for the volatility alpha.",
        "- Score inputs: balance sheet strength, cash-flow quality, profitability stability, valuation buffer.",
        "- Excluded from score: returns, volatility, drawdown, momentum, and beta.",
        "- Beta is used only after selection for sleeve construction.",
        "- RL disabled.",
        "",
        "## Data Availability",
        "",
        data_audit.to_markdown(index=False, floatfmt=".4f") if not data_audit.empty else "No data audit rows.",
        "",
        "## Standalone Metrics",
        "",
        metrics.to_markdown(index=False, floatfmt=".4f") if not metrics.empty else "No metrics.",
        "",
        "## Hard Gate",
        "",
        gates.to_markdown(index=False, floatfmt=".4f") if not gates.empty else "No gate rows.",
        "",
        f"Gate result: {'PASS' if not pass_rows.empty else 'FAIL'}",
        "",
        "## Correlation",
        "",
        corr.to_markdown(index=False, floatfmt=".4f") if not corr.empty else "No correlation rows.",
        "",
        "## Crisis Correlation",
        "",
        crisis_corr.to_markdown(index=False, floatfmt=".4f") if not crisis_corr.empty else "No crisis correlation rows.",
        "",
        "## Rolling Correlation",
        "",
        rolling_corr.to_markdown(index=False, floatfmt=".4f") if not rolling_corr.empty else "No rolling correlation rows.",
        "",
        "## Overlap",
        "",
        overlaps.to_markdown(index=False, floatfmt=".4f") if not overlaps.empty else "No overlap rows.",
        "",
        "## Benchmarks",
        "",
        benchmarks.to_markdown(index=False, floatfmt=".4f") if not benchmarks.empty else "No benchmark rows.",
        "",
    ]
    if not pass_rows.empty:
        lines.extend(
            [
                "## Blend Metrics",
                "",
                blend_metrics.to_markdown(index=False, floatfmt=".4f") if not blend_metrics.empty else "No blend metrics.",
                "",
                "## Decision",
                "",
                "At least one crisis diversifier passed the standalone/correlation gate. Evaluate the 60/40 and 50/50 blends before considering SP500 scaling.",
            ]
        )
    else:
        lines.extend(
            [
                "## Blend Metrics",
                "",
                "Skipped by decision rule because no standalone crisis diversifier passed the hard gate.",
                "",
                "## Decision",
                "",
                "Do not tune blend weights and do not scale SEC ingestion to SP500 from this result. The next step is feature-level redesign or a different orthogonal sleeve.",
            ]
        )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.4.1 crisis diversifier v2 experiment")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml"])
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    metric_rows = []
    blend_rows = []
    corr_frames = []
    crisis_corr_frames = []
    rolling_corr_frames = []
    overlap_rows_all = []
    benchmarks_all = []
    audit_rows = []

    for universe_path in args.universes:
        logger.info("Running Phase A.4.1 crisis diversifier v2 for %s", universe_path)
        inputs = load_inputs(args.config, universe_path)
        diversifier_scores = compute_crisis_diversifier_score_frame(inputs["stock_features"])
        audit = audit_fundamental_features(inputs["stock_features"], list(inputs["universe_config"].tickers.keys()))
        audit.insert(0, "universe", inputs["universe_config"].name)
        audit_rows.append(audit)

        paths = build_weight_paths(inputs, diversifier_scores)
        returns_by_name = {}
        for name, path in paths.items():
            row, returns = backtest_weight_path(inputs, name, path)
            metric_rows.append(row)
            returns_by_name[name] = returns

        corr, crisis_corr, rolling_corr = correlation_rows(inputs, returns_by_name)
        corr_frames.append(corr)
        crisis_corr_frames.append(crisis_corr)
        rolling_corr_frames.append(rolling_corr)
        overlap_rows_all.extend(overlap_rows(inputs, paths))
        benchmarks_all.extend(benchmark_rows(inputs))

        metrics_so_far = pd.DataFrame([row for row in metric_rows if row["universe"] == inputs["universe_config"].name])
        gates_so_far = gate_rows(metrics_so_far, corr, crisis_corr)
        pass_names = set(gates_so_far.loc[gates_so_far["passes_hard_gate"], "sleeve"])
        if pass_names:
            for vol_name in [n for n, p in paths.items() if p["sleeve_type"] == "volatility"]:
                for div_name in pass_names:
                    for vol_weight, div_weight in BLEND_WEIGHTS:
                        blend_name = f"blend_{vol_name}_{div_name}_{int(vol_weight * 100)}_{int(div_weight * 100)}"
                        blend_path = combine_weight_paths(paths[vol_name], paths[div_name], vol_weight, div_weight)
                        row, _ = backtest_weight_path(inputs, blend_name, blend_path)
                        row["vol_sleeve"] = vol_name
                        row["diversifier_sleeve"] = div_name
                        row["vol_weight"] = vol_weight
                        row["diversifier_weight"] = div_weight
                        blend_rows.append(row)

    metrics = pd.DataFrame(metric_rows)
    blend_metrics = pd.DataFrame(blend_rows)
    corr = pd.concat(corr_frames, ignore_index=True) if corr_frames else pd.DataFrame()
    crisis_corr = pd.concat(crisis_corr_frames, ignore_index=True) if crisis_corr_frames else pd.DataFrame()
    rolling_corr = pd.concat(rolling_corr_frames, ignore_index=True) if rolling_corr_frames else pd.DataFrame()
    overlaps = pd.DataFrame(overlap_rows_all)
    benchmarks = pd.DataFrame(benchmarks_all)
    data_audit = pd.concat(audit_rows, ignore_index=True) if audit_rows else pd.DataFrame()
    gates = gate_rows(metrics, corr, crisis_corr)

    metrics.to_csv(reports_dir / "defensive_v2_metrics.csv", index=False)
    blend_metrics.to_csv(reports_dir / "defensive_v2_blend_metrics.csv", index=False)
    corr.to_csv(reports_dir / "correlation_report.csv", index=False)
    crisis_corr.to_csv(reports_dir / "crisis_corr_report.csv", index=False)
    rolling_corr.to_csv(reports_dir / "defensive_v2_rolling_corr_report.csv", index=False)
    overlaps.to_csv(reports_dir / "defensive_v2_overlap_report.csv", index=False)
    benchmarks.to_csv(reports_dir / "defensive_v2_benchmarks.csv", index=False)
    data_audit.to_csv(reports_dir / "defensive_v2_data_availability.csv", index=False)
    gates.to_csv(reports_dir / "defensive_v2_gate_report.csv", index=False)
    (reports_dir / "defensive_v2_results.md").write_text(
        render_report(metrics, blend_metrics, corr, crisis_corr, rolling_corr, overlaps, benchmarks, gates, data_audit)
    )
    logger.info("Saved Phase A.4.1 artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
