# Phase C — LightGBM Hyperparameter Search

> **Navigation:** [← Phase B](phase_b.md) | [← ROADMAP](../ROADMAP.md) | Next: [Phase D →](phase_d.md)

**Objective:** Find the LightGBM configuration that maximises IC Sharpe on the 2019–2026 holdout, using the best feature set and label identified in Phase B.

**Entry gate:** Phase B complete — best (label, top-N, retrain freq, feature set) combo identified.

---

## Success Criteria

| Metric | Target |
|---|---|
| IC Sharpe on 2019–2026 holdout | ≥ 0.50 |
| No overfit signal | IC Sharpe on train window within 20% of holdout |

---

## Iteration Log

| Date | Params | IC Sharpe (holdout) | Notes |
|---|---|---|---|
| — | Not started | — | Waiting on Phase B gate |

---

## Hyperparameter Grid

| Param | Values | Count |
|---|---|---|
| `n_estimators` | 50, 100, 200, 300 | 4 |
| `max_depth` | 3, 5, 7 | 3 |
| `num_leaves` | 15, 31, 63 | 3 |
| `learning_rate` | 0.02, 0.05, 0.1 | 3 |
| `min_child_samples` | 20, 50, 100 | 3 |

**Total:** ~486 combinations. With `joblib.Parallel(n_jobs=32)`: ~32× speedup vs sequential.

---

## Architecture

```
joblib.Parallel(n_jobs=32)
    └── each job: fit LightGBM on train window → evaluate IC Sharpe on holdout
            ├── train: 2008–2018 (walk-forward, 3yr rolling)
            ├── holdout: 2019–2026 (never seen during search)
            └── metric: mean IC Sharpe across holdout dates
```

### Files to build
| File | Status | Notes |
|---|---|---|
| `scripts/run_lgbm_search.py` | ⏳ TODO | Grid search runner |

---

## Design Decisions

| Decision | Rationale |
|---|---|
| Evaluate on IC Sharpe, not CAGR | IC Sharpe measures pure signal quality independent of optimizer/risk choices; CAGR conflates alpha quality with portfolio construction |
| Hold out 2019–2026 strictly | Feature selection (Phase A) and experiment grid (Phase B) both used sp100 2016–2026; Phase C uses a disjoint sp500 2019–2026 window to avoid selection bias |
| joblib not multiprocessing | LightGBM itself is multi-threaded; joblib loky backend handles thread-process interaction more cleanly than Pool for this case |
| Prune early | If after 50 estimators IC Sharpe < 0.15, skip remaining estimator counts for that (max_depth, num_leaves) combo |
