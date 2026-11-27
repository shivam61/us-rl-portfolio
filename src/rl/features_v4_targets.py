"""Decision grids and forward targets for the v4 feature certification (v4.1, experiment FH).

Decision grids
  14d : biweekly decision dates from 2008-01-01 (same rule as H1's common.biweekly; reproduced exactly).
  8w  : the B.5 control dates (history _meta['control_dates']), i.e. the dates where the B.5 book changes.
Both grids are built from the SAME canonical daily unit-book series (history['unit_ret']), so the
targets of a date depend only on the book path between that date and the next decision date.

Targets (decision date d_i, period (d_i, d_{i+1}], daily unit-book returns u_t, no cash in the period):
  T1_mdd    : worst peak-to-trough drawdown of the NAV path starting at 1.0 at d_i (<= 0).
  T2_vol    : annualised std of daily returns in the period (ddof 1).
  T3_ret    : compounded return over the period.
  T4_sign   : 1 if T3_ret > 0, else 0.
  T5_regret : U(e*) - U(0.72), where U(e) = sum_t log(1 + e * u_t) is the realised log utility of holding
              equity share e (cash return 0; no cash-rate series exists in the library) over the period, e
              taken from the grid SHARES = (0, 0.25, 0.5, 0.72, 1.0), and e* = argmax U(e). Always >= 0.
  T5_call   : sign(e* - 0.72) in {-1, 0, +1}: the direction of the best-share call (ties resolve to 0.72).
  T5_signed : T5_call * T5_regret, the signed regret (sign = direction of the call, magnitude = utility gap).
The last decision has no following period and is NaN for every target. A period containing any NaN daily
return gives NaN targets (never zero-filled).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

START = pd.Timestamp("2008-01-01")
END = pd.Timestamp("2026-04-24")  # end of the certified materialised window (sealed holdout starts 2026-05-01)
SHARES = (0.0, 0.25, 0.5, 0.72, 1.0)
STATIC_SHARE = 0.72
TARGET_COLS = ["T1_mdd", "T2_vol", "T3_ret", "T4_sign", "T5_regret", "T5_call", "T5_signed"]


def biweekly_dates(prices_index: pd.DatetimeIndex, start=START, stop=END) -> list[pd.Timestamp]:
    """Same rule as runs_h1 common.biweekly: every 14 calendar days from start, snapped forward to the
    next trading day, de-duplicated."""
    idx = prices_index[(prices_index >= start) & (prices_index <= stop)]
    out, last = [], None
    for t in pd.date_range(start, stop, freq="14D"):
        p = idx.searchsorted(t)
        if p >= len(idx):
            break
        if idx[p] != last:
            out.append(idx[p])
            last = idx[p]
    return out


def grid_dates(name: str, control_dates, prices_index) -> list[pd.Timestamp]:
    if name == "14d":
        return biweekly_dates(prices_index)
    if name == "8w":
        return [pd.Timestamp(d) for d in control_dates if START <= pd.Timestamp(d) <= END]
    raise ValueError(name)


def period_targets(u: pd.Series, t0: pd.Timestamp, t1: pd.Timestamp) -> dict:
    """Targets for the period (t0, t1] from the daily unit-book return series u (NaN-aware)."""
    nan = {k: np.nan for k in TARGET_COLS}
    s = u[(u.index > t0) & (u.index <= t1)]
    if len(s) == 0 or s.isna().any():
        return nan
    x = s.values.astype(float)
    nav = np.concatenate([[1.0], np.cumprod(1.0 + x)])
    R = nav[-1] - 1.0
    mdd = float(np.min(nav / np.maximum.accumulate(nav) - 1.0))
    vol = float(np.std(x, ddof=1) * np.sqrt(252)) if len(x) > 1 else np.nan
    util = {e: float(np.sum(np.log1p(e * x))) for e in SHARES}
    best = max(SHARES, key=lambda e: (util[e], -abs(e - STATIC_SHARE)))
    regret = util[best] - util[STATIC_SHARE]
    call = float(np.sign(best - STATIC_SHARE))
    return dict(T1_mdd=mdd, T2_vol=vol, T3_ret=R, T4_sign=float(R > 0), T5_regret=float(regret),
                T5_call=call, T5_signed=float(call * regret))


def targets_for_grid(u: pd.Series, dates) -> pd.DataFrame:
    """One row per decision date. The last decision gets NaN (no following period)."""
    dates = list(pd.DatetimeIndex(dates))
    rows = []
    for i, t in enumerate(dates):
        if i + 1 >= len(dates):
            rows.append(dict(date=t, **{k: np.nan for k in TARGET_COLS}))
        else:
            rows.append(dict(date=t, **period_targets(u, t, dates[i + 1])))
    return pd.DataFrame(rows).set_index("date")[TARGET_COLS]
