# Claude Compatibility Context

Claude should use [`AGENTS.md`](./AGENTS.md) as the primary repo entry point.
All repo rules, workflow rules, save rules, file lookup order, roadmap-first behavior, and git workflow requirements are governed by `AGENTS.md`.
Do not treat this file as an independent source of repo instructions.

<!-- CURRENT_STATE_START -->
## Current State — 2026-05-05T15:18:19+00:00
- Branch: `main`
- Working tree: 15 changed path(s)
- Dirty paths sample: `M AGENTS.md`, ` M CLAUDE.md`, ` M docs/ROADMAP.md`, ` M docs/agent_handoff.md`, ` M docs/phases/phase_g.md`
- Latest commit: `60669251 2026-05-04 Phase G.0/G.1/G.2: feature parity PASS, signal pipeline, audit trail`
- Active jobs: none detected
- Deep handoff: `docs/agent_handoff.md`
- Refresh command: `bash scripts/refresh_session_context.sh`
<!-- CURRENT_STATE_END -->

## Rules

- Read `AGENTS.md` first and follow it as the canonical instruction file for this repo.
- Use `docs/agent_handoff.md` only when deep history is required, following the pattern defined by `AGENTS.md`.
- Refresh state with `bash scripts/refresh_session_context.sh`.
- Do not add Claude-specific repo rules here unless they are purely compatibility notes that point back to `AGENTS.md`.
