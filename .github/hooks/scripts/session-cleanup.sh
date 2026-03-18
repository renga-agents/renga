#!/usr/bin/env bash
set +e

SESSION_FILE=".copilot/reports/.current-session"
SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR=".copilot/reports/${SESSION_ID}"

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
