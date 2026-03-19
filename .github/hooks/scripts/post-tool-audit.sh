#!/usr/bin/env bash
# NEVER exit non-zero — audit must not block tool execution
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"

# Derive project root — try BASH_SOURCE, then $0, then search upward for .renga.yml
_self="${BASH_SOURCE[0]:-$0}"
_dir="$(cd "$(dirname "$_self")" 2>/dev/null && pwd)"
PROJECT_ROOT="$(cd "$_dir/../../.." 2>/dev/null && pwd)"
# Fallback: search upward from CWD for .renga.yml
if [[ ! -f "$PROJECT_ROOT/.renga.yml" ]]; then
  _d="$(pwd)"
  while [[ "$_d" != "/" ]]; do
    [[ -f "$_d/.renga.yml" ]] && PROJECT_ROOT="$_d" && break
    _d="$(dirname "$_d")"
  done
fi
RENGA_BASE="${RENGA_DIR:-$PROJECT_ROOT/.renga}"

# Always dump raw payload for diagnostics (answers "what does Copilot actually send?")
_tmp="${TMPDIR:-/tmp}"
printf '=== %s %s ===\n%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(basename "$0")" "$INPUT" \
  >> "$_tmp/renga-last-hook-payload.txt" 2>/dev/null || true

# Debug mode: full dump when .hook-debug exists at project root
[[ -f "$PROJECT_ROOT/.hook-debug" ]] && \
  printf '[post-tool-audit] %s\n' "$INPUT" >> "$_tmp/renga-hook-debug.log" 2>/dev/null || true

# Require jq for safe parsing
if ! command -v jq &>/dev/null; then exit 0; fi

# Try broad set of field names — exact names depend on Copilot payload schema
TOOL="$(echo "$INPUT" | jq -r '
  .tool // .toolName // .tool_name // .name //
  .toolUse.name // .tool_use.name //
  .data.tool // .data.toolName // .data.name //
  "unknown"
' 2>/dev/null || echo "unknown")"

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")"
ARGS_KEYS="$(echo "$INPUT" | jq -r '
  (.input // .args // .parameters // .toolUse.input // .data.input // {}) | keys | join(",")
' 2>/dev/null || echo "")"
EXIT_CODE="$(echo "$INPUT" | jq -r '
  .exitCode // .exit_code // .result.exitCode // .data.exitCode // "N/A"
' 2>/dev/null || echo "N/A")"

SESSION_FILE="$RENGA_BASE/reports/.current-session"
SESSION_ID="$(cat "$SESSION_FILE" 2>/dev/null | tr -d '[:space:]')"
SESSION_ID="${SESSION_ID:-default}"
REPORT_DIR="${AUDIT_LOG_DIR:-$RENGA_BASE/reports/$SESSION_ID}"
mkdir -p "$REPORT_DIR" 2>/dev/null || true

jq -n --arg tool "$TOOL" --arg ts "$TIMESTAMP" --arg keys "$ARGS_KEYS" --arg exit "$EXIT_CODE" \
  '{tool: $tool, timestamp: $ts, args_keys: $keys, exit_code: $exit}' \
  >> "$REPORT_DIR/tool-audit.jsonl" 2>/dev/null || true

exit 0
