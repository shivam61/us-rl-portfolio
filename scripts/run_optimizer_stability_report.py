import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.alpha import build_alpha_score_provider, compute_volatility_score_frame
from src.backtest.walk_forward import WalkForwardEngine
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.macro_features import MacroFeatureGenerator
from src.features.stock_features import StockFeatureGenerator
from src.labels.targets import TargetGenerator
from src.reporting.metrics import calculate_metrics


def load_inputs(config_path: str, universe_path: str):
    base_config, universe_config = load_config(config_path, universe_path)
    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(
        set(
            list(universe_config.tickers.keys())
            + universe_config.sector_etfs
            + universe_config.macro_etfs
            + [universe_config.benchmark, universe_config.vix_proxy]
        )
    )
    data_dict = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)
    prices_dict = ingestion.build_all_matrices(data_dict)
    sector_mapping = dict(universe_config.tickers)
    stock_features = StockFeatureGenerator(
        data_dict,
        benchmark_ticker=universe_config.benchmark,
        sector_mapping=sector_mapping,
    ).generate()
    macro_features = MacroFeatureGenerator(
        data_dict,
        benchmark_ticker=universe_config.benchmark,
        vix_proxy=universe_config.vix_proxy,
    ).generate()
    targets = TargetGenerator(
        data_dict,
        forward_horizon=21,
        sector_mapping=sector_mapping,
    ).generate()
    pit_mask = pd.read_parquet(universe_config.pit_mask_path) if (not universe_config.is_static and universe_config.pit_mask_path) else None
    return base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask


def main():
    parser = argparse.ArgumentParser(description="Run optimizer stability report")
    parser.add_argument("--config", type=str, default="config/baseline_v1_volatility_score_sp100.yaml")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml")
    args = parser.parse_args()

    base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask = load_inputs(
        args.config, args.universe
    )
    score_frame = compute_volatility_score_frame(stock_features)
    engine = WalkForwardEngine(
        config=base_config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices_dict=prices_dict,
        pit_mask=pit_mask,
    )
    history, _, diagnostics = engine.run(
        use_optimizer=True,
        use_risk_engine=True,
        top_n_equal_weight=None,
        alpha_score_provider=build_alpha_score_provider(score_frame, "volatility_score"),
    )

    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    optimizer_stats = pd.DataFrame(diagnostics.get("optimizer_stats", []))
    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    fallback_counts = {}
    if not optimizer_stats.empty and "fallback_level" in optimizer_stats.columns:
        fallback_counts = optimizer_stats["fallback_level"].value_counts(dropna=False).to_dict()

    worst_condition_rows = pd.DataFrame()
    if not optimizer_stats.empty and "cov_condition_number" in optimizer_stats.columns:
        worst_condition_rows = optimizer_stats.sort_values("cov_condition_number", ascending=False).head(10)

    equal_weight_fallbacks = pd.DataFrame()
    if not optimizer_stats.empty and "fallback_level" in optimizer_stats.columns:
        equal_weight_fallbacks = optimizer_stats[optimizer_stats["fallback_level"] == "equal_weight_top_n"].head(10)

    run_id = datetime.now(timezone.utc).strftime("optimizer_stability_%Y%m%dT%H%M%SZ")
    lines = [
        "# Optimizer Stability",
        "",
        f"- Run ID: `{run_id}`",
        f"- Config: `{args.config}`",
        f"- Universe: `{args.universe}`",
        f"- Default alpha: `{base_config.alpha.default_score}`",
        "",
        "## Strategy Metrics",
        "",
        f"- CAGR: `{metrics.get('CAGR', float('nan')):.2%}`",
        f"- Sharpe: `{metrics.get('Sharpe', float('nan')):.3f}`",
        f"- MaxDD: `{metrics.get('Max Drawdown', float('nan')):.2%}`",
        "",
        "## Fallback Counts",
        "",
    ]

    if fallback_counts:
        for key, value in fallback_counts.items():
            lines.append(f"- `{key}`: {value}")
    else:
        lines.append("- No optimizer diagnostics captured")

    if not optimizer_stats.empty:
        lines.extend(
            [
                "",
                "## Aggregate Diagnostics",
                "",
                f"- Rebalances: `{len(optimizer_stats)}`",
                f"- Max covariance condition number: `{optimizer_stats['cov_condition_number'].max():.3e}`",
                f"- Median covariance condition number: `{optimizer_stats['cov_condition_number'].median():.3e}`",
                f"- Max stock-weight overage: `{optimizer_stats['constraint_violations'].map(lambda x: x.get('max_weight_overage', float('nan')) if isinstance(x, dict) else float('nan')).max():.3e}`",
                f"- Max sector-cap overage: `{optimizer_stats['constraint_violations'].map(lambda x: x.get('sector_cap_overage', float('nan')) if isinstance(x, dict) else float('nan')).max():.3e}`",
                f"- Max turnover overage: `{optimizer_stats['constraint_violations'].map(lambda x: x.get('turnover_overage', float('nan')) if isinstance(x, dict) else float('nan')).max():.3e}`",
            ]
        )

    if not worst_condition_rows.empty:
        lines.extend(
            [
                "",
                "## Worst Condition Numbers",
                "",
                worst_condition_rows[
                    ["date", "fallback_level", "cov_condition_number", "num_assets", "gross_raw"]
                ].to_markdown(index=False, floatfmt=".4e"),
            ]
        )

    if not equal_weight_fallbacks.empty:
        lines.extend(
            [
                "",
                "## Equal-Weight Fallback Samples",
                "",
                equal_weight_fallbacks[
                    ["date", "cov_condition_number", "num_assets", "gross_raw"]
                ].to_markdown(index=False, floatfmt=".4e"),
            ]
        )

    (reports_dir / "optimizer_stability.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
