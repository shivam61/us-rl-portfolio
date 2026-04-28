from __future__ import annotations

import logging
from collections.abc import Callable

import pandas as pd

logger = logging.getLogger(__name__)

VOL_FEATURES_ASCENDING = [
    "volatility_63d",
    "downside_vol_63d",
    "beta_to_spy_63d",
]

VOL_FEATURES_DESCENDING = [
    "max_drawdown_63d",
]


def compute_volatility_score_frame(panel: pd.DataFrame) -> pd.DataFrame:
    """Build the production volatility alpha sleeve from lagged stock features."""
    avail_vol_asc = [c for c in VOL_FEATURES_ASCENDING if c in panel.columns]
    avail_vol_dsc = [c for c in VOL_FEATURES_DESCENDING if c in panel.columns]

    expected = set(VOL_FEATURES_ASCENDING) | set(VOL_FEATURES_DESCENDING)
    available = set(avail_vol_asc) | set(avail_vol_dsc)
    missing = expected - available
    if missing:
        logger.warning("volatility_score missing features: %s", ", ".join(sorted(missing)))

    rank_frames: list[pd.Series] = []
    for col in avail_vol_asc:
        rank_frames.append(
            panel.groupby(level="date")[col].rank(ascending=True, pct=True).rename(f"rank_{col}")
        )
    for col in avail_vol_dsc:
        rank_frames.append(
            panel.groupby(level="date")[col].rank(ascending=False, pct=True).rename(f"rank_{col}")
        )

    result = pd.DataFrame(index=panel.index)
    if not rank_frames:
        result["volatility_score"] = pd.Series(float("nan"), index=panel.index)
    else:
        result["volatility_score"] = pd.concat(rank_frames, axis=1).mean(axis=1)
    result["volatility_score_rank"] = result.groupby(level="date")["volatility_score"].rank(pct=True)
    return result


def build_alpha_score_provider(
    score_frame: pd.DataFrame,
    score_col: str = "volatility_score",
) -> Callable[[pd.Timestamp, list[str], object], pd.Series]:
    if score_col not in score_frame.columns:
        raise KeyError(f"{score_col} not found in score frame")

    def _provider(signal_date: pd.Timestamp, active_tickers: list[str], engine: object) -> pd.Series:
        idx = score_frame.index.levels[0].get_indexer([signal_date], method="ffill")[0]
        if idx < 0:
            return pd.Series(dtype=float)
        feature_date = score_frame.index.levels[0][idx]
        latest = score_frame.xs(feature_date, level="date")
        return latest.reindex(active_tickers)[score_col].dropna()

    return _provider
