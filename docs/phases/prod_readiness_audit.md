> Audit run 2026-11-27 by a subagent in a worktree based on the pre-consolidation commit 33f54bb. Items marked "missing" docs (rl_shadow_mode.md, rl_consolidation_notes.md) and the "15 tests" count reflect that old base, not branch consolidate/rl-fixes.

# Production-readiness audit: B.5 + B.4 book (US equities)

Date 2026-11-27. Worktree `.claude/worktrees/agent-a8bc72d751b8f1e00` (HEAD 33f54bb). Scratch `runs_pa/` (51 MB). No output computed on the sealed 2026-05..11 window. Caveat: `load_inputs` loads the raw cache through 2026-11-24 into memory.

## Verdict
- **Paper trading: NO-GO as the code stands.** Conditional GO after B1, B3-B6 (about 1.5 engineer-days, mostly parallel).
- **Live: NO-GO.** Needs B7 (no broker boundary exists), M1 (survivorship), and the paper gates below.

## 1. Reference reconciliation (Q1): PASS for the explanation; 13.2 / 22-23 / 21.3 NOT VERIFIED

All runs at 10 bps, one-day lag, adjusted closes (`runs_pa/q1_q2_repro.py`, `q1b_variants.py`, `q1c_full_period.py`).

| Book | Window | CAGR | MaxDD | Sharpe | vs doc |
|---|---|---|---|---|---|
| B.5 report code, commit 92def7e, current data (multi-sleeve) | 2008-2026 | 16.22 | -31.46 | 1.092 | report 16.04 / -32.98 / 1.078; turnover 84.12 exact |
| HEAD equity-only (SPY and trend to cash) | 2008-2026 | 9.24 | -23.20 | 0.781 | fails Sharpe > 0.9 gate |
| HEAD equity-only, SPY overlay = cash | holdout 2019-01-01..2026-04-24 | **14.09** | **-20.40** | **1.108** | doc sec. 2: 14.1 / -20.4 / 1.10 |
| Same, 0 / 50 bps | holdout | 14.28 / 13.31 | -20.3 / -20.7 | 1.12 / 1.05 | "14.2" (0 bps); "13.2" not exact |
| HEAD, SPY overlay kept as SPY (B.4 spec) | holdout | 16.29 | -27.01 | 1.037 | not in docs |
| HEAD equity-only | 3y 2023-05-09..2026-04-06 | 18.91 | -8.18 | 2.00 | doc 21.3 / -8.2 / 2.09: CAGR NOT reproduced |
| Equity-only book x0.5 / x0.72 | holdout | 7.0 / 10.1 | -10.5 / -15.0 | 1.11 | doc "static 50/72%" 22.5 / 32.0: NOT reproduced |
| SPY buy-and-hold | holdout | 17.21 | -33.72 | 0.88 | doc 17.2 / -33.7: PASS |

**What explains each number**
- **16.04%**: multi-sleeve book (stocks plus SPY/TLT/GLD/UUP). Commit 860fa26 (2026-11-27) added `constrained.drop(columns=NON_TRADABLE_ASSETS)` at `scripts/run_phase_b5_final_gate.py:168`. That turns the sleeves into cash: full-period CAGR about -7 pp, MaxDD from -33% to -23%. The pre-strip commit, run on current data, reproduces the report to 0.2 pp.
- **14.1%**: equity-only, overlay as cash, 10 bps, holdout. Cost moves it 14.28 (0 bps) to 13.89 (20 bps).
- **22-23%**: no B.5/B.4 variant reproduces it. The tracker's H1 explanation ("static 0.5 = same book at 50% gross") is refuted: scaling a 29%-gross book by 0.5 gives 7.0%. 23.1% equals the j2r env 3y CAGR (env run not checked, NOT VERIFIED).

**Expectation for live.** The code as it stands (equity-only, b5_only) is 9.2% CAGR / -23% MaxDD / Sharpe 0.78 over 2008-2026 at 10 bps. That is the only window not used for selection. The 14% holdout is optimistic: it was used to promote the model (`artifacts/production/rl_e7_manifest.json`, promoted 2026-05-04 on that holdout) and to gate the book, and survivorship bias (M1) is unquantified. Plan on about 9-10% CAGR and -23% MaxDD. Restoring the overlay (B2) gives 11.8% / -27% over the full period.

## 2. Parity (Q2): PASS for weights, FAIL for spec

`runs_pa/q2_parity.py` calls the real `run_prod_signal.compute_allocation` on 18 holdout dates (12 fixed, 6 control), cold-start state.
- `b5_only` vs backtest book: max abs weight difference **4.8e-7** on all 18 dates (rounding). PASS.
- Both drop the SPY overlay (`run_prod_signal.py:348`; `run_phase_b5_final_gate.py:168`). Beta is **below the 0.50 floor on 6 of 48 holdout control dates (min 0.41)**. FAIL against B.4.
- Holdout NAV/exposure: average gross **0.29 (drop) vs 0.49 (overlay kept)**; CAGR 14.1 vs 16.3; MaxDD -20.4 vs -27.0.
- **Default prod mode is RL** (`run_prod_signal.py:392`, `default="rl_e7"`). Across the 18 dates the RL equity share runs 0.25-0.80, its stock sum differs from the B.5 book by 0.091 on average (max 0.20), and its beta is pinned to 0.50 by scaling, not by the overlay. FAIL parity.
- NOT VERIFIED: the CLI `main()` end to end, and a full daily holdout run.

## 3. Execution timing (Q3): timing effect small; stale-data handling FAIL

- Backtest: decide and fill at close d-1, earn d (`shift(1)`). Paper journal: fill at next-day `adj_close` (`log_paper_fills.py:85-111`; docstring says open). Live intent: 16:05 ET signal, 09:35 ET market order, so fill near the open. Holdout CAGR: 14.09 / 13.90 / 14.15. Effect about 0.25 pp.
- `run_prod_signal` defaults `as_of` to `prices.index.max()` with no staleness check. `compute_paper_orders.load_close_prices` silently uses the last price <= target. Data refresh is fail-open (`run_daily_paper_ops.py:164`: "will use existing (possibly stale) features", then continues).
- Non-rebalance days: `b5_only` holds the latest control weights (same as backtest). `rl_e7` carries weights only in equity-only mode.
- Holidays: `run_j2_backfill.py:38` uses `pd.bdate_range`, so it runs on NYSE holidays (duplicate decisions). Code reading only.
- Missing prices: NaN becomes zero return via `fillna(0)`. BK and CTRA have no cache; neither is in the book (checked). Latent.

## 4. Order sizing (Q4): BLOCKER, sizing on initial NAV still present

- `scripts/compute_paper_orders.py:133` sets `nav = cfg["capital"]["initial_nav"]` (50k); `:172` computes `target_s = floor(w * nav / price)`. Holdout NAV ranges 0.95x-2.63x of 50k, so the effective weight multiplier (50k / current NAV) is **0.38 to 1.05**.
- Over-budget normalisation applies only when the sum exceeds 1; equity-only sums are at most 0.34, so it never fires.
- Rounding: 6 dp fractional shares (fine). Minimum notional $1 turns small trades into holds, and drift is not tracked. No cash buffer. `est_slippage_bps` is a label, not applied to NAV.
- Cost: backtest 10 bps vs config `slippage.assumption_bps: 20`. The gap is small (13.89 at 20 bps) but must be aligned.
- Turnover: 19 of 120 control dates exceed 0.35 one-way (max 0.54), against `max_turnover_rebalance: 0.35`, which nothing enforces. `max_position_weight: 0.05` is also unenforced (book max 2%, not binding today).

## 5. Data pipeline (Q5): PARTIAL

- `adj_close` for signals and sizing. No independent corporate-action check. NOT VERIFIED.
- Universe: 503 current constituents (`config/universes/sp500.yaml`). PIT membership is an ADV-based mask (`data/artifacts/universe_mask_sp500.parquet`, about 268 active names per date), not index membership. **Survivorship bias present, unquantified** (NOT VERIFIED).
- Guard CSV `artifacts/reports/phase_b0_data_window_guard.csv`: sp500_dynamic `last_nonzero_active_date=2026-04-24`, `needs_clip_or_mask_refresh=True`. The B.2 candidate is clipped there (`run_phase_b3_exposure_control.py:216`). Live use goes stale (B4).
- BK and CTRA fetch failures are logged, then ignored.
- Determinism: pure build, PPO `deterministic=True`; but the same commit on a later data cut differs (16.22 vs 16.04). Same-day rerun NOT VERIFIED.

## 6. Journal replay (Q6): NOT RUN (owner constraint)

- J2 starts 2026-05-12, inside the sealed 2026-05..11 window. A replay would run on it, so it was not run.
- `data/paper_trading_j2`, `allocations_j2`, `audit_j2`, `prod_state` are absent in this checkout. Cold start would silently reinitialise state.
- The journal records `Mode: rl_e7 (dual-mode switching active)` (`docs/paper_trading_j2_journal.md:4`). J2 ran the RL path, not the deterministic book.

## 7. Operations (Q7): FAIL on idempotency and kill switch

- Idempotency FAIL: `src/rl/audit_trail.py:45-70` `append_decision` appends with no dedupe on `as_of_date`; `log_paper_fills.append_slippage_summary` appends. Reruns duplicate rows. Rerun test NOT RUN.
- Failure handling: a failed signal step stops orders; 300 s subprocess timeout per step; the refresh fail-open is in section 3.
- Logging: allocation JSON has as_of, mode, weights, 42-dim state, raw action, policy diagnostics, NAV. No input checksums or config hash. Partial.
- Kill switch: only `--mode-override` and `--force-rebalance`. No halt flag, no loss stop. The G.4 rule (`src/rl/switching_rule.py`) can move rl_e7 to b5_only automatically. Hard-coded references (`run_prod_signal.py:468-469`: Sharpe 1.296, MaxDD -24.48%) do not match the B.5 report (1.078 / -32.98%).
- Secrets: none in repo. Broker boundary: **none** (orders are CSV; no submission or reconciliation).
- RL shadow (doc missing): attach after the allocation JSON write in `run_prod_signal.main()`; call `model.predict` on the same `rl_state` and log only.

## 8. Tests and CI (Q8): PASS for existing tests; large gap

- `PYTHONPATH=. .venv/bin/python -m pytest -q tests`: **15 passed in 0.83 s** (`runs_pa/pytest_out.log`).
- Covered: equity-only invariants, leakage guards, optimizer, volatility alpha.
- Not covered: B.4 projection and beta band, `compute_allocation`, sizing, fills, daily ops, switching, idempotency, golden parity. No artifact-gated tests. CI NOT VERIFIED.

## 9. Risk limits and monitoring (Q9): PARTIAL

- Enforced in code: gross cap 1.5 and beta band on control dates (B.3/B.4 projection). The overlay strip (B2) breaks the floor.
- Not enforced in prod: drawdown, turnover (0.35), position cap (0.05), kill switch.
- G.3 drift report as-of 2026-08-18; G.5 dashboard as-of 2026-04-24; both generated 2026-08-19, about three months stale. No crontab or LaunchAgent on this host, so nothing schedules them here.

## Ranked defects

| ID | Sev | Defect | Evidence | Fix | Hours | Parallel |
|---|---|---|---|---|---|---|
| B1 | BLOCKER | Default and journal mode is RL, bypassing B.4 and contradicting the B.5-only decision | `run_prod_signal.py:392`; `paper_trading_j2.yaml:38`; journal line 4 | Hard-set b5_only; remove default; assert in daily ops | 2 | yes |
| B2 | BLOCKER | Overlay dropped: beta < 0.50 on 6/48 dates; gross 0.29 vs 0.49 | `run_phase_b5_final_gate.py:168`; sec. 2 | Owner decides: restore overlay as SPY weight (16.3% / -27%) or amend spec; regenerate | 3 + decision | owner first |
| B3 | BLOCKER | B.5 gate PASS does not reproduce on HEAD (9.24 / 0.78; Sharpe > 0.9 at 10 bps fails) | `artifacts/reports/phase_b5_final_gate.md:28,77`; `q1c` | Re-issue gate on HEAD; record the 860fa26 cause | 3 | yes |
| B4 | BLOCKER | Book frozen at 2026-04-24 (clip and mask end) | `run_phase_b3_exposure_control.py:216`; `run_prod_signal.py:193`; guard CSV | Separate research clip from live; refresh mask; fail unless snapshot date is last trading day <= as_of | 6 | partly |
| B5 | BLOCKER | Sizing on initial NAV (50k); multiplier 0.38-1.05 | `compute_paper_orders.py:133,172` | Size on MTM NAV; unit test | 3 | yes |
| B6 | BLOCKER | Fail-open data refresh; silent last-price fallback | `run_daily_paper_ops.py:164`; `refresh_market_data.py:201`; `load_close_prices` | Fail closed; require price date == signal date | 3 | yes |
| B7 | BLOCKER (live) | No broker submission, reconciliation or kill switch | none | Executor with reconciliation and kill flag | 16-24 | after paper |
| M1 | MAJOR | Survivorship: 503 current names, ADV mask | `sp500.yaml`; mask | Historical constituents, or disclose and quantify | 8-16 | data |
| M2 | MAJOR | Reruns duplicate audit and slippage rows; no lock | `audit_trail.py:45-70`; `log_paper_fills.py` | Upsert on (as_of, journey); lock | 3 | yes |
| M3 | MAJOR | Turnover and position limits unenforced; 19/120 dates over 0.35 | `paper_trading_j2.yaml` risk block | Enforce or record owner waiver | 3 | yes |
| M4 | MAJOR | Reference table unreproduced (22-23%, 21.3%, static 50/72%) | `rl_allocator_experiments.md` sec. 2, H1 row | Correct doc; regenerate from code | 2 | yes |
| M5 | MAJOR | Holdout used for promotion and gating, so 14% is not out-of-sample | `rl_e7_manifest.json`; B.5 gate | Treat as dev; owner runs sealed test once | owner | owner |
| M6 | MAJOR | Test gaps (sec. 8) | `tests/` | Add beta-band, projection, sizing, idempotency, golden parity tests | 6 | yes |
| M7 | MAJOR | Monitoring stale; no scheduler or alert | report dates; no cron | Schedule daily ops; alert on non-zero exit | 4 | yes |
| M8 | MAJOR | Switching refs hard-coded, inconsistent with B.5 | `run_prod_signal.py:468-469` | Read from gate artifact | 1 | yes |
| M9 | MAJOR | Silent cold start when state missing | `load_portfolio_state` | Fail if journey state missing | 1 | yes |
| m1 | MINOR | Backtest 10 bps vs config 20 bps | `paper_trading_j2.yaml` | Align and document | 0.5 | yes |
| m2 | MINOR | Fill docstring says open, code uses adj_close | `log_paper_fills.py:85-88` | Fix docstring | 0.25 | yes |
| m3 | MINOR | Holidays in `bdate_range` | `run_j2_backfill.py:38` | NYSE calendar | 1 | yes |
| m4 | MINOR | Silent fetch failures; NaN as zero return | BK, CTRA | Log; fail if a held name lacks prices | 1 | yes |
| m5 | MINOR | Docs named in brief missing (`rl_shadow_mode.md`, `rl_consolidation_notes.md`); experiments doc has no sec. 12 or 23 | repo search | Restore or correct references | 0.5 | yes |

Parallel: B1, B3, B5, B6, M2-M4, M6-M9, m1-m5. Sequential: B2 (owner), then B3 re-run, then B4, then go/no-go.

## Go / no-go

**Paper trading (B.5-only, owner-chosen spec), all required:**
1. Mode hard-set to b5_only; test that no RL path is reachable from daily ops.
2. Overlay decision (B2) recorded; gate re-issued on HEAD, PASS or owner-accepted FAIL.
3. Staleness gate: fails unless the B.5 snapshot date is the last trading day <= as_of (test on a post-clip date).
4. Sizing on MTM NAV: notional error < 1% on a synthetic 2x-NAV case.
5. Two runs on the same date give identical files and no duplicate rows.
6. Data refresh failure gives non-zero exit and no orders.
7. Daily ops scheduled, with alert on non-zero exit.

**Live, in addition:**
8. Broker executor with reconciliation: zero breaks over at least 20 paper days.
9. Kill switch tested; turnover and position limits enforced or formally waived.
10. Survivorship addressed or quantified (M1).
11. Owner runs the sealed test once; result recorded.
12. Cost model calibrated to at least 20 paper fills; median slippage at or below the configured assumption.

## NOT VERIFIED (owner or live data)
- Broker fill quality, real spreads, whether 10 or 20 bps is realistic for high-beta names.
- Survivorship magnitude (needs historical constituents).
- 13.2%, 22-23%, 21.3% (3y), static 50/72% rows; j2r env runs not re-run.
- J2 journal replay and NAV comparison (sealed window; state absent here).
- Same-day rerun determinism; holiday and early-close behaviour (code reading only).
- End-to-end CLI runs of `run_prod_signal.py` and `run_daily_paper_ops.py`.
- Dollar impact of the sizing bug on the real J2 NAV.
- CI configuration; `docs/phases/rl_shadow_mode.md` (missing).
