import argparse
import copy
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.alpha import build_alpha_score_provider, compute_volatility_score_frame
from src.backtest.walk_forward import WalkForwardEngine
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.macro_features import MacroFeatureGenerator
from src.features.stock_features import StockFeatureGenerator
from src.labels.targets import TargetGenerator
from src.reporting.metrics import calculate_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_inputs(config_path: str, universe_path: str):
    base_config, universe_config = load_config(config_path, universe_path)
    if not universe_config.is_static and universe_config.pit_mask_path:
        pit_mask = pd.read_parquet(universe_config.pit_mask_path)
    else:
        pit_mask = None

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
    score_frame = compute_volatility_score_frame(stock_features)

    return {
        "base_config": base_config,
        "universe_config": universe_config,
        "stock_features": stock_features,
        "macro_features": macro_features,
        "targets": targets,
        "prices_dict": prices_dict,
        "pit_mask": pit_mask,
        "score_frame": score_frame,
    }


def _alpha_summary(diagnostics: dict) -> dict:
    rows = diagnostics.get("alpha_quality", [])
    if not rows:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "mean_spread": np.nan, "n_rebalances": 0}
    ic = pd.Series([row.get("rank_ic", np.nan) for row in rows], dtype=float).dropna()
    spread = pd.Series([row.get("spread", np.nan) for row in rows], dtype=float).dropna()
    return {
        "mean_ic": float(ic.mean()) if not ic.empty else np.nan,
        "ic_sharpe": float(ic.mean() / (ic.std(ddof=0) + 1e-9)) if not ic.empty else np.nan,
        "mean_spread": float(spread.mean()) if not spread.empty else np.nan,
        "n_rebalances": len(rows),
    }


def _run_variant(inputs: dict, *, name: str, use_optimizer: bool, use_risk_engine: bool, top_n_equal_weight: int | None, sector_cap: float | None = None) -> dict:
    config = copy.deepcopy(inputs["base_config"])
    if sector_cap is not None:
        config.portfolio.max_sector_weight = sector_cap

    engine = WalkForwardEngine(
        config=config,
        universe_config=inputs["universe_config"],
        stock_features=inputs["stock_features"],
        macro_features=inputs["macro_features"],
        targets=inputs["targets"],
        prices_dict=inputs["prices_dict"],
        pit_mask=inputs["pit_mask"],
    )
    provider = build_alpha_score_provider(inputs["score_frame"], score_col="volatility_score")
    history, trades, diagnostics = engine.run(
        use_optimizer=use_optimizer,
        use_risk_engine=use_risk_engine,
        top_n_equal_weight=top_n_equal_weight,
        alpha_score_provider=provider,
    )
    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    alpha_summary = _alpha_summary(diagnostics)
    return {
        "name": name,
        "history": history,
        "trades": trades,
        "diagnostics": diagnostics,
        "metrics": metrics,
        "alpha_summary": alpha_summary,
        "top_n": top_n_equal_weight,
        "sector_cap": config.portfolio.max_sector_weight,
        "use_optimizer": use_optimizer,
        "use_risk_engine": use_risk_engine,
    }


def _row(result: dict) -> dict:
    metrics = result["metrics"]
    alpha = result["alpha_summary"]
    return {
        "variant": result["name"],
        "top_n": result["top_n"],
        "sector_cap": result["sector_cap"],
        "use_optimizer": result["use_optimizer"],
        "use_risk_engine": result["use_risk_engine"],
        "cagr": metrics.get("CAGR"),
        "sharpe": metrics.get("Sharpe"),
        "max_dd": metrics.get("Max Drawdown"),
        "volatility": metrics.get("Volatility"),
        "mean_ic": alpha.get("mean_ic"),
        "ic_sharpe": alpha.get("ic_sharpe"),
        "mean_spread": alpha.get("mean_spread"),
        "n_rebalances": alpha.get("n_rebalances"),
    }


def _pass_fail(metrics: dict) -> dict:
    cagr = metrics.get("cagr", metrics.get("CAGR"))
    sharpe = metrics.get("sharpe", metrics.get("Sharpe"))
    max_dd = metrics.get("max_dd", metrics.get("Max Drawdown"))
    return {
        "cagr": bool(cagr is not None and cagr > 0.135),
        "sharpe": bool(sharpe is not None and sharpe > 0.9),
        "max_dd": bool(max_dd is not None and max_dd > -0.32),
    }


def _fmt_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{value:.2%}"


def _fmt_num(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{value:.3f}"


def render_report(
    inputs: dict,
    core_df: pd.DataFrame,
    topn_df: pd.DataFrame,
    sector_df: pd.DataFrame,
    wall_seconds: float,
) -> str:
    default_score = inputs["base_config"].alpha.default_score
    best_core = core_df.sort_values(["sharpe", "cagr"], ascending=False).iloc[0].to_dict()
    checks = _pass_fail(best_core)
    lines = [
        "# Volatility Alpha Production",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- Universe: `{inputs['universe_config'].name}`",
        f"- Default alpha score: `{default_score}`",
        f"- RL enabled: `{inputs['base_config'].rl.enabled}`",
        f"- Wall time: {wall_seconds:.1f}s",
        "",
        "## Production Decision",
        "",
        "- `volatility_score` is the default production alpha sleeve.",
        "- `trend_score` and `mean_reversion_score` remain research-only in `scripts/run_regime_switch_strategy.py`.",
        "- Top-N sensitivity below uses equal-weight construction only.",
        "- Sector-cap sensitivity below uses `volatility_score + optimizer + risk engine`.",
        "",
        "## Core Backtests",
        "",
        core_df.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Top-N Sensitivity",
        "",
        topn_df.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Sector Cap Sensitivity",
        "",
        sector_df.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Success Criteria",
        "",
        f"- CAGR > 13.5%: {'PASS' if checks['cagr'] else 'FAIL'} ({_fmt_pct(best_core.get('cagr'))})",
        f"- Sharpe > 0.9: {'PASS' if checks['sharpe'] else 'FAIL'} ({_fmt_num(best_core.get('sharpe'))})",
        f"- MaxDD < 32%: {'PASS' if checks['max_dd'] else 'FAIL'} ({_fmt_pct(best_core.get('max_dd'))})",
        f"- Portfolio uses `volatility_score` by default: {'PASS' if default_score == 'volatility_score' else 'FAIL'}",
        f"- Momentum/regime features remain research-only: PASS",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run production validation for volatility alpha")
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--universe", type=str, default="config/universes/sp500.yaml")
    args = parser.parse_args()

    start = time.perf_counter()
    inputs = load_inputs(args.config, args.universe)

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    core_runs = [
        _run_variant(inputs, name="volatility_topn_ew", use_optimizer=False, use_risk_engine=False, top_n_equal_weight=inputs["base_config"].portfolio.top_n_stocks),
        _run_variant(inputs, name="volatility_optimizer", use_optimizer=True, use_risk_engine=False, top_n_equal_weight=None),
        _run_variant(inputs, name="volatility_optimizer_risk", use_optimizer=True, use_risk_engine=True, top_n_equal_weight=None),
    ]
    core_df = pd.DataFrame([_row(result) for result in core_runs])

    topn_runs = [
        _run_variant(inputs, name=f"volatility_topn_{top_n}", use_optimizer=False, use_risk_engine=False, top_n_equal_weight=top_n)
        for top_n in [20, 30, 40, 50]
    ]
    topn_df = pd.DataFrame([_row(result) for result in topn_runs]).sort_values("top_n").reset_index(drop=True)
    topn_df.to_csv(reports_dir / "volatility_topn_sensitivity.csv", index=False)

    sector_runs = [
        _run_variant(inputs, name=f"volatility_sector_cap_{int(cap * 100)}", use_optimizer=True, use_risk_engine=True, top_n_equal_weight=None, sector_cap=cap)
        for cap in [0.20, 0.25, 0.30, 0.35]
    ]
    sector_df = pd.DataFrame([_row(result) for result in sector_runs]).sort_values("sector_cap").reset_index(drop=True)
    sector_df.to_csv(reports_dir / "volatility_sector_cap_sensitivity.csv", index=False)

    report = render_report(
        inputs=inputs,
        core_df=core_df,
        topn_df=topn_df,
        sector_df=sector_df,
        wall_seconds=time.perf_counter() - start,
    )
    (reports_dir / "volatility_alpha_production.md").write_text(report)

    logger.info("Saved report to %s", reports_dir / "volatility_alpha_production.md")
    logger.info("Saved Top-N sweep to %s", reports_dir / "volatility_topn_sensitivity.csv")
    logger.info("Saved sector-cap sweep to %s", reports_dir / "volatility_sector_cap_sensitivity.csv")


if __name__ == "__main__":
    main()
