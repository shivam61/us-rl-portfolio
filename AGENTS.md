# US RL Portfolio — Shared Agent Context

Canonical repo entry point for Codex, Claude, and future agents.

Keep this file small. Do not turn it into a running notebook of prior sessions.

<!-- CURRENT_STATE_START -->
## Current State — 2026-05-03T19:08:06+00:00
- Branch: `main`
- Working tree: 18 changed path(s)
- Dirty paths sample: `M AGENTS.md`, ` M CLAUDE.md`, ` M artifacts/models/rl_e_ppo_best.zip`, ` M artifacts/models/rl_e_ppo_final.zip`, ` M artifacts/reports/phase_e5_training_log.csv`
- Latest commit: `35361dba 2026-05-03 Phase E.8 REJECT: rolling 252d peak regression — Sharpe 1.296→1.277, p75 gate fails`
- Active jobs: none detected
- Deep handoff: `docs/agent_handoff.md`
- Refresh command: `bash scripts/refresh_session_context.sh`
<!-- CURRENT_STATE_END -->

## Purpose

Quantitative US equity research system with point-in-time data handling, feature generation, LightGBM alpha models, portfolio optimization, heuristic risk overlays, and walk-forward backtesting. RL remains disabled by default.

## Context Loading Rules

- Auto-load only this file at session start when possible.
- Do not auto-load deep history docs into every session.
- Open additional files only when the current task requires them.
- Prefer reading smaller summary docs before code or large phase notes.

## Agent Execution Policy

- Work strictly as a single sequential agent by default.
- Do not spawn subagents, parallel agents, background agents, or `general-purpose` agents unless the user explicitly asks.
- Do all analysis, file inspection, code edits, test runs, and validation in the main agent context.
- If the task is large, make a sequential plan and execute it step by step.
- Before using any subagent, ask the user for explicit approval and explain why it is necessary.
- Prefer targeted file reads and targeted edits over delegation.

### Output budget

- Keep responses concise and actionable.
- Do not exceed ~100 lines of normal output.
- Do not print full file contents unless explicitly requested.
- Prefer targeted diffs over full rewrites.
- Do not regenerate unchanged code.


### Context reuse

- Read large docs (ROADMAP, phase docs, agent_handoff) at most once per session.
- Do not re-read unless:
  - task materially changes
  - or user explicitly asks.
- Reuse already-read context.

### Subagent hard ban

Forbidden unless explicitly approved:
- subagents
- parallel agents
- background agents
- `general-purpose` agents
- separate test/debug/refactor agents

## Productivity Exception (important)

- Cost controls must not compromise correctness.
- Never skip:
  - repo rules
  - validation
  - required checks
- If a task requires:
  - reading large files
  - generating more output
  - deeper reasoning  
  → do it, but briefly explain why.



## File Lookup Order

- Start with [`README.md`](/home/shivamguptanit/github/us-rl-portfolio/README.md) for setup and top-level commands.
- For planning or execution tasks, read [`docs/ROADMAP.md`](/home/shivamguptanit/github/us-rl-portfolio/docs/ROADMAP.md) first for current phase, gates, and stable baselines.
- After `docs/ROADMAP.md`, read only the relevant phase doc in `docs/phases/` for the task being worked.
- Read [`docs/ARCHITECTURE.md`](/home/shivamguptanit/github/us-rl-portfolio/docs/ARCHITECTURE.md) when the task touches system boundaries.
- Read [`docs/agent_handoff.md`](/home/shivamguptanit/github/us-rl-portfolio/docs/agent_handoff.md) only for deep history, prior experiment context, or session handoff.
- Read phase docs in `docs/phases/` only when working inside that phase.
- Open source files only after the relevant summary docs are read.

## Save Rules

- Refresh session state at the end of any material work session.
- Refresh after starting or finishing a long-running job that changes the repo's current operating state.
- Refresh after updating baselines, changing the active research focus, or changing the recommended next step.
- Refresh before handing work off to another agent or engineer.
- Do not refresh for trivial read-only exploration unless the current-state block has become stale.

## How To Save State

1. Update [`docs/agent_handoff.md`](/home/shivamguptanit/github/us-rl-portfolio/docs/agent_handoff.md) if there was a material decision, experiment result, bug fix, or next-step change.
2. Run `bash scripts/refresh_session_context.sh`.
3. If Claude compatibility matters, no extra step is needed; the same refresh script updates shared entry docs.

## Repo Rules

- Preserve point-in-time correctness: features must be lagged and labels must remain forward-looking.
- Keep RL disabled by default unless explicitly working on RL.
- Isolate experiment changes so attribution remains clear.
- Prefer `.venv/bin/python` when dependencies are needed.
- After verified code or doc changes, create a git commit with a focused message.
- After a successful commit, sync to the remote repository with `git push`.
