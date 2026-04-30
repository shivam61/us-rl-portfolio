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

from run_phase_a7_1_drawdown_control import TREND_NAME, VOL_NAME, stress_frame  # noqa: E402
from run_phase_a7_2_robustness import (  # noqa: E402
    REGIMES,
    evaluate_stress_blend,
    evaluation_dates,
    stress_variant_frame,
    weight_frame,
)
from run_phase_a7_trend_overlay import (  # noqa: E402
    TREND_ASSETS,
    build_trend_weight_paths,
    equal_weights,
    latest_scores,
    load_inputs,
    rebalance_dates,
)
from src.alpha.volatility_score import VOL_FEATURES_ASCENDING, VOL_FEATURES_DESCENDING  # noqa: E402
from src.reporting.metrics import calculate_metrics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CANDIDATE_BASE_TREND_WEIGHT = 0.50
CANDIDATE_STRESS_K = 0.30
CANDIDATE_COST_BPS = 10.0
COVERAGE_THRESHOLD = 0.75


def active_matrix(inputs: dict) -> pd.DataFrame:
    tickers = list(inputs["universe_config"].tickers.keys())
    dates = pd.Index(evaluation_dates(inputs))
    pit_mask = inputs["pit_mask"]
    if pit_mask is None:
        return pd.DataFrame(True, index=dates, columns=tickers)
    mask = pit_mask.reindex(dates, method="ffill").reindex(columns=tickers, fill_value=False).fillna(False)
    return mask.astype(bool)


def price_matrix(inputs: dict) -> pd.DataFrame:
    tickers = list(inputs["universe_config"].tickers.keys())
    return inputs["prices"].reindex(index=evaluation_dates(inputs), columns=tickers)


def regime_for_date(date: pd.Timestamp) -> str | None:
    for regime, (start, end) in REGIMES.items():
        if pd.Timestamp(start) <= date <= pd.Timestamp(end):
            return regime
    return None


def scoped_dates(dates: pd.Index, start: str, end: str) -> pd.Index:
    return dates[(dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))]


def universe_audit(inputs: dict) -> pd.DataFrame:
    active = active_matrix(inputs)
    prices = price_matrix(inputs)
    vol_score = inputs["vol_scores"]["volatility_score"].unstack("ticker").reindex(index=active.index)
    rows = []
    for regime, (start, end) in REGIMES.items():
        dates = scoped_dates(active.index, start, end)
        if dates.empty:
            continue
        active_counts = active.loc[dates].sum(axis=1)
        nonzero_active = active_counts[active_counts > 0]
        price_counts = prices.loc[dates].notna().sum(axis=1)
        score_counts = (vol_score.loc[dates].notna() & active.loc[dates]).sum(axis=1)
        rows.append(
            {
                "universe": inputs["universe_config"].name,
                "regime": regime,
                "configured_tickers": len(active.columns),
                "dates": len(dates),
                "active_zero_days": int((active_counts == 0).sum()),
                "active_mean": float(active_counts.mean()),
                "active_p10": float(active_counts.quantile(0.10)),
                "active_min": int(active_counts.min()),
                "active_min_nonzero": int(nonzero_active.min()) if not nonzero_active.empty else 0,
                "active_median": float(active_counts.median()),
                "active_max": int(active_counts.max()),
                "price_non_null_mean": float(price_counts.mean()),
                "vol_score_active_non_null_mean": float(score_counts.mean()),
                "vol_score_active_coverage_mean": float((score_counts / active_counts.replace(0, np.nan)).mean()),
            }
        )
    return pd.DataFrame(rows)


def feature_coverage(inputs: dict) -> pd.DataFrame:
    active = active_matrix(inputs)
    panel = inputs["stock_features"]
    scores = inputs["vol_scores"]
    features = [c for c in VOL_FEATURES_ASCENDING + VOL_FEATURES_DESCENDING if c in panel.columns] + ["volatility_score"]
    rows = []
    for feature in features:
        source = scores if feature == "volatility_score" else panel
        wide = source[feature].unstack("ticker").reindex(index=active.index)
        for regime, (start, end) in REGIMES.items():
            dates = scoped_dates(active.index, start, end)
            if dates.empty:
                continue
            active_counts = active.loc[dates].sum(axis=1)
            non_null = (wide.loc[dates].notna() & active.loc[dates]).sum(axis=1)
            coverage = non_null / active_counts.replace(0, np.nan)
            rows.append(
                {
                    "universe": inputs["universe_config"].name,
                    "regime": regime,
                    "feature": feature,
                    "dates": len(dates),
                    "active_mean": float(active_counts.mean()),
                    "non_null_mean": float(non_null.mean()),
                    "coverage_mean": float(coverage.mean()),
                    "coverage_p10": float(coverage.quantile(0.10)),
                    "coverage_min": float(coverage.min()),
                }
            )
    return pd.DataFrame(rows)


def first_active_dates(active: pd.DataFrame) -> pd.Series:
    result = {}
    for ticker in active.columns:
        dates = active.index[active[ticker]]
        result[ticker] = dates.min() if len(dates) else pd.NaT
    return pd.Series(result)


def all_regime_covered_tickers(inputs: dict, threshold: float) -> set[str]:
    active = active_matrix(inputs)
    score = inputs["vol_scores"]["volatility_score"].unstack("ticker").reindex(index=active.index)
    keep = set(active.columns)
    for _, (start, end) in REGIMES.items():
        dates = scoped_dates(active.index, start, end)
        if dates.empty:
            continue
        active_any = active.loc[dates].any(axis=0)
        coverage = (score.loc[dates].notna() & active.loc[dates]).sum(axis=0) / active.loc[dates].sum(axis=0).replace(0, np.nan)
        keep &= set(coverage[(active_any) & (coverage >= threshold)].index)
    return keep


def cohort_definitions(inputs: dict) -> list[tuple[str, set[str] | None, bool]]:
    active = active_matrix(inputs)
    first_active = first_active_dates(active)
    all_tickers = set(active.columns)
    early_2010 = set(first_active[first_active <= pd.Timestamp("2010-01-01")].index)
    pre_2020 = set(first_active[first_active <= pd.Timestamp("2020-01-01")].index)
    all_regime_covered = all_regime_covered_tickers(inputs, COVERAGE_THRESHOLD)
    return [
        ("baseline_current_mask", None, True),
        ("no_pit_mask_configured_list", None, False),
        ("early_active_by_2010", early_2010, True),
        ("pre_2020_active_only", pre_2020, True),
        ("all_regime_score_coverage_75pct", all_regime_covered, True),
        ("full_configured_list_with_current_mask", all_tickers, True),
    ]


def active_tickers_for_date(inputs: dict, date: pd.Timestamp, active: pd.DataFrame | None, eligible: set[str] | None) -> list[str]:
    base = list(inputs["universe_config"].tickers.keys())
    if active is None:
        candidates = base
    else:
        idx = active.index.get_indexer([date], method="ffill")[0]
        if idx < 0:
            candidates = []
        else:
            row = active.iloc[idx]
            candidates = [ticker for ticker in base if bool(row.get(ticker, False))]
    if eligible is not None:
        candidates = [ticker for ticker in candidates if ticker in eligible]
    return candidates


def build_filtered_vol_path(inputs: dict, active: pd.DataFrame | None, eligible: set[str] | None) -> tuple[dict, pd.DataFrame]:
    weights_by_date = {}
    selected_by_date = {}
    audit_rows = []
    for date in rebalance_dates(inputs["base_config"], inputs["prices"]):
        candidates = active_tickers_for_date(inputs, date, active, eligible)
        scores = latest_scores(inputs["vol_scores"], date, "volatility_score").reindex(candidates)
        available = scores.dropna()
        selected = available.sort_values(ascending=False).head(20).index.tolist()
        weights_by_date[date] = equal_weights(selected)
        selected_by_date[date] = selected
        audit_rows.append(
            {
                "date": date,
                "regime": regime_for_date(date),
                "candidate_count": len(candidates),
                "score_non_null_count": int(available.shape[0]),
                "selected_count": len(selected),
            }
        )
    return {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": "volatility"}, pd.DataFrame(audit_rows)


def run_artifact_sensitivity(inputs: dict) -> pd.DataFrame:
    active = active_matrix(inputs)
    paths = build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63)
    trend_weights = weight_frame(paths[TREND_NAME], evaluation_dates(inputs))
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)

    rows = []
    for cohort, eligible, use_pit_mask in cohort_definitions(inputs):
        cohort_active = active if use_pit_mask else None
        vol_path, selection_audit = build_filtered_vol_path(inputs, cohort_active, eligible)
        vol_weights = weight_frame(vol_path, evaluation_dates(inputs))
        metrics, _, nav = evaluate_stress_blend(
            inputs,
            vol_weights,
            trend_weights,
            stress,
            CANDIDATE_BASE_TREND_WEIGHT,
            CANDIDATE_STRESS_K,
            CANDIDATE_COST_BPS,
        )
        selected = selection_audit["selected_count"]
        candidate = selection_audit["candidate_count"]
        score_count = selection_audit["score_non_null_count"]
        row = {
            "universe": inputs["universe_config"].name,
            "cohort": cohort,
            "eligible_tickers": len(eligible) if eligible is not None else len(active.columns),
            "uses_current_pit_mask": use_pit_mask,
            "avg_candidates": float(candidate.mean()),
            "min_candidates": int(candidate.min()),
            "avg_score_non_null": float(score_count.mean()),
            "min_score_non_null": int(score_count.min()),
            "avg_selected": float(selected.mean()),
            "min_selected": int(selected.min()),
            **metrics,
            "passes_drawdown": bool(metrics["max_dd"] > -0.40),
            "passes_sharpe": bool(metrics["sharpe"] > 0.80),
            "passes_selection_depth": bool(selected.min() >= 20),
        }
        for regime, (start, end) in REGIMES.items():
            scoped = nav.loc[(nav.index >= pd.Timestamp(start)) & (nav.index <= pd.Timestamp(end))]
            if len(scoped) < 2:
                continue
            regime_metrics = calculate_metrics(scoped)
            row[f"{regime}_max_dd"] = regime_metrics.get("Max Drawdown", np.nan)
            row[f"{regime}_sharpe"] = regime_metrics.get("Sharpe", np.nan)
        rows.append(row)
    return pd.DataFrame(rows)


def render_report(universe: pd.DataFrame, coverage: pd.DataFrame, sensitivity: pd.DataFrame) -> str:
    sp500 = sensitivity[sensitivity["universe"] == "sp500_dynamic"]
    baseline = sp500[sp500["cohort"] == "baseline_current_mask"]
    fragile = sensitivity[
        (~sensitivity["passes_drawdown"])
        | (~sensitivity["passes_sharpe"])
        | (~sensitivity["passes_selection_depth"])
    ]
    coverage_flags = coverage[coverage["coverage_p10"] < 0.95]
    active_flags = universe[universe["active_zero_days"] > 0] if "active_zero_days" in universe.columns else pd.DataFrame()
    lines = [
        "# Phase A.7.3 Membership/Coverage Artifact Validation",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Goal: validate that the A.7.2 candidate is not inflated by current-universe, PIT-mask, or missing-data artifacts before portfolio stabilization.",
        "- This is not true historical S&P 500/S&P 100 membership validation; no external historical constituent data is imported.",
        "- Real historical membership data should only be added if this current-setup validation fails or looks fragile.",
        "- Candidate: `vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`, 10 bps cost.",
        "",
        "## Baseline Candidate",
        "",
        baseline.to_markdown(index=False, floatfmt=".4f") if not baseline.empty else "No sp500 baseline row.",
        "",
        "## Universe Audit",
        "",
        universe.to_markdown(index=False, floatfmt=".4f") if not universe.empty else "No universe audit rows.",
        "",
        "## Coverage Flags",
        "",
        coverage_flags.to_markdown(index=False, floatfmt=".4f") if not coverage_flags.empty else "No feature coverage p10 flags below 95%.",
        "",
        "## Active-Count Flags",
        "",
        active_flags.to_markdown(index=False, floatfmt=".4f") if not active_flags.empty else "No zero-active days in audited regimes.",
        "",
        "## Artifact Sensitivity",
        "",
        sensitivity.to_markdown(index=False, floatfmt=".4f") if not sensitivity.empty else "No sensitivity rows.",
        "",
        "## Decision",
        "",
    ]
    if fragile.empty and coverage_flags.empty and active_flags.empty:
        lines.append("- PASS: no current-setup membership/coverage artifact fragility detected.")
    elif fragile.empty:
        lines.append("- WATCH: strategy sensitivity passed, but coverage or active-count flags need review before Phase B.")
    else:
        lines.append("- FAIL/WATCH: at least one artifact cohort failed drawdown, Sharpe, or selection-depth checks.")
    lines.extend(
        [
            "- Interpretation must remain scoped to the configured ticker lists plus current PIT liquidity masks, not true historical index membership.",
            "",
            "## Output Files",
            "",
            "- `artifacts/reports/phase_a7_3_membership_coverage_artifacts.md`",
            "- `artifacts/reports/universe_membership_audit.csv`",
            "- `artifacts/reports/feature_coverage_by_regime.csv`",
            "- `artifacts/reports/artifact_sensitivity.csv`",
        ]
    )
    return "\n".join(lines) + "\n"


def run_universe(config_path: str, universe_path: str, trend_assets: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    inputs = load_inputs(config_path, universe_path, trend_assets)
    logger.info("Running Phase A.7.3 membership/coverage artifact validation for %s", inputs["universe_config"].name)
    return universe_audit(inputs), feature_coverage(inputs), run_artifact_sensitivity(inputs)


def main():
    parser = argparse.ArgumentParser(description="Run Phase A.7.3 membership/coverage artifact validation")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml", "config/universes/sp500.yaml"])
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    universe_frames = []
    coverage_frames = []
    sensitivity_frames = []
    for universe_path in args.universes:
        universe, coverage, sensitivity = run_universe(args.config, universe_path, args.trend_assets)
        universe_frames.append(universe)
        coverage_frames.append(coverage)
        sensitivity_frames.append(sensitivity)

    universe_df = pd.concat(universe_frames, ignore_index=True) if universe_frames else pd.DataFrame()
    coverage_df = pd.concat(coverage_frames, ignore_index=True) if coverage_frames else pd.DataFrame()
    sensitivity_df = pd.concat(sensitivity_frames, ignore_index=True) if sensitivity_frames else pd.DataFrame()

    universe_df.to_csv(reports_dir / "universe_membership_audit.csv", index=False)
    coverage_df.to_csv(reports_dir / "feature_coverage_by_regime.csv", index=False)
    sensitivity_df.to_csv(reports_dir / "artifact_sensitivity.csv", index=False)
    (reports_dir / "phase_a7_3_membership_coverage_artifacts.md").write_text(
        render_report(universe_df, coverage_df, sensitivity_df)
    )
    logger.info("Saved Phase A.7.3 artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
