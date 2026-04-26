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

def run_experiment(name, engine, **kwargs):
    logger.info(f"Running Experiment: {name}")
    history, trades, diagnostics = engine.run(**kwargs)
    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    return {
        "name": name,
        "metrics": metrics,
        "diagnostics": diagnostics,
        "history": history
    }

def main():
    parser = argparse.ArgumentParser(description="Run Portfolio Diagnostics")
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml")
    args = parser.parse_args()
    
    base_config, universe_config = load_config(args.config, args.universe)
    
    # Create diagnostic directory
    diag_dir = Path("data/artifacts/diagnostics") / datetime.now().strftime("%Y%m%d_%H%M%S")
    diag_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Loading features and data...")
    cache_dir = Path(base_config.data.cache_dir)
    features_dir = cache_dir / "features"
    
    stock_features = pd.read_parquet(features_dir / "stock_features.parquet")
    macro_features = pd.read_parquet(features_dir / "macro_features.parquet")
    targets = pd.read_parquet(features_dir / "targets.parquet")
    
    pit_mask = None
    if not universe_config.is_static and universe_config.pit_mask_path:
        pit_mask = pd.read_parquet(universe_config.pit_mask_path)
    
    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(set(list(universe_config.tickers.keys()) + universe_config.macro_etfs + universe_config.sector_etfs + [universe_config.benchmark]))
    data_dict = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)
    prices_dict = ingestion.build_all_matrices(data_dict)
    
    def get_engine():
        return WalkForwardEngine(
            config=base_config,
            universe_config=universe_config,
            stock_features=stock_features,
            macro_features=macro_features,
            targets=targets,
            prices_dict=prices_dict,
            pit_mask=pit_mask
        )

    results = []

    # 1. Equal Weight PIT Universe (Baseline)
    results.append(run_experiment("Equal_Weight_Universe", get_engine(), use_optimizer=False, use_risk_engine=False))

    # 2. Alpha Only, Top-20 Equal Weight (Selection only)
    results.append(run_experiment("Alpha_Top20_EW", get_engine(), use_optimizer=False, use_risk_engine=False, top_n_equal_weight=20))

    # 3. Alpha + Optimizer (No Risk Engine)
    results.append(run_experiment("Alpha_Opt_NoRisk", get_engine(), use_optimizer=True, use_risk_engine=False))

    # 4. Alpha + Optimizer + Risk Engine (Full System)
    full_sys = run_experiment("Full_System", get_engine(), use_optimizer=True, use_risk_engine=True)
    results.append(full_sys)

    # --- Optimizer Sensitivity ---
    sensitivity_results = []
    # Test different risk_aversion (implicitly via modifying config before get_engine)
    # This is a bit hacky but works for a diagnostic script
    orig_ra = base_config.portfolio.max_turnover # Not risk_aversion, but let's try turnover
    for turnover in [0.3, 0.5, 0.8]:
        base_config.portfolio.max_turnover = turnover
        res = run_experiment(f"Opt_Turnover_{turnover}", get_engine(), use_optimizer=True, use_risk_engine=False)
        sensitivity_results.append({
            "turnover_limit": turnover,
            "cagr": res["metrics"].get("CAGR"),
            "sharpe": res["metrics"].get("Sharpe"),
            "max_dd": res["metrics"].get("Max Drawdown")
        })
    base_config.portfolio.max_turnover = orig_ra # Reset

    # --- Reporting ---
    
    # Ablation CSV
    ablation_df = pd.DataFrame([
        {
            "Experiment": r["name"],
            "CAGR": r["metrics"].get("CAGR"),
            "Sharpe": r["metrics"].get("Sharpe"),
            "MaxDD": r["metrics"].get("Max Drawdown"),
            "Volatility": r["metrics"].get("Volatility")
        } for r in results
    ])
    ablation_df.to_csv(diag_dir / "ablation_results.csv", index=False)

    # Sensitivity CSV
    pd.DataFrame(sensitivity_results).to_csv(diag_dir / "optimizer_sensitivity.csv", index=False)

    # Risk Intervention Log (from Full System)
    risk_log = pd.DataFrame(full_sys["diagnostics"]["risk_interventions"])
    risk_log.to_csv(diag_dir / "risk_intervention_log.csv", index=False)

    # Alpha Quality (from Full System)
    alpha_q = full_sys["diagnostics"]["alpha_quality"]
    with open(diag_dir / "alpha_quality.json", "w") as f:
        json.dump(alpha_q, f, indent=4)

    # Exposure Stats (from Full System)
    exposure_df = pd.DataFrame(full_sys["diagnostics"]["exposure"])
    
    # Summary Report
    avg_exposure = exposure_df["gross_exposure"].mean()
    pct_risk_active = (len(risk_log) / len(exposure_df)) if not exposure_df.empty else 0
    
    summary = [
        "# Diagnostic Summary",
        f"Generated at: {datetime.now()}",
        "",
        "## Exposure Metrics (Full System)",
        f"- Average Gross Exposure: {avg_exposure:.2%}",
        f"- Average Cash %: {exposure_df['cash_pct'].mean():.2%}",
        f"- Max Cash %: {exposure_df['cash_pct'].max():.2%}",
        f"- Average Holdings: {exposure_df['num_holdings'].mean():.1f}",
        f"- % Rebalances with Risk Intervention: {pct_risk_active:.2%}",
        "",
        "## Key Findings",
    ]
    
    if avg_exposure < 0.5:
        summary.append("- **CASH DRAG DETECTED**: Average exposure is significantly below 100%.")
    
    # Compare EW vs Alpha_EW
    ew_cagr = ablation_df[ablation_df["Experiment"]=="Equal_Weight_Universe"]["CAGR"].values[0]
    alpha_ew_cagr = ablation_df[ablation_df["Experiment"]=="Alpha_Top20_EW"]["CAGR"].values[0]
    
    if alpha_ew_cagr > ew_cagr:
        summary.append(f"- **ALPHA IS POSITIVE**: Alpha selection (Top 20) outperformed Equal Weight ({alpha_ew_cagr:.2%} vs {ew_cagr:.2%}).")
    else:
        summary.append(f"- **ALPHA IS WEAK**: Alpha selection underperformed Equal Weight ({alpha_ew_cagr:.2%} vs {ew_cagr:.2%}).")

    # Optimizer suppression
    opt_no_risk_cagr = ablation_df[ablation_df["Experiment"]=="Alpha_Opt_NoRisk"]["CAGR"].values[0]
    if opt_no_risk_cagr < alpha_ew_cagr:
        summary.append(f"- **OPTIMIZER SUPPRESSION**: Optimizer reduced CAGR from {alpha_ew_cagr:.2%} (EW) to {opt_no_risk_cagr:.2%}.")

    with open(diag_dir / "diagnostic_summary.md", "w") as f:
        f.write("\n".join(summary))

    logger.info(f"Diagnostics complete. Results in {diag_dir}")

if __name__ == "__main__":
    main()
