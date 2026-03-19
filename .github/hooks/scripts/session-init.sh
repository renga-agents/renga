#!/usr/bin/env bash
set +e

RENGA_BASE="${RENGA_DIR:-.renga}"
SESSION_FILE="${RENGA_BASE}/reports/.current-session"

# Generate session ID
SESSION_ID="$(python3 -c 'import uuid; print(uuid.uuid4())' 2>/dev/null || date +%s)"

# Create reports directory and persist SESSION_ID to file (env vars don't survive across hook subprocess calls)
REPORT_DIR="${RENGA_BASE}/reports/${SESSION_ID}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true
echo "$SESSION_ID" > "$SESSION_FILE" 2>/dev/null || true

# Initialize audit log
touch "$REPORT_DIR/tool-audit.jsonl" 2>/dev/null || true

# Check jq dependency
if ! command -v jq &>/dev/null; then
  echo "⚠️ jq not found — hook scripts will not function correctly." >&2
  echo "Install: brew install jq (macOS) or apt-get install jq (Linux)" >&2
  exit 0
fi

# Log session start
jq -n --arg event "session_start" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg sid "$SESSION_ID" \
  '{event: $event, timestamp: $ts, session_id: $sid}' \
  >> "$REPORT_DIR/session.log" 2>/dev/null || true

exit 0
