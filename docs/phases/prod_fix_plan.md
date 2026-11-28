# Fix plan: production blockers for the B.5 + B.4 book

Status: PLAN (2026-11-28), not executed. Source: `docs/phases/prod_readiness_audit.md` (defect IDs B1-B7, M1-M9, m1-m5). Scope: the deterministic B.5 stock book with the B.4 risk engine, equity and cash only. The RL allocator is out of scope: it stays in shadow mode (`docs/phases/rl_shadow_mode.md`, branch `consolidate/rl-fixes`).

## 0. Goal and non-goals

Goal: the paper-trading path does what the owner-approved spec says, is idempotent and fails closed, sizes on current NAV, and has tests that would catch the audit's findings.

Non-goals:
- Changing B.5 stock picks (frozen).
- Any change to RL training or the reward.
- Touching the sealed window 2026-05..11 (one-shot, owner decision).
- Broker integration (B7) is a separate later track.

## 1. Owner decisions required before coding

| ID | Decision | Options | Default if no answer |
|---|---|---|---|
| D-a | SPY overlay (B2) | (i) restore as SPY weight to the beta floor (holdout 16.3% / -27%); (ii) amend the spec to equity plus cash, accept beta below 0.50 on some dates | (ii), documented, with beta reported daily; (i) is the spec-faithful choice |
| D-b | Cost assumption | 10 bps (backtest) or 20 bps (config) | 20 bps in prod config and sizing; 10 bps backtest kept, sensitivity reported |
| D-c | Turnover limit (M3) | enforce 0.35 on rebalance days, or waive per date | enforce, with waiver log |
| D-d | Sealed test (M5) | run once on the baseline now, or later | later, after paper gates |

Work on B1, B3-B6, B8 and M-items does not depend on D-a to D-d and can start immediately.

## 2. Work packages

Each package has a branch off `consolidate/rl-fixes` (or main once PR #2 merges), one PR per package unless noted, tests first.

### WP1 Mode lock (B1, M8, M9) — 2 h
- `run_prod_signal.py`: default `--mode b5_only`; remove `rl_e7` from the choices in daily ops; `run_daily_paper_ops.py` asserts mode == `b5_only`.
- Replace hard-coded switching references (`run_prod_signal.py:468-469`) with values read from the B.5 gate artifact.
- `load_portfolio_state`: fail if the journey state is missing (no cold start unless `--init-journey` is given explicitly).
- Tests: `test_daily_ops_cannot_select_rl` (argparse and config path), `test_missing_state_fails`.

### WP2 Staleness and data fail-closed (B4, B6, m4) — 4 h
- Data refresh failure in `run_daily_paper_ops.py:164` becomes a non-zero exit with no orders written.
- `load_close_prices` (`compute_paper_orders`): require the price date equal to the signal date; no last-price fallback.
- Fail unless the B.5 snapshot date is the last trading day <= `as_of`.
- Missing price for a held or targeted name: fail; `fillna(0)` on return paths is removed for live use (kept for research).
- Separate the research clip/mask (`run_phase_b3_exposure_control.py:216`) from the live path; refresh the universe mask through the last available date (needs data).
- Tests: `test_refresh_failure_no_orders`, `test_stale_snapshot_rejected`, `test_missing_price_fails`, a post-clip date case.

### WP3 Sizing on current NAV (B5) — 3 h
- `compute_paper_orders.py:133,172`: size on mark-to-market NAV from the journal at `as_of` (previous close), not `initial_nav`.
- Add a drift-tracking note: targets are weights of current NAV; minimum notional rule documented.
- Tests: synthetic 2x NAV case gives notional error < 1%; 0.5x case; unit test on the NAV source.

### WP4 Overlay and beta band (B2) — 3 h after D-a
- If D-a = (i): restore the SPY overlay as an explicit SPY weight in `run_prod_signal` and in the backtest so both use one function (`finalize_b4_weights`); add a parity test on 18 dates to 1e-6 (the audit's `q2_parity.py` is the template).
- If D-a = (ii): amend `docs/phases/prod_readiness_audit.md` and the B.4 spec; the report records daily beta and flags dates below 0.50.
- Either way: one shared function for env, backtest and prod (this also closes the RL parity issue).

### WP5 Gate reproduction (B3) — 3 h, runs in parallel
- Re-issue `artifacts/reports/phase_b5_final_gate.md` on HEAD. Record the cause (commit 860fa26 stripped the sleeves; 9.24% CAGR full period, Sharpe 0.78 fails the gate).
- Gate outcome is owner-accepted FAIL or a PASS with a documented change. No edits to thresholds to make it pass.

### WP6 Idempotency and logging (M2, parts of section 7) — 3 h
- `audit_trail.append_decision` and `log_paper_fills.append_slippage_summary`: upsert on (as_of, journey); a file lock per journey.
- Allocation JSON records input checksums, config hash, code commit.
- Test: running the same date twice gives identical files and no duplicate rows.

### WP7 Limits (M3) — 2 h (after D-c)
- Enforce `max_turnover_rebalance` (0.35) and `max_position_weight` (0.05) as checks that block the order file unless a waiver is recorded in the allocation JSON.
- Test: a 0.54 turnover case is blocked or waived explicitly.

### WP8 Tests and CI (M6) — 4 h, parallel with everything
- Golden parity test for `b5_only` (the 18-date set, 1e-6), beta band tests, projection tests, sizing tests, idempotency tests, staleness tests.
- Artifact-gated tests get a CI job that has the artifacts, or are listed as not run.

### WP9 Corrections and hygiene (M4, m1, m2, m3, m5) — 2 h
- Correct the tracker section 2 reference table (22-23%, 21.3%, static 50/72% not reproduced; state the explanation found in the audit).
- `log_paper_fills` docstring (open vs adj_close).
- NYSE holiday calendar in `run_j2_backfill.py:38` (`pd.bdate_range` runs on holidays).
- Align cost (m1) per D-b.
- Restore or correct the missing doc references.

### WP10 Monitoring and scheduling (M7) — 4 h
- Schedule the daily ops job; alert on any non-zero exit (email or log file that is checked).
- Regenerate the G.3 drift report and G.5 dashboard from current data.

### WP11 Survivorship (M1) — 8-16 h, data-dependent, not on the paper path
- Historical constituents, or quantify the bias on the 2015+ window and disclose.

### Deferred (not in this plan)
- B7 broker executor, reconciliation and kill switch (16-24 h): needed before live only.
- M5 sealed test: owner decision D-d.

## 3. Order and parallelism

```
D-a..D-d (owner)  ───────────────┐
WP1 mode lock ──┐                │
WP2 staleness ──┼─> WP5 gate ────┼─> WP4 overlay (after D-a) ─┐
WP3 sizing ─────┤                │                             ├─> paper-trading go/no-go
WP6 idempotency ┘                │                             │
WP8 tests (throughout) ──────────┴─> WP7 limits (after D-c) ───┘
WP9 corrections, WP10 monitoring: any time
```

Parallel now: WP1, WP2, WP3, WP6, WP8, WP9, WP10. WP5 follows WP2 and WP3 (it needs the fixed sizing and staleness behaviour to reproduce). WP4 waits on D-a.

Estimated effort: about 30 engineer-hours total for WP1-WP10 (about 1.5 days of wall time with 3 parallel workers). WP11 is extra and data-bound.

## 4. Acceptance criteria (paper-trading go, all required)

1. Mode is `b5_only` and no RL path is reachable from daily ops (test).
2. Overlay decision recorded; parity test on 18 dates passes at 1e-6 for the chosen design.
3. Staleness gate: stale snapshot or price date mismatch exits non-zero with no orders (tests).
4. Sizing on current NAV: notional error < 1% on the 2x synthetic case.
5. Two runs on the same date give identical files and no duplicate rows.
6. Refresh failure: non-zero exit, no orders.
7. Gate re-issued on HEAD (PASS, or owner-accepted FAIL with reason).
8. Turnover limit enforced or waived per date with a record.
9. Daily ops scheduled; a failure alerts.
10. CI runs the new tests; artifact-gated tests are listed as not run if skipped.

Live go additionally needs B7, M1 addressed or quantified, 20 paper days with zero reconciliation breaks, a tested kill switch, and the owner's sealed-test result.

## 5. Risks

- Restoring the overlay (D-a i) lowers the 2008-2026 return and raises gross; the gate may then fail on Sharpe. That is a result to report, not a reason to change thresholds.
- Current NAV sizing changes historical replay numbers; the journal replay must be re-baselined and not compared to the old journal without a note.
- The sealed window must not be used to choose any fix.
- Survivorship may be large; the paper gates do not measure it.
