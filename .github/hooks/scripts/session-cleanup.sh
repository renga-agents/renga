#!/usr/bin/env bash
set +e

_self="${BASH_SOURCE[0]:-$0}"
_dir="$(cd "$(dirname "$_self")" 2>/dev/null && pwd)"
PROJECT_ROOT="$(cd "$_dir/../../.." 2>/dev/null && pwd)"
if [[ ! -f "$PROJECT_ROOT/.renga.yml" ]]; then
  _d="$(pwd)"
  while [[ "$_d" != "/" ]]; do
    [[ -f "$_d/.renga.yml" ]] && PROJECT_ROOT="$_d" && break
    _d="$(dirname "$_d")"
  done
fi
RENGA_BASE="${RENGA_DIR:-$PROJECT_ROOT/.renga}"
SESSION_FILE="$RENGA_BASE/reports/.current-session"

_tmp="${TMPDIR:-/tmp}"
printf '=== %s session-cleanup project=%s ===\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$PROJECT_ROOT" \
  >> "$_tmp/renga-last-hook-payload.txt" 2>/dev/null || true

SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="$RENGA_BASE/reports/$SESSION_ID"

if ! command -v jq &>/dev/null; then exit 0; fi

if [[ -d "$REPORT_DIR" ]]; then
  jq -n --arg event "session_end" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg sid "$SESSION_ID" \
    '{event: $event, timestamp: $ts, session_id: $sid}' \
    >> "$REPORT_DIR/session.log" 2>/dev/null || true
fi

rm -f "$SESSION_FILE" 2>/dev/null || true

exit 0
