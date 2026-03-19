---
name: commit-discipline
description: "Enforces coherent commit batches, asset/source separation, multiline convention, reference checks, and per-wave cadence."
argument-hint: "Describe the wave or set of changes to commit"
user-invocable: true
---
# Skill: Commit Discipline

Authoritative source for all commit rules. Every agent that produces file changes must follow these rules.

---

## General Principle — Coherent Batches

Each commit must be a **coherent batch**: governance, implementation, tests, and documentation must not be mixed without explicit justification. A pure governance change belongs in a dedicated commit (`docs(governance): ...` or `chore(governance): ...`).

- If a task produces several batches, log the expected commit order in `.github/logs/decisions-<slug>.md`
- Reject a catch-all commit if the diff prevents clear identification of the decision, risk, and rollback strategy

---

## Asset / Source Separation (ERR-018)

Always separate **binary assets** (images, audio, sprites, fonts) from **source files** (code, tests, config) into distinct commits. Assets have a high Git footprint and low reversibility.

```bash
# ✅ Correct: 2 separate commits
git commit -m "feat(game): add player sprite sheet"   # assets only
git commit -m "feat(game): add player animation logic" # code only

# ❌ Incorrect: 1 mixed commit
git commit -m "feat(game): add player with sprites and animation"
```

---

## Multiline Commit Convention (ERR-005)

Any commit whose message exceeds 1 line must use `git commit -F /tmp/commit_msg.txt`:

1. Write the message into a temporary file via `create_file`
2. Commit by referencing that file

**Never** use `git commit -m "..."` with multiline content — the VS Code Copilot terminal enters `dquote>` mode and the command is lost.

```bash
# 1. Write the message
create_file /tmp/commit_msg.txt "feat(notifications): add WebSocket support

- Add notification controller and service
- Wire up WebSocket gateway
- Refs: DEC-042, ERR-008"

# 2. Commit
git commit -F /tmp/commit_msg.txt
```

---

## Reference Check (ERR-001)

Before each commit, reread the message body and verify that all DEC/ERR references point to the **current** session's decisions, not a previous session. Copy-pasting commit messages across sessions is a frequent source of dead references.

**Safeguard**: each `DEC-xxx` and `ERR-xxx` must match an entry in the active `decisions-<slug>.md`, identified by the slug.

---

## Commit Cadence by Wave (ERR-015)

Every wave that produces artifacts (created, modified, or deleted files) **must** be followed by a commit before the next wave starts.

- **Format**: `<type>(<scope>): wave N — <description>`
- **Exception**: read-only waves (typically wave 0) do not generate their own commit
- **Guardrail**: if wave N is not committed, wave N+1 cannot start
- **Anti-pattern**: a single catch-all commit grouping multiple waves is a **governance incident** — it prevents granular rollback and makes the diff unreadable

### TDD Red Checkpoint (Special Case)

The prompt sent to qa-engineer must include:
> `At the end of your mission, commit the specs plus empty stubs with: git -C <worktree_path> commit -m 'test(<scope>): add failing tests (TDD red)'. This commit must exist before wave 2 starts.`

The red commit **is** the wave 1 commit in a TDD DAG.

---

## File Plan Before Parallel Dispatch (ERR-004)

If several agents will operate on the same file tree, publish the list of canonical files in the scratchpad — with path + owning agent — **before** dispatch. Each agent creates only the files assigned to them.

```markdown
## File plan — wave 2
| File | Owning agent |
|---|---|
| src/api/notifications.controller.ts | backend-dev |
| src/api/notifications.service.ts    | backend-dev |
| migrations/20260307_notifications.sql | database-engineer |
| tests/notifications.spec.ts         | qa-engineer (wave 1) |
```

Without a file plan, two agents can create the same file in parallel → write conflicts and data loss.
