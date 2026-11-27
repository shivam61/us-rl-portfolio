# RL shadow mode: what to log per rebalance

Status: SPEC (2026-11-27). Scope: a logging contract only. Shadow mode never changes the live allocation.
`scripts/run_prod_signal.py` is NOT modified by this spec; production engineering is a separate task.

## Principle

The live book is B.5 + B.4 (equity-only, the frozen stock book with the stress cap). An RL policy, if
present, runs alongside it and records what it WOULD have done. Nothing it computes is traded, and its
output is never read by the allocation path. The log exists to measure the gap between the shadow target
and the live book, and to make every shadow decision reproducible.

## Fields per rebalance date (one JSON record per decision)

| Field | Type | Definition |
|---|---|---|
| `as_of_date` | date | Decision date t (close t). The record is written after the close, before any fill. |
| `grid` | str | `8w` or `14d` (the rebalance cadence in use). |
| `state_vector` | float[] | The exact observation fed to the policy (dims and names in `OBS_NAMES`/`FEATURE_NAMES`). Stored in full so the decision can be replayed. |
| `state_schema` | str | Name and version of the state builder (e.g. `state_builder_v2`, `features_v4.1`). |
| `raw_action` | float[] | Policy output before the exposure projection (2 dims for the equity-only policy). |
| `equity_target` | float | Equity share after `apply_exposure_mix` and the action map. `None` when no policy is loaded (baseline-only record). |
| `cash_target` | float | `1 - equity_target`. |
| `b5_b4_equity_actual` | float | Equity share the live B.5 + B.4 book holds at this date (sum of absolute stock weights after B.4). |
| `equity_gap` | float | `equity_target - b5_b4_equity_actual`. The number the shadow study is about. |
| `target_weights` | dict | Shadow stock weights after `finalize_equity_only`. Sum equals `equity_target` to 1e-6. |
| `live_weights` | dict | Live B.5 + B.4 weights at the same date, for turnover and overlap comparison. |
| `turnover_shadow` | float | Sum of absolute weight changes versus the shadow book at the previous decision (fill convention per the next section). |
| `turnover_live` | float | Same for the live book. |
| `reward_components` | dict | Per-period reward terms as computed by `compute_reward_v2` (Sharpe term, drawdown penalty, cash drag, churn, recovery), plus the lambdas used (`lambda_dd`, `lambda_cash`, `lambda_churn`). Recorded for the shadow period, not for training. |
| `fill_convention` | str | `close_t` or `close_t+1`. Must be `close_t+1` for any result that is reported as evidence (spec M2). |
| `cost_bps` | float | Cost applied in the shadow accounting (10 for evaluation). |
| `model_checksum` | str | SHA-256 of the policy file (weights + config). |
| `feature_checksum` | str | SHA-256 of the feature table or the `features_v4` manifest used for the state vector. |
| `code_version` | str | Commit hash of the repo at run time. |
| `run_id` | str | Identifier of the shadow run (one per deployed model). |

## Storage

- One line per decision in `data/shadow/rl/{run_id}/decisions.jsonl` (append-only).
- A run manifest `data/shadow/rl/{run_id}/manifest.json` holds the model and feature checksums, `code_version`,
  the start date, `fill_convention` and `cost_bps`. Written once at start.
- Nothing is written under `data/allocations/` or `data/prod_state/`. The live files stay as they are.

## Reporting (computed from the log, not from the live process)

- Realised shadow NAV versus live NAV on the same dates, with `cost_bps` applied to both books.
- `equity_gap` distribution by regime block, and the share of decisions with |gap| > 0.05.
- Mean and max of `turnover_shadow` versus `turnover_live`.
- Reward components summed by regime block, to show which term drives the shadow policy.
- A replay check: recompute `equity_target` from `raw_action` and confirm the match to 1e-9. Recompute
  `raw_action` from `state_vector` with the stored model and confirm the match to 1e-6.

## Promotion gate (before any live use)

The shadow log must cover at least one full 14d holdout of out-of-sample decisions, and it must pass the
pre-registered bars in `docs/phases/rl_allocator_experiments.md` section 7. Shadow results do not override
those bars. Until they pass, live allocation stays B.5 + B.4.

## Open items for the production task

- Where the shadow hook runs (a separate script or a flag in `run_prod_signal.py`); this spec does not choose.
- Whether `state_vector` should be stored in full or as a feature-store key (storage cost versus replay ease).
