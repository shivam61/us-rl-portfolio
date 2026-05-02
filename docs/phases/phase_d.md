# Phase D — RL Overlay on the Locked B.5 System

> **Navigation:** [← Phase C](phase_c.md) | [← ROADMAP](../ROADMAP.md)

**Locked baseline:** B.5 promoted system = `b4_stress_cap_trend_boost`
— vol_score signal, dynamic beta cap `0.90 − 0.20 × stress`, floor 0.50, trend sleeve, stress blend.
— sp500, 10 bps: CAGR `16.04%`, Sharpe `1.078`, MaxDD `−32.98%`, turnover `84.12`, 50 bps Sharpe `0.934`.

**Objective:** Add a reinforcement-learning overlay that adjusts sector allocation and stock-sleeve
aggressiveness around the locked B.5 system. RL learns regime-dependent tilts that the static
heuristic cannot express. The B.5 system retains full control over stock selection, trend exposure,
and risk limits.

---

## What RL Can and Cannot Do

### RL CAN adjust (bounded overlay on stock sleeve only)

| Lever | Applied range | Effect |
|---|---|---|
| Sector tilts | ±15% per sector; Σ\|tilt\| ≤ 35% total | Reallocate weight among GICS sectors within the stock sleeve; zero-sum |
| Stock-sleeve aggressiveness | [0.75, 1.0] | Scale stock sleeve; remainder to cash. Cannot lever above 1.0. |

### RL CANNOT touch (all locked)

| Component | Why it is locked |
|---|---|
| `volatility_score` signal | Stock selection and initial weights set by vol_score; RL does not change which stocks are held |
| Trend sleeve (TLT / GLD / UUP) | Exposure and sizing fixed by B.5 stress-blend formula; passes through RL unchanged |
| Stress blend formula | `CANDIDATE_BASE_TREND_WEIGHT + CANDIDATE_STRESS_K × stress`, clipped at `CANDIDATE_TREND_CAP` |
| Beta cap | `0.90 − 0.20 × stress`, floor 0.50 — re-applied as hard circuit-breaker **after** every RL step |
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
  └── apply_b4_constraints (beta cap + gross cap)
       │
       ▼
W_base = B.5 constrained weights          ← RL reads these as part of state
       │
       ▼
RL overlay (stock sleeve only; trend sleeve frozen)
  └── Tilt application — 10-step sequence:
        1.  base_sector_weight[i]  = Σ B.5 stock-sleeve weights for tickers in sector i
        2.  raw_tilt[i]            = action[i] mapped to [−0.15, +0.15]  (per-sector cap)
        3.  budget enforcement:     if Σ|raw_tilt| > 0.35 → rescale: raw_tilt *= 0.35 / Σ|raw_tilt|
        4.  zero-sum enforcement:   raw_tilt -= mean(raw_tilt)
        5.  tilted_sector[i]       = max(0, base_sector_weight[i] + raw_tilt[i])
        6.  re-normalise:           tilted_sector *= sum(base_sector_weights) / sum(tilted_sector)
        7.  within-sector:          each ticker's weight ∝ original B.5 weight within that sector
        8.  aggressiveness:         W_stock_final = W_tilted × aggressiveness
                                    W_cash        = sum(W_tilted) × (1 − aggressiveness)
        9.  recombine:              W_final = W_stock_final + W_trend (frozen) + W_cash
       10.  hard floor:             apply_b4_constraints (beta cap, gross cap) — non-negotiable
       │
       ▼
Execution Simulator
```

Steps 3, 4, and 6 together ensure RL is purely redistributive: it cannot increase gross exposure
through sector manipulation or tilt magnitudes.

---

## State Vector

```
obs_dim = 3 (macro) + 1 (stress) + 11 (sector vol_score signals) + 11 (sector weights) + 2 (portfolio state)
        = 28 dimensions
```

| Component | Dim | Features | Source |
|---|---|---|---|
| Macro | 3 | VIX 252d percentile, SPY 252d drawdown from peak, yield-curve proxy (TLT vs SPY 63d momentum) | prices + ^VIX |
| Stress | 1 | Current stress score (weighted_50_50 from B.5 `build_stress_series`) | `build_stress_series` |
| Sector vol_score signals | 11 | Median vol_score rank within each GICS sector at rebalance date | `vol_scores` |
| Current sector weights | 11 | Stock-sleeve weight allocated per sector from B.5 output | B.5 weights |
| Portfolio state | 2 | Current drawdown from peak NAV; weeks since last rebalance | simulator |

---

## Action Space

```
action_dim = 11 (sector tilts) + 1 (aggressiveness)
           = 12 dimensions, raw ∈ [−1, +1] (mapped to valid ranges via tilt application steps above)
```

| Component | Raw | Applied | Constraint |
|---|---|---|---|
| `sector_tilt[i]` | [−1, +1] | [−0.15, +0.15] per sector | Σ\|tilt\| ≤ 35% total; zero-sum |
| `aggressiveness` | [−1, +1] | [0.75, 1.0] | Cannot lever above 1.0 |

**Total tilt budget (Σ|tilt| ≤ 35%):** prevents RL from applying simultaneous large tilts
across multiple sectors (e.g. +15% Tech +15% Energy −15% Utilities −15% Staples = 60% gross
tilt). After per-sector clipping and budget rescaling, zero-sum is enforced so Σ tilt = 0.

---

## Reward Function

```
reward_t = rolling_sharpe_21d(portfolio_returns)
         − 0.01 × Σ|sector_tilt[i]|
         − 0.05 × max(0.0, −portfolio_drawdown_from_peak)
```

| Term | λ | Rationale |
|---|---|---|
| `rolling_sharpe_21d` | — | Risk-adjusted; penalises volatility naturally |
| Σ\|sector_tilt\| | 0.01 | Discourages unnecessary sector churn |
| `max(0, −drawdown_from_peak)` | 0.05 | Penalises tail risk; at −15% drawdown → 0.0075 penalty ≈ 9% of reward signal. Operates at cumulative timescale vs 21d Sharpe window |

No raw-return reward. Prevents the agent learning to maximise leverage or chase momentum spikes.

---

## Training / Evaluation Split

| Window | Purpose |
|---|---|
| 2008–2016 | RL training episodes |
| 2017–2018 | Validation / early stopping |
| 2019–2026-04-24 | **Holdout** — compare RL vs B.5 baseline (same window as Phase B.5 and C evaluation; never seen during training) |

The holdout window is fixed at 2019–2026-04-24 to match Phase B.5 and C evaluation windows.
Any B.5 comparison number used as the promotion benchmark must come from this same window.

---

## Phase D Steps

| Step | Purpose | Output |
|---|---|---|
| D.0 | Measure B.5 baseline on holdout window 2019–2026-04-24 (Sharpe, MaxDD, 50 bps Sharpe, regime breakdown) | `artifacts/reports/phase_d0_holdout_baseline.md` |
| D.1 | Build state vector | `src/rl/state_builder.py` |
| D.2 | Build sector tilt application (10-step sequence above) | `src/rl/tilts.py` |
| D.3 | Flesh out RL environment (step/reset/reward wired) | `src/rl/environment.py` |
| D.4 | Reward function (wired into env step) | `src/rl/reward.py` |
| D.5 | PPO training script + early stopping on validation Sharpe | `scripts/train_rl.py` |
| D.6 | RL vs B.5 evaluation — four-way comparison | `scripts/run_rl_backtest.py` |

---

## D.6 Four-Way Comparison (mandatory)

| Policy | Description |
|---|---|
| **B.5 locked** | No RL; vol_score + B.5 harness only |
| **RL no-op** | Trained RL policy replaced by zero tilts + aggressiveness=1.0 |
| **Random bounded** | Uniform random tilts in [−0.15,+0.15] subject to budget + random aggressiveness in [0.75,1.0]; average over 50 seeds |
| **Trained RL** | PPO policy trained on 2008–2016 |

No RL improvement is valid unless it beats both the no-op and random bounded baselines.

---

## Phase D Promotion Gate

Promote trained RL only if **all** of the following hold on the 2019–2026-04-24 holdout.

**D.0 established holdout benchmark (2026-05-02):** B.5 holdout Sharpe = **1.270**, MaxDD = **−32.98%**, 50 bps Sharpe = **1.135**.

| Condition | Target |
|---|---|
| Sharpe (Path A — clear win) | ≥ 1.270 (matches or beats B.5 **holdout**) AND MaxDD ≥ −32.98% |
| Sharpe (Path B — tail improvement) | ≥ 1.240 (= B.5 holdout − 0.03) AND MaxDD materially better (≥ B.5 holdout MaxDD + 1.5pp, i.e. ≥ −31.48%) |
| **Either path** also requires | 50 bps Sharpe ≥ 0.90 |
| **Either path** also requires | Beats RL no-op AND random bounded policy on holdout Sharpe |
| **Hard rejections** | MaxDD < −35%, OR any beta violation, OR max gross > 1.50 |

If RL does not meet either promotion path: reject, keep B.5 as final production system.

---

## Implementation Notes

### D.1 State builder (`src/rl/state_builder.py`)
- VIX percentile: rolling 252d rank of daily VIX closes, clipped [0,1]
- SPY drawdown: `(SPY − rolling_252d_max) / rolling_252d_max`, clipped [−1, 0]
- Yield-curve proxy: 63d momentum of TLT minus 63d momentum of SPY, z-scored
- Sector vol_score signals: for each of 11 GICS sectors, median `vol_score` rank across active
  tickers in that sector at the rebalance date (from `inputs["vol_scores"]`)
- Current sector weights: from B.5 constrained weights, sum by sector (stock tickers only,
  excluding trend assets TLT/GLD/UUP/SPY)

### D.2 Tilt application (`src/rl/tilts.py`)
Implement the 10-step sequence from the Architecture section exactly.
Key invariants to unit-test:
- After step 4: `sum(tilts) == 0` (zero-sum)
- After step 6: `sum(tilted_sector) == sum(base_sector_weights)` (stock-sleeve total preserved)
- After step 8: gross does not exceed B.5 gross (aggressiveness ≤ 1.0)
- After step 10: beta ≤ dynamic cap; gross ≤ 1.50 (B.4 hard floor holds)

### D.3 Environment (`src/rl/environment.py`)
- Existing skeleton already has correct obs_dim=28, action_dim=13 (update to 12)
- Episode = 2008-01-01 to 2016-12-31; step = one every_2_rebalances date (~200 steps/episode)
- State computed via `state_builder.py` at each rebalance date
- Reward computed via `reward.py` using daily portfolio returns since last rebalance

### D.5 Training (`scripts/train_rl.py`)
- Algorithm: PPO (`stable-baselines3`, already installed)
- Policy: MlpPolicy, 2 × 64 hidden layers
- Early stopping: track validation Sharpe (2017–2018); stop if no improvement for 50 episodes
- Minimum: 500 episodes; checkpoint every 100
- Parallelism: 4 parallel envs (training only; SB3 SubprocVecEnv)
- Seed: 42

---

## Design Decisions

| Decision | What was rejected | Rationale |
|---|---|---|
| RL as overlay, not replacement | RL replacing vol_score or B.4 | B.5 is proven (Sharpe 1.078). RL adds regime adaptation on top |
| Sector tilts only | Direct stock weight changes | 11-dim action vs 503-dim; stable credit assignment; vol_score handles stock selection |
| Total tilt budget Σ\|tilt\| ≤ 35% | Per-sector cap only | Per-sector ±15% without total cap allows 60% gross tilt across 4 sectors |
| Zero-sum tilt enforcement | RL sets absolute sector weights | RL adjusts B.5 weights; it cannot set them independently |
| Aggressiveness floor 0.75, no levering | Aggressiveness in [0.5, 1.5] | Prevents RL leveraging to boost reward; preserves B.5 gross control |
| B.4 re-applied after RL as hard floor | RL can override beta cap | Beta cap is non-negotiable |
| Trend sleeve frozen | RL adjusts trend/stock split | Trend sleeve provides proven regime diversification |
| Drawdown penalty (λ=0.05) in reward | Sharpe-only reward | 21d Sharpe window misses cumulative tail risk; drawdown penalty operates at a longer timescale |
| Rolling 21d Sharpe reward | Raw return | Raw return leads to max-leverage or momentum-chasing policies |
| Four-way D.6 comparison | Single RL vs baseline | No-op and random baselines are necessary to detect spurious improvement |
| Holdout fixed at 2019–2026-04-24 | Holdout starting 2020 | Must match Phase B.5 / C evaluation window for apples-to-apples Sharpe comparison |
| Train 2008–2016 | Train 2008–2015 | 8 training years vs 7; sparse cadence (~200 steps/episode) benefits from more data |

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-05-01 | Phase C complete | Entry gate cleared | `vol_score` locked, B.5 construction locked. Sharpe `1.078`, MaxDD `−32.98%`. |
| 2026-05-01 | Phase D spec | Refined + agreed | Drawdown penalty, total tilt budget, zero-sum enforcement, four-way D.6, tightened gate, 2019 holdout. |
| 2026-05-02 | D.0 baseline | **DONE** | B.5 holdout (2019–2026-04-24): CAGR `20.69%`, Sharpe `1.270`, MaxDD `−32.98%`, 50 bps Sharpe `1.135`. Holdout Sharpe (1.270) > full-period (1.078) — 2019+ is a strong regime. RL promotion gates updated to holdout numbers: Path A ≥ 1.270, Path B ≥ 1.240. |
| 2026-05-02 | D.1–D.4 build | **DONE** | `state_builder.py` (28-dim obs), `tilts.py` (10-step sequence + invariant tests), `reward.py` (three-term reward), `environment.py` (full PortfolioEnv wired). |
| — | D.5 training | Not started | PPO on 2008–2016 training window (`scripts/train_rl.py`) |
| — | D.6 evaluation | Not started | Four-way: B.5 locked / no-op / random / trained RL (`scripts/run_rl_backtest.py`) |
