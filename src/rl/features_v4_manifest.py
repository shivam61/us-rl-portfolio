"""Shared constants and checksum helpers for the v4.1 materialisation (used by scripts/features_v4_materialize.py
and by the certification tests). Kept free of process-level side effects."""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

BLOCKS = [("2008-H1 warm-up", "2008-01-01", "2008-06-30"), ("2008-H2 GFC", "2008-07-01", "2009-12-31"),
          ("2010-12", "2010-01-01", "2012-12-31"), ("2013-18Q3", "2013-01-01", "2018-09-30"),
          ("2018Q4", "2018-10-01", "2018-12-31"), ("2019", "2019-01-01", "2019-12-31"),
          ("2020 crash+rec", "2020-01-01", "2020-12-31"), ("2021", "2021-01-01", "2021-12-31"),
          ("2022 bear", "2022-01-01", "2022-12-31"), ("2023-26Apr", "2023-01-01", "2026-04-24")]


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_checksum(df: pd.DataFrame) -> str:
    """sha256 of the 10-dp rounded values with the ISO date index and fixed column order (portable)."""
    r = df.copy()
    r.index = [pd.Timestamp(i).date().isoformat() for i in r.index]
    txt = r.round(10).to_csv(float_format="%.10f", lineterminator="\n", na_rep="NaN")
    return hashlib.sha256(txt.encode()).hexdigest()


def block_of(dates: pd.DatetimeIndex) -> list[str]:
    out = [""] * len(dates)
    for name, a, b in BLOCKS:
        m = (dates >= pd.Timestamp(a)) & (dates <= pd.Timestamp(b))
        for i in np.where(m)[0]:
            out[i] = name
    return out
