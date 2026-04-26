# US RL Portfolio System

A complete end-to-end, runnable US equity portfolio system that features walk-forward backtesting, feature generation, risk overlays, and a mean-variance-turnover optimizer.

**Disclaimer:** This is research infrastructure, NOT investment advice. Do not use for real trading without extensive validation.

## Architecture
See `docs/ARCHITECTURE.md` for a full breakdown.
- **Data & Features:** Point-in-time safe, yfinance driven.
- **Models:** LightGBM-based sector and stock scorers.
- **Optimizer:** CVXPY based mean-variance optimization with turnover penalty.
- **Risk:** Rule-based heuristics for macro crashes.
- **RL Overlay:** A skeleton PPO agent is provided but disabled by default.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commands
```bash
# 1. Download Data
python scripts/download_data.py --config config/base.yaml

# 2. Build Features & Labels
python scripts/build_features.py --config config/base.yaml

# 3. Run Walk-Forward Backtest
python scripts/run_backtest.py --config config/base.yaml

# 4. Generate Current Portfolio
python scripts/current_portfolio.py --config config/base.yaml
```

## Testing
```bash
pytest -q tests/
```
