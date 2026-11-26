"""Equity-only policy: only individual stocks are ever bought; the rest is cash.

TLT/GLD/UUP remain readable as RL state signals (obs[7..12]) but are never traded.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO, REPO / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from run_phase_a7_trend_overlay import NON_TRADABLE_ASSETS, SIGNAL_ONLY_ASSETS, TREND_ASSETS  # noqa: E402
from run_phase_b4_risk_engine import _NON_BENCHMARK_TREND  # noqa: E402
from src.rl.exposure_mix import apply_exposure_mix  # noqa: E402
from src.rl.state_builder_v2 import OBS_DIM  # noqa: E402


def test_no_tradable_trend_assets():
    assert _NON_BENCHMARK_TREND == []
    for t in ("TLT", "GLD", "UUP"):
        assert t not in TREND_ASSETS
        assert t in SIGNAL_ONLY_ASSETS
        assert t in NON_TRADABLE_ASSETS
    assert "SPY" in NON_TRADABLE_ASSETS


def test_state_dimension_unchanged():
    # TLT/GLD/UUP momentum stay in the state as signals, so the E.7 checkpoint shape is intact.
    assert OBS_DIM == 42


def test_two_sleeve_action_splits_whole_book_between_equity_and_cash():
    w = pd.Series({"AAA": 0.5, "BBB": 0.3, "CCC": 0.2})
    seen = set()
    for raw in ([1.0, -1.0], [-1.0, 1.0], [0.0, 0.0], [1.0, 1.0], [-1.0, -1.0], [0.3, -0.7]):
        result, info = apply_exposure_mix(w, [], np.array(raw))
        invested = float(result.abs().sum())
        assert info["trend_frac"] == 0.0
        assert abs(invested - info["equity_frac"]) < 1e-9          # equity share is fully invested
        assert abs(info["equity_frac"] + info["cash_frac"] - 1.0) < 1e-9   # nothing else exists
        assert 0.0 <= info["cash_frac"] <= 0.5 + 1e-9
        seen.add(round(info["equity_frac"], 3))
    assert len(seen) > 3  # the agent's two outputs actually move the equity/cash split
    assert apply_exposure_mix(w, [], np.array([1.0, -1.0]))[1]["equity_frac"] == 1.0  # can be fully invested


def test_finalize_equity_only_sum_equals_agent_share_and_drops_non_stocks():
    import pytest
    from src.rl.exposure_mix import NON_TRADABLE_ASSETS, finalize_equity_only
    w = pd.Series({"AAA": 0.5, "BBB": 0.3, "CCC": 0.2, "SPY": 0.0, "TLT": 0.0, "GLD": 0.0, "UUP": 0.0})
    rng = np.random.default_rng(0)
    for _ in range(200):
        raw = rng.uniform(-1, 1, 2)
        mixed, info = apply_exposure_mix(w, [], raw)
        final = finalize_equity_only(mixed, info["equity_frac"])
        assert abs(float(final.abs().sum()) - info["equity_frac"]) < 1e-6
        assert not set(final.index) & set(NON_TRADABLE_ASSETS)
    # an overlay or a beta scale-down breaks the invariant loudly instead of silently
    with pytest.raises(AssertionError):
        finalize_equity_only(pd.Series({"AAA": 0.2, "BBB": 0.1}), 0.73)


def test_non_tradable_constant_is_single_source():
    from src.rl.exposure_mix import NON_TRADABLE_ASSETS as shared
    assert set(shared) <= set(NON_TRADABLE_ASSETS)
    assert {"SPY", "TLT", "GLD", "UUP"} == set(shared)


def test_env_action_dim_follows_module_default():
    import src.rl.environment_v2 as env_mod
    assert env_mod.DEFAULT_ACTION_DIM in (2, 3)
