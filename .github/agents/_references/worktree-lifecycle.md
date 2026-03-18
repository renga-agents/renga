# Worktree Lifecycle — Orchestrator Reference

> This file describes the complete lifecycle of a Git worktree managed by the orchestrator:
> creation, zoning rules, simultaneous multi-MOE handling, common errors, and closure.

---

## Creation During INITIALIZATION

Any `L2+` task that creates or modifies source files requires an isolated worktree.

### Creation Steps

1. **Derive a short slug** from the task: `<verb>-<domain>`, for example `add-notifications` or `fix-auth`
2. **Create the worktree**:

   ```bash

   git worktree add /tmp/worktrees/<slug>-<YYYYMMDD> -b feat/<slug>

   # or fix/<slug> depending on the task type

   ```

3. **Create the session file**: `create_file .copilot/memory/scratchpad-<slug>.md` using the template in `scratchpad.md`. This file is the only scratchpad for the session.
4. **Update the index** `.copilot/memory/scratchpad.md` by adding a line `| <slug> | <YYYY-MM-DD> | In progress | scratchpad-<slug>.md |`

### Exceptions (No Worktree)

- Pure L1 tasks such as memory or logs
- Audit or read-only missions with no source edits

---

## Mandatory Zoning Rule

Two file categories, two **non-overlapping** zones:

| Zone | Content | Example |
| --- | --- | --- |
| **Worktree** (`worktree_path/`) | All feature source code | `src/`, `tests/`, migrations, module README |
| **Main workspace** | Governance and memory files | `.copilot/memory/scratchpad-<slug>.md`, `.github/logs/decisions-<slug>.md`, `.copilot/docs/` |

### Why This Separation?

Governance files such as `decisions-<slug>.md` and `scratchpad-<slug>.md` belong to the current session branch, **not to the feature**. They must remain accessible even if the feature is abandoned or the worktree is removed.

If those files were written inside the worktree, they would disappear from the main branch after the feature merge, making the governance journal incomplete.

---

## Creating the Reports Directory

At the same time as the worktree and scratchpad, create:

1. `create_directory .copilot/reports/<slug>/`
2. `create_file .copilot/reports/<slug>/index.md` with:

   ```markdown

   # Reports — Session <slug>

   **Date**: <YYYY-MM-DD>

   | Wave | Agent | Status | Summary |
   | --- | --- | --- | --- |

   ```

This directory will hold the report files created by each dispatched subagent. See ERR-025 in `error-catalog.md`.

---

## Simultaneous Multi-MOE

Isolation between simultaneous orchestrators is ensured through `scratchpad-<slug>.md` files. Each orchestrator gets its own session file.

`decisions-<slug>.md` is now **separated by session**, one file per slug. Each entry carries the slug, and each orchestrator writes to its own file. The central `decisions.md` index holds the links.

---

## Common Error: Missing `worktree_path`

**Symptom**: an agent writes in the root workspace instead of the worktree, polluting the main branch.

**Cause**: the orchestrator forgot to pass `worktree_path` to agents in the prompt.

**Prevention**: verify that `scratchpad-<slug>.md` contains the `worktree_path` field before the first dispatch.

**Instruction to include verbatim in the prompt of every agent that writes source files**:
> `All your source files must be created inside the worktree directory: <worktree_path>/. Prefix all absolute paths with this worktree_path. Do not write anything in the root workspace.`

**Exception**: read-only agents in wave 0, such as security-engineer, code-reviewer, software-architect, api-designer, proxy-po, and legal-compliance, do not need that prefix. They read the main workspace for existing context and do not create files. See ERR-013.

---

## Worktree Closure

### Closure Steps

1. **Ensure that all commits** for the task are in the worktree branch `feat/<slug>`
2. **Mandatory user validation (ERR-022)**: NEVER merge to the main branch without **explicit** user approval. The orchestrator presents a structured summary with bugs fixed, tests passed, screenshots, and commits, then WAITS for written confirmation.
3. **Merge** from the main workspace by opening a PR `feat/<slug> -> main` or merging with `git merge --no-ff feat/<slug>`. Never squash merge unless explicitly requested. See ERR-023.
4. **Cleanup**:

   ```bash

   git worktree remove /tmp/worktrees/<slug>-<YYYYMMDD> --force
   git branch -d feat/<slug>

   ```

5. **Delete the scratchpad**: remove `.copilot/memory/scratchpad-<slug>.md` and mark the matching line in `scratchpad.md` as `Completed`

### If the Merge Fails (Conflicts)

Dispatch `git-expert` with the `worktree_path` and target branch name. Do not resolve conflicts manually.

---

## Partial Rollback — Failed Wave

When a wave N produces incorrect files, such as failing tests, regressions, or malformed output:

### Option 1 — Immediate Fix (Failed Wave, Few Files)

1. Identify the files modified in wave N: `git diff --name-only HEAD~1 HEAD`
2. Redispatch a fixing agent with the file list and error report
3. Do not delete the files. Fix them in a new commit.

### Option 2 — Worktree Rollback (Failed Wave, Broad Impact)

```bash

# Inside the session worktree
git stash                        # Save uncommitted changes aside
# or
git checkout HEAD -- <files>  # Restore the concerned files to HEAD

```

### Option 3 — Abandon the Session (Failed Wave, Not Recoverable)

1. Do not merge the worktree into main
2. Document the failure and cause in `scratchpad-<slug>.md`
3. Remove the worktree: `git worktree remove <path> --force`
4. Create a ticket or issue to revisit the task later

### Decision Rule

| Situation | Recommended option |
| --- | --- |
| < 5 impacted files, obvious fix | Option 1 |
| >= 5 files or test regression | Option 2 |
| Fundamental architecture questioned | Option 3 + HITL |

> **Important**: never continue to wave N+1 if wave N produced unresolved failing tests.

---

## Closing Background Terminals

Check subagent reports to ensure all background terminals have been closed. If an `id` is still recorded in `scratchpad-<slug>.md` without justification, call `kill_terminal(id)` before finalizing the task.

**Instruction to include in the prompt of every agent running background commands**:
> `If you open a terminal with isBackground: true, you must call kill_terminal(id) after await_terminal. Do not leave any background terminal open at the end of your mission, unless you recorded its id in the scratchpad with a justification.`

Detailed rule: `agents/execution-modes.agent.md §Background Terminals`.

---

## Closing Reports

Verify that every non-pending line in `.copilot/reports/<slug>/index.md` has a matching `wave-*.md` file. Any inconsistency is a governance incident, and the session cannot be considered traceable.
