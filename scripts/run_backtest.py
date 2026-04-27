import argparse
import logging
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

from src.config.loader import load_config
from src.backtest.walk_forward import WalkForwardEngine
from src.data.ingestion import DataIngestion
from src.backtest.baselines import BaselineEngine
from src.reporting.metrics import calculate_metrics, calculate_annual_returns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_data(base_config, universe_config):
    cache_dir    = Path(base_config.data.cache_dir)
    features_dir = cache_dir / "features"
    stock_features = pd.read_parquet(features_dir / "stock_features.parquet")
    macro_features = pd.read_parquet(features_dir / "macro_features.parquet")
    targets        = pd.read_parquet(features_dir / "targets.parquet")

    pit_mask = None
    if not universe_config.is_static and universe_config.pit_mask_path:
        pit_mask = pd.read_parquet(universe_config.pit_mask_path)

    ingestion   = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(set(
        list(universe_config.tickers.keys()) +
        universe_config.macro_etfs + universe_config.sector_etfs + [universe_config.benchmark]
    ))
    data_dict   = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)
    prices_dict = ingestion.build_all_matrices(data_dict)

    return stock_features, macro_features, targets, prices_dict, pit_mask


def run_single(base_config, universe_config, out_dir: Path, label: str = "Strategy"):
    if universe_config.is_static:
        logger.warning("!!! STATIC UNIVERSE: survivorship bias present !!!")

    stock_features, macro_features, targets, prices_dict, pit_mask = _load_data(
        base_config, universe_config
    )

    engine = WalkForwardEngine(
        config=base_config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices_dict=prices_dict,
        pit_mask=pit_mask
    )

    history, trades, _ = engine.run(
        use_optimizer=True,
        use_risk_engine=True,
        top_n_equal_weight=base_config.portfolio.top_n_stocks
    )

    baseline_engine = BaselineEngine(base_config, universe_config, prices_dict)
    rebalance_dates = engine.generate_rebalance_dates()
    baselines_df    = baseline_engine.run_baselines(rebalance_dates)

    if not history.empty:
        history = history.join(baselines_df, how="left").ffill()

    out_dir.mkdir(parents=True, exist_ok=True)
    history.to_csv(out_dir / "daily_nav.csv")
    trades.to_csv(out_dir  / "trades.csv")

    metrics = {}
    diagnostics = {}
    if not history.empty:
        metrics[label] = calculate_metrics(history["nav"])
        for col in ["SPY_BnH", "Equal_Weight"]:
            if col in history.columns:
                metrics[col] = calculate_metrics(history[col])

        diagnostics = {
            "Total_TC_Drag":       float(history["tc_drag"].sum()),
            "Total_Slippage_Drag": float(history["slippage_drag"].sum()),
            "Average_Turnover":    float(history[history["turnover"] > 0]["turnover"].mean()),
            "Annual_Returns":      calculate_annual_returns(history["nav"])
        }

        with open(out_dir / "metrics.json",     "w") as f: json.dump(metrics,      f, indent=4)
        with open(out_dir / "diagnostics.json", "w") as f: json.dump(diagnostics,  f, indent=4)

        logger.info(f"[{label}] CAGR={metrics[label].get('CAGR',0):.2%}  "
                    f"Sharpe={metrics[label].get('Sharpe',0):.2f}  "
                    f"MaxDD={metrics[label].get('Max Drawdown',0):.2%}")

    report = [
        f"# Backtest Report — {label}",
        f"Run: {out_dir.name}",
        "",
        "## Config",
        f"- Universe: {universe_config.name}  |  tickers: {len(universe_config.tickers)}",
        f"- PIT mask: {'yes' if not universe_config.is_static else 'NO (survivorship bias)'}",
        f"- Top-N stocks: {base_config.portfolio.top_n_stocks}",
        f"- Capital: ${base_config.portfolio.initial_capital:,.0f}",
        "",
        "## Performance",
        "```json",
        json.dumps(metrics,      indent=2),
        "```",
        "## Diagnostics",
        "```json",
        json.dumps(diagnostics,  indent=2),
        "```",
    ]
    (out_dir / "report.md").write_text("\n".join(report))
    return metrics, history


def main():
    parser = argparse.ArgumentParser(description="Run Portfolio Backtest")
    parser.add_argument("--config",           type=str, required=True)
    parser.add_argument("--universe",         type=str, default="config/universes/sp100.yaml")
    parser.add_argument("--compare-universe", type=str, default=None,
                        help="Second universe for side-by-side comparison")
    args = parser.parse_args()

    run_id       = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_out     = Path("data/artifacts/runs") / run_id
    base_config, universe_config = load_config(args.config, args.universe)

    metrics_a, hist_a = run_single(base_config, universe_config, base_out / "primary", "Strategy_A")

    if args.compare_universe:
        _, universe_config_b = load_config(args.config, args.compare_universe)
        metrics_b, hist_b = run_single(base_config, universe_config_b,
                                       base_out / "compare", "Strategy_B")

        rows = []
        for key in ["CAGR", "Sharpe", "Max Drawdown", "Volatility", "Calmar"]:
            va = metrics_a.get("Strategy_A", {}).get(key, "")
            vb = metrics_b.get("Strategy_B", {}).get(key, "")
            rows.append({"Metric": key, "Universe_A": va, "Universe_B": vb})
        comparison = pd.DataFrame(rows)
        comparison.to_csv(base_out / "universe_comparison.csv", index=False)
        logger.info(f"\n{comparison.to_string(index=False)}")

    logger.info(f"Done. Artifacts in {base_out}")


if __name__ == "__main__":
    main()
