# RL feature set certification gate (v4)

Status: NOT CERTIFIED (2026-11-27). Gate between feature construction (track FB/FH) and the feature-selection experiment (track FS). No feature enters an RL experiment until the set is CERTIFIED here. The sign-off table in section 3 is the current state; the verdict in tracker section 18 (FH) stands.

## 0. Decision-timing convention (spec amendment, M2 and M8)

This section replaces the timing wording in M2 and M8. It is the convention every certified result must use.

- Decision at close t: the observation uses data available at the close of t (prices, B.5 snapshot dated <= t, same-day VIX only if the VIX timing check below passes).
- Fill at close t+1: the book chosen at t is held from close t+1. The period (t, t+1] earns the previous book. The turnover of the new book is charged at the fill.
- The last decision's period is simulated to min(end, last price date) (terminal period, M8).
- Cost: 10 bps on turnover for evaluation. Training uses the same cost (owner decision pending; see `rl_consolidation_notes.md`).

What the environment does today (`src/rl/environment_v2.py`, branch commit `ed8ab62`):

| Convention | Default (legacy) | Option that implements the spec | Train/CLI flag |
|---|---|---|---|
| Fill timing | fill at close t (`fill_delay=0`) | `fill_delay=1` | `--fill-delay 1` |
| Last period | not simulated (`terminal_period=False`) | `terminal_period=True` | `--terminal-period` |
| Grid start | may precede the first non-empty B.5 snapshot (`require_book=False`) | `require_book=True` | `--require-book` |
| Cost, training | 0 bps (`cost_bps=0`) | `cost_bps=10` | `--train-cost-bps 10` |
| Cost, validation | 0 bps | `cost_bps=10` | `--val-cost-bps 10` |

The defaults above are legacy and are not certified. A result reported as certification evidence must
state the flags it ran with, and the M2 items below must be true for those flags.

Amendment to M2: the spec requirement "orders executed t+1 as in the env" was wrong for the env as built.
The env fills at close t (the FC/FH finding). M2 is satisfied only when the run uses `fill_delay=1`. The
library itself has no fill dependency: its features use data through t and its targets are forward from t.

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
Evidence run 2026-11-27 on branch commit `5345eda` plus later commits, with the FH materialised outputs (`runs_fh/features_v4_1/`, 148 MB, not committed) linked locally. Fast: `pytest -q -m "not slow" tests/test_features_v4_*.py` = 46 passed. Slow: `pytest -q -m slow tests/test_features_v4_*.py` = 5 passed (14.6 min). Without the artifacts, these tests skip (set `V4_REQUIRE_ARTIFACTS=1` to fail).

| Item | Status | Evidence (test names; slow marked) | Reviewer |
|---|---|---|---|
| M1 | PASS | `test_no_lookahead_truncation`, `test_future_corruption_invariance`, `test_leak_detector_catches_injected_leak`; 100-date sweep `test_causality_full_sweep_100_dates` (slow, PASS) | |
| M2 | OPEN | Env fills at close t: `test_env_fill_convention_is_close_of_decision_date` codifies the legacy convention, not t+1. `test_vix_same_day_convention` passes but VIX publication lag is not verifiable from the repo; adj_close vintage not verifiable. Amendment written (section 0). `fill_delay=1` option exists but is not the default. | |
| M3 | PARTIAL | Library: `test_path_independence_mid_history_start`, `test_no_episode_local_state` PASS. Existing env: FAIL (`state_builder_v2` reads episode NAV, dims 39-41; FC xfail `test_existing_env_observation_has_no_episode_nav` not ported). | |
| M4 | PASS | `test_causal_normalisation`, `test_warmup_nan_policy`. Coverage caveat: first complete-case date 2008-10-31; 2008-09 has NaN for 505 days in some features. | |
| M5 | PARTIAL | Store vs prod-path parity `test_train_serve_parity_one_rebalance_date` PASS (2015-06-12, 1e-9). Env observation vs prod: NOT TESTED (`build_state_v4` not wired into training). | |
| M6 | PASS | `test_manifest_row_counts_and_checksums`, `test_manifest_input_hashes_and_library_hash`, `test_no_constant_or_duplicate_columns`; deterministic rebuild `test_deterministic_rebuild` (slow, PASS) and `test_history_build_is_deterministic` (slow, PASS). FC note: rebuild matched only with PYTHONHASHSEED=0 and one BLAS thread; not re-checked for FH. | |
| M7 | PASS with flags | `test_distribution_regression_by_block`, `test_outlier_flag_clip_is_documented` PASS. ADF is custom; flags on `rv_s_63`, `ewdn_u_126` unstable across builds (FH). | |
| M8 | PARTIAL | Target construction PASS: `test_targets_forward_only_no_overlap`, `test_target_nan_policy_and_last_period`, `test_targets_match_h1_8w_cache`, `test_embargo_removes_two_decisions_each_side`. Embargo inside the LORO screen: FC found none; not separately re-verified for FH. | |
| M9 | PASS (power-limited) | `test_leak_detector_catches_injected_leak`, `test_block_permuted_feature_has_no_ic`, `test_stationary_perm_null_is_centred`, `test_noise_feature_null_calibration` (slow, PASS), `test_power_curve_reported_and_consistent` (slow, PASS). Minimum detectable delta IC at 80% power about 0.24. | |
| M10 | PASS (library) / FAIL (env) | `test_library_reads_no_agent_state`, `test_build_state_v4_takes_only_equity_share` PASS. Existing env reads own NAV (see M3). | |
| S1 | FAIL (waiver) | `test_clusters_have_one_representative` PASS; VIF > 10 on volatility features remains (FH). | |
| S2 | NOT TESTED | Missing-day handling not tested separately. | |
| S3 | PARTIAL | Full panel ~3.4 s, store read < 1 s (FH measurement; no test). | |
| S4 | PASS | `test_feature_meta_complete`. | |

Survivorship (not a MUST item): raw stocks are current constituents; no index history before 2015 in `data/`; the PIT mask is an ADV filter. Pre-2015 bias is unmeasurable.

## 4. After certification: follow-up experiments (FS)

FS1 Incremental value of each new feature over (a) the FA-cleaned existing set and (b) trailing-volatility predictors (leave-one-regime-out ridge/trees, block-permutation, BH-FDR across all tests, sign consistency across regime blocks).
FS2 Group ablation and add-one-group.
FS3 Freeze v4 (<= 20 dims) with written rationale and the list of dropped features; commit before any RL training.
FS4 RL runs on the frozen v4 set with the R1/C1 harness (3 seeds), then permutation importance on the trained agents.
FS5 Sealed test on 2026-05..11 (masks rebuilt), one shot.
