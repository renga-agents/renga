# Commit Discipline — Orchestrator Reference

> This file details the commit rules that the orchestrator and agents must follow.

---

## General Principle

Each commit must be a **coherent batch**: it should not mix governance, implementation, tests, and documentation without explicit justification. A pure governance change belongs in a dedicated commit such as `docs(governance): ...` or `chore(governance): ...`.

---

## Coherent Batches

- Prepare **coherent batches**: governance, implementation, tests, and documentation should not be mixed without explicit justification
- If the same task produces several batches, log the expected commit order in `.github/logs/decisions-<slug>.md`
- Reject a catch-all commit if the diff prevents a clear identification of the decision, risk, and rollback strategy

---

## Asset / Source Separation (ERR-018)

Always separate **binary assets** such as images, sounds, sprites, and fonts from **source files** such as code, tests, and configuration into distinct commits. Assets have a high Git footprint and low reversibility, so they should never be mixed with logical changes.

```bash

# ✅ Correct: 2 separate commits
git commit -m "feat(game): add player sprite sheet"  # assets only
git commit -m "feat(game): add player animation logic"  # code only

# ❌ Incorrect: 1 mixed commit
git commit -m "feat(game): add player with sprites and animation"

```

---

## Multi-Line Commit Message Convention (ERR-005)

Any commit whose message exceeds 1 line must use `git commit -F /tmp/commit_msg.txt`:

1. Write the message into a temporary file via `create_file`
2. Commit by referencing that file

**Never** use `git commit -m "..."` with multiline content. The VS Code Copilot terminal enters `dquote>` mode and the command is lost.

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

Before each commit, reread the message body and make sure DEC/ERR references point to the **current** decision, not a previous session. Copy-pasting between sessions is a frequent source of dead references.

---

## Commit Cadence by Wave (ERR-015)

On a multi-wave task, a commit must be produced at the end of each wave that generates artifacts:

- **Format**: `<type>(<scope>): wave N - <description>`
- **Exception**: read-only waves, typically wave 0, do not generate their own commit
- **Guardrail**: if wave N is not committed, wave N+1 cannot start
- **Anti-pattern**: a single catch-all commit grouping multiple waves is a **governance incident**. It prevents granular rollback by wave and makes the diff unreadable

### TDD Red Checkpoint (Special Case)

The prompt sent to qa-engineer must include this instruction:
> `At the end of your mission, commit the specs plus empty stubs with: git -C <worktree_path> commit -m 'test(<scope>): add failing tests (TDD red)'. This commit must exist before wave 2 starts.`

The red commit IS the wave 1 commit in a TDD DAG.
