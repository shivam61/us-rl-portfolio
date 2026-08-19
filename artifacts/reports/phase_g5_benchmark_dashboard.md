# Phase G.5 — Benchmark Dashboard

**As-of:** 2026-04-24  
**Generated:** 2026-08-19T16:28:47Z  
**Chart window:** 2020-01-01 →  

---

## Data Freshness

| Series | Start | End | Rows | Source | Stale? |
|--------|-------|-----|------|--------|--------|
| RL (E.7) backtest | 2019-01-22 | 2026-04-06 | 1811 | `data/switching/nav_rl_backtest.parquet` | ⚠️ Yes |
| B.5-only backtest | 2019-01-02 | 2026-04-24 | 1838 | `data/switching/nav_b5_backtest.parquet` | ⚠️ Yes |
| SPY prices | 2006-01-03 | 2026-08-19 | 5189 | `data/raw/SPY.parquet` | ✅ No |
| TLT prices | 2006-01-03 | 2026-08-19 | 5189 | `data/raw/TLT.parquet` | ✅ No |
| Audit trail (live) | 2026-05-09 | 2026-08-18 | 81 | `data/audit/decisions.parquet` | ✅ No |

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
| 2026-08-06 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.069 | 50000.0200 |
| 2026-08-07 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.045 | 50000.0000 |
| 2026-08-10 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.088 | 49999.9900 |
| 2026-08-11 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.076 | 49999.9800 |
| 2026-08-12 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.029 | 50000.0000 |
| 2026-08-13 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.031 | 50000.0000 |
| 2026-08-13 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.031 | 50000.0000 |
| 2026-08-14 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.024 | 50000.0000 |
| 2026-08-17 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.081 | 49999.9600 |
| 2026-08-18 | `b5_only` | 25.0% | 69.2% | 5.8% | 0.141 | 49999.9800 |

---

## Active Drift Flags (G.3 — Latest Run)

**As-of:** 2026-08-18 00:00:00  
**Status:** ✅ No Alert

| Status | Flag | Value |
|--------|------|-------|
| 🟢 | `sharpe_degradation` | 0.7040 |
| 🟢 | `drawdown_excess` | 0.2399 |
| 🟢 | `cash_trap` | 0.2500 |
| 🔴 | `feature_psi` | 8.6185 |
| 🟢 | `stress_breach` | 0.1409 |

---

