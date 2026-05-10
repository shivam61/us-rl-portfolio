# Phase H — Paper Trading Journal

> **Portfolio:** $50,000 NAV | Broker: Alpaca paper | Config: v H.0.0
> **Rebalance cadence:** every 14 days | **Mode:** rl_e7 (dual-mode switching active)
> **Gates:** H-1 pipeline · H-2 slippage <20 bps · H-3 turnover <35% · H-4 drift <5pp · H-5 RL mode · H-6 Sharpe · H-7 data parity · H-8 audit trail

Newest entries at the top. Updated automatically by `scripts/generate_paper_journal.py`.

---

## 2026-05-09

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `rl_e7` |
| Rebalance day | no |
| Signal | ✅ OK |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Allocation
| Sleeve | Weight |
|--------|--------|
| Equity | 25.00% |
| Trend | 62.14% |
| Cash | 12.86% |

**Trend breakdown:**
- GLD: 9.02%
- UUP: 53.11%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 22 positions + cash |
| Invested | $49,999.99 (100.0% of NAV) |
| Cash | $0.01 (0.0% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 1104.6016 | $27.59 | $30,475.96 | 60.95% | 60.95% | +0.000 |
| GLD | trend | 12.3926 | $417.88 | $5,178.63 | 10.36% | 10.36% | +0.000 |
| APP | equity | 1.5308 | $468.55 | $717.27 | 1.43% | 1.43% | +0.000 |
| ARES | equity | 5.6813 | $126.25 | $717.27 | 1.43% | 1.43% | +0.000 |
| AMD | equity | 1.5758 | $455.19 | $717.27 | 1.43% | 1.43% | +0.000 |
| APH | equity | 5.6024 | $128.03 | $717.27 | 1.43% | 1.43% | +0.000 |
| COHR | equity | 2.1394 | $335.26 | $717.27 | 1.43% | 1.43% | +0.000 |
| AXON | equity | 1.7774 | $403.54 | $717.27 | 1.43% | 1.43% | +0.000 |
| DDOG | equity | 3.5835 | $200.16 | $717.27 | 1.43% | 1.43% | +0.000 |
| COIN | equity | 3.5657 | $201.16 | $717.27 | 1.43% | 1.43% | +0.000 |
| EL | equity | 8.3210 | $86.20 | $717.27 | 1.43% | 1.43% | +0.000 |
| EPAM | equity | 7.2284 | $99.23 | $717.27 | 1.43% | 1.43% | +0.000 |
| HOOD | equity | 9.3116 | $77.03 | $717.27 | 1.43% | 1.43% | +0.000 |
| CVNA | equity | 9.2029 | $77.94 | $717.27 | 1.43% | 1.43% | +0.000 |
| INTC | equity | 5.7418 | $124.92 | $717.27 | 1.43% | 1.43% | +0.000 |
| LITE | equity | 0.7936 | $903.80 | $717.27 | 1.43% | 1.43% | +0.000 |
| NCLH | equity | 41.9948 | $17.08 | $717.27 | 1.43% | 1.43% | +0.000 |
| MU | equity | 0.9604 | $746.81 | $717.27 | 1.43% | 1.43% | +0.000 |
| PLTR | equity | 5.2052 | $137.80 | $717.27 | 1.43% | 1.43% | +0.000 |
| SMCI | equity | 20.2791 | $35.37 | $717.27 | 1.43% | 1.43% | +0.000 |
| SNDK | equity | 0.4591 | $1562.34 | $717.27 | 1.43% | 1.43% | +0.000 |
| XYZ | equity | 9.5828 | $74.85 | $717.27 | 1.43% | 1.43% | +0.000 |
| __CASH__ | cash | — | — | $0.01 | 0.00% | 0.00% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 22 (22 buys, 0 sells) |
| Total notional | $49,999.99 |
| Estimated turnover | 100.0% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +1.5758 | $455.19 | $717.27 |
| APH | buy | +5.6024 | $128.03 | $717.27 |
| APP | buy | +1.5308 | $468.55 | $717.27 |
| ARES | buy | +5.6813 | $126.25 | $717.27 |
| AXON | buy | +1.7774 | $403.54 | $717.27 |
| COHR | buy | +2.1394 | $335.26 | $717.27 |
| COIN | buy | +3.5657 | $201.16 | $717.27 |
| CVNA | buy | +9.2029 | $77.94 | $717.27 |
| DDOG | buy | +3.5835 | $200.16 | $717.27 |
| EL | buy | +8.3210 | $86.20 | $717.27 |
| EPAM | buy | +7.2284 | $99.23 | $717.27 |
| GLD | buy | +12.3926 | $417.88 | $5,178.63 |
| HOOD | buy | +9.3116 | $77.03 | $717.27 |
| INTC | buy | +5.7418 | $124.92 | $717.27 |
| LITE | buy | +0.7936 | $903.80 | $717.27 |
| MU | buy | +0.9604 | $746.81 | $717.27 |
| NCLH | buy | +41.9948 | $17.08 | $717.27 |
| PLTR | buy | +5.2052 | $137.80 | $717.27 |
| SMCI | buy | +20.2791 | $35.37 | $717.27 |
| SNDK | buy | +0.4591 | $1562.34 | $717.27 |
| UUP | buy | +1104.6016 | $27.59 | $30,475.96 |
| XYZ | buy | +9.5828 | $74.85 | $717.27 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 22 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 22 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $455.19 | $455.19 | +0.0 | ✅ |
| APH | buy | $128.03 | $128.03 | +0.0 | ✅ |
| APP | buy | $468.55 | $468.55 | +0.0 | ✅ |
| ARES | buy | $126.25 | $126.25 | +0.0 | ✅ |
| AXON | buy | $403.54 | $403.54 | +0.0 | ✅ |
| COHR | buy | $335.26 | $335.26 | +0.0 | ✅ |
| COIN | buy | $201.16 | $201.16 | +0.0 | ✅ |
| CVNA | buy | $77.94 | $77.94 | +0.0 | ✅ |
| DDOG | buy | $200.16 | $200.16 | +0.0 | ✅ |
| EL | buy | $86.20 | $86.20 | +0.0 | ✅ |
| EPAM | buy | $99.23 | $99.23 | +0.0 | ✅ |
| GLD | buy | $417.88 | $417.88 | +0.0 | ✅ |
| HOOD | buy | $77.03 | $77.03 | +0.0 | ✅ |
| INTC | buy | $124.92 | $124.92 | +0.0 | ✅ |
| LITE | buy | $903.80 | $903.80 | +0.0 | ✅ |
| MU | buy | $746.81 | $746.81 | +0.0 | ✅ |
| NCLH | buy | $17.08 | $17.08 | +0.0 | ✅ |
| PLTR | buy | $137.80 | $137.80 | +0.0 | ✅ |
| SMCI | buy | $35.37 | $35.37 | +0.0 | ✅ |
| SNDK | buy | $1562.34 | $1562.34 | +0.0 | ✅ |
| UUP | buy | $27.59 | $27.59 | +0.0 | ✅ |
| XYZ | buy | $74.85 | $74.85 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

