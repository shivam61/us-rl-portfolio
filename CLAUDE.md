# Claude Compatibility Context

Claude should use [`AGENTS.md`](./AGENTS.md) as the primary repo entry point.

<!-- CURRENT_STATE_START -->
## Current State — 2026-04-28T09:12:58+00:00
- Branch: `main`
- Working tree: 11 changed path(s)
- Dirty paths sample: `M .claude/settings.json`, ` M .claudeignore`, ` M CLAUDE.md`, ` M docs/session_handoff.md`, ` M scripts/save_context.sh`
- Latest commit: `7f4cc80b 2026-04-28 Clarify sp100 and sp500 baseline terminology`
- Active jobs: none detected
- Deep handoff: `docs/agent_handoff.md`
- Refresh command: `bash scripts/refresh_session_context.sh`
<!-- CURRENT_STATE_END -->

## Rules

- Keep this file small.
- Use `AGENTS.md` for shared instructions.
- Use `docs/agent_handoff.md` only when deep history is required.
- Refresh state with `bash scripts/refresh_session_context.sh`.
