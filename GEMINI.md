# AI Agent Guidelines for US RL Portfolio

This repository enforces strict, Staff-level engineering constraints modeled on previous quantitative research and ML pipeline best practices. 

When assisting or generating code for this repository, you **MUST** adhere to the following rules:

## 1. Decision Protocol
All agents MUST follow the **Decision Protocol** before making implementation changes:
- **Root Cause Before Fix:** Identify what failed, where, why, and what evidence supports it before changing code. Do not implement speculative fixes.
- **Plan Before Implementation:** Briefly outline the proposed step, the "why", alternative considerations, and failure modes. 
- **One Major Change Per Run:** Do not bundle objective, execution, labels, and breadth updates into a single experiment/commit. Isolate changes so attribution is reliable.
- **Preserve Stable Baselines:** Compare all research modifications against the `SPY Buy and Hold` and `Equal Weight Universe` baselines, as well as stable model layers.

## 2. Strict Artifact and Leakage Discipline
- **Data & Feature Boundaries:** Never use current-bar information for trading decisions on the current bar. All features must be shifted strictly by at least `T-1`. Targets must look strictly forward (`T+horizon`).
- **Execution Realism:** Signals generated on `T` execute on `T+1` Open. Fall back to Close only if Open is missing. 
- **Artifact Saving:** Every backtest run MUST emit its isolated context into `data/artifacts/runs/<run_id>`, including logs, diagnostics, `metrics.json`, trades, and NAV traces.

## 3. Communication & Transparency
- **Always Add a Log:** Any change to execution thresholds, risk guardrails, or model failures MUST emit a `logger.info` or `logger.warning`. Silent fallbacks are forbidden.
- **Next Steps Documentation:** Whenever you conclude a major iteration, update `docs/NEXT_STEPS.md` to ensure the next engineer (or AI agent) has a clear handoff of assumptions, open limitations, and the immediate next task.

## 4. Git Workflow
- **Keep Committing:** Break up work into atomic, logical commits.
- **Remote Sync:** It is a strict rule to execute `git push` to `git@github.com:shivam61/us-rl-portfolio.git` after successfully implementing and verifying a feature or bug fix.

## 5. Architectural Integrity
- Keep RL (`src/rl`) disabled by default until the foundational supervised + optimizer layers are confirmed stable.
- The Optimizer handles *weights*; the RL agent handles *tilts and macro sizing*. Never mix them.
- The Risk Engine (`src/risk`) strictly overrides outputs (e.g., forcing cash allocations when VIX > threshold). Do not embed risk heuristics inside the Alpha model.