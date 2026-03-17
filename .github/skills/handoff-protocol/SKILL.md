---
name: handoff-protocol
description: "Standardizes handoffs between agents with a structured block (recipient, fixed decisions, open questions, artifacts, next action) and commit discipline."
argument-hint: "Describe the handoff to prepare or the transition context between agents"
user-invocable: true

# Skill: Inter-Agent Handoff Protocol

This skill standardizes transitions between agents to ensure traceability and information continuity.

---

## Mandatory Handoff Block

Each dispatched agent must produce a final handoff block in its report:

```markdown

### Handoff

**For**: <recipient agent or orchestrator>
**Fixed decisions**:
- <decision 1 with justification>
- <decision 2 with justification>

**Open questions**:
- <question 1 - context>
- <question 2 - context>

**Artifacts**:
- <path/file1> - <description>
- <path/file2> - <description>

**Next action**: <description of what the recipient must do>

```

---

## Standard Handoff Chains

### Product Chain

```

ProductStrategist → ProductManager → ProxyPO → Devs

```

- **ProductStrategist**: vision, OKRs, strategic constraints
- **ProductManager**: prioritization, tradeoffs, coordination
- **ProxyPO**: user stories, acceptance criteria, backlog
- **Devs**: implementation according to the specs

### Analytics Chain

```

ProductManager ↔ ProductAnalytics ↔ ProductStrategist

```

Two-way loop: data -> insights -> decisions -> measurement.

### Incident Chain

```

IncidentCommander → ObservabilityEngineer → Debugger → DevOpsEngineer → IncidentCommander

```

Closed loop: detection -> diagnosis -> fix -> validation -> postmortem.

---

## Commit Discipline at Handoff

### Coherent Batches

- Governance, implementation, tests, and documentation must not be mixed
- If a task produces several batches, log the order in `decisions-<slug>.md`

### Asset / Source Separation (ERR-018)

Binary assets (images, audio, sprites) and source files (code, tests) must be in separate commits.

### Multi-Line Convention (ERR-005)

Messages longer than 1 line -> `git commit -F /tmp/commit_msg.txt`. Never use `-m` with multiline content.

### Cadence by Wave (ERR-015)

- 1 commit per productive wave
- Format: `<type>(<scope>): wave N - <description>`
- Read-only waves do not generate commits
- Uncommitted wave N -> wave N+1 blocked

---

## Report Persistence (ERR-025)

Subagent reports must be persisted:

- **Path**: `.copilot/reports/<slug>/wave-<N>-<agent-name>.md`
- **Index**: `.copilot/reports/<slug>/index.md` updated after each wave

---

## Reference Check (ERR-001)

Before each commit, verify that DEC/ERR references point to the current decision, not a previous session.

---

## Security Brief (ERR-008)

When handing off from wave 0 to wave 1, inject SecurityEngineer P0 constraints into the QAEngineer prompt.

---

## Validation Scope (ERR-007)

Before wave 2, QAEngineer produces tests and pure interfaces only. No implementation.
