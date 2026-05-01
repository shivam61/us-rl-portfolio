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

from run_phase_a7_1_drawdown_control import TREND_NAME, VOL_NAME, stress_frame  # noqa: E402
from run_phase_a7_2_robustness import stress_variant_frame, weight_frame  # noqa: E402
from run_phase_a7_trend_overlay import (  # noqa: E402
    TREND_ASSETS,
    build_trend_weight_paths,
    equal_weights,
    load_inputs,
    rebalance_dates,
)
from run_phase_b1_simulator_reproduction import (  # noqa: E402
    CANDIDATE_BASE_TREND_WEIGHT,
    CANDIDATE_STRESS_K,
    CANDIDATE_TREND_CAP,
    MAX_GROSS_LIMIT,
    clipped_evaluation_dates,
    recommended_end_for_universe,
)
from src.reporting.metrics import calculate_metrics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("src.backtest.simulator").setLevel(logging.ERROR)

B1_SP500_CAGR = 0.1756
B1_SP500_SHARPE = 1.116
B1_SP500_MAX_DD = -0.2698
B1_SP500_TURNOVER = 230.7242
B1_COST_BPS = 10.0
COST_BPS = [10.0, 25.0, 50.0]
TRADE_THRESHOLDS = [0.0025, 0.0050, 0.0100]
PERSISTENCE_EXIT_RANKS = [30, 40]
PARTIAL_REBALANCE_RATIOS = [0.50, 0.75, 1.00]


@dataclass(frozen=True)
class Variant:
    sleeve: str
    trade_threshold: float = 0.0
    persistence_exit_rank: int | None = None
    update_frequency: str = "daily"
    partial_rebalance: float = 1.0
    cost_bps: float = B1_COST_BPS

    @property
    def name(self) -> str:
        parts = [self.sleeve]
        if self.trade_threshold:
            parts.append(f"thr_{int(self.trade_threshold * 10000)}bps")
        if self.persistence_exit_rank:
            parts.append(f"persist_top{self.persistence_exit_rank}")
        if self.update_frequency != "daily":
            parts.append(self.update_frequency)
        if self.partial_rebalance != 1.0:
            parts.append(f"partial_{int(self.partial_rebalance * 100)}")
        parts.append(f"cost_{int(self.cost_bps)}bps")
        return "_".join(parts)


def volatility_score_matrix(inputs: dict) -> pd.DataFrame:
    return inputs["vol_scores"]["volatility_score"].unstack().sort_index().ffill()


def active_mask_frame(inputs: dict, dates: list[pd.Timestamp], columns: pd.Index) -> pd.DataFrame:
    pit_mask = inputs["pit_mask"]
    if pit_mask is None:
        return pd.DataFrame(True, index=dates, columns=columns)
    return pit_mask.reindex(dates, method="ffill").reindex(columns=columns, fill_value=False).fillna(False).astype(bool)


def build_vol_path_fast(inputs: dict, exit_rank: int | None) -> dict:
    weights_by_date = {}
    selected_by_date = {}
    previous: list[str] = []
    dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    scores_by_date = volatility_score_matrix(inputs).reindex(dates, method="ffill")
    active = active_mask_frame(inputs, dates, scores_by_date.columns)
    for date in dates:
        scores = scores_by_date.loc[date].where(active.loc[date]).dropna()
        ranked = scores.sort_values(ascending=False)
        if exit_rank is None:
            selected = ranked.head(20).index.tolist()
        else:
            rank_map = pd.Series(np.arange(1, len(ranked) + 1), index=ranked.index)
            keep = [ticker for ticker in previous if ticker in rank_map.index and rank_map.loc[ticker] <= exit_rank]
            entrants = [ticker for ticker in ranked.head(20).index if ticker not in keep]
            selected = (keep + entrants)[:20]
        weights_by_date[date] = equal_weights(selected)
        selected_by_date[date] = selected
        previous = selected
    sleeve_type = "volatility" if exit_rank is None else "volatility_persistent"
    return {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": sleeve_type}


def combine_candidate_weights(
    dates: list[pd.Timestamp],
    vol_path: dict,
    trend_path: dict,
    stress: pd.DataFrame,
) -> pd.DataFrame:
    vol_weights = weight_frame(vol_path, dates)
    trend_weights = weight_frame(trend_path, dates)
    columns = vol_weights.columns.union(trend_weights.columns)
    vol = vol_weights.reindex(columns=columns, fill_value=0.0)
    trend = trend_weights.reindex(columns=columns, fill_value=0.0)
    stress_score = stress["stress_score"].reindex(dates).fillna(0.0)
    trend_sleeve_weight = (CANDIDATE_BASE_TREND_WEIGHT + CANDIDATE_STRESS_K * stress_score).clip(
        upper=CANDIDATE_TREND_CAP
    )
    vol_sleeve_weight = (1.0 - trend_sleeve_weight).clip(lower=0.0)
    return (vol.mul(vol_sleeve_weight, axis=0) + trend.mul(trend_sleeve_weight, axis=0)).fillna(0.0)


def candidate_weights_with_persistence(
    dates: list[pd.Timestamp],
    vol_path: dict,
    trend_path: dict,
    stress: pd.DataFrame,
) -> pd.DataFrame:
    return combine_candidate_weights(dates, vol_path, trend_path, stress)


def signal_dates_for_frequency(inputs: dict, target_weights: pd.DataFrame, validation_end: pd.Timestamp, frequency: str) -> list[pd.Timestamp]:
    dates = list(target_weights.index[target_weights.index <= validation_end])
    if frequency == "daily":
        return dates
    configured = [date for date in rebalance_dates(inputs["base_config"], inputs["prices"]) if date <= validation_end]
    configured = [date for date in configured if date in target_weights.index]
    if frequency == "every_2_rebalances":
        return configured[::2]
    if frequency == "4w":
        return configured[::4]
    raise ValueError(f"Unsupported update frequency: {frequency}")


def apply_execution_controls(
    target_weights: pd.DataFrame,
    signal_dates: list[pd.Timestamp],
    trade_threshold: float,
    partial_rebalance: float,
) -> pd.DataFrame:
    rows = []
    current = pd.Series(dtype=float)
    signal_set = set(signal_dates)
    for date, target_row in target_weights.iterrows():
        if date in signal_set:
            raw_target = target_row[target_row.abs() > 1e-12]
            idx = current.index.union(raw_target.index)
            current_aligned = current.reindex(idx, fill_value=0.0)
            raw_aligned = raw_target.reindex(idx, fill_value=0.0)
            desired = current_aligned + partial_rebalance * (raw_aligned - current_aligned)
            if trade_threshold > 0:
                diff = desired - current_aligned
                desired = desired.where(diff.abs() >= trade_threshold, current_aligned)
            current = desired[desired.abs() > 1e-12]
        rows.append(current.rename(date))
    return pd.DataFrame(rows).fillna(0.0)


def run_execution_simulator(
    inputs: dict,
    target_weights: pd.DataFrame,
    validation_end: pd.Timestamp,
    variant: Variant,
) -> dict:
    dates = target_weights.index[target_weights.index <= validation_end]
    weights = target_weights.reindex(dates).fillna(0.0)
    executable_weights = weights.shift(1).fillna(0.0)
    returns = inputs["prices"].pct_change().fillna(0.0).reindex(index=dates, columns=weights.columns).fillna(0.0)
    turnover = executable_weights.diff().abs().sum(axis=1)
    if not executable_weights.empty:
        turnover.iloc[0] = executable_weights.iloc[0].abs().sum()
    gross = executable_weights.abs().sum(axis=1)
    selected = (executable_weights.abs() > 1e-9).sum(axis=1)
    raw_returns = (executable_weights * returns).sum(axis=1)
    cost_rate = variant.cost_bps / 10000.0
    net_returns = (1.0 - turnover * cost_rate).clip(lower=0.0) * (1.0 + raw_returns) - 1.0
    nav = (1.0 + net_returns).cumprod() * inputs["base_config"].portfolio.initial_capital
    metrics = calculate_metrics(nav)
    nav_before = nav.shift(1).fillna(inputs["base_config"].portfolio.initial_capital)
    total_cost = float((nav_before * turnover * cost_rate).sum())
    changed = executable_weights.diff().abs() > 1e-12
    if not changed.empty:
        changed.iloc[0] = executable_weights.iloc[0].abs() > 1e-12
    row = {
        "universe": inputs["universe_config"].name,
        "runner": variant.name,
        "execution_timing": "next_day_weight_lag",
        "price_mode": "adj_close_fast",
        "start_date": nav.index.min().date().isoformat() if not nav.empty else "",
        "end_date": nav.index.max().date().isoformat() if not nav.empty else "",
        "cagr": metrics.get("CAGR", np.nan),
        "sharpe": metrics.get("Sharpe", np.nan),
        "max_dd": metrics.get("Max Drawdown", np.nan),
        "volatility": metrics.get("Volatility", np.nan),
        "avg_turnover_per_rebalance": float(turnover[turnover > 0].mean()) if (turnover > 0).any() else 0.0,
        "peak_turnover_per_rebalance": float(turnover.max()) if not turnover.empty else 0.0,
        "turnover_sum": float(turnover.sum()) if not turnover.empty else 0.0,
        "total_cost": total_cost,
        "tc_drag": total_cost,
        "slippage_drag": 0.0,
        "avg_cash_exposure": float((1.0 - gross).mean()) if not gross.empty else np.nan,
        "min_cash_exposure": float((1.0 - gross).min()) if not gross.empty else np.nan,
        "max_target_gross": float(gross.max()) if not gross.empty else np.nan,
        "avg_target_gross": float(gross.mean()) if not gross.empty else np.nan,
        "min_selected": int(selected[selected > 0].min()) if (selected > 0).any() else 0,
        "n_rebalances": int((turnover > 0).sum()),
        "n_trades": int(changed.sum().sum()) if not changed.empty else 0,
    }
    row.update(
        {
            "variant": variant.name,
            "sleeve": variant.sleeve,
            "trade_threshold": variant.trade_threshold,
            "persistence_exit_rank": variant.persistence_exit_rank,
            "update_frequency": variant.update_frequency,
            "partial_rebalance": variant.partial_rebalance,
            "cost_bps": variant.cost_bps,
        }
    )
    return row


def evaluate_variant(
    inputs: dict,
    raw_weights_by_persistence: dict[int | None, pd.DataFrame],
    validation_end: pd.Timestamp,
    variant: Variant,
) -> dict:
    raw = raw_weights_by_persistence[variant.persistence_exit_rank]
    signal_dates = signal_dates_for_frequency(inputs, raw, validation_end, variant.update_frequency)
    controlled = apply_execution_controls(raw, signal_dates, variant.trade_threshold, variant.partial_rebalance)
    target_turnover = controlled.diff().abs().sum(axis=1)
    if not controlled.empty:
        target_turnover.iloc[0] = controlled.iloc[0].abs().sum()
    changed_dates = list(target_turnover[target_turnover > 1e-12].index)
    row = run_execution_simulator(inputs, controlled, validation_end, variant)
    row["raw_signal_dates"] = len(signal_dates)
    row["controlled_signal_dates"] = len(changed_dates)
    row["passes_sharpe"] = bool(row["sharpe"] >= B1_SP500_SHARPE - 0.10) if row["universe"] == "sp500_dynamic" else np.nan
    row["passes_max_dd"] = bool(row["max_dd"] > -0.35) if row["universe"] == "sp500_dynamic" else np.nan
    row["passes_cagr"] = bool(row["cagr"] >= B1_SP500_CAGR - 0.02) if row["universe"] == "sp500_dynamic" else np.nan
    row["passes_gross"] = bool(row["max_target_gross"] <= MAX_GROSS_LIMIT)
    row["turnover_reduction_pct"] = (
        1.0 - row["turnover_sum"] / B1_SP500_TURNOVER if row["universe"] == "sp500_dynamic" else np.nan
    )
    row["passes_turnover"] = bool(row["turnover_reduction_pct"] >= 0.10) if row["universe"] == "sp500_dynamic" else np.nan
    return row


def build_variants(cost_bps: float = B1_COST_BPS) -> list[Variant]:
    variants = [Variant("baseline", cost_bps=cost_bps)]
    variants.extend(Variant("threshold", trade_threshold=threshold, cost_bps=cost_bps) for threshold in TRADE_THRESHOLDS)
    variants.extend(Variant("persistence", persistence_exit_rank=rank, cost_bps=cost_bps) for rank in PERSISTENCE_EXIT_RANKS)
    variants.extend(
        Variant("frequency", update_frequency=frequency, cost_bps=cost_bps)
        for frequency in ["every_2_rebalances", "4w"]
    )
    variants.extend(
        Variant("partial", partial_rebalance=ratio, cost_bps=cost_bps)
        for ratio in PARTIAL_REBALANCE_RATIOS
        if ratio < 1.0
    )
    variants.extend(
        Variant("combo", trade_threshold=threshold, persistence_exit_rank=rank, partial_rebalance=ratio, cost_bps=cost_bps)
        for threshold in [0.0025, 0.0050]
        for rank in PERSISTENCE_EXIT_RANKS
        for ratio in [0.75, 1.0]
    )
    return variants


def add_cost_pass_flags(cost_df: pd.DataFrame, frontier_10bps: pd.DataFrame) -> pd.DataFrame:
    if cost_df.empty:
        return cost_df
    base = cost_df[(cost_df["sleeve"] == "baseline") & (cost_df["universe"] == "sp500_dynamic")]
    base_by_cost = base.set_index("cost_bps")["sharpe"].to_dict()
    cost_df = cost_df.copy()
    cost_df["baseline_cost_sharpe"] = cost_df["cost_bps"].map(base_by_cost)
    cost_df["improves_vs_baseline_cost_sharpe"] = cost_df["sharpe"] >= cost_df["baseline_cost_sharpe"]
    def control_key(row) -> tuple:
        exit_rank = None if pd.isna(row.persistence_exit_rank) else int(row.persistence_exit_rank)
        return (
            row.universe,
            row.sleeve,
            round(float(row.trade_threshold), 8),
            exit_rank,
            row.update_frequency,
            round(float(row.partial_rebalance), 8),
        )

    pass_map = {
        control_key(row): bool(row.passes_b2_candidate)
        for row in frontier_10bps.itertuples()
    }
    cost_df["passes_10bps_candidate"] = [
        pass_map.get(control_key(row), False)
        for row in cost_df.itertuples()
    ]
    return cost_df


def render_report(frontier: pd.DataFrame, cost: pd.DataFrame) -> str:
    sp500 = frontier[frontier["universe"] == "sp500_dynamic"].copy()
    eligible = sp500[sp500["passes_b2_candidate"]].sort_values(
        ["turnover_reduction_pct", "sharpe"], ascending=[False, False]
    )
    cost_50 = cost[(cost["universe"] == "sp500_dynamic") & (cost["cost_bps"] == 50.0)].copy()
    lines = [
        "# Phase B.2 Turnover Control / Rebalance Hysteresis",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Goal: reduce turnover/cost drag without materially changing the B.1 return profile.",
        "- Baseline: B.1 production simulator on `sp500_dynamic` clipped to `2026-04-24`: CAGR `17.56%`, Sharpe `1.116`, MaxDD `-26.98%`, max gross `1.375`.",
        "- Method: fast one-day-lagged target-weight execution approximation for turnover frontier selection; B.1 exact open/next-day simulator remains the Phase B promotion anchor.",
        "- Scope: no `volatility_score` changes, no trend-signal changes, no stress-formula changes, RL disabled.",
        "",
        "## B.2 Gates",
        "",
        "- Sharpe must stay at least `B.1 - 0.10` (`>=1.016` on sp500).",
        "- MaxDD must remain better than `-35%`.",
        "- CAGR drop must be `<=2` percentage points.",
        "- Turnover must drop meaningfully, defined here as at least `10%` lower than B.1 turnover.",
        "- 50 bps cost-adjusted Sharpe should improve or remain competitive versus the B.1 cost baseline.",
        "",
        "## Passing 10 bps Frontier Rows",
        "",
        eligible.to_markdown(index=False, floatfmt=".4f") if not eligible.empty else "No B.2 candidate rows passed all 10 bps gates.",
        "",
        "## Full 10 bps Frontier",
        "",
        sp500.sort_values(["passes_b2_candidate", "turnover_reduction_pct", "sharpe"], ascending=[False, False, False]).to_markdown(index=False, floatfmt=".4f")
        if not sp500.empty
        else "No sp500 rows.",
        "",
        "## 50 bps Cost Sensitivity",
        "",
        cost_50.sort_values(["improves_vs_baseline_cost_sharpe", "sharpe"], ascending=[False, False]).to_markdown(index=False, floatfmt=".4f")
        if not cost_50.empty
        else "No 50 bps cost rows.",
        "",
        "## Decision",
        "",
    ]
    if eligible.empty:
        lines.append("- FAIL/WATCH: no turnover-control variant passed all B.2 gates at 10 bps.")
    else:
        best = eligible.iloc[0]
        lines.append(
            f"- PASS: best B.2 candidate is `{best['variant']}` with Sharpe `{best['sharpe']:.3f}`, CAGR `{best['cagr']:.2%}`, MaxDD `{best['max_dd']:.2%}`, and turnover reduction `{best['turnover_reduction_pct']:.1%}`."
        )
    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `artifacts/reports/phase_b2_turnover_control.md`",
            "- `artifacts/reports/turnover_frontier.csv`",
            "- `artifacts/reports/cost_sensitivity.csv`",
            "- `artifacts/reports/trade_threshold_results.csv`",
            "- `artifacts/reports/persistence_results.csv`",
        ]
    )
    return "\n".join(lines) + "\n"


def run_universe(config_path: str, universe_path: str, trend_assets: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    inputs = load_inputs(config_path, universe_path, trend_assets)
    validation_end = recommended_end_for_universe(inputs["universe_config"].name, inputs["prices"].index.max())
    logger.info("Running Phase B.2 turnover controls for %s through %s", inputs["universe_config"].name, validation_end.date())

    started = time.perf_counter()
    persistence_keys = {variant.persistence_exit_rank for variant in build_variants(B1_COST_BPS)}
    dates = clipped_evaluation_dates(inputs, validation_end)
    logger.info("Prepared %d evaluation dates in %.1fs", len(dates), time.perf_counter() - started)
    started = time.perf_counter()
    trend_path = build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63)[TREND_NAME]
    logger.info("Built trend path in %.1fs", time.perf_counter() - started)
    started = time.perf_counter()
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)
    logger.info("Built stress path in %.1fs", time.perf_counter() - started)
    started = time.perf_counter()
    raw_weights_by_persistence = {
        exit_rank: candidate_weights_with_persistence(
            dates,
            build_vol_path_fast(inputs, exit_rank),
            trend_path,
            stress,
        )
        for exit_rank in sorted(persistence_keys, key=lambda value: -1 if value is None else value)
    }
    logger.info("Built raw weight paths in %.1fs", time.perf_counter() - started)

    started = time.perf_counter()
    frontier_rows = [
        evaluate_variant(inputs, raw_weights_by_persistence, validation_end, variant)
        for variant in build_variants(B1_COST_BPS)
    ]
    logger.info("Evaluated 10 bps frontier in %.1fs", time.perf_counter() - started)
    frontier = pd.DataFrame(frontier_rows)
    if inputs["universe_config"].name == "sp500_dynamic":
        frontier["passes_b2_candidate"] = (
            frontier["passes_sharpe"]
            & frontier["passes_max_dd"]
            & frontier["passes_cagr"]
            & frontier["passes_gross"]
            & frontier["passes_turnover"]
        )
    else:
        frontier["passes_b2_candidate"] = False

    candidates = frontier[(frontier["universe"] == "sp500_dynamic") & (frontier["passes_b2_candidate"])]
    cost_variants = [Variant("baseline", cost_bps=cost) for cost in COST_BPS]
    for row in candidates.sort_values(["turnover_reduction_pct", "sharpe"], ascending=[False, False]).head(8).itertuples():
        for cost_bps in COST_BPS:
            cost_variants.append(
                Variant(
                    row.sleeve,
                    trade_threshold=float(row.trade_threshold),
                    persistence_exit_rank=None if pd.isna(row.persistence_exit_rank) else int(row.persistence_exit_rank),
                    update_frequency=row.update_frequency,
                    partial_rebalance=float(row.partial_rebalance),
                    cost_bps=cost_bps,
                )
            )
    seen = set()
    deduped = []
    for variant in cost_variants:
        key = variant.name
        if key not in seen:
            deduped.append(variant)
            seen.add(key)
    started = time.perf_counter()
    cost_rows = [
        evaluate_variant(inputs, raw_weights_by_persistence, validation_end, variant)
        for variant in deduped
    ]
    logger.info("Evaluated cost sensitivity in %.1fs", time.perf_counter() - started)
    return frontier, pd.DataFrame(cost_rows)


def main():
    parser = argparse.ArgumentParser(description="Run Phase B.2 turnover control / rebalance hysteresis")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp500.yaml"])
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    frontier_frames = []
    cost_frames = []
    for universe_path in args.universes:
        frontier, cost = run_universe(args.config, universe_path, args.trend_assets)
        frontier_frames.append(frontier)
        cost_frames.append(cost)

    frontier_df = pd.concat(frontier_frames, ignore_index=True) if frontier_frames else pd.DataFrame()
    cost_df = pd.concat(cost_frames, ignore_index=True) if cost_frames else pd.DataFrame()
    cost_df = add_cost_pass_flags(cost_df, frontier_df[frontier_df["cost_bps"] == B1_COST_BPS])

    frontier_df.to_csv(reports_dir / "turnover_frontier.csv", index=False)
    cost_df.to_csv(reports_dir / "cost_sensitivity.csv", index=False)
    frontier_df[frontier_df["sleeve"].isin(["baseline", "threshold"])].to_csv(
        reports_dir / "trade_threshold_results.csv", index=False
    )
    frontier_df[frontier_df["sleeve"].isin(["baseline", "persistence", "combo"])].to_csv(
        reports_dir / "persistence_results.csv", index=False
    )
    (reports_dir / "phase_b2_turnover_control.md").write_text(render_report(frontier_df, cost_df))
    logger.info("Saved Phase B.2 turnover artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
