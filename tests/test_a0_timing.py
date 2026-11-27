"""A0 task 3: timing convention of PortfolioEnvV2 (decision at close t, fill at close t, returns from t+1).

Uses runs_a0/cache (built by scripts/a0_build_cache.py). Skipped if the cache is absent.
"""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from a0_action_map import raw_for_equity  # noqa: E402
from src.rl.environment_v2 import PortfolioEnvV2  # noqa: E402

CACHE = REPO_ROOT / "runs_a0" / "cache" / "a0_cache.pkl"
pytestmark = pytest.mark.skipif(not CACHE.exists(), reason="runs_a0/cache not built")


@pytest.fixture(scope="module")
def cache():
    with open(CACHE, "rb") as fh:
        return pickle.load(fh)


def _env(c, dates, cost_bps=0.0):
    sector = pd.read_parquet(REPO_ROOT / "data" / "features" / "sector_features.parquet")
    import src.rl.environment_v2 as envmod
    envmod.DEFAULT_ACTION_DIM = 2
    return PortfolioEnvV2(c["inputs"], c["b5"], start_date=str(dates[0].date()),
                          end_date=str(dates[-1].date()), rebalance_dates=dates,
                          sector_features_df=sector, cost_bps=cost_bps)


def test_default_costs_train_zero_eval_ten():
    """Legacy defaults are kept (0 bps train/val). Cost is an explicit CLI flag; 10 bps is opt-in."""
    import inspect
    assert inspect.signature(PortfolioEnvV2.__init__).parameters["cost_bps"].default == 0.0
    src = (REPO_ROOT / "scripts" / "train_rl_v2.py").read_text()
    assert '"--train-cost-bps", type=float, default=0.0' in src
    assert '"--val-cost-bps", type=float, default=0.0' in src
    assert "env_kwargs=dict(timing_kwargs, cost_bps=args.train_cost_bps)" in src


def test_first_period_earns_close_t_to_next_close(cache):
    dates = [d for d in cache["ctrl"] if pd.Timestamp("2008-01-01") <= d <= pd.Timestamp("2009-12-31")][:3]
    env = _env(cache, dates)
    env.reset()
    re_, rc = raw_for_equity(1.0)
    env.step(np.array([re_, rc]))
    w = env._current_weights.copy()
    px = cache["inputs"]["prices"]
    t0, t1 = dates[0], dates[1]
    tickers = [t for t in w.index if abs(w[t]) > 1e-12]
    p_t0 = px.loc[px.index <= t0, tickers].iloc[-1]
    day1 = px.index[px.index > t0][0]  # first trading day after the decision close
    expected = 1.0 + float((w[tickers] * (px.loc[day1, tickers] / p_t0 - 1.0)).sum())
    assert env._nav_series.loc[day1] == pytest.approx(expected, rel=1e-9)
    assert day1 <= t1


def test_last_decision_period_is_not_simulated(cache):
    dates = [d for d in cache["ctrl"] if pd.Timestamp("2008-01-01") <= d <= pd.Timestamp("2009-12-31")][:3]
    env = _env(cache, dates)
    env.reset()
    done = False
    last_info = None
    while not done:
        _, _, term, _, info = env.step(np.array([0.0, 0.0]))
        done = term
        last_info = info
    assert env._nav_series.index[-1] == dates[-1]
    assert last_info["next_date"] == dates[-1].isoformat()


def test_next_observation_carries_the_action_just_taken(cache):
    dates = [d for d in cache["ctrl"] if pd.Timestamp("2008-01-01") <= d <= pd.Timestamp("2009-12-31")][:4]
    env = _env(cache, dates)
    env.reset()
    obs, _, _, _, info = env.step(np.array([0.0, 0.0]))
    assert float(obs[36]) == pytest.approx(info["equity_frac"], abs=1e-6)
    assert float(obs[38]) == pytest.approx(info["cash_frac"], abs=1e-6)


def test_cost_applies_to_first_day_of_period_only(cache):
    dates = [d for d in cache["ctrl"] if pd.Timestamp("2008-01-01") <= d <= pd.Timestamp("2009-12-31")][:3]
    e0 = _env(cache, dates, cost_bps=0.0)
    e10 = _env(cache, dates, cost_bps=10.0)
    e0.reset()
    e10.reset()
    re_, rc = raw_for_equity(1.0)
    _, _, _, _, i0 = e0.step(np.array([re_, rc]))
    _, _, _, _, i10 = e10.step(np.array([re_, rc]))
    turnover = i10["turnover"]
    nav0 = e0._nav_series
    nav10 = e10._nav_series
    ratio = nav10.iloc[-1] / nav0.iloc[-1]
    assert ratio < 1.0
    assert ratio == pytest.approx(1.0 - turnover * 10 / 1e4, rel=2e-3)
