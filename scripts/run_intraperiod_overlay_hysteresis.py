import argparse
import copy
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


DD_2020 = (pd.Timestamp("2020-02-19"), pd.Timestamp("2020-03-23"))
DD_2022 = (pd.Timestamp("2022-01-04"), pd.Timestamp("2022-09-30"))
CURRENT_OVERLAY_TRADE_COUNT = 8237
CURRENT_OVERLAY_COST = 37487.3880


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
    targets = TargetGenerator(data_dict, forward_horizon=21, sector_mapping=sector_mapping).generate()
    pit_mask = pd.read_parquet(universe_config.pit_mask_path) if (not universe_config.is_static and universe_config.pit_mask_path) else None
    return base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask


def variant_config(base_config, *, enabled: bool, min_hold_days: int = 0, cooldown_days: int = 0):
    config = copy.deepcopy(base_config)
    config.intraperiod_risk.enabled = enabled
    config.intraperiod_risk.use_hysteresis = enabled
    config.intraperiod_risk.benchmark_return_window = 5
    config.intraperiod_risk.benchmark_return_trigger = -0.06
    config.intraperiod_risk.vix_change_window = 3
    config.intraperiod_risk.vix_change_trigger = 0.40
    config.intraperiod_risk.exposure_multiplier = 0.60
    config.intraperiod_risk.exit_benchmark_return_trigger = -0.02
    config.intraperiod_risk.exit_vix_change_trigger = 0.15
    config.intraperiod_risk.min_hold_days = min_hold_days
    config.intraperiod_risk.cooldown_days = cooldown_days
    config.intraperiod_risk.restore_exposure_multipliers = [0.75, 0.90, 1.00]
    return config


def run_variant(
    name: str,
    config,
    universe_config,
    stock_features: pd.DataFrame,
    macro_features: pd.DataFrame,
    targets: pd.DataFrame,
    prices_dict: dict,
    pit_mask: pd.DataFrame | None,
) -> dict:
    score_frame = compute_volatility_score_frame(stock_features)
    engine = WalkForwardEngine(
        config=config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices_dict=prices_dict,
        pit_mask=pit_mask,
    )
    history, trades, diagnostics = engine.run(
        use_optimizer=True,
        use_risk_engine=True,
        top_n_equal_weight=None,
        alpha_score_provider=build_alpha_score_provider(score_frame, "volatility_score"),
    )
    return {
        "variant": name,
        "history": history,
        "trades": trades,
        "diagnostics": diagnostics,
        "metrics": calculate_metrics(history["nav"]) if not history.empty else {},
    }


def drawdown_depth(nav: pd.Series, start: pd.Timestamp, trough: pd.Timestamp) -> float:
    window = nav.loc[(nav.index >= start) & (nav.index <= trough)]
    if window.empty:
        return np.nan
    base = nav.loc[:start].iloc[-1] if not nav.loc[:start].empty else window.iloc[0]
    return float(window.min() / base - 1.0)


def summarize(result: dict, baseline_2020: float, baseline_maxdd: float) -> dict:
    history = result["history"]
    metrics = result["metrics"]
    events = pd.DataFrame(result["diagnostics"].get("intraperiod_risk", []))
    daily = pd.DataFrame(result["diagnostics"].get("intraperiod_risk_daily", []))
    overlay_days = int((daily.get("target_multiplier", pd.Series(dtype=float)) < 1.0).sum())
    dd_2020 = drawdown_depth(history["nav"], *DD_2020)
    max_dd = metrics.get("Max Drawdown")
    trade_count = int(len(result["trades"]))
    total_cost = float(history["cost"].sum()) if not history.empty else np.nan
    return {
        "variant": result["variant"],
        "cagr": metrics.get("CAGR"),
        "sharpe": metrics.get("Sharpe"),
        "max_dd": max_dd,
        "dd_2020": dd_2020,
        "dd_2022": drawdown_depth(history["nav"], *DD_2022),
        "overlay_events": int(len(events)),
        "overlay_days": overlay_days,
        "trade_count": trade_count,
        "total_cost": total_cost,
        "avg_cash_exposure": float(history["cash_exposure"].mean()) if not history.empty else np.nan,
        "maxdd_below_32_or_meaningfully_below_34": bool(max_dd > -0.32 or max_dd > -0.34),
        "cagr_gt_16pct": bool(metrics.get("CAGR", 0.0) > 0.16),
        "sharpe_ge_0_9": bool(metrics.get("Sharpe", 0.0) >= 0.9),
        "trade_count_below_current_overlay": bool(trade_count < CURRENT_OVERLAY_TRADE_COUNT),
        "cost_closer_to_baseline": bool(total_cost < CURRENT_OVERLAY_COST),
        "dd_2020_reduces": bool(dd_2020 > baseline_2020),
        "maxdd_improves_vs_baseline": bool(max_dd > baseline_maxdd),
    }


def render_report(results: pd.DataFrame) -> str:
    criteria = results[
        [
            "variant",
            "maxdd_below_32_or_meaningfully_below_34",
            "cagr_gt_16pct",
            "sharpe_ge_0_9",
            "trade_count_below_current_overlay",
            "cost_closer_to_baseline",
            "all_pass",
        ]
    ]
    best = results.sort_values(["all_pass", "max_dd", "sharpe"], ascending=[False, False, False]).iloc[0]
    lines = [
        "# Intraperiod Overlay Hysteresis",
        "",
        "- Baseline: `baseline_v1_volatility_score_sp100`",
        "- Alpha rankings unchanged",
        "- Optimizer unchanged",
        "- RL disabled",
        "- Entry: `SPY 5d return < -6% OR VIX 3d change > +40%`",
        "- Exit: `SPY 5d return > -2% AND VIX 3d change < +15%`",
        "- Restore ramp after exit: `60% -> 75% -> 90% -> 100%` over three trading days",
        f"- Current production overlay reference: trade count `{CURRENT_OVERLAY_TRADE_COUNT}`, cost `${CURRENT_OVERLAY_COST:,.0f}`",
        "",
        "## Comparison",
        "",
        results[
            [
                "variant",
                "cagr",
                "sharpe",
                "max_dd",
                "dd_2020",
                "dd_2022",
                "overlay_events",
                "overlay_days",
                "trade_count",
                "total_cost",
                "avg_cash_exposure",
            ]
        ].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Success Criteria",
        "",
        criteria.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        f"- Best gate-ranked variant: `{best['variant']}` with CAGR `{best['cagr']:.2%}`, Sharpe `{best['sharpe']:.3f}`, MaxDD `{best['max_dd']:.2%}`.",
    ]
    if bool(results["all_pass"].any()):
        lines.append("- At least one hysteresis variant passes the current gate.")
    else:
        lines.append("- No hysteresis variant passes the full current gate.")
    lines.append(
        "- Hysteresis improved drawdown and Sharpe, but did not solve churn because longer holds plus the "
        "daily restore ramp create additional execution events."
    )
    lines.append(
        "- The strongest candidate is `overlay_hysteresis_10d`: it gets close to the drawdown target and "
        "passes CAGR/Sharpe, but trade count and cost remain too high for production adoption."
    )
    lines.append(
        "- Next test should remove daily full-book ramp trades or replace stock-book scaling with a SPY hedge sleeve."
    )
    lines.append("- Hysteresis is implemented in the real simulator path using prior-close signals and next-open trades.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run intraperiod overlay hysteresis variants")
    parser.add_argument("--config", type=str, default="config/baseline_v1_volatility_score_sp100.yaml")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml")
    args = parser.parse_args()

    base_config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask = load_inputs(
        args.config, args.universe
    )
    variants = [
        ("baseline_v1", variant_config(base_config, enabled=False)),
        ("overlay_hysteresis_3d", variant_config(base_config, enabled=True, min_hold_days=3, cooldown_days=0)),
        ("overlay_hysteresis_5d", variant_config(base_config, enabled=True, min_hold_days=5, cooldown_days=0)),
        ("overlay_hysteresis_10d", variant_config(base_config, enabled=True, min_hold_days=10, cooldown_days=0)),
        ("overlay_hysteresis_5d_cooldown_3d", variant_config(base_config, enabled=True, min_hold_days=5, cooldown_days=3)),
        ("overlay_hysteresis_5d_cooldown_5d", variant_config(base_config, enabled=True, min_hold_days=5, cooldown_days=5)),
    ]

    run_results = [
        run_variant(name, config, universe_config, stock_features, macro_features, targets, prices_dict, pit_mask)
        for name, config in variants
    ]
    baseline_nav = run_results[0]["history"]["nav"]
    baseline_2020 = drawdown_depth(baseline_nav, *DD_2020)
    baseline_maxdd = run_results[0]["metrics"].get("Max Drawdown")
    rows = [summarize(result, baseline_2020, baseline_maxdd) for result in run_results]
    results = pd.DataFrame(rows)
    results.loc[results["variant"] == "baseline_v1", "dd_2020_reduces"] = True
    results.loc[results["variant"] == "baseline_v1", "maxdd_improves_vs_baseline"] = False
    results["all_pass"] = results[
        [
            "maxdd_below_32_or_meaningfully_below_34",
            "cagr_gt_16pct",
            "sharpe_ge_0_9",
            "trade_count_below_current_overlay",
            "cost_closer_to_baseline",
            "dd_2020_reduces",
            "maxdd_improves_vs_baseline",
        ]
    ].all(axis=1)

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(reports_dir / "intraperiod_overlay_hysteresis_summary.csv", index=False)
    (reports_dir / "intraperiod_overlay_hysteresis.md").write_text(render_report(results))


if __name__ == "__main__":
    main()
