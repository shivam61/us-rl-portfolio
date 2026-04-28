# Beta Decomposition — Momentum + Vol Factor Scores

_Eval: 2016-01-01 – 2026-01-01 | sp100 (44 tickers) | Monthly rebalancing (non-overlapping 21-day) | Wall time: 4s_

## Methodology

For each date in the eval window (sampled every 21 trading days):
- **Long portfolio** = equal-weight top-quintile stocks by score
- **Short portfolio** = equal-weight bottom-quintile stocks by score
- **Long-short (LS)** = long return − short return
- **SPY return** = 21-day forward return from same date

OLS regression: `portfolio_return ~ α + β · SPY_return`
- α (Jensen's alpha) = return unexplained by market exposure
- β = portfolio market loading
- Annualised: multiply by 252/21 ≈ 12×

---

## Regression Results

| Score | Avg long β | Long β | Long α (ann%) | t(α) | Long R² | LS β | LS α (ann%) | t(α) |
|---|---|---|---|---|---|---|---|---|
| score_50_50 | 0.627 | 1.092 | 6.08% | 1.19 | 0.517 | 0.592 | 3.44% | 0.50 |
| momentum_only | 0.513 | 1.130 | 6.55% | 1.32 | 0.549 | 0.497 | 0.46% | 0.06 |
| volatility_only | 0.791 | 1.084 | 16.36% | 3.36 | 0.537 | 0.619 | 11.61% | 1.79 |

> β = portfolio OLS beta vs SPY. α = annualised Jensen's alpha. t(α) > 1.96 → significant at 95%. LS = long-short (top20% − bottom20%).

---

## Avg beta of selected stocks (from `beta_to_spy_63d` feature)

| Score | Avg beta of long stocks | Avg beta of short stocks | L-S beta spread |
|---|---|---|---|
| score_50_50 | 0.627 | 0.629 | -0.002 |
| momentum_only | 0.513 | 0.845 | -0.331 |
| volatility_only | 0.791 | 0.483 | 0.308 |

_Avg beta of long stocks comes directly from the `beta_to_spy_63d` feature — reflects the stocks' realised rolling beta at the time of selection._

---

## Rolling 12-month beta (long-short portfolio)

- **score_50_50**: mean 0.438, min -1.307, max 1.968, std 0.674 (n=115 12m windows)
- **momentum_only**: mean 0.274, min -1.532, max 2.389, std 0.903 (n=115 12m windows)
- **volatility_only**: mean 0.512, min -1.301, max 1.884, std 0.690 (n=115 12m windows)

---

## Conclusion — Is the signal just beta exposure?

### score_50_50

- Long portfolio beta = **1.092** (avg selected stock β = 0.627)
- Long-short beta = **0.592** — significant market loading in the spread
- Long annualised alpha = **6.08%** (t = 1.19)
- Long-short annualised alpha = **3.44%** (t = 0.50)
- **Verdict: Beta-plus-noise — market-like β=1.092 with no significant alpha (t=1.19)**

### momentum_only

- Long portfolio beta = **1.130** (avg selected stock β = 0.513)
- Long-short beta = **0.497** — significant market loading in the spread
- Long annualised alpha = **6.55%** (t = 1.32)
- Long-short annualised alpha = **0.46%** (t = 0.06)
- **Verdict: Beta-plus-noise — market-like β=1.130 with no significant alpha (t=1.32)**

### volatility_only

- Long portfolio beta = **1.084** (avg selected stock β = 0.791)
- Long-short beta = **0.619** — significant market loading in the spread
- Long annualised alpha = **16.36%** (t = 3.36)
- Long-short annualised alpha = **11.61%** (t = 1.79)
- **Verdict: NOT just beta — statistically significant alpha at 95% (long t=3.36, LS t=1.79)**
