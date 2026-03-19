#!/usr/bin/env bash
# NEVER exit non-zero — error tracking must not cause additional errors
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"

# Debug mode: dump raw payload if .hook-debug exists in project root
[[ -f ".hook-debug" ]] && echo "[error-tracker] $INPUT" >> /tmp/renga-hook-debug.log

if ! command -v jq &>/dev/null; then exit 0; fi

ERROR_TYPE="$(echo "$INPUT" | jq -r '.error // .errorType // .message // "unknown"' 2>/dev/null || echo "unknown")"
TOOL="$(echo "$INPUT" | jq -r '.tool // .toolName // .name // "unknown"' 2>/dev/null || echo "unknown")"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"

# Session directory (read from file — env vars don't survive across hook subprocess calls)
SESSION_FILE=".renga/reports/.current-session"
SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="${ERROR_LOG_DIR:-.renga/reports/${SESSION_ID}}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

jq -n --arg err "$ERROR_TYPE" --arg tool "$TOOL" --arg ts "$TIMESTAMP" \
  '{error: $err, tool: $tool, timestamp: $ts}' \
  >> "$REPORT_DIR/errors.jsonl" 2>/dev/null || true

exit 0
