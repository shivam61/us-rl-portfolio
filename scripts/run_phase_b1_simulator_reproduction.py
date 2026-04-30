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
    evaluate_stress_blend,
    evaluation_dates,
    stress_variant_frame,
    weight_frame,
)
from run_phase_a7_trend_overlay import (  # noqa: E402
    TREND_ASSETS,
    build_trend_weight_paths,
    build_vol_weight_paths,
    load_inputs,
    rebalance_dates,
)
from src.backtest.simulator import ExecutionSimulator  # noqa: E402
from src.config.loader import load_config  # noqa: E402
from src.data.calendar import get_next_trading_day  # noqa: E402
from src.data.ingestion import DataIngestion  # noqa: E402
from src.reporting.metrics import calculate_metrics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CANDIDATE_BASE_TREND_WEIGHT = 0.50
CANDIDATE_STRESS_K = 0.30
CANDIDATE_COST_BPS = 10.0
CANDIDATE_TREND_CAP = 0.75
MAX_GROSS_LIMIT = 1.5
MIN_SELECTED = 20
SHARPE_DRIFT_TOLERANCE = 0.15


def simulator_config(config):
    """Clone config and match A.7.3's all-in 10 bps turnover cost."""
    cfg = config.model_copy(deep=True) if hasattr(config, "model_copy") else config.copy(deep=True)
    cfg.portfolio.transaction_cost_bps = CANDIDATE_COST_BPS
    cfg.portfolio.slippage_bps = 0.0
    cfg.rl.enabled = False
    cfg.intraperiod_risk.enabled = False
    return cfg


def load_price_matrices(config_path: str, universe_path: str, trend_assets: list[str]) -> dict[str, pd.DataFrame]:
    base_config, universe_config = load_config(config_path, universe_path)
    ingestion = DataIngestion(
        cache_dir=base_config.data.cache_dir,
        force_download=False,
        fundamental_provider=base_config.fundamentals.provider,
        fundamental_path=base_config.fundamentals.path,
    )
    tickers = sorted(
        set(
            list(universe_config.tickers.keys())
            + universe_config.sector_etfs
            + universe_config.macro_etfs
            + [universe_config.benchmark, universe_config.vix_proxy]
            + trend_assets
        )
    )
    data_dict = ingestion.fetch_universe_data(tickers=tickers, start_date=base_config.backtest.start_date)
    matrices = ingestion.build_all_matrices(data_dict)
    return {name: frame.ffill() for name, frame in matrices.items()}


def recommended_end_for_universe(universe_name: str, fallback: pd.Timestamp) -> pd.Timestamp:
    guard_path = Path("artifacts/reports/phase_b0_data_window_guard.csv")
    if not guard_path.exists():
        return fallback
    guard = pd.read_csv(guard_path)
    rows = guard[guard["universe"] == universe_name]
    if rows.empty or "recommended_validation_end" not in rows.columns:
        return fallback
    return min(fallback, pd.Timestamp(rows.iloc[0]["recommended_validation_end"]))


def clipped_evaluation_dates(inputs: dict, validation_end: pd.Timestamp) -> list[pd.Timestamp]:
    return [date for date in evaluation_dates(inputs) if date <= validation_end]


def candidate_weight_frame(inputs: dict, validation_end: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    paths = {}
    paths.update(build_vol_weight_paths(inputs))
    paths.update(build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63))
    dates = clipped_evaluation_dates(inputs, validation_end)
    vol_weights = weight_frame(paths[VOL_NAME], dates)
    trend_weights = weight_frame(paths[TREND_NAME], dates)
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)

    columns = vol_weights.columns.union(trend_weights.columns)
    vol = vol_weights.reindex(columns=columns, fill_value=0.0)
    trend = trend_weights.reindex(columns=columns, fill_value=0.0)
    stress_score = stress["stress_score"].reindex(dates).fillna(0.0)
    trend_sleeve_weight = (CANDIDATE_BASE_TREND_WEIGHT + CANDIDATE_STRESS_K * stress_score).clip(
        upper=CANDIDATE_TREND_CAP
    )
    vol_sleeve_weight = (1.0 - trend_sleeve_weight).clip(lower=0.0)
    weights = vol.mul(vol_sleeve_weight, axis=0) + trend.mul(trend_sleeve_weight, axis=0)
    diagnostics = pd.DataFrame(
        {
            "stress_score": stress_score,
            "vol_sleeve_weight": vol_sleeve_weight,
            "trend_sleeve_weight": trend_sleeve_weight,
            "gross_target": weights.abs().sum(axis=1),
            "selected_names": (weights.abs() > 1e-9).sum(axis=1),
        }
    )
    return weights.fillna(0.0), diagnostics


def a73_reference(inputs: dict, target_weights: pd.DataFrame, validation_end: pd.Timestamp) -> tuple[dict, pd.Series]:
    paths = {}
    paths.update(build_vol_weight_paths(inputs))
    paths.update(build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63))
    dates = clipped_evaluation_dates(inputs, validation_end)
    vol_weights = weight_frame(paths[VOL_NAME], dates)
    trend_weights = weight_frame(paths[TREND_NAME], dates)
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)
    row, _, nav = evaluate_stress_blend(
        inputs,
        vol_weights,
        trend_weights,
        stress,
        CANDIDATE_BASE_TREND_WEIGHT,
        CANDIDATE_STRESS_K,
        CANDIDATE_COST_BPS,
        trend_cap=CANDIDATE_TREND_CAP,
    )
    row["avg_turnover_per_period"] = float(target_weights.diff().abs().sum(axis=1).mean())
    row["peak_turnover_per_period"] = float(target_weights.diff().abs().sum(axis=1).max())
    return row, nav


def lagged_matrix_reference(inputs: dict, target_weights: pd.DataFrame) -> tuple[dict, pd.Series]:
    columns = target_weights.columns
    returns = inputs["prices"].pct_change().fillna(0.0).reindex(index=target_weights.index, columns=columns).fillna(0.0)
    executable_weights = target_weights.shift(1).fillna(0.0)
    turnover = executable_weights.diff().abs().sum(axis=1)
    if not executable_weights.empty:
        turnover.iloc[0] = executable_weights.iloc[0].abs().sum()
    raw_returns = (executable_weights * returns).sum(axis=1)
    net_returns = (1.0 - turnover * CANDIDATE_COST_BPS / 10000.0).clip(lower=0.0) * (1.0 + raw_returns) - 1.0
    nav = (1.0 + net_returns).cumprod() * inputs["base_config"].portfolio.initial_capital
    metrics = calculate_metrics(nav)
    daily_gross = executable_weights.abs().sum(axis=1)
    row = {
        "cagr": metrics.get("CAGR", np.nan),
        "sharpe": metrics.get("Sharpe", np.nan),
        "max_dd": metrics.get("Max Drawdown", np.nan),
        "volatility": metrics.get("Volatility", np.nan),
        "turnover_sum": float(turnover.sum()),
        "avg_gross": float(daily_gross.mean()) if not daily_gross.empty else np.nan,
        "max_gross": float(daily_gross.max()) if not daily_gross.empty else np.nan,
        "n_rebalances": int((turnover > 0).sum()),
        "avg_turnover_per_period": float(turnover[turnover > 0].mean()) if (turnover > 0).any() else 0.0,
        "peak_turnover_per_period": float(turnover.max()) if not turnover.empty else 0.0,
    }
    return row, nav


def equal_weight_targets(inputs: dict, validation_end: pd.Timestamp) -> pd.DataFrame:
    dates = clipped_evaluation_dates(inputs, validation_end)
    targets = []
    pit_mask = inputs["pit_mask"]
    tickers = list(inputs["universe_config"].tickers.keys())
    for date in dates:
        if pit_mask is None:
            active = tickers
        else:
            idx = pit_mask.index.get_indexer([date], method="ffill")[0]
            if idx < 0:
                active = []
            else:
                row = pit_mask.iloc[idx]
                active = [ticker for ticker in tickers if bool(row.get(ticker, False))]
        weights = pd.Series(dtype=float)
        if active:
            weights = pd.Series(1.0 / len(active), index=active)
        targets.append(weights.rename(date))
    return pd.DataFrame(targets).fillna(0.0)


def run_simulator(
    inputs: dict,
    matrices: dict[str, pd.DataFrame],
    target_weights: pd.DataFrame,
    validation_end: pd.Timestamp,
    label: str,
    signal_dates: list[pd.Timestamp] | None = None,
    execution_timing: str = "next_day",
    price_mode: str = "raw_open",
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    cfg = simulator_config(inputs["base_config"])
    simulator = ExecutionSimulator(config=cfg)
    prices_adj_close = matrices["adj_close"].reindex(index=inputs["prices"].index).ffill()
    if price_mode == "adj_close":
        prices_open = prices_adj_close
        prices_close = prices_adj_close
    elif price_mode == "raw_open":
        prices_open = matrices["open"].reindex(index=inputs["prices"].index).ffill()
        prices_close = matrices["close"].reindex(index=inputs["prices"].index).ffill()
    else:
        raise ValueError(f"Unsupported price_mode: {price_mode}")
    volume = matrices["volume"].reindex(index=inputs["prices"].index).fillna(0)
    adv = (prices_close * volume).rolling(63, min_periods=1).mean().ffill()

    trading_dates = [date for date in prices_adj_close.index if date <= validation_end]
    rebalances = signal_dates if signal_dates is not None else rebalance_dates(inputs["base_config"], inputs["prices"])
    rebalances = [date for date in rebalances if date <= validation_end and date in target_weights.index]
    execution_by_date = {}
    for signal_date in rebalances:
        if execution_timing == "same_day":
            exec_date = signal_date
        elif execution_timing == "next_day":
            try:
                exec_date = get_next_trading_day(signal_date, trading_dates)
            except ValueError:
                continue
        else:
            raise ValueError(f"Unsupported execution_timing: {execution_timing}")
        if exec_date <= validation_end:
            execution_by_date[exec_date] = signal_date

    if not execution_by_date:
        raise ValueError(f"No executable rebalance dates for {inputs['universe_config'].name}")
    first_execution_date = min(execution_by_date)
    mtm_dates = [date for date in trading_dates if date >= first_execution_date]

    executed_target_gross = []
    executed_target_selected = []
    executed_target_turnover = []
    previous_target = pd.Series(dtype=float)
    for date in mtm_dates:
        if date in execution_by_date:
            signal_date = execution_by_date[date]
            target = target_weights.loc[signal_date]
            target = target[target.abs() > 1e-12]
            idx = previous_target.index.union(target.index)
            executed_target_turnover.append(
                float((target.reindex(idx, fill_value=0.0) - previous_target.reindex(idx, fill_value=0.0)).abs().sum())
            )
            previous_target = target
            executed_target_gross.append(float(target.abs().sum()))
            executed_target_selected.append(int((target.abs() > 1e-9).sum()))
            curr_adv = adv.loc[:signal_date].iloc[-1]
            simulator.rebalance(
                target_weights=target,
                execution_date=date,
                prices_open=prices_open.loc[date],
                prices_close=prices_close.loc[date],
                daily_volume=volume.loc[date],
                adv=curr_adv,
            )
        else:
            simulator.mark_to_market(date, prices_adj_close.loc[date])

    history = simulator.get_history()
    trades = simulator.get_trades()
    metrics = calculate_metrics(history["nav"]) if not history.empty else {}
    turnover = pd.Series(executed_target_turnover, dtype=float)
    row = {
        "universe": inputs["universe_config"].name,
        "runner": label,
        "execution_timing": execution_timing,
        "price_mode": price_mode,
        "start_date": history.index.min().date().isoformat() if not history.empty else "",
        "end_date": history.index.max().date().isoformat() if not history.empty else "",
        "cagr": metrics.get("CAGR", np.nan),
        "sharpe": metrics.get("Sharpe", np.nan),
        "max_dd": metrics.get("Max Drawdown", np.nan),
        "volatility": metrics.get("Volatility", np.nan),
        "avg_turnover_per_rebalance": float(turnover[turnover > 0].mean()) if (turnover > 0).any() else 0.0,
        "peak_turnover_per_rebalance": float(turnover.max()) if not turnover.empty else 0.0,
        "turnover_sum": float(turnover.sum()) if not turnover.empty else 0.0,
        "total_cost": float(history["cost"].sum()) if "cost" in history else 0.0,
        "tc_drag": float(history["tc_drag"].sum()) if "tc_drag" in history else 0.0,
        "slippage_drag": float(history["slippage_drag"].sum()) if "slippage_drag" in history else 0.0,
        "avg_cash_exposure": float(history["cash_exposure"].mean()) if "cash_exposure" in history else np.nan,
        "min_cash_exposure": float(history["cash_exposure"].min()) if "cash_exposure" in history else np.nan,
        "max_target_gross": max(executed_target_gross) if executed_target_gross else np.nan,
        "avg_target_gross": float(np.mean(executed_target_gross)) if executed_target_gross else np.nan,
        "min_selected": min([n for n in executed_target_selected if n > 0], default=0),
        "n_rebalances": len(executed_target_gross),
        "n_trades": len(trades),
    }
    return row, history, trades


def run_universe(config_path: str, universe_path: str, trend_assets: list[str]) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    inputs = load_inputs(config_path, universe_path, trend_assets)
    validation_end = recommended_end_for_universe(inputs["universe_config"].name, inputs["prices"].index.max())
    logger.info("Running Phase B.1 simulator reproduction for %s through %s", inputs["universe_config"].name, validation_end.date())
    matrices = load_price_matrices(config_path, universe_path, trend_assets)
    candidate_weights, target_diag = candidate_weight_frame(inputs, validation_end)
    reference_row, _ = a73_reference(inputs, candidate_weights, validation_end)
    lagged_reference_row, _ = lagged_matrix_reference(inputs, candidate_weights)
    daily_signal_dates = list(candidate_weights.index)
    simulator_row, history, trades = run_simulator(
        inputs,
        matrices,
        candidate_weights,
        validation_end,
        "phase_b1_production_open_next_day",
        signal_dates=daily_signal_dates,
        execution_timing="next_day",
        price_mode="raw_open",
    )
    adjusted_next_row, _, _ = run_simulator(
        inputs,
        matrices,
        candidate_weights,
        validation_end,
        "diagnostic_adj_close_next_day",
        signal_dates=daily_signal_dates,
        execution_timing="next_day",
        price_mode="adj_close",
    )
    aligned_row, _, _ = run_simulator(
        inputs,
        matrices,
        candidate_weights,
        validation_end,
        "diagnostic_adj_close_same_day",
        signal_dates=daily_signal_dates,
        execution_timing="same_day",
        price_mode="adj_close",
    )
    equal_row, _, _ = run_simulator(inputs, matrices, equal_weight_targets(inputs, validation_end), validation_end, "equal_weight_simulator")

    drift = simulator_row["sharpe"] / reference_row["sharpe"] - 1.0 if reference_row["sharpe"] else np.nan
    lagged_drift = (
        simulator_row["sharpe"] / lagged_reference_row["sharpe"] - 1.0 if lagged_reference_row["sharpe"] else np.nan
    )
    summary = {
        "universe": inputs["universe_config"].name,
        "validation_end": validation_end.date().isoformat(),
        "reference_cagr": reference_row["cagr"],
        "reference_sharpe": reference_row["sharpe"],
        "reference_max_dd": reference_row["max_dd"],
        "reference_max_gross": reference_row["max_gross"],
        "lagged_reference_cagr": lagged_reference_row["cagr"],
        "lagged_reference_sharpe": lagged_reference_row["sharpe"],
        "lagged_reference_max_dd": lagged_reference_row["max_dd"],
        "sim_cagr": simulator_row["cagr"],
        "sim_sharpe": simulator_row["sharpe"],
        "sim_max_dd": simulator_row["max_dd"],
        "sim_max_target_gross": simulator_row["max_target_gross"],
        "equal_weight_sharpe": equal_row["sharpe"],
        "sharpe_drift_pct": drift,
        "sharpe_drift_vs_lagged_pct": lagged_drift,
        "avg_turnover_per_rebalance": simulator_row["avg_turnover_per_rebalance"],
        "peak_turnover_per_rebalance": simulator_row["peak_turnover_per_rebalance"],
        "total_cost": simulator_row["total_cost"],
        "n_rebalances": simulator_row["n_rebalances"],
        "n_trades": simulator_row["n_trades"],
        "min_selected": simulator_row["min_selected"],
        "passes_sharpe_drift": bool(np.isfinite(drift) and abs(drift) <= SHARPE_DRIFT_TOLERANCE),
        "passes_lagged_sharpe_drift": bool(np.isfinite(lagged_drift) and abs(lagged_drift) <= SHARPE_DRIFT_TOLERANCE),
        "passes_max_dd": bool(simulator_row["max_dd"] > -0.40),
        "passes_max_gross": bool(simulator_row["max_target_gross"] <= MAX_GROSS_LIMIT),
        "passes_equal_weight": bool(simulator_row["sharpe"] > equal_row["sharpe"]),
        "passes_selection_depth": bool(simulator_row["min_selected"] >= MIN_SELECTED),
    }
    summary["passes_b1_gate"] = bool(
        summary["passes_sharpe_drift"]
        and summary["passes_max_dd"]
        and summary["passes_max_gross"]
        and summary["passes_equal_weight"]
        and summary["passes_selection_depth"]
    )
    summary["passes_reconciled_b1_gate"] = bool(
        summary["passes_lagged_sharpe_drift"]
        and summary["passes_max_dd"]
        and summary["passes_max_gross"]
        and summary["passes_equal_weight"]
        and summary["passes_selection_depth"]
    )

    detail = pd.DataFrame(
        [
            {"runner": "a7_3_matrix_reference", "execution_timing": "same_day", "price_mode": "adj_close", **reference_row},
            {
                "runner": "lagged_matrix_reference",
                "execution_timing": "next_day_proxy",
                "price_mode": "adj_close",
                **lagged_reference_row,
            },
            simulator_row,
            adjusted_next_row,
            aligned_row,
            equal_row,
        ]
    )
    target_diag = target_diag.reset_index(names="date")
    history.to_csv(Path("artifacts/reports") / f"phase_b1_{inputs['universe_config'].name}_history.csv")
    trades.to_csv(Path("artifacts/reports") / f"phase_b1_{inputs['universe_config'].name}_trades.csv", index=False)
    target_diag.to_csv(Path("artifacts/reports") / f"phase_b1_{inputs['universe_config'].name}_target_diagnostics.csv", index=False)
    return summary, detail, trades


def render_report(summary: pd.DataFrame, detail: pd.DataFrame) -> str:
    failed = summary[~summary["passes_b1_gate"]] if not summary.empty else pd.DataFrame()
    lines = [
        "# Phase B.1 Simulator Reproduction",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Goal: reproduce the A.7.3 candidate in the production execution simulator before portfolio stabilization changes.",
        "- Candidate: `vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`, trend cap `0.75`.",
        "- Cost assumption: all-in `10` bps turnover cost, modeled as transaction cost with simulator slippage set to `0` for parity.",
        "- Signal construction, sleeve weights, stress scaling, and rebalance schedule are inherited from A.7.3.",
        "- Simulator differences versus A.7.3 reference: next-trading-day open execution, cash/share accounting, ADV and participation checks, close mark-to-market.",
        "- The candidate simulator path executes the daily stress-scaled target path because A.7.3 changes the volatility/trend sleeve mix daily between 4-week sleeve refreshes.",
        "- Diagnostic rows isolate adjusted-close execution and same-day timing; promotion still uses the production open/next-day row.",
        "- The lagged matrix reference shifts target weights by one trading day to remove same-day signal/return alignment from A.7.3.",
        "",
        "## Gate Summary",
        "",
        summary.to_markdown(index=False, floatfmt=".4f") if not summary.empty else "No summary rows.",
        "",
        "## Runner Detail",
        "",
        detail.to_markdown(index=False, floatfmt=".4f") if not detail.empty else "No detail rows.",
        "",
        "## Decision",
        "",
    ]
    reconciled_failed = summary[~summary["passes_reconciled_b1_gate"]] if "passes_reconciled_b1_gate" in summary else summary
    if failed.empty:
        lines.append("- PASS: B.1 reproduction is within tolerance; Phase B can proceed to B.2 turnover smoothing.")
    elif reconciled_failed.empty:
        lines.append(
            "- RECONCILED: original A.7.3 same-day matrix baseline fails the reproduction gate, but the production simulator is within tolerance versus the lagged matrix reference."
        )
        lines.append(
            "- Action: reset the Phase B baseline to the production open/next-day simulator row before proceeding; do not use the unlagged A.7.3 headline as a promotion baseline."
        )
    else:
        lines.append("- FAIL: do not proceed to B.2 until reproduction drift is reconciled.")
    lines.extend(
        [
            "- Drift attribution should focus on execution timing, cash/share accounting, liquidity filtering, and cost timing; alpha and stress logic were unchanged.",
            "",
            "## Output Files",
            "",
            "- `artifacts/reports/phase_b1_simulator_reproduction.md`",
            "- `artifacts/reports/phase_b1_simulator_reproduction.csv`",
            "- `artifacts/reports/phase_b1_runner_detail.csv`",
            "- `artifacts/reports/phase_b1_<universe>_history.csv`",
            "- `artifacts/reports/phase_b1_<universe>_trades.csv`",
            "- `artifacts/reports/phase_b1_<universe>_target_diagnostics.csv`",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase B.1 simulator reproduction")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml", "config/universes/sp500.yaml"])
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    details = []
    for universe_path in args.universes:
        summary, detail, _ = run_universe(args.config, universe_path, args.trend_assets)
        summaries.append(summary)
        details.append(detail)

    summary_df = pd.DataFrame(summaries)
    detail_df = pd.concat(details, ignore_index=True) if details else pd.DataFrame()
    summary_df.to_csv(reports_dir / "phase_b1_simulator_reproduction.csv", index=False)
    detail_df.to_csv(reports_dir / "phase_b1_runner_detail.csv", index=False)
    (reports_dir / "phase_b1_simulator_reproduction.md").write_text(render_report(summary_df, detail_df))
    logger.info("Saved Phase B.1 simulator reproduction artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
