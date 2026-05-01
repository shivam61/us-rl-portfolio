import argparse
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_phase_a7_1_drawdown_control import TREND_NAME, stress_frame  # noqa: E402
from run_phase_a7_2_robustness import stress_variant_frame  # noqa: E402
from run_phase_a7_trend_overlay import TREND_ASSETS, build_trend_weight_paths, load_inputs  # noqa: E402
from run_phase_b1_simulator_reproduction import (  # noqa: E402
    CANDIDATE_BASE_TREND_WEIGHT,
    CANDIDATE_STRESS_K,
    CANDIDATE_TREND_CAP,
    MAX_GROSS_LIMIT,
    clipped_evaluation_dates,
    recommended_end_for_universe,
)
from run_phase_b2_turnover_control import (  # noqa: E402
    B1_COST_BPS,
    Variant,
    apply_execution_controls,
    build_vol_path_fast,
    candidate_weights_with_persistence,
    run_execution_simulator,
    signal_dates_for_frequency,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

B2_CAGR = 0.183299
B2_SHARPE = 1.143805
B2_MAX_DD = -0.336869
B2_TURNOVER = 89.621518
B2_MAX_GROSS = 1.3462
BETA_MIN = 0.50
BETA_MAX = 0.80


@dataclass(frozen=True)
class ExposureVariant:
    name: str
    project_beta: bool


def rolling_beta_matrix(prices: pd.DataFrame, benchmark: str, window: int = 63) -> pd.DataFrame:
    returns = prices.pct_change()
    benchmark_returns = returns[benchmark]
    variance = benchmark_returns.rolling(window, min_periods=window // 2).var()
    betas = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
    for column in returns.columns:
        covariance = returns[column].rolling(window, min_periods=window // 2).cov(benchmark_returns)
        betas[column] = covariance / variance
    if benchmark in betas.columns:
        betas[benchmark] = 1.0
    return betas.replace([np.inf, -np.inf], np.nan).ffill()


def portfolio_beta(weights: pd.Series, betas: pd.Series) -> float:
    aligned = betas.reindex(weights.index)
    valid = aligned.notna() & weights.notna()
    if not valid.any():
        return np.nan
    return float((weights[valid] * aligned[valid]).sum())


def projection_scale(beta: float, gross: float, project_beta: bool) -> tuple[float, str]:
    if gross <= 1e-12:
        return 1.0, "empty"
    scale = min(1.0, MAX_GROSS_LIMIT / gross)
    reason = "gross_cap" if scale < 1.0 else "none"
    scaled_beta = beta * scale if np.isfinite(beta) else np.nan
    scaled_gross = gross * scale

    if not project_beta or not np.isfinite(scaled_beta):
        return scale, reason

    if scaled_beta > BETA_MAX and scaled_beta > 0:
        beta_scale = BETA_MAX / scaled_beta
        scale *= beta_scale
        reason = "beta_down" if reason == "none" else f"{reason}+beta_down"
    elif 0 < scaled_beta < BETA_MIN:
        beta_scale = BETA_MIN / scaled_beta
        max_scale = MAX_GROSS_LIMIT / scaled_gross if scaled_gross > 0 else 1.0
        applied = min(beta_scale, max_scale)
        if applied > 1.0:
            scale *= applied
            reason = "beta_up" if reason == "none" else f"{reason}+beta_up"
    return float(scale), reason


def project_weights(
    weights: pd.Series,
    beta_row: pd.Series,
    benchmark: str,
    project_beta: bool,
) -> tuple[pd.Series, float, float, str]:
    gross = float(weights.abs().sum())
    beta = portfolio_beta(weights, beta_row)
    scale, reason = projection_scale(beta, gross, project_beta)
    projected = weights * scale
    overlay = 0.0
    if not project_beta:
        return projected, scale, overlay, reason

    beta_after = portfolio_beta(projected, beta_row)
    gross_after = float(projected.abs().sum())
    if gross_after <= 1e-12 or not np.isfinite(beta_after) or beta_after >= BETA_MIN - 1e-6:
        return projected, scale, overlay, reason

    beta_gap = BETA_MIN - beta_after
    if gross_after + beta_gap <= MAX_GROSS_LIMIT + 1e-9:
        overlay = beta_gap
    else:
        denominator = gross_after - beta_after
        preserve_scale = min(1.0, (MAX_GROSS_LIMIT - BETA_MIN) / denominator) if denominator > 1e-12 else 1.0
        projected = projected * preserve_scale
        scale *= preserve_scale
        beta_after = portfolio_beta(projected, beta_row)
        overlay = max(0.0, BETA_MIN - beta_after)
    if overlay > 0:
        projected = projected.copy()
        projected.loc[benchmark] = projected.get(benchmark, 0.0) + overlay
        reason = "spy_beta_floor" if reason == "none" else f"{reason}+spy_beta_floor"
    return projected, float(scale), float(overlay), reason


def beta_out_of_band(beta: float, gross: float, tolerance: float = 1e-6) -> bool:
    if gross <= 1e-12:
        return False
    return (not np.isfinite(beta)) or beta < BETA_MIN - tolerance or beta > BETA_MAX + tolerance


def apply_exposure_constraints(
    target_weights: pd.DataFrame,
    beta_frame: pd.DataFrame,
    variant: ExposureVariant,
    control_dates: list[pd.Timestamp],
    benchmark: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    diagnostics = []
    current = pd.Series(dtype=float)
    control_set = set(control_dates)
    for date, row in target_weights.iterrows():
        is_control_date = date in control_set
        weights = row[row.abs() > 1e-12]
        gross_before = float(weights.abs().sum())
        beta_before = portfolio_beta(weights, beta_frame.loc[date]) if date in beta_frame.index else np.nan
        if is_control_date:
            current, scale, overlay, reason = project_weights(
                weights,
                beta_frame.loc[date],
                benchmark=benchmark,
                project_beta=variant.project_beta,
            )
        else:
            scale, overlay, reason = 1.0, 0.0, "held"
        gross_after = float(current.abs().sum())
        beta_after = portfolio_beta(current, beta_frame.loc[date]) if date in beta_frame.index else np.nan
        rows.append(current.rename(date))
        diagnostics.append(
            {
                "date": date,
                "variant": variant.name,
                "is_control_date": is_control_date,
                "gross_before": gross_before,
                "gross_after": gross_after,
                "beta_before": beta_before,
                "beta_after": beta_after,
                "scale": scale,
                "spy_overlay": overlay,
                "projection_reason": reason,
                "gross_violation_before": gross_before > MAX_GROSS_LIMIT + 1e-9,
                "gross_violation_after": gross_after > MAX_GROSS_LIMIT + 1e-9,
                "beta_violation_before": beta_out_of_band(beta_before, gross_before),
                "beta_violation_after": beta_out_of_band(beta_after, gross_after),
                "gate_violation_after": is_control_date
                and (
                    gross_after > MAX_GROSS_LIMIT + 1e-9
                    or beta_out_of_band(beta_after, gross_after)
                ),
            }
        )
    return pd.DataFrame(rows).fillna(0.0), pd.DataFrame(diagnostics)


def build_b2_candidate(inputs: dict, validation_end: pd.Timestamp) -> pd.DataFrame:
    dates = clipped_evaluation_dates(inputs, validation_end)
    trend_path = build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63)[TREND_NAME]
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)
    raw = candidate_weights_with_persistence(
        dates,
        build_vol_path_fast(inputs, None),
        trend_path,
        stress,
    )
    signal_dates = signal_dates_for_frequency(inputs, raw, validation_end, "every_2_rebalances")
    return apply_execution_controls(raw, signal_dates, trade_threshold=0.0, partial_rebalance=1.0)


def realized_beta(nav_returns: pd.Series, benchmark_returns: pd.Series, window: int = 63) -> pd.Series:
    aligned = pd.concat([nav_returns.rename("portfolio"), benchmark_returns.rename("benchmark")], axis=1).dropna()
    covariance = aligned["portfolio"].rolling(window, min_periods=window // 2).cov(aligned["benchmark"])
    variance = aligned["benchmark"].rolling(window, min_periods=window // 2).var()
    return (covariance / variance).replace([np.inf, -np.inf], np.nan)


def evaluate_exposure_variant(
    inputs: dict,
    validation_end: pd.Timestamp,
    target_weights: pd.DataFrame,
    beta_frame: pd.DataFrame,
    variant: ExposureVariant,
    control_dates: list[pd.Timestamp],
) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    constrained, diagnostics = apply_exposure_constraints(
        target_weights,
        beta_frame,
        variant,
        control_dates,
        inputs["universe_config"].benchmark,
    )
    metrics = run_execution_simulator(
        inputs,
        constrained,
        validation_end,
        Variant(variant.name, update_frequency="every_2_rebalances", cost_bps=B1_COST_BPS),
    )
    dates = constrained.index[constrained.index <= validation_end]
    executable = constrained.reindex(dates).fillna(0.0).shift(1).fillna(0.0)
    returns = inputs["prices"].pct_change().fillna(0.0).reindex(index=dates, columns=executable.columns).fillna(0.0)
    turnover = executable.diff().abs().sum(axis=1)
    if not executable.empty:
        turnover.iloc[0] = executable.iloc[0].abs().sum()
    raw_returns = (executable * returns).sum(axis=1)
    net_returns = (1.0 - turnover * B1_COST_BPS / 10000.0).clip(lower=0.0) * (1.0 + raw_returns) - 1.0
    spy_returns = inputs["prices"][inputs["universe_config"].benchmark].pct_change().reindex(dates)
    realized = realized_beta(net_returns, spy_returns)

    beta_rows = diagnostics.copy()
    beta_rows["realized_beta_63d"] = realized.reindex(beta_rows["date"]).values
    gross_rows = diagnostics[
        ["date", "variant", "gross_before", "gross_after", "scale", "projection_reason"]
    ].copy()
    violation_rows = diagnostics[diagnostics["gate_violation_after"]].copy()

    metrics.update(
        {
            "variant": variant.name,
            "project_beta": variant.project_beta,
            "avg_beta_before": float(diagnostics["beta_before"].mean()),
            "avg_beta_after": float(diagnostics["beta_after"].mean()),
            "min_beta_after": float(diagnostics["beta_after"].min()),
            "max_beta_after": float(diagnostics["beta_after"].max()),
            "control_beta_violations_after": int(
                diagnostics.loc[diagnostics["is_control_date"], "beta_violation_after"].sum()
            ),
            "daily_beta_violations_after": int(diagnostics["beta_violation_after"].sum()),
            "control_gross_violations_after": int(
                diagnostics.loc[diagnostics["is_control_date"], "gross_violation_after"].sum()
            ),
            "daily_gross_violations_after": int(diagnostics["gross_violation_after"].sum()),
            "avg_control_scale": float(diagnostics.loc[diagnostics["is_control_date"], "scale"].mean()),
            "min_control_scale": float(diagnostics.loc[diagnostics["is_control_date"], "scale"].min()),
            "turnover_vs_b2_delta": metrics["turnover_sum"] - B2_TURNOVER,
            "sharpe_vs_b2_delta": metrics["sharpe"] - B2_SHARPE,
            "cagr_vs_b2_delta": metrics["cagr"] - B2_CAGR,
            "max_dd_vs_b2_delta": metrics["max_dd"] - B2_MAX_DD,
            "passes_b3": bool(
                metrics["max_target_gross"] <= MAX_GROSS_LIMIT
                and diagnostics["gate_violation_after"].sum() == 0
                and metrics["sharpe"] >= B2_SHARPE - 0.10
                and metrics["cagr"] >= B2_CAGR - 0.02
                and metrics["turnover_sum"] <= B2_TURNOVER * 1.05
            ),
        }
    )
    return metrics, violation_rows, beta_rows, gross_rows


def render_report(summary: pd.DataFrame, violations: pd.DataFrame) -> str:
    lines = [
        "# Phase B.3 Exposure-Constrained Portfolio Shaping",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Baseline: B.2 `every_2_rebalances` turnover-control candidate.",
        "- Scope: no `volatility_score` changes, no trend-signal changes, no stress-formula changes, no new alpha, RL disabled.",
        "- Method: constraint-based scalar shaping of the existing B.2 target book; when scalar scaling cannot meet the beta floor inside gross `1.5`, apply a minimal SPY beta-floor projection. No return-maximizing optimizer is used.",
        "",
        "## Gates",
        "",
        "- Gross exposure must stay `<=1.5`.",
        "- Ex-ante portfolio beta must stay in `[0.5, 0.8]` using 63-day rolling beta to SPY.",
        "- B.2 turnover improvement should be maintained.",
        "- Sharpe and CAGR should remain within B.2 tolerance: Sharpe no worse than `B.2 - 0.10`, CAGR drop no worse than `2` percentage points.",
        "",
        "## Summary",
        "",
        summary.to_markdown(index=False, floatfmt=".4f") if not summary.empty else "No summary rows.",
        "",
        "## Interpretation",
        "",
    ]
    projected = summary[summary["project_beta"]].copy()
    if projected.empty:
        lines.append("No projected row was produced.")
    else:
        row = projected.iloc[0]
        if row["control_beta_violations_after"] == 0 and row["control_gross_violations_after"] == 0:
            lines.append(
                f"- Projection satisfies rebalance-date gross and beta constraints, with Sharpe drift `{row['sharpe_vs_b2_delta']:.3f}` and CAGR drift `{row['cagr_vs_b2_delta']:.2%}` versus B.2."
            )
        if not row["passes_b3"]:
            reasons = []
            if row["sharpe"] < B2_SHARPE - 0.10:
                reasons.append("Sharpe drift exceeds tolerance")
            if row["cagr"] < B2_CAGR - 0.02:
                reasons.append("CAGR drop exceeds 2 percentage points")
            if row["turnover_sum"] > B2_TURNOVER * 1.05:
                reasons.append("turnover exceeds B.2 tolerance")
            if row["control_beta_violations_after"] > 0 or row["control_gross_violations_after"] > 0:
                reasons.append("rebalance-date constraints still violate")
            lines.append("- B.3 gate status: FAIL/WATCH because " + "; ".join(reasons) + ".")
    lines.extend(
        [
            "",
        "## Remaining Violations",
        "",
        ]
    )
    remaining = violations.copy()
    if remaining.empty:
        lines.append("No post-projection gross or beta violations.")
    else:
        lines.append(
            remaining[
                [
                    "date",
                    "variant",
                    "is_control_date",
                    "gross_after",
                    "beta_after",
                    "scale",
                    "projection_reason",
                    "gross_violation_after",
                    "beta_violation_after",
                ]
            ]
            .head(25)
            .to_markdown(index=False, floatfmt=".4f")
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
        ]
    )
    passing = summary[summary["passes_b3"]].copy()
    if passing.empty:
        lines.append("- FAIL/WATCH: projection satisfies rebalance-date exposure constraints, but no B.3 variant stays within all B.2 performance tolerances.")
    else:
        best = passing.sort_values(["project_beta", "sharpe"], ascending=[False, False]).iloc[0]
        lines.append(
            f"- PASS: `{best['variant']}` satisfies gross/beta constraints with Sharpe `{best['sharpe']:.3f}`, CAGR `{best['cagr']:.2%}`, MaxDD `{best['max_dd']:.2%}`, and turnover `{best['turnover_sum']:.2f}`."
        )
    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `artifacts/reports/phase_b3_exposure_control.md`",
            "- `artifacts/reports/constraint_violations.csv`",
            "- `artifacts/reports/beta_tracking.csv`",
            "- `artifacts/reports/gross_exposure.csv`",
        ]
    )
    return "\n".join(lines) + "\n"


def run_universe(config_path: str, universe_path: str, trend_assets: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    inputs = load_inputs(config_path, universe_path, trend_assets)
    validation_end = recommended_end_for_universe(inputs["universe_config"].name, inputs["prices"].index.max())
    logger.info("Running Phase B.3 exposure control for %s through %s", inputs["universe_config"].name, validation_end.date())
    started = time.perf_counter()
    target_weights = build_b2_candidate(inputs, validation_end)
    logger.info("Built B.2 candidate target weights in %.1fs", time.perf_counter() - started)
    target_turnover = target_weights.diff().abs().sum(axis=1)
    if not target_weights.empty:
        target_turnover.iloc[0] = target_weights.iloc[0].abs().sum()
    control_dates = list(target_turnover[target_turnover > 1e-12].index)
    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    variants = [
        ExposureVariant("b2_every_2_no_projection", project_beta=False),
        ExposureVariant("b3_every_2_beta_projection", project_beta=True),
    ]
    summaries = []
    violation_frames = []
    beta_frames = []
    gross_frames = []
    for variant in variants:
        row, violations, beta_tracking, gross_exposure = evaluate_exposure_variant(
            inputs,
            validation_end,
            target_weights,
            beta_frame,
            variant,
            control_dates,
        )
        summaries.append(row)
        violation_frames.append(violations)
        beta_frames.append(beta_tracking)
        gross_frames.append(gross_exposure)
    return (
        pd.DataFrame(summaries),
        pd.concat(violation_frames, ignore_index=True),
        pd.concat(beta_frames, ignore_index=True),
        pd.concat(gross_frames, ignore_index=True),
    )


def main():
    parser = argparse.ArgumentParser(description="Run Phase B.3 exposure-constrained portfolio shaping")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary, violations, beta_tracking, gross_exposure = run_universe(args.config, args.universe, args.trend_assets)
    summary.to_csv(reports_dir / "phase_b3_summary.csv", index=False)
    violations.to_csv(reports_dir / "constraint_violations.csv", index=False)
    beta_tracking.to_csv(reports_dir / "beta_tracking.csv", index=False)
    gross_exposure.to_csv(reports_dir / "gross_exposure.csv", index=False)
    (reports_dir / "phase_b3_exposure_control.md").write_text(render_report(summary, violations))
    logger.info("Saved Phase B.3 exposure-control artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
