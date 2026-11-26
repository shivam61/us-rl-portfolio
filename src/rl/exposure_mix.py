"""Phase E.2 — Target-proportion action space with simplex projection.

RL outputs raw_action ∈ [−1, +1]^3 = [raw_equity, raw_trend, raw_cash].

These are mapped to target proportions (equity, trend, cash) that:
  - sum exactly to 1.0
  - satisfy: equity ∈ [0.25, 1.00], trend ∈ [0.00, 1.00], cash ∈ [0.00, 0.50]

E.7 change: cash cap tightened from 0.60 → 0.50. Equity floor unchanged at 0.25.
The within-sleeve proportions (vol_score stock weights and TLT/GLD/UUP weights)
are preserved; the RL only sets the sleeve-level exposure fractions.
"""
import numpy as np
import pandas as pd

# Box constraints for each proportion component
_EQ_MIN, _EQ_MAX = 0.25, 1.00
_TR_MIN, _TR_MAX = 0.00, 1.00
_CA_MIN, _CA_MAX = 0.00, 0.50  # E.7: tightened from 0.60

# Equity-only policy: these are never bought. TLT/GLD/UUP are state signals only; SPY is the benchmark.
NON_TRADABLE_ASSETS = ("GLD", "SPY", "TLT", "UUP")

# Fallback allocation when raw_action sums to near zero
_FALLBACK = (0.85, 0.10, 0.05)


def _project_to_simplex(eq: float, tr: float, ca: float) -> tuple[float, float, float]:
    """Project (eq, tr, ca) onto the constrained simplex sum=1 with box constraints.

    Algorithm (5 steps):
      1. Normalize proportionally to sum=1.
      2. Clip to box constraints.
      3. Distribute residual to the component with the most room.
      4. Re-clip.
      5. Final normalize to sum=1 (handles floating-point drift).
    """
    total = eq + tr + ca
    if total < 1e-12:
        return _FALLBACK

    # Step 1 — proportional normalize
    eq, tr, ca = eq / total, tr / total, ca / total

    # Step 2 — clip to box
    eq = float(np.clip(eq, _EQ_MIN, _EQ_MAX))
    tr = float(np.clip(tr, _TR_MIN, _TR_MAX))
    ca = float(np.clip(ca, _CA_MIN, _CA_MAX))

    # Step 3 — single redistribution of residual (one pass)
    residual = 1.0 - (eq + tr + ca)
    if abs(residual) > 1e-9:
        # Room = distance to far bound for each component
        rooms = [
            (_EQ_MAX - eq, 0),
            (_TR_MAX - tr, 1),
            (_CA_MAX - ca, 2),
        ]
        rooms.sort(key=lambda x: -x[0])  # most room first
        components = [eq, tr, ca]
        for room, idx in rooms:
            add = min(residual, room) if residual > 0 else max(residual, -components[idx] + [_EQ_MIN, _TR_MIN, _CA_MIN][idx])
            components[idx] += add
            residual -= add
            if abs(residual) < 1e-9:
                break
        eq, tr, ca = components

    # Step 4 — re-clip
    eq = float(np.clip(eq, _EQ_MIN, _EQ_MAX))
    tr = float(np.clip(tr, _TR_MIN, _TR_MAX))
    ca = float(np.clip(ca, _CA_MIN, _CA_MAX))

    # Step 5 — final normalize
    total = eq + tr + ca
    if total < 1e-12:
        return _FALLBACK
    eq, tr, ca = eq / total, tr / total, ca / total
    return eq, tr, ca


def project_two_sleeve(raw_eq: float, raw_ca: float) -> tuple[float, float]:
    """Equity-only policy: the agent splits the WHOLE book between equity and cash.

    raw in [-1,+1]^2 -> equity share = eq/(eq+ca) of two box-mapped scores, cash = 1 - equity,
    with cash <= _CA_MAX. No third sleeve exists, so nothing is decided for the agent.
    """
    eq_s = _EQ_MIN + (_EQ_MAX - _EQ_MIN) * (raw_eq + 1.0) / 2.0
    ca_s = _CA_MIN + (_CA_MAX - _CA_MIN) * (raw_ca + 1.0) / 2.0
    eq = eq_s / (eq_s + ca_s)
    ca = min(1.0 - eq, _CA_MAX)
    return 1.0 - ca, ca


def apply_two_sleeve_mix(
    b5_weights: pd.Series,
    trend_tickers: list[str],
    raw_action: np.ndarray,
) -> tuple[pd.Series, dict]:
    """2-dim action [raw_equity, raw_cash]: stock weights are rescaled to the equity share;
    the rest is cash. trend_tickers (if any exist in b5_weights) are ignored/zeroed."""
    raw_action = np.asarray(raw_action, dtype=float)
    eq, ca = project_two_sleeve(float(raw_action[0]), float(raw_action[1]))
    trend_set = set(trend_tickers)
    result = pd.Series(0.0, index=b5_weights.index)
    stock_slice = b5_weights[[t for t in b5_weights.index if t not in trend_set]]
    stock_total = float(stock_slice.abs().sum())
    if stock_total > 1e-12:
        result[stock_slice.index] = stock_slice * (eq / stock_total)
    info = {"equity_frac": float(eq), "trend_frac": 0.0, "cash_frac": float(ca),
            "gross": float(result.abs().sum())}
    return result, info


def apply_exposure_mix(
    b5_weights: pd.Series,
    trend_tickers: list[str],
    raw_action: np.ndarray,
) -> tuple[pd.Series, dict]:
    """Convert a 3-dim raw RL action to a valid portfolio weight vector.

    Steps:
      1. Map raw ∈ [−1,+1]^3 to initial proportions within box constraints.
      2. Project to simplex: equity + trend + cash = 1.0.
      3. Scale equity sleeve (preserving within-sleeve vol_score proportions).
      4. Scale trend sleeve (preserving within-sleeve TLT/GLD/UUP proportions).
      5. Gross cap check (max gross ≤ 1.5).

    Args:
        b5_weights: B.5 constrained weight vector at current rebalance date.
        trend_tickers: List of trend sleeve tickers (e.g. ["TLT", "GLD", "UUP"]).
        raw_action: Shape (3,), values in [−1, +1] = [raw_equity, raw_trend, raw_cash].

    Returns:
        result: pd.Series of portfolio weights (cash is implicit residual 1 − sum).
        info: dict with keys equity_frac, trend_frac, cash_frac, gross.
    """
    raw_action = np.asarray(raw_action, dtype=float)
    if raw_action.shape == (2,):
        return apply_two_sleeve_mix(b5_weights, trend_tickers, raw_action)
    assert raw_action.shape == (3,), f"Expected action shape (2,) or (3,), got {raw_action.shape}"

    raw_eq, raw_tr, raw_ca = float(raw_action[0]), float(raw_action[1]), float(raw_action[2])

    # Step 1 — map raw [−1,+1] to box proportions
    eq_init = _EQ_MIN + (_EQ_MAX - _EQ_MIN) * (raw_eq + 1.0) / 2.0
    tr_init = _TR_MIN + (_TR_MAX - _TR_MIN) * (raw_tr + 1.0) / 2.0
    ca_init = _CA_MIN + (_CA_MAX - _CA_MIN) * (raw_ca + 1.0) / 2.0

    # Step 2 — project to simplex with box constraints
    eq, tr, ca = _project_to_simplex(eq_init, tr_init, ca_init)

    trend_set = set(trend_tickers)
    result = pd.Series(0.0, index=b5_weights.index)

    # Step 3 — scale equity sleeve
    stock_slice = b5_weights[[t for t in b5_weights.index if t not in trend_set]]
    stock_total = float(stock_slice.abs().sum())
    if stock_total > 1e-12:
        result[stock_slice.index] = stock_slice * (eq / stock_total)

    # Step 4 — scale trend sleeve
    trend_slice = b5_weights[[t for t in b5_weights.index if t in trend_set]]
    trend_total = float(trend_slice.abs().sum())
    if trend_total > 1e-12:
        result[trend_slice.index] = trend_slice * (tr / trend_total)
    # If trend_total == 0 (no trend sleeve in this snapshot), cash absorbs the shortfall.

    # Step 5 — gross cap (max gross ≤ 1.5)
    gross = float(result.abs().sum())
    if gross > 1.5:
        result = result * (1.5 / gross)
        gross = 1.5

    info = {
        "equity_frac": float(eq),
        "trend_frac":  float(tr),
        "cash_frac":   float(ca),
        "gross":       float(result.abs().sum()),
    }
    return result, info


def finalize_equity_only(mixed_weights: pd.Series, equity_frac: float, tol: float = 1e-6) -> pd.Series:
    """Equity-only finalisation shared by the training env and production.

    Drops every non-tradable column and applies NO beta projection, so the stock weights sum
    to exactly the agent's equity share and the rest is cash. Raises if that invariant breaks.
    """
    w = mixed_weights.drop(labels=[c for c in NON_TRADABLE_ASSETS if c in mixed_weights.index]).fillna(0.0)
    gap = abs(float(w.abs().sum()) - float(equity_frac))
    if gap > tol and float(mixed_weights.abs().sum()) > 1e-12:
        raise AssertionError(f"equity-only invariant broken: stock sum {w.abs().sum():.6f} != equity_frac {equity_frac:.6f}")
    return w
