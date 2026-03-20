#!/usr/bin/env bash
set -euo pipefail

# Input JSON from stdin: {"tool": "bash", "args": {"command": "ls -la"}}
# Exit 0 = approve, Exit 1 = deny

# Read stdin
INPUT="$(cat)"

# Validate jq is available
if ! command -v jq &>/dev/null; then
  echo "Security hook disabled: jq not found. Install with: brew install jq (macOS) or apt-get install jq (Linux)" >&2
  exit 0
fi

# Validate JSON
if ! echo "$INPUT" | jq empty 2>/dev/null; then
  echo "Invalid JSON input" >&2
  exit 1
fi

TOOL="$(echo "$INPUT" | jq -r '.tool_name // .tool // empty')"

# If tool name is empty, log the input keys to help diagnose then pass through
if [[ -z "$TOOL" ]]; then
  KEYS="$(echo "$INPUT" | jq -r 'keys | join(", ")' 2>/dev/null || echo "?")"
  echo "Unknown tool: (empty name — input keys: $KEYS)" >&2
  exit 0
fi

# --- Tool categories ---
# Tools that execute commands (need command whitelist check)
EXEC_TOOLS="bash execute run_in_terminal shell terminal"
# Tools that edit files (need path check)
EDIT_TOOLS="edit replace_string_in_file create_file write_file multi_replace_string_in_file edit_notebook_file create_directory apply_patch"
# Tools that are always safe (read-only)
SAFE_TOOLS="read_file grep_search semantic_search file_search list_dir get_errors read_notebook_cell_output copilot_getNotebookSummary get_terminal_output manage_todo_list tool_search_tool_regex runSubagent memory await_terminal get_changed_files get_project_setup_info get_search_view_results get_vscode_api terminal_last_command terminal_selection test_failure vscode_askQuestions vscode_listCodeUsages vscode_searchExtensions_internal vscode_renameSymbol fetch_webpage renderMermaidDiagram switch_agent run_notebook_cell run_vscode_command create_and_run_task install_extension open_browser_page kill_terminal prisma-migrate-status prisma-studio prisma-platform-login"

# Check if tool is in a category
in_list() {
  local needle="$1"
  shift
  for item in "$@"; do
    [[ "$item" == "$needle" ]] && return 0
  done
  return 1
}

# --- SAFE tools: always approve ---
if in_list "$TOOL" $SAFE_TOOLS; then
  exit 0
fi

# --- EXEC tools: check command whitelist ---
if in_list "$TOOL" $EXEC_TOOLS; then
  COMMAND="$(echo "$INPUT" | jq -r '.tool_input.command // empty')"

  if [[ -z "$COMMAND" ]]; then
    exit 1  # Empty command = deny
  fi

  # Reject dangerous patterns BEFORE whitelist check
  # Subshells, backticks, process substitution, and output redirections can execute/write arbitrary content
  if [[ "$COMMAND" =~ \$\( ]] || [[ "$COMMAND" =~ \` ]] || [[ "$COMMAND" =~ \<\( ]] || [[ "$COMMAND" =~ \>\( ]]; then
    echo "Dangerous pattern: subshell/backtick/process-substitution detected" >&2
    exit 1
  fi
  # Block output redirections: >, >>, 1>, 1>> (but allow stderr redirect 2>, 2>>)
  if echo "$COMMAND" | grep -qE '(^|[^2[:alnum:]])[1]?\s*>{1,2}' 2>/dev/null; then
    echo "Dangerous pattern: output redirection detected" >&2
    exit 1
  fi

  # Whitelist of safe command prefixes (first word)
  SAFE_COMMANDS="ls cat grep git npm npx node python python3 pytest pip pip3 find head tail wc sort uniq diff echo printf test true false cd pwd mkdir touch cp mv tee sed awk tr cut date env which type file stat basename dirname readlink realpath xargs less more hexdump od xxd sha256sum md5sum"

  # Extract first command from potentially piped/chained commands
  # Split on |, &&, ;, || and check each segment
  # Use tr to split and check each command
  CMDS="$(echo "$COMMAND" | tr '|;&' '\n' | sed 's/^[[:space:]]*//' | awk '{print $1}')"

  while IFS= read -r cmd; do
    [[ -z "$cmd" ]] && continue
    # Strip path prefix to get basename
    cmd="$(basename "$cmd" 2>/dev/null || echo "$cmd")"
    if ! in_list "$cmd" $SAFE_COMMANDS; then
      echo "Command not in whitelist: $cmd" >&2
      exit 1
    fi
  done <<< "$CMDS"

  exit 0
fi

# --- EDIT tools: check path safety ---
if in_list "$TOOL" $EDIT_TOOLS; then
  FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.filePath // .tool_input.path // .tool_input.file_path // empty')"

  if [[ -z "$FILE_PATH" ]]; then
    exit 1  # No path = deny
  fi

  # Canonicalize path
  REAL_PATH="$(realpath -m "$FILE_PATH" 2>/dev/null || realpath "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")"

  # Protected paths — ALWAYS blocked (absolute and relative)
  if [[ "$REAL_PATH" == *"/.git/"* ]] || [[ "$REAL_PATH" == *"/.git" ]] || [[ "$REAL_PATH" == ".git/"* ]] || [[ "$REAL_PATH" == ".git" ]]; then
    echo "Protected path: .git/" >&2
    exit 1
  fi
  if [[ "$REAL_PATH" == *"/.github/hooks/scripts/"* ]] || [[ "$REAL_PATH" == *"/.github/hooks/scripts" ]] || [[ "$REAL_PATH" == ".github/hooks/scripts/"* ]] || [[ "$REAL_PATH" == ".github/hooks/scripts" ]]; then
    echo "Protected path: .github/hooks/scripts/" >&2
    exit 1
  fi

  exit 0
fi


# --- MCP tools: approve (external API calls, no local filesystem side effects) ---
if [[ "$TOOL" == mcp_* ]]; then
  exit 0
fi

# --- DEFAULT: DENY ---
echo "Unknown tool: '$TOOL' (not in any whitelist)" >&2
exit 1
