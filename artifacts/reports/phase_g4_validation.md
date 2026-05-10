# Phase G.4 — Historical Validation Report

**Generated:** 2026-05-10T05:55:46Z  

## Test Summary

| Test | Window | Status | Mode | Reason |
|------|--------|--------|------|--------|
| ✅ 2020-03 COVID crash — RL outperformance | 2020-01-01 to 2020-06-30 | **PASS** | `rl_e7` | no_trigger_all_within_bounds |
| ✅ 2022-01 rate shock onset — RL degradation | 2021-10-01 to 2022-03-31 | **PASS** | `b5_only` | sharpe_degradation: rolling_sharpe=-0.723 vs floor=1.196 (re |
| ✅ 2025-04 recovery phase — RL recovery | 2025-01-01 to 2026-01-31 | **PASS** | `rl_e7` | recovery: flags_quiescent_for=181d (need≥10d) + rl_paper_sha |

---

## Test Details

### 2020-03 COVID crash — RL outperformance

**Window:** 2020-01-01 to 2020-06-30  
**Expected:** stay rl_e7 (RL outperformed B.5 during COVID)  
**Actual mode:** `rl_e7`  
**Actual reason:** no_trigger_all_within_bounds  
**Gate:** PASS ✅  

**Diagnostics:**
- Audit records: 125
- Drift flag records: 116

### 2022-01 rate shock onset — RL degradation

**Window:** 2021-10-01 to 2022-03-31  
**Expected:** rl_e7 → b5_only (sharpe degradation)  
**Actual mode:** `b5_only`  
**Actual reason:** sharpe_degradation: rolling_sharpe=-0.723 vs floor=1.196 (ref=1.296 + -0.100); days_below=63 (flag_at≥21d)  
**Gate:** PASS ✅  

**Diagnostics:**
- Audit records: 126
- Drift flag records: 117

### 2025-04 recovery phase — RL recovery

**Window:** 2025-01-01 to 2026-01-31  
**Expected:** b5_only → rl_e7 (flags quiescent, RL recovered)  
**Actual mode:** `rl_e7`  
**Actual reason:** recovery: flags_quiescent_for=181d (need≥10d) + rl_paper_sharpe=1.857 vs b5_rolling=1.811 (delta=+0.046, need≥-0.050)  
**Gate:** PASS ✅  

**Diagnostics:**
- Audit records: 270
- Drift flag records: 261

---

**Overall gate:** PASS if all 3 tests pass individually.
