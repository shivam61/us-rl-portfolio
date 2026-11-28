# Next steps plan (2026-11-28)

Status: PLAN, not executed. Supersedes nothing; companion to `prod_fix_plan.md` (production work packages), `survivorship_data_plan.md` (data) and the tracker `rl_allocator_experiments.md` (section 33 is the latest result).

## 0. Where we are

- Survivorship-reduced picks test (section 33): B.5 vol_top_20, holdout CAGR 19.4% (28.8% with today's constituents), SPY 15.3%; Sharpe 0.43 vs SPY 0.80; max drawdown about -53% vs -29%. Every figure is an upper bound (about 360 truly delisted names have no data; coverage 57% in 2008, 86% in 2020).
- The B.5+B.4 book (picks plus the risk engine and cash layer) was measured earlier at 9.24% CAGR, Sharpe 0.78 on survivor-only data. It has NOT been rerun on the survivorship-reduced universe.
- RL: no variant beat matched static; bandit Gate A not met. RL stays shadow-only and is out of scope below.
- Production: gate fails on current code, committed PASS report is stale, owner decisions D-a to D-i open, four fix branches local and unpushed.

## 1. Gate 0: decide what "ship" means (owner, before any production spend)

The picks alone trail SPY on Sharpe and drawdown. The case for shipping B.5+B.4 must be stated, then tested. Owner picks one:

| Objective | Bar to beat | Reading on current evidence |
|---|---|---|
| Beat SPY on return | CAGR above SPY net of 10 bps costs | picks only, upper bound: yes. B.5+B.4: no (9.2% vs 15%) |
| Beat SPY risk-adjusted | Sharpe and Calmar above SPY | no on picks; B.5+B.4 about equal on Sharpe (0.78 vs 0.80), not shown better |
| Lower drawdown than SPY at acceptable return | MaxDD at least 10 points shallower, CAGR within a stated gap | B.4 aims at this; needs the rerun below |

Output: one paragraph in the tracker stating the objective and the bar. Everything after this is conditional on it.

## 2. Track A: evidence on the real universe (about 3-4 days, no spend)

A1. Wire an experiment universe: config `config/universes/sp500_pit_experiment.yaml` (503 plus Tier A and Tier B tickers), membership mask with usable windows, merged cache path. Production `sp500.yaml` is not touched. Add the missing BK and CTRA prices (still-listed names, yfinance).
A2. Rerun the full B.5+B.4 book (not only the picks) on this universe with costs 10 bps and the 25 and 50 bps sensitivities: CAGR, Sharpe, Calmar, MaxDD, turnover, beta; holdout, 3y window, and 2008-2018. Same harness as the committed gate so the comparison is like for like.
A3. Resolve open data items: JEF identity (Leucadia vs old Jefferies Group), BWA and BBWI spin adjustment, WHR add date, ILMN second stint, membership-file removal dates (use S&P press dates), HP/CE stray stints. Add each as a test or an override row.
A4. Independent price audit on a random 15 of 62 Tier B names using non-Yahoo sources (filings, press-release closes), so the audit claim rests on more than 5 anchors.
Gate A: report B.5+B.4 vs SPY under the Gate 0 bar, with the range (survivor-only, reduced, and the stated gap to full survivorship-free).

## 3. Track B: survivorship-free data decision (owner, in parallel with A)

Free sources are exhausted (yfinance, Stooq, INDmoney, EODHD demo, WIKI mirrors need keys). Choose one:
1. Trial EODHD (cheapest stated delisted support), run the 10-name spot check from `survivorship_data_plan.md` section 5, buy only if it passes.
2. Trial Norgate (Platinum, about USD 630 a year; delisted names and index membership history).
3. Institutional access (WRDS/CRSP or LSEG via a university or employer), if available.
4. Stop at the free result and report the range with the upper-bound label.
If 1-3: about 4-5 working days to pull, validate and rerun (plan section 6). Decision needed: provider and budget cap.

## 4. Track C: production fixes (only after Gate 0 says ship is plausible)

C1. Push the four local branches and open one PR each against `exp/no-tlt`: WP0 live snapshot, WP1 mode lock, WP6 idempotency, WP9 corrections. Review each diff first. Trial merge already passes 27 tests.
C2. Owner decisions D-a to D-i. D-a (overlay) has no default and blocks paper go; list each with a recommended default in one page.
C3. Implement WP2 (fail-closed preflight), WP3 (NAV sizing from fill ledger), WP4 (overlay per D-a), WP7 (limits and cost), WP10 (scheduling), each in its own worktree with tests and an EGM review before merge.
C4. WP5 run 2: regenerate the B.5 gate on fixed code and universe, replace the stale committed PASS report (mark the old one superseded), then paper-trading go or no-go.
Exit: gate passes with zero hand-edited rows, preflight fails closed on stale data, one command runs the daily job idempotently.

## 5. Track D: records and repo hygiene (about 0.5-1 day)

D1. Land the audit and tracker history on `main`: retarget or rebase PR #2 (`consolidate/rl-fixes`) so it includes the docs now on `exp/no-tlt` (tracker sections 30-33, audit, plans). Move section 29 onto `exp/no-tlt`.
D2. Log fixes: a run manifest written by each run script (config, data checksum, seed, commit); a `holdout_used` flag per results row; regenerate the stale B.5 gate report.
D3. Cleanup: delete `data/raw_delisted_QUARANTINED/`, prune the 44 agent worktrees and scratch copies (about 158 MB), untrack `__pycache__` files that show as modified.

## 6. Order and decisions

1. Gate 0 and D3 (now). 2. A1-A2 first, B in parallel (owner decision). 3. A3-A4 while A2 runs. 4. Gate A decides ship vs park. 5. If ship: Track C. 6. D1-D2 any time.

Owner decisions needed now: (a) Gate 0 objective and bar; (b) data provider and budget, or stop at the free result; (c) approve opening PRs for the four production branches; (d) confirm RL stays parked.

## 7. Risks

- The universe-size sensitivity of the vol score (adding names alone moved the holdout by -67 points): all comparisons must use the same universe construction; report ranges, not point estimates.
- The reused 2019-2026 holdout is optimistic; the sealed 2026-05..11 window stays untouched until the one-shot decision.
- Tier B identity rests on SEC records; the audit in A4 is the control.
- A paid source can still fail the spot check; set the cap before buying.
