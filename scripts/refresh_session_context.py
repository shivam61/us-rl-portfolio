#!/usr/bin/env python3
"""Refresh shared session context for repo agents."""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


MARKER_START = "<!-- CURRENT_STATE_START -->"
MARKER_END = "<!-- CURRENT_STATE_END -->"
TIMESTAMP_PREFIX = "Last updated:"


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def load_config(repo_root: Path) -> dict:
    return json.loads((repo_root / ".agent-context.json").read_text())


def current_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def git_branch(repo_root: Path) -> str:
    branch = run(["git", "branch", "--show-current"], repo_root)
    return branch or "detached"


def git_status(repo_root: Path) -> list[str]:
    output = run(["git", "status", "--short"], repo_root)
    return [line for line in output.splitlines() if line.strip()]


def git_recent_commits(repo_root: Path, limit: int) -> list[str]:
    output = run(["git", "log", f"-{limit}", "--pretty=format:%h %cs %s"], repo_root)
    return [line for line in output.splitlines() if line.strip()]


def active_jobs(patterns: list[dict]) -> list[str]:
    try:
        output = subprocess.run(
            ["ps", "-eo", "pid=,etimes=,args="],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return []

    jobs: list[str] = []
    self_pids = {os.getpid(), os.getppid()}
    for raw_line in output.splitlines():
        parts = raw_line.strip().split(maxsplit=2)
        if len(parts) != 3:
            continue
        pid_text, elapsed_text, command = parts
        try:
            pid = int(pid_text)
            elapsed = int(elapsed_text)
        except ValueError:
            continue
        if pid in self_pids:
            continue
        for item in patterns:
            pattern = item.get("pattern")
            label = item.get("label")
            if pattern and label and pattern in command:
                jobs.append(f"{label}: pid={pid} elapsed={elapsed}s")
                break
    return jobs


def replace_marker_block(path: Path, block: str) -> None:
    content = path.read_text()
    pattern = re.compile(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}",
        re.DOTALL,
    )
    if pattern.search(content):
        updated = pattern.sub(block, content, count=1)
    else:
        updated = content.rstrip() + "\n\n" + block + "\n"
    path.write_text(updated)


def refresh_timestamp(path: Path, timestamp: str) -> None:
    content = path.read_text()
    replacement = f"{TIMESTAMP_PREFIX} {timestamp}"
    pattern = re.compile(rf"^{re.escape(TIMESTAMP_PREFIX)}.*$", re.MULTILINE)
    if pattern.search(content):
        updated = pattern.sub(replacement, content, count=1)
    else:
        updated = replacement + "\n\n" + content
    path.write_text(updated)


def build_state_block(repo_root: Path, config: dict, timestamp: str) -> str:
    dirty_paths = git_status(repo_root)
    dirty_limit = int(config.get("dirty_paths_limit", 5))
    recent_commits = git_recent_commits(repo_root, int(config.get("recent_commits_limit", 3)))
    jobs = active_jobs(config.get("process_patterns", []))

    lines = [
        MARKER_START,
        f"## Current State — {timestamp}",
        f"- Branch: `{git_branch(repo_root)}`",
        f"- Working tree: {len(dirty_paths)} changed path(s)",
    ]

    if dirty_paths:
        sample = ", ".join(f"`{line}`" for line in dirty_paths[:dirty_limit])
        lines.append(f"- Dirty paths sample: {sample}")
    else:
        lines.append("- Dirty paths sample: none")

    if recent_commits:
        lines.append(f"- Latest commit: `{recent_commits[0]}`")

    if jobs:
        lines.append(f"- Active jobs: {'; '.join(jobs)}")
    else:
        lines.append("- Active jobs: none detected")

    lines.append("- Deep handoff: `docs/agent_handoff.md`")
    lines.append("- Refresh command: `bash scripts/refresh_session_context.sh`")
    lines.append(MARKER_END)
    return "\n".join(lines)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    config = load_config(repo_root)
    timestamp = current_timestamp()
    state_block = build_state_block(repo_root, config, timestamp)

    for rel_path in config.get("entry_docs", []):
        path = repo_root / rel_path
        if path.exists():
            replace_marker_block(path, state_block)

    for rel_path in config.get("handoff_docs", []):
        path = repo_root / rel_path
        if path.exists():
            refresh_timestamp(path, timestamp)

    print(f"Refreshed session context at {timestamp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
