# Phase A — Alpha Improvement Plan

> **Phase B, C, D and full roadmap:** see [docs/ROADMAP.md](ROADMAP.md).  
> This file contains the detailed Phase A implementation spec only.
**Machine:** n2-highmem-32 · 32 vCPUs (Intel Xeon @ 2.80GHz, 2 threads/core) · 31GB RAM  
**Last updated:** 2026-04-27

---

## Why We're Here

Current alpha IC = 0.033 (Rank IC), IC Sharpe = 0.086. Both are below usable thresholds.  
The 21 existing features are commodity price/momentum factors — heavily arbitraged since the 1990s.  
Goal: lift IC to ≥ 0.04, IC Sharpe to ≥ 0.3 by adding genuinely differentiated signal families.

---

## Parallelization Strategy (32 cores)

| Layer | How | Expected speedup |
|---|---|---|
| LightGBM training | `n_jobs=-1` → now uses 32 cores | ~4x vs 8 cores |
| Feature family IC (run_alpha_research.py) | `joblib.Parallel(n_jobs=-1)` across families | ~8x (8 families) |
| Parallel backtests (run_diagnostics.py) | `multiprocessing.Pool(processes=8)` | 8 experiments simultaneously |
| Hyperparameter search | `joblib.Parallel(n_jobs=-1)` across grid | ~32x vs sequential |
| Feature building | Vectorized pandas already; no change needed | — |

Rule: always pass `n_jobs=-1` to LightGBM. Always use `joblib.Parallel` for experiment loops.

---

## Phase A — Implementation Steps

### Step 1: Config layer (src/config/loader.py)
Add `ResearchConfig` dataclass:
```python
class ResearchConfig(BaseModel):
    research_universe: str = "config/universes/sp100.yaml"
    diagnostic_universe: str = "config/universes/sp500.yaml"
```
Wire into `BaseConfig` as `research: ResearchConfig = ResearchConfig()`.

### Step 2: Labels (src/labels/targets.py)
Add alongside existing `target_fwd_ret`:
- `target_rank_cs` — cross-sectional rank [0,1] of fwd_ret within each date
- `target_fwd_ret_sector_rel` — fwd_ret minus mean fwd_ret of same-sector stocks

Both require `sector_mapping: dict` parameter on `TargetGenerator`.

### Step 3: Reversal features (src/features/stock_features.py)
New feature family: **short-term reversal** (contrarian signal, negative alpha expected)
| Feature | Definition | Why |
|---|---|---|
| `ret_1w` | 5-day return | Microstructure reversal |
| `ret_2w` | 10-day return | Short-term mean reversion |
| `ret_zscore_21d` | zscore of daily ret over 21d | Normalized price pressure |
| `overextension_20dma` | (price / 20dma) − 1 | Distance from trend |
| `rsi_proxy` | 14-day RSI approx | Overbought/oversold |
| `gap_overnight` | open/prev_close − 1 | Overnight sentiment |

### Step 4: Improved momentum features (src/features/stock_features.py)
New feature family: **quality momentum** (replaces raw ret_12m)
| Feature | Definition | Why |
|---|---|---|
| `ret_3m_ex_1w` | ret_3m minus ret_1w | Skip-last-week momentum |
| `ret_6m_ex_1m` | ret_6m minus ret_1m | Medium-term skip |
| `ret_3m_adj` | ret_3m / realized_vol_63d | Risk-adjusted momentum |
| `ret_6m_adj` | ret_6m / realized_vol_63d | Risk-adjusted 6m |
| `mom_stability_3m` | frac of positive days in 63d | Consistency of uptrend |
| `trend_consistency` | ret_3m sign matches ret_6m sign | Momentum alignment |
| `sector_rel_momentum_3m` | ret_3m minus sector median ret_3m | Alpha within sector |

### Step 5: Feature building (scripts/build_features.py)
Pass `sector_mapping=dict(universe_config.tickers)` to both:
- `StockFeatureGenerator(sector_mapping=...)`
- `TargetGenerator(sector_mapping=...)`

### Step 6: Alpha research script (scripts/run_alpha_research.py)
Evaluate each feature family independently. Output: `artifacts/reports/feature_family_ic.csv`.

**Architecture:**
```
For each label type (raw, rank_cs, sector_rel):
  For each feature family (momentum, reversal, volume, volatility, ...):
    [PARALLEL] Walk-forward IC eval on sp100 (2016–2026, annual retrain)
    → mean IC, IC Sharpe, Precision@20, top-minus-bottom spread
Output ranked table + summary markdown
```

---

## Phase B — Experiment Matrix (parallel grid)
*Run after Phase A features are validated.*

With 32 cores, run all combinations simultaneously:

| Dimension | Values |
|---|---|
| Universe | sp100 (fast), sp500 (stress) |
| Label type | raw_fwd_ret, rank_cs, sector_rel |
| Top-N selection | 30, 50, 75 |
| Retrain frequency | 1 (always), 3 (current), 6 |
| Feature set | baseline (21 features), +reversal, +momentum, full |

→ ~72 combinations × ~15 min each = would take 18h sequential.  
With `Pool(processes=8)`: ~2.2h wall-clock.

Script: `scripts/run_experiment_grid.py` (Phase B).

---

## Phase C — LightGBM Hyperparameter Search
*Run after best feature set is identified.*

Grid:
| Param | Values |
|---|---|
| n_estimators | 50, 100, 200, 300 |
| max_depth | 3, 5, 7 |
| num_leaves | 15, 31, 63 |
| learning_rate | 0.02, 0.05, 0.1 |
| min_child_samples | 20, 50, 100 |

Evaluation metric: IC Sharpe on 2019–2026 holdout (not seen during feature selection).

With 32 cores: `joblib.Parallel(n_jobs=32)` across all combinations.  
Script: `scripts/run_lgbm_search.py` (Phase C).

---

## Success Criteria

| Metric | Current | Phase A target | Phase B target |
|---|---|---|---|
| Mean Rank IC | 0.033 | ≥ 0.040 | ≥ 0.050 |
| IC Sharpe | 0.086 | ≥ 0.30 | ≥ 0.50 |
| Top-bot spread | 0.19% | ≥ 0.40% (covers 30bps TC) | ≥ 0.60% |
| Precision@20 | ~10% | ≥ 15% | ≥ 20% |

---

## Governance

- All research uses sp100 (fast iteration). sp500 only for final validation.
- No feature may use data after `signal_date - 25 days` (leakage rule).
- All new features must pass a PIT audit: `assert df.groupby('date').apply(check_no_future_leak).all()`
- Commit features parquet + IC report together: `git add artifacts/ data/features/ && git commit`
- Rebuild features after any stock_features.py change: `make features` (or see Useful Commands).

---

## Status

| Step | Status | Notes |
|---|---|---|
| config/base.yaml research flags | ✅ Done | research_universe + diagnostic_universe |
| src/config/loader.py ResearchConfig | ✅ Done | Already present |
| src/labels/targets.py new labels | ✅ Done | target_rank_cs + target_fwd_ret_sector_rel |
| src/features/stock_features.py reversal | ✅ Done | ret_1w/2w, ret_zscore_21d, overextension_20dma, rsi_proxy, gap_overnight |
| src/features/stock_features.py momentum | ✅ Done | ret_3m/6m_ex, ret_3m/6m_adj, mom_stability_3m, trend_consistency, sector_rel_momentum_3m |
| scripts/build_features.py sector_mapping | ✅ Done | Wired to both StockFeatureGenerator + TargetGenerator |
| scripts/run_alpha_research.py | ✅ Done | Walk-forward IC eval, joblib parallel, 5 families × 3 labels |
| rebuild features parquet | ⏳ Pending | Run: .venv/bin/python scripts/build_features.py --config config/base.yaml --universe config/universes/sp100.yaml |
| run IC evaluation | ⏳ Pending | Run: .venv/bin/python scripts/run_alpha_research.py |
| Phase B experiment grid | ⏳ Pending | After IC ≥ 0.04 |
| Phase C hyperparameter search | ⏳ Pending | After best features known |
