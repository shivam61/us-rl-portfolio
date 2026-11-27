"""A0 env options: fill_delay, terminal_period, require_book (all off by default = legacy behaviour).

Uses runs_a0/cache (scripts/a0_build_cache.py). Skipped if the cache or data/ is absent.
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
SECTOR = REPO_ROOT / "data" / "features" / "sector_features.parquet"
pytestmark = pytest.mark.skipif(not (CACHE.exists() and SECTOR.exists()),
                                reason="runs_a0/cache or data/ not available")


@pytest.fixture(scope="module")
def cache():
    with open(CACHE, "rb") as fh:
        return pickle.load(fh)


@pytest.fixture(scope="module")
def sector():
    return pd.read_parquet(SECTOR)


def _env(c, sector, dates, end_date=None, **kwargs):
    import src.rl.environment_v2 as envmod
    envmod.DEFAULT_ACTION_DIM = 2
    return PortfolioEnvV2(c["inputs"], c["b5"], start_date=str(dates[0].date()),
                          end_date=str(end_date or dates[-1].date()), rebalance_dates=dates,
                          sector_features_df=sector, **kwargs)


def _window(c, n=3):
    return [d for d in c["ctrl"] if pd.Timestamp("2008-01-01") <= d <= pd.Timestamp("2009-12-31")][:n]


def test_legacy_defaults_are_off(cache, sector):
    dates = _window(cache)
    env = _env(cache, sector, dates)
    assert env.fill_delay == 0 and env.terminal_period is False and env.require_book is False


def test_fill_delay_first_period_is_cash_then_earns_previous_book(cache, sector):
    dates = _window(cache, 4)
    env = _env(cache, sector, dates, fill_delay=1)
    env.reset()
    re_, rc = raw_for_equity(1.0)
    px = cache["inputs"]["prices"]
    t0, t1 = dates[0], dates[1]
    env.step(np.array([re_, rc]))
    day1 = px.index[px.index > t0][0]
    assert env._nav_series.loc[day1] == pytest.approx(1.0, abs=1e-12)  # nothing held until the fill at t1
    w0 = env._current_weights.copy()
    nav_t1 = float(env._nav_series.loc[t1])
    env.step(np.array([re_, rc]))
    tickers = [t for t in w0.index if abs(w0[t]) > 1e-12]
    p_t1 = px.loc[px.index <= t1, tickers].iloc[-1]
    day_after = px.index[px.index > t1][0]
    expected = nav_t1 * (1.0 + float((w0[tickers] * (px.loc[day_after, tickers] / p_t1 - 1.0)).sum()))
    assert env._nav_series.loc[day_after] == pytest.approx(expected, rel=1e-9)


def test_fill_delay_turnover_is_reported_at_the_fill(cache, sector):
    dates = _window(cache, 4)
    env = _env(cache, sector, dates, fill_delay=1)
    env.reset()
    re_, rc = raw_for_equity(1.0)
    _, _, _, _, info0 = env.step(np.array([re_, rc]))
    _, _, _, _, info1 = env.step(np.array([re_, rc]))
    assert info0["turnover"] == 0.0           # nothing filled before the first decision
    assert info1["turnover"] > 0.0            # first real book is filled at the second decision


def test_terminal_period_simulated_to_horizon(cache, sector):
    dates = _window(cache, 3)
    end = pd.Timestamp("2009-12-31")
    env = _env(cache, sector, dates, end_date=end, terminal_period=True)
    env.reset()
    done, info = False, None
    while not done:
        _, _, done, _, info = env.step(np.array([0.0, 0.0]))
    assert dates[-1] < env._nav_series.index[-1] <= end
    assert info["next_date"] == env._nav_series.index[-1].isoformat()


def test_terminal_period_off_matches_legacy(cache, sector):
    dates = _window(cache, 3)
    env = _env(cache, sector, dates, end_date=pd.Timestamp("2009-12-31"))
    env.reset()
    done = False
    while not done:
        _, _, done, _, _ = env.step(np.array([0.0, 0.0]))
    assert env._nav_series.index[-1] == dates[-1]


def test_require_book_drops_dates_before_first_snapshot(cache, sector):
    b5 = cache["b5"]
    first_snapshot = b5.index[b5.fillna(0.0).abs().sum(axis=1) > 1e-12][0]   # 2008-01-07 in the A0 cache
    assert first_snapshot == pd.Timestamp("2008-01-07")
    later = [d for d in _window(cache, 4) if d >= first_snapshot][:3]
    grid = [pd.Timestamp("2008-01-02")] + later
    assert grid[0] < first_snapshot
    legacy = _env(cache, sector, grid)
    assert legacy.rebalance_dates[0] == pd.Timestamp("2008-01-02")
    strict = _env(cache, sector, grid, require_book=True)
    assert strict.rebalance_dates[0] >= first_snapshot
    assert len(strict.rebalance_dates) == len(grid) - 1


def test_fill_delay_rejects_other_values(cache, sector):
    with pytest.raises(ValueError):
        _env(cache, sector, _window(cache), fill_delay=2)
