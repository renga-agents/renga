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

if [[ -f "$PROJECT_ROOT/.hook-debug" ]]; then
  _tmp="${TMPDIR:-/tmp}"
  printf '=== %s %s ===\n%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(basename "$0")" "$INPUT" \
    >> "$_tmp/renga-last-hook-payload.txt" 2>/dev/null || true
  mkdir -p "$RENGA_BASE" 2>/dev/null || true
  printf '[error-tracker] %s\n' "$INPUT" >> "$RENGA_BASE/hook-debug.log" 2>/dev/null || true
fi

if ! command -v jq &>/dev/null; then exit 0; fi

ERROR_TYPE="$(echo "$INPUT" | jq -r '.error // .message // "unknown"' 2>/dev/null || echo "unknown")"
TOOL="$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null || echo "unknown")"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"

SESSION_FILE="$RENGA_BASE/reports/.current-session"
SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="${ERROR_LOG_DIR:-$RENGA_BASE/reports/$SESSION_ID}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

jq -n --arg err "$ERROR_TYPE" --arg tool "$TOOL" --arg ts "$TIMESTAMP" \
  '{error: $err, tool: $tool, timestamp: $ts}' \
  >> "$REPORT_DIR/errors.jsonl" 2>/dev/null || true

exit 0
