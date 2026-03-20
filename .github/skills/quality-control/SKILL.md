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

Each subagent writes its own full report to `.renga/reports/<slug>/wave-<N>-<agent-name>.md` and returns only a structured summary (verdict + findings + top-3 P0 + file path).

After receipt of each summary:

1. Verify the file exists at the specified path
2. Update `.renga/reports/<slug>/index.md`
3. Evaluate: `BLOCKING` or ≥1 critical → read the full report | `RISKS` → assess P0 items | `OK` → summary sufficient
4. Update status: `Accepted` / `Rejected` / `Retry N`

**Fallback**: if the file is missing, recreate it from the summary and note the incident in `error-patterns.md`.

**Inter-wave referencing**: pass a report to the next wave by referencing its **file path** in the prompt — never copy the content inline.

---

## Output Evaluation

- **Satisfactory** → accept and move to the next step
- **Insufficient** → return with precise criticism. Maximum 2 retries, then log in `error-patterns.md` and choose an alternative approach
- **Disagreement** → consensus via skill `consensus-protocol`
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

1. Score each dispatched agent using the rubric below (raw + weighted)
2. Update `agent-performance-<slug>.md` with this session's scores
3. Log error patterns in `error-patterns-<slug>.md` if any retry or failure occurred
4. Add entry in `prompt-improvements.md` if an agent failed ≥2 times
5. Run `python scripts/generate_dashboard.py` after `consolidate_memory.py`

L0-L1 tasks: no formal retrospective, but error patterns are still logged if a retry occurred.

---

## Scoring Rubric

### Complexity Coefficients

| Level | Description | Coefficient |
| --- | --- | --- |
| L0 | Trivial single-file task (< 15 min) | × 0.5 |
| L1 | Simple multi-file task (< 1h) | × 1.0 |
| L2 | Coordinated complex task (< 4h) | × 1.5 |
| L3 | Multi-wave project (< 1 day) | × 2.0 |
| L4 | Extended multi-session project | × 3.0 |

**Weighted score** = Raw score × Complexity coefficient
Example: agent scores 4/5 on an L3 task → weighted score = 4 × 2.0 = **8.0**

### Evaluation Scale (raw score 0–5)

| Score | Criterion |
| --- | --- |
| 5 | Output matches acceptance criteria on first try, complete handoff |
| 4 | Output compliant, 1 minor retry or incomplete but fixed handoff |
| 3 | Output partially compliant, 1 substantial retry required |
| 2 | Output non-compliant, 2 retries or partial escalation |
| 1 | Output failed, HITL escalation required |
| 0 | Circuit breaker triggered (≥ 2 consecutive failures) |

### Evaluation Dimensions

Score these 3 dimensions per agent and average them:

1. **Compliance** — does the output meet the acceptance criteria?
2. **Completeness** — is the handoff complete, all required artifacts delivered?
3. **Autonomy** — did the agent handle ambiguity without unnecessary escalation?

### Output Format

```markdown
| Agent | Task | Level | Raw Score | Weighted Score | Notes |
| --- | --- | --- | --- | --- | --- |
| backend-dev | Auth API | L2 | 4/5 | 6.0 | 1 retry on tests |
```

---

## Auditable Exit Checklist

> This checklist is a safety net against seiji omissions (SPOF mitigation). Each item must be checked EXPLICITLY before the final synthesis. An unchecked item = governance incident.

### Automatic trigger coverage

- [ ] Automatic trigger table reviewed (see skill `auto-triggers`)
- [ ] Every applicable condition triggered the corresponding agent OR was justified as non-applicable
- [ ] No trigger was silently omitted (ERR-017)

### Multi-agent coverage

- [ ] Agents excluded from the DAG listed with justification in the scratchpad
- [ ] Coverage floors respected (see ERR-014): L2 >= 4 agents, L3 >= 6, L4 >= 8
- [ ] All 4 tracks reviewed (see ERR-024)

### Deliverable control

- [ ] **Plan-only mode**: output is the `=== DRY-RUN PLAN ===` block only — no executive summary, no tech rationale, no delivery checklists (ERR-028)
- [ ] Every dispatched agent prompt included the self-config loading prefix (`.github/agents/<name>.agent.md`)
- [ ] All dispatched agents delivered an output or were relaunched (max 2 retries)
- [ ] Subagent reports persisted in `.renga/reports/<slug>/` (ERR-025)
- [ ] Reports index up to date (ERR-025)
- [ ] No output accepted without verification against acceptance criteria (ERR-019)

### Governance discipline

- [ ] Non-trivial decisions logged in `decisions-<slug>.md`
- [ ] Session scratchpad up to date with final status
- [ ] Seiji direct reads <= 2 (outside memory)
- [ ] Retrospective completed (L2+, **mandatory**) and `agent-performance-<slug>.md` populated with weighted scores
- [ ] Coherent commit batches (see skill `commit-discipline`)

### Escalation

- [ ] No unresolved human escalation situation (see skill `auto-triggers` §Escalation)
- [ ] Inter-agent disagreements resolved (consensus or escalation)
