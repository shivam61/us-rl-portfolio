# Phase D — Implementation Plan

> **Status:** Planning complete. Ready to implement D.0 → D.6 sequentially.
> **Locked baseline:** B.5 = `b4_stress_cap_trend_boost`, Sharpe 1.078, MaxDD −32.98%.
> **Constraints:** See `phase_d.md` — RL adjusts sector tilts + aggressiveness only.

---

## D.0 — Measure B.5 Holdout Baseline

**Goal:** Establish the precise B.5 numbers on the 2019–2026-04-24 holdout window (full-period
metrics are already known; we need the holdout-only slice as the RL promotion benchmark).

**Script:** `scripts/run_phase_d0_holdout_baseline.py`

**Logic:**
- Load B.5 constrained weights (re-run `build_promoted_weights` from `run_phase_b5_final_gate.py`)
- Clip to holdout window 2019-01-01 → 2026-04-24
- Compute: CAGR, Sharpe, MaxDD at 10/25/50 bps
- Regime breakdown within holdout (2020 COVID, 2022 bear, 2023-26 recovery)

**Output:** `artifacts/reports/phase_d0_holdout_baseline.md`

**Reuse:** `build_promoted_weights`, `run_execution_simulator`, `cost_sensitivity_table`,
`regime_breakdown_table` from `run_phase_b5_final_gate.py` and `run_phase_c3_portfolio_validation.py`.

**Run:** `.venv/bin/python scripts/run_phase_d0_holdout_baseline.py`
**Time:** ~30 seconds.

---

## D.1 — State Vector Builder

**Goal:** Build the 28-dim observation at each rebalance date from prices + vol_scores + B.5 weights.

**File:** `src/rl/state_builder.py`

**Inputs:** `inputs` dict (prices, vol_scores, pit_mask, universe_config), B.5 constrained weights
DataFrame, current portfolio NAV series, rebalance date.

**Output:** `np.ndarray` shape (28,), dtype float32.

**Breakdown:**

| Feature | Index | Formula |
|---|---|---|
| VIX 252d percentile | 0 | `vix.rolling(252).rank(pct=True).iloc[-1]` |
| SPY 252d drawdown | 1 | `(SPY − SPY.rolling(252).max()) / SPY.rolling(252).max()` |
| Yield-curve proxy | 2 | z-score of `(TLT_63d_ret − SPY_63d_ret)`, rolling 252d window |
| Stress score | 3 | `build_stress_series(inputs)` value at date |
| Sector vol_score [0..10] | 4–14 | Median `vol_score` rank across active tickers per GICS sector |
| Sector weights [0..10] | 15–25 | B.5 stock-sleeve weight summed per GICS sector, normalised |
| Portfolio drawdown | 26 | `(nav − nav.cummax()) / nav.cummax()` |
| Weeks since rebalance | 27 | `(date − last_rebalance_date).days / 7` |

**Key implementation detail:**
- GICS sector mapping from `universe_config.tickers` (`{ticker: sector_etf}`)
- Sector vol_score computed from `inputs["vol_scores"]` at the latest available date ≤ rebalance date
- Sector weights computed from B.5 constrained weights at the rebalance date (stock tickers only;
  exclude TLT, GLD, UUP, SPY from the sector weight vector)

**Test:** unit test that output is shape (28,), all finite, VIX percentile ∈ [0,1],
drawdown ≤ 0, sector weights sum to ~1.0.

---

## D.2 — Sector Tilt Application

**Goal:** Apply RL action (raw 12-dim ∈ [−1,+1]) to B.5 weights using the 10-step sequence.

**File:** `src/rl/tilts.py`

**Signature:**
```python
def apply_sector_tilts(
    b5_weights: pd.Series,          # full B.5 constrained weights at this date
    ticker_to_sector: dict[str,str],# from universe_config.tickers
    trend_tickers: list[str],       # TLT, GLD, UUP, SPY — frozen
    sector_order: list[str],        # canonical 11-sector ordering
    raw_action: np.ndarray,         # shape (12,); [0:11]=tilts, [11]=aggressiveness
    per_sector_cap: float = 0.15,
    total_budget: float = 0.35,
    aggressiveness_floor: float = 0.75,
) -> pd.Series:                     # final weights (stock sleeve tilted + trend frozen + cash)
```

**10-step sequence (as in phase_d.md):**
1. Split `b5_weights` into stock sleeve and trend sleeve
2. Compute `base_sector_weight[i]` = sum of stock-sleeve weights per sector
3. Map `raw_action[0:11]` → tilts clipped to `[−per_sector_cap, +per_sector_cap]`
4. Budget: if `Σ|tilt| > total_budget` → rescale
5. Zero-sum: `tilt -= mean(tilt)`
6. `tilted_sector[i] = max(0, base_sector_weight[i] + tilt[i])`
7. Normalise: `tilted_sector *= sum(base) / sum(tilted_sector)`
8. Within-sector redistribution: proportional to original stock weights in sector
9. Aggressiveness: map `raw_action[11]` → `[aggressiveness_floor, 1.0]`; scale stock sleeve
10. Recombine with frozen trend sleeve; do NOT apply B.4 here (caller applies it)

**Unit tests (critical):**
- After step 5: `sum(tilts) ≈ 0`
- After step 7: `sum(tilted_sector) ≈ sum(base_sector_weights)`
- After step 8: `sum(all stock weights) ≈ sum(tilted_sector)` (within-sector redistribution is lossless)
- After step 9: `sum(stock_sleeve_final) ≤ sum(tilted_sector)` (aggressiveness can only shrink)
- Gross of final output ≤ B.5 gross (since aggressiveness ≤ 1.0 and trend is frozen)

---

## D.3 — RL Environment

**Goal:** Flesh out `src/rl/environment.py` to wire state builder, tilt application, and reward.

**File:** `src/rl/environment.py` (existing skeleton — update in place)

**Changes to skeleton:**
- Action space: update `action_dim` to 12 (was 13; remove separate cash_target)
- `__init__`: accept `inputs`, `b5_weights_df` (precomputed B.5 weight path), `nav_series`
- `reset()`: set episode start to first training date; initialise NAV=1.0, portfolio=B.5 initial weights
- `step(action)`:
  1. Get current B.5 weights at this rebalance date
  2. Call `state_builder.build_state(...)` for observation
  3. Call `tilts.apply_sector_tilts(...)` to get tilted weights
  4. Call `apply_b4_constraints(...)` to enforce hard floor
  5. Compute daily returns from last rebalance date to current date (using stored price slice)
  6. Compute reward: `rolling_sharpe_21d − 0.01×Σ|tilt| − 0.05×max(0,−drawdown)`
  7. Advance to next every_2_rebalances date; check episode termination
  8. Build next observation; return (obs, reward, terminated, truncated, info)

**Training / validation boundary:** Environment is parameterised by `start_date` and `end_date`.
Training env: 2008-01-01 → 2016-12-31. Validation env: 2017-01-01 → 2018-12-31.

---

## D.4 — Reward Function

**Goal:** Isolated reward computation module (makes reward easy to tune without touching env logic).

**File:** `src/rl/reward.py`

**Signature:**
```python
def compute_reward(
    daily_returns: pd.Series,       # returns from last rebalance to current date
    sector_tilts: np.ndarray,       # applied tilts (shape 11)
    portfolio_nav: pd.Series,       # full NAV history (for drawdown)
    lambda_tilt: float = 0.01,
    lambda_dd: float = 0.05,
) -> float:
```

**Formula:**
```python
rolling_sharpe = annualised_sharpe(daily_returns[-21:])  # last 21 trading days
tilt_penalty   = lambda_tilt * np.sum(np.abs(sector_tilts))
drawdown       = (portfolio_nav.iloc[-1] - portfolio_nav.cummax().iloc[-1]) / portfolio_nav.cummax().iloc[-1]
dd_penalty     = lambda_dd * max(0.0, -drawdown)
return rolling_sharpe - tilt_penalty - dd_penalty
```

**Edge cases:**
- If fewer than 5 returns in window: return 0.0 (warm-up period)
- If NAV is zero or negative: return −1.0 (terminal penalty)

---

## D.5 — PPO Training

**Goal:** Train PPO policy on 2008–2016; early-stop on validation Sharpe (2017–2018).

**File:** `scripts/train_rl.py`

**Key parameters:**
```python
TRAIN_START  = "2008-01-01"
TRAIN_END    = "2016-12-31"
VAL_START    = "2017-01-01"
VAL_END      = "2018-12-31"
N_ENVS       = 4           # SubprocVecEnv parallel training
POLICY       = "MlpPolicy"
NET_ARCH     = [64, 64]
SEED         = 42
MAX_EPISODES = 1000
PATIENCE     = 50          # early stop if val Sharpe does not improve
CHECKPOINT_EVERY = 100
```

**Training loop:**
```
for episode in range(MAX_EPISODES):
    train model.learn(n_steps_per_episode)
    val_sharpe = evaluate_policy(val_env, model)
    if val_sharpe > best_val_sharpe:
        best_val_sharpe = val_sharpe
        save_checkpoint(model, "best")
        patience_counter = 0
    else:
        patience_counter += 1
    if patience_counter >= PATIENCE:
        break  # early stop
```

**Output:**
- `artifacts/models/rl_ppo_best.zip` — best checkpoint (SB3 format)
- `artifacts/reports/phase_d5_training_log.csv` — episode / train_sharpe / val_sharpe per episode

**Run:** `.venv/bin/python scripts/train_rl.py`
**Estimated time:** ~30 min on 32-core machine (4 parallel envs × 200 steps/episode × 500 episodes)

---

## D.6 — Evaluation: Four-Way Comparison

**Goal:** Compare four policies on holdout 2019–2026-04-24. Determine promotion.

**File:** `scripts/run_rl_backtest.py`

**Four policies:**

| Policy | Implementation |
|---|---|
| B.5 locked | `build_promoted_weights` from `run_phase_b5_final_gate.py`; no RL |
| RL no-op | `apply_sector_tilts` with all-zero action + aggressiveness=1.0 |
| Random bounded | 50 seeds; uniform tilts in `[−0.15, +0.15]` subject to budget; random aggressiveness in `[0.75, 1.0]` |
| Trained RL | Load `artifacts/models/rl_ppo_best.zip`; run on holdout without retraining |

**Metrics per policy:**
- CAGR, Sharpe, MaxDD at 10/25/50 bps
- Turnover sum
- Beta violations (from `apply_b4_constraints` diagnostics)
- Regime breakdown: 2020 COVID, 2022 bear, 2023-26 recovery
- Average sector tilt magnitude (for trained RL and random)

**Promotion decision:** evaluate against Phase D gates from `phase_d.md`.

**Outputs:**
- `artifacts/reports/phase_d6_rl_evaluation.md` — verdict + full comparison tables
- `artifacts/reports/d6_policy_comparison.csv`
- `artifacts/reports/d6_regime_breakdown.csv`
- `artifacts/reports/d6_cost_sensitivity.csv`

---

## File Inventory

### New files to create

| File | Step | Reuses |
|---|---|---|
| `scripts/run_phase_d0_holdout_baseline.py` | D.0 | `build_promoted_weights`, `run_execution_simulator`, `cost_sensitivity_table` |
| `src/rl/state_builder.py` | D.1 | `build_stress_series`, `vol_scores`, `pit_mask` |
| `src/rl/tilts.py` | D.2 | `apply_b4_constraints` (caller applies it after tilts) |
| `src/rl/reward.py` | D.4 | standalone |
| `scripts/train_rl.py` | D.5 | `PortfolioEnv`, `state_builder`, `tilts`, `reward` |
| `scripts/run_rl_backtest.py` | D.6 | all of the above + `build_promoted_weights` |

### Files to modify

| File | Step | Change |
|---|---|---|
| `src/rl/environment.py` | D.3 | Flesh out skeleton: wire state/tilt/reward; action_dim 13→12 |
| `src/rl/fallback_policy.py` | D.3 | No change needed (pass-through policy is already correct) |

### No changes needed

- `src/alpha/volatility_score.py` — locked
- `run_phase_b*` scripts — locked
- `run_phase_b5_final_gate.py:build_promoted_weights` — imported as-is in D.0 and D.6

---

## Execution Order

```
D.0  →  D.1  →  D.2  →  D.4  →  D.3  →  D.5  →  D.6
```

D.1, D.2, D.4 can be built and unit-tested before D.3. D.3 depends on D.1, D.2, D.4.
D.5 depends on D.3. D.6 depends on D.5.

D.0 is independent and can run immediately.

---

## Verification Checklist

| Check | How |
|---|---|
| D.0: B.5 holdout Sharpe matches expected ~1.078 range | Read `phase_d0_holdout_baseline.md` |
| D.2: Tilt invariants hold | Unit test: zero-sum, budget ≤35%, gross preserved |
| D.3: Env step returns finite obs and non-NaN reward | Run `env.step(env.action_space.sample())` 10 times |
| D.5: Validation Sharpe tracked correctly | Check `phase_d5_training_log.csv` — should trend up then plateau |
| D.6: No-op policy matches B.5 locked within rounding | Sharpe difference < 0.01 |
| D.6: Trained RL beats random bounded policy | Otherwise RL is not adding learned value |
| D.6: Promotion gate evaluation is explicit in report | Pass/fail per gate row |
