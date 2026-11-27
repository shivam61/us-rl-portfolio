# A0 timing convention (PortfolioEnvV2, committed equity-only code)

Verified by `tests/test_a0_timing.py` (5 pass) and by reading `src/rl/environment_v2.py`.

| Event | Convention in code | Spec (`docs/phases/rl_feature_certification.md`, M2/M8) |
|---|---|---|
| Observation for decision t | prices and stress with date <= t (close t); B.5 snapshot with date <= t | same ("decision at close t uses data through t") |
| Action taken | weights set at close t (`_current_weights` after `step`) | "orders executed t+1" |
| Returns earned by the action | days in (t, next_decision], first return = close(t+1)/close(t) | t+1 execution means first return = close(t+2)/close(t+1) |
| Reward at step t | uses the returns of the same period (t, next] | not specified |
| Next observation | built at next decision date; carries the action just taken (obs[36], obs[38], obs[39:42]) | n/a |
| Last decision | weights set, but next_date = current_date, so the last period is never simulated (NAV ends at last decision date) | M8: "last decision's period handled explicitly" (not done) |
| Transaction cost | `cost_bps` applied to the first return of the period, scaled by turnover | n/a |
| Cost in training | 0 bps (`make_env_fn` and `val_env` do not pass cost_bps; default 0.0) | eval/prod 10 bps |
| Cost in evaluation | 10 bps (C1 eval, H2/W1 checkpoint checks in this audit) | 10 bps |
| B.5 snapshot between control dates | snapshot changes only on the 120 control dates; 14d decisions reuse the latest control-date book | prod uses 14d rebalances |

## Places the env differs from the spec
1. Fill timing: env = fill at close t (zero-delay). Spec = t+1. Numerically verified; H1 showed a 1-step delay removes the 14d signal, so this matters.
2. Last period: not simulated (silently dropped). Spec requires explicit handling.
3. Costs: 0 bps in training and validation, 10 bps in eval. Training is cost-free, so the agent never sees turnover cost in the reward path that matters for eval.
4. 14d grid start: the first 14d decision (2008-01-02) precedes the first B.5 snapshot (2008-01-07), so the book is empty and holdings are 0 while equity_frac is reported (defect D4, see report).
5. VIX close is same-day (spec M2 requires lagged availability); recorded in the FC track, not re-tested here.
