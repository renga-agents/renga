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

_tmp="${TMPDIR:-/tmp}"
printf '=== %s %s ===\n%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(basename "$0")" "$INPUT" \
  >> "$_tmp/renga-last-hook-payload.txt" 2>/dev/null || true
if [[ -f "$PROJECT_ROOT/.hook-debug" ]]; then
  mkdir -p "$RENGA_BASE" 2>/dev/null || true
  printf '[session-cleanup] %s\n' "$INPUT" >> "$RENGA_BASE/hook-debug.log" 2>/dev/null || true
fi

SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="$RENGA_BASE/reports/$SESSION_ID"

if ! command -v jq &>/dev/null; then exit 0; fi

if [[ -d "$REPORT_DIR" ]]; then
  jq -n --arg event "agent_stop" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg sid "$SESSION_ID" \
    '{event: $event, timestamp: $ts, session_id: $sid}' \
    >> "$REPORT_DIR/session.log" 2>/dev/null || true
fi

exit 0
