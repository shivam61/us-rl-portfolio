# Phase A — Feature Engineering & IC Evaluation

> **Navigation:** [← ROADMAP](../ROADMAP.md) | Next: [Phase B →](phase_b.md)

**Objective:** Lift mean Rank IC from 0.033 → ≥ 0.040 and IC Sharpe from 0.086 → ≥ 0.30 by adding differentiated feature families to replace commodity price/momentum factors.

---

## Success Criteria

| Metric | Baseline | Target | Status |
|---|---|---|---|
| Mean Rank IC | 0.033 | ≥ 0.040 | 🔄 eval running |
| IC Sharpe | 0.086 | ≥ 0.30 | 🔄 eval running |
| Top-bot spread | 0.19% | ≥ 0.40% | 🔄 eval running |
| Precision@20 | ~10% | ≥ 15% | 🔄 eval running |

---

## Iteration Log

| Date | Change | Mean IC | IC Sharpe | Top-bot | Conclusion |
|---|---|---|---|---|---|
| 2026-04-27 | Baseline (17 features, raw fwd_ret label) | 0.033 | 0.086 | 0.19% | Below gate — root cause: commodity factors arbitraged away |
| 2026-04-27 | +6 reversal +7 momentum features (30 total), all 3 labels | TBD | TBD | TBD | Running — `scripts/run_alpha_research.py` |

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
| Run IC eval | `scripts/run_alpha_research.py` | 🔄 Running |

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
