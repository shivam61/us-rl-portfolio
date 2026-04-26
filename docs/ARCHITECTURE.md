# System Architecture

## Core Philosophy
- **Separation of Concerns:** Modeling (Alpha) is strictly separated from Optimization (Portfolio weights) and Risk (Constraints).
- **Leakage Prevention:** All features are strictly shifted by $T-1$. Targets are shifted by $-H$.

## Layers
1. **Data:** YFinance wrapper, caching to parquet.
2. **Features:** Cross-sectional and time-series metrics.
3. **Labels:** Forward horizons.
4. **Scorers:** LightGBM regressors predicting expected returns.
5. **Optimizer:** CVXPY Mean-Variance, penalizing turnover and tracking sector bounds.
6. **Risk Engine:** Heuristics (e.g. VIX threshold) that can override the optimizer.
7. **Backtest:** Simulator executing trades at $T+1$ open/close prices.

## RL Overlay
- The RL agent sits above the optimizer. Instead of predicting individual weights, it acts as a **Portfolio Manager**, choosing sector tilts (`-1 to 1`), cash targets, and overall aggressiveness parameters based on macro state features.
- *Currently disabled by default.*
