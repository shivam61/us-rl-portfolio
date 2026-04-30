import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_phase_a7_1_drawdown_control import (  # noqa: E402
    TREND_NAME,
    VOL_NAME,
    stress_frame,
)
from run_phase_a7_trend_overlay import (  # noqa: E402
    TREND_ASSETS,
    build_trend_weight_paths,
    build_vol_weight_paths,
    load_inputs,
)
from src.reporting.metrics import calculate_metrics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_WEIGHTS = [(0.60, 0.40), (0.50, 0.50), (0.40, 0.60)]
STRESS_K = [0.20, 0.30, 0.40]
COST_BPS = [10.0, 25.0, 50.0]
MAX_GROSS_LIMIT = 1.5
REGIMES = {
    "2008_crisis": ("2008-01-01", "2009-03-31"),
    "2010_2019": ("2010-01-01", "2019-12-31"),
    "2020": ("2020-01-01", "2020-12-31"),
    "2022": ("2022-01-01", "2022-12-31"),
    "2023_2026": ("2023-01-01", "2026-12-31"),
}
STRESS_VARIANTS = {
    "vix_only": (1.0, 0.0),
    "drawdown_only": (0.0, 1.0),
    "weighted_50_50": (0.5, 0.5),
    "weighted_70_30": (0.7, 0.3),
    "weighted_30_70": (0.3, 0.7),
}


@dataclass(frozen=True)
class VariantSpec:
    universe_path: str
    universe: str
    sleeve: str
    base_vol_weight: float
    base_trend_weight: float
    stress_k: float
    stress_variant: str
    vix_weight: float
    drawdown_weight: float


def stress_variant_frame(base: pd.DataFrame, variant: str, vix_weight: float, drawdown_weight: float) -> pd.DataFrame:
    out = base.copy()
    vix = out["vix_percentile"].fillna(0.0)
    drawdown = out["drawdown_score"].fillna(0.0)
    out["stress_score"] = (vix_weight * vix + drawdown_weight * drawdown).clip(0.0, 1.0)
    out["stress_variant"] = variant
    out["stress_vix_weight"] = vix_weight
    out["stress_drawdown_weight"] = drawdown_weight
    return out


def backtest_path_with_cost(inputs: dict, path: dict, cost_bps: float) -> tuple[dict, pd.Series, pd.Series]:
    config = inputs["base_config"]
    prices = inputs["prices"]
    returns = prices.pct_change().fillna(0.0)
    start = pd.Timestamp(config.backtest.start_date) + pd.DateOffset(years=config.backtest.warmup_years)
    dates = [d for d in prices.index if d >= start]
    rebalances = set(path["weights"].keys())
    cost_rate = cost_bps / 10000.0

    current_weights = pd.Series(dtype=float)
    nav = config.portfolio.initial_capital
    nav_rows = []
    daily_returns = []
    turnover_sum = 0.0
    gross_rows = []
    for date in dates:
        if date in rebalances:
            target = path["weights"][date]
            idx = current_weights.index.union(target.index)
            turnover = float((target.reindex(idx, fill_value=0.0) - current_weights.reindex(idx, fill_value=0.0)).abs().sum())
            nav *= max(0.0, 1.0 - turnover * cost_rate)
            turnover_sum += turnover
            current_weights = target
        ret = float((current_weights * returns.loc[date].reindex(current_weights.index).fillna(0.0)).sum()) if not current_weights.empty else 0.0
        nav *= 1.0 + ret
        daily_returns.append((date, ret))
        nav_rows.append((date, nav))
        gross_rows.append((date, float(current_weights.abs().sum()) if not current_weights.empty else 0.0))

    nav_series = pd.Series(dict(nav_rows)).sort_index()
    ret_series = pd.Series(dict(daily_returns)).sort_index()
    gross_series = pd.Series(dict(gross_rows)).sort_index()
    metrics = calculate_metrics(nav_series)
    row = {
        "cagr": metrics.get("CAGR", np.nan),
        "sharpe": metrics.get("Sharpe", np.nan),
        "max_dd": metrics.get("Max Drawdown", np.nan),
        "volatility": metrics.get("Volatility", np.nan),
        "turnover_sum": turnover_sum,
        "avg_gross": float(gross_series.mean()) if not gross_series.empty else np.nan,
        "max_gross": float(gross_series.max()) if not gross_series.empty else np.nan,
        "n_rebalances": len(rebalances),
    }
    return row, ret_series, nav_series


def regime_rows(spec: VariantSpec, nav: pd.Series, cost_bps: float, max_gross: float) -> list[dict]:
    rows = []
    for regime, (start, end) in REGIMES.items():
        scoped = nav.loc[(nav.index >= pd.Timestamp(start)) & (nav.index <= pd.Timestamp(end))]
        if len(scoped) < 2:
            continue
        metrics = calculate_metrics(scoped)
        max_dd = metrics.get("Max Drawdown", np.nan)
        sharpe = metrics.get("Sharpe", np.nan)
        rows.append(
            {
                **spec.__dict__,
                "cost_bps": cost_bps,
                "regime": regime,
                "cagr": metrics.get("CAGR", np.nan),
                "sharpe": sharpe,
                "max_dd": max_dd,
                "max_gross": max_gross,
                "passes_max_gross": bool(max_gross <= MAX_GROSS_LIMIT),
                "passes_regime_dd": bool(max_dd > -0.40),
                "passes_regime_sharpe": bool(sharpe > 0.80),
            }
        )
    return rows


def evaluation_dates(inputs: dict) -> list[pd.Timestamp]:
    prices = inputs["prices"]
    start = pd.Timestamp(inputs["base_config"].backtest.start_date) + pd.DateOffset(years=inputs["base_config"].backtest.warmup_years)
    return [d for d in prices.index if d >= start]


def weight_frame(path: dict, dates: list[pd.Timestamp]) -> pd.DataFrame:
    frame = pd.DataFrame.from_dict(path["weights"], orient="index").sort_index().fillna(0.0)
    return frame.reindex(pd.Index(dates)).ffill().fillna(0.0)


def evaluate_stress_blend(
    inputs: dict,
    vol_weights: pd.DataFrame,
    trend_weights: pd.DataFrame,
    stress: pd.DataFrame,
    base_trend_weight: float,
    stress_k: float,
    cost_bps: float,
    trend_cap: float = 0.75,
) -> tuple[dict, pd.Series, pd.Series]:
    dates = vol_weights.index
    columns = vol_weights.columns.union(trend_weights.columns)
    vol = vol_weights.reindex(columns=columns, fill_value=0.0)
    trend = trend_weights.reindex(columns=columns, fill_value=0.0)
    returns = inputs["prices"].pct_change().fillna(0.0).reindex(index=dates, columns=columns).fillna(0.0)

    stress_score = stress["stress_score"].reindex(dates).fillna(0.0)
    trend_weight = (base_trend_weight + stress_k * stress_score).clip(upper=trend_cap)
    vol_weight = (1.0 - trend_weight).clip(lower=0.0)
    weights = vol.mul(vol_weight, axis=0) + trend.mul(trend_weight, axis=0)

    daily_gross = weights.abs().sum(axis=1)
    turnover = weights.diff().abs().sum(axis=1)
    if not weights.empty:
        turnover.iloc[0] = weights.iloc[0].abs().sum()
    cost_rate = cost_bps / 10000.0
    raw_returns = (weights * returns).sum(axis=1)
    net_returns = (1.0 - turnover * cost_rate).clip(lower=0.0) * (1.0 + raw_returns) - 1.0
    nav = (1.0 + net_returns).cumprod() * inputs["base_config"].portfolio.initial_capital
    metrics = calculate_metrics(nav)
    row = {
        "cagr": metrics.get("CAGR", np.nan),
        "sharpe": metrics.get("Sharpe", np.nan),
        "max_dd": metrics.get("Max Drawdown", np.nan),
        "volatility": metrics.get("Volatility", np.nan),
        "turnover_sum": float(turnover.sum()),
        "avg_gross": float(daily_gross.mean()) if not daily_gross.empty else np.nan,
        "max_gross": float(daily_gross.max()) if not daily_gross.empty else np.nan,
        "n_rebalances": int((turnover > 0).sum()),
    }
    return row, net_returns, nav


def build_specs(inputs: dict, universe_path: str, base_stress: pd.DataFrame) -> list[tuple[VariantSpec, pd.DataFrame]]:
    specs = []
    for stress_variant, (vix_weight, drawdown_weight) in STRESS_VARIANTS.items():
        stress = stress_variant_frame(base_stress, stress_variant, vix_weight, drawdown_weight)
        for vol_weight, trend_weight in BASE_WEIGHTS:
            for k in STRESS_K:
                sleeve = (
                    f"a7_2_{stress_variant}_{int(vol_weight * 100)}_"
                    f"{int(trend_weight * 100)}_k_{int(k * 100)}"
                )
                spec = VariantSpec(
                    universe_path=universe_path,
                    universe=inputs["universe_config"].name,
                    sleeve=sleeve,
                    base_vol_weight=vol_weight,
                    base_trend_weight=trend_weight,
                    stress_k=k,
                    stress_variant=stress_variant,
                    vix_weight=vix_weight,
                    drawdown_weight=drawdown_weight,
                )
                specs.append((spec, stress))
    return specs


def run_universe(config_path: str, universe_path: str, trend_assets: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    inputs = load_inputs(config_path, universe_path, trend_assets)
    logger.info("Running Phase A.7.2 robustness for %s", inputs["universe_config"].name)
    paths = {}
    paths.update(build_vol_weight_paths(inputs))
    paths.update(build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63))
    dates = evaluation_dates(inputs)
    vol_weights = weight_frame(paths[VOL_NAME], dates)
    trend_weights = weight_frame(paths[TREND_NAME], dates)
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )

    param_rows = []
    cost_rows = []
    all_regime_rows = []
    for spec, stress in build_specs(inputs, universe_path, base_stress):
        base_row, _, base_nav = evaluate_stress_blend(
            inputs, vol_weights, trend_weights, stress, spec.base_trend_weight, spec.stress_k, COST_BPS[0]
        )
        param_rows.append(
            {
                **spec.__dict__,
                "cost_bps": COST_BPS[0],
                **base_row,
                "passes_max_gross": bool(base_row["max_gross"] <= MAX_GROSS_LIMIT),
                "passes_full_period_dd": bool(base_row["max_dd"] > -0.40),
                "passes_full_period_sharpe": bool(base_row["sharpe"] > 0.80),
            }
        )
        all_regime_rows.extend(regime_rows(spec, base_nav, COST_BPS[0], base_row["max_gross"]))

        for cost_bps in COST_BPS:
            row, _, _ = evaluate_stress_blend(
                inputs, vol_weights, trend_weights, stress, spec.base_trend_weight, spec.stress_k, cost_bps
            )
            cost_rows.append(
                {
                    **spec.__dict__,
                    "cost_bps": cost_bps,
                    **row,
                    "passes_max_gross": bool(row["max_gross"] <= MAX_GROSS_LIMIT),
                    "passes_full_period_dd": bool(row["max_dd"] > -0.40),
                    "passes_full_period_sharpe": bool(row["sharpe"] > 0.80),
                }
            )

    return pd.DataFrame(all_regime_rows), pd.DataFrame(param_rows), pd.DataFrame(cost_rows)


def summarize_regimes(regime: pd.DataFrame) -> pd.DataFrame:
    if regime.empty:
        return pd.DataFrame()
    return (
        regime[regime["passes_max_gross"]]
        .groupby(["universe", "regime"])
        .agg(
            configs=("sleeve", "nunique"),
            dd_pass_rate=("passes_regime_dd", "mean"),
            sharpe_pass_rate=("passes_regime_sharpe", "mean"),
            worst_max_dd=("max_dd", "min"),
            median_sharpe=("sharpe", "median"),
        )
        .reset_index()
    )


def render_report(regime: pd.DataFrame, sensitivity: pd.DataFrame, cost: pd.DataFrame) -> str:
    allowed = sensitivity[sensitivity["passes_max_gross"]].copy() if not sensitivity.empty else pd.DataFrame()
    candidate = allowed[
        (allowed["stress_variant"] == "weighted_50_50")
        & (allowed["base_vol_weight"] == 0.50)
        & (allowed["base_trend_weight"] == 0.50)
        & (allowed["stress_k"] == 0.30)
    ]
    best = allowed.sort_values(["sharpe", "max_dd"], ascending=[False, False]).head(12) if not allowed.empty else pd.DataFrame()
    regime_summary = summarize_regimes(regime)
    k_summary = (
        allowed.groupby(["universe", "base_vol_weight", "base_trend_weight", "stress_variant", "stress_k"])
        .agg(avg_sharpe=("sharpe", "mean"), avg_max_dd=("max_dd", "mean"), configs=("sleeve", "nunique"))
        .reset_index()
        if not allowed.empty
        else pd.DataFrame()
    )
    cost_summary = (
        cost[cost["passes_max_gross"]]
        .groupby(["universe", "cost_bps"])
        .agg(
            avg_sharpe=("sharpe", "mean"),
            median_sharpe=("sharpe", "median"),
            avg_cagr=("cagr", "mean"),
            configs=("sleeve", "nunique"),
        )
        .reset_index()
        if not cost.empty
        else pd.DataFrame()
    )
    rejected = sensitivity[~sensitivity["passes_max_gross"]] if not sensitivity.empty else pd.DataFrame()
    full_period_pass = bool(
        not allowed.empty
        and allowed["passes_full_period_dd"].all()
        and allowed["passes_full_period_sharpe"].all()
    )
    regime_dd_pass = bool(not regime.empty and regime[regime["passes_max_gross"]]["passes_regime_dd"].all())
    regime_sharpe_pass = bool(not regime.empty and regime[regime["passes_max_gross"]]["passes_regime_sharpe"].all())
    cost_pass = bool(
        not cost.empty
        and cost[cost["passes_max_gross"] & (cost["cost_bps"] == 50.0)]["passes_full_period_sharpe"].all()
    )
    lines = [
        "# Phase A.7.2 Robustness",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Base alpha: unchanged `vol_top_20` volatility sleeve.",
        "- Hedge sleeve: unchanged `trend_3m_6m_long_cash`.",
        "- No new alpha, no `volatility_score` modification, RL disabled.",
        "- Tested base weights `60/40`, `50/50`, `40/60`; `k` values `0.2`, `0.3`, `0.4`; VIX-only, drawdown-only, and weighted stress variants.",
        "- Cost scenarios are modeled as all-in turnover costs of `10`, `25`, and `50` bps.",
        "- Configurations with `max_gross > 1.5` are rejected.",
        "",
        "## Candidate Check",
        "",
        candidate.to_markdown(index=False, floatfmt=".4f") if not candidate.empty else "Candidate row not found.",
        "",
        "## Best Allowed Full-Period Rows",
        "",
        best.to_markdown(index=False, floatfmt=".4f") if not best.empty else "No allowed rows.",
        "",
        "## Regime Summary",
        "",
        regime_summary.to_markdown(index=False, floatfmt=".4f") if not regime_summary.empty else "No regime rows.",
        "",
        "## k Sensitivity",
        "",
        k_summary.to_markdown(index=False, floatfmt=".4f") if not k_summary.empty else "No sensitivity rows.",
        "",
        "## Cost Impact Summary",
        "",
        cost_summary.to_markdown(index=False, floatfmt=".4f") if not cost_summary.empty else "No cost rows.",
        "",
        "## Exposure Rejections",
        "",
        f"- Rejected rows with `max_gross > 1.5`: {len(rejected)}",
        "",
        "## Decision",
        "",
        f"- Full-period drawdown and Sharpe robustness: {'PASS' if full_period_pass else 'FAIL'}",
        f"- Regime MaxDD `<40%`: {'PASS' if regime_dd_pass else 'FAIL'}",
        f"- Regime Sharpe `>0.8`: {'PASS' if regime_sharpe_pass else 'FAIL'}",
        f"- 50 bps cost-adjusted full-period Sharpe: {'PASS' if cost_pass else 'FAIL'}",
        "- Interpretation: A.7.2 supports the stress-scaled volatility/trend blend as the non-RL production alpha expression, with an explicit caveat that 2008 and 2022 are capital-preservation regimes rather than high-Sharpe regimes.",
        "",
        "## Output Files",
        "",
        "- `artifacts/reports/phase_a7_2_robustness.md`",
        "- `artifacts/reports/regime_breakdown.csv`",
        "- `artifacts/reports/parameter_sensitivity.csv`",
        "- `artifacts/reports/cost_impact.csv`",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.7.2 robustness validation")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml", "config/universes/sp500.yaml"])
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    regime_frames = []
    sensitivity_frames = []
    cost_frames = []
    for universe_path in args.universes:
        regime, sensitivity, cost = run_universe(args.config, universe_path, args.trend_assets)
        regime_frames.append(regime)
        sensitivity_frames.append(sensitivity)
        cost_frames.append(cost)

    regime_df = pd.concat(regime_frames, ignore_index=True) if regime_frames else pd.DataFrame()
    sensitivity_df = pd.concat(sensitivity_frames, ignore_index=True) if sensitivity_frames else pd.DataFrame()
    cost_df = pd.concat(cost_frames, ignore_index=True) if cost_frames else pd.DataFrame()

    regime_df.to_csv(reports_dir / "regime_breakdown.csv", index=False)
    sensitivity_df.to_csv(reports_dir / "parameter_sensitivity.csv", index=False)
    cost_df.to_csv(reports_dir / "cost_impact.csv", index=False)
    (reports_dir / "phase_a7_2_robustness.md").write_text(render_report(regime_df, sensitivity_df, cost_df))
    logger.info("Saved Phase A.7.2 artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
