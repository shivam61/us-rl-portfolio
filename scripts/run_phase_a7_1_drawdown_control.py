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

from run_phase_a7_trend_overlay import (  # noqa: E402
    PERIODS,
    TREND_ASSETS,
    backtest_path,
    benchmark_rows,
    build_trend_weight_paths,
    build_vol_weight_paths,
    correlation_reports,
    load_inputs,
    period_drawdown_rows,
)
from src.reporting.metrics import calculate_metrics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_CONFIGS = [
    ("frontier_60_40", 0.60, 0.40),
    ("frontier_55_45", 0.55, 0.45),
    ("frontier_50_50", 0.50, 0.50),
    ("frontier_45_55", 0.45, 0.55),
    ("frontier_40_60", 0.40, 0.60),
]
STRESS_K = [0.10, 0.20, 0.30]
BETA_TARGETS = [0.70, 0.50]
VOL_NAME = "vol_top_20"
TREND_NAME = "trend_3m_6m_long_cash"


def stress_frame(prices: pd.DataFrame, vix_col: str = "^VIX", spy_col: str = "SPY") -> pd.DataFrame:
    index = prices.index
    vix = prices[vix_col].ffill() if vix_col in prices.columns else pd.Series(np.nan, index=index)
    spy = prices[spy_col].ffill()
    vix_pct = vix.rolling(504, min_periods=126).rank(pct=True)
    drawdown = spy / spy.expanding().max() - 1.0
    dd_score = (-drawdown / 0.30).clip(lower=0.0, upper=1.0)
    stress = (0.5 * vix_pct.fillna(0.0) + 0.5 * dd_score.fillna(0.0)).clip(0.0, 1.0)
    return pd.DataFrame(
        {
            "vix_percentile": vix_pct,
            "spy_drawdown": drawdown,
            "drawdown_score": dd_score,
            "stress_score": stress,
        }
    )


def path_daily_weights(path: dict, dates: list[pd.Timestamp]) -> dict[pd.Timestamp, pd.Series]:
    rebalances = sorted(path["weights"])
    current = pd.Series(dtype=float)
    result = {}
    rebalance_set = set(rebalances)
    for date in dates:
        if date in rebalance_set:
            current = path["weights"][date]
        result[date] = current
    return result


def latest_beta(inputs: dict, date: pd.Timestamp) -> pd.Series:
    panel = inputs["stock_features"]
    if "beta_to_spy_63d" not in panel.columns:
        return pd.Series(dtype=float)
    dates = panel.index.levels[0]
    idx = dates.get_indexer([date], method="ffill")[0]
    if idx < 0:
        return pd.Series(dtype=float)
    return panel.xs(dates[idx], level="date")["beta_to_spy_63d"].replace([np.inf, -np.inf], np.nan)


def estimate_beta(inputs: dict, date: pd.Timestamp, weights: pd.Series, trend_asset_betas: dict[str, float]) -> float:
    if weights.empty:
        return 0.0
    stock_betas = latest_beta(inputs, date)
    betas = []
    for ticker in weights.index:
        if ticker in stock_betas.index and np.isfinite(stock_betas.loc[ticker]):
            betas.append(float(stock_betas.loc[ticker]))
        elif ticker in trend_asset_betas:
            betas.append(trend_asset_betas[ticker])
        elif ticker == inputs["universe_config"].benchmark:
            betas.append(1.0)
        else:
            betas.append(0.0)
    beta_series = pd.Series(betas, index=weights.index)
    return float((weights * beta_series).sum())


def combine_weights(vol_weights: pd.Series, trend_weights: pd.Series, vol_weight: float, trend_weight: float) -> pd.Series:
    vol_part = vol_weights * vol_weight
    trend_part = trend_weights * trend_weight
    index = vol_part.index.union(trend_part.index)
    return vol_part.reindex(index, fill_value=0.0) + trend_part.reindex(index, fill_value=0.0)


def build_variant_weights(
    inputs: dict,
    vol_path: dict,
    trend_path: dict,
    name: str,
    base_vol_weight: float,
    base_trend_weight: float,
    stress: pd.DataFrame,
    stress_k: float = 0.0,
    beta_target: float | None = None,
    trend_cap: float = 0.75,
    hedge_stress_floor: float = 0.0,
) -> dict:
    prices = inputs["prices"]
    start = pd.Timestamp(inputs["base_config"].backtest.start_date) + pd.DateOffset(years=inputs["base_config"].backtest.warmup_years)
    dates = [d for d in prices.index if d >= start]
    vol_daily = path_daily_weights(vol_path, dates)
    trend_daily = path_daily_weights(trend_path, dates)
    trend_asset_betas = {"SPY": 1.0, "TLT": -0.2, "GLD": 0.0, "UUP": -0.1}

    weights_by_date = {}
    diagnostics = {}
    for date in dates:
        stress_score = float(stress.loc[date, "stress_score"]) if date in stress.index else 0.0
        trend_weight = min(trend_cap, base_trend_weight + stress_k * stress_score)
        vol_weight = max(0.0, 1.0 - trend_weight)
        weights = combine_weights(vol_daily[date], trend_daily[date], vol_weight, trend_weight)

        pre_hedge_beta = estimate_beta(inputs, date, weights, trend_asset_betas)
        hedge_weight = 0.0
        if beta_target is not None and stress_score >= hedge_stress_floor:
            hedge_weight = -stress_score * max(0.0, pre_hedge_beta - beta_target)
            if hedge_weight:
                weights.loc[inputs["universe_config"].benchmark] = weights.get(inputs["universe_config"].benchmark, 0.0) + hedge_weight
        post_hedge_beta = estimate_beta(inputs, date, weights, trend_asset_betas)

        weights_by_date[date] = weights
        diagnostics[date] = {
            "sleeve": name,
            "stress_score": stress_score,
            "vol_weight": vol_weight,
            "trend_weight": trend_weight,
            "pre_hedge_beta": pre_hedge_beta,
            "hedge_weight": hedge_weight,
            "post_hedge_beta": post_hedge_beta,
            "gross_weight": float(weights.abs().sum()),
        }
    return {
        "weights": weights_by_date,
        "selected": {date: weights[weights.abs() > 0].index.tolist() for date, weights in weights_by_date.items()},
        "sleeve_type": "a7_1_blend",
        "diagnostics": diagnostics,
    }


def metric_row(inputs: dict, name: str, path: dict) -> tuple[dict, pd.Series, pd.Series, pd.DataFrame]:
    row, returns, nav = backtest_path(inputs, name, path)
    diag = pd.DataFrame.from_dict(path.get("diagnostics", {}), orient="index").reset_index(names="date")
    return row, returns, nav, diag


def run_variants(inputs: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = {}
    paths.update(build_vol_weight_paths(inputs))
    paths.update(build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63))
    vol_path = paths[VOL_NAME]
    trend_path = paths[TREND_NAME]
    stress = stress_frame(inputs["prices"], vix_col=inputs["universe_config"].vix_proxy, spy_col=inputs["universe_config"].benchmark)

    metrics = []
    returns_by_name = {}
    nav_by_name = {}
    diagnostics = []

    # Include reference sleeves.
    for name in [VOL_NAME, TREND_NAME]:
        row, returns, nav = backtest_path(inputs, name, paths[name])
        metrics.append(row)
        returns_by_name[name] = returns
        nav_by_name[name] = nav

    variant_specs = []
    for label, vol_weight, trend_weight in BASE_CONFIGS:
        variant_specs.append((label, vol_weight, trend_weight, 0.0, None))
    for label, vol_weight, trend_weight in [("stress_60_40", 0.60, 0.40), ("stress_50_50", 0.50, 0.50)]:
        for k in STRESS_K:
            variant_specs.append((f"{label}_k_{int(k * 100)}", vol_weight, trend_weight, k, None))
    for label, vol_weight, trend_weight in [("hedge_60_40", 0.60, 0.40), ("hedge_50_50", 0.50, 0.50)]:
        for k in [0.10, 0.20]:
            for beta_target in BETA_TARGETS:
                variant_specs.append((f"{label}_k_{int(k * 100)}_beta_{str(beta_target).replace('.', '_')}", vol_weight, trend_weight, k, beta_target))

    for label, vol_weight, trend_weight, k, beta_target in variant_specs:
        name = f"a7_1_{label}"
        path = build_variant_weights(
            inputs,
            vol_path,
            trend_path,
            name=name,
            base_vol_weight=vol_weight,
            base_trend_weight=trend_weight,
            stress=stress,
            stress_k=k,
            beta_target=beta_target,
        )
        row, returns, nav, diag = metric_row(inputs, name, path)
        row["base_vol_weight"] = vol_weight
        row["base_trend_weight"] = trend_weight
        row["stress_k"] = k
        row["beta_target"] = beta_target
        metrics.append(row)
        returns_by_name[name] = returns
        nav_by_name[name] = nav
        diagnostics.append(diag)

    corr, crisis_corr, rolling_corr = correlation_reports(inputs, returns_by_name)
    period_dd = period_drawdown_rows(inputs, nav_by_name)
    diag_df = pd.concat(diagnostics, ignore_index=True) if diagnostics else pd.DataFrame()
    return pd.DataFrame(metrics), corr, crisis_corr, rolling_corr, period_dd, diag_df


def benchmark_frame(inputs: dict) -> pd.DataFrame:
    return pd.DataFrame(benchmark_rows(inputs))


def gate_report(metrics: pd.DataFrame, benchmarks: pd.DataFrame, crisis_corr: pd.DataFrame) -> pd.DataFrame:
    ew = benchmarks[benchmarks["benchmark"] == "equal_weight_universe_daily"]
    ew_sharpe = float(ew.iloc[0]["sharpe"]) if not ew.empty else np.nan
    rows = []
    for _, row in metrics[metrics["sleeve_type"] == "a7_1_blend"].iterrows():
        trend_crisis = crisis_corr[
            (crisis_corr["vol_sleeve"] == VOL_NAME)
            & (crisis_corr["other_sleeve"] == TREND_NAME)
            & (crisis_corr["other_type"] == "trend")
        ]["crisis_correlation"].min()
        rows.append(
            {
                "universe": row["universe"],
                "sleeve": row["sleeve"],
                "cagr": row["cagr"],
                "sharpe": row["sharpe"],
                "max_dd": row["max_dd"],
                "equal_weight_sharpe": ew_sharpe,
                "trend_crisis_corr_vs_vol": trend_crisis,
                "passes_gate": bool(row["max_dd"] > -0.40 and row["sharpe"] > ew_sharpe and row["cagr"] > 0.18 and trend_crisis < 0.6),
            }
        )
    return pd.DataFrame(rows)


def diagnostics_summary(diagnostics: pd.DataFrame) -> pd.DataFrame:
    if diagnostics.empty:
        return diagnostics
    return (
        diagnostics.groupby("sleeve")
        .agg(
            avg_stress=("stress_score", "mean"),
            p95_stress=("stress_score", lambda s: s.quantile(0.95)),
            avg_trend_weight=("trend_weight", "mean"),
            p95_trend_weight=("trend_weight", lambda s: s.quantile(0.95)),
            avg_hedge_weight=("hedge_weight", "mean"),
            min_hedge_weight=("hedge_weight", "min"),
            avg_pre_hedge_beta=("pre_hedge_beta", "mean"),
            avg_post_hedge_beta=("post_hedge_beta", "mean"),
            avg_gross_weight=("gross_weight", "mean"),
            max_gross_weight=("gross_weight", "max"),
        )
        .reset_index()
    )


def render_report(metrics: pd.DataFrame, benchmarks: pd.DataFrame, gate: pd.DataFrame, crisis_corr: pd.DataFrame, period_dd: pd.DataFrame) -> str:
    passed = gate[gate["passes_gate"]] if not gate.empty else pd.DataFrame()
    best_sharpe = gate.sort_values(["sharpe", "max_dd"], ascending=[False, False]).head(10) if not gate.empty else pd.DataFrame()
    best_dd = gate.sort_values(["max_dd", "sharpe"], ascending=[False, False]).head(10) if not gate.empty else pd.DataFrame()
    lines = [
        "# Phase A.7.1 Drawdown Control Results",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Base alpha: unchanged `vol_top_20` volatility sleeve.",
        "- Hedge sleeve: `trend_3m_6m_long_cash` from A.7.",
        "- Tests: wider trend frontier, continuous stress scaling, residual beta hedge.",
        "- RL disabled.",
        "",
        "## Benchmarks",
        "",
        benchmarks.to_markdown(index=False, floatfmt=".4f") if not benchmarks.empty else "No benchmarks.",
        "",
        "## Metrics",
        "",
        metrics.to_markdown(index=False, floatfmt=".4f") if not metrics.empty else "No metrics.",
        "",
        "## Gate",
        "",
        gate.to_markdown(index=False, floatfmt=".4f") if not gate.empty else "No gate rows.",
        "",
        f"Validation gate result: {'PASS' if not passed.empty else 'FAIL'}",
        "",
        "## Best By Sharpe",
        "",
        best_sharpe.to_markdown(index=False, floatfmt=".4f") if not best_sharpe.empty else "No rows.",
        "",
        "## Best By Drawdown",
        "",
        best_dd.to_markdown(index=False, floatfmt=".4f") if not best_dd.empty else "No rows.",
        "",
        "## Crisis Correlation",
        "",
        crisis_corr.to_markdown(index=False, floatfmt=".4f") if not crisis_corr.empty else "No crisis correlation rows.",
        "",
        "## Period Drawdowns",
        "",
        period_dd.to_markdown(index=False, floatfmt=".4f") if not period_dd.empty else "No period drawdown rows.",
        "",
        "## Decision",
        "",
    ]
    if not passed.empty:
        lines.append("At least one A.7.1 variant passed the sp500 drawdown, Sharpe, CAGR, and trend-correlation gates. Review turnover/hedge diagnostics before promotion.")
    else:
        lines.append("A.7.1 did not pass the full gate. The remaining blocker is drawdown control; avoid RL until a non-RL expression clears MaxDD < 40%.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.7.1 trend drawdown-control experiment")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    inputs = load_inputs(args.config, args.universe, args.trend_assets)
    logger.info("Running Phase A.7.1 for %s", inputs["universe_config"].name)

    metrics, corr, crisis_corr, rolling_corr, period_dd, diagnostics = run_variants(inputs)
    benchmarks = benchmark_frame(inputs)
    gate = gate_report(metrics, benchmarks, crisis_corr)

    metrics.to_csv(reports_dir / "phase_a7_1_metrics.csv", index=False)
    corr.to_csv(reports_dir / "phase_a7_1_correlation_report.csv", index=False)
    crisis_corr.to_csv(reports_dir / "phase_a7_1_crisis_corr_report.csv", index=False)
    rolling_corr.to_csv(reports_dir / "phase_a7_1_rolling_corr_report.csv", index=False)
    period_dd.to_csv(reports_dir / "phase_a7_1_period_drawdowns.csv", index=False)
    diagnostics_summary(diagnostics).to_csv(reports_dir / "phase_a7_1_weight_diagnostics.csv", index=False)
    benchmarks.to_csv(reports_dir / "phase_a7_1_benchmarks.csv", index=False)
    gate.to_csv(reports_dir / "phase_a7_1_gate_report.csv", index=False)
    (reports_dir / "phase_a7_1_drawdown_control_results.md").write_text(
        render_report(metrics, benchmarks, gate, crisis_corr, period_dd)
    )
    logger.info("Saved Phase A.7.1 artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
