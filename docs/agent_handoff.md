# Agent Handoff — Deep Context

Last updated: 2026-05-04T09:46:36+00:00

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

### 2026-04-30

- Phase A.7.2 robustness validation was implemented in `scripts/run_phase_a7_2_robustness.py`.
- A.7.2 preserved the constraints: `volatility_score` unchanged, no new alpha, RL disabled.
- Outputs were saved to:
  `artifacts/reports/phase_a7_2_robustness.md`,
  `artifacts/reports/regime_breakdown.csv`,
  `artifacts/reports/parameter_sensitivity.csv`,
  `artifacts/reports/cost_impact.csv`.
- Tested both `sp100_sample` and `sp500_dynamic` across base weights `60/40`, `50/50`, `40/60`; k values `0.2`, `0.3`, `0.4`; VIX-only, drawdown-only, and weighted stress functions; costs of `10`, `25`, and `50` bps.
- Recommended conservative candidate remains `vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`.
- Candidate metrics:
  sp500 CAGR `23.51%`, Sharpe `1.538`, MaxDD `-26.36%`, max gross `1.375`;
  sp100 CAGR `18.22%`, Sharpe `1.739`, MaxDD `-17.00%`, max gross `1.375`.
- All tested sp500 full-period rows passed MaxDD `<40%`, Sharpe `>0.8`, and max gross `<=1.5`.
- Cost-adjusted sp500 performance remained competitive:
  average Sharpe `1.446` at 10 bps, `1.307` at 25 bps, `1.080` at 50 bps.
- Regime MaxDD passed across all tested regimes; worst sp500 regime MaxDD was `-37.71%` in 2020.
- Regime Sharpe `>0.8` failed in 2008 and 2022 for all tested rows. Treat those as capital-preservation regimes, not high-Sharpe regimes.
- Phase A can hand off to Phase B portfolio stabilization. Next work should focus on execution realism, turnover control, optimizer/risk integration, and preserving the A.7.2 drawdown/gross/cost profile. Keep RL disabled.
- Phase A.7.3 membership/coverage artifact validation was implemented in `scripts/run_phase_a7_3_membership_coverage_artifacts.py`.
- A.7.3 wording is intentional: this is not true PIT historical index-membership validation. It validates current configured universes plus current ADV/PIT liquidity masks. Do not import historical membership unless current-setup checks fail or become fragile.
- A.7.3 outputs were saved to:
  `artifacts/reports/phase_a7_3_membership_coverage_artifacts.md`,
  `artifacts/reports/universe_membership_audit.csv`,
  `artifacts/reports/feature_coverage_by_regime.csv`,
  `artifacts/reports/artifact_sensitivity.csv`.
- sp500 A.7.3 baseline current-mask candidate:
  CAGR `23.51%`, Sharpe `1.538`, MaxDD `-26.36%`, min candidates `128`, min selected `20`.
- sp500 artifact cohorts all passed drawdown, Sharpe, and selection-depth checks:
  no PIT mask `27.15% / 1.691 / -26.94%`,
  early-active-by-2010 `20.95% / 1.486 / -24.61%`,
  pre-2020 active-only `22.71% / 1.531 / -26.36%`,
  all-regime score coverage `21.05% / 1.495 / -24.61%`.
- Coverage/data flags:
  sp500 active `volatility_score` coverage is strong across regimes (`~99.8%+` average);
  sp100 2008 feature coverage is thinner at `92.3%` but sensitivity still passed;
  sp500 has three trailing zero-active PIT-mask days from `2026-04-27` to `2026-04-29`, likely a mask/date refresh artifact.
- A.7.3 decision:
  no current-setup membership/coverage artifact fragility detected in the strategy result. Do not import historical constituents now. Before Phase B production validation, clean/rebuild the trailing PIT mask or clip validation to the last nonzero active-mask date.
- Phase A baseline is locked for Phase B:
  `vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`, 10 bps cost.
- Phase B.0 baseline guard was implemented in `scripts/run_phase_b0_baseline_guard.py`.
- B.0 artifacts were saved to:
  `artifacts/reports/phase_b0_baseline_guard.md`,
  `artifacts/reports/phase_b0_data_window_guard.csv`,
  `artifacts/reports/phase_b0_baseline_lock.csv`.
- B.0 baseline lock:
  sp500 CAGR `23.51%`, Sharpe `1.538`, MaxDD `-26.36%`, max gross `1.375`, min candidates `128`, min selected `20`.
- B.0 data-window guard:
  sp500 raw prices run through `2026-04-29`, but the last nonzero active PIT-mask date is `2026-04-24`; production validation should clip to `2026-04-24` or refresh/rebuild the mask before using trailing dates.
- B.0 handed off to B.1 to reproduce the A.7.3 candidate in a production-style portfolio runner and measure drift versus the matrix-return baseline before adding turnover smoothing, optimizer, or risk overlays.
- Phase B.1 simulator reproduction was implemented in `scripts/run_phase_b1_simulator_reproduction.py`.
- B.1 artifacts were saved to:
  `artifacts/reports/phase_b1_simulator_reproduction.md`,
  `artifacts/reports/phase_b1_simulator_reproduction.csv`,
  `artifacts/reports/phase_b1_runner_detail.csv`,
  plus per-universe history, trade, and target-diagnostic CSVs.
- B.1 found that the unlagged A.7.3 matrix headline used same-day signal/return alignment: date-t stress-scaled target weights were applied to date-t returns.
- Diagnostic rows isolated execution timing and price mode. Even adjusted-close/same-day simulator accounting did not reproduce the unlagged A.7.3 headline, while a one-day-lagged matrix reference matched the production simulator within tolerance.
- B.1 sp500 clipped validation through `2026-04-24`:
  unlagged A.7.3 matrix reference `23.53% / 1.539 / -26.36%`;
  lagged matrix reference `17.65% / 1.147 / -29.44%`;
  production open/next-day simulator `17.56% / 1.116 / -26.98%`;
  equal-weight simulator Sharpe `0.619`;
  max gross `1.375`; min selected `21`.
- B.1 sp100:
  lagged matrix reference `14.78% / 1.394 / -20.32%`;
  production open/next-day simulator `14.54% / 1.381 / -18.70%`;
  equal-weight simulator Sharpe `0.864`.
- Decision:
  original B.1 drift versus the unlagged A.7.3 matrix headline fails and should not be ignored, but it is reconciled by the lagged matrix reference. Reset Phase B promotion baseline to the production open/next-day simulator row. Do not optimize future Phase B work against the unlagged A.7.3 headline.
- B.1 handed off to B.2:
  turnover smoothing / rebalance hysteresis on the production-realistic baseline, preserving the B.1 sp500 MaxDD `<40%`, max gross `<=1.5`, Sharpe `>1.0` preferred, and same-universe equal-weight outperformance. Keep `volatility_score` unchanged, add no alpha, and keep RL disabled.
- Phase B.2 turnover control / rebalance hysteresis was implemented in `scripts/run_phase_b2_turnover_control.py`.
- B.2 artifacts were saved to:
  `artifacts/reports/phase_b2_turnover_control.md`,
  `artifacts/reports/turnover_frontier.csv`,
  `artifacts/reports/cost_sensitivity.csv`,
  `artifacts/reports/trade_threshold_results.csv`,
  `artifacts/reports/persistence_results.csv`.
- B.2 used a fast one-day-lagged target-weight approximation for frontier selection. The B.1 exact open/next-day simulator remains the Phase B promotion anchor.
- B.2 did not change `volatility_score`, trend signal construction, stress-scaling formula, or RL settings.
- B.2 primary promoted turnover-control candidate:
  `every_2_rebalances` on `sp500_dynamic` clipped to `2026-04-24`;
  CAGR `18.33%`, Sharpe `1.144`, MaxDD `-33.69%`, max gross `1.346`, turnover sum `89.62`, turnover reduction `61.2%`.
- B.2 cost sensitivity:
  every-2-rebalances Sharpe was `1.089` at 25 bps and `0.999` at 50 bps, versus baseline same-cost Sharpe `0.999` and `0.765`, respectively.
- Other passing reference rows:
  50 bps trade threshold `18.16% / 1.166 / -31.57%` with `25.0%` turnover reduction;
  50 bps threshold + top-40 persistence `18.06% / 1.147 / -33.78%` with `34.7%` turnover reduction;
  50% partial rebalance `18.07% / 1.176 / -28.43%` with `25.0%` turnover reduction.
- Fragile/rejected B.2 rows:
  4-week cadence reduced turnover `73.3%` but failed MaxDD at `-36.65%`;
  100 bps threshold failed MaxDD/gross gates;
  partial-rebalance plus threshold/persistence combinations can accumulate stale residual positions and exceed max gross.
- Next Phase B step:
  B.3 exposure-constrained portfolio shaping, using B.2 every-2-rebalances as the primary turnover-control candidate and threshold/partial rows as secondary references. Do not use B.3 as return maximization.
- Phase B.3 exposure-constrained portfolio shaping was implemented in `scripts/run_phase_b3_exposure_control.py`.
- B.3 artifacts were saved to:
  `artifacts/reports/phase_b3_exposure_control.md`,
  `artifacts/reports/constraint_violations.csv`,
  `artifacts/reports/beta_tracking.csv`,
  `artifacts/reports/gross_exposure.csv`,
  plus convenience summary `artifacts/reports/phase_b3_summary.csv`.
- B.3 preserved the constraints: no `volatility_score` change, no trend-signal change, no stress-formula change, no new alpha, RL disabled.
- B.3 compared B.2 `every_2_rebalances` with and without projection. Projection uses scalar shaping first; if scalar scaling cannot meet beta floor inside gross `1.5`, it adds a minimal SPY beta-floor projection. This is constraint repair, not alpha.
- B.3 result:
  B.2 no projection remains `18.33% / 1.144 / -33.69%`, turnover `89.62`, max gross `1.346`, but has `90` rebalance-date beta-band violations.
- B.3 projected row:
  CAGR `15.50%`, Sharpe `1.069`, MaxDD `-31.28%`, turnover `81.67`, max gross `1.500`, rebalance-date beta violations `0`.
- Decision:
  B.3 is FAIL/WATCH. The hard `0.5-0.8` beta band is mechanically feasible, but it drops CAGR by `2.83` percentage points versus B.2, exceeding the `2` pp tolerance. Do not promote the projected B.3 row as-is.
- Recommended next step:
  stay in B.3 and test less punitive exposure policy before B.4, specifically a one-sided beta cap such as beta `<=0.8` and/or a wider beta band such as `0.4-0.9` or `0.5-0.9`. Keep B.2 `every_2_rebalances` as the active construction until B.3 clears both constraint and performance gates.
- Phase B.3.1 soft exposure policy design was run through the same `scripts/run_phase_b3_exposure_control.py` runner.
- B.3.1 tested:
  no-projection reference,
  hard band `0.5-0.8`,
  one-sided caps `<=0.8`, `<=0.85`, `<=0.9`,
  cap `<=0.8` with `0.05` action tolerance,
  wider bands `0.4-0.9` and `0.5-0.9`.
- B.3.1 decision:
  promote `b3_band_50_90` as the current B.3 exposure-policy candidate. It has CAGR `16.49%`, Sharpe `1.075`, MaxDD `-33.69%`, turnover `85.36`, max gross `1.500`, and zero rebalance-date beta/gross violations. CAGR drop is `1.84` pp vs B.2, inside the `2` pp tolerance; Sharpe drop is `0.069`, inside the `0.10` tolerance.
- Explicit promotion:
  `b3_band_50_90` is the Phase B baseline for B.4. Treat it as the deployable compromise: B.1 made the system production-realistic, B.2 made it turnover-efficient, and B.3.1 made it rebalance-date exposure-compliant without over-constraining the economics.
- Cap-only policies reduced turnover more but failed CAGR tolerance:
  cap `<=0.80` CAGR `15.11%`,
  cap `<=0.85` CAGR `15.62%`,
  cap `<=0.90` CAGR `16.10%`.
- B.3.1 caveat:
  gates are rebalance-date ex-ante beta/gross controls. Daily beta drift remains visible in `beta_tracking.csv` but should not be corrected daily unless B.4 proves the need; daily beta-chasing would undo B.2 turnover improvements.
- Next Phase B step:
  proceed to B.4 risk engine formalization from the B.3.1 `0.5-0.9` soft beta-band candidate. Do not reintroduce the hard `0.5-0.8` band without a new tolerance rationale.
- Phase B.4 risk engine formalization was implemented in `scripts/run_phase_b4_risk_engine.py`.
- B.4 replaced the static B.3.1 beta cap (0.90) with a stress-aware dynamic cap: `beta_cap = 0.90 - 0.20 * stress_score`, clamped to [0.51, 0.90]. Beta floor held at 0.50; gross ≤ 1.5 preserved. No change to `volatility_score`, trend signal, or stress-scaling formula.
- B.4 artifacts saved to:
  `artifacts/reports/phase_b4_risk_engine.md`,
  `artifacts/reports/beta_cap_tracking.csv`,
  `artifacts/reports/stress_vs_exposure.csv`,
  `artifacts/reports/performance_vs_b3_1.csv`.
- B.4 tested:
  B.3.1 reference (`b3_band_50_90` static cap 0.90),
  `b4_stress_beta_cap` (dynamic cap only),
  `b4_stress_cap_trend_boost` (dynamic cap + small trend boost when stress > 0.50).
- B.4 result:
  both B.4 variants passed all gates.
  `b4_stress_beta_cap`: CAGR `15.95%`, Sharpe `1.073`, MaxDD `-32.98%`, turnover `83.49`, violations `0`.
  `b4_stress_cap_trend_boost`: CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`, turnover `84.12`, violations `0`.
- Dynamic cap dynamics: averaged `0.829` across 120 rebalance dates, ranged from `0.70` (peak stress) to `0.90` (zero stress).
- B.4 decision:
  promote `b4_stress_cap_trend_boost` as the Phase B.4 candidate. Sharpe improved (+0.003), MaxDD improved by 0.71 pp, CAGR drop only 0.45 pp — all within gates. Turnover reduced slightly.
- Next Phase B step:
  proceed to B.5 final Phase B gate run using `b4_stress_cap_trend_boost` as the promoted candidate. Validate sp500 results, check cost-adjusted Sharpe at 25/50 bps, and confirm the construction clears all Phase B exit criteria.
- Phase B.5 final gate run was implemented in `scripts/run_phase_b5_final_gate.py`.
- B.5 artifacts saved to:
  `artifacts/reports/phase_b5_final_gate.md`,
  `artifacts/reports/phase_b5_cost_sensitivity.csv`,
  `artifacts/reports/phase_b5_regime_breakdown.csv`,
  `artifacts/reports/phase_b5_attribution.csv`,
  `artifacts/reports/phase_b5_beta_compliance.csv`.
- B.5 validated `b4_stress_cap_trend_boost` against all 8 Phase B exit criteria — all passed:
  MaxDD `-32.98%` (gate `<40%`); 50 bps Sharpe `0.934` (gate `>0.90`); 25 bps Sharpe `1.024`; 10 bps Sharpe `1.078`; beats equal-weight `0.619`; max gross `1.500`; zero beta violations; turnover `84.12` (gate `<=90`).
- Cost sensitivity: Sharpe at 10 bps `1.078`, 25 bps `1.024`, 50 bps `0.934` — competitive at all cost levels.
- Regime breakdown: 2008 Sharpe `0.54`, 2022 Sharpe `-0.73` (expected capital-preservation regimes); 2023–2026 recovery Sharpe `2.47`, full-period Sharpe `1.08`.
- Beta compliance: 120 rebalance dates, 0 violations, compliance rate 100%; avg beta `0.770`, range `[0.500, 0.899]`; avg dynamic cap `0.829`, min `0.701`.
- Phase B decision: COMPLETE. `b4_stress_cap_trend_boost` is the Phase B promoted construction.
- Next step: proceed to Phase C — model refinement: LightGBM tuning and feature improvements. Phase C entry point is `docs/phases/phase_c.md`. The Phase B baseline for Phase C is B.5 (`b4_stress_cap_trend_boost`, sp500, CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`).
- **Phase C.1 COMPLETE — Verdict: REJECT** (2026-05-01).
- C.1 grid search: 216 combos, 95 holdout dates, completed in 38 min on 32-core machine. Grid results saved: `artifacts/reports/phase_c1_grid_results.csv`.
- Best config found: `num_leaves=15, min_data_in_leaf=100, feature_fraction=0.6, bagging_fraction=0.9, lambda_l1=0.0, lambda_l2=0.0` — holdout IC Sharpe=-0.1389, Mean IC=-0.0021.
- Root cause of REJECT: LightGBM has negative IC on sp500 across nearly all regimes (baseline IC Sharpe=-1.3831, best holdout IC Sharpe=-0.1389). The model is anti-predictive. HPO cannot fix this.
- Portfolio despite negative IC: CAGR=14.78%, Sharpe=1.029, MaxDD=-29.68% (B.5 harness is doing the lifting).
- Gate failures: 50 bps Sharpe=0.819 (gate ≥0.884), Turnover=119.3 (gate ≤100), preferred Sharpe=1.029 (gate ≥1.128). Sharpe floor 1.029 barely passes (≥1.028).
- IC by regime: only positive IC in 2020 COVID (best IC Sharpe=0.39) and 2023-2026 recovery (0.44). Negative in crisis, train window, and 2015-16 vol stress.
- Bug fixed in runner: `_make_lgbm_params` now casts integer params (num_leaves, min_data_in_leaf) from np.float64→int; `--skip-grid` flag added to reload saved grid CSV without re-running 38-min search.
- C.1 artifacts: `phase_c1_lgbm_tuning.md`, `ic_by_regime.csv`, `portfolio_vs_baseline.csv`, `phase_c1_grid_results.csv`.
- Run command (re-run without grid): `.venv/bin/python scripts/run_phase_c1_lgbm_tuning.py --config config/base.yaml --universe config/universes/sp500.yaml --skip-grid`
- **Phase C.2 COMPLETE — Verdict: POSITIVE IC FOUND** (2026-05-01).
- Script: `scripts/run_phase_c2_feature_attribution.py` — 33 signals evaluated (32 stock features + vol_score composite), completed in ~7 min on 32 cores.
- 18/32 features anti-predictive on sp500 holdout; signal concentrated in 4 vol features.
- Top positive-IC features (holdout IC Sharpe): beta_to_spy_63d=1.79, downside_vol_63d=1.78, volatility_21d=1.76, volatility_63d=1.76, vol_score_composite=1.67.
- Critical insight: **LightGBM itself destroys the signal.** Vol features alone: direct rank IC Sharpe=1.668, LGBM on same=1.196. All 32 features in LGBM=-0.139. Signal is rank-linear, not tree-based.
- Best model: **simple_mean_rank** over 14 positive-IC features → holdout IC Sharpe=1.8559 (beats vol_score 1.668).
- 14 positive-IC features: beta_to_spy_63d, downside_vol_63d, volatility_21d, volatility_63d, liquidity_rank, avg_dollar_volume_63d, ret_12m_ex_1m, ret_12m, sector_rel_momentum_6m, trend_consistency, ma_50_200_ratio, above_200dma, ret_6m_adj, ret_6m.
- Also: max_drawdown_63d is ANTI-PREDICTIVE (IC Sharpe=-1.40) despite being in the vol_score composite — the other 3 vol features dominate.
- C.2 artifacts: `phase_c2_feature_attribution.md`, `feature_ic_by_regime.csv`, `feature_ic_by_period.csv`, `anti_predictive_features.csv`, `feature_subset_results.csv`, `model_sanity_comparison.csv`.
- **Phase C.3 COMPLETE — Verdict: REJECT** (2026-05-01).
- Script: `scripts/run_phase_c3_portfolio_validation.py` — ran in 67s on 32-core machine.
- Candidate: `simple_mean_rank_14` (equal-weight rank percentile of 14 positive-IC features, no model). IC Sharpe=1.8559 vs vol_score 1.6682.
- Portfolio results (10 bps): CAGR=15.65%, Sharpe=1.050, MaxDD=-33.94%, Turnover=90.5.
- Gate results: Sharpe floor (≥1.05) FAIL by hairline (1.0498), MaxDD PASS, 50 bps Sharpe PASS (0.895), Turnover PASS (90.5), Beta violations PASS (0).
- Root cause of REJECT: high-vol/high-beta selection catastrophically underperforms in 2008 financial crisis (SMR Sharpe=-0.270 vs vol_score +0.542, delta=-0.811). SMR wins in all other regimes (2015-16: +0.19, 2020: +0.65, 2022: +0.47) but cannot recover the 2008 crisis gap over full period.
- Name overlap: only 22.1% of SMR selection shared with vol_score (Jaccard 0.131). These are fundamentally different portfolios: SMR selects high-vol/high-beta/high-momentum, vol_score selects low-vol/low-beta.
- Sector shifts: SMR overweights XLV (+3.3%), XLC (+2.3%), XLI (+1.3%); underweights XLF (-4.5%), XLE (-2.0%).
- IC → portfolio disconnect: better IC (1.86 vs 1.67) does not translate to better portfolio Sharpe. High-vol selections carry higher idiosyncratic risk even after beta cap — especially punishing in 2008 crisis.
- C.3 artifacts: `phase_c3_signal_validation.md`, `c3_portfolio_comparison.csv`, `c3_regime_breakdown.csv`, `c3_selected_overlap.csv`, `c3_cost_sensitivity.csv`.
- **Phase C COMPLETE. Production signal: `vol_score` (unchanged). All LightGBM and feature-selection work for this alpha family is frozen. Proceed to Phase D with vol_score.**
- Run command: `.venv/bin/python scripts/run_phase_c3_portfolio_validation.py --config config/base.yaml --universe config/universes/sp500.yaml`

### 2026-04-29

- Phase A.3 multi-sleeve alpha system was implemented in `scripts/run_phase_a3_multi_sleeve_alpha.py`.
- Experiment rules were preserved: existing `volatility_score` was not modified, quality features were not merged into the volatility model, and RL stayed disabled.
- Outputs were saved to:
  `artifacts/reports/multi_sleeve_results.md`,
  `artifacts/reports/sleeve_metrics.csv`,
  `artifacts/reports/blend_metrics.csv`,
  `artifacts/reports/correlation_matrix.csv`,
  `artifacts/reports/overlap_report.csv`.
- sp100 quality sleeve looked superficially useful:
  best quality sleeve `CAGR=16.82%`, `Sharpe=0.897`, `MaxDD=-39.43%`.
- sp500 quality sleeve did not generalize:
  best quality sleeve `CAGR=9.82%`, `Sharpe=0.555`, `MaxDD=-48.42%`.
- sp500 blends preserved high CAGR but failed the investability gate:
  best blend Sharpe was `0.698` versus equal-weight `0.779`, with MaxDD `-53.53%`.
- Best sp500 blend CAGR was `22.80%`, but Sharpe was only `0.606` and MaxDD was `-69.68%`.
- Cross-sleeve independence failed:
  sp500 vol-quality full correlations ranged `0.633` to `0.708`, and crisis correlations ranged `0.728` to `0.798`.
- Ticker overlap on sp500 was very low (`0.04%` to `1.57%`), so the failure is not duplicate names; it is common market/risk exposure and weak defensive signal quality.
- Decision:
  do not proceed to optimizer integration, improved risk engine, or RL from this A.3 blend. Keep `volatility_score` as Sleeve 1 and return to defensive-sleeve feature engineering.
- Recommended next work:
  build Sleeve 2 with stronger non-price fundamentals: true leverage/debt, accruals or earnings quality, profitability persistence, value-quality composite, and analyst revisions if available. Avoid price-risk-heavy defensive quality because it remains correlated with volatility alpha in stress regimes.
- Phase A.4 defensive stability sleeve was implemented in `scripts/run_phase_a4_defensive_sleeve.py`.
- A.4 intentionally avoided `ROE + momentum + growth` as the quality score. Sleeve 2 was reframed as stability/survivability plus beta control inside the defensive sleeve.
- A.4 outputs were saved to:
  `artifacts/reports/phase_a4_defensive_sleeve_results.md`,
  `artifacts/reports/phase_a4_sleeve_metrics.csv`,
  `artifacts/reports/phase_a4_blend_metrics.csv`,
  `artifacts/reports/phase_a4_correlation_matrix.csv`,
  `artifacts/reports/phase_a4_overlap_report.csv`,
  `artifacts/reports/phase_a4_data_availability.csv`.
- Beta targeting worked mechanically:
  target beta `0.6` realized around `0.604-0.606` on sp100 and `0.601-0.603` on sp500.
- A.4 lowered sp500 vol-defensive correlation, but not enough:
  best full correlation was `0.563`, best crisis correlation was `0.645`; gates were `<0.5` and `<0.6`.
- A.4 sp500 defensive sleeve remained weak:
  best standalone defensive sleeve `CAGR=8.51%`, `Sharpe=0.487`, `MaxDD=-48.78%`.
- A.4 best sp500 blend Sharpe:
  `0.694` with `CAGR=18.29%`, `MaxDD=-53.51%`, below equal-weight Sharpe `0.779`.
- A.4 best sp500 blend drawdown:
  `MaxDD=-50.49%`, still above the `<40%` gate.
- Data audit explains the failure:
  sp500 ROE/PE/PB/EPS-growth coverage is only about `8.0-8.5%`; debt/leverage, cash-flow accruals, gross margin, and analyst revisions are unavailable.
- Decision:
  beta-neutralization inside Sleeve 2 is directionally correct and should be retained, but A.4 still failed the sp500 gate. Do not proceed to optimizer/risk/RL. Next work should be data-layer upgrade for true survivability fundamentals before more blend tuning.
- Phase A.5 data/feature hygiene was implemented.
- Root cause fixed:
  `fetch_universe_fundamentals()` previously used one global `data/raw/fundamentals.parquet`, so sp500 reused a 44-ticker sp100 cache. It now supports universe/ticker-set scoped cache files such as `fundamentals_sp100_sample.parquet` and `fundamentals_sp500_dynamic.parquet`.
- Fundamental call sites now pass `cache_key=universe_config.name`.
- `FundamentalFeatureGenerator` now emits survivability features when raw fields exist:
  `debt_to_assets`, `debt_to_equity`, `asset_turnover`, `accruals_proxy`, `net_debt_to_assets`, `interest_coverage`, `ocf_to_net_income`, `gross_margin`.
- Added `docs/DATA_AND_FEATURE_ENGINEERING.md` as the guide for future data/feature additions.
- Added A.5 audit runner:
  `scripts/run_phase_a5_data_feature_audit.py`.
- A.5 audit artifacts:
  `artifacts/reports/phase_a5_data_feature_audit.md`,
  `artifacts/reports/phase_a5_data_feature_summary.csv`,
  `artifacts/reports/phase_a5_data_feature_coverage.csv`.
- A.5 audit result:
  sp100 fundamental coverage `44/44`; sp500 fundamental coverage `503/503`; engineered survivability fields mostly `~98.6%` row coverage and `100%` ticker coverage on sp500.
- Important caveat:
  current `FundamentalProvider` is simulated. A.5 validates plumbing and schema coverage, not research-grade alpha.
- A.4 was revisited after wiring survivability features into `defensive_stability_score`.
- A.4 revisit result:
  best sp500 standalone defensive Sharpe improved from `0.487` to `0.650`; best blend Sharpe improved from `0.694` to `0.745`, but remains below equal-weight `0.779`; best blend MaxDD remained around `-49.34%`; best crisis correlation improved to `0.610` but still missed `<0.6`.
- Decision:
  A.5 plumbing is fixed, A.4 direction improved, but no production decision should be made from simulated fundamentals. Next step is replacing/augmenting the fundamental provider with real point-in-time survivability data, then rerunning A.5 and A.4.
- Phase A.6 canonical fundamentals contract was implemented.
- `src/data/providers/canonical_fundamental_provider.py` now defines the canonical local parquet/CSV schema, required fields, common column aliases, date parsing, ticker normalization, deduping, ticker/date filtering, and schema validation.
- `config/base.yaml` now has `fundamentals.provider`, `fundamentals.path`, `fundamentals.min_ticker_coverage`, and `fundamentals.require_pit_dates`.
- `src/data/ingestion.py` selects either `simulated` or `canonical_local` fundamentals based on config.
- `scripts/run_phase_a5_data_feature_audit.py` now records provider, minimum coverage threshold, coverage pass/fail, and canonical required-column presence.
- `docs/DATA_AND_FEATURE_ENGINEERING.md` was updated to state that local parquet/CSV canonical fundamentals are the stable research contract. Future SEC/FMP/Polygon/Sharadar/manual sources should normalize into that schema first.
- Next step:
  obtain or create a real PIT canonical fundamentals parquet/CSV, switch `fundamentals.provider` to `canonical_local`, rerun A.5 audit, then rerun A.4. Do not make optimizer/RL decisions from the simulated provider.
- Added `scripts/prepare_canonical_fundamentals.py`, a local CSV/parquet normalization utility for vendor exports. It writes the canonical schema consumed by `canonical_local` and validates required columns, PIT dates, duplicate ticker/date rows, and optional ticker coverage.
- Added `scripts/build_sec_fundamentals_poc.py`, a bounded SEC company-facts POC that downloads SEC company ticker mapping and company facts, maps available us-gaap tags into the canonical schema, and writes `data/fundamentals/sec_poc_canonical_fundamentals.parquet`.
- SEC POC outputs when run:
  `artifacts/reports/phase_a6_1_sec_fundamentals_poc.md` and `artifacts/reports/phase_a6_1_sec_fundamentals_coverage.csv`.
- SEC POC status:
  live SP100 sample run completed with `--user-agent "Shivam Gupta nitshivamgupta@gmail.com"`.
- SEC POC result:
  `1,965` canonical rows, `44/44` tickers, filing date range `2015-01-26` to `2026-04-29`. Raw gross-profit tag coverage was weak at `17/44`, so gross-margin conclusions remain fragile.
- SEC PIT A.4 result:
  best standalone defensive sleeve was `defensive_stability_top_50_equal_weight` with `CAGR=16.33%`, `Sharpe=0.876`, `MaxDD=-38.61%`; best drawdown-aware blend had `CAGR=17.79%`, `Sharpe=0.887`, `MaxDD=-42.17%`; best full vol-defensive corr remained about `0.70` and crisis corr about `0.75`.
- Added `scripts/run_phase_a4_1_crisis_diversifier_v2.py`, an isolated fundamental-only crisis-diversifier runner. It excludes returns, volatility, drawdown, momentum, and beta from alpha scoring; beta is used only after selection for weighting.
- A.4.1 result:
  failed hard gate. Best full corr was about `0.711`, best crisis corr about `0.766`, despite standalone Sharpe above `0.7` for most variants. Blend metrics were skipped by rule because no standalone diversifier passed.
- SEC POC decision rule:
  do not scale SEC ingestion to sp500/2006+ from this result. Quality/fundamental-only defensive sleeves still behave like long-equity risk in stress. Next Sleeve 2 candidate should be a different economic exposure: explicit crisis hedge/carry, trend-following hedge, sector/cash rotation, or market-neutral long-short research.
- Added `scripts/run_phase_a7_trend_overlay.py`, an isolated trend hedge overlay runner. It uses `SPY`, `TLT`, `GLD`, and `UUP`; tests 3m, 6m, and 3m/6m TSMOM; supports long/cash and long/short variants; inverse-vol weights to a 10% target sleeve vol with 1.5x gross cap; and blends with unchanged `volatility_score` sleeves.
- A.7 result:
  trend sleeves are genuinely orthogonal to volatility alpha in crisis. On sp500, trend crisis correlations versus `vol_top_20` ranged roughly `-0.10` to `-0.23`.
- A.7 validation result:
  SP100 research passed with 29 blend variants, but SP500 validation failed because MaxDD remained above the `<40%` gate. Best SP500 Sharpe variant was `blend_vol_top_20_trend_3m_6m_long_cash_60_40` with `CAGR=24.15%`, `Sharpe=0.947`, `MaxDD=-45.09%`. Best drawdown group was long/short 60/40 around `MaxDD=-44.57%`.
- Current decision:
  trend hedge overlay is the leading Sleeve 2 candidate, but not production-passed. Next work should be A.7.1 drawdown control: stronger hedge expression, higher trend allocation, crash-triggered trend scaling, explicit SPY hedge overlay, or portfolio-level beta cap. Keep RL disabled.
- Added `scripts/run_phase_a7_1_drawdown_control.py`, a focused sp500 validation runner for wider trend weights, continuous stress scaling, and residual beta hedging. It keeps `vol_top_20` and `trend_3m_6m_long_cash` fixed.
- A.7.1 result:
  passed the sp500 validation gate. 16 variants cleared MaxDD `<40%`, Sharpe above equal-weight, CAGR `>18%`, and low trend crisis correlation.
- Leading simple candidate:
  `a7_1_stress_50_50_k_30` with `CAGR=22.76%`, `Sharpe=1.488`, `MaxDD=-26.41%`, max gross `1.375`, and no residual SPY short hedge.
- Best Sharpe hedged candidate:
  `a7_1_hedge_50_50_k_20_beta_0_5` with `CAGR=23.59%`, `Sharpe=1.584`, `MaxDD=-28.85%`, but it uses residual SPY hedge down to about `-59%` and max gross `1.713`.
- Current decision:
  A.7.1 produced the first candidate investable non-RL expression. Prefer the simpler stress-scaled blend for next validation; treat beta-hedged variants as secondary until leverage/turnover are reviewed. Next work should be A.7.2 robustness/cost/leverage review before optimizer/RL.
- Future 20-year/RL note:
  current raw backtest starts in 2006, but metrics start after warmup around 2008. Preserve chronological splits for RL, keep 2019-2026 as a candidate final holdout, and require A.5 coverage by period before using fundamentals in RL state features.

### 2026-04-28

- Shared agent-state migration planned: replace Claude-only context persistence with repo-level `AGENTS.md` plus a generic refresh script.
- Legacy handoff content was migrated into this file so there is a single deep handoff source.
- Existing Claude implementation was refactored to use the shared refresh flow through `scripts/save_context.sh` and `.claude/settings.json`.
- Target design keeps the auto-loaded context small and uses this file as the single deep history path.
- Added non-LGBM regime-switch factor research via `scripts/run_regime_switch_strategy.py`.
- Added `pct_pos_months_6m` and `sector_rel_momentum_6m` to `StockFeatureGenerator`, both still lagged by one day.
- Added an optional `alpha_score_provider` path to `WalkForwardEngine.run()` so factor sleeves can be backtested through the existing selection, risk, and execution stack without enabling LGBM or RL.
- sp100 regime-switch result was negative versus the strongest single sleeve:
  `volatility_score` stayed best with `IC=0.0547`, `IC Sharpe=0.2085`, `Top-Bot=1.79%`, `CAGR=13.61%`, `MaxDD=-31.86%`.
- `regime_switch_score` reached `IC=0.0427`, `IC Sharpe=0.1834`, `Top-Bot=1.27%`, `CAGR=13.49%`, `MaxDD=-31.86%`.
- Main conclusion: the current regime map helps volatility signals in low-vol windows, but switching away from `volatility_score` in neutral and high-vol states degrades the overall sp100 result.
- Artifacts saved to `artifacts/reports/regime_switch_results.md` and `artifacts/reports/regime_ic.csv`.
- Production default was switched to `volatility_score` via a reusable `src/alpha/` module and the default backtest path now uses that sleeve when `alpha.default_score` is set to `volatility_score`.
- `trend_score` and `mean_reversion_score` remain research-only in `scripts/run_regime_switch_strategy.py`; no regime switching or RL changes were carried into production.
- New sp100 production sweep artifacts:
  `artifacts/reports/volatility_alpha_production.md`,
  `artifacts/reports/volatility_topn_sensitivity.csv`,
  `artifacts/reports/volatility_sector_cap_sensitivity.csv`.
- sp100 production sweep result:
  `volatility_score + optimizer + risk` improved risk-adjusted performance to `CAGR=17.97%`, `Sharpe=0.932`, `MaxDD=-36.51%`.
- Best sector-cap variant on sp100 was `20%` with `CAGR=18.13%`, `Sharpe=0.941`, `MaxDD=-36.50%`; Sharpe target passed, drawdown target still failed.
- Equal-weight Top-N sensitivity on sp100 favored smaller books for CAGR (`Top-20 = 19.76%`) but none of the equal-weight variants met Sharpe `> 0.9` or MaxDD `< 32%`.
- During optimizer-based runs, OSQP occasionally returned `infeasible` or `user_limit`, so some periods fell back to the optimizer's equal-weight backup path; worth hardening before treating optimizer results as final production behavior.
- Baseline frozen as `baseline_v1_volatility_score_sp100` with:
  `sp100`, `volatility_score`, optimizer enabled, risk enabled, sector cap `20%`, RL disabled.
- Exact frozen run ID:
  `baseline_v1_volatility_score_sp100_2026-04-28T12:25:04Z`
- Baseline record saved to:
  `artifacts/reports/baseline_v1_volatility_score_sp100.md`
- Production-default config now aligns with the frozen sector cap (`config/base.yaml`) and the named baseline config is:
  `config/baseline_v1_volatility_score_sp100.yaml`
- Recommended next step: harden optimizer stability first, then do drawdown decomposition on the frozen baseline.
- Optimizer stability hardening implemented:
  alpha z-score clipping at `±3`, covariance repair helpers, deterministic fallback hierarchy (`full -> relaxed -> equal-weight Top-N`), and per-rebalance optimizer diagnostics.
- Optimizer diagnostics now capture:
  covariance condition number, fallback level, solver attempt statuses, constraint-violation summaries, asset count, and sector distribution.
- Stability regression report saved to:
  `artifacts/reports/optimizer_stability.md`
- Optimizer stability report run ID:
  `optimizer_stability_20260428T125149Z`
- Report summary on frozen sp100 baseline:
  `239` rebalances, `236` full solves, `2` relaxed solves, `1` equal-weight fallback.
- Post-hardening baseline run in the stability report came in at:
  `CAGR=17.30%`, `Sharpe=0.917`, `MaxDD=-37.06%`.
- Constraint enforcement is effectively stable:
  max stock-cap overage `0`, max sector-cap overage `0`, max turnover overage `4.399e-04` (numerical-scale residual).
- Recommended next step tightened:
  analyze the remaining drawdown episodes first, then decide whether the final optimizer polish should target turnover tolerance, alternate solver settings, or additional cash/risk controls.
- Drawdown attribution completed for frozen `baseline_v1_volatility_score_sp100` without changing strategy.
- Artifacts saved:
  `artifacts/reports/drawdown_attribution.md`,
  `artifacts/reports/drawdown_periods.csv`.
- Top drawdowns were:
  2020 COVID crash `-37.06%`, 2022 bear market `-33.65%`, 2008 crisis `-29.83%`, 2011 drawdown `-21.94%`, 2018 Q4 `-19.63%`.
- Attribution conclusion:
  drawdowns are primarily from market crashes plus volatility-factor failure during stress windows; not primarily from sector concentration or turnover/whipsaw.
- Drawdown aggregate:
  average gross exposure during top drawdowns `77.46%` vs normal `91.02%`, average drawdown beta `0.915`, average top-10 loser contribution `-22.66%`.
- Next recommended work:
  focus risk controls on stress-window exposure/beta reduction and factor-failure detection rather than tighter sector caps or turnover throttles.
- Stress-conditioned alpha tests completed without inversion, new features, optimizer changes, or RL.
- Artifact saved:
  `artifacts/reports/stress_conditioned_alpha.md`.
- Tested variants:
  baseline, sector-neutral stress alpha, stress cash/exposure scaling, and dampened alpha control.
- Result:
  `sector_neutral_stress` improved 2022 drawdown (`-28.95%` vs baseline `-33.65%`) but lowered broad stress IC (`0.0249` vs `0.0371`) and did not pass the MaxDD gate (`-36.92%`).
- `stress_cash_exposure` improved 2020/2022 drawdowns (`-36.36%`, `-29.37%`) and Sharpe (`0.934`) but still missed MaxDD `<32%` and CAGR was barely above the `16%` gate (`16.06%`).
- `dampened_stress` was identical to baseline, confirming scalar alpha dampening is a no-op under per-rebalance optimizer alpha normalization.
- Important nuance:
  broad stress regime IC remained positive for baseline; the negative IC issue appears concentrated in the top drawdown windows, not every `vix>=0.8 or drawdown<=-10%` stress date.
- Recommended next step:
  stop sector-neutral stress alpha as formulated; focus on narrower drawdown-onset / crash-state detection and exposure/beta risk control, or add a true alpha-confidence channel inside the optimizer if confidence weighting is needed.
- Crash-onset exposure/beta control test completed without changing alpha rankings, optimizer normalization, sector-neutral alpha, or RL.
- Artifacts saved:
  `artifacts/reports/crash_onset_control.md`,
  `artifacts/reports/crash_onset_events.csv`.
- Tested variants:
  `baseline_v1`, `crash_onset_exposure_50`, `crash_onset_exposure_60`, `crash_onset_beta_cap_075`, `crash_onset_exposure_60_plus_beta_cap`.
- Result:
  no crash-onset variant improved MaxDD or 2020/2022 drawdowns; all remained around `MaxDD=-37.06%`.
- Trigger diagnostics:
  `576` trigger days, `11.27%` trigger-day share, `75.17%` false-positive rate, `41.75%` missed-crash rate.
- Conclusion:
  current crash-onset formulation is too broad and too late; do not adopt as production default.
- Recommended next step:
  design a narrower crash detector around actual rebalance timing and early drawdown inflection, then re-test before adding any production risk overlay.
- Intraperiod risk-control overlay test completed without changing alpha rankings, optimizer, regime switching, or RL.
- Artifact saved:
  `artifacts/reports/intraperiod_risk_control.md`.
- Tested variants:
  `baseline_v1`, `intraperiod_overlay`, `drawdown_brake`, `intraperiod_overlay_plus_drawdown_brake`, plus diagnostic `entry_smoothing` and `all_controls`.
- Result:
  `intraperiod_overlay` passed the gate with `CAGR=23.53%`, `Sharpe=1.334`, `MaxDD=-30.42%`, `2020 DD=-22.27%`, `2022 DD=-30.42%`.
- `intraperiod_overlay_plus_drawdown_brake` also passed with `CAGR=16.86%`, `Sharpe=1.168`, `MaxDD=-23.27%`.
- `all_controls` had the best drawdown at `MaxDD=-22.87%` but CAGR was close to the floor at `16.19%`.
- Drawdown brake alone improved MaxDD to `-25.49%` but failed the CAGR gate at `12.81%`; do not use it alone.
- Entry smoothing alone helped only modestly (`MaxDD=-34.35%`) and did not pass the MaxDD gate.
- Important caveat:
  this is a daily return overlay on realized baseline returns; before production adoption, implement the overlay in the execution/backtest path with explicit cash or SPY hedge mechanics and transaction-cost/slippage assumptions.
- Recommended next step:
  productionize the sparse intraperiod shock overlay first, then separately test whether the drawdown brake is worth keeping once execution and costs are modeled.
- Production intraperiod overlay was implemented in the real walk-forward engine as an opt-in config block:
  `intraperiod_risk.enabled`.
- Named production overlay config:
  `config/baseline_v1_intraperiod_overlay_sp100.yaml`.
- Production comparison artifacts saved:
  `artifacts/reports/production_intraperiod_overlay.md`,
  `artifacts/reports/production_intraperiod_overlay_summary.csv`,
  `artifacts/reports/production_intraperiod_overlay_events.csv`.
- Implementation details:
  SPY/VIX shock is measured at prior close and executed at the next trading day's open; active overlay scales target stock weights to `60%` and leaves the residual in cash.
- Production result:
  baseline `CAGR=17.30%`, `Sharpe=0.917`, `MaxDD=-37.06%`;
  overlay `CAGR=16.25%`, `Sharpe=0.894`, `MaxDD=-34.61%`.
- Production overlay did not pass the full gate:
  MaxDD remained worse than `-32%` and Sharpe fell below `0.9`, though 2020 drawdown improved from `-37.06%` to `-33.18%`.
- Main failure mode:
  one-day enter/exit behavior increased churn; trade count rose from `5769` to `8237`, and total execution costs rose from about `$29.5k` to `$37.5k`.
- Recommended next step:
  do not adopt current production overlay as default; test hysteresis/min-hold exits or a SPY hedge sleeve that avoids repeatedly scaling the full stock book.
- Intraperiod overlay hysteresis test completed without changing alpha, optimizer, or RL.
- Artifact saved:
  `artifacts/reports/intraperiod_overlay_hysteresis.md`.
- Tested variants:
  `baseline_v1`, `overlay_hysteresis_3d`, `overlay_hysteresis_5d`, `overlay_hysteresis_10d`,
  `overlay_hysteresis_5d_cooldown_3d`, `overlay_hysteresis_5d_cooldown_5d`.
- Hysteresis mechanics:
  same entry trigger as current overlay, exit requires both `SPY 5d > -2%` and `VIX 3d < +15%`,
  min-hold/cooldown variants, and a `60% -> 75% -> 90% -> 100%` restore ramp.
- Result:
  no hysteresis variant passed the full gate because trade counts remained above the current overlay reference.
- Best candidate:
  `overlay_hysteresis_10d` with `CAGR=16.95%`, `Sharpe=1.005`, `MaxDD=-32.37%`,
  `2020 DD=-25.02%`, `2022 DD=-32.19%`, but trade count `9264` and cost about `$37.6k`.
- Main conclusion:
  hysteresis improves drawdown and Sharpe, but longer holds plus daily restore-ramp trades do not solve churn.
- Recommended next step:
  stop full-book scaling variants for now; test either a no-ramp/fixed-hold exposure rule or a SPY hedge sleeve that avoids repeatedly trading the entire stock book.
- Phase A.1 volatility/risk-premium robustness validation completed.
- Artifacts saved:
  `artifacts/reports/phase_a1_volatility_robustness.md`,
  `artifacts/reports/volatility_ic_by_period.csv`,
  `artifacts/reports/volatility_ic_by_regime.csv`,
  `artifacts/reports/volatility_selection_sweep.csv`,
  `artifacts/reports/volatility_directionality.csv`,
  `artifacts/reports/volatility_portfolio_backtests.csv`.
- Universes tested:
  `sp100_sample` and `sp500_dynamic`; optional `config/universes/top_200_liquid.yaml` was not present and was skipped.
- Directionality result:
  high-vol/risk-premium direction passed; low-vol/quality direction was negative across sp500 periods and should not be used.
- IC robustness:
  `sp100` high-vol mean period IC `0.0379`, positive in `4/5` periods, average top-bottom spread `1.55%`;
  `sp500` high-vol mean period IC `0.0259`, positive in `5/5` periods, average top-bottom spread `1.23%`.
- Selection result:
  Top-10 had the best forward-return selection edge on both universes; sp500 Top-10 excess forward return was about `2.03%` per rebalance.
- Portfolio result:
  sp500 high-vol Top-N variants beat equal-weight on CAGR but had much worse drawdowns and weaker Sharpe;
  Top-50 EW had `CAGR=18.93%`, `Sharpe=0.596`, `MaxDD=-63.78%` versus equal-weight `CAGR=16.49%`, `Sharpe=0.779`, `MaxDD=-49.12%`.
- Optimizer/risk result:
  sp500 high-vol optimizer+risk reduced drawdown to `-57.79%` but still had weak Sharpe `0.583`; not production-clean.
- Optimizer numerical patch:
  `PortfolioOptimizer` now wraps the repaired covariance matrix with `cp.psd_wrap` before `quad_form`, eliminating repeated CVXPY ARPACK PSD-certification exceptions observed during sp500 Phase A.1.
- Current decision:
  `volatility_score` is real alpha, not just a sp100 artifact, but current portfolio expression is too crash/beta-heavy for production. Keep RL disabled and do not resume momentum-first work.
- Recommended next step:
  design a controlled-beta/crash-aware expression of the validated high-vol alpha, or return to feature engineering if the alpha cannot survive risk control.
- Phase A.2 portfolio-expression experiment completed.
- Artifacts saved:
  `artifacts/reports/portfolio_expression_results.md`,
  `artifacts/reports/portfolio_expression_results.csv`,
  `artifacts/reports/beta_targeting_results.csv`,
  `artifacts/reports/vol_scaling_results.csv`,
  `artifacts/reports/hedge_comparison.csv`,
  `artifacts/reports/portfolio_expression_benchmarks.csv`.
- Tested without changing the alpha:
  beta-targeted long-only weights, equal/inverse-vol/alpha-vol weighting, regime-aware exposure scaling, sector-balanced selection, and explicit SPY hedge variants.
- sp500 result:
  no variant met the hard gate of `MaxDD < 40%` and Sharpe above equal-weight.
- Best sp500 Sharpe:
  `sector_balanced_top_20_beta_target_0.7_exposure_scaled` with `CAGR=16.29%`, `Sharpe=0.753`, `MaxDD=-46.32%`; equal-weight Sharpe was `0.779`.
- Best drawdown-controlled sp500 hedge:
  `sector_balanced_top_20_spy_hedge_beta_1.0_exposure_scaled` with `CAGR=13.58%`, `Sharpe=0.727`, `MaxDD=-35.88%`.
- Best high-CAGR sp500 expression:
  `top_20_equal_weight_exposure_scaled` with `CAGR=22.08%`, `Sharpe=0.700`, `MaxDD=-52.73%`.
- Important critique:
  SPY hedging controls drawdown but gives up too much return/Sharpe; long-only beta targeting preserves return but cannot truly hit low beta targets and leaves drawdown too high.
- Current decision:
  stop standalone volatility-sleeve tuning for now. Keep `volatility_score` as a validated alpha component, but move next to multi-factor blending before Phase B/C/RL.

### 2026-05-02 — Phase D.5 + D.6 Complete

#### Phase D.5 — RL PPO Training
- Training completed with early stopping at episode 66 (patience=50), total time ~40 min.
- Best validation Sharpe: `1.1163` (achieved around episode 11–12, then plateaued).
- Final model saved: `artifacts/models/rl_ppo_final.zip`; best checkpoint: `artifacts/models/rl_ppo_best.zip`.
- Training log: `artifacts/reports/phase_d5_training_log.csv`.

#### Phase D.6 — Four-Way Holdout Comparison (2019–2026-04-24)
- Run date: 2026-05-02 09:27:33 UTC.
- Sanity check PASS: no-op Sharpe `1.245` vs B.5 locked `1.270` (diff `0.025` < `0.05` threshold).

| Policy | CAGR | Sharpe | MaxDD | Avg tilt |
|---|---|---|---|---|
| B.5 locked | 20.69% | 1.270 | -32.98% | — |
| RL no-op | 20.33% | 1.245 | -32.98% | 0 |
| Random bounded (50 seeds) | 17.72% | 1.321 | -27.04% | 0.014 |
| **Trained RL** | **17.40%** | **1.295** | **-24.90%** | **0.012** |

- **Verdict: REJECT trained RL. Keep B.5 as production system.**
- Failing gate: trained RL Sharpe (`1.295`) did not beat random bounded (`1.321`).
- Gates passed: Path A (Sharpe ≥ 1.270, MaxDD ≥ -32.98%) ✅, Path B ✅, 50 bps Sharpe `1.203` ≥ 0.90 ✅, beats no-op ✅.
- Notable positives: trained RL shows genuine tail improvement — MaxDD `-24.90%` vs B.5 `-32.98%` (8pp better); 2020 COVID crash regime Sharpe `0.81` vs B.5 `0.44`.
- Root cause of REJECT: the RL policy adds value over no-op (+0.05 Sharpe) but cannot demonstrate skill above a random bounded tilt policy, indicating the learned tilt structure is not meaningfully better than noise within the bounded action space.
- Artifacts: `artifacts/reports/phase_d6_rl_evaluation.md`, `d6_policy_comparison.csv`, `d6_regime_breakdown.csv`, `d6_promotion_gates.csv`.

#### Phase D — Status and Next Steps
- Phase D is functionally complete. The RL overlay experiment was run to conclusion.
- B.5 (`b4_stress_cap_trend_boost`, sp500, 2008–2026) remains the locked production system: CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`.
- Phase D CLOSED. Root cause: sector-tilt action space too constrained for genuine regime switching.

### 2026-05-02 — Phase E Implementation (E.1–E.6 complete)

Phase E redesigns the RL action space from sector tilts (12-dim, ±15%) to explicit exposure control
(3-dim: equity/trend/cash target proportions via simplex projection).

#### Key Design Decisions (Final Agreed Spec)

1. **Action space:** 3-dim raw ∈ [−1,+1] mapped to target proportions (equity ∈ [0.25,1.0],
   trend ∈ [0.0,1.0], cash ∈ [0.0,0.60]) via simplex projection so all three always sum to 1.0.
   Simplex projection (not independent normalization) ensures cash is not silently absorbed when
   equity + trend > 1.0.

2. **State vector:** 42-dim (vs 14-dim in Phase D). New groups added:
   - Size/style spreads: IWM−SPY and QQQ−SPY 63d momentum (dims 5–6)
   - Trend asset returns: TLT/GLD/UUP 3m+6m (dims 7–12)
   - Sector momentum vs SPY for 11 SPDR sectors (dims 14–24) from `sector_features.parquet`
   - Sector volatility 63d for 11 sectors (dims 25–35) from same parquet
   - Portfolio exposure fracs (dims 36–38) and portfolio risk (dims 39–41)

3. **Reward (5 terms):**
   - Term 1: `sharpe_63d` (63d vs 21d in Phase D; longer to capture regime transitions)
   - Term 2: `+0.10 × recovery_bonus` (incentivises re-risking after trough)
   - Term 3: `−0.15 × max(0.0, −drawdown_from_peak)` — CORRECTED sign (Phase D bug had `max(0, drawdown)` always 0)
   - Term 4: `−0.03 × cash_frac × bull_indicator` (fires only when spy_trend_positive AND stress < 0.30)
   - Term 5: `−0.02 × |equity_frac − prev_equity_frac|` (churn penalty)

4. **Five-way E.6 comparison:** B.5 locked / RL no-op / random bounded (50 seeds) / **rule-based VIX+SPY controller** / trained Phase E RL.
   - Rule-based: tier-1 (vix_pct > 0.75 OR spy_dd < -0.15) → 50/40/10; tier-2 (vix_pct > 0.50 OR spy_ret_3m < 0) → 70/20/10; benign → 85/10/5.
   - Why VIX + SPY (not VIX-only): SPY drawdown catches sustained bear markets where VIX has normalized but prices remain depressed.

5. **Random gates:** median = hard minimum (Gate 5), p75 = preferred (Gate 6, conditional pass if failed but median passes). NOT p95.

6. **No walk-forward retraining** in Phase E. Fixed window: 2008–2016 train, 2017–2018 val. Walk-forward deferred.

#### Files Implemented

| File | Phase | Status |
|---|---|---|
| `src/rl/state_builder_v2.py` | E.1 | ✅ Complete |
| `src/rl/exposure_mix.py` | E.2 | ✅ Complete |
| `src/rl/reward_v2.py` | E.3/E.4 | ✅ Complete |
| `src/rl/environment_v2.py` | E.3 | ✅ Complete |
| `scripts/train_rl_v2.py` | E.5 | ✅ Complete |
| `scripts/run_rl_backtest_v2.py` | E.6 | ✅ Complete |

#### E.5 Training Results (2026-05-03)

- sp500, 2008–2016 train / 2017–2018 val.
- Best val Sharpe: `1.0746` at episode 13; early stopping at episode 63 (patience=50).
- Total time: ~82 min. Model: `artifacts/models/rl_e_ppo_best.zip`.
- Training log: `artifacts/reports/phase_e5_training_log.csv`.

#### E.6 Evaluation Results (2026-05-03) — CONDITIONAL PROMOTE

Five-way holdout (2019-01-01 → 2026-04-24, 10 bps):

| Policy | CAGR | Sharpe | MaxDD | Avg equity |
|---|---|---|---|---|
| B.5 locked | 20.69% | 1.270 | −32.98% | — |
| RL no-op | 17.95% | 1.058 | −29.28% | 1.000 |
| Rule-based (VIX+SPY) | 18.25% | 1.083 | −30.08% | 0.696 |
| Random (50 seeds) | 18.46% | 1.218 mean / 1.206 median / 1.279 p75 | −25.90% | — |
| **Trained Phase E RL** | **16.86%** | **1.275** | **−21.73%** | **0.365** |

- All hard gates pass: Path A (Sharpe ≥ 1.270 AND MaxDD ≥ −32.98%) ✅, Path B ✅, 50 bps Sharpe `1.208` ≥ 0.90 ✅, beats no-op ✅, beats random median ✅, beats rule-based ✅, no blowup ✅.
- Missed p75 preferred gate by `0.004` (1.275 vs 1.279) ❌ → CONDITIONAL (not clean) promote.
- Key strength: tail protection. 2020 COVID Sharpe `0.888` vs B.5 `0.435`. MaxDD `−21.73%` vs B.5 `−32.98%` (11pp improvement).
- Key concern: avg equity `0.365` — RL is over-defensive; CAGR sacrifice `3.83pp`. The `λ_dd=0.15` drawdown penalty likely dominates the reward.
- B.5 remains the production system. RL v2 model is a tail-protection overlay candidate.
- Artifacts: `artifacts/reports/phase_e6_rl_evaluation.md`, `e6_policy_comparison.csv`, `e6_regime_breakdown.csv`, `e6_promotion_gates.csv`, `e6_random_distribution.csv`.

#### Phase E.7 — PROMOTE (2026-05-03)

E.7 reward calibration fixed the over-defensiveness diagnosed in E.6:
- `λ_dd` 0.15→0.08, `λ_cash` 0.03→0.05, `bull_regime` removes `stress<0.30` gate, cash cap 0.60→0.50.
- Drawdown definition (expanding all-time-high peak) intentionally unchanged.

Training: best val Sharpe `1.0761` at episode 51; early stopping episode 101 (~132 min). Model: `artifacts/models/rl_e_ppo_best.zip`.

Five-way holdout (2019-01-01 → 2026-04-24, 10 bps): Sharpe `1.296`, MaxDD `−24.48%`, CAGR `17.79%`, avg equity `0.406`. All 8 gates pass incl. p75 (`1.296 > 1.280`). CAGR sacrifice `2.9pp` vs B.5. 2019 bull `3.18` (improved), 2020 COVID `0.63` (weaker than E.6's `0.89` — accepted trade-off).

**Phase E CLOSED — PROMOTE.** E.8 deferred: if further tuning needed, test rolling 252d peak drawdown definition instead of expanding all-time-high.

#### Phase E.8 — REJECT (2026-05-03)

E.8 hypothesis: expanding all-time-high creates a permanent scar keeping RL over-defensive; rolling 252d peak would make penalty forward-looking and allow re-risking in recovery.

Change tested: `portfolio_nav.expanding().max()` → `portfolio_nav.rolling(252, min_periods=1).max()` in `reward_v2.py`.

Training: best val Sharpe `1.0923` at episode 49; early stopping episode 99 (~128 min).

Five-way holdout (2019–2026-04-24, 10 bps): Sharpe `1.277`, MaxDD `−24.54%`, avg equity `0.396`. 7/8 gates — p75 gate **fails** (`1.277 < 1.280`). Regression on all dimensions vs E.7 (Sharpe −0.019, avg equity −0.010).

Hypothesis disproved: rolling peak resets faster in recovery regimes, creating fresh penalties earlier → RL more defensive in 2021/2023 bull phases (2021 Sharpe 1.593 vs B.5's 2.420). `reward_v2.py` reverted to E.7 state. E.7 remains the production model.

**Conclusion:** avg equity ~0.40 is likely the policy's correct posture for 2019–2026, not a fixable bug. The CAGR sacrifice is the price paid for MaxDD improvement. Proceed to F.1 (Top-N sensitivity) if higher CAGR is desired.

#### Useful Commands (Phase E)

- Re-run evaluation: `.venv/bin/python scripts/run_rl_backtest_v2.py`
- Full retrain (sp500): `.venv/bin/python scripts/train_rl_v2.py`
- Smoke test: `.venv/bin/python scripts/train_rl_v2.py --total-timesteps 2000 --eval-freq 500 --universe config/universes/sp100.yaml`

### 2026-05-03 — Phase F.1 Complete

#### Phase F.1 — Top-N Sensitivity Under E.7 RL — REJECT all alternatives (2026-05-03)

Goal: test whether changing equity sleeve breadth (Top-N) improves CAGR without sacrificing
the E.7 drawdown advantage. No reward change, no RL retraining in F.1a.

Script: `scripts/run_phase_f1_topn_sensitivity.py` — sp500, holdout 2019-01-01→2026-04-24, 10 bps, 20 random seeds per variant.

**Model checkpoint note:** `rl_e_ppo_best.zip` is the E.8 checkpoint (E.7's file was
overwritten during E.8 training; not recovered). Evaluated with E.7 expanding-peak
reward environment. Top-20 internal baseline = Sharpe `1.277` (vs E.7 published `1.296`).
All four variants use the same checkpoint — comparison is internally consistent.

**F.1a results (RL, 10 bps holdout):**

| Top-N | Sharpe | MaxDD | CAGR | 50bps Sharpe | Avg equity | Rand p75 |
|---|---|---|---|---|---|---|
| 10 | 1.217 | −25.69% | 18.39% | 1.119 | 0.396 | 1.194 |
| 15 | 1.199 | −27.48% | 17.43% | 1.095 | 0.395 | 1.196 |
| **20 (baseline)** | **1.277** | **−24.54%** | **17.72%** | **1.165** | **0.396** | **1.275** |
| 30 | 1.209 | −24.14% | 16.19% | 1.093 | 0.396 | 1.204 |

**B.5 no-RL by Top-N (10 bps holdout):** Top-10: 1.191/−33.93%/21.02%, Top-15: 1.158/−36.58%/19.84%, Top-20: 1.270/−32.98%/20.69%, Top-30: 1.242/−32.67%/19.60%. RL drawdown advantage preserved (~8–10pp) across all Top-N.

**Gate results (all non-20 REJECT):**
- Top-10: Sharpe gate FAIL (1.217 < 1.270). CAGR (+0.67pp vs Top-20) and rand p75 pass. Concentrated book hurts Sharpe.
- Top-15: Sharpe FAIL + MaxDD FAIL (−27.48% just under −27% gate). Not material vs Top-20.
- Top-30: Sharpe FAIL + CAGR FAIL (16.19% < 17.79%). Dilution hurts both metrics.

**Key findings:**
- Avg equity ~0.396 is stable across all Top-N — RL posture is insensitive to breadth.
- RL Sharpe is highest at Top-20 because the policy was trained with Top-20 weights.
- Top-10 shows CAGR benefit but idiosyncratic risk exceeds the RL's hedging capacity.

**F.1b: No retrain recommended.** Top-20 remains the optimal breadth.

**Phase F.1 CLOSED — Top-20 confirmed.** Next step: if CAGR improvement still desired, consider Phase F.2 (walk-forward RL retraining with the current E.7 reward setup) or Phase F.3 (signal enhancement on the volatility_score alpha).

Artifacts: `artifacts/reports/phase_f1_topn_sensitivity.md`, `f1_topn_comparison.csv`, `f1_regime_breakdown.csv`, `f1_sector_concentration.csv`.

Run command: `.venv/bin/python scripts/run_phase_f1_topn_sensitivity.py`

### 2026-05-04 — Phase F.2 Complete + Phase G/H/PROD Plans Created

#### Phase F.2 — Clean E.7 Retrain — PROMOTE (2026-05-04)

**Context:** `rl_e_ppo_best.zip` was contaminated by E.8 training (rolling 252d peak, rejected).
F.2 retrains E.7 exactly, with explicit lambda pinning in `train_rl_v2.py` to lock in the
effective values (env defaults, not reward_v2.py function defaults).

**Lambda bug resolved:** `reward_v2.py` advertises `lambda_dd=0.08, lambda_cash=0.05` as function
defaults, but `PortfolioEnvV2.__init__` defaults are `0.15 / 0.03` and passes `self.lambda_*` to
the reward function — overriding the function defaults. Training never explicitly set these, so
E.7 was effectively trained with `0.15 / 0.03`. F.2 pins this explicitly as
`LAMBDA_DD_E7_EFFECTIVE=0.15`, `LAMBDA_CASH_E7_EFFECTIVE=0.03` in `train_rl_v2.py`.

**Training outcome:** Best checkpoint at ep=51 (val_sharpe=1.0761 on 2017–2018 val window).
Process was killed by session reset before final model save, but best checkpoint was already
written to `rl_e_ppo_best.zip` at 07:35.

**Holdout evaluation (2019–2026-04-24, 10 bps):**

| Metric | Value | Gate | Pass |
|--------|-------|------|------|
| Sharpe | 1.296 | ≥ 1.270 | ✅ |
| MaxDD | -24.48% | ≥ -32.98% | ✅ |
| 50 bps Sharpe | 1.179 | ≥ 1.0 | ✅ |
| MaxDD hard floor | -24.48% | ≥ -35% | ✅ |

Checkpoint reproduces original E.7 exactly (seed=42, same lambdas, same training window).

**Phase F CLOSED — PROMOTE.** `rl_e_ppo_best.zip` is now a clean E.7 checkpoint.

#### Phase G/H/PROD Plans Created (2026-05-04)

Production deployment plan split into three phases:
- **Phase G** (`docs/phases/phase_g.md`): Production infrastructure — feature parity check (G.0),
  signal gen pipeline (G.1), audit trail (G.2), drift monitoring (G.3), dual-mode switching (G.4),
  benchmark dashboard (G.5).
- **Phase H** (`docs/phases/phase_h.md`): Paper trading — 8–12 week forward test, daily ops
  schedule, 8 exit gates (slippage < 20 bps, pipeline reliability, RL mode operational, etc.).
  Recommended broker: Alpaca for Phase H.
- **Phase PROD** (`docs/phases/phase_prod.md`): Live capital deployment — `$[BUDGET]` placeholder
  (min ~$25K), 4-week capital ramp (25%→50%→75%→100%), circuit breakers (15% HWM drawdown →
  liquidate, 2-day pipeline failure → hold), T+1 execution, quarterly retrain gate.

**Next active phase: Phase G** — build production infrastructure starting from G.0 feature parity.

Useful commands:
```bash
# Holdout evaluation (trained RL only, ~70s):
.venv/bin/python scripts/run_rl_backtest_v2.py --policy trained

# Full 5-way holdout comparison (~15 min with 50 random seeds):
.venv/bin/python scripts/run_rl_backtest_v2.py --policy all
```
