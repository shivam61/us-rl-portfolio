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
| Trend | 56.52% |
| Cash | 18.48% |

**Trend breakdown:**
- GLD: 14.49%
- UUP: 85.29%

### Portfolio Snapshot
| Metric | Value |
|--------|-------|
| Holdings | 22 |
| Total market value | $66,488.46 |
| Max weight drift | 0.18 pp (H-4 gate: 5.0 pp) |

| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |
|--------|--------|--------|-------|-----------|---------|-----------|----------|
| UUP | trend | 1545.6307 | $27.56 | $42,597.58 | 85.20% | 85.29% | -0.093 |
| GLD | trend | 17.3406 | $416.74 | $7,226.53 | 14.45% | 14.49% | -0.040 |
| APH | equity | 6.6281 | $137.58 | $911.90 | 1.82% | 1.70% | +0.127 |
| AXON | equity | 2.1029 | $431.01 | $906.37 | 1.81% | 1.70% | +0.115 |
| APP | equity | 1.8111 | $494.07 | $894.82 | 1.79% | 1.70% | +0.092 |
| CVNA | equity | 10.8879 | $81.03 | $882.24 | 1.76% | 1.70% | +0.067 |
| EPAM | equity | 8.5518 | $103.11 | $881.78 | 1.76% | 1.70% | +0.066 |
| LITE | equity | 0.9389 | $915.87 | $859.93 | 1.72% | 1.70% | +0.023 |
| NCLH | equity | 49.6838 | $17.28 | $858.54 | 1.72% | 1.70% | +0.020 |
| XYZ | equity | 11.3373 | $75.63 | $857.44 | 1.71% | 1.70% | +0.018 |
| EL | equity | 9.8445 | $85.72 | $843.87 | 1.69% | 1.70% | -0.010 |
| HOOD | equity | 11.0165 | $76.24 | $839.90 | 1.68% | 1.70% | -0.017 |
| PLTR | equity | 6.1582 | $135.87 | $836.68 | 1.67% | 1.70% | -0.024 |
| ARES | equity | 6.7216 | $123.56 | $830.52 | 1.66% | 1.70% | -0.036 |
| COHR | equity | 2.5312 | $325.93 | $824.97 | 1.65% | 1.70% | -0.047 |
| SMCI | equity | 23.9921 | $33.32 | $799.42 | 1.60% | 1.70% | -0.098 |
| DDOG | equity | 4.2396 | $185.50 | $786.45 | 1.57% | 1.70% | -0.124 |
| COIN | equity | 4.2185 | $185.84 | $783.98 | 1.57% | 1.70% | -0.129 |
| AMD | equity | 1.8643 | $418.30 | $779.83 | 1.56% | 1.70% | -0.138 |
| MU | equity | 1.1363 | $676.43 | $768.63 | 1.54% | 1.70% | -0.160 |
| INTC | equity | 6.7931 | $111.83 | $759.71 | 1.52% | 1.70% | -0.178 |
| SNDK | equity | 0.5432 | $1394.37 | $757.37 | 1.51% | 1.70% | -0.183 |

### Orders
| Metric | Value |
|--------|-------|
| Total orders | 22 (22 buys, 0 sells) |
| Total notional | $66,862.25 |
| Estimated turnover | 133.7% |

| Ticker | Action | Delta Shares | Est Price | Notional |
|--------|--------|-------------|-----------|----------|
| AMD | buy | +1.8643 | $455.19 | $848.60 |
| APH | buy | +6.6281 | $128.03 | $848.60 |
| APP | buy | +1.8111 | $468.55 | $848.60 |
| ARES | buy | +6.7216 | $126.25 | $848.60 |
| AXON | buy | +2.1029 | $403.54 | $848.60 |
| COHR | buy | +2.5312 | $335.26 | $848.60 |
| COIN | buy | +4.2185 | $201.16 | $848.60 |
| CVNA | buy | +10.8879 | $77.94 | $848.60 |
| DDOG | buy | +4.2396 | $200.16 | $848.60 |
| EL | buy | +9.8445 | $86.20 | $848.60 |
| EPAM | buy | +8.5518 | $99.23 | $848.60 |
| GLD | buy | +17.3406 | $417.88 | $7,246.30 |
| HOOD | buy | +11.0165 | $77.03 | $848.60 |
| INTC | buy | +6.7931 | $124.92 | $848.60 |
| LITE | buy | +0.9389 | $903.80 | $848.60 |
| MU | buy | +1.1363 | $746.81 | $848.60 |
| NCLH | buy | +49.6838 | $17.08 | $848.60 |
| PLTR | buy | +6.1582 | $137.80 | $848.60 |
| SMCI | buy | +23.9921 | $35.37 | $848.60 |
| SNDK | buy | +0.5432 | $1562.34 | $848.60 |
| UUP | buy | +1545.6307 | $27.59 | $42,643.95 |
| XYZ | buy | +11.3373 | $74.85 | $848.60 |

### Fills & Slippage
| Metric | Value | H-2 Gate (< 20 bps avg) |
|--------|-------|------------------------|
| Trades filled | 22 | — |
| Avg slippage | 449.6 bps | ⚠️ above target |
| Flagged trades (> 30 bps) | 20 / 22 | — |

| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |
|--------|--------|-----------|-------------|-------------|---------|
| AMD | buy | $418.30 | $455.19 | -810.4 | 🚨 |
| APH | buy | $137.58 | $128.03 | +745.9 | 🚨 |
| APP | buy | $494.07 | $468.55 | +544.7 | 🚨 |
| ARES | buy | $123.56 | $126.25 | -213.1 | 🚨 |
| AXON | buy | $431.01 | $403.54 | +680.7 | 🚨 |
| COHR | buy | $325.93 | $335.26 | -278.4 | 🚨 |
| COIN | buy | $185.84 | $201.16 | -761.5 | 🚨 |
| CVNA | buy | $81.03 | $77.94 | +396.5 | 🚨 |
| DDOG | buy | $185.50 | $200.16 | -732.4 | 🚨 |
| EL | buy | $85.72 | $86.20 | -55.7 | 🚨 |
| EPAM | buy | $103.11 | $99.23 | +391.0 | 🚨 |
| GLD | buy | $416.74 | $417.88 | -27.3 | ✅ |
| HOOD | buy | $76.24 | $77.03 | -102.6 | 🚨 |
| INTC | buy | $111.83 | $124.92 | -1047.5 | 🚨 |
| LITE | buy | $915.87 | $903.80 | +133.6 | 🚨 |
| MU | buy | $676.43 | $746.81 | -942.4 | 🚨 |
| NCLH | buy | $17.28 | $17.08 | +117.1 | 🚨 |
| PLTR | buy | $135.87 | $137.80 | -140.4 | 🚨 |
| SMCI | buy | $33.32 | $35.37 | -579.6 | 🚨 |
| SNDK | buy | $1394.37 | $1562.34 | -1075.1 | 🚨 |
| UUP | buy | $27.56 | $27.59 | -10.9 | ✅ |
| XYZ | buy | $75.63 | $74.85 | +104.2 | 🚨 |

### H-Gate Status (running)
| Gate | Metric | Status |
|------|--------|--------|
| H-1 Pipeline reliability | Errors today: 0 | ✅ |
| H-2 Fill slippage | 449.6 bps avg | ⚠️ T=0 artifact |
| H-4 Weight drift | 0.18 pp max | ✅ |
| H-5 RL mode | rl_e7 | ✅ |
| H-7 Drift flags | 0 active | ✅ |

---


