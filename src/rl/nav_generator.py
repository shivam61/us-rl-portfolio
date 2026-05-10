"""NAV generation utilities for Phase G.4 switching rule.

Provides on-demand RL NAV backtest computation for B.5→RL recovery checks.
"""
import logging
import sys
from pathlib import Path

import pandas as pd
from stable_baselines3 import PPO

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logger = logging.getLogger(__name__)


def generate_rl_nav_on_demand(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    sector_features_df: pd.DataFrame,
    start_date: str = "2019-01-01",
    end_date: str | None = None,
    model_path: str | Path | None = None,
    cost_bps: float = 10.0,
) -> pd.Series:
    """
    Run RL backtest to generate NAV series on-demand.

    WARNING: Expensive computation (full RL episode). Only call when:
      - Current mode is b5_only, AND
      - Flags quiescent for ≥10 days, AND
      - Considering B.5→RL switch

    Args:
        inputs: Standard inputs dict from load_inputs()
        b5_weights_df: B.5 promoted weights (output of build_promoted_weights())
        sector_features_df: Sector features parquet
        start_date: Backtest start (ISO date string)
        end_date: Backtest end (ISO date string or None for max available)
        model_path: Path to RL checkpoint (defaults to production E.7)
        cost_bps: Transaction cost basis points

    Returns:
        NAV series indexed by date (pd.Series with name="nav")
    """
    from src.rl.environment_v2 import PortfolioEnvV2

    if end_date is None:
        end_date = str(inputs["prices"].index.max().date())

    if model_path is None:
        model_path = _REPO_ROOT / "artifacts" / "production" / "rl_e7_clean_promoted.zip"

    logger.info("Loading RL model from %s …", model_path)
    model = PPO.load(str(model_path))

    logger.info("Creating RL environment: %s to %s", start_date, end_date)
    env = PortfolioEnvV2(
        inputs,
        b5_weights_df,
        start_date=start_date,
        end_date=end_date,
        cost_bps=cost_bps,
        sector_features_df=sector_features_df,
    )

    logger.info("Running RL episode …")
    obs, _ = env.reset()
    done = False
    steps = 0
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        steps += 1

    logger.info(
        "RL NAV computed: %d steps, %d records, %.2f → %.2f",
        steps,
        len(env._nav_series),
        float(env._nav_series.iloc[0]),
        float(env._nav_series.iloc[-1]),
    )

    return env._nav_series.rename("nav")


def load_b5_nav_backtest(path: str | Path | None = None) -> pd.Series:
    """
    Load pre-computed B.5 NAV backtest from parquet.

    Args:
        path: Path to nav_b5_backtest.parquet (defaults to data/switching/nav_b5_backtest.parquet)

    Returns:
        NAV series indexed by as_of_date
    """
    if path is None:
        path = _REPO_ROOT / "data" / "switching" / "nav_b5_backtest.parquet"

    logger.info("Loading B.5 NAV backtest from %s", path)
    df = pd.read_parquet(path)
    df["as_of_date"] = pd.to_datetime(df["as_of_date"])
    nav = df.set_index("as_of_date")["nav"]
    logger.info(
        "B.5 NAV loaded: %d records, %s to %s",
        len(nav),
        nav.index.min().date(),
        nav.index.max().date(),
    )
    return nav
