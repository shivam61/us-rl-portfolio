# Phase G.3 — Drift Monitor Report

**As-of:** 2026-04-20  
**Generated:** 2026-05-05T15:17:29Z  
**Mode:** simulate_breach  

## ⚠️ ALERT ACTIVE

> ALERT: 2 drift flags active simultaneously (cash_trap, stress_breach) — escalate to manual review; consider switching to b5_only mode (G.4 switching rule)

## Flag Summary

**Active flags:** 2 / 5

| Status | Flag | Value | Threshold | Detail |
|--------|------|-------|-----------|--------|
| 🟢 | `sharpe_degradation` | N/A | -0.0500 | Insufficient data (20 records; need ≥65 for 63d rolling Sharpe) |
| 🟢 | `drawdown_excess` | 0.2258 | -0.0500 | Live MaxDD=-1.9% vs B.5 ref -24.5% (excess=-22.6%; flag at >5%) |
| 🔴 | `cash_trap` | 0.2000 | 0.2500 | equity_frac=0.200 (threshold=0.25); consecutive rebalances below threshold = 18 (flag at ≥10) |
| 🟢 | `feature_psi` | N/A | 0.2000 | Insufficient data for PSI (20 records; need ≥73) |
| 🔴 | `stress_breach` | 0.7500 | 0.7000 | stress_score=0.750 (threshold=0.70); consecutive days above threshold = 15 (flag at ≥5d) |

---

## Alert Rule

Alert fires when **any 2 flags co-occur within 5 trading days**.  
Action: escalate to manual review; consider switching to `b5_only` mode (G.4).

## Flag Definitions

| Flag | Metric | Threshold | Window |
|------|--------|-----------|--------|
| `sharpe_degradation` | Rolling 63d live Sharpe < B.5 ref − 0.05 | sustained ≥ 21d | 63d |
| `drawdown_excess` | Live MaxDD exceeds B.5 MaxDD | by > 5pp | expanding |
| `cash_trap` | equity_frac < 0.25 | ≥ 10 consecutive rebalances | — |
| `feature_psi` | PSI on VIX/vol/stress state features | PSI > 0.20 | baseline vs rolling 63d |
| `stress_breach` | stress_score > 0.70 | ≥ 5 consecutive days | — |
