#!/usr/bin/env bash
set +e

# Generate session ID
SESSION_ID="${SESSION_ID:-$(python3 -c 'import uuid; print(uuid.uuid4())' 2>/dev/null || date +%s)}"
export SESSION_ID

# Create reports directory
COPILOT_BASE="${COPILOT_DIR:-.copilot}"
REPORT_DIR="${COPILOT_BASE}/reports/${SESSION_ID}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

# Initialize audit log
touch "$REPORT_DIR/tool-audit.jsonl" 2>/dev/null || true

# Check jq dependency
if ! command -v jq &>/dev/null; then
  echo "⚠️ jq not found — hook scripts will not function correctly." >&2
  echo "Install: brew install jq (macOS) or apt-get install jq (Linux)" >&2
fi

# Log session start
jq -n --arg event "session_start" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg sid "$SESSION_ID" \
  '{event: $event, timestamp: $ts, session_id: $sid}' \
  >> "$REPORT_DIR/session.log" 2>/dev/null || true

exit 0
