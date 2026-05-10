# Phase H — Paper Trading Journal

> **Portfolio:** $50,000 NAV | Broker: Alpaca paper | Config: v H.0.0
> **Rebalance cadence:** every 14 days | **Mode:** rl_e7 (dual-mode switching active)
> **Gates:** H-1 pipeline · H-2 slippage <20 bps · H-3 turnover <35% · H-4 drift <5pp · H-5 RL mode · H-6 Sharpe · H-7 data parity · H-8 audit trail

Newest entries at the top. Updated automatically by `scripts/generate_paper_journal.py`.

---

## 2026-05-09

### Allocation
| Sleeve | Weight |
|--------|--------|
| Equity | 25.00% |
| Trend | 56.52% |
| Cash | 18.48% |

**Trend breakdown:**
- GLD: 14.49%
- UUP: 85.29%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 22 positions + cash |
| Invested | $50,000.04 (100.0% of NAV) |
| Cash | $-0.04 (-0.0% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 1155.8321 | $27.59 | $31,889.41 | 63.78% | 63.78% | +0.000 |
| GLD | trend | 12.9674 | $417.88 | $5,418.83 | 10.84% | 10.84% | +0.000 |
| APP | equity | 1.3544 | $468.55 | $634.59 | 1.27% | 1.27% | +0.000 |
| ARES | equity | 5.0264 | $126.25 | $634.59 | 1.27% | 1.27% | +0.000 |
| AMD | equity | 1.3941 | $455.19 | $634.59 | 1.27% | 1.27% | +0.000 |
| APH | equity | 4.9566 | $128.03 | $634.59 | 1.27% | 1.27% | +0.000 |
| COHR | equity | 1.8928 | $335.26 | $634.59 | 1.27% | 1.27% | +0.000 |
| AXON | equity | 1.5726 | $403.54 | $634.59 | 1.27% | 1.27% | +0.000 |
| DDOG | equity | 3.1704 | $200.16 | $634.59 | 1.27% | 1.27% | +0.000 |
| COIN | equity | 3.1546 | $201.16 | $634.59 | 1.27% | 1.27% | +0.000 |
| EL | equity | 7.3618 | $86.20 | $634.59 | 1.27% | 1.27% | +0.000 |
| EPAM | equity | 6.3951 | $99.23 | $634.59 | 1.27% | 1.27% | +0.000 |
| HOOD | equity | 8.2382 | $77.03 | $634.59 | 1.27% | 1.27% | +0.000 |
| CVNA | equity | 8.1420 | $77.94 | $634.59 | 1.27% | 1.27% | +0.000 |
| INTC | equity | 5.0800 | $124.92 | $634.59 | 1.27% | 1.27% | +0.000 |
| LITE | equity | 0.7021 | $903.80 | $634.59 | 1.27% | 1.27% | +0.000 |
| NCLH | equity | 37.1539 | $17.08 | $634.59 | 1.27% | 1.27% | +0.000 |
| MU | equity | 0.8497 | $746.81 | $634.59 | 1.27% | 1.27% | +0.000 |
| PLTR | equity | 4.6051 | $137.80 | $634.59 | 1.27% | 1.27% | +0.000 |
| SMCI | equity | 17.9414 | $35.37 | $634.59 | 1.27% | 1.27% | +0.000 |
| SNDK | equity | 0.4062 | $1562.34 | $634.59 | 1.27% | 1.27% | +0.000 |
| XYZ | equity | 8.4781 | $74.85 | $634.59 | 1.27% | 1.27% | +0.000 |
| __CASH__ | cash | — | — | $-0.04 | -0.00% | -0.00% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 22 (22 buys, 0 sells) |
| Total notional | $50,000.04 |
| Estimated turnover | 100.0% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +1.3941 | $455.19 | $634.59 |
| APH | buy | +4.9566 | $128.03 | $634.59 |
| APP | buy | +1.3544 | $468.55 | $634.59 |
| ARES | buy | +5.0264 | $126.25 | $634.59 |
| AXON | buy | +1.5726 | $403.54 | $634.59 |
| COHR | buy | +1.8928 | $335.26 | $634.59 |
| COIN | buy | +3.1546 | $201.16 | $634.59 |
| CVNA | buy | +8.1420 | $77.94 | $634.59 |
| DDOG | buy | +3.1704 | $200.16 | $634.59 |
| EL | buy | +7.3618 | $86.20 | $634.59 |
| EPAM | buy | +6.3951 | $99.23 | $634.59 |
| GLD | buy | +12.9674 | $417.88 | $5,418.83 |
| HOOD | buy | +8.2382 | $77.03 | $634.59 |
| INTC | buy | +5.0800 | $124.92 | $634.59 |
| LITE | buy | +0.7021 | $903.80 | $634.59 |
| MU | buy | +0.8497 | $746.81 | $634.59 |
| NCLH | buy | +37.1539 | $17.08 | $634.59 |
| PLTR | buy | +4.6051 | $137.80 | $634.59 |
| SMCI | buy | +17.9414 | $35.37 | $634.59 |
| SNDK | buy | +0.4062 | $1562.34 | $634.59 |
| UUP | buy | +1155.8321 | $27.59 | $31,889.41 |
| XYZ | buy | +8.4781 | $74.85 | $634.59 |

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
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |

---

