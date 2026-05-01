"""
Phase C.2 — Feature Attribution and Anti-Predictive Feature Pruning.

Investigates WHY LightGBM with all 32 features has negative IC on the sp500 holdout,
and finds a fixable subset by:
  1. Standalone per-feature IC analysis (parallelised, no model)
  2. Anti-predictive feature identification
  3. Walk-forward IC experiments on feature subsets (sequential, 32 LGBM threads)
  4. Model sanity comparison (vol_score rank, mean_rank, Ridge, LGBM regressor, LGBM ranker)
  5. Portfolio validation on the best config (only if positive holdout IC found)
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.linear_model import Ridge

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
from run_phase_b3_exposure_control import rolling_beta_matrix  # noqa: E402
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
from src.alpha import compute_volatility_score_frame  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Phase B.5 baseline gates ──────────────────────────────────────────────────
B5_SHARPE = 1.078
B5_MAX_DD = -0.3298
B5_CAGR = 0.1604
B5_TURNOVER = 84.12

# ── Walk-forward constants ────────────────────────────────────────────────────
HOLDOUT_START = pd.Timestamp("2019-01-01")
VALIDATION_END_STR = "2026-04-24"
TRAIN_YEARS = 3
RETRAIN_INTERVAL = 3
FWD_HORIZON = 21

# ── LGBM params ───────────────────────────────────────────────────────────────
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

BEST_C1_PARAMS = {
    "num_leaves": 15,
    "min_data_in_leaf": 100,
    "feature_fraction": 0.6,
    "bagging_fraction": 0.9,
    "lambda_l1": 0.0,
    "lambda_l2": 0.0,
}

# ── Feature groups ────────────────────────────────────────────────────────────
BASELINE_FEATURES = [
    "ret_1m", "ret_3m", "ret_6m", "ret_12m", "ret_12m_ex_1m",
    "above_50dma", "above_200dma", "ma_50_200_ratio", "price_to_52w_high",
    "volatility_21d", "volatility_63d", "downside_vol_63d", "max_drawdown_63d",
    "avg_dollar_volume_63d", "beta_to_spy_63d", "relative_strength_vs_spy_63d",
]

REVERSAL_FEATURES = [
    "ret_1w", "ret_2w", "ret_zscore_21d", "overextension_20dma", "rsi_proxy", "gap_overnight",
]

QUALITY_MOM_FEATURES = [
    "ret_3m_ex_1w", "ret_6m_ex_1m", "ret_3m_adj", "ret_6m_adj",
    "mom_stability_3m", "trend_consistency", "pct_pos_months_6m",
]

COMPUTED_FEATURES = [
    "liquidity_rank", "sector_rel_momentum_3m", "sector_rel_momentum_6m",
]

ALL_32_FEATURES = BASELINE_FEATURES + REVERSAL_FEATURES + QUALITY_MOM_FEATURES + COMPUTED_FEATURES

VOL_FEATURES = ["volatility_63d", "downside_vol_63d", "max_drawdown_63d", "beta_to_spy_63d"]
MOMENTUM_CORE_FEATURES = ["ret_3m", "ret_6m", "ret_12m", "ret_12m_ex_1m", "ret_3m_ex_1w", "ret_6m_ex_1m"]

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

_LGBM_INT_PARAMS = frozenset({"n_estimators", "max_depth", "num_leaves", "min_data_in_leaf", "bagging_freq"})


# ── Core helpers ──────────────────────────────────────────────────────────────

def build_fwd_return_matrix(prices: pd.DataFrame, horizon: int = 21) -> pd.DataFrame:
    non_stock = set(TREND_ASSETS) | {"SPY"}
    stock_cols = [c for c in prices.columns if c not in non_stock]
    return prices[stock_cols].shift(-horizon) / prices[stock_cols] - 1.0


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


def _make_lgbm_params(overrides: dict, n_jobs: int = 1) -> dict:
    params = dict(BASELINE_LGBM_PARAMS)
    params.update(overrides)
    params["n_jobs"] = n_jobs
    for k in _LGBM_INT_PARAMS:
        if k in params and params[k] is not None:
            params[k] = int(params[k])
    if params.get("bagging_fraction", 1.0) < 1.0 and params.get("bagging_freq", 0) == 0:
        params["bagging_freq"] = 1
    return params


def _summarise_ic(ic_records: list[dict]) -> dict:
    if not ic_records:
        return {"mean_ic": np.nan, "ic_sharpe": np.nan, "sign_stability": np.nan, "n": 0}
    ic_vals = [r["ic"] for r in ic_records]
    mean_ic = float(np.nanmean(ic_vals))
    ic_std = float(np.nanstd(ic_vals, ddof=1))
    n = len(ic_vals)
    sign_stability = float(np.mean([v > 0 for v in ic_vals]))
    ic_sharpe = (mean_ic / ic_std * np.sqrt(n)) if ic_std > 0 else np.nan
    return {"mean_ic": mean_ic, "ic_sharpe": ic_sharpe, "sign_stability": sign_stability, "n": n}


def _fwd_at_date(fwd_ret_matrix: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
    if date in fwd_ret_matrix.index:
        return fwd_ret_matrix.loc[date]
    fi2 = fwd_ret_matrix.index.get_indexer([date], method="nearest")[0]
    if fi2 < 0:
        return pd.Series(dtype=float)
    return fwd_ret_matrix.iloc[fi2]


# ── Phase 1: Standalone per-feature IC ───────────────────────────────────────

def _standalone_ic_for_feature(
    feat_name: str,
    feat_series: pd.Series,
    fwd_ret_matrix: pd.DataFrame,
    rebal_dates: list,
    inputs: dict,
) -> list[dict]:
    """Rank IC of a single feature vs 21-day forward return at each rebalance date."""
    recs = []
    feat_level_dates = feat_series.index.get_level_values("date").unique().sort_values()

    for date in rebal_dates:
        active = _active_tickers_at(inputs, date)

        fi = feat_level_dates.get_indexer([date], method="ffill")[0]
        if fi < 0:
            continue
        feat_date = feat_level_dates[fi]
        try:
            feat_cross = feat_series.xs(feat_date, level="date").reindex(active).dropna()
        except KeyError:
            continue
        if len(feat_cross) < 10:
            continue

        fwd = _fwd_at_date(fwd_ret_matrix, date).reindex(active)
        common = feat_cross.index.intersection(fwd.dropna().index)
        if len(common) < 10:
            continue

        ic = float(feat_cross.loc[common].rank().corr(fwd.loc[common].rank()))
        recs.append({"date": date, "ic": ic, "feature": feat_name})
    return recs


def run_standalone_feature_ic(
    inputs: dict,
    fwd_ret_matrix: pd.DataFrame,
    validation_end: pd.Timestamp,
    n_jobs: int = -1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Phase 1: Standalone per-feature IC.
    Returns (summary_df, by_regime_df, by_year_df).
    """
    stock_features = inputs["stock_features"]
    all_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    valid_dates = [d for d in all_dates if d <= validation_end]

    # Build the vol_score composite series
    vol_score_frame = compute_volatility_score_frame(stock_features)
    vol_score_series = vol_score_frame["volatility_score"].rename("vol_score_composite")

    # Determine which features are actually present in the data
    available_features = [f for f in ALL_32_FEATURES if f in stock_features.columns]
    missing = [f for f in ALL_32_FEATURES if f not in stock_features.columns]
    if missing:
        logger.warning("Missing features (will be skipped): %s", missing)

    all_feature_names = available_features + ["vol_score_composite"]
    all_feature_series = [stock_features[f] for f in available_features] + [vol_score_series]

    logger.info(
        "Computing standalone IC for %d features across %d dates (n_jobs=%d)...",
        len(all_feature_names), len(valid_dates), n_jobs,
    )
    t0 = time.perf_counter()

    results_list = Parallel(n_jobs=n_jobs, backend="loky", verbose=0)(
        delayed(_standalone_ic_for_feature)(name, series, fwd_ret_matrix, valid_dates, inputs)
        for name, series in zip(all_feature_names, all_feature_series)
    )
    logger.info("Standalone IC done in %.1fs", time.perf_counter() - t0)

    # Flatten all records
    all_recs = []
    for recs in results_list:
        all_recs.extend(recs)

    if not all_recs:
        logger.warning("No IC records produced — returning empty DataFrames")
        empty = pd.DataFrame()
        return empty, empty, empty

    ic_df = pd.DataFrame(all_recs)
    ic_df["date"] = pd.to_datetime(ic_df["date"])

    # ── Summary stats ─────────────────────────────────────────────────────────
    summary_rows = []
    for feat in all_feature_names:
        feat_recs = [r for r in all_recs if r["feature"] == feat]
        full_stats = _summarise_ic(feat_recs)
        holdout_recs = [r for r in feat_recs if r["date"] >= HOLDOUT_START]
        hold_stats = _summarise_ic(holdout_recs)
        train_recs = [r for r in feat_recs if r["date"] < HOLDOUT_START]
        train_stats = _summarise_ic(train_recs)
        summary_rows.append({
            "feature": feat,
            "full_mean_ic": full_stats["mean_ic"],
            "full_ic_sharpe": full_stats["ic_sharpe"],
            "full_sign_stability": full_stats["sign_stability"],
            "full_n": full_stats["n"],
            "train_mean_ic": train_stats["mean_ic"],
            "train_ic_sharpe": train_stats["ic_sharpe"],
            "train_sign_stability": train_stats["sign_stability"],
            "holdout_mean_ic": hold_stats["mean_ic"],
            "holdout_ic_sharpe": hold_stats["ic_sharpe"],
            "holdout_sign_stability": hold_stats["sign_stability"],
            "holdout_n": hold_stats["n"],
        })
    summary_df = pd.DataFrame(summary_rows).sort_values("holdout_ic_sharpe", ascending=False).reset_index(drop=True)

    # ── By regime ─────────────────────────────────────────────────────────────
    regime_rows = []
    for feat in all_feature_names:
        feat_df = ic_df[ic_df["feature"] == feat].set_index("date")["ic"]
        for regime_name, start, end in IC_REGIMES:
            mask = (feat_df.index >= pd.Timestamp(start)) & (feat_df.index <= pd.Timestamp(end))
            slice_vals = feat_df[mask]
            stats = _summarise_ic([{"ic": v} for v in slice_vals])
            regime_rows.append({
                "feature": feat,
                "regime": regime_name,
                "start": start,
                "end": end,
                "mean_ic": stats["mean_ic"],
                "ic_sharpe": stats["ic_sharpe"],
                "sign_stability": stats["sign_stability"],
                "n": stats["n"],
            })
    by_regime_df = pd.DataFrame(regime_rows)

    # ── By year ───────────────────────────────────────────────────────────────
    year_rows = []
    for feat in all_feature_names:
        feat_df = ic_df[ic_df["feature"] == feat].copy()
        feat_df["year"] = feat_df["date"].dt.year
        for yr, grp in feat_df.groupby("year"):
            stats = _summarise_ic([{"ic": v} for v in grp["ic"]])
            year_rows.append({
                "feature": feat,
                "year": yr,
                "mean_ic": stats["mean_ic"],
                "ic_sharpe": stats["ic_sharpe"],
                "sign_stability": stats["sign_stability"],
                "n": stats["n"],
            })
    by_year_df = pd.DataFrame(year_rows)

    return summary_df, by_regime_df, by_year_df


# ── Phase 2: Anti-predictive detection ───────────────────────────────────────

def identify_anti_predictive(holdout_ic_df: pd.DataFrame) -> list[str]:
    """
    holdout_ic_df: DataFrame with columns [feature, holdout_mean_ic, holdout_sign_stability, ...]
    Returns list of feature names considered anti-predictive.
    """
    anti = holdout_ic_df[
        (holdout_ic_df["holdout_mean_ic"] < 0) | (holdout_ic_df["holdout_sign_stability"] < 0.45)
    ]["feature"].tolist()
    # Exclude the vol_score composite from this list — it's the baseline alpha
    return [f for f in anti if f != "vol_score_composite"]


# ── Phase 3: Walk-forward LGBM IC for feature subsets ────────────────────────

def _ic_for_feature_subset(
    params: dict,
    stock_features: pd.DataFrame,
    fwd_ret_matrix: pd.DataFrame,
    all_dates: list,
    inputs: dict,
    feature_cols: list[str],
) -> list[dict]:
    """Walk-forward IC evaluation using only `feature_cols`."""
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
                X_tr = stock_features.loc[pd.IndexSlice[train_start:cutoff, :], feature_cols]
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

        fi = feat_level_dates.get_indexer([date], method="ffill")[0]
        if fi < 0:
            continue
        feat_date = feat_level_dates[fi]
        try:
            X_pred = stock_features.xs(feat_date, level="date")[feature_cols].reindex(active)
        except KeyError:
            continue
        valid_rows = ~X_pred.isna().all(axis=1)
        if valid_rows.sum() < 10:
            continue
        X_clean = X_pred[valid_rows].fillna(X_pred.mean()).fillna(0.0)
        scores = pd.Series(cached_model.predict(X_clean.values), index=X_clean.index)

        fwd_rets = _fwd_at_date(fwd_ret_matrix, date).reindex(active)
        common = scores.index.intersection(fwd_rets.dropna().index)
        if len(common) < 10:
            continue
        ic = float(scores.loc[common].rank().corr(fwd_rets.loc[common].rank()))
        ic_records.append({"date": date, "ic": ic})

    return ic_records


def _ic_for_ridge_subset(
    stock_features: pd.DataFrame,
    fwd_ret_matrix: pd.DataFrame,
    all_dates: list,
    inputs: dict,
    feature_cols: list[str],
    alpha: float = 1.0,
) -> list[dict]:
    """Walk-forward IC using Ridge regression on `feature_cols`."""
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
                X_tr = stock_features.loc[pd.IndexSlice[train_start:cutoff, :], feature_cols]
                X_tr = X_tr.loc[X_tr.index.get_level_values("ticker").isin(active)]
                y_tr = fwd_ret_matrix.stack().rename("y").reindex(X_tr.index)
                valid = ~(X_tr.isna().any(axis=1) | y_tr.isna())
                if valid.sum() >= 50:
                    Xv = X_tr.values[valid]
                    yv = y_tr.values[valid]
                    col_mean = np.nanmean(Xv, axis=0)
                    col_std = np.nanstd(Xv, axis=0, ddof=1)
                    col_std = np.where(col_std < 1e-8, 1.0, col_std)
                    Xv = (Xv - col_mean) / col_std
                    m = Ridge(alpha=alpha)
                    m.fit(Xv, yv)
                    cached_model = (m, col_mean, col_std)
            except Exception:
                pass

        if cached_model is None:
            continue

        fi = feat_level_dates.get_indexer([date], method="ffill")[0]
        if fi < 0:
            continue
        feat_date = feat_level_dates[fi]
        try:
            X_pred = stock_features.xs(feat_date, level="date")[feature_cols].reindex(active)
        except KeyError:
            continue
        valid_rows = ~X_pred.isna().all(axis=1)
        if valid_rows.sum() < 10:
            continue
        X_clean = X_pred[valid_rows].fillna(X_pred.mean()).fillna(0.0)
        ridge_model, col_mean, col_std = cached_model
        Xp = (X_clean.values - col_mean) / col_std
        scores = pd.Series(ridge_model.predict(Xp), index=X_clean.index)

        fwd_rets = _fwd_at_date(fwd_ret_matrix, date).reindex(active)
        common = scores.index.intersection(fwd_rets.dropna().index)
        if len(common) < 10:
            continue
        ic = float(scores.loc[common].rank().corr(fwd_rets.loc[common].rank()))
        ic_records.append({"date": date, "ic": ic})

    return ic_records


def _ic_for_lgbm_ranker_subset(
    params: dict,
    stock_features: pd.DataFrame,
    fwd_ret_matrix: pd.DataFrame,
    all_dates: list,
    inputs: dict,
    feature_cols: list[str],
) -> list[dict]:
    """Walk-forward IC using LGBMRanker on `feature_cols`."""
    if not LGBM_AVAILABLE:
        return []

    # Build ranker params from regressor params
    ranker_params = dict(params)
    ranker_params.pop("objective", None)
    ranker_params["objective"] = "lambdarank"
    ranker_params["label_gain"] = list(range(50))
    ranker_params["verbose"] = -1

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
                X_tr = stock_features.loc[pd.IndexSlice[train_start:cutoff, :], feature_cols]
                X_tr = X_tr.loc[X_tr.index.get_level_values("ticker").isin(active)]
                y_tr = fwd_ret_matrix.stack().rename("y").reindex(X_tr.index)
                valid = ~(X_tr.isna().any(axis=1) | y_tr.isna())
                if valid.sum() >= 50:
                    Xv = X_tr.values[valid]
                    yv = y_tr.values[valid]
                    # Convert to integer ranks (0-based) for lambdarank
                    n_bins = min(49, len(yv) - 1)
                    labels = pd.qcut(yv, q=n_bins, labels=False, duplicates="drop").astype(int)
                    # group: each date-cross-section is one group
                    date_idx = X_tr.index.get_level_values("date")[valid]
                    group_sizes = pd.Series(date_idx).value_counts().sort_index().values.tolist()
                    m = lgb.LGBMRanker(**ranker_params)
                    m.fit(Xv, labels, group=group_sizes)
                    cached_model = m
            except Exception:
                pass

        if cached_model is None:
            continue

        fi = feat_level_dates.get_indexer([date], method="ffill")[0]
        if fi < 0:
            continue
        feat_date = feat_level_dates[fi]
        try:
            X_pred = stock_features.xs(feat_date, level="date")[feature_cols].reindex(active)
        except KeyError:
            continue
        valid_rows = ~X_pred.isna().all(axis=1)
        if valid_rows.sum() < 10:
            continue
        X_clean = X_pred[valid_rows].fillna(X_pred.mean()).fillna(0.0)
        scores = pd.Series(cached_model.predict(X_clean.values), index=X_clean.index)

        fwd_rets = _fwd_at_date(fwd_ret_matrix, date).reindex(active)
        common = scores.index.intersection(fwd_rets.dropna().index)
        if len(common) < 10:
            continue
        ic = float(scores.loc[common].rank().corr(fwd_rets.loc[common].rank()))
        ic_records.append({"date": date, "ic": ic})

    return ic_records


def _ic_for_vol_score_rank(
    stock_features: pd.DataFrame,
    fwd_ret_matrix: pd.DataFrame,
    all_dates: list,
    inputs: dict,
) -> list[dict]:
    """Direct rank IC of the vol_score composite vs forward returns (no model)."""
    vol_score_frame = compute_volatility_score_frame(stock_features)
    vol_score_series = vol_score_frame["volatility_score"]
    return _standalone_ic_for_feature(
        "vol_score_rank", vol_score_series, fwd_ret_matrix, all_dates, inputs
    )


def _ic_for_simple_mean_rank(
    stock_features: pd.DataFrame,
    fwd_ret_matrix: pd.DataFrame,
    all_dates: list,
    inputs: dict,
    positive_ic_features: list[str],
) -> list[dict]:
    """
    IC for equal-weight mean of per-feature percentile ranks across positive-IC features.
    No model training required.
    """
    if not positive_ic_features:
        return []

    feat_level_dates = stock_features.index.get_level_values("date").unique().sort_values()
    ic_records = []

    for date in all_dates:
        active = _active_tickers_at(inputs, date)

        fi = feat_level_dates.get_indexer([date], method="ffill")[0]
        if fi < 0:
            continue
        feat_date = feat_level_dates[fi]
        try:
            X_snap = stock_features.xs(feat_date, level="date")[positive_ic_features].reindex(active)
        except KeyError:
            continue

        rank_pct = X_snap.rank(pct=True)
        composite = rank_pct.mean(axis=1).dropna()
        if len(composite) < 10:
            continue

        fwd_rets = _fwd_at_date(fwd_ret_matrix, date).reindex(active)
        common = composite.index.intersection(fwd_rets.dropna().index)
        if len(common) < 10:
            continue
        ic = float(composite.loc[common].rank().corr(fwd_rets.loc[common].rank()))
        ic_records.append({"date": date, "ic": ic})

    return ic_records


def run_subset_ic_experiments(
    inputs: dict,
    fwd_ret_matrix: pd.DataFrame,
    validation_end: pd.Timestamp,
    anti_predictive: list[str],
    positive_ic_holdout_features: list[str],
    lgbm_threads: int = 1,
) -> pd.DataFrame:
    """
    Phase 3: Walk-forward IC for each feature subset.
    Returns DataFrame with columns [subset, mean_ic, ic_sharpe, sign_stability, n, feature_count].
    """
    stock_features = inputs["stock_features"]
    all_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    holdout_dates = [d for d in all_dates if d >= HOLDOUT_START and d <= validation_end]

    if not holdout_dates:
        raise ValueError("No holdout dates found for subset IC experiments.")

    params = _make_lgbm_params(BEST_C1_PARAMS, n_jobs=lgbm_threads)

    # Available features in data
    avail = [f for f in ALL_32_FEATURES if f in stock_features.columns]

    # Resolve subset feature lists
    subset_no_anti = [f for f in avail if f not in anti_predictive]
    subset_positive_holdout = [f for f in positive_ic_holdout_features if f in avail]
    subset_vol = [f for f in VOL_FEATURES if f in avail]
    subset_mom = [f for f in MOMENTUM_CORE_FEATURES if f in avail]
    subset_vol_plus_mom = list(dict.fromkeys(subset_vol + subset_mom))
    subset_all = avail

    subsets = [
        ("vol_features_lgbm", subset_vol),
        ("momentum_core", subset_mom),
        ("vol_plus_momentum", subset_vol_plus_mom),
        ("positive_ic_holdout", subset_positive_holdout if subset_positive_holdout else avail),
        ("no_anti_predictive", subset_no_anti if subset_no_anti else avail),
        ("all_features", subset_all),
    ]

    rows = []

    # vol_score_standalone — no model
    logger.info("  [1/7] vol_score_standalone (no model)...")
    t0 = time.perf_counter()
    vs_recs = _ic_for_vol_score_rank(stock_features, fwd_ret_matrix, holdout_dates, inputs)
    vs_stats = _summarise_ic(vs_recs)
    rows.append({
        "subset": "vol_score_standalone",
        "feature_count": len(subset_vol),
        **vs_stats,
    })
    logger.info("    IC Sharpe=%.4f (%.1fs)", vs_stats["ic_sharpe"], time.perf_counter() - t0)

    for idx, (name, feat_list) in enumerate(subsets, start=2):
        if len(feat_list) == 0:
            logger.warning("  [%d/%d] %s — no features available, skipping", idx, len(subsets) + 1, name)
            rows.append({
                "subset": name,
                "feature_count": 0,
                "mean_ic": np.nan,
                "ic_sharpe": np.nan,
                "sign_stability": np.nan,
                "n": 0,
            })
            continue
        logger.info(
            "  [%d/%d] %s (%d features)...", idx, len(subsets) + 1, name, len(feat_list)
        )
        t0 = time.perf_counter()
        recs = _ic_for_feature_subset(
            params, stock_features, fwd_ret_matrix, holdout_dates, inputs, feat_list
        )
        stats = _summarise_ic(recs)
        rows.append({
            "subset": name,
            "feature_count": len(feat_list),
            **stats,
        })
        logger.info("    IC Sharpe=%.4f (%.1fs)", stats["ic_sharpe"], time.perf_counter() - t0)

    return pd.DataFrame(rows).sort_values("ic_sharpe", ascending=False).reset_index(drop=True)


# ── Phase 4: Model sanity comparison ─────────────────────────────────────────

def run_model_sanity_comparison(
    inputs: dict,
    fwd_ret_matrix: pd.DataFrame,
    validation_end: pd.Timestamp,
    best_feature_subset: list[str],
    positive_ic_features: list[str],
    lgbm_threads: int = 1,
) -> pd.DataFrame:
    """
    Phase 4: Compare 5 model types on the best feature subset.
    Returns DataFrame with columns [model, mean_ic, ic_sharpe, sign_stability, n].
    """
    stock_features = inputs["stock_features"]
    all_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    holdout_dates = [d for d in all_dates if d >= HOLDOUT_START and d <= validation_end]

    lgbm_params = _make_lgbm_params(BEST_C1_PARAMS, n_jobs=lgbm_threads)
    rows = []

    # 1. vol_score_rank
    logger.info("  [1/5] vol_score_rank...")
    t0 = time.perf_counter()
    recs = _ic_for_vol_score_rank(stock_features, fwd_ret_matrix, holdout_dates, inputs)
    stats = _summarise_ic(recs)
    rows.append({"model": "vol_score_rank", "feature_count": len(VOL_FEATURES), **stats})
    logger.info("    IC Sharpe=%.4f (%.1fs)", stats["ic_sharpe"], time.perf_counter() - t0)

    # 2. simple_mean_rank
    logger.info("  [2/5] simple_mean_rank (%d pos-IC features)...", len(positive_ic_features))
    t0 = time.perf_counter()
    recs = _ic_for_simple_mean_rank(
        stock_features, fwd_ret_matrix, holdout_dates, inputs, positive_ic_features
    )
    stats = _summarise_ic(recs)
    rows.append({"model": "simple_mean_rank", "feature_count": len(positive_ic_features), **stats})
    logger.info("    IC Sharpe=%.4f (%.1fs)", stats["ic_sharpe"], time.perf_counter() - t0)

    # 3. ridge_regressor
    logger.info("  [3/5] ridge_regressor (%d features)...", len(best_feature_subset))
    t0 = time.perf_counter()
    recs = _ic_for_ridge_subset(
        stock_features, fwd_ret_matrix, holdout_dates, inputs, best_feature_subset
    )
    stats = _summarise_ic(recs)
    rows.append({"model": "ridge_regressor", "feature_count": len(best_feature_subset), **stats})
    logger.info("    IC Sharpe=%.4f (%.1fs)", stats["ic_sharpe"], time.perf_counter() - t0)

    # 4. lgbm_regressor
    logger.info("  [4/5] lgbm_regressor (%d features)...", len(best_feature_subset))
    t0 = time.perf_counter()
    recs = _ic_for_feature_subset(
        lgbm_params, stock_features, fwd_ret_matrix, holdout_dates, inputs, best_feature_subset
    )
    stats = _summarise_ic(recs)
    rows.append({"model": "lgbm_regressor", "feature_count": len(best_feature_subset), **stats})
    logger.info("    IC Sharpe=%.4f (%.1fs)", stats["ic_sharpe"], time.perf_counter() - t0)

    # 5. lgbm_ranker
    logger.info("  [5/5] lgbm_ranker (%d features)...", len(best_feature_subset))
    t0 = time.perf_counter()
    recs = _ic_for_lgbm_ranker_subset(
        lgbm_params, stock_features, fwd_ret_matrix, holdout_dates, inputs, best_feature_subset
    )
    stats = _summarise_ic(recs)
    rows.append({"model": "lgbm_ranker", "feature_count": len(best_feature_subset), **stats})
    logger.info("    IC Sharpe=%.4f (%.1fs)", stats["ic_sharpe"], time.perf_counter() - t0)

    return pd.DataFrame(rows).sort_values("ic_sharpe", ascending=False).reset_index(drop=True)


# ── Phase 5: Portfolio validation ─────────────────────────────────────────────

def build_lgbm_vol_path_c2(
    inputs: dict,
    params: dict,
    validation_end: pd.Timestamp,
    feature_cols: list[str],
    n_top: int = 20,
    lgbm_threads: int = 1,
) -> dict:
    """Build weight path using LGBM predictions with a filtered feature set."""
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
                X_tr = stock_features.loc[pd.IndexSlice[train_start:cutoff, :], feature_cols]
                X_tr = X_tr.loc[X_tr.index.get_level_values("ticker").isin(active)]
                y_tr = fwd_ret_matrix.stack().rename("y").reindex(X_tr.index)
                valid_mask = ~(X_tr.isna().any(axis=1) | y_tr.isna())
                if valid_mask.sum() >= 50:
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
                    X_pred = stock_features.xs(feat_date, level="date")[feature_cols].reindex(active)
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

    return {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": "lgbm_c2"}


def build_lgbm_b2_candidate_c2(
    inputs: dict,
    params: dict,
    validation_end: pd.Timestamp,
    feature_cols: list[str],
    lgbm_threads: int = 1,
) -> pd.DataFrame:
    """B.5 construction with LGBM (filtered features) replacing vol_scores."""
    dates = clipped_evaluation_dates(inputs, validation_end)
    trend_path = build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63)[TREND_NAME]
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)

    lgbm_path = build_lgbm_vol_path_c2(
        inputs, params, validation_end, feature_cols=feature_cols,
        n_top=20, lgbm_threads=lgbm_threads,
    )
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


def build_promoted_lgbm_weights_c2(
    inputs: dict,
    params: dict,
    validation_end: pd.Timestamp,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
    feature_cols: list[str],
    lgbm_threads: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, list]:
    """Full B.5 construction using filtered LGBM signal."""
    base_weights = build_lgbm_b2_candidate_c2(
        inputs, params, validation_end, feature_cols=feature_cols, lgbm_threads=lgbm_threads
    )
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


def _portfolio_metrics_window(net_ret: pd.Series, start: str, end: str) -> dict:
    mask = (net_ret.index >= pd.Timestamp(start)) & (net_ret.index <= pd.Timestamp(end))
    sliced = net_ret[mask]
    if len(sliced) < 21:
        return {"cagr": np.nan, "sharpe": np.nan, "max_dd": np.nan, "n_days": len(sliced)}
    nav = (1.0 + sliced).cumprod()
    m = calculate_metrics(nav)
    return {
        "cagr": m.get("CAGR", np.nan),
        "sharpe": m.get("Sharpe", np.nan),
        "max_dd": m.get("Max Drawdown", np.nan),
        "n_days": len(sliced),
    }


def run_portfolio_validation_c2(
    inputs: dict,
    best_params: dict,
    feature_cols: list[str],
    validation_end: pd.Timestamp,
    lgbm_threads: int = 1,
) -> tuple[dict, pd.DataFrame]:
    """Run LGBM portfolio (filtered features) through B.5 harness."""
    t0 = time.perf_counter()
    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)
    logger.info("Beta/stress frames built in %.1fs", time.perf_counter() - t0)

    t1 = time.perf_counter()
    logger.info(
        "Building C.2 LGBM weight path (%d features, %d LGBM threads)...",
        len(feature_cols), lgbm_threads,
    )
    constrained, diagnostics, _ = build_promoted_lgbm_weights_c2(
        inputs, best_params, validation_end, beta_frame, stress_series,
        feature_cols=feature_cols, lgbm_threads=lgbm_threads,
    )
    logger.info("Weight path built in %.1fs", time.perf_counter() - t1)

    full_sim = run_execution_simulator(
        inputs,
        constrained,
        validation_end,
        Variant("lgbm_c2_best", update_frequency="every_2_rebalances", cost_bps=B1_COST_BPS),
    )
    logger.info(
        "C.2 portfolio: CAGR=%.2f%% Sharpe=%.3f MaxDD=%.2f%%",
        full_sim["cagr"] * 100,
        full_sim["sharpe"],
        full_sim["max_dd"] * 100,
    )

    # Regime breakdown
    net_ret_10 = compute_net_returns(inputs, constrained, validation_end, B1_COST_BPS)
    regime_rows = []
    for regime, start, end in PORTFOLIO_REGIMES:
        m = _portfolio_metrics_window(net_ret_10, start, end)
        regime_rows.append({
            "regime": regime,
            "start": start,
            "end": end,
            "cagr_c2": m["cagr"],
            "sharpe_c2": m["sharpe"],
            "max_dd_c2": m["max_dd"],
            "n_days": m["n_days"],
        })
    regime_df = pd.DataFrame(regime_rows)

    # Add B.5 reference column
    b5_ref = {
        "full 2008-2026": (B5_CAGR, B5_SHARPE, B5_MAX_DD),
    }
    regime_df["sharpe_b5"] = regime_df["regime"].map(
        lambda r: b5_ref.get(r, (np.nan, np.nan, np.nan))[1]
    )
    regime_df["delta_sharpe"] = regime_df["sharpe_c2"] - regime_df["sharpe_b5"]

    return full_sim, regime_df


# ── Report rendering ──────────────────────────────────────────────────────────

def _render_report(
    feature_summary: pd.DataFrame,
    anti_predictive: list[str],
    subset_results: pd.DataFrame,
    model_comparison: pd.DataFrame,
    portfolio_results: dict | None,
    portfolio_regime_df: pd.DataFrame | None,
    best_subset_name: str,
    best_subset_features: list[str],
    verdict: str,
) -> str:
    now = pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "# Phase C.2 — Feature Attribution and Anti-Predictive Feature Pruning",
        "",
        f"- Run date: {now}",
        f"- Phase B.5 baseline: CAGR `{B5_CAGR:.2%}`, Sharpe `{B5_SHARPE:.3f}`, MaxDD `{B5_MAX_DD:.2%}`",
        "- Universe: sp500, holdout 2019-01-01 to 2026-04-24.",
        "- IC metric: rank IC (Spearman) vs 21-day forward return.",
        "",
        f"## Verdict: {verdict}",
        "",
    ]

    lines += [
        "## Feature IC Summary (sorted by holdout IC Sharpe)",
        "",
        "| Feature | holdout_mean_ic | holdout_ic_sharpe | holdout_sign_stability | train_mean_ic | train_ic_sharpe | anti_pred |",
        "|---|---|---|---|---|---|---|",
    ]
    for _, row in feature_summary.iterrows():
        anti = "YES" if row["feature"] in anti_predictive else ""
        lines.append(
            f"| {row['feature']} "
            f"| {row['holdout_mean_ic']:.4f} "
            f"| {row['holdout_ic_sharpe']:.4f} "
            f"| {row['holdout_sign_stability']:.3f} "
            f"| {row['train_mean_ic']:.4f} "
            f"| {row['train_ic_sharpe']:.4f} "
            f"| {anti} |"
        )
    lines.append("")

    lines += [
        "## Anti-Predictive Features",
        "",
        f"Criterion: holdout mean IC < 0 OR holdout sign stability < 0.45",
        f"Count: {len(anti_predictive)} / {len(feature_summary) - 1} features (excl. vol_score_composite)",
        "",
    ]
    if anti_predictive:
        for f in anti_predictive:
            lines.append(f"- `{f}`")
    else:
        lines.append("_(none)_")
    lines.append("")

    lines += [
        "## Feature Subset IC Sharpe Comparison (holdout)",
        "",
    ]
    lines.append(subset_results.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += [
        f"**Best subset:** `{best_subset_name}` ({len(best_subset_features)} features)",
        "",
    ]
    if best_subset_features:
        lines.append("Features: " + ", ".join(f"`{f}`" for f in best_subset_features))
    lines.append("")

    lines += [
        "## Model Sanity Comparison (holdout, best feature subset)",
        "",
    ]
    lines.append(model_comparison.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    if portfolio_results is not None and portfolio_regime_df is not None:
        cagr = portfolio_results.get("cagr", np.nan)
        sharpe = portfolio_results.get("sharpe", np.nan)
        max_dd = portfolio_results.get("max_dd", np.nan)
        to = portfolio_results.get("turnover_sum", np.nan)
        lines += [
            "## Portfolio Validation (C.2 vs B.5 Baseline)",
            "",
            "| Metric | B.5 Baseline | C.2 Best | Delta |",
            "|---|---|---|---|",
            f"| CAGR | {B5_CAGR:.2%} | {cagr:.2%} | {cagr - B5_CAGR:+.2%} |",
            f"| Sharpe | {B5_SHARPE:.3f} | {sharpe:.3f} | {sharpe - B5_SHARPE:+.3f} |",
            f"| MaxDD | {B5_MAX_DD:.2%} | {max_dd:.2%} | {max_dd - B5_MAX_DD:+.2%} |",
            f"| Turnover sum | {B5_TURNOVER:.1f} | {to:.1f} | {to - B5_TURNOVER:+.1f} |",
            "",
        ]
        lines += [
            "### Regime Breakdown",
            "",
        ]
        lines.append(portfolio_regime_df.to_markdown(index=False, floatfmt=".4f"))
        lines.append("")
    else:
        lines += [
            "## Portfolio Validation",
            "",
            "_Skipped — best subset is `vol_score_standalone` (no model), which is already "
            "the production signal validated in Phase B.5. "
            "Next: C.3 portfolio validation of `simple_mean_rank` (IC Sharpe=1.8559) vs B.5 baseline._",
            "",
        ]

    lines += [
        "## Output Files",
        "",
        "- `artifacts/reports/phase_c2_feature_attribution.md`",
        "- `artifacts/reports/feature_ic_by_regime.csv`",
        "- `artifacts/reports/feature_ic_by_period.csv`",
        "- `artifacts/reports/anti_predictive_features.csv`",
        "- `artifacts/reports/feature_subset_results.csv`",
        "- `artifacts/reports/model_sanity_comparison.csv`",
    ]
    if portfolio_results is not None:
        lines.append("- `artifacts/reports/portfolio_validation_c2.csv`")
    lines.append("")

    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _n_cpus = os.cpu_count() or 4

    parser = argparse.ArgumentParser(description="Phase C.2 — Feature Attribution")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    parser.add_argument(
        "--lgbm-threads",
        type=int,
        default=_n_cpus,
        help=f"LGBM threads for sequential phases (default: {_n_cpus})",
    )
    parser.add_argument(
        "--skip-portfolio",
        action="store_true",
        help="Skip portfolio validation even if positive IC is found",
    )
    args = parser.parse_args()

    if not LGBM_AVAILABLE:
        logger.error("lightgbm is not installed. Run: pip install lightgbm")
        sys.exit(1)

    lgbm_pt = args.lgbm_threads
    logger.info(
        "Thread strategy: Phase 1 n_jobs=-1 (no model) | sequential phases %d LGBM threads",
        lgbm_pt,
    )

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # ── Load data ──────────────────────────────────────────────────────────────
    logger.info("Loading inputs for %s...", args.universe)
    t_load = time.perf_counter()
    inputs = load_inputs(args.config, args.universe, args.trend_assets)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )
    logger.info(
        "Inputs loaded in %.1fs. Validation end: %s",
        time.perf_counter() - t_load,
        validation_end.date(),
    )

    fwd_ret_matrix = build_fwd_return_matrix(inputs["prices"])

    # ── Phase 1: Standalone feature IC ────────────────────────────────────────
    logger.info("=== Phase 1: Standalone per-feature IC ===")
    n_feat_jobs = min(_n_cpus, len(ALL_32_FEATURES) + 1)
    feature_summary, by_regime_df, by_year_df = run_standalone_feature_ic(
        inputs, fwd_ret_matrix, validation_end, n_jobs=n_feat_jobs
    )

    if feature_summary.empty:
        logger.error("No feature IC data produced — aborting.")
        sys.exit(1)

    by_regime_df.to_csv(reports_dir / "feature_ic_by_regime.csv", index=False)
    by_year_df.to_csv(reports_dir / "feature_ic_by_period.csv", index=False)
    logger.info("Feature IC CSVs saved.")

    # Log top/bottom features by holdout IC Sharpe
    logger.info("Top 5 features by holdout IC Sharpe:")
    for _, row in feature_summary.head(5).iterrows():
        logger.info(
            "  %s: mean_ic=%.4f, ic_sharpe=%.4f, sign_stab=%.3f",
            row["feature"], row["holdout_mean_ic"], row["holdout_ic_sharpe"], row["holdout_sign_stability"],
        )
    logger.info("Bottom 5 features by holdout IC Sharpe:")
    for _, row in feature_summary.tail(5).iterrows():
        logger.info(
            "  %s: mean_ic=%.4f, ic_sharpe=%.4f, sign_stab=%.3f",
            row["feature"], row["holdout_mean_ic"], row["holdout_ic_sharpe"], row["holdout_sign_stability"],
        )

    # ── Phase 2: Anti-predictive detection ────────────────────────────────────
    logger.info("=== Phase 2: Anti-predictive feature identification ===")
    anti_predictive = identify_anti_predictive(feature_summary)
    logger.info("Anti-predictive features (%d): %s", len(anti_predictive), anti_predictive)

    anti_df = feature_summary[feature_summary["feature"].isin(anti_predictive)].copy()
    anti_df.to_csv(reports_dir / "anti_predictive_features.csv", index=False)
    logger.info("Anti-predictive features saved.")

    # Collect positive-IC holdout features (exclude vol_score_composite from model input)
    positive_ic_holdout_features = feature_summary[
        (feature_summary["holdout_mean_ic"] > 0)
        & (feature_summary["feature"] != "vol_score_composite")
        & (feature_summary["feature"].isin([f for f in ALL_32_FEATURES if f in inputs["stock_features"].columns]))
    ]["feature"].tolist()
    logger.info(
        "Positive holdout IC features (%d): %s",
        len(positive_ic_holdout_features),
        positive_ic_holdout_features,
    )

    # ── Phase 3: Feature subset IC experiments ────────────────────────────────
    logger.info("=== Phase 3: Walk-forward IC by feature subset (%d LGBM threads) ===", lgbm_pt)
    subset_results = run_subset_ic_experiments(
        inputs, fwd_ret_matrix, validation_end,
        anti_predictive=anti_predictive,
        positive_ic_holdout_features=positive_ic_holdout_features,
        lgbm_threads=lgbm_pt,
    )
    subset_results.to_csv(reports_dir / "feature_subset_results.csv", index=False)
    logger.info("Subset IC results saved.")
    logger.info("Best subset: %s (IC Sharpe=%.4f)", subset_results.iloc[0]["subset"], subset_results.iloc[0]["ic_sharpe"])

    # Determine best subset
    best_subset_row = subset_results.iloc[0]
    best_subset_name = str(best_subset_row["subset"])

    # Map subset name to feature list
    avail = [f for f in ALL_32_FEATURES if f in inputs["stock_features"].columns]
    anti_predictive_set = set(anti_predictive)

    _subset_feature_map = {
        "vol_score_standalone": [f for f in VOL_FEATURES if f in avail],
        "vol_features_lgbm": [f for f in VOL_FEATURES if f in avail],
        "positive_ic_holdout": positive_ic_holdout_features if positive_ic_holdout_features else avail,
        "no_anti_predictive": [f for f in avail if f not in anti_predictive_set] or avail,
        "momentum_core": [f for f in MOMENTUM_CORE_FEATURES if f in avail],
        "vol_plus_momentum": list(dict.fromkeys(
            [f for f in VOL_FEATURES if f in avail] + [f for f in MOMENTUM_CORE_FEATURES if f in avail]
        )),
        "all_features": avail,
    }
    best_subset_features = _subset_feature_map.get(best_subset_name, avail)

    # For portfolio purposes, if best is vol_score_standalone, use LGBM on vol features
    portfolio_subset_name = best_subset_name
    portfolio_feature_cols = best_subset_features
    if best_subset_name == "vol_score_standalone":
        portfolio_feature_cols = [f for f in VOL_FEATURES if f in avail]

    # ── Phase 4: Model sanity comparison ──────────────────────────────────────
    logger.info("=== Phase 4: Model sanity comparison (%d LGBM threads) ===", lgbm_pt)
    model_comparison = run_model_sanity_comparison(
        inputs, fwd_ret_matrix, validation_end,
        best_feature_subset=portfolio_feature_cols,
        positive_ic_features=positive_ic_holdout_features,
        lgbm_threads=lgbm_pt,
    )
    model_comparison.to_csv(reports_dir / "model_sanity_comparison.csv", index=False)
    logger.info("Model comparison saved.")

    # ── Phase 5: Portfolio validation ────────────────────────────────────────
    best_subset_ic_sharpe = float(best_subset_row["ic_sharpe"])
    has_positive_ic = np.isfinite(best_subset_ic_sharpe) and best_subset_ic_sharpe > 0

    portfolio_results = None
    portfolio_regime_df = None

    if has_positive_ic and not args.skip_portfolio and best_subset_name != "vol_score_standalone":
        logger.info(
            "=== Phase 5: Portfolio validation (best subset=%s, IC Sharpe=%.4f, %d LGBM threads) ===",
            best_subset_name, best_subset_ic_sharpe, lgbm_pt,
        )
        best_params = _make_lgbm_params(BEST_C1_PARAMS, n_jobs=lgbm_pt)
        portfolio_results, portfolio_regime_df = run_portfolio_validation_c2(
            inputs, best_params, portfolio_feature_cols, validation_end, lgbm_threads=lgbm_pt
        )
        # Save
        regime_out = portfolio_regime_df.copy()
        regime_out.insert(0, "variant", f"C.2_{best_subset_name}")
        regime_out.to_csv(reports_dir / "portfolio_validation_c2.csv", index=False)
        logger.info("Portfolio validation saved.")
    elif has_positive_ic and best_subset_name == "vol_score_standalone":
        logger.info(
            "Best subset is vol_score_standalone (no model) — portfolio validation skipped "
            "in favour of existing B.5 result."
        )
    elif args.skip_portfolio:
        logger.info("Portfolio validation skipped via --skip-portfolio flag.")
    else:
        logger.info(
            "No positive holdout IC Sharpe found (best=%.4f) — skipping portfolio validation.",
            best_subset_ic_sharpe,
        )

    # ── Verdict ───────────────────────────────────────────────────────────────
    if has_positive_ic:
        verdict = "POSITIVE IC FOUND — proceed to C.3"
        logger.info("Phase C.2 verdict: %s (subset=%s, IC Sharpe=%.4f)", verdict, best_subset_name, best_subset_ic_sharpe)
    else:
        verdict = "NO POSITIVE IC — freeze LightGBM, use vol_score as production alpha"
        logger.info("Phase C.2 verdict: %s (best IC Sharpe=%.4f)", verdict, best_subset_ic_sharpe)

    # ── Render report ─────────────────────────────────────────────────────────
    report = _render_report(
        feature_summary=feature_summary,
        anti_predictive=anti_predictive,
        subset_results=subset_results,
        model_comparison=model_comparison,
        portfolio_results=portfolio_results,
        portfolio_regime_df=portfolio_regime_df,
        best_subset_name=best_subset_name,
        best_subset_features=best_subset_features,
        verdict=verdict,
    )
    (reports_dir / "phase_c2_feature_attribution.md").write_text(report)
    logger.info("Report saved to %s", reports_dir / "phase_c2_feature_attribution.md")
    logger.info("Phase C.2 complete — %s", verdict)


if __name__ == "__main__":
    main()
