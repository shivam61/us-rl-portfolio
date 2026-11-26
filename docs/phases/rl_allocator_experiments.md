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
