#!/usr/bin/env bash
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"

# Project root from payload .cwd (most reliable) with BASH_SOURCE fallback
PROJECT_ROOT="$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)"
if [[ -z "$PROJECT_ROOT" || ! -f "$PROJECT_ROOT/.renga.yml" ]]; then
  _self="${BASH_SOURCE[0]:-$0}"
  _dir="$(cd "$(dirname "$_self")" 2>/dev/null && pwd)"
  PROJECT_ROOT="$(cd "$_dir/../../.." 2>/dev/null && pwd)"
fi
RENGA_BASE="${RENGA_DIR:-$PROJECT_ROOT/.renga}"
SESSION_FILE="$RENGA_BASE/reports/.current-session"
MEMORY_DIR="$RENGA_BASE/memory"

_tmp="${TMPDIR:-/tmp}"
printf '=== %s %s ===\n%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(basename "$0")" "$INPUT" \
  >> "$_tmp/renga-last-hook-payload.txt" 2>/dev/null || true
[[ -f "$PROJECT_ROOT/.hook-debug" ]] && \
  printf '[session-init] %s\n' "$INPUT" >> "$RENGA_BASE/hook-debug.log" 2>/dev/null || true

# Generate session ID
SESSION_ID="$(python3 -c 'import uuid; print(uuid.uuid4())' 2>/dev/null || date +%s)"

# Create reports directory and persist SESSION_ID to file
REPORT_DIR="$RENGA_BASE/reports/$SESSION_ID"
mkdir -p "$REPORT_DIR" 2>/dev/null || true
echo "$SESSION_ID" > "$SESSION_FILE" 2>/dev/null || true

# Append minimal entry to scratchpad.md master index
mkdir -p "$MEMORY_DIR" 2>/dev/null || true
SCRATCHPAD="$MEMORY_DIR/scratchpad.md"
if [[ ! -f "$SCRATCHPAD" ]]; then
  printf '# Session Index\n\n> Append-only master index.\n\n<!-- Sessions (append below) -->\n' \
    > "$SCRATCHPAD" 2>/dev/null || true
fi
printf -- '- %sZ | session-%s | started |\n' \
  "$(date -u +%Y-%m-%dT%H:%M)" "${SESSION_ID:0:8}" \
  >> "$SCRATCHPAD" 2>/dev/null || true

# Initialize audit log
touch "$REPORT_DIR/tool-audit.jsonl" 2>/dev/null || true

# Check jq dependency
if ! command -v jq &>/dev/null; then
  echo "⚠️ jq not found — hook scripts will not function correctly." >&2
  exit 0
fi

# Log session start
jq -n --arg event "session_start" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg sid "$SESSION_ID" \
  '{event: $event, timestamp: $ts, session_id: $sid}' \
  >> "$REPORT_DIR/session.log" 2>/dev/null || true

exit 0
