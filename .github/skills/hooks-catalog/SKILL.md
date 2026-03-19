---
name: hooks-catalog
description: "Describes active Copilot hooks, their impact on agent behavior, allowlisted commands, and protected paths."
argument-hint: "Describe the tool use or action to check against hook policy"
user-invocable: true
---
# Skill: Hooks Catalog

Authoritative source for active Copilot hooks and their behavioral impact on agents.

> Hooks add **defense-in-depth** — they reinforce existing ERR rules but do not replace instructions. A hook DENY is final and irrevocable by the runtime.

---

## Active Hooks

| Hook | File | Script | Agent impact |
|---|---|---|---|
| preToolUse (security) | security.hooks.json | pre-tool-security.sh | Blocks commands outside the allowlist and edits to protected paths |
| preToolUse (worktree) | governance.hooks.json | pre-tool-worktree.sh | Blocks edits outside `WORKTREE_ZONE` |
| postToolUse (audit) | audit.hooks.json | post-tool-audit.sh | Transparent logging, never blocks |
| postToolUse (markdown) | markdown.hooks.json | post-tool-md-format.sh | Auto-formats `.renga/**/*.md` after create/edit — silent skip if no formatter installed |
| sessionStart | audit.hooks.json | session-init.sh | Initializes the session directory |
| sessionEnd | audit.hooks.json | session-cleanup.sh | Archives session logs |
| userPromptSubmitted | audit.hooks.json | post-tool-audit.sh | Logs anonymized prompt hash |
| agentStop | quality.hooks.json | quality-check.sh | Logs stop reason |
| subagentStop | quality.hooks.json | quality-check.sh | Logs subagent stop reason |
| errorOccurred | audit.hooks.json | error-tracker.sh | Captures the error as JSONL |

---

## Allowlisted Commands (`pre-tool-security`)

Tools are classified into 3 categories:

- **SAFE** (always allowed): read_file, grep_search, semantic_search, file_search, list_dir, get_errors, manage_todo_list, runSubagent, and similar read-only tools
- **EXEC** (command checked against allowlist): bash, execute, run_in_terminal, shell, terminal
- **EDIT** (path checked): edit, replace_string_in_file, create_file, write_file, multi_replace_string_in_file

Allowlisted commands: `ls cat grep git npm npx node python python3 pytest pip find head tail wc sort uniq diff echo printf test true false cd pwd mkdir touch cp mv tee sed awk tr cut date env which type file stat basename dirname readlink realpath xargs`

---

## Protected Paths (Edits Always Blocked)

- `.git/` — repository integrity
- `.github/hooks/scripts/` — security-script integrity

---

## What Agents Must Know

1. A `preToolUse` DENY is **final**. Rephrase the command; do not retry the same action.
2. Audit logs are transparent. Do not attempt to bypass them.
3. If `WORKTREE_ZONE` is defined, edits outside that zone will be blocked.
4. Hooks do not replace instructions — they are a safety net layer.
