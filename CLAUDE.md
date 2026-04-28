# Claude Compatibility Context

Claude should use [`AGENTS.md`](./AGENTS.md) as the primary repo entry point.

<!-- CURRENT_STATE_START -->
## Current State — 2026-04-28T09:19:19+00:00
- Branch: `main`
- Working tree: 8 changed path(s)
- Dirty paths sample: `M .agent-context.json`, ` M .claudeignore`, ` M .codexignore`, ` M AGENTS.md`, ` M CLAUDE.md`
- Latest commit: `d8abbb2f 2026-04-28 chore: add shared agent session context`
- Active jobs: none detected
- Deep handoff: `docs/agent_handoff.md`
- Refresh command: `bash scripts/refresh_session_context.sh`
<!-- CURRENT_STATE_END -->

## Rules

- Keep this file small.
- Use `AGENTS.md` for shared instructions.
- Use `docs/agent_handoff.md` only when deep history is required.
- Refresh state with `bash scripts/refresh_session_context.sh`.
