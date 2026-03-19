#!/usr/bin/env bash
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"

# Debug mode: dump raw payload if .hook-debug exists in project root
[[ -f ".hook-debug" ]] && echo "[quality-check] $INPUT" >> /tmp/renga-hook-debug.log

if ! command -v jq &>/dev/null; then exit 0; fi

AGENT="$(echo "$INPUT" | jq -r '.agent // .agentName // .name // "unknown"' 2>/dev/null || echo "unknown")"
REASON="$(echo "$INPUT" | jq -r '.reason // .stopReason // .stop_reason // "unknown"' 2>/dev/null || echo "unknown")"

# Session directory (read from file — env vars don't survive across hook subprocess calls)
SESSION_FILE=".renga/reports/.current-session"
SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR=".renga/reports/${SESSION_ID}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"
jq -n --arg agent "$AGENT" --arg reason "$REASON" --arg ts "$TIMESTAMP" \
  '{event: "agent_stop", agent: $agent, reason: $reason, timestamp: $ts}' \
  >> "$REPORT_DIR/quality.jsonl" 2>/dev/null || true

exit 0
