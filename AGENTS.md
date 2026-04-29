# US RL Portfolio — Shared Agent Context

Canonical repo entry point for Codex, Claude, and future agents.

Keep this file small. Do not turn it into a running notebook of prior sessions.

<!-- CURRENT_STATE_START -->
## Current State — 2026-04-29T16:12:49+00:00
- Branch: `main`
- Working tree: 0 changed path(s)
- Dirty paths sample: none
- Latest commit: `bdc9f7ff 2026-04-29 add sec fundamentals poc builder`
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
