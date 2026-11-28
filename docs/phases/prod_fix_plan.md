# Fix plan: production blockers for the B.5 + B.4 book (rev 3, after three EGM reviews)

Status: PLAN (2026-11-28), not executed. Source: `docs/phases/prod_readiness_audit.md` (defect IDs B1-B7, M1-M9, m1-m5). Scope: the deterministic B.5 stock book with the B.4 risk engine, equity and cash only. The RL allocator stays in shadow mode (`docs/phases/rl_shadow_mode.md`, branch `consolidate/rl-fixes`).

Base branch: `exp/no-tlt` for this plan. Each work package (WP) is one branch off `exp/no-tlt` and one PR, merged in the order given in section 3. No parallel edits to the same file (see section 3).

Rev 3 changes (from the readiness review and two design reviews): a new WP0 (clip and mask refresh) goes before everything else; the sealed window is redefined as backtest-only (paper trading already runs inside 2026-05..11); WP1 covers the real RL re-entry paths in the switching engine and daily ops; cost and turnover get one source of truth; D-a has no default and blocks paper go until answered; WP5 runs first as a baseline and again as the acceptance artifact; a preflight module gates every write.

## 0. Goal and non-goals

Goal: paper trading does what the owner-approved spec says, fails closed before any write, sizes on current NAV, uses one cost and one turnover setting everywhere, and has tests that would catch the audit's findings.

Non-goals:
- Changing B.5 stock picks (frozen).
- Any change to RL training, the reward or the RL env. RL is shadow-only.
- Using the sealed backtest window 2026-05..11 to choose or tune any fix. Paper trading data inside that window is live operation, not a backtest; the M5 sealed test is a separate hashed artifact run once on frozen code.
- Broker integration (B7), survivorship quantification (M1), dashboard regeneration: separate tickets.

## 1. Owner decisions

| ID | Decision | Options | Default |
|---|---|---|---|
| D-a | SPY overlay (B2) | (i) restore as explicit SPY weight to the beta floor (holdout 16.3% / -27%); (ii) amend the B.4 spec to equity plus cash, accept beta below 0.50 on some dates | **None. Paper go is blocked until answered.** Nothing is decided on silence (a spec amendment is a governance change). |
| D-b | Cost assumption | 10 bps (backtest gate) or 20 bps (paper config) | 20 bps in sizing and the paper config; the gate is re-reported at 10 and 20 bps |
| D-c | Turnover breach behaviour (M3) | (a) skip the rebalance and hold; (b) scale the trade down to the limit; (c) waiver record | (a) skip and hold, logged in the allocation JSON; waiver needs a named key |
| D-d | Sealed test (M5) | run once on frozen code now, or after paper gates | after paper gates |
| D-e | Scheduler and alert channel (WP10) | launchd or cron on this host, plus email or a checked log file | launchd, alert by log file checked each morning |
| D-f | Holiday calendar (WP9) | `src/data/calendar.py` (confirm NYSE) or a new dependency | `src/data/calendar.py` if it is NYSE; otherwise owner picks |
| D-g | NAV source for sizing (WP3) | fill-based MTM from the ledger (`compute_mtm_nav`) or close-based MTM from positions | close-based at `as_of`, with the ledger cash term; the formula is in WP3 |
| D-h | Survivorship data source (M1, out of plan) | constituent history file | owner picks; not needed for paper |
| D-i | Mode of record | the journey state file is the mode of record | state file, with daily ops refusing any mode other than `b5_only` |

WP0, WP1, WP2, WP5 (baseline), WP6, WP9 and WP10 do not depend on D-a to D-i and can start now.

## 2. Work packages

### WP0 Clip and mask refresh (B4) — 4-6 h, first
Why first: `recommended_end_for_universe` returns 2026-04-24 for `sp500_dynamic` (`artifacts/reports/phase_b0_data_window_guard.csv`), so `run_prod_signal.py:409-426` builds B.5 weights only to that date and `_b5_weights_at` (`run_prod_signal.py:192-196`) returns April weights for a November `as_of`. A fail-closed rule (WP2) would trip every day until this is fixed.
- Split the live path from the research clip: the research clip `clipped_evaluation_dates` (`scripts/run_phase_b1_simulator_reproduction.py:90`, called at `scripts/run_phase_b3_exposure_control.py:216`) stays for the gate. Live reads the mask built by `scripts/build_pit_universe.py` refreshed through the last available date.
- Any change to the clip changes the gate numbers, so WP0 ends with a gate re-run (see WP5).
- Tests: `test_live_snapshot_reaches_as_of`, `test_research_clip_unchanged_for_gate` (golden on the gate's clip dates).

### WP1 Mode lock (B1, M8, M9) — 3 h
Files: `scripts/run_prod_signal.py`, `scripts/run_daily_paper_ops.py`, `src/rl/switching_rule.py`, `config/paper_trading_j2.yaml`, `tests/test_mode_lock.py`.
- Daily ops passes no `--mode` (`run_daily_paper_ops.py:170-177`), so today it defaults to `rl_e7` (`run_prod_signal.py:392`). Fix the default to `b5_only`.
- `SwitchingRuleEngine.evaluate` can return `rl_e7` from `b5_only` (`src/rl/switching_rule.py:113, 276-303`). For prod, the engine may not return `rl_e7`.
- `--mode-override` (`run_prod_signal.py:393`) and `model_path` (`run_daily_paper_ops.py:171-172`, `config/paper_trading_j2.yaml:38` `rl_mode_required`) are rejected in daily ops.
- `--initial` (`run_daily_paper_ops.py:146, 173-174, 194-195`) maps to `--init-journey` explicitly; cold start only with that flag.
- Hard-coded switching references (`run_prod_signal.py:468-469`) read from a JSON gate output (WP5 writes it).
- Tests: `test_argparse_rejects_rl_mode`, `test_engine_never_returns_rl_in_prod`, `test_daily_ops_rejects_model_path`, `test_missing_state_fails`.

### WP2 Fail-closed data and preflight (B6, m4) — 4 h
Files: `src/paper/preflight.py` (new), `scripts/run_daily_paper_ops.py`, `scripts/compute_paper_orders.py`, `scripts/run_prod_signal.py`, `tests/test_preflight.py`.
- New `preflight.py` returns `{data_ok, mode_ok, snapshot_ok, prices_ok}`. Every write (signal, orders, fills, experience log) is gated on it. This removes the collision between work packages on `run_daily_paper_ops.py`.
- Today a failed refresh only warns (`run_daily_paper_ops.py:162-164`); orders still run because the check at `:192` looks only at `signal_ok`; the exit at `:272-276` comes after fills (`:205`) and the experience log (`:231`) have written. The fix exits before any write.
- `load_close_prices` (`compute_paper_orders.py:75-112`): require the price date to equal the signal date; drop fallback 2 (`:93-110`, a mixed-date Series) on the live path; return `(date, series)`.
- Missing price for a held or targeted name on the live path fails the run (today `:161-163` silently keeps the position with no sell).
- Fail-open defaults on the live path: stress defaults to 0.0 (`run_prod_signal.py:222`); `spy_ret_63` set to 0.0 on short history (`:230`); `fillna(0.0)` makes a missing B.5 name zero weight (`:196`). Each becomes an explicit failure.
- Research `fillna(0)` paths are unchanged.
- Tests: `test_refresh_failure_writes_nothing`, `test_stale_snapshot_rejected`, `test_price_date_must_match_signal`, `test_missing_price_fails_live`, `test_stress_default_fails_live`.

### WP3 Sizing on current NAV (B5) — 2 h
Files: `scripts/compute_paper_orders.py` (lines 133, 172), `tests/test_sizing_nav.py`.
- NAV at `as_of` (D-g default): shares held x `adj_close` at `as_of` plus the ledger cash. Do not reuse `compute_mtm_nav` (`scripts/log_paper_fills.py:263`) without checking: its comments say the cash term is untrusted. The formula and the ledger cash source are written into the test fixture.
- Fallback to `initial_nav` only when no positions exist (T=0).
- Tests: 2x-NAV synthetic case has notional error < 1%; 0.5x case; T=0 fallback; cash term matches the ledger.

### WP4 Overlay (B2) — blocked on D-a
Files depend on the option.
- D-a (ii): amend the B.4 spec (file to be named by the owner: the spec file must be confirmed first; the audit does not name it); add daily beta and a flag for dates below 0.50 to the allocation JSON. No change to book weights.
- D-a (i): the overlay drop is in `scripts/run_phase_b5_final_gate.py:166-168`, after the beta constraint at `:158-165`. Edit `build_promoted_weights` there, so the gate and prod share the path (`run_prod_signal.py:423` already imports it). Add an explicit SPY weight to the beta floor. Golden test: the 18 holdout dates listed in `tests/fixtures/b5_parity_dates.json` (to be created from the audit's list; the audit's `q2_parity.py` exists only in worktree `agent-a8bc72d751b8f1e00/runs_pa/`), tolerance 1e-6.
- Delete the dead `rl_e7` branch in `run_prod_signal.py:313-334` in either option. Do not claim RL parity from this.
- Note: `finalize_b4_weights` does not exist; no shared finalize function is planned.

### WP5 Gate reproduction (B3) — 1 h twice
Files: `scripts/run_phase_b5_final_gate.py`, `artifacts/reports/phase_b5_final_gate.md`, `artifacts/reports/phase_b5_final_gate.json` (new, read by WP1).
- Run 1 (now, pre-fix baseline): run the gate on current HEAD to record the reproduction status (the 9.24% / 0.78 finding).
- Run 2 (acceptance artifact): after WP0 and WP4. The gate imports neither the paper-order nor the staleness code (imports at `run_phase_b5_final_gate.py:16-49`), but it does depend on the clip (WP0) and the overlay (WP4), so it must follow them.
- Report the gate at 10 and 20 bps (D-b).
- Outcome: owner-accepted FAIL or PASS. Record the owner's acceptance at `docs/phases/prod_gate_acceptance.md`. Thresholds are not edited.

### WP6 Idempotency (M2) — 2 h
Files: `src/rl/audit_trail.py` (`append_decision`, lines 45-70), `scripts/log_paper_fills.py` (`append_slippage_summary`, line 252), `tests/test_idempotency.py`.
- Rows get a `journey` column (today they have none). Upsert key: (journey, as_of). Skip if the day's output exists. No file lock: one daily job.
- Allocation JSON records the config hash and the code commit.
- Test: a dual run on one `as_of` gives identical files and no duplicate rows.

### WP7 Cost and turnover, one source of truth (m1, M3) — 2 h, after D-b and D-c
Files: `config/paper_trading.yaml`, `config/base.yaml`, `scripts/compute_paper_orders.py`, `tests/test_cost_config.py`.
- Today: cost is 20 bps in `config/paper_trading.yaml:26`, 5 bps in `config/base.yaml:29`, and 10 bps in the gate (`run_phase_b2_turnover_control.py:44`). Turnover is 0.30 in `config/base.yaml:32` and 0.35 in `config/paper_trading.yaml:32`.
- One cost key and one turnover key in one config, read by backtest, gate and prod. Sizing applies the cost reserve only if D-b says so.
- Turnover breach behaviour per D-c. "Rebalance day" for `b5_only` is defined from the B.2 `every_2_rebalances` schedule, not from the RL cadence (`run_prod_signal.py:213-215`).
- Position cap (0.05) enforced as a check.
- Tests: `test_single_cost_key`, `test_turnover_breach_skips_and_logs`, `test_position_cap`.

### WP9 Corrections (M4, m1, m2, m3, m5) — 1-2 h
- Correct the tracker section 2 reference table (22-23%, 21.3%, static 50/72% not reproduced; state the audit's explanation).
- Holiday fix in `scripts/run_j2_backfill.py:38` (`pd.bdate_range`): use `src/data/calendar.py` if D-f confirms NYSE.
- `log_paper_fills` docstring (open vs adj_close) fixed.
- Restore or correct the references to `rl_shadow_mode.md` and `rl_consolidation_notes.md` (they live on `consolidate/rl-fixes`).

### WP10 Scheduling and alert (M7) — 1 h, D-e
- Schedule the daily ops job via the chosen scheduler; any non-zero exit writes to the alert log, which is checked each morning.
- Dashboard and drift-report regeneration are not paper gates and are removed from this plan.

### Out of plan (separate tickets)
- M1 survivorship: one disclosure line in the gate report now (WP5); constituent data later (D-h), 8-16 h, required before live.
- B7 broker executor, reconciliation and kill switch (16-24 h): before live only.
- M5 sealed test (D-d): frozen code, one run, hashed artifact.

## 3. Order and parallelism

Sequential core: WP0 -> WP5 (run 2 later) -> WP4 (after D-a) -> WP5 run 2 -> paper go.

```
WP0 clip/mask  ──> WP5 run1 (baseline, now)
WP1 mode lock  ──┐
WP2 preflight  ──┼─> WP3 NAV sizing ─> WP7 limits (after D-b, D-c)
WP6 idempotency ─┘
WP4 overlay (after D-a) ──> WP5 run2 (acceptance) ──> paper go
WP9 corrections, WP10 scheduling (after D-e): any time
```

File ownership to avoid collisions: `scripts/run_daily_paper_ops.py` is edited by WP1, WP2, WP6 and WP10 in that order, one PR each. `scripts/compute_paper_orders.py` is edited by WP2, WP3 and WP7 in that order.

Parallel now: WP0, WP1, WP2 (preflight only), WP6, WP9, WP10.

Estimated effort: about 25 engineer-hours for WP0-WP10 (earlier 17-20 h estimate omitted WP0 and the cost/turnover work). Roughly 2 days of wall time with three workers, mostly serialised on the shared files above.

## 4. Acceptance criteria (paper-trading go, all required)

1. Daily ops cannot reach any RL mode, `--mode-override`, or `model_path` (WP1 tests).
2. The live snapshot reaches `as_of` on the current date (WP0 test).
3. Preflight fails before any write when data, mode, snapshot or prices are not OK (WP2 tests).
4. Sizing on current NAV: notional error < 1% on the 2x synthetic case (WP3).
5. Two runs on the same date give identical files and no duplicate rows (WP6).
6. One cost key and one turnover key, read by backtest, gate and prod (WP7).
7. Overlay decision D-a recorded by the owner. If (i), the 18-date golden parity test passes at 1e-6.
8. Gate run 2 on the fixed code, reported at 10 and 20 bps, with owner acceptance recorded (WP5).
9. Daily ops scheduled with D-e; a non-zero exit writes to the alert log (WP10).
10. CI runs the new tests; artifact-gated tests are listed as not run when skipped.
11. Survivorship disclosed in the gate report (one line).

Live go additionally needs B7, D-h constituent data, 20 paper days with zero reconciliation breaks, a tested kill switch, and the owner's sealed-test result (D-d).

## 5. Risks

- Restoring the overlay (D-a i) lowers the 2008-2026 return and raises gross; the gate may then fail on Sharpe. That is a result to report, not a reason to change thresholds.
- Current-NAV sizing and the WP0 clip change historical replay numbers; the journal replay must be re-baselined and compared to the old journal only with a note.
- Paper data already exists inside 2026-05..11. Any backtest using that window is contaminated by paper decisions and cannot serve as the sealed test. The sealed test needs a clean cut that is set now and frozen.
- Survivorship may be large; the paper gates do not measure it.

## 6. Review log

- Simplicity review (egm-zoom-out, 2026-11-28): cuts applied in rev 2.
- Readiness review (egm-implementation-readiness, 2026-11-28, first pass): file lists, decisions D-e to D-i, a single base branch, the missing flags and function names. Applied in rev 3.
- Second readiness review (2026-11-28): found the WP0 blocker (clip stops at 2026-04-24), the sealed-window conflict with live paper trading, the RL re-entry paths in the switching engine, three cost sources, the D-a default on silence, the WP5 dependency inversion, and the file collisions. Applied in rev 3.
- Design review (egm-design, 2026-11-28, first run): ran before the audit file was on the branch and could not verify audit IDs. Its code-level findings (items 2-13) were checked and applied in rev 3. A re-run against the audit is still open.
