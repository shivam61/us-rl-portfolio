# Session Handoff — Deep Context

Last updated: 2026-04-27T12:39:04

---

## Active Job
| Field | Value |
|---|---|
| Script | `scripts/run_diagnostics.py` |
| PID | 2634 |
| Log | `/tmp/diag_run.log` |
| Config | `config/base.yaml` + `config/universes/sp500.yaml` |
| Compare | `config/universes/sp100.yaml` |
| Status | Experiment 8/8 (sp100 comparison) — ~1,500 rebalances done |
| Output | `data/artifacts/reports/universe_expansion_results.md` (writes on completion) |

Check progress: `grep -c "Rebalancing:" /tmp/diag_run.log && grep "Signal Date" /tmp/diag_run.log | tail -1`

---

## Experiment Chain

### Session 1 (prior)
- Built initial pipeline: data ingestion → features → LightGBM ranker → MVO optimizer → risk engine → simulator
- **sp100 universe (44 tickers), 2006–2026**
- Initial ablation showed Sharpe 1.86 — **INVALID** (simulator MtM tautology bug: NAV only changed 10.4% of days)

### Session 2 (this session)
**Bug fixes:**
1. `src/backtest/simulator.py` — Explicit `self.cash` tracking. Old code: `cash = nav*(1-invested_weight)` → `nav = port_value + cash = nav` (no-op). Fix: cash decremented per trade.
2. `src/backtest/walk_forward.py` — `targets.reindex(X_train.index)` instead of `targets.loc[X_train.index]` — prevented KeyError on pre-IPO (date, ticker) pairs for post-2017 stocks (PLTR, ABNB, DASH, etc.)
3. `src/features/fundamental_features.py` — datetime64[ms] vs datetime64[us] mismatch in `merge_asof`
4. `scripts/build_pit_universe.py` — NYSE trading calendar via `pandas_market_calendars` instead of `freq='B'` (excluded actual market holidays)
5. `scripts/run_diagnostics.py` — typo `npec50_clean` → `np.mean(prec50_clean)`; None format crash in summary template

**Universe expansion to sp500:**
- `scripts/build_universe_config.py` — Fetched S&P 500 from Wikipedia, mapped GICS → sector ETFs, wrote `config/universes/sp500.yaml` (503 tickers)
- Downloaded 459 new tickers (519 total raw parquets)
- Rebuilt PIT mask: `data/artifacts/universe_mask_sp500.parquet` (avg 252 active tickers/day)
- Rebuilt features: 517 tickers, 21 features, 5109 dates

**Post-fix sp500 ablation results (2008–2026):**
| Experiment | CAGR | Sharpe | MaxDD | Vol |
|---|---|---|---|---|
| Equal Weight Universe | 12.94% | 0.616 | -55.1% | 21.0% |
| Alpha Top-50 EW | 13.47% | 0.635 | -55.3% | 21.2% |
| Alpha + Optimizer (no risk) | 11.23% | 0.551 | -54.8% | 20.4% |
| Full System | 8.70% | 0.590 | -34.4% | 14.8% |

**Optimizer sensitivity (no risk engine):**
| Max Turnover | CAGR | Sharpe | MaxDD |
|---|---|---|---|
| 0.3 | 11.23% | 0.551 | -54.8% |
| 0.5 | 11.91% | 0.683 | -40.4% |
| 0.8 | 11.98% | 0.689 | -39.8% |

**Key insights:**
- Alpha IC was 0.033 (below 0.04 target) on sp100 — root cause of weak alpha lift
- Risk engine adds Sharpe (0.64 → 0.59 with lower vol) but causes ~30% cash drag on average
- Optimizer suppresses CAGR (13.5% → 11.2%) suggesting turnover limit is binding
- Turnover 0.5 sweet spot: +13% Sharpe improvement vs 0.3 with minimal CAGR cost

---

## Key Design Decisions

| Decision | Rationale | Revisit if... |
|---|---|---|
| LightGBM regressor (not ranker) | Ranker needs group structure per cross-section date; regressor is simpler and nearly equivalent for top-N selection | IC stays below 0.03 for 3+ experiments |
| Top-50 equal weight selection | MVO optimizer on 500 stocks is slow (CVXPY ~2s/rebalance); EW Top-50 is faster and competitive | Need precise weights for RL overlay |
| Monthly rebalance (`BMS`) | Weekly is too costly in TC; monthly captures most factor decay for momentum/value | Factor half-life analysis suggests shorter |
| Heuristic risk engine (not learned) | VIX + SPY drawdown triggers are explainable and avoid overfitting to macro regimes | Sharpe < 0.5 on last 5-year window |
| ADV $100M liquidity threshold | Excludes pre-IPO and micro-cap contamination without being too restrictive (~252 active/day out of 503) | Want to include small-caps |
| 25-day feature cutoff | Prevents leakage from last-month features bleeding into current signal | Need to verify vs 1-day shift |

---

## What to Do When Diagnostics Complete

1. Read `data/artifacts/reports/universe_expansion_results.md`
2. Check success criteria:
   - IC > 0.04? (was 0.033 on sp100)
   - CAGR improved by 2–5 pp vs sp100 baseline?
   - Sharpe stable or better?
3. If IC ≥ 0.04 → promote to next phase (Brinson attribution or RL overlay planning)
4. If IC < 0.04 → investigate feature engineering:
   - Add quality factors (gross profit margin, asset turnover)
   - Add short-term reversal (ret_1w)
   - Try LGBMRanker with per-rebalance group structure
5. Commit results: `git add data/artifacts/reports/ && git commit -m "results: sp500 universe expansion diagnostics"`

---

## Useful Commands

```bash
# Check if diagnostics is still running
grep -c "Rebalancing:" /tmp/diag_run.log && grep "Signal Date" /tmp/diag_run.log | tail -1

# View results when done
cat data/artifacts/reports/universe_expansion_results.md
cat data/artifacts/reports/alpha_quality_large_universe.json | python -m json.tool

# Rebuild features after universe/config change
.venv/bin/python scripts/build_pit_universe.py --config config/universes/sp500.yaml \
  --output data/artifacts/universe_mask_sp500.parquet --adv-threshold 1e8
.venv/bin/python scripts/build_features.py --config config/base.yaml \
  --universe config/universes/sp500.yaml

# Run diagnostics (sp500 vs sp100 comparison)
.venv/bin/python scripts/run_diagnostics.py --config config/base.yaml \
  --universe config/universes/sp500.yaml \
  --compare-universe config/universes/sp100.yaml

# Run full backtest
.venv/bin/python scripts/run_backtest.py --config config/base.yaml \
  --universe config/universes/sp500.yaml

# Quick ablation check (single experiment)
.venv/bin/python -c "
from src.config.loader import load_config
from src.backtest.walk_forward import WalkForwardEngine
# ... see run_diagnostics.py for full pattern
"

# Check active tickers in PIT mask for a date
.venv/bin/python -c "
import pandas as pd
m = pd.read_parquet('data/artifacts/universe_mask_sp500.parquet')
date = '2020-01-31'
print(m.loc[date][m.loc[date]].index.tolist()[:10])
"
```
