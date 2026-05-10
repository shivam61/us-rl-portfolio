---
name: rl-backtest-debugging
description: Debug RL backtest and historical executor issues — state/action/reward causality, leakage checks, walk-forward boundaries, NAV divergence.
---

# RL Backtest Debugging

## When to use this skill

- When RL results don't reproduce across runs
- When feature parity fails or state vectors show drift
- When action space violations occur (e.g., equity+trend+cash ≠ 1.0)
- When NAV diverges from expected or regime behavior looks wrong
- When t+1 execution causality is unclear or leakage is suspected

## Required context to read first

1. `AGENTS.md` — repo rules, point-in-time discipline
2. `docs/ARCHITECTURE.md` — system boundaries
3. Relevant RL implementation files:
   - `src/rl/state_builder_v2.py` or equivalent — state construction
   - `src/rl/environment_v2.py` or equivalent — observation/action/reward
   - `src/rl/reward_v2.py` or equivalent — reward function
   - `src/rl/exposure_mix.py` or equivalent — action projection

## Workflow

### 1. Identify Symptom

Classify the bug:
- **Non-deterministic:** Same seed/data → different results
- **Feature drift:** Feature parity fails (max dev > threshold)
- **Action violations:** Fractions don't sum to 1.0 or exceed bounds
- **NAV mismatch:** Backtest NAV diverges from expected
- **Causality unclear:** Unsure if state_t → action_t → reward_t+1 timeline is correct

### 2. Check Feature Parity

If feature parity script exists (e.g., `check_feature_parity_g0.py`):

```bash
.venv/bin/python scripts/check_feature_parity_g0.py
cat artifacts/reports/phase_g0_feature_parity.md
```

**Gate:** Max deviation < threshold (e.g., 1e-6), zero NaN values, zero range violations.

If parity fails:
- Identify which features have max deviation
- Check if state builder has hidden state (should be stateless)
- Verify no `.shift()` operations inside state builder (shifts happen in feature generators)

### 3. Check State Builder Determinism

Verify state builder is stateless:

```python
# Good: stateless feature access
spy_ret_3m = market_data.loc[date, 'spy_ret_3m']  # column already lagged

# Bad: stateful shift inside state builder
spy_ret_3m = market_data['spy_ret_3m'].shift(1).loc[date]  # NO!
```

All `.shift(1)` operations must happen in feature generators, NOT in state builder.

### 4. Check Action Constraints

Verify action projection (e.g., simplex projection for equity/trend/cash):

```bash
# Check allocation logs
grep "equity_frac\|trend_frac\|cash_frac" data/prod_state/current_state.json

# Verify sum = 1.0
python3 -c "import json; s=json.load(open('data/prod_state/current_state.json')); print(s['equity_frac']+s['trend_frac']+s['cash_frac'])"
```

**Gate:** Sum must equal 1.0 within tolerance (e.g., ±1e-6).

If violated:
- Check action projection logic (e.g., `exposure_mix.py`)
- Verify action bounds enforced before and after projection

### 5. Check Reward Causality

Verify reward function uses only t-1 data (no lookahead):

```python
# Good: reward uses prior NAV and returns
sharpe_63d = portfolio_nav[:current_idx].pct_change().rolling(63).mean() / (...).std()

# Bad: reward uses future returns
future_ret = portfolio_nav[current_idx+1:current_idx+21].pct_change().mean()  # NO!
```

Typical reward structure: rolling Sharpe + recovery bonus - drawdown penalty - cash penalty - churn penalty. All terms use t-1 or earlier data.

### 6. Check Execution Timing

Verify t+1 execution discipline:

```
Date t-1 close:
  - Compute features (all .shift(1) already applied)
  - Build state_t-1
  - RL policy → action_t-1

Date t open:
  - Execute trades based on action_t-1
  - Apply transaction costs

Date t close:
  - Observe returns
  - Compute reward_t
```

Causality: `state_t-1 → action_t-1 → execution_t → reward_t`

### 7. Check Walk-Forward Splits

Verify no temporal leakage:

```bash
# Check splits in training script
grep "train_start\|train_end\|val_start\|val_end\|holdout_start" scripts/train_rl*.py
```

**Gates:**
- Train end < Val start
- Val end < Holdout start
- No data from holdout used in training or validation

### 8. Check Transaction Costs

Verify costs applied at execution:

```bash
grep "transaction_cost" src/backtest/executor.py
```

Cost = `turnover × cost_bps / 10000`. Verify turnover = sum of abs(weight_changes) on rebalance dates.

## Checks

- [ ] Feature parity PASS (if applicable)
- [ ] State builder is stateless (no `.shift()` inside)
- [ ] All features lagged by 1 day (`.shift(1)` in feature generators)
- [ ] Action constraints satisfied (e.g., sum = 1.0 ± tolerance)
- [ ] Reward uses only t-1 data (no lookahead)
- [ ] Execution timing correct (state_t → action_t → execution_t+1)
- [ ] Walk-forward splits non-overlapping
- [ ] Transaction costs applied
- [ ] Deterministic: same seed + same data → same output

## Output format

**Root Cause:** [1-2 sentences]

**Location:** `file_path:line_number`

**Proposed Fix:**
```python
# Before
<code>

# After
<code>
```

**Verification:**
```bash
# Re-run command to confirm fix
```

## Guardrails

- Do NOT modify feature lag structure without full backtest validation
- Do NOT skip walk-forward boundary checks
- Do NOT trust results if feature parity fails
- Do NOT change action projection logic without understanding impact
- Do NOT introduce lookahead in reward function
- Do NOT skip transaction cost accounting
