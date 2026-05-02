"""Phase D.3 — RL environment wiring state builder, tilt application, and reward.

Episode = one pass through rebalance dates in [start_date, end_date].
Step = one every_2_rebalances interval (apply action, observe outcome, advance).
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

from src.rl.state_builder import TREND_ASSETS, build_state
from src.rl.tilts import apply_sector_tilts
from src.rl.reward import compute_reward

_B5_VARIANT = B4Variant(
    name="b4_stress_cap_trend_boost",
    beta_min=BETA_MIN,
    beta_max_base=BETA_MAX_BASE,
    beta_max_sensitivity=BETA_MAX_SENSITIVITY,
    trend_stress_boost=True,
    trend_stress_threshold=TREND_STRESS_THRESHOLD,
    trend_stress_scale_max=TREND_STRESS_SCALE_MAX,
)


class PortfolioEnv(gym.Env):
    """RL overlay environment for Phase D.

    Observation: 28-dim state (macro + stress + sector vol_scores + sector weights + portfolio state).
    Action: 12-dim raw ∈ [−1, +1] (11 sector tilts + 1 aggressiveness).
    Reward: rolling_sharpe_21d − tilt_penalty − drawdown_penalty.

    Args:
        inputs: Standard inputs dict (prices, vol_scores, universe_config, …).
        b5_weights_df: Precomputed B.5 constrained weights DataFrame (dates × tickers).
        start_date: First rebalance date to include in episodes.
        end_date: Last rebalance date to include in episodes.
        lambda_tilt: Tilt penalty coefficient in reward.
        lambda_dd: Drawdown penalty coefficient in reward.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        inputs: dict,
        b5_weights_df: pd.DataFrame,
        start_date: str = "2008-01-01",
        end_date: str = "2016-12-31",
        lambda_tilt: float = 0.01,
        lambda_dd: float = 0.05,
        rebalance_dates: list[pd.Timestamp] | None = None,
        cost_bps: float = 0.0,
    ):
        super().__init__()

        self.inputs = inputs
        self.b5_weights_df = b5_weights_df.copy()
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date)
        self.lambda_tilt = lambda_tilt
        self.lambda_dd = lambda_dd
        self._cost_bps = float(cost_bps)

        # Use provided rebalance_dates (actual change dates from build_promoted_weights),
        # or detect them from weight differences in the DataFrame.
        if rebalance_dates is not None:
            all_dates = [
                d for d in rebalance_dates
                if self.start_date <= d <= self.end_date
            ]
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

        # Precompute helpers
        self.stress_series: pd.Series = build_stress_series(inputs)
        self.beta_frame: pd.DataFrame = rolling_beta_matrix(
            inputs["prices"], inputs["universe_config"].benchmark
        )
        self.prices: pd.DataFrame = inputs["prices"]
        self.ticker_to_sector: dict[str, str] = dict(inputs["universe_config"].tickers)
        self.trend_tickers: list[str] = [
            t for t in _NON_BENCHMARK_TREND if t in b5_weights_df.columns
        ]

        # Gymnasium spaces
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(28,), dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(12,), dtype=np.float32
        )

        # Episode state (initialised in reset)
        self._step_idx: int = 0
        self._nav_series: pd.Series = pd.Series(dtype=float)
        self._last_rebalance_date: pd.Timestamp | None = None
        self._current_weights: pd.Series | None = None  # weights held since last rebalance

    # ------------------------------------------------------------------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._step_idx = 0
        first_date = self.rebalance_dates[0]
        self._last_rebalance_date = None
        self._nav_series = pd.Series(
            [1.0], index=pd.DatetimeIndex([first_date], name="date")
        )
        # Initialise _current_weights from B.5 weights just before episode start.
        # This gives correct turnover on the first rebalance (change from pre-episode
        # B.5 weights). For the holdout window, the portfolio was already running;
        # for training windows that start at the first-ever B.5 date, _current_weights
        # = None, which triggers full-acquisition turnover.
        pre_start = self.b5_weights_df[self.b5_weights_df.index < first_date]
        self._current_weights = pre_start.iloc[-1].fillna(0.0) if not pre_start.empty else None
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

        # --- Apply sector tilts ---
        action_arr = np.asarray(action, dtype=float)
        tilted = apply_sector_tilts(
            b5_snap,
            self.ticker_to_sector,
            self.trend_tickers,
            raw_action=action_arr,
        )

        # --- Apply B.4 constraints as hard floor ---
        tilted_constrained = self._apply_b4_single_date(tilted, current_date)

        # --- Compute sector tilts applied (for reward/info) ---
        b5_sector_weights = self._sector_weights_from_slice(b5_snap)
        tilted_sector_weights = self._sector_weights_from_slice(tilted_constrained)
        applied_tilts = tilted_sector_weights - b5_sector_weights

        # --- Compute turnover vs weights held since last rebalance ---
        prev_w = self._current_weights
        if prev_w is not None:
            turnover = float(
                (tilted_constrained - prev_w.reindex(tilted_constrained.index).fillna(0.0))
                .abs().sum()
            )
        else:
            # First rebalance with no prior weights: treat as full acquisition
            turnover = float(tilted_constrained.abs().sum())
        self._current_weights = tilted_constrained

        # --- Simulate returns from current_date to next_date ---
        daily_returns = self._compute_daily_returns(
            tilted_constrained, current_date, next_date, rebalance_turnover=turnover
        )

        # --- Update NAV ---
        if len(daily_returns) > 0:
            nav_values = (1.0 + daily_returns).cumprod() * float(self._nav_series.iloc[-1])
            self._nav_series = pd.concat([self._nav_series, nav_values])

        # --- Compute reward ---
        reward = compute_reward(
            daily_returns,
            applied_tilts,
            self._nav_series,
            lambda_tilt=self.lambda_tilt,
            lambda_dd=self.lambda_dd,
        )

        # --- Advance step ---
        self._last_rebalance_date = current_date
        self._step_idx = next_idx

        # --- Build next observation ---
        obs = self._build_obs(next_date if not terminated else current_date)

        info = {
            "date": current_date.isoformat(),
            "nav": float(self._nav_series.iloc[-1]),
            "applied_tilts": applied_tilts.tolist(),
            "aggressiveness": float(
                0.75 + (1.0 - 0.75) * (float(action_arr[11]) + 1.0) / 2.0
            ),
            "turnover": turnover,           # for post-hoc cost sensitivity in D.6
            "next_date": next_date.isoformat(),
        }
        return obs, float(reward), bool(terminated), False, info

    # ------------------------------------------------------------------
    def _build_obs(self, date: pd.Timestamp) -> np.ndarray:
        return build_state(
            inputs=self.inputs,
            b5_weights=self.b5_weights_df,
            nav_series=self._nav_series,
            date=date,
            stress_series=self.stress_series,
            last_rebalance_date=self._last_rebalance_date,
        )

    def _b5_weights_at(self, date: pd.Timestamp) -> pd.Series:
        available = self.b5_weights_df[self.b5_weights_df.index <= date]
        if available.empty:
            return pd.Series(dtype=float)
        return available.iloc[-1].fillna(0.0)

    def _apply_b4_single_date(
        self, weights: pd.Series, date: pd.Timestamp
    ) -> pd.Series:
        """Wrap apply_b4_constraints for a single rebalance date."""
        single_row = pd.DataFrame([weights], index=[date])
        beta_slice = self.beta_frame.reindex(index=[date]).fillna(0.0)
        if beta_slice.empty or (beta_slice.abs().sum().sum() < 1e-12):
            # No beta data: skip constraint (env handles startup gracefully)
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

    def _sector_weights_from_slice(self, weights: pd.Series) -> np.ndarray:
        from src.rl.state_builder import SECTOR_ORDER
        ticker_to_sector = self.ticker_to_sector
        trend_set = TREND_ASSETS | set(self.trend_tickers)
        stock_w = weights[[t for t in weights.index if t not in trend_set]]
        out = np.zeros(11, dtype=float)
        for i, sec in enumerate(SECTOR_ORDER):
            tickers = [t for t in stock_w.index if ticker_to_sector.get(t) == sec]
            out[i] = float(stock_w.reindex(tickers).fillna(0.0).sum())
        return out

    def _compute_daily_returns(
        self,
        weights: pd.Series,
        from_date: pd.Timestamp,
        to_date: pd.Timestamp,
        rebalance_turnover: float = 0.0,
    ) -> pd.Series:
        """Compute portfolio daily returns from from_date+1 through to_date.

        Transaction cost (if cost_bps > 0) is applied to the first day's return only,
        matching the logic in compute_net_returns: cost = turnover * cost_bps / 10_000.
        """
        mask = (self.prices.index > from_date) & (self.prices.index <= to_date)
        price_slice = self.prices.loc[mask]
        if price_slice.empty:
            return pd.Series(dtype=float)
        tickers = [t for t in weights.index if t in price_slice.columns and abs(float(weights.get(t, 0.0))) > 1e-12]
        if not tickers:
            return pd.Series(0.0, index=price_slice.index)
        w = weights.reindex(tickers).fillna(0.0)

        # Use prior close to avoid NaN on first day
        prior = self.prices.loc[self.prices.index <= from_date, tickers]
        if prior.empty:
            return pd.Series(0.0, index=price_slice.index)
        prior_close = prior.iloc[-1]

        daily_prices = pd.concat([prior_close.to_frame().T, price_slice[tickers]])
        ret = daily_prices.pct_change().iloc[1:].fillna(0.0)
        raw_returns = (ret * w.values).sum(axis=1)

        # Apply transaction cost on first day of this holding interval
        if self._cost_bps > 0.0 and rebalance_turnover > 0.0 and len(raw_returns) > 0:
            cost_fraction = rebalance_turnover * self._cost_bps / 10_000.0
            r0 = float(raw_returns.iloc[0])
            raw_returns.iloc[0] = float(
                max(-1.0, (1.0 - cost_fraction) * (1.0 + r0) - 1.0)
            )

        return raw_returns
