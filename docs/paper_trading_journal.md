# Phase H — Paper Trading Journal

> **Portfolio:** $50,000 NAV | Broker: Alpaca paper | Config: v H.0.0
> **Rebalance cadence:** every 14 days | **Mode:** rl_e7 (dual-mode switching active)
> **Gates:** H-1 pipeline · H-2 slippage <20 bps · H-3 turnover <35% · H-4 drift <5pp · H-5 RL mode · H-6 Sharpe · H-7 data parity · H-8 audit trail

Newest entries at the top. Updated automatically by `scripts/generate_paper_journal.py`.

---

## 2026-05-10

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
| Trend | 56.52% |
| Cash | 18.48% |

**Trend breakdown:**
- GLD: 14.49%
- UUP: 85.29%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 22 |
| Total market value | $66,652.16 |
| Max weight drift | 0.09 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 1545.6307 | $27.56 | $42,597.58 | 85.20% | 85.29% | -0.093 |
| GLD | trend | 17.3406 | $416.74 | $7,226.53 | 14.45% | 14.49% | -0.040 |
| APP | equity | 1.8930 | $455.00 | $861.30 | 1.72% | 1.70% | +0.025 |
| EPAM | equity | 7.1323 | $120.50 | $859.44 | 1.72% | 1.70% | +0.022 |
| COIN | equity | 4.2479 | $202.08 | $858.41 | 1.72% | 1.70% | +0.020 |
| APH | equity | 5.6683 | $151.36 | $857.95 | 1.72% | 1.70% | +0.019 |
| COHR | equity | 2.5249 | $337.36 | $851.81 | 1.70% | 1.70% | +0.006 |
| HOOD | equity | 10.0177 | $84.90 | $850.50 | 1.70% | 1.70% | +0.004 |
| EL | equity | 10.9047 | $77.95 | $850.02 | 1.70% | 1.70% | +0.003 |
| PLTR | equity | 5.9305 | $142.96 | $847.83 | 1.70% | 1.70% | -0.002 |
| MU | equity | 1.7084 | $495.92 | $847.23 | 1.69% | 1.70% | -0.003 |
| ARES | equity | 7.3644 | $114.96 | $846.61 | 1.69% | 1.70% | -0.004 |
| NCLH | equity | 45.8455 | $18.46 | $846.31 | 1.69% | 1.70% | -0.005 |
| INTC | equity | 10.2811 | $82.20 | $845.10 | 1.69% | 1.70% | -0.007 |
| AXON | equity | 2.1369 | $394.12 | $842.19 | 1.68% | 1.70% | -0.013 |
| CVNA | equity | 2.0744 | $405.57 | $841.32 | 1.68% | 1.70% | -0.015 |
| DDOG | equity | 6.5539 | $128.13 | $839.75 | 1.68% | 1.70% | -0.018 |
| XYZ | equity | 11.8470 | $70.34 | $833.32 | 1.67% | 1.70% | -0.031 |
| AMD | equity | 2.4398 | $336.76 | $821.64 | 1.64% | 1.70% | -0.054 |
| SNDK | equity | 0.8573 | $954.56 | $818.30 | 1.64% | 1.70% | -0.061 |
| LITE | equity | 0.9625 | $837.02 | $805.65 | 1.61% | 1.70% | -0.086 |
| SMCI | equity | 29.1816 | $27.53 | $803.37 | 1.61% | 1.70% | -0.090 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 22 (22 buys, 0 sells) |
| Total notional | $66,862.25 |
| Estimated turnover | 133.7% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +2.4398 | $347.81 | $848.60 |
| APH | buy | +5.6683 | $149.71 | $848.60 |
| APP | buy | +1.8930 | $448.29 | $848.60 |
| ARES | buy | +7.3644 | $115.23 | $848.60 |
| AXON | buy | +2.1369 | $397.12 | $848.60 |
| COHR | buy | +2.5249 | $336.09 | $848.60 |
| COIN | buy | +4.2479 | $199.77 | $848.60 |
| CVNA | buy | +2.0744 | $409.08 | $848.60 |
| DDOG | buy | +6.5539 | $129.48 | $848.60 |
| EL | buy | +10.9047 | $77.82 | $848.60 |
| EPAM | buy | +7.1323 | $118.98 | $848.60 |
| GLD | buy | +17.3406 | $417.88 | $7,246.30 |
| HOOD | buy | +10.0177 | $84.71 | $848.60 |
| INTC | buy | +10.2811 | $82.54 | $848.60 |
| LITE | buy | +0.9625 | $881.64 | $848.60 |
| MU | buy | +1.7084 | $496.72 | $848.60 |
| NCLH | buy | +45.8455 | $18.51 | $848.60 |
| PLTR | buy | +5.9305 | $143.09 | $848.60 |
| SMCI | buy | +29.1816 | $29.08 | $848.60 |
| SNDK | buy | +0.8573 | $989.90 | $848.60 |
| UUP | buy | +1545.6307 | $27.59 | $42,643.95 |
| XYZ | buy | +11.8470 | $71.63 | $848.60 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 22 | — |
| Avg slippage | 131.6 bps | ⚠️ above target |
| Flagged trades (> 30 bps) | 14 / 22 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $336.76 | $347.81 | -317.7 | 🚨 |
| APH | buy | $151.36 | $149.71 | +110.2 | 🚨 |
| APP | buy | $455.00 | $448.29 | +149.7 | 🚨 |
| ARES | buy | $114.96 | $115.23 | -23.4 | ✅ |
| AXON | buy | $394.12 | $397.12 | -75.5 | 🚨 |
| COHR | buy | $337.36 | $336.09 | +37.8 | 🚨 |
| COIN | buy | $202.08 | $199.77 | +115.6 | 🚨 |
| CVNA | buy | $405.57 | $409.08 | -85.8 | 🚨 |
| DDOG | buy | $128.13 | $129.48 | -104.3 | 🚨 |
| EL | buy | $77.95 | $77.82 | +16.7 | ✅ |
| EPAM | buy | $120.50 | $118.98 | +127.8 | 🚨 |
| GLD | buy | $416.74 | $417.88 | -27.3 | ✅ |
| HOOD | buy | $84.90 | $84.71 | +22.4 | ✅ |
| INTC | buy | $82.20 | $82.54 | -41.2 | 🚨 |
| LITE | buy | $837.02 | $881.64 | -506.1 | 🚨 |
| MU | buy | $495.92 | $496.72 | -16.1 | ✅ |
| NCLH | buy | $18.46 | $18.51 | -27.0 | ✅ |
| PLTR | buy | $142.96 | $143.09 | -9.1 | ✅ |
| SMCI | buy | $27.53 | $29.08 | -533.0 | 🚨 |
| SNDK | buy | $954.56 | $989.90 | -357.0 | 🚨 |
| UUP | buy | $27.56 | $27.59 | -10.9 | ✅ |
| XYZ | buy | $70.34 | $71.63 | -180.1 | 🚨 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 131.6 bps avg | ⚠️ T=0 artifact |
| H-4 Weight drift | 0.09 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---

