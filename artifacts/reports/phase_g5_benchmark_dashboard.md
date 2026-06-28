# Phase G.5 — Benchmark Dashboard

**As-of:** 2026-04-24  
**Generated:** 2026-06-28T19:32:07Z  
**Chart window:** 2020-01-01 →  

---

## Data Freshness

| Series | Start | End | Rows | Source | Stale? |
|--------|-------|-----|------|--------|--------|
| RL (E.7) backtest | 2019-01-22 | 2026-04-06 | 1811 | `data/switching/nav_rl_backtest.parquet` | ⚠️ Yes |
| B.5-only backtest | 2019-01-02 | 2026-04-24 | 1838 | `data/switching/nav_b5_backtest.parquet` | ⚠️ Yes |
| SPY prices | 2006-01-03 | 2026-06-26 | 5152 | `data/raw/SPY.parquet` | ✅ No |
| TLT prices | 2006-01-03 | 2026-04-29 | 5112 | `data/raw/TLT.parquet` | ⚠️ Yes |
| Audit trail (live) | 2026-05-09 | 2026-06-28 | 43 | `data/audit/decisions.parquet` | ✅ No |

---

## Performance Summary (Chart Window)

| Series | Start | End | Total Return | Ann. Return | Ann. Vol | Sharpe | Max DD |
|--------|-------|-----|-------------|------------|---------|--------|--------|
| RL (E.7) | 2020-01-02 | 2026-04-06 | 156.5% | 16.3% | 14.4% | 1.136 | -24.5% |
| B.5-only | 2020-01-02 | 2026-04-24 | 206.2% | 19.5% | 17.0% | 1.143 | -33.0% |
| SPY | 2020-01-02 | 2026-04-24 | 140.5% | 15.0% | 20.5% | 0.731 | -33.7% |
| 60/40 | 2020-01-02 | 2026-04-24 | 60.9% | 7.9% | 13.3% | 0.590 | -27.2% |

---

## Rolling 63-Day Metrics (Most Recent)

| Series | Rolling Sharpe | Rolling MaxDD |
|--------|---------------|--------------|
| RL (E.7) | 0.515 | -4.9% |
| B.5-only | 1.027 | -4.8% |
| SPY | 1.083 | -8.9% |
| 60/40 | 0.897 | -6.7% |

---

## Regime Posture (Last 10 Records)

| Date | Mode | Equity | Trend | Cash | Stress | NAV |
|------|------|--------|-------|------|--------|-----|
| 2026-06-17 | `rl_e7` | 25.0% | 72.3% | 2.7% | 0.361 | 1.0000 |
| 2026-06-18 | `rl_e7` | 25.0% | 72.3% | 2.7% | 0.208 | 1.0000 |
| 2026-06-19 | `rl_e7` | 25.0% | 72.3% | 2.7% | 0.208 | 1.0000 |
| 2026-06-22 | `rl_e7` | 25.0% | 72.3% | 2.7% | 0.285 | 1.0000 |
| 2026-06-22 | `rl_e7` | 25.0% | 72.3% | 2.7% | 0.285 | 1.0000 |
| 2026-06-23 | `rl_e7` | 25.0% | 73.5% | 1.5% | 0.418 | 1.0000 |
| 2026-06-24 | `rl_e7` | 25.0% | 73.5% | 1.5% | 0.382 | 1.0000 |
| 2026-06-25 | `rl_e7` | 25.0% | 73.5% | 1.5% | 0.387 | 1.0000 |
| 2026-06-26 | `rl_e7` | 25.0% | 73.5% | 1.5% | 0.379 | 1.0000 |
| 2026-06-28 | `rl_e7` | 25.0% | 73.5% | 1.5% | 0.379 | 1.0000 |

---

## Active Drift Flags (G.3 — Latest Run)

**As-of:** 2026-06-28 00:00:00  
**Status:** ✅ No Alert

| Status | Flag | Value |
|--------|------|-------|
| 🟢 | `sharpe_degradation` | N/A |
| 🟢 | `drawdown_excess` | 0.2448 |
| 🟢 | `cash_trap` | 0.2500 |
| 🟢 | `feature_psi` | N/A |
| 🟢 | `stress_breach` | 0.3786 |

---

