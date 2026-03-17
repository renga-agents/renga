---
name: worktree-lifecycle
description: "Manages the full lifecycle of an isolated Git worktree: creation, zoning, multi-MOE, closure, and rollback."
argument-hint: "Indicate the requested action: 'create <slug>', 'close <slug>', 'rollback wave N'"
user-invocable: true
---

# Skill: Worktree Lifecycle

This skill describes the complete lifecycle of a Git worktree managed by the orchestrator: creation, zoning, multi-MOE handling, common errors, and closure.

---

## When to Create a Worktree

Any `L2+` task that creates or modifies source files requires an isolated worktree.

**Exceptions** (no worktree):

- Pure L1 tasks (memory, logs)
- Audit/read-only missions without source writes

---

## Creation

1. **Derive a slug**: `<verb>-<domain>` (for example: `add-notifications`, `fix-auth`)
2. **Create the worktree**:

   ```bash

   git worktree add /tmp/worktrees/<slug>-<YYYYMMDD> -b feat/<slug>

   ```

3. **Create the scratchpad**: `.copilot/memory/scratchpad-<slug>.md`
4. **Update the index**: `.copilot/memory/scratchpad.md`
5. **Create the reports directory**: `.copilot/reports/<slug>/index.md`

---

## Mandatory Zoning

| Zone | Content | Example |
| --- | --- | --- |
| **Worktree** (`worktree_path/`) | Feature source code | `src/`, `tests/`, migrations |
| **Main workspace** | Governance and memory files | `scratchpad-<slug>.md`, `decisions-<slug>.md` |

### Why This Separation?

Governance files belong to the session branch, **not to the feature**. They must remain accessible even if the feature is abandoned or the worktree is removed.

---

## Worktree Instruction for Agents

Include this in the prompt of every agent that writes source files:

> *All your source files must be created inside the worktree directory: `<worktree_path>/`. Prefix all absolute paths with this worktree_path. Do not write anything to the root workspace.*

**Exception**: read-only agents in wave 0 do not need this prefix (ERR-013).

---

## Simultaneous Multi-MOE

Isolation between simultaneous orchestrators is ensured by `scratchpad-<slug>.md` files: each orchestrator has its own session file. `decisions-<slug>.md` is separated per session.

---

## Closure

1. **Ensure** that all commits are in the `feat/<slug>` branch
2. **Mandatory user validation** (ERR-022): never merge without explicit validation
3. **Merge**: PR `feat/<slug> -> main` or `git merge --no-ff feat/<slug>`
4. **Cleanup**:

   ```bash

   git worktree remove /tmp/worktrees/<slug>-<YYYYMMDD> --force
   git branch -d feat/<slug>

   ```

5. **Delete** the scratchpad and update the index

---

## Rollback

| Situation | Option | Action |
| --- | --- | --- |
| < 5 impacted files | Immediate fix | Redispatch a fixing agent |
| ≥ 5 files or regression | Worktree rollback | `git stash` or `git checkout HEAD -- <files>` |
| Architecture called into question | Session abandonment | Do not merge, remove the worktree |

**Rule**: never continue to wave N+1 if wave N produced unresolved failing tests.

---

## Background Terminals

Verify that all background terminals have been closed before closure.

Instruction for agents running background commands:

> *If you open a terminal with `isBackground: true`, call `kill_terminal(id)` after `await_terminal`. Do not leave any background terminal open.*
