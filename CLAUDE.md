# Claude Compatibility Context

Claude should use [`AGENTS.md`](./AGENTS.md) as the primary repo entry point.
All repo rules, workflow rules, save rules, file lookup order, roadmap-first behavior, and git workflow requirements are governed by `AGENTS.md`.
Do not treat this file as an independent source of repo instructions.

<!-- CURRENT_STATE_START -->
## Current State — 2026-04-30T20:00:59+00:00
- Branch: `main`
- Working tree: 13 changed path(s)
- Dirty paths sample: `M docs/ROADMAP.md`, ` M docs/agent_handoff.md`, ` M docs/phases/phase_b.md`, `?? artifacts/reports/phase_b1_runner_detail.csv`, `?? artifacts/reports/phase_b1_simulator_reproduction.csv`
- Latest commit: `40ec7b59 2026-04-30 tighten phase b reproduction gates`
- Active jobs: none detected
- Deep handoff: `docs/agent_handoff.md`
- Refresh command: `bash scripts/refresh_session_context.sh`
<!-- CURRENT_STATE_END -->

## Rules

- Read `AGENTS.md` first and follow it as the canonical instruction file for this repo.
- Use `docs/agent_handoff.md` only when deep history is required, following the pattern defined by `AGENTS.md`.
- Refresh state with `bash scripts/refresh_session_context.sh`.
- Do not add Claude-specific repo rules here unless they are purely compatibility notes that point back to `AGENTS.md`.
