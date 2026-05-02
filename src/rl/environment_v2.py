"""Phase E.3 — RL environment for Regime Controller v2.

Episode: one pass through rebalance dates in [start_date, end_date].
Step:    one every_2_rebalances interval (apply 3-dim action, observe, advance).

Action space: 3-dim raw ∈ [−1, +1] = [raw_equity, raw_trend, raw_cash]
  → mapped by exposure_mix.apply_exposure_mix to (equity, trend, cash) target proportions
  → combined weight vector passed through B.4 hard constraints.

Observation space: 42-dim (see state_builder_v2.py for layout).
"""
import sys
from pathlib import Path

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (_REPO_ROOT, _SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from run_phase_b4_risk_engine import (  # noqa: E402
    BETA_MAX_BASE,
    BETA_MAX_SENSITIVITY,
    BETA_MIN,
    TREND_STRESS_SCALE_MAX,
    TREND_STRESS_THRESHOLD,
    B4Variant,
    _NON_BENCHMARK_TREND,
    apply_b4_constraints,
    build_stress_series,
)
from run_phase_b3_exposure_control import rolling_beta_matrix  # noqa: E402

from src.rl.state_builder_v2 import OBS_DIM, build_state_v2
from src.rl.exposure_mix import apply_exposure_mix
from src.rl.reward_v2 import compute_reward_v2

_B5_VARIANT = B4Variant(
    name="b4_stress_cap_trend_boost",
    beta_min=BETA_MIN,
    beta_max_base=BETA_MAX_BASE,
    beta_max_sensitivity=BETA_MAX_SENSITIVITY,
    trend_stress_boost=True,
    trend_stress_threshold=TREND_STRESS_THRESHOLD,
    trend_stress_scale_max=TREND_STRESS_SCALE_MAX,
)

_DEFAULT_SECTOR_FEATURES_PATH = _REPO_ROOT / "data" / "features" / "sector_features.parquet"


def _initial_trend_frac(b5_weights_df: pd.DataFrame, date: pd.Timestamp, trend_tickers: list[str]) -> float:
    """Compute initial trend sleeve fraction from B.5 weights at or before date."""
    avail = b5_weights_df[b5_weights_df.index <= date]
    if avail.empty:
        return 0.0
    w = avail.iloc[-1].fillna(0.0)
    trend_total = float(w[[t for t in w.index if t in trend_tickers]].abs().sum())
    total = float(w.abs().sum())
    return trend_total / total if total > 1e-12 else 0.0


class PortfolioEnvV2(gym.Env):
    """RL regime controller environment for Phase E.

    Observation: 42-dim state (market + trend + stress + sector signals + portfolio exposure/risk).
    Action: 3-dim raw ∈ [−1, +1] (equity_target, trend_target, cash_target).
    Reward: 63d Sharpe + recovery bonus − drawdown penalty − cash drag − churn penalty.

    Args:
        inputs: Standard inputs dict (prices, vol_scores, universe_config, …).
        b5_weights_df: Precomputed B.5 constrained weights DataFrame (dates × tickers).
        start_date: First rebalance date to include in episodes.
        end_date: Last rebalance date to include in episodes.
        lambda_dd: Drawdown penalty coefficient (default 0.15).
        lambda_cash: Cash-drag penalty coefficient (default 0.03).
        lambda_churn: Equity-churn penalty coefficient (default 0.02).
        rebalance_dates: Optional explicit list of rebalance dates.
        cost_bps: Transaction cost in basis points (applied in daily return sim).
        sector_features_df: Preloaded sector_features parquet; loaded from disk if None.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        inputs: dict,
        b5_weights_df: pd.DataFrame,
        start_date: str = "2008-01-01",
        end_date: str = "2016-12-31",
        lambda_dd: float = 0.15,
        lambda_cash: float = 0.03,
        lambda_churn: float = 0.02,
        rebalance_dates: list[pd.Timestamp] | None = None,
        cost_bps: float = 0.0,
        sector_features_df: pd.DataFrame | None = None,
    ):
        super().__init__()

        self.inputs = inputs
        self.b5_weights_df = b5_weights_df.copy()
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date)
        self.lambda_dd = lambda_dd
        self.lambda_cash = lambda_cash
        self.lambda_churn = lambda_churn
        self._cost_bps = float(cost_bps)

        # Resolve rebalance dates
        if rebalance_dates is not None:
            all_dates = [d for d in rebalance_dates if self.start_date <= d <= self.end_date]
        else:
            diff_mask = b5_weights_df.diff().abs().sum(axis=1) > 1e-8
            all_dates = list(
                b5_weights_df.index[
                    diff_mask
                    & (b5_weights_df.index >= self.start_date)
                    & (b5_weights_df.index <= self.end_date)
                ]
            )
        self.rebalance_dates: list[pd.Timestamp] = all_dates
        assert len(self.rebalance_dates) >= 2, (
            f"Need ≥2 rebalance dates in [{start_date}, {end_date}]; got {len(self.rebalance_dates)}"
        )

        # Precompute helpers (shared across all episodes)
        self.stress_series: pd.Series = build_stress_series(inputs)
        self.beta_frame: pd.DataFrame = rolling_beta_matrix(
            inputs["prices"], inputs["universe_config"].benchmark
        )
        self.prices: pd.DataFrame = inputs["prices"]
        self.ticker_to_sector: dict[str, str] = dict(inputs["universe_config"].tickers)
        self.trend_tickers: list[str] = [
            t for t in _NON_BENCHMARK_TREND if t in b5_weights_df.columns
        ]

        # Precompute SPY trend boolean series (63d return > 0) for cash-drag penalty
        spy_col = inputs["universe_config"].benchmark
        spy_prices = self.prices[spy_col].dropna() if spy_col in self.prices.columns else pd.Series(dtype=float)
        spy_trend_raw = spy_prices.pct_change(63)
        self._spy_trend_positive: pd.Series = spy_trend_raw > 0  # bool Series indexed by date

        # Sector features (load once)
        if sector_features_df is not None:
            self.sector_features_df = sector_features_df
        else:
            self.sector_features_df = pd.read_parquet(_DEFAULT_SECTOR_FEATURES_PATH)

        # Gymnasium spaces
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(OBS_DIM,), dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(3,), dtype=np.float32
        )

        # Episode state (initialised in reset)
        self._step_idx: int = 0
        self._nav_series: pd.Series = pd.Series(dtype=float)
        self._last_rebalance_date: pd.Timestamp | None = None
        self._current_weights: pd.Series | None = None
        self._current_equity_frac: float = 1.0
        self._current_trend_frac: float = 0.0
        self._current_cash_frac: float = 0.0
        self._prev_equity_frac: float = 1.0

    # ------------------------------------------------------------------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._step_idx = 0
        first_date = self.rebalance_dates[0]
        self._last_rebalance_date = None
        self._nav_series = pd.Series(
            [1.0], index=pd.DatetimeIndex([first_date], name="date")
        )
        pre_start = self.b5_weights_df[self.b5_weights_df.index < first_date]
        self._current_weights = pre_start.iloc[-1].fillna(0.0) if not pre_start.empty else None

        # Initialise exposure fracs from B.5 weights (equity = 1 - trend)
        trend_f = _initial_trend_frac(self.b5_weights_df, first_date, self.trend_tickers)
        self._current_equity_frac = max(0.25, 1.0 - trend_f)
        self._current_trend_frac = trend_f
        self._current_cash_frac = 0.0
        self._prev_equity_frac = self._current_equity_frac

        obs = self._build_obs(first_date)
        return obs, {}

    # ------------------------------------------------------------------
    def step(self, action):
        current_date = self.rebalance_dates[self._step_idx]
        next_idx = self._step_idx + 1
        terminated = next_idx >= len(self.rebalance_dates)
        next_date = self.rebalance_dates[next_idx] if not terminated else current_date

        # --- Get B.5 weights at current date ---
        b5_snap = self._b5_weights_at(current_date)

        # --- Apply exposure mix (simplex projection) ---
        action_arr = np.asarray(action, dtype=float)
        mixed_weights, exposure_info = apply_exposure_mix(
            b5_snap, self.trend_tickers, action_arr
        )

        # --- Apply B.4 constraints as hard floor (non-negotiable) ---
        mixed_constrained = self._apply_b4_single_date(mixed_weights, current_date)

        # --- Compute turnover ---
        prev_w = self._current_weights
        if prev_w is not None:
            turnover = float(
                (mixed_constrained - prev_w.reindex(mixed_constrained.index).fillna(0.0))
                .abs().sum()
            )
        else:
            turnover = float(mixed_constrained.abs().sum())
        self._current_weights = mixed_constrained

        # --- Simulate returns ---
        daily_returns = self._compute_daily_returns(
            mixed_constrained, current_date, next_date, rebalance_turnover=turnover
        )

        # --- Update NAV ---
        if len(daily_returns) > 0:
            nav_values = (1.0 + daily_returns).cumprod() * float(self._nav_series.iloc[-1])
            self._nav_series = pd.concat([self._nav_series, nav_values])

        # --- Compute reward ---
        stress_at_step = float(
            self.stress_series[self.stress_series.index <= current_date].iloc[-1]
            if not self.stress_series[self.stress_series.index <= current_date].empty
            else 0.0
        )
        spy_trend = bool(
            self._spy_trend_positive[self._spy_trend_positive.index <= current_date].iloc[-1]
            if not self._spy_trend_positive[self._spy_trend_positive.index <= current_date].empty
            else True
        )

        reward = compute_reward_v2(
            daily_returns=daily_returns,
            portfolio_nav=self._nav_series,
            equity_frac=exposure_info["equity_frac"],
            prev_equity_frac=self._prev_equity_frac,
            cash_frac=exposure_info["cash_frac"],
            stress_score=stress_at_step,
            spy_trend_positive=spy_trend,
            lambda_dd=self.lambda_dd,
            lambda_cash=self.lambda_cash,
            lambda_churn=self.lambda_churn,
        )

        # --- Advance episode state ---
        self._prev_equity_frac = self._current_equity_frac
        self._current_equity_frac = exposure_info["equity_frac"]
        self._current_trend_frac = exposure_info["trend_frac"]
        self._current_cash_frac = exposure_info["cash_frac"]
        self._last_rebalance_date = current_date
        self._step_idx = next_idx

        # --- Build next observation ---
        obs = self._build_obs(next_date if not terminated else current_date)

        info = {
            "date":         current_date.isoformat(),
            "nav":          float(self._nav_series.iloc[-1]),
            "equity_frac":  exposure_info["equity_frac"],
            "trend_frac":   exposure_info["trend_frac"],
            "cash_frac":    exposure_info["cash_frac"],
            "gross":        exposure_info["gross"],
            "turnover":     turnover,
            "next_date":    next_date.isoformat(),
        }
        return obs, float(reward), bool(terminated), False, info

    # ------------------------------------------------------------------
    def _build_obs(self, date: pd.Timestamp) -> np.ndarray:
        return build_state_v2(
            inputs=self.inputs,
            b5_weights=self.b5_weights_df,
            nav_series=self._nav_series,
            date=date,
            stress_series=self.stress_series,
            last_rebalance_date=self._last_rebalance_date,
            current_equity_frac=self._current_equity_frac,
            current_trend_frac=self._current_trend_frac,
            current_cash_frac=self._current_cash_frac,
            sector_features_df=self.sector_features_df,
        )

    def _b5_weights_at(self, date: pd.Timestamp) -> pd.Series:
        available = self.b5_weights_df[self.b5_weights_df.index <= date]
        if available.empty:
            return pd.Series(dtype=float)
        return available.iloc[-1].fillna(0.0)

    def _apply_b4_single_date(self, weights: pd.Series, date: pd.Timestamp) -> pd.Series:
        """Wrap apply_b4_constraints for a single rebalance date."""
        single_row = pd.DataFrame([weights], index=[date])
        beta_slice = self.beta_frame.reindex(index=[date]).fillna(0.0)
        if beta_slice.empty or (beta_slice.abs().sum().sum() < 1e-12):
            return weights
        constrained, _ = apply_b4_constraints(
            single_row,
            beta_slice,
            self.stress_series,
            _B5_VARIANT,
            control_dates=[date],
            benchmark=self.inputs["universe_config"].benchmark,
        )
        return constrained.iloc[0].fillna(0.0)

    def _compute_daily_returns(
        self,
        weights: pd.Series,
        from_date: pd.Timestamp,
        to_date: pd.Timestamp,
        rebalance_turnover: float = 0.0,
    ) -> pd.Series:
        """Portfolio daily returns from from_date+1 through to_date."""
        mask = (self.prices.index > from_date) & (self.prices.index <= to_date)
        price_slice = self.prices.loc[mask]
        if price_slice.empty:
            return pd.Series(dtype=float)
        tickers = [
            t for t in weights.index
            if t in price_slice.columns and abs(float(weights.get(t, 0.0))) > 1e-12
        ]
        if not tickers:
            return pd.Series(0.0, index=price_slice.index)
        w = weights.reindex(tickers).fillna(0.0)

        prior = self.prices.loc[self.prices.index <= from_date, tickers]
        if prior.empty:
            return pd.Series(0.0, index=price_slice.index)
        prior_close = prior.iloc[-1]

        daily_prices = pd.concat([prior_close.to_frame().T, price_slice[tickers]])
        ret = daily_prices.pct_change().iloc[1:].fillna(0.0)
        raw_returns = (ret * w.values).sum(axis=1)

        if self._cost_bps > 0.0 and rebalance_turnover > 0.0 and len(raw_returns) > 0:
            cost_fraction = rebalance_turnover * self._cost_bps / 10_000.0
            r0 = float(raw_returns.iloc[0])
            raw_returns.iloc[0] = float(max(-1.0, (1.0 - cost_fraction) * (1.0 + r0) - 1.0))

        return raw_returns
