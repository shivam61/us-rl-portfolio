# Phase D — RL Sector Rotation Overlay

> **Navigation:** [← Phase C](phase_c.md) | [← ROADMAP](../ROADMAP.md)

**Objective:** Replace the static heuristic risk engine (VIX + SPY drawdown triggers) with a learned RL policy that dynamically adjusts sector weights and cash level based on macro regime and sector alpha signals.

**Entry gate:** Phase C complete — IC Sharpe ≥ 0.50 on 2019–2026 holdout.

---

## Success Criteria

| Metric | Heuristic baseline | RL target |
|---|---|---|
| Sharpe (2019–2026) | ~0.59 | ≥ 0.70 |
| Max Drawdown | -34% | ≥ -28% |
| CAGR | 8.7% | ≥ 10% |
| Avg cash drag | ~30% | ≤ 15% |

The cash drag reduction (RL learns to stay invested in benign regimes vs heuristic being too conservative) is expected to account for most of the CAGR improvement.

---

## Iteration Log

| Date | Config | Sharpe | MaxDD | CAGR | Cash drag | Notes |
|---|---|---|---|---|---|---|
| — | Not started | — | — | — | — | Waiting on Phase C gate |

---

## Architecture

### Where RL sits in the pipeline

```
MVO Optimizer output (weights_opt)
        │
        ▼
RL policy.get_action(state)          ← replaces heuristic when rl.enabled=True
        │  → sector_tilts, cash_target, aggressiveness
        ▼
apply_tilts(weights_opt, tilts)      ← new: src/rl/tilts.py
        │
        ▼
Heuristic risk engine                ← still runs as hard circuit-breaker floor
        │                               RL cannot override VIX/drawdown hard stops
        ▼
Execution Simulator
```

### Why sector rotation, not stock picking
- 11 sectors vs 500 stocks → lower-dimensional action space, cleaner signal
- Sector-level IC is more stable than per-stock IC (0.033)
- The LightGBM alpha signal feeds into state as sector-aggregated scores — clean bridge from Phase C
- RL can learn regime-dependent rules (defensives in high-VIX, growth in low-rate) a static heuristic can't

---

## State Vector

```
obs_dim = 6 (macro) + 11 (sector alpha scores) + 11 (current sector weights) + 1 (cash) + 1 (drawdown)
        = 30 dimensions
```

| Component | Features | Source |
|---|---|---|
| Macro (6) | VIX percentile (252d), SPY drawdown from peak, yield curve slope, credit spread, USD 3m momentum, CPI regime flag | `src/rl/state_builder.py` |
| Sector alpha scores (11) | LightGBM predicted return aggregated (median) per sector ETF | walk_forward signal at rebalance date |
| Current sector weights (11) | Actual portfolio % per sector | simulator state |
| Cash (1) | Cash % of NAV | simulator state |
| Portfolio drawdown (1) | Current drawdown from peak NAV | simulator state |

---

## Action Space

```
action_dim = 11 (sector tilts) + 1 (cash target) + 1 (aggressiveness)
           = 13 dimensions, all ∈ [-1, 1] (clipped to valid ranges below)
```

| Component | Range | Applied as |
|---|---|---|
| `sector_tilt[i]` | [-0.20, +0.20] | Added to MVO weight for sector i; final weight clipped to [0, max_sector_weight + 0.20] |
| `cash_target` | [0.0, 0.30] | Overrides `portfolio.cash_min` for this rebalance |
| `aggressiveness` | [0.5, 1.0] | Scales all position sizes (1.0 = full conviction) |

---

## Reward Function

```
reward = rolling_sharpe_21d  -  λ × turnover_penalty
```

- `rolling_sharpe_21d`: annualized Sharpe on last 21 trading days of portfolio returns
- `turnover_penalty`: `λ × |sector_tilts|.sum()` where `λ = 0.01`
- No raw return reward — prevents the agent learning to chase volatility

---

## Training / Evaluation Split

| Window | Purpose |
|---|---|
| 2006–2007 | Warm-up only (excluded from reward — insufficient history for rolling features) |
| 2008–2015 | RL training |
| 2016–2018 | RL validation (early stopping) |
| 2019–2026 | Holdout — compare RL vs heuristic (never seen during training) |

---

## Implementation Steps

| Step | File | Status |
|---|---|---|
| State vector builder | `src/rl/state_builder.py` | ⏳ TODO |
| Reward function | `src/rl/reward.py` | ⏳ TODO |
| Flesh out env step/reset | `src/rl/environment.py` | ⏳ TODO (skeleton exists) |
| Sector tilt application | `src/rl/tilts.py` | ⏳ TODO |
| RL training script | `scripts/train_rl.py` | ⏳ TODO |
| Policy loader | `src/rl/policy.py` | ⏳ TODO |
| Wire into walk_forward | `src/backtest/walk_forward.py` | ⏳ TODO |
| RL vs heuristic evaluation | `scripts/run_rl_backtest.py` | ⏳ TODO |
| Results report | `artifacts/reports/rl_comparison.md` | ⏳ TODO |

---

## Design Decisions

| Decision | What was rejected | Rationale |
|---|---|---|
| PPO (stable-baselines3) | SAC, DQN | PPO is stable on continuous action spaces; SB3 handles the training loop boilerplate |
| Sector tilts as actions | Direct stock weight actions | 11-dim action space vs 500-dim; cleaner credit assignment; LightGBM handles stock selection |
| RL replaces risk engine, not optimizer | RL replaces optimizer | Optimizer handles turnover/concentration constraints efficiently; RL should focus on regime-level decisions |
| Hard heuristic floor retained | RL controls everything | VIX circuit-breakers are explainable and non-negotiable; RL cannot override them |
| Reward = rolling Sharpe | Reward = raw return | Raw return reward leads to max-leverage policy; Sharpe reward penalises vol naturally |
| Sector alpha scores as state | Raw feature matrix as state | Aggregated scores are 11-dim and regime-stable; raw features are 500×30 = 15000-dim and too noisy |

---

## Open Questions

- Should aggressiveness scale position size or leverage? (position size preferred — avoids margin)
- Minimum episodes for PPO convergence on 10-year daily data? (estimate: 500 episodes × 2520 steps)
- How to handle sector ETF constituents changing over time in PIT-correct state builder?
