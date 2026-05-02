"""Phase D.2 — Sector tilt application (10-step sequence).

RL action (12-dim raw ∈ [−1,+1]) → valid weight vector.
  action[0:11] = sector tilts → mapped to [−per_sector_cap, +per_sector_cap]
  action[11]   = aggressiveness → mapped to [aggressiveness_floor, 1.0]

10-step sequence:
  1. Split b5_weights into stock sleeve and trend sleeve.
  2. Compute base_sector_weight[i] = sum of stock-sleeve weights per sector.
  3. Map raw_action[0:11] → tilts clipped to [−per_sector_cap, +per_sector_cap].
  4. Budget: if Σ|tilt| > total_budget → rescale proportionally.
  5. Zero-sum: tilt -= mean(tilt).
  6. tilted_sector[i] = max(0, base_sector_weight[i] + tilt[i]).
  7. Re-normalise: tilted_sector *= sum(base) / sum(tilted_sector).
  8. Within-sector redistribution: proportional to original B.5 weights.
  9. Aggressiveness: map action[11] → [aggressiveness_floor, 1.0]; scale stock sleeve.
 10. Recombine with frozen trend sleeve; cash absorbs the aggressiveness gap.
     (Caller applies apply_b4_constraints as hard floor.)

Invariants (verified by unit tests):
  - After step 5: sum(tilts) ≈ 0
  - After step 7: sum(tilted_sector) ≈ sum(base_sector_weights)
  - After step 8: sum(all stock weights) ≈ sum(tilted_sector)
  - After step 9: sum(stock_sleeve_final) ≤ sum(tilted_sector)
  - Final gross ≤ B.5 gross (aggressiveness ≤ 1.0; trend sleeve frozen)
"""
import numpy as np
import pandas as pd

from src.rl.state_builder import SECTOR_ORDER, TREND_ASSETS


def apply_sector_tilts(
    b5_weights: pd.Series,
    ticker_to_sector: dict[str, str],
    trend_tickers: list[str],
    sector_order: list[str] | None = None,
    raw_action: np.ndarray | None = None,
    per_sector_cap: float = 0.15,
    total_budget: float = 0.35,
    aggressiveness_floor: float = 0.75,
) -> pd.Series:
    """Apply RL action to B.5 weights using the 10-step tilt sequence.

    Args:
        b5_weights: Full B.5 constrained weights at this rebalance date (pd.Series, index=tickers).
        ticker_to_sector: Maps stock ticker → sector ETF (e.g., "MMM" → "XLI").
        trend_tickers: Tickers that belong to the frozen trend sleeve (TLT, GLD, UUP, SPY).
        sector_order: Canonical 11-sector ordering. Defaults to SECTOR_ORDER.
        raw_action: shape (12,); raw ∈ [−1, +1]. If None, returns B.5 weights unchanged.
        per_sector_cap: Max absolute tilt per sector (default 0.15).
        total_budget: Max Σ|tilt| across all sectors (default 0.35).
        aggressiveness_floor: Minimum stock-sleeve scale factor (default 0.75).

    Returns:
        pd.Series of final weights (stock sleeve tilted + trend frozen + cash gap).
        The series index matches b5_weights.index plus a "_cash" entry for any residual.
    """
    if sector_order is None:
        sector_order = SECTOR_ORDER

    trend_set = set(trend_tickers) | TREND_ASSETS

    # --- Step 1: Split into stock sleeve and trend sleeve ---
    w = b5_weights.dropna()
    trend_slice = w[w.index.isin(trend_set)]
    stock_slice = w[~w.index.isin(trend_set)]

    # No-op: return B.5 weights if action is None
    if raw_action is None:
        return b5_weights.copy()

    raw_action = np.asarray(raw_action, dtype=float)
    assert raw_action.shape == (12,), f"raw_action must be shape (12,), got {raw_action.shape}"

    # --- Step 2: Base sector weights ---
    base_sector = np.zeros(len(sector_order), dtype=float)
    for i, sec in enumerate(sector_order):
        tickers_in_sec = [t for t in stock_slice.index if ticker_to_sector.get(t) == sec]
        base_sector[i] = float(stock_slice.reindex(tickers_in_sec).fillna(0.0).sum())

    stock_total = float(base_sector.sum())

    # --- Step 3: Map raw_action[0:11] → tilts clipped to [−cap, +cap] ---
    tilts = np.clip(raw_action[:11] * per_sector_cap, -per_sector_cap, per_sector_cap)

    # --- Step 4: Budget enforcement ---
    total_abs = float(np.sum(np.abs(tilts)))
    if total_abs > total_budget and total_abs > 1e-12:
        tilts = tilts * (total_budget / total_abs)

    # --- Step 5: Zero-sum enforcement ---
    tilts = tilts - tilts.mean()

    # --- Step 6: Apply tilts; floor at 0 ---
    tilted_sector = np.maximum(0.0, base_sector + tilts)

    # --- Step 7: Re-normalise to preserve stock-sleeve total ---
    tilted_sum = float(tilted_sector.sum())
    if tilted_sum > 1e-12:
        tilted_sector = tilted_sector * (stock_total / tilted_sum)
    else:
        tilted_sector = base_sector.copy()

    # --- Step 8: Within-sector redistribution (proportional to B.5 weights) ---
    new_stock_weights = pd.Series(0.0, index=stock_slice.index)
    for i, sec in enumerate(sector_order):
        tickers_in_sec = [t for t in stock_slice.index if ticker_to_sector.get(t) == sec]
        if not tickers_in_sec:
            continue
        orig_sec_weights = stock_slice.reindex(tickers_in_sec).fillna(0.0)
        orig_sec_total = float(orig_sec_weights.abs().sum())
        if orig_sec_total < 1e-12:
            continue
        new_stock_weights[tickers_in_sec] = orig_sec_weights * (tilted_sector[i] / orig_sec_total)

    # --- Step 9: Aggressiveness scaling ---
    agg_raw = float(raw_action[11])
    aggressiveness = aggressiveness_floor + (1.0 - aggressiveness_floor) * (agg_raw + 1.0) / 2.0
    aggressiveness = float(np.clip(aggressiveness, aggressiveness_floor, 1.0))
    stock_final = new_stock_weights * aggressiveness

    # --- Step 10: Recombine with frozen trend sleeve; cash = aggressiveness gap ---
    result = pd.Series(0.0, index=b5_weights.index)
    for t in trend_slice.index:
        if t in result.index:
            result[t] = float(trend_slice[t])
    for t in stock_final.index:
        if t in result.index:
            result[t] = float(stock_final[t])

    return result
