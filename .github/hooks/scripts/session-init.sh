#!/usr/bin/env bash
set +e

# Derive project root from script location — robust against CWD variations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RENGA_BASE="${RENGA_DIR:-$PROJECT_ROOT/.renga}"
SESSION_FILE="$RENGA_BASE/reports/.current-session"
MEMORY_DIR="$RENGA_BASE/memory"

# Unconditional trace — proves hooks are firing (always writes regardless of .hook-debug)
echo "[$(date -u +%T)] session-init.sh pid=$$ project=$PROJECT_ROOT" >> /tmp/renga-hooks-trace.log 2>/dev/null || true

# Generate session ID
SESSION_ID="$(python3 -c 'import uuid; print(uuid.uuid4())' 2>/dev/null || date +%s)"

# Create reports directory and persist SESSION_ID to file
REPORT_DIR="$RENGA_BASE/reports/$SESSION_ID"
mkdir -p "$REPORT_DIR" 2>/dev/null || true
echo "$SESSION_ID" > "$SESSION_FILE" 2>/dev/null || true

# Append minimal entry to scratchpad.md master index (session tracking)
mkdir -p "$MEMORY_DIR" 2>/dev/null || true
SCRATCHPAD="$MEMORY_DIR/scratchpad.md"
if [[ ! -f "$SCRATCHPAD" ]]; then
  printf '# Session Index\n\n> Append-only master index.\n\n<!-- Sessions (append below) -->\n' > "$SCRATCHPAD" 2>/dev/null || true
fi
printf -- '- %s | session-%s | started |\n' \
  "$(date -u +%Y-%m-%dT%H:%M)Z" "${SESSION_ID:0:8}" \
  >> "$SCRATCHPAD" 2>/dev/null || true

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
