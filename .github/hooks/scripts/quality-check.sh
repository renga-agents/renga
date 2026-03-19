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

_tmp="${TMPDIR:-/tmp}"
printf '=== %s %s ===\n%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(basename "$0")" "$INPUT" \
  >> "$_tmp/renga-last-hook-payload.txt" 2>/dev/null || true

[[ -f "$PROJECT_ROOT/.hook-debug" ]] && \
  printf '[quality-check] %s\n' "$INPUT" >> "$RENGA_BASE/hook-debug.log" 2>/dev/null || true

if ! command -v jq &>/dev/null; then exit 0; fi

# Stop event payload: {hook_event_name, session_id, transcript_path, cwd, stop_hook_active}
# agent and reason fields are not present — log as "unknown"
AGENT="unknown"
REASON="$(echo "$INPUT" | jq -r 'if .stop_hook_active == false then "end_of_turn" else "unknown" end' 2>/dev/null || echo "unknown")"

SESSION_FILE="$RENGA_BASE/reports/.current-session"
SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="$RENGA_BASE/reports/$SESSION_ID"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"
jq -n --arg agent "$AGENT" --arg reason "$REASON" --arg ts "$TIMESTAMP" \
  '{event: "agent_stop", agent: $agent, reason: $reason, timestamp: $ts}' \
  >> "$REPORT_DIR/quality.jsonl" 2>/dev/null || true

exit 0
