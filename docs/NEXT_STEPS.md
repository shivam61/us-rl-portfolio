# Next Steps & Handoff

*This document serves as the rolling context and immediate roadmap for engineers and AI agents working on the repository.*

## Current System State
- The foundational US RL Portfolio system is successfully implemented and passing all tests.
- Core layers: Feature Generation, LightGBM Ranker, CVXPY Optimizer, Heuristic Risk Engine, and $T+1$ Execution Simulator.
- RL is disabled natively; fallback pass-through policy is active.
- Features are aggressively lagged (`T-1`). Backtest correctly leverages `pandas` `YE`/`ME` offsets for reporting.
- **WARNING:** The static universe `sp100_sample.yaml` introduces survivorship bias. Logs explicitly warn against relying on these absolute Sharpe metrics until point-in-time members are fed.

## Immediate Next Actions (Prioritized)
1. **Dynamic Universe Construction:** 
   - Integrate a Point-In-Time (PIT) dataset for historical S&P 500 constituents to eliminate survivorship bias.
   - Update `data/ingestion.py` to handle changing membership dynamically rather than relying purely on the static `config/universes` YAML files.

2. **Fundamental Data Integration:**
   - Enhance the feature generation pipeline (`src/features`) to utilize fundamental metrics (e.g., P/E, EPS surprises).
   - Ensure these fundamental data streams are strictly aligned to their public filing dates to avoid lookahead leakage.

3. **RL Pipeline Integration:**
   - Complete `scripts/train_rl.py` to plug `stable-baselines3` into `src/rl/environment.py`.
   - Validate that the RL agent successfully manipulates sector tilts under a supervised baseline without breaking volume/turnover constraints.

4. **Slippage Model Refinement:**
   - Evolve the static basis-point slippage model into an impact-aware model utilizing the `adv` (average daily dollar volume) metric inside `ExecutionSimulator`.

## Assumptions to Verify
- Test the fallback behaviors when `LightGBM` entirely fails to build a tree (e.g., NaN inputs).
- Verify the overnight cash reinvestment assumptions logic. Currently, T+1 uninvested cash is instantaneously rolled, which ignores T+2 actual settlement latency.