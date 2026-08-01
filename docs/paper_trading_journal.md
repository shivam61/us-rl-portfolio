# Phase H — Paper Trading Journal

> **Portfolio:** $50,000 NAV | Broker: Alpaca paper | Config: v H.0.0
> **Rebalance cadence:** every 14 days | **Mode:** rl_e7 (dual-mode switching active)
> **Gates:** H-1 pipeline · H-2 slippage <20 bps · H-3 turnover <35% · H-4 drift <5pp · H-5 RL mode · H-6 Sharpe · H-7 data parity · H-8 audit trail

Newest entries at the top. Updated automatically by `scripts/generate_paper_journal.py`.

---

## 2026-08-01

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `b5_only` |
| Rebalance day | no |
| Signal | ✅ OK |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Allocation
| Sleeve | Weight |
|--------|--------|
| Equity | 25.00% |
| Trend | 69.16% |
| Cash | 5.84% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $29,829.06 (59.7% of NAV) |
| Cash | $20,170.94 (40.3% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 4.17 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 224.5546 | $82.25 | $18,469.61 | 36.94% | 32.77% | +4.166 |
| SNDK | equity | 0.8030 | $1214.83 | $975.55 | 1.95% | 1.04% | +0.908 |
| COHR | equity | 3.1661 | $262.89 | $832.34 | 1.66% | 1.04% | +0.622 |
| LITE | equity | 1.1449 | $713.94 | $817.39 | 1.63% | 1.04% | +0.592 |
| AMD | equity | 1.6295 | $476.15 | $775.87 | 1.55% | 1.04% | +0.509 |
| MU | equity | 0.9397 | $823.03 | $773.40 | 1.55% | 1.04% | +0.504 |
| SMCI | equity | 24.8516 | $28.40 | $705.79 | 1.41% | 1.04% | +0.369 |
| HOOD | equity | 7.5195 | $86.56 | $650.89 | 1.30% | 1.04% | +0.259 |
| INTC | equity | 7.1024 | $90.20 | $640.64 | 1.28% | 1.04% | +0.238 |
| ARES | equity | 4.1183 | $128.09 | $527.51 | 1.05% | 1.04% | +0.012 |
| PLTR | equity | 4.2445 | $123.06 | $522.33 | 1.04% | 1.04% | +0.002 |
| COIN | equity | 3.5044 | $146.26 | $512.55 | 1.03% | 1.04% | -0.018 |
| APH | equity | 3.1847 | $160.70 | $511.79 | 1.02% | 1.04% | -0.019 |
| NCLH | equity | 26.1611 | $18.53 | $484.77 | 0.97% | 1.04% | -0.073 |
| APP | equity | 1.1565 | $395.90 | $457.87 | 0.92% | 1.04% | -0.127 |
| EL | equity | 4.9467 | $83.90 | $415.03 | 0.83% | 1.04% | -0.213 |
| CVNA | equity | 6.4678 | $62.36 | $403.33 | 0.81% | 1.04% | -0.236 |
| AXON | equity | 0.7505 | $527.76 | $396.07 | 0.79% | 1.04% | -0.251 |
| DDOG | equity | 1.4365 | $267.97 | $384.94 | 0.77% | 1.04% | -0.273 |
| XYZ | equity | 4.7360 | $81.24 | $384.75 | 0.77% | 1.04% | -0.274 |
| EPAM | equity | 1.7681 | $105.56 | $186.64 | 0.37% | 1.04% | -0.670 |
| __CASH__ | cash | — | — | $20,170.94 | 40.34% | 40.34% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (11 buys, 9 sells) |
| Total notional | $1,343.97 |
| Estimated turnover | 2.7% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0961 | $476.15 | $45.76 |
| APH | sell | -0.1707 | $160.70 | $27.43 |
| APP | sell | -0.0132 | $395.90 | $5.22 |
| ARES | sell | -0.0508 | $128.09 | $6.51 |
| AXON | sell | -0.0500 | $527.76 | $26.39 |
| COHR | buy | +0.1370 | $262.89 | $36.01 |
| COIN | buy | +0.2710 | $146.26 | $39.63 |
| CVNA | sell | -0.2628 | $62.36 | $16.39 |
| DDOG | sell | -0.1664 | $267.97 | $44.60 |
| EL | sell | -0.2795 | $83.90 | $23.45 |
| EPAM | sell | -0.8638 | $105.56 | $91.18 |
| HOOD | buy | +0.5300 | $86.56 | $45.88 |
| INTC | buy | +0.1328 | $90.20 | $11.98 |
| LITE | buy | +0.0470 | $713.94 | $33.53 |
| MU | buy | +0.0674 | $823.03 | $55.45 |
| NCLH | buy | +1.2205 | $18.53 | $22.62 |
| SMCI | buy | +1.0371 | $28.40 | $29.45 |
| SNDK | buy | +0.0663 | $1214.83 | $80.49 |
| TLT | buy | +8.1988 | $82.25 | $674.35 |
| XYZ | sell | -0.3403 | $81.24 | $27.65 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $476.15 | $476.15 | +0.0 | ✅ |
| APH | sell | $160.70 | $160.70 | -0.0 | ✅ |
| APP | sell | $395.90 | $395.90 | -0.0 | ✅ |
| ARES | sell | $128.09 | $128.09 | -0.0 | ✅ |
| AXON | sell | $527.76 | $527.76 | -0.0 | ✅ |
| COHR | buy | $262.89 | $262.89 | +0.0 | ✅ |
| COIN | buy | $146.26 | $146.26 | +0.0 | ✅ |
| CVNA | sell | $62.36 | $62.36 | -0.0 | ✅ |
| DDOG | sell | $267.97 | $267.97 | -0.0 | ✅ |
| EL | sell | $83.90 | $83.90 | -0.0 | ✅ |
| EPAM | sell | $105.56 | $105.56 | -0.0 | ✅ |
| HOOD | buy | $86.56 | $86.56 | +0.0 | ✅ |
| INTC | buy | $90.20 | $90.20 | +0.0 | ✅ |
| LITE | buy | $713.94 | $713.94 | +0.0 | ✅ |
| MU | buy | $823.03 | $823.03 | +0.0 | ✅ |
| NCLH | buy | $18.53 | $18.53 | +0.0 | ✅ |
| SMCI | buy | $28.40 | $28.40 | +0.0 | ✅ |
| SNDK | buy | $1214.83 | $1214.83 | +0.0 | ✅ |
| TLT | buy | $82.25 | $82.25 | +0.0 | ✅ |
| XYZ | sell | $81.24 | $81.24 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 4.17 pp max | ✅ |
| H-5 RL mode | b5_only | ⚠️ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-31

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `b5_only` |
| Rebalance day | no |
| Signal | ✅ OK |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Allocation
| Sleeve | Weight |
|--------|--------|
| Equity | 25.00% |
| Trend | 69.16% |
| Cash | 5.84% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $29,829.06 (59.7% of NAV) |
| Cash | $20,170.94 (40.3% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 4.17 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 224.5546 | $82.25 | $18,469.61 | 36.94% | 32.77% | +4.166 |
| SNDK | equity | 0.8030 | $1214.83 | $975.55 | 1.95% | 1.04% | +0.908 |
| COHR | equity | 3.1661 | $262.89 | $832.34 | 1.66% | 1.04% | +0.622 |
| LITE | equity | 1.1449 | $713.94 | $817.39 | 1.63% | 1.04% | +0.592 |
| AMD | equity | 1.6295 | $476.15 | $775.87 | 1.55% | 1.04% | +0.509 |
| MU | equity | 0.9397 | $823.03 | $773.40 | 1.55% | 1.04% | +0.504 |
| SMCI | equity | 24.8516 | $28.40 | $705.79 | 1.41% | 1.04% | +0.369 |
| HOOD | equity | 7.5195 | $86.56 | $650.89 | 1.30% | 1.04% | +0.259 |
| INTC | equity | 7.1024 | $90.20 | $640.64 | 1.28% | 1.04% | +0.238 |
| ARES | equity | 4.1183 | $128.09 | $527.51 | 1.05% | 1.04% | +0.012 |
| PLTR | equity | 4.2445 | $123.06 | $522.33 | 1.04% | 1.04% | +0.002 |
| COIN | equity | 3.5044 | $146.26 | $512.55 | 1.03% | 1.04% | -0.018 |
| APH | equity | 3.1847 | $160.70 | $511.79 | 1.02% | 1.04% | -0.019 |
| NCLH | equity | 26.1611 | $18.53 | $484.77 | 0.97% | 1.04% | -0.073 |
| APP | equity | 1.1565 | $395.90 | $457.87 | 0.92% | 1.04% | -0.127 |
| EL | equity | 4.9467 | $83.90 | $415.03 | 0.83% | 1.04% | -0.213 |
| CVNA | equity | 6.4678 | $62.36 | $403.33 | 0.81% | 1.04% | -0.236 |
| AXON | equity | 0.7505 | $527.76 | $396.07 | 0.79% | 1.04% | -0.251 |
| DDOG | equity | 1.4365 | $267.97 | $384.94 | 0.77% | 1.04% | -0.273 |
| XYZ | equity | 4.7360 | $81.24 | $384.75 | 0.77% | 1.04% | -0.274 |
| EPAM | equity | 1.7681 | $105.56 | $186.64 | 0.37% | 1.04% | -0.670 |
| __CASH__ | cash | — | — | $20,170.94 | 40.34% | 40.34% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (11 buys, 9 sells) |
| Total notional | $1,343.97 |
| Estimated turnover | 2.7% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0961 | $476.15 | $45.76 |
| APH | sell | -0.1707 | $160.70 | $27.43 |
| APP | sell | -0.0132 | $395.90 | $5.22 |
| ARES | sell | -0.0508 | $128.09 | $6.51 |
| AXON | sell | -0.0500 | $527.76 | $26.39 |
| COHR | buy | +0.1370 | $262.89 | $36.01 |
| COIN | buy | +0.2710 | $146.26 | $39.63 |
| CVNA | sell | -0.2628 | $62.36 | $16.39 |
| DDOG | sell | -0.1664 | $267.97 | $44.60 |
| EL | sell | -0.2795 | $83.90 | $23.45 |
| EPAM | sell | -0.8638 | $105.56 | $91.18 |
| HOOD | buy | +0.5300 | $86.56 | $45.88 |
| INTC | buy | +0.1328 | $90.20 | $11.98 |
| LITE | buy | +0.0470 | $713.94 | $33.53 |
| MU | buy | +0.0674 | $823.03 | $55.45 |
| NCLH | buy | +1.2205 | $18.53 | $22.62 |
| SMCI | buy | +1.0371 | $28.40 | $29.45 |
| SNDK | buy | +0.0663 | $1214.83 | $80.49 |
| TLT | buy | +8.1988 | $82.25 | $674.35 |
| XYZ | sell | -0.3403 | $81.24 | $27.65 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $476.15 | $476.15 | +0.0 | ✅ |
| APH | sell | $160.70 | $160.70 | -0.0 | ✅ |
| APP | sell | $395.90 | $395.90 | -0.0 | ✅ |
| ARES | sell | $128.09 | $128.09 | -0.0 | ✅ |
| AXON | sell | $527.76 | $527.76 | -0.0 | ✅ |
| COHR | buy | $262.89 | $262.89 | +0.0 | ✅ |
| COIN | buy | $146.26 | $146.26 | +0.0 | ✅ |
| CVNA | sell | $62.36 | $62.36 | -0.0 | ✅ |
| DDOG | sell | $267.97 | $267.97 | -0.0 | ✅ |
| EL | sell | $83.90 | $83.90 | -0.0 | ✅ |
| EPAM | sell | $105.56 | $105.56 | -0.0 | ✅ |
| HOOD | buy | $86.56 | $86.56 | +0.0 | ✅ |
| INTC | buy | $90.20 | $90.20 | +0.0 | ✅ |
| LITE | buy | $713.94 | $713.94 | +0.0 | ✅ |
| MU | buy | $823.03 | $823.03 | +0.0 | ✅ |
| NCLH | buy | $18.53 | $18.53 | +0.0 | ✅ |
| SMCI | buy | $28.40 | $28.40 | +0.0 | ✅ |
| SNDK | buy | $1214.83 | $1214.83 | +0.0 | ✅ |
| TLT | buy | $82.25 | $82.25 | +0.0 | ✅ |
| XYZ | sell | $81.24 | $81.24 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 4.17 pp max | ✅ |
| H-5 RL mode | b5_only | ⚠️ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-30

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `b5_only` |
| Rebalance day | no |
| Signal | ✅ OK |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Allocation
| Sleeve | Weight |
|--------|--------|
| Equity | 25.00% |
| Trend | 69.16% |
| Cash | 5.84% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $28,216.38 (56.4% of NAV) |
| Cash | $21,783.62 (43.6% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 1.47 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 208.1570 | $82.25 | $17,120.92 | 34.24% | 32.77% | +1.468 |
| SNDK | equity | 0.6705 | $1214.83 | $814.56 | 1.63% | 1.04% | +0.586 |
| COHR | equity | 2.8921 | $262.89 | $760.32 | 1.52% | 1.04% | +0.478 |
| LITE | equity | 1.0510 | $713.94 | $750.34 | 1.50% | 1.04% | +0.458 |
| AMD | equity | 1.4373 | $476.15 | $684.35 | 1.37% | 1.04% | +0.326 |
| MU | equity | 0.8050 | $823.03 | $662.50 | 1.32% | 1.04% | +0.282 |
| SMCI | equity | 22.7774 | $28.40 | $646.88 | 1.29% | 1.04% | +0.251 |
| INTC | equity | 6.8369 | $90.20 | $616.69 | 1.23% | 1.04% | +0.190 |
| APH | equity | 3.5261 | $160.70 | $566.65 | 1.13% | 1.04% | +0.090 |
| HOOD | equity | 6.4594 | $86.56 | $559.12 | 1.12% | 1.04% | +0.075 |
| ARES | equity | 4.2200 | $128.09 | $540.54 | 1.08% | 1.04% | +0.038 |
| PLTR | equity | 4.2445 | $123.06 | $522.33 | 1.04% | 1.04% | +0.002 |
| DDOG | equity | 1.7693 | $267.97 | $474.13 | 0.95% | 1.04% | -0.095 |
| APP | equity | 1.1829 | $395.90 | $468.30 | 0.94% | 1.04% | -0.106 |
| EL | equity | 5.5057 | $83.90 | $461.93 | 0.92% | 1.04% | -0.119 |
| AXON | equity | 0.8505 | $527.76 | $448.85 | 0.90% | 1.04% | -0.145 |
| XYZ | equity | 5.4166 | $81.24 | $440.04 | 0.88% | 1.04% | -0.163 |
| NCLH | equity | 23.7202 | $18.53 | $439.53 | 0.88% | 1.04% | -0.164 |
| CVNA | equity | 6.9934 | $62.36 | $436.11 | 0.87% | 1.04% | -0.171 |
| COIN | equity | 2.9624 | $146.26 | $433.28 | 0.87% | 1.04% | -0.176 |
| EPAM | equity | 3.4957 | $105.56 | $369.01 | 0.74% | 1.04% | -0.305 |
| __CASH__ | cash | — | — | $21,783.62 | 43.57% | 43.57% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (12 buys, 9 sells) |
| Total notional | $1,204.21 |
| Estimated turnover | 2.4% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0753 | $485.39 | $36.53 |
| APH | sell | -0.1528 | $159.82 | $24.42 |
| APP | sell | -0.0392 | $403.87 | $15.82 |
| ARES | buy | +0.0794 | $124.12 | $9.85 |
| AXON | sell | -0.0454 | $525.30 | $23.84 |
| COHR | buy | +0.2471 | $249.06 | $61.55 |
| COIN | sell | -0.1065 | $163.58 | $17.43 |
| CVNA | sell | -0.1376 | $61.44 | $8.45 |
| DDOG | sell | -0.1707 | $268.56 | $45.84 |
| EL | sell | -0.3512 | $84.88 | $29.81 |
| EPAM | sell | -0.7732 | $103.66 | $80.15 |
| HOOD | buy | +0.5273 | $86.60 | $45.66 |
| INTC | buy | +0.0738 | $91.13 | $6.72 |
| LITE | buy | +0.0688 | $693.24 | $47.67 |
| MU | buy | +0.0300 | $874.66 | $26.21 |
| NCLH | buy | +0.9348 | $18.72 | $17.50 |
| PLTR | buy | +0.0229 | $122.26 | $2.80 |
| SMCI | buy | +1.4808 | $27.73 | $41.06 |
| SNDK | buy | +0.0444 | $1279.96 | $56.85 |
| TLT | buy | +6.8753 | $82.80 | $569.28 |
| XYZ | sell | -0.4452 | $82.59 | $36.77 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 239.8 bps | ⚠️ above target |
| Flagged trades (> 30 bps) | 19 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $476.15 | $485.39 | -190.4 | 🚨 |
| APH | sell | $160.70 | $159.82 | -55.1 | 🚨 |
| APP | sell | $395.90 | $403.87 | +197.3 | 🚨 |
| ARES | buy | $128.09 | $124.12 | +319.9 | 🚨 |
| AXON | sell | $527.76 | $525.30 | -46.8 | 🚨 |
| COHR | buy | $262.89 | $249.06 | +555.3 | 🚨 |
| COIN | sell | $146.26 | $163.58 | +1058.8 | 🚨 |
| CVNA | sell | $62.36 | $61.44 | -149.7 | 🚨 |
| DDOG | sell | $267.97 | $268.56 | +22.0 | ✅ |
| EL | sell | $83.90 | $84.88 | +115.5 | 🚨 |
| EPAM | sell | $105.56 | $103.66 | -183.3 | 🚨 |
| HOOD | buy | $86.56 | $86.60 | -4.6 | ✅ |
| INTC | buy | $90.20 | $91.13 | -102.0 | 🚨 |
| LITE | buy | $713.94 | $693.24 | +298.6 | 🚨 |
| MU | buy | $823.03 | $874.66 | -590.3 | 🚨 |
| NCLH | buy | $18.53 | $18.72 | -101.5 | 🚨 |
| PLTR | buy | $123.06 | $122.26 | +65.4 | 🚨 |
| SMCI | buy | $28.40 | $27.73 | +241.6 | 🚨 |
| SNDK | buy | $1214.83 | $1279.96 | -508.8 | 🚨 |
| TLT | buy | $82.25 | $82.80 | -66.4 | 🚨 |
| XYZ | sell | $81.24 | $82.59 | +163.5 | 🚨 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 239.8 bps avg | ⚠️ T=0 artifact |
| H-4 Weight drift | 1.47 pp max | ✅ |
| H-5 RL mode | b5_only | ⚠️ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-29

### Pipeline
| Field | Value |
|-------|-------|
| Mode | `b5_only` |
| Rebalance day | no |
| Signal | ✅ OK |
| Drift flags active | ✅ no (0) |
| Pipeline errors | none |

### Allocation
| Sleeve | Weight |
|--------|--------|
| Equity | 25.00% |
| Trend | 69.16% |
| Cash | 5.84% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $27,760.39 (55.5% of NAV) |
| Cash | $22,239.61 (44.5% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.56 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 201.2817 | $82.80 | $16,666.12 | 33.33% | 32.77% | +0.559 |
| SNDK | equity | 0.6261 | $1279.96 | $801.38 | 1.60% | 1.04% | +0.560 |
| LITE | equity | 0.9822 | $693.24 | $680.91 | 1.36% | 1.04% | +0.319 |
| MU | equity | 0.7750 | $874.66 | $677.85 | 1.36% | 1.04% | +0.313 |
| AMD | equity | 1.3620 | $485.39 | $661.10 | 1.32% | 1.04% | +0.279 |
| COHR | equity | 2.6450 | $249.06 | $658.77 | 1.32% | 1.04% | +0.274 |
| INTC | equity | 6.7631 | $91.13 | $616.32 | 1.23% | 1.04% | +0.190 |
| SMCI | equity | 21.2966 | $27.73 | $590.56 | 1.18% | 1.04% | +0.138 |
| APH | equity | 3.6789 | $159.82 | $587.97 | 1.18% | 1.04% | +0.133 |
| DDOG | equity | 1.9400 | $268.56 | $521.01 | 1.04% | 1.04% | -0.001 |
| PLTR | equity | 4.2216 | $122.26 | $516.14 | 1.03% | 1.04% | -0.011 |
| ARES | equity | 4.1406 | $124.12 | $513.93 | 1.03% | 1.04% | -0.015 |
| HOOD | equity | 5.9321 | $86.60 | $513.72 | 1.03% | 1.04% | -0.016 |
| COIN | equity | 3.0690 | $163.58 | $502.02 | 1.00% | 1.04% | -0.039 |
| EL | equity | 5.8569 | $84.88 | $497.14 | 0.99% | 1.04% | -0.049 |
| APP | equity | 1.2220 | $403.87 | $493.54 | 0.99% | 1.04% | -0.056 |
| XYZ | equity | 5.8618 | $82.59 | $484.13 | 0.97% | 1.04% | -0.075 |
| AXON | equity | 0.8958 | $525.30 | $470.59 | 0.94% | 1.04% | -0.102 |
| EPAM | equity | 4.2690 | $103.66 | $442.52 | 0.89% | 1.04% | -0.158 |
| CVNA | equity | 7.1310 | $61.44 | $438.13 | 0.88% | 1.04% | -0.167 |
| NCLH | equity | 22.7853 | $18.72 | $426.54 | 0.85% | 1.04% | -0.190 |
| __CASH__ | cash | — | — | $22,239.61 | 44.48% | 44.48% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (11 buys, 9 sells) |
| Total notional | $1,636.01 |
| Estimated turnover | 3.3% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.2149 | $429.56 | $92.31 |
| APH | buy | +0.0536 | $150.31 | $8.06 |
| APP | sell | -0.0249 | $399.46 | $9.95 |
| ARES | buy | +0.0632 | $124.60 | $7.87 |
| AXON | sell | -0.0564 | $531.20 | $29.96 |
| COHR | buy | +0.5018 | $222.05 | $111.43 |
| COIN | sell | -0.0370 | $160.09 | $5.93 |
| CVNA | sell | -0.7621 | $66.32 | $50.55 |
| DDOG | sell | -0.1386 | $264.20 | $36.63 |
| EL | sell | -0.2965 | $84.13 | $24.94 |
| EPAM | sell | -0.9253 | $106.89 | $98.90 |
| HOOD | buy | +0.3101 | $89.84 | $27.86 |
| INTC | buy | +0.7202 | $81.88 | $58.97 |
| LITE | buy | +0.1823 | $602.35 | $109.80 |
| MU | buy | +0.1394 | $739.00 | $103.03 |
| NCLH | sell | -1.7905 | $20.75 | $37.15 |
| SMCI | buy | +2.9662 | $25.70 | $76.23 |
| SNDK | buy | +0.1503 | $1015.89 | $152.71 |
| TLT | buy | +6.7559 | $82.85 | $559.73 |
| XYZ | sell | -0.4137 | $82.18 | $34.00 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 708.9 bps | ⚠️ above target |
| Flagged trades (> 30 bps) | 19 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $485.39 | $429.56 | +1299.7 | 🚨 |
| APH | buy | $159.82 | $150.31 | +632.7 | 🚨 |
| APP | sell | $403.87 | $399.46 | -110.4 | 🚨 |
| ARES | buy | $124.12 | $124.60 | -38.5 | 🚨 |
| AXON | sell | $525.30 | $531.20 | +111.1 | 🚨 |
| COHR | buy | $249.06 | $222.05 | +1216.4 | 🚨 |
| COIN | sell | $163.58 | $160.09 | -218.0 | 🚨 |
| CVNA | sell | $61.44 | $66.32 | +735.8 | 🚨 |
| DDOG | sell | $268.56 | $264.20 | -165.0 | 🚨 |
| EL | sell | $84.88 | $84.13 | -89.2 | 🚨 |
| EPAM | sell | $103.66 | $106.89 | +302.2 | 🚨 |
| HOOD | buy | $86.60 | $89.84 | -360.6 | 🚨 |
| INTC | buy | $91.13 | $81.88 | +1129.7 | 🚨 |
| LITE | buy | $693.24 | $602.35 | +1508.9 | 🚨 |
| MU | buy | $874.66 | $739.00 | +1835.7 | 🚨 |
| NCLH | sell | $18.72 | $20.75 | +978.3 | 🚨 |
| SMCI | buy | $27.73 | $25.70 | +789.9 | 🚨 |
| SNDK | buy | $1279.96 | $1015.89 | +2599.4 | 🚨 |
| TLT | buy | $82.80 | $82.85 | -6.0 | ✅ |
| XYZ | sell | $82.59 | $82.18 | -49.9 | 🚨 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 708.9 bps avg | ⚠️ T=0 artifact |
| H-4 Weight drift | 0.56 pp max | ✅ |
| H-5 RL mode | b5_only | ⚠️ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-28

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
| Trend | 69.16% |
| Cash | 5.84% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,235.56 (52.5% of NAV) |
| Cash | $23,764.44 (47.5% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.54 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 194.5258 | $82.85 | $16,116.46 | 32.23% | 32.77% | -0.541 |
| EPAM | equity | 5.1942 | $106.89 | $555.21 | 1.11% | 1.04% | +0.067 |
| DDOG | equity | 2.0787 | $264.20 | $549.19 | 1.10% | 1.04% | +0.055 |
| APH | equity | 3.6253 | $150.31 | $544.92 | 1.09% | 1.04% | +0.047 |
| CVNA | equity | 7.8931 | $66.32 | $523.47 | 1.05% | 1.04% | +0.004 |
| PLTR | equity | 4.2216 | $123.00 | $519.26 | 1.04% | 1.04% | -0.004 |
| EL | equity | 6.1534 | $84.13 | $517.68 | 1.04% | 1.04% | -0.008 |
| XYZ | equity | 6.2756 | $82.18 | $515.73 | 1.03% | 1.04% | -0.012 |
| NCLH | equity | 24.5759 | $20.75 | $509.95 | 1.02% | 1.04% | -0.023 |
| ARES | equity | 4.0774 | $124.60 | $508.04 | 1.02% | 1.04% | -0.027 |
| AXON | equity | 0.9523 | $531.20 | $505.84 | 1.01% | 1.04% | -0.031 |
| HOOD | equity | 5.6220 | $89.84 | $505.08 | 1.01% | 1.04% | -0.033 |
| APP | equity | 1.2470 | $399.46 | $498.11 | 1.00% | 1.04% | -0.047 |
| COIN | equity | 3.1060 | $160.09 | $497.24 | 0.99% | 1.04% | -0.048 |
| INTC | equity | 6.0429 | $81.88 | $494.79 | 0.99% | 1.04% | -0.053 |
| AMD | equity | 1.1471 | $429.56 | $492.75 | 0.99% | 1.04% | -0.058 |
| SNDK | equity | 0.4758 | $1015.89 | $483.34 | 0.97% | 1.04% | -0.076 |
| LITE | equity | 0.7999 | $602.35 | $481.84 | 0.96% | 1.04% | -0.079 |
| COHR | equity | 2.1432 | $222.05 | $475.89 | 0.95% | 1.04% | -0.091 |
| SMCI | equity | 18.3304 | $25.70 | $471.09 | 0.94% | 1.04% | -0.101 |
| MU | equity | 0.6356 | $739.00 | $469.68 | 0.94% | 1.04% | -0.104 |
| __CASH__ | cash | — | — | $23,764.44 | 47.53% | 47.53% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (10 buys, 11 sells) |
| Total notional | $1,153.53 |
| Estimated turnover | 2.3% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.1480 | $454.62 | $67.27 |
| APH | buy | +0.2094 | $143.85 | $30.13 |
| APP | sell | -0.0835 | $418.22 | $34.91 |
| ARES | sell | -0.0448 | $127.90 | $5.73 |
| AXON | sell | -0.0859 | $547.65 | $47.04 |
| COHR | buy | +0.2964 | $243.33 | $72.13 |
| COIN | sell | -0.1886 | $167.90 | $31.66 |
| CVNA | sell | -0.7324 | $66.07 | $48.39 |
| DDOG | sell | -0.0339 | $250.88 | $8.49 |
| EL | sell | -0.3418 | $84.75 | $28.97 |
| EPAM | sell | -0.6099 | $100.40 | $61.23 |
| HOOD | buy | +0.1274 | $92.76 | $11.81 |
| INTC | buy | +0.3940 | $86.30 | $34.01 |
| LITE | buy | +0.1164 | $651.93 | $75.91 |
| MU | buy | +0.0693 | $820.53 | $56.86 |
| NCLH | sell | -2.3472 | $21.22 | $49.81 |
| PLTR | sell | -0.0209 | $123.53 | $2.59 |
| SMCI | buy | +1.0048 | $28.45 | $28.59 |
| SNDK | buy | +0.1128 | $1096.10 | $123.59 |
| TLT | buy | +3.4923 | $84.24 | $294.19 |
| XYZ | sell | -0.4840 | $83.10 | $40.22 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 450.2 bps | ⚠️ above target |
| Flagged trades (> 30 bps) | 21 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $429.56 | $454.62 | -551.2 | 🚨 |
| APH | buy | $150.31 | $143.85 | +449.1 | 🚨 |
| APP | sell | $399.46 | $418.22 | +448.6 | 🚨 |
| ARES | sell | $124.60 | $127.90 | +258.0 | 🚨 |
| AXON | sell | $531.20 | $547.65 | +300.4 | 🚨 |
| COHR | buy | $222.05 | $243.33 | -874.5 | 🚨 |
| COIN | sell | $160.09 | $167.90 | +465.2 | 🚨 |
| CVNA | sell | $66.32 | $66.07 | -37.8 | 🚨 |
| DDOG | sell | $264.20 | $250.88 | -530.9 | 🚨 |
| EL | sell | $84.13 | $84.75 | +73.2 | 🚨 |
| EPAM | sell | $106.89 | $100.40 | -646.4 | 🚨 |
| HOOD | buy | $89.84 | $92.76 | -314.8 | 🚨 |
| INTC | buy | $81.88 | $86.30 | -512.2 | 🚨 |
| LITE | buy | $602.35 | $651.93 | -760.5 | 🚨 |
| MU | buy | $739.00 | $820.53 | -993.6 | 🚨 |
| NCLH | sell | $20.75 | $21.22 | +221.5 | 🚨 |
| PLTR | sell | $123.00 | $123.53 | +42.9 | 🚨 |
| SMCI | buy | $25.70 | $28.45 | -966.6 | 🚨 |
| SNDK | buy | $1015.89 | $1096.10 | -731.8 | 🚨 |
| TLT | buy | $82.85 | $84.24 | -165.0 | 🚨 |
| XYZ | sell | $82.18 | $83.10 | +110.7 | 🚨 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 450.2 bps avg | ⚠️ T=0 artifact |
| H-4 Weight drift | 0.54 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

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
| Invested | $29,829.06 (59.7% of NAV) |
| Cash | $20,170.94 (40.3% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 4.17 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 224.5546 | $82.25 | $18,469.61 | 36.94% | 32.77% | +4.166 |
| SNDK | equity | 0.8030 | $1214.83 | $975.55 | 1.95% | 1.04% | +0.908 |
| COHR | equity | 3.1661 | $262.89 | $832.34 | 1.66% | 1.04% | +0.622 |
| LITE | equity | 1.1449 | $713.94 | $817.39 | 1.63% | 1.04% | +0.592 |
| AMD | equity | 1.6295 | $476.15 | $775.87 | 1.55% | 1.04% | +0.509 |
| MU | equity | 0.9397 | $823.03 | $773.40 | 1.55% | 1.04% | +0.504 |
| SMCI | equity | 24.8516 | $28.40 | $705.79 | 1.41% | 1.04% | +0.369 |
| HOOD | equity | 7.5195 | $86.56 | $650.89 | 1.30% | 1.04% | +0.259 |
| INTC | equity | 7.1024 | $90.20 | $640.64 | 1.28% | 1.04% | +0.238 |
| ARES | equity | 4.1183 | $128.09 | $527.51 | 1.05% | 1.04% | +0.012 |
| PLTR | equity | 4.2445 | $123.06 | $522.33 | 1.04% | 1.04% | +0.002 |
| COIN | equity | 3.5044 | $146.26 | $512.55 | 1.03% | 1.04% | -0.018 |
| APH | equity | 3.1847 | $160.70 | $511.79 | 1.02% | 1.04% | -0.019 |
| NCLH | equity | 26.1611 | $18.53 | $484.77 | 0.97% | 1.04% | -0.073 |
| APP | equity | 1.1565 | $395.90 | $457.87 | 0.92% | 1.04% | -0.127 |
| EL | equity | 4.9467 | $83.90 | $415.03 | 0.83% | 1.04% | -0.213 |
| CVNA | equity | 6.4678 | $62.36 | $403.33 | 0.81% | 1.04% | -0.236 |
| AXON | equity | 0.7505 | $527.76 | $396.07 | 0.79% | 1.04% | -0.251 |
| DDOG | equity | 1.4365 | $267.97 | $384.94 | 0.77% | 1.04% | -0.273 |
| XYZ | equity | 4.7360 | $81.24 | $384.75 | 0.77% | 1.04% | -0.274 |
| EPAM | equity | 1.7681 | $105.56 | $186.64 | 0.37% | 1.04% | -0.670 |
| __CASH__ | cash | — | — | $20,170.94 | 40.34% | 40.34% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 4.17 pp max | ✅ |
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
| Invested | $29,829.06 (59.7% of NAV) |
| Cash | $20,170.94 (40.3% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 4.17 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 224.5546 | $82.25 | $18,469.61 | 36.94% | 32.77% | +4.166 |
| SNDK | equity | 0.8030 | $1214.83 | $975.55 | 1.95% | 1.04% | +0.908 |
| COHR | equity | 3.1661 | $262.89 | $832.34 | 1.66% | 1.04% | +0.622 |
| LITE | equity | 1.1449 | $713.94 | $817.39 | 1.63% | 1.04% | +0.592 |
| AMD | equity | 1.6295 | $476.15 | $775.87 | 1.55% | 1.04% | +0.509 |
| MU | equity | 0.9397 | $823.03 | $773.40 | 1.55% | 1.04% | +0.504 |
| SMCI | equity | 24.8516 | $28.40 | $705.79 | 1.41% | 1.04% | +0.369 |
| HOOD | equity | 7.5195 | $86.56 | $650.89 | 1.30% | 1.04% | +0.259 |
| INTC | equity | 7.1024 | $90.20 | $640.64 | 1.28% | 1.04% | +0.238 |
| ARES | equity | 4.1183 | $128.09 | $527.51 | 1.05% | 1.04% | +0.012 |
| PLTR | equity | 4.2445 | $123.06 | $522.33 | 1.04% | 1.04% | +0.002 |
| COIN | equity | 3.5044 | $146.26 | $512.55 | 1.03% | 1.04% | -0.018 |
| APH | equity | 3.1847 | $160.70 | $511.79 | 1.02% | 1.04% | -0.019 |
| NCLH | equity | 26.1611 | $18.53 | $484.77 | 0.97% | 1.04% | -0.073 |
| APP | equity | 1.1565 | $395.90 | $457.87 | 0.92% | 1.04% | -0.127 |
| EL | equity | 4.9467 | $83.90 | $415.03 | 0.83% | 1.04% | -0.213 |
| CVNA | equity | 6.4678 | $62.36 | $403.33 | 0.81% | 1.04% | -0.236 |
| AXON | equity | 0.7505 | $527.76 | $396.07 | 0.79% | 1.04% | -0.251 |
| DDOG | equity | 1.4365 | $267.97 | $384.94 | 0.77% | 1.04% | -0.273 |
| XYZ | equity | 4.7360 | $81.24 | $384.75 | 0.77% | 1.04% | -0.274 |
| EPAM | equity | 1.7681 | $105.56 | $186.64 | 0.37% | 1.04% | -0.670 |
| __CASH__ | cash | — | — | $20,170.94 | 40.34% | 40.34% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 4.17 pp max | ✅ |
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
| Invested | $29,829.06 (59.7% of NAV) |
| Cash | $20,170.94 (40.3% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 4.17 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 224.5546 | $82.25 | $18,469.61 | 36.94% | 32.77% | +4.166 |
| SNDK | equity | 0.8030 | $1214.83 | $975.55 | 1.95% | 1.04% | +0.908 |
| COHR | equity | 3.1661 | $262.89 | $832.34 | 1.66% | 1.04% | +0.622 |
| LITE | equity | 1.1449 | $713.94 | $817.39 | 1.63% | 1.04% | +0.592 |
| AMD | equity | 1.6295 | $476.15 | $775.87 | 1.55% | 1.04% | +0.509 |
| MU | equity | 0.9397 | $823.03 | $773.40 | 1.55% | 1.04% | +0.504 |
| SMCI | equity | 24.8516 | $28.40 | $705.79 | 1.41% | 1.04% | +0.369 |
| HOOD | equity | 7.5195 | $86.56 | $650.89 | 1.30% | 1.04% | +0.259 |
| INTC | equity | 7.1024 | $90.20 | $640.64 | 1.28% | 1.04% | +0.238 |
| ARES | equity | 4.1183 | $128.09 | $527.51 | 1.05% | 1.04% | +0.012 |
| PLTR | equity | 4.2445 | $123.06 | $522.33 | 1.04% | 1.04% | +0.002 |
| COIN | equity | 3.5044 | $146.26 | $512.55 | 1.03% | 1.04% | -0.018 |
| APH | equity | 3.1847 | $160.70 | $511.79 | 1.02% | 1.04% | -0.019 |
| NCLH | equity | 26.1611 | $18.53 | $484.77 | 0.97% | 1.04% | -0.073 |
| APP | equity | 1.1565 | $395.90 | $457.87 | 0.92% | 1.04% | -0.127 |
| EL | equity | 4.9467 | $83.90 | $415.03 | 0.83% | 1.04% | -0.213 |
| CVNA | equity | 6.4678 | $62.36 | $403.33 | 0.81% | 1.04% | -0.236 |
| AXON | equity | 0.7505 | $527.76 | $396.07 | 0.79% | 1.04% | -0.251 |
| DDOG | equity | 1.4365 | $267.97 | $384.94 | 0.77% | 1.04% | -0.273 |
| XYZ | equity | 4.7360 | $81.24 | $384.75 | 0.77% | 1.04% | -0.274 |
| EPAM | equity | 1.7681 | $105.56 | $186.64 | 0.37% | 1.04% | -0.670 |
| __CASH__ | cash | — | — | $20,170.94 | 40.34% | 40.34% | +0.000 |

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
| H-4 Weight drift | 4.17 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-25

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
| Trend | 69.16% |
| Cash | 5.84% |

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
| ARES | equity | 4.1222 | $126.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9991 | $521.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.4159 | $152.67 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.3304 | $391.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.8467 | $282.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0381 | $502.34 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2946 | $158.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1125 | $246.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.8041 | $89.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.4947 | $94.91 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.6255 | $60.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.4952 | $80.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.6488 | $92.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6835 | $762.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5663 | $920.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.9231 | $19.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.2426 | $122.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.3256 | $30.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3630 | $1436.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.7596 | $77.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-24

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
| Trend | 69.16% |
| Cash | 5.84% |

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
| ARES | equity | 4.1222 | $126.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9991 | $521.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.4159 | $152.67 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.3304 | $391.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.8467 | $282.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0381 | $502.34 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2946 | $158.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1125 | $246.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.8041 | $89.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.4947 | $94.91 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.6255 | $60.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.4952 | $80.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.6488 | $92.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6835 | $762.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5663 | $920.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.9231 | $19.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.2426 | $122.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.3256 | $30.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3630 | $1436.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.7596 | $77.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (12 buys, 8 sells) |
| Total notional | $424.80 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0328 | $521.95 | $17.14 |
| APH | buy | +0.1050 | $152.67 | $16.02 |
| APP | buy | +0.0229 | $391.98 | $9.00 |
| ARES | sell | -0.1778 | $126.51 | $22.49 |
| AXON | sell | -0.0229 | $502.34 | $11.51 |
| COHR | buy | +0.1818 | $282.39 | $51.33 |
| COIN | buy | +0.0587 | $158.29 | $9.29 |
| CVNA | sell | -0.0387 | $60.46 | $2.34 |
| DDOG | sell | -0.0214 | $246.86 | $5.27 |
| EL | sell | -0.0301 | $80.29 | $2.41 |
| EPAM | sell | -0.2500 | $89.85 | $22.46 |
| HOOD | buy | +0.3608 | $94.91 | $34.24 |
| INTC | buy | +0.4458 | $92.32 | $41.16 |
| LITE | buy | +0.0579 | $762.99 | $44.20 |
| MU | buy | +0.0396 | $920.95 | $36.48 |
| NCLH | sell | -0.9497 | $19.37 | $18.40 |
| PLTR | buy | +0.0155 | $122.92 | $1.90 |
| SMCI | buy | +0.6108 | $30.10 | $18.39 |
| SNDK | buy | +0.0392 | $1436.56 | $56.27 |
| XYZ | sell | -0.0583 | $77.15 | $4.50 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $521.95 | $521.95 | +0.0 | ✅ |
| APH | buy | $152.67 | $152.67 | +0.0 | ✅ |
| APP | buy | $391.98 | $391.98 | +0.0 | ✅ |
| ARES | sell | $126.51 | $126.51 | -0.0 | ✅ |
| AXON | sell | $502.34 | $502.34 | -0.0 | ✅ |
| COHR | buy | $282.39 | $282.39 | +0.0 | ✅ |
| COIN | buy | $158.29 | $158.29 | +0.0 | ✅ |
| CVNA | sell | $60.46 | $60.46 | -0.0 | ✅ |
| DDOG | sell | $246.86 | $246.86 | -0.0 | ✅ |
| EL | sell | $80.29 | $80.29 | -0.0 | ✅ |
| EPAM | sell | $89.85 | $89.85 | -0.0 | ✅ |
| HOOD | buy | $94.91 | $94.91 | +0.0 | ✅ |
| INTC | buy | $92.32 | $92.32 | +0.0 | ✅ |
| LITE | buy | $762.99 | $762.99 | +0.0 | ✅ |
| MU | buy | $920.95 | $920.95 | +0.0 | ✅ |
| NCLH | sell | $19.37 | $19.37 | -0.0 | ✅ |
| PLTR | buy | $122.92 | $122.92 | +0.0 | ✅ |
| SMCI | buy | $30.10 | $30.10 | +0.0 | ✅ |
| SNDK | buy | $1436.56 | $1436.56 | +0.0 | ✅ |
| XYZ | sell | $77.15 | $77.15 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-23

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
| Trend | 69.16% |
| Cash | 5.84% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.02 (53.6% of NAV) |
| Cash | $23,182.98 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| AXON | equity | 1.0611 | $491.90 | $521.93 | 1.04% | 1.04% | +0.001 |
| AMD | equity | 0.9663 | $539.69 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.3000 | $121.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.3075 | $398.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.2030 | $100.23 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.6650 | $313.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2359 | $161.16 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1339 | $244.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.0541 | $86.14 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.1339 | $101.58 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.6642 | $60.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.5253 | $79.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.2271 | $123.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6256 | $833.64 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5267 | $990.21 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 27.8728 | $18.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3238 | $1610.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 16.7147 | $31.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.8179 | $76.49 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.3109 | $157.43 | $521.24 | 1.04% | 1.04% | -0.000 |
| __CASH__ | cash | — | — | $23,182.98 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 18 (12 buys, 6 sells) |
| Total notional | $186.42 |
| Estimated turnover | 0.4% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0221 | $539.69 | $11.93 |
| APP | buy | +0.0432 | $398.86 | $17.22 |
| ARES | sell | -0.0615 | $121.28 | $7.46 |
| COHR | sell | -0.0055 | $313.22 | $1.72 |
| COIN | buy | +0.0966 | $161.16 | $15.57 |
| CVNA | buy | +0.3535 | $60.19 | $21.28 |
| DDOG | buy | +0.0120 | $244.39 | $2.93 |
| EL | buy | +0.2140 | $79.92 | $17.10 |
| EPAM | buy | +0.0301 | $86.14 | $2.59 |
| HOOD | buy | +0.1425 | $101.58 | $14.48 |
| INTC | buy | +0.1212 | $100.23 | $12.15 |
| LITE | sell | -0.0030 | $833.64 | $2.48 |
| MU | sell | -0.0169 | $990.21 | $16.70 |
| NCLH | buy | +0.8940 | $18.71 | $16.73 |
| PLTR | buy | +0.0407 | $123.37 | $5.02 |
| SMCI | sell | -0.3500 | $31.20 | $10.92 |
| SNDK | sell | -0.0022 | $1610.33 | $3.61 |
| XYZ | buy | +0.0854 | $76.49 | $6.53 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 18 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 18 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $539.69 | $539.69 | +0.0 | ✅ |
| APP | buy | $398.86 | $398.86 | +0.0 | ✅ |
| ARES | sell | $121.28 | $121.28 | -0.0 | ✅ |
| COHR | sell | $313.22 | $313.22 | -0.0 | ✅ |
| COIN | buy | $161.16 | $161.16 | +0.0 | ✅ |
| CVNA | buy | $60.19 | $60.19 | +0.0 | ✅ |
| DDOG | buy | $244.39 | $244.39 | +0.0 | ✅ |
| EL | buy | $79.92 | $79.92 | +0.0 | ✅ |
| EPAM | buy | $86.14 | $86.14 | +0.0 | ✅ |
| HOOD | buy | $101.58 | $101.58 | +0.0 | ✅ |
| INTC | buy | $100.23 | $100.23 | +0.0 | ✅ |
| LITE | sell | $833.64 | $833.64 | -0.0 | ✅ |
| MU | sell | $990.21 | $990.21 | -0.0 | ✅ |
| NCLH | buy | $18.71 | $18.71 | +0.0 | ✅ |
| PLTR | buy | $123.37 | $123.37 | +0.0 | ✅ |
| SMCI | sell | $31.20 | $31.20 | -0.0 | ✅ |
| SNDK | sell | $1610.33 | $1610.33 | -0.0 | ✅ |
| XYZ | buy | $76.49 | $76.49 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-22

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
| Trend | 69.16% |
| Cash | 5.84% |

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
| ARES | equity | 4.3615 | $119.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9442 | $552.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.3109 | $157.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.2643 | $412.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.6705 | $312.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0611 | $491.49 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1393 | $166.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1219 | $245.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.0240 | $86.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.9914 | $104.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.3108 | $62.75 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3113 | $82.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.0819 | $102.62 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6285 | $829.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5435 | $959.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.9788 | $19.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.1864 | $124.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.0648 | $30.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3261 | $1599.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.7325 | $77.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (20 buys, 1 sells) |
| Total notional | $29,241.32 |
| Estimated turnover | 58.5% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.2991 | $552.33 | $165.20 |
| APH | buy | +1.0854 | $157.51 | $170.97 |
| APP | buy | +0.4451 | $412.48 | $183.58 |
| ARES | buy | +1.4537 | $119.57 | $173.82 |
| AXON | buy | +0.3740 | $491.49 | $183.82 |
| COHR | buy | +0.5633 | $312.19 | $175.87 |
| COIN | buy | +1.1421 | $166.12 | $189.73 |
| CVNA | buy | +2.9555 | $62.75 | $185.46 |
| DDOG | buy | +0.7435 | $245.77 | $182.73 |
| EL | buy | +2.0476 | $82.63 | $169.19 |
| EPAM | buy | +2.0877 | $86.57 | $180.73 |
| HOOD | buy | +1.6894 | $104.48 | $176.51 |
| INTC | buy | +1.7514 | $102.62 | $179.73 |
| LITE | buy | +0.2092 | $829.70 | $173.60 |
| MU | buy | +0.1818 | $959.48 | $174.40 |
| NCLH | buy | +8.9222 | $19.33 | $172.47 |
| PLTR | buy | +1.5390 | $124.57 | $191.72 |
| SMCI | buy | +3.2922 | $30.56 | $100.61 |
| SNDK | buy | +0.1051 | $1599.27 | $168.12 |
| TLT | sell | -300.3031 | $85.78 | $25,760.00 |
| XYZ | buy | +2.3633 | $77.46 | $183.06 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $552.33 | $552.33 | +0.0 | ✅ |
| APH | buy | $157.51 | $157.51 | +0.0 | ✅ |
| APP | buy | $412.48 | $412.48 | +0.0 | ✅ |
| ARES | buy | $119.57 | $119.57 | +0.0 | ✅ |
| AXON | buy | $491.49 | $491.49 | +0.0 | ✅ |
| COHR | buy | $312.19 | $312.19 | +0.0 | ✅ |
| COIN | buy | $166.12 | $166.12 | +0.0 | ✅ |
| CVNA | buy | $62.75 | $62.75 | +0.0 | ✅ |
| DDOG | buy | $245.77 | $245.77 | +0.0 | ✅ |
| EL | buy | $82.63 | $82.63 | +0.0 | ✅ |
| EPAM | buy | $86.57 | $86.57 | +0.0 | ✅ |
| HOOD | buy | $104.48 | $104.48 | +0.0 | ✅ |
| INTC | buy | $102.62 | $102.62 | +0.0 | ✅ |
| LITE | buy | $829.70 | $829.70 | +0.0 | ✅ |
| MU | buy | $959.48 | $959.48 | +0.0 | ✅ |
| NCLH | buy | $19.33 | $19.33 | +0.0 | ✅ |
| PLTR | buy | $124.57 | $124.57 | +0.0 | ✅ |
| SMCI | buy | $30.56 | $30.56 | +0.0 | ✅ |
| SNDK | buy | $1599.27 | $1599.27 | +0.0 | ✅ |
| TLT | sell | $85.78 | $85.78 | -0.0 | ✅ |
| XYZ | buy | $77.46 | $77.46 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-21

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
| Equity | 25.00% |
| Trend | 69.16% |
| Cash | 5.84% |

**Trend breakdown:**
- TLT: 84.29%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $49,170.85 (98.3% of NAV) |
| Cash | $829.15 (1.7% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 491.3366 | $85.78 | $42,146.85 | 84.29% | 84.29% | +0.000 |
| ARES | equity | 2.9078 | $120.78 | $351.20 | 0.70% | 0.70% | +0.000 |
| AMD | equity | 0.6451 | $544.43 | $351.20 | 0.70% | 0.70% | +0.000 |
| APH | equity | 2.2255 | $157.81 | $351.20 | 0.70% | 0.70% | +0.000 |
| APP | equity | 0.8192 | $428.69 | $351.20 | 0.70% | 0.70% | +0.000 |
| COHR | equity | 1.1071 | $317.22 | $351.20 | 0.70% | 0.70% | +0.000 |
| AXON | equity | 0.6871 | $511.17 | $351.20 | 0.70% | 0.70% | +0.000 |
| COIN | equity | 1.9972 | $175.85 | $351.20 | 0.70% | 0.70% | +0.000 |
| DDOG | equity | 1.3784 | $254.79 | $351.20 | 0.70% | 0.70% | +0.000 |
| EPAM | equity | 3.9363 | $89.22 | $351.20 | 0.70% | 0.70% | +0.000 |
| HOOD | equity | 3.3020 | $106.36 | $351.20 | 0.70% | 0.70% | +0.000 |
| CVNA | equity | 5.3553 | $65.58 | $351.20 | 0.70% | 0.70% | +0.000 |
| EL | equity | 4.2637 | $82.37 | $351.20 | 0.70% | 0.70% | +0.000 |
| INTC | equity | 3.3305 | $105.45 | $351.20 | 0.70% | 0.70% | +0.000 |
| LITE | equity | 0.4193 | $837.56 | $351.20 | 0.70% | 0.70% | +0.000 |
| MU | equity | 0.3618 | $970.82 | $351.20 | 0.70% | 0.70% | +0.000 |
| NCLH | equity | 18.0566 | $19.45 | $351.20 | 0.70% | 0.70% | +0.000 |
| PLTR | equity | 2.6474 | $132.66 | $351.20 | 0.70% | 0.70% | +0.000 |
| SMCI | equity | 13.7725 | $25.50 | $351.20 | 0.70% | 0.70% | +0.000 |
| SNDK | equity | 0.2210 | $1589.40 | $351.20 | 0.70% | 0.70% | +0.000 |
| XYZ | equity | 4.3692 | $80.38 | $351.20 | 0.70% | 0.70% | +0.000 |
| __CASH__ | cash | — | — | $829.15 | 1.66% | 1.66% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (1 buys, 20 sells) |
| Total notional | $29,619.00 |
| Estimated turnover | 59.2% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.3905 | $544.43 | $212.61 |
| APH | sell | -1.2394 | $157.81 | $195.59 |
| APP | sell | -0.4091 | $428.69 | $175.40 |
| ARES | sell | -1.3926 | $120.78 | $168.19 |
| AXON | sell | -0.3016 | $511.17 | $154.18 |
| COHR | sell | -0.7201 | $317.22 | $228.44 |
| COIN | sell | -1.2535 | $175.85 | $220.42 |
| CVNA | sell | -2.7754 | $65.58 | $182.01 |
| DDOG | sell | -0.6030 | $254.79 | $153.64 |
| EL | sell | -1.9714 | $82.37 | $162.38 |
| EPAM | sell | -1.8970 | $89.22 | $169.25 |
| HOOD | sell | -1.9508 | $106.36 | $207.49 |
| INTC | sell | -2.0425 | $105.45 | $215.38 |
| LITE | sell | -0.2619 | $837.56 | $219.35 |
| MU | sell | -0.2408 | $970.82 | $233.79 |
| NCLH | sell | -8.7420 | $19.45 | $170.03 |
| PLTR | sell | -1.2199 | $132.66 | $161.83 |
| SMCI | sell | -8.1116 | $25.50 | $206.85 |
| SNDK | sell | -0.1540 | $1589.40 | $244.70 |
| TLT | buy | +300.3031 | $85.78 | $25,760.00 |
| XYZ | sell | -2.2079 | $80.38 | $177.47 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $544.43 | $544.43 | -0.0 | ✅ |
| APH | sell | $157.81 | $157.81 | -0.0 | ✅ |
| APP | sell | $428.69 | $428.69 | -0.0 | ✅ |
| ARES | sell | $120.78 | $120.78 | -0.0 | ✅ |
| AXON | sell | $511.17 | $511.17 | -0.0 | ✅ |
| COHR | sell | $317.22 | $317.22 | -0.0 | ✅ |
| COIN | sell | $175.85 | $175.85 | -0.0 | ✅ |
| CVNA | sell | $65.58 | $65.58 | -0.0 | ✅ |
| DDOG | sell | $254.79 | $254.79 | -0.0 | ✅ |
| EL | sell | $82.37 | $82.37 | -0.0 | ✅ |
| EPAM | sell | $89.22 | $89.22 | -0.0 | ✅ |
| HOOD | sell | $106.36 | $106.36 | -0.0 | ✅ |
| INTC | sell | $105.45 | $105.45 | -0.0 | ✅ |
| LITE | sell | $837.56 | $837.56 | -0.0 | ✅ |
| MU | sell | $970.82 | $970.82 | -0.0 | ✅ |
| NCLH | sell | $19.45 | $19.45 | -0.0 | ✅ |
| PLTR | sell | $132.66 | $132.66 | -0.0 | ✅ |
| SMCI | sell | $25.50 | $25.50 | -0.0 | ✅ |
| SNDK | sell | $1589.40 | $1589.40 | -0.0 | ✅ |
| TLT | buy | $85.78 | $85.78 | +0.0 | ✅ |
| XYZ | sell | $80.38 | $80.38 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-20

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.72 (53.6% of NAV) |
| Cash | $23,182.28 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| NCLH | equity | 26.7986 | $19.49 | $522.30 | 1.04% | 1.04% | +0.002 |
| APP | equity | 1.2284 | $424.60 | $521.57 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.3003 | $121.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0356 | $503.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.8273 | $285.40 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.4649 | $150.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.9887 | $527.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 1.9814 | $263.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.8333 | $89.40 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.2528 | $99.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2506 | $160.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2351 | $83.64 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.3730 | $97.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.1307 | $64.14 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.6026 | $865.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6812 | $765.55 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8673 | $134.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 21.8842 | $23.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3749 | $1390.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.5771 | $79.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.28 | 46.36% | 46.36% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 18 (6 buys, 12 sells) |
| Total notional | $203.42 |
| Estimated turnover | 0.4% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0163 | $503.57 | $8.22 |
| APH | buy | +0.0158 | $150.51 | $2.38 |
| ARES | buy | +0.1509 | $121.27 | $18.30 |
| AXON | sell | -0.0333 | $527.48 | $17.58 |
| COHR | sell | -0.0513 | $285.40 | $14.65 |
| COIN | sell | -0.0685 | $160.43 | $10.99 |
| CVNA | buy | +0.3864 | $64.14 | $24.78 |
| DDOG | sell | -0.0345 | $263.20 | $9.09 |
| EL | sell | -0.1146 | $83.64 | $9.59 |
| EPAM | sell | -0.0487 | $89.40 | $4.35 |
| HOOD | buy | +0.0357 | $99.28 | $3.55 |
| INTC | sell | -0.1142 | $97.06 | $11.08 |
| LITE | sell | -0.0304 | $765.55 | $23.29 |
| MU | sell | -0.0117 | $865.46 | $10.14 |
| PLTR | sell | -0.0722 | $134.85 | $9.73 |
| SMCI | buy | +0.3168 | $23.83 | $7.55 |
| SNDK | sell | -0.0100 | $1390.95 | $13.91 |
| XYZ | buy | +0.0535 | $79.29 | $4.24 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 18 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 18 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $503.57 | $503.57 | -0.0 | ✅ |
| APH | buy | $150.51 | $150.51 | +0.0 | ✅ |
| ARES | buy | $121.27 | $121.27 | +0.0 | ✅ |
| AXON | sell | $527.48 | $527.48 | -0.0 | ✅ |
| COHR | sell | $285.40 | $285.40 | -0.0 | ✅ |
| COIN | sell | $160.43 | $160.43 | -0.0 | ✅ |
| CVNA | buy | $64.14 | $64.14 | +0.0 | ✅ |
| DDOG | sell | $263.20 | $263.20 | -0.0 | ✅ |
| EL | sell | $83.64 | $83.64 | -0.0 | ✅ |
| EPAM | sell | $89.40 | $89.40 | -0.0 | ✅ |
| HOOD | buy | $99.28 | $99.28 | +0.0 | ✅ |
| INTC | sell | $97.06 | $97.06 | -0.0 | ✅ |
| LITE | sell | $765.55 | $765.55 | -0.0 | ✅ |
| MU | sell | $865.46 | $865.46 | -0.0 | ✅ |
| PLTR | sell | $134.85 | $134.85 | -0.0 | ✅ |
| SMCI | buy | $23.83 | $23.83 | +0.0 | ✅ |
| SNDK | sell | $1390.95 | $1390.95 | -0.0 | ✅ |
| XYZ | buy | $79.29 | $79.29 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-17

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

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
| ARES | equity | 4.1494 | $125.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0519 | $495.76 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.4491 | $151.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.2284 | $424.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.8786 | $277.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0220 | $510.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.3191 | $157.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0159 | $258.69 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.8820 | $88.66 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.2171 | $99.96 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.7443 | $67.34 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3497 | $82.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.4872 | $95.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.7116 | $732.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.6143 | $848.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.7986 | $19.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.9394 | $132.38 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 21.5674 | $24.18 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3849 | $1354.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.5236 | $79.94 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (16 buys, 4 sells) |
| Total notional | $224.37 |
| Estimated turnover | 0.4% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0109 | $495.76 | $5.39 |
| APH | buy | +0.0437 | $151.20 | $6.61 |
| APP | buy | +0.0281 | $424.54 | $11.93 |
| ARES | sell | -0.0083 | $125.68 | $1.04 |
| AXON | buy | +0.0582 | $510.28 | $29.72 |
| COHR | sell | -0.0043 | $277.60 | $1.21 |
| COIN | buy | +0.0697 | $157.12 | $10.95 |
| CVNA | buy | +0.3566 | $67.34 | $24.01 |
| DDOG | buy | +0.0279 | $258.69 | $7.22 |
| EL | buy | +0.0544 | $82.13 | $4.47 |
| EPAM | sell | -0.0664 | $88.66 | $5.89 |
| HOOD | buy | +0.2982 | $99.96 | $29.81 |
| INTC | buy | +0.1098 | $95.04 | $10.43 |
| LITE | sell | -0.0268 | $732.82 | $19.64 |
| MU | buy | +0.0031 | $848.95 | $2.60 |
| NCLH | buy | +0.2050 | $19.46 | $3.99 |
| PLTR | buy | +0.0604 | $132.38 | $7.99 |
| SMCI | buy | +0.4369 | $24.18 | $10.57 |
| SNDK | buy | +0.0153 | $1354.82 | $20.79 |
| XYZ | buy | +0.1264 | $79.94 | $10.11 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $495.76 | $495.76 | +0.0 | ✅ |
| APH | buy | $151.20 | $151.20 | +0.0 | ✅ |
| APP | buy | $424.54 | $424.54 | +0.0 | ✅ |
| ARES | sell | $125.68 | $125.68 | -0.0 | ✅ |
| AXON | buy | $510.28 | $510.28 | +0.0 | ✅ |
| COHR | sell | $277.60 | $277.60 | -0.0 | ✅ |
| COIN | buy | $157.12 | $157.12 | +0.0 | ✅ |
| CVNA | buy | $67.34 | $67.34 | +0.0 | ✅ |
| DDOG | buy | $258.69 | $258.69 | +0.0 | ✅ |
| EL | buy | $82.13 | $82.13 | +0.0 | ✅ |
| EPAM | sell | $88.66 | $88.66 | -0.0 | ✅ |
| HOOD | buy | $99.96 | $99.96 | +0.0 | ✅ |
| INTC | buy | $95.04 | $95.04 | +0.0 | ✅ |
| LITE | sell | $732.82 | $732.82 | -0.0 | ✅ |
| MU | buy | $848.95 | $848.95 | +0.0 | ✅ |
| NCLH | buy | $19.46 | $19.46 | +0.0 | ✅ |
| PLTR | buy | $132.38 | $132.38 | +0.0 | ✅ |
| SMCI | buy | $24.18 | $24.18 | +0.0 | ✅ |
| SNDK | buy | $1354.82 | $1354.82 | +0.0 | ✅ |
| XYZ | buy | $79.94 | $79.94 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-16

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.98 (53.6% of NAV) |
| Cash | $23,182.02 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| AXON | equity | 0.9637 | $541.75 | $522.11 | 1.04% | 1.04% | +0.001 |
| CVNA | equity | 7.3877 | $70.66 | $522.02 | 1.04% | 1.04% | +0.001 |
| ARES | equity | 4.1577 | $125.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.2003 | $434.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.8829 | $276.96 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.4054 | $153.14 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0410 | $500.94 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2494 | $160.49 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2953 | $82.84 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.9484 | $87.67 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.9189 | $106.02 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 1.9880 | $262.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.3774 | $96.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.7384 | $706.23 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.6112 | $853.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.5936 | $19.61 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8791 | $134.44 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 21.1305 | $24.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3696 | $1411.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.3972 | $81.52 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.02 | 46.36% | 46.36% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 18 (14 buys, 4 sells) |
| Total notional | $393.72 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0555 | $500.94 | $27.79 |
| APH | buy | +0.0846 | $153.14 | $12.95 |
| APP | buy | +0.0484 | $434.48 | $21.02 |
| ARES | sell | -0.0213 | $125.43 | $2.67 |
| COHR | buy | +0.1410 | $276.96 | $39.05 |
| COIN | buy | +0.1306 | $160.49 | $20.96 |
| DDOG | buy | +0.0161 | $262.32 | $4.22 |
| EL | sell | -0.0405 | $82.84 | $3.36 |
| EPAM | sell | -0.1205 | $87.67 | $10.56 |
| HOOD | buy | +0.4053 | $106.02 | $42.97 |
| INTC | buy | +0.3138 | $96.98 | $30.43 |
| LITE | buy | +0.0449 | $706.23 | $31.74 |
| MU | buy | +0.0345 | $853.20 | $29.46 |
| NCLH | buy | +0.1617 | $19.61 | $3.17 |
| PLTR | sell | -0.0209 | $134.44 | $2.81 |
| SMCI | buy | +1.7366 | $24.68 | $42.86 |
| SNDK | buy | +0.0467 | $1411.08 | $65.85 |
| XYZ | buy | +0.0227 | $81.52 | $1.85 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 18 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 18 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $500.94 | $500.94 | +0.0 | ✅ |
| APH | buy | $153.14 | $153.14 | +0.0 | ✅ |
| APP | buy | $434.48 | $434.48 | +0.0 | ✅ |
| ARES | sell | $125.43 | $125.43 | -0.0 | ✅ |
| COHR | buy | $276.96 | $276.96 | +0.0 | ✅ |
| COIN | buy | $160.49 | $160.49 | +0.0 | ✅ |
| DDOG | buy | $262.32 | $262.32 | +0.0 | ✅ |
| EL | sell | $82.84 | $82.84 | -0.0 | ✅ |
| EPAM | sell | $87.67 | $87.67 | -0.0 | ✅ |
| HOOD | buy | $106.02 | $106.02 | +0.0 | ✅ |
| INTC | buy | $96.98 | $96.98 | +0.0 | ✅ |
| LITE | buy | $706.23 | $706.23 | +0.0 | ✅ |
| MU | buy | $853.20 | $853.20 | +0.0 | ✅ |
| NCLH | buy | $19.61 | $19.61 | +0.0 | ✅ |
| PLTR | sell | $134.44 | $134.44 | -0.0 | ✅ |
| SMCI | buy | $24.68 | $24.68 | +0.0 | ✅ |
| SNDK | buy | $1411.08 | $1411.08 | +0.0 | ✅ |
| XYZ | buy | $81.52 | $81.52 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-15

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.01 (53.6% of NAV) |
| Cash | $23,182.99 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| PLTR | equity | 3.8999 | $133.76 | $521.66 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9856 | $529.14 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.1790 | $124.79 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.1519 | $452.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.7419 | $299.38 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.3208 | $157.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.9637 | $541.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 1.9719 | $264.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.0689 | $85.93 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.5136 | $115.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1188 | $167.21 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3358 | $82.31 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.0636 | $102.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.3877 | $70.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.4318 | $19.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6935 | $752.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5767 | $904.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 19.3938 | $26.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3229 | $1615.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.3745 | $81.81 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.99 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (10 buys, 9 sells) |
| Total notional | $311.30 |
| Estimated turnover | 0.6% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0341 | $529.14 | $18.07 |
| APH | buy | +0.0279 | $157.04 | $4.38 |
| APP | sell | -0.0096 | $452.73 | $4.36 |
| ARES | sell | -0.1506 | $124.79 | $18.79 |
| AXON | buy | +0.0104 | $541.12 | $5.63 |
| COHR | buy | +0.0638 | $299.38 | $19.11 |
| COIN | sell | -0.1103 | $167.21 | $18.44 |
| CVNA | sell | -0.0220 | $70.59 | $1.56 |
| DDOG | buy | +0.0457 | $264.46 | $12.08 |
| EL | sell | -0.1136 | $82.31 | $9.35 |
| EPAM | sell | -0.1027 | $85.93 | $8.83 |
| HOOD | sell | -0.0832 | $115.54 | $9.61 |
| INTC | buy | +0.2241 | $102.99 | $23.08 |
| LITE | buy | +0.0534 | $752.00 | $40.19 |
| MU | buy | +0.0462 | $904.28 | $41.82 |
| NCLH | sell | -0.3667 | $19.73 | $7.24 |
| SMCI | buy | +0.5399 | $26.89 | $14.52 |
| SNDK | buy | +0.0262 | $1615.00 | $42.37 |
| XYZ | sell | -0.1450 | $81.81 | $11.87 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $529.14 | $529.14 | +0.0 | ✅ |
| APH | buy | $157.04 | $157.04 | +0.0 | ✅ |
| APP | sell | $452.73 | $452.73 | -0.0 | ✅ |
| ARES | sell | $124.79 | $124.79 | -0.0 | ✅ |
| AXON | buy | $541.12 | $541.12 | +0.0 | ✅ |
| COHR | buy | $299.38 | $299.38 | +0.0 | ✅ |
| COIN | sell | $167.21 | $167.21 | -0.0 | ✅ |
| CVNA | sell | $70.59 | $70.59 | -0.0 | ✅ |
| DDOG | buy | $264.46 | $264.46 | +0.0 | ✅ |
| EL | sell | $82.31 | $82.31 | -0.0 | ✅ |
| EPAM | sell | $85.93 | $85.93 | -0.0 | ✅ |
| HOOD | sell | $115.54 | $115.54 | -0.0 | ✅ |
| INTC | buy | $102.99 | $102.99 | +0.0 | ✅ |
| LITE | buy | $752.00 | $752.00 | +0.0 | ✅ |
| MU | buy | $904.28 | $904.28 | +0.0 | ✅ |
| NCLH | sell | $19.73 | $19.73 | -0.0 | ✅ |
| SMCI | buy | $26.89 | $26.89 | +0.0 | ✅ |
| SNDK | buy | $1615.00 | $1615.00 | +0.0 | ✅ |
| XYZ | sell | $81.81 | $81.81 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-14

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.23 (53.6% of NAV) |
| Cash | $23,183.77 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| AXON | equity | 0.9533 | $547.26 | $521.72 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.2929 | $158.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9514 | $548.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.1615 | $448.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.8395 | $107.76 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.6781 | $310.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2291 | $161.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 1.9263 | $270.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.1716 | $84.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.5967 | $113.45 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.4098 | $70.38 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.4494 | $80.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8999 | $133.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6400 | $814.80 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5305 | $983.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.7986 | $19.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.5196 | $79.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2967 | $1757.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 18.8539 | $27.65 | $521.31 | 1.04% | 1.04% | -0.000 |
| ARES | equity | 4.3296 | $120.30 | $520.85 | 1.04% | 1.04% | -0.001 |
| __CASH__ | cash | — | — | $23,183.77 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 17 (3 buys, 14 sells) |
| Total notional | $276.62 |
| Estimated turnover | 0.6% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0245 | $548.13 | $13.41 |
| APH | sell | -0.0502 | $158.37 | $7.96 |
| APP | sell | -0.0161 | $448.98 | $7.22 |
| COHR | sell | -0.0185 | $310.77 | $5.73 |
| COIN | sell | -0.0847 | $161.50 | $13.69 |
| CVNA | sell | -0.6145 | $70.38 | $43.25 |
| DDOG | sell | -0.0776 | $270.73 | $21.02 |
| EL | buy | +0.0230 | $80.86 | $1.86 |
| EPAM | buy | +0.1343 | $84.50 | $11.35 |
| HOOD | sell | -0.1502 | $113.45 | $17.04 |
| INTC | sell | -0.2178 | $107.76 | $23.47 |
| LITE | sell | -0.0389 | $814.80 | $31.67 |
| MU | sell | -0.0261 | $983.12 | $25.67 |
| NCLH | buy | +0.2050 | $19.46 | $3.99 |
| PLTR | sell | -0.1104 | $133.72 | $14.76 |
| SNDK | sell | -0.0149 | $1757.82 | $26.12 |
| XYZ | sell | -0.1052 | $79.99 | $8.41 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 17 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 17 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $548.13 | $548.13 | -0.0 | ✅ |
| APH | sell | $158.37 | $158.37 | -0.0 | ✅ |
| APP | sell | $448.98 | $448.98 | -0.0 | ✅ |
| COHR | sell | $310.77 | $310.77 | -0.0 | ✅ |
| COIN | sell | $161.50 | $161.50 | -0.0 | ✅ |
| CVNA | sell | $70.38 | $70.38 | -0.0 | ✅ |
| DDOG | sell | $270.73 | $270.73 | -0.0 | ✅ |
| EL | buy | $80.86 | $80.86 | +0.0 | ✅ |
| EPAM | buy | $84.50 | $84.50 | +0.0 | ✅ |
| HOOD | sell | $113.45 | $113.45 | -0.0 | ✅ |
| INTC | sell | $107.76 | $107.76 | -0.0 | ✅ |
| LITE | sell | $814.80 | $814.80 | -0.0 | ✅ |
| MU | sell | $983.12 | $983.12 | -0.0 | ✅ |
| NCLH | buy | $19.46 | $19.46 | +0.0 | ✅ |
| PLTR | sell | $133.72 | $133.72 | -0.0 | ✅ |
| SNDK | sell | $1757.82 | $1757.82 | -0.0 | ✅ |
| XYZ | sell | $79.99 | $79.99 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-13

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.38 (53.6% of NAV) |
| Cash | $23,182.62 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| NCLH | equity | 26.5936 | $19.63 | $522.03 | 1.04% | 1.04% | +0.001 |
| AMD | equity | 0.9759 | $534.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.3296 | $120.45 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.1776 | $442.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.6965 | $307.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.3432 | $155.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.9533 | $547.03 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0039 | $260.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.0373 | $86.38 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.7470 | $109.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.3138 | $157.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.4264 | $81.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 5.0572 | $103.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.0243 | $64.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5566 | $937.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6789 | $768.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.0103 | $130.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 18.8539 | $27.66 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3115 | $1673.97 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.6247 | $78.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.62 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (15 buys, 4 sells) |
| Total notional | $376.95 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0411 | $534.39 | $21.97 |
| APH | buy | +0.0645 | $155.99 | $10.07 |
| APP | buy | +0.1490 | $442.85 | $65.97 |
| ARES | buy | +0.0431 | $120.45 | $5.19 |
| AXON | buy | +0.0316 | $547.03 | $17.30 |
| COHR | buy | +0.0895 | $307.39 | $27.50 |
| COIN | buy | +0.0354 | $157.37 | $5.57 |
| CVNA | buy | +0.1024 | $64.99 | $6.65 |
| DDOG | sell | -0.0210 | $260.24 | $5.47 |
| EL | buy | +0.1174 | $81.15 | $9.53 |
| EPAM | sell | -0.1792 | $86.38 | $15.48 |
| HOOD | buy | +0.0895 | $109.86 | $9.83 |
| INTC | buy | +0.3094 | $103.12 | $31.91 |
| LITE | buy | +0.0287 | $768.15 | $22.02 |
| MU | buy | +0.0240 | $937.00 | $22.53 |
| PLTR | sell | -0.1028 | $130.04 | $13.37 |
| SMCI | buy | +0.4329 | $27.66 | $11.97 |
| SNDK | buy | +0.0393 | $1673.97 | $65.86 |
| XYZ | sell | -0.1112 | $78.72 | $8.76 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $534.39 | $534.39 | +0.0 | ✅ |
| APH | buy | $155.99 | $155.99 | +0.0 | ✅ |
| APP | buy | $442.85 | $442.85 | +0.0 | ✅ |
| ARES | buy | $120.45 | $120.45 | +0.0 | ✅ |
| AXON | buy | $547.03 | $547.03 | +0.0 | ✅ |
| COHR | buy | $307.39 | $307.39 | +0.0 | ✅ |
| COIN | buy | $157.37 | $157.37 | +0.0 | ✅ |
| CVNA | buy | $64.99 | $64.99 | +0.0 | ✅ |
| DDOG | sell | $260.24 | $260.24 | -0.0 | ✅ |
| EL | buy | $81.15 | $81.15 | +0.0 | ✅ |
| EPAM | sell | $86.38 | $86.38 | -0.0 | ✅ |
| HOOD | buy | $109.86 | $109.86 | +0.0 | ✅ |
| INTC | buy | $103.12 | $103.12 | +0.0 | ✅ |
| LITE | buy | $768.15 | $768.15 | +0.0 | ✅ |
| MU | buy | $937.00 | $937.00 | +0.0 | ✅ |
| PLTR | sell | $130.04 | $130.04 | -0.0 | ✅ |
| SMCI | buy | $27.66 | $27.66 | +0.0 | ✅ |
| SNDK | buy | $1673.97 | $1673.97 | +0.0 | ✅ |
| XYZ | sell | $78.72 | $78.72 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-10

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.68 (53.6% of NAV) |
| Cash | $23,183.32 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.2865 | $121.81 | $522.14 | 1.04% | 1.04% | +0.001 |
| APP | equity | 1.0286 | $506.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.2786 | $159.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9348 | $557.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.6071 | $324.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.9217 | $565.80 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2784 | $159.07 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0249 | $257.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.2165 | $83.89 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.6575 | $111.97 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.9219 | $65.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3090 | $82.66 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.7478 | $109.84 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6502 | $802.01 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5325 | $979.30 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.5936 | $19.61 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.1131 | $126.79 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 18.4211 | $28.31 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2722 | $1915.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.7360 | $77.30 | $520.69 | 1.04% | 1.04% | -0.002 |
| __CASH__ | cash | — | — | $23,183.32 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 18 (12 buys, 6 sells) |
| Total notional | $186.65 |
| Estimated turnover | 0.4% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0191 | $557.89 | $10.65 |
| APH | buy | +0.0643 | $159.06 | $10.22 |
| APP | buy | +0.0266 | $506.98 | $13.48 |
| AXON | buy | +0.0257 | $565.80 | $14.52 |
| COHR | buy | +0.0135 | $324.50 | $4.37 |
| COIN | sell | -0.0130 | $159.07 | $2.07 |
| CVNA | buy | +0.1523 | $65.83 | $10.02 |
| DDOG | buy | +0.0863 | $257.54 | $22.22 |
| EL | sell | -0.0516 | $82.66 | $4.26 |
| EPAM | buy | +0.2421 | $83.89 | $20.31 |
| HOOD | buy | +0.1270 | $111.97 | $14.23 |
| INTC | buy | +0.1139 | $109.84 | $12.51 |
| LITE | sell | -0.0134 | $802.01 | $10.78 |
| MU | buy | +0.0066 | $979.30 | $6.49 |
| NCLH | buy | +0.2019 | $19.61 | $3.96 |
| PLTR | buy | +0.0717 | $126.79 | $9.09 |
| SMCI | sell | -0.0457 | $28.31 | $1.29 |
| SNDK | sell | -0.0084 | $1915.92 | $16.18 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 18 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 18 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $557.89 | $557.89 | -0.0 | ✅ |
| APH | buy | $159.06 | $159.06 | +0.0 | ✅ |
| APP | buy | $506.98 | $506.98 | +0.0 | ✅ |
| AXON | buy | $565.80 | $565.80 | +0.0 | ✅ |
| COHR | buy | $324.50 | $324.50 | +0.0 | ✅ |
| COIN | sell | $159.07 | $159.07 | -0.0 | ✅ |
| CVNA | buy | $65.83 | $65.83 | +0.0 | ✅ |
| DDOG | buy | $257.54 | $257.54 | +0.0 | ✅ |
| EL | sell | $82.66 | $82.66 | -0.0 | ✅ |
| EPAM | buy | $83.89 | $83.89 | +0.0 | ✅ |
| HOOD | buy | $111.97 | $111.97 | +0.0 | ✅ |
| INTC | buy | $109.84 | $109.84 | +0.0 | ✅ |
| LITE | sell | $802.01 | $802.01 | -0.0 | ✅ |
| MU | buy | $979.30 | $979.30 | +0.0 | ✅ |
| NCLH | buy | $19.61 | $19.61 | +0.0 | ✅ |
| PLTR | buy | $126.79 | $126.79 | +0.0 | ✅ |
| SMCI | sell | $28.31 | $28.31 | -0.0 | ✅ |
| SNDK | sell | $1915.92 | $1915.92 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-09

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

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
| ARES | equity | 4.2865 | $121.66 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9539 | $546.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.2144 | $162.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0021 | $520.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.5936 | $327.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.8960 | $582.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2915 | $158.44 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 1.9387 | $269.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.9743 | $87.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.5304 | $115.11 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.7697 | $67.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3605 | $81.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.6339 | $112.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6637 | $785.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5259 | $991.64 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.3917 | $19.76 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.0414 | $129.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 18.4667 | $28.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2806 | $1858.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.7360 | $77.42 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (4 buys, 16 sells) |
| Total notional | $321.62 |
| Estimated turnover | 0.6% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0540 | $546.72 | $29.54 |
| APH | sell | -0.0817 | $162.24 | $13.25 |
| APP | buy | +0.0034 | $520.43 | $1.75 |
| ARES | sell | -0.1273 | $121.66 | $15.49 |
| AXON | buy | +0.0266 | $582.00 | $15.48 |
| COHR | sell | -0.0512 | $327.24 | $16.76 |
| COIN | buy | +0.0190 | $158.44 | $3.01 |
| CVNA | sell | -0.0890 | $67.12 | $5.97 |
| DDOG | sell | -0.0587 | $269.00 | $15.80 |
| EL | sell | -0.0148 | $81.99 | $1.21 |
| EPAM | sell | -0.0903 | $87.29 | $7.88 |
| HOOD | sell | -0.0630 | $115.11 | $7.26 |
| INTC | sell | -0.0967 | $112.54 | $10.88 |
| LITE | sell | -0.0738 | $785.77 | $58.02 |
| MU | sell | -0.0237 | $991.64 | $23.55 |
| NCLH | sell | -1.8433 | $19.76 | $36.42 |
| PLTR | buy | +0.0972 | $129.04 | $12.54 |
| SMCI | sell | -0.0459 | $28.24 | $1.30 |
| SNDK | sell | -0.0213 | $1858.27 | $39.58 |
| XYZ | sell | -0.0766 | $77.42 | $5.93 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $546.72 | $546.72 | -0.0 | ✅ |
| APH | sell | $162.24 | $162.24 | -0.0 | ✅ |
| APP | buy | $520.43 | $520.43 | +0.0 | ✅ |
| ARES | sell | $121.66 | $121.66 | -0.0 | ✅ |
| AXON | buy | $582.00 | $582.00 | +0.0 | ✅ |
| COHR | sell | $327.24 | $327.24 | -0.0 | ✅ |
| COIN | buy | $158.44 | $158.44 | +0.0 | ✅ |
| CVNA | sell | $67.12 | $67.12 | -0.0 | ✅ |
| DDOG | sell | $269.00 | $269.00 | -0.0 | ✅ |
| EL | sell | $81.99 | $81.99 | -0.0 | ✅ |
| EPAM | sell | $87.29 | $87.29 | -0.0 | ✅ |
| HOOD | sell | $115.11 | $115.11 | -0.0 | ✅ |
| INTC | sell | $112.54 | $112.54 | -0.0 | ✅ |
| LITE | sell | $785.77 | $785.77 | -0.0 | ✅ |
| MU | sell | $991.64 | $991.64 | -0.0 | ✅ |
| NCLH | sell | $19.76 | $19.76 | -0.0 | ✅ |
| PLTR | buy | $129.04 | $129.04 | +0.0 | ✅ |
| SMCI | sell | $28.24 | $28.24 | -0.0 | ✅ |
| SNDK | sell | $1858.27 | $1858.27 | -0.0 | ✅ |
| XYZ | sell | $77.42 | $77.42 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-08

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.18 (53.6% of NAV) |
| Cash | $23,183.82 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| AMD | equity | 1.0079 | $517.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.2960 | $158.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.6449 | $317.05 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9987 | $522.18 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.7306 | $110.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.8695 | $599.80 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2725 | $159.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 1.9974 | $261.09 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.0647 | $85.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.5935 | $113.53 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8586 | $66.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3753 | $81.80 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.9442 | $132.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.7375 | $707.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5496 | $948.80 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 28.2350 | $18.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3019 | $1727.18 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 18.5126 | $28.17 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.8125 | $76.55 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.4138 | $118.00 | $520.83 | 1.04% | 1.04% | -0.001 |
| __CASH__ | cash | — | — | $23,183.82 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (4 buys, 16 sells) |
| Total notional | $10,774.45 |
| Estimated turnover | 21.5% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0243 | $517.41 | $12.59 |
| APH | sell | -0.0628 | $158.22 | $9.94 |
| APP | sell | -0.0103 | $522.18 | $5.40 |
| AXON | buy | +0.0376 | $599.80 | $22.57 |
| COHR | sell | -0.0511 | $317.05 | $16.20 |
| COIN | buy | +0.0143 | $159.36 | $2.27 |
| CVNA | sell | -0.0351 | $66.36 | $2.33 |
| DDOG | sell | -0.0771 | $261.09 | $20.13 |
| EL | buy | +0.0661 | $81.80 | $5.41 |
| EPAM | buy | +0.1155 | $85.99 | $9.93 |
| HOOD | sell | -0.1253 | $113.53 | $14.22 |
| INTC | sell | -0.0955 | $110.24 | $10.53 |
| LITE | sell | -0.0247 | $707.10 | $17.49 |
| MU | sell | -0.0181 | $948.80 | $17.17 |
| NCLH | sell | -0.0576 | $18.47 | $1.06 |
| PLTR | sell | -0.0206 | $132.22 | $2.73 |
| SMCI | sell | -1.7826 | $28.17 | $50.22 |
| SNDK | sell | -0.0274 | $1727.18 | $47.30 |
| TLT | sell | -122.4370 | $85.78 | $10,502.65 |
| XYZ | sell | -0.0563 | $76.55 | $4.31 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $517.41 | $517.41 | -0.0 | ✅ |
| APH | sell | $158.22 | $158.22 | -0.0 | ✅ |
| APP | sell | $522.18 | $522.18 | -0.0 | ✅ |
| AXON | buy | $599.80 | $599.80 | +0.0 | ✅ |
| COHR | sell | $317.05 | $317.05 | -0.0 | ✅ |
| COIN | buy | $159.36 | $159.36 | +0.0 | ✅ |
| CVNA | sell | $66.36 | $66.36 | -0.0 | ✅ |
| DDOG | sell | $261.09 | $261.09 | -0.0 | ✅ |
| EL | buy | $81.80 | $81.80 | +0.0 | ✅ |
| EPAM | buy | $85.99 | $85.99 | +0.0 | ✅ |
| HOOD | sell | $113.53 | $113.53 | -0.0 | ✅ |
| INTC | sell | $110.24 | $110.24 | -0.0 | ✅ |
| LITE | sell | $707.10 | $707.10 | -0.0 | ✅ |
| MU | sell | $948.80 | $948.80 | -0.0 | ✅ |
| NCLH | sell | $18.47 | $18.47 | -0.0 | ✅ |
| PLTR | sell | $132.22 | $132.22 | -0.0 | ✅ |
| SMCI | sell | $28.17 | $28.17 | -0.0 | ✅ |
| SNDK | sell | $1727.18 | $1727.18 | -0.0 | ✅ |
| TLT | sell | $85.78 | $85.78 | -0.0 | ✅ |
| XYZ | sell | $76.55 | $76.55 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-07

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
| Equity | 46.22% |
| Trend | 53.78% |
| Cash | 0.00% |

**Trend breakdown:**
- TLT: 53.78%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $37,544.50 (75.1% of NAV) |
| Cash | $12,455.50 (24.9% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 313.4705 | $85.78 | $26,889.50 | 53.78% | 53.78% | +0.000 |
| ARES | equity | 4.4138 | $120.70 | $532.75 | 1.07% | 1.07% | +0.000 |
| AMD | equity | 1.0322 | $516.11 | $532.75 | 1.07% | 1.07% | +0.000 |
| APH | equity | 3.3589 | $158.61 | $532.75 | 1.07% | 1.07% | +0.000 |
| APP | equity | 1.0090 | $527.98 | $532.75 | 1.07% | 1.07% | +0.000 |
| COHR | equity | 1.6960 | $314.13 | $532.75 | 1.07% | 1.07% | +0.000 |
| AXON | equity | 0.8318 | $640.46 | $532.75 | 1.07% | 1.07% | +0.000 |
| COIN | equity | 3.2582 | $163.51 | $532.75 | 1.07% | 1.07% | +0.000 |
| DDOG | equity | 2.0745 | $256.81 | $532.75 | 1.07% | 1.07% | +0.000 |
| EPAM | equity | 5.9492 | $89.55 | $532.75 | 1.07% | 1.07% | +0.000 |
| HOOD | equity | 4.7188 | $112.90 | $532.75 | 1.07% | 1.07% | +0.000 |
| CVNA | equity | 7.8938 | $67.49 | $532.75 | 1.07% | 1.07% | +0.000 |
| EL | equity | 6.3092 | $84.44 | $532.75 | 1.07% | 1.07% | +0.000 |
| INTC | equity | 4.8261 | $110.39 | $532.75 | 1.07% | 1.07% | +0.000 |
| LITE | equity | 0.7623 | $698.91 | $532.75 | 1.07% | 1.07% | +0.000 |
| MU | equity | 0.5677 | $938.38 | $532.75 | 1.07% | 1.07% | +0.000 |
| NCLH | equity | 28.2926 | $18.83 | $532.75 | 1.07% | 1.07% | +0.000 |
| PLTR | equity | 3.9648 | $134.37 | $532.75 | 1.07% | 1.07% | +0.000 |
| SMCI | equity | 20.2952 | $26.25 | $532.75 | 1.07% | 1.07% | +0.000 |
| SNDK | equity | 0.3293 | $1617.70 | $532.75 | 1.07% | 1.07% | +0.000 |
| XYZ | equity | 6.8689 | $77.56 | $532.75 | 1.07% | 1.07% | +0.000 |
| __CASH__ | cash | — | — | $12,455.50 | 24.91% | 24.91% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (19 buys, 2 sells) |
| Total notional | $11,053.10 |
| Estimated turnover | 22.1% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0876 | $516.11 | $45.20 |
| APH | buy | +0.2326 | $158.61 | $36.89 |
| APP | buy | +0.0500 | $527.98 | $26.41 |
| ARES | buy | +0.1333 | $120.70 | $16.09 |
| AXON | sell | -0.0061 | $640.46 | $3.93 |
| COHR | buy | +0.1425 | $314.13 | $44.76 |
| COIN | buy | +0.1700 | $163.51 | $27.80 |
| CVNA | buy | +0.4840 | $67.49 | $32.66 |
| DDOG | buy | +0.0324 | $256.81 | $8.31 |
| EL | buy | +0.1667 | $84.44 | $14.08 |
| EPAM | sell | -0.0554 | $89.55 | $4.96 |
| HOOD | buy | +0.2824 | $112.90 | $31.88 |
| INTC | buy | +0.5585 | $110.39 | $61.65 |
| LITE | buy | +0.0491 | $698.91 | $34.31 |
| MU | buy | +0.0382 | $938.38 | $35.81 |
| NCLH | buy | +1.2158 | $18.83 | $22.89 |
| PLTR | buy | +0.0301 | $134.37 | $4.05 |
| SMCI | buy | +1.1365 | $26.25 | $29.83 |
| SNDK | buy | +0.0305 | $1617.70 | $49.29 |
| TLT | buy | +122.4370 | $85.78 | $10,502.65 |
| XYZ | buy | +0.2534 | $77.56 | $19.65 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $516.11 | $516.11 | +0.0 | ✅ |
| APH | buy | $158.61 | $158.61 | +0.0 | ✅ |
| APP | buy | $527.98 | $527.98 | +0.0 | ✅ |
| ARES | buy | $120.70 | $120.70 | +0.0 | ✅ |
| AXON | sell | $640.46 | $640.46 | -0.0 | ✅ |
| COHR | buy | $314.13 | $314.13 | +0.0 | ✅ |
| COIN | buy | $163.51 | $163.51 | +0.0 | ✅ |
| CVNA | buy | $67.49 | $67.49 | +0.0 | ✅ |
| DDOG | buy | $256.81 | $256.81 | +0.0 | ✅ |
| EL | buy | $84.44 | $84.44 | +0.0 | ✅ |
| EPAM | sell | $89.55 | $89.55 | -0.0 | ✅ |
| HOOD | buy | $112.90 | $112.90 | +0.0 | ✅ |
| INTC | buy | $110.39 | $110.39 | +0.0 | ✅ |
| LITE | buy | $698.91 | $698.91 | +0.0 | ✅ |
| MU | buy | $938.38 | $938.38 | +0.0 | ✅ |
| NCLH | buy | $18.83 | $18.83 | +0.0 | ✅ |
| PLTR | buy | $134.37 | $134.37 | +0.0 | ✅ |
| SMCI | buy | $26.25 | $26.25 | +0.0 | ✅ |
| SNDK | buy | $1617.70 | $1617.70 | +0.0 | ✅ |
| TLT | buy | $85.78 | $85.78 | +0.0 | ✅ |
| XYZ | buy | $77.56 | $77.56 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-06

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
| Trend | 73.55% |
| Cash | 1.45% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.71 (53.6% of NAV) |
| Cash | $23,183.29 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| XYZ | equity | 6.6155 | $78.92 | $522.10 | 1.04% | 1.04% | +0.001 |
| AMD | equity | 0.9447 | $552.05 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.2806 | $121.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9590 | $543.79 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.5535 | $335.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1263 | $166.81 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.8380 | $622.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0421 | $255.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.0046 | $86.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.4364 | $117.55 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.0882 | $168.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.1425 | $84.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.2676 | $122.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.4098 | $70.38 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.7132 | $731.25 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 27.0768 | $19.26 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.9347 | $132.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5296 | $984.75 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2989 | $1744.43 | $521.33 | 1.04% | 1.04% | -0.000 |
| SMCI | equity | 19.1587 | $27.19 | $520.93 | 1.04% | 1.04% | -0.001 |
| __CASH__ | cash | — | — | $23,183.29 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 17 (3 buys, 14 sells) |
| Total notional | $220.00 |
| Estimated turnover | 0.4% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0624 | $552.05 | $34.47 |
| APH | sell | -0.0422 | $166.81 | $7.03 |
| APP | sell | -0.0304 | $543.79 | $16.55 |
| ARES | sell | -0.1805 | $121.83 | $21.99 |
| AXON | sell | -0.0355 | $622.35 | $22.11 |
| COHR | sell | -0.0109 | $335.70 | $3.66 |
| COIN | sell | -0.0633 | $168.87 | $10.68 |
| CVNA | sell | -0.1923 | $70.38 | $13.53 |
| DDOG | buy | +0.0391 | $255.37 | $9.99 |
| EL | sell | -0.0873 | $84.90 | $7.41 |
| EPAM | buy | +0.0966 | $86.85 | $8.39 |
| HOOD | sell | -0.1897 | $117.55 | $22.30 |
| INTC | sell | -0.0656 | $122.20 | $8.02 |
| LITE | sell | -0.0029 | $731.25 | $2.10 |
| MU | sell | -0.0051 | $984.75 | $4.99 |
| NCLH | buy | +0.7118 | $19.26 | $13.71 |
| PLTR | sell | -0.0986 | $132.54 | $13.07 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 17 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 17 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $552.05 | $552.05 | -0.0 | ✅ |
| APH | sell | $166.81 | $166.81 | -0.0 | ✅ |
| APP | sell | $543.79 | $543.79 | -0.0 | ✅ |
| ARES | sell | $121.83 | $121.83 | -0.0 | ✅ |
| AXON | sell | $622.35 | $622.35 | -0.0 | ✅ |
| COHR | sell | $335.70 | $335.70 | -0.0 | ✅ |
| COIN | sell | $168.87 | $168.87 | -0.0 | ✅ |
| CVNA | sell | $70.38 | $70.38 | -0.0 | ✅ |
| DDOG | buy | $255.37 | $255.37 | +0.0 | ✅ |
| EL | sell | $84.90 | $84.90 | -0.0 | ✅ |
| EPAM | buy | $86.85 | $86.85 | +0.0 | ✅ |
| HOOD | sell | $117.55 | $117.55 | -0.0 | ✅ |
| INTC | sell | $122.20 | $122.20 | -0.0 | ✅ |
| LITE | sell | $731.25 | $731.25 | -0.0 | ✅ |
| MU | sell | $984.75 | $984.75 | -0.0 | ✅ |
| NCLH | buy | $19.26 | $19.26 | +0.0 | ✅ |
| PLTR | sell | $132.54 | $132.54 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-03

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
| Trend | 73.55% |
| Cash | 1.45% |

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
| ARES | equity | 4.4611 | $116.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0071 | $517.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1685 | $164.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9895 | $527.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.5644 | $333.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.8735 | $597.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1514 | $165.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0030 | $260.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.9080 | $88.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.6261 | $112.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.6020 | $68.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2298 | $83.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.3332 | $120.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.7160 | $728.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5346 | $975.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.3650 | $19.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.0333 | $129.30 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 19.1587 | $27.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2989 | $1745.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.6155 | $78.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-02

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
| Trend | 73.55% |
| Cash | 1.45% |

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
| ARES | equity | 4.4611 | $116.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0071 | $517.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1685 | $164.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9895 | $527.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.5644 | $333.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.8735 | $597.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1514 | $165.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0030 | $260.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.9080 | $88.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.6261 | $112.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.6020 | $68.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2298 | $83.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.3332 | $120.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.7160 | $728.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5346 | $975.41 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.3650 | $19.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.0333 | $129.30 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 19.1587 | $27.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2989 | $1745.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.6155 | $78.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (11 buys, 9 sells) |
| Total notional | $461.78 |
| Estimated turnover | 0.9% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0429 | $517.82 | $22.23 |
| APH | buy | +0.1404 | $164.59 | $23.10 |
| APP | buy | +0.0658 | $527.06 | $34.68 |
| ARES | sell | -0.1284 | $116.90 | $15.01 |
| AXON | sell | -0.0045 | $597.04 | $2.70 |
| COHR | buy | +0.1498 | $333.36 | $49.92 |
| COIN | sell | -0.1235 | $165.48 | $20.44 |
| CVNA | sell | -0.0818 | $68.60 | $5.61 |
| DDOG | buy | +0.0312 | $260.36 | $8.12 |
| EL | sell | -0.0937 | $83.71 | $7.84 |
| EPAM | sell | -0.2100 | $88.27 | $18.54 |
| HOOD | sell | -0.1737 | $112.73 | $19.58 |
| INTC | buy | +0.2275 | $120.35 | $27.38 |
| LITE | buy | +0.0651 | $728.32 | $47.41 |
| MU | buy | +0.0294 | $975.41 | $28.65 |
| NCLH | buy | +1.1352 | $19.78 | $22.45 |
| PLTR | sell | -0.1145 | $129.30 | $14.81 |
| SMCI | buy | +0.2979 | $27.22 | $8.11 |
| SNDK | buy | +0.0422 | $1745.00 | $73.71 |
| XYZ | sell | -0.1458 | $78.83 | $11.49 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $517.82 | $517.82 | +0.0 | ✅ |
| APH | buy | $164.59 | $164.59 | +0.0 | ✅ |
| APP | buy | $527.06 | $527.06 | +0.0 | ✅ |
| ARES | sell | $116.90 | $116.90 | -0.0 | ✅ |
| AXON | sell | $597.04 | $597.04 | -0.0 | ✅ |
| COHR | buy | $333.36 | $333.36 | +0.0 | ✅ |
| COIN | sell | $165.48 | $165.48 | -0.0 | ✅ |
| CVNA | sell | $68.60 | $68.60 | -0.0 | ✅ |
| DDOG | buy | $260.36 | $260.36 | +0.0 | ✅ |
| EL | sell | $83.71 | $83.71 | -0.0 | ✅ |
| EPAM | sell | $88.27 | $88.27 | -0.0 | ✅ |
| HOOD | sell | $112.73 | $112.73 | -0.0 | ✅ |
| INTC | buy | $120.35 | $120.35 | +0.0 | ✅ |
| LITE | buy | $728.32 | $728.32 | +0.0 | ✅ |
| MU | buy | $975.41 | $975.41 | +0.0 | ✅ |
| NCLH | buy | $19.78 | $19.78 | +0.0 | ✅ |
| PLTR | sell | $129.30 | $129.30 | -0.0 | ✅ |
| SMCI | buy | $27.22 | $27.22 | +0.0 | ✅ |
| SNDK | buy | $1745.00 | $1745.00 | +0.0 | ✅ |
| XYZ | sell | $78.83 | $78.83 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-07-01

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
| Trend | 73.55% |
| Cash | 1.45% |

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
| ARES | equity | 4.5895 | $113.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9642 | $540.88 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.0281 | $172.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9236 | $564.61 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.4146 | $368.65 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.8780 | $593.96 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2749 | $159.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 1.9718 | $264.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.1180 | $85.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.7998 | $108.65 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.6838 | $67.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3235 | $82.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.1057 | $127.02 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6509 | $801.16 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5053 | $1032.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 25.2298 | $20.67 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.1478 | $125.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 18.8608 | $27.65 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2566 | $2032.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.7613 | $77.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (9 buys, 11 sells) |
| Total notional | $631.78 |
| Estimated turnover | 1.3% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0664 | $540.88 | $35.94 |
| APH | buy | +0.0704 | $172.22 | $12.13 |
| APP | sell | -0.0885 | $564.61 | $49.98 |
| ARES | sell | -0.0957 | $113.63 | $10.87 |
| AXON | sell | -0.0522 | $593.96 | $31.02 |
| COHR | buy | +0.0926 | $368.65 | $34.13 |
| COIN | sell | -0.2923 | $159.24 | $46.55 |
| CVNA | sell | -0.2393 | $67.87 | $16.24 |
| DDOG | sell | -0.0312 | $264.48 | $8.25 |
| EL | sell | -0.2819 | $82.47 | $23.25 |
| EPAM | sell | -0.4541 | $85.24 | $38.71 |
| HOOD | sell | -0.4006 | $108.65 | $43.53 |
| INTC | buy | +0.3708 | $127.02 | $47.10 |
| LITE | buy | +0.0432 | $801.16 | $34.58 |
| MU | buy | +0.0534 | $1032.12 | $55.12 |
| NCLH | buy | +0.5259 | $20.67 | $10.87 |
| PLTR | sell | -0.3221 | $125.73 | $40.50 |
| SMCI | buy | +1.0803 | $27.65 | $29.87 |
| SNDK | buy | +0.0273 | $2032.22 | $55.39 |
| XYZ | sell | -0.1005 | $77.13 | $7.75 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $540.88 | $540.88 | +0.0 | ✅ |
| APH | buy | $172.22 | $172.22 | +0.0 | ✅ |
| APP | sell | $564.61 | $564.61 | -0.0 | ✅ |
| ARES | sell | $113.63 | $113.63 | -0.0 | ✅ |
| AXON | sell | $593.96 | $593.96 | -0.0 | ✅ |
| COHR | buy | $368.65 | $368.65 | +0.0 | ✅ |
| COIN | sell | $159.24 | $159.24 | -0.0 | ✅ |
| CVNA | sell | $67.87 | $67.87 | -0.0 | ✅ |
| DDOG | sell | $264.48 | $264.48 | -0.0 | ✅ |
| EL | sell | $82.47 | $82.47 | -0.0 | ✅ |
| EPAM | sell | $85.24 | $85.24 | -0.0 | ✅ |
| HOOD | sell | $108.65 | $108.65 | -0.0 | ✅ |
| INTC | buy | $127.02 | $127.02 | +0.0 | ✅ |
| LITE | buy | $801.16 | $801.16 | +0.0 | ✅ |
| MU | buy | $1032.12 | $1032.12 | +0.0 | ✅ |
| NCLH | buy | $20.67 | $20.67 | +0.0 | ✅ |
| PLTR | sell | $125.73 | $125.73 | -0.0 | ✅ |
| SMCI | buy | $27.65 | $27.65 | +0.0 | ✅ |
| SNDK | buy | $2032.22 | $2032.22 | +0.0 | ✅ |
| XYZ | sell | $77.13 | $77.13 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-30

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
| Trend | 73.55% |
| Cash | 1.45% |

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
| ARES | equity | 4.6851 | $111.31 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.8977 | $580.91 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 2.9577 | $176.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0122 | $515.23 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3220 | $394.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 0.9302 | $560.61 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.5673 | $146.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0030 | $260.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.5721 | $79.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.2004 | $100.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.9231 | $65.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.6054 | $78.95 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 3.7349 | $139.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6078 | $858.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4519 | $1154.11 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 24.7039 | $21.11 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.4699 | $116.67 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.7804 | $29.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2294 | $2273.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.8618 | $76.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (6 buys, 14 sells) |
| Total notional | $392.81 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0689 | $580.91 | $40.04 |
| APH | sell | -0.1759 | $176.32 | $31.02 |
| APP | sell | -0.0334 | $515.23 | $17.22 |
| ARES | sell | -0.1615 | $111.31 | $17.98 |
| AXON | sell | -0.0911 | $560.61 | $51.08 |
| COHR | sell | -0.0110 | $394.47 | $4.33 |
| COIN | buy | +0.1284 | $146.19 | $18.78 |
| CVNA | sell | -0.2611 | $65.82 | $17.19 |
| DDOG | sell | -0.0950 | $260.36 | $24.74 |
| EL | buy | +0.0350 | $78.95 | $2.76 |
| EPAM | buy | +0.0558 | $79.35 | $4.43 |
| HOOD | buy | +0.0792 | $100.28 | $7.94 |
| INTC | sell | -0.2243 | $139.63 | $31.32 |
| LITE | sell | -0.0048 | $858.06 | $4.08 |
| MU | sell | -0.0036 | $1154.11 | $4.10 |
| NCLH | buy | +0.9129 | $21.11 | $19.27 |
| PLTR | sell | -0.0375 | $116.67 | $4.37 |
| SMCI | sell | -0.7453 | $29.33 | $21.86 |
| SNDK | sell | -0.0250 | $2273.73 | $56.80 |
| XYZ | buy | +0.1777 | $76.00 | $13.50 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $580.91 | $580.91 | -0.0 | ✅ |
| APH | sell | $176.32 | $176.32 | -0.0 | ✅ |
| APP | sell | $515.23 | $515.23 | -0.0 | ✅ |
| ARES | sell | $111.31 | $111.31 | -0.0 | ✅ |
| AXON | sell | $560.61 | $560.61 | -0.0 | ✅ |
| COHR | sell | $394.47 | $394.47 | -0.0 | ✅ |
| COIN | buy | $146.19 | $146.19 | +0.0 | ✅ |
| CVNA | sell | $65.82 | $65.82 | -0.0 | ✅ |
| DDOG | sell | $260.36 | $260.36 | -0.0 | ✅ |
| EL | buy | $78.95 | $78.95 | +0.0 | ✅ |
| EPAM | buy | $79.35 | $79.35 | +0.0 | ✅ |
| HOOD | buy | $100.28 | $100.28 | +0.0 | ✅ |
| INTC | sell | $139.63 | $139.63 | -0.0 | ✅ |
| LITE | sell | $858.06 | $858.06 | -0.0 | ✅ |
| MU | sell | $1154.11 | $1154.11 | -0.0 | ✅ |
| NCLH | buy | $21.11 | $21.11 | +0.0 | ✅ |
| PLTR | sell | $116.67 | $116.67 | -0.0 | ✅ |
| SMCI | sell | $29.33 | $29.33 | -0.0 | ✅ |
| SNDK | sell | $2273.73 | $2273.73 | -0.0 | ✅ |
| XYZ | buy | $76.00 | $76.00 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-29

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
| Trend | 73.55% |
| Cash | 1.45% |

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
| ARES | equity | 4.8467 | $107.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9667 | $539.49 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1336 | $166.42 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0456 | $498.76 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3330 | $391.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.0213 | $510.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.4388 | $151.65 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.0980 | $248.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.5163 | $80.03 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.1213 | $101.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.1842 | $63.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.5705 | $79.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 3.9592 | $131.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6125 | $851.40 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4554 | $1145.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 23.7911 | $21.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.5073 | $115.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 18.5258 | $28.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2543 | $2050.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.6842 | $78.02 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (5 buys, 15 sells) |
| Total notional | $316.29 |
| Estimated turnover | 0.6% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0332 | $539.49 | $17.91 |
| APH | sell | -0.0517 | $166.42 | $8.60 |
| APP | sell | -0.0475 | $498.76 | $23.70 |
| ARES | buy | +0.0679 | $107.60 | $7.31 |
| AXON | sell | -0.1006 | $510.60 | $51.35 |
| COHR | sell | -0.0373 | $391.22 | $14.61 |
| COIN | sell | -0.0598 | $151.65 | $9.06 |
| CVNA | sell | -0.1798 | $63.72 | $11.46 |
| DDOG | sell | -0.0770 | $248.57 | $19.14 |
| EL | buy | +0.0954 | $79.37 | $7.58 |
| EPAM | buy | +0.0525 | $80.03 | $4.20 |
| HOOD | sell | -0.1629 | $101.83 | $16.59 |
| INTC | sell | -0.1049 | $131.72 | $13.82 |
| LITE | sell | -0.0258 | $851.40 | $21.97 |
| MU | sell | -0.0051 | $1145.10 | $5.88 |
| NCLH | sell | -0.7617 | $21.92 | $16.70 |
| PLTR | sell | -0.1106 | $115.70 | $12.79 |
| SMCI | buy | +1.5000 | $28.15 | $42.22 |
| SNDK | buy | +0.0049 | $2050.39 | $10.06 |
| XYZ | sell | -0.0172 | $78.02 | $1.34 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $539.49 | $539.49 | -0.0 | ✅ |
| APH | sell | $166.42 | $166.42 | -0.0 | ✅ |
| APP | sell | $498.76 | $498.76 | -0.0 | ✅ |
| ARES | buy | $107.60 | $107.60 | +0.0 | ✅ |
| AXON | sell | $510.60 | $510.60 | -0.0 | ✅ |
| COHR | sell | $391.22 | $391.22 | -0.0 | ✅ |
| COIN | sell | $151.65 | $151.65 | -0.0 | ✅ |
| CVNA | sell | $63.72 | $63.72 | -0.0 | ✅ |
| DDOG | sell | $248.57 | $248.57 | -0.0 | ✅ |
| EL | buy | $79.37 | $79.37 | +0.0 | ✅ |
| EPAM | buy | $80.03 | $80.03 | +0.0 | ✅ |
| HOOD | sell | $101.83 | $101.83 | -0.0 | ✅ |
| INTC | sell | $131.72 | $131.72 | -0.0 | ✅ |
| LITE | sell | $851.40 | $851.40 | -0.0 | ✅ |
| MU | sell | $1145.10 | $1145.10 | -0.0 | ✅ |
| NCLH | sell | $21.92 | $21.92 | -0.0 | ✅ |
| PLTR | sell | $115.70 | $115.70 | -0.0 | ✅ |
| SMCI | buy | $28.15 | $28.15 | +0.0 | ✅ |
| SNDK | buy | $2050.39 | $2050.39 | +0.0 | ✅ |
| XYZ | sell | $78.02 | $78.02 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-28

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
| Trend | 73.55% |
| Cash | 1.45% |

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
| ARES | equity | 4.7787 | $109.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9998 | $521.58 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1853 | $163.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0931 | $477.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3703 | $380.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1219 | $464.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.4986 | $149.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1750 | $239.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.4638 | $80.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.2842 | $98.69 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.3641 | $62.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.4750 | $80.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.0641 | $128.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6383 | $816.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4606 | $1132.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 24.5527 | $21.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.6179 | $112.93 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.0258 | $30.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2494 | $2090.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.7014 | $77.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-26

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
| Trend | 73.55% |
| Cash | 1.45% |

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
| ARES | equity | 4.7787 | $109.13 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9998 | $521.58 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1853 | $163.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0931 | $477.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3703 | $380.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1219 | $464.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.4986 | $149.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.1750 | $239.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.4638 | $80.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.2842 | $98.69 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.3641 | $62.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.4750 | $80.54 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.0641 | $128.32 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6383 | $816.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4606 | $1132.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 24.5527 | $21.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.6179 | $112.93 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.0258 | $30.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2494 | $2090.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.7014 | $77.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (11 buys, 9 sells) |
| Total notional | $492.62 |
| Estimated turnover | 1.0% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0206 | $521.58 | $10.76 |
| APH | buy | +0.0276 | $163.72 | $4.52 |
| APP | sell | -0.0764 | $477.08 | $36.43 |
| ARES | buy | +0.1419 | $109.13 | $15.49 |
| AXON | sell | -0.0507 | $464.83 | $23.57 |
| COHR | buy | +0.0898 | $380.56 | $34.18 |
| COIN | sell | -0.1605 | $149.06 | $23.93 |
| CVNA | buy | +0.4864 | $62.35 | $30.33 |
| DDOG | sell | -0.1854 | $239.77 | $44.45 |
| EL | buy | +0.0763 | $80.54 | $6.14 |
| EPAM | sell | -0.2765 | $80.68 | $22.31 |
| HOOD | sell | -0.2951 | $98.69 | $29.12 |
| INTC | buy | +0.1392 | $128.32 | $17.86 |
| LITE | buy | +0.0333 | $816.98 | $27.22 |
| MU | buy | +0.0308 | $1132.33 | $34.91 |
| NCLH | sell | -0.2688 | $21.24 | $5.71 |
| PLTR | sell | -0.2437 | $112.93 | $27.52 |
| SMCI | buy | +0.5643 | $30.63 | $17.28 |
| SNDK | buy | +0.0261 | $2090.71 | $54.56 |
| XYZ | sell | -0.3383 | $77.82 | $26.33 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $521.58 | $521.58 | +0.0 | ✅ |
| APH | buy | $163.72 | $163.72 | +0.0 | ✅ |
| APP | sell | $477.08 | $477.08 | -0.0 | ✅ |
| ARES | buy | $109.13 | $109.13 | +0.0 | ✅ |
| AXON | sell | $464.83 | $464.83 | -0.0 | ✅ |
| COHR | buy | $380.56 | $380.56 | +0.0 | ✅ |
| COIN | sell | $149.06 | $149.06 | -0.0 | ✅ |
| CVNA | buy | $62.35 | $62.35 | +0.0 | ✅ |
| DDOG | sell | $239.77 | $239.77 | -0.0 | ✅ |
| EL | buy | $80.54 | $80.54 | +0.0 | ✅ |
| EPAM | sell | $80.68 | $80.68 | -0.0 | ✅ |
| HOOD | sell | $98.69 | $98.69 | -0.0 | ✅ |
| INTC | buy | $128.32 | $128.32 | +0.0 | ✅ |
| LITE | buy | $816.98 | $816.98 | +0.0 | ✅ |
| MU | buy | $1132.33 | $1132.33 | +0.0 | ✅ |
| NCLH | sell | $21.24 | $21.24 | -0.0 | ✅ |
| PLTR | sell | $112.93 | $112.93 | -0.0 | ✅ |
| SMCI | buy | $30.63 | $30.63 | +0.0 | ✅ |
| SNDK | buy | $2090.71 | $2090.71 | +0.0 | ✅ |
| XYZ | sell | $77.82 | $77.82 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-25

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
| Trend | 73.55% |
| Cash | 1.45% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,816.11 (53.6% of NAV) |
| Cash | $23,183.89 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| ARES | equity | 4.6368 | $112.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9792 | $532.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1577 | $165.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.1695 | $445.93 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2805 | $407.25 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1726 | $444.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.6591 | $142.52 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3604 | $220.94 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.7403 | $77.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.5793 | $93.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8776 | $66.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3988 | $81.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 3.9249 | $132.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6050 | $861.97 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.8616 | $107.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4297 | $1213.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2233 | $2335.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 16.4615 | $31.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.0397 | $74.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 24.8215 | $20.98 | $520.76 | 1.04% | 1.04% | -0.001 |
| __CASH__ | cash | — | — | $23,183.89 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (12 buys, 7 sells) |
| Total notional | $428.40 |
| Estimated turnover | 0.9% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0242 | $532.57 | $12.87 |
| APH | sell | -0.0460 | $165.15 | $7.59 |
| APP | buy | +0.0479 | $445.93 | $21.34 |
| ARES | buy | +0.0570 | $112.47 | $6.41 |
| AXON | buy | +0.0308 | $444.73 | $13.70 |
| COHR | sell | -0.0481 | $407.25 | $19.60 |
| COIN | buy | +0.1850 | $142.52 | $26.37 |
| CVNA | buy | +0.1984 | $66.20 | $13.13 |
| DDOG | buy | +0.0181 | $220.94 | $4.01 |
| EL | buy | +0.1360 | $81.50 | $11.09 |
| EPAM | buy | +0.0877 | $77.37 | $6.79 |
| HOOD | buy | +0.2136 | $93.47 | $19.96 |
| INTC | sell | -0.0364 | $132.87 | $4.83 |
| LITE | sell | -0.0140 | $861.97 | $12.03 |
| MU | sell | -0.0676 | $1213.56 | $82.09 |
| PLTR | buy | +0.2669 | $107.27 | $28.63 |
| SMCI | buy | +0.3906 | $31.68 | $12.37 |
| SNDK | sell | -0.0491 | $2335.00 | $114.56 |
| XYZ | buy | +0.1488 | $74.08 | $11.03 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $532.57 | $532.57 | -0.0 | ✅ |
| APH | sell | $165.15 | $165.15 | -0.0 | ✅ |
| APP | buy | $445.93 | $445.93 | +0.0 | ✅ |
| ARES | buy | $112.47 | $112.47 | +0.0 | ✅ |
| AXON | buy | $444.73 | $444.73 | +0.0 | ✅ |
| COHR | sell | $407.25 | $407.25 | -0.0 | ✅ |
| COIN | buy | $142.52 | $142.52 | +0.0 | ✅ |
| CVNA | buy | $66.20 | $66.20 | +0.0 | ✅ |
| DDOG | buy | $220.94 | $220.94 | +0.0 | ✅ |
| EL | buy | $81.50 | $81.50 | +0.0 | ✅ |
| EPAM | buy | $77.37 | $77.37 | +0.0 | ✅ |
| HOOD | buy | $93.47 | $93.47 | +0.0 | ✅ |
| INTC | sell | $132.87 | $132.87 | -0.0 | ✅ |
| LITE | sell | $861.97 | $861.97 | -0.0 | ✅ |
| MU | sell | $1213.56 | $1213.56 | -0.0 | ✅ |
| PLTR | buy | $107.27 | $107.27 | +0.0 | ✅ |
| SMCI | buy | $31.68 | $31.68 | +0.0 | ✅ |
| SNDK | sell | $2335.00 | $2335.00 | -0.0 | ✅ |
| XYZ | buy | $74.08 | $74.08 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-24

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
| Trend | 73.55% |
| Cash | 1.45% |

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
| ARES | equity | 4.5798 | $113.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0034 | $519.74 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.2037 | $162.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.1216 | $464.96 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3287 | $392.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1418 | $456.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.4741 | $150.11 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3422 | $222.65 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.6526 | $78.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.3658 | $97.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.6793 | $67.91 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.2628 | $83.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 3.9613 | $131.65 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6190 | $842.53 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4974 | $1048.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 24.8215 | $21.01 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.5947 | $113.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 16.0709 | $32.45 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2724 | $1914.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.8909 | $75.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (20 buys, 1 sells) |
| Total notional | $28,572.11 |
| Estimated turnover | 57.1% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.3861 | $519.74 | $200.67 |
| APH | buy | +1.1817 | $162.78 | $192.35 |
| APP | buy | +0.4345 | $464.96 | $202.02 |
| ARES | buy | +1.9229 | $113.87 | $218.96 |
| AXON | buy | +0.4008 | $456.73 | $183.04 |
| COHR | buy | +0.4869 | $392.50 | $191.10 |
| COIN | buy | +1.4454 | $150.11 | $216.97 |
| CVNA | buy | +2.7294 | $67.91 | $185.35 |
| DDOG | buy | +0.8874 | $222.65 | $197.57 |
| EL | buy | +2.4316 | $83.27 | $202.48 |
| EPAM | buy | +2.4791 | $78.39 | $194.34 |
| HOOD | buy | +2.2578 | $97.19 | $219.43 |
| INTC | buy | +1.5353 | $131.65 | $202.13 |
| LITE | buy | +0.2314 | $842.53 | $194.94 |
| MU | buy | +0.1923 | $1048.51 | $201.59 |
| NCLH | buy | +9.0834 | $21.01 | $190.84 |
| PLTR | buy | +1.8449 | $113.50 | $209.40 |
| SMCI | buy | +6.4400 | $32.45 | $208.98 |
| SNDK | buy | +0.1090 | $1914.46 | $208.63 |
| TLT | sell | -286.3768 | $85.78 | $24,565.40 |
| XYZ | buy | +2.4567 | $75.68 | $185.92 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $519.74 | $519.74 | +0.0 | ✅ |
| APH | buy | $162.78 | $162.78 | +0.0 | ✅ |
| APP | buy | $464.96 | $464.96 | +0.0 | ✅ |
| ARES | buy | $113.87 | $113.87 | +0.0 | ✅ |
| AXON | buy | $456.73 | $456.73 | +0.0 | ✅ |
| COHR | buy | $392.50 | $392.50 | +0.0 | ✅ |
| COIN | buy | $150.11 | $150.11 | +0.0 | ✅ |
| CVNA | buy | $67.91 | $67.91 | +0.0 | ✅ |
| DDOG | buy | $222.65 | $222.65 | +0.0 | ✅ |
| EL | buy | $83.27 | $83.27 | +0.0 | ✅ |
| EPAM | buy | $78.39 | $78.39 | +0.0 | ✅ |
| HOOD | buy | $97.19 | $97.19 | +0.0 | ✅ |
| INTC | buy | $131.65 | $131.65 | +0.0 | ✅ |
| LITE | buy | $842.53 | $842.53 | +0.0 | ✅ |
| MU | buy | $1048.51 | $1048.51 | +0.0 | ✅ |
| NCLH | buy | $21.01 | $21.01 | +0.0 | ✅ |
| PLTR | buy | $113.50 | $113.50 | +0.0 | ✅ |
| SMCI | buy | $32.45 | $32.45 | +0.0 | ✅ |
| SNDK | buy | $1914.46 | $1914.46 | +0.0 | ✅ |
| TLT | sell | $85.78 | $85.78 | -0.0 | ✅ |
| XYZ | buy | $75.68 | $75.68 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-23

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
| Equity | 25.00% |
| Trend | 73.55% |
| Cash | 1.45% |

**Trend breakdown:**
- TLT: 81.90%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $47,370.25 (94.7% of NAV) |
| Cash | $2,629.75 (5.3% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 477.4102 | $85.78 | $40,952.25 | 81.90% | 81.90% | +0.000 |
| ARES | equity | 2.6569 | $120.78 | $320.90 | 0.64% | 0.64% | +0.000 |
| AMD | equity | 0.6173 | $519.85 | $320.90 | 0.64% | 0.64% | +0.000 |
| APH | equity | 2.0221 | $158.70 | $320.90 | 0.64% | 0.64% | +0.000 |
| APP | equity | 0.6871 | $467.02 | $320.90 | 0.64% | 0.64% | +0.000 |
| COHR | equity | 0.8418 | $381.22 | $320.90 | 0.64% | 0.64% | +0.000 |
| AXON | equity | 0.7410 | $433.04 | $320.90 | 0.64% | 0.64% | +0.000 |
| COIN | equity | 2.0287 | $158.18 | $320.90 | 0.64% | 0.64% | +0.000 |
| DDOG | equity | 1.4549 | $220.57 | $320.90 | 0.64% | 0.64% | +0.000 |
| EPAM | equity | 4.1735 | $76.89 | $320.90 | 0.64% | 0.64% | +0.000 |
| HOOD | equity | 3.1080 | $103.25 | $320.90 | 0.64% | 0.64% | +0.000 |
| CVNA | equity | 4.9499 | $64.83 | $320.90 | 0.64% | 0.64% | +0.000 |
| EL | equity | 3.8312 | $83.76 | $320.90 | 0.64% | 0.64% | +0.000 |
| INTC | equity | 2.4259 | $132.28 | $320.90 | 0.64% | 0.64% | +0.000 |
| LITE | equity | 0.3876 | $827.92 | $320.90 | 0.64% | 0.64% | +0.000 |
| MU | equity | 0.3051 | $1051.77 | $320.90 | 0.64% | 0.64% | +0.000 |
| NCLH | equity | 15.7381 | $20.39 | $320.90 | 0.64% | 0.64% | +0.000 |
| PLTR | equity | 2.7498 | $116.70 | $320.90 | 0.64% | 0.64% | +0.000 |
| SMCI | equity | 9.6309 | $33.32 | $320.90 | 0.64% | 0.64% | +0.000 |
| SNDK | equity | 0.1634 | $1963.60 | $320.90 | 0.64% | 0.64% | +0.000 |
| XYZ | equity | 4.4342 | $72.37 | $320.90 | 0.64% | 0.64% | +0.000 |
| __CASH__ | cash | — | — | $2,629.75 | 5.26% | 5.26% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (1 buys, 20 sells) |
| Total notional | $28,178.59 |
| Estimated turnover | 56.4% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.3281 | $519.85 | $170.56 |
| APH | sell | -1.1250 | $158.70 | $178.54 |
| APP | sell | -0.4231 | $467.02 | $197.61 |
| ARES | sell | -1.4853 | $120.78 | $179.39 |
| AXON | sell | -0.5308 | $433.04 | $229.87 |
| COHR | sell | -0.3839 | $381.22 | $146.35 |
| COIN | sell | -1.1350 | $158.18 | $179.53 |
| CVNA | sell | -2.8852 | $64.83 | $187.05 |
| DDOG | sell | -0.9009 | $220.57 | $198.72 |
| EL | sell | -2.3382 | $83.76 | $195.85 |
| EPAM | sell | -2.6847 | $76.89 | $206.43 |
| HOOD | sell | -1.8253 | $103.25 | $188.46 |
| INTC | sell | -1.2742 | $132.28 | $168.56 |
| LITE | sell | -0.1958 | $827.92 | $162.09 |
| MU | sell | -0.1254 | $1051.77 | $131.89 |
| NCLH | sell | -10.2848 | $20.39 | $209.71 |
| PLTR | sell | -1.6142 | $116.70 | $188.38 |
| SMCI | sell | -5.0759 | $33.32 | $169.13 |
| SNDK | sell | -0.0659 | $1963.60 | $129.47 |
| TLT | buy | +286.3768 | $85.78 | $24,565.40 |
| XYZ | sell | -2.7028 | $72.37 | $195.60 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $519.85 | $519.85 | -0.0 | ✅ |
| APH | sell | $158.70 | $158.70 | -0.0 | ✅ |
| APP | sell | $467.02 | $467.02 | -0.0 | ✅ |
| ARES | sell | $120.78 | $120.78 | -0.0 | ✅ |
| AXON | sell | $433.04 | $433.04 | -0.0 | ✅ |
| COHR | sell | $381.22 | $381.22 | -0.0 | ✅ |
| COIN | sell | $158.18 | $158.18 | -0.0 | ✅ |
| CVNA | sell | $64.83 | $64.83 | -0.0 | ✅ |
| DDOG | sell | $220.57 | $220.57 | -0.0 | ✅ |
| EL | sell | $83.76 | $83.76 | -0.0 | ✅ |
| EPAM | sell | $76.89 | $76.89 | -0.0 | ✅ |
| HOOD | sell | $103.25 | $103.25 | -0.0 | ✅ |
| INTC | sell | $132.28 | $132.28 | -0.0 | ✅ |
| LITE | sell | $827.92 | $827.92 | -0.0 | ✅ |
| MU | sell | $1051.77 | $1051.77 | -0.0 | ✅ |
| NCLH | sell | $20.39 | $20.39 | -0.0 | ✅ |
| PLTR | sell | $116.70 | $116.70 | -0.0 | ✅ |
| SMCI | sell | $33.32 | $33.32 | -0.0 | ✅ |
| SNDK | sell | $1963.60 | $1963.60 | -0.0 | ✅ |
| TLT | buy | $85.78 | $85.78 | +0.0 | ✅ |
| XYZ | sell | $72.37 | $72.37 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-22

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
| Trend | 72.33% |
| Cash | 2.67% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.35 (53.6% of NAV) |
| Cash | $23,182.65 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| CVNA | equity | 7.8350 | $66.67 | $522.36 | 1.04% | 1.04% | +0.002 |
| AMD | equity | 0.9454 | $551.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1471 | $165.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.1422 | $125.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 3.7002 | $140.94 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2257 | $425.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1637 | $164.84 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.2719 | $410.03 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.1694 | $84.53 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.8582 | $76.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.9333 | $105.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3558 | $221.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.3640 | $119.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5834 | $893.93 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4305 | $1211.38 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.0230 | $20.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2294 | $2273.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 14.7067 | $35.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.1370 | $73.07 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.1103 | $469.39 | $521.14 | 1.04% | 1.04% | -0.001 |
| __CASH__ | cash | — | — | $23,182.65 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 18 (9 buys, 9 sells) |
| Total notional | $375.59 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0251 | $551.63 | $13.84 |
| APH | sell | -0.0384 | $165.71 | $6.36 |
| ARES | buy | +0.1102 | $125.90 | $13.87 |
| AXON | buy | +0.0390 | $410.03 | $16.00 |
| COHR | sell | -0.1130 | $425.48 | $48.07 |
| COIN | sell | -0.0306 | $164.84 | $5.05 |
| DDOG | buy | +0.0172 | $221.37 | $3.81 |
| EL | buy | +0.0204 | $84.53 | $1.72 |
| EPAM | buy | +0.0537 | $76.04 | $4.08 |
| HOOD | buy | +0.1113 | $105.71 | $11.77 |
| INTC | sell | -0.1919 | $140.94 | $27.05 |
| LITE | sell | -0.0301 | $893.93 | $26.95 |
| MU | sell | -0.0294 | $1211.38 | $35.59 |
| NCLH | buy | +0.5093 | $20.04 | $10.21 |
| PLTR | buy | +0.3047 | $119.50 | $36.41 |
| SMCI | sell | -2.3024 | $35.46 | $81.64 |
| SNDK | sell | -0.0093 | $2273.73 | $21.24 |
| XYZ | buy | +0.1632 | $73.07 | $11.93 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 18 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 18 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $551.63 | $551.63 | -0.0 | ✅ |
| APH | sell | $165.71 | $165.71 | -0.0 | ✅ |
| ARES | buy | $125.90 | $125.90 | +0.0 | ✅ |
| AXON | buy | $410.03 | $410.03 | +0.0 | ✅ |
| COHR | sell | $425.48 | $425.48 | -0.0 | ✅ |
| COIN | sell | $164.84 | $164.84 | -0.0 | ✅ |
| DDOG | buy | $221.37 | $221.37 | +0.0 | ✅ |
| EL | buy | $84.53 | $84.53 | +0.0 | ✅ |
| EPAM | buy | $76.04 | $76.04 | +0.0 | ✅ |
| HOOD | buy | $105.71 | $105.71 | +0.0 | ✅ |
| INTC | sell | $140.94 | $140.94 | -0.0 | ✅ |
| LITE | sell | $893.93 | $893.93 | -0.0 | ✅ |
| MU | sell | $1211.38 | $1211.38 | -0.0 | ✅ |
| NCLH | buy | $20.04 | $20.04 | +0.0 | ✅ |
| PLTR | buy | $119.50 | $119.50 | +0.0 | ✅ |
| SMCI | sell | $35.46 | $35.46 | -0.0 | ✅ |
| SNDK | sell | $2273.73 | $2273.73 | -0.0 | ✅ |
| XYZ | buy | $73.07 | $73.07 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-19

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
| Trend | 72.33% |
| Cash | 2.67% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.33 (53.6% of NAV) |
| Cash | $23,182.67 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| AXON | equity | 1.2328 | $423.40 | $521.98 | 1.04% | 1.04% | +0.001 |
| AMD | equity | 0.9705 | $537.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.0320 | $129.34 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.1103 | $469.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3387 | $389.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1855 | $163.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1943 | $163.26 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3386 | $223.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.8045 | $76.64 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.8220 | $108.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8350 | $66.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.1490 | $84.81 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 3.8921 | $133.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6135 | $850.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4599 | $1133.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 25.5137 | $20.44 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.0593 | $128.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.0091 | $30.66 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2387 | $2184.75 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.9738 | $74.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.67 | 46.37% | 46.37% | +0.000 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-18

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
| Trend | 72.33% |
| Cash | 2.67% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.33 (53.6% of NAV) |
| Cash | $23,182.67 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| AXON | equity | 1.2328 | $423.40 | $521.98 | 1.04% | 1.04% | +0.001 |
| AMD | equity | 0.9705 | $537.37 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 4.0320 | $129.34 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.1103 | $469.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3387 | $389.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.1855 | $163.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1943 | $163.26 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3386 | $223.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 6.8045 | $76.64 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.8220 | $108.15 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.8350 | $66.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.1490 | $84.81 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 3.8921 | $133.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6135 | $850.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4599 | $1133.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 25.5137 | $20.44 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.0593 | $128.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.0091 | $30.66 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2387 | $2184.75 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.9738 | $74.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.67 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (6 buys, 13 sells) |
| Total notional | $469.17 |
| Estimated turnover | 0.9% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0471 | $537.37 | $25.33 |
| APH | sell | -0.0563 | $163.71 | $9.23 |
| APP | buy | +0.0226 | $469.71 | $10.64 |
| ARES | sell | -0.0311 | $129.34 | $4.02 |
| COHR | sell | -0.0379 | $389.57 | $14.76 |
| COIN | buy | +0.0322 | $163.26 | $5.25 |
| CVNA | sell | -0.4612 | $66.56 | $30.70 |
| DDOG | buy | +0.0375 | $223.00 | $8.35 |
| EL | sell | -0.1752 | $84.81 | $14.86 |
| EPAM | buy | +0.8581 | $76.64 | $65.77 |
| HOOD | sell | -0.1352 | $108.15 | $14.62 |
| INTC | sell | -0.4143 | $133.99 | $55.51 |
| LITE | buy | +0.0141 | $850.00 | $11.98 |
| MU | sell | -0.0400 | $1133.99 | $45.39 |
| NCLH | sell | -0.7848 | $20.44 | $16.04 |
| PLTR | buy | +0.0671 | $128.47 | $8.62 |
| SMCI | sell | -1.7634 | $30.66 | $54.06 |
| SNDK | sell | -0.0275 | $2184.75 | $60.15 |
| XYZ | sell | -0.1857 | $74.78 | $13.89 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $537.37 | $537.37 | -0.0 | ✅ |
| APH | sell | $163.71 | $163.71 | -0.0 | ✅ |
| APP | buy | $469.71 | $469.71 | +0.0 | ✅ |
| ARES | sell | $129.34 | $129.34 | -0.0 | ✅ |
| COHR | sell | $389.57 | $389.57 | -0.0 | ✅ |
| COIN | buy | $163.26 | $163.26 | +0.0 | ✅ |
| CVNA | sell | $66.56 | $66.56 | -0.0 | ✅ |
| DDOG | buy | $223.00 | $223.00 | +0.0 | ✅ |
| EL | sell | $84.81 | $84.81 | -0.0 | ✅ |
| EPAM | buy | $76.64 | $76.64 | +0.0 | ✅ |
| HOOD | sell | $108.15 | $108.15 | -0.0 | ✅ |
| INTC | sell | $133.99 | $133.99 | -0.0 | ✅ |
| LITE | buy | $850.00 | $850.00 | +0.0 | ✅ |
| MU | sell | $1133.99 | $1133.99 | -0.0 | ✅ |
| NCLH | sell | $20.44 | $20.44 | -0.0 | ✅ |
| PLTR | buy | $128.47 | $128.47 | +0.0 | ✅ |
| SMCI | sell | $30.66 | $30.66 | -0.0 | ✅ |
| SNDK | sell | $2184.75 | $2184.75 | -0.0 | ✅ |
| XYZ | sell | $74.78 | $74.78 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-17

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
| Trend | 72.33% |
| Cash | 2.67% |

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
| ARES | equity | 4.0631 | $128.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0176 | $512.48 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.2418 | $160.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0876 | $479.49 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3765 | $378.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.2328 | $423.01 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.1621 | $164.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.3011 | $226.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.9464 | $87.70 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 4.9572 | $105.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.2962 | $62.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.3243 | $82.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.3064 | $121.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5994 | $869.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4999 | $1043.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.2985 | $19.83 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.9922 | $130.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 18.7725 | $27.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2662 | $1958.80 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.1595 | $72.84 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (15 buys, 5 sells) |
| Total notional | $383.24 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0104 | $512.48 | $5.34 |
| APH | sell | -0.0515 | $160.87 | $8.29 |
| APP | buy | +0.0754 | $479.49 | $36.15 |
| ARES | buy | +0.1996 | $128.35 | $25.62 |
| AXON | buy | +0.0351 | $423.01 | $14.83 |
| COHR | buy | +0.0142 | $378.85 | $5.39 |
| COIN | buy | +0.0813 | $164.92 | $13.40 |
| CVNA | buy | +0.8505 | $62.86 | $53.46 |
| DDOG | buy | +0.0446 | $226.63 | $10.11 |
| EL | buy | +0.3697 | $82.46 | $30.49 |
| EPAM | buy | +0.3587 | $87.70 | $31.46 |
| HOOD | sell | -0.4352 | $105.20 | $45.78 |
| INTC | sell | -0.1490 | $121.10 | $18.04 |
| LITE | buy | +0.0037 | $869.98 | $3.21 |
| MU | sell | -0.0110 | $1043.19 | $11.46 |
| NCLH | buy | +0.6468 | $19.83 | $12.83 |
| PLTR | buy | +0.0785 | $130.63 | $10.25 |
| SMCI | buy | +0.9251 | $27.78 | $25.70 |
| SNDK | buy | +0.0044 | $1958.80 | $8.58 |
| XYZ | buy | +0.1764 | $72.84 | $12.85 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $512.48 | $512.48 | -0.0 | ✅ |
| APH | sell | $160.87 | $160.87 | -0.0 | ✅ |
| APP | buy | $479.49 | $479.49 | +0.0 | ✅ |
| ARES | buy | $128.35 | $128.35 | +0.0 | ✅ |
| AXON | buy | $423.01 | $423.01 | +0.0 | ✅ |
| COHR | buy | $378.85 | $378.85 | +0.0 | ✅ |
| COIN | buy | $164.92 | $164.92 | +0.0 | ✅ |
| CVNA | buy | $62.86 | $62.86 | +0.0 | ✅ |
| DDOG | buy | $226.63 | $226.63 | +0.0 | ✅ |
| EL | buy | $82.46 | $82.46 | +0.0 | ✅ |
| EPAM | buy | $87.70 | $87.70 | +0.0 | ✅ |
| HOOD | sell | $105.20 | $105.20 | -0.0 | ✅ |
| INTC | sell | $121.10 | $121.10 | -0.0 | ✅ |
| LITE | buy | $869.98 | $869.98 | +0.0 | ✅ |
| MU | sell | $1043.19 | $1043.19 | -0.0 | ✅ |
| NCLH | buy | $19.83 | $19.83 | +0.0 | ✅ |
| PLTR | buy | $130.63 | $130.63 | +0.0 | ✅ |
| SMCI | buy | $27.78 | $27.78 | +0.0 | ✅ |
| SNDK | buy | $1958.80 | $1958.80 | +0.0 | ✅ |
| XYZ | buy | $72.84 | $72.84 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-16

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
| Trend | 72.33% |
| Cash | 2.67% |

**Trend breakdown:**
- TLT: 32.77%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $26,817.57 (53.6% of NAV) |
| Cash | $23,182.43 (46.4% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 191.0335 | $85.78 | $16,386.85 | 32.77% | 32.77% | +0.000 |
| APH | equity | 3.2933 | $158.57 | $522.22 | 1.04% | 1.04% | +0.001 |
| APP | equity | 1.0122 | $515.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0280 | $507.29 | $521.50 | 1.04% | 1.04% | +0.000 |
| ARES | equity | 3.8635 | $134.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3623 | $382.81 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1978 | $435.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.0809 | $169.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.2565 | $231.11 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.5877 | $93.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.3924 | $96.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.4457 | $70.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 5.9546 | $87.58 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.4554 | $117.05 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5958 | $875.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5109 | $1020.76 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 25.6517 | $20.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.9137 | $133.25 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.8474 | $29.22 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2619 | $1991.55 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 6.9831 | $74.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,182.43 | 46.36% | 46.36% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 19 (14 buys, 5 sells) |
| Total notional | $325.04 |
| Estimated turnover | 0.7% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0751 | $507.29 | $38.09 |
| APP | buy | +0.0110 | $515.20 | $5.67 |
| ARES | sell | -0.0280 | $134.98 | $3.77 |
| AXON | buy | +0.0211 | $435.39 | $9.20 |
| COHR | buy | +0.1021 | $382.81 | $39.10 |
| COIN | buy | +0.0064 | $169.27 | $1.08 |
| CVNA | sell | -0.1232 | $70.04 | $8.63 |
| DDOG | buy | +0.0192 | $231.11 | $4.43 |
| EL | buy | +0.1601 | $87.58 | $14.02 |
| EPAM | sell | -0.0368 | $93.33 | $3.43 |
| HOOD | buy | +0.0775 | $96.71 | $7.49 |
| INTC | buy | +0.3767 | $117.05 | $44.09 |
| LITE | buy | +0.0510 | $875.36 | $44.61 |
| MU | buy | +0.0316 | $1020.76 | $32.22 |
| NCLH | sell | -0.2420 | $20.33 | $4.92 |
| PLTR | buy | +0.0424 | $133.25 | $5.65 |
| SMCI | buy | +0.9430 | $29.22 | $27.55 |
| SNDK | buy | +0.0144 | $1991.55 | $28.78 |
| XYZ | sell | -0.0310 | $74.68 | $2.31 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 19 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 19 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $507.29 | $507.29 | +0.0 | ✅ |
| APP | buy | $515.20 | $515.20 | +0.0 | ✅ |
| ARES | sell | $134.98 | $134.98 | -0.0 | ✅ |
| AXON | buy | $435.39 | $435.39 | +0.0 | ✅ |
| COHR | buy | $382.81 | $382.81 | +0.0 | ✅ |
| COIN | buy | $169.27 | $169.27 | +0.0 | ✅ |
| CVNA | sell | $70.04 | $70.04 | -0.0 | ✅ |
| DDOG | buy | $231.11 | $231.11 | +0.0 | ✅ |
| EL | buy | $87.58 | $87.58 | +0.0 | ✅ |
| EPAM | sell | $93.33 | $93.33 | -0.0 | ✅ |
| HOOD | buy | $96.71 | $96.71 | +0.0 | ✅ |
| INTC | buy | $117.05 | $117.05 | +0.0 | ✅ |
| LITE | buy | $875.36 | $875.36 | +0.0 | ✅ |
| MU | buy | $1020.76 | $1020.76 | +0.0 | ✅ |
| NCLH | sell | $20.33 | $20.33 | -0.0 | ✅ |
| PLTR | buy | $133.25 | $133.25 | +0.0 | ✅ |
| SMCI | buy | $29.22 | $29.22 | +0.0 | ✅ |
| SNDK | buy | $1991.55 | $1991.55 | +0.0 | ✅ |
| XYZ | sell | $74.68 | $74.68 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-15

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
| Trend | 72.33% |
| Cash | 2.67% |

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
| ARES | equity | 3.8915 | $134.01 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 0.9529 | $547.26 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.2933 | $158.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0012 | $520.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2601 | $413.84 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1766 | $443.21 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.0745 | $169.62 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.2373 | $233.09 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.6245 | $92.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.3149 | $98.12 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.5689 | $68.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 5.7944 | $90.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.0787 | $127.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5448 | $957.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.4793 | $1087.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 25.8937 | $20.14 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8713 | $134.71 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 16.9044 | $30.85 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2474 | $2107.86 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.0141 | $74.35 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (1 buys, 19 sells) |
| Total notional | $456.34 |
| Estimated turnover | 0.9% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0665 | $547.26 | $36.38 |
| APH | sell | -0.1026 | $158.35 | $16.24 |
| APP | sell | -0.0486 | $520.86 | $25.29 |
| ARES | sell | -0.0133 | $134.01 | $1.78 |
| AXON | sell | -0.0039 | $443.21 | $1.75 |
| COHR | sell | -0.0943 | $413.84 | $39.02 |
| COIN | sell | -0.1893 | $169.62 | $32.12 |
| CVNA | sell | -0.5668 | $68.90 | $39.05 |
| DDOG | sell | -0.0310 | $233.09 | $7.24 |
| EL | sell | -0.0207 | $90.00 | $1.86 |
| EPAM | buy | +0.1569 | $92.72 | $14.54 |
| HOOD | sell | -0.2812 | $98.12 | $27.59 |
| INTC | sell | -0.1077 | $127.86 | $13.77 |
| LITE | sell | -0.0211 | $957.24 | $20.19 |
| MU | sell | -0.0519 | $1087.99 | $56.52 |
| NCLH | sell | -0.9462 | $20.14 | $19.06 |
| PLTR | sell | -0.2033 | $134.71 | $27.38 |
| SMCI | sell | -0.2164 | $30.85 | $6.68 |
| SNDK | sell | -0.0160 | $2107.86 | $33.65 |
| XYZ | sell | -0.4873 | $74.35 | $36.23 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $547.26 | $547.26 | -0.0 | ✅ |
| APH | sell | $158.35 | $158.35 | -0.0 | ✅ |
| APP | sell | $520.86 | $520.86 | -0.0 | ✅ |
| ARES | sell | $134.01 | $134.01 | -0.0 | ✅ |
| AXON | sell | $443.21 | $443.21 | -0.0 | ✅ |
| COHR | sell | $413.84 | $413.84 | -0.0 | ✅ |
| COIN | sell | $169.62 | $169.62 | -0.0 | ✅ |
| CVNA | sell | $68.90 | $68.90 | -0.0 | ✅ |
| DDOG | sell | $233.09 | $233.09 | -0.0 | ✅ |
| EL | sell | $90.00 | $90.00 | -0.0 | ✅ |
| EPAM | buy | $92.72 | $92.72 | +0.0 | ✅ |
| HOOD | sell | $98.12 | $98.12 | -0.0 | ✅ |
| INTC | sell | $127.86 | $127.86 | -0.0 | ✅ |
| LITE | sell | $957.24 | $957.24 | -0.0 | ✅ |
| MU | sell | $1087.99 | $1087.99 | -0.0 | ✅ |
| NCLH | sell | $20.14 | $20.14 | -0.0 | ✅ |
| PLTR | sell | $134.71 | $134.71 | -0.0 | ✅ |
| SMCI | sell | $30.85 | $30.85 | -0.0 | ✅ |
| SNDK | sell | $2107.86 | $2107.86 | -0.0 | ✅ |
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

## 2026-06-12

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
| Trend | 72.33% |
| Cash | 2.67% |

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
| ARES | equity | 3.9048 | $133.55 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0194 | $511.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.3959 | $153.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0498 | $496.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.3544 | $385.03 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1806 | $441.73 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2639 | $159.78 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.2684 | $229.90 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.4676 | $95.38 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.5961 | $93.19 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 8.1357 | $64.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 5.8151 | $89.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.1864 | $124.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5659 | $921.56 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5313 | $981.61 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 26.8399 | $19.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.0745 | $127.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.1208 | $30.46 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2634 | $1980.10 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.5014 | $69.52 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (7 buys, 13 sells) |
| Total notional | $301.38 |
| Estimated turnover | 0.6% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0483 | $511.57 | $24.68 |
| APH | sell | -0.0298 | $153.57 | $4.58 |
| APP | sell | -0.0399 | $496.77 | $19.83 |
| ARES | sell | -0.0611 | $133.55 | $8.17 |
| AXON | buy | +0.0118 | $441.73 | $5.22 |
| COHR | sell | -0.0799 | $385.03 | $30.77 |
| COIN | buy | +0.0132 | $159.78 | $2.11 |
| CVNA | buy | +0.4463 | $64.10 | $28.60 |
| DDOG | buy | +0.0420 | $229.90 | $9.66 |
| EL | sell | -0.1097 | $89.68 | $9.84 |
| EPAM | sell | -0.1544 | $95.38 | $14.73 |
| HOOD | sell | -0.0582 | $93.19 | $5.43 |
| INTC | sell | -0.2724 | $124.57 | $33.93 |
| LITE | sell | -0.0203 | $921.56 | $18.74 |
| MU | buy | +0.0076 | $981.61 | $7.47 |
| NCLH | sell | -0.5210 | $19.43 | $10.12 |
| PLTR | buy | +0.0961 | $127.99 | $12.29 |
| SMCI | buy | +0.8086 | $30.46 | $24.63 |
| SNDK | sell | -0.0138 | $1980.10 | $27.33 |
| XYZ | sell | -0.0467 | $69.52 | $3.25 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $511.57 | $511.57 | -0.0 | ✅ |
| APH | sell | $153.57 | $153.57 | -0.0 | ✅ |
| APP | sell | $496.77 | $496.77 | -0.0 | ✅ |
| ARES | sell | $133.55 | $133.55 | -0.0 | ✅ |
| AXON | buy | $441.73 | $441.73 | +0.0 | ✅ |
| COHR | sell | $385.03 | $385.03 | -0.0 | ✅ |
| COIN | buy | $159.78 | $159.78 | +0.0 | ✅ |
| CVNA | buy | $64.10 | $64.10 | +0.0 | ✅ |
| DDOG | buy | $229.90 | $229.90 | +0.0 | ✅ |
| EL | sell | $89.68 | $89.68 | -0.0 | ✅ |
| EPAM | sell | $95.38 | $95.38 | -0.0 | ✅ |
| HOOD | sell | $93.19 | $93.19 | -0.0 | ✅ |
| INTC | sell | $124.57 | $124.57 | -0.0 | ✅ |
| LITE | sell | $921.56 | $921.56 | -0.0 | ✅ |
| MU | buy | $981.61 | $981.61 | +0.0 | ✅ |
| NCLH | sell | $19.43 | $19.43 | -0.0 | ✅ |
| PLTR | buy | $127.99 | $127.99 | +0.0 | ✅ |
| SMCI | buy | $30.46 | $30.46 | +0.0 | ✅ |
| SNDK | sell | $1980.10 | $1980.10 | -0.0 | ✅ |
| XYZ | sell | $69.52 | $69.52 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-11

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
| Trend | 72.33% |
| Cash | 2.67% |

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
| ARES | equity | 3.9659 | $131.50 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0677 | $488.45 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.4257 | $152.23 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0897 | $478.57 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.4343 | $363.58 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1688 | $446.20 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2506 | $160.43 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.2263 | $234.24 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.6220 | $92.76 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 5.6543 | $92.23 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.6895 | $67.82 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 5.9248 | $88.02 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.4588 | $116.96 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5862 | $889.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5237 | $995.87 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 27.3610 | $19.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.9785 | $131.08 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 16.3122 | $31.97 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.2772 | $1881.51 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.5481 | $69.09 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (3 buys, 17 sells) |
| Total notional | $506.51 |
| Estimated turnover | 1.0% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.0851 | $488.45 | $41.56 |
| APH | sell | -0.0744 | $152.23 | $11.32 |
| APP | buy | +0.0319 | $478.57 | $15.24 |
| ARES | sell | -0.1394 | $131.50 | $18.33 |
| AXON | buy | +0.0036 | $446.20 | $1.62 |
| COHR | sell | -0.0356 | $363.58 | $12.95 |
| COIN | sell | -0.1364 | $160.43 | $21.88 |
| CVNA | sell | -0.0652 | $67.82 | $4.42 |
| DDOG | sell | -0.0646 | $234.24 | $15.14 |
| EL | sell | -0.1825 | $88.02 | $16.06 |
| EPAM | buy | +0.0169 | $92.76 | $1.57 |
| HOOD | sell | -0.3843 | $92.23 | $35.45 |
| INTC | sell | -0.4132 | $116.96 | $48.33 |
| LITE | sell | -0.0250 | $889.59 | $22.20 |
| MU | sell | -0.0611 | $995.87 | $60.80 |
| NCLH | sell | -1.7406 | $19.06 | $33.18 |
| PLTR | sell | -0.0266 | $131.08 | $3.48 |
| SMCI | sell | -1.5047 | $31.97 | $48.11 |
| SNDK | sell | -0.0402 | $1881.51 | $75.62 |
| XYZ | sell | -0.2787 | $69.09 | $19.25 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $488.45 | $488.45 | -0.0 | ✅ |
| APH | sell | $152.23 | $152.23 | -0.0 | ✅ |
| APP | buy | $478.57 | $478.57 | +0.0 | ✅ |
| ARES | sell | $131.50 | $131.50 | -0.0 | ✅ |
| AXON | buy | $446.20 | $446.20 | +0.0 | ✅ |
| COHR | sell | $363.58 | $363.58 | -0.0 | ✅ |
| COIN | sell | $160.43 | $160.43 | -0.0 | ✅ |
| CVNA | sell | $67.82 | $67.82 | -0.0 | ✅ |
| DDOG | sell | $234.24 | $234.24 | -0.0 | ✅ |
| EL | sell | $88.02 | $88.02 | -0.0 | ✅ |
| EPAM | buy | $92.76 | $92.76 | +0.0 | ✅ |
| HOOD | sell | $92.23 | $92.23 | -0.0 | ✅ |
| INTC | sell | $116.96 | $116.96 | -0.0 | ✅ |
| LITE | sell | $889.59 | $889.59 | -0.0 | ✅ |
| MU | sell | $995.87 | $995.87 | -0.0 | ✅ |
| NCLH | sell | $19.06 | $19.06 | -0.0 | ✅ |
| PLTR | sell | $131.08 | $131.08 | -0.0 | ✅ |
| SMCI | sell | $31.97 | $31.97 | -0.0 | ✅ |
| SNDK | sell | $1881.51 | $1881.51 | -0.0 | ✅ |
| XYZ | sell | $69.09 | $69.09 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-10

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
| Trend | 72.33% |
| Cash | 2.67% |

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
| ARES | equity | 4.1053 | $127.03 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.1527 | $452.40 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.5001 | $149.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 1.0579 | $492.98 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.4700 | $354.77 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1651 | $447.59 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.3870 | $153.97 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.2910 | $227.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.6051 | $93.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.0387 | $86.36 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.7546 | $67.25 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.1073 | $85.39 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.8720 | $107.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.6112 | $853.26 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5847 | $891.88 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 29.1016 | $17.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 4.0051 | $130.21 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 17.8169 | $29.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3174 | $1643.23 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.8268 | $66.63 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (20 buys, 1 sells) |
| Total notional | $24,622.73 |
| Estimated turnover | 49.2% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.5468 | $452.40 | $247.35 |
| APH | buy | +1.6270 | $149.00 | $242.42 |
| APP | buy | +0.5046 | $492.98 | $248.76 |
| ARES | buy | +1.8769 | $127.03 | $238.42 |
| AXON | buy | +0.5283 | $447.59 | $236.48 |
| COHR | buy | +0.6604 | $354.77 | $234.30 |
| COIN | buy | +1.5340 | $153.97 | $236.19 |
| CVNA | buy | +3.6152 | $67.25 | $243.12 |
| DDOG | buy | +1.0235 | $227.63 | $232.98 |
| EL | buy | +2.7784 | $85.39 | $237.24 |
| EPAM | buy | +2.5926 | $93.04 | $241.21 |
| HOOD | buy | +2.5989 | $86.36 | $224.44 |
| INTC | buy | +2.2020 | $107.04 | $235.70 |
| LITE | buy | +0.2605 | $853.26 | $222.30 |
| MU | buy | +0.2768 | $891.88 | $246.90 |
| NCLH | buy | +13.9597 | $17.92 | $250.16 |
| PLTR | buy | +1.8233 | $130.21 | $237.41 |
| SMCI | buy | +10.7266 | $29.27 | $313.97 |
| SNDK | buy | +0.1424 | $1643.23 | $233.93 |
| TLT | sell | -230.5794 | $85.78 | $19,779.10 |
| XYZ | buy | +3.6073 | $66.63 | $240.35 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $452.40 | $452.40 | +0.0 | ✅ |
| APH | buy | $149.00 | $149.00 | +0.0 | ✅ |
| APP | buy | $492.98 | $492.98 | +0.0 | ✅ |
| ARES | buy | $127.03 | $127.03 | +0.0 | ✅ |
| AXON | buy | $447.59 | $447.59 | +0.0 | ✅ |
| COHR | buy | $354.77 | $354.77 | +0.0 | ✅ |
| COIN | buy | $153.97 | $153.97 | +0.0 | ✅ |
| CVNA | buy | $67.25 | $67.25 | +0.0 | ✅ |
| DDOG | buy | $227.63 | $227.63 | +0.0 | ✅ |
| EL | buy | $85.39 | $85.39 | +0.0 | ✅ |
| EPAM | buy | $93.04 | $93.04 | +0.0 | ✅ |
| HOOD | buy | $86.36 | $86.36 | +0.0 | ✅ |
| INTC | buy | $107.04 | $107.04 | +0.0 | ✅ |
| LITE | buy | $853.26 | $853.26 | +0.0 | ✅ |
| MU | buy | $891.88 | $891.88 | +0.0 | ✅ |
| NCLH | buy | $17.92 | $17.92 | +0.0 | ✅ |
| PLTR | buy | $130.21 | $130.21 | +0.0 | ✅ |
| SMCI | buy | $29.27 | $29.27 | +0.0 | ✅ |
| SNDK | buy | $1643.23 | $1643.23 | +0.0 | ✅ |
| TLT | sell | $85.78 | $85.78 | -0.0 | ✅ |
| XYZ | buy | $66.63 | $66.63 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-09

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
| Equity | 25.00% |
| Trend | 72.33% |
| Cash | 2.67% |

**Trend breakdown:**
- TLT: 72.33%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 21 positions + cash |
| Invested | $41,928.95 (83.9% of NAV) |
| Cash | $8,071.05 (16.1% of NAV) |
| Total NAV | $50,000.00 |
| Max weight drift | 0.00 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| TLT | trend | 421.6129 | $85.78 | $36,165.95 | 72.33% | 72.33% | +0.000 |
| ARES | equity | 2.2284 | $129.31 | $288.15 | 0.58% | 0.58% | +0.000 |
| AMD | equity | 0.6060 | $475.51 | $288.15 | 0.58% | 0.58% | +0.000 |
| APH | equity | 1.8731 | $153.84 | $288.15 | 0.58% | 0.58% | +0.000 |
| APP | equity | 0.5532 | $520.84 | $288.15 | 0.58% | 0.58% | +0.000 |
| COHR | equity | 0.8095 | $355.94 | $288.15 | 0.58% | 0.58% | +0.000 |
| AXON | equity | 0.6368 | $452.51 | $288.15 | 0.58% | 0.58% | +0.000 |
| COIN | equity | 1.8531 | $155.50 | $288.15 | 0.58% | 0.58% | +0.000 |
| DDOG | equity | 1.2675 | $227.34 | $288.15 | 0.58% | 0.58% | +0.000 |
| EPAM | equity | 3.0125 | $95.65 | $288.15 | 0.58% | 0.58% | +0.000 |
| HOOD | equity | 3.4398 | $83.77 | $288.15 | 0.58% | 0.58% | +0.000 |
| CVNA | equity | 4.1395 | $69.61 | $288.15 | 0.58% | 0.58% | +0.000 |
| EL | equity | 3.3289 | $86.56 | $288.15 | 0.58% | 0.58% | +0.000 |
| INTC | equity | 2.6700 | $107.92 | $288.15 | 0.58% | 0.58% | +0.000 |
| LITE | equity | 0.3506 | $821.76 | $288.15 | 0.58% | 0.58% | +0.000 |
| MU | equity | 0.3079 | $935.89 | $288.15 | 0.58% | 0.58% | +0.000 |
| NCLH | equity | 15.1419 | $19.03 | $288.15 | 0.58% | 0.58% | +0.000 |
| PLTR | equity | 2.1818 | $132.07 | $288.15 | 0.58% | 0.58% | +0.000 |
| SMCI | equity | 7.0903 | $40.64 | $288.15 | 0.58% | 0.58% | +0.000 |
| SNDK | equity | 0.1750 | $1646.54 | $288.15 | 0.58% | 0.58% | +0.000 |
| XYZ | equity | 4.2195 | $68.29 | $288.15 | 0.58% | 0.58% | +0.000 |
| __CASH__ | cash | — | — | $8,071.05 | 16.14% | 16.14% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 21 (1 buys, 20 sells) |
| Total notional | $24,217.21 |
| Estimated turnover | 48.4% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | sell | -0.4576 | $475.51 | $217.59 |
| APH | sell | -1.7640 | $153.84 | $271.37 |
| APP | sell | -0.3719 | $520.84 | $193.71 |
| ARES | sell | -1.9235 | $129.31 | $248.72 |
| AXON | sell | -0.4703 | $452.51 | $212.81 |
| COHR | sell | -0.4879 | $355.94 | $173.68 |
| COIN | sell | -1.3639 | $155.50 | $212.09 |
| CVNA | sell | -3.3695 | $69.61 | $234.55 |
| DDOG | sell | -0.9835 | $227.34 | $223.58 |
| EL | sell | -2.8325 | $86.56 | $245.18 |
| EPAM | sell | -2.3793 | $95.65 | $227.58 |
| HOOD | sell | -2.6926 | $83.77 | $225.56 |
| INTC | sell | -2.0593 | $107.92 | $222.24 |
| LITE | sell | -0.2318 | $821.76 | $190.46 |
| MU | sell | -0.2415 | $935.89 | $225.99 |
| NCLH | sell | -12.9713 | $19.03 | $246.84 |
| PLTR | sell | -1.6396 | $132.07 | $216.54 |
| SMCI | sell | -4.7647 | $40.64 | $193.64 |
| SNDK | sell | -0.1426 | $1646.54 | $234.79 |
| TLT | buy | +230.5794 | $85.78 | $19,779.10 |
| XYZ | sell | -3.2390 | $68.29 | $221.19 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 21 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 21 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | sell | $475.51 | $475.51 | -0.0 | ✅ |
| APH | sell | $153.84 | $153.84 | -0.0 | ✅ |
| APP | sell | $520.84 | $520.84 | -0.0 | ✅ |
| ARES | sell | $129.31 | $129.31 | -0.0 | ✅ |
| AXON | sell | $452.51 | $452.51 | -0.0 | ✅ |
| COHR | sell | $355.94 | $355.94 | -0.0 | ✅ |
| COIN | sell | $155.50 | $155.50 | -0.0 | ✅ |
| CVNA | sell | $69.61 | $69.61 | -0.0 | ✅ |
| DDOG | sell | $227.34 | $227.34 | -0.0 | ✅ |
| EL | sell | $86.56 | $86.56 | -0.0 | ✅ |
| EPAM | sell | $95.65 | $95.65 | -0.0 | ✅ |
| HOOD | sell | $83.77 | $83.77 | -0.0 | ✅ |
| INTC | sell | $107.92 | $107.92 | -0.0 | ✅ |
| LITE | sell | $821.76 | $821.76 | -0.0 | ✅ |
| MU | sell | $935.89 | $935.89 | -0.0 | ✅ |
| NCLH | sell | $19.03 | $19.03 | -0.0 | ✅ |
| PLTR | sell | $132.07 | $132.07 | -0.0 | ✅ |
| SMCI | sell | $40.64 | $40.64 | -0.0 | ✅ |
| SNDK | sell | $1646.54 | $1646.54 | -0.0 | ✅ |
| TLT | buy | $85.78 | $85.78 | +0.0 | ✅ |
| XYZ | sell | $68.29 | $68.29 | -0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

## 2026-06-08

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
| ARES | equity | 4.1519 | $125.60 | $521.50 | 1.04% | 1.04% | +0.000 |
| AMD | equity | 1.0636 | $490.33 | $521.50 | 1.04% | 1.04% | +0.000 |
| APH | equity | 3.6371 | $143.38 | $521.50 | 1.04% | 1.04% | +0.000 |
| APP | equity | 0.9252 | $563.69 | $521.50 | 1.04% | 1.04% | +0.000 |
| COHR | equity | 1.2975 | $401.93 | $521.50 | 1.04% | 1.04% | +0.000 |
| AXON | equity | 1.1071 | $471.06 | $521.50 | 1.04% | 1.04% | +0.000 |
| COIN | equity | 3.2170 | $162.11 | $521.50 | 1.04% | 1.04% | +0.000 |
| DDOG | equity | 2.2509 | $231.68 | $521.50 | 1.04% | 1.04% | +0.000 |
| EPAM | equity | 5.3919 | $96.72 | $521.50 | 1.04% | 1.04% | +0.000 |
| HOOD | equity | 6.1324 | $85.04 | $521.50 | 1.04% | 1.04% | +0.000 |
| CVNA | equity | 7.5090 | $69.45 | $521.50 | 1.04% | 1.04% | +0.000 |
| EL | equity | 6.1614 | $84.64 | $521.50 | 1.04% | 1.04% | +0.000 |
| INTC | equity | 4.7293 | $110.27 | $521.50 | 1.04% | 1.04% | +0.000 |
| LITE | equity | 0.5824 | $895.40 | $521.50 | 1.04% | 1.04% | +0.000 |
| MU | equity | 0.5494 | $949.28 | $521.50 | 1.04% | 1.04% | +0.000 |
| NCLH | equity | 28.1132 | $18.55 | $521.50 | 1.04% | 1.04% | +0.000 |
| PLTR | equity | 3.8214 | $136.47 | $521.50 | 1.04% | 1.04% | +0.000 |
| SMCI | equity | 11.8550 | $43.99 | $521.50 | 1.04% | 1.04% | +0.000 |
| SNDK | equity | 0.3176 | $1642.00 | $521.50 | 1.04% | 1.04% | +0.000 |
| XYZ | equity | 7.4585 | $69.92 | $521.50 | 1.04% | 1.04% | +0.000 |
| __CASH__ | cash | — | — | $23,183.15 | 46.37% | 46.37% | +0.000 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 20 (17 buys, 3 sells) |
| Total notional | $397.34 |
| Estimated turnover | 0.8% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +0.0668 | $490.33 | $32.76 |
| APH | buy | +0.0839 | $143.38 | $12.03 |
| APP | sell | -0.0080 | $563.69 | $4.50 |
| ARES | buy | +0.1557 | $125.60 | $19.56 |
| AXON | buy | +0.0909 | $471.06 | $42.82 |
| COHR | buy | +0.0614 | $401.93 | $24.68 |
| COIN | buy | +0.0396 | $162.11 | $6.42 |
| CVNA | sell | -0.3698 | $69.45 | $25.68 |
| DDOG | buy | +0.1101 | $231.68 | $25.52 |
| EL | sell | -0.1293 | $84.64 | $10.95 |
| EPAM | buy | +0.0481 | $96.72 | $4.65 |
| HOOD | buy | +0.2284 | $85.04 | $19.42 |
| INTC | buy | +0.0639 | $110.27 | $7.04 |
| LITE | buy | +0.0306 | $895.40 | $27.41 |
| MU | buy | +0.0258 | $949.28 | $24.46 |
| NCLH | buy | +0.8524 | $18.55 | $15.81 |
| PLTR | buy | +0.1410 | $136.47 | $19.25 |
| SMCI | buy | +0.7356 | $43.99 | $32.36 |
| SNDK | buy | +0.0212 | $1642.00 | $34.88 |
| XYZ | buy | +0.1021 | $69.92 | $7.14 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 20 | — |
| Avg slippage | 0.0 bps | ✅ PASS |
| Flagged trades (> 30 bps) | 0 / 20 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $490.33 | $490.33 | +0.0 | ✅ |
| APH | buy | $143.38 | $143.38 | +0.0 | ✅ |
| APP | sell | $563.69 | $563.69 | -0.0 | ✅ |
| ARES | buy | $125.60 | $125.60 | +0.0 | ✅ |
| AXON | buy | $471.06 | $471.06 | +0.0 | ✅ |
| COHR | buy | $401.93 | $401.93 | +0.0 | ✅ |
| COIN | buy | $162.11 | $162.11 | +0.0 | ✅ |
| CVNA | sell | $69.45 | $69.45 | -0.0 | ✅ |
| DDOG | buy | $231.68 | $231.68 | +0.0 | ✅ |
| EL | sell | $84.64 | $84.64 | -0.0 | ✅ |
| EPAM | buy | $96.72 | $96.72 | +0.0 | ✅ |
| HOOD | buy | $85.04 | $85.04 | +0.0 | ✅ |
| INTC | buy | $110.27 | $110.27 | +0.0 | ✅ |
| LITE | buy | $895.40 | $895.40 | +0.0 | ✅ |
| MU | buy | $949.28 | $949.28 | +0.0 | ✅ |
| NCLH | buy | $18.55 | $18.55 | +0.0 | ✅ |
| PLTR | buy | $136.47 | $136.47 | +0.0 | ✅ |
| SMCI | buy | $43.99 | $43.99 | +0.0 | ✅ |
| SNDK | buy | $1642.00 | $1642.00 | +0.0 | ✅ |
| XYZ | buy | $69.92 | $69.92 | +0.0 | ✅ |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 0.0 bps avg | ✅ |
| H-4 Weight drift | 0.00 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

