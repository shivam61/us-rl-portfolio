# Production Intraperiod Overlay

- Baseline: `baseline_v1_volatility_score_sp100`
- Production variant: `baseline_v1_intraperiod_overlay_sp100`
- Alpha rankings unchanged
- Optimizer unchanged
- RL disabled
- Signal timing: SPY/VIX shock is measured at prior close and executed at the next trading day's open.
- Execution mechanics: target stock weights are scaled to 60% while overlay is active; residual remains cash.

## Comparison

| variant                        |   cagr |   sharpe |   max_dd |   dd_2020 |   dd_2022 |   overlay_events |   avg_cash_exposure |   total_cost |   trade_count |
|:-------------------------------|-------:|---------:|---------:|----------:|----------:|-----------------:|--------------------:|-------------:|--------------:|
| baseline_v1                    | 0.1730 |   0.9169 |  -0.3706 |   -0.3706 |   -0.3365 |                0 |              0.1070 |   29516.7396 |          5769 |
| production_intraperiod_overlay | 0.1625 |   0.8943 |  -0.3461 |   -0.3318 |   -0.3461 |              126 |              0.1145 |   37487.3880 |          8237 |

## Hedge Timing

- First production overlay event lag vs 2020 crash start: `6` days
- First production overlay event lag vs 2022 drawdown start: `42` days

## Success Criteria

| variant                        | maxdd_lt_32pct   | cagr_gt_16pct   | sharpe_ge_0_9   | dd_2020_reduces   | all_pass   |
|:-------------------------------|:-----------------|:----------------|:----------------|:------------------|:-----------|
| baseline_v1                    | False            | True            | True            | True              | False      |
| production_intraperiod_overlay | False            | True            | False           | True              | False      |

## Interpretation

- Production intraperiod overlay does not pass the full current gate.
- MaxDD changed from `-37.06%` to `-34.61%`, while Sharpe changed from `0.917` to `0.894`.
- Trade count increased from `5769` to `8237` and total costs increased from `$29,517` to `$37,487`.
- Main failure mode: the one-day trigger enters and exits frequently, so execution friction erodes much of the post-hoc overlay benefit.
- Recommended next test: add hysteresis/min-hold rules or implement the overlay as a SPY hedge sleeve instead of repeatedly scaling the entire stock book.
- This run uses actual simulator rebalances, cash, transaction costs, and slippage; it is no longer a post-hoc NAV multiplier.
