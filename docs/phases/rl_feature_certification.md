# RL feature set certification gate (v4)

Status: PLAN (2026-11-27). Gate between feature construction (track FB) and the feature-selection experiment (track FS). No feature enters an RL experiment until the set is CERTIFIED here.

## Sequence (strictly gated)

1. FB finishes: candidate library `src/rl/features_risk_v4.py`, materialized full-period table (`runs_fb/features_v4/`), metadata and manifest. FA finishes: keep/drop verdict for the existing 42 dims.
2. EGM review of the feature set (five lenses) against the checklist below: design, code correctness and reuse, simplicity/scope, leakage and failure-mode hunt, implementation readiness. Read-only.
3. Test hardening: fix every confirmed review finding; add the tests listed in section 2; re-run materialization.
4. Certification: all MUST items pass, the sign-off table below is filled with evidence (command + output location), and the feature spec is frozen (version v4, checksum recorded in the manifest).
5. Only then: selection experiment FS (incremental value over the cleaned existing set and over trailing volatility; block-permutation, per-regime, group ablation), then a frozen v4 set (<= 20 dims), then RL runs.

## 1. Certification checklist

MUST items (any failure blocks certification):

M1 Causality / no look-ahead. For every feature and a random sample of >= 100 dates (always including 2008-10, 2020-03, 2022-06): the value computed from the full history equals the value computed from history truncated at that date; corrupting all future data (set prices after the date to NaN or random) leaves the value unchanged. Includes universe membership, B.5 weights and any normalisation statistic.
M2 Availability lag. Every input series has a documented publication/availability lag (e.g. VIX close, ETF adjusted close, any macro series); features use only data available at the decision time (decision at close t uses data through t, orders executed t+1 as in the env); no revised/restated data used.
M3 Continuity / path independence. A value at date t is identical whether computed in a continuous run from 2008, a run started mid-history after the warm-up, or inside a training episode started at any date; no feature depends on an episode-local NAV or counter (the old own-NAV defect).
M4 Normalisation is causal. Z-scores/ranks use expanding or trailing windows ending at t (never whole-sample mean/std/quantiles); winsorisation bounds are causal; warm-up period documented and NaN-handled identically in training, backtest and prod.
M5 Train/serve parity. One function builds the features for env, training, backtest and prod (`features_at(date, history)`); a parity test on at least one historical rebalance date compares env observation vs prod-path observation to 1e-9.
M6 Data integrity. Manifest with row counts, date range, NaN/inf counts per feature, constant-feature check (variance > 0 over each regime block), duplicate-column check (|corr| > 0.999), checksum of the materialized table; regeneration from data/ is deterministic (two builds produce identical checksums).
M7 Statistical sanity per feature. Distribution summary by regime block (min/median/max/quantiles), stationarity check (ADF or rolling-mean drift) and a flag for any feature whose first-valid date is later than 2008 (coverage bias); outlier audit (|z| > 6 events listed and explained, e.g. 2008-10, 2020-03).
M8 Target hygiene. Targets T1-T5 are strictly forward-looking from the decision date to the next decision date (no overlap bug); the last decision's period is handled explicitly; purge/embargo of at least 2 decisions in expanding-window evaluation.
M9 Negative controls. Permuting a feature's time order (block-wise) destroys any IC; a deliberately leaked feature (next-period return injected) is detected by the M1 test (the test must fail on it, proving the test works); a random-noise feature gets IC ~ 0 with block-permutation p-values uniform-ish across 200 draws.
M10 No dependency on the agent. No feature reads the agent's own positions, NAV or actions except the explicit current equity share (and, for the multiplier action, the agent's exposure relative to the a=0 baseline).

SHOULD items (documented if waived):
S1 Redundancy clusters resolved (one representative per cluster at |corr| > 0.95) and VIF < 10.
S2 Robustness to data revisions/gaps: features handle missing days and holidays identically in training and prod.
S3 Runtime budget: feature computation for one decision date under 1 s with cached history.
S4 Documentation: every feature has definition, inputs, lag, warm-up, group, rationale and literature reference where relevant.

## 2. Required test suite (tests/test_features_v4_*.py)

- test_no_lookahead_truncation (M1), test_future_corruption_invariance (M1), test_leak_detector_catches_injected_leak (M9)
- test_input_availability_lags (M2), test_decision_time_alignment_with_env (M2/M8)
- test_path_independence_mid_history_start (M3), test_no_episode_local_state (M3, M10)
- test_causal_normalisation (M4), test_warmup_nan_policy (M4)
- test_train_serve_parity_one_rebalance_date (M5)
- test_manifest_row_counts_and_checksum, test_deterministic_rebuild, test_no_constant_or_duplicate_columns (M6)
- test_distribution_regression: stored summary statistics per regime block must match within tolerance (M7)
- test_target_forward_only_no_overlap, test_embargo_in_cv (M8)
- test_noise_feature_null_calibration (M9)
All tests must run in < 5 minutes on the CI machine; heavy checks (full rebuild, 200-draw null) are marked slow and run in the certification step.

## 3. Sign-off table (filled at step 4)

| Item | Status | Evidence (command, output file, commit) | Reviewer |
|---|---|---|---|
| M1 | pending | | |
| M2 | pending | | |
| M3 | pending | | |
| M4 | pending | | |
| M5 | pending | | |
| M6 | pending | | |
| M7 | pending | | |
| M8 | pending | | |
| M9 | pending | | |
| M10 | pending | | |
| S1-S4 | pending | | |

## 4. After certification: follow-up experiments (FS)

FS1 Incremental value of each new feature over (a) the FA-cleaned existing set and (b) trailing-volatility predictors (leave-one-regime-out ridge/trees, block-permutation, BH-FDR across all tests, sign consistency across regime blocks).
FS2 Group ablation and add-one-group.
FS3 Freeze v4 (<= 20 dims) with written rationale and the list of dropped features; commit before any RL training.
FS4 RL runs on the frozen v4 set with the R1/C1 harness (3 seeds), then permutation importance on the trained agents.
FS5 Sealed test on 2026-05..11 (masks rebuilt), one shot.
