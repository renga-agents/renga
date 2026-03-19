#!/usr/bin/env bash
set +e

# Derive project root from script location — robust against CWD variations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RENGA_BASE="${RENGA_DIR:-$PROJECT_ROOT/.renga}"
SESSION_FILE="$RENGA_BASE/reports/.current-session"

# Unconditional trace
echo "[$(date -u +%T)] session-cleanup.sh pid=$$ project=$PROJECT_ROOT" >> /tmp/renga-hooks-trace.log 2>/dev/null || true

SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="$RENGA_BASE/reports/$SESSION_ID"

# Check jq dependency
if ! command -v jq &>/dev/null; then
  echo "⚠️ jq not found — cannot log session end." >&2
  exit 0
fi

# Log session end
if [[ -d "$REPORT_DIR" ]]; then
  jq -n --arg event "session_end" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg sid "$SESSION_ID" \
    '{event: $event, timestamp: $ts, session_id: $sid}' \
    >> "$REPORT_DIR/session.log" 2>/dev/null || true
fi

# Remove session file so next session starts fresh
rm -f "$SESSION_FILE" 2>/dev/null || true

exit 0
