---
name: rl-experiment-review
description: Review RL experiment results, training logs, metrics, and gate validation. Use after RL training completes or when evaluating holdout results.
---

# RL Experiment Review

## When to use this skill

- After RL training completes or when evaluating holdout results
- Before deciding to promote or reject a checkpoint
- When comparing multiple RL variants or debugging experiment failures

## Required context to read first

1. `AGENTS.md` — canonical repo entry point
2. `docs/ROADMAP.md` — current phase status, production baselines, gate definitions
3. Relevant phase doc in `docs/phases/` for detailed context
4. Production manifest: `artifacts/production/*_manifest.json` — current baseline thresholds

## Workflow

### 1. Read Current Baseline from Manifest

**IMPORTANT:** Always read manifest first to get current thresholds (do not use stale hardcoded values).

```bash
cat artifacts/production/*_manifest.json
```

Extract: baseline Sharpe, MaxDD, CAGR, git commit. Use these as gate thresholds.

### 2. Locate Artifacts

```bash
# Training checkpoint and log
ls -lh artifacts/models/rl_*_best.zip
cat artifacts/reports/phase_*_training_log.csv | tail -20

# Holdout evaluation report
cat artifacts/reports/phase_*_rl_evaluation.md
cat artifacts/reports/*_policy_comparison.csv
cat artifacts/reports/*_regime_breakdown.csv
```

### 3. Review Gate Scorecard

From ROADMAP or phase doc, extract current gate framework (typically 8 gates):

1. **Sharpe floor** — RL Sharpe ≥ baseline (from manifest) OR path B variant
2. **MaxDD ceiling** — RL MaxDD ≥ baseline MaxDD (less negative) OR hard floor
3. **Cost tolerance** — 50 bps Sharpe ≥ floor (typically 1.0)
4. **Beats no-op** — RL Sharpe > no-op Sharpe + buffer
5. **Beats random median** — RL ≥ random bounded median (HARD gate)
6. **Beats random p75** — RL ≥ random p75 (PREFERRED gate)
7. **Beats rule-based** — RL ≥ simple heuristic controller (if applicable)
8. **Crisis behavior** — regime-specific Sharpe floors (e.g., 2008: ≥ -0.50, 2020: ≥ 0.0)

**Decision classification:**
- **PROMOTE (clean):** All gates pass including p75
- **CONDITIONAL:** Beats median + crisis + rule-based but misses p75 → requires robustness validation
- **REJECT:** Fails median OR crisis gates OR <6 total gates

### 4. Review Regime Breakdown

Compare RL vs baseline across stress regimes:
- Crisis periods (2008, 2020) — verify floor Sharpe met
- Bear markets (2022) — stress resilience
- Bull periods (2019, 2023) — participation check

### 5. Sanity and Causality Checks

- **No-op sanity:** No-op Sharpe within tolerance of baseline (e.g., 0.05)
- **Overfitting:** Val Sharpe within tolerance of train Sharpe (e.g., 0.15)
- **Action space:** Verify equity/trend/cash fractions sum to 1.0, within bounds
- **Leakage:** Confirm `state_t` uses only t-1 data; `action_t` applied to t+1 returns
- **Causality:** Confirm reward_t computed from t-1 NAV/returns (no lookahead)
- **Rebalance alignment:** Confirm rebalance dates match historical executor

### 6. Feature Parity (if applicable, e.g., Phase G)

If production feature parity is a gate:

```bash
# Run G.0 feature parity check
.venv/bin/python scripts/check_feature_parity_g0.py

# Gate: max deviation < 1e-6, zero NaN values
cat artifacts/reports/phase_g0_feature_parity.md
```

Check state vector determinism, normalization stability, regime coverage (stress score distribution), sector count.

## Checks

- [ ] Baseline thresholds read from manifest (not stale hardcoded values)
- [ ] Training converged (early stopping triggered, not max episodes)
- [ ] All gates evaluated and documented
- [ ] Random median PASS (auto-reject if fail)
- [ ] Crisis regime PASS (auto-reject if fail)
- [ ] Random p75 evaluated (CONDITIONAL if miss, not auto-reject)
- [ ] No-op sanity check PASS
- [ ] Leakage/causality checks PASS (state_t → action_t → execution_t+1)
- [ ] Action statistics reasonable (not extreme concentrations)

## Output format

**Gate Scorecard:** [Table with gate / metric / value / threshold / pass/fail]

**Decision:** PROMOTE / CONDITIONAL / REJECT

**Rationale:** [1-2 sentences]

If REJECT: root cause + next experiment direction

## Guardrails

- Read manifest first — do NOT use hardcoded thresholds from old phases
- Auto-reject: random median fail OR crisis regime fail
- CONDITIONAL (not auto-reject): p75 miss alone if median + crisis + rule-based pass
- Do NOT skip leakage/causality checks (state_t → action_t → execution_t+1)
- Do NOT promote if action statistics are degenerate (e.g., avg equity <0.2 or >0.95)
- Do NOT skip cost-adjusted Sharpe stress test (typically 50 bps gate)
