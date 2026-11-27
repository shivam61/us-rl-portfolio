# Contextual-bandit experiment plan (BD): can a learned one-step policy size equity better than matched static?

Status: PLAN (2026-11-27), not executed. Companion to `rl_allocator_experiments.md` (tracker) and `rl_redesign_plan.md` (Phase 1 B3).
Scope: equity-vs-cash share of the frozen B.5 book. Individual equities only, remainder cash; TLT/GLD/UUP/SPY read-only signals. No hand rules (no vol-target rule, no caps beyond the existing 50% floor).

## 0. Why a bandit, and what it can and cannot prove

- Evidence so far: return timing IC ~0.02; only next-period drawdown/vol is predictable and trailing vol carries it (FA, FB, FH, FM); PPO variants (R1, C1, W1, H2, RS1) never beat matched static; train-to-holdout gap +0.30 / +0.14 / -0.02 Sharpe.
- The decision is one-step: the next market state does not depend on the action, except through the churn cost and the agent's own previous share. A bandit removes PPO's long-horizon credit assignment, which only adds variance here.
- Full information: the book's daily unit returns are known, so the outcome of EVERY arm can be computed for every decision. There is no exploration problem; this is cost-sensitive supervised learning of the best arm given context, scored out of sample as a policy.
- What it can prove: whether ANY learned map from a small risk context to equity share beats matched static and the simple trailing-vol sizer (TR sizer, FM) after delay and costs. What it cannot prove: absence of signal in features we do not test.
- Expected outcome stated up front (pre-registration): the bandit matches the TR sizer and does not beat it beyond noise. A pass requires a CI above zero, not a point estimate.

## 1. Hypotheses (pre-registered)

- H1 (primary): learner L2 (linear contextual bandit) on observation X0 with utility U1, pooled over walk-forward test folds, beats matched static in net Calmar OR Sharpe by more than 2 SE on both the 14d and 8w grids.
- H2: it also beats the TR sizer (FM) with CI above zero; if not, the conclusion is "use the simple sizer, RL adds nothing".
- H3: the shuffled-context control and the random-arm control do materially worse than H1's learner (otherwise the gain is not state-dependent).
- Multiplicity: H1 is the single primary test. Everything else (other learners, observation sets, utilities) is secondary and reported with BH-FDR.

## 2. Decision problem definition

- Decision dates: B.5 control dates (8w grid, comparable to history) and the 14d grid (prod). Both are evaluated; train on the grid being evaluated (fixes the A0 train/eval grid mismatch).
- Timing: decision at close t, fill at close t+1 (one-day delay, the A0 correction), outcome = net return from t+1 close to the next decision's t'+1 close. 10 bps per unit turnover on every trade, in training and evaluation.
- Arms (owner decision 2026-11-27: minimum equity share 0.25): realised equity share a in {0.25, 0.4375, 0.625, 0.8125, 1.00} (even 0.1875 steps), applied via `finalize_equity_only` (stock weights sum == a, rest cash). The 50% floor of `apply_two_sleeve_mix` is not used; the bandit sets the share directly. Sensitivities: floor 0.5 arms {0.50, 0.625, 0.75, 0.875, 1.00} (the previous design), 3 arms {0.25, 0.625, 1.0}, 9 arms. Check in BD0 that `finalize_equity_only` and the outcome table enforce no hidden floor and that the weights sum equals the arm exactly.
- Matched static is recomputed per arm set at the learner's own average equity, so a lower floor cannot inflate the comparison. Prior PPO runs with lower floors (X1 floor 0.25, X2 floor 0.0) showed no crash protection and are the reference; the oracle with a wider floor (H1) is large only with hindsight and vanishes after a one-step delay. Expect larger swings, higher turnover and cost drag at 0.25, so the cost-aware decoding and the 20 bps sensitivity matter more.
- Outcome table: for every decision d and arm a, store R(d,a) net of costs given the previous share p, MaxDD(d,a), vol(d,a). Built once from the unit-book daily returns; reused by all learners (reproduces the env to 1e-6 on a sample, test below).
- Utilities (pre-registered):
  - U1 (primary): log(1 + R(d,a)) (growth; penalises variance through concavity).
  - U2 (secondary): R(d,a) - 0.5 * MaxDD(d,a) (explicit drawdown penalty).
  - Both are forward and share-dependent (the RS1 lesson); neither contains a trailing term.
- Churn: not included in the labels. Evaluation charges real costs. Cost-aware decoding (still learned): choose argmax_a [predicted U(a) - cost(|a - p|)], where p is the previous share. This is not a hand rule: it is the expected-utility argmax with an explicit cost.

## 3. Observation sets (small by design, no own-NAV)

- X0 (6 dims, primary): trailing vol of the unit book 21d and 63d; baseline book drawdown (continuous, not episode-local); SPY drawdown; VIX 252d rank; B.5 stress score. This is the TR set.
- X1 (<= 12): X0 + FH drawdown-state features (days since peak, recovery fraction, last-leg speed, vol-of-vol).
- X2 (<= 12): X0 + cross-asset 63d (TLT, GLD, UUP) + IWM-SPY.
- All causal (expanding z-score, warm-up documented), via `build_state_v4`/`features_risk_v4` where available; else the reduced RS1 builder. Previous share is not a context (cost handled in decoding).
- Dropped on evidence: the 22 sector dims, own-NAV dims 39-41, constant dims 37-38.

## 4. Learner ladder

| ID | Learner | Notes |
|---|---|---|
| L0 | Matched static (and best constant arm) | baseline; static at the agent's average equity on the same grid |
| L1 | TR sizer (from FM, ridge forecast of risk -> share) | main competitor |
| L2 | Linear contextual bandit: per-arm ridge on U(d,a), cost-aware argmax | PRIMARY learner |
| L3 | Shallow gradient-boosted trees per arm (depth <= 3, strong shrinkage) | nonlinearity check |
| L4 | One-step softmax policy gradient, tiny MLP (16 units), entropy bonus | the "RL" version of a bandit; reference to L2 |
| C1 | Shuffled-context control (block-shuffle X within fold) | must degrade |
| C2 | Random-arm control | calibrates luck |
| C3 | Planted-signal and planted-noise controls (section 6) | pipeline calibration |

PPO is not rerun; RS1 is its reference.

## 5. Evaluation protocol

- Primary: expanding walk-forward. Train on 2008..Y, test Y+1, for Y = 2012..2025 (14 folds, min ~4 years of training), 2-decision purge/embargo at fold boundaries. Hyper-parameters (ridge alpha, tree depth, entropy) chosen by INNER walk-forward on the training portion only, grids pre-registered and small. Pooled out-of-sample series from all folds is the headline.
- Comparability: also run the legacy split (train 2008-2016, validation 2017-2018, holdout 2019-2026-04-24, 3y 2023-04-25..2026-04-24) and report in the same table format as the tracker.
- Sealed window 2026-05..11: not touched until the decision at the end; one shot only if Gate A passes.
- Metrics (net of 10 bps, repo conventions: Sharpe = CAGR/vol, Sortino = CAGR/downside vol): CAGR, Sharpe, Calmar, MaxDD, turnover, average equity, equity std (> 0.05), per-fold sign consistency.
- Inference: paired stationary block bootstrap (block 8-12 decisions) on period utility differences and on Sharpe/Calmar differences vs L0 and vs L1; report point, 95% CI, 2 SE.
- Crash fold: 2020 MaxDD at least 10 points shallower than matched static (default bar, can be overruled); also 2022.

## 6. Controls and power (run BEFORE any real result)

- C3a planted signal: add a synthetic regime-dependent edge of known size to U(d,a) in a fixed fraction of decisions; verify the pipeline recovers it at the stated n and report the minimum detectable Sharpe/Calmar gain for the bandit with ~330 pooled test decisions (14d) and ~60 (8w).
- C3b planted noise: replace contexts with Gaussian noise; the false-positive rate of Gate A must be <= 5%.
- Oracle bounds: (i) hindsight best arm with a one-step delay (H1 found ~0 gain after delay: confirm on this arm set); (ii) "predictable-risk oracle" that sees next-period realised vol but not returns, as an upper bound on what a risk signal can deliver.
- If the MDE exceeds the plausible effect size, the report must state the experiment cannot resolve small gains, as in FM.

## 7. Gates and decision table

Gate A (all required): H1 met on both grids; not worse than matched static on the 3y window; crash-fold bar; shuffled-context control degrades; equity std > 0.05; no fold-sign pathology (>= 9 of 14 folds non-negative on the primary metric); H1 survives the cost 20 bps and delay 2d sensitivities.

| Outcome | Reading | Action |
|---|---|---|
| Gate A met and beats L1 | learned state-dependent sizing adds value | sealed window one-shot, then shadow mode of the bandit policy |
| Gate A met but equals L1 | the signal is trailing vol | ship the simple sizer logic as the policy, RL not needed |
| Gate A not met, controls fine | no exploitable state signal at this horizon | park RL, ship B.5+B.4 with shadow logging |
| Controls fail (planted signal missed) | experiment under-powered | state so; do not conclude absence |

## 8. Stages (each in its own worktree and `runs_bd*` dir)

| Stage | What | Hours | Depends on | Parallel |
|---|---|---|---|---|
| BD0 | Outcome table R/MaxDD/vol for every (date, arm) with delay and costs; checks vs env; fix 14d grid start (A0 D1), terminal period (D3); tests | 5-6 | none | alone |
| BD1 | Controls and power: planted signal/noise, oracle bounds, MDE | 3-4 | BD0 | with BD2 setup |
| BD2 | Walk-forward harness + L0, L1 (reuse FM sizer), L2 on X0, bootstrap inference | 6 | BD0 | after BD1 spec |
| BD3 | L3, L4, C1, C2 on X0; observation ladder X1, X2 | 5-6 | BD2 | L3/L4 and X1/X2 in parallel |
| BD4 | Robustness: U2, 3/9 arms, 20 bps, 2d delay, legacy split table | 4 | BD2 | parallel with BD3 |
| BD5 | Decision report, tracker section, PR update; sealed-window one-shot only if Gate A passes | 2-3 | BD3, BD4 | alone |

Total about 25-30 hours of agent time; BD0-BD2 (the part that decides whether to continue) about 14 hours.

## 9. Tests

- `test_outcome_table_matches_env`: arm returns equal the env's net returns for sampled dates to 1e-6, including costs.
- `test_no_lookahead_in_context` (truncation and future corruption on X0) and `test_fill_delay_one_day`.
- `test_walk_forward_purge`: no train decision within 2 decisions of a test fold; no future information in the inner CV.
- `test_arm_weights_sum_to_share`: `finalize_equity_only` assertion for every arm.
- `test_shuffled_context_destroys_signal` and `test_planted_signal_recovered`.
- `test_bootstrap_coverage` on synthetic data with known difference.

## 10. Risks and caveats

- The reused 2019-2026 period is also test data under walk-forward; walk-forward removes the tuning-on-holdout problem but not the reuse of one historical path. The sealed window is the only truly clean test and covers ~6 months.
- Survivorship in unit-book returns before 2015 is unmeasurable (FH); pooled results should also be shown for 2015+.
- Baseline reference mismatch (R1 13.2% vs 14.1% CAGR) is unreconciled; all comparisons here are within one harness.
- Seed noise only applies to L4; L2/L3 are deterministic given data.
- Trailing-vol collinearity: the learner may reproduce L1 exactly; that is an informative result, not a failure.
- A pass is a statement about this book and period; it does not justify extending to sector tilts or more actions.

## 11. Owner decisions (defaults in brackets)

- Minimum equity share [0.25, decided by owner; 0.5 kept as a sensitivity]. Crash-fold bar may need a re-look at 0.25 (more room to de-risk).
- Does a fitted contextual bandit count as RL? [yes]
- Crash-fold bar [10 MaxDD points]; primary utility [U1 log growth].
- Walk-forward folds 2012-2025 [yes] vs the legacy single split only.
- Budget: continue past BD2 only if the controls resolve the effect size and L2 is not worse than L0.
