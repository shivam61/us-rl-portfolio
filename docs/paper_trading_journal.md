# Phase H — Paper Trading Journal

> **Portfolio:** $50,000 NAV | Broker: Alpaca paper | Config: v H.0.0
> **Rebalance cadence:** every 14 days | **Mode:** rl_e7 (dual-mode switching active)
> **Gates:** H-1 pipeline · H-2 slippage <20 bps · H-3 turnover <35% · H-4 drift <5pp · H-5 RL mode · H-6 Sharpe · H-7 data parity · H-8 audit trail

Newest entries at the top. Updated automatically by `scripts/generate_paper_journal.py`.

---

## 2026-05-15

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `rl_e7` |
| Rebalance day | no |
| Signal | 🚨 FAILED |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 22 positions + cash |
| Invested | $46,457.30 (92.9% of NAV) |
| Cash | $3,542.60 (7.1% of NAV) |
| Total NAV | $49,999.90 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 1052.0207 | $27.59 | $29,025.25 | 58.05% | 58.05% | +0.000 |
| GLD | trend | 11.8028 | $417.88 | $4,932.15 | 9.86% | 9.86% | +0.000 |
| SNDK | equity | 0.4526 | $1381.02 | $625.05 | 1.25% | 1.25% | +0.000 |
| HOOD | equity | 8.1322 | $76.86 | $625.04 | 1.25% | 1.25% | +0.000 |
| EPAM | equity | 6.5203 | $95.86 | $625.04 | 1.25% | 1.25% | +0.000 |
| EL | equity | 7.4338 | $84.08 | $625.03 | 1.25% | 1.25% | +0.000 |
| COHR | equity | 1.7751 | $352.10 | $625.01 | 1.25% | 1.25% | +0.000 |
| COIN | equity | 3.0984 | $201.72 | $625.01 | 1.25% | 1.25% | +0.000 |
| PLTR | equity | 4.6684 | $133.88 | $625.01 | 1.25% | 1.25% | +0.000 |
| DDOG | equity | 3.1927 | $195.76 | $625.00 | 1.25% | 1.25% | +0.000 |
| INTC | equity | 5.3616 | $116.57 | $625.00 | 1.25% | 1.25% | +0.000 |
| AXON | equity | 1.5816 | $395.17 | $625.00 | 1.25% | 1.25% | +0.000 |
| CVNA | equity | 8.4757 | $73.74 | $625.00 | 1.25% | 1.25% | +0.000 |
| XYZ | equity | 8.6254 | $72.46 | $625.00 | 1.25% | 1.25% | +0.000 |
| ARES | equity | 5.0265 | $124.34 | $625.00 | 1.25% | 1.25% | +0.000 |
| APH | equity | 4.9852 | $125.37 | $624.99 | 1.25% | 1.25% | +0.000 |
| MU | equity | 0.8700 | $718.38 | $624.99 | 1.25% | 1.25% | +0.000 |
| AMD | equity | 1.4579 | $428.69 | $624.99 | 1.25% | 1.25% | +0.000 |
| APP | equity | 1.2994 | $480.98 | $624.99 | 1.25% | 1.25% | +0.000 |
| SMCI | equity | 19.7716 | $31.61 | $624.98 | 1.25% | 1.25% | +0.000 |
| LITE | equity | 0.6605 | $946.20 | $624.97 | 1.25% | 1.25% | +0.000 |
| NCLH | equity | 38.5446 | $16.21 | $624.81 | 1.25% | 1.25% | +0.000 |
| __CASH__ | cash | — | — | $3,542.60 | 7.09% | 7.09% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-14

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `rl_e7` |
| Rebalance day | no |
| Signal | 🚨 FAILED |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 22 positions + cash |
| Invested | $46,457.30 (92.9% of NAV) |
| Cash | $3,542.60 (7.1% of NAV) |
| Total NAV | $49,999.90 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 1052.0207 | $27.59 | $29,025.25 | 58.05% | 58.05% | +0.000 |
| GLD | trend | 11.8028 | $417.88 | $4,932.15 | 9.86% | 9.86% | +0.000 |
| SNDK | equity | 0.4526 | $1381.02 | $625.05 | 1.25% | 1.25% | +0.000 |
| HOOD | equity | 8.1322 | $76.86 | $625.04 | 1.25% | 1.25% | +0.000 |
| EPAM | equity | 6.5203 | $95.86 | $625.04 | 1.25% | 1.25% | +0.000 |
| EL | equity | 7.4338 | $84.08 | $625.03 | 1.25% | 1.25% | +0.000 |
| COHR | equity | 1.7751 | $352.10 | $625.01 | 1.25% | 1.25% | +0.000 |
| COIN | equity | 3.0984 | $201.72 | $625.01 | 1.25% | 1.25% | +0.000 |
| PLTR | equity | 4.6684 | $133.88 | $625.01 | 1.25% | 1.25% | +0.000 |
| DDOG | equity | 3.1927 | $195.76 | $625.00 | 1.25% | 1.25% | +0.000 |
| INTC | equity | 5.3616 | $116.57 | $625.00 | 1.25% | 1.25% | +0.000 |
| AXON | equity | 1.5816 | $395.17 | $625.00 | 1.25% | 1.25% | +0.000 |
| CVNA | equity | 8.4757 | $73.74 | $625.00 | 1.25% | 1.25% | +0.000 |
| XYZ | equity | 8.6254 | $72.46 | $625.00 | 1.25% | 1.25% | +0.000 |
| ARES | equity | 5.0265 | $124.34 | $625.00 | 1.25% | 1.25% | +0.000 |
| APH | equity | 4.9852 | $125.37 | $624.99 | 1.25% | 1.25% | +0.000 |
| MU | equity | 0.8700 | $718.38 | $624.99 | 1.25% | 1.25% | +0.000 |
| AMD | equity | 1.4579 | $428.69 | $624.99 | 1.25% | 1.25% | +0.000 |
| APP | equity | 1.2994 | $480.98 | $624.99 | 1.25% | 1.25% | +0.000 |
| SMCI | equity | 19.7716 | $31.61 | $624.98 | 1.25% | 1.25% | +0.000 |
| LITE | equity | 0.6605 | $946.20 | $624.97 | 1.25% | 1.25% | +0.000 |
| NCLH | equity | 38.5446 | $16.21 | $624.81 | 1.25% | 1.25% | +0.000 |
| __CASH__ | cash | — | — | $3,542.60 | 7.09% | 7.09% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-13

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `rl_e7` |
| Rebalance day | no |
| Signal | 🚨 FAILED |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 22 positions + cash |
| Invested | $46,457.30 (92.9% of NAV) |
| Cash | $3,542.60 (7.1% of NAV) |
| Total NAV | $49,999.90 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 1052.0207 | $27.59 | $29,025.25 | 58.05% | 58.05% | +0.000 |
| GLD | trend | 11.8028 | $417.88 | $4,932.15 | 9.86% | 9.86% | +0.000 |
| SNDK | equity | 0.4526 | $1381.02 | $625.05 | 1.25% | 1.25% | +0.000 |
| HOOD | equity | 8.1322 | $76.86 | $625.04 | 1.25% | 1.25% | +0.000 |
| EPAM | equity | 6.5203 | $95.86 | $625.04 | 1.25% | 1.25% | +0.000 |
| EL | equity | 7.4338 | $84.08 | $625.03 | 1.25% | 1.25% | +0.000 |
| COHR | equity | 1.7751 | $352.10 | $625.01 | 1.25% | 1.25% | +0.000 |
| COIN | equity | 3.0984 | $201.72 | $625.01 | 1.25% | 1.25% | +0.000 |
| PLTR | equity | 4.6684 | $133.88 | $625.01 | 1.25% | 1.25% | +0.000 |
| DDOG | equity | 3.1927 | $195.76 | $625.00 | 1.25% | 1.25% | +0.000 |
| INTC | equity | 5.3616 | $116.57 | $625.00 | 1.25% | 1.25% | +0.000 |
| AXON | equity | 1.5816 | $395.17 | $625.00 | 1.25% | 1.25% | +0.000 |
| CVNA | equity | 8.4757 | $73.74 | $625.00 | 1.25% | 1.25% | +0.000 |
| XYZ | equity | 8.6254 | $72.46 | $625.00 | 1.25% | 1.25% | +0.000 |
| ARES | equity | 5.0265 | $124.34 | $625.00 | 1.25% | 1.25% | +0.000 |
| APH | equity | 4.9852 | $125.37 | $624.99 | 1.25% | 1.25% | +0.000 |
| MU | equity | 0.8700 | $718.38 | $624.99 | 1.25% | 1.25% | +0.000 |
| AMD | equity | 1.4579 | $428.69 | $624.99 | 1.25% | 1.25% | +0.000 |
| APP | equity | 1.2994 | $480.98 | $624.99 | 1.25% | 1.25% | +0.000 |
| SMCI | equity | 19.7716 | $31.61 | $624.98 | 1.25% | 1.25% | +0.000 |
| LITE | equity | 0.6605 | $946.20 | $624.97 | 1.25% | 1.25% | +0.000 |
| NCLH | equity | 38.5446 | $16.21 | $624.81 | 1.25% | 1.25% | +0.000 |
| __CASH__ | cash | — | — | $3,542.60 | 7.09% | 7.09% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-12

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `rl_e7` |
| Rebalance day | no |
| Signal | 🚨 FAILED |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Allocation
| Sleeve | Weight |
|--------|--------|
| Equity | 25.00% |
| Trend | 69.37% |
| Cash | 5.63% |

**Trend breakdown:**
- TLT: 69.37%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 22 positions + cash |
| Invested | $46,457.30 (92.9% of NAV) |
| Cash | $3,542.60 (7.1% of NAV) |
| Total NAV | $49,999.90 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 1052.0207 | $27.59 | $29,025.25 | 58.05% | 58.05% | +0.000 |
| GLD | trend | 11.8028 | $417.88 | $4,932.15 | 9.86% | 9.86% | +0.000 |
| SNDK | equity | 0.4526 | $1381.02 | $625.05 | 1.25% | 1.25% | +0.000 |
| HOOD | equity | 8.1322 | $76.86 | $625.04 | 1.25% | 1.25% | +0.000 |
| EPAM | equity | 6.5203 | $95.86 | $625.04 | 1.25% | 1.25% | +0.000 |
| EL | equity | 7.4338 | $84.08 | $625.03 | 1.25% | 1.25% | +0.000 |
| COHR | equity | 1.7751 | $352.10 | $625.01 | 1.25% | 1.25% | +0.000 |
| COIN | equity | 3.0984 | $201.72 | $625.01 | 1.25% | 1.25% | +0.000 |
| PLTR | equity | 4.6684 | $133.88 | $625.01 | 1.25% | 1.25% | +0.000 |
| DDOG | equity | 3.1927 | $195.76 | $625.00 | 1.25% | 1.25% | +0.000 |
| INTC | equity | 5.3616 | $116.57 | $625.00 | 1.25% | 1.25% | +0.000 |
| AXON | equity | 1.5816 | $395.17 | $625.00 | 1.25% | 1.25% | +0.000 |
| CVNA | equity | 8.4757 | $73.74 | $625.00 | 1.25% | 1.25% | +0.000 |
| XYZ | equity | 8.6254 | $72.46 | $625.00 | 1.25% | 1.25% | +0.000 |
| ARES | equity | 5.0265 | $124.34 | $625.00 | 1.25% | 1.25% | +0.000 |
| APH | equity | 4.9852 | $125.37 | $624.99 | 1.25% | 1.25% | +0.000 |
| MU | equity | 0.8700 | $718.38 | $624.99 | 1.25% | 1.25% | +0.000 |
| AMD | equity | 1.4579 | $428.69 | $624.99 | 1.25% | 1.25% | +0.000 |
| APP | equity | 1.2994 | $480.98 | $624.99 | 1.25% | 1.25% | +0.000 |
| SMCI | equity | 19.7716 | $31.61 | $624.98 | 1.25% | 1.25% | +0.000 |
| LITE | equity | 0.6605 | $946.20 | $624.97 | 1.25% | 1.25% | +0.000 |
| NCLH | equity | 38.5446 | $16.21 | $624.81 | 1.25% | 1.25% | +0.000 |
| __CASH__ | cash | — | — | $3,542.60 | 7.09% | 7.09% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (21 buys, 0 sells) |
| Total notional | $40,447.60 |
| Estimated turnover | 80.9% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.6722 | $428.69 | $288.15 |
| APH | buy | +2.2984 | $125.37 | $288.15 |
| APP | buy | +0.5991 | $480.98 | $288.15 |
| ARES | buy | +2.3174 | $124.34 | $288.15 |
| AXON | buy | +0.7292 | $395.17 | $288.15 |
| COHR | buy | +0.8184 | $352.10 | $288.15 |
| COIN | buy | +1.4285 | $201.72 | $288.15 |
| CVNA | buy | +3.9076 | $73.74 | $288.15 |
| DDOG | buy | +1.4720 | $195.76 | $288.15 |
| EL | buy | +3.4273 | $84.08 | $288.15 |
| EPAM | buy | +3.0061 | $95.86 | $288.15 |
| HOOD | buy | +3.7493 | $76.86 | $288.15 |
| INTC | buy | +2.4719 | $116.57 | $288.15 |
| LITE | buy | +0.3045 | $946.20 | $288.15 |
| MU | buy | +0.4011 | $718.38 | $288.15 |
| NCLH | buy | +17.7706 | $16.21 | $288.15 |
| PLTR | buy | +2.1523 | $133.88 | $288.15 |
| SMCI | buy | +9.1155 | $31.61 | $288.15 |
| SNDK | buy | +0.2087 | $1381.02 | $288.15 |
| TLT | buy | +404.3437 | $85.78 | $34,684.60 |
| XYZ | buy | +3.9767 | $72.46 | $288.15 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $428.69 | $428.69 | +0.0 | ✅ |
| APH | buy | $125.37 | $125.37 | +0.0 | ✅ |
| APP | buy | $480.98 | $480.98 | +0.0 | ✅ |
| ARES | buy | $124.34 | $124.34 | +0.0 | ✅ |
| AXON | buy | $395.17 | $395.17 | +0.0 | ✅ |
| COHR | buy | $352.10 | $352.10 | +0.0 | ✅ |
| COIN | buy | $201.72 | $201.72 | +0.0 | ✅ |
| CVNA | buy | $73.74 | $73.74 | +0.0 | ✅ |
| DDOG | buy | $195.76 | $195.76 | +0.0 | ✅ |
| EL | buy | $84.08 | $84.08 | +0.0 | ✅ |
| EPAM | buy | $95.86 | $95.86 | +0.0 | ✅ |
| HOOD | buy | $76.86 | $76.86 | +0.0 | ✅ |
| INTC | buy | $116.57 | $116.57 | +0.0 | ✅ |
| LITE | buy | $946.20 | $946.20 | +0.0 | ✅ |
| MU | buy | $718.38 | $718.38 | +0.0 | ✅ |
| NCLH | buy | $16.21 | $16.21 | +0.0 | ✅ |
| PLTR | buy | $133.88 | $133.88 | +0.0 | ✅ |
| SMCI | buy | $31.61 | $31.61 | +0.0 | ✅ |
| SNDK | buy | $1381.02 | $1381.02 | +0.0 | ✅ |
| TLT | buy | $85.78 | $85.78 | +0.0 | ✅ |
| XYZ | buy | $72.46 | $72.46 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

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
| Invested | $43,567.95 (87.1% of NAV) |
| Cash | $6,432.05 (12.9% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 962.5045 | $27.59 | $26,555.50 | 53.11% | 53.11% | +0.000 |
| GLD | trend | 10.7984 | $417.88 | $4,512.45 | 9.02% | 9.02% | +0.000 |
| APP | equity | 1.3339 | $468.55 | $625.00 | 1.25% | 1.25% | +0.000 |
| ARES | equity | 4.9505 | $126.25 | $625.00 | 1.25% | 1.25% | +0.000 |
| AMD | equity | 1.3731 | $455.19 | $625.00 | 1.25% | 1.25% | +0.000 |
| APH | equity | 4.8817 | $128.03 | $625.00 | 1.25% | 1.25% | +0.000 |
| COHR | equity | 1.8642 | $335.26 | $625.00 | 1.25% | 1.25% | +0.000 |
| AXON | equity | 1.5488 | $403.54 | $625.00 | 1.25% | 1.25% | +0.000 |
| DDOG | equity | 3.1225 | $200.16 | $625.00 | 1.25% | 1.25% | +0.000 |
| COIN | equity | 3.1070 | $201.16 | $625.00 | 1.25% | 1.25% | +0.000 |
| EL | equity | 7.2506 | $86.20 | $625.00 | 1.25% | 1.25% | +0.000 |
| EPAM | equity | 6.2985 | $99.23 | $625.00 | 1.25% | 1.25% | +0.000 |
| HOOD | equity | 8.1137 | $77.03 | $625.00 | 1.25% | 1.25% | +0.000 |
| CVNA | equity | 8.0190 | $77.94 | $625.00 | 1.25% | 1.25% | +0.000 |
| INTC | equity | 5.0032 | $124.92 | $625.00 | 1.25% | 1.25% | +0.000 |
| LITE | equity | 0.6915 | $903.80 | $625.00 | 1.25% | 1.25% | +0.000 |
| NCLH | equity | 36.5925 | $17.08 | $625.00 | 1.25% | 1.25% | +0.000 |
| MU | equity | 0.8369 | $746.81 | $625.00 | 1.25% | 1.25% | +0.000 |
| PLTR | equity | 4.5356 | $137.80 | $625.00 | 1.25% | 1.25% | +0.000 |
| SMCI | equity | 17.6703 | $35.37 | $625.00 | 1.25% | 1.25% | +0.000 |
| SNDK | equity | 0.4000 | $1562.34 | $625.00 | 1.25% | 1.25% | +0.000 |
| XYZ | equity | 8.3500 | $74.85 | $625.00 | 1.25% | 1.25% | +0.000 |
| __CASH__ | cash | — | — | $6,432.05 | 12.86% | 12.86% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 22 (22 buys, 0 sells) |
| Total notional | $43,567.95 |
| Estimated turnover | 87.1% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +1.3731 | $455.19 | $625.00 |
| APH | buy | +4.8817 | $128.03 | $625.00 |
| APP | buy | +1.3339 | $468.55 | $625.00 |
| ARES | buy | +4.9505 | $126.25 | $625.00 |
| AXON | buy | +1.5488 | $403.54 | $625.00 |
| COHR | buy | +1.8642 | $335.26 | $625.00 |
| COIN | buy | +3.1070 | $201.16 | $625.00 |
| CVNA | buy | +8.0190 | $77.94 | $625.00 |
| DDOG | buy | +3.1225 | $200.16 | $625.00 |
| EL | buy | +7.2506 | $86.20 | $625.00 |
| EPAM | buy | +6.2985 | $99.23 | $625.00 |
| GLD | buy | +10.7984 | $417.88 | $4,512.45 |
| HOOD | buy | +8.1137 | $77.03 | $625.00 |
| INTC | buy | +5.0032 | $124.92 | $625.00 |
| LITE | buy | +0.6915 | $903.80 | $625.00 |
| MU | buy | +0.8369 | $746.81 | $625.00 |
| NCLH | buy | +36.5925 | $17.08 | $625.00 |
| PLTR | buy | +4.5356 | $137.80 | $625.00 |
| SMCI | buy | +17.6703 | $35.37 | $625.00 |
| SNDK | buy | +0.4000 | $1562.34 | $625.00 |
| UUP | buy | +962.5045 | $27.59 | $26,555.50 |
| XYZ | buy | +8.3500 | $74.85 | $625.00 |

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

