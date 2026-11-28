# Plan (rev 2): is stock selection worth improving? Controls first

Status: PLAN rev 2 (2026-11-28), not executed. Rev 1 was reviewed by six EGM reviewers (design, zoom-out, implementation readiness, codebase details, inventive catalyst, comprehension); this revision folds in their findings. Evidence: tracker sections 25, 33, 34.

## 0. Terms (for a new reader)

- B.5: the stock sleeve. Score = mean percentile rank of 63-day volatility, downside volatility, beta to SPY (all higher = riskier) and max drawdown; top 20 names, equal weight (scripts/run_phase_b2_turnover_control.py build_vol_path_fast).
- Trend sleeve: a volatility-targeted SPY position (TREND_ASSETS = ["SPY"], target vol 10%, gross cap 1.5).
- Promoted book: stock sleeve and trend sleeve blended each control date. Trend weight = 0.50 + 0.30 x stress score, capped at 0.75; stock weight = 1 - trend weight (so 25% to 50%). scripts/run_phase_b2_turnover_control.py combine_candidate_weights, built by build_b2_candidate.
- B.4: the risk engine: beta band (floor 0.50, cap 0.90 - 0.20 x stress), gross and turnover caps (scripts/run_phase_b4_risk_engine.py).
- Equity-only mode: SPY and other non-stock columns are dropped after B.4 (scripts/run_phase_b5_final_gate.py, NON_TRADABLE_ASSETS); the freed weight is held as cash.
- Gate 0: the owner's definition of success (section 2). Tier B: index exits added from free data (PR #3). Survivorship-reduced universe: 568 names, corrected point-in-time mask (tracker 34). Holdout: 2019-01-01..2026-04-24, already reused; sealed window 2026-05..11 untouched.

## 1. What rev 1 missed (new facts)

1. In equity-only mode the trend sleeve is deleted and its weight becomes cash. With trend weight 0.50-0.75, the stock sleeve receives only 25-50% of capital before B.4 and about 30% gross after it. The 9.1% holdout CAGR is therefore mostly an idle-cash result, not a stock-selection result: picks fully invested earn 21.8%. Selection can only move 25-50% of the book.
2. The vol score is a percentile over every column in the loaded panel, including sector ETFs, macro ETFs, the VIX proxy and non-members (volatility_score.py:35-47; the mask is applied after scoring, run_phase_b2_turnover_control.py:94). The "-67 points" in section 33 is cumulative return (+519% to +452%); in CAGR it is 2 points (28.8% to 26.8%). The flaw is real but smaller than I said.
3. C2 (quality filter) is infeasible: the 32 stock features contain no fundamentals and base.yaml sets the fundamentals provider to "simulated".
4. The loader reads sealed-window rows (no end cap in load_inputs); only the harness clips at 2026-04-24.
5. scripts/run_trackA_book.py and config/universes/sp500_pit_experiment.yaml exist only on branch worktree-agent-a88e253b6b67161cf (unmerged). No bootstrap, Newey-West or IC-by-horizon code exists on exp/no-tlt; rank-IC pieces exist in src/backtest/walk_forward.py:478-499 and scripts/run_alpha_research.py.
6. Walk-forward folds have nothing to fit for fixed-rule scores; they only measure per-year stability.

## 2. Gate 0 (owner decides before Phase 1; recommendation)

Options: (A) beat SPY on Sharpe and Calmar after 10 bps; (B) keep a lower-drawdown book: MaxDD at least 10 points shallower than SPY with CAGR within X points of SPY (owner states X); (C) maximise return with a drawdown cap. Recommendation: B, because the book's only demonstrated edge is drawdown (-21% vs -34%). Under A the current book fails on both survivorship-reduced and survivor data.

## 3. Phase 1: controls (about 1.5 days, no new signals)

Run through the same harness (merge run_trackA_book.py first) on the experiment universe, 10 bps, holdout, 3y and 2008-2018:
- P1a Sleeve split: report the stock-sleeve weight, the trend-sleeve weight and the cash share over time for the promoted book.
- P1b Idle-cash test: the same picks with the trend sleeve replaced by SPY exposure (non-equity-only) and with the stock sleeve fixed at 100%, 75%, 50%, 30% of capital, remainder cash and remainder SPY.
- P1c Random-pick null: 500 random 20-name draws from the point-in-time members through the identical book; report the distribution of CAGR, Sharpe, Calmar, MaxDD.
- P1d SPY scaled to the book's average gross and beta, and an equal-weight member basket at the same gross.
- P1e Minimum detectable effect for Sharpe and Calmar differences at the pooled sample size (block bootstrap, block length 6 monthly observations).
Decision rule: if the real picks do not beat the 90th percentile of the random-pick null on Sharpe or Calmar, selection adds nothing measurable: stop improving selection and go to the structure question (section 5). If the scaled-SPY control matches the book on Sharpe and Calmar, the book's value is the cash, not the stocks.

## 4. Phase 2: bug fixes (about 1-1.5 days, do regardless)

- S0: compute percentile ranks over the point-in-time members active on each control date only: add a members mask argument to compute_volatility_score_frame, passed from load_inputs; exclude ETFs and non-stock columns from the pool. Test: adding unrelated columns does not change scores, picks, or liquidity_rank and the sector medians (these two are pool-dependent too). Check the rank denominator equals the active count. Rebaseline B.5 and the book; all later numbers use the new baseline.
- Truncate or assert on data after 2026-04-24 in load_inputs for any evaluation run.
- Make top-N a parameter (the 20 is hardcoded at lines 97 and 101-102).

## 5. Structure question (decide after Phase 1)

If P1b shows the idle cash is the main drag, the real decision is the design: (a) keep the trend sleeve as SPY exposure (the pre-equity-only book), (b) raise the stock share and let B.4 cap beta, (c) accept a low-return, low-drawdown book. This needs an owner decision and conflicts with the "individual equities only" rule; state it plainly. The earlier committed 16% PASS included the SPY overlay.

## 6. Phase 3: signal audit and candidates (only if Phase 1 says selection is worth testing; about 5-6 days)

S1 signal audit: rank IC and quintile spread for the continuous features and the four score components against forward returns at 10, 40 and 65 trading days from the t+1 fill, sampled every 10 days to limit overlap, Newey-West lag = horizon/10, by year, net of 10 bps at the rank-turnover observed. Reuse src/backtest/walk_forward.py IC code. Binary and non-cross-sectional features are excluded (above_50dma, trend_consistency, avg_dollar_volume_63d).
Candidates (pre-registered, at most 3, chosen by S1 and fixed before any book run):
- K1 baseline (rebaselined S0).
- K2 momentum only: top 20 by ret_12m_ex_1m (select for return, let B.4 size the risk).
- K3 lowest-risk first: the same score, sorted ascending (one direction, declared now).
- K4 (optional, if S1 supports it): 50/50 risk percentile and 12-1 momentum percentile.
Dropped: C2 (no real fundamentals; revisit only with a paid fundamentals source), C4 (folded into S1 as a signal), C6 (sector cap needs sectors for 68 Unknown names).
Reported per candidate: selection fully invested, at matched gross, and through B.4; gross, pre-projection beta, beta_up and SPY-overlay counts (K3 will trigger the beta floor and SPY would confound it).

Evaluation: per-calendar-year test slices 2009-2025 (17 years), described as stability, not out-of-sample fitting; the pooled monthly return series is the unit. Paired stationary block bootstrap (new code, block 6 months, 5,000 draws) for Sharpe and Calmar differences vs K1 and vs SPY.

## 7. Gates (a candidate advances only if ALL hold)

1. Sharpe and Calmar difference vs K1 above 2 bootstrap SE on the pooled monthly series, fully invested and at matched gross; primary metric = Sharpe difference (BH-FDR over the 2-3 candidates).
2. Beats the 90th percentile of the random-pick null (P1c).
3. At least 11 of 17 calendar years non-negative vs K1; 2020 calendar-year MaxDD no worse than K1.
4. Survives 25 bps and the removal of BWA, BBWI, JEF and Tier B as a block (CAGR change under 2 points).
5. Meets the Gate 0 objective on the holdout.
A pass is a statement about this upper-bound universe; before any shipping step, buy survivorship-free data and rerun, then use the sealed window once.

## 8. Outcomes and deciders

| Outcome | Next action | Decider |
|---|---|---|
| Phase 1: picks do not beat random | Park selection work; go to section 5 | Owner |
| Phase 1: scaled SPY matches the book | Book value is the cash; decide whether to ship a low-drawdown SPY-plus-cash book | Owner |
| Phase 3: no candidate passes | Keep K1, close the experiment, record the null | Owner |
| Phase 3: a candidate passes | Buy delisted data and rerun; then one sealed-window test; then production planning | Owner approves each step |

## 9. Effort and impact

Phase 1 about 1.5 days, Phase 2 about 1-1.5 days, Phase 3 about 5-6 more (reviewer estimate for the full rev 1 scope was 7-10 days; this plan cuts C2, C4, C6). Reviewer estimates of outcomes (not measured): the controls most likely show the book's value is the cash and the drawdown (about 60%), little return signal in the audit (about 30%), a passing candidate (about 10%, still an upper bound). The cheapest and most informative step is Phase 1.

## 10. Risks

Reused history (one path, holdout already used); survivorship still partial (about 360 delisted names missing, which are disproportionately the risky names this score picks); Tier B prices not independently validated at scale; Gate 0 undecided.
