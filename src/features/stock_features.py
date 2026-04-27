import pandas as pd
import numpy as np
from typing import Dict, Any
from src.features.base import BaseFeatureGenerator
import logging

logger = logging.getLogger(__name__)


class StockFeatureGenerator(BaseFeatureGenerator):
    def __init__(self, data_dict: Dict[str, pd.DataFrame], benchmark_ticker: str = "SPY", **kwargs: Any):
        super().__init__(data_dict, **kwargs)
        self.benchmark_ticker = benchmark_ticker

    def generate(self) -> pd.DataFrame:
        stock_tickers = [t for t in self.data_dict if t != self.benchmark_ticker]

        # ── Build wide price / volume matrices (dates × tickers) ────────────
        close_matrix = pd.DataFrame({
            t: self.data_dict[t]["adj_close"]
            for t in stock_tickers
            if "adj_close" in self.data_dict[t].columns
        }).sort_index()

        vol_matrix = pd.DataFrame({
            t: self.data_dict[t]["volume"]
            for t in stock_tickers
            if "volume" in self.data_dict[t].columns
        }).reindex(close_matrix.index)

        # Align columns (only tickers present in both)
        tickers = close_matrix.columns.intersection(vol_matrix.columns).tolist()
        close_matrix = close_matrix[tickers]
        vol_matrix = vol_matrix[tickers]

        # ── Benchmark series ─────────────────────────────────────────────────
        spy_returns = None
        if self.benchmark_ticker in self.data_dict:
            spy_adj = self.data_dict[self.benchmark_ticker]["adj_close"]
            spy_adj = spy_adj.reindex(close_matrix.index).ffill()
            spy_returns = spy_adj.pct_change()

        # ── Vectorised features (all tickers at once) ───────────────────────
        returns = close_matrix.pct_change()

        ret_1m  = close_matrix.pct_change(21)
        ret_3m  = close_matrix.pct_change(63)
        ret_6m  = close_matrix.pct_change(126)
        ret_12m = close_matrix.pct_change(252)
        ret_12m_ex_1m = close_matrix.shift(21).pct_change(231)

        ma50  = close_matrix.rolling(50).mean()
        ma200 = close_matrix.rolling(200).mean()
        above_50dma    = (close_matrix > ma50).astype(int)
        above_200dma   = (close_matrix > ma200).astype(int)
        ma_50_200_ratio = ma50 / ma200.replace(0, np.nan)

        high_52w = close_matrix.rolling(252).max()
        price_to_52w_high = close_matrix / high_52w.replace(0, np.nan)

        vol_21d = returns.rolling(21).std() * np.sqrt(252)
        vol_63d = returns.rolling(63).std() * np.sqrt(252)

        downside = returns.clip(upper=0)
        downside_vol_63d = downside.rolling(63).std() * np.sqrt(252)

        rolling_max_63 = close_matrix.rolling(63, min_periods=1).max()
        drawdown_63d = (close_matrix / rolling_max_63.replace(0, np.nan) - 1.0).rolling(63).min()

        avg_dv_63d = (close_matrix * vol_matrix).rolling(63).mean()

        # Beta and relative strength vs SPY
        if spy_returns is not None:
            spy_var = spy_returns.rolling(63).var()
            # rolling cov of each column vs spy
            beta_63d = returns.rolling(63).cov(spy_returns).div(
                spy_var.values.reshape(-1, 1), axis=0
            )
            rs_vs_spy = ret_3m.sub(spy_returns.pct_change(63), axis=0)
        else:
            beta_63d      = pd.DataFrame(1.0, index=close_matrix.index, columns=tickers)
            rs_vs_spy     = pd.DataFrame(0.0, index=close_matrix.index, columns=tickers)

        # ── Shift all features by 1 day (leakage guard) ─────────────────────
        feature_frames = {
            "ret_1m":                   ret_1m,
            "ret_3m":                   ret_3m,
            "ret_6m":                   ret_6m,
            "ret_12m":                  ret_12m,
            "ret_12m_ex_1m":            ret_12m_ex_1m,
            "above_50dma":              above_50dma,
            "above_200dma":             above_200dma,
            "ma_50_200_ratio":          ma_50_200_ratio,
            "price_to_52w_high":        price_to_52w_high,
            "volatility_21d":           vol_21d,
            "volatility_63d":           vol_63d,
            "downside_vol_63d":         downside_vol_63d,
            "max_drawdown_63d":         drawdown_63d,
            "avg_dollar_volume_63d":    avg_dv_63d,
            "beta_to_spy_63d":          beta_63d,
            "relative_strength_vs_spy_63d": rs_vs_spy,
        }

        shifted = {name: df.shift(1) for name, df in feature_frames.items()}

        # ── Stack to (date, ticker) MultiIndex ───────────────────────────────
        panel = pd.concat(
            {name: df for name, df in shifted.items()},
            axis=1
        )
        # panel columns: MultiIndex(feature, ticker)
        # Rearrange to (date, ticker) × feature
        panel = panel.stack(future_stack=True)   # → MultiIndex(date, ticker)
        panel.index.names = ["date", "ticker"]
        panel = panel.sort_index()

        # ── Cross-sectional liquidity rank ────────────────────────────────────
        panel["liquidity_rank"] = (
            panel.groupby(level="date")["avg_dollar_volume_63d"]
            .rank(pct=True)
        )

        logger.info(f"StockFeatureGenerator: {panel.shape[1]} features, "
                    f"{panel.index.get_level_values('ticker').nunique()} tickers, "
                    f"{panel.index.get_level_values('date').nunique()} dates")
        return panel
