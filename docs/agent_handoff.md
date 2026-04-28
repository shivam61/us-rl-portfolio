# Agent Handoff — Deep Context

Last updated: 2026-04-28T09:19:19+00:00

This is the deep-history document for all agents. Keep `AGENTS.md` short and put long-form notes here.

## What Belongs Here

- Material experiment outcomes
- Decisions that change future work
- Active risks, caveats, and follow-up tasks
- Useful commands that the next agent is likely to need

## Current Baseline Convention

- **sp100 (44 tickers)** = research baseline / dev universe / fast iteration track
- **sp500 (503 tickers)** = validation baseline / system benchmark / locked comparison track
- Historical notes may say "baseline" loosely; verify the universe before comparing metrics

## Current Recommended Workflow

1. Read `AGENTS.md`.
2. Read `docs/ROADMAP.md`.
3. Read this file only if prior experiment history or handoff detail is needed.

## Legacy Sessions

### Legacy Session 1

- Built the initial end-to-end pipeline: data ingestion, feature generation, LightGBM ranking, MVO optimizer, risk engine, and simulator.
- Used the sp100 universe for the original research baseline across 2006–2026.
- Initial ablation looked strong but was invalidated by a simulator mark-to-market tautology bug.

### Legacy Session 2

- Fixed simulator cash tracking, walk-forward `KeyError`, datetime mismatch, NYSE calendar issues, and typos.
- Expanded from sp100 to sp500 and rebuilt the point-in-time universe mask and features.
- Established locked sp500 validation baselines: equal weight `12.9% / 0.62`, full system `8.7% / 0.59`.
- Observed sp100 IC at `0.033`, which triggered Phase A feature engineering work.

### Legacy Session 3

- Added 13 new features across reversal and quality-momentum families.
- Phase A LightGBM IC results reached `0.038 / 0.186` Sharpe for momentum and `0.032 / 0.183` for volatility.
- Main conclusion: reversal features diluted the signal and `all_new` underperformed the narrower momentum slice.

### Legacy Session 4

- Ran rank-based momentum and volatility combo research on sp100.
- `score_50_50` reached `IC=0.041`, `Sharpe=0.150`, `Top-Bot=1.22%`.
- `volatility_only` was the strongest raw signal at `IC=0.050`, `Sharpe=0.175`, `Top-Bot=1.64%`.
- Beta decomposition showed `volatility_only` had genuine alpha at `16.4%` annualized with `t=3.36`.
- Expanded momentum-v2 features improved directionally but still missed the target gate.
- Main conclusion: the 44-name universe appears to impose an IC-Sharpe ceiling near `0.175`, so the next meaningful validation step is sp500 scale.

## Legacy Research Summary

### Phase A Research Summary

- Three pure rank-based research scripts were added for the sp100 universe:
- `scripts/run_momentum_vol_combo.py`: momentum and volatility rank-combo evaluation
- `scripts/run_beta_analysis.py`: beta decomposition of factor scores
- `scripts/run_momentum_v2.py`: expanded momentum feature audit

### Core Empirical Finding

- Cross-sectional reversal dominated classical momentum continuation in sp100 over 2016–2026.
- Risk-premium and volatility-linked signals dominated low-volatility style effects.
- Only `trend_consistency` and `sector_rel_momentum_6m` stayed positive in the traditional momentum direction.

### Factor Score Results

- `volatility_only`: `IC=0.050`, `IC Sharpe=0.175`, `Top-Bot=1.64%`, `P@20=33.6%`
- `score_50_50`: `IC=0.041`, `IC Sharpe=0.150`, `Top-Bot=1.22%`, `P@20=28.9%`
- `score_60_40`: `IC=0.036`, `IC Sharpe=0.131`, `Top-Bot=1.19%`, `P@20=28.3%`
- `momentum_only`: `IC=0.018`, `IC Sharpe=0.066`, `Top-Bot=0.71%`, `P@20=24.9%`

### Beta Decomposition Results

- `volatility_only` long portfolio beta: `1.084`
- `volatility_only` long alpha: `16.4%` annualized, `t=3.36`
- `volatility_only` long-short alpha: `11.6%` annualized, `t=1.79`
- Main conclusion: the risk-premium signal was not just beta exposure; it carried statistically meaningful alpha.

### Momentum V2 Results

- Theory-direction momentum-v2 failed with `IC=-0.022` and `IC Sharpe=-0.080`.
- Calibrated momentum-v2 improved to `IC=0.027`, `IC Sharpe=0.097`, `Top-Bot=0.97%`, `Long alpha=8.9%`, `t=1.77`.
- It still failed the IC, IC-Sharpe, and top-bottom spread gates.

### Phase A Gate Status

- Mean Rank IC: passed at `0.050`
- IC Sharpe: failed at `0.175` versus `0.30` target
- Top-bottom spread: passed at `1.64%`
- Precision@20: passed at `33.6%`
- Main conclusion: both LGBM and rank-based variants hit the same sp100 ceiling; broader universe validation is required.

## Recommended Next Steps

1. Validate the rank-combo research on sp500 with `run_momentum_vol_combo.py` and `run_beta_analysis.py`.
2. Add fundamental momentum features such as earnings surprise and analyst revision momentum.
3. Test longer skip periods such as `18m-ex-3m`.
4. Move to Phase B once sp500 IC-Sharpe results are strong enough.

## Useful Commands

- Run factor combo evaluation on sp100:
  `.venv/bin/python scripts/run_momentum_vol_combo.py --config config/base.yaml --universe config/universes/sp100.yaml`
- Run beta decomposition on sp100:
  `.venv/bin/python scripts/run_beta_analysis.py --config config/base.yaml --universe config/universes/sp100.yaml`
- Run momentum-v2 evaluation on sp100:
  `.venv/bin/python scripts/run_momentum_v2.py --config config/base.yaml --universe config/universes/sp100.yaml`
- Validate factor combo work on sp500:
  `.venv/bin/python scripts/run_momentum_vol_combo.py --config config/base.yaml --universe config/universes/sp500.yaml`
- Run the full backtest on sp500:
  `.venv/bin/python scripts/run_backtest.py --config config/base.yaml --universe config/universes/sp500.yaml`

## Session Notes

### 2026-04-28

- Shared agent-state migration planned: replace Claude-only context persistence with repo-level `AGENTS.md` plus a generic refresh script.
- Legacy handoff content was migrated into this file so there is a single deep handoff source.
- Existing Claude implementation was refactored to use the shared refresh flow through `scripts/save_context.sh` and `.claude/settings.json`.
- Target design keeps the auto-loaded context small and uses this file as the single deep history path.
