#!/usr/bin/env bash
# NEVER exit non-zero — audit must not block tool execution
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"

# Debug mode: dump raw payload if .hook-debug exists in project root
[[ -f ".hook-debug" ]] && echo "[post-tool-audit] $INPUT" >> /tmp/renga-hook-debug.log

# Require jq for safe parsing
if ! command -v jq &>/dev/null; then exit 0; fi

TOOL="$(echo "$INPUT" | jq -r '.tool // .toolName // .name // "unknown"' 2>/dev/null || echo "unknown")"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"
# Log keys only, not values (security: avoid logging secrets)
ARGS_KEYS="$(echo "$INPUT" | jq -r '(.args // .input // .parameters) | keys | join(",")' 2>/dev/null || echo "")"
EXIT_CODE="$(echo "$INPUT" | jq -r '.result.exitCode // .exitCode // "N/A"' 2>/dev/null || echo "N/A")"

# Session directory (read from file — env vars don't survive across hook subprocess calls)
SESSION_FILE=".copilot/reports/.current-session"
SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="${AUDIT_LOG_DIR:-.copilot/reports/${SESSION_ID}}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

# Append JSONL (jq ensures proper escaping)
jq -n --arg tool "$TOOL" --arg ts "$TIMESTAMP" --arg keys "$ARGS_KEYS" --arg exit "$EXIT_CODE" \
  '{tool: $tool, timestamp: $ts, args_keys: $keys, exit_code: $exit}' \
  >> "$REPORT_DIR/tool-audit.jsonl" 2>/dev/null || true

exit 0
