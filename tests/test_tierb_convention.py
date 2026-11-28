"""Tests for the Tier B -> main cache price convention (scripts/convert_tierb_convention.py)."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("convert_tierb_convention", REPO / "scripts" / "convert_tierb_convention.py")
conv = importlib.util.module_from_spec(_spec)
sys.modules["convert_tierb_convention"] = conv
_spec.loader.exec_module(conv)

TIERB_SRC = Path("data/raw_tierB/raw")


def _synthetic() -> pd.DataFrame:
    idx = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"])
    close = np.array([10.0, 10.5, 9.8, 10.2])
    adj = np.array([6.0, 6.3, 5.88, 6.12])  # dividend-like adjustment: adj/close varies by row
    return pd.DataFrame(
        {
            "open": close * 0.99,
            "high": close * 1.02,
            "low": close * 0.97,
            "close": close,
            "volume": np.array([1000, 2000, 1500, 1200], dtype="int64"),
            "adj_close": adj,
        },
        index=idx,
    )


def test_converted_close_equals_adj_close():
    out = conv.convert_frame(_synthetic())
    assert np.array_equal(out["close"].to_numpy(), _synthetic()["adj_close"].to_numpy())


def test_returns_of_converted_close_match_adj_close_returns():
    src = _synthetic()
    out = conv.convert_frame(src)
    r_new = out["close"].pct_change().dropna()
    r_adj = src["adj_close"].pct_change().dropna()
    assert np.allclose(r_new.to_numpy(), r_adj.to_numpy(), rtol=0, atol=1e-12)


def test_ohlc_scaled_and_volume_dtype_index_preserved():
    src = _synthetic()
    out = conv.convert_frame(src)
    factor = src["adj_close"] / src["close"]
    assert np.allclose(out["high"].to_numpy(), (src["high"] * factor).to_numpy(), rtol=0, atol=1e-12)
    assert out["volume"].dtype == src["volume"].dtype
    assert (out["volume"].to_numpy() == src["volume"].to_numpy()).all()
    assert out.index.equals(src.index)
    assert list(out.columns) == list(src.columns)
    assert all(out[c].dtype == src[c].dtype for c in src.columns)


def test_rejects_nonpositive_close():
    bad = _synthetic()
    bad.iloc[1, bad.columns.get_loc("close")] = 0.0
    with pytest.raises(ValueError):
        conv.convert_frame(bad)


@pytest.mark.skipif(not (TIERB_SRC / "JEF.parquet").exists(), reason="Tier B raw files not present")
def test_real_tierb_file_converted_matches_adj_close_returns():
    src = pd.read_parquet(TIERB_SRC / "JEF.parquet")
    out = conv.convert_frame(src)
    assert np.array_equal(out["close"].to_numpy(), src["adj_close"].to_numpy())
    r_new = out["close"].pct_change().dropna()
    r_adj = src["adj_close"].pct_change().dropna()
    assert np.allclose(r_new.to_numpy(), r_adj.to_numpy(), rtol=0, atol=1e-12)
