"""Contextual-bandit experiment BD (docs/phases/rl_bandit_plan.md): shared core.

Decision problem (spec section 2):
- Decision at close d (B.5 control dates for the 8w grid; the 14d grid restricted to dates on or
  after the first B.5 snapshot, fixing A0 D1). The book in force at d is the B.5+B.4 unit book
  u_d (unit weights summing to 1), read from the H1 history `unit_w` (piecewise constant between
  control dates; verified in tests).
- Fill at close d + FILL_LAG (spec: 1 trading day). The position a*u_d is held (daily rebalanced
  to fixed weights, as the env does) until the next decision's fill, and the terminal date.
- Cost: 10 bps per unit turnover, turnover = sum |a*u_d - p*u_prev| with p the previous share,
  charged on the first day return of the period (env formula r' = (1-c)(1+r)-1).
- Period outcome R(d,a,p) = net return over the fill days; U1 = log(1 + R).

Everything is computed from unit-book prices (`stocks` in the H1 history). The env equivalence is
tested in tests/test_bd_outcome_table.py (fill lag 0 reproduces PortfolioEnvV2 to 1e-6).

Sealed window: every series is cut at TERMINAL (2026-04-24, the legacy holdout end). Nothing
dated after TERMINAL is read into any statistic.
"""
from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = REPO_ROOT / "runs_bd" / "inputs"
OUT_DIR = REPO_ROOT / "runs_bd"

ANN = 252
COST_BPS = 10.0
FILL_LAG = 1  # spec: decision at close t, fill at close t+1
TERMINAL = pd.Timestamp("2026-04-24")
FIRST_SNAPSHOT = pd.Timestamp("2008-01-07")
CTX_MIN_OBS = 126  # expanding z-score warm-up (same convention as FM / FH)

ARMS_PRIMARY = (0.25, 0.4375, 0.625, 0.8125, 1.0)
ARMS_FLOOR05 = (0.5, 0.625, 0.75, 0.875, 1.0)  # sensitivity: 0.5-floor arm set
ARMS_3 = (0.25, 0.625, 1.0)  # BD4 sensitivity
ARMS_9 = tuple(round(0.25 + k * 0.09375, 8) for k in range(9))  # BD4 sensitivity
ARMS_UNION = tuple(sorted({*ARMS_PRIMARY, *ARMS_FLOOR05, *ARMS_3, *ARMS_9}))
WINDOW_2020 = ("2020-02-19", "2020-06-30")
WINDOW_2022 = ("2022-01-03", "2022-12-30")


# ----------------------------------------------------------------------------- data
def load_history() -> dict:
    """H1 unit-book history, cut at TERMINAL. Only the keys used here are kept."""
    h = pickle.load(open(INPUT_DIR / "history_v41.pkl", "rb"))
    cut = lambda s: s.loc[s.index <= TERMINAL]  # noqa: E731
    out = {
        "unit_w": h["unit_w"].loc[h["unit_w"].index <= TERMINAL],
        "stocks": h["stocks"].loc[h["stocks"].index <= TERMINAL],
        "unit_ret": cut(h["unit_ret"]),
        "base_ret": cut(h["base_ret"]),
        "spy": cut(h["spy"]),
        "vix": cut(h["vix"]),
        "stress": cut(h["stress"]),
    }
    assert out["unit_w"].index.max() <= TERMINAL
    return out


def stock_returns(prices: pd.DataFrame, cols) -> np.ndarray:
    """Daily stock returns as the env computes them (pct_change, NaN -> 0), columns = cols."""
    r = prices.pct_change(fill_method=None).fillna(0.0)
    return r.reindex(columns=list(cols)).fillna(0.0).values


def control_dates(unit_w: pd.DataFrame) -> pd.DatetimeIndex:
    """Dates where the B.5 book snapshot changes (the 8w grid)."""
    w = unit_w.fillna(0.0)
    chg = w.diff().abs().sum(axis=1) > 1e-12
    chg.iloc[0] = w.iloc[0].abs().sum() > 1e-12
    d = w.index[chg.values]
    return pd.DatetimeIndex(d[d >= FIRST_SNAPSHOT])


def decision_dates(name: str, h: dict) -> pd.DatetimeIndex:
    """'8w': B.5 control dates. '14d': existing 14d grid on or after the first B.5 snapshot."""
    if name == "8w":
        return control_dates(h["unit_w"])
    if name == "14d":
        g = pd.read_parquet(INPUT_DIR / "grid_14d_v4.parquet").index
        g = pd.DatetimeIndex(g)
        return g[(g >= FIRST_SNAPSHOT) & (g <= TERMINAL)]
    raise ValueError(name)


# ----------------------------------------------------------------------------- grid
@dataclass
class Grid:
    name: str
    dates: pd.DatetimeIndex  # decision closes
    dpos: np.ndarray  # positions in calendar
    fill_pos: np.ndarray  # dpos + lag
    end_pos: np.ndarray  # last day (inclusive) of each period
    book: np.ndarray  # N x S unit weights in force at each decision
    s_days: list  # per period: book daily returns on the period days (unit weights)
    q_dates: list  # per period: dates of the period days
    cols: list
    fill_lag: int = FILL_LAG

    @property
    def n(self) -> int:
        return len(self.dates)


def build_grid(name: str, h: dict, fill_lag: int = FILL_LAG, terminal: pd.Timestamp = TERMINAL) -> Grid:
    uw = h["unit_w"]
    cols = list(uw.columns)
    cal = pd.DatetimeIndex(h["unit_ret"].index)
    dates = decision_dates(name, h)
    dpos = cal.get_indexer(dates)
    assert (dpos >= 0).all(), "decision date missing from calendar"
    term_pos = int(cal.searchsorted(terminal, side="right") - 1)
    fill = dpos + fill_lag
    keep = fill < term_pos  # decisions whose fill is at or after the terminal date have no period
    dates, dpos, fill = dates[keep], dpos[keep], fill[keep]
    n = len(dates)
    end = np.empty(n, dtype=int)
    end[:-1] = fill[1:]
    end[-1] = term_pos
    book = uw.reindex(index=dates, columns=cols).fillna(0.0).values
    rets_cal = pd.DataFrame(
        stock_returns(h["stocks"], cols), index=h["stocks"].index
    ).reindex(cal).fillna(0.0).values  # T x S on the calendar, NaN -> 0 as in the env
    s_days, q_dates = [], []
    for i in range(n):
        q = np.arange(fill[i] + 1, end[i] + 1)
        assert len(q) >= 1, f"empty period at decision {dates[i]}"
        s_days.append(rets_cal[q] @ book[i])
        q_dates.append(cal[q])
    return Grid(name=name, dates=dates, dpos=dpos, fill_pos=fill, end_pos=end, book=book,
                s_days=s_days, q_dates=q_dates, cols=cols, fill_lag=fill_lag)


# ----------------------------------------------------------------------------- engine
def period_returns(g: Grid, i: int, a: float, p: float, bps: float = COST_BPS):
    """Net daily returns of period i with share a, previous share p. Returns (daily, turnover)."""
    prev = p * g.book[i - 1] if (i > 0 and p > 0) else 0.0
    turn = float(np.abs(a * g.book[i] - prev).sum())
    r = a * g.s_days[i]
    r = r.copy()
    if turn > 0 and r.size:
        r[0] = (1.0 - bps / 1e4 * turn) * (1.0 + r[0]) - 1.0
    return r, turn


def wealth_stats(r: np.ndarray) -> dict:
    r = np.asarray(r, dtype=float)
    n = len(r)
    if n == 0:
        return {"R": np.nan, "MaxDD": np.nan, "vol": np.nan, "n": 0}
    w = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(np.concatenate([[1.0], w]))[1:]
    mdd = float(np.min(w / peak - 1.0))
    vol = float(np.std(r, ddof=1) * np.sqrt(ANN)) if n > 1 else np.nan
    return {"R": float(w[-1] - 1.0), "MaxDD": mdd, "vol": vol, "n": n}


def path_stats(r: np.ndarray) -> dict:
    """Metrics of a daily path (repo convention: Sharpe = CAGR/vol, Sortino = CAGR/downside vol)."""
    r = np.asarray(r, dtype=float)
    r = r[np.isfinite(r)]
    n = len(r)
    if n < 21:
        return {k: np.nan for k in ["CAGR", "MaxDD", "vol", "Sharpe", "Sortino", "Calmar", "n_days"]}
    nav = np.cumprod(1.0 + r)
    yrs = n / ANN
    cagr = float(nav[-1] ** (1.0 / yrs) - 1.0)
    peak = np.maximum.accumulate(np.concatenate([[1.0], nav]))[1:]
    mdd = float(np.min(nav / peak - 1.0))
    vol = float(np.std(r, ddof=1) * np.sqrt(ANN))
    dd = float(np.sqrt(np.mean(np.minimum(r, 0.0) ** 2)) * np.sqrt(ANN))
    return {
        "CAGR": cagr,
        "MaxDD": mdd,
        "vol": vol,
        "Sharpe": cagr / vol if vol > 0 else np.nan,
        "Sortino": cagr / dd if dd > 0 else np.nan,
        "Calmar": cagr / abs(mdd) if mdd < 0 else np.nan,
        "n_days": n,
    }


def window_mdd(r: np.ndarray, dates: pd.DatetimeIndex, start: str, end: str) -> float:
    m = (dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))
    x = np.asarray(r)[m]
    if len(x) < 2:
        return np.nan
    return wealth_stats(x)["MaxDD"]


def run_shares(g: Grid, idx, shares, p0: float = 0.0, bps: float = COST_BPS, edge_fn=None) -> dict:
    """Evaluate a share sequence over decision positions idx (previous-share chain starts at p0).

    Per-period lists: daily net returns, period dates, decision dates, shares, turnover, R, U1, n_days.
    Use `flatten(res)` for the daily path arrays. edge_fn(i, a) -> log-utility edge added to a period
    (planted-signal controls only; the period's log(1+R) increases by exactly the edge)."""
    idx = np.asarray(idx, dtype=int)
    shares = np.asarray(shares, dtype=float)
    out = {k: [] for k in ["daily", "period_dates", "turn", "R", "U1", "n_days"]}
    p = p0
    for k, i in enumerate(idx):
        a = float(shares[k])
        r, t = period_returns(g, i, a, p, bps)
        if edge_fn is not None and r.size:
            r = (1.0 + r) * np.exp(edge_fn(i, a) / r.size) - 1.0
        ws = wealth_stats(r)
        out["daily"].append(r)
        out["period_dates"].append(np.asarray(g.q_dates[i]))
        out["turn"].append(t)
        out["R"].append(ws["R"])
        out["U1"].append(np.log1p(ws["R"]))
        out["n_days"].append(len(r))
        p = a
    res = {k: (np.asarray(v) if k in ("turn", "R", "U1", "n_days") else v) for k, v in out.items()}
    res["idx"] = idx
    res["shares"] = shares
    res["dec_dates"] = pd.DatetimeIndex(g.dates[idx])
    res["share_period"] = [np.full(len(r), a) for r, a in zip(out["daily"], shares)]
    return res


def subset(res: dict, mask: np.ndarray) -> dict:
    """Keep periods where mask is True (per-period mask)."""
    mask = np.asarray(mask, dtype=bool)
    out = {}
    for k, v in res.items():
        if isinstance(v, list):
            out[k] = [x for x, m in zip(v, mask) if m]
        elif isinstance(v, np.ndarray) and len(v) == len(mask):
            out[k] = v[mask]
        elif isinstance(v, pd.DatetimeIndex) and len(v) == len(mask):
            out[k] = v[mask]
        else:
            out[k] = v
    return out


def flatten(res: dict):
    """(daily returns, dates, share per day) concatenated over periods."""
    daily = np.concatenate([np.asarray(x) for x in res["daily"]]) if len(res["daily"]) else np.array([])
    dates = pd.DatetimeIndex(np.concatenate([np.asarray(x) for x in res["period_dates"]]))
    share = np.concatenate([np.asarray(x) for x in res["share_period"]])
    return daily, dates, share


def flat(daily_list) -> np.ndarray:
    return np.concatenate([np.asarray(x) for x in daily_list]) if len(daily_list) else np.array([])


# ----------------------------------------------------------------------------- contexts
def _expanding_z(x: pd.Series) -> pd.Series:
    mu = x.expanding(min_periods=CTX_MIN_OBS).mean()
    sd = x.expanding(min_periods=CTX_MIN_OBS).std()
    return (x - mu) / sd.where(sd > 1e-12)


def x0_daily(h: dict) -> pd.DataFrame:
    """X0 (6 dims) on the calendar, causal: value at t uses data dated <= t only.

    vol_book_21, vol_book_63: log annualised realised vol of the unit-book returns.
    base_dd: magnitude of the baseline-book drawdown from its running peak (continuous, since inception).
    spy_dd: magnitude of the SPY drawdown from its running peak.
    vix_rank: trailing 252-day percentile rank of VIX.
    stress: B.5 stress score in force.
    Each is standardised by an expanding z-score (min 126 obs). Warm-up rows are NaN.
    """
    ur = h["unit_ret"]
    vol21 = ur.rolling(21, min_periods=21).std() * np.sqrt(ANN)
    vol63 = ur.rolling(63, min_periods=63).std() * np.sqrt(ANN)
    br = h["base_ret"].fillna(0.0)
    bw = (1.0 + br).cumprod()
    base_dd = -(bw / bw.cummax() - 1.0)
    sp = h["spy"]
    spy_dd = -(sp / sp.cummax() - 1.0)
    vix_rank = h["vix"].rolling(252, min_periods=252).rank(pct=True)
    raw = pd.DataFrame(
        {
            "vol_book_21": np.log(vol21.where(vol21 > 0)),
            "vol_book_63": np.log(vol63.where(vol63 > 0)),
            "base_dd": base_dd,
            "spy_dd": spy_dd,
            "vix_rank": vix_rank,
            "stress": h["stress"],
        }
    )
    raw = raw.loc[raw.index <= TERMINAL]
    z = raw.apply(_expanding_z)
    return z


X0_COLS = ["vol_book_21", "vol_book_63", "base_dd", "spy_dd", "vix_rank", "stress"]


# ----------------------------------------------------------------------------- outcome table
def outcome_table(g: Grid, arms=ARMS_UNION, prevs=None, bps: float = COST_BPS) -> pd.DataFrame:
    """Long table of R(d,a,p) for every decision d, arm a and previous share p (p=0 means no position)."""
    prevs = (0.0,) + tuple(arms) if prevs is None else tuple(prevs)
    rows = []
    for i in range(g.n):
        for a in arms:
            for p in prevs:
                r, t = period_returns(g, i, a, p, bps)
                rg, _ = period_returns(g, i, a, p, 0.0)
                ws = wealth_stats(r)
                rows.append((
                    g.dates[i], g.q_dates[i][0], g.q_dates[i][-1], ws["n"], a, p,
                    ws["R"], float(np.prod(1.0 + rg) - 1.0), float(np.log1p(ws["R"])),
                    ws["MaxDD"], ws["vol"], t,
                ))
    cols = ["decision_date", "period_start", "period_end", "n_days", "arm", "prev_share",
            "R_net", "R_gross", "U1", "MaxDD", "vol", "turnover"]
    df = pd.DataFrame(rows, columns=cols)
    df.insert(0, "grid", g.name)
    return df
