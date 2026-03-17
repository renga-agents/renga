#!/usr/bin/env bash
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"

if ! command -v jq &>/dev/null; then exit 0; fi

AGENT="$(echo "$INPUT" | jq -r '.agent // "unknown"' 2>/dev/null || echo "unknown")"
REASON="$(echo "$INPUT" | jq -r '.reason // "unknown"' 2>/dev/null || echo "unknown")"

# Log agent stop event
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR=".copilot/reports/${SESSION_ID}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"
jq -n --arg agent "$AGENT" --arg reason "$REASON" --arg ts "$TIMESTAMP" \
  '{event: "agent_stop", agent: $agent, reason: $reason, timestamp: $ts}' \
  >> "$REPORT_DIR/quality.jsonl" 2>/dev/null || true

exit 0
