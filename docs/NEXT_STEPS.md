# Next Steps & Handoff

*This document serves as the rolling context and immediate roadmap for engineers and AI agents working on the repository.*

## Current System State
- **PIT Universe Integrated:** The system now uses a simulated Point-In-Time universe mask (`data/artifacts/universe_mask.parquet`). The backtest engine only trades stocks active on the signal date.
- **Fundamentals Integrated:** A fundamental feature pipeline is live, providing P/E, P/B, ROE, and EPS Growth. These are joined with daily prices using a strict `filing_date` (delayed by 10-45 days from quarter-end) to prevent lookahead.
- **20-Year Horizon:** Backtest start date set to 2006 to capture GFC and multiple cycles.
- **Baseline Results:** Initial supervised + optimizer path is stable. The system correctly identifies transaction costs, slippage, and liquidity constraints.

## Immediate Next Actions (Prioritized)
1. **RL Pipeline Integration:**
   - Complete `scripts/train_rl.py` to plug `stable-baselines3` into `src/rl/environment.py`.
   - The RL agent should act as an overlay, choosing sector tilts and cash targets.
   - Validate that the RL agent can improve on the supervised baseline (Sharpe 1.86 in previous biased run).

2. **Slippage Model Refinement:**
   - Evolve the static basis-point slippage model into an impact-aware model utilizing the `adv` (average daily dollar volume) metric inside `ExecutionSimulator`.

3. **Hyperparameter Tuning:**
   - The LightGBM model and cvxpy optimizer parameters are currently static. Use a validation window within the walk-forward loop to optimize these.

4. **Brinson Attribution:**
   - Implement `src/attribution/brinson.py` to decompose returns into Sector Allocation vs. Stock Selection components.

## Assumptions to Verify
- Verify that the synthetic PIT mask doesn't introduce hidden biases by being *too* selective.
- Confirm that the `pd.merge_asof` in `FundamentalFeatureGenerator` correctly handles tickers that were delisted (the PIT mask should handle this, but verify the data alignment).
