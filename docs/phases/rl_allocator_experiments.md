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
