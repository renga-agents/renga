#!/usr/bin/env bash
# NEVER exit non-zero — audit must not block tool execution
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"

# Require jq for safe parsing
if ! command -v jq &>/dev/null; then exit 0; fi

TOOL="$(echo "$INPUT" | jq -r '.tool // "unknown"' 2>/dev/null || echo "unknown")"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"
# Log keys only, not values (security: avoid logging secrets)
ARGS_KEYS="$(echo "$INPUT" | jq -r '.args | keys | join(",")' 2>/dev/null || echo "")"
EXIT_CODE="$(echo "$INPUT" | jq -r '.result.exitCode // "N/A"' 2>/dev/null || echo "N/A")"

# Session directory
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="${AUDIT_LOG_DIR:-.copilot/reports/${SESSION_ID}}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

# Append JSONL (jq ensures proper escaping)
jq -n --arg tool "$TOOL" --arg ts "$TIMESTAMP" --arg keys "$ARGS_KEYS" --arg exit "$EXIT_CODE" \
  '{tool: $tool, timestamp: $ts, args_keys: $keys, exit_code: $exit}' \
  >> "$REPORT_DIR/tool-audit.jsonl" 2>/dev/null || true

exit 0
