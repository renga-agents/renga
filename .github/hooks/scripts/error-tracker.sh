#!/usr/bin/env bash
# NEVER exit non-zero — error tracking must not cause additional errors
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"

# Derive project root from script location — robust against CWD variations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RENGA_BASE="${RENGA_DIR:-$PROJECT_ROOT/.renga}"

# Unconditional trace
echo "[$(date -u +%T)] error-tracker.sh pid=$$ cwd=$(pwd)" >> /tmp/renga-hooks-trace.log 2>/dev/null || true

# Debug mode: dump raw payload if .hook-debug exists in project root
[[ -f "$PROJECT_ROOT/.hook-debug" ]] && echo "[error-tracker] $INPUT" >> /tmp/renga-hook-debug.log 2>/dev/null || true

if ! command -v jq &>/dev/null; then exit 0; fi

ERROR_TYPE="$(echo "$INPUT" | jq -r '.error // .errorType // .message // "unknown"' 2>/dev/null || echo "unknown")"
TOOL="$(echo "$INPUT" | jq -r '.tool // .toolName // .name // "unknown"' 2>/dev/null || echo "unknown")"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"

# Session directory (read from file — env vars don't survive across hook subprocess calls)
SESSION_FILE="$RENGA_BASE/reports/.current-session"
SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="${ERROR_LOG_DIR:-$RENGA_BASE/reports/$SESSION_ID}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

jq -n --arg err "$ERROR_TYPE" --arg tool "$TOOL" --arg ts "$TIMESTAMP" \
  '{error: $err, tool: $tool, timestamp: $ts}' \
  >> "$REPORT_DIR/errors.jsonl" 2>/dev/null || true

exit 0
