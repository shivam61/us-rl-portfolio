# Phase H — Paper Trading Journal

> **Portfolio:** $50,000 NAV | Broker: Alpaca paper | Config: v H.0.0
> **Rebalance cadence:** every 14 days | **Mode:** rl_e7 (dual-mode switching active)
> **Gates:** H-1 pipeline · H-2 slippage <20 bps · H-3 turnover <35% · H-4 drift <5pp · H-5 RL mode · H-6 Sharpe · H-7 data parity · H-8 audit trail

Newest entries at the top. Updated automatically by `scripts/generate_paper_journal.py`.

---

## 2026-06-05

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
| Equity | 35.86% |
| Trend | 57.60% |
| Cash | 6.54% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 3.9962 | $130.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9968 | $523.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5532 | $146.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9331 | $558.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2361 | $421.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0162 | $513.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1774 | $164.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1408 | $243.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.3438 | $97.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.9040 | $88.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8788 | $66.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2907 | $82.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.6654 | $111.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5518 | $945.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5236 | $996.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 27.2608 | $19.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.6803 | $141.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 11.1194 | $46.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2964 | $1759.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.3565 | $70.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-04

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
| Equity | 35.86% |
| Trend | 57.60% |
| Cash | 6.54% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 3.9962 | $130.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9968 | $523.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5532 | $146.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9331 | $558.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2361 | $421.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0162 | $513.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1774 | $164.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1408 | $243.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.3438 | $97.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.9040 | $88.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8788 | $66.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2907 | $82.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.6654 | $111.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5518 | $945.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5236 | $996.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 27.2608 | $19.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.6803 | $141.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 11.1194 | $46.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2964 | $1759.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.3565 | $70.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (9 buys, 11 sells) |
| Total notional | $296.59 |
| Estimated turnover | 0.6% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0355 | $523.20 | $18.57 |
| APH | buy | +0.0205 | $146.77 | $3.00 |
| APP | buy | +0.0196 | $558.87 | $10.93 |
| ARES | sell | -0.2402 | $130.50 | $31.35 |
| AXON | sell | -0.0669 | $513.20 | $34.36 |
| COHR | sell | -0.0132 | $421.90 | $5.58 |
| COIN | sell | -0.0177 | $164.13 | $2.91 |
| CVNA | sell | -0.3144 | $66.19 | $20.81 |
| DDOG | buy | +0.0576 | $243.60 | $14.02 |
| EL | sell | -0.0652 | $82.90 | $5.40 |
| EPAM | sell | -0.0170 | $97.59 | $1.66 |
| HOOD | sell | -0.3905 | $88.33 | $34.49 |
| INTC | buy | +0.0385 | $111.78 | $4.30 |
| LITE | sell | -0.0042 | $945.08 | $3.94 |
| MU | buy | +0.0405 | $996.00 | $40.37 |
| NCLH | sell | -1.5036 | $19.13 | $28.76 |
| PLTR | buy | +0.0129 | $141.70 | $1.83 |
| SMCI | buy | +0.1219 | $46.90 | $5.72 |
| SNDK | buy | +0.0116 | $1759.68 | $20.45 |
| XYZ | sell | -0.1149 | $70.89 | $8.14 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $523.20 | $523.20 | +0.0 | ✅ |
| APH | buy | $146.77 | $146.77 | +0.0 | ✅ |
| APP | buy | $558.87 | $558.87 | +0.0 | ✅ |
| ARES | sell | $130.50 | $130.50 | -0.0 | ✅ |
| AXON | sell | $513.20 | $513.20 | -0.0 | ✅ |
| COHR | sell | $421.90 | $421.90 | -0.0 | ✅ |
| COIN | sell | $164.13 | $164.13 | -0.0 | ✅ |
| CVNA | sell | $66.19 | $66.19 | -0.0 | ✅ |
| DDOG | buy | $243.60 | $243.60 | +0.0 | ✅ |
| EL | sell | $82.90 | $82.90 | -0.0 | ✅ |
| EPAM | sell | $97.59 | $97.59 | -0.0 | ✅ |
| HOOD | sell | $88.33 | $88.33 | -0.0 | ✅ |
| INTC | buy | $111.78 | $111.78 | +0.0 | ✅ |
| LITE | sell | $945.08 | $945.08 | -0.0 | ✅ |
| MU | buy | $996.00 | $996.00 | +0.0 | ✅ |
| NCLH | sell | $19.13 | $19.13 | -0.0 | ✅ |
| PLTR | buy | $141.70 | $141.70 | +0.0 | ✅ |
| SMCI | buy | $46.90 | $46.90 | +0.0 | ✅ |
| SNDK | buy | $1759.68 | $1759.68 | +0.0 | ✅ |
| XYZ | sell | $70.89 | $70.89 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-03

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
| Equity | 35.86% |
| Trend | 57.60% |
| Cash | 6.54% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.43 (53.6% of NAV) |
| Cash | $23,182.57 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| NCLH | equity | 28.7645 | $18.15 | $522.08 | 1.04% | 1.04% | +0.001 |
| AMD | equity | 0.9613 | $542.52 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.2364 | $123.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9136 | $570.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2493 | $417.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5327 | $147.62 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0831 | $481.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0833 | $250.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.3608 | $97.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.2945 | $82.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1951 | $163.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3559 | $82.05 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.6269 | $112.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.1932 | $63.65 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4831 | $1079.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5560 | $938.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.6674 | $142.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 10.9975 | $47.42 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2847 | $1831.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.4713 | $69.80 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.57 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (15 buys, 4 sells) |
| Total notional | $455.74 |
| Estimated turnover | 0.9% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0387 | $542.52 | $20.98 |
| APH | buy | +0.0186 | $147.62 | $2.74 |
| APP | buy | +0.0525 | $570.83 | $29.97 |
| ARES | buy | +0.1780 | $123.10 | $21.92 |
| AXON | buy | +0.0191 | $481.48 | $9.19 |
| COHR | buy | +0.0277 | $417.43 | $11.56 |
| COIN | buy | +0.1978 | $163.22 | $32.28 |
| CVNA | buy | +0.2435 | $63.65 | $15.50 |
| DDOG | buy | +0.1455 | $250.33 | $36.43 |
| EL | buy | +0.1036 | $82.05 | $8.50 |
| EPAM | buy | +0.3090 | $97.28 | $30.06 |
| HOOD | buy | +0.3791 | $82.85 | $31.41 |
| INTC | sell | -0.2049 | $112.71 | $23.10 |
| LITE | buy | +0.0492 | $938.00 | $46.19 |
| MU | sell | -0.0070 | $1079.57 | $7.58 |
| PLTR | buy | +0.2403 | $142.20 | $34.17 |
| SMCI | buy | +0.6028 | $47.42 | $28.59 |
| SNDK | sell | -0.0191 | $1831.50 | $34.98 |
| XYZ | buy | +0.4383 | $69.80 | $30.59 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $542.52 | $542.52 | -0.0 | ✅ |
| APH | buy | $147.62 | $147.62 | +0.0 | ✅ |
| APP | buy | $570.83 | $570.83 | +0.0 | ✅ |
| ARES | buy | $123.10 | $123.10 | +0.0 | ✅ |
| AXON | buy | $481.48 | $481.48 | +0.0 | ✅ |
| COHR | buy | $417.43 | $417.43 | +0.0 | ✅ |
| COIN | buy | $163.22 | $163.22 | +0.0 | ✅ |
| CVNA | buy | $63.65 | $63.65 | +0.0 | ✅ |
| DDOG | buy | $250.33 | $250.33 | +0.0 | ✅ |
| EL | buy | $82.05 | $82.05 | +0.0 | ✅ |
| EPAM | buy | $97.28 | $97.28 | +0.0 | ✅ |
| HOOD | buy | $82.85 | $82.85 | +0.0 | ✅ |
| INTC | sell | $112.71 | $112.71 | -0.0 | ✅ |
| LITE | buy | $938.00 | $938.00 | +0.0 | ✅ |
| MU | sell | $1079.57 | $1079.57 | -0.0 | ✅ |
| PLTR | buy | $142.20 | $142.20 | +0.0 | ✅ |
| SMCI | buy | $47.42 | $47.42 | +0.0 | ✅ |
| SNDK | sell | $1831.50 | $1831.50 | -0.0 | ✅ |
| XYZ | buy | $69.80 | $69.80 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-02

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
| Equity | 35.86% |
| Trend | 57.60% |
| Cash | 6.54% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,815.96 (53.6% of NAV) |
| Cash | $23,184.04 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| AMD | equity | 0.9999 | $521.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5142 | $148.40 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2216 | $426.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.8611 | $605.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.8318 | $107.93 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0640 | $490.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.9973 | $173.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 1.9377 | $269.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.0518 | $103.23 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.9154 | $88.16 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.9497 | $65.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2522 | $83.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.4271 | $152.17 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5067 | $1029.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4901 | $1064.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 28.7645 | $18.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3038 | $1716.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 10.3947 | $50.17 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.0330 | $74.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.0584 | $128.28 | $520.61 | 1.04% | 1.04% | -0.002 |
| __CASH__ | cash | — | — | $23,184.04 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (10 buys, 9 sells) |
| Total notional | $637.26 |
| Estimated turnover | 1.3% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0105 | $521.54 | $5.50 |
| APH | buy | +0.0085 | $148.40 | $1.26 |
| APP | buy | +0.0105 | $605.63 | $6.35 |
| AXON | sell | -0.0982 | $490.12 | $48.11 |
| COHR | sell | -0.2211 | $426.89 | $94.38 |
| COIN | buy | +0.2385 | $173.99 | $41.49 |
| CVNA | buy | +0.8059 | $65.60 | $52.86 |
| DDOG | sell | -0.1706 | $269.13 | $45.92 |
| EL | buy | +0.3894 | $83.41 | $32.48 |
| EPAM | sell | -0.0380 | $103.23 | $3.92 |
| HOOD | buy | +0.3852 | $88.16 | $33.96 |
| INTC | buy | +0.2844 | $107.93 | $30.70 |
| LITE | sell | -0.1032 | $1029.15 | $106.25 |
| MU | sell | -0.0470 | $1064.10 | $50.00 |
| NCLH | buy | +0.3294 | $18.13 | $5.97 |
| PLTR | buy | +0.0957 | $152.17 | $14.56 |
| SMCI | sell | -0.9202 | $50.17 | $46.16 |
| SNDK | sell | -0.0038 | $1716.36 | $6.58 |
| XYZ | buy | +0.1458 | $74.15 | $10.81 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $521.54 | $521.54 | -0.0 | ✅ |
| APH | buy | $148.40 | $148.40 | +0.0 | ✅ |
| APP | buy | $605.63 | $605.63 | +0.0 | ✅ |
| AXON | sell | $490.12 | $490.12 | -0.0 | ✅ |
| COHR | sell | $426.89 | $426.89 | -0.0 | ✅ |
| COIN | buy | $173.99 | $173.99 | +0.0 | ✅ |
| CVNA | buy | $65.60 | $65.60 | +0.0 | ✅ |
| DDOG | sell | $269.13 | $269.13 | -0.0 | ✅ |
| EL | buy | $83.41 | $83.41 | +0.0 | ✅ |
| EPAM | sell | $103.23 | $103.23 | -0.0 | ✅ |
| HOOD | buy | $88.16 | $88.16 | +0.0 | ✅ |
| INTC | buy | $107.93 | $107.93 | +0.0 | ✅ |
| LITE | sell | $1029.15 | $1029.15 | -0.0 | ✅ |
| MU | sell | $1064.10 | $1064.10 | -0.0 | ✅ |
| NCLH | buy | $18.13 | $18.13 | +0.0 | ✅ |
| PLTR | buy | $152.17 | $152.17 | +0.0 | ✅ |
| SMCI | sell | $50.17 | $50.17 | -0.0 | ✅ |
| SNDK | sell | $1716.36 | $1716.36 | -0.0 | ✅ |
| XYZ | buy | $74.15 | $74.15 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-29

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
| Equity | 35.86% |
| Trend | 57.60% |
| Cash | 6.54% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.0584 | $128.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0105 | $516.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5056 | $148.76 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.8506 | $613.09 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.4427 | $361.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1622 | $448.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.7588 | $189.03 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1083 | $247.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.0898 | $102.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.5302 | $94.30 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.1438 | $73.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 5.8628 | $88.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.5474 | $114.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6100 | $854.96 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5371 | $971.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 28.4351 | $18.34 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.3314 | $156.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 11.3148 | $46.09 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3077 | $1694.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.8872 | $75.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (6 buys, 14 sells) |
| Total notional | $400.58 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0039 | $516.10 | $2.00 |
| APH | sell | -0.0256 | $148.76 | $3.81 |
| APP | sell | -0.0187 | $613.09 | $11.48 |
| ARES | sell | -0.0805 | $128.50 | $10.35 |
| AXON | sell | -0.0249 | $448.72 | $11.16 |
| COHR | buy | +0.0592 | $361.47 | $21.42 |
| COIN | sell | -0.1026 | $189.03 | $19.40 |
| CVNA | buy | +0.0476 | $73.00 | $3.48 |
| DDOG | sell | -0.2070 | $247.35 | $51.19 |
| EL | buy | +0.1017 | $88.95 | $9.05 |
| EPAM | sell | -0.0517 | $102.46 | $5.30 |
| HOOD | sell | -0.6166 | $94.30 | $58.15 |
| INTC | buy | +0.2336 | $114.68 | $26.79 |
| LITE | buy | +0.0040 | $854.96 | $3.43 |
| MU | sell | -0.0276 | $971.00 | $26.81 |
| NCLH | sell | -0.0933 | $18.34 | $1.71 |
| PLTR | sell | -0.3068 | $156.54 | $48.02 |
| SMCI | sell | -1.3123 | $46.09 | $60.48 |
| SNDK | sell | -0.0100 | $1694.98 | $16.94 |
| XYZ | sell | -0.1269 | $75.72 | $9.61 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $516.10 | $516.10 | +0.0 | ✅ |
| APH | sell | $148.76 | $148.76 | -0.0 | ✅ |
| APP | sell | $613.09 | $613.09 | -0.0 | ✅ |
| ARES | sell | $128.50 | $128.50 | -0.0 | ✅ |
| AXON | sell | $448.72 | $448.72 | -0.0 | ✅ |
| COHR | buy | $361.47 | $361.47 | +0.0 | ✅ |
| COIN | sell | $189.03 | $189.03 | -0.0 | ✅ |
| CVNA | buy | $73.00 | $73.00 | +0.0 | ✅ |
| DDOG | sell | $247.35 | $247.35 | -0.0 | ✅ |
| EL | buy | $88.95 | $88.95 | +0.0 | ✅ |
| EPAM | sell | $102.46 | $102.46 | -0.0 | ✅ |
| HOOD | sell | $94.30 | $94.30 | -0.0 | ✅ |
| INTC | buy | $114.68 | $114.68 | +0.0 | ✅ |
| LITE | buy | $854.96 | $854.96 | +0.0 | ✅ |
| MU | sell | $971.00 | $971.00 | -0.0 | ✅ |
| NCLH | sell | $18.34 | $18.34 | -0.0 | ✅ |
| PLTR | sell | $156.54 | $156.54 | -0.0 | ✅ |
| SMCI | sell | $46.09 | $46.09 | -0.0 | ✅ |
| SNDK | sell | $1694.98 | $1694.98 | -0.0 | ✅ |
| XYZ | sell | $75.72 | $75.72 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-28

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
| Equity | 35.86% |
| Trend | 57.60% |
| Cash | 6.54% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.1389 | $126.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0066 | $518.09 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5313 | $147.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.8693 | $599.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3835 | $376.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1871 | $439.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.8615 | $182.25 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3153 | $225.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.1415 | $101.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.1469 | $84.84 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.0962 | $73.49 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 5.7612 | $90.52 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.3138 | $120.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6060 | $860.62 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5647 | $923.52 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 28.5284 | $18.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.6382 | $143.34 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 12.6271 | $41.30 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3177 | $1641.64 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.0141 | $74.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (7 buys, 13 sells) |
| Total notional | $408.47 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0458 | $518.09 | $23.73 |
| APH | sell | -0.1873 | $147.68 | $27.67 |
| APP | sell | -0.0491 | $599.89 | $29.44 |
| ARES | buy | +0.0190 | $126.00 | $2.39 |
| AXON | sell | -0.1456 | $439.32 | $63.97 |
| COHR | buy | +0.0118 | $376.95 | $4.43 |
| COIN | sell | -0.1395 | $182.25 | $25.42 |
| CVNA | sell | -0.0476 | $73.49 | $3.50 |
| DDOG | sell | -0.0358 | $225.24 | $8.06 |
| EL | buy | +0.0208 | $90.52 | $1.89 |
| EPAM | buy | +0.0126 | $101.43 | $1.28 |
| HOOD | sell | -0.6943 | $84.84 | $58.90 |
| INTC | buy | +0.0312 | $120.89 | $3.77 |
| LITE | buy | +0.0280 | $860.62 | $24.09 |
| MU | buy | +0.0030 | $923.52 | $2.75 |
| NCLH | sell | -0.2043 | $18.28 | $3.74 |
| PLTR | sell | -0.2974 | $143.34 | $42.62 |
| SMCI | sell | -1.0283 | $41.30 | $42.47 |
| SNDK | sell | -0.0103 | $1641.64 | $16.96 |
| XYZ | sell | -0.2878 | $74.35 | $21.39 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $518.09 | $518.09 | -0.0 | ✅ |
| APH | sell | $147.68 | $147.68 | -0.0 | ✅ |
| APP | sell | $599.89 | $599.89 | -0.0 | ✅ |
| ARES | buy | $126.00 | $126.00 | +0.0 | ✅ |
| AXON | sell | $439.32 | $439.32 | -0.0 | ✅ |
| COHR | buy | $376.95 | $376.95 | +0.0 | ✅ |
| COIN | sell | $182.25 | $182.25 | -0.0 | ✅ |
| CVNA | sell | $73.49 | $73.49 | -0.0 | ✅ |
| DDOG | sell | $225.24 | $225.24 | -0.0 | ✅ |
| EL | buy | $90.52 | $90.52 | +0.0 | ✅ |
| EPAM | buy | $101.43 | $101.43 | +0.0 | ✅ |
| HOOD | sell | $84.84 | $84.84 | -0.0 | ✅ |
| INTC | buy | $120.89 | $120.89 | +0.0 | ✅ |
| LITE | buy | $860.62 | $860.62 | +0.0 | ✅ |
| MU | buy | $923.52 | $923.52 | +0.0 | ✅ |
| NCLH | sell | $18.28 | $18.28 | -0.0 | ✅ |
| PLTR | sell | $143.34 | $143.34 | -0.0 | ✅ |
| SMCI | sell | $41.30 | $41.30 | -0.0 | ✅ |
| SNDK | sell | $1641.64 | $1641.64 | -0.0 | ✅ |
| XYZ | sell | $74.35 | $74.35 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-27

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
| Equity | 35.86% |
| Trend | 57.60% |
| Cash | 6.54% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.1199 | $126.58 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0524 | $495.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.7186 | $140.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9184 | $567.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3717 | $380.18 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.3327 | $391.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.0009 | $173.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3511 | $221.81 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.1288 | $101.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.8411 | $76.23 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.1438 | $73.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 5.7403 | $90.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.2827 | $121.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5780 | $902.31 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5617 | $928.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 28.7328 | $18.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.9356 | $132.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 13.6554 | $38.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3280 | $1589.94 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.3019 | $71.42 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (20 buys, 1 sells) |
| Total notional | $14,443.37 |
| Estimated turnover | 28.9% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.2321 | $495.54 | $115.00 |
| APH | buy | +0.7568 | $140.24 | $106.14 |
| APP | buy | +0.1146 | $567.83 | $65.07 |
| ARES | buy | +0.8205 | $126.58 | $103.86 |
| AXON | buy | +0.2599 | $391.32 | $101.69 |
| COHR | buy | +0.2878 | $380.18 | $109.42 |
| COIN | buy | +0.7047 | $173.78 | $122.46 |
| CVNA | buy | +1.2515 | $73.00 | $91.36 |
| DDOG | buy | +0.5029 | $221.81 | $111.55 |
| EL | buy | +0.9488 | $90.85 | $86.19 |
| EPAM | buy | +0.9825 | $101.68 | $99.90 |
| HOOD | buy | +1.2621 | $76.23 | $96.21 |
| INTC | buy | +0.9362 | $121.77 | $114.01 |
| LITE | buy | +0.1241 | $902.31 | $112.01 |
| MU | buy | +0.1003 | $928.41 | $93.14 |
| NCLH | buy | +4.5603 | $18.15 | $82.77 |
| PLTR | buy | +0.9096 | $132.51 | $120.53 |
| SMCI | buy | +2.5139 | $38.19 | $96.01 |
| SNDK | buy | +0.0680 | $1589.94 | $108.05 |
| TLT | sell | -144.7109 | $85.78 | $12,413.30 |
| XYZ | buy | +1.3260 | $71.42 | $94.70 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $495.54 | $495.54 | +0.0 | ✅ |
| APH | buy | $140.24 | $140.24 | +0.0 | ✅ |
| APP | buy | $567.83 | $567.83 | +0.0 | ✅ |
| ARES | buy | $126.58 | $126.58 | +0.0 | ✅ |
| AXON | buy | $391.32 | $391.32 | +0.0 | ✅ |
| COHR | buy | $380.18 | $380.18 | +0.0 | ✅ |
| COIN | buy | $173.78 | $173.78 | +0.0 | ✅ |
| CVNA | buy | $73.00 | $73.00 | +0.0 | ✅ |
| DDOG | buy | $221.81 | $221.81 | +0.0 | ✅ |
| EL | buy | $90.85 | $90.85 | +0.0 | ✅ |
| EPAM | buy | $101.68 | $101.68 | +0.0 | ✅ |
| HOOD | buy | $76.23 | $76.23 | +0.0 | ✅ |
| INTC | buy | $121.77 | $121.77 | +0.0 | ✅ |
| LITE | buy | $902.31 | $902.31 | +0.0 | ✅ |
| MU | buy | $928.41 | $928.41 | +0.0 | ✅ |
| NCLH | buy | $18.15 | $18.15 | +0.0 | ✅ |
| PLTR | buy | $132.51 | $132.51 | +0.0 | ✅ |
| SMCI | buy | $38.19 | $38.19 | +0.0 | ✅ |
| SNDK | buy | $1589.94 | $1589.94 | +0.0 | ✅ |
| TLT | sell | $85.78 | $85.78 | -0.0 | ✅ |
| XYZ | buy | $71.42 | $71.42 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-26

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `rl_e7` |
| Rebalance day | ✅ YES |
| Signal | ✅ OK |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Allocation
| Sleeve | Weight |
|--------|--------|
| Equity | 35.86% |
| Trend | 57.60% |
| Cash | 6.54% |

**Trend breakdown:**
- TLT: 57.60%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $37,067.15 (74.1% of NAV) |
| Cash | $12,932.85 (25.9% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 335.7443 | $85.78 | $28,800.15 | 57.60% | 57.60% | +0.000 |
| ARES | equity | 3.2994 | $125.28 | $413.35 | 0.83% | 0.83% | +0.000 |
| AMD | equity | 0.8203 | $503.89 | $413.35 | 0.83% | 0.83% | +0.000 |
| APH | equity | 2.9618 | $139.56 | $413.35 | 0.83% | 0.83% | +0.000 |
| APP | equity | 0.8038 | $514.24 | $413.35 | 0.83% | 0.83% | +0.000 |
| COHR | equity | 1.0839 | $381.35 | $413.35 | 0.83% | 0.83% | +0.000 |
| AXON | equity | 1.0728 | $385.30 | $413.35 | 0.83% | 0.83% | +0.000 |
| COIN | equity | 2.2963 | $180.01 | $413.35 | 0.83% | 0.83% | +0.000 |
| DDOG | equity | 1.8482 | $223.65 | $413.35 | 0.83% | 0.83% | +0.000 |
| EPAM | equity | 4.1464 | $99.69 | $413.35 | 0.83% | 0.83% | +0.000 |
| HOOD | equity | 5.5790 | $74.09 | $413.35 | 0.83% | 0.83% | +0.000 |
| CVNA | equity | 5.8924 | $70.15 | $413.35 | 0.83% | 0.83% | +0.000 |
| EL | equity | 4.7915 | $86.27 | $413.35 | 0.83% | 0.83% | +0.000 |
| INTC | equity | 3.3464 | $123.52 | $413.35 | 0.83% | 0.83% | +0.000 |
| LITE | equity | 0.4538 | $910.81 | $413.35 | 0.83% | 0.83% | +0.000 |
| MU | equity | 0.4614 | $895.88 | $413.35 | 0.83% | 0.83% | +0.000 |
| NCLH | equity | 24.1725 | $17.10 | $413.35 | 0.83% | 0.83% | +0.000 |
| PLTR | equity | 3.0260 | $136.60 | $413.35 | 0.83% | 0.83% | +0.000 |
| SMCI | equity | 11.1415 | $37.10 | $413.35 | 0.83% | 0.83% | +0.000 |
| SNDK | equity | 0.2600 | $1589.55 | $413.35 | 0.83% | 0.83% | +0.000 |
| XYZ | equity | 5.9759 | $69.17 | $413.35 | 0.83% | 0.83% | +0.000 |
| __CASH__ | cash | — | — | $12,932.85 | 25.87% | 25.87% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (1 buys, 20 sells) |
| Total notional | $14,861.22 |
| Estimated turnover | 29.7% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.2952 | $503.89 | $148.73 |
| APH | sell | -0.9872 | $139.56 | $137.77 |
| APP | sell | -0.2789 | $514.24 | $143.40 |
| ARES | sell | -0.8924 | $125.28 | $111.80 |
| AXON | sell | -0.2782 | $385.30 | $107.20 |
| COHR | sell | -0.2957 | $381.35 | $112.77 |
| COIN | sell | -0.5228 | $180.01 | $94.11 |
| CVNA | sell | -1.7453 | $70.15 | $122.43 |
| DDOG | sell | -0.4975 | $223.65 | $111.27 |
| EL | sell | -1.1359 | $86.27 | $97.99 |
| EPAM | sell | -0.9320 | $99.69 | $92.91 |
| HOOD | sell | -1.5027 | $74.09 | $111.34 |
| INTC | sell | -1.0052 | $123.52 | $124.16 |
| LITE | sell | -0.0969 | $910.81 | $88.27 |
| MU | sell | -0.2330 | $895.88 | $208.76 |
| NCLH | sell | -7.8214 | $17.10 | $133.75 |
| PLTR | sell | -0.7839 | $136.60 | $107.08 |
| SMCI | sell | -3.5156 | $37.10 | $130.43 |
| SNDK | sell | -0.0926 | $1589.55 | $147.25 |
| TLT | buy | +144.7109 | $85.78 | $12,413.30 |
| XYZ | sell | -1.6842 | $69.17 | $116.50 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $503.89 | $503.89 | -0.0 | ✅ |
| APH | sell | $139.56 | $139.56 | -0.0 | ✅ |
| APP | sell | $514.24 | $514.24 | -0.0 | ✅ |
| ARES | sell | $125.28 | $125.28 | -0.0 | ✅ |
| AXON | sell | $385.30 | $385.30 | -0.0 | ✅ |
| COHR | sell | $381.35 | $381.35 | -0.0 | ✅ |
| COIN | sell | $180.01 | $180.01 | -0.0 | ✅ |
| CVNA | sell | $70.15 | $70.15 | -0.0 | ✅ |
| DDOG | sell | $223.65 | $223.65 | -0.0 | ✅ |
| EL | sell | $86.27 | $86.27 | -0.0 | ✅ |
| EPAM | sell | $99.69 | $99.69 | -0.0 | ✅ |
| HOOD | sell | $74.09 | $74.09 | -0.0 | ✅ |
| INTC | sell | $123.52 | $123.52 | -0.0 | ✅ |
| LITE | sell | $910.81 | $910.81 | -0.0 | ✅ |
| MU | sell | $895.88 | $895.88 | -0.0 | ✅ |
| NCLH | sell | $17.10 | $17.10 | -0.0 | ✅ |
| PLTR | sell | $136.60 | $136.60 | -0.0 | ✅ |
| SMCI | sell | $37.10 | $37.10 | -0.0 | ✅ |
| SNDK | sell | $1589.55 | $1589.55 | -0.0 | ✅ |
| TLT | buy | $85.78 | $85.78 | +0.0 | ✅ |
| XYZ | sell | $69.17 | $69.17 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-22

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
| Trend | 69.37% |
| Cash | 5.63% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.26 (53.6% of NAV) |
| Cash | $23,183.74 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.1918 | $124.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.1155 | $467.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.9490 | $132.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0827 | $481.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.3516 | $119.84 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.3510 | $386.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.8191 | $184.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3457 | $222.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.0784 | $102.69 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 7.0817 | $73.64 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.6377 | $68.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 5.9275 | $87.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8099 | $136.88 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5507 | $946.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.6944 | $751.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 31.9939 | $16.30 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3527 | $1478.69 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 14.6571 | $35.58 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.6601 | $68.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3796 | $377.57 | $520.91 | 1.04% | 1.04% | -0.001 |
| __CASH__ | cash | — | — | $23,183.74 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (11 buys, 8 sells) |
| Total notional | $296.80 |
| Estimated turnover | 0.6% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0445 | $467.51 | $20.79 |
| APH | sell | -0.2277 | $132.06 | $30.07 |
| APP | buy | +0.0094 | $481.68 | $4.52 |
| ARES | sell | -0.0142 | $124.41 | $1.77 |
| AXON | buy | +0.0133 | $386.00 | $5.14 |
| COIN | buy | +0.1248 | $184.99 | $23.09 |
| CVNA | sell | -0.4614 | $68.28 | $31.51 |
| DDOG | sell | -0.0460 | $222.32 | $10.24 |
| EL | sell | -0.7069 | $87.98 | $62.19 |
| EPAM | buy | +0.0246 | $102.69 | $2.53 |
| HOOD | buy | +0.2127 | $73.64 | $15.66 |
| INTC | sell | -0.0492 | $119.84 | $5.90 |
| LITE | buy | +0.0100 | $946.90 | $9.52 |
| MU | buy | +0.0101 | $751.00 | $7.60 |
| NCLH | buy | +0.3302 | $16.30 | $5.38 |
| PLTR | buy | +0.0148 | $136.88 | $2.03 |
| SMCI | sell | -0.9287 | $35.58 | $33.04 |
| SNDK | buy | +0.0145 | $1478.69 | $21.49 |
| XYZ | buy | +0.0636 | $68.08 | $4.33 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $467.51 | $467.51 | -0.0 | ✅ |
| APH | sell | $132.06 | $132.06 | -0.0 | ✅ |
| APP | buy | $481.68 | $481.68 | +0.0 | ✅ |
| ARES | sell | $124.41 | $124.41 | -0.0 | ✅ |
| AXON | buy | $386.00 | $386.00 | +0.0 | ✅ |
| COIN | buy | $184.99 | $184.99 | +0.0 | ✅ |
| CVNA | sell | $68.28 | $68.28 | -0.0 | ✅ |
| DDOG | sell | $222.32 | $222.32 | -0.0 | ✅ |
| EL | sell | $87.98 | $87.98 | -0.0 | ✅ |
| EPAM | buy | $102.69 | $102.69 | +0.0 | ✅ |
| HOOD | buy | $73.64 | $73.64 | +0.0 | ✅ |
| INTC | sell | $119.84 | $119.84 | -0.0 | ✅ |
| LITE | buy | $946.90 | $946.90 | +0.0 | ✅ |
| MU | buy | $751.00 | $751.00 | +0.0 | ✅ |
| NCLH | buy | $16.30 | $16.30 | +0.0 | ✅ |
| PLTR | buy | $136.88 | $136.88 | +0.0 | ✅ |
| SMCI | sell | $35.58 | $35.58 | -0.0 | ✅ |
| SNDK | buy | $1478.69 | $1478.69 | +0.0 | ✅ |
| XYZ | buy | $68.08 | $68.08 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-21

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
| Trend | 69.37% |
| Cash | 5.63% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.2060 | $123.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.1599 | $449.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 4.1767 | $124.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0733 | $485.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3796 | $378.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.3377 | $389.84 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.6943 | $193.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3918 | $218.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.0538 | $103.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.8691 | $75.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.0991 | $64.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.6343 | $78.61 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.4008 | $118.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5407 | $964.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.6843 | $762.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 31.6636 | $16.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.7951 | $137.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 15.5858 | $33.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3381 | $1542.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.5965 | $68.65 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (5 buys, 14 sells) |
| Total notional | $266.82 |
| Estimated turnover | 0.5% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0052 | $449.59 | $2.34 |
| APH | sell | -0.0614 | $124.86 | $7.67 |
| APP | sell | -0.0080 | $485.89 | $3.90 |
| ARES | sell | -0.0648 | $123.99 | $8.03 |
| AXON | buy | +0.0289 | $389.84 | $11.26 |
| COHR | sell | -0.0750 | $378.00 | $28.37 |
| COIN | sell | -0.0320 | $193.56 | $6.19 |
| CVNA | buy | +0.0649 | $64.39 | $4.18 |
| DDOG | sell | -0.0654 | $218.04 | $14.25 |
| EL | sell | -0.0602 | $78.61 | $4.73 |
| EPAM | buy | +0.0538 | $103.19 | $5.55 |
| HOOD | sell | -0.0145 | $75.92 | $1.10 |
| INTC | buy | +0.0170 | $118.50 | $2.02 |
| LITE | sell | -0.0601 | $964.50 | $57.93 |
| MU | sell | -0.0281 | $762.10 | $21.45 |
| NCLH | sell | -0.8691 | $16.47 | $14.31 |
| PLTR | sell | -0.0073 | $137.41 | $1.01 |
| SNDK | sell | -0.0363 | $1542.24 | $56.05 |
| XYZ | buy | +0.2400 | $68.65 | $16.48 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $449.59 | $449.59 | -0.0 | ✅ |
| APH | sell | $124.86 | $124.86 | -0.0 | ✅ |
| APP | sell | $485.89 | $485.89 | -0.0 | ✅ |
| ARES | sell | $123.99 | $123.99 | -0.0 | ✅ |
| AXON | buy | $389.84 | $389.84 | +0.0 | ✅ |
| COHR | sell | $378.00 | $378.00 | -0.0 | ✅ |
| COIN | sell | $193.56 | $193.56 | -0.0 | ✅ |
| CVNA | buy | $64.39 | $64.39 | +0.0 | ✅ |
| DDOG | sell | $218.04 | $218.04 | -0.0 | ✅ |
| EL | sell | $78.61 | $78.61 | -0.0 | ✅ |
| EPAM | buy | $103.19 | $103.19 | +0.0 | ✅ |
| HOOD | sell | $75.92 | $75.92 | -0.0 | ✅ |
| INTC | buy | $118.50 | $118.50 | +0.0 | ✅ |
| LITE | sell | $964.50 | $964.50 | -0.0 | ✅ |
| MU | sell | $762.10 | $762.10 | -0.0 | ✅ |
| NCLH | sell | $16.47 | $16.47 | -0.0 | ✅ |
| PLTR | sell | $137.41 | $137.41 | -0.0 | ✅ |
| SNDK | sell | $1542.24 | $1542.24 | -0.0 | ✅ |
| XYZ | buy | $68.65 | $68.65 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-20

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
| Trend | 69.37% |
| Cash | 5.63% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.2707 | $122.11 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.1652 | $447.58 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 4.2381 | $123.05 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0813 | $482.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.4547 | $358.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.3089 | $398.44 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.7262 | $191.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.4571 | $212.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.0000 | $104.30 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.8836 | $75.76 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.0342 | $64.91 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.6946 | $77.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.3838 | $118.96 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6008 | $868.07 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.7124 | $731.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 32.5327 | $16.03 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8024 | $137.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 15.5858 | $33.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3745 | $1392.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.3565 | $70.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (3 buys, 17 sells) |
| Total notional | $348.99 |
| Estimated turnover | 0.7% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0944 | $447.58 | $42.23 |
| APH | sell | -0.1369 | $123.05 | $16.84 |
| APP | sell | -0.0122 | $482.28 | $5.88 |
| ARES | sell | -0.0353 | $122.11 | $4.31 |
| AXON | sell | -0.0219 | $398.44 | $8.73 |
| COHR | sell | -0.0200 | $358.50 | $7.18 |
| COIN | buy | +0.0304 | $191.29 | $5.82 |
| CVNA | sell | -0.1978 | $64.91 | $12.84 |
| DDOG | buy | +0.0332 | $212.24 | $7.05 |
| EL | sell | -0.1811 | $77.90 | $14.11 |
| EPAM | sell | -0.1885 | $104.30 | $19.66 |
| HOOD | sell | -0.1485 | $75.76 | $11.25 |
| INTC | sell | -0.3229 | $118.96 | $38.41 |
| LITE | buy | +0.0149 | $868.07 | $12.90 |
| MU | sell | -0.0339 | $731.99 | $24.82 |
| NCLH | sell | -2.7276 | $16.03 | $43.72 |
| PLTR | sell | -0.0531 | $137.15 | $7.29 |
| SMCI | sell | -1.4790 | $33.46 | $49.49 |
| SNDK | sell | -0.0025 | $1392.56 | $3.49 |
| XYZ | sell | -0.1829 | $70.89 | $12.97 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $447.58 | $447.58 | -0.0 | ✅ |
| APH | sell | $123.05 | $123.05 | -0.0 | ✅ |
| APP | sell | $482.28 | $482.28 | -0.0 | ✅ |
| ARES | sell | $122.11 | $122.11 | -0.0 | ✅ |
| AXON | sell | $398.44 | $398.44 | -0.0 | ✅ |
| COHR | sell | $358.50 | $358.50 | -0.0 | ✅ |
| COIN | buy | $191.29 | $191.29 | +0.0 | ✅ |
| CVNA | sell | $64.91 | $64.91 | -0.0 | ✅ |
| DDOG | buy | $212.24 | $212.24 | +0.0 | ✅ |
| EL | sell | $77.90 | $77.90 | -0.0 | ✅ |
| EPAM | sell | $104.30 | $104.30 | -0.0 | ✅ |
| HOOD | sell | $75.76 | $75.76 | -0.0 | ✅ |
| INTC | sell | $118.96 | $118.96 | -0.0 | ✅ |
| LITE | buy | $868.07 | $868.07 | +0.0 | ✅ |
| MU | sell | $731.99 | $731.99 | -0.0 | ✅ |
| NCLH | sell | $16.03 | $16.03 | -0.0 | ✅ |
| PLTR | sell | $137.15 | $137.15 | -0.0 | ✅ |
| SMCI | sell | $33.46 | $33.46 | -0.0 | ✅ |
| SNDK | sell | $1392.56 | $1392.56 | -0.0 | ✅ |
| XYZ | sell | $70.89 | $70.89 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-19

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
| Trend | 69.37% |
| Cash | 5.63% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.46 (53.6% of NAV) |
| Cash | $23,182.54 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| AXON | equity | 1.3308 | $392.34 | $522.11 | 1.04% | 1.04% | +0.001 |
| AMD | equity | 1.2595 | $414.05 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.3060 | $121.11 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0935 | $476.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.4747 | $353.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 4.3750 | $119.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.6958 | $193.45 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.4239 | $215.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.1885 | $100.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 7.0321 | $74.16 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.2320 | $63.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.8757 | $75.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.7067 | $110.80 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5859 | $890.09 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.7463 | $698.74 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 35.2603 | $14.79 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8555 | $135.26 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.0648 | $30.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3770 | $1383.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.5394 | $69.17 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.54 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (15 buys, 4 sells) |
| Total notional | $379.67 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0298 | $414.05 | $12.36 |
| APH | buy | +0.2030 | $119.20 | $24.20 |
| APP | buy | +0.0526 | $476.90 | $25.09 |
| ARES | buy | +0.0803 | $121.11 | $9.72 |
| COHR | buy | +0.1111 | $353.63 | $39.30 |
| COIN | buy | +0.0273 | $193.45 | $5.28 |
| CVNA | buy | +0.4682 | $63.35 | $29.66 |
| DDOG | sell | -0.0836 | $215.15 | $17.98 |
| EL | buy | +0.3546 | $75.85 | $26.89 |
| EPAM | sell | -0.4178 | $100.51 | $41.99 |
| HOOD | buy | +0.2717 | $74.16 | $20.15 |
| INTC | sell | -0.0878 | $110.80 | $9.73 |
| LITE | buy | +0.0487 | $890.09 | $43.31 |
| MU | buy | +0.0267 | $698.74 | $18.65 |
| NCLH | buy | +1.6585 | $14.79 | $24.53 |
| PLTR | sell | -0.0365 | $135.26 | $4.94 |
| SMCI | buy | +0.2639 | $30.56 | $8.06 |
| SNDK | buy | +0.0065 | $1383.29 | $9.01 |
| XYZ | buy | +0.1275 | $69.17 | $8.82 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $414.05 | $414.05 | +0.0 | ✅ |
| APH | buy | $119.20 | $119.20 | +0.0 | ✅ |
| APP | buy | $476.90 | $476.90 | +0.0 | ✅ |
| ARES | buy | $121.11 | $121.11 | +0.0 | ✅ |
| COHR | buy | $353.63 | $353.63 | +0.0 | ✅ |
| COIN | buy | $193.45 | $193.45 | +0.0 | ✅ |
| CVNA | buy | $63.35 | $63.35 | +0.0 | ✅ |
| DDOG | sell | $215.15 | $215.15 | -0.0 | ✅ |
| EL | buy | $75.85 | $75.85 | +0.0 | ✅ |
| EPAM | sell | $100.51 | $100.51 | -0.0 | ✅ |
| HOOD | buy | $74.16 | $74.16 | +0.0 | ✅ |
| INTC | sell | $110.80 | $110.80 | -0.0 | ✅ |
| LITE | buy | $890.09 | $890.09 | +0.0 | ✅ |
| MU | buy | $698.74 | $698.74 | +0.0 | ✅ |
| NCLH | buy | $14.79 | $14.79 | +0.0 | ✅ |
| PLTR | sell | $135.26 | $135.26 | -0.0 | ✅ |
| SMCI | buy | $30.56 | $30.56 | +0.0 | ✅ |
| SNDK | buy | $1383.29 | $1383.29 | +0.0 | ✅ |
| XYZ | buy | $69.17 | $69.17 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-05-16

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
| Trend | 69.37% |
| Cash | 5.63% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.2258 | $123.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.2297 | $424.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 4.1720 | $125.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0409 | $501.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3636 | $382.45 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.3308 | $391.88 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.6685 | $195.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.5075 | $207.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.6063 | $93.02 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.7604 | $77.14 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.7639 | $67.17 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.5211 | $79.97 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.7945 | $108.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5372 | $970.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.7196 | $724.66 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 33.6018 | $15.52 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8921 | $133.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 16.8009 | $31.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3705 | $1407.61 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.4119 | $70.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 23 (1 buys, 22 sells) |
| Total notional | $52,352.98 |
| Estimated turnover | 104.7% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.2282 | $424.10 | $96.80 |
| APH | sell | -0.8132 | $125.00 | $101.65 |
| APP | sell | -0.2585 | $501.00 | $129.50 |
| ARES | sell | -0.8007 | $123.41 | $98.82 |
| AXON | sell | -0.2508 | $391.88 | $98.30 |
| COHR | sell | -0.4115 | $382.45 | $157.39 |
| COIN | sell | -0.4299 | $195.43 | $84.02 |
| CVNA | sell | -0.7118 | $67.17 | $47.81 |
| DDOG | sell | -0.6852 | $207.98 | $142.52 |
| EL | sell | -0.9127 | $79.97 | $72.99 |
| EPAM | sell | -0.9140 | $93.02 | $85.02 |
| GLD | sell | -11.8028 | $429.71 | $5,071.78 |
| HOOD | sell | -1.3718 | $77.14 | $105.82 |
| INTC | sell | -0.5671 | $108.77 | $61.68 |
| LITE | sell | -0.1233 | $970.70 | $119.65 |
| MU | sell | -0.1504 | $724.66 | $108.95 |
| NCLH | sell | -4.9428 | $15.52 | $76.71 |
| PLTR | sell | -0.7763 | $133.99 | $104.02 |
| SMCI | sell | -2.9707 | $31.04 | $92.21 |
| SNDK | sell | -0.0821 | $1407.61 | $115.58 |
| TLT | buy | +191.0335 | $85.78 | $16,386.85 |
| UUP | sell | -1052.0207 | $27.48 | $28,909.53 |
| XYZ | sell | -1.2135 | $70.36 | $85.38 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 23 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 23 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $424.10 | $424.10 | -0.0 | ✅ |
| APH | sell | $125.00 | $125.00 | -0.0 | ✅ |
| APP | sell | $501.00 | $501.00 | -0.0 | ✅ |
| ARES | sell | $123.41 | $123.41 | -0.0 | ✅ |
| AXON | sell | $391.88 | $391.88 | -0.0 | ✅ |
| COHR | sell | $382.45 | $382.45 | -0.0 | ✅ |
| COIN | sell | $195.43 | $195.43 | -0.0 | ✅ |
| CVNA | sell | $67.17 | $67.17 | -0.0 | ✅ |
| DDOG | sell | $207.98 | $207.98 | -0.0 | ✅ |
| EL | sell | $79.97 | $79.97 | -0.0 | ✅ |
| EPAM | sell | $93.02 | $93.02 | -0.0 | ✅ |
| GLD | sell | $429.71 | $429.71 | -0.0 | ✅ |
| HOOD | sell | $77.14 | $77.14 | -0.0 | ✅ |
| INTC | sell | $108.77 | $108.77 | -0.0 | ✅ |
| LITE | sell | $970.70 | $970.70 | -0.0 | ✅ |
| MU | sell | $724.66 | $724.66 | -0.0 | ✅ |
| NCLH | sell | $15.52 | $15.52 | -0.0 | ✅ |
| PLTR | sell | $133.99 | $133.99 | -0.0 | ✅ |
| SMCI | sell | $31.04 | $31.04 | -0.0 | ✅ |
| SNDK | sell | $1407.61 | $1407.61 | -0.0 | ✅ |
| TLT | buy | $85.78 | $85.78 | +0.0 | ✅ |
| UUP | sell | $27.48 | $27.48 | -0.0 | ✅ |
| XYZ | sell | $70.36 | $70.36 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

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
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.2258 | $123.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.2297 | $424.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 4.1720 | $125.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0409 | $501.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3636 | $382.45 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.3308 | $391.88 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 2.6685 | $195.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.5075 | $207.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.6063 | $93.02 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.7604 | $77.14 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.7639 | $67.17 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.5211 | $79.97 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.7945 | $108.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5372 | $970.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.7196 | $724.66 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 33.6018 | $15.52 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8921 | $133.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 16.8009 | $31.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3705 | $1407.61 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.4119 | $70.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

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
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 3.9962 | $130.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9968 | $523.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5532 | $146.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9331 | $558.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2361 | $421.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0162 | $513.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1774 | $164.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1408 | $243.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.3438 | $97.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.9040 | $88.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8788 | $66.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2907 | $82.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.6654 | $111.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5518 | $945.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5236 | $996.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 27.2608 | $19.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.6803 | $141.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 11.1194 | $46.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2964 | $1759.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.3565 | $70.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

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
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 3.9962 | $130.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9968 | $523.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5532 | $146.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9331 | $558.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2361 | $421.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0162 | $513.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1774 | $164.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1408 | $243.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.3438 | $97.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.9040 | $88.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8788 | $66.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2907 | $82.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.6654 | $111.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5518 | $945.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5236 | $996.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 27.2608 | $19.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.6803 | $141.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 11.1194 | $46.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2964 | $1759.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.3565 | $70.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

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
| Holdings | 21 positions + cash |
| Invested | $26,816.85 (53.6% of NAV) |
| Cash | $23,183.15 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 3.9962 | $130.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9968 | $523.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5532 | $146.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9331 | $558.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2361 | $421.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0162 | $513.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1774 | $164.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1408 | $243.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.3438 | $97.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.9040 | $88.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8788 | $66.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2907 | $82.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.6654 | $111.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5518 | $945.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5236 | $996.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 27.2608 | $19.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.6803 | $141.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 11.1194 | $46.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2964 | $1759.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.3565 | $70.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 22 (22 buys, 0 sells) |
| Total notional | $46,457.30 |
| Estimated turnover | 92.9% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| UUP | buy | +1052.0207 | $27.59 | $29,025.25 |
| GLD | buy | +11.8028 | $417.88 | $4,932.15 |
| APP | buy | +1.2994 | $480.98 | $624.99 |
| ARES | buy | +5.0265 | $124.34 | $625.00 |
| AMD | buy | +1.4579 | $428.69 | $624.99 |
| APH | buy | +4.9852 | $125.37 | $624.99 |
| COHR | buy | +1.7751 | $352.10 | $625.01 |
| AXON | buy | +1.5816 | $395.17 | $625.00 |
| DDOG | buy | +3.1927 | $195.76 | $625.00 |
| COIN | buy | +3.0984 | $201.72 | $625.01 |
| EL | buy | +7.4338 | $84.08 | $625.03 |
| EPAM | buy | +6.5203 | $95.86 | $625.04 |
| HOOD | buy | +8.1322 | $76.86 | $625.04 |
| CVNA | buy | +8.4757 | $73.74 | $625.00 |
| INTC | buy | +5.3616 | $116.57 | $625.00 |
| LITE | buy | +0.6605 | $946.20 | $624.97 |
| NCLH | buy | +38.5446 | $16.21 | $624.81 |
| MU | buy | +0.8700 | $718.38 | $624.99 |
| PLTR | buy | +4.6684 | $133.88 | $625.01 |
| SMCI | buy | +19.7716 | $31.61 | $624.98 |
| SNDK | buy | +0.4526 | $1381.02 | $625.05 |
| XYZ | buy | +8.6254 | $72.46 | $625.00 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 22 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 22 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| UUP | buy | $27.59 | $27.59 | +0.0 | ✅ |
| GLD | buy | $417.88 | $417.88 | +0.0 | ✅ |
| APP | buy | $480.98 | $480.98 | +0.0 | ✅ |
| ARES | buy | $124.34 | $124.34 | +0.0 | ✅ |
| AMD | buy | $428.69 | $428.69 | +0.0 | ✅ |
| APH | buy | $125.37 | $125.37 | +0.0 | ✅ |
| COHR | buy | $352.10 | $352.10 | +0.0 | ✅ |
| AXON | buy | $395.17 | $395.17 | +0.0 | ✅ |
| DDOG | buy | $195.76 | $195.76 | +0.0 | ✅ |
| COIN | buy | $201.72 | $201.72 | +0.0 | ✅ |
| EL | buy | $84.08 | $84.08 | +0.0 | ✅ |
| EPAM | buy | $95.86 | $95.86 | +0.0 | ✅ |
| HOOD | buy | $76.86 | $76.86 | +0.0 | ✅ |
| CVNA | buy | $73.74 | $73.74 | +0.0 | ✅ |
| INTC | buy | $116.57 | $116.57 | +0.0 | ✅ |
| LITE | buy | $946.20 | $946.20 | +0.0 | ✅ |
| NCLH | buy | $16.21 | $16.21 | +0.0 | ✅ |
| MU | buy | $718.38 | $718.38 | +0.0 | ✅ |
| PLTR | buy | $133.88 | $133.88 | +0.0 | ✅ |
| SMCI | buy | $31.61 | $31.61 | +0.0 | ✅ |
| SNDK | buy | $1381.02 | $1381.02 | +0.0 | ✅ |
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

