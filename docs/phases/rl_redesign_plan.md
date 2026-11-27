# RL allocator redesign plan: separate the three problems (2026-11-27)

Status: PLAN, not executed. Inputs: owner's external review (three problems mixed in one PPO policy; observation and reward critique), tracker sections 1-21, tracks FA/FB/FC/FH/R1/C1, FM (running).
Constraints kept: B.5 frozen; equity vs cash only; no hand-written caps on the agent (a vol rule is allowed only as a yardstick); holdout 2019-2026 reused (never select on it), sealed 2026-05..11 untouched; each experiment in its own worktree and `runs_*` dir.

## 1. Review of the suggestions against our evidence

Central claim: one PPO policy is asked to forecast market state, react to its own portfolio state, and optimise a multi-term reward. VERDICT: AGREE. The evidence fits: the agent's actions were driven by its own trailing return (P0/P3, C1 O1 importance), removing it left a near-static agent (C1 O2), offered vol/drawdown features it uses them (C1 O3) but gets no crash protection; and the only predictable quantity (risk) is not what a return-style reward pays for.

| Claim | Verdict | Evidence / what is still missing |
|---|---|---|
| Dims 0-13 reasonable | Mostly agree | Vol/drawdown dims (0, 1, 4, 13) carry what signal there is; 2-3, 5-12 are return momentum with IC ~0.02. |
| Sector dims 14-35 redundant (22 of 42) | AGREE, partly answered | Q1-Q3: FA A2 found no increment over TR (which contains VIX and SPY vol) and none over SPY features; dims 23/24/34/35 are ETF-inception artifacts; sector parquet construction unverified. Low power caveat applies. Q4 (does the B.5 book actually carry these sector exposures) is NOT tested: needs a book sector-weight audit. |
| Dims 36-38 agent state | Agree | Equity-only: trend share (37) is constant, cash share (38) = 1 - equity share (deterministic): both redundant. Only equity share (36) is a legitimate control state. The environment is exogenous: market path does not respond to the action; the only action-dependent state is equity share and NAV, so the problem is essentially a contextual bandit with a churn cost. |
| Dims 39-41 feedback loop (highest priority) | AGREE, confirmed | FA restart test: dims 39-41 change with episode start; P0/P3 and C1 O1 permutation importance: own trailing return dominates; procyclical chasing is the observed mechanism. C1 O2/O3 removed them. |
| Reward P1: rolling Sharpe noisy/overlapping | AGREE with a correction | Correction to my earlier wording: `compute_reward_v2` takes `daily_returns` of the step just taken (after the action), window = min(63, n) days, i.e. a Sharpe of the ~40 (8w) or ~10 (14d) realised daily returns of the decision period, not a trailing window. It is forward but very noisy, and Sharpe is scale-invariant: with cash earning ~0 it is nearly share-blind, so it gives no gradient on the one thing the agent controls. |
| P2 recovery bonus rewards re-risking | Agree in principle | Magnitude is 0.10 x recovery (~0.005): probably negligible next to Sharpe; verify with the component report. R1's reward (excess mean-variance + 0.15 x MDD) already dropped it. |
| P3 cash drag adds momentum-timing preference | Agree in principle | 0.03 x cash share (<= 0.015) is small vs Sharpe; verify. R1's reward dropped it; R1 and the mean_var/dsr/semivar/cvar variants never showed de-risking. |
| P4 drawdown penalty is backward-looking | AGREE | Expanding-peak drawdown of own NAV: history-dependent and self-referential. R1 replaced it with a forward-window MDD. |
| P5 scales/weights uncalibrated; runtime lambdas | AGREE, not done | Lambda mismatch is real (runtime 0.15/0.03, function defaults 0.08/0.05; documented in `train_rl_v2.py`). No reward-component report exists. This is cheap and should be first. |
| Sequence: observation audit, reward ablation, action/state audit, simple benchmarks, then PPO | AGREE with changes | Observation ladder is mostly done (C1) and the forward baseline-relative reward was done in R1, but never CROSSED: per the reports C1 used old reward modes and R1 used the existing observation. The cross (clean obs x forward share-dependent reward) is the real gap. Simple benchmarks (step 4) should come BEFORE any new PPO run, and FM already runs them. |

What is not supported: replacing all features or the whole reward "immediately" (agree with the reviewer: isolate causes first); PPO retest before a monetizable signal is shown.

## 2. Holistic diagnosis

1. Information: past evidence says the observation carries trailing-vol/drawdown information and no return-timing signal (power caveat: IC screens cannot see deltas below ~0.24; agent- and policy-level tests carry the conclusion).
2. Objective: the reward does not pay for the predictable quantity in a share-dependent way (Sharpe is share-blind; penalties are on own history). A policy cannot learn risk sizing from a signal that is not in its reward gradient.
3. Estimator: PPO on ~58 decisions per episode, near-independent steps, one path; memorisation (+0.30 train vs -0.02 holdout). Bandit or supervised sizing fits the structure better.
4. Action: floor/cap and the 14.1% vs 23.1% gross-exposure gap mean "protection" in B.4 is mostly low average gross, not timing.
5. Evidence quality: reused holdout, survivorship, unresolved fill-at-close-t vs t+1, 8w train vs 14d prod, seed noise ~0.05 Sharpe.

## 3. Plan (gated; each step names its pass/fail)

Phase 0: audits, no training (parallel, ~1 day)
- R0 Reward component report: roll out saved checkpoints (E.7-style, C1, R1) over train/val/holdout; for each reward term give distribution, mean, std, covariance and share of reward variance; derive lambdas from the runtime env config, not the function signature; test whether the agent could change reward by changing share (correlation of reward with equity share). PASS = we know the effective objective; expectation: Sharpe dominates and is share-blind.
- A0 Action/transition audit: assert each raw action maps to the intended equity share (including the corrected static inverse for 0.5-2/3); list exactly what the next state depends on (equity share, NAV; market is exogenous); confirm dims 37/38 redundancy; merge the C1 SPY-in-snapshot fix into a clean test.
- S0 Sector exposure audit (Q4): B.5 book sector weights per decision vs sectors in dims 14-35; if exposures are minor or sector features duplicate SPY/VIX after FM, prune.
- FM (running): horizon matrix, paired incremental value vs TR, economic value after execution delay; feeds Phase 1.

Phase 1: decompose and benchmark (before any new PPO)
- B1 Forecaster: supervised risk models (TR, TR+groups) on next-period drawdown/vol at the right horizon (FM output).
- B2 Sizer: fitted monotone forecast-to-share map inside training folds; benchmarks: static (matched), trailing-vol sizing, B.4, B.5+B.4. Metrics after fill-at-close and 1-day delay, 10 bps, paired block-bootstrap CIs, shuffle and delay controls, crash and bear folds (FM part 3).
- B3 One-step bandit/supervised policy with reward = forward utility difference of the chosen share vs static (FH signed regret T5 over shares {0, .25, .5, .72, 1}); reduced observation (market-only M, then M + equity share E, then M + continuous baseline-book risk P from the BASELINE book, never own NAV).
- GATE G-A: proceed to PPO only if some B2/B3 model beats matched static with a bootstrap CI above zero on both grids after delay and costs, not worse on the 3y window, shuffle degrades, and a crash-fold MaxDD gain of at least the pre-registered bar (default 10 points). If not: stop; Option B (ship B.5+B.4, RL in shadow with logging).

Phase 2: PPO retest (only after G-A)
- Observation ladder M, M+E, M+P (reduced dims; drop 14-35 unless S0/FM justify, drop 37/38, drop 39-41) crossed with a reward ladder: R-A existing (runtime lambdas), R-B without recovery and cash drag, R-C forward share-dependent baseline-relative (R1 form), R-D forward risk-adjusted regret over shares. 3 seeds, shared harness, matched-static yardstick, permutation importance on trained agents.
- GATE G-B: agent beats the Phase 1 sizer or matched static by > 2 SE with crash protection; else keep the simple sizer or Option B.

Phase 3: consolidation and sealed test
- Merge code to the branch (feature library v4.1 behind a build_state_v4, C1 SPY fix, tests), one coherent PR; resolve the decision-timing convention and write the spec amendment; rebuild masks past 2026-04-24; one-shot sealed test 2026-05..11 for the single frozen candidate.

## 4. Decisions needed from the owner
1. Approve Phase 0 now (cheap, no training), with Phase 1 following FM.
2. Is a fitted, learned sizing map (bandit/supervised) acceptable as "RL"? Default assumed: yes (learned from data, not a hand rule).
3. Crash-fold bar (default 10 points), PPO vs bandit for Phase 2 (default: bandit first).

## 5. Owner's ranked weaknesses mapped to the plan (added 2026-11-27)

| Rank | Weakness | Evidence status | Where addressed |
|---|---|---|---|
| 1 High | Reward mixes return timing, risk reduction, recovery, cash drag | Confirmed in structure; term magnitudes unmeasured (recovery <= ~0.005, cash drag <= 0.015 vs Sharpe O(1) suggests Sharpe dominates but it is share-blind) | R0 component report; B3 single-purpose reward (forward utility difference over shares); Phase 2 reward ladder R-A..R-D |
| 2 High | Portfolio-derived observations: feedback loop and episode-boundary artifacts | Confirmed (FA restart test; P0/P3; C1 importance) | Drop 39-41; use baseline-book P features only (C1 O3 form); observation ladder M, M+E, M+P |
| 3 Medium | 22 sector dims add complexity without information | FA: no increment over TR/SPY; low-power caveat; Q4 untested | S0 exposure audit; prune unless FM shows value |
| 4 Medium | Correlated market/stress features hamper attribution | Known: d31 with d04 (VIF 62/153), 13 pairs |corr| > 0.95 and 16 features with VIF > 10 in v4 (FH S1 waiver) | Cluster representatives in B1; permutation importance by cluster, not by feature, in Phase 2 |
| 5 Medium | Decision cadence and overlapping reward horizons vs production | 8w training vs 14d prod; step reward windows differ by grid; 63-day window clipped to the step | FM horizon matrix picks the actionable horizon; train and evaluate the chosen cadence in prod terms; B3 reward horizon equals the decision horizon, non-overlapping |
| 6 Medium | Reward defaults differ from documented defaults | Confirmed (runtime 0.15/0.03 vs function 0.08/0.05) | R0: log the resolved runtime config into every run's manifest; test that the signature default equals the env default or is passed explicitly |
