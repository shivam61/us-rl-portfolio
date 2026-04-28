# Session Handoff — Deprecated Path

Last updated: 2026-04-28T09:17:07+00:00

Do not add new handoff notes here.

## New Flow

- Use [`docs/agent_handoff.md`](./agent_handoff.md) as the single deep handoff document.
- Follow the structure and section pattern already used in `docs/agent_handoff.md`.
- Keep [`AGENTS.md`](../AGENTS.md) small and use it only as the repo entry point plus current-state snapshot.
- Refresh shared state with `bash scripts/refresh_session_context.sh` after updating `docs/agent_handoff.md`.

## Migration Rule

- If an old workflow, script, bookmark, or agent points to `docs/session_handoff.md`, move the new notes into `docs/agent_handoff.md` instead of extending this file.
- Treat this file as a redirect stub only.
