# Phase D — RL Overlay on the Locked B.5 System

> **Navigation:** [← Phase C](phase_c.md) | [← ROADMAP](../ROADMAP.md)

**Objective:** Add a reinforcement-learning overlay that adjusts sector allocation and stock-sleeve aggressiveness around the locked Phase B.5 construction. RL learns regime-dependent tilts that the static heuristic cannot express, while the B.5 system retains full control over stock selection, trend exposure, and risk limits.

**Entry state (Phase C complete — 2026-05-01):**
- Production signal: `vol_score` (unchanged, locked)
- Construction: `b4_stress_cap_trend_boost` — locked
- B.5 metrics (sp500, 2008–2026, 10 bps): CAGR `16.04%`, Sharpe `1.078`, MaxDD `−32.98%`, turnover `84.12`

---

## What RL Can and Cannot Do

### RL CAN adjust (overlay only, bounded)
| Lever | Allowed range | Effect |
|---|---|---|
| Sector tilts | ±15% of stock sleeve per sector | Reallocate weight among GICS sectors within the stock sleeve |
| Stock-sleeve aggressiveness | [0.75, 1.0] | Scale stock sleeve down to 75% (remainder to cash); cannot lever up |

### RL CANNOT touch (locked)
| Component | Why it is locked |
|---|---|
| `volatility_score` signal | Stock selection and initial weights are set by vol_score; RL cannot change which stocks are held |
| Trend sleeve (TLT / GLD / UUP) | Trend exposure and sizing remain fixed by the B.5 stress-blend formula |
| Stress blend formula | CANDIDATE_BASE_TREND_WEIGHT + CANDIDATE_STRESS_K × stress, clipped at CANDIDATE_TREND_CAP |
| Beta cap | 0.90 − 0.20 × stress, floor 0.50 — runs as a hard circuit-breaker AFTER RL adjustments |
| Gross cap | 1.50 — hard floor, unchanged |
| Rebalance cadence | every_2_rebalances — unchanged |

---

## Architecture

```
vol_score signal
       │
       ▼
B.5 construction (locked)
  ├── stress blend: vol sleeve + trend sleeve
  ├── every_2_rebalances execution filter
  └── apply_b4_constraints (beta cap 0.90−0.20×stress, floor 0.50)
       │
       ▼
B.5 base weights (W_base)       ← RL reads these as part of state
       │
       ▼
RL overlay (sector tilts + aggressiveness)
  └── applied to stock sleeve only; trend sleeve frozen
       │
       ▼
apply_b4_constraints (re-run as hard floor after RL)
       │
       ▼
Execution Simulator
```

The trend sleeve passes through RL untouched. RL adjustments happen inside the stock sleeve only.

---

## State Vector

```
obs_dim = 3 (macro) + 1 (stress) + 11 (sector vol_score signals) + 11 (current sector weights) + 2 (portfolio state)
        = 28 dimensions
```

| Component | Dim | Features | Source |
|---|---|---|---|
| Macro | 3 | VIX 252d percentile, SPY 252d drawdown from peak, yield-curve slope proxy (TLT vs SPY 63d momentum) | prices + ^VIX |
| Stress | 1 | Current stress score (weighted_50_50 from B.5) | `build_stress_series` |
| Sector vol_score signals | 11 | Median vol_score rank within each GICS sector (11 sectors) | `vol_scores` at rebalance date |
| Current sector weights | 11 | Stock-sleeve weight allocated per sector from B.5 output | B.5 weights at rebalance date |
| Portfolio state | 2 | Current drawdown from peak NAV, weeks since last rebalance | simulator |

---

## Action Space

```
action_dim = 11 (sector tilts) + 1 (aggressiveness)
           = 12 dimensions, all ∈ [−1, 1] raw (clipped to valid ranges below)
```

| Component | Raw range | Applied range | Applied as |
|---|---|---|---|
| `sector_tilt[i]` | [−1, +1] | [−0.15, +0.15] | Additive to sector's stock-sleeve weight; zero-sum within stock sleeve |
| `aggressiveness` | [−1, +1] | [0.75, 1.0] | Scales all stock positions; (1 − aggressiveness) goes to cash |

**Zero-sum constraint on sector tilts:** tilts are normalised so Σ tilt[i] = 0. RL cannot add aggregate gross exposure; it can only reallocate among sectors.

**Aggressiveness cannot lever up:** 1.0 = exactly B.5 stock sleeve size. 0.75 = 25% cash within the stock sleeve. No values above 1.0.

---

## Reward Function

```
reward_t = rolling_sharpe_21d(portfolio_returns)  −  λ × Σ|sector_tilt[i]|
```

| Term | Value | Rationale |
|---|---|---|
| `rolling_sharpe_21d` | Annualised Sharpe on last 21 trading days | Risk-adjusted; penalises volatility naturally |
| `λ × Σ|tilt|` | λ = 0.01 | Discourages unnecessary churn from sector reallocation |

No raw-return reward. This prevents the agent learning to maximise leverage or chase momentum spikes.

---

## Training / Evaluation Split

| Window | Purpose |
|---|---|
| 2008–2015 | RL training episodes |
| 2016–2018 | Validation / early stopping |
| 2019–2026-04-24 | **Holdout** — compare RL vs B.5 (never seen during training) |

Training on 2008–2018 is deliberately the same window used to build B.5 signal weights. Holdout is disjoint and matches the Phase B.5 holdout exactly.

---

## Phase D Steps

| Step | Purpose | Output |
|---|---|---|
| D.0 | Measure B.5 baseline on holdout window (2019–2026) separately | IC and portfolio metrics on holdout only |
| D.1 | Build state vector | `src/rl/state_builder.py` |
| D.2 | Build sector tilt application | `src/rl/tilts.py` |
| D.3 | Flesh out RL environment | `src/rl/environment.py` |
| D.4 | Reward function | `src/rl/reward.py` |
| D.5 | PPO training script | `scripts/train_rl.py` |
| D.6 | RL vs B.5 evaluation | `scripts/run_rl_backtest.py` |

---

## Phase D Non-Negotiable Gates

| Gate | Target | Notes |
|---|---|---|
| Holdout Sharpe ≥ B.5 | ≥ 1.078 (preferred) | Measured on 2019–2026 holdout |
| Holdout Sharpe floor | ≥ 1.00 | Hard floor; below this: reject RL and keep B.5 |
| MaxDD not worse | ≥ −35% | RL must not increase drawdown by more than 2 pp vs B.5 |
| No beta cap violations | 0 on rebalance dates | B.4 constraints re-applied after RL; must still hold |
| No gross cap violations | Max gross ≤ 1.50 | Aggressiveness cannot increase gross above B.5 |
| No new alpha sleeve | — | RL is an overlay; vol_score remains the only stock-selection signal |

If RL does not clear the Sharpe floor (≥ 1.00): reject, keep B.5 as final production system.

---

## Implementation Notes

### D.1 State builder
- VIX 252d percentile: rolling rank of daily VIX closes, clipped [0, 1]
- SPY drawdown: (SPY − rolling 252d max) / rolling 252d max, clipped [−1, 0]
- Yield curve proxy: (TLT 63d return) − (SPY 63d return), normalised
- Sector vol_score signals: for each of 11 GICS sectors, median `vol_score` rank across tickers in that sector at the rebalance date
- Current sector weights: from B.5 constrained weights, sum by sector (stock tickers only, excluding trend assets)

### D.2 Sector tilt application (`src/rl/tilts.py`)
```
1. Start with B.5 stock-sleeve weights (W_stock)
2. Map each stock to its GICS sector
3. Apply sector_tilt[i] additively to each sector's weight proportion
4. Normalise so Σ tilted_sector_weights = Σ original_sector_weights (zero-sum)
5. Redistribute within sector proportionally (equal within sector)
6. Apply aggressiveness: W_stock_tilted × aggressiveness + cash × (1 − aggressiveness)
7. Recombine with trend sleeve (frozen)
8. Re-apply B.4 constraints as hard circuit breaker
```

### D.3 Environment
- Episode = one training epoch (2008-01-01 to 2015-12-31, ~2000 trading days)
- Step = one rebalance date (every_2_rebalances cadence, ~125 steps per episode)
- State computed fresh at each rebalance date; carried between rebalances using last-rebalance state
- Reward accumulated daily but only on rebalance dates the RL decision is applied

### D.5 Training
- Algorithm: PPO (`stable-baselines3`)
- Policy: MlpPolicy (2 × 64 hidden layers)
- Episodes: 500 minimum; early stop if validation Sharpe does not improve for 50 episodes
- Seed: 42 (reproducibility)
- Parallelism: vec_env with 4 parallel environments (training only)

---

## Design Decisions

| Decision | What was rejected | Rationale |
|---|---|---|
| RL as overlay, not replacement | RL replacing vol_score or B.4 | Phase B.5 is proven. RL should add regime-level adaptation on top, not undo what works |
| Sector tilts only (no stock picking) | Direct stock weight changes | 11-dim action space vs 503-dim; stable credit assignment; vol_score handles stock selection |
| Aggressiveness floor at 0.75 (no levering up) | Aggressiveness in [0.5, 1.5] | Prevents RL from leveraging to boost reward; upper bound 1.0 preserves B.5 gross control |
| B.4 re-applied as hard floor after RL | RL allowed to override beta cap | Beta cap is non-negotiable; RL learns within the constrained space |
| Trend sleeve frozen | RL adjusts trend/stock split | Trend sleeve provides genuine regime diversification; RL cannot degrade it |
| Rolling 21d Sharpe reward | Raw return | Raw return leads to max-leverage or momentum-chasing policies |
| Sector tilts zero-sum | Tilts add gross | Prevents RL from circumventing aggressiveness control through sector manipulation |

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-05-01 | Phase C complete | Entry gate cleared | `vol_score` carries to Phase D. B.5: Sharpe `1.078`, MaxDD `−32.98%`. |
| — | D.0 baseline | Not started | Measure B.5 on 2019–2026 holdout only |
| — | D.1–D.4 build | Not started | State builder, tilts, env, reward |
| — | D.5 training | Not started | PPO on 2008–2015 training window |
| — | D.6 evaluation | Not started | RL vs B.5 on 2019–2026 holdout |
