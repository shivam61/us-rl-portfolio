"""M8 target hygiene, the v4.1 regret target T5 (hand-built cases), and grid consistency (FH tasks 5 and 6)."""
import pickle

import numpy as np
import pandas as pd
import pytest

from features_v4_helpers import H1_8W, load_history, load_meta, load_daily, require
from src.rl import features_v4_targets as T


@pytest.fixture(scope="module")
def H():
    return load_history()


def _u(vals, start="2020-01-01"):
    idx = pd.bdate_range(start, periods=len(vals))
    return pd.Series(vals, index=idx, dtype=float)


def test_t5_hand_built_cases():
    """T5 = U(e*) - U(0.72) with U(e) = sum log(1 + e*u). Hand-computed cases."""
    # all days +1%: log-utility increases in e, best share = 1.0, call +1
    t = T.period_targets(_u([0.01] * 5), pd.Timestamp("2019-12-31"), _u([0.01] * 5).index[-1])
    assert t["T5_call"] == 1.0 and t["T5_regret"] > 0
    assert np.isclose(t["T5_regret"], 5 * (np.log(1.01) - np.log(1 + 0.72 * 0.01)))
    assert np.isclose(t["T5_signed"], t["T5_regret"])
    # all days -1%: best share = 0, call -1, regret = U(0) - U(0.72) = -U(0.72) (positive)
    u = _u([-0.01] * 4)
    t = T.period_targets(u, pd.Timestamp("2019-12-31"), u.index[-1])
    assert t["T5_call"] == -1.0 and np.isclose(t["T5_regret"], -4 * np.log(1 - 0.72 * 0.01))
    assert np.isclose(t["T5_signed"], -t["T5_regret"])
    # zero returns: every share has utility 0, ties resolve to the static share, call 0, regret 0
    u = _u([0.0] * 3)
    t = T.period_targets(u, pd.Timestamp("2019-12-31"), u.index[-1])
    assert t["T5_call"] == 0.0 and t["T5_regret"] == 0.0 and t["T5_signed"] == 0.0


def test_t5_regret_nonnegative_and_grid_bounded():
    rng = np.random.default_rng(5)
    for _ in range(200):
        u = _u(rng.normal(0.0005, 0.02, size=40))
        t = T.period_targets(u, pd.Timestamp("2019-12-31"), u.index[-1])
        assert t["T5_regret"] >= 0
        assert t["T5_call"] in (-1.0, 0.0, 1.0)
        assert np.isclose(t["T5_signed"], t["T5_call"] * t["T5_regret"])


def test_targets_forward_only_no_overlap():
    """M8: each decision's target uses only returns in (d_i, d_{i+1}]; periods are disjoint; last NaN."""
    u = _u(np.random.default_rng(1).normal(0, 0.01, 60))
    dates = [u.index[0], u.index[10], u.index[25], u.index[59]]
    tg = T.targets_for_grid(u, dates)
    assert tg.iloc[-1].isna().all()
    for i in range(len(dates) - 1):
        u2 = u.copy()
        u2[u2.index <= dates[i]] = 99.0  # corrupt the past
        u2[u2.index > dates[i + 1]] = -99.0  # and the future
        t2 = T.period_targets(u2, dates[i], dates[i + 1])
        assert np.isclose(t2["T3_ret"], tg.iloc[i]["T3_ret"]), "target uses data outside its period"


def test_target_nan_policy_and_last_period():
    u = _u([0.01, np.nan, 0.01, 0.01])
    t = T.period_targets(u, u.index[0], u.index[-1])
    assert all(pd.isna(v) for v in t.values())  # NaN inside the period -> NaN target, never zero-filled


def test_targets_match_h1_8w_cache(H):
    """FH task 5: the 8w targets rebuilt from the canonical series reproduce H1's 8w cache (T3, T1)."""
    h8 = pickle.load(open(require(H1_8W), "rb"))
    dates = T.grid_dates("8w", load_meta()["control_dates"], H["spy"].index)
    tg = T.targets_for_grid(H["unit_ret"], dates)
    R = pd.Series(h8["R"], index=pd.DatetimeIndex(h8["dates"]))
    M = pd.Series(h8["PATHMDD"], index=pd.DatetimeIndex(h8["dates"]))
    ok = R.notna() & tg.T3_ret.notna()
    assert int(ok.sum()) >= 115
    assert float((tg.T3_ret[ok] - R[ok]).abs().max()) < 1e-9
    assert float((tg.T1_mdd[ok] - M[ok]).abs().max()) < 1e-9


def test_8w_and_14d_grids_agree_on_shared_definitions(H):
    """FH task 5: both grids come from one feature panel and one canonical unit series.
    (a) features in both tables equal the daily table on the same dates (one panel);
    (b) every target is recomputed independently here from the canonical series (one definition);
    (c) the two decision sets are reported: the 8w control dates and the biweekly dates share no date by
        construction, so 'agreement on overlapping dates' is tested through (a) and (b), not through shared
        target rows. The count of shared dates is asserted, so a future change of grid is noticed."""
    G14 = pd.read_parquet(require(__import__("features_v4_helpers").GRID14_PATH))
    G8 = pd.read_parquet(require(__import__("features_v4_helpers").GRID8W_PATH))
    D = load_daily()
    feats = [c for c in G14.columns if c not in T.TARGET_COLS and c != "block"]
    for G in (G14, G8):
        assert np.allclose(G[feats].astype(float).values, D.loc[G.index, feats].astype(float).values,
                           equal_nan=True, atol=1e-12)
    u = H["unit_ret"]
    checked = {"14d": 0, "8w": 0}
    for G, name in ((G14, "14d"), (G8, "8w")):
        dates = list(G.index)
        for i in range(0, len(dates) - 1, max(1, (len(dates) - 1) // 25)):  # about 25 periods per grid
            a, b = dates[i], dates[i + 1]
            s = u.loc[(u.index > a) & (u.index <= b)]
            if s.isna().any() or len(s) == 0:
                assert pd.isna(G.loc[a, "T3_ret"]), (name, a)  # NaN period -> NaN target, never zero
                continue
            nav = np.cumprod(1.0 + s.values)
            R = nav[-1] - 1.0
            assert abs(R - G.loc[a, "T3_ret"]) < 1e-12, (name, a)
            assert abs(float(np.min(np.r_[1.0, nav] / np.maximum.accumulate(np.r_[1.0, nav]) - 1.0))
                       - G.loc[a, "T1_mdd"]) < 1e-12, (name, a)
            checked[name] += 1
    assert checked["14d"] >= 10 and checked["8w"] >= 10
    assert len(G14.index.intersection(G8.index)) == 0, "grids now share decision dates: revisit this test"


def test_grids_have_documented_targets_and_block():
    d = load_daily()
    G = pd.read_parquet(require(__import__("features_v4_helpers").GRID14_PATH))
    assert set(T.TARGET_COLS) <= set(G.columns) and "block" in G.columns
    assert G.index.max() <= T.END
    assert G[T.TARGET_COLS].iloc[-1].isna().all()
    assert set(d.columns) <= set(G.columns)
