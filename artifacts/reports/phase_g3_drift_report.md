# Phase G.3 — Drift Monitor Report

**As-of:** 2026-08-18  
**Generated:** 2026-08-19T16:28:32Z  
**Mode:** live  

## ✅ No Alert

> All drift flags within normal bounds — RL policy operating in-distribution.

## Flag Summary

**Active flags:** 1 / 5

| Status | Flag | Value | Threshold | Detail |
|--------|------|-------|-----------|--------|
| 🟢 | `sharpe_degradation` | 0.7040 | -0.0500 | Rolling Sharpe=2.000 vs B.5 ref 1.296 (delta=+0.704); days below 1.246 = 0 (flag at ≥21d) |
| 🟢 | `drawdown_excess` | 0.2399 | -0.0500 | Live MaxDD=-0.5% vs B.5 ref -24.5% (excess=-24.0%; flag at >5%) |
| 🟢 | `cash_trap` | 0.2500 | 0.2500 | equity_frac=0.250 (threshold=0.25); consecutive rebalances below threshold = 0 (flag at ≥10) |
| 🔴 | `feature_psi` | 8.6185 | 0.2000 | Max PSI=8.618 on 'realized_market_vol_63d' (threshold=0.20); by feature: vix_percentile_1y=6.350, realized_market_vol_63d=8.618, stress_score=5.149 |
| 🟢 | `stress_breach` | 0.1409 | 0.7000 | stress_score=0.141 (threshold=0.70); consecutive days above threshold = 0 (flag at ≥5d) |

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
