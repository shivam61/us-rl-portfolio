#!/usr/bin/env bash
# save_context.sh — Update CLAUDE.md and session_handoff.md with current run state.
# Run manually: bash scripts/save_context.sh
# Or fires automatically via Stop hook in .claude/settings.json

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_MD="$REPO_ROOT/CLAUDE.md"
HANDOFF_MD="$REPO_ROOT/docs/session_handoff.md"
LOG_FILE="/tmp/diag_run.log"
NOW="$(date -u +%Y-%m-%dT%H:%M:%S)"

# ── Detect background job ─────────────────────────────────────────────────────
JOB_STATUS="none"
JOB_DETAIL=""

DIAG_PID=$(pgrep -f "run_diagnostics.py" | head -1)
BACKTEST_PID=$(pgrep -f "run_backtest.py" | head -1)

if [ -n "$DIAG_PID" ]; then
    JOB_STATUS="running"
    if [ -f "$LOG_FILE" ]; then
        REBAL_COUNT=$(grep -c "Rebalancing:" "$LOG_FILE" 2>/dev/null || echo 0)
        LATEST=$(grep "Signal Date" "$LOG_FILE" 2>/dev/null | tail -1 | grep -o "Signal Date [0-9-]*" | head -1)
        JOB_DETAIL="diagnostics PID=$DIAG_PID | $REBAL_COUNT rebalances | $LATEST"
    else
        JOB_DETAIL="diagnostics PID=$DIAG_PID (no log)"
    fi
elif [ -n "$BACKTEST_PID" ]; then
    JOB_STATUS="running"
    JOB_DETAIL="backtest PID=$BACKTEST_PID"
else
    # Check if report was written recently (within last hour)
    if [ -f "$REPO_ROOT/data/artifacts/reports/universe_expansion_results.md" ]; then
        JOB_STATUS="completed"
        JOB_DETAIL="diagnostics complete — see data/artifacts/reports/universe_expansion_results.md"
    else
        JOB_STATUS="idle"
        JOB_DETAIL="no active job"
    fi
fi

# ── Build new Current State block ────────────────────────────────────────────
NEW_STATE="<!-- CURRENT_STATE_START -->
## Current State — $NOW
**Active job:** $JOB_DETAIL"

if [ "$JOB_STATUS" = "running" ]; then
    NEW_STATE="$NEW_STATE
**Log:** \`$LOG_FILE\`
Check progress: \`grep -c \"Rebalancing:\" $LOG_FILE && grep \"Signal Date\" $LOG_FILE | tail -1\`"
fi

# Append last ablation result if available
ABLATION="$REPO_ROOT/data/artifacts/diagnostics"
LATEST_ABLATION=$(ls -td "$ABLATION"/2* 2>/dev/null | head -1)
if [ -n "$LATEST_ABLATION" ] && [ -f "$LATEST_ABLATION/ablation_results.csv" ]; then
    FULL_SYS=$(grep "Full_System" "$LATEST_ABLATION/ablation_results.csv" 2>/dev/null | head -1)
    if [ -n "$FULL_SYS" ]; then
        NEW_STATE="$NEW_STATE
**Last Full_System result:** $FULL_SYS"
    fi
fi

NEW_STATE="$NEW_STATE
<!-- CURRENT_STATE_END -->"

# ── Replace Current State block in CLAUDE.md ─────────────────────────────────
.venv/bin/python - <<PYEOF
import re, pathlib

claude_md = pathlib.Path("$CLAUDE_MD")
content = claude_md.read_text()

new_block = """$NEW_STATE"""

updated = re.sub(
    r'<!-- CURRENT_STATE_START -->.*?<!-- CURRENT_STATE_END -->',
    new_block,
    content,
    flags=re.DOTALL
)
claude_md.write_text(updated)
print("CLAUDE.md updated.")
PYEOF

# ── Update Last updated in session_handoff.md ────────────────────────────────
sed -i "s/^Last updated: .*/Last updated: $NOW/" "$HANDOFF_MD" 2>/dev/null
echo "session_handoff.md timestamp updated."

# ── Print commit command ──────────────────────────────────────────────────────
echo ""
echo "Context saved. To commit:"
echo "  git add CLAUDE.md docs/session_handoff.md && git commit -m 'chore: update session context [$NOW]'"
