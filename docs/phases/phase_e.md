# Phase E — RL Regime Controller v2

> **Navigation:** [← Phase D](phase_d.md) | [← ROADMAP](../ROADMAP.md)

**Locked baseline:** B.5 promoted system = `b4_stress_cap_trend_boost`
— vol_score signal, dynamic beta cap `0.90 − 0.20 × stress`, floor 0.50, trend sleeve, stress blend.
— sp500, 10 bps: CAGR `16.04%`, Sharpe `1.078`, MaxDD `−32.98%`, turnover `84.12`, 50 bps Sharpe `0.934`.
— Holdout (2019–2026-04-24): CAGR `20.69%`, Sharpe `1.270`, MaxDD `−32.98%`, 50 bps Sharpe `1.135`.

**Objective:** Build a second-generation RL controller that performs explicit regime-level exposure
control — how much equity, trend/hedge, and cash to hold, and when to de-risk and re-risk — rather
than small bounded sector tilts. Phase D RL (sector tilts only) could not beat a random bounded
policy because the action space was too constrained to express genuine regime switching.

Phase E is experimental. B.5 remains the production system unless Phase E clearly beats it
out-of-sample on the locked holdout window.

---

## Why Phase D Failed (Motivation)

| Problem | Effect |
|---|---|
| Sector tilts small (±15%, Σ≤35%) | Max gross tilt ~5%; negligible impact on returns |
| Aggressiveness floor 0.75 | RL could only reduce stock exposure by 25% |
| No explicit cash control | Cash was a byproduct of aggressiveness, not a strategic lever |
| No explicit trend/hedge control | Trend sleeve frozen; RL could not increase hedge when regime worsened |
| 21d Sharpe reward too short | Could not see full regime transitions; learned noise |
| B.5 already handled regime risk | Stress blend + beta cap already did the work; overlay had no room |

Core failure: the bounded sector-tilt action space is too small to express meaningful regime switching.
PPO learned to approximate bounded random tilts, not a strategy.

---

## What Phase E RL Can Control

| Lever | Range | Purpose |
|---|---|---|
| Equity sleeve multiplier | `[0.25, 1.00]` | Reduce stock exposure in stress; re-risk in recovery |
| Trend/hedge sleeve multiplier | `[0.00, 1.00]` | Scale up hedge when regime deteriorates |
| Cash allocation | `[0.00, 0.60]` | Move to cash during severe stress |
| Sector tilt (optional) | `±10%` total budget | Secondary refinement only; not primary lever |

Portfolio composition after RL action:
```
W_equity  = equity_multiplier  × W_b5_stock_sleeve   (renormalized within-sleeve)
W_trend   = trend_multiplier   × W_b5_trend_sleeve   (renormalized within-sleeve)
W_cash    = residual after equity + trend (clipped to [0, 0.60])
```

Normalization: if `W_equity + W_trend > 1.0`, rescale proportionally to sum to 1.0 then set cash=0.
The three always sum to 1.0. RL cannot lever above 1.0 (no leverage).

---

## What RL Cannot Touch

| Component | Why it is locked |
|---|---|
| `volatility_score` | Stock selection and initial weights set by vol_score |
| Stock selection and universe | PIT/liquidity mask, ticker set — unchanged |
| Within-stock-sleeve weights | vol_score proportions preserved when equity sleeve is scaled |
| Within-trend-sleeve weights | TLT/GLD/UUP proportions preserved when trend sleeve is scaled |
| Beta cap hard floor | `0.90 − 0.20 × stress`, floor 0.50 — re-applied after every RL step |
| Gross cap | 1.50 hard ceiling — unchanged |
| Rebalance cadence | every_2_rebalances — unchanged |
| Feature generation | All features locked |
| Execution model | Cost model, simulator mechanics — unchanged |

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
W_b5_stock  = B.5 stock sleeve weights
W_b5_trend  = B.5 trend sleeve weights (TLT/GLD/UUP)
       │
       ▼
RL Regime Controller (Phase E)
  reads:  macro state + stress + portfolio state + regime features
  outputs: equity_multiplier, trend_multiplier, cash_target
       │
       ▼
Exposure Mixer
  W_equity  = equity_multiplier  × W_b5_stock  (renorm sum preserved)
  W_trend   = trend_multiplier   × W_b5_trend  (renorm sum preserved)
  W_cash    = max(0, 1.0 − sum(W_equity) − sum(W_trend))  (clipped to [0, 0.60])
  normalize to sum = 1.0
       │
       ▼
Optional: apply bounded sector tilt on equity sleeve (±10% total budget)
       │
       ▼
Hard constraints (non-negotiable)
  apply_b4_constraints: beta cap + gross cap (max gross ≤ 1.50)
       │
       ▼
Execution Simulator
```

---

## State Vector

```
obs_dim = 5 (macro) + 1 (stress) + 3 (portfolio exposure state) + 3 (regime momentum) + 2 (portfolio risk state)
        = 14 dimensions  (expand as needed)
```

| Component | Dim | Features | Source |
|---|---|---|---|
| Macro | 5 | VIX 252d percentile, SPY 252d drawdown from peak, yield-curve proxy (TLT−SPY 63d mom), SPY 21d return, SPY 63d return | prices + ^VIX |
| Stress | 1 | Current stress score (B.5 `build_stress_series`) | `build_stress_series` |
| Portfolio exposure state | 3 | Current equity fraction, current trend fraction, current cash fraction | simulator |
| Regime momentum | 3 | 63d realized vol of portfolio, 21d return rolling z-score, 63d return rolling z-score | simulator |
| Portfolio risk state | 2 | Current drawdown from peak NAV, weeks since last rebalance | simulator |

Note: sector vol_score signals (11-dim from Phase D) are dropped — they were inputs to sector tilt
which is now a secondary lever, not the primary action.

---

## Action Space

```
action_dim = 3  (equity_multiplier, trend_multiplier, cash_target)
raw ∈ [−1, +1] (mapped to valid ranges below)
```

| Component | Raw | Applied | Constraint |
|---|---|---|---|
| `equity_multiplier` | [−1, +1] | [0.25, 1.00] | Cannot lever; floor 0.25 prevents full de-risking in single step |
| `trend_multiplier` | [−1, +1] | [0.00, 1.00] | Can go to zero hedge or full hedge |
| `cash_target` | [−1, +1] | [0.00, 0.60] | Max cash 60%; prevents hiding entirely in cash |

After applying all three, the Exposure Mixer normalizes to sum=1.0. The RL action defines
relative proportions, not absolute weights.

---

## Reward Function

```
reward_t = α × sharpe_63d(portfolio_returns)
         + β × drawdown_recovery_bonus(peak_nav, current_nav)
         − γ × max(0, drawdown_63d)
         − δ × |Δ_equity_multiplier|
```

| Term | Coefficient | Rationale |
|---|---|---|
| `sharpe_63d` | α = 1.0 | Longer window (63d vs 21d in Phase D) to capture regime transitions |
| `drawdown_recovery_bonus` | β = 0.10 | Positive reward when portfolio recovers from trough; encourages re-risking |
| `max(0, drawdown_63d)` | γ = 0.15 | Penalises cumulative losses; stronger than Phase D (0.05) because RL now has real de-risking levers |
| `|Δ_equity_multiplier|` | δ = 0.02 | Discourages excessive churn in equity exposure; does not penalise drift |

No raw-return reward. Prevents the agent learning to lever or momentum-chase.
63d window is ~3 months — long enough to see a full regime episode but short enough to give credit signal.

---

## Training / Evaluation Split

| Window | Purpose |
|---|---|
| 2008–2016 | RL training episodes (same as Phase D — includes 2008 crisis, 2010–2013 recovery, 2015–2016 volatility) |
| 2017–2018 | Validation / early stopping |
| 2019–2026-04-24 | **Holdout** — fixed; never touched during training; matches Phase B.5/C/D evaluation window |

---

## Phase E Steps

| Step | Purpose | Output |
|---|---|---|
| E.0 | Baseline (reuse D.0) | `artifacts/reports/phase_d0_holdout_baseline.md` — already exists |
| E.1 | Build Phase E state vector | `src/rl/state_builder_v2.py` |
| E.2 | Build exposure mixing layer | `src/rl/exposure_mix.py` |
| E.3 | Build Phase E RL environment | `src/rl/environment_v2.py` |
| E.4 | Phase E reward function | `src/rl/reward_v2.py` |
| E.5 | PPO training on Phase E env | `scripts/train_rl_v2.py` |
| E.6 | E vs B.5 four-way comparison on holdout | `scripts/run_rl_backtest_v2.py` |

---

## E.6 Four-Way Comparison (mandatory)

| Policy | Description |
|---|---|
| **B.5 locked** | No RL; B.5 harness only |
| **RL no-op** | Equity=1.0, trend=1.0, cash=0.0 (pass-through; same as B.5) |
| **Random bounded** | Random equity_mult ∈ [0.25,1.0], trend_mult ∈ [0.0,1.0], cash ∈ [0.0,0.60]; 50 seeds |
| **Trained Phase E RL** | PPO policy trained on 2008–2016 with Phase E env + reward |

No RL improvement is valid unless it beats both no-op and random baselines.

---

## Promotion Gate

Promote Phase E RL only if **all** of the following hold on 2019–2026-04-24 holdout.

**Locked B.5 holdout benchmark:** Sharpe = `1.270`, MaxDD = `−32.98%`, 50 bps Sharpe = `1.135`.

| Condition | Target |
|---|---|
| Path A — clear Sharpe win | Sharpe ≥ 1.270 AND MaxDD ≥ −32.98% |
| Path B — tail improvement | Sharpe ≥ 1.240 AND MaxDD ≥ −31.48% (i.e. ≥ B.5 holdout + 1.5pp) |
| Either path also requires | 50 bps Sharpe ≥ 0.90 |
| Either path also requires | Beats RL no-op AND random bounded on holdout Sharpe |
| Hard rejections | MaxDD < −35%, OR any beta violation, OR max gross > 1.50 |

Same gate structure as Phase D. Phase E has more room to pass (wider action space) but the bar is the same.

---

## Design Decisions

| Decision | What was rejected | Rationale |
|---|---|---|
| Exposure control (equity/trend/cash) | Sector tilts as primary lever | Phase D showed sector tilts too small to express regime switching |
| action_dim=3 | action_dim=14 (full sector tilt set) | Simpler action → better credit assignment; sector tilt is secondary |
| 63d reward window | 21d (Phase D) | 21d too short to see regime transitions; 63d ≈ one quarter |
| Drawdown recovery bonus | Sharpe-only | Recovery bonus explicitly incentivises re-risking after a drawdown bottom |
| Stronger drawdown penalty (γ=0.15) | γ=0.05 (Phase D) | RL now has full de-risking levers; must be penalised meaningfully for sitting in drawdown |
| Within-sleeve proportions preserved | RL changes stock weights directly | vol_score selects stocks; RL controls exposure level only |
| Cash cap 0.60 | Unlimited cash | Prevents RL hiding entirely in cash to avoid drawdown penalty |
| Equity floor 0.25 | Equity can go to 0 | Prevents catastrophic single-step de-risk; smoother regime transitions |
| Trend multiplier ∈ [0.0, 1.0] | Trend frozen (Phase D) | Trend sleeve is the primary hedge; RL must be able to scale it to get credit for hedging |
| B.4 hard constraints after RL | RL can override beta cap | Non-negotiable |

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-05-02 | Phase D closed | Entry gate cleared | Phase D REJECT — sector tilts too constrained; trained RL could not beat random bounded. B.5 holdout Sharpe `1.270`, MaxDD `−32.98%`. |
| 2026-05-02 | Phase E spec | Agreed | Wider action space: equity/trend/cash exposure control. 63d reward. Recovery bonus. B.5 remains production. |
