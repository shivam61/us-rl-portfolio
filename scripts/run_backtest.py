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

def main():
    parser = argparse.ArgumentParser(description="Run Portfolio Backtest")
    parser.add_argument("--config", type=str, required=True, help="Path to base config")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml", help="Path to universe config")
    args = parser.parse_args()
    
    base_config, universe_config = load_config(args.config, args.universe)
    
    # Create unique run directory
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifacts_dir = Path("data/artifacts/runs") / run_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Static universe warning
    pit_mask = None
    if universe_config.is_static:
        logger.warning("!!! STATIC UNIVERSE DETECTED: This backtest contains survivorship bias. !!!")
    else:
        if universe_config.pit_mask_path:
            logger.info(f"Loading PIT universe mask from {universe_config.pit_mask_path}")
            pit_mask = pd.read_parquet(universe_config.pit_mask_path)
        else:
            logger.warning("is_static is False but no pit_mask_path provided in universe config. Falling back to static universe.")
        
    logger.info("Loading features and data...")
    cache_dir = Path(base_config.data.cache_dir)
    features_dir = cache_dir / "features"
    
    stock_features = pd.read_parquet(features_dir / "stock_features.parquet")
    macro_features = pd.read_parquet(features_dir / "macro_features.parquet")
    targets = pd.read_parquet(features_dir / "targets.parquet")
    
    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(set(list(universe_config.tickers.keys()) + universe_config.macro_etfs + universe_config.sector_etfs + [universe_config.benchmark]))
    data_dict = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)
    prices_dict = ingestion.build_all_matrices(data_dict)
    
    logger.info("Initializing Walk-Forward Engine...")
    engine = WalkForwardEngine(
        config=base_config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices_dict=prices_dict,
        pit_mask=pit_mask
    )
    
    history, trades = engine.run()
    
    logger.info("Running Baselines...")
    baseline_engine = BaselineEngine(base_config, universe_config, prices_dict)
    rebalance_dates = engine.generate_rebalance_dates()
    baselines_df = baseline_engine.run_baselines(rebalance_dates)
    
    # Merge history with baselines
    if not history.empty:
        history = history.join(baselines_df, how="left").ffill()
    
    logger.info("Saving artifacts...")
    history.to_csv(artifacts_dir / "daily_nav.csv")
    trades.to_csv(artifacts_dir / "trades.csv")
    
    # Calculate Metrics
    metrics = {}
    if not history.empty:
        metrics["Strategy"] = calculate_metrics(history["nav"])
        if "SPY_BnH" in history.columns:
            metrics["SPY_BnH"] = calculate_metrics(history["SPY_BnH"])
        if "Equal_Weight" in history.columns:
            metrics["Equal_Weight"] = calculate_metrics(history["Equal_Weight"])
            
        diagnostics = {
            "Total_TC_Drag": float(history["tc_drag"].sum()),
            "Total_Slippage_Drag": float(history["slippage_drag"].sum()),
            "Average_Turnover": float(history[history["turnover"] > 0]["turnover"].mean()),
            "Annual_Returns": calculate_annual_returns(history["nav"])
        }
        
        with open(artifacts_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)
            
        with open(artifacts_dir / "diagnostics.json", "w") as f:
            json.dump(diagnostics, f, indent=4)
            
        logger.info(f"Strategy Sharpe: {metrics['Strategy'].get('Sharpe', 0):.2f}")
        logger.info(f"SPY Sharpe: {metrics.get('SPY_BnH', {}).get('Sharpe', 0):.2f}")
    
    # Write Report
    report_lines = [
        "# Backtest Report",
        f"Run ID: {run_id}",
        "",
        "## Configuration",
        f"- Static Universe: {universe_config.is_static} (WARNING: Survivorship Bias!)" if universe_config.is_static else "- Point-in-time Universe: True",
        f"- Max Participation Rate: {base_config.execution.max_participation_rate}",
        f"- Initial Capital: {base_config.portfolio.initial_capital}",
        "",
        "## Performance",
        "```json",
        json.dumps(metrics, indent=2),
        "```",
        "",
        "## Diagnostics",
        "```json",
        json.dumps(diagnostics if not history.empty else {}, indent=2),
        "```"
    ]
    with open(artifacts_dir / "report.md", "w") as f:
        f.write("\n".join(report_lines))

    logger.info(f"Done. Artifacts saved to {artifacts_dir}")

if __name__ == "__main__":
    main()
