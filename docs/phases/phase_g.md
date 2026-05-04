# Phase G — Paper Trading & Production Hardening

> **Navigation:** [← Phase F](phase_f.md) | [← ROADMAP](../ROADMAP.md)

**Prerequisite:** Phase F.2 must promote (Sharpe ≥ 1.270, all 8 gates pass) before Phase G begins.

**Objective:** Harden the promoted E.7 RL system from a research backtest into a production-ready
allocation engine — deterministic signal generation, reproducible outputs, live drift monitoring,
and a clean dual-mode architecture that can switch between B.5 and RL without manual intervention.

---

## Phase G Overview

| Step | Name | Status | Gate to next |
|------|------|--------|-------------|
| G.0 | Feature Parity Check | ✅ **COMPLETE** (2026-05-04) — max dev 0.00e+00, 30/30 pass | All features match within 1e-6 on last 30 trading days |
| G.1 | Signal Generation Pipeline | ✅ **COMPLETE** (2026-05-04) — dry-run validated; state persistence verified | Signal exports run unattended for 5 consecutive days |
| G.2 | Audit Trail | ⏳ NEXT | Every allocation decision has a queryable record |
| G.3 | Live Drift Monitoring | ⏳ PENDING | Dashboard live; alert fires on simulated breach |
| G.4 | Dual-Mode Allocation | ⏳ PENDING | Mode switch validated on 3 historical transition dates |
| G.5 | Benchmark Dashboard | ⏳ PENDING | Dashboard auto-updates daily |

---

## G.0 — Feature Parity Check

**Status: COMPLETE — PASS (2026-05-04)**

**Objective:** Confirm that the 42-dim RL state vector (computed nightly from live market data)
matches the backtest-computed state exactly. Any silent drift here means the live RL policy
operates on a different input distribution than it was trained on.

**Scope:**
- All 42 features used in `PortfolioEnvV2._build_state()` (or equivalent observation builder)
- Covers: price-derived features (momentum, vol, beta), macro features (VIX, rates), sector
  features, stress score, SPY trend signal, B.5 current weights

**Gate:** Max absolute deviation < 1e-6 on last 30 trading days for all 42 features.

**Results:**

| Metric | Value | Gate | Pass |
|--------|-------|------|------|
| Max global deviation | 0.00e+00 | < 1e-6 | ✅ |
| Total NaN values | 0 | 0 | ✅ |
| Range violations | 0 | 0 | ✅ |
| Steps passing gate | 30 / 30 | 30 / 30 | ✅ |

All deviations exactly zero — `build_state_v2` is fully deterministic and stateless.

**Script:** `scripts/check_feature_parity_g0.py`
**Report:** `artifacts/reports/phase_g0_feature_parity.md`
**Baseline CSVs:** `artifacts/reports/g0_feature_max_dev.csv`, `g0_per_step_deviation.csv` (for G.3 drift baseline)

---

## G.1 — Signal Generation Pipeline

**Status: COMPLETE — validated (2026-05-04)**

**Objective:** Build a scheduled, end-of-day pipeline that:
1. Fetches/updates market data
2. Computes all features and the RL state vector
3. Runs the RL policy deterministically
4. Exports the target allocation (equity/trend/cash fractions + per-stock weights) to a
   standardized output file

**Design constraints:**
- Must be deterministic: same input → same output on repeated runs
- Must handle missing data gracefully (halt with error, not silent NaN propagation)
- Must output both the B.5 allocation and the RL-adjusted allocation in every run
- No live trading integration in G.1 — outputs are for paper trading and audit only

**Output format (per run):**
```json
{
  "as_of_date": "YYYY-MM-DD",
  "mode": "rl_e7" | "b5_only",
  "equity_frac": float,
  "trend_frac": float,
  "cash_frac": float,
  "stock_weights": {"TICKER": float, ...},
  "trend_weights": {"TLT": float, "GLD": float, "UUP": float},
  "rl_state_vector": [float × 42],
  "stress_score": float,
  "spy_trend_positive": bool
}
```

**Gate:** Pipeline runs unattended for 5 consecutive trading days with correct output.

**Script:** `scripts/run_prod_signal.py`

**Validation (2026-05-04):**
- Dry-run at 2026-04-29: mode=rl_e7, is_rebalance=True, equity=25.0%, trend=56.5%, cash=18.5%, stress=0.333, spy_trend=True, n_stocks=20
- Cold-start write at 2026-04-06: is_rebalance=True, equity=25.0%, trend=52.7%, cash=22.3%, stress=0.535, spy_trend=False
- Hold-day check at 2026-04-07 (1 day gap): is_rebalance=False — prior state loaded correctly

State persistence: `data/prod_state/current_state.json` (tracks equity/trend/cash fracs, NAV, last_rebalance_date)
Allocation output: `data/allocations/{YYYY-MM-DD}.json` + `data/allocations/latest.json`

**G.1 gate pending:** 5 consecutive live trading days with correct output — begins once data feed is live.

---

## G.2 — Audit Trail

**Objective:** Every allocation decision is logged with a full input snapshot so it can be
reconstructed, debugged, or audited without re-running the pipeline.

**Requirements:**
- Append-only log (no in-place updates)
- Each record includes: date, mode, full state vector, action taken, resulting allocation,
  reward signal (if computable), any overrides or flags
- Queryable by date range and mode
- Retention: minimum 2 years rolling

**Implementation path:** Parquet-partitioned store under `data/audit/` is sufficient for V1.
Database migration is a G.2+ concern, not a G.2 blocker.

---

## G.3 — Live Drift Monitoring

**Objective:** Detect two classes of degradation in production:

1. **Regime drift** — the market environment shifts outside the training distribution
   (features, stress scores, volatility regime). Signals the RL policy is operating out-of-distribution.

2. **RL policy degradation** — the live strategy's rolling Sharpe or drawdown materially
   underperforms the B.5 baseline. Triggers consideration of switching to B.5-only mode.

**Metrics to monitor (rolling 63d unless noted):**
- Live Sharpe vs B.5 rolling Sharpe (flag if delta < -0.05 sustained 21d)
- Live MaxDD vs B.5 MaxDD (flag if RL MaxDD exceeds B.5 by > 5pp)
- Avg equity fraction (flag if < 0.25 for 10 consecutive rebalances — RL stuck in cash)
- Feature distribution shift (PSI on key state features vs training distribution)
- Stress score trajectory (flag if > 0.70 sustained 5d — potential regime breach)

**Alert rule:** Any two flags co-occurring within 5 trading days → escalate to manual review
and consider switching to B.5-only mode.

---

## G.4 — Dual-Mode Allocation with Switching Rule

**Objective:** The production system can operate in two modes — B.5-only and RL — and can switch
between them based on a quantitative rule. This ensures continuity if the RL policy degrades or
a regime breach occurs.

### Two-Mode Design

| Mode | Description | When to use |
|------|-------------|-------------|
| `b5_only` | B.5 construction only; no RL overlay | Default safe mode; fallback on degradation |
| `rl_e7` | B.5 construction + E.7 RL exposure overlay | When RL is in-distribution and performing |

**Key design principle:** Both modes use the same vol_score signal, the same trend sleeve,
the same beta constraints, and the same rebalance cadence. The only difference is whether the RL
exposure fractions are applied. Switching must be zero-disruption (no forced trades beyond
normal rebalance).

### Switching Rule (V1)

**Switch from `rl_e7` → `b5_only`** when any of:
- Rolling 63d live Sharpe < B.5 baseline Sharpe − 0.10 (sustained ≥ 21 trading days)
- Live MaxDD exceeds B.5 running MaxDD by > 7pp
- Two or more G.3 drift flags co-occur within 5 trading days
- Manual override (always available)

**Switch from `b5_only` → `rl_e7`** when all of:
- G.3 no active flags for ≥ 10 consecutive trading days
- Rolling 63d RL paper-trading Sharpe ≥ B.5 rolling Sharpe − 0.05
- Manual approval (for the initial switch back after any automatic fallback)

**Validation:** The switching rule must be validated on 3 historical transition dates from the
holdout window (2019–2026) before it is considered production-ready. Recommended dates:
- 2020-03 COVID crash onset (RL should de-risk; B.5 fallback should not degrade)
- 2022-01 rate shock onset (stress score spike; drift flags should fire)
- 2023-10 recovery (switch back from b5_only to rl_e7 if paper RL recovered)

---

## G.5 — Benchmark Dashboard

**Objective:** Auto-updating daily dashboard showing live performance of both modes vs benchmarks.

**Contents:**
- Cumulative NAV: RL mode vs B.5-only vs SPY vs 60/40
- Rolling 63d Sharpe: all four series
- Rolling 63d MaxDD
- RL equity fraction over time (regime posture visualization)
- Stress score over time
- Active G.3 drift flags

**Update cadence:** Daily, post-market close, automated via G.1 pipeline output.

---

## Phase G Entry Gate

Before starting G.0:
1. F.2 training complete and all 8 promotion gates pass
2. `rl_e_ppo_best.zip` replaced with clean E.7 checkpoint
3. F.2 results committed to main with ROADMAP.md updated
4. `docs/phases/phase_f.md` F.2 section updated with final results

---

## Open Design Questions (to resolve in G.0/G.1)

- **State vector versioning:** If the 42-dim state is extended, existing checkpoint becomes
  invalid. Need a version tag in the checkpoint filename and audit log.
- **Rebalance cadence in live:** Every-2-rebalances was calibrated on historical data. In live
  operation, define what "every 2 rebalances" means when the rebalance schedule is fixed calendar
  (vs data-driven as in backtest).
- **Cash representation:** In backtest, cash is implicit (no instrument). In live, cash must
  map to a specific instrument (T-bill ETF, money market). Accounting for yield differential.
- **Partial fills / liquidity:** Top-20 from sp500 are large-cap; liquidity is not a concern
  at typical AUM < $50M. Document the AUM ceiling for this assumption.
