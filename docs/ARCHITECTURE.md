# System Architecture

> For full context including roadmap and design decisions, see [docs/ROADMAP.md](ROADMAP.md).

## Layers

```
Raw Data (yfinance) → Features → Labels → LightGBM Ranker
    → Top-N Selection → MVO Optimizer → [RL Sector Overlay]
    → Heuristic Risk Engine → Execution Simulator
```

| Layer | File | Notes |
|---|---|---|
| Data | `src/data/ingestion.py` | yfinance, cached to parquet |
| Features | `src/features/stock_features.py` | 30 features: momentum, reversal, volatility, sector |
| Labels | `src/labels/targets.py` | 3 targets: raw fwd_ret, rank_cs, sector_rel |
| Scorer | `src/models/stock_ranker.py` | LightGBM regressor |
| Optimizer | `src/optimizer/portfolio_optimizer.py` | CVXPY MVO, sector ≤ 25%, turnover ≤ 30% |
| RL Overlay | `src/rl/environment.py` | Sector tilt ±20% + cash target (Phase D — disabled) |
| Risk Engine | `src/risk/risk_engine.py` | VIX + SPY drawdown hard triggers |
| Simulator | `src/backtest/simulator.py` | TC 10bps, slippage 5bps, explicit cash tracking |

## Core invariants
- All features `.shift(1)` before use (leakage guard)
- Targets use `shift(-horizon)` (forward-only)
- RL sits above optimizer, below hard risk engine floor
- Research on sp100 (44 tickers), validation on sp500 (503 tickers)
- Data and feature additions must follow [DATA_AND_FEATURE_ENGINEERING.md](DATA_AND_FEATURE_ENGINEERING.md)
