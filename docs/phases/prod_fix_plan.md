# Fix plan: production blockers for the B.5 + B.4 book (rev 2, after EGM review)

Status: PLAN (2026-11-28), not executed. Source: `docs/phases/prod_readiness_audit.md` (defect IDs B1-B7, M1-M9, m1-m5). Scope: the deterministic B.5 stock book with the B.4 risk engine, equity and cash only. The RL allocator is out of scope: it stays in shadow mode (`docs/phases/rl_shadow_mode.md`, branch `consolidate/rl-fixes`).

Revision 2 applies the EGM design, simplicity and readiness reviews (2026-11-28). Changes: survivorship and dashboard regeneration moved off the paper path; the shared-function refactor removed (D-a default is a doc amendment); the per-journey lock dropped; tests merged into each package; research-path `fillna` untouched; WP3 reuses the existing MTM NAV function.

## 0. Goal and non-goals

Goal: the paper-trading path does what the owner-approved spec says, is idempotent and fails closed, sizes on current NAV, and has tests that would catch the audit's findings.

Non-goals:
- Changing B.5 stock picks (frozen).
- Any change to RL training, the reward, or the RL env (RL is shadow-only).
- Touching the sealed window 2026-05..11 (one-shot, owner decision).
- Broker integration (B7), survivorship (M1), dashboard regeneration: separate tickets.

## 1. Owner decisions required before coding

| ID | Decision | Options | Default if no answer |
|---|---|---|---|
| D-a | SPY overlay (B2) | (i) restore as an explicit SPY weight to the beta floor (holdout 16.3% / -27%); (ii) amend the spec to equity plus cash and accept beta below 0.50 on some dates | (ii): a documented spec amendment, with daily beta reported and dates below 0.50 flagged |
| D-b | Cost assumption | 10 bps (backtest) or 20 bps (config) | 20 bps in the prod config and sizing; backtest stays 10 bps with a sensitivity line in the report |
| D-c | Turnover limit (M3) | enforce 0.35 on rebalance days, or waive per date | enforce, with a waiver record |
| D-d | Sealed test (M5) | run once on the baseline now, or later | later, after paper gates |

WP1, WP2, WP3, WP6, WP8 and WP9 do not depend on D-a to D-d and can start now.

## 2. Work packages

Each package is one branch off `consolidate/rl-fixes` (or main after PR #2 merges) and one PR. Tests are written first inside each package.

### WP1 Mode lock (B1, M8, M9) — 2 h
- `run_prod_signal.py:392`: default `--mode b5_only`; remove `rl_e7` from the daily-ops path. `run_daily_paper_ops.py` asserts mode == `b5_only`.
- Replace the hard-coded switching references (`run_prod_signal.py:468-469`) with values read from the B.5 gate artifact.
- `load_portfolio_state`: fail if the journey state is missing. Cold start only with an explicit `--init-journey` flag.
- Tests: `test_daily_ops_cannot_select_rl`, `test_missing_state_fails`.

### WP2 Staleness and fail-closed data (B4, B6, m4) — 3-4 h
- `run_daily_paper_ops.py:164`: a failed data refresh exits non-zero before any order step. Today it logs a warning and continues; the fix is the exit change plus the stop.
- `compute_paper_orders.load_close_prices`: require the price date to equal the signal date; remove the last-price fallback on the live path.
- Fail unless the B.5 snapshot date is the last trading day <= `as_of`.
- Missing price for a held or targeted name on the live path: fail. The `fillna(0)` on research return paths is left unchanged.
- Research clip and mask (`run_phase_b3_exposure_control.py:216`) stay as they are; the live path reads a mask refreshed through the last available date (data step, needs the data pipeline).
- Tests: `test_refresh_failure_no_orders`, `test_stale_snapshot_rejected`, `test_price_date_must_match_signal`, `test_missing_price_fails`.

### WP3 Sizing on current NAV (B5) — 1-2 h
- `compute_paper_orders.py:133,172`: replace `initial_nav` with the mark-to-market NAV at `as_of`. Reuse `compute_mtm_nav` from `scripts/log_paper_fills.py` (already used on the fills path, lines 174-175 and 378-387). Do not write a second NAV function.
- Fall back to `initial_nav` only when no positions exist (matches the existing T=0 rule).
- Tests: a 2x-NAV synthetic case gives notional error < 1%; a 0.5x case; the T=0 fallback.

### WP4 Overlay decision (B2) — D-a (ii): 1 h; D-a (i): 4 h, after D-a
- D-a (ii): amend the B.4 spec and `prod_readiness_audit.md` section on B2; add a daily beta column to the allocation JSON and flag dates below 0.50. No code change to the book.
- D-a (i) only: add an explicit SPY weight in `run_prod_signal.py` to the beta floor, matching the backtest's overlay (`run_phase_b4_risk_engine.py`). Copy the audit's 18-date parity script (`runs_pa/q2_parity.py` in worktree `agent-a8bc72d751b8f1e00`, not on any branch) into `tests/` as a golden test, at 1e-6 tolerance.
- Not in scope: a shared finalize function for env and RL. RL is shadow-only.

### WP5 Gate reproduction (B3) — 1 h of doc work, after WP2 and WP3
- Re-issue `artifacts/reports/phase_b5_final_gate.md` from the current code. Record the cause: commit 860fa26 stripped the sleeves (`run_phase_b5_final_gate.py:168`); 9.24% CAGR full period, Sharpe 0.78 fails the gate.
- Outcome is an owner-accepted FAIL or a PASS with a documented change. Thresholds are not edited.

### WP6 Idempotency (M2) — 2 h
- `audit_trail.append_decision` (`src/rl/audit_trail.py:45-70`) and `log_paper_fills.append_slippage_summary`: upsert on (as_of, journey), and skip if the day's output already exists. No file lock: this is one daily job.
- Allocation JSON records the config hash and the code commit. Input checksums are optional.
- Test: running the same date twice gives identical files and no duplicate rows.

### WP7 Limits (M3) — 2 h, after D-c
- Enforce `max_turnover_rebalance` (0.35) and `max_position_weight` (0.05) as checks that block the order file unless a waiver is recorded in the allocation JSON.
- Test: a 0.54 turnover case is blocked, or waived with a record.

### WP8 CI wiring — 1 h
- Test writing is inside each package above. This item is only CI: run the new tests on every push, and list artifact-gated tests as not run when their artifacts are absent.

### WP9 Corrections (M4, m1, m2, m3, m5) — 1-2 h
- Correct the tracker section 2 reference table (22-23%, 21.3%, static 50/72% not reproduced; state the audit's explanation).
- Holiday fix: `run_j2_backfill.py:38` uses `pd.bdate_range`. Replace with the calendar already in `src/data/calendar.py` after confirming it is the NYSE calendar. Do not build a new one.
- Fix the `log_paper_fills` docstring (open vs adj_close). Align the cost value per D-b.
- Restore or correct the doc references (`rl_shadow_mode.md`, `rl_consolidation_notes.md`).

### WP10 Scheduling and alert (M7) — 1 h
- Schedule the daily ops job. Alert on any non-zero exit through a log that is checked, or email.
- Dashboard and drift-report regeneration are not paper gates and are removed from this plan.

### Out of plan (separate tickets)
- M1 survivorship: one disclosure line in the gate report now; historical constituents later (8-16 h, data-bound). Required before live.
- B7 broker executor, reconciliation and kill switch (16-24 h): before live only.
- M5 sealed test: owner decision D-d.

## 3. Order and parallelism

```
D-a..D-d (owner)            ──────────────────────┐
WP1 mode lock ──┐                                  │
WP2 fail-closed ─┼─> WP5 gate ──────────────────────┼─> paper go/no-go
WP3 NAV sizing ──┤                                  │
WP6 idempotency ─┘                                  │
WP4 overlay (after D-a) ────────────────────────────┤
WP7 limits (after D-c) ─────────────────────────────┤
WP8 CI, WP9 corrections, WP10 scheduling: any time ─┘
```

Parallel now: WP1, WP2, WP3, WP6, WP9, WP10. WP5 waits for WP2 and WP3. WP4 waits for D-a. WP7 waits for D-c.

Estimated effort: about 17-20 engineer-hours for WP1-WP10, about one day of wall time with three workers. Earlier estimate (30 h) included items now moved out of scope.

## 4. Acceptance criteria (paper-trading go, all required)

1. Mode is `b5_only` and no RL path is reachable from daily ops (test).
2. Overlay decision recorded; if D-a (i), the 18-date parity test passes at 1e-6.
3. Stale snapshot or price-date mismatch exits non-zero with no orders (tests).
4. Sizing on current NAV: notional error < 1% on the 2x synthetic case.
5. Two runs on the same date give identical files and no duplicate rows.
6. Refresh failure: non-zero exit, no orders.
7. Gate re-issued from the current code (PASS, or owner-accepted FAIL with reason).
8. Turnover limit enforced, or waived per date with a record.
9. Daily ops scheduled; a failure alerts.
10. CI runs the new tests; artifact-gated tests are listed as not run when skipped.
11. Survivorship disclosed in the gate report (one line, quantification deferred).

Live go additionally needs B7, M1 quantified or addressed, 20 paper days with zero reconciliation breaks, a tested kill switch, and the owner's sealed-test result.

## 5. Risks

- Restoring the overlay (D-a i) lowers the 2008-2026 return and raises gross; the gate may then fail on Sharpe. That is a result to report, not a reason to change thresholds.
- Current-NAV sizing changes historical replay numbers; the journal replay must be re-baselined and not compared to the old journal without a note.
- The sealed window must not be used to choose any fix.
- Survivorship may be large; the paper gates do not measure it.

## 6. EGM review log

- Design review (egm-design): pending at time of writing; findings to be recorded here.
- Simplicity review (egm-zoom-out, 2026-11-28): applied the cuts in rev 2 (WP4 shared function removed; WP6 lock dropped; WP8 merged; WP9 trimmed; WP10 dashboards dropped; WP11 moved out). Verified in code: `finalize_b4_weights` does not exist; `compute_mtm_nav` already exists on the fills path.
- Readiness review (egm-implementation-readiness, 2026-11-28): the first attempt could not read the audit file (it was on another branch). Fixed by copying `prod_readiness_audit.md` onto this branch. Re-review pending.
