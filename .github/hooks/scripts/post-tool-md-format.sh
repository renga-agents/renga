#!/usr/bin/env bash
# post-tool-md-format.sh — auto-format .renga/ markdown files after create/edit
# NEVER exit non-zero — must not block tool execution
set +e

INPUT="$(cat 2>/dev/null || echo '{}')"
if ! command -v jq &>/dev/null; then exit 0; fi

TOOL="$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null)"

# Only act on file write/edit operations (Copilot tool names)
case "$TOOL" in
  create_file|write_file|edit|replace_string_in_file|multi_replace_string_in_file|apply_patch) ;;
  *) exit 0 ;;
esac

FILE="$(echo "$INPUT" | jq -r '
  .tool_input.filePath //
  .tool_input.path //
  .tool_input.file_path //
  ""
' 2>/dev/null)"

# Only target .renga/**/*.md files (agent working memory — not framework source)
[[ "$FILE" == *".renga/"*".md" ]] || exit 0
[[ -f "$FILE" ]] || exit 0

# Try markdownlint-cli2 --fix (preferred: targeted fixes, non-destructive to content)
if command -v markdownlint-cli2 &>/dev/null; then
  markdownlint-cli2 --fix "$FILE" &>/dev/null || true
  exit 0
fi

# Try markdownlint --fix (older CLI)
if command -v markdownlint &>/dev/null; then
  markdownlint --fix "$FILE" &>/dev/null || true
  exit 0
fi

# Fallback: prettier (more aggressive reformatting, but widely available in JS projects)
if command -v prettier &>/dev/null; then
  prettier --write --parser markdown "$FILE" &>/dev/null || true
fi

exit 0
