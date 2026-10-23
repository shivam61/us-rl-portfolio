# Remediation Plan — Validity Audit Follow-up

Origin: holistic design review (2026-10-23). Goal: find out whether the B.5 + RL system has real edge
once survivorship bias, holdout reuse, and small-sample noise are removed — before any real capital.

Order matters: R1 gates everything else. Each step has a pass/fail criterion fixed *before* running.

## Status

| Step | What | Needs market data? | Status |
|---|---|---|---|
| R0 | RL vs random-policy significance (tracked reports only) | No | **DONE** — see Results |
| R1 | Point-in-time universe (survivorship fix), rerun A.7.3 + B.5 | Yes | BLOCKED (data) |
| R2 | Null-model ablation on the same holdout | Yes | BLOCKED (data) |
| R3 | RL re-validation: multi-seed, walk-forward, untouched holdout | Yes | BLOCKED (data) |
| R4 | Turnover attribution by sleeve, fix at source | Yes | BLOCKED (data) |
| R5 | Drift monitor: baseline = stored training distribution; advisory-only | Partly | PLANNED |
| R6 | Truly forward paper trading with pre-registered, CI-aware gates | Live feed | PLANNED |
| R7 | Engineering hygiene (shared engine, tests, repo size) | No | PLANNED |

## R0 — RL vs random policies (done)

Method: `scripts/analyze_rl_vs_random.py` on `artifacts/reports/e7_random_distribution.csv` and
`e7_policy_comparison.csv`. Output: `artifacts/reports/rl_vs_random_significance.md`.

## R1 — Point-in-time universe

- Membership: historical S&P 500 changes (`raw.githubusercontent.com/fja05680/sp500` is reachable; verify license/quality).
- Prices incl. delisted names: yfinance cannot supply most of them. Real fix = CRSP / Norgate / Sharadar.
  Interim: add every removed name Yahoo still serves, and report how many removed names remain missing
  (this bounds the residual bias).
- Rebuild `universe_mask_sp500.parquet` from membership-by-date AND the existing ADV rule.
- Rerun: A.7.3 raw signal, B.5 full system, 2008–2026 and holdout 2019–2026, 10 and 50 bps.
- **Pass:** B.5 holdout Sharpe >= 0.90 and MaxDD >= -35% on the PIT universe.
  If it drops below 0.90, R3 is moot and the alpha needs rework (Phase A).
- Also report: Sharpe of the *same* signal long-only top-20 equal-weight vs SPY, to size the survivorship haircut.

## R2 — Null models (same dates, costs, holdout)

Compare against B.5 and trained RL, matched on average equity exposure:
1. Fixed mixes: equity 40/60, 50/50 with the same trend sleeve.
2. Vol-targeted equity (10% / 12% target), same trend sleeve.
3. B.5 scaled by a constant to RL's average equity (0.41).
4. Trend-only (TLT/GLD/UUP) and SPY buy-and-hold.
- **Pass (keep RL):** trained RL beats the best null on Sharpe AND MaxDD by more than the seed std (R3).
  Otherwise delete the RL layer and ship the best null (simpler, no retraining risk).

## R3 — RL re-validation (only if R2 says RL is worth keeping)

- >= 20 training seeds; walk-forward retrain (expanding window, yearly); no hyper-parameter edits after seeing results.
- Holdout = data never used in any gate decision (forward-only from 2026-05 onward + a reserved 2024+ slice).
- Report block-bootstrap 90% CI on Sharpe difference vs best null; apply a deflated-Sharpe / trials-count haircut
  (count E.1–E.8, F.2 and every lambda change as trials).
- **Pass:** lower CI bound of Sharpe difference > 0.

## R4 — Turnover

- Decompose each rebalance's turnover into: stock-sleeve rotation, intra-sleeve reweighting, sleeve-fraction moves
  (RL), trend-sleeve. Use one-way turnover and the *real* NAV (not the hard-coded 50000 in
  `generate_paper_journal.py:164`); restate the H-3 gate in those units.
- Fix at the source: rank hysteresis for top-20 (hold until rank > 40), no-trade band on weight changes,
  optimizer turnover penalty. Do **not** add a turnover term to the RL reward until attribution shows RL is the cause.
- **Pass:** one-way turnover per rebalance < 20% with Sharpe loss < 0.05 (10 bps) in backtest.

## R5 — Drift monitor / switching

- Persist the training-state distribution at train time; `flag_feature_psi` must receive it as `baseline_df`
  (today it defaults to the first 63 live audit rows, `drift_monitor.py:178-186`).
- Minimum live-window length (>= 30 points) before PSI can fire.
- Fix reference constants in `SwitchingRuleEngine` (1.296 / -24.48% are RL numbers, not B.5's).
- Switching becomes advisory (alert, no auto mode change) until backtested on training-period folds — not on J2.

## R6 — Forward paper trading

- Real-time daily runs via the Alpaca paper API; no backfills, no replays of past windows.
- Pre-register gates: >= 6 months, gates stated as confidence intervals (a Sharpe estimate over 71 days has SE ~ 2).
- Replace H-2 (T vs T+1 close) with fill price vs arrival mid.

## R7 — Engineering

- Move shared logic out of `scripts/run_phase_*` into `src/`; `src` must not import `scripts`.
- One backtest/live engine; add live-vs-backtest parity test for `run_prod_signal.py`.
- Tests for: universe mask PIT correctness, turnover calc, drift baseline, reward terms.
- Stop committing generated 8K-line journals; snapshot `data/` (hash manifest) per release.

## Unblocking R1–R4

This container's network policy blocks Yahoo, Stooq, Wikipedia, FRED (GitHub raw and PyPI work).
Either (a) allow `query1.finance.yahoo.com`, `query2.finance.yahoo.com`, `fc.yahoo.com`
(+ `fred.stlouisfed.org` for rates) in the environment's network settings, or (b) provide `data/` (raw + features
parquet) in the repo/branch, and install deps (`pip install -r requirements.txt`; PyPI is reachable).
Delisted-name prices need a paid vendor either way.

## Results so far

### R0 — trained RL is not distinguishable from random bounded policies

| Metric | Value |
|---|---|
| Random-policy Sharpe mean / median / p75 / max | 1.221 / 1.212 / 1.280 / 1.568 |
| Trained RL Sharpe (percentile among 50 random) | 1.296 (78th, z = 0.68) |
| Random seeds with Sharpe >= trained RL | 11 / 50 |
| Random seeds with Sharpe >= B.5 (1.270) | 15 / 50 |
| Random seeds with better MaxDD than B.5 (-33.0%) | 50 / 50 |
| Random seeds with better MaxDD than trained RL (-24.5%) | 18 / 50 |
| Random seeds with higher CAGR than trained RL (17.8%) | 39 / 50 |

Reading: (1) the drawdown improvement vs B.5 comes from the action bounds (every random policy has it), not
from learning. (2) The promotion cleared the p75 gate (1.280) by 0.016 Sharpe, vs a seed std of 0.109.
(3) 11 of 50 do-nothing-smart policies matched or beat the "promoted" policy on Sharpe, and 39 of 50 had higher CAGR.
Caveat: one trained seed (42) vs 50 random seeds; the random runs share the same holdout that was reused for
E.6 -> E.7 tuning.
