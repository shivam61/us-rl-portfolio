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
| D-e | Scheduler and alert channel (WP10) | launchd or cron on this host, plus email or push | launchd; alert by email (push if available). A log file nobody reads is not an alert. |
| D-f | Holiday calendar (WP9) | `src/data/calendar.py` (confirm NYSE) or a new dependency | `src/data/calendar.py` if it is NYSE; otherwise owner picks |
| D-g | NAV source for sizing (WP3) | fill-based MTM from the ledger (`compute_mtm_nav`) or close-based MTM from positions | close-based at `as_of`, with the ledger cash term; the formula is in WP3 |
| D-h | Survivorship data source (M1, out of plan) | constituent history file | owner picks; not needed for paper |
| D-i | Mode of record | the journey state file is the mode of record | state file, with daily ops refusing any mode other than `b5_only` |

WP0, WP1, WP2, WP5 (baseline), WP6, WP9 and WP10 do not depend on D-a to D-i and can start now.

## 2. Work packages

### WP0 Clip and mask refresh (B4) — 4-6 h, first
Why first: `recommended_end_for_universe` returns 2026-04-24 for `sp500_dynamic` (`artifacts/reports/phase_b0_data_window_guard.csv`), so `run_prod_signal.py:409-426` builds B.5 weights only to that date and `_b5_weights_at` (`run_prod_signal.py:192-196`) returns April weights for a November `as_of`. A fail-closed rule (WP2) would trip every day until this is fixed.
- Split the live path from the research clip: the research clip `clipped_evaluation_dates` (`scripts/run_phase_b1_simulator_reproduction.py:90`, called at `scripts/run_phase_b3_exposure_control.py:216`) stays for the gate. Live reads the mask built by `scripts/build_pit_universe.py` refreshed through the last available date.
- Interface: add `live_end: Timestamp | None` to `build_promoted_weights` (`scripts/run_phase_b5_final_gate.py:137`) and `build_b2_candidate` (`scripts/run_phase_b3_exposure_control.py:215`, which calls `clipped_evaluation_dates` at :216). `scripts/run_prod_signal.py:424` passes `as_of`; the gate passes `validation_end` unchanged.
- Re-run the gate only if `clipped_evaluation_dates` (`scripts/run_phase_b1_simulator_reproduction.py:90`) itself changes. The `live_end` path alone does not change gate numbers.
- Tests: `test_live_snapshot_reaches_as_of`, `test_research_clip_unchanged_for_gate` (golden on the gate's clip dates).
- Mask regeneration command: `python scripts/build_pit_universe.py --config config/universes/sp500.yaml --output data/artifacts/universe_mask_sp500.parquet --cache-dir data` (arguments checked against `scripts/build_pit_universe.py:83-87`). Whether it extends past 2026-04-24 depends on the cache, to be confirmed on the first run.

### WP1 Mode lock (B1, M8, M9) — 3 h
Files: `scripts/run_prod_signal.py`, `scripts/run_daily_paper_ops.py`, `src/rl/switching_rule.py`, `config/paper_trading_j2.yaml`, `tests/test_mode_lock.py`.
- Daily ops passes no `--mode` (`run_daily_paper_ops.py:170-177`), so today it defaults to `rl_e7` (`run_prod_signal.py:392`). Fix the default to `b5_only`.
- argparse choices (`run_prod_signal.py:392-393`) become `choices=["b5_only"]`; `--mode-override` is removed from the prod entry point.
- `config/paper_trading_j2.yaml:38` `rl_mode_required: true` cannot pass in `b5_only`. Decide and record: set it to `false` in the live journey config, with the reason in the commit message.
- Hard-coded switching references read the gate JSON from WP5 run 2. Until then, WP1 uses a constant `b5_only`; the JSON schema is `{"mode": "b5_only", "gate": "<name>", "cost_bps": <number>}`.
- `SwitchingRuleEngine.evaluate` can return `rl_e7` from `b5_only` (`src/rl/switching_rule.py:113, 276-303`). For prod, the engine may not return `rl_e7`.
- `--mode-override` (`run_prod_signal.py:393`) and `model_path` (`run_daily_paper_ops.py:171-172`, `config/paper_trading_j2.yaml:38` `rl_mode_required`) are rejected in daily ops.
- Cold start stays on the existing `--initial` flag (`run_daily_paper_ops.py:146, 173-174, 194-195`). Do not add `--init-journey`; it would duplicate `--initial`.
- Hard-coded switching references (`run_prod_signal.py:468-469`) read from the WP5 gate JSON (see above).
- Tests: `test_argparse_rejects_rl_mode`, `test_engine_never_returns_rl_in_prod`, `test_daily_ops_rejects_model_path`, `test_missing_state_fails`.

### WP2 Fail-closed data and preflight (B6, m4) — 4 h, after WP0
Files: `src/paper/preflight.py` (new), `scripts/run_daily_paper_ops.py`, `scripts/compute_paper_orders.py`, `scripts/run_prod_signal.py`, `tests/test_preflight.py`.
- New `preflight.py` returns `{data_ok, mode_ok, snapshot_ok, prices_ok}`. Every write (signal, orders, fills, experience log) is gated on it. This removes the collision between work packages on `run_daily_paper_ops.py`.
- Today a failed refresh only warns (`run_daily_paper_ops.py:162-164`); orders still run because the check at `:192` looks only at `signal_ok`; the exit at `:272-276` comes after fills (`:205`) and the experience log (`:231`) have written. The fix exits before any write.
- `scripts/refresh_market_data.py:115,121` only warn on a per-ticker fetch failure; the script exits 1 only on feature rebuild (`:201-202`). Add a non-zero exit when a held or targeted ticker's fetch fails.
- `load_close_prices` (`compute_paper_orders.py:75-112`): require the price date to equal the signal date; drop fallback 2 (`:93-110`, a mixed-date Series) on the live path; return `(date, series)`.
- Missing price for a held or targeted name on the live path fails the run (today `:161-163` silently keeps the position with no sell).
- Fail-open defaults on the live path: stress defaults to 0.0 (`run_prod_signal.py:222`); `spy_ret_63` set to 0.0 on short history (`:230`); `fillna(0.0)` makes a missing B.5 name zero weight (`:196`). Each becomes an explicit failure.
- Research `fillna(0)` paths are unchanged.
- Tests: `test_refresh_failure_writes_nothing`, `test_stale_snapshot_rejected`, `test_price_date_must_match_signal`, `test_missing_price_fails_live`, `test_stress_default_fails_live`.

### WP3 Sizing on current NAV (B5) — 2 h
Files: `scripts/compute_paper_orders.py` (lines 133, 172), `tests/test_sizing_nav.py`.
- NAV at `as_of` (D-g default): shares held x `adj_close` at `as_of` plus the ledger cash. Do not reuse `compute_mtm_nav` (`scripts/log_paper_fills.py:263`) without checking: its comments say the cash term is untrusted. The formula and the ledger cash source are written into the test fixture.
- Formula: NAV(as_of) = sum over non-cash rows of `positions_latest.parquet` of shares_held x `adj_close` at `as_of`, plus cash.
- Cash must NOT come from the `__CASH__` row's market_value. That value is initial_nav minus invested at signal prices (`scripts/log_paper_fills.py:284-310`), which the file itself calls untrusted. Cash is derived from the fill ledger: initial cash minus cumulative net buy notionals plus sell proceeds, as the comment at `scripts/log_paper_fills.py:288-289` describes. Test: cash from the ledger equals the sum of fills to the cent on a fixture. Do not reuse `compute_mtm_nav` as-is.
- Fallback to `initial_nav` only on the explicit `--initial` cold start (`scripts/compute_paper_orders.py:150`).
- Tests: 2x-NAV synthetic case has notional error < 1%; 0.5x case; T=0 fallback; cash term matches the ledger.

### WP4 Overlay (B2) — blocked on D-a
Files depend on the option.
- D-a (ii): amend the B.4 spec (the audit does not name it; the B.4 spec is `docs/phases/phase_b.md`, section "Phase B.4 — Risk Engine Formalization", line 241; owner to confirm); add daily beta and a flag for dates below 0.50 to the allocation JSON. No change to book weights.
- Tests in both options: `test_beta_band_flags_below_0_50` and `test_project_weights_in_band` (`scripts/run_phase_b3_exposure_control.py:109-145`). The audit lists no beta-band test (M6).
- D-a (i): the overlay drop is in `scripts/run_phase_b5_final_gate.py:166-168`, after the beta constraint at `:158-165`. Edit `build_promoted_weights` there, so the gate and prod share the path (`run_prod_signal.py:423` already imports it). Add an explicit SPY weight to the beta floor. Golden test: copy the fixed dates and the seeded control draw from `runs_pa/q2_parity.py:27-32` (worktree `agent-a8bc72d751b8f1e00`, not on any branch) into `tests/fixtures/b5_parity_dates.json`, record the seed in the fixture, tolerance 1e-6. The audit gives only counts (12 fixed, 6 control), not the dates.
- Delete the dead `rl_e7` branch in `run_prod_signal.py:313-334` in either option. Do not claim RL parity from this.
- Note: `finalize_b4_weights` does not exist; no shared finalize function is planned.

### WP5 Gate reproduction (B3) — 1 h twice
Files: `scripts/run_phase_b5_final_gate.py`, `artifacts/reports/phase_b5_final_gate.md`, `artifacts/reports/phase_b5_final_gate.json` (new, read by WP1).
- Run 1 (now, pre-fix baseline): run the gate on current HEAD to record the reproduction status (the 9.24% / 0.78 finding).
- Root cause to record: commit 860fa26 added the `NON_TRADABLE_ASSETS` strip at `scripts/run_phase_b5_final_gate.py:168`, turning the sleeves into cash (9.24% CAGR full period, Sharpe 0.78).
- Cost: 20 bps is not in the gate's cost table (`artifacts/reports/phase_b5_final_gate.md:37-41` shows 10 / 25 / 50). Add a 20 bps row in run 2.
- Run 2 (acceptance artifact): after WP0 and WP4. The gate imports neither the paper-order nor the staleness code (imports at `run_phase_b5_final_gate.py:16-49`), but it does depend on the clip (WP0) and the overlay (WP4), so it must follow them.
- Report the gate at 10 and 20 bps (D-b).
- Outcome: owner-accepted FAIL or PASS. Record the owner's acceptance at `docs/phases/prod_gate_acceptance.md`. Thresholds are not edited.

### WP6 Idempotency (M2) — 2 h
Files: `src/rl/audit_trail.py` (row building at 45-70; the write at 92-98), `scripts/log_paper_fills.py` (`append_slippage_summary`, line 252), `tests/test_idempotency.py`.
- Rows get a `journey` column (today they have none). Upsert key: (journey, as_of). Skip if the day's output exists.
- Migration: existing rows without a `journey` column are backed up, then tagged `journey = 'j2'` once.
- Deviation from the audit's M2 wording: no file lock, because this is one daily job. Recorded in section 6.
- Allocation JSON records the config hash and the code commit.
- Test: a dual run on one `as_of` gives identical files and no duplicate rows.

### WP7 Cost and turnover, one source of truth (m1, M3) — 2 h, after D-b and D-c
Files: `config/paper_trading_j2.yaml` (live journey config), `config/paper_trading.yaml`, `config/base.yaml`, `scripts/compute_paper_orders.py`, `tests/test_cost_config.py`. Covers m1.
- Today: cost is 20 bps in `config/paper_trading.yaml:26`, 5 bps in `config/base.yaml:29`, and 10 bps in the gate (`run_phase_b2_turnover_control.py:44`). Turnover is 0.30 in `config/base.yaml:32` and 0.35 in `config/paper_trading.yaml:32`.
- One cost key and one turnover key in one config, read by backtest, gate and prod. Sizing applies the 20 bps reserve per the D-b default.
- Turnover breach behaviour per D-c. "Rebalance day" for `b5_only` is defined from the B.2 `every_2_rebalances` schedule, not from the RL cadence (`run_prod_signal.py:213-215`).
- Position cap (0.05) enforced as a check.
- Tests: `test_single_cost_key`, `test_turnover_breach_skips_and_logs`, `test_position_cap`.

### WP9 Corrections (M4, m1, m2, m3, m5) — 1-2 h
- Correct the tracker section 2 reference table (22-23%, 21.3%, static 50/72% not reproduced; state the audit's explanation).
- Holiday fix in `scripts/run_j2_backfill.py:38` (`pd.bdate_range`): use `src/data/calendar.py` if D-f confirms NYSE.
- `log_paper_fills` docstring fixed at `scripts/log_paper_fills.py:3, 29, 85-88` (says open; code uses adj_close).
- The audit's m5 says the tracker has "no sec. 12 or 23". The tracker does have those headings (`docs/phases/rl_allocator_experiments.md`); correct the audit's reference, not the tracker.
- `rl_shadow_mode.md` and `rl_consolidation_notes.md` are on `consolidate/rl-fixes`, not on `exp/no-tlt`. Merge PR #2 or cite the branch path.

### WP10 Scheduling and alert (M7) — 1 h, D-e
- Schedule the daily ops job via the chosen scheduler; any non-zero exit writes to the alert log, which is checked each morning.
- Dashboard and drift-report regeneration are not paper gates and are removed from this plan.

### Out of plan (separate tickets)
- M1 survivorship: one disclosure line in the gate report now (WP5); constituent data later (D-h), 8-16 h, required before live.
- B7 broker executor, reconciliation and kill switch (16-24 h): before live only.
- M5 sealed test (D-d): frozen code, one run, hashed artifact.

## 3. Order and parallelism

Dependencies: WP5 run 1 has no dependencies and runs now. WP2 waits for WP0 (its snapshot check trips until WP0 lands). WP1 uses a constant `b5_only` until WP5 run 2 writes the gate JSON. WP5 run 2 waits for WP0 and WP4.

```
WP5 run1 (baseline, now)
WP0 clip/mask ──> WP2 preflight ──┐
WP1 mode lock (constant until WP5 run2 JSON) ──┤
WP6 idempotency ─────────────────┼─> WP3 NAV sizing ─> WP7 limits (after D-b, D-c)
WP4 overlay (after D-a) ──> WP5 run2 (acceptance, reads JSON) ──> paper go
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
- Design review (egm-design, 2026-11-28, first run): ran before the audit file was on the branch and could not verify audit IDs. Its code-level findings (items 2-13) were checked and applied in rev 3.
- Rev 3 review (2026-11-28): all audit IDs confirmed. Applied in rev 4: explicit NAV formula; `live_end` interface for WP0; WP5 run 1 and WP1 ordering; WP0 re-run condition; 18 dates sourced from `q2_parity.py:27-32` (the audit gives counts only); 860fa26 root cause restored in WP5; `choices=["b5_only"]` and `rl_mode_required` decision in WP1; beta-band tests in WP4; refresh fetch failure in WP2; cost wording in WP7; `--initial` kept, no `--init-journey`; docstring locations in WP9; D-e alert by email or push.
- Deviations from the audit, recorded: WP6 drops the file lock (audit M2 wording); the B.4 spec file is not named by the audit and must be identified before D-a (ii).
- Rev 4 spot check (2026-11-28, by main agent): line references for WP0-WP6 and WP9 confirmed against code. Corrected: the WP3 cash source (the `__CASH__` row is the untrusted value, not a fallback); the `build_b2_candidate` line (215, not 216); the B.4 spec file (`phase_b.md`, line 241); the mask regeneration command. Still not verified: whether the mask extends past 2026-04-24 on a fresh run; `consolidate/rl-fixes` file contents for the rev 4 paths.
