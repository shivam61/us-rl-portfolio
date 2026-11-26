# RL feature plan: find the features that do not help, build a set that does

Status: PLAN (2026-11-27). Not yet executed. Companion to `docs/phases/rl_allocator_experiments.md` (tracker, section 6 cause 6 and 8).
Scope: observation design for the RL allocator (equity-vs-cash of the frozen B.5 book). No hand rules on the agent. B.5 picks untouched.

## 0. What we already know (evidence, not assumptions)

- Current state: 42 dims (`state_builder_v2.py`): SPY drawdown/trailing returns/realized vol, IWM-vs-SPY, TLT/GLD/UUP momentum, sector momentum and vol, B.5 stress score, VIX, own-portfolio features, current equity/cash share.
- Verified defects: constant dims (`trend_frac`, `sec_vol_XLC`; dims 36-38 in equity-only), redundant dims (eq_frac vs cash_frac r=-1; XLRE/XLC momentum = -SPY momentum), own-portfolio features computed on a NAV that restarts at 1.0 per episode (differ across train/val/holdout/prod).
- Signal evidence (H1, 477 biweekly decisions, 9 regime blocks): return timing not predictable (IC 0.02); next-period DRAWDOWN size predictable (IC 0.38, p 0.005, not yet block-permutation-validated, see G1); strongest single feature SPY drawdown (mean reversion, 9/9 blocks, |IC| ~0.09); every other univariate |IC| <= ~0.12 = noise for 42 tests.
- Behaviour evidence (P0, P3): the agent's actions are driven mainly by its own trailing portfolio return, then stress/VIX: a self-referential input, not a market signal.
- Breadth (v3ab, 50 dims) added no signal. More inputs with ~58 decisions per episode adds memorization room: every variant that added inputs failed acceptance.
- Consequence: the aim is a SMALL set of causal, regime-stable, risk-focused features that survive a pre-registered selection protocol, not a bigger set.

## 1. Targets (what a feature must help predict)

Features are judged against the quantities the allocator can actually monetize, at the decision grids (8w control dates and 14d):
- T1: next-period max drawdown of the unit B.5 book (primary: shown predictable).
- T2: next-period realized volatility of the unit book.
- T3: next-period book return excess over the B.5+B.4 baseline (sanity: expected to be ~0; any signal is a bonus).
- T4: sign of next-period book return (AUC).
Primary acceptance is on T1/T2; T3/T4 are reported, not required.

## 2. Part A: identify features that do not help (pruning protocol)

Run all of this at the 14d grid (477 decisions) and confirm on 8w; shared harness is H1's code (`runs_h1/scripts`, worktree agent-a31db186a7b693ee9).

Stage A0, hygiene (free, deterministic)
- Drop constants and near-constants (variance < 1e-8 over train) and exact duplicates; report |corr| > 0.95 clusters and keep one representative per cluster (prefer the one with the cleaner economic definition); compute VIF and drop > 10 unless it is the only carrier of a regime signal.
- Look-ahead audit: for every feature, truncate the price history at each decision date and assert identical values (unit test); check availability lag of VIX/rates data (use t-1 if released after the close).
- Consistency audit: compute every feature from a continuous history; assert a training episode started mid-history gets the same observation as the continuous run (kills the NAV-reset defect). Remove all own-NAV features (own trailing return, own drawdown); replace by features of the BASELINE book's continuous return series (not the agent's).

Stage A1, univariate usefulness (regime-aware)
- For each feature x target (T1-T4): rank IC (Spearman) by regime block (GFC 2008-09, 2010-12, 2013-17, 2018Q4, 2019, 2020 crash+recovery, 2021, 2022 bear, 2023-26).
- Keep only features whose IC has the SAME SIGN in >= 7 of 9 blocks and whose pooled IC passes a BLOCK permutation test (circular block shifts / stationary bootstrap, block length 8-12 decisions) at FDR q < 0.10 across all tests (Benjamini-Hochberg). The old joint-shuffle p-values are not acceptable.

Stage A2, incremental value over trivial predictors (the key filter)
- Trivial set TR = {trailing 21d/63d realized vol of the unit book, trailing 21d/63d realized vol of SPY, VIX level, B.5 stress score, previous decision's realized drawdown}.
- For each candidate, measure incremental out-of-sample gain over TR (leave-one-regime-out ridge: delta rank-IC / delta AUC / delta pinball loss for T1, T2) with a block-permutation null of the delta. A feature that does not beat TR is "not helping" even if its univariate IC looks fine (it is re-expressing volatility persistence).

Stage A3, group ablation (supervised proxy, cheap: minutes)
- Feature groups: G-vol (realized vol multi-horizon, vol-of-vol, semivariance), G-dd (drawdown depth/duration/recovery of SPY and of the baseline book), G-mom (trailing returns), G-xasset (TLT/GLD/UUP momentum), G-sector (sector momentum/vol), G-macro (VIX level/term, stress score), G-breadth, G-own (own-portfolio).
- Leave-one-group-out and add-one-group-to-TR, leave-one-regime-out folds; report delta metric per group with block-permutation CI. A group is "not helping" if removing it changes no fold metric beyond noise (< 1 SE) and adding it to TR does not help.

Stage A4, in-agent confirmation (only on a trained agent; expensive, last)
- Permutation importance on actions of trained C1/R1 agents: shuffle each feature (and group) across time within the holdout; measure the change in the agent's equity/gross path and in its out-of-sample Calmar; report which inputs the policy actually uses. Cross-check against A1-A3: features the policy uses but A1-A3 call useless = overfit channels (candidates to remove); features A1-A3 call useful but the policy ignores = candidates for rescaling or a different reward.
- Retraining ablation: from the best variant, retrain 3 seeds with the dropped groups removed (leave-group-out) and compare pooled agent-minus-matched-static; only keep a group if its removal hurts by more than 1 SE.

Decision rule for pruning: a feature is removed if it fails A0, or (fails A1 AND fails A2), or its group's A3 and A4 deltas are both within noise. Features are never added or removed based on holdout 2019-2026 performance of the RL agent; A1-A3 use leave-one-regime-out folds, and the sealed 2026-05..11 window stays untouched.

## 3. Part B: build the candidate set that can help

Principle: the evidence says RISK is predictable and RETURN is not. Build features that describe the risk regime, are causal, persistent enough to act on at 8w/14d cadence, and are stable across the 9 regime blocks. Every candidate is tested through Part A before it enters the agent.

Candidate groups (add only what the data pipeline supplies; confirm availability before coding, mark missing ones as data requests):

1. Volatility term structure and dynamics (primary): realized vol of the unit book and SPY at 5/21/63d; ratio short/long (vol acceleration); vol-of-vol; downside semivariance and ratio down/up; Parkinson/Garman-Klass range vol if OHLC available; VIX level, VIX change, VIX vs realized vol spread (variance risk premium proxy); VIX term slope (VIX vs VIX3M/VIX9D if in the data store).
2. Drawdown state (the one consistent mean-reversion feature): SPY and unit-book drawdown depth, days since peak, speed of the latest leg (return over the last 5/10/21d), recovery fraction from the trough; computed on a continuous history.
3. Cross-sectional risk structure of the traded book (this is where the high-beta B.5 book differs from SPY): average pairwise correlation of the held stocks (21/63d), dispersion of stock returns, share of the book in the worst-drawdown decile, book beta to SPY (rolling), book concentration (HHI of B.5 weights); these describe the risk the equity sleeve actually carries.
4. Breadth and participation: % of universe above 50/200d, net new highs/lows, advance/decline proxy, equal-weight vs cap-weight spread (IWM-SPY already in), momentum of breadth; v3ab already tried raw breadth: re-test only as risk-conditioning features.
5. Cross-asset stress (already partially present): TLT/GLD/UUP momentum and their volatility, stock-bond correlation (21/63d), credit proxy if available (HYG/LQD ratio), yield-curve slope if available (do not buy anything: read-only signals).
6. Calendar/event regime (low-cost, causal): month-end/quarter-end, FOMC/CPI proximity if a calendar is available; test as sparse flags; expect weak.
7. Baseline-book state (replaces own-NAV features): continuous return/vol/drawdown of the B.5+B.4 baseline NAV, current baseline gross/beta/stress-scale (a=0 reference), distance of the agent's current exposure from the baseline (for the multiplier action in R1).

Representation rules (to make the few useful features learnable at n~58 per episode):
- Standardize with expanding-window z-scores computed causally (no whole-sample mean/std); winsorize at +-3; use rank/percentile transforms for heavy-tailed vol features.
- Keep the total at <= ~15-20 dims after pruning; one feature per redundancy cluster; no raw-price levels.
- Provide the same observation function to env, training, backtest and prod (single source; add a prod-parity test on one rebalance date).

## 4. Execution plan (phases, parallel where possible, each in its own worktree)

| Phase | What | Hours | Depends on | Pass/fail |
|---|---|---|---|---|
| FP0 | Hygiene A0 + consistency audit; inventory data actually available (VIX term, credit, OHLC, calendar) | 3-4 | none | dead/duplicate dims removed; look-ahead and continuity tests green; data-availability table |
| FP1 | Build candidate feature library for groups 1-7 (causal, single function, unit tests) | 8-10 | FP0 | library + tests; every feature has a documented definition and lag |
| FP2 | Stages A1-A3 on all existing + candidate features (block permutation, FDR, incremental over TR, group ablation) | 6-8 | FP1; reuse G1 harness | ranked table with keep/drop verdicts per feature and group |
| FP3 | Freeze feature set v4 (<= 20 dims) with a written rationale and a pre-registered list of dropped features | 1-2 | FP2 | frozen spec committed before any new RL training |
| FP4 | Train the RL agent(s) on v4 (reuse R1/C1 setups; 3 seeds x variants) and run A4 (in-agent permutation importance, retraining ablation) | 10-14 | FP3, R1/C1 harness | pass bars from tracker section 7 (pooled > 2 SE over control, crash-fold MaxDD >= 10 points shallower, shuffle degrades) |
| FP5 | Sealed test of the frozen v4 agent on 2026-05..11 (masks rebuilt), one shot | 6-8 | FP4 | can only falsify; report, do not tune |

Minimum path to a feature verdict (FP0-FP3): about 18-24 hours; with FP4: about 30-40 hours. FP0 and FP1 can start now in parallel with R1/C1 (they only read data); FP2 reuses G1's block-permutation machinery, so start it after G1 reports.

## 5. Rules to keep the process honest

- Pre-register: the target list, folds, block-permutation settings and the keep/drop thresholds above are fixed before looking at FP2 results.
- Multiple testing: report the number of features tested; use BH-FDR; treat any feature that clears only a joint (non-block) permutation as unproven.
- No selection on the reused holdout: feature decisions use leave-one-regime-out folds on 2008-2026 per A1-A3; RL training/validation windows follow the walk-forward rules (2019 as second validation block; 2020 untouched until final test); the sealed window is one-shot.
- Small-sample caution: 9 regime blocks, 6-26 decisions in the crisis folds, effective n for drawdown targets is smaller because drawdown is autocorrelated (use block methods).
- Expected outcome (stated up front): most candidates will fail A2 because they re-express trailing volatility; success looks like 3-8 features that add incremental, regime-stable information on T1/T2. If nothing beats TR, the correct conclusion is that the agent's best input set IS the trivial volatility/drawdown set, and the RL value rests on the reward/action design (R1), not on features.

## 6. Open items needing owner input

- Data requests if missing: VIX term structure (VIX3M/VIX9D), credit ETFs (HYG/LQD), yield-curve series, OHLC for range vol, event calendar.
- Whether FP4 uses PPO or a contextual bandit (plan review recommends bandit for sizing; untested).
- Dimension budget (default <= 20).
