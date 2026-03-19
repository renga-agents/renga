#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"

if ! command -v jq &>/dev/null; then exit 1; fi
if ! echo "$INPUT" | jq empty 2>/dev/null; then exit 1; fi

# Only applies to file-editing tools
TOOL="$(echo "$INPUT" | jq -r '.tool_name // empty')"
EDIT_TOOLS="edit replace_string_in_file create_file write_file multi_replace_string_in_file"

in_list() {
  local needle="$1"; shift
  for item in "$@"; do [[ "$item" == "$needle" ]] && return 0; done
  return 1
}

if ! in_list "$TOOL" $EDIT_TOOLS; then
  exit 0  # Not a file-editing tool, skip check
fi

FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.filePath // .tool_input.path // .tool_input.file_path // empty')"
if [[ -z "$FILE_PATH" ]]; then
  echo "No file path provided" >&2
  exit 1
fi

# Check WORKTREE_ZONE
ZONE="${WORKTREE_ZONE:-}"
if [[ -z "$ZONE" ]] || [[ "$ZONE" == "/" ]]; then
  exit 0  # No worktree zone configured — allow all edits (normal session)
fi

# Canonicalize
REAL_PATH="$(realpath -m "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")"
REAL_ZONE="$(realpath -m "$ZONE" 2>/dev/null || echo "$ZONE")"

# Protected paths — ALWAYS blocked regardless of zone
if [[ "$REAL_PATH" == *"/.git/"* ]] || [[ "$REAL_PATH" == *"/.git" ]]; then
  echo "Protected path: .git/" >&2
  exit 1
fi
if [[ "$REAL_PATH" == *"/.github/hooks/scripts/"* ]] || [[ "$REAL_PATH" == *"/.github/hooks/scripts" ]]; then
  echo "Protected path: .github/hooks/scripts/" >&2
  exit 1
fi

# Ensure trailing slash for prefix match to prevent /tmp/wt matching /tmp/wt-evil/
REAL_ZONE_SLASH="${REAL_ZONE%/}/"
if [[ "$REAL_PATH" != "$REAL_ZONE_SLASH"* ]] && [[ "$REAL_PATH" != "${REAL_ZONE%/}" ]]; then
  echo "Path outside worktree zone" >&2
  exit 1
fi

exit 0
