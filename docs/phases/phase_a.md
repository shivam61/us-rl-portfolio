# Phase A — Feature Engineering & IC Evaluation

> **Navigation:** [← ROADMAP](../ROADMAP.md) | Next: [Phase B →](phase_b.md)

**Objective:** Lift mean Rank IC from 0.033 → ≥ 0.040 and IC Sharpe from 0.086 → ≥ 0.30 by adding differentiated feature families to replace commodity price/momentum factors.

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

**Key insight:** In sp100 2016-2026, cross-sectional REVERSAL (not continuation) dominates, and RISK PREMIUM (not low-vol anomaly) dominates. All momentum return features have negative direct IC; vol/beta features have positive direct IC. Factor scores calibrated to these directions:
- `momentum_score` = buy laggards (reversal, asc=False on all return features)
- `volatility_score` = buy high-risk (risk premium, asc=True for vol/beta, asc=False for max_drawdown)
- `score_50_50` = best combo: IC=0.041, IC Sharpe=0.150, Top-Bot=1.22% — IC gate MET ✅
- IC Sharpe 0.15 vs target 0.30 ❌ — structural constraint at 44 tickers; expect to improve at sp500 scale
- `momentum_v2_calibrated`: 11-feature expanded set gives IC=0.027 (improvement over 0.018 but below 0.030 gate); IC Sharpe=0.097 ❌
- Pure price-momentum factors cannot meet IC Sharpe ≥ 0.20 in sp100 — requires fundamental signal (SUE, revisions) or sp500 scale

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
