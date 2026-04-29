# Phase A — Feature Engineering & IC Evaluation

> **Navigation:** [← ROADMAP](../ROADMAP.md) | Next: [Phase B →](phase_b.md)

**Objective:** Lift mean Rank IC from 0.033 → ≥ 0.040 and IC Sharpe from 0.086 → ≥ 0.30 by adding differentiated feature families to replace commodity price/momentum factors.

**Current decision:** Phase A is conditionally passed, not fully passed. Mean IC passed, but IC Sharpe remains below the original gate. Do not continue momentum-first research. Use `volatility_score` / `volatility_only` as the current production alpha candidate, keep RL disabled, and run Phase A.1 robustness validation before further optimizer/risk/RL tuning.

---

## Success Criteria

| Metric | Baseline | Best result | Target | Status |
|---|---|---|---|---|
| Mean Rank IC | 0.033 | **0.0500** (vol-only rank) | ≥ 0.040 | ✅ exceeded |
| IC Sharpe | 0.086 | **0.186** (LGBM momentum) | ≥ 0.30 | ❌ below gate — structural at 44 tickers |
| Top-bot spread | 0.19% | **1.64%** (vol-only rank) | ≥ 0.40% | ✅ exceeded |
| Precision@20 | ~10% | **33.6%** (vol-only rank) | ≥ 15% | ✅ exceeded |

---

## Iteration Log

| Date | Family | Label | Mean IC | IC Sharpe | Precision@20 | Top-bot | Conclusion |
|---|---|---|---|---|---|---|---|
| 2026-04-27 | baseline (17 features) | raw_fwd_ret | 0.033 | 0.086 | ~10% | 0.19% | Below gate — commodity factors arbitraged away |
| 2026-04-27 | **momentum** | raw_fwd_ret | **0.0379** | 0.186 | 27.9% | 1.23% | IC gate ✅ met — IC Sharpe still below 0.30 ❌ |
| 2026-04-27 | volatility | raw_fwd_ret | 0.0321 | 0.183 | 28.4% | 0.94% | Strong vol signal, close to momentum |
| 2026-04-27 | baseline | rank_cs | 0.0263 | 0.137 | 25.9% | 2.36% | rank_cs label doesn't help baseline |
| 2026-04-27 | all_new (13 new features) | raw_fwd_ret | 0.0310 | 0.146 | 27.5% | 1.10% | Lower than momentum alone — reversal features diluting signal |
| 2026-04-27 | reversal | raw_fwd_ret | 0.0149 | 0.069 | 26.4% | 0.65% | Weak — reversal alone is noise on monthly horizon |
| 2026-04-27 | reversal | rank_cs | -0.0003 | -0.002 | 23.3% | -0.19% | Negative signal — confirmed: drop from feature set |
| 2026-04-28 | **mom+vol combo (score_50_50)** | raw_fwd_ret | **0.0411** | 0.150 | 28.9% | 1.22% | Exceeds IC gate ✅ — factor directions calibrated empirically (reversal+risk-prem) |
| 2026-04-28 | vol only (risk premium) | raw_fwd_ret | **0.0500** | 0.175 | 33.6% | 1.64% | Strongest raw signal — high-vol/high-beta outperforms in sp100 2016-2026 |
| 2026-04-28 | **momentum_v2_calibrated** | raw_fwd_ret | 0.0271 | 0.097 | 24.7% | 0.97% | 11-feature momentum+stability composite; α_ann=8.9% (t=1.77, 90% sig) — IC below 0.030 gate ❌ |
| 2026-04-28 | **Phase A.1 volatility robustness** | raw_fwd_ret | sp100 0.0379 / sp500 0.0259 | ~0.13 rebalance IC Sharpe | sp500 top-10 hit 37.3% | sp500 1.23% avg spread | High-vol/risk-premium direction survives sp500; low-vol quality rejected; portfolio drawdown remains too high |

**Key insight:** In sp100 2016-2026, cross-sectional REVERSAL (not continuation) dominates, and RISK PREMIUM (not low-vol anomaly) dominates. All momentum return features have negative direct IC; vol/beta features have positive direct IC. Factor scores calibrated to these directions:
- `momentum_score` = buy laggards (reversal, asc=False on all return features)
- `volatility_score` = buy high-risk (risk premium, asc=True for vol/beta, asc=False for max_drawdown)
- `score_50_50` = best combo: IC=0.041, IC Sharpe=0.150, Top-Bot=1.22% — IC gate MET ✅
- IC Sharpe 0.15 vs target 0.30 ❌ — structural constraint at 44 tickers; expect to improve at sp500 scale
- `momentum_v2_calibrated`: 11-feature expanded set gives IC=0.027 (improvement over 0.018 but below 0.030 gate); IC Sharpe=0.097 ❌
- Pure price-momentum factors cannot meet IC Sharpe ≥ 0.20 in sp100 — requires fundamental signal (SUE, revisions) or sp500 scale

## Phase A.1 — Volatility Robustness Validation

**Goal:** decide whether `volatility_score` is real alpha or a sp100 artifact before continuing production optimizer/risk/RL work.

### Required validation

| Dimension | Tests |
|---|---|
| Universes | sp100, sp500, optional `top_200_liquid` if available |
| Time periods | 2006-2009, 2010-2014, 2015-2019, 2020-2022, 2023-2026 |
| Regimes | low VIX, high VIX, crash, recovery, trending, sideways |
| Selection sizes | top 10, top 20, top 30, top 50, sector-balanced top 20, sector-balanced top 50 |
| Directionality | long high-vol rebound/risk-premium vs long low-vol quality |
| Portfolio tests | Top-N equal weight, optimizer no risk, optimizer + risk, SPY, equal-weight universe |

### Success criteria

- Mean IC > 0.03 on sp100.
- Mean IC > 0.02 on sp500 or optional top-200-liquid universe.
- IC positive in most time periods.
- Top-bottom spread > 1% per rebalance on sp100.
- Top-N portfolio beats equal-weight by at least 1.5-2% CAGR, or materially improves Sharpe/drawdown.
- Directionality stable enough to encode.

### Stop condition

If `volatility_score` fails robustness on sp500 and recent periods, stop optimizer/RL tuning and return to feature engineering:
earnings quality, analyst revisions if available, value-quality composite, and regime-conditional factors.

### Implementation

| Step | File | Status |
|---|---|---|
| Phase A.1 robustness runner | `scripts/run_phase_a1_volatility_robustness.py` | ✅ Implemented |
| Main report | `artifacts/reports/phase_a1_volatility_robustness.md` | ✅ Done |
| IC by period | `artifacts/reports/volatility_ic_by_period.csv` | ✅ Done |
| IC by regime | `artifacts/reports/volatility_ic_by_regime.csv` | ✅ Done |
| Selection sweep | `artifacts/reports/volatility_selection_sweep.csv` | ✅ Done |
| Directionality | `artifacts/reports/volatility_directionality.csv` | ✅ Done |
| Portfolio backtests | `artifacts/reports/volatility_portfolio_backtests.csv` | ✅ Done |

### Phase A.1 results

| Check | Result | Decision |
|---|---|---|
| sp100 mean period IC > 0.03 | `0.0379` | ✅ Pass |
| sp500 mean period IC > 0.02 | `0.0259` | ✅ Pass |
| Positive in most periods | sp100 `4/5`, sp500 `5/5` | ✅ Pass |
| sp100 top-bottom spread > 1% | `1.55%` | ✅ Pass |
| sp500 top-bottom spread > 1% | `1.23%` | ✅ Pass |
| Directionality | high-vol positive; low-vol negative in every sp500 period | ✅ Encode high-vol/risk-premium direction |
| Portfolio vs equal weight | sp500 high-vol Top-N beats CAGR but has worse Sharpe/drawdown | ⚠️ Alpha real, expression not production-clean |

**Conclusion:** `volatility_score` is not just a sp100 artifact. The high-vol/risk-premium direction is the correct direction to encode. However, naive Top-N and current optimizer/risk expressions create unacceptable sp500 drawdowns (`-58%` to `-71%` for high-vol variants) and Sharpe below equal-weight. Treat this as a production alpha candidate, not a finished production baseline.

**Pushback:** the next step should not be RL or more momentum work. The next decision is how to express the validated high-vol alpha with controlled beta/crash exposure. If that cannot be solved without destroying the alpha, return to feature engineering: earnings quality, analyst revisions, value-quality composite, and regime-conditional factors.

## Phase A.2 — Portfolio Expression of Volatility Alpha

**Goal:** convert the validated `volatility_score` alpha into an investable portfolio without changing the alpha definition.

**Experiment discipline:**
- Do not remove high-beta stocks from the candidate set.
- Do not disable the alpha in crash regimes.
- Do not add new factors yet.
- Keep RL disabled.
- Use sp100 as the quick development screen and sp500 as the final decision universe.

### Hypothesis

`volatility_score` has real cross-sectional alpha, but naive long-only Top-N portfolios express it as excessive beta/crash exposure. A better construction may preserve the selection edge while reducing drawdown through beta-targeted weights, volatility scaling, explicit SPY hedging, and regime-aware gross exposure.

### Test matrix

| Dimension | Tests |
|---|---|
| Universes | sp100, sp500_dynamic |
| Selection | Top-10, Top-20, Top-30, sector-balanced Top-20, sector-balanced Top-30 |
| Volatility scaling | equal weight, inverse-vol, alpha/vol |
| Beta targeting | target beta 1.0, 0.7, 0.5; long-only, max weight 15% |
| Exposure scaling | crash 0.6, high VIX 0.7, trending 0.9, normal 1.0 |
| Hedge comparison | long-only beta targeting vs explicit SPY hedge |

### Required outputs

| Output | Purpose |
|---|---|
| `artifacts/reports/portfolio_expression_results.md` | Main interpretation and decision |
| `artifacts/reports/beta_targeting_results.csv` | Long-only beta-targeted variants |
| `artifacts/reports/vol_scaling_results.csv` | Equal/inverse-vol/alpha-vol variants |
| `artifacts/reports/hedge_comparison.csv` | Beta-targeting versus SPY hedge variants |

### Success criteria

Find at least one sp500 configuration with:
- MaxDD < 40%.
- Sharpe above equal-weight universe.
- CAGR within 2-3% of simple Top-N equal weight, or materially better Sharpe/drawdown.
- Realized beta reasonably close to target; do not accept a nominal target that the long-only basket cannot actually reach.

### Expected outcome

The most likely investable construction is explicit SPY hedging or beta-targeted weighting plus regime-aware exposure scaling. If no configuration clears the sp500 criteria, conclude the standalone volatility alpha is not directly investable and move to multi-factor blending.

### Phase A.2 results

| Check | Result | Decision |
|---|---|---|
| Best sp500 Sharpe | `0.753` (`sector_balanced_top_20_beta_target_0.7`) vs equal-weight `0.779` | ❌ Fail |
| Best sp500 drawdown-controlled hedge | MaxDD `-35.88%`, CAGR `13.58%`, Sharpe `0.727` | ❌ Drawdown passes, Sharpe/CAGR insufficient |
| Best sp500 CAGR expression | `22.08%` (`top_20_equal_weight_exposure_scaled`) | ⚠️ MaxDD `-52.73%`, Sharpe `0.700` |
| Long-only beta targeting | Realized beta stayed around `0.86-0.87` for target `0.5-0.7` | ❌ Low beta targets not truly reachable |
| Hard gate | MaxDD < 40% and Sharpe > equal-weight | ❌ No sp500 variant passed |

**Conclusion:** Phase A.2 did not find an investable standalone `volatility_score` sleeve. SPY hedging can reduce drawdown, but it gives up too much return and still does not beat equal-weight Sharpe. Long-only beta targeting preserves more return but fails to hit low beta targets and leaves drawdown too high.

**Next decision:** stop standalone volatility-sleeve tuning for now. Keep `volatility_score` as a useful alpha component, but move to multi-factor blending before Phase B/C/RL: combine the validated risk-premium signal with stabilizers such as earnings quality, value-quality, and revisions where available.

## Phase A.3 — Multi-Sleeve Alpha System

**Goal:** build a non-RL multi-sleeve alpha system that separates alpha discovery from portfolio construction.

**Rules:**
- Do not modify `volatility_score`.
- Do not merge quality/value features into the volatility model.
- Do not enable RL.
- Treat each sleeve as an independent portfolio, then blend sleeve weights.

### Sleeve design

| Sleeve | Purpose | Selection |
|---|---|---|
| Sleeve 1: volatility | Existing high-vol/risk-premium return engine | Top-10 and Top-20 equal weight |
| Sleeve 2: defensive quality | Low drawdown and low correlation to volatility sleeve | Sector-balanced Top-30 and Top-50 |

Quality sleeve features:
- `roe` clipped.
- Earnings stability from rolling `eps_growth_yoy` stability.
- Low leverage proxy from low `pb_ratio` because true debt/leverage is not currently available in cached fundamentals.
- Low downside volatility.
- Low max drawdown.
- Return consistency.
- Sector-relative normalization before scoring.

### Blend tests

| Volatility weight | Quality weight |
|---:|---:|
| 0.6 | 0.4 |
| 0.5 | 0.5 |
| 0.7 | 0.3 |
| 0.4 | 0.6 |

### Diagnostics

| Output | Purpose |
|---|---|
| `artifacts/reports/multi_sleeve_results.md` | Main experiment report |
| `artifacts/reports/sleeve_metrics.csv` | Standalone sleeve metrics |
| `artifacts/reports/blend_metrics.csv` | Blend metrics |
| `artifacts/reports/correlation_matrix.csv` | Full, rolling, and crisis vol-quality correlations |
| `artifacts/reports/overlap_report.csv` | Ticker and sector overlap |

### Success criteria

Proceed only if a sp500 blend reaches:
- CAGR >= equal-weight.
- Sharpe > equal-weight.
- MaxDD < 40%.
- Vol-quality correlation < 0.5.

If successful, proceed to optimizer integration, improved risk engine, then RL. If it fails, return to feature engineering for the defensive sleeve.

### Phase A.3 results

Artifacts:
- `artifacts/reports/multi_sleeve_results.md`
- `artifacts/reports/sleeve_metrics.csv`
- `artifacts/reports/blend_metrics.csv`
- `artifacts/reports/correlation_matrix.csv`
- `artifacts/reports/overlap_report.csv`

| Check | sp100 result | sp500 result | Decision |
|---|---:|---:|---|
| Equal-weight universe benchmark | CAGR `16.20%`, Sharpe `0.830`, MaxDD `-43.18%` | CAGR `16.49%`, Sharpe `0.779`, MaxDD `-49.12%` | Comparison baseline |
| Best quality sleeve | CAGR `16.82%`, Sharpe `0.897`, MaxDD `-39.43%` | CAGR `9.82%`, Sharpe `0.555`, MaxDD `-48.42%` | Defensive sleeve does not generalize |
| Best sp500 blend Sharpe | n/a | Sharpe `0.698`, CAGR `19.41%`, MaxDD `-53.53%` | ❌ Below equal-weight Sharpe and drawdown gate |
| Best sp500 blend CAGR | n/a | CAGR `22.80%`, Sharpe `0.606`, MaxDD `-69.68%` | ❌ Return comes with unacceptable drawdown |
| Vol-quality correlation | `0.877` to `0.967` | `0.633` to `0.708` | ❌ Fails `<0.5` independence gate |
| Crisis correlation | `0.922` to `0.980` | `0.728` to `0.798` | ❌ Diversification weakens when needed most |
| Ticker overlap | `51.8%` to `100%` | `0.04%` to `1.57%` | Low sp500 overlap, but common market/risk exposure remains |

**Conclusion:** Phase A.3 failed the sp500 decision gate. The multi-sleeve structure is implemented correctly and kept `volatility_score` unchanged, but the first defensive quality sleeve is not independent enough and does not stabilize the system. On sp500, blends preserve high CAGR but still miss equal-weight Sharpe, fail MaxDD `<40%`, and remain too correlated with volatility alpha.

**Decision:** do not proceed to optimizer integration, improved risk engine, or RL from this A.3 blend. Keep `volatility_score` as Sleeve 1, but return to feature engineering for Sleeve 2. The next defensive sleeve needs stronger non-price fundamentals such as true leverage/debt, earnings quality/accruals, profitability persistence, value-quality composite, and analyst revisions if available. Avoid relying mainly on price-risk features for the defensive sleeve because they leave the sleeve tied to the same market stress exposure.

---

## Phase A.4 — Defensive Stability Sleeve With Beta Targeting

**Goal:** create a more orthogonal Sleeve 2 by changing the economic exposure from growth/quality to stability/survivability and by enforcing beta control inside the defensive sleeve.

**Rules:**
- Do not modify `volatility_score`.
- Do not merge defensive features into the volatility model.
- Do not enable RL.
- Avoid the trap `quality_score = ROE + momentum + growth`; that becomes growth/high-beta exposure.
- Apply beta targeting inside the defensive sleeve, not only at the final blend layer.

### Implementation

| Component | Design |
|---|---|
| Runner | `scripts/run_phase_a4_defensive_sleeve.py` |
| Sleeve 1 | Existing `volatility_score`, Top-10 and Top-20 equal weight |
| Sleeve 2 score | `defensive_stability_score` |
| Defensive selection | Sector-balanced Top-30 and Top-50 |
| Defensive beta targets | Equal weight, target beta `0.6`, target beta `0.8` |
| Blends | `60/40`, `50/50`, `70/30`, `40/60` |

Defensive score ingredients use only currently available point-in-time features:
- Profitability survival from clipped `roe`.
- Profitability stability from rolling ROE stability.
- Earnings stability and downside EPS survival from `eps_growth_yoy`.
- Valuation buffer from `pe_ratio` and `pb_ratio`.
- Low downside volatility and low max drawdown.
- Beta survivability around target beta `0.65`.
- Return stability around steady positive-day frequency.

### Data availability

| Data family | sp100 | sp500 | Decision |
|---|---:|---:|---|
| ROE / PE / PB / EPS growth | `91.6%` to `96.5%` coverage on sp100 | only `8.0%` to `8.5%` coverage on sp500 | Insufficient for sp500 defensive sleeve |
| Price risk / beta / stability | `96.7%` to `98.8%` coverage on sp100 | `90.5%` to `98.8%` coverage on sp500 | Usable but not independent alpha |
| Debt, leverage, interest coverage | `0%` | `0%` | Missing |
| Cash-flow accruals, gross margin | `0%` | `0%` | Missing |
| Analyst revisions | `0%` | `0%` | Missing |

### Phase A.4 results

Artifacts:
- `artifacts/reports/phase_a4_defensive_sleeve_results.md`
- `artifacts/reports/phase_a4_sleeve_metrics.csv`
- `artifacts/reports/phase_a4_blend_metrics.csv`
- `artifacts/reports/phase_a4_correlation_matrix.csv`
- `artifacts/reports/phase_a4_overlap_report.csv`
- `artifacts/reports/phase_a4_data_availability.csv`

| Check | sp100 result | sp500 result | Decision |
|---|---:|---:|---|
| Defensive beta targeting mechanics | Target `0.6` realized `0.604` to `0.606` | Target `0.6` realized `0.601` to `0.603` | Pass mechanically |
| Best defensive sleeve | CAGR `17.02%`, Sharpe `0.901`, MaxDD `-42.13%` | CAGR `8.51%`, Sharpe `0.487`, MaxDD `-48.78%` | Does not generalize |
| Best beta-targeted defensive sleeve | CAGR `13.15%`, Sharpe `0.828`, MaxDD `-39.60%` | CAGR `7.50%`, Sharpe `0.468`, MaxDD `-47.17%` | Beta lower, alpha too weak |
| Best sp500 blend Sharpe | n/a | Sharpe `0.694`, CAGR `18.29%`, MaxDD `-53.51%` | Fails equal-weight Sharpe `0.779` |
| Best sp500 blend drawdown | n/a | MaxDD `-50.49%`, CAGR `16.37%`, Sharpe `0.685` | Fails MaxDD `<40%` |
| Best sp500 vol-defensive correlation | n/a | full corr `0.563`, crisis corr `0.645` | Improved but fails `<0.5` / `<0.6` gates |

**Conclusion:** A.4 confirms the critique: beta-neutralization is necessary, but not sufficient. It materially reduces correlation versus A.3, especially for `vol_top_10` with beta-target `0.6`, but the current defensive sleeve still lacks enough independent economic alpha on sp500. The core blocker is data, not blend math: sp500 fundamental coverage for ROE/PE/PB/EPS growth is only about `8%`, and the real defensive fields needed for survivability are unavailable.

**Decision:** do not proceed to optimizer integration, improved risk engine, or RL. Keep `volatility_score` as Sleeve 1 and keep the beta-targeted defensive-sleeve machinery, but pause further sleeve-blend tuning until the data layer supports true orthogonal fundamentals.

**Next logical work:** Phase A.5 should be a data-layer and feature-layer upgrade for orthogonal economic exposure:
1. Add point-in-time balance sheet and cash-flow fields: debt/equity, debt/assets, interest coverage, operating cash flow, accruals, gross margin, asset turnover.
2. Add analyst revisions or earnings surprise data if available.
3. Rebuild Defensive Sleeve v3 from survivability, balance-sheet strength, cash-flow quality, and valuation buffer.
4. Retest A.4 beta-targeted construction only after sp500 fundamental coverage is adequate.

---

## Feature Families

### Baseline (17 features — already existed)
`ret_1m`, `ret_3m`, `ret_6m`, `ret_12m`, `ret_12m_ex_1m`, `above_50dma`, `above_200dma`, `ma_50_200_ratio`, `price_to_52w_high`, `volatility_21d`, `volatility_63d`, `downside_vol_63d`, `max_drawdown_63d`, `avg_dollar_volume_63d`, `beta_to_spy_63d`, `relative_strength_vs_spy_63d`, `liquidity_rank`

### Reversal (6 new — contrarian signal, negative alpha expected)
| Feature | Definition |
|---|---|
| `ret_1w` | 5-day return |
| `ret_2w` | 10-day return |
| `ret_zscore_21d` | zscore of daily returns over 21d |
| `overextension_20dma` | price / 20dma − 1 |
| `rsi_proxy` | 14-day RSI via Wilder EWM |
| `gap_overnight` | open / prev_close − 1 |

### Quality Momentum (7 new — skip-last-week + risk-adjusted)
| Feature | Definition |
|---|---|
| `ret_3m_ex_1w` | ret_3m − ret_1w |
| `ret_6m_ex_1m` | ret_6m − ret_1m |
| `ret_3m_adj` | ret_3m / realized_vol_63d |
| `ret_6m_adj` | ret_6m / realized_vol_63d |
| `mom_stability_3m` | fraction of positive days in 63d window |
| `trend_consistency` | sign(ret_3m) == sign(ret_6m) |
| `sector_rel_momentum_3m` | ret_3m − sector median ret_3m (computed post-stack) |

### Labels (3)
| Label | Definition | Use case |
|---|---|---|
| `target_fwd_ret` | raw 21-day forward return | baseline |
| `target_rank_cs` | cross-sectional rank [0,1] within date | cleaner, less beta contamination |
| `target_fwd_ret_sector_rel` | fwd_ret − sector mean fwd_ret | pure stock selection signal |

---

## Implementation

| Step | File | Status |
|---|---|---|
| ResearchConfig | `src/config/loader.py` | ✅ Done |
| New labels | `src/labels/targets.py` | ✅ Done |
| Reversal features | `src/features/stock_features.py` | ✅ Done |
| Momentum features | `src/features/stock_features.py` | ✅ Done |
| sector_mapping wiring | `scripts/build_features.py` | ✅ Done |
| IC eval script | `scripts/run_alpha_research.py` | ✅ Done |
| Rebuild features parquet | `scripts/build_features.py` | ✅ Done (30 features, 58 tickers, 5109 dates) |
| Run IC eval | `scripts/run_alpha_research.py` | ✅ Done (21.8s) — results in `artifacts/reports/feature_family_ic.md` |
| Run momentum+vol combo | `scripts/run_momentum_vol_combo.py` | ✅ Done — results in `artifacts/reports/momentum_vol_combo.md` |

### Run commands
```bash
# Rebuild features (already done)
.venv/bin/python scripts/build_features.py \
  --config config/base.yaml --universe config/universes/sp100.yaml

# IC eval (running)
.venv/bin/python scripts/run_alpha_research.py \
  --config config/base.yaml --universe config/universes/sp100.yaml

# Results
cat artifacts/reports/feature_family_ic.md
```

---

## Design Decisions

| Decision | What was rejected | Rationale |
|---|---|---|
| Use all 3 labels in IC eval | Eval only raw fwd_ret | rank_cs removes market-beta noise; sector_rel isolates stock selection — running all three costs nothing with parallelism |
| joblib.Parallel for IC eval | Sequential loop | 15 jobs × ~2min each = 30min sequential → ~4min parallel on 32 cores |
| Wilder EWM for RSI | Simple rolling avg | Wilder smoothing is the standard definition; avoids look-back window edge effects |
| sector_rel_momentum_3m computed post-stack | Wide matrix computation | Requires panel-level groupby — more natural after stacking to (date, ticker) index |
| sp100 for Phase A research | sp500 | sp100 (44 tickers) is 10× faster per backtest; sp500 used only for final gate validation |

---

## If Phase A Gate Not Met

In priority order:
1. Switch primary label to `target_rank_cs` — reduces market-beta contamination
2. Add quality fundamentals: gross profit margin, asset turnover, ROE (already in parquet via `FundamentalFeatureGenerator`)
3. Try `LGBMRanker` with per-date group structure (drop-in in `src/models/stock_ranker.py`)
4. Add earnings surprise (SUE) and analyst revision features
5. Increase training window from 3yr to 5yr for more signal stability
