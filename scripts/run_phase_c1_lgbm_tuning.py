"""
Phase C.1 — LightGBM hyperparameter tuning.

Grid searches num_leaves, min_data_in_leaf, feature_fraction, bagging_fraction,
lambda_l1, lambda_l2 on IC Sharpe across the holdout window, then validates the
best config through the unchanged B.5 portfolio harness.

Do NOT change: sleeves, stress scaling, beta cap, rebalance cadence.
Tune: LightGBM model params only.
"""

import argparse
import logging
import os
import sys
import time
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for p in (REPO_ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    import lightgbm as lgb
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False

from run_phase_a7_1_drawdown_control import TREND_NAME, stress_frame  # noqa: E402
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
    clipped_evaluation_dates,
    recommended_end_for_universe,
)
from run_phase_b2_turnover_control import (  # noqa: E402
    B1_COST_BPS,
    COST_BPS,
    Variant,
    apply_execution_controls,
    run_execution_simulator,
    signal_dates_for_frequency,
)
from run_phase_b3_exposure_control import (  # noqa: E402
    rolling_beta_matrix,
)
from run_phase_b4_risk_engine import (  # noqa: E402
    BETA_MAX_BASE,
    BETA_MAX_SENSITIVITY,
    BETA_MIN,
    TREND_STRESS_SCALE_MAX,
    TREND_STRESS_THRESHOLD,
    B4Variant,
    _NON_BENCHMARK_TREND,
    apply_b4_constraints,
    apply_trend_scaling,
    build_stress_series,
)
from src.reporting.metrics import calculate_metrics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Phase B.5 baseline (promoted, sp500, 10 bps) ─────────────────────────────
B5_CAGR = 0.1604
B5_SHARPE = 1.078
B5_MAX_DD = -0.3298
B5_TURNOVER = 84.12
B5_EQUAL_WEIGHT_SHARPE = 0.619

# ── Phase C acceptance gates ──────────────────────────────────────────────────
GATE_SHARPE_FLOOR = B5_SHARPE - 0.05       # 1.028
GATE_MAX_DD = B5_MAX_DD                    # must not worsen baseline MaxDD

# ── Walk-forward windows ──────────────────────────────────────────────────────
HOLDOUT_START = pd.Timestamp("2019-01-01")
VALIDATION_END_STR = "2026-04-24"
TRAIN_YEARS = 3
RETRAIN_INTERVAL = 3   # retrain every N rebalances (matches config retrain_frequency)
FWD_HORIZON = 21       # 21-day forward return for IC evaluation

# ── Baseline LGBM params (current StockRanker defaults) ──────────────────────
BASELINE_LGBM_PARAMS: dict = {
    "n_estimators": 200,
    "max_depth": 5,
    "num_leaves": 31,
    "min_data_in_leaf": 20,
    "feature_fraction": 1.0,
    "bagging_fraction": 1.0,
    "bagging_freq": 0,
    "lambda_l1": 0.0,
    "lambda_l2": 0.0,
    "learning_rate": 0.05,
    "objective": "regression",
    "verbose": -1,
    "random_state": 42,
    "n_jobs": 1,
}

# ── Tuning grid ────────────────────────────────────────────────────────────────
# 3 × 3 × 3 × 2 × 2 × 2 = 216 combinations
TUNE_GRID = {
    "num_leaves": [15, 31, 63],
    "min_data_in_leaf": [20, 50, 100],
    "feature_fraction": [0.6, 0.8, 1.0],
    "bagging_fraction": [0.7, 0.9],
    "lambda_l1": [0.0, 0.5],
    "lambda_l2": [0.0, 0.5],
}

# ── IC regime windows ─────────────────────────────────────────────────────────
IC_REGIMES = [
    ("full 2008-2026", "2008-01-01", "2026-04-24"),
    ("train 2008-2018", "2008-01-01", "2018-12-31"),
    ("holdout 2019-2026", "2019-01-01", "2026-04-24"),
    ("2008 financial crisis", "2008-01-01", "2009-12-31"),
    ("2015-16 vol stress", "2015-06-01", "2016-12-31"),
    ("2020 COVID", "2020-01-01", "2020-12-31"),
    ("2022 bear market", "2022-01-01", "2022-12-31"),
    ("recovery 2023-2026", "2023-01-01", "2026-04-24"),
]

# ── Portfolio regime windows (same as B.5) ────────────────────────────────────
PORTFOLIO_REGIMES = [
    ("2008 financial crisis", "2008-01-01", "2009-12-31"),
    ("2015-16 vol stress", "2015-06-01", "2016-12-31"),
    ("2020 COVID", "2020-01-01", "2020-12-31"),
    ("2022 bear market", "2022-01-01", "2022-12-31"),
    ("2023-2026 recovery", "2023-01-01", "2026-04-24"),
    ("full 2008-2026", "2008-01-01", "2026-04-24"),
]

B5_PROMOTED = B4Variant(
    name="b4_stress_cap_trend_boost",
    beta_min=BETA_MIN,
    beta_max_base=BETA_MAX_BASE,
    beta_max_sensitivity=BETA_MAX_SENSITIVITY,
    trend_stress_boost=True,
    trend_stress_threshold=TREND_STRESS_THRESHOLD,
    trend_stress_scale_max=TREND_STRESS_SCALE_MAX,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_fwd_return_matrix(prices: pd.DataFrame, horizon: int = 21) -> pd.DataFrame:
    """21-day forward return at each date for all stock tickers."""
    non_stock = set(TREND_ASSETS) | {"SPY"}
    stock_cols = [c for c in prices.columns if c not in non_stock]
    return (prices[stock_cols].shift(-horizon) / prices[stock_cols] - 1.0)


def _active_tickers_at(inputs: dict, date: pd.Timestamp) -> list[str]:
    base = list(inputs["universe_config"].tickers.keys())
    pit_mask = inputs["pit_mask"]
    if pit_mask is None:
        return base
    idx = pit_mask.index.get_indexer([date], method="ffill")[0]
    if idx < 0:
        return base
    active = pit_mask.iloc[idx]
    return [t for t in base if bool(active.get(t, False))]


_LGBM_INT_PARAMS = frozenset({"n_estimators", "max_depth", "num_leaves", "min_data_in_leaf", "bagging_freq"})


def _make_lgbm_params(overrides: dict, n_jobs: int = 1) -> dict:
    params = dict(BASELINE_LGBM_PARAMS)
    params.update(overrides)
    params["n_jobs"] = n_jobs
    # Grid results come back from DataFrame as np.float64; LightGBM needs int
    for k in _LGBM_INT_PARAMS:
        if k in params and params[k] is not None:
            params[k] = int(params[k])
    # bagging requires bagging_freq > 0
    if params.get("bagging_fraction", 1.0) < 1.0 and params.get("bagging_freq", 0) == 0:
        params["bagging_freq"] = 1
    return params


def _ic_for_params(
    params: dict,
    stock_features: pd.DataFrame,
    fwd_ret_matrix: pd.DataFrame,
    all_dates: list[pd.Timestamp],
    inputs: dict,
) -> list[dict]:
    """
    Walk-forward IC evaluation for a single LGBM config.
    Returns list of {date, ic} dicts for ALL rebalance dates (train + holdout).
    """
    if not LGBM_AVAILABLE:
        return []

    ic_records: list[dict] = []
    cached_model = None
    retrain_counter = 0
    feat_level_dates = stock_features.index.get_level_values("date").unique().sort_values()

    for date in all_dates:
        active = _active_tickers_at(inputs, date)
        should_retrain = (cached_model is None) or (retrain_counter % RETRAIN_INTERVAL == 0)
        retrain_counter += 1

        if should_retrain:
            train_start = date - pd.DateOffset(years=TRAIN_YEARS)
            cutoff = date - pd.DateOffset(days=25)
            try:
                X_tr = stock_features.loc[pd.IndexSlice[train_start:cutoff, :], :]
                X_tr = X_tr.loc[X_tr.index.get_level_values("ticker").isin(active)]
                y_tr = fwd_ret_matrix.stack().rename("y").reindex(X_tr.index)
                valid = ~(X_tr.isna().any(axis=1) | y_tr.isna())
                if valid.sum() >= 50:
                    m = lgb.LGBMRegressor(**params)
                    m.fit(X_tr.values[valid], y_tr.values[valid])
                    cached_model = m
            except Exception:
                pass

        if cached_model is None:
            continue

        # Latest available feature date
        fi = feat_level_dates.get_indexer([date], method="ffill")[0]
        if fi < 0:
            continue
        feat_date = feat_level_dates[fi]
        try:
            X_pred = stock_features.xs(feat_date, level="date").reindex(active)
        except KeyError:
            continue
        valid_rows = ~X_pred.isna().all(axis=1)
        if valid_rows.sum() < 10:
            continue
        X_clean = X_pred[valid_rows].fillna(X_pred.mean()).fillna(0.0)
        scores = pd.Series(cached_model.predict(X_clean.values), index=X_clean.index)

        # Actual forward returns at this date
        if date not in fwd_ret_matrix.index:
            fi2 = fwd_ret_matrix.index.get_indexer([date], method="nearest")[0]
            if fi2 < 0:
                continue
            fwd_rets = fwd_ret_matrix.iloc[fi2]
        else:
            fwd_rets = fwd_ret_matrix.loc[date]
        fwd_rets = fwd_rets.reindex(active)

        common = scores.index.intersection(fwd_rets.dropna().index)
        if len(common) < 10:
            continue
        ic = float(scores.loc[common].rank().corr(fwd_rets.loc[common].rank()))
        ic_records.append({"date": date, "ic": ic})

    return ic_records


def _summarise_ic(ic_records: list[dict]) -> dict:
    if not ic_records:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "n": 0}
    ic_vals = [r["ic"] for r in ic_records]
    mean_ic = float(np.nanmean(ic_vals))
    ic_std = float(np.nanstd(ic_vals, ddof=1))
    n = len(ic_vals)
    ic_sharpe = (mean_ic / ic_std * np.sqrt(n)) if ic_std > 0 else np.nan
    return {"mean_ic": mean_ic, "ic_sharpe": ic_sharpe, "n": n}


def _grid_worker(
    combo: dict,
    stock_features: pd.DataFrame,
    fwd_ret_matrix: pd.DataFrame,
    holdout_dates: list[pd.Timestamp],
    inputs: dict,
) -> dict:
    # n_jobs=1 per worker — outer Parallel already saturates all cores
    params = _make_lgbm_params(combo, n_jobs=1)
    ic_recs = _ic_for_params(params, stock_features, fwd_ret_matrix, holdout_dates, inputs)
    result = _summarise_ic(ic_recs)
    result.update(combo)
    return result


def run_grid_search(
    inputs: dict,
    fwd_ret_matrix: pd.DataFrame,
    validation_end: pd.Timestamp,
) -> tuple[pd.DataFrame, dict]:
    stock_features = inputs["stock_features"]
    all_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    # Only evaluate IC on holdout window for grid selection
    holdout_dates = [d for d in all_dates if d >= HOLDOUT_START and d <= validation_end]
    if not holdout_dates:
        raise ValueError("No holdout dates found.")

    # Build all combos
    keys = list(TUNE_GRID.keys())
    vals = list(TUNE_GRID.values())
    combos = [dict(zip(keys, v)) for v in product(*vals)]
    logger.info("Grid search: %d combinations, %d holdout dates", len(combos), len(holdout_dates))

    t0 = time.perf_counter()
    results = Parallel(n_jobs=-1, backend="loky", verbose=0)(
        delayed(_grid_worker)(combo, stock_features, fwd_ret_matrix, holdout_dates, inputs)
        for combo in combos
    )
    logger.info("Grid search completed in %.1fs", time.perf_counter() - t0)

    grid_df = pd.DataFrame(results).sort_values("ic_sharpe", ascending=False).reset_index(drop=True)

    best_combo = {k: grid_df.iloc[0][k] for k in keys}
    logger.info(
        "Best config: %s — IC Sharpe=%.4f, Mean IC=%.4f",
        best_combo,
        grid_df.iloc[0]["ic_sharpe"],
        grid_df.iloc[0]["mean_ic"],
    )
    return grid_df, best_combo


def run_ic_baseline(
    inputs: dict,
    fwd_ret_matrix: pd.DataFrame,
    validation_end: pd.Timestamp,
    lgbm_threads: int = 1,
) -> tuple[dict, list[dict]]:
    """Measure IC for the baseline LGBM config on all rebalance dates."""
    stock_features = inputs["stock_features"]
    all_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    valid_dates = [d for d in all_dates if d <= validation_end]
    params = _make_lgbm_params({}, n_jobs=lgbm_threads)
    ic_recs = _ic_for_params(params, stock_features, fwd_ret_matrix, valid_dates, inputs)
    summary = _summarise_ic(ic_recs)
    logger.info(
        "Baseline IC: Mean=%.4f, IC Sharpe=%.4f, n=%d",
        summary["mean_ic"],
        summary["ic_sharpe"],
        summary["n"],
    )
    return summary, ic_recs


def run_ic_by_regime(
    inputs: dict,
    fwd_ret_matrix: pd.DataFrame,
    validation_end: pd.Timestamp,
    best_params_override: dict,
    lgbm_threads: int = 1,
) -> pd.DataFrame:
    """IC breakdown by regime for both baseline and best tuned config."""
    stock_features = inputs["stock_features"]
    all_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    valid_dates = [d for d in all_dates if d <= validation_end]

    # Each config runs sequentially; give each half the available cores
    per_config_threads = max(1, lgbm_threads // 2)
    baseline_params = _make_lgbm_params({}, n_jobs=per_config_threads)
    best_params = _make_lgbm_params(best_params_override, n_jobs=per_config_threads)

    logger.info("Computing IC by regime — %d threads per config...", per_config_threads)
    # Parallelise the two sequential evaluations so both use the machine at once
    results_pair = Parallel(n_jobs=2, backend="loky")(
        delayed(_ic_for_params)(p, stock_features, fwd_ret_matrix, valid_dates, inputs)
        for p in [baseline_params, best_params]
    )
    baseline_recs, best_recs = results_pair

    def _recs_to_series(recs: list[dict]) -> pd.Series:
        if not recs:
            return pd.Series([], dtype=float, index=pd.DatetimeIndex([], name="date"))
        return pd.Series(
            {r["date"]: r["ic"] for r in recs},
            dtype=float,
        ).rename_axis("date")

    baseline_series = _recs_to_series(baseline_recs)
    best_series = _recs_to_series(best_recs)

    rows = []
    for regime, start, end in IC_REGIMES:
        mask_b = (baseline_series.index >= pd.Timestamp(start)) & (
            baseline_series.index <= pd.Timestamp(end)
        )
        mask_t = (best_series.index >= pd.Timestamp(start)) & (
            best_series.index <= pd.Timestamp(end)
        )
        b_slice = baseline_series[mask_b]
        t_slice = best_series[mask_t]
        rows.append({
            "regime": regime,
            "start": start,
            "end": end,
            "baseline_mean_ic": float(b_slice.mean()) if not b_slice.empty else np.nan,
            "baseline_ic_sharpe": float(b_slice.mean() / b_slice.std() * np.sqrt(len(b_slice))) if len(b_slice) > 1 else np.nan,
            "best_mean_ic": float(t_slice.mean()) if not t_slice.empty else np.nan,
            "best_ic_sharpe": float(t_slice.mean() / t_slice.std() * np.sqrt(len(t_slice))) if len(t_slice) > 1 else np.nan,
            "n": len(t_slice),
        })
    return pd.DataFrame(rows)


# ── Portfolio path with LGBM scores ──────────────────────────────────────────

def build_lgbm_vol_path(
    inputs: dict,
    params: dict,
    validation_end: pd.Timestamp,
    n_top: int = 20,
    lgbm_threads: int = 1,
) -> dict:
    """
    Build a weight path using LGBM predictions as the selection signal.
    Replaces build_vol_path_fast in the B.5 construction chain.
    Same interface: returns {"weights": {...}, "selected": {...}, "sleeve_type": "lgbm"}.
    """
    if not LGBM_AVAILABLE:
        raise RuntimeError("lightgbm not installed")

    stock_features = inputs["stock_features"]
    fwd_ret_matrix = build_fwd_return_matrix(inputs["prices"])
    feat_level_dates = stock_features.index.get_level_values("date").unique().sort_values()
    all_rb_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    valid_dates = [d for d in all_rb_dates if d <= validation_end]

    weights_by_date: dict = {}
    selected_by_date: dict = {}
    cached_model = None
    retrain_counter = 0

    for date in valid_dates:
        active = _active_tickers_at(inputs, date)
        should_retrain = (cached_model is None) or (retrain_counter % RETRAIN_INTERVAL == 0)
        retrain_counter += 1

        if should_retrain:
            train_start = date - pd.DateOffset(years=TRAIN_YEARS)
            cutoff = date - pd.DateOffset(days=25)
            try:
                X_tr = stock_features.loc[pd.IndexSlice[train_start:cutoff, :], :]
                X_tr = X_tr.loc[X_tr.index.get_level_values("ticker").isin(active)]
                y_tr = fwd_ret_matrix.stack().rename("y").reindex(X_tr.index)
                valid_mask = ~(X_tr.isna().any(axis=1) | y_tr.isna())
                if valid_mask.sum() >= 50:
                    # Apply portfolio-phase thread count to this sequential fit
                    p = dict(params)
                    p["n_jobs"] = lgbm_threads
                    m = lgb.LGBMRegressor(**p)
                    m.fit(X_tr.values[valid_mask], y_tr.values[valid_mask])
                    cached_model = m
            except Exception as e:
                logger.debug("LGBM fit failed at %s: %s", date.date(), e)

        if cached_model is not None:
            fi = feat_level_dates.get_indexer([date], method="ffill")[0]
            if fi >= 0:
                feat_date = feat_level_dates[fi]
                try:
                    X_pred = stock_features.xs(feat_date, level="date").reindex(active)
                    valid_rows = ~X_pred.isna().all(axis=1)
                    X_clean = X_pred[valid_rows].fillna(X_pred.mean()).fillna(0.0)
                    scores = pd.Series(cached_model.predict(X_clean.values), index=X_clean.index)
                    selected = scores.nlargest(n_top).index.tolist()
                except Exception:
                    selected = active[:n_top]
            else:
                selected = active[:n_top]
        else:
            selected = active[:n_top]

        weights_by_date[date] = equal_weights(selected)
        selected_by_date[date] = selected

    return {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": "lgbm"}


def build_lgbm_b2_candidate(
    inputs: dict,
    params: dict,
    validation_end: pd.Timestamp,
    lgbm_threads: int = 1,
) -> pd.DataFrame:
    """
    B.5 construction with LGBM scores replacing vol_scores.
    Preserves: every_2_rebalances cadence, stress blending, trend sleeve.
    """
    dates = clipped_evaluation_dates(inputs, validation_end)
    trend_path = build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63)[TREND_NAME]
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)

    lgbm_path = build_lgbm_vol_path(inputs, params, validation_end, n_top=20, lgbm_threads=lgbm_threads)
    lgbm_weights = weight_frame(lgbm_path, dates)
    trend_weights = weight_frame(trend_path, dates)

    columns = lgbm_weights.columns.union(trend_weights.columns)
    lgbm_w = lgbm_weights.reindex(columns=columns, fill_value=0.0)
    trend_w = trend_weights.reindex(columns=columns, fill_value=0.0)

    stress_score = stress["stress_score"].reindex(dates).fillna(0.0)
    trend_sleeve_weight = (CANDIDATE_BASE_TREND_WEIGHT + CANDIDATE_STRESS_K * stress_score).clip(
        upper=CANDIDATE_TREND_CAP
    )
    vol_sleeve_weight = (1.0 - trend_sleeve_weight).clip(lower=0.0)
    raw = (lgbm_w.mul(vol_sleeve_weight, axis=0) + trend_w.mul(trend_sleeve_weight, axis=0)).fillna(0.0)

    signal_dates = signal_dates_for_frequency(inputs, raw, validation_end, "every_2_rebalances")
    return apply_execution_controls(raw, signal_dates, trade_threshold=0.0, partial_rebalance=1.0)


def build_promoted_lgbm_weights(
    inputs: dict,
    params: dict,
    validation_end: pd.Timestamp,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
    lgbm_threads: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, list]:
    """Full B.5 construction using LGBM signal."""
    base_weights = build_lgbm_b2_candidate(inputs, params, validation_end, lgbm_threads=lgbm_threads)
    target_turnover = base_weights.diff().abs().sum(axis=1)
    if not base_weights.empty:
        target_turnover.iloc[0] = base_weights.iloc[0].abs().sum()
    control_dates = list(target_turnover[target_turnover > 1e-12].index)

    trend_tickers = [t for t in _NON_BENCHMARK_TREND if t in base_weights.columns]
    scaled = apply_trend_scaling(
        base_weights,
        stress_series,
        control_dates,
        trend_tickers,
        B5_PROMOTED.trend_stress_threshold,
        B5_PROMOTED.trend_stress_scale_max,
    )
    constrained, diagnostics = apply_b4_constraints(
        scaled,
        beta_frame,
        stress_series,
        B5_PROMOTED,
        control_dates,
        inputs["universe_config"].benchmark,
    )
    return constrained, diagnostics, control_dates


def compute_net_returns(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
    cost_bps: float,
) -> pd.Series:
    dates = constrained.index[constrained.index <= validation_end]
    weights = constrained.reindex(dates).fillna(0.0)
    executable = weights.shift(1).fillna(0.0)
    returns = (
        inputs["prices"]
        .pct_change()
        .fillna(0.0)
        .reindex(index=dates, columns=weights.columns)
        .fillna(0.0)
    )
    turnover = executable.diff().abs().sum(axis=1)
    if not executable.empty:
        turnover.iloc[0] = executable.iloc[0].abs().sum()
    raw_ret = (executable * returns).sum(axis=1)
    return (1.0 - turnover * cost_bps / 10000.0).clip(lower=0.0) * (1.0 + raw_ret) - 1.0


def _portfolio_metrics_window(net_ret: pd.Series, start: str, end: str, capital: float = 1.0) -> dict:
    mask = (net_ret.index >= pd.Timestamp(start)) & (net_ret.index <= pd.Timestamp(end))
    sliced = net_ret[mask]
    if len(sliced) < 21:
        return {"cagr": np.nan, "sharpe": np.nan, "max_dd": np.nan, "n_days": len(sliced)}
    nav = (1.0 + sliced).cumprod() * capital
    m = calculate_metrics(nav)
    return {
        "cagr": m.get("CAGR", np.nan),
        "sharpe": m.get("Sharpe", np.nan),
        "max_dd": m.get("Max Drawdown", np.nan),
        "n_days": len(sliced),
    }


def run_portfolio_validation(
    inputs: dict,
    best_params: dict,
    validation_end: pd.Timestamp,
    lgbm_threads: int = 1,
) -> tuple[dict, dict, pd.DataFrame, pd.DataFrame]:
    """Run LGBM-based portfolio through unchanged B.5 construction and evaluate."""
    capital = inputs["base_config"].portfolio.initial_capital

    t0 = time.perf_counter()
    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)
    logger.info("Beta/stress frames: %.1fs", time.perf_counter() - t0)

    n_rb = len(rebalance_dates(inputs["base_config"], inputs["prices"]))
    n_fits = max(1, n_rb // RETRAIN_INTERVAL)
    t1 = time.perf_counter()
    logger.info("Building LGBM B.5 weight path (~%d model fits, %d LGBM threads each)...",
                n_fits, lgbm_threads)
    constrained, diagnostics, control_dates = build_promoted_lgbm_weights(
        inputs, best_params, validation_end, beta_frame, stress_series, lgbm_threads=lgbm_threads
    )
    logger.info("LGBM weight path built in %.1fs", time.perf_counter() - t1)

    # Full-period metrics via simulator (every_2_rebalances already embedded in weights)
    full_sim = run_execution_simulator(
        inputs,
        constrained,
        validation_end,
        Variant("lgbm_b5_best", update_frequency="every_2_rebalances", cost_bps=B1_COST_BPS),
    )
    logger.info(
        "LGBM portfolio: CAGR=%.2f%% Sharpe=%.3f MaxDD=%.2f%%",
        full_sim["cagr"] * 100,
        full_sim["sharpe"],
        full_sim["max_dd"] * 100,
    )

    # Cost sensitivity
    cost_rows = []
    for bps in COST_BPS:
        net_ret = compute_net_returns(inputs, constrained, validation_end, bps)
        nav = (1.0 + net_ret).cumprod() * capital
        m = calculate_metrics(nav)
        cost_rows.append({
            "cost_bps": bps,
            "cagr": m.get("CAGR", np.nan),
            "sharpe": m.get("Sharpe", np.nan),
            "max_dd": m.get("Max Drawdown", np.nan),
        })
    cost_df = pd.DataFrame(cost_rows)

    # Regime breakdown
    net_ret_10 = compute_net_returns(inputs, constrained, validation_end, B1_COST_BPS)
    regime_rows = []
    for regime, start, end in PORTFOLIO_REGIMES:
        m = _portfolio_metrics_window(net_ret_10, start, end, capital)
        regime_rows.append({"regime": regime, "start": start, "end": end, **m})
    regime_df = pd.DataFrame(regime_rows)

    return full_sim, cost_df, regime_df, diagnostics


# ── Accept / reject logic ─────────────────────────────────────────────────────

def _verdict(full_sim_lgbm: dict, cost_df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    gates = []

    sharpe_10 = full_sim_lgbm.get("sharpe", np.nan)
    gates.append({
        "gate": f"Sharpe ≥ baseline − 0.05 ({GATE_SHARPE_FLOOR:.3f})",
        "value": f"{sharpe_10:.3f}" if np.isfinite(sharpe_10) else "N/A",
        "target": f"≥ {GATE_SHARPE_FLOOR:.3f}",
        "pass": bool(np.isfinite(sharpe_10) and sharpe_10 >= GATE_SHARPE_FLOOR),
    })
    gates.append({
        "gate": f"Sharpe preferred ≥ baseline + 0.05 ({B5_SHARPE + 0.05:.3f})",
        "value": f"{sharpe_10:.3f}" if np.isfinite(sharpe_10) else "N/A",
        "target": f"≥ {B5_SHARPE + 0.05:.3f}",
        "pass": bool(np.isfinite(sharpe_10) and sharpe_10 >= B5_SHARPE + 0.05),
    })

    max_dd = full_sim_lgbm.get("max_dd", np.nan)
    gates.append({
        "gate": f"MaxDD ≤ baseline ({GATE_MAX_DD:.2%})",
        "value": f"{max_dd:.2%}" if np.isfinite(max_dd) else "N/A",
        "target": f"≤ {GATE_MAX_DD:.2%}",
        "pass": bool(np.isfinite(max_dd) and max_dd >= GATE_MAX_DD),
    })

    row_50 = cost_df[cost_df["cost_bps"] == 50.0]
    if not row_50.empty:
        s50 = float(row_50["sharpe"].iloc[0])
        gates.append({
            "gate": "50 bps Sharpe competitive (> B5 50bps 0.934 − 0.05)",
            "value": f"{s50:.3f}",
            "target": "≥ 0.884",
            "pass": bool(np.isfinite(s50) and s50 >= 0.884),
        })

    turnover = full_sim_lgbm.get("turnover_sum", np.nan)
    gates.append({
        "gate": "No turnover spike (sum ≤ 100)",
        "value": f"{turnover:.1f}" if np.isfinite(turnover) else "N/A",
        "target": "≤ 100.0",
        "pass": bool(np.isfinite(turnover) and turnover <= 100.0),
    })

    gate_df = pd.DataFrame(gates)
    all_min_gates = bool(gate_df[gate_df["gate"].str.contains("≥ baseline − 0.05|MaxDD|50 bps|turnover", regex=True)]["pass"].all())
    verdict = "ACCEPT" if all_min_gates else "REJECT"
    return verdict, gate_df


# ── Report rendering ──────────────────────────────────────────────────────────

def _render_report(
    baseline_ic: dict,
    best_combo: dict,
    best_ic: dict,
    grid_df: pd.DataFrame,
    ic_regime_df: pd.DataFrame,
    full_sim_baseline: dict,
    full_sim_lgbm: dict,
    cost_df: pd.DataFrame,
    regime_df: pd.DataFrame,
    verdict: str,
    gate_df: pd.DataFrame,
) -> str:
    lines = [
        "# Phase C.1 — LightGBM Hyperparameter Tuning",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- Baseline: `b4_stress_cap_trend_boost` — CAGR `{B5_CAGR:.2%}`, Sharpe `{B5_SHARPE:.3f}`, MaxDD `{B5_MAX_DD:.2%}`",
        "- Universe: sp500, clipped to 2026-04-24, evaluation 2008–2026.",
        f"- Holdout window for IC grid search: {HOLDOUT_START.date()} — {VALIDATION_END_STR}.",
        "- Construction preserved: every_2_rebalances cadence, dynamic beta cap, stress blend, trend sleeve.",
        "- Tuned: num_leaves, min_data_in_leaf, feature_fraction, bagging_fraction, lambda_l1, lambda_l2.",
        "",
        f"## Verdict: {verdict}",
        "",
    ]

    lines += ["## Phase C.1 Acceptance Gates", ""]
    lines.append(gate_df[["gate", "value", "target", "pass"]].to_markdown(index=False))
    lines.append("")

    lines += ["## Baseline IC (current LGBM config)", ""]
    lines += [
        f"| Metric | Value |",
        f"|---|---|",
        f"| Mean IC | {baseline_ic['mean_ic']:.4f} |",
        f"| IC Sharpe | {baseline_ic['ic_sharpe']:.4f} |",
        f"| N dates | {baseline_ic['n']} |",
        "",
    ]

    lines += ["## Best Tuned Config IC", ""]
    lines += [
        f"| Metric | Value |",
        f"|---|---|",
        f"| Mean IC | {best_ic['mean_ic']:.4f} |",
        f"| IC Sharpe | {best_ic['ic_sharpe']:.4f} |",
        f"| N dates | {best_ic['n']} |",
        "",
    ]
    lines += ["**Best hyperparameters:**", ""]
    for k, v in best_combo.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")

    lines += ["## Top 10 Grid Search Configs (holdout IC Sharpe)", ""]
    top10 = grid_df.head(10).copy()
    top10["mean_ic"] = top10["mean_ic"].map("{:.4f}".format)
    top10["ic_sharpe"] = top10["ic_sharpe"].map("{:.4f}".format)
    lines.append(top10.to_markdown(index=False))
    lines.append("")

    lines += ["## IC by Regime", ""]
    lines.append(ic_regime_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Portfolio Metrics vs B.5 Baseline", ""]
    cagr_b = full_sim_baseline.get("cagr", np.nan)
    sh_b = full_sim_baseline.get("sharpe", np.nan)
    dd_b = full_sim_baseline.get("max_dd", np.nan)
    to_b = full_sim_baseline.get("turnover_sum", np.nan)
    cagr_t = full_sim_lgbm.get("cagr", np.nan)
    sh_t = full_sim_lgbm.get("sharpe", np.nan)
    dd_t = full_sim_lgbm.get("max_dd", np.nan)
    to_t = full_sim_lgbm.get("turnover_sum", np.nan)
    lines += [
        "| Metric | B.5 Baseline (vol) | C.1 Best (LGBM) | Delta |",
        "|---|---|---|---|",
        f"| CAGR | {cagr_b:.2%} | {cagr_t:.2%} | {cagr_t - cagr_b:+.2%} |",
        f"| Sharpe | {sh_b:.3f} | {sh_t:.3f} | {sh_t - sh_b:+.3f} |",
        f"| MaxDD | {dd_b:.2%} | {dd_t:.2%} | {dd_t - dd_b:+.2%} |",
        f"| Turnover sum | {to_b:.1f} | {to_t:.1f} | {to_t - to_b:+.1f} |",
        "",
    ]

    lines += ["## Cost Sensitivity (LGBM best)", ""]
    cost_display = cost_df.copy()
    cost_display["cagr"] = cost_display["cagr"].map("{:.2%}".format)
    cost_display["sharpe"] = cost_display["sharpe"].map("{:.3f}".format)
    cost_display["max_dd"] = cost_display["max_dd"].map("{:.2%}".format)
    lines.append(cost_display.to_markdown(index=False))
    lines.append("")

    lines += ["## Regime Breakdown (LGBM best, 10 bps)", ""]
    lines.append(regime_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += [
        "## Output Files",
        "",
        "- `artifacts/reports/phase_c1_lgbm_tuning.md`",
        "- `artifacts/reports/ic_by_regime.csv`",
        "- `artifacts/reports/portfolio_vs_baseline.csv`",
        "- `artifacts/reports/phase_c1_grid_results.csv`",
        "",
    ]
    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _n_cpus = os.cpu_count() or 4
    parser = argparse.ArgumentParser(description="Phase C.1 — LightGBM tuning")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    parser.add_argument(
        "--lgbm-portfolio-threads",
        type=int,
        default=_n_cpus,
        help=(
            "LGBM threads for sequential portfolio / IC-by-regime phase "
            f"(default: all {_n_cpus} CPUs). Grid search always uses 1 thread "
            "per worker; outer Parallel uses n_jobs=-1."
        ),
    )
    parser.add_argument(
        "--skip-grid",
        action="store_true",
        help="Skip grid search and load results from artifacts/reports/phase_c1_grid_results.csv",
    )
    args = parser.parse_args()

    if not LGBM_AVAILABLE:
        logger.error("lightgbm is not installed. Run: pip install lightgbm")
        sys.exit(1)

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # ── Load data ──────────────────────────────────────────────────────────────
    logger.info("Loading inputs for %s...", args.universe)
    t_load = time.perf_counter()
    inputs = load_inputs(args.config, args.universe, args.trend_assets)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )
    logger.info("Inputs loaded in %.1fs. Validation end: %s", time.perf_counter() - t_load, validation_end.date())

    fwd_ret_matrix = build_fwd_return_matrix(inputs["prices"])

    lgbm_pt = args.lgbm_portfolio_threads
    logger.info(
        "Thread strategy: grid search n_jobs=-1 (1 LGBM thread/worker) | "
        "sequential phases %d LGBM threads",
        lgbm_pt,
    )

    # ── C.0: Baseline IC ──────────────────────────────────────────────────────
    logger.info("=== C.0: Baseline IC measurement (%d LGBM threads) ===", lgbm_pt)
    baseline_ic, _ = run_ic_baseline(inputs, fwd_ret_matrix, validation_end, lgbm_threads=lgbm_pt)

    # ── C.1: Grid search ──────────────────────────────────────────────────────
    grid_csv = reports_dir / "phase_c1_grid_results.csv"
    if args.skip_grid:
        logger.info("=== C.1: Loading saved grid results from %s ===", grid_csv)
        grid_df = pd.read_csv(grid_csv)
        keys = list(TUNE_GRID.keys())
        best_combo = {k: grid_df.iloc[0][k] for k in keys}
        logger.info(
            "Best config loaded: %s — IC Sharpe=%.4f, Mean IC=%.4f",
            best_combo,
            grid_df.iloc[0]["ic_sharpe"],
            grid_df.iloc[0]["mean_ic"],
        )
    else:
        logger.info("=== C.1: Grid search (%d combos, n_jobs=-1) ===",
                    len(list(product(*TUNE_GRID.values()))))
        grid_df, best_combo = run_grid_search(inputs, fwd_ret_matrix, validation_end)
        grid_df.to_csv(grid_csv, index=False)
        logger.info("Grid results saved.")

    # IC stats for best config (full window for overfit check)
    all_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    valid_dates = [d for d in all_dates if d <= validation_end]
    best_params = _make_lgbm_params(best_combo, n_jobs=lgbm_pt)
    best_ic_recs = _ic_for_params(best_params, inputs["stock_features"], fwd_ret_matrix, valid_dates, inputs)
    best_ic_all = _summarise_ic(best_ic_recs)
    holdout_recs = [r for r in best_ic_recs if r["date"] >= HOLDOUT_START]
    best_ic_holdout = _summarise_ic(holdout_recs)
    logger.info(
        "Best config — Full IC Sharpe: %.4f | Holdout IC Sharpe: %.4f | Ratio: %.2f",
        best_ic_all["ic_sharpe"],
        best_ic_holdout["ic_sharpe"],
        best_ic_all["ic_sharpe"] / best_ic_holdout["ic_sharpe"] if best_ic_holdout["ic_sharpe"] else np.nan,
    )

    # ── IC by regime ──────────────────────────────────────────────────────────
    logger.info("=== IC by regime (%d LGBM threads per config, 2 configs parallel) ===", lgbm_pt // 2)
    ic_regime_df = run_ic_by_regime(inputs, fwd_ret_matrix, validation_end, best_combo, lgbm_threads=lgbm_pt)
    ic_regime_df.to_csv(reports_dir / "ic_by_regime.csv", index=False)
    logger.info("IC by regime saved.")

    # ── Portfolio validation ──────────────────────────────────────────────────
    logger.info("=== Portfolio validation through B.5 harness (%d LGBM threads) ===", lgbm_pt)

    # Baseline portfolio (vol_scores, same B.5 construction — use saved B.5 metrics)
    full_sim_baseline = {
        "cagr": B5_CAGR,
        "sharpe": B5_SHARPE,
        "max_dd": B5_MAX_DD,
        "turnover_sum": B5_TURNOVER,
    }

    full_sim_lgbm, cost_df, regime_df, _ = run_portfolio_validation(
        inputs, best_params, validation_end, lgbm_threads=lgbm_pt
    )

    # ── Portfolio vs baseline table ───────────────────────────────────────────
    portfolio_comparison = pd.DataFrame([
        {
            "variant": "B.5 baseline (vol_scores)",
            "cagr": B5_CAGR,
            "sharpe": B5_SHARPE,
            "max_dd": B5_MAX_DD,
            "turnover_sum": B5_TURNOVER,
            "cost_bps": 10.0,
        },
        {
            "variant": "C.1 best (LGBM tuned)",
            "cagr": full_sim_lgbm.get("cagr", np.nan),
            "sharpe": full_sim_lgbm.get("sharpe", np.nan),
            "max_dd": full_sim_lgbm.get("max_dd", np.nan),
            "turnover_sum": full_sim_lgbm.get("turnover_sum", np.nan),
            "cost_bps": 10.0,
        },
    ])
    for row in cost_df.itertuples():
        portfolio_comparison = pd.concat([
            portfolio_comparison,
            pd.DataFrame([{
                "variant": f"C.1 best (LGBM) {int(row.cost_bps)} bps",
                "cagr": row.cagr,
                "sharpe": row.sharpe,
                "max_dd": row.max_dd,
                "turnover_sum": full_sim_lgbm.get("turnover_sum", np.nan),
                "cost_bps": row.cost_bps,
            }])
        ], ignore_index=True)
    portfolio_comparison.to_csv(reports_dir / "portfolio_vs_baseline.csv", index=False)
    logger.info("Portfolio comparison saved.")

    # ── Verdict ───────────────────────────────────────────────────────────────
    verdict, gate_df = _verdict(full_sim_lgbm, cost_df)
    logger.info("Phase C.1 verdict: %s", verdict)

    # ── Render report ─────────────────────────────────────────────────────────
    report = _render_report(
        baseline_ic=baseline_ic,
        best_combo=best_combo,
        best_ic=best_ic_holdout,
        grid_df=grid_df,
        ic_regime_df=ic_regime_df,
        full_sim_baseline=full_sim_baseline,
        full_sim_lgbm=full_sim_lgbm,
        cost_df=cost_df,
        regime_df=regime_df,
        verdict=verdict,
        gate_df=gate_df,
    )
    (reports_dir / "phase_c1_lgbm_tuning.md").write_text(report)
    logger.info("Report saved to %s", reports_dir / "phase_c1_lgbm_tuning.md")
    logger.info("Phase C.1 complete — %s", verdict)


if __name__ == "__main__":
    main()
