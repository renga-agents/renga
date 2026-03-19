---
name: quality-control
description: "Verifies subagent outputs, drives the review loop, enforces browser validation, and runs the mandatory retrospective."
argument-hint: "Describe the deliverable or wave output to evaluate"
user-invocable: true
---
# Skill: Quality Control

Authoritative source for output verification, review loops, validation gates, and retrospective.

---

## Report Verification (ERR-025)

Each subagent writes its own full report to `.copilot/reports/<slug>/wave-<N>-<agent-name>.md` and returns only a structured summary (verdict + findings + top-3 P0 + file path).

After receipt of each summary:

1. Verify the file exists at the specified path
2. Update `.copilot/reports/<slug>/index.md`
3. Evaluate: `BLOCKING` or ≥1 critical → read the full report | `RISKS` → assess P0 items | `OK` → summary sufficient
4. Update status: `Accepted` / `Rejected` / `Retry N`

**Fallback**: if the file is missing, recreate it from the summary and note the incident in `error-patterns.md`.

**Inter-wave referencing**: pass a report to the next wave by referencing its **file path** in the prompt — never copy the content inline.

---

## Output Evaluation

- **Satisfactory** → accept and move to the next step
- **Insufficient** → return with precise criticism. Maximum 2 retries, then log in `error-patterns.md` and choose an alternative approach
- **Disagreement** → consensus via `consensus-protocol.agent.md`
- **Blocker** → human escalation with a structured summary

---

## Cyclical Review Loop (ERR-019)

The review wave does not end after a single pass. The cycle `code-reviewer → DevAgent fix → code-reviewer re-review` repeats until code-reviewer issues an **Approve** verdict with zero P0/blocking issues.

- **Maximum 3 iterations**
- After 3 iterations without convergence → human escalation
- **Never** declare a task complete while P0 issues remain open

---

## Browser Validation (ERR-021)

Any interactive deliverable (game, UI, form, web application) must be validated with Playwright or equivalent **before** being declared complete.

Checklist:
1. Start the application — verify it boots with no console errors
2. Reproduce main user scenarios (navigation, interactions, inputs)
3. Capture screenshots at key steps as visual proof
4. Verify no JavaScript errors in the console

**A deliverable declared "done" without browser testing is a governance incident.**

---

## User Validation Before Merge (ERR-022)

**Never** merge into the main branch without the user's **explicit** written approval.

Process:
1. Present a structured summary: fixed bugs, passed tests, screenshots, commits
2. Wait for written confirmation
3. Only then proceed with the merge

An unauthorized merge is a **non-negotiable governance incident**.

---

## Squash Merge Forbidden (ERR-023)

Never use `git merge --squash` unless the user explicitly requests it. Squash merge destroys per-wave commit granularity and prevents partial rollback.

Default: `git merge --no-ff feat/<slug>`

---

## Retrospective — Mandatory for L2+

> An empty dashboard = missed retrospectives. The retrospective is a quality gate, not optional.

1. Score each dispatched agent via `.copilot/memory/rubric.md` (raw + weighted)
2. Update `agent-performance-<slug>.md` with this session's scores
3. Log error patterns in `error-patterns-<slug>.md` if any retry or failure occurred
4. Add entry in `prompt-improvements.md` if an agent failed ≥2 times
5. Run `python scripts/generate_dashboard.py` after `consolidate_memory.py`

L0-L1 tasks: no formal retrospective, but error patterns are still logged if a retry occurred.

---

## Auditable Exit Checklist

> Authoritative version: `seiji.agent.md §Auditable Exit Checklist`. This skill does not duplicate it — refer to seiji for the up-to-date list.
