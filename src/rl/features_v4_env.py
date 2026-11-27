"""Train/serve adapter for the v4.1 risk feature set (FH, certification M5, M10). NOT wired into training.

One store is built from the causal history (always starting at ORIGIN) and serves every consumer:
environment, training, backtest and prod. Row t of the panel depends only on history rows dated <= t (M1),
so reading row t from the shared store equals ``features_at(t, history)`` and does not depend on the
episode that asks for it (M3).

``build_state_v4(date, store, agent_state)`` = the 49 market/book features at ``date`` followed by the
agent's current equity share, and nothing else (M10: no NAV, no positions, no action history).

NaN policy (M4): an observation is returned only when every feature is past its warm-up. Inside warm-up
``build_state_v4`` raises ``WarmupError``; it never zero-fills (v2 imputed 0.0, which put fake zeros into
the z-score baselines). Episodes must start on or after ``first_full_date(store)``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.rl.features_risk_v4 import FEATURE_NAMES, ORIGIN, build_panel


class WarmupError(ValueError):
    """Raised when a requested date has at least one feature still inside its warm-up."""


class V4FeatureStore:
    """Causal, path-independent feature store over a history dict that starts at ORIGIN."""

    def __init__(self, history: dict):
        first = history["spy"].index.min()
        if first > ORIGIN:
            raise ValueError(f"history must start at ORIGIN {ORIGIN.date()}, got {first.date()} (NAV-reset guard)")
        self._panel = build_panel(history)[FEATURE_NAMES].astype(np.float64)

    @property
    def index(self) -> pd.DatetimeIndex:
        return self._panel.index

    def valid(self, date) -> bool:
        """True when every feature is past its warm-up at ``date``."""
        d = pd.Timestamp(date)
        if d not in self._panel.index:
            return False
        return bool(self._panel.loc[d].notna().all())

    def first_full_date(self) -> pd.Timestamp:
        """First trading day on which every feature is valid (earliest legal episode start)."""
        ok = self._panel.notna().all(axis=1)
        return ok[ok].index[0]

    def row(self, date) -> np.ndarray:
        d = pd.Timestamp(date)
        if d not in self._panel.index:
            raise KeyError(f"{d.date()} is not a trading day in the feature store")
        return self._panel.loc[d].to_numpy(dtype=np.float64, copy=True)


def build_state_v4(date, store: V4FeatureStore, agent_state: dict) -> np.ndarray:
    """Observation for a decision taken at the close of ``date``.

    agent_state: {"equity_share": e} with e in [0, 1], the agent's CURRENT equity share (M10). Any other
    key is rejected so that NAV, positions or actions cannot leak in by accident."""
    extra = set(agent_state) - {"equity_share"}
    if extra:
        raise KeyError(f"build_state_v4 accepts only equity_share from the agent, got {sorted(extra)}")
    e = float(agent_state["equity_share"])
    if not (0.0 <= e <= 1.0):
        raise ValueError(f"equity_share must be in [0, 1], got {e}")
    feats = store.row(date)
    if not np.isfinite(feats).all():
        bad = [FEATURE_NAMES[i] for i in np.where(~np.isfinite(feats))[0]]
        raise WarmupError(f"{pd.Timestamp(date).date()} is inside warm-up for {bad[:5]}{'...' if len(bad) > 5 else ''}")
    return np.concatenate([feats, [e]])


OBS_NAMES = list(FEATURE_NAMES) + ["equity_share"]
