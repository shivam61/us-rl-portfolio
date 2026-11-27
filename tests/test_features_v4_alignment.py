"""M2 availability lags, decision-time alignment with the env, and reconciliation of the canonical unit book
to H1 and to the env's own return routine (FH task 1 and task 4)."""
import ast
import os
import pickle
import types

import numpy as np
import pandas as pd
import pytest

from features_v4_helpers import H1_14D, H1_8W, META_PATH, ROOT, load_history, load_meta, require, truncate
from src.rl import features_v4_targets as T
from src.rl.features_risk_v4 import FEATURE_NAMES, build_panel
from src.rl.environment_v2 import PortfolioEnvV2

LIB = os.path.join(ROOT, "src", "rl", "features_risk_v4.py")
DOCUMENTED_INPUTS = {"spy", "iwm", "tlt", "gld", "uup", "vix", "spy_high", "spy_low", "stocks", "universe_mask",
                     "unit_w", "unit_ret", "base_ret", "base_gross", "stress"}


@pytest.fixture(scope="module")
def H():
    return load_history()


@pytest.fixture(scope="module")
def full(H):
    return build_panel(H)


def test_input_availability_lags_documented():
    """M2: the library reads only documented history series, and every feature has a recorded lag."""
    used = set()
    for node in ast.walk(ast.parse(open(LIB).read())):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "history":
            if isinstance(node.slice, ast.Constant):
                used.add(node.slice.value)
    assert used <= DOCUMENTED_INPUTS, used - DOCUMENTED_INPUTS
    meta = pd.read_csv(require(META_PATH))
    live = meta[meta["group"] != "REMOVED"]
    assert len(live) == len(FEATURE_NAMES)
    assert live["lag"].notna().all() and (live["lag"].str.startswith("0")).all()


def test_vix_same_day_convention(H):
    """M2: VIX enters at its close of t (lag 0). Changing VIX on t moves vix_level(t) and no earlier row."""
    d = pd.Timestamp("2016-03-15")
    base = build_panel(H)
    Hx = dict(H)
    v = H["vix"].copy()
    v.loc[d] = v.loc[d] * 1.5
    Hx["vix"] = v
    alt = build_panel(Hx)
    assert not np.isclose(base.loc[d, "vix_level"], alt.loc[d, "vix_level"], equal_nan=True)
    prev = base.index[base.index < d][-5:]
    assert np.allclose(base.loc[prev, "vix_level"].astype(float), alt.loc[prev, "vix_level"].astype(float),
                       equal_nan=True)


def _stub(prices):
    return types.SimpleNamespace(prices=prices, _cost_bps=0.0)


def test_env_fill_convention_is_close_of_decision_date(H):
    """M2/M8 decision time: the env fills at the close of the decision date t (its base price is the close
    on or before t) and earns the first return from close t to close t+1. Asserted on the env routine."""
    prices = H["stocks"]
    stub = _stub(prices)
    t = prices.index[100]
    w = pd.Series({prices.columns[0]: 1.0})
    r = PortfolioEnvV2._compute_daily_returns(stub, w, t, prices.index[103])
    p = prices[prices.columns[0]]
    assert np.isclose(r.iloc[0], p.iloc[101] / p.iloc[100] - 1, rtol=1e-12, atol=0)
    assert r.index[0] == prices.index[101]


def test_decision_time_alignment_with_env(H, full):
    """The library's information set at each decision t is a subset of the env's: every history input is
    read at or before t (truncation check) and the env fill uses the close of t. Checked on the 8w control
    dates (the B.5 rebalance schedule), 3 decisions in the crises and 3 others."""
    dates = T.grid_dates("8w", load_meta()["control_dates"], H["spy"].index)
    picks = [dates[5], dates[40], dates[60], dates[-3]]
    for d in picks:
        a = full.loc[d, FEATURE_NAMES]
        b = build_panel(truncate(H, d)).loc[d, FEATURE_NAMES]
        same = (a.isna() & b.isna()) | np.isclose(a.astype(float), b.astype(float), rtol=1e-9, atol=1e-12)
        assert bool(np.all(same)), f"information after t used at {d.date()}: {list(a.index[~same])}"
    # the env earns the first return strictly after the decision close
    stub = _stub(H["stocks"])
    d, d_next = picks[0], dates[dates.index(picks[0]) + 1]
    w = H["unit_w"].loc[d]
    r = PortfolioEnvV2._compute_daily_returns(stub, w[w != 0], d, d_next)
    assert r.index.min() > d, "env earns returns only after the decision close"


def test_canonical_unit_ret_reconciles_to_h1_8w(H):
    """FH task 1: the canonical unit return equals the H1 8-week cache to 1e-9 (measured 3.6e-16)."""
    h8 = pickle.load(open(require(H1_8W), "rb"))["base_daily"]
    c = pd.concat([H["unit_ret"].rename("canon"), h8.rename("h1")], axis=1).loc["2008-01-08":"2026-04-06"]
    dev = (c.canon - c.h1).abs()
    assert c.canon.notna().all(), "canonical unit return has NaN inside the H1 window"
    assert float(dev.max()) < 1e-9, f"max deviation {float(dev.max()):.3e}"


def test_canonical_unit_ret_reconciles_to_env_routine_on_8w_windows(H):
    """FH task 1: for every 8w control-date window, the env's own return routine with the weights set at the
    window start equals the canonical unit return over that window (max deviation < 1e-9)."""
    dates = T.grid_dates("8w", load_meta()["control_dates"], H["spy"].index)
    prices = H["stocks"]
    stub = _stub(prices)
    worst = 0.0
    for a, b in zip(dates[:-1], dates[1:]):
        w = H["unit_w"].loc[a]
        w = w[w.abs() > 0]
        env_r = PortfolioEnvV2._compute_daily_returns(stub, w, a, b)
        canon = H["unit_ret"].loc[(H["unit_ret"].index > a) & (H["unit_ret"].index <= b)]
        j = pd.concat([env_r.rename("e"), canon.rename("c")], axis=1).dropna()
        assert len(j) == len(canon.dropna()) and len(j) > 0
        worst = max(worst, float((j.e - j.c).abs().max()))
    assert worst < 1e-9, f"env routine vs canonical: {worst:.3e}"


def test_h1_14d_grid_dates_reproduced(H):
    """The biweekly decision grid is reproduced exactly from prices (no H1 run needed at build time)."""
    h14 = pickle.load(open(require(H1_14D), "rb"))
    assert list(pd.DatetimeIndex(h14["dates"])) == T.grid_dates("14d", None, H["spy"].index)
