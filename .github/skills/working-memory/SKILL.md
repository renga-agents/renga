---
name: working-memory
description: "Documents the .renga/ working memory structure — what lives where, what to read vs write, file naming conventions, and retention rules."
argument-hint: "Describe what you need to read or write in .renga/ (e.g. 'initialize session', 'log agent scores', 'read infra context')"
user-invocable: true
---
# Skill: Working Memory

The `.renga/` directory is the agent team's persistent working memory for a given project. It is created by `renga install` and is **project-specific** — its content varies per project.

> `.renga/` is separate from `.github/` (framework source). Never confuse the two.

---

## Directory Structure

```text
.renga/
  memory/
    scratchpad.md                    # Session index — append-only, never delete
    scratchpad-<slug>.md             # Active session scratchpad (deleted on closure)
    project-context.md               # Stack, constraints, key decisions for this project
    agent-performance[-<slug>].md    # Agent scoring: consolidated (read-only) / current session
    error-patterns[-<slug>].md       # Error patterns: consolidated (read-only) / current session
    prompt-improvements.md           # Prompt improvement changelog (append-only)
    rubric.md                        # (optional) project overrides — rubric is in skill quality-control
    vps-access.md                    # (project-specific) SSH/infra access, server topology
    <any>.md                         # Project-specific context files added by the team
  reports/
    .current-session                 # Active session UUID (written by session-init hook)
    <slug>/
      index.md                       # Wave/agent report index for this session
      wave-<N>-<agent-name>.md       # Full agent report (written by the agent itself)
      tool-audit.jsonl               # Hook: tool usage log
      quality.jsonl                  # Hook: agent stop events
      session.log                    # Hook: session start/end timestamps
      errors.jsonl                   # Hook: error events
```

---

## Writing Rules for Memory Files

**Generate markdownlint-compliant markdown on the first draft** — no post-generation fix loop.

The `markdown.instructions.md` is auto-injected by Copilot for all `.md` files. Apply these rules proactively before writing, not after:

- Blank line before and after every heading (MD022)
- Blank line before and after every list (MD032)
- Blank line before and after every code block (MD031)
- Every fenced code block must declare a language (MD040)
- File must end with a newline (MD047)

Writing and then correcting in multiple passes wastes tokens and creates noise in the tool log.

---

## Read vs Write by Agent Type

### Seiji (orchestrator)
**Reads**: `scratchpad.md`, `scratchpad-<slug>.md`, `project-context.md`, report `index.md`
**Writes**: `scratchpad-<slug>.md`, `decisions-<slug>.md`, `agent-performance-<slug>.md`, `error-patterns-<slug>.md`, `prompt-improvements.md`, report `index.md`
**Never reads**: full wave reports (reads summaries only — ERR-025)

### Specialized agents (devops, infra, database, scrum-master, etc.)
**Reads**: `project-context.md` + any project-specific files in `.renga/memory/` relevant to their domain (infra topology, DB schema context, VPS access, etc.)
**Writes**: their own wave report to `.renga/reports/<slug>/wave-<N>-<agent-name>.md`
**Note**: the content of `.renga/memory/` varies per project — always check what files exist before assuming a specific file is present.

### Hook scripts (runtime, not agents)
Write automatically to `.renga/reports/<slug>/` — agents do not need to manage this.

---

## File Naming Conventions

- **slug**: short kebab-case identifier for the session task (e.g. `add-notif-api`, `auth-redesign`). Seiji generates it at session start.
- **Per-session files** (`-<slug>.md`): written during the session, consolidated by `scripts/consolidate_memory.py` into the master file after closure.
- **Consolidated files** (no slug suffix): read-only once consolidated. Never write directly to `agent-performance.md` or `error-patterns.md` — always write to the per-session variant.

---

## Retention Rules

| File | Retention |
| --- | --- |
| `scratchpad-<slug>.md` | Deleted by seiji on session closure |
| `wave-<N>-<agent-name>.md` | Kept permanently (audit trail) |
| `tool-audit.jsonl`, `quality.jsonl` | Kept permanently (governance) |
| `agent-performance-<slug>.md` | Consolidated → master, then deletable |
| `error-patterns-<slug>.md` | Consolidated → master, then deletable |

---

## Initialization Checklist (Seiji — session start)

**New session:**
1. Generate a slug (short kebab-case, e.g. `sso-auth`, `timeline-3d`)
2. Create `.renga/memory/scratchpad-<slug>.md`
3. Append a session entry to `.renga/memory/scratchpad.md` (master index — create if absent)
4. Resolve agent roster via skill `agent-roster` → write resolved roster to `.renga/memory/scratchpad-<slug>.md`
5. Create `.renga/reports/<slug>/index.md`

**Resuming an existing session:**
1. Read `.renga/memory/scratchpad.md` → find the active session slug
2. Read `.renga/memory/scratchpad-<slug>.md` (2 reads max)

**Both cases:**
- Read `.renga/memory/project-context.md` for stack and structuring decisions (1 targeted read)
