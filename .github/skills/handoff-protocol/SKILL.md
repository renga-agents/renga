---
name: handoff-protocol
description: "Standardizes handoffs between agents with a structured block (recipient, fixed decisions, open questions, artifacts, next action) and commit discipline."
argument-hint: "Describe the handoff to prepare or the transition context between agents"
user-invocable: true
---
# Skill: Inter-Agent Handoff Protocol

Standardizes transitions between agents to ensure traceability and information continuity.

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
- <question 1 — context>
- <question 2 — context>

**Artifacts**:
- <path/file1> — <description>
- <path/file2> — <description>

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

Two-way loop: data → insights → decisions → measurement.

### Incident Chain

```
IncidentCommander → ObservabilityEngineer → Debugger → DevOpsEngineer → IncidentCommander
```

Closed loop: detection → diagnosis → fix → validation → postmortem.

---

## Related Skills

Commit rules, dispatch sequencing, and report persistence are governed by dedicated skills:

- **Commit discipline** (batches, multiline, wave cadence, asset separation) → skill `commit-discipline`
- **Dispatch rules** (QA scope, security brief, wave 0 read-only, coverage) → skill `dispatch-protocol`
- **Report persistence and output evaluation** → skill `quality-control`
