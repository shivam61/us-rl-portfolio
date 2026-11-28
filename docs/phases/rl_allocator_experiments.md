# RL allocator: review findings, experiment tracker, decision log

Status: LIVE document (started 2026-11-26). Branch `exp/no-tlt`, nothing committed yet.
Scope: B.5 (stock picks) is FROZEN and is handled as a separate production-engineering task. This document covers only the RL allocator that decides the equity-vs-cash split of the B.5 book. Rules for the agent: no hand-written rule caps; individual equities only, the remainder is cash; TLT/GLD/UUP remain read-only state signals, SPY/TLT/GLD/UUP are never bought.

Windows (unless stated): train 2008-2016, validation 2017-2018 (checkpoint selection), holdout 2019-2026-04-24 (heavily reused for selection, so optimistic), 3y window 2023-04-25..2026-04-24. All metrics are net of 10 bps. "8w" = the B.5 control-date grid used in training (~every 8 weeks); "14d" = biweekly (prod cadence). "Matched static" = a static policy at the agent's own average equity on the same grid.

Evidence quality tags: V = verified in code or by a direct run; I = inferred.

---

## 1. Headline

1. Across every reward, data, observation and seed variant tried so far, the RL agent has not shown a reliable edge over a static allocation at the same average equity. The agents' in-sample edge is large and does not transfer (section 3).
2. The agent cannot protect capital because the action space does not allow it: cash is capped at 0.5, so equity never goes below 50% on a high-beta book (V).
3. The value in the deterministic B.5 + B.4 risk engine (not RL) comes from its time-varying exposure. The RL setup replaced that exposure control with the agent's own equity share.
4. Decision pending on the running experiments (section 4) and a sealed out-of-sample test (not yet run).

## 2. Reference results (not RL)

| Strategy | Window | CAGR | MaxDD | Sharpe | Sortino |
|---|---|---|---|---|---|
| B.5 + B.4, equity-only (avg gross ~28%) | holdout | 14.1% | -20.4% | 1.10 | 1.65 |
| B.5 + B.4, equity-only | 3y | 21.3% | -8.2% | 2.09 | 3.33 |
| B.5 + B.4, equity-only | 2020 crash window | 7.4% | -17.6% | 0.40 | 0.56 |
| static 50 / 72 / 100% of the book | holdout | 22.5 / 32.0 / 43.3% | -32.7 / -44.1 / -56.3% | 1.05 | 1.56 |
| static 50 / 72 / 100% of the book | 3y | 33.4 / 50.0 / 72.7% | -15.4 / -21.8 / -29.5% | 1.74 | 2.66 |
| SPY | holdout | 17.2% | -33.7% | 0.91 | 1.29 |
| SPY | 3y | 21.6% | -18.8% | 1.36 | 2.05 |

Static policies at any equity share have the same Sharpe and Sortino (scale invariance). Only real timing can raise risk-adjusted return.

Journal replays (2026-05-12 to 2026-11-24, $50k; carry-day bug affects legacy runs): j2s +1.51%, j2r +1.87%, j2n -0.86%, j2k -2.72%, SPY -2.19%.
3y env backtests (2023-05-09..2026-04-06): j2s 20.9% CAGR / -9.0% MaxDD / Sharpe 1.85; j2r 23.1 / -9.1 / 2.00; j2n 22.2 / -10.9 / 1.72; j2k 49.0 / -22.3 / 1.69; SPY 19.0 / -18.8 / 1.23. j2s/j2r use TLT/GLD/UUP/SPY and the beta cap; j2n is 3-dim with the beta cap; j2k is the equity-only two-sleeve agent with no beta cap.

## 3. Memorization evidence (2026-11-26, V)

Control config (mean_var k=1, Calmar selection, 8 seeds 42-49). Agent minus matched static (8w grid):

| Window | Sharpe (mean, std over seeds) | Calmar | Seeds positive (Sharpe) |
|---|---|---|---|
| Train 2008-16 | +0.296 (0.097) | +0.375 | 8/8 |
| Validation 2017-18 | +0.144 (0.089) | +0.432 | 7/8 |
| Holdout 2019-26 | -0.017 (0.048) | -0.096 | 3/8 |

In training the agents cut the 2008 drawdown (-38% vs -60% matched static) but on the holdout they hold -56% (same as static 100%). Interpretation (I): date-specific memorization of one crisis, not a transferable market-risk relationship. Caveats: single deterministic evaluation per window; 2008 dominates training.

## 4. Experiment tracker

Legend: DONE / RUNNING / PROPOSED. Worktrees live under `/Users/shivamgupta/github/us-rl-portfolio/.claude/worktrees/`.

| ID | What it tests | Status | Result / verdict |
|---|---|---|---|
| EQ | Equity-only plumbing (stocks + cash, agent decides split; finalize_equity_only invariant, carry-forward) | DONE | Verified on j2k replay: 141 days, 0 failures, stock sum == agent target (gap <= 1e-5). 15 tests pass. Uncommitted on `exp/no-tlt`. |
| DX | Diagnosis of collapsed agent | DONE | Best checkpoint = episode 1 (untrained, raw action ~[0,0] -> 71.4% equity); 63d-Sharpe reward is share-blind; selection by Sharpe is share-blind. |
| A | First reward fix (agent-ac687acff9f40ee7f): excess_static72, mean_var, Calmar selection, 14d cadence, ent_coef | DONE | mean_var + Calmar removed the collapse (equity std 0.08-0.24); excess_static72 collapsed to ~100% equity; ent_coef no effect. Not accepted. |
| P0 | Diagnostics (agent-a482d05bc472a0b22): shuffled-obs, delay, oracle, reward SNR, walk-forward tool | DONE | No tested model shows reliable timing. Agent reacts mostly to its own trailing return (port_ret_21d_z). Tool: scripts/eval_rl_controls.py. |
| P1 | Reward variants (agent-a943f01b9478e9118): mean_var k=1/4, dsr, semivar, cvar5 | DONE (partial; I took over) | dsr equity-blind; k=4 drifts to ~60% equity (fails); k=1 seed 42 looked best (holdout Sharpe 1.097 vs 1.025 matched) but did not replicate. |
| P2 | Data diversity (agent-a3dc707057f908053): random offsets, mixed cadence, sub-windows | DONE | b collapsed to static; a fails both grids (8w 1.017, 14d 1.014 vs ~1.04/1.08); c fails 8w (0.988), passes 14d (1.193). Bootstrap not implemented. |
| P3 | Observations (agent-ac00019ad6bd61274): v3a/v3ab/v3abs | DONE | v3ab seed 42 holdout 8w Sharpe 1.40 vs 1.03 did NOT replicate (seeds 43/44: -0.04/+0.09); 14d holdout edge +0.17..+0.23 on 3 seeds; 3y no gain; 0/3 pass. State audit: dead and redundant dims, all |corr| < 0.3. |
| P4 | Paper-inspired rewards (agent-a225a07f6a3c4f2f8): composite, semivar, mv1_down | DONE | Not accepted; composite fails replication (seeds 43/44) and fails the shuffled-obs control; semivar/mv1_down lose 8w. Paper formulas unverified (second-hand). |
| E1 | Action-averaging ensembles (agent-aa453f5a5f9340a58) | DONE | mv1 median ensemble passes on paper (8w 1.118 vs 1.024; 14d 1.277 vs 1.075; shuffle drops 1.118->0.907) but picked on holdout; loses 3 of 6 walk-forward folds incl. 2020. Fragile. |
| E2 | 8 seeds of mean_var k=1 (agent-a545d4c06b656cfa0) | DONE | Pooled agent-minus-matched: holdout Sharpe 8w -0.024 (t -1.0), Calmar 8w -0.096 (0/8 positive), 14d Sharpe +0.060 (t 2.3, 7/8); 3y Sharpe -0.02/-0.05; 1/8 seeds pass. No demonstrated edge. |
| EGM | Five-lens holistic review (report: scratchpad `rl_review_report.md`) | DONE | Section 5. |
| MEM | In-sample vs out-of-sample gap (above) | DONE | Section 3. |
| X1 | Equity floor 0.25 (`--eq-floor`, default 0.5 unchanged), mean_var k=1 and k=2, seeds 42-44 (agent-a924487ffc6f27961) | RUNNING | Floor flag + regression tests done (19 pass); trainings in progress; eval/crash analysis pending. |
| X2 | Equity floor 0.0, same grid (agent-acffe4b0af4b12652) | DONE (2026-11-26) | NOT ACCEPTED. 6 runs, no collapse (eq std 0.05-0.16, avg eq 0.66-0.75). Agent minus matched static, 3-seed pooled: holdout 8w Sharpe -0.013 / Calmar -0.031 (k1), -0.013 / -0.042 (k2); 14d Sharpe +0.060 / +0.069; 3y 8w Sharpe +0.11 / +0.09, Calmar +0.26 / +0.19 (SE ~0.06), 3y 14d ~0. Crash protection FAILS: 2020 crash MaxDD -46.4% vs matched -45.1% (k1), equity share HIGHER in the crash (0.85 vs 0.73 calm); 2022 Sharpe worse than matched (-0.82 vs -0.74). De-risks on top-quintile stress dates only. Shuffled obs: 3y Sharpe 1.88 vs 1.70 (partial signal), holdout no difference. Lower floor lets agent hold 16-40% equity but did not use it in the crash. Caveats: 3y inside reused holdout; 2020 fold only 3 decisions. Floor code (RL_EQ_FLOOR, tests) in worktree agent-acffe4b0af4b12652. |
| H1 | Headroom (oracle policies, wider floor, 1-step delay) + signal-existence gate (out-of-sample prediction by regime) | DONE (2026-11-26) | Worktree agent-a31db186a7b693ee9, outputs runs_h1/. Headroom (14d holdout Sharpe): static 1.07; hindsight oracle {0.5,1} 2.11, {0..1} 3.20 (Calmar 2.9 -> 6.7, 2020 MaxDD -32% -> -23%); with a 1-step delay Sharpe 1.06 (= static), Calmar below static 0.5. Signal gate (n=477, 9 regime blocks, leave-one-regime-out): return rank IC 0.023 (p 0.32), AUC 0.556 (p 0.04), long/flat Sharpe 0.76 vs 0.92 always-invested; no regime fold (2020, 2022) predicts sign. Only next-period drawdown magnitude is predictable (IC 0.38, p 0.005) = sizing/risk signal, not timing. Verdict: STOP RL for return timing; only a drawdown-scaled sizing policy remains untested. Caveats: oracles greedy; permutation null not block-wise; reference B.5+B.4 numbers not reproduced in this setup. |
| H2 | PPO settings sweep: gamma 0.9, gamma 0, log_std_init -1, fewer epochs / whole-episode n_steps, reward normalization, 10 bps training cost (+ n_steps/epochs, ent_coef 0.01 screens) | DONE (2026-11-26) | NOT ACCEPTED: learning settings not shown to be the bottleneck. 9 single-seed screens (S1 gamma .9; S2 gamma 0; S3 log_std -1; S4 n_steps 236/epochs 3; S5 reward norm; S6 train cost 10 bps; S7 n_steps 118/epochs 5; S8 ent .01; S9 ent .01 + log_std -1). No screen beat the control on both grids; S4 partly and S7 fully collapsed to ~100% validation equity. Best two by validation only: S2, S3, run on 3 seeds vs the 8-seed control: S2 holdout 8w Sharpe -0.007 (vs control +0.016, z +0.4), 14d Sharpe +0.157 (z +3.3 vs control) but 8w Calmar -0.113 (no gain); S3 fails (8w Sharpe -0.053, seed 44 equity SD 0.046). Diagnostics: learning does happen (approx_kl 0.015-0.03, clip fraction 0.15-0.23, explained variance -> ~1.0); policy std shrinks (log_std 0 -> -0.6..-1.0) and ent_coef 0.01 did not stop it; validation Calmar plateaus at ~1.55-1.62 with avg equity 0.77-0.80 for almost every config. The 14d-grid holdout Sharpe gain repeats but never holds on 8w or Calmar. Caveats: 1 seed per screen, holdout seen for all screens (configs chosen on validation only), baseline PPO diagnostics by proxy (S6). Worktree agent-a0804b0bf3e4723ae. |
| W1 | Walk-forward folds with 2020/2022 in training, low update intensity (3 epochs, small net), memorization gap monitor (agent-a44a76ccd7b545cbb) | DONE (2026-11-26) | NOT ACCEPTED. 15 runs (LOW: 3 epochs, 2 episodes/rollout, 64x64, seeds 42-44; CONTROL: current settings, seeds 42-43), 150-episode cap, folds F1 (test 2020-21), F2 (test 2022), F3 (test 2023-Apr 2026). Agent minus matched static on test, 8w, seed mean: Sharpe LOW F1 -0.027 / F2 -0.003 / F3 +0.001 (pooled -0.010; 1 of 3 folds positive, need 2); CONTROL -0.006 / +0.005 / +0.016. F1 (2020 crash) MaxDD LOW -48.2% vs matched -47.3%; equity share in stress vs calm decisions 0.82 vs 0.81 (no de-risking). F2 parity. Train-test gap small in most folds (LOW mean 0.019 vs CONTROL 0.053; CONTROL F3 seed 43 is the clear memorization case +0.28 in-sample vs +0.01 test). Shuffled-obs control did not reliably degrade (4 of 6 cases equal or better). Caveats: only 13/6/22 test decisions on 8w; 150-episode cap may truncate CONTROL (F3 still improving); only first gap_monitor rows inspected. Code: --train/val-start/end, --val-cadence, --n-steps-episodes, --net-arch, gap monitor (worktree agent-a44a76ccd7b545cbb). |
| R1 | Baseline-relative action: multiplier on the B.4-constrained B.5 book (a=0 reproduces B.5+B.4), wide range, near-zero floor (EGM recommendation) | RUNNING (2026-11-27) | Start after X1/X2/H1 results. |
| N1 | State consistency: remove or recompute self-referential features (NAV restarts at 1.0 per episode; own trailing return dominates) | RUNNING as C1 (2026-11-27) | See cause 6. |
| S1 | Sealed one-shot test on 2026-05..11 | PROPOSED | Needs universe masks rebuilt past 2026-04-24; no model may be tuned on it. |
| C1 | Train at deployment cadence (14d) with all other fixes | PROPOSED | After R1. |

## 5. EGM review findings (five lenses; verified-in-code vs inferred)

Ranking with analysis and way forward (section 6 expands each):

1. Action floor and exposure replacement (V, high). `exposure_mix.py` caps cash at 0.5, so equity >= 50%. B.5/B.4's own exposure control (~28% gross) is discarded and replaced by the agent's equity share. Explains failure to protect capital; does not alone explain the Sharpe deficit.
2. Reward effectively share-blind (arithmetic V; effect I). Extra terms <= ~0.075 vs per-step std ~2.2; reward window is only the ~40 days since the last decision so the "63" cap never binds.
3. ~3 regimes and ~58 decisions per path (counts I). Each PPO update replays one path ~9 times (80 gradient steps).
4. Validation and selection (mostly V). Selection on ~13 decisions with winner's curse over ~50 noisy evaluations; holdout reused. Correction to the brief: 2017-18 contains Q4 2018 (SPY ~-19%, I) but no 2020-style crash.
5. PPO scaling (config V, mechanism I). No VecNormalize, no gamma/ent_coef/clip override, unscaled rewards, near-constant volatility dims.
6. Self-referential state mismatch across train/val/holdout/prod (V). NAV restarts at 1.0 per episode so drawdown and long-window features behave differently per setting; training likely learns "deep drawdown means stay invested" from the 2008 recovery (I).
7. Cadence mismatch 8w training vs 14d prod (I).

Plain mistakes found (V): `--action-dim` defaults to 3 (a silently invalid run); churn compares E_t with E_{t-2} (negligible); the final decision's period is never simulated; training cost_bps = 0; dead and redundant state dims. Checked clean (V): B.5 snapshot alignment, reward vs NAV ordering, turnover timing, feature look-ahead.

Evaluation caveat found 2026-11-26 (V): the old `static_action` helper (scratchpad `nt/eval_nt.py`, `scripts/eval_rl_controls.py`) mis-inverts the mapping for target equity between 0.5 and 2/3 (a requested 0.612 realised 0.577). Affects CAGR/Calmar/MaxDD comparisons for agents with average equity ~0.55-0.67 only (mean_var k=4, P2 a and c, P3 v3a); Sharpe/Sortino comparisons are essentially unaffected. X1 fixed it with `raw_for_equity()`; H1, H2, W1 and X2 were told to use a numerical inverse.

Reviewers' recommended reformulation: action as a multiplier m = exp(a * ln M) on the B.4-constrained B.5 book (a=0 reproduces B.5+B.4), wide range, near-zero floor; baseline-relative or risk-sensitive reward with 10 bps cost and a fixed 63-day window and scaling; anchored walk-forward folds including 2020 and 2022; seal 2026-05..11 for a one-shot test. Reviewers disagreed on the multiplier range (1.5x vs 3x upside) and on the crash-fold MaxDD pass bar (3 vs 10 points; the review used 10).

## 6. Causes, evidence and way forward

| # | Cause | Evidence | Experiments that test it | Way forward |
|---|---|---|---|---|
| 1 | 50% equity floor; agent's share replaces B.5/B.4 exposure | V: raw [-1,+1] -> equity 0.5; static 50% holdout MaxDD -32.7% ~ SPY -33.7%; agents -56% in 2020 | X1, X2, H1 (headroom with wider floor), R1 | If a lower floor lets the agent cut exposure in the 2020 and 2022 folds without hiding in cash, keep it. If not, use R1 (relative multiplier) so the baseline is B.5+B.4, not a fixed 72%. This is the first fix because it is structural. |
| 2 | Reward barely depends on the action | Reward SNR (P0): mean_var spread/sigma 0.16-0.18 vs sharpe 0.006-0.010; paired gates mostly |t| < 2 | P1, P4 (done), R1 reward with baseline-relative term | After the action space is fixed, use a baseline-relative or risk-sensitive reward; re-run the paired gate (reward(100%)-reward(50%) per step) before any training. |
| 3 | Memorization / too little independent data | Section 3; ~58 decisions, ~3 regimes | W1, H2 (update intensity), P2 (done) | Put crashes into training via anchored walk-forward folds; lower update intensity; monitor the train-vs-validation gap. Random offsets/sub-windows alone did not help. If the gap does not shrink, accept that RL cannot be validated on this history. |
| 4 | Validation/selection design | Winner's curse on ~13 decisions; holdout reused | W1 (folds), S1 (sealed) | Select on a longer, denser validation (14d grid); report sealed 2026-05..11 once. Never tune on it. |
| 5 | PPO settings | No normalization; ~80 gradient steps per update on 58 distinct states | H2 | Accept only if the pooled 3-seed gain beats the control by > 2 SE on both grids. Otherwise not a bottleneck. |
| 6 | Self-referential / inconsistent state | Top sensitivity: own trailing return (P0, P3); NAV reset per episode | N1 (proposed), P3 (v3 features) | Remove or recompute own-NAV features on a continuous history; drop dead/redundant dims (trend_frac, sec_vol_XLC, eq_frac vs cash_frac). Re-test shuffled-obs control. |
| 7 | Cadence mismatch (8w train vs 14d prod) | 14d results differ by ~+0.05 Sharpe even for static; mv1 edge present on 14d only | C1 (proposed), E2 | Train and evaluate on the deployment cadence after the other fixes; avoid comparing across grids. |
| 8 | Observations carry little signal | P3 audit: all |corr| < 0.3 with n=58 | H1 signal gate | If out-of-sample prediction by regime is at noise level (permutation test), stop RL on these inputs. |

## 7. Decision rules (to apply when the tracker is complete)

Go (continue RL) only if all hold:
1. H1: headroom after a 1-step delay is meaningful AND the signal gate shows out-of-sample predictability in at least one crash fold (permutation p < 0.05).
2. A fixed action space (X1/X2 floor or R1) gives crash-fold MaxDD at least 10 points shallower than matched static, with the 2022 fold not worse.
3. Out-of-sample (W1 test folds, then the sealed 2026-05..11 test): agent minus matched static > 0 on Sharpe and Calmar, on at least 2 of 3 folds, mean across >= 3 seeds, t > 2 on the pooled mean; the shuffled-observation control degrades performance.
4. The train-vs-test gap is smaller than the +0.30 vs -0.02 pattern.

Stop (ship B.5 + B.4 as the exposure engine, keep RL out of the decision loop) if H1 fails, or if R1/X1/X2 show no crash-fold gain, or W1 shows the gap persists. Note the reviewers' own expectation (I): with ~3 regimes RL may not beat the B.5+B.4 prior.

## 8. Open items and process notes

- Nothing is committed; `exp/no-tlt` has uncommitted changes (equity-only plumbing, tests, configs). Per `AGENTS.md`, update `docs/agent_handoff.md` when a material decision is made. Untrack tracked `__pycache__` files before any commit; delete the temporary journey configs (j2s, j2r, j2n, j2m, j2k) when finished.
- Legacy prod path: carry-day weights snap back to raw B.5 on non-rebalance days and are renormalized, overriding the agent's cash share (affects legacy journals only); order sizing from initial NAV and over-budget normalization bugs remain; decision cadence in prod (14 days) is not what the env trains on. B.5 cache (3.9 s -> 0.07 s) is in worktree agent-a63867a25b7570e35, not reviewed or merged.
- Single paths, heavily reused holdout, seed noise ~0.05 Sharpe; any differences below that are noise.
- Update this file when each running experiment reports (X1 still outstanding).

## 9. Round-2 EGM review and plan (2026-11-27)

Full report (scratchpad, may be cleared): `/private/tmp/claude-501/-Users-shivamgupta-github-us-rl-portfolio/5058cb96-5758-4d0d-bf44-39a776434699/scratchpad/rl_plan_report.md`. No reviewer re-ran a backtest; all tracker numbers are still unreproduced.

Verdict: stopping RL for RETURN timing is justified (high confidence: delayed oracle Sharpe 1.06 = static; return IC 0.02). A full stop is slightly overstated (medium): the history is "unvalidatable", not "disproven"; drawdown sizing was never tried. The drawdown IC 0.38 is optimistic because the permutation null is not block-wise.

Reference gap (14.1% vs 23.1% CAGR): most likely not a failed reproduction. 14.1% is the B.5+B.4 book at ~28% average gross; H1's static 0.5 rescales the same book to 50% gross (tracker's static-50% = 22.5%, consistent with 23.1%). Provenance of 14.1% is undocumented (no script emits it); 23.1% also equals the j2r 3y CAGR (possible transcription mix-up, inferred). Fix: run B.5+B.4 through the env at a=0 and diff gross, cost, grid.

Pre-registered gates: G0 reconcile reference; G1 block-permutation leave-one-regime-out test of the drawdown forecast; G2 learned sizing policy needs crash-fold MaxDD >= 10 points shallower than matched static, 2022 not worse, no Calmar loss to B.4; G3 baseline-relative RL must beat the simpler supervised/bandit solution. The sealed 2026-05..11 test can only falsify (~12 decisions, partly contaminated by journal replays).

Plan (minimum path to a decision ~20 h; full ~40-55 h): P0 consolidate the 16 worktrees (6-8 h); F reconcile reference (3-4 h); E production logging (4-6 h); A drawdown-sizing gate (8-10 h); C state cleanup (4-6 h); B baseline-relative multiplier (10-14 h); S sealed test (6-8 h). F, E, C parallel in separate worktrees. Cut: more PPO sweeps and reward variants, PPO ensembles, 14d-cadence retrain, simulation. Report includes edit points for the multiplier action, dead state dims, mask extension past 2026-04-24, and prod logging gaps.

Owner decisions needed: (1) is a FITTED drawdown-to-size map a "hand-written rule" (a fixed formula would be vol-targeting in disguise); (2) multiplier range 1.5x vs 3x upside (hidden prior, reviewers split); (3) crash-fold MaxDD bar 3 vs 10 points (report uses 10); (4) contextual bandit instead of PPO for sizing experiments (inferred, untested).

Executive recommendation: ship B.5+B.4 now, keep RL in shadow mode with richer logging; spend ~20 h on one last test (can a small learned policy centred on a=0 monetise the predictable drawdown signal and beat B.5+B.4?). If it fails, park RL as allocator for this history; if it passes, test baseline-relative RL only to see whether it beats the simpler answer.

## 10. Owner direction 2026-11-27: continue RL development

Owner wants RL development continued (not parked). Running tracks, each in its own worktree, outputs in its own runs_* dir:
- F (agent ac2d8568346f01881): reconcile the B.5+B.4 reference numbers (gate G0) and measure what B.4's time-varying exposure adds over a constant-gross static: the bar RL must beat.
- G1 (agent a0f565fbd18acc683): block-permutation test of the drawdown forecast and a first rule-free, fitted monetization check (gate G1).
- R1 (agent ae80a5baaf5ebaa0c): baseline-relative multiplier action, m = exp(a*ln 3) on the B.4-constrained B.5 book (a=0 reproduces B.5+B.4; only physical limit: stock weight <= 1), baseline-relative mean-variance reward on a fixed 63-day window with 10 bps cost and reward normalization, 9 runs (V1 8w k=1, V2 8w k=2, V3 14d k=1; seeds 42-44). Selection on excess Calmar over the a=0 baseline.
- C1 (agent a5162ab49bcbd8f9f): clean observations O1 (drop dead/redundant dims), O2 (no self-referential own-portfolio features), O3 (O2 + continuous causal risk features); 18 runs.
Defaults assumed for the open decisions (owner may overrule): fitted learned maps count as RL; multiplier range 1/3x-3x; crash-fold bar 10 points; PPO retained (bandit not yet tried).

## 11. Consolidated results (CAGR, MaxDD, Sharpe, Sortino per experiment, compiled 2026-11-27)

Compiled from output files by a read-only script (not from memory); see the Notes and gaps list at the end. X1 is pending (no evaluation output yet); R1, C1, F and G1 are not yet included. Note: the 14.1% equity-only holdout CAGR quoted in section 2 appears in no output file (unresolved, track F); static 50% = 22.6% is confirmed by output files.

All numbers read from output files unless flagged in Notes. Net of 10 bps. Calmar = CAGR / |MaxDD|. Matched-static = static policy at the agent's own average equity on the same grid. Repo base: `/Users/shivamgupta/github/us-rl-portfolio/`, worktree base: `.claude/worktrees/`.

### A. Holdout window 2019-01-01 to 2026-04-24

| ID | Experiment / variant | Grid | CAGR | MaxDD | Sharpe | Sortino | Calmar | Avg equity | Matched-static CAGR | Matched-static MaxDD | Matched-static Sharpe | Source | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REF | B.5+B.4 equity-only (tracker sec. 2; 14.1% under review) | n/a | 14.1% | -20.4% | 1.10 | 1.65 | 0.69 | n/a | n/a | n/a | n/a | `docs/phases/rl_allocator_experiments.md (sec. 2)` | Tracker-only numbers, no output file has CAGR. Calmar computed. eq_eval.log gives Sharpe 1.108 / MaxDD -20.40% (window not stated). Gap vs 22.5-23.1% unresolved. |
| REF | B.5 locked (Phase E.6 holdout benchmark) | n/a | 20.7% | -33.0% | 1.27 | n/a | 0.63 | n/a | n/a | n/a | n/a | `artifacts/reports/e6_policy_comparison.csv` | Output file; Calmar computed; avg equity not given. |
| REF | B.5 locked (computed from NAV) | n/a | 21.0% | -31.5% | 1.27 | 1.82 | 0.67 | n/a | n/a | n/a | n/a | `data/scratch_rl/baseline_backup/nav_b5_backtest.parquet` | Computed from daily NAV (E.6 file shows 20.69% / -32.98% / 1.270 for same window). Differences unexplained. |
| REF | static 50% of book | 8w | 22.6% | -32.7% | 1.04 | 1.56 | 0.69 | 50.0% | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv` |  |
| REF | static 72% of book | 8w | 32.2% | -44.1% | 1.03 | 1.56 | 0.73 | 72.0% | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv` |  |
| REF | static 100% of book | 8w | 43.5% | -56.3% | 1.00 | 1.56 | 0.77 | 100.0% | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv` |  |
| REF | SPY (buy and hold) | n/a | 17.2% | -33.7% | 0.91 | 1.29 | 0.51 | n/a | n/a | n/a | n/a | `data/raw/SPY.parquet (adj_close)` | Computed; matches tracker sec. 2. |
| P1 | mean_var k=1, seed 42 (single) | 8w | 38.3% | -56.3% | 1.10 | n/a | 0.68 | 77.7% | 34.6% | -46.8% | 1.03 | `data/scratch_rl/e2_eval/e2_eval.csv (= p1_eval/eval.csv)` | Single seed; matched = static at its avg equity. |
| P1 | mean_var k=1, seed 42 (single) | 14d | 37.6% | -37.0% | 1.25 | n/a | 1.01 | 74.2% | 34.5% | -45.0% | 1.08 | `data/scratch_rl/e2_eval/e2_eval.csv (= p1_eval/eval.csv)` | Single seed; matched = static at its avg equity. |
| E2 | mean_var k=1, 8-seed pooled mean (seeds 42-49) | 8w | 35.6% | -55.1% | 1.00 | n/a | 0.65 | 80.7% | 35.8% | -48.2% | 1.02 | `data/scratch_rl/e2_eval/e2_eval.csv` | Mean across 8 seeds; Sortino not in source (n/a). |
| E2 | mean_var k=1, 8-seed pooled mean (seeds 42-49) | 14d | 35.9% | -42.7% | 1.13 | n/a | 0.86 | 77.7% | 36.0% | -46.6% | 1.07 | `data/scratch_rl/e2_eval/e2_eval.csv` | Mean across 8 seeds; Sortino not in source (n/a). |
| P2-a | a: random offsets (seed 42) | 8w | 27.3% | -41.1% | 1.02 | n/a | 0.66 | 62.1% | 26.7% | -37.8% | 1.04 | `data/scratch_rl/p2_eval/a_off/eval.csv` | Matched row present only for 8w. |
| P2-a | a: random offsets (seed 42) | 14d | 27.4% | -41.0% | 1.01 | n/a | 0.67 | 61.0% | n/a | n/a | n/a | `data/scratch_rl/p2_eval/a_off/eval.csv` | No 14d matched row in file: matched n/a. |
| P2-b | b: offsets + mixed cadence (seed 42) | 8w | 32.1% | -43.9% | 1.03 | n/a | 0.73 | 71.5% | 32.0% | -43.9% | 1.03 | `data/scratch_rl/p2_eval/b_offmix/eval.csv` | Matched row present only for 8w. |
| P2-b | b: offsets + mixed cadence (seed 42) | 14d | 33.3% | -45.0% | 1.06 | n/a | 0.74 | 71.6% | n/a | n/a | n/a | `data/scratch_rl/p2_eval/b_offmix/eval.csv` | No 14d matched row in file: matched n/a. |
| P2-c | c: mixed cadence + sub-windows (seed 42) | 8w | 27.3% | -42.9% | 0.99 | n/a | 0.64 | 63.4% | 27.7% | -38.9% | 1.04 | `data/scratch_rl/p2_eval/c_mixsub/eval.csv` | Matched row present only for 8w. |
| P2-c | c: mixed cadence + sub-windows (seed 42) | 14d | 33.2% | -35.0% | 1.19 | n/a | 0.95 | 62.4% | n/a | n/a | n/a | `data/scratch_rl/p2_eval/c_mixsub/eval.csv` | No 14d matched row in file: matched n/a. |
| P3 | v3ab observation set, 3-seed pooled mean (42-44) | 8w | 34.0% | -39.8% | 1.17 | n/a | 0.88 | 68.7% | 30.8% | -42.5% | 1.03 | `data/scratch_rl/p3_eval_s42/eval.csv; data/scratch_rl/p3_eval_s43_44/eval.csv` | Mean of seeds 42-44; Sortino not in source. |
| P3 | v3ab observation set, 3-seed pooled mean (42-44) | 14d | 34.5% | -35.0% | 1.27 | n/a | 0.99 | 69.4% | 32.0% | -42.4% | 1.08 | `data/scratch_rl/p3_eval_s42/eval.csv; data/scratch_rl/p3_eval_s43_44/eval.csv` | Mean of seeds 42-44; Sortino not in source. |
| P4 | composite_paper reward (seed 42) | 8w | 38.9% | -56.3% | 1.09 | n/a | 0.69 | 81.2% | 36.0% | -48.4% | 1.02 | `data/scratch_rl/p4_eval_composite_paper/eval.csv` | Seeds 43/44 trained (p4_comp_s43/44) but no eval output. |
| P4 | composite_paper reward (seed 42) | 14d | 37.8% | -40.4% | 1.19 | n/a | 0.94 | 77.7% | 37.5% | -48.2% | 1.07 | `data/scratch_rl/p4_eval_composite_paper/eval.csv` |  |
| P4 | mv1_down reward (seed 42) | 8w | 33.8% | -56.3% | 0.99 | n/a | 0.60 | 73.2% | 32.7% | -44.7% | 1.03 | `data/scratch_rl/p4_eval3/eval.csv` | Trained in data/scratch_rl/p4_mv1_down. |
| P4 | mv1_down reward (seed 42) | 14d | 35.9% | -37.4% | 1.25 | n/a | 0.96 | 69.0% | 34.0% | -44.6% | 1.08 | `data/scratch_rl/p4_eval3/eval.csv; p4_eval4/eval.csv` |  |
| E1 | median ensemble of mean_var k=1 seeds 42-44 (action median) | 8w | 39.5% | -56.3% | 1.12 | n/a | 0.70 | 78.9% | 35.1% | -47.4% | 1.02 | `data/scratch_rl/e1_ensemble/eval.csv` | Picked on holdout; loses 3 of 6 walk-forward folds (tracker). |
| E1 | median ensemble of mean_var k=1 seeds 42-44 (action median) | 14d | 39.2% | -37.0% | 1.28 | n/a | 1.06 | 76.2% | 35.3% | -46.0% | 1.08 | `data/scratch_rl/e1_ensemble/eval.csv` | Picked on holdout; loses 3 of 6 walk-forward folds (tracker). |
| X1 | equity floor 0.25, k1 and k2, seeds 42-44 | 8w | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv (smoke only)` | pending: 6 trainings exit 0 (data/scratch_rl/x1_logs/lanes_status.txt) but no eval.csv for k1/k2. |
| X1 | equity floor 0.25, k1 and k2, seeds 42-44 | 14d | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv (smoke only)` | pending: 6 trainings exit 0 (data/scratch_rl/x1_logs/lanes_status.txt) but no eval.csv for k1/k2. |
| X2 | equity floor 0.0, k1, 3-seed pooled | 8w | 32.8% | -46.9% | 1.03 | 1.53 | 0.70 | 75.0% | 33.3% | -45.5% | 1.05 | `data/scratch_rl/x2_eval/eval.csv` | Mean of seeds 42-44. |
| X2 | equity floor 0.0, k2, 3-seed pooled | 8w | 28.6% | -42.4% | 1.04 | 1.52 | 0.67 | 66.5% | 29.7% | -41.4% | 1.05 | `data/scratch_rl/x2_eval/eval.csv` | Mean of seeds 42-44. |
| X2 | equity floor 0.0, k1+k2, 6-run pooled | 8w | 30.7% | -44.7% | 1.04 | 1.53 | 0.69 | 70.8% | 31.5% | -43.5% | 1.05 | `data/scratch_rl/x2_eval/eval.csv` | Mean of 6 runs. |
| X2 | equity floor 0.0, k1, 3-seed pooled | 14d | 34.4% | -43.2% | 1.13 | 1.71 | 0.80 | 74.4% | 33.8% | -45.1% | 1.07 | `data/scratch_rl/x2_eval/eval.csv` | Mean of seeds 42-44. |
| X2 | equity floor 0.0, k2, 3-seed pooled | 14d | 29.9% | -38.6% | 1.14 | 1.71 | 0.77 | 65.7% | 30.0% | -40.9% | 1.07 | `data/scratch_rl/x2_eval/eval.csv` | Mean of seeds 42-44. |
| X2 | equity floor 0.0, k1+k2, 6-run pooled | 14d | 32.1% | -40.9% | 1.13 | 1.71 | 0.78 | 70.1% | 31.9% | -43.0% | 1.07 | `data/scratch_rl/x2_eval/eval.csv` | Mean of 6 runs. |
| H2 | S2 (gamma 0), 3-seed pooled | 8w | 35.1% | -56.3% | 1.02 | 1.55 | 0.62 | 76.3% | 34.0% | -46.2% | 1.03 | `runs_h2/eval/s2_seed42-44.json (worktree agent-a0804b0bf3e4723ae)` | Mean of seeds 42-44. |
| H2 | S2 (gamma 0), 3-seed pooled | 14d | 38.0% | -44.0% | 1.23 | 1.77 | 0.88 | 73.4% | 34.1% | -44.6% | 1.08 | `runs_h2/eval/s2_seed42-44.json (worktree agent-a0804b0bf3e4723ae)` | Mean of seeds 42-44. |
| H2 | S3 (log_std -1), 3-seed pooled | 8w | 32.7% | -50.9% | 0.98 | 1.50 | 0.65 | 73.6% | 32.8% | -44.9% | 1.03 | `runs_h2/eval/s3_seed42-44.json (worktree agent-a0804b0bf3e4723ae)` | Mean of seeds 42-44. |
| H2 | S3 (log_std -1), 3-seed pooled | 14d | 36.7% | -41.6% | 1.19 | 1.73 | 0.89 | 72.9% | 33.9% | -44.4% | 1.08 | `runs_h2/eval/s3_seed42-44.json (worktree agent-a0804b0bf3e4723ae)` | Mean of seeds 42-44. |
| H2-ctl | H2 control (current settings), 8-seed pooled | 8w | 35.6% | -55.1% | 1.00 | 1.52 | 0.65 | 80.7% | 35.8% | -48.2% | 1.02 | `runs_h2/eval/control_8seed.json (worktree agent-a0804b0bf3e4723ae)` | Same configuration as E2 (8 seeds). |
| H2-ctl | H2 control (current settings), 8-seed pooled | 14d | 35.9% | -42.7% | 1.13 | 1.67 | 0.86 | 77.7% | 36.0% | -46.6% | 1.07 | `runs_h2/eval/control_8seed.json (worktree agent-a0804b0bf3e4723ae)` | Same configuration as E2 (8 seeds). |
| H1 | oracle, 2-level {0.5,1} (HINDSIGHT, not tradable) | 8w | 63.7% | -37.4% | 1.60 | 2.56 | 1.70 | 84.4% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | oracle, 2-level {0.5,1} (HINDSIGHT, not tradable) | 14d | 94.6% | -32.5% | 2.11 | 3.50 | 2.91 | 81.2% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | oracle, 5-level {0..1} (HINDSIGHT, not tradable) | 8w | 82.1% | -25.7% | 2.09 | 3.52 | 3.19 | 68.8% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | oracle, 5-level {0..1} (HINDSIGHT, not tradable) | 14d | 155.9% | -23.2% | 3.20 | 5.78 | 6.72 | 62.3% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | same as oracle {0.5,1} with 1-step delay (tradable check) | 8w | 32.1% | -56.3% | 0.97 | 1.41 | 0.57 | 83.3% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | same as oracle {0.5,1} with 1-step delay (tradable check) | 14d | 35.1% | -45.9% | 1.06 | 1.61 | 0.76 | 80.9% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | same as oracle {0..1} with 1-step delay (tradable check) | 8w | 18.8% | -58.0% | 0.70 | 1.00 | 0.32 | 66.7% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | same as oracle {0..1} with 1-step delay (tradable check) | 14d | 23.1% | -43.8% | 0.85 | 1.31 | 0.53 | 61.8% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |

### B. 3y window 2023-04-25 to 2026-04-24

| ID | Experiment / variant | Grid | CAGR | MaxDD | Sharpe | Sortino | Calmar | Avg equity | Matched-static CAGR | Matched-static MaxDD | Matched-static Sharpe | Source | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REF | B.5+B.4 equity-only (tracker sec. 2) | n/a | 21.3% | -8.2% | 2.09 | 3.33 | 2.60 | n/a | n/a | n/a | n/a | `docs/phases/rl_allocator_experiments.md (sec. 2)` | Tracker-only numbers, no output file. Calmar computed. |
| REF | B.5 locked (computed from NAV) | n/a | 29.5% | -10.6% | 2.17 | 3.34 | 2.80 | n/a | n/a | n/a | n/a | `data/scratch_rl/baseline_backup/nav_b5_backtest.parquet` | Computed from daily NAV. Provenance of this NAV series not documented. |
| REF | static 50% of book | 8w | 34.5% | -15.4% | 1.97 | 2.66 | 2.24 | 50.0% | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv` |  |
| REF | static 72% of book | 8w | 51.8% | -21.8% | 2.05 | 2.66 | 2.38 | 72.0% | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv` |  |
| REF | static 100% of book | 8w | 75.5% | -29.5% | 2.16 | 2.66 | 2.56 | 100.0% | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv` |  |
| REF | SPY (buy and hold) | n/a | 21.6% | -18.8% | 1.36 | 2.05 | 1.15 | n/a | n/a | n/a | n/a | `data/raw/SPY.parquet (adj_close)` | Computed; matches tracker sec. 2. |
| P1 | mean_var k=1, seed 42 (single) | 8w | 60.7% | -20.0% | 2.23 | n/a | 3.03 | 80.8% | 56.5% | -23.4% | 2.08 | `data/scratch_rl/e2_eval/e2_eval.csv (= p1_eval/eval.csv)` | Single seed; matched = static at its avg equity. |
| P1 | mean_var k=1, seed 42 (single) | 14d | 55.4% | -20.2% | 2.15 | n/a | 2.75 | 78.4% | 54.4% | -22.8% | 2.11 | `data/scratch_rl/e2_eval/e2_eval.csv (= p1_eval/eval.csv)` | Single seed; matched = static at its avg equity. |
| E2 | mean_var k=1, 8-seed pooled mean (seeds 42-49) | 8w | 58.4% | -22.9% | 2.07 | n/a | 2.59 | 83.6% | 59.0% | -24.2% | 2.09 | `data/scratch_rl/e2_eval/e2_eval.csv` | Mean across 8 seeds; Sortino not in source (n/a). |
| E2 | mean_var k=1, 8-seed pooled mean (seeds 42-49) | 14d | 56.1% | -22.6% | 2.08 | n/a | 2.50 | 82.2% | 57.3% | -23.8% | 2.12 | `data/scratch_rl/e2_eval/e2_eval.csv` | Mean across 8 seeds; Sortino not in source (n/a). |
| P2-a | a: random offsets (seed 42) | 8w | 40.0% | -16.8% | 1.91 | n/a | 2.38 | 58.0% | 41.7% | -18.1% | 2.01 | `data/scratch_rl/p2_eval/a_off/eval.csv` | Matched row present only for 8w. |
| P2-a | a: random offsets (seed 42) | 14d | 40.4% | -19.0% | 1.92 | n/a | 2.12 | 58.1% | n/a | n/a | n/a | `data/scratch_rl/p2_eval/a_off/eval.csv` | No 14d matched row in file: matched n/a. |
| P2-b | b: offsets + mixed cadence (seed 42) | 8w | 51.5% | -22.1% | 2.04 | n/a | 2.33 | 71.5% | 51.4% | -21.7% | 2.05 | `data/scratch_rl/p2_eval/b_offmix/eval.csv` | Matched row present only for 8w. |
| P2-b | b: offsets + mixed cadence (seed 42) | 14d | 52.3% | -22.2% | 2.09 | n/a | 2.36 | 71.4% | n/a | n/a | n/a | `data/scratch_rl/p2_eval/b_offmix/eval.csv` | No 14d matched row in file: matched n/a. |
| P2-c | c: mixed cadence + sub-windows (seed 42) | 8w | 42.8% | -15.4% | 2.05 | n/a | 2.77 | 60.4% | 43.4% | -18.8% | 2.02 | `data/scratch_rl/p2_eval/c_mixsub/eval.csv` | Matched row present only for 8w. |
| P2-c | c: mixed cadence + sub-windows (seed 42) | 14d | 41.8% | -22.0% | 1.74 | n/a | 1.90 | 60.9% | n/a | n/a | n/a | `data/scratch_rl/p2_eval/c_mixsub/eval.csv` | No 14d matched row in file: matched n/a. |
| P3 | v3ab observation set, 3-seed pooled mean (42-44) | 8w | 49.0% | -18.7% | 2.05 | n/a | 2.63 | 69.4% | 49.1% | -20.9% | 2.04 | `data/scratch_rl/p3_eval_s42/eval.csv; data/scratch_rl/p3_eval_s43_44/eval.csv` | Mean of seeds 42-44; Sortino not in source. |
| P3 | v3ab observation set, 3-seed pooled mean (42-44) | 14d | 49.0% | -17.9% | 2.15 | n/a | 2.77 | 68.8% | 49.9% | -21.2% | 2.09 | `data/scratch_rl/p3_eval_s42/eval.csv; data/scratch_rl/p3_eval_s43_44/eval.csv` | Mean of seeds 42-44; Sortino not in source. |
| P4 | composite_paper reward (seed 42) | 8w | 62.8% | -21.2% | 2.25 | n/a | 2.96 | 84.1% | 59.4% | -24.4% | 2.09 | `data/scratch_rl/p4_eval_composite_paper/eval.csv` | Seeds 43/44 trained (p4_comp_s43/44) but no eval output. |
| P4 | composite_paper reward (seed 42) | 14d | 59.4% | -22.6% | 2.14 | n/a | 2.62 | 85.3% | 60.3% | -24.8% | 2.14 | `data/scratch_rl/p4_eval_composite_paper/eval.csv` |  |
| P4 | mv1_down reward (seed 42) | 8w | 49.7% | -20.0% | 1.96 | n/a | 2.48 | 72.3% | 52.8% | -22.1% | 2.06 | `data/scratch_rl/p4_eval3/eval.csv` | Trained in data/scratch_rl/p4_mv1_down. |
| P4 | mv1_down reward (seed 42) | 14d | 49.8% | -20.2% | 2.12 | n/a | 2.46 | 69.6% | 53.6% | -22.5% | 2.11 | `data/scratch_rl/p4_eval3/eval.csv; p4_eval4/eval.csv` |  |
| E1 | median ensemble of mean_var k=1 seeds 42-44 (action median) | 8w | 65.1% | -20.0% | 2.33 | n/a | 3.25 | 83.0% | 60.9% | -24.9% | 2.09 | `data/scratch_rl/e1_ensemble/eval.csv` | Picked on holdout; loses 3 of 6 walk-forward folds (tracker). |
| E1 | median ensemble of mean_var k=1 seeds 42-44 (action median) | 14d | 58.6% | -20.2% | 2.23 | n/a | 2.91 | 81.0% | 60.1% | -24.7% | 2.14 | `data/scratch_rl/e1_ensemble/eval.csv` | Picked on holdout; loses 3 of 6 walk-forward folds (tracker). |
| X1 | equity floor 0.25, k1 and k2, seeds 42-44 | 8w | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv (smoke only)` | pending: 6 trainings exit 0 (data/scratch_rl/x1_logs/lanes_status.txt) but no eval.csv for k1/k2. |
| X1 | equity floor 0.25, k1 and k2, seeds 42-44 | 14d | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `data/scratch_rl/x1_eval/eval_rows.csv (smoke only)` | pending: 6 trainings exit 0 (data/scratch_rl/x1_logs/lanes_status.txt) but no eval.csv for k1/k2. |
| X2 | equity floor 0.0, k1, 3-seed pooled | 8w | 54.0% | -21.0% | 1.86 | 2.85 | 2.57 | 75.7% | 52.4% | -22.6% | 1.74 | `data/scratch_rl/x2_eval/eval.csv` | Mean of seeds 42-44. |
| X2 | equity floor 0.0, k2, 3-seed pooled | 8w | 46.9% | -19.2% | 1.83 | 2.81 | 2.45 | 68.2% | 45.8% | -20.2% | 1.74 | `data/scratch_rl/x2_eval/eval.csv` | Mean of seeds 42-44. |
| X2 | equity floor 0.0, k1+k2, 6-run pooled | 8w | 50.5% | -20.1% | 1.84 | 2.83 | 2.51 | 71.9% | 49.1% | -21.4% | 1.74 | `data/scratch_rl/x2_eval/eval.csv` | Mean of 6 runs. |
| X2 | equity floor 0.0, k1, 3-seed pooled | 14d | 52.9% | -23.0% | 1.77 | 2.69 | 2.30 | 77.4% | 52.8% | -22.8% | 1.77 | `data/scratch_rl/x2_eval/eval.csv` | Mean of seeds 42-44. |
| X2 | equity floor 0.0, k2, 3-seed pooled | 14d | 46.1% | -20.4% | 1.76 | 2.67 | 2.26 | 69.5% | 45.9% | -20.4% | 1.77 | `data/scratch_rl/x2_eval/eval.csv` | Mean of seeds 42-44. |
| X2 | equity floor 0.0, k1+k2, 6-run pooled | 14d | 49.5% | -21.7% | 1.76 | 2.68 | 2.28 | 73.5% | 49.3% | -21.6% | 1.77 | `data/scratch_rl/x2_eval/eval.csv` | Mean of 6 runs. |
| H2 | S2 (gamma 0), 3-seed pooled | 8w | 57.1% | -20.1% | 2.11 | 2.72 | 2.84 | 79.3% | 55.3% | -23.0% | 2.07 | `runs_h2/eval/s2_seed42-44.json (worktree agent-a0804b0bf3e4723ae)` | Mean of seeds 42-44. |
| H2 | S2 (gamma 0), 3-seed pooled | 14d | 56.8% | -21.6% | 2.25 | 2.82 | 2.64 | 77.2% | 53.7% | -22.6% | 2.11 | `runs_h2/eval/s2_seed42-44.json (worktree agent-a0804b0bf3e4723ae)` | Mean of seeds 42-44. |
| H2 | S3 (log_std -1), 3-seed pooled | 8w | 52.3% | -23.4% | 2.04 | 2.66 | 2.25 | 74.4% | 53.1% | -22.2% | 2.06 | `runs_h2/eval/s3_seed42-44.json (worktree agent-a0804b0bf3e4723ae)` | Mean of seeds 42-44. |
| H2 | S3 (log_std -1), 3-seed pooled | 14d | 52.5% | -21.2% | 2.14 | 2.75 | 2.48 | 71.9% | 53.4% | -22.4% | 2.11 | `runs_h2/eval/s3_seed42-44.json (worktree agent-a0804b0bf3e4723ae)` | Mean of seeds 42-44. |
| H2-ctl | H2 control (current settings), 8-seed pooled | 8w | 58.4% | -22.9% | 2.07 | 2.66 | 2.59 | 83.6% | 59.0% | -24.2% | 2.09 | `runs_h2/eval/control_8seed.json (worktree agent-a0804b0bf3e4723ae)` | Same configuration as E2 (8 seeds). |
| H2-ctl | H2 control (current settings), 8-seed pooled | 14d | 56.1% | -22.6% | 2.08 | 2.62 | 2.50 | 82.2% | 57.3% | -23.8% | 2.12 | `runs_h2/eval/control_8seed.json (worktree agent-a0804b0bf3e4723ae)` | Same configuration as E2 (8 seeds). |
| H1 | oracle, 2-level {0.5,1} (HINDSIGHT, not tradable) | 8w | 80.7% | -25.7% | 1.98 | 3.13 | 3.14 | 90.0% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | oracle, 2-level {0.5,1} (HINDSIGHT, not tradable) | 14d | 111.7% | -15.7% | 2.84 | 4.86 | 7.10 | 85.3% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | oracle, 5-level {0..1} (HINDSIGHT, not tradable) | 8w | 88.0% | -25.7% | 2.15 | 3.43 | 3.42 | 80.0% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | oracle, 5-level {0..1} (HINDSIGHT, not tradable) | 14d | 153.8% | -9.8% | 3.87 | 7.17 | 15.65 | 70.5% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | same as oracle {0.5,1} with 1-step delay (tradable check) | 8w | 62.2% | -24.5% | 1.77 | 2.68 | 2.53 | 90.0% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | same as oracle {0.5,1} with 1-step delay (tradable check) | 14d | 57.2% | -25.1% | 1.77 | 2.69 | 2.28 | 84.6% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | same as oracle {0..1} with 1-step delay (tradable check) | 8w | 50.7% | -21.3% | 1.61 | 2.42 | 2.38 | 80.0% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |
| H1 | same as oracle {0..1} with 1-step delay (tradable check) | 14d | 40.0% | -24.0% | 1.46 | 2.23 | 1.66 | 69.2% | n/a | n/a | n/a | `runs_h1 taskA_summary.csv (worktree agent-a31db186a7b693ee9)` | Matched n/a: no static row at the same avg equity; nearest static grid row used only in notes. |

### Notes and gaps

- Pooled rows: arithmetic mean across seeds of each metric (not pooled return series). Matched columns are pooled the same way, each seed against its own average equity.
- **Sortino n/a** for P1, E2, P2, P3, P4, E1: no daily return series was saved (`e2_eq_series.json` and `p3_cache/all.pkl` hold equity decisions or features only). Sortino was not recomputed; it needs a re-run of the eval. Sortino is read from files for X1/X2 (not yet produced), H1, H2, W1 and the static/SPY/B.5 reference rows.
- **Computed, not read**: SPY (from `data/raw/SPY.parquet` adj_close; matches tracker sec. 2); B.5 locked from `data/scratch_rl/baseline_backup/nav_b5_backtest.parquet` (CAGR, MaxDD, Sharpe, Sortino from daily NAV, Sharpe = mean/std*sqrt(252), Sortino with downside deviation over all days); Calmar for the tracker and E6 reference rows (CAGR/|MaxDD|). Computed B.5 holdout (21.0% / -31.5% / 1.27) does not match E6 (20.7% / -33.0% / 1.270) for the same window: source NAV provenance unknown.
- **B.5+B.4 equity-only reference (14.1% vs 22.5-23.1%)**: the 14.1% holdout CAGR and the 21.3% 3y CAGR exist only in tracker sec. 2; no output file in the repo or scratchpad carries them. `/private/tmp/claude-501/-Users-shivamgupta-github-us-rl-portfolio/5058cb96-5758-4d0d-bf44-39a776434699/scratchpad/eq_eval.log` (2026-11-25) reports B.5 locked Sharpe 1.108 and MaxDD -20.40% at 10 bps, window not stated (its MaxDD matches the tracker holdout row). The static 50% holdout CAGR is 22.6% (X1 file, P1, P2) and 22.8% (H1 `taskA_summary.csv`, Sharpe 1.057 vs 1.044 elsewhere). The tracker's 23.1% is the j2r 3y CAGR, so it is not a holdout reference. Unresolved; the tracker's own reconciliation gate G0 is still open.
- **Matched-static at 14d**: n/a for P2 a/b/c (file has no 14d matched row). Other 14d matched values come from the same file as the agent row (P3, P4, E2, E1 files) or from `e1_ensemble/eval.csv` (P1 seed 42 uses E2 file).
- **H1 matched n/a**: H1 has no static row at the oracle average equity (0.844, 0.688, 0.812, 0.623 etc.). Nearest static grid rows (0.80 and 0.90, or 0.70) are in `taskA_summary.csv` but were not interpolated.
- **H1 is hindsight**: the oracle rows use future returns to choose exposure and are not tradable. Only the `delay1` rows are a tradable check.
- **X1 pending**: all six floor-0.25 trainings (k1/k2 x seeds 42-44) exited 0 (`data/scratch_rl/x1_logs/lanes_status.txt`; models in `data/scratch_rl/x1_f025_*/models`), but no eval.csv exists. `data/scratch_rl/x1_eval/eval_rows.csv` only has `smoke` rows, which are not used.
- **P4**: composite seeds 43/44 trained (`p4_comp_s43`, `p4_comp_s44`) with no eval output. The labels for `s43`/`s44` in `p4_eval5`/`p4_eval6` could not be mapped to a reward, so they are excluded. `downside_mv` (`p4_eval_downside_mv`) and `diff_sharpe` (`p4_eval_diff_sharpe`) exist but are not in this table. Only seed 42 is shown for composite and mv1_down.
- **P2 and P1 seed 42** are single-seed results. The E2 8-seed mean is the replication check for the seed-42 row.
- **E1** is the median of three mv1 seeds (42-44), not the 8-seed mean. It was picked on holdout; the tracker records it losing 3 of 6 walk-forward folds.
- **W1 windows** are fold test windows: F1 = 2020-21 (contains the 2020 crash), F2 = 2022, F3 = 2023-Apr 2026. They are in section C, not in the holdout or 3y sections. Matched values are the file's `static_*` columns. LOW uses seeds 42-44 and CTL seeds 42-43 (per the file).
- **H2 control** (8 seeds) equals the E2 pooled values, as expected.
- Grid 14d static rows are in the X1 and H1 files but were omitted from the reference rows for compactness.
- Holdout reuse: the holdout (2019-2026-04-24) has been used for selection; the 3y window sits inside it. Seed noise is about 0.05 Sharpe (tracker sec. 8).


### C. Walk-forward fold windows (W1, not holdout or 3y)

| ID | Experiment / variant | Grid | CAGR | MaxDD | Sharpe | Sortino | Calmar | Avg equity | Matched-static CAGR | Matched-static MaxDD | Matched-static Sharpe | Source | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 | LOW (low update intensity), F1 test 2020-21, 3-seed mean | 8w | 46.7% | -48.2% | 1.10 | 1.62 | 0.97 | 80.1% | 47.8% | -47.3% | 1.13 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | LOW (low update intensity), F1 test 2020-21, 3-seed mean | 14d | 44.2% | -48.6% | 1.08 | 1.58 | 0.91 | 80.7% | 45.2% | -48.0% | 1.10 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | LOW (low update intensity), F2 test 2022, 3-seed mean | 8w | -34.1% | -38.2% | -0.55 | -0.79 | -0.89 | 81.5% | -33.9% | -38.0% | -0.55 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | LOW (low update intensity), F2 test 2022, 3-seed mean | 14d | -40.3% | -41.2% | -0.82 | -1.17 | -0.98 | 81.3% | -39.9% | -40.8% | -0.81 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | LOW (low update intensity), F3 test 2023-Apr 2026, 3-seed mean | 8w | 49.9% | -22.1% | 1.70 | 2.63 | 2.26 | 72.8% | 49.9% | -22.0% | 1.69 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | LOW (low update intensity), F3 test 2023-Apr 2026, 3-seed mean | 14d | 60.4% | -22.1% | 1.95 | 3.06 | 2.73 | 72.7% | 60.4% | -22.0% | 1.96 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | CTL (current settings), F1 test 2020-21, 2-seed mean | 8w | 42.6% | -43.5% | 1.12 | 1.65 | 0.98 | 71.1% | 42.9% | -43.2% | 1.13 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | CTL (current settings), F1 test 2020-21, 2-seed mean | 14d | 39.8% | -43.8% | 1.09 | 1.60 | 0.91 | 71.1% | 40.3% | -43.7% | 1.10 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | CTL (current settings), F2 test 2022, 2-seed mean | 8w | -32.1% | -36.7% | -0.54 | -0.78 | -0.88 | 78.0% | -32.3% | -36.7% | -0.55 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | CTL (current settings), F2 test 2022, 2-seed mean | 14d | -38.7% | -39.7% | -0.82 | -1.16 | -0.98 | 78.1% | -38.5% | -39.5% | -0.81 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | CTL (current settings), F3 test 2023-Apr 2026, 2-seed mean | 8w | 56.3% | -23.4% | 1.71 | 2.69 | 2.40 | 77.0% | 53.1% | -23.2% | 1.69 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |
| W1 | CTL (current settings), F3 test 2023-Apr 2026, 2-seed mean | 14d | 64.5% | -23.8% | 1.93 | 3.07 | 2.71 | 73.5% | 61.1% | -22.2% | 1.96 | `runs_w1/eval/fold_eval.csv (worktree agent-a44a76ccd7b545cbb)` |  |

## 12. Track F result: reference reconciled (2026-11-27, agent ac2d8568346f01881, gate G0)

Verdict: the B.5+B.4 equity-only reference REPRODUCES exactly from the equity-only code (now committed). The gap to ~23% is gross exposure, not a failed reproduction. Outputs: worktree agent-ac2d8568346f01881, `runs_f/`.

- Reproduced vs quoted (convention: CAGR on 365.25-day calendar, Sharpe = mean/std * sqrt(252), Sortino = zero-threshold semideviation, Calmar = CAGR/|MaxDD|): holdout CAGR 14.13 / MaxDD -20.40 / Sharpe 1.105 / Sortino 1.651; 3y 21.33 / -8.18 / 2.087 / 3.329; 2020 crash 7.41 / -17.58 / 0.397 / 0.564. Average daily stock gross 28.8% (median 28.1%, IQR 25.0-33.0%); 48 rebalances, mean turnover 0.26.
- Convention warning: the repo's `calculate_metrics` uses Sharpe = CAGR/vol and Sortino = CAGR/neg-std (holdout 1.11 / 1.58); do not mix conventions.
- Setup warning: a worktree whose scripts still include TLT/GLD/UUP in TREND_ASSETS gives 14.7% / -27.7% (wrong). Equity-only code (TREND_ASSETS = ["SPY"], committed in 860fa26) gives the reference.
- Reconciliation: static at 28.8% equity (8w) gives 13.87 / -20.10 / 1.106 / 1.645; static 50 / 72 / 100 (8w): CAGR 24.04 / 34.37 / 46.82, MaxDD -32.75 / -44.13 / -56.34. Static-28.8 equals 0.576 x the static-50 return series exactly: CAGR scales ~linearly, MaxDD does not (-18.9 predicted vs -20.1 actual). So 14.1% = the book at ~28.8% gross; ~23% = the same book at 50% gross.
- Truncation artifact: the env never simulates the last decision's period (2026-04-06 to 04-24). Raw env gives static-50 22.75 (8w) / 23.00 (14d) and the tracker's static CAGRs (22.5 / 32.0 / 43.3) match this truncated run; with a terminal no-trade date they are 24.0 / 34.4 / 46.8 (8w). Treat static-row CAGRs in this tracker as understated by ~0.3-2.5 pp (larger at higher gross); Sharpe unaffected.
- Provenance: the 14.1 / -20.4 / 1.10 / 1.65 figures were only in this tracker; Sharpe 1.108 / MaxDD -20.40% also appear in the scratchpad `eq_eval.log` (2026-11-25), no CAGR printed. The "23.1% = j2r 3y CAGR" suspicion could not be confirmed (no CAGR in docs/paper_trading_j2*); the 23.1 in question is static-50 14d, which reproduces (23.0-23.5).

B.4 timing value (what RL must beat): B.5+B.4 time-varying minus constant at the same average gross (Sharpe / Calmar / MaxDD pp / CAGR pp): holdout 8w +0.00 / +0.00 / -0.3 / +0.26; holdout 14d +0.02 / +0.06 / +1.05 / +0.47; 3y 8w +0.21 / +0.39 / +0.3 / +2.5; 3y 14d +0.15 / +0.32 / +0.5 / +1.6; 2020 8w +0.03 / +0.09 / +2.3 / +0.8; 2020 14d +0.10 / +0.20 / +2.1 / +2.6; 2022 8w -0.03 / -0.02 / -0.3 / -0.6; 2022 14d +0.02 / +0.01 / -0.1 / -0.1.

Implication: on the full holdout B.4's own risk engine adds essentially no Sharpe over a constant-gross static; its value is in the 3y window (Sharpe +0.15-0.21) and about 2 pp of 2020 MaxDD, with 2022 neutral. The bar R1 must clear is therefore modest on the holdout and larger on 3y/2020. Also, most of "B.5+B.4 protects capital" is the LOW AVERAGE GROSS (~29%), not timing: any constant-gross static at 29% gets the same -20% MaxDD.

## 13. Track G1 result: drawdown signal is real but is trailing volatility; monetization fails (2026-11-27, agent a0f565fbd18acc683, gate G1)

Worktree agent-a0f565fbd18acc683, outputs `runs_g1/` (monetise_14d.csv, monetise_8w.csv, scripts g1_*.py).

- Forecast, 14d (n=470, 185 drawdown events): pooled leave-one-regime-out IC 0.385 (block-permutation p 0.0005, circular-shift p 0.022, joint p 0.0005); AUC 0.684 (circ p 0.020); expanding+embargo IC 0.288 (circ p 0.043). 8w (n=117): IC 0.220 (block p 0.04, circ p 0.10), AUC 0.45 (n.s.). Joint p-values are optimistic; the circular null is the honest one for autocorrelated targets. Signal sits in the 2020 fold (IC 0.56, block p 0.020; AUC 0.83); 2022 fold IC -0.13, 2021 IC -0.36.
- Trivial predictors beat the 42-dim state (14d pooled IC / AUC): vol_book_21 0.437 / 0.719, VIX 0.434 / 0.734, stress 0.400 / 0.722, previous drawdown 0.389; state model 0.385. Incremental over vol_book_21: delta IC -0.006 (block p 0.80), residualised-target IC 0.117 (block p 0.20); only the partial-correlation spec clears p < 0.05 (0.028). 8w: delta IC -0.11 (p 0.91). Conclusion: the "predictable drawdown" signal is trailing volatility persistence; the state adds little beyond it.
- Monetization (fitted logistic map e = 0.5 + 0.5*sigmoid(a + b*z) on predicted drawdown, or on vol_book_21; per-fold fitting on Calmar): all four pre-registered bars FAIL on both grids. 2020 crash MaxDD (14d): state map -43.5% vs matched static -37.0% (6.5 pts DEEPER), vol map -44.8% vs -37.8%; 2022: state -41.4% vs -33.8%. Mean Calmar over holdout/2020/2022/3y: B.4 0.569; state map 0.344 (matched static 0.595); vol map 0.463 (static 0.641). 8w similar (B.4 0.595; state 0.207; vol 0.290). B.4 has the shallowest MaxDD in every window on both grids (2020: -31.3% on 14d).
- Caveats: one crash event drives the signal; fitted slope b sits at the grid edge (-3) in most folds and intercept ranges -1.75..3.0 (maps unstable); the B.4 book includes the SPY beta overlay (gross ~1.03) while policies use the normalised stock book with equity <= 1; vol_book_21 was chosen as best trivial on observed data (selection not inside the nulls); isotonic mapping not tried; reused holdout.

Implication for RL: a risk-sizing policy built on this state does not beat constant-gross static, let alone B.4. The information content of the current observation set about the drawdown it could protect against is explained by trailing volatility. A better feature set (tracks FA, FB) is the remaining route; if it adds nothing beyond volatility, the RL value must come from the action/reward design (R1) or not at all.

## 14. Track FB result: candidate feature library v4 (2026-11-27, agent af86d15771da1cf40)

Worktree agent-af86d15771da1cf40 (nothing committed); outputs `runs_fb/` (fp0_inventory.csv, features_v4/, screen_v4/, scripts/), library `src/rl/features_risk_v4.py`, tests `tests/test_features_risk_v4.py` (14 pass) and `tests/test_features_v4_materialized.py`. STATUS: built and materialized, NOT yet certified (see docs/phases/rl_feature_certification.md).

- Data on disk: SPY, IWM, TLT, GLD, UUP, 11 sector ETFs (XLC from 2018-06, XLRE from 2015-10), ^VIX with OHLC/volume 2006-01-03..2026-11-24; 502 stock OHLCV files (current constituents only: survivorship), point-in-time S&P membership mask (2006+), fundamentals. NOT on disk (data requests): VIX3M/VIX9D, HYG/LQD, IEF/SHY, yield curve, event calendar.
- Library: 61 features in 7 groups, `features_at(date, history)` with an origin guard (rejects mid-sample start), expanding z-score (min 252 obs), winsorised +-3; includes HAR-RV (expanding OLS), VRP proxies, inverse-variance inputs, GJR-GARCH with FIXED parameters, 2-means regime on SPY downside deviation (refit yearly) and a simple persistent-regime baseline. Dead features: hhi_u, n_names (B.5 book is equal-weight top-20). Not done: a true statistical jump model.
- Materialized: daily_v4.parquet (4,607 rows 2008-01-01..2026-04-24, 61 columns), grid_14d_v4.parquet (478 rows), grid_8w_v4.parquet (120 rows) with targets T1 (path max drawdown), T2 (annualised vol), T3 (return), T4 (sign), T5 (regret = max(0.5R, R) - 0.72R) and regime block; feature_meta.csv; manifest.json (sha256, row counts, library hash).
- Screening (14d, 477 decisions, 9 blocks; circular block permutation L=10, 1000 draws, BH over 295 A1 and 159 A2 tests): the trivial set TR (trailing vol, VIX, stress, previous drawdown) gives pooled leave-one-regime-out IC T1 0.390, T2 0.721, T5 0.360. NO new feature adds measurable information beyond TR: best delta IC +0.022 (dd_s on T2) and +0.009 (beta_u_63 on T1), all BH q >= 0.68. Many features pass A1 but are TR-equivalent (clusters: {rv_u_21, har_u_fc, garch_u_fc, invvar_u_21, base_vol_21}, {rv_u_63, base_vol_63}, {rv_s_21, park_s_21, invvar_s_21}, {spd_b_21, base_ret_21}). T3 has univariate IC 0.10-0.15 for book vol and GARCH/HAR forecasts (q<0.01): the trailing-vol effect, not a new signal.
- Provisional v4 (19 dims, one per cluster): rv_u_5, rv_u_21, rv_u_63, rv_s_5, rv_s_21, vix_level, vr_u_5_63, downup_s_63, dd_s, dsp_s, dd_b, corr_held_21, disp_held_21, worst_dec_share, beta_u_63, tlt_vol_21, regime_km_bear, stress_b5, base_gross. Agent's own conclusion: freezing it is not supported by A2; the honest minimal set is TR itself.
- Caveats: 9 blocks (~48 effective blocks with L=10); 295 + 159 tests; unit-book returns from H1's cache; survivorship in universe-level breadth; same-day VIX close; NOT done: group ablation (A3), 8w screen, in-agent permutation (A4), GARCH fitting, true jump model.

Next: EGM review of the feature set against the certification checklist (also asked to test whether this null is real, not an artefact of the target definitions or construction).

## 15. EGM review of feature set v4 (2026-11-27; reading-only; report in scratchpad `feature_review_report.md`)

Recommendation: CERTIFY WITH FIXES, scoped to a reduced set; do NOT certify the 61-feature / 19-dim v4 set as it stands (one lens said REJECT the 61/19-dim set and certify a reduced TR-4+ set). The "no feature beats trailing vol" null is NOT yet a demonstrated null. Empirical checks are being run separately by track FC (leak injection, truncation, rebuild, power analysis, survivorship).

Certification audit (by reading): M1 FAIL (truncation test vacuous: silently skips without history.pkl, 6 probe dates, upstream book/stress/membership never rebuilt on truncated data); M2 FAIL/NOT TESTED (env computes returns from the prior close at the decision date vs spec's t+1: unresolved mismatch); M3 PARTIAL/FAIL (guard rejects mid-history starts, does not prove path independence; baseline NAV filled with 0 before live start puts zero rows into z-score baselines of dd_b, dsp_b, rec_b, spd_b_*, base_ret_21, base_gross, worst_dec_share); M4 PARTIAL; M5 FAIL (no env/prod wiring; features_at recomputes the whole panel per call); M6 FAIL (rebuild reads unit_ret from another worktree's H1 cache at hard-coded paths; no NaN/inf/constant checks; hhi_u and n_names constant); M7, M8 NOT TESTED (target code looks right: forward-only, last decision NaN); M9 FAIL (nothing implemented); M10 PASS by design.

Blockers: (1) unit-book returns not reproducible from the repo; (2) no plug-in path to env/training/prod; (3) GFC 2008-09 block has no book-feature coverage (rv_u_* first valid 2009-01-09, har_u_fc 2010-03-04), so the null excludes the worst drawdown regime; (4) incremental test compares different row masks (late-starting features confounded with sample change); (5) truncation test vacuous and M9 absent.

Why the null is unproven: BH cannot reject (500/1000 permutations give p-value floors 0.002/0.001, best possible q ~0.30; observed min q 0.677 carries no information); wrong null (permutes y, destroying the TR-to-y link; the incremental question needs permuting the feature or the residual); low power (IC SE ~0.05-0.06; detectable delta IC ~0.02-0.03 on T1, ~0.01 on T2, same order as the largest observed deltas); collinearity (most candidates are vol proxies); ridge cannot see interactions; 8w grid not screened; block length 10 short for autocorrelated 14d targets.

Other major findings: T5 (max(0.5R,R) - 0.72R) is a V-shape in R (magnitude/vol proxy), not a sleeve call: replace by signed regret over a grid of equity shares; survivorship (current constituents only, no point-in-time mask on breadth/cross-sectional features before 2015; netnewhl divides by ffilled counts); GARCH forecast off-by-one (conservative, mislabelled one-step-ahead); duplication/convention clash with state_builder_v2 (rolling-252 rank vs expanding z); dead and odd features (binary flags z-scored); runtime and KMeans/BLAS determinism.

Zoom-out: run one cheap decision experiment before more feature work: PPO on TR-4 (vol_book_21, vol SPY, VIX, stress_b5, previous drawdown, base_gross, equity share) vs a hand-set vol-target rule and B.4 in the same harness; if PPO cannot beat the rule, stop RL feature work. Note the contradiction: risk is highly predictable (T2 IC ~0.72) but returns are not (~0.02); if the RL objective rewards CAGR, vol information is correctly unused, so the objective may be the real problem; sleeve value shows in Sharpe/MaxDD, which a return IC does not test.

Hardening plan (~24 h total, ~12 h wall-clock): Phase 0 (~4 h serial): in-library unit_ret and history adapter, remove hard-coded paths, drop dead features, mask pre-inception NAV features, membership mask, fix GARCH timing/label, replace T5, GFC warm-up or explicit exclusion, regenerate manifest; Phase 1A/1B (parallel ~8 h + ~6 h): the tests listed in rl_feature_certification.md section 2 (non-vacuous truncation on 100+ dates + crisis dates, future corruption, injected-leak detector, availability lags, env alignment, path independence, causal normalisation, no constant/duplicate columns, manifest/rebuild determinism, target hygiene, embargo >= 2 decisions); Phase 2 (~6 h slow): train/serve parity, 200-noise-feature null calibration, block-permuted feature has no IC, synthetic-signal power curve; Phase 3 (~2 h): sign-off. Selection experiment FS to do differently: fix row masks and embargo first, conditional null (permute feature or residual), >= 20k permutations or analytic p-values, power curve first, screen the 8w grid, TR-only and FA-cleaned baselines, GBM/interaction and tail targets, sleeve-level overlay evaluation with paired block bootstrap, pre-register TR-4 as default, data requests VIX3M/VIX9D and HYG/LQD first.

## 16. Track FA result: audit of the existing 42-dim observation set (2026-11-27, agent a01d398dec9b4270c)

Worktree agent-a01d398dec9b4270c, outputs `runs_fa/` (dims_verdict_14d.csv, a0..a3 CSVs, ub_sleeve_policy_14d.csv, effective_n_14d.csv, dataset_14d.pkl, dataset_8w.pkl). Analysis only.

Verdict: the existing set carries no usable, regime-stable signal for changing sleeves. Every feature that passes the univariate screen re-expresses the trivial volatility/drawdown predictors (TR). The signed sleeve call D = R(1.0) - R(0.72) is not predictable out of sample.

- Dataset: 42-dim state from the e=1 env run, matches H1's cache exactly (max diff 0.0); 477 labelled decisions (14d), 119 (8w). Dims 36-38 constant in this run (their policy-state effect untested).
- Hygiene: constants d36-38; redundant d31 with d04 (VIX 62 / 153); truncated-history test zero diff on all dims; NAV-restart test: only d39-41 change at episode start (own-NAV dims are restart-dependent); d34/d35 (XLRE/XLC vol) zero before 2016/2018; d23/d24 (XLRE/XLC momentum) equal minus SPY momentum before ETF inception (44% / 59% of decisions); the sector parquet correlates 0.976 with ETF 63d returns (construction/causality unverified).
- Incremental over TR (clean set, block-shift null 1000 draws, BH): TR alone IC T1 0.43, T2 0.75, T5 0.31, D -0.05. Best single-feature delta IC: T1 +0.007, T2 +0.006, T5 +0.014, D +0.063; smallest p 0.34 / 0.38 / 0.40 / 0.055; no q < 0.1. 8w replication same picture (best D delta +0.106, p 0.072, q 0.54). With artifact dims d34 looked significant on D (delta +0.09, p 0.002): a pre/post-2016 data artifact.
- Group ablation: no group significant (largest: own-portfolio group leave-out T2 +0.054, p 0.12; T1 +0.035, p 0.17); adding groups to TR mostly lowers IC (ridge overfit).
- Upper bound (leave-one-regime-out GBT / ridge, threshold policy over {0.5, 0.72, 1.0}, env-based, matched static asserted within 1e-3): GBT IC for D 0.01, sign AUC 0.51; captures 9% (GBT) / 11% (ridge) of the oracle gain, -2% with a one-step delay. Sharpe / Calmar: GBT 0.76 / 0.40, ridge 0.76 / 0.35 vs matched static 0.83 / 0.42; oracle 1.82 / 2.01.
- Keep/drop of the 42 dims: KEEP none (d13 is a TR member); DROP constant d36-38; redundant d31; A0 artifact / own-NAV d23, d24, d34, d35, d39, d40, d41; 16 pass A1 but have no A2 increment (mostly vol, drawdown, sector vol); 14 fail A1.
- Caveats: 2018 Jan-Sep unassigned in the block spec (used H1's 2013-18Q3 block; 2018Q4 has 6 decisions); effective n (AR1) T1 ~156, T2 ~70, T5/D ~375-480; same reused history, 2019-2026 not sealed; block nulls are circular shifts (min shift 20); no A4, no T3/T4 in A2. The EGM review's null-power critique (section 15: permutation count, null choice, power) applies equally to this audit: treat the per-feature "no increment" results as "not detectable with this design".

## 17. Track FC result: empirical certification checks of feature set v4 (2026-11-27, agent a468abd5b451fcba8)

Worktree agent-a468abd5b451fcba8 (nothing committed); evidence `runs_fc/`; tests `tests/fc_cert_lib.py`, `tests/test_features_v4_cert_{causality,stats,targets,nulls,sitems}.py`, `conftest.py` (fast: 32 pass, 2 fail, 2 xfail; slow: 200-draw null and deterministic rebuild pass). Verdict: NOT CERTIFIABLE as built; causality holds, but M2, M6, M8, S1 fail.

- M1 PASS: 100 dates (incl. 2008-10-10, 2020-03-16, 2022-06-15) x 61 features x {truncation, NaN-after, noise-after}: 0 mismatches; an injected next-day-SPY leak column IS detected (M9 leak check works).
- M2 FAIL (open): env fills at close t (returns from t+1 use close t as base), not "t+1" as the certification spec says; VIX close is same-day and publishes after the 16:00 close; adj_close is current-vintage restated (no vintage store). Unit-book vs env routine: 477 decisions, max deviation 3e-16.
- M3 PASS for library/store; FAIL for env (state_builder_v2 still reads the episode's own NAV; xfail test). M4 PASS with coverage caveat (23 features start after 2008-01-31; har/garch/regime_km NaN for 505 days in 2008-09; 53 grid14 rows pre-2010 unusable; complete-case rows 421 of 478). M5 PASS (store vs prod `features_at` vs training table agree to 1e-9 on 2015-06-12 via src/rl/features_v4_env.py; env observation does not yet consume v4). M10 PASS for v4 library.
- M6 FAIL as built: 2 dead (hhi_u, n_names) and 3 exact duplicates (invvar_u_21 = rv_u_21, invvar_s_21 = rv_s_21 after log-z; base_ret_21 = spd_b_21); two rebuilds bitwise identical only with PYTHONHASHSEED=0 and 1 BLAS thread (canonical round-10dp checksum matches across 4 builds; FB's manifest sha not reproduced, 3e-14 value diff).
- M7 PASS with flags (ADF non-stationary: ewdn_u_126, base_vol_63; |z|>6 events 333, concentrated in 2008-10 and 2020-03). M8 PARTIAL/FAIL: 14d targets match an independent recompute exactly (forward-only, last decision 2026-04-14 NaN and dropped, T5 formula correct); screen LORO had no embargo (embargo 2 changes IC by 0.0002); the 8w grid was built on a different H1 run than the features (T1 diff 0.070): FAIL. M9 PASS: 200 noise features (B=1000) p mean 0.53, KS p 0.42, 0 BH discoveries; block-permuting real features collapses median |IC| 0.28 -> 0.05. S1 FAIL (13 pairs |corr| > 0.95; 16 features with VIF > 10; greedy pruning needs 16 drops). S2 PASS. S3 PARTIAL (store lookup < 1 s; full panel build 3.4 s). S4 PARTIAL (no literature references).
- DATA DEFECT FOUND: H1's cache ends 2026-04-14 but `build_history` fillna(0) made unit_ret zero-return from 2026-04-15, pinning rv_u_5 at the -3 clip 2026-04-21..24. Fixed in the FC worktree (NaN after cache end, 158 days; `runs_fc/history_fixed.pkl`, rebuilt `runs_fc/features_v4_fixed/`). FB's `runs_fb/features_v4` still has the zero-fill tail.
- POWER ANALYSIS (planted signal, LORO ridge increment over TR, BH q < 0.10 over 59 tests): empirical detection is 0.00 at delta IC 0.02 / 0.05 / 0.10 and 0.03 at 0.15 (parametric normal-null: 0.10 / 0.43 / 0.98 / 1.00). Structural reason: minimum attainable p is 1/200 but the BH threshold is 0.10/59 = 0.0017, so the screen (A2: B=500, m=177) cannot reject anything. A null from this design means nothing below delta IC ~0.10 unless B >= 1000 and the family is small (use >= 20k draws or analytic block-adjusted p-values).
- SURVIVORSHIP: raw stocks are 502 current constituents, no index history in data/ (95 start after 2008-01-02, 47 after 2015; delisted 2008-2015 names absent: bias unmeasurable); the PIT mask `data/artifacts/universe_mask_sp500.parquet` is an ADV liquidity filter, not index membership; 237 holding-instances across 153 decisions sit outside the mask (mostly before 2018); empty book only on 2008-01-02, no partial books.
- Unverified: B.5 pipeline not re-run (history patched, not regenerated); VIX timing and adj_close vintage not checkable from the repo; ADF is a custom implementation; first M7 run printed z-values for 2026-05..07 before the window was restricted (no performance evaluated; sealed-window hygiene note).

## 18. Track FH result: hardening of feature set v4 -> v4.1 (2026-11-27, agent a6cfacb3e016cf4f0)

Worktree agent-a6cfacb3e016cf4f0 (nothing committed); outputs `runs_fh/` (features_v4_1/, screen_v4_1/, pytest logs); scripts `scripts/features_v4_{history_build,materialize,screen,before_after,stationarity}.py`. Verdict: NOT CERTIFIED as a signal library. Infrastructure checks pass; the screen finds no incremental information beyond trailing volatility, and power is too low to rule small signals out.

- Fixes (before -> after): dead/duplicate columns 5 -> 0 (48 features remain); zero-fill tail removed (rv_u_5 clip-pinned 4 days -> 0); 8w unit_ret deviation 0.052 -> 0.0 (both grids from one series); pre-inception NAV features no longer enter z baselines; T5 replaced by signed regret over equity shares (flat -2% period: 0.0044 V-shape -> -1.0 de-risk); breadth now uses the PIT mask; metadata text per feature.
- Survivorship: holdings outside the PIT mask on 153 of 478 14d decisions (237 instances, max weight 0.25, median 0.05, 83 decisions with >5% outside), concentrated 2008-2017; 0 of 120 on the 8w grid. Pre-2015 bias unmeasurable (current constituents only; mask is an ADV filter).
- Sign-off: M1 fast test pass, 100-date sweep did not finish (UNVERIFIED); M2 OPEN (env fills at close t vs spec t+1; spec amendment not written); M3 library/store pass, env (state_builder_v2) not wired; M4 pass (first complete-case date 2008-10-31); M5 pass (build_state_v4 plug-in, not wired into training); M6 fast pass, history-rebuild slow test not run (needs network for BK/CTRA); M7 flagged (ADF custom: rv_s_63, ewdn_u_126; flags unstable across builds); M8 pass; M9 pass (200 noise features B=20000 KS ok; leak detector flags injected leak); survivorship PARTIAL; S1 FAIL (waiver, VIF>10 on vol features); S3 full panel ~3.4 s (store read <1 s). Tests: fast 46 pass / 0 fail; slow stats 2 pass; causality sweep and rebuild unfinished.
- Power (N=455, m=60, BH q<0.10, AR(1)-planted signal with phi 0.80): before 0.01/0.02/0.05/0.09 at delta IC 0.02/0.05/0.10/0.15; after (analytic) 0.035/0.076/0.197/0.399; block-permutation B=20000: 0.04/0.03/0.06/0.18. Minimum detectable delta IC at 80% power is about 0.24. The screen cannot detect delta IC 0.05 at 80%; "no increment" is only meaningful for deltas of roughly 0.25 or more. (Strong autocorrelation of 14d targets, effective n small, is the cause; FC's earlier iid-planting numbers were optimistic.)
- Screen (T1, 48 features, B=20000): 31 BH rejections, all vol/drawdown predictors (rv_u_5, worst_dec_share, disp_held_21, corr_held_21, dd_b, dd_s, vix_level, stress_b5 ...). Incremental over trailing-vol baseline (IC 0.425): best delta IC 0.010 (disp_held_21), q 0.64; nothing significant.
- Consequence: more feature screening on 455 autocorrelated decisions cannot settle the question; the feature question must be answered by the decision experiment (RL on small risk sets vs vol rule and B.4), not by IC screens.

## 19. Track R1 result: baseline-relative multiplier action (2026-11-27, agent ae80a5baaf5ebaa0c)

Worktree agent-ae80a5baaf5ebaa0c (uncommitted); outputs `runs_r1/` (V1-V3 x seeds 42-44, eval/all.json, report_tables.md, regression report); code: `exposure_mix.apply_multiplier_mix` (m = exp(a ln3), stock sum capped at 1.0), env `action_mode=mult` (63-day forward reward window), `reward_v2.compute_reward_bl`, `train_rl_v2.py --action-mode mult`, `r1_*.py`, `tests/test_r1_multiplier.py` (7 pass; with test_equity_only 13 pass).

Result: FAILS the pre-registered bars. The learned multiplier adds leverage, not demonstrated timing value.

- Regression: a=0 weights bit-identical to B.5+B.4 equity book on 5085/5085 dates; env a=0 NAV vs independent recompute max rel err 7e-16. Baseline: 8w holdout MaxDD -20.4% (matches), CAGR 13.2% (reference 14.1%, unreconciled); 3y MaxDD -8.2%, CAGR 19.1% (ref 21.3%); 2020 crash -17.6%.
- Training: 9 runs completed; selected episodes V1 36/3/4, V2 30/3/4, V3 1/24/307: five of nine checkpoints are episodes 1-4, so selection is largely noise.
- Pooled (9 runs, agent minus a=0; t in brackets): 8w holdout dCalmar +0.039 (0.9), dSharpe -0.002 (0.0), dCAGR +8.6pp (3.0), dMaxDD -11.5pp worse (t -2.8), Calmar vs matched static +0.009. 14d holdout dCalmar +0.061 (1.0), dSharpe +0.056 (1.5), dCAGR +9.4pp, dMaxDD -11.1pp, vs static +0.092. Excluding 2019: 14d dCalmar -0.084 (t -3.0), dSharpe -0.048, dMaxDD -14.6pp; i.e. the 14d holdout gain is mostly 2019 (a logged validation block). 3y: 8w dCalmar +0.16 (0.9), 14d -0.07 (-0.6).
- Crash/bear MaxDD (baseline in brackets): 2020 8w [-17.6%] V1 -29.4, V2 -25.5, V3 -25.3; 2020 14d V1 -28.6, V2 -26.6, V3 -36.0; 2022 8w [-17.1%] V1 -15.0, V2 -12.7, V3 -22.2; 2022 14d [-18.2%] V1 -22.0, V2 -18.5, V3 -24.4.
- Controls: shuffled-observation control degrades Calmar in only 3 of 9 runs (other six are baseline-like, i.e. the agent barely uses the observation); 1-step delay on the best validation seed removes the 8w gain (Calmar 1.02 -> 0.58) but not on 14d.
- Bars: pooled Calmar and Sharpe beat a=0 on both grids FAIL (8w Sharpe -0.002); pooled t>2 FAIL (max 1.5); 2020 crash MaxDD not worse FAIL in all six cells (7 to 18 pp worse); 2022 MIXED; gross std > 0.05 PASS (8 of 9); shuffle degrades PARTIAL.
- Reading: gains come from higher average gross (CAGR +9pp) while MaxDD deepens ~11pp, so Calmar is flat and matched constant-gross static is about equal. Baseline-relative framing did not make the agent de-risk in the crash; consistent with FA/G1/FH (no usable timing signal in the observation) and with W1/X2.
- Caveats: repo Sharpe/Sortino are CAGR/vol and CAGR/downside-vol; crash windows have only 3 (8w) / 11 (14d) decisions so MaxDD is used; 2019-only split not computed separately; reward drawdown lambda 0.15 inherited, untuned; forward window clipped at split end; load_inputs attempts a network fetch for BK/CTRA each run (no writes under data/ observed).

## 20. Track C1 result: clean risk observations (2026-11-27, agent a5162ab49bcbd8f9f)

Worktree agent-a5162ab49bcbd8f9f (uncommitted); outputs `runs_c1/` (18 runs, eval JSON, aggregate_output.txt, summary_pooled.csv, summary_per_run.csv). Code: `src/rl/state_builder_c1.py` (O1 36 dims: drops XLRE/XLC sector, trend_frac, cash_frac; O2 33 dims: also drops NAV dims 39-41; O3 44 dims: O2 + 11 causal continuous-book / SPY / VIX risk features), env `obs_version`, `train_rl_v2.py --obs-version/--train-cost-bps/--val-blocks`, `scripts/run_c1_eval.py`, `aggregate_c1.py`, `tests/test_rl_c1_obs.py` (6 pass). Continuity check: mid-start episodes match continuous-run observations exactly for O2/O3.

Result: FAILS all pre-registered bars. No variant beats matched static on both grids; crash-fold MaxDD gains are under 4 points (bar 10); the shuffled-observation control does not consistently degrade.

- Setup: 18 runs (O1/O2/O3 x mean_var k=1,2 x seeds 42-44), 10 bps train/val cost, up to 150 episodes, Calmar selection on mean of 2017-18 and 2019 blocks (2019 therefore overlaps the holdout); most runs early-stopped at episodes 51-70.
- Holdout 8w pooled agent minus matched static Sharpe (SE): O1 k1 +0.002 (0.001), O1 k2 -0.046 (0.028), O2 k1 +0.001, O2 k2 +0.031 (0.059), O3 k1 -0.001 (0.005), O3 k2 +0.032 (0.021); dCalmar mostly negative (O1 k2 -0.113, O3 k1 -0.107; only O2 k2 +0.052); dMaxDD from +2.8 to -8.3 pts. 14d Sharpe: +0.003 to +0.103 (O2 k2 +0.103, SE 0.049). Control (8 seeds): 8w Sharpe -0.024, Calmar -0.096; 14d Sharpe +0.060. No variant clears 2 SE over control on both grids.
- Crash 2020 / bear 2022 MaxDD, agent minus static (8w): O1 k1 -1.3/-1.2 pts; O1 k2 +3.0/0.0; O2 k1 0/0; O2 k2 +3.9/0.0; O3 k1 -6.1/+0.9; O3 k2 -1.8/+2.0. Bar (10 pts shallower) not met anywhere.
- Train/val/holdout gap (8w Sharpe agent minus static): O1 k2 +0.27 / +0.11 / -0.05; O3 k2 +0.02 / 0.00 / 0.00: gaps shrink out of sample, but only where the agent barely moves from static. Removing self-reference (O2) makes the agent nearly static (equity std 0.007 at k=1); O3 raises equity variance (std ~0.20) but not crash protection.
- Shuffle: agent minus shuffled Sharpe O1 +0.08, O2 +0.12 (one seed +0.5), O3 -0.01: does not reliably degrade; 2020 shuffle sometimes better than real.
- Permutation importance (holdout 8w): O1 dominated by own trailing portfolio return (port_ret21_z 0.062), then eq_frac, stress: self-reference persists when kept. O2: tlt_6m, vix_pct_1y, stress (~0.025 each). O3: bk_vol21_z 0.125, vix_over_spy_rv21 0.091, bk_dd21_z 0.088, bk_dd63_z 0.060, i.e. the agent does use trailing vol/drawdown when offered.
- Bug fix found: B.5 snapshots hold SPY on some dates; equity-only finalize dropped it and raised an invariant AssertionError; `apply_two_sleeve_mix` now excludes NON_TRADABLE from equity scaling (only changes snapshots that previously crashed; every sibling worktree has the old code: fold into main during consolidation). An earlier eval version without the action-dim override flattened equity exposure; those numbers were discarded; constant 50%/100% static checks match the tracker (MaxDD -32.7% / -56.3%).
- Caveats: matched static does not match turnover; single deterministic path per run; reused holdout; 8w Calmar comparisons use control SE 0 (generous); yfinance fetch attempt for BK/CTRA per run (no data/ writes observed).

Summary of round 3 (FA, FB, FH, FC, R1, C1, EGM review): features carry only trailing-vol information; clean observations and a baseline-relative action both fail the bars; an agent offered vol/drawdown features uses them but gets no crash protection beyond matched static. Remaining decision experiment: PPO on a small risk set vs a vol-target rule and B.4.

## 21. Design assessment, open decision, and track FM (2026-11-27)

Design problems identified (ranked), from sections 1-20:
1. Learning problem too small/noisy for PPO: ~58 decisions per episode, one market path, 42 dims; memorization (agent minus matched-static Sharpe: train +0.30, val +0.14, holdout -0.02); PPO settings not the bottleneck (H2). Decisions are near-independent, so a contextual bandit or supervised one-step sizing model fits better (untested).
2. Objective/signal mismatch: risk is predictable (vol IC ~0.72), returns are not (~0.02); hindsight oracle doubles Sharpe but a one-step delay removes it; return-focused rewards pay for timing that does not exist at this cadence (R1's baseline-relative reward added leverage only).
3. Action design cannot deliver crash protection: 50% floor cannot protect capital, lowering it (X2) did not help; B.4 protection is mostly low average gross (~29%).
4. Observation defects (own-NAV restarts, constant/duplicate/artifact dims): fixed in C1/FH, no edge.
5. Evaluation/data: reused holdout, survivorship (current constituents), unresolved decision-timing convention (fill at close t vs t+1), 8w training vs 14d prod cadence, seed noise ~0.05 Sharpe.
6. The no-hand-rules constraint excludes the vol-target rule (the one approach with a clear predictive basis); it would be used only as a yardstick.

How the current features were judged unusable: five independent lines (per-feature screens A0-A3 incl. block-permutation and incremental-over-TR; FA out-of-sample sleeve policy capturing 9-11% of oracle gain, -2% with delay; H1 signal gate; G1 state vs single trailing-vol feature; trained-agent controls P0/P3/C1). Caveat: IC screens have low power (min detectable incremental IC ~0.24); the agent-level and policy-level tests carry the conclusion. Untested: VIX3M/VIX9D, HYG/LQD, yield curve, event calendar.

Open owner decision: Option A (recommended) run the last decision experiment (PPO on a small risk-only observation vs a vol-target rule and B.4 as yardsticks), then fix the SPY bug (C1) in main and consolidate worktrees; Option B park RL as allocator, ship B.5+B.4, RL in shadow mode.

Track FM (owner request, launched 2026-11-27, agent a74eecb66c706c91f, analysis only, pre-registered in runs_fm/PREREG.md): (1) feature x target x horizon matrix (5/10/14/21/42/56/63 days) with block-bootstrap/HAC effective n; (2) paired out-of-sample loss comparison TR vs TR+group on identical masks/folds, block bootstrap >= 10,000, min detectable improvement via planted signal; (3) economic value after execution delay: fitted monotone forecast-to-equity map inside training folds, fill at close t vs t+1, net Calmar/Sharpe/MaxDD/turnover at 10 bps vs matched static and B.4 with bootstrap CIs, shuffled-forecast and one-step-delay controls. Status: RUNNING. X1 (floor 0.25) never delivered a final report; treated as redundant given X2.

## 22. Track S0 result: B.5 book sector/risk exposure audit (2026-11-27, agent aca95f48e99ff11bc, Phase 0 of rl_redesign_plan.md)

Worktree agent-aca95f48e99ff11bc (uncommitted); outputs `runs_s0/`; scripts `s0_{build_book,lib,exposure,relevance,audit_sector}.py`; `tests/test_s0_sector_audit.py` (10 pass). Analysis only.

Recommendation: drop all 22 raw sector dims (14-35). They are redundant with market features, harmful out of sample, and carry a default-value bug. Optionally keep a 2-dim exposure-weighted set (book-weighted sector momentum, book-weighted sector vol) as a single ablation only.

- Book: B.5 holds 20 names on every date and is sector-concentrated: unit-book mean sector HHI 0.28 (~3.5 effective sectors), XLK the top sector in 294/478 14d decisions (mean XLK 31.5%, XLY 17%, XLF 16%). Beta to SPY (63d) 1.67 at 100% equity; B.5 raw equity ~29%, effective beta ~0.49 (near the gate band). B.4 (stress cap, no trend boost) yields identical equity weights to B.5 (max diff 0.0), so B.5+B.4 is the same book. The agent controls only the equity share, so sector information matters only through the cash/equity decision.
- Relevance (leave-one-calendar-block-out ridge, paired block-bootstrap CI): book-weighted sector features E2 beat the 22 raw dims (14d T1 MSE -13.6%, CI excludes 0; 8w T1 -43%, T2 -33%, CIs exclude 0), but E2 vs SPY-only features is not significant, and SPY4+E2 vs SPY4 not significant: exposure weighting adds nothing beyond SPY/realised-vol features. Returns (T3): OOS R2 <= 0 for all sets.
- Redundancy: the 22 dims have mean R2 0.61 on the market block, max |corr| 0.97, 17 sector pairs |r| > 0.9, VIF up to 53; first 3 PCs explain 66%; ~4.7 effective dimensions.
- Incremental over TR + stress: adding the 22 raw dims HURTS (14d T1 dR2 -0.12; 8w T2 dR2 -0.59, CIs exclude 0 on the harmful side); adding E2 gives no gain. Over SPY/IWM/QQQ momentum E2 adds dR2 +0.21 / +0.41 (14d), but that base has no volatility term and E2 is mostly vol: confounded. MDE on IC: 0.09 (14d iid), 0.22 (14d block-adjusted), 0.18 / 0.31 (8w).
- Data audit of the sector parquet (src/features/sector_features.py): reproduced exactly; perturbation causality 33/33 and truncation invariance 5/5 pass; features shifted one row (row t uses data through t-1). Defects: (1) inception defaults are not neutral: XLRE valid from 2016-01-11, XLC from 2018-09-19; before then `state_builder_v2._sector_latest` returns 0.0, so momentum = -SPY 3m (a negated SPY feature, collinear with dim 2) and vol = 0; affects 280/478 14d decisions (59%) and 70/120 8w; (2) timing mismatch: sector returns through t-1 vs SPY 3m through t (mean |diff| 0.014 vs same-day sector momentum); (3) static GICS tags are current membership (look-ahead not checked). Neutralising defaults raises S22 R2 but it still does not beat TR + stress.
- Caveats: SPY sector weights are a dollar-volume proxy; unit-book returns match the H1 cache at corr 0.994 (max daily diff 5.2pp; daily-held weights, no NAV drift); targets taken from the FA dataset; ridge alpha fixed at 1; 8w n=119 low power.

## 23. Track A0 result: action and transition audit (2026-11-27, agent a7389e2fe3dfbf490, Phase 0 of rl_redesign_plan.md)

Worktree agent-a7389e2fe3dfbf490 (uncommitted); outputs `runs_a0/` (TIMING.md; cache/a0_cache.pkl 808 MB: never commit); tests `tests/test_a0_action.py`, `test_a0_timing.py`: 25 pass, 2 strict xfail (D1, zero-stock synthetic).

- Action to exposure: 2-dim raw map gives equity in [0.5, 1.0]; the floor binds on 10% of a uniform raw grid. Corners: (-1,-1) -> 1.0; (-1,+1) -> 0.5; (+1,-1) -> 1.0; (+1,+1) -> 0.667; (0,0) -> 0.714. Across 6589 real decision steps (train/val/holdout x 8w/14d x 11 policies incl. random) stock-weight sum equals the agent equity share to 1e-6, except 11 steps on 2008-01-02 on the 14d grid (D1). Trained C1 O1 agents sit on the equity floor in 12-19% of decisions and the ceiling (1.0) in 16-23%. The corrected matched-static inverse is verified (realises targets 0.5-1.0 to 1e-16). Binding numbers for C1 O2/O3, W1, H2 and R1 not produced (jobs stalled).
- Transition: with the same market path and four different action sequences, dims 0-35 are bit-identical; only dims 36 (equity share), 38 (cash share = 1 - dim 36 exactly), 39-41 (own-NAV drawdown/vol/z-return, via NAV history; max diffs 0.16 / 0.38 / 0.77) depend on the action; dim 37 is constant 0. Turnover cost and previous weights enter the reward only, not the observation. So the problem is a contextual bandit with a churn cost and NAV feedback; dims 39-41 are the only path-dependent action-driven inputs (the self-reference). Minimal well-defined agent state: dim 36 plus market dims.
- Timing (TIMING.md, 5 tests): decision at close t, weights fill at close t, first return close(t+1)/close(t); spec says t+1; the last decision's period is never simulated; training and validation cost 0 bps vs eval 10 bps.
- Cadence: decisions per episode train 8w 59 / 14d 235, holdout 48 / 191; realised daily returns per step median 39 (8w) / 10 (14d); the 63-day reward window never binds, so each reward is the full decision period (a Sharpe over 10-40 days). Env is otherwise identical for both grids.
- 3-dim legacy path: post-B.4 realised non-trend weight differs from reported equity_frac on 58% of steps (median 1.8 pp, max 58.5 pp): the reported share is not what is held in that path.
- Defects: D1 14d grid starts before the first B.5 snapshot (2008-01-07): empty book reported as full equity (fix: start at the first snapshot or report 0); D2 fill at close t vs spec t+1 (fix: add a one-day delay option in the env, amend the spec; H1 showed delay removes the hindsight signal); D3 last period never simulated (add a terminal no-trade date); D4 training/validation cost 0 bps vs eval 10 (pass cost_bps=10 in make_env_fn and val_env); D5 3-dim path reports pre-B.4 equity (report realised or drop); D6 the C1 SPY fix applies only to the 2-dim path and committed B.5 snapshots contain no SPY/TLT/GLD/UUP columns, so the C1 SPY bug is not reproduced on committed data (keep the fix with a regression test).
- Unverified: floor/cap binding for O2/O3/W1/H2/R1; 2-dim eval of C1 checkpoints under main code; same-day VIX timing.

## 24. Track R0 result: reward component report (2026-11-27, agent a223e0fd173eee9c6, Phase 0 of rl_redesign_plan.md)

Worktree agent-a223e0fd173eee9c6 (uncommitted); outputs `runs_r0/{main,c1,analysis}` (component_distributions, variance_share, contribution_by_regime_block, by_equity_bin, finite_difference_per_0.05_share, share_sensitivity_by_block, block_calmar_by_share, incentive_ranking, report_tables.md); `tests/test_r0_reward_guard.py` 6 pass + 1 strict xfail (signature-vs-env default drift); the reconstruction test passes (recomputed terms equal env reward, max error 0.0 over 14,376 main steps and 1,198 C1 steps). Also `src/rl/reward_config.py` and `train_rl_v2.py` now writes `reports/run_manifest.json` with the resolved reward config.

Effective objective, in plain words: the reward is almost entirely the annualised Sharpe of each decision step's own daily returns (8-14 days for 14d, ~39 for 8w; not a 63-day trailing window). That term is essentially share-blind, so changes in equity share barely move the reward. Drawdown, recovery, cash drag and churn together are under 2% of the total. The agent is effectively paid for noise it cannot influence much.

- Resolved lambdas: function defaults 0.08 / 0.05 / 0.02; env defaults 0.15 / 0.03 / 0.02; `train_rl_v2.py` passes 0.15 / 0.03 / 0.02 explicitly, so runtime = 0.15 / 0.03 / 0.02 for the E.7 and C1 families. Reward mode: Sharpe (committed code) for E.7; mean_var k=1 for C1.
- Components (E.7 agent, holdout 14d, per step): sharpe63 mean 1.63, std 5.04, median 1.36, p5 -6.44, p95 9.96; recovery 0.007 (std 0.006); drawdown penalty 0.006 (std 0.007); cash drag 0.005; churn 0.001. Variance share: sharpe63 0.999, others ~0 (corr with total: recovery 0.32, drawdown 0.38, cash drag/churn ~-0.02). C1 mean_var: score variance share 0.991.
- Share sensitivity: finite difference per +0.05 equity share: Sharpe term mean |delta| 0.00013; penalty and cash terms 0.001-0.002; total reward rises with share by only +0.0002 to +0.0005 per +0.05 in most blocks, with a sign flip in 2022 (-0.002). Reward-optimal constant share (holdout 14d): 1.0 in 2019, 2020, 2021, 2023-26; 0.5 in 2022. Calmar-optimal: 1.0 in 2019, 2021, 2023-26; 0.5 in 2020 and 2022. They disagree in 2020: the reward does not value avoiding the crash.
- Incentive ranking (mean per-step reward, holdout 14d): always max 1.746, constant 1.0 1.746, constant 0.5 1.733, E.7 agent 1.746 (mean equity 0.38: no better than always-invested), momentum cash-drag avoider 1.729, derisk-lagged 1.718, hindsight de-risk 1.731, chase winners 1.695, always min -0.023. Hindsight de-risking scores below always-invested because the Sharpe term rewards the step's own return, not avoided drawdown.
- Consequence: confirms the owner's reward critique (items 1 and 6 of the ranked weaknesses): recovery bonus, cash drag and drawdown penalty are negligible by magnitude, so they are not what shaped behaviour; the agent has been optimising a noisy share-blind Sharpe plus self-referential inputs. The reward gives no gradient for crash avoidance. Redesign (share-dependent, forward, decision-horizon) is justified before any PPO retest.
- Not done: per-episode contribution tables; crash-vs-recovery split; R1/P-series/E2/W1/H2/X2 families (reward modes not in committed code); one-step-deviation sensitivity (constant-share finite differences only); results rest on single deterministic paths. Follow-up requested from the R0 agent.

### 24b. R0 extras: per-episode and crash/recovery contributions

Files in `runs_r0/analysis/` (R0 worktree): episode_component_contribution.csv, crash_recovery_components.csv, constant_share_reward_in_windows{_raw,,_best}.csv, report_extra.md; script `scripts/r0_extra.py`. Built from existing rollouts.

- Per episode (E.7 agent): the Sharpe term is 100.2-100.5% of every episode total on both grids; recovery +0.2 to +0.6%, drawdown penalty -0.1 to -0.4%, cash drag -0.3 to -0.5%, churn ~-0.1%.
- Crash vs recovery (mean per-step total): 2020 Feb-Mar crash -3.68 (Sharpe -3.66, drawdown penalty -0.023); 2008-09 crash -0.40; 2022 bear -0.61; recoveries 2009 +2.69, 2020 Apr-Dec +2.36, 2023 +1.96. The drawdown penalty is 3-5x larger in crashes than in recoveries but still ~0.6% of the crash total.
- Constant share in windows: per-step reward is monotone increasing in equity share within every window, including crashes. The best constant share is 0.5 in all three crashes (2020 -3.694 at 0.5 vs -3.702 at 1.0; 2008-09 -0.405 vs -0.421; 2022 -0.614 vs -0.632), 1.0 in recoveries. The crash-window differences are ~0.01 per step, i.e. a small sign-flipped penalty effect, not a real de-risking signal: the reward never meaningfully prefers de-risking in a crash.
- One-step deviation sensitivity not run (E.7 is a 3-dim policy with the B.4 band; each deviation re-simulates the path). Windows are single deterministic paths, 8w and 14d pooled; R1, P-series, E2, W1, H2, X2 not covered.

## 25. Track FM result: horizon matrix, paired incremental value, economic value after delay (2026-11-27, agent a74eecb66c706c91f)

Worktree agent-a74eecb66c706c91f (uncommitted); outputs `runs_fm/` (PREREG.md written before results, amendments A1-A8; part1_*, part2_*, part3_*; summary part3_summary.md); tests `tests/test_fm_*.py` 11 pass; engine vs repo `PortfolioEnvV2` max NAV deviation 3.5e-16 (share 1.0), 5.4e-9 (0.72). Sealed window: all series cut at 2026-04-30; 2026-05..11 never used (the H1 pickle physically holds returns to 2026-11-24, loaded then cut).

Bottom line: nothing beats matched static robustly. No candidate group beats the trivial set TR on risk at any horizon with a CI excluding zero. Economic gains vs matched static are not significant, and shuffled-forecast controls do as well or better.

- Part 1 (horizons 5/10/14/21/42/56/63 days; GBM, LORO and expanding): the full 48-feature set collapses at long horizons (negative RMSE and pinball skill vs TR at 42-63 days). 42-dim state on the 14d grid: IC(T1) 0.33 vs TR 0.43, RMSE skill 0.08 vs 0.16 (42-dim includes own-NAV dims 39-41). Use LORO for RMSE (expanding-window ridge extrapolated badly on low-variance features, e.g. dsp_s, test z ~ -25; a clipped-test sensitivity was added post hoc).
- Part 2 (paired TR vs TR+group, identical masks, block bootstrap B=10,000; MDE from a planted AR(1) signal phi 0.9: 80% power at h14 needs MSE improvement 0.045 (kappa 0.19), at h42 0.077 (kappa 0.28)): on T1 (drawdown magnitude) groups are neutral or harmful: vol h14 -0.00015 [-0.00027, -0.00004] (helps 1/8 folds); regime h14 -0.00024, h42 -0.00136 (harm); drawdown h14 -0.00004 [-0.00015, +0.00006], h63 -0.00076 [-0.00156, +0.00001]; cross-sectional h42 +0.00007 [-0.00033, +0.00047]; breadth h14 +0.00006 [0.0000, +0.00013]; ALL48 h42 -0.00299 [-0.00424, -0.00183], h63 -0.00413 (harms). Only consistent positive: drawdown-group features on T2 (volatility): LORO h14 +0.00342 [+0.00145, +0.00545], helps 6/8 folds; h42 +0.00335 [+0.00042, +0.00684]; clipped +0.00275 [+0.00096, +0.00455]: plausible volatility information, not return timing. Pinball (tau 0.8, 0.9) mixed.
- Part 3 (economics; decision grids 14d and 8w; fill at close t (L0) vs t+1 (L1); 10 bps; fitted monotone share map, in-fold quartiles, levels {0.25, 0.5, 0.72, 1.0}; matched static; B.4 and 100% invested baselines; bootstrap CI block 21, B=10,000). 14d, 2013-2026, L0: TR CAGR 25.1%, MaxDD -38.7%, Sharpe 1.09, Calmar 0.65 vs matched static 0.59 (MaxDD -45.2%): dCalmar +0.060 [-0.40, +0.62]; 42-dim state Calmar 0.74, dCalmar +0.156 [-0.51, +0.56]; 8w TR Calmar 0.28, dCalmar -0.361 [-0.82, +0.17] (worse than static). References: B.4 (14d) CAGR 10.8%, MaxDD -20.3%, Calmar 0.53; 100% invested CAGR 35.0%, MaxDD -56.2%, Calmar 0.62. TR's protection is concentrated in COVID: 2020 MaxDD -17.5% vs static -45.1% (one episode).
- Controls: shuffled-forecast TR Calmar mean 0.83 vs model 0.65 (99.5% of shuffles at least as good as the model); 42-dim shuffled mean 0.79 vs model 0.74 (60.5%); 8w TR shuffled 0.77 vs model 0.28 (99.5%): the timing is no better than random allocation of the same shape. One-decision-lag variants give similar Calmar (TR 0.68-0.72); fill lag L1 lowers TR Calmar by about 0.04. By period (TR dCalmar vs matched static): dev 2013-16 -0.23 [-0.66, +0.13]; validation 2017-18 -0.10 [-0.95, +0.71]; holdout 2019-26 +0.09 [-0.60, +1.06]: negative in dev, positive in holdout with wide CIs, so the full-sample result is holdout-driven. part3_promising.csv is empty under PREREG.
- Limitations: B.4 convention taken from H1 outputs; 42-dim set includes own-NAV dims as supplied; the env cannot reach a 0.25 share (primary map used 0.25 via the engine; a reachable-grid variant {0.5, 0.72, 1.0} is reported); 8w map is near-extreme (most decisions at bounds); circular fixed-block bootstrap (no stationary-bootstrap check); unit_ret daily-weight convention differs from env grid-held weights (economics follow the env); clipped Part 2 sensitivity post hoc; expanding-window ridge extrapolation affects h >= 56 unclipped results.

Gate A (rl_redesign_plan.md) status: NOT MET. No simple sizer beats matched static with a CI above zero on both grids after delay and costs; shuffle control does not degrade. Per the plan, PPO retest is not justified; the remaining open item is Option A vs Option B for the owner.

## 26. Track RS1 result: reduced observation set x redesigned reward, 2x2 PPO (2026-11-27, agent a9331dd83a7c6f856)

Worktree agent-a9331dd83a7c6f856 (uncommitted); `runs_rs1/` (PREREG.md written before training, REPORT_TABLES.md, summary.json, eval/, reward_scale.json); 9 RS1 tests pass (5 reward, 4 obs); the full suite was not re-run after the aggregator parser fix.

Design: cells O1 (cleaned 36-dim C1 O1) and RS (reduced ~10-12 dims: SPY drawdown, SPY 63d vol, VIX rank, stress, continuous baseline-book vol/drawdown 21/63, vol ratio, SPY 21d vol, own equity share only) x reward OLD (mean_var k=1) and NEW (forward, share-dependent, decision-horizon: return and max drawdown relative to a constant 0.72 reference, 10 bps costs, no recovery/cash-drag/own-NAV terms); 3 seeds each (42-44), 12 runs, 10 bps training cost, selection on 2017-18 Calmar only (2019 logged), floor 0.5. All runs early-stopped at episodes 51-76; selected epochs for O1_NEW were 6-9 and for RS_OLD seeds 42/43 were 2 and 1 (near-untrained checkpoints).

Outcome: no cell passes the pre-registered bars. The redesigned reward does not produce a robust improvement, and the reduced observation set does not clearly help.

- Pooled agent minus matched static (3-seed mean, net 10 bps), holdout 8w dSharpe / dCalmar, 14d dSharpe / dCalmar, 2020 8w dSharpe: O1_OLD -0.015 / -0.055, +0.050 / +0.079, -0.237; O1_NEW -0.005 / +0.036, +0.030 / +0.072, +0.007; RS_OLD +0.001 / -0.058, +0.038 / +0.070, -0.164; RS_NEW +0.013 / -0.106 (SE 0.008), +0.086 / +0.082, -0.180. RS_NEW 8w holdout shows a Sharpe gain with a Calmar loss and deeper drawdown (agent MaxDD -45.7% vs static -37.2%).
- Bars: bar 3 (2020 crash 8w MaxDD >= 10 points shallower) fails in all four cells; O1_OLD fails bar 1 on 8w; O1_NEW passes bar 1 and 2 but fails bars 3 and 4 on 8w; RS_OLD fails bars 1 and 3; RS_NEW passes bars 1 and 4 but fails bar 3.
- 2x2 effects (holdout 8w, 95% CI): observation main effect (RS minus O1) Sharpe +0.017 [+0.002, +0.032], Calmar -0.073 [-0.130, -0.015], MaxDD -5.7 pts [-9.2, -2.2] (worse); reward main effect (NEW minus OLD) Sharpe +0.011 [-0.004, +0.026], Calmar +0.022 [-0.036, +0.080]: both include zero; interaction Calmar -0.140 [-0.255, -0.024], Sharpe +0.003.
- Memorization gap (8w Sharpe agent minus static, train / val / holdout): O1_OLD +0.149 / +0.024 / -0.015; O1_NEW +0.048 / +0.024 / -0.005; RS_OLD +0.077 / +0.021 / +0.001; RS_NEW +0.166 / +0.088 / +0.013: RS_NEW shows the largest train-to-holdout decay.
- Behaviour: O1_NEW sits at or near the 0.5 floor almost always (equity std ~0.03): effectively a fixed-floor policy, so its deltas are small by construction. RS_NEW equity responds to volatility (corr with baseline-book 21d vol -0.32 to -0.48; with SPY 63d vol -0.16 to -0.31) and de-risks to the floor in several 2020 and 2022 periods, but its 2020 8w result is still worse than static (-0.180 Sharpe). OLD cells correlate with volatility inconsistently across seeds (-0.67 to +0.50).
- Reward check: the NEW reward is negatively related to equity share on the holdout trajectory (mean r(e+0.1) - r(e) about -0.16, positive on 35% of steps), pushing policies toward the floor; OLD about +0.02. So the reward is share-sensitive now, but its sign tilts toward de-risking whenever the drawdown term dominates, which costs return in bull periods.
- Controls: shuffled observations degrade Sharpe on both grids for RS_OLD and RS_NEW, and on 14d only for O1; one-step-delayed controls show no consistent degradation. Permutation importance: RS cells dominated by baseline-book risk (0.10-0.11 mean absolute equity change), own equity near zero; O1 cells depend mainly on own-portfolio inputs (0.05-0.12).
- References (holdout 2019-26, 8w): B.5+B.4 in this harness CAGR 13.2%, Sharpe 1.039, Calmar 0.645, MaxDD -20.4% (FM's B4 reference 14.2% CAGR, Sharpe 1.106; ~1 pt CAGR gap unreconciled). FM TR sizer, 14d: CAGR 32.9%, Sharpe 1.212, Calmar 0.850, MaxDD -38.7%; FM TR 8w holdout Sharpe only 0.595, so the cadence result is grid-sensitive; the RS1 agents (Sharpe ~1.04-1.16) are not on the same footing without matching cost and cadence assumptions.
- Caveats: the 3-seed SE uses t(2), so the 2-SE bars are fragile; several effects with |t| 2-3 would not survive more seeds; reward scale taken from a random policy; very early checkpoints in some cells are selection noise; the loader fetches delisted BK/CTRA each run (harmless); a PREREG vs final-table section mismatch was noted, not resolved; nothing committed.

Reading: with the two main design defects addressed (reward made share-dependent and forward; observation reduced and de-referenced), PPO still does not beat matched static, and the cell where the agent most clearly responds to volatility (RS_NEW) pays for it with deeper drawdown and the biggest overfit gap. This closes the pre-registered "one last experiment": Gate A and Gate B are both unmet; RL as live allocator is not supported by the evidence.

## 27. BD0-BD2: contextual-bandit experiment (floor 0.25), Gate A NOT MET

Spec: `rl_bandit_plan.md`. Worktree `agent-a41c358bf0f41c224`, outputs `runs_bd/` (uncommitted; code `src/rl/bd_core.py`, `bd_learners.py`, `scripts/bd0_outcome.py`, `bd1_controls.py`, `bd2_walkforward.py`, tests `tests/test_bd_outcome_table.py`, `test_bd_walkforward.py`, 14 pass). Sealed window not used (data cut 2026-04-24). L3, L4, X1/X2, U2, 20 bps / 2d-delay robustness not run (BD3/BD4).

BD0: outcome table over arms {0.25, 0.4375, 0.625, 0.8125, 1.0}, fill t+1, 10 bps, terminal period included, 14d grid starts at first snapshot (A0 D1, D3 fixed). 8w = 120 decisions, 14d = 477. Weights sum to arm to 1e-9, no hidden floor. Env parity 1e-6 only for shares 1.0/0.625/0.8125 (0.25 and 0.4375 unreachable in the env's 2-dim map, checked against the engine only).

BD1 (controls): planted edge delta*1{VIX rank>0.5}*(0.625-a). 14d z(dU1): delta 0.0025 -> -0.89, 0.005 -> -1.14, 0.01 -> -1.60, 0.02 -> +2.75 (Sharpe z only +1.05); 8w never recovered. For delta <= 0.01 the learner is worse than static (switching noise > edge). Noise false-positive rate 0-2%. MDE (80% power): 14d Sharpe/Calmar +0.087 (347 decisions), 8w +0.18 (87 decisions). Oracles (14d): static Sharpe 0.99 / Calmar 0.62 / MaxDD -55%; hindsight best arm 3.66 / 3.90 / -24%; predictable-risk oracle (knows next-period vol only) 1.79 / 0.96 / -27% (roughly halves drawdown), while the realised TR sizer captures none of it. Note: the hindsight oracle is full-period, so it does not test H1's "gain vanishes after one-step delay".

BD2 (14 expanding folds, test years 2013-2026, pooled OOS, net 10 bps):

| Learner | Grid | CAGR | MaxDD | Sharpe | Calmar | Avg eq |
|---|---|---|---|---|---|---|
| L2 bandit | 14d | 33.7% | -56.0% | 0.97 | 0.60 | 0.97 |
| matched static | 14d | 34.0% | -54.6% | 0.99 | 0.62 | 0.97 |
| L1 TR sizer | 14d | 25.0% | -41.6% | 0.99 | 0.60 | 0.81 |
| matched static (L1 avg) | 14d | 28.8% | -47.9% | 1.01 | 0.60 | 0.81 |
| shuffled context | 14d | 33.6% | -56.0% | 0.95 | 0.60 | 0.98 |
| L2 bandit | 8w | 30.3% | -56.0% | 0.89 | 0.54 | 0.92 |
| matched static | 8w | 31.6% | -52.9% | 0.96 | 0.60 | 0.92 |

- L2 sits at 100% equity in 93% of 14d decisions and 87% of 8w decisions: effectively always invested with rare de-risking.
- H1 (L2 - matched static): 14d dSharpe -0.027 (z -0.81), dCalmar -0.021 (z -0.75); 8w dSharpe -0.073 (z -1.13), dCalmar -0.057 (z -0.84). Not met.
- H2 (vs L1): no Sharpe/Calmar gain; utility gains track average equity, not timing (equal-equity gap z -0.3 to -0.5).
- H3 (shuffled control): L2 = shuffled (14d dSharpe +0.014, z 0.40). Does not degrade.
- Fold sign (Sharpe) 8/14 (14d), 7/14 (8w), need 9. Crash bar: 2020 L2 -55.9% vs -54.5% (14d), 2022 -48.2% vs -46.8%: L2 deeper, bar (10 points shallower) fails.
- 0.5-floor sensitivity: same picture. Multiplicity: primary family 4 tests; secondary 68 comparisons with BH-FDR, 4 pass q<0.10, all utility comparisons explained by average equity.
- Legacy split holdout: 14d L2 = matched static (Sharpe 1.09 / Calmar 0.83 both); 8w L2 Sharpe 1.24 vs 1.05, CI [-0.00, +0.39], 48 decisions, not pre-registered. 3y: legacy 14d L2 = static; pooled walk-forward 8w worse than static (Sharpe 1.88 vs 2.18).

Verdict: Gate A NOT MET. Controls are under-powered for small effects (planted edge delta <= 0.01 missed), so this is "no detectable gain", not "no signal". Budget rule for continuing (controls resolve the effect and L2 not worse than L0) not met.

Deviations disclosed: 14d dates not re-anchored; terminal 2026-04-24; labels gross of cost, decoding charges 10 bps x |a-p|; minimum training size 20 decisions (changed from 40 after the first run dropped 8w 2013-2015 folds; qualitatively same); fold-sign metric defined as Sharpe difference; env check used direct share mapping and still fills at close t (A0 D2 fixed in the outcome engine only); `REPORT.md` could not be written by the subagent. `runs_bd/inputs/` holds copies of FM history files containing returns past the sealed cut (never used in statistics); delete before sharing.

## 28. Results index for experiments after section 11 (2026-11-27)

Section 11 holds the per-variant tables up to the round-2 PPO runs. Experiments run afterwards are indexed here with their verdict; full numbers are in the section named. All verdicts are against matched static (static at the agent's own average equity, same grid), net of 10 bps, holdout 2019-01-01..2026-04-24 unless stated.

| Track | Section | What was tested | Verdict |
|---|---|---|---|
| F | 12 | Reference reconciliation (B.5+B.4 14.1% vs 22-23%) | Reconciled for gate G0; a ~1 pt CAGR gap remains between harnesses (R1 13.2% vs 14.1%) |
| G1 | 13 | Is the drawdown signal real and monetizable? | Real, but equals trailing volatility; monetization fails |
| FB / FC / FH | 14, 17, 18 | Candidate feature library v4 / certification checks / v4.1 (48 features) | Library hardened, not certified as a signal library; no feature beats the trivial set TR |
| EGM | 15 | Review of feature set v4 | Certify with fixes; screens have low power (min detectable incremental IC ~0.24) |
| FA | 16 | Audit of the existing 42 dims | Dead/redundant/self-referential dims confirmed; sector dims harmful out of sample |
| R1 | 19 | Baseline-relative multiplier action | Failed bars |
| C1 | 20 | Clean risk observations | Failed bars |
| S0 | 22 | B.5 book sector/risk exposure audit | 22 sector dims redundant and buggy (XLRE/XLC defaults) |
| A0 | 23 | Action/transition audit | Defects D1-D6 found (grid start, fill timing, terminal period, 0 vs 10 bps training cost) |
| R0 | 24 | Reward component audit | Reward is ~100% a share-blind step Sharpe; other terms <2% |
| FM | 25 | Horizon matrix, paired incremental value, economics after delay | No group beats TR; sizer dCalmar +0.06 [-0.40, +0.62]; Gate A not met |
| RS1 | 26 | Reduced observation x redesigned reward, 2x2 PPO, 12 runs | No cell passes; 2020 MaxDD bar fails in all four cells; reward effect undetectable |
| BD | 27 | Contextual bandit, equity floor 0.25, 14-fold walk-forward | Gate A not met; L2 14d Sharpe 0.97 vs matched static 0.99, shuffled context equal; controls resolve only Sharpe gains >= ~0.09 (14d) / ~0.18 (8w) |

Overall conclusion (owner direction 2026-11-27 to continue RL was followed through PPO fixes, reward redesign, reduced observations and a bandit): no RL variant beats matched static; RL as the live allocator is not supported by this evidence. Plan: consolidate verified fixes into one PR and ship B.5+B.4 with RL in shadow mode.

## 30. WP5 run 1: B.5 gate baseline on current code (2026-11-28)

Command: `scripts/run_phase_b5_final_gate.py` with default arguments (config/base.yaml, universes/sp500.yaml, trend-assets default), run in worktree `agent-ad881cba32463b094/runs_wp5` (outputs only, nothing tracked changed; data symlinked read-only).

Result on current HEAD (full period 2008-2026-04-24, equity-only, 10 bps): CAGR 9.24%, Sharpe 0.781, MaxDD -23.20%. Sharpe at 25 bps 0.757, at 50 bps 0.718, all below the 0.90 gate: FAIL on the Sharpe gate. Beats-equal-weight passes (0.781 vs 0.619). Computed max gross 0.399, turnover 31.23, avg beta 0.796, 0 band violations on 120 dates.

The committed `artifacts/reports/phase_b5_final_gate.md` shows 16.04% CAGR / Sharpe 1.078 / MaxDD -32.98%, PASS, dated 2026-05-01. That report predates commit 860fa26 (the `NON_TRADABLE_ASSETS` strip at `scripts/run_phase_b5_final_gate.py:168`). The committed PASS does not reproduce on the current code.

Second finding: the committed report's "Max gross 1.500" and "turnover 84.12" rows are hardcoded constants (`B4_MAX_GROSS`, `B4_TURNOVER`, `scripts/run_phase_b5_final_gate.py:26-33`, written at `:333-354`), not computed. The computed values are 0.399 and 31.23, so the PASS rows are not evidence.

Consequence: the B.5 gate as committed says PASS, and on current code it FAILS. Do not cite the committed report as evidence until WP5 run 2 regenerates it with computed values.

## 31. Point-in-time S&P 500 membership and the B.5 picks (2026-11-28)

Data: fja05680/sp500, "S&P 500 Historical Components & Changes (Updated).csv" (MIT License, Copyright 2019-2020 Farrell J. Aultman), 2,720 snapshots 1996-01-02 to 2026-08-18. Built by `scripts/build_sp500_pit_membership.py` into `data/artifacts/sp500_pit_membership_mask.parquet` (gitignored). Tests: `tests/test_sp500_pit_membership.py` (3 pass; suite 18 pass).

Coverage: members with price history in `data/raw` (current tickers only):

| Year | Members | Priced | Coverage |
|---|---|---|---|
| 2008 | 498 | 265 | 53% |
| 2012 | 497 | 300 | 60% |
| 2016 | 506 | 343 | 68% |
| 2020 | 505 | 406 | 80% |
| 2024 | 503 | 472 | 94% |
| 2026 | 503 | 499 | 99% |

Mean coverage 2008 to 2026-04: 63%. The price cache cannot price names removed from the index before the present, so the membership mask still carries survivorship bias.

B.5 picks (top 20 by volatility score, equal weight, every control date, no cash, no costs; holdout 2019 to 2026-04, 94 periods):

| Universe | Cumulative | CAGR (approx.) |
|---|---|---|
| Unrestricted (current constituents, ADV mask) | +1,087% | about 42% |
| Restricted to point-in-time members with prices | +484% | about 27% |
| SPY, same periods | +180% | about 15% |

Reading: about a third of the unrestricted return came from the survivorship effect. The restricted picks still beat SPY by about 12 points a year, but the remaining bias from the 37% of members with no price data is unmeasured and likely still positive. A clean answer needs survivorship-free prices (for example Norgate or CRSP).

Price-data check for removed names (2026-11-28): 709 of the 1,209 tickers that were ever in the index have no price cache. Yahoo via yfinance returns nothing for most removed names (BSC, CFC, CCE, BRCM, WFM: no data). Where it returns data it can be a different company that reused the ticker (WB now Weibo, JAVA now a 2021 listing, ADCT from 2020). Using those series would corrupt the test, so no yfinance prices were added to the cache. A survivorship-free source is needed (Norgate, CRSP, EODHD or Tiingo, all paid or key-based). No data was written.

## 32. Correction: the 93 "verified" delisted price series are not delisted histories (2026-11-28)

What was run: yfinance histories for 156 candidate names; checks for date-window overlap, gaps and large moves (section 31 follow-up). 93 passed as VERIFIED and were copied to `data/raw_delisted/`. A PIT picks rerun then added them to a 503-name universe (596 total, sector 'Unknown').

What is wrong: every one of the 93 files runs to 2026-11-27 with no gap. Examples: ENPH starts 2012, SOLS 2025, OGN 2021. Most top names (ENPH, SEDG, CZR, ETSY, NOV) are still listed. These are current-ticker series, not the price history of the original index members. The verification check tested whether the window overlapped, but did not test whether the series stopped at the company's removal date. It also could not catch a reused ticker that is still trading. The VERIFIED label was therefore wrong.

Effect: the extended-universe result (+252% holdout, about 18.8% CAGR) is not a valid correction and must not be used. The earlier point-in-time result (restricted to members with price data in the original cache, about 27% CAGR, section 31) does not use these files and stands as reported.

Action: `data/raw_delisted/` renamed to `data/raw_delisted_QUARANTINED/` (gitignored). Not used by any pipeline. The worktree copy `runs_pit/raw_extended/` (about 158 MB) is scratch and should be deleted.

Still needed: a survivorship-free source with real delisting dates and final prices. The verification logic also needs to require that each series stops at the membership removal date, and that a ticker's history matches the company that was in the index (name or CIK check).

## 33. Survivorship-reduced picks test with free-source data (2026-11-28)

Data added: Tier A (5 current members, in data/raw) and Tier B (62 index exits that still trade, in data/raw_tierB, identity from SEC records, usable window per name from web-confirmed index dates; table in artifacts/reports/tierb_usable_windows.csv). 58 names rejected; about 360 truly delisted names still have no data. Only 5 of 176 price anchors came from a non-Yahoo source, so prices are not independently audited. Branch worktree-agent-af1eb684ae07face5 (not pushed): scripts/run_pit_corrected.py, convert_tierb_convention.py, build_merged_cache.py; runbook docs/runbooks/survivorship_data_ingest.md.

Method: B.5 vol_top_20, equal weight, fully invested, no costs, membership-only mask, holdout 2019-01-22..2026-04-06 (95 rebalances); training 2008-01..2018-12. Sealed window not used.

| Variant | Holdout cum | CAGR | Sharpe | MaxDD | Train cum | Train CAGR |
|---|---|---|---|---|---|---|
| A: 503 names, corrected mask | +519% | 28.8% | 0.65 | -50.5% | +423% | 16.3% |
| A_pool: same mask, Tier pool loaded | +452% | 26.8% | 0.60 | -52.2% | +386% | 15.5% |
| B: A + Tier A + Tier B in windows | +258% | 19.4% | 0.44 | -53.1% | +338% | 14.4% |
| C: B minus BWA, BBWI, JEF | +256% | 19.3% | 0.43 | -53.1% | +308% | 13.7% |
| SPY | +180% | 15.3% | 0.80 | -28.8% | +109% | 6.9% |

Coverage of members with prices: 57% (2008), 65% (2012), 75% (2016), 86% (2020), 96% (2024).

Reading: the 28% figure (A) is the most survivorship-biased; adding exits that still trade cuts the holdout to about 19% CAGR. The volatility score is a cross-sectional percentile, so adding names alone moved the holdout by -67 points (A to A_pool) with no change in membership; differences under about 30 points in training (tie dates) are not signal. Every variant trails SPY on Sharpe and has about 20 points deeper drawdown. Because truly delisted names are missing, all numbers are upper bounds. The earlier +252% run is reproduced (+251.9%); the corrected mask adds +47 points, the universe swap removes 41. Price-convention conversion of Tier B changed nothing (selection uses adj_close).

## 34. Track A: full B.5+B.4 book on the survivorship-reduced universe (2026-11-28)

Branch worktree-agent-a88e253b6b67161cf (not merged): config/universes/sp500_pit_experiment.yaml (568 names), scripts/run_trackA_book.py, tests/test_experiment_universe.py (6 pass; suite 47 passed, 1 skipped). Same gate code and parameters, no retuning, 10 bps costs, evaluation ends 2026-04-24. Independent price audit (18 names): scratchpad trackA4, summary in this section.

Control reproduction: the committed gate reproduces WP5 run 1 exactly on the FULL period 2008..2026-04-24 (CAGR 9.24%, Sharpe 0.781, MaxDD -23.2%). Correction: the 9.24% / 0.78 figures are FULL-period, not holdout. Holdout control is 14.1% / 1.11 / -20.4%.

| B.5+B.4 (CAGR / Sharpe / Calmar / MaxDD) | Control (survivors) | Experiment (reduced) | SPY |
|---|---|---|---|
| Holdout 2019-2026-04 | 14.1 / 1.11 / 0.69 / -20.4 | 9.1 / 0.74 / 0.43 / -21.0 | 17.2 / 0.88 / 0.51 / -33.7 |
| 3y | 21.9 / 2.30 / 2.67 / -8.2 | 11.6 / 1.26 / 1.23 / -9.4 | 22.4 / 1.47 / 1.19 / -18.8 |
| 2008-2018 | 6.1 / 0.54 / 0.26 / -23.2 | 5.9 / 0.49 / 0.29 / -20.6 | 7.3 / 0.36 / 0.14 / -52.3 |

Cost sensitivity, holdout CAGR/Sharpe at 10/25/50 bps: control 14.1/1.11, 13.8/1.09, 13.3/1.05; experiment 9.1/0.74, 8.8/0.71, 8.3/0.67. Dropping BWA, BBWI, JEF: 9.1 -> 9.0.
Picks only (vol top-20, 10 bps, drift-correct, holdout): control 43.7% (Sharpe 0.99, MDD -59.6%), experiment 21.8% (0.52, -63.7%).

Reading: on the survivorship-reduced universe the book does not beat SPY on return, Sharpe or Calmar over the holdout; it only has a shallower MaxDD (-21% vs -34%). It is 5.0 points CAGR and 0.37 Sharpe worse than the survivor-only control, which is an upper bound; truly delisted names (about 360) are still missing, so the true figure is likely lower. The earlier "28.8% survivor-only baseline" in section 33 used a membership mask on 501 names; the original ADV-mask production book gives 41%/43.7% on picks, so that baseline was not the production book.

B.4 checks: rolling betas and stress series identical to control on common names; no NaN betas for held names. Caveats: vol-score pool changes 503 -> 568 so percentiles shift; the mask changes from ADV-based to membership plus price-gated; Tier B sector Unknown; the loader reads the sealed 2026-05..11 rows (metrics clipped at 2026-04-24, features backward-looking, but rows are loaded); BK and CTRA not added (yfinance returned nothing; BK predecessor identity fails).

Independent audit (18 names): dividends vs SEC XBRL pass 12, fail 5 (BWA, FMC, FHN, FLS, M; 7-36% gaps); only 5 independent closes found, 4 exact; BWA PHINIA spin (2023-07-03) not adjusted, restrict BWA to end 2023-06-30; BBWI and JEF windows valid as set. Tier B prices usable for specific names only, not independently validated at scale.
