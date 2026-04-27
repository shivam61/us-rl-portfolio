# Phase B — Experiment Matrix

> **Navigation:** [← Phase A](phase_a.md) | [← ROADMAP](../ROADMAP.md) | Next: [Phase C →](phase_c.md)

**Objective:** Identify the best combination of (label type, top-N stocks, retrain frequency, feature set) using a parallel grid search across full walk-forward backtests.

**Entry gate:** Phase A complete — Mean Rank IC ≥ 0.040, IC Sharpe ≥ 0.30

---

## Success Criteria

| Metric | Target |
|---|---|
| Best config identified | top-N, label type, retrain freq, feature set |
| CAGR vs EW baseline | ≥ 14% (beat 12.9% EW by meaningful margin) |
| Sharpe vs EW baseline | ≥ 0.75 |
| IC Sharpe on winning config | ≥ 0.40 |

---

## Iteration Log

| Date | Config | CAGR | Sharpe | IC Sharpe | Notes |
|---|---|---|---|---|---|
| — | Not started | — | — | — | Waiting on Phase A gate |

---

## Experiment Grid

| Dimension | Values | Count |
|---|---|---|
| Universe | sp100 (fast), sp500 (stress) | 2 |
| Label type | raw_fwd_ret, rank_cs, sector_rel | 3 |
| Top-N selection | 30, 50, 75 | 3 |
| Retrain frequency (months) | 1, 3, 6 | 3 |
| Feature set | baseline, +reversal, +momentum, full | 4 |

**Total:** ~72 combinations × ~15 min each = 18h sequential → **~2.2h with Pool(processes=8)**

---

## Architecture

```
multiprocessing.Pool(processes=8)
    └── each worker: full walk-forward backtest (2008–2026)
            ├── own copy of config (no shared state)
            ├── feature set from config/feature_sets.yaml
            └── writes result atomically to shared CSV
```

### Files to build
| File | Status | Notes |
|---|---|---|
| `scripts/run_experiment_grid.py` | ⏳ TODO | Main grid runner |
| `config/feature_sets.yaml` | ⏳ TODO | Named feature subsets |

### Pre-requisites before running
- [ ] Verify `walk_forward.py` has no hardcoded feature column lists
- [ ] Create `config/feature_sets.yaml` with 4 named feature subsets
- [ ] Rebuild sp500 features parquet with 30 new features

---

## Design Decisions

| Decision | Rationale |
|---|---|
| Pool(processes=8) not Pool(32) | Each backtest uses LightGBM with n_jobs=-1 (32 threads); 8 processes × 32 threads = 256 logical workers — saturates machine without thrashing |
| sp100 for fast combos, sp500 for stress | Don't waste 15min sp500 runs on clearly losing configs; run sp100 first, promote top-10 to sp500 |
| Atomic result writes | Partial failures don't corrupt the output CSV |
| Evaluate on 2019–2026 holdout only | Training window is 2008–2018; holdout is never seen during grid search |
