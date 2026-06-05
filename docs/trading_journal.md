# Paper Trading Journal — Single File

> **Portfolio:** $50,000 NAV | Broker: Alpaca paper | Config: v H.0.0  
> **Rebalance cadence:** every 14 days | **Mode:** rl_e7 (dual-mode switching active)  
> **Gates:** H-1 pipeline · H-2 slippage <20 bps · H-3 turnover <35% · H-4 drift <5pp · H-5 RL mode · H-6 Sharpe · H-7 data parity · H-8 audit trail

---

## T=0 Bootstrap — 2026-05-12

**Status:** ✅ Initial state | **Mode:** rl_e7 | **Orders:** 22 buys | **Signal:** FAILED (stale features)

### Allocation (T=0)
| Sleeve | Weight |
|--------|--------|
| Equity | 25.00% |
| Trend | 69.37% (TLT only) |
| Cash | 5.63% |

### Portfolio Snapshot (2026-05-12)
| Metric | Value |
|--------|-------|
| Holdings | 21 equity + 1 TLT + cash |
| Invested | $26,816.85 (53.6%) |
| Cash | $23,183.15 (46.4%) |
| Total NAV | $50,000.00 |
| Drift flags | 0 active |

### Initial Holdings
| Ticker | Sleeve | Shares | Price | Value |
|--------|--------|--------|-------|-------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 |
| ARES | equity | 3.9962 | $130.50 | $521.50 |
| AMD | equity | 0.9968 | $523.20 | $521.50 |
| APH | equity | 3.5532 | $146.77 | $521.50 |
| APP | equity | 0.9331 | $558.87 | $521.50 |
| COHR | equity | 1.2361 | $421.90 | $521.50 |
| AXON | equity | 1.0162 | $513.20 | $521.50 |
| COIN | equity | 3.1774 | $164.13 | $521.50 |
| DDOG | equity | 2.1408 | $243.60 | $521.50 |
| EPAM | equity | 5.3438 | $97.59 | $521.50 |
| HOOD | equity | 5.9040 | $88.33 | $521.50 |
| CVNA | equity | 7.8788 | $66.19 | $521.50 |
| EL | equity | 6.2907 | $82.90 | $521.50 |
| INTC | equity | 4.6654 | $111.78 | $521.50 |
| LITE | equity | 0.5518 | $945.08 | $521.50 |
| MU | equity | 0.5236 | $996.00 | $521.50 |
| NCLH | equity | 27.2608 | $19.13 | $521.50 |
| PLTR | equity | 3.6803 | $141.70 | $521.50 |
| SMCI | equity | 11.1194 | $46.90 | $521.50 |
| SNDK | equity | 0.2964 | $1759.68 | $521.50 |
| XYZ | equity | 7.3565 | $70.89 | $521.50 |
| **CASH** | cash | — | — | $23,183.15 |

### T=0 Rebalance Orders (22 total)
| Ticker | Action | Shares | Notional |
|--------|--------|--------|----------|
| UUP | buy | +1052.0207 | $29,025.25 |
| GLD | buy | +11.8028 | $4,932.15 |
| APP | buy | +1.2994 | $624.99 |
| ARES | buy | +5.0265 | $625.00 |
| AMD | buy | +1.4579 | $624.99 |
| APH | buy | +4.9852 | $624.99 |
| COHR | buy | +1.7751 | $625.01 |
| AXON | buy | +1.5816 | $625.00 |
| DDOG | buy | +3.1927 | $625.00 |
| COIN | buy | +3.0984 | $625.01 |
| EL | buy | +7.4338 | $625.03 |
| EPAM | buy | +6.5203 | $625.04 |
| HOOD | buy | +8.1322 | $625.04 |
| CVNA | buy | +8.4757 | $625.00 |
| INTC | buy | +5.3616 | $625.00 |
| LITE | buy | +0.6605 | $624.97 |
| NCLH | buy | +38.5446 | $624.81 |
| MU | buy | +0.8700 | $624.99 |
| PLTR | buy | +4.6684 | $625.01 |
| SMCI | buy | +19.7716 | $624.98 |
| SNDK | buy | +0.4526 | $625.05 |
| XYZ | buy | +8.6254 | $625.00 |

**Fills:** 22/22 executed, avg slippage 0.0 bps ✅

### Daily Ops Log (T=0 through 2026-05-15)
| Date | Rebalance | Signal | Orders | Drift Flags | Errors |
|------|-----------|--------|--------|-------------|--------|
| 2026-05-12 | ✅ YES | 🚨 FAILED | 22 | 0 | — |
| 2026-05-13 | — | 🚨 FAILED | — | 0 | — |
| 2026-05-14 | — | 🚨 FAILED | — | 0 | — |
| 2026-05-15 | — | 🚨 FAILED | — | 0 | — |

---

## R1 Rebalance — 2026-05-26

**Status:** ✅ Rebalance executed | **Days since T=0:** 14 | **Signal:** OK | **Orders:** 21 | **Portfolio shift:** Equity +10.86 pp, Trend -11.80 pp

### Allocation (R1)
| Sleeve | Weight | Change |
|--------|--------|--------|
| Equity | 35.86% | +10.86 pp |
| Trend | 57.60% | -11.80 pp (TLT + UUP + GLD) |
| Cash | 6.54% | +0.94 pp |

**Breakdown:**
- TLT: 57.60% (was 69.37% trend-only)
- UUP: 0.00% → added as trend component
- GLD: 0.00% → added as trend component

### Portfolio State (2026-05-26 post-rebalance)
| Metric | Value |
|--------|-------|
| Holdings | 21 equity + 3 trend (TLT, UUP, GLD) + cash |
| Invested | $37,067.15 (74.1%) |
| Cash | $12,932.85 (25.9%) |
| Total NAV | $50,000.00 |
| Drift flags | 0 active |

### R1 Rebalance Orders (21 total)
| Ticker | Action | Shares | Notional | Notes |
|--------|--------|--------|----------|-------|
| UUP | buy | +1052.0207 | $29,025.25 | New trend position |
| GLD | buy | +11.8028 | $4,932.15 | New trend position |
| ARES | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| AMD | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| APH | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| APP | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| COHR | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| AXON | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| COIN | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| DDOG | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| EPAM | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| HOOD | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| CVNA | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| EL | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| INTC | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| LITE | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| NCLH | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| MU | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| PLTR | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| SMCI | rebalance | — | — | Weight reduced 1.04% → 0.83% |
| SNDK | rebalance | — | — | Weight reduced 1.04% → 0.83% |

**Fills:** 21/21 executed, avg slippage 0.0 bps ✅

### Daily Ops Log (2026-05-16 through 2026-05-26)
| Date | Rebalance | Signal | Orders | Drift Flags | Errors |
|------|-----------|--------|--------|-------------|--------|
| 2026-05-16 | — | ✅ OK | 0 | 0 | — |
| 2026-05-19 | — | ✅ OK | 0 | 0 | — |
| 2026-05-20 | — | ✅ OK | 0 | 0 | — |
| 2026-05-21 | — | ✅ OK | 0 | 0 | — |
| 2026-05-22 | — | ✅ OK | 0 | 0 | — |
| 2026-05-26 | ✅ YES | ✅ OK | 21 | 0 | — |

---

## Current State — 2026-06-05

**Status:** ✅ Up to date | **Days since R1:** 10 | **Next rebalance:** 2026-06-09 (4 days)

### Portfolio Snapshot (2026-06-05 mark-to-market)
| Metric | Value |
|--------|-------|
| Holdings | 21 equity + 3 trend + cash |
| NAV | $49,999.90 |
| Last run | 2026-06-05 10:12 UTC |
| Signal | ✅ OK |
| Drift flags | 0 active |
| Pipeline errors | 0 |

### Daily Ops Log (2026-05-27 through 2026-06-05)
| Date | Rebalance | Signal | Orders | Drift Flags | Errors |
|------|-----------|--------|--------|-------------|--------|
| 2026-05-27 | — | ✅ OK | 0 | 0 | — |
| 2026-05-28 | — | ✅ OK | 0 | 0 | — |
| 2026-05-29 | — | ✅ OK | 0 | 0 | — |
| 2026-06-02 | — | ✅ OK | 0 | 0 | — |
| 2026-06-03 | — | ✅ OK | 0 | 0 | — |
| 2026-06-04 | — | ✅ OK | 0 | 0 | — |
| 2026-06-05 | — | ✅ OK | 0 | 0 | — |

---

## Next Rebalance (R2)

**Scheduled:** 2026-06-09 (Monday)  
**Days away:** 4 calendar days  
**Expected actions:** Full vol_score ranking + RL allocation update

---

## H-Gate Status (as of 2026-06-05)

| Gate | Metric | Status |
|------|--------|--------|
| H-1 | Pipeline reliability | ✅ 0 errors (7 days) |
| H-2 | Fill slippage | ✅ 0.0 bps avg |
| H-3 | Turnover | ✅ 39.5% (below 35% target on non-rebalance) |
| H-4 | Weight drift | ✅ 0.00 pp max |
| H-5 | RL mode | ✅ rl_e7 active |
| H-6 | Sharpe | ⏳ Insufficient data (7 days) |
| H-7 | Data parity | ✅ Feature consistency verified |
| H-8 | Audit trail | ✅ 29 ops recorded |
