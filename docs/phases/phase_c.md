# Phase C — Model Refinement

> **Navigation:** [← Phase B](phase_b.md) | [← ROADMAP](../ROADMAP.md) | Next: [Phase D →](phase_d.md)

**Objective:** Improve LightGBM signal quality (IC Sharpe) via hyperparameter search and feature improvements, then validate that gains flow through the Phase B portfolio construction into better portfolio-level metrics.

**Entry baseline (Phase B.5 promoted, sp500, 2008–2026):**
- Construction: `b4_stress_cap_trend_boost` — every-2-rebalances cadence, dynamic beta cap `0.90 − 0.20 × stress`, beta floor `0.50`, max gross `1.50`
- CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`, turnover `84.12`
- 50 bps Sharpe `0.934`, equal-weight Sharpe (B.1 reference) `0.619`

**Scope constraint:** do not modify `volatility_score` signal logic in a way that changes the Phase B construction without re-running Phase B gates. LightGBM model changes are signal-layer only — the Phase B portfolio harness remains fixed until Phase C validates improvement.

---

## Phase C Goals

| Goal | Target |
|---|---|
| Improve LightGBM IC Sharpe | Holdout IC Sharpe ≥ current baseline (measure first) |
| No overfit signal | IC Sharpe on train window within 20% of holdout |
| Portfolio-level validation | Promoted C candidate must match or improve B.5 Sharpe/MaxDD through Phase B harness |
| Keep RL disabled | RL remains off until Phase D |

---

## Phase C Non-Negotiable Gates

| Gate | Target |
|---|---|
| Holdout IC Sharpe | ≥ Phase B signal baseline (measure first in C.0) |
| Train/holdout IC Sharpe ratio | ≤ 1.20 (overfit check) |
| Portfolio Sharpe through B.5 harness | ≥ 1.05 (maintain or improve) |
| Portfolio MaxDD through B.5 harness | ≥ −35% |
| No new alpha sleeve | Do not add a new model without attribution vs the existing `volatility_score` |

---

## Phase C Steps

| Step | Purpose | Output |
|---|---|---|
| C.0 | Measure Phase B signal IC Sharpe baseline on sp500; establish Phase C floor | IC baseline report |
| C.1 | LightGBM hyperparameter grid search | Best-config report + grid CSV |
| C.2 | Feature attribution / importance pruning | Feature selection report |
| C.3 | Portfolio-level validation of C.1/C.2 winner through Phase B harness | Portfolio validation report |
| C.4 (optional) | Walk-forward retrain frequency sensitivity | Retrain cadence report |

---

## C.1 Hyperparameter Grid

| Param | Values | Count |
|---|---|---|
| `n_estimators` | 50, 100, 200, 300 | 4 |
| `max_depth` | 3, 5, 7 | 3 |
| `num_leaves` | 15, 31, 63 | 3 |
| `learning_rate` | 0.02, 0.05, 0.1 | 3 |
| `min_child_samples` | 20, 50, 100 | 3 |

**Total:** ~486 combinations.

**Parallelism:** use `joblib.Parallel(n_jobs=-1)` to auto-detect available cores. Scale the machine before running — 32+ cores will complete the grid in minutes. Do not hardcode a core count; let `-1` auto-detect so the script is portable across environments.

---

## Architecture

```
C.0: measure baseline IC Sharpe (sp500, current LightGBM config)
C.1: joblib.Parallel(n_jobs=-1)
    └── each job: fit LightGBM on train window → evaluate IC Sharpe on holdout
            ├── train: 2008–2018 (walk-forward, 3yr rolling)
            ├── holdout: 2019–2026-04-24 (same validation end as Phase B)
            └── metric: mean IC Sharpe across holdout dates
C.2: feature importance + pruning on C.1 winner
C.3: run Phase B harness (b4_stress_cap_trend_boost) with C.1/C.2 signal
     compare portfolio metrics vs B.5 baseline
```

### Files to build

| File | Status | Notes |
|---|---|---|
| `scripts/run_phase_c0_signal_baseline.py` | ✅ Merged into C.1 | Baseline IC measured inside `run_phase_c1_lgbm_tuning.py` |
| `scripts/run_phase_c1_lgbm_tuning.py` | ✅ Built | Grid search + IC baseline + portfolio validation in one runner |
| `scripts/run_phase_c2_feature_attribution.py` | ✅ Built + Run | Feature IC attribution, anti-predictive pruning, subset IC experiments, model comparison |
| `scripts/run_phase_c3_portfolio_validation.py` | ✅ Built + Run | Portfolio validation of `simple_mean_rank` (14 features, IC Sharpe=1.8559) — REJECT |

---

## Design Decisions

| Decision | Rationale |
|---|---|
| Evaluate on IC Sharpe, not CAGR | IC Sharpe measures pure signal quality independent of optimizer/risk choices; CAGR conflates alpha quality with portfolio construction |
| Holdout 2019–2026-04-24 | Disjoint from sp100 research window; same clipped end as Phase B to ensure fair comparison |
| joblib `n_jobs=-1` | Auto-detects cores; LightGBM itself is multi-threaded; loky backend handles thread-process interaction cleanly |
| Prune early | If after 50 estimators IC Sharpe < 0.15, skip remaining estimator counts for that `(max_depth, num_leaves)` combo |
| Portfolio gate required | IC improvement must translate to portfolio improvement through the Phase B harness; IC alone is not a promotion criterion |

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-05-01 | Phase B gate cleared | Entry baseline locked | `b4_stress_cap_trend_boost`: CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%` |
| 2026-05-01 | C.1 script written | Ready to run | `scripts/run_phase_c1_lgbm_tuning.py` — 216-combo grid, IC baseline, portfolio validation; run on n2dhighcpu-32 |
| 2026-05-01 | C.1 grid run | **REJECT** | Best: `num_leaves=15, min_data_in_leaf=100, ff=0.6, bf=0.9`. Holdout IC Sharpe=-0.1389, Mean IC=-0.0021. Portfolio: Sharpe=1.029, MaxDD=-29.68%, Turnover=119. Gate failures: 50 bps Sharpe 0.819 (gate ≥0.884), turnover 119 (gate ≤100). Root: LightGBM negative IC on sp500; HPO cannot fix. |
| 2026-05-01 | C.2 feature attribution | **POSITIVE IC FOUND** | 18/32 features anti-predictive. Top: `beta_to_spy_63d` (1.79), `downside_vol_63d` (1.78), `volatility_21d` (1.76). Best model: `simple_mean_rank` (14 features, IC Sharpe=1.8559). Vol_score_standalone=1.6682. LightGBM itself destroys signal regardless of feature selection — max IC with LGBM=1.1960 (4 vol features). |
| 2026-05-01 | C.3 portfolio validation | **REJECT** | `simple_mean_rank` (14 features, IC Sharpe=1.8559): Sharpe=1.050, MaxDD=-33.94%, Turnover=90.5. Both Sharpe gates missed (floor 1.05, preferred 1.078). Root: high-vol/high-beta selections crushed in 2008 crisis (SMR Sharpe=-0.270 vs vol_score 0.542). Only 22% name overlap with vol_score. Keep vol_score as production signal. **Phase C COMPLETE — vol_score carries into Phase D.** |
