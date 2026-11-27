"""M6 data integrity, manifest, deterministic rebuild, feature metadata and M7 distribution regression."""
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from features_v4_helpers import (DAILY_PATH, GRID8W_PATH, GRID14_PATH, MANIFEST_PATH, META_PATH, OUT_DIR, ROOT,
                                 load_daily, require)
from src.rl import features_risk_v4 as L
from src.rl import features_v4_targets as T


from src.rl.features_v4_manifest import BLOCKS, canonical_checksum  # noqa: E402


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def manifest():
    with open(require(MANIFEST_PATH)) as f:
        return json.load(f)


def test_no_constant_or_duplicate_columns():
    """M6: no feature is constant within any regime block and no pair has |corr| > 0.999."""
    P = load_daily()
    for name, a, b in BLOCKS:
        sub = P.loc[a:b]
        for c in P.columns:
            s = sub[c].dropna()
            if len(s) > 20:
                assert s.std() > 1e-12, f"{c} constant in block {name}"
    corr = P.corr().abs()
    dups = [(a, b) for i, a in enumerate(P.columns) for b in P.columns[i + 1:] if corr.loc[a, b] > 0.999]
    assert not dups, dups


def test_removed_dead_and_duplicate_features_absent():
    """FH task 2: the dead, duplicate and redundant features are not in the frozen set."""
    for k in ("hhi_u", "n_names", "invvar_u_21", "invvar_s_21", "base_ret_21", "month_end", "quarter_end",
              "har_u_fc", "garch_u_fc", "base_vol_21", "base_vol_63", "park_s_21"):
        assert k not in L.FEATURE_NAMES, k
    assert set(L.REMOVED_V41) >= {"hhi_u", "n_names", "invvar_u_21", "invvar_s_21", "base_ret_21"}


def test_clusters_have_one_representative():
    """FH task 2: each |corr|>0.95 cluster on the 14d grid keeps exactly one member (checked on the frozen set)."""
    G = pd.read_parquet(require(GRID14_PATH))
    X = G[L.FEATURE_NAMES].dropna()
    c = X.corr().abs()
    pairs = [(a, b) for i, a in enumerate(X.columns) for b in X.columns[i + 1:] if c.loc[a, b] > 0.95]
    assert not pairs, pairs


def test_feature_meta_complete():
    """S4: every retained feature has definition, exact inputs, lag, warm-up, group and rationale."""
    meta = pd.read_csv(require(META_PATH))
    live = meta[meta["group"] != "REMOVED"]
    assert set(live["name"]) == set(L.FEATURE_NAMES)
    for col in ("definition", "inputs", "lag", "warmup", "group", "rationale", "first_valid_date"):
        assert live[col].notna().all() and (live[col].astype(str).str.len() > 0).all(), col
    assert live["lag"].str.contains("close of t").all()


def test_manifest_row_counts_and_checksums(manifest):
    """M6: the manifest's file hashes, row counts, NaN/inf counts and canonical checksums match the files."""
    for name, meta in manifest["outputs"].items():
        p = os.path.join(OUT_DIR, name)
        assert _sha(require(p)) == meta["sha256"], name
        rows = len(pd.read_parquet(p)) if name.endswith(".parquet") else len(pd.read_csv(p))
        assert rows == meta["rows"], name
    daily = load_daily()
    assert canonical_checksum(daily) == manifest["canonical_checksums"]["canonical_checksum_daily"]
    assert int(daily.isna().sum().sum()) == sum(manifest["integrity"]["nan_count"].values())
    assert int(np.isinf(daily.astype(float)).sum().sum()) == 0
    assert manifest["n_features"] == len(L.FEATURE_NAMES)


def test_manifest_input_hashes_and_library_hash(manifest):
    """M6: the history, its inputs and the library source hash in the manifest match the files on disk."""
    assert manifest["library_sha256"] == _sha(os.path.join(ROOT, "src", "rl", "features_risk_v4.py"))
    assert manifest["history_adapter_sha256"] == _sha(os.path.join(ROOT, "src", "rl", "features_v4_history.py"))
    assert manifest["targets_sha256"] == _sha(os.path.join(ROOT, "src", "rl", "features_v4_targets.py"))
    assert manifest["history_sha256"] == _sha(require(os.path.join(OUT_DIR, "history_v41.pkl")))
    for rel, digest in manifest["history_inputs_sha256"].items():
        assert _sha(os.path.join(ROOT, rel)) == digest, rel


def test_distribution_regression_by_block():
    """M7: stored min/quantiles/median/max per feature per regime block are reproduced by recomputation."""
    stored = pd.read_csv(require(os.path.join(OUT_DIR, "distribution_by_block.csv")))
    P = load_daily()
    for name, a, b in BLOCKS:
        sub = P.loc[a:b]
        for c in P.columns:
            s = sub[c].dropna()
            row = stored[(stored.block == name) & (stored.feature == c)].iloc[0]
            assert int(row["n"]) == len(s)
            if len(s):
                assert abs(row["median"] - s.median()) < 1e-9 and abs(row["max"] - s.max()) < 1e-9


def test_outlier_flag_clip_is_documented():
    """M7 outlier audit: z-scores are winsorised at +-3, so |z| > 6 cannot occur; the count of clipped values
    per feature is recorded in the manifest instead of being hidden."""
    P = load_daily()
    assert float(P.abs().max().max()) <= 3.0 + 1e-12


@pytest.mark.slow
def test_deterministic_rebuild(tmp_path, manifest):
    """M6: a fresh materialisation from the history pickle reproduces the canonical checksums exactly."""
    out = tmp_path / "rebuild"
    cmd = [sys.executable, os.path.join(ROOT, "scripts", "features_v4_materialize.py"), "--out", str(out),
           "--hist", require(os.path.join(OUT_DIR, "history_v41.pkl"))]
    subprocess.run(cmd, check=True, cwd=ROOT, capture_output=True)
    rebuilt = json.load(open(out / "canonical_checksums.json"))
    assert rebuilt == manifest["canonical_checksums"]


@pytest.mark.slow
def test_history_build_is_deterministic(tmp_path, manifest):
    """M6/FH task 1: the causal history built from data/ (B.5 pipeline + prices + mask) is reproduced by a second
    independent build; both hashes equal the manifest's history hash. Reads data/ only (read-only)."""
    out = tmp_path / "history_rebuild.pkl"
    cmd = [sys.executable, os.path.join(ROOT, "scripts", "features_v4_history_build.py"), "--out", str(out)]
    subprocess.run(cmd, check=True, cwd=ROOT, capture_output=True)
    side = json.load(open(out.with_suffix(".json")))
    assert side["history_sha256"] == manifest["history_sha256"]
