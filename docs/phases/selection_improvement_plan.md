# Plan: improve stock selection (B.5 successor experiment)

Status: PLAN (2026-11-28), not executed. B.5 stays frozen in production until a candidate passes the gates below. Evidence base: tracker sections 33 and 34.

## 1. Why

- Current score = mean percentile rank of 63-day volatility, downside volatility, beta, and max drawdown; top 20, equal weight. It selects the riskiest stocks and has no return, quality or valuation input.
- On the survivorship-reduced universe the picks earn 21.8% (holdout, 10 bps) with Sharpe 0.52 and MaxDD -64%; the full B.5+B.4 book earns 9.1% / 0.74 vs SPY 17.2% / 0.88.
- The score is a percentile over whatever names are loaded, so adding names alone moved the holdout by 67 points (section 33). This is a design flaw to fix first.

## 2. Objective (Gate 0, owner to confirm; default below)

Default: beat SPY on Sharpe AND Calmar net of 10 bps, with MaxDD at least 10 points shallower, on the survivorship-reduced universe. Alternative: maximise return subject to a drawdown cap. The choice decides which candidates are worth testing.

## 3. Rules to avoid repeating past mistakes

- Evaluate on the experiment universe (568 names, corrected PIT mask), 10 bps costs, with 25 and 50 bps sensitivities. Every result stated as an upper bound until delisted names are added.
- Candidates are pre-registered below (at most 6). No candidate is added after seeing results. Multiplicity: BH-FDR across the candidates; one primary test.
- Selection and parameters are chosen on walk-forward folds only. The holdout 2019-2026-04 is reported, not tuned on. The sealed 2026-05..11 window is touched once, only if a candidate passes every gate.
- No lookahead: features at date t use data through t; fills at t+1 close (the A0 delay correction).

## 4. Steps

S0. Fix the universe-size flaw (about 0.5 day): compute percentile ranks over the point-in-time members active on each control date, not over all loaded columns. Add a test: adding unrelated non-member columns must not change the picks. Rerun B.5 and B.5+B.4 as the new baseline. All later comparisons are against this baseline.

S1. Signal audit (about 1.5 days, no new book runs): for each of the 32 stock features and the four score components, compute cross-sectional rank IC against forward returns at 14d, 8w and 13w on the PIT universe, by year, with t-stats (Newey-West) and turnover of the signal. Also the quintile spread (top minus bottom) net of costs. Output a table: which components carry return information, which only carry risk. Prior evidence (tracker section 25: return timing IC about 0.02) suggests little return signal; this tests the cross-section, which has not been tested for stock selection.

S2. Candidate scores (pre-registered; each built from existing features, no new data):
  C1. Baseline S0 (control).
  C2. Risk score plus quality filter: drop the bottom third on profitability and leverage fields available in the feature set, then top 20 by the risk score.
  C3. Risk score plus momentum: risk percentile averaged with 12-1 month momentum percentile (50/50).
  C4. Risk-adjusted: rank by trailing return per unit of downside volatility (a Sortino-style score).
  C5. Lower-risk tilt: invert the score (lowest risk first), as a direction check since the high-vol anomaly literature predicts low-risk stocks do better on risk-adjusted terms.
  C6. Diversified risk: baseline score with at most 3 names per sector and 30 names instead of 20 (limits concentration; Tier B sectors are Unknown, so sector caps apply only to names with sector data and the limit is stated).
Each is run through the same B.5+B.4 harness (scripts/run_trackA_book.py) with no other change.

S3. Evaluation: walk-forward 2013-2025 folds (train 2008..Y, test Y+1) for any parameter; headline is the pooled out-of-sample series; also the holdout, 3y window and 2008-2018 table. Metrics: CAGR, Sharpe, Sortino, Calmar, MaxDD, turnover, average gross and beta, 2020 and 2022 drawdowns, cost sensitivity. Paired stationary block bootstrap on period differences vs C1 and vs SPY (95% CI and 2 SE).

## 5. Gates

A candidate advances only if ALL hold: beats C1 on Sharpe and Calmar by more than 2 SE on the pooled walk-forward series; beats SPY on the Gate 0 objective on the holdout; at least 9 of 14 folds non-negative vs C1; crash fold (2020) MaxDD at least as good as C1; survives 25 bps costs; robust to dropping flagged names (BWA, BBWI, JEF) and Tier B as a block. If none passes, the conclusion is that selection by these features does not improve the book on this data, and the decision moves to Gate 0 (ship a lower-drawdown book or park).

## 6. Effort and order

S0 0.5 day, S1 1.5 days, S2 and S3 about 3 days (candidates in parallel worktrees). About 5-6 days of agent time. RL work stays parked; the bandit rerun on the new book follows only if a candidate passes.

## 7. Risks

- With about 6 candidates and one reused history, a false positive is likely; the walk-forward pooled test and FDR are the guard, and a pass is a statement about this data, not a promise.
- Feature coverage: quality fields may be missing for Tier B and older names; report coverage and the effect of dropping uncovered names.
- Survivorship is reduced, not removed; a signal that works only on survivors is not evidence.
- Sector data is missing for Tier B names; C6 is partial.

## 8. Owner decisions

1. Gate 0 objective (default in section 2).
2. Approve lifting the B.5 freeze for this experiment only.
3. OK to run S0 first and rebaseline before any candidate.
