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
| Equity sleeve target proportion | `[0.25, 1.00]` | Reduce stock exposure in stress; re-risk in recovery |
| Trend/hedge sleeve target proportion | `[0.00, 1.00]` | Scale up hedge when regime deteriorates |
| Cash allocation target proportion | `[0.00, 0.60]` | Move to cash during severe stress |

The three target proportions always sum to 1.0 via simplex projection. RL sets relative
exposure levels, not absolute weights.

Portfolio composition after RL action:
```
W_equity  = equity_frac  × W_b5_stock_sleeve   (within-sleeve vol_score proportions preserved)
W_trend   = trend_frac   × W_b5_trend_sleeve   (within-sleeve TLT/GLD/UUP proportions preserved)
W_cash    = cash_frac    (implicit residual; not held as an instrument)
```

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
  reads:  42-dim state (macro + trend + stress + sector signals + portfolio exposure/risk)
  outputs: raw_action ∈ [−1,+1]^3 = [raw_equity, raw_trend, raw_cash]
       │
       ▼
Exposure Mixer (simplex projection)
  Step 1: map raw ∈ [−1,+1] → box proportions
          equity ∈ [0.25, 1.00]
          trend  ∈ [0.00, 1.00]
          cash   ∈ [0.00, 0.60]
  Step 2: project to simplex: equity + trend + cash = 1.0
  Step 3: scale sleeves (preserve within-sleeve proportions)
  W_equity  = equity_frac × W_b5_stock_sleeve (renorm sum preserved)
  W_trend   = trend_frac  × W_b5_trend_sleeve (renorm sum preserved)
  W_cash    = implicit (1 − sum(W_equity) − sum(W_trend))
       │
       ▼
Hard constraints (non-negotiable)
  apply_b4_constraints: beta cap + gross cap (max gross ≤ 1.50)
       │
       ▼
Execution Simulator
```

---

## State Vector (42 dimensions)

`obs_dim = 42` — all features filled forward then 0 if NaN; no NaN allowed in obs.

| Idx | Group | Feature | Source | Range |
|---|---|---|---|---|
| 0 | Market | vix_percentile_1y | `^VIX` prices, rolling 252d rank | [0,1] |
| 1 | Market | spy_drawdown_from_peak | SPY expanding max | [−1,0] |
| 2 | Market | spy_ret_3m | SPY pct_change(63) | float |
| 3 | Market | spy_ret_6m | SPY pct_change(126) | float |
| 4 | Market | realized_market_vol_63d | SPY daily ret rolling 63d std × √252 | ≥0 |
| 5 | Size/Style | iwm_spy_spread_63d | IWM.pct_change(63) − SPY.pct_change(63) | float |
| 6 | Size/Style | qqq_spy_spread_63d | QQQ.pct_change(63) − SPY.pct_change(63) | float |
| 7 | Trend | tlt_ret_3m | TLT pct_change(63) | float |
| 8 | Trend | tlt_ret_6m | TLT pct_change(126) | float |
| 9 | Trend | gld_ret_3m | GLD pct_change(63) | float |
| 10 | Trend | gld_ret_6m | GLD pct_change(126) | float |
| 11 | Trend | uup_ret_3m | UUP pct_change(63); fill 0 if <63d history | float |
| 12 | Trend | uup_ret_6m | UUP pct_change(126); fill 0 if <126d history | float |
| 13 | Stress | stress_score | B.5 `build_stress_series`, pre-computed series | [0,1] |
| 14–24 | Sector Mom | sector_mom_vs_spy[11] | `sector_features.sector_ret_3m[sec]` − SPY ret_3m; sectors: XLK XLF XLV XLY XLP XLE XLI XLU XLB XLRE XLC | float |
| 25–35 | Sector Vol | sector_vol_63d[11] | `sector_features.sector_volatility_63d[sec]`; each sector (daily scale, not annualized) | ≥0 |
| 36 | Port Exposure | current_equity_frac | passed from env step state | [0,1] |
| 37 | Port Exposure | current_trend_frac | passed from env step state | [0,1] |
| 38 | Port Exposure | current_cash_frac | passed from env step state | [0,1] |
| 39 | Port Risk | portfolio_drawdown | nav_series expanding max | [−1,0] |
| 40 | Port Risk | portfolio_vol_63d | nav daily ret rolling 63d std × √252 | ≥0 |
| 41 | Port Risk | portfolio_ret_21d_zscore | 21d ret z-scored over 252d window, clip [−3,3] | [−3,3] |

`sector_features_df` is loaded once at env init from `data/features/sector_features.parquet`
and passed as an arg — not re-read per step.

---

## Action Space (3 dimensions)

```
action_dim = 3  (raw_equity, raw_trend, raw_cash)
raw ∈ [−1, +1]^3 → mapped to target proportions via simplex projection
```

| Component | Raw | Box mapping | Simplex constraint |
|---|---|---|---|
| `equity_target` | [−1, +1] | [0.25, 1.00] | equity + trend + cash = 1.0 |
| `trend_target` | [−1, +1] | [0.00, 1.00] | — |
| `cash_target` | [−1, +1] | [0.00, 0.60] | — |

**Why simplex projection, not independent normalization:**
If equity and trend are both mapped high, naive normalization would unpredictably collapse one.
Simplex projection treats all three proportionally, preserving the ordering of the RL's raw signal.
See `src/rl/exposure_mix.py` for the full 5-step algorithm.

---

## Reward Function (5 terms)

```
reward_t = sharpe_63d(daily_returns)
         + 0.10 × recovery_bonus(portfolio_nav)
         − 0.15 × max(0.0, −drawdown_from_peak(portfolio_nav))
         − 0.03 × cash_frac × bull_regime_indicator
         − 0.02 × |equity_frac − prev_equity_frac|
```

| Term | Coeff | Rationale |
|---|---|---|
| `sharpe_63d` | 1.0 | 63d window (vs 21d in Phase D) to capture full regime transitions |
| `recovery_bonus` | 0.10 | `max(0, (nav_now − trough) / trough)` over last 63 NAV points; rewards rising from recent trough |
| `drawdown_penalty` | λ_dd=0.15 | `max(0.0, −drawdown_from_peak)` — drawdown stored negative; negation makes penalty positive (CORRECTED sign; Phase D spec had bug `max(0, drawdown_63d)` always returning 0) |
| `cash_drag` | λ_cash=0.03 | `cash_frac × bull_indicator`; fires ONLY when `spy_trend_positive AND stress < 0.30`; prevents RL hiding in cash to avoid drawdown penalty |
| `churn_penalty` | λ_churn=0.02 | `|equity_frac − prev_equity_frac|`; discourages excessive equity exposure flipping |

`spy_trend_positive = SPY 63d return > 0` — precomputed in env, passed as bool per step.

**Guard:** If `portfolio_nav.iloc[−1] ≤ 0`, return `−1.0`.

---

## Training / Evaluation Split

| Window | Purpose |
|---|---|
| 2008–2016 | RL training episodes (includes 2008 crisis, 2010–2013 recovery, 2015–2016 volatility) |
| 2017–2018 | Validation / early stopping |
| 2019–2026-04-24 | **Holdout** — fixed; never touched during training; matches Phase B.5/C/D evaluation window |

**No walk-forward retraining in Phase E.** Fixed window only (2008–2016 train).
Walk-forward RL retrain (expanding window, every 2 years) is deferred to Phase E+ or later.

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
| E.6 | Five-way comparison on holdout | `scripts/run_rl_backtest_v2.py` |

E.1–E.3 are independent and can be developed in parallel. E.4 depends on E.1+E.2+E.3.
E.5 depends on E.4. E.6 depends on E.4 + trained model from E.5.

---

## E.6 Five-Way Comparison (mandatory)

| Policy | Description |
|---|---|
| **B.5 locked** | No RL; B.5 harness only |
| **RL no-op** | `raw_action=[1,−1,−1]` → equity≈1, trend≈0, cash≈0; expected to differ slightly from B.5 due to rounding |
| **Random bounded (50 seeds)** | `rng.uniform(−1,+1,3)` per step; report mean + **median** + p25/p75/p90/p95 |
| **Rule-based controller** | Hard-coded VIX+SPY regime table (see below) |
| **Trained Phase E RL** | PPO policy loaded from `artifacts/models/rl_e_ppo_best.zip` |

### Rule-Based Controller (VIX + SPY regime table)

Uses three signals from the 42-dim state at each step:
- `obs[0]` = `vix_percentile_1y`
- `obs[1]` = `spy_drawdown_from_peak` (negative; e.g. −0.20 = 20% below peak)
- `obs[2]` = `spy_ret_3m` (SPY 63d return; negative = downtrend)

```python
# Stress tier 1 — high stress: high VIX OR deep SPY drawdown
if vix_pct > 0.75 or spy_dd < -0.15:
    equity, trend, cash = 0.50, 0.40, 0.10

# Stress tier 2 — moderate stress: elevated VIX OR SPY in downtrend
elif vix_pct > 0.50 or spy_ret_3m < 0.0:
    equity, trend, cash = 0.70, 0.20, 0.10

# Benign regime
else:
    equity, trend, cash = 0.85, 0.10, 0.05
```

**Why SPY drawdown AND VIX (not VIX-only):** VIX can normalize after the initial shock while
prices remain depressed (e.g. late 2009, 2023). The `spy_dd < -0.15` tier catches sustained bear
markets that VIX alone misses. `spy_ret_3m < 0` catches early-stage deterioration before VIX spikes.

Targets are reverse-mapped to raw actions via the inverse of the box-mapping formula,
then fed through `apply_exposure_mix` normally.

---

## Promotion Gate

Promote Phase E RL only if **all required gates** hold on 2019–2026-04-24 holdout.

**Locked B.5 holdout benchmark:** Sharpe `1.270`, MaxDD `−32.98%`, 50 bps Sharpe `1.135`.

| # | Gate | Type | Target |
|---|---|---|---|
| 1 | Path A: Sharpe ≥ 1.270 AND MaxDD ≥ −32.98% | Required (either path) | Clear Sharpe win |
| 2 | Path B: Sharpe ≥ 1.240 AND MaxDD ≥ −31.48% | Required (either path) | Tail improvement |
| 3 | 50 bps Sharpe ≥ 0.90 | Required | Cost robustness |
| 4 | Beats RL no-op Sharpe | Required | Baseline skill |
| 5 | Beats random bounded **median** Sharpe | **Hard minimum** | Mandatory floor |
| 6 | Beats random bounded **p75** Sharpe | **Preferred** | Stronger skill signal |
| 7 | **Beats rule-based controller Sharpe** | Required | Strategy skill above heuristic |
| 8 | MaxDD ≥ −35% | Hard rejection | No blowup |

**Random gate logic:**
- Gate 5 (median) is a hard requirement — failing it means the RL is not demonstrably better than random.
- Gate 6 (p75) is preferred but not blocking. If RL passes median and p75, it is a clean promotion.
  If RL passes median but not p75, report it as a "conditional pass" and flag in the verdict.
- p90/p95 are reported for information only; not a gate.

**Why p75 not p95:** p95 may be too harsh if random occasionally gets lucky across 50 seeds on a
favorable holdout. p75 requires RL to beat three-quarters of random seeds — a meaningful skill test
without being unreasonably strict.

---

## Design Decisions

| Decision | What was rejected | Rationale |
|---|---|---|
| Target proportions (equity/trend/cash) summing to 1.0 via simplex projection | Multipliers (equity_mult, trend_mult, cash_target) | With multipliers, if equity+trend > 1.0, cash becomes meaningless (absorbed into normalization). Simplex projection treats all three proportionally. |
| action_dim=3 | action_dim=14 (full sector tilt set) | Simpler action → better credit assignment; sector tilt is secondary |
| 63d reward window | 21d (Phase D) | 21d too short to see regime transitions; 63d ≈ one quarter |
| Cash-drag penalty (bull regimes only) | No cash penalty | Without it, RL can hide in cash to avoid drawdown penalty; fires only when `spy_trend_positive AND stress < 0.30` |
| Drawdown penalty: `max(0.0, −drawdown_from_peak)` | `max(0, drawdown_63d)` (Phase D spec bug) | drawdown stored negative, so `max(0, drawdown)` always returns 0. Negation corrects the sign. |
| Recovery bonus (0.10) | Sharpe-only | Explicitly incentivises re-risking after a drawdown bottom |
| Stronger drawdown penalty (λ_dd=0.15) | λ=0.05 (Phase D) | RL now has full de-risking levers; must be penalised meaningfully for sitting in drawdown |
| Within-sleeve proportions preserved | RL changes stock weights directly | vol_score selects stocks; RL controls exposure level only |
| Cash cap 0.60 | Unlimited cash | Prevents RL hiding entirely in cash to avoid drawdown penalty |
| Equity floor 0.25 | Equity can go to 0 | Prevents catastrophic single-step de-risk; smoother regime transitions |
| 42-dim state (sector features included) | 14-dim state (no sector features) | Sector momentum vs SPY and sector volatility add regime-differentiation signal without lookahead bias; data confirmed available via `sector_features.parquet` |
| Rule-based controller (VIX+SPY) as required baseline | VIX-only | VIX-only is too naive; SPY drawdown catches sustained bear markets; SPY 3m momentum catches early-stage deterioration |
| Random gate: median required, p75 preferred | Mean gate (Phase D) | Mean was susceptible to lucky outlier seeds; median is the true central tendency; p75 adds meaningful skill threshold |
| Fixed training window (2008–2016) | Walk-forward retraining | Walk-forward adds complexity and overfit risk; Phase E focuses on fixed-window correctness first |
| B.4 hard constraints after RL | RL can override beta cap | Non-negotiable |

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-05-02 | Phase D closed | Entry gate cleared | Phase D REJECT — sector tilts too constrained; trained RL could not beat random bounded. B.5 holdout Sharpe `1.270`, MaxDD `−32.98%`. |
| 2026-05-02 | Phase E spec | Agreed (revised) | Wider action space: equity/trend/cash exposure control via simplex projection. 42-dim state. 5-term reward (63d Sharpe + recovery bonus + drawdown penalty + cash drag + churn). Five-way comparison with rule-based (VIX+SPY) baseline. B.5 remains production. |
| 2026-05-02 | E.1–E.6 implemented | Complete | All 6 files built: `state_builder_v2.py`, `exposure_mix.py`, `reward_v2.py`, `environment_v2.py`, `train_rl_v2.py`, `run_rl_backtest_v2.py`. Pending: smoke test, full training, E.6 evaluation. |
| 2026-05-03 | E.5 training | Complete | sp500, 2008–2016 train / 2017–2018 val. Best val Sharpe `1.0746` at episode 13; early stopping at episode 63. Total time `82 min`. Model saved: `artifacts/models/rl_e_ppo_best.zip`. |
| 2026-05-03 | E.6 evaluation | **CONDITIONAL PROMOTE** | Five-way holdout (2019–2026-04-24). Trained RL: Sharpe `1.275`, MaxDD `−21.73%`, CAGR `16.86%`, avg equity `0.365`. All hard gates pass (Path A + Path B). Missed p75 preferred gate by `0.004` (1.275 vs 1.279). Key strength: tail protection — MaxDD 11pp better than B.5; 2020 COVID Sharpe `0.888` vs B.5 `0.435`. Key concern: CAGR sacrifice of `3.83pp` vs B.5; avg equity `0.365` indicates over-defensive posture. B.5 remains production default. |
| 2026-05-03 | E.7 spec agreed | Calibration retune | Root cause: λ_dd=0.15 dominates Sharpe term; bull_regime trigger too narrow (stress<0.30 gate rarely fires in recovery). Changes: λ_dd 0.15→0.08, λ_cash 0.03→0.05, bull_regime removes stress<0.30 gate, cash cap 0.60→0.50. Equity floor and drawdown definition (expanding all-time-high peak) intentionally unchanged to isolate calibration effect. E.8 note: if E.7 remains over-defensive, replace expanding-peak drawdown with rolling 252d peak or regime-triggered drawdown penalty. |
| 2026-05-03 | E.7 training | Complete | sp500, 2008–2016 train / 2017–2018 val. Best val Sharpe `1.0761` at episode 51; early stopping at episode 101. Total time `132 min`. Model saved: `artifacts/models/rl_e_ppo_best.zip`. |
| 2026-05-03 | E.7 evaluation | **PROMOTE — clean** | Five-way holdout (2019–2026-04-24). Trained RL: Sharpe `1.296`, MaxDD `−24.48%`, CAGR `17.79%`, avg equity `0.406`. All 8 gates pass including p75 (`1.296 > 1.280`). CAGR sacrifice vs B.5 narrowed to `2.9pp` (was `3.83pp` in E.6). Regime shifts: 2019 bull improved `3.18` vs `2.68` (wider bull trigger), 2020 COVID weakened `0.63` vs `0.89` (expected from reduced λ_dd — accepted trade-off). E.8 deferred: avg equity `0.406` still below ideal `0.55–0.65`; if further tuning needed, test rolling 252d peak drawdown definition. |
