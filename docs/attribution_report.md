# Phase H — Weekly Attribution Report

> Generated from real prices in `data/raw/`. Updated each time `generate_attribution_report.py` runs.
>
> **Framework:**
> - **Equity contribution** = sleeve return × equity weight
> - **Trend contribution** = weighted return of TLT/GLD/UUP × trend weight
> - **RL allocation effect** = actual portfolio return − B.5 counterfactual return
>   (same assets, B.5 sleeve weights at same stress level)
> - **Stock selection effect** = (equity basket return − SPY) × equity weight
>   (basket is fixed 20-name equal-weight universe; measures quality of the universe pick, not rebalance decisions)

---
## Attribution Summary — All Periods

| Period | Eq contrib | Trend contrib | Cash | RL vs B.5 | Stock sel | Total | SPY |
|--------|-----------|--------------|------|-----------|-----------|-------|-----|
| R1 2026-05-26→2026-06-09 | +0.33% | +0.24% | +0.00% | -0.14% | +1.07% | +0.57% | -2.06% |
| R2 2026-06-09→2026-06-23 | +0.36% | +0.92% | +0.00% | -0.08% | +0.42% | +1.28% | -0.21% |
| R3 2026-06-23→2026-07-07 | +0.32% | -1.14% | +0.00% | -0.76% | -0.16% | -0.82% | +1.93% |
| R4 2026-07-07→2026-07-21 | -0.41% | -0.57% | +0.00% | -0.02% | -0.45% | -0.98% | +0.08% |

**Cumulative RL return (T=0 → R5 entry):** +1.46%  
**Cumulative SPY return:** +2.10%  
**Active return vs SPY:** -0.65%

### R1 — 2026-05-26 → 2026-06-09

**Stress score at entry:** 0.238 | **Equity:** 35.9% | **Trend:** 57.6% | **Cash:** 6.5%

#### Return Attribution

| Component | Return | Weight | Contribution |
|-----------|--------|--------|--------------|
| Equity sleeve (20 stocks, equal-wt) | +0.92% | 35.9% | **+0.33%** |
| Trend sleeve (TLT: +0.42%) | +0.42% | 57.6% | **+0.24%** |
| Cash | +0.00% | 6.5% | **+0.00%** |
| **Total portfolio return** | | | **+0.57%** |
| SPY benchmark | -2.06% | — | — |

#### Decision Decomposition

| Effect | Value | Interpretation |
|--------|-------|---------------|
| RL allocation vs B.5 | -0.14% | ❌ RL held 36% eq vs B.5 ~58% eq |
| Stock selection vs SPY | +1.07% | ✅ Basket +0.92% vs SPY -2.06% |
| B.5 counterfactual return | +0.71% | B.5 would: 58% eq / 42% trend |

#### Equity Sleeve: Top & Bottom 3

| Rank | Ticker | Return | Contribution to equity sleeve |
|------|--------|--------|-------------------------------|
| 🟢 Best | AXON | +17.44% | +0.87% |
| 🟢 Best | HOOD | +13.07% | +0.65% |
| 🟢 Best | NCLH | +11.29% | +0.56% |
| 🔴 Worst | COIN | -13.62% | -0.68% |
| 🔴 Worst | INTC | -12.63% | -0.63% |
| 🔴 Worst | LITE | -9.78% | -0.49% |

---
### R2 — 2026-06-09 → 2026-06-23

**Stress score at entry:** 0.430 | **Equity:** 25.0% | **Trend:** 72.3% | **Cash:** 2.7%

#### Return Attribution

| Component | Return | Weight | Contribution |
|-----------|--------|--------|--------------|
| Equity sleeve (20 stocks, equal-wt) | +1.45% | 25.0% | **+0.36%** |
| Trend sleeve (TLT: +1.27%) | +1.27% | 72.3% | **+0.92%** |
| Cash | +0.00% | 2.7% | **+0.00%** |
| **Total portfolio return** | | | **+1.28%** |
| SPY benchmark | -0.21% | — | — |

#### Decision Decomposition

| Effect | Value | Interpretation |
|--------|-------|---------------|
| RL allocation vs B.5 | -0.08% | ❌ RL held 25% eq vs B.5 ~52% eq |
| Stock selection vs SPY | +0.42% | ✅ Basket +1.45% vs SPY -0.21% |
| B.5 counterfactual return | +1.37% | B.5 would: 52% eq / 48% trend |

#### Equity Sleeve: Top & Bottom 3

| Rank | Ticker | Return | Contribution to equity sleeve |
|------|--------|--------|-------------------------------|
| 🟢 Best | HOOD | +23.25% | +1.16% |
| 🟢 Best | INTC | +22.57% | +1.13% |
| 🟢 Best | SNDK | +19.26% | +0.96% |
| 🔴 Worst | EPAM | -19.61% | -0.98% |
| 🔴 Worst | SMCI | -18.01% | -0.90% |
| 🔴 Worst | PLTR | -11.64% | -0.58% |

---
### R3 — 2026-06-23 → 2026-07-07

**Stress score at entry:** 0.418 | **Equity:** 25.0% | **Trend:** 73.5% | **Cash:** 1.5%

#### Return Attribution

| Component | Return | Weight | Contribution |
|-----------|--------|--------|--------------|
| Equity sleeve (20 stocks, equal-wt) | +1.30% | 25.0% | **+0.32%** |
| Trend sleeve (TLT: -1.55%) | -1.55% | 73.5% | **-1.14%** |
| Cash | +0.00% | 1.5% | **+0.00%** |
| **Total portfolio return** | | | **-0.82%** |
| SPY benchmark | +1.93% | — | — |

#### Decision Decomposition

| Effect | Value | Interpretation |
|--------|-------|---------------|
| RL allocation vs B.5 | -0.76% | ❌ RL held 25% eq vs B.5 ~52% eq |
| Stock selection vs SPY | -0.16% | ❌ Basket +1.30% vs SPY +1.93% |
| B.5 counterfactual return | -0.06% | B.5 would: 52% eq / 48% trend |

#### Equity Sleeve: Top & Bottom 3

| Rank | Ticker | Return | Contribution to equity sleeve |
|------|--------|--------|-------------------------------|
| 🟢 Best | AXON | +47.90% | +2.39% |
| 🟢 Best | EPAM | +16.47% | +0.82% |
| 🟢 Best | DDOG | +16.43% | +0.82% |
| 🔴 Worst | SMCI | -21.22% | -1.06% |
| 🔴 Worst | SNDK | -17.62% | -0.88% |
| 🔴 Worst | COHR | -17.60% | -0.88% |

---
### R4 — 2026-07-07 → 2026-07-21

**Stress score at entry:** 0.167 | **Equity:** 46.2% | **Trend:** 53.8% | **Cash:** 0.0%

#### Return Attribution

| Component | Return | Weight | Contribution |
|-----------|--------|--------|--------------|
| Equity sleeve (20 stocks, equal-wt) | -0.89% | 46.2% | **-0.41%** |
| Trend sleeve (TLT: -1.05%) | -1.05% | 53.8% | **-0.57%** |
| Cash | +0.00% | 0.0% | **+0.00%** |
| **Total portfolio return** | | | **-0.98%** |
| SPY benchmark | +0.08% | — | — |

#### Decision Decomposition

| Effect | Value | Interpretation |
|--------|-------|---------------|
| RL allocation vs B.5 | -0.02% | ❌ RL held 46% eq vs B.5 ~60% eq |
| Stock selection vs SPY | -0.45% | ❌ Basket -0.89% vs SPY +0.08% |
| B.5 counterfactual return | -0.95% | B.5 would: 60% eq / 40% trend |

#### Equity Sleeve: Top & Bottom 3

| Rank | Ticker | Return | Contribution to equity sleeve |
|------|--------|--------|-------------------------------|
| 🟢 Best | LITE | +19.84% | +0.99% |
| 🟢 Best | COIN | +7.55% | +0.38% |
| 🟢 Best | AMD | +5.49% | +0.27% |
| 🔴 Worst | AXON | -20.19% | -1.01% |
| 🔴 Worst | APP | -18.81% | -0.94% |
| 🔴 Worst | HOOD | -5.79% | -0.29% |

---