# Phase B — Portfolio Stabilization

> **Navigation:** [← Phase A](phase_a.md) | [← ROADMAP](../ROADMAP.md) | Next: [Phase C →](phase_c.md)

**Objective:** turn the A.7.3 stress-scaled volatility/trend expression into a stable portfolio construction path with explicit data-window guards, turnover controls, execution realism, and optimizer/risk integration.

**Entry baseline:** Phase A locked candidate:
`vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`, 10 bps cost.

**Entry metrics on `sp500_dynamic`:**
- CAGR `23.51%`
- Sharpe `1.538`
- MaxDD `-26.36%`
- max gross `1.375`
- min candidate count `128`
- min selected count `20`

**Important scope:** do not modify `volatility_score`, add a new alpha, import historical index membership, or enable RL in Phase B.

---

## Phase B Goals

| Goal | Target |
|---|---|
| Preserve Phase A drawdown profile | sp500 MaxDD stays `<40%` |
| Preserve risk-adjusted return | sp500 Sharpe stays above equal-weight baseline and preferably `>1.0` |
| Control exposure | max gross `<=1.5` unless explicitly testing rejected variants |
| Control turnover/cost | 25-50 bps cost-adjusted Sharpe remains competitive |
| Improve implementation realism | actual simulator/optimizer path matches A.7.3 path closely enough to explain differences |
| Keep attribution clear | each change isolated as data-window, turnover, optimizer, or risk-engine effect |

---

## Phase B.0 — Baseline Guard

**Goal:** lock the Phase A baseline and cleanly define the usable validation window before changing portfolio construction.

### Implementation

| Item | File | Status |
|---|---|---|
| B.0 baseline/data-window guard | `scripts/run_phase_b0_baseline_guard.py` | Implemented |
| Main report | `artifacts/reports/phase_b0_baseline_guard.md` | Done |
| Data-window audit | `artifacts/reports/phase_b0_data_window_guard.csv` | Done |
| Baseline lock | `artifacts/reports/phase_b0_baseline_lock.csv` | Done |

### B.0 Result

Use A.7.3 as the Phase A baseline for Phase B comparisons. Before production-style validation, clip `sp500_dynamic` to `2026-04-24` or rebuild the PIT mask around the trailing zero-active dates observed from `2026-04-27` to `2026-04-29`.

---

## Planned Work

| Step | Purpose | Output |
|---|---|---|
| B.0 | Lock A.7.3 baseline and define valid data window | baseline guard report |
| B.1 | Reproduce A.7.3 candidate in a production-style portfolio runner | simulator-compatible baseline |
| B.2 | Turnover smoothing / rebalance hysteresis | turnover-cost frontier |
| B.3 | Optimizer integration without alpha dilution | optimizer-vs-equal-weight attribution |
| B.4 | Risk overlay integration only if it preserves A.7.3 profile | risk attribution report |
| B.5 | Final Phase B gate run on sp500 | promoted portfolio construction |

---

## Current Open Risks

- Current A.7.x blend runner is return/weight-matrix based, not the main simulator path.
- sp500 PIT mask has three trailing zero-active dates in late April 2026; this is a data-window artifact to clean or clip.
- Regime Sharpe remains weak in 2008 and 2022 even though regime MaxDD passes.
- Historical index-membership data remains intentionally deferred; do not import it unless current-setup artifact checks become fragile.

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-04-30 | B.0 baseline guard | Done | A.7.3 baseline locked; sp500 recommended validation end is `2026-04-24` unless PIT mask is refreshed |
