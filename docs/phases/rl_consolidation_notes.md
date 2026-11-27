# RL consolidation notes (2026-11-27)

Branch `worktree-agent-a1e39ad77fd1df684`, branched from `exp/no-tlt` at `33f54bb`. One commit per logical unit.
The tracker `docs/phases/rl_allocator_experiments.md` is owned by the main agent and was not edited.

## 1. What was merged

| Commit | Source worktree | Content | Behaviour change |
|---|---|---|---|
| R0 `2bed70e` | agent-a223e0fd173eee9c6 | `src/rl/reward_config.py`; `train_rl_v2.py` writes `reports/run_manifest.json`; `tests/test_r0_reward_guard.py` | None (manifest is new output) |
| A0 `ed8ab62` | agent-a7389e2fe3dfbf490 (tests, scripts, TIMING) + new env options | `PortfolioEnvV2(fill_delay, terminal_period, require_book)`; train CLI flags; `scripts/a0_*.py`; `tests/test_a0_{action,timing,env_options}.py`; `docs/phases/rl_a0_timing.md` | None by default (see section 2) |
| A0/C1 | agent-a5162ab49bcbd8f9f (identical in A0) | `apply_two_sleeve_mix` excludes NON_TRADABLE assets from equity scaling | Only snapshots containing SPY change; those previously raised AssertionError |
| C1 `9929cce` | agent-a5162ab49bcbd8f9f | `tests/test_c1_spy_snapshot.py` (moved from test_a0_action) | None |
| FH `5345eda` | agent-a6cfacb3e016cf4f0 (FC, FB not used where superseded) | `features_risk_v4.py`, `features_v4_{env,history,manifest,meta,screen,targets}.py`, 5 `scripts/features_v4_*.py`, 7 `tests/test_features_v4_*.py`, helpers and conftest | None (library not wired into training) |
| BD `4be4cfd` | agent-a41c358bf0f41c224 | `bd_core.py`, `bd_learners.py`, `scripts/bd{0,1,2}_*.py`, 2 test modules | None (analysis code) |
| Docs (this commit series) | n/a | `rl_feature_certification.md` (amended), `rl_shadow_mode.md`, this file | None |
| Cleanup | n/a | 3 tracked `__pycache__` `.pyc` removed from index; `.gitignore` gains `runs_*/`, `*.pkl`, `*.parquet` | None |

Not copied: `runs_*/` outputs, `runs_a0/cache` (808 MB), `runs_fh/` (148 MB), `runs_bd/` (53 MB), `data` symlinks,
materialised parquet/pickle files.

## 2. Defaults changed

None. Every new option defaults to the legacy behaviour:

- `PortfolioEnvV2(fill_delay=0)`: fill at close t (legacy). Spec M2 requires `fill_delay=1`; owner decision.
- `terminal_period=False`: last decision period is not simulated (legacy). Spec M8 requires it; owner decision.
- `require_book=False`: 14d grid may start on 2008-01-02, before the first non-empty B.5 snapshot (2008-01-07),
  and the empty-book date reports equity (defect D1). The fix is opt-in.
- Cost: `--train-cost-bps 0` and `--val-cost-bps 0` (legacy). Eval and prod use 10 bps. **Owner decision:**
  training at 0 bps means the agent never pays turnover cost in training. Recommended: 10 bps for both.
- `tests/features_v4_helpers.require()`: missing `runs_fh/` artifacts now SKIP by default (were failures). Set
  `V4_REQUIRE_ARTIFACTS=1` to fail. Owner decision: keep the skip or make CI always require artifacts.
- `tests/test_bd_*`: skip when `runs_bd/inputs` is absent (new gate).

If any default is flipped, record the change in the commit that flips it and update the table above.

## 3. Not merged, and why

- R1 `apply_multiplier_mix`, `action_mode=mult`, `reward_v2.compute_reward_bl`, `r1_*.py`: failed pre-registered bars
  (tracker section 19); not a consolidation target.
- C1 observation variants O1-O3 (`state_builder_c1.py`, `obs_version`, `aggregate_c1.py`, `run_c1_eval.py`):
  failed all bars (section 20). Kept out of the consolidated code; the branch keeps the SPY fix only.
- C1 `environment_v2`/`reward_v2` changes and `state_builder_v3.py`: tied to O1-O3; not merged.
- FC certification tests `nulls` and `sitems` and `fc_cert_lib.py`: not ported. FH superseded the causality,
  stats and targets tests. `nulls` depends on FC outputs (`runs_fc/`), `sitems` on the S1-S4 checks. Open item.
- FB (`agent-af86d15771da1cf40`): superseded by FH (v4 -> v4.1 fixes, documented in tracker section 18).
- FH `environment_v2.py`, `exposure_mix.py`, `train_rl_v2.py` edits: none beyond the base; no v4 wiring.
- A0 `runs_a0/TIMING.md` moved to `docs/phases/rl_a0_timing.md`. The A0 defects D1-D4 are implemented as options
  (section 2), not as default fixes.
- Rejected: any change to `scripts/run_prod_signal.py` (production task).
- `config/paper_trading_j2.yaml` is tracked and referenced by `docs/phase_h_j2_analysis.md` and the journey
  pipeline; kept. The brief's j2k/j2m/j2n/j2r/j2s configs are not tracked, so nothing was removed.
- `rl_redesign_plan.md` and `rl_bandit_plan.md` are not in this branch's `docs/phases/` (the tracker's section 27
  cites `rl_bandit_plan.md`). Not added; owner to confirm where these live.

## 4. Open items

1. M2 (decision timing): spec amendment is written in `rl_feature_certification.md` section 0. The env still
   defaults to fill at close t. Any RL result reported as evidence must run with `--fill-delay 1`.
2. Causality sweep (100 dates, `test_causality_full_sweep_100_dates`) and deterministic rebuild
   (`test_deterministic_rebuild`, `test_history_build_is_deterministic`, needs BK/CTRA network): see sign-off table
   for the status of each run.
3. Env wiring not done: `state_builder_v2` still reads episode NAV (dims 39-41, the own-NAV defect). `build_state_v4`
   is not called from training.
4. Survivorship: raw stocks are current S&P 500 constituents; index membership history is absent before 2015 (95
   names start after 2008, 47 after 2015). Survivorship bias before 2015 is unmeasurable with this data.
5. S1 redundancy/VIF fails on volatility features (FH waiver). The 48-feature set needs a representative pick per
   cluster before any RL experiment.
6. Feature certification sign-off is not complete. No feature enters RL until `rl_feature_certification.md` section 3
   shows PASS on all MUST items.
7. Tracker sections 15-27 exist only in the main checkout (uncommitted). The branch does not include the tracker.
8. Large tracked files (listed in the final report): three CSV/log artifacts in `artifacts/reports/` exceed 5 MB.
   Not deleted.
