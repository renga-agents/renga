---
name: task-decomposition
description: "Breaks down a complex task into atomic subtasks with criticality classification (L0-L4), multi-agent coverage, and acceptance criteria."
argument-hint: "Describe the task to decompose (example: 'Add a POST /api/v1/notifications endpoint with WebSocket')"
user-invocable: true

# Skill: Task Decomposition

This skill guides the structured breakdown of a task into atomic subtasks while applying the renga framework conventions.

---

## Criticality Classification

| Level | Definition | Rule |
| --- | --- | --- |
| `L0` | Trivial, single-file, purely mechanical | Fast-track: direct agent, no DAG, no logging |
| `L1` | Local, reversible, no external impact | Simple execution + standard control |
| `L2` | Multi-file/agent, moderate rollback | Mandatory intermediate checkpoint |
| `L3` | Production, security, compliance, data, cost, architecture | Broader consultation + stronger logging |
| `L4` | Critical or irreversible decision | Consensus or mandatory human escalation |

---

## Decomposition Principles

1. **Break down** into atomic subtasks with explicit acceptance criteria
2. **Identify** dependencies (blocking vs non-blocking)
3. **Estimate** complexity (simple / medium / complex)
4. **Check** automatic triggers (see the `auto-triggers` skill)

---

## Multi-Agent Coverage

List the facets of the task and assign at least 1 agent to each non-trivial facet.

### Minimums by Level

| Level | Min agents | Min lanes |
| --- | --- | --- |
| L2 | 4-6 | 2 |
| L3 | 6-10 | 3 |
| L4 | 8-15 | 4 (+ mandatory consensus) |

### Scan the 4 Lanes

Scan the 4 lanes and produce an included/excluded list with justification:

- **Tech**: backend, frontend, QA, DevOps, infra, performance, observability
- **Product**: product manager, proxy PO, UX/UI, analytics, GTM
- **Data/AI**: data science, ML, MLOps, data engineering
- **Governance**: security, compliance, risk, AI ethics, FinOps

---

## L0 Fast Track

### Criteria (all required)

- Single-file task (only 1 modified file)
- Immediately reversible
- No external impact (no migration, deployment, or public API)
- No architecture decision
- No sensitive data
- No multi-agent coordination needed

### L0 Examples

- Reformat a file
- Rename a local variable
- Add a comment or a type annotation
- Fix a typo
- Change a CSS value

### When It Is NOT L0

Reclassify as L1+ if:

- Multiple files are modified
- There is an impact on an API contract or shared interface
- It touches authentication, permissions, or personal data
- It requires choosing between multiple approaches
- It introduces or removes a dependency

---

## Visual Deliverables

Visual L3+ work requires `creative-director` + `ux-ui-designer` + `performance-engineer`.

---

## Expected Output Format

```

=== DECOMPOSITION ===
Criticality: L<N>

Subtasks:
1. [Agent] Description - acceptance criteria
2. [Agent] Description - acceptance criteria
...

Dependencies:
- Task 2 -> Task 1 (blocking)
- Task 3 ‖ Task 4 (can run in parallel)

Covered lanes: Tech, Product, Governance
Excluded agents: MobileDev (no mobile), MLEngineer (no AI) - justification

```

---

## Dry-run Gate (plan-only mode)

When the user prefixes a request with **"plan-only"** (or equivalent: "just plan", "propose a plan", "what would you do"):

> Seiji produces the **agentique execution plan only** — not the product deliverable.

### What Seiji DOES in dry-run mode

- Classify the task (L0-L4)
- Resolve the agent roster from `.renga.yml`
- Build the DAG (waves, agents, dependencies)
- Write acceptance criteria per agent/wave
- List open questions that must be resolved before dispatch

### What Seiji NEVER does in dry-run mode

- ❌ Produce design proposals, UX recommendations, or architecture choices
- ❌ Read project instruction files (`.github/instructions/`) — that is specialized agent work
- ❌ Write code, TypeScript types, component structures, or content
- ❌ Substitute for the agents it would dispatch

### Dry-run output format

```text
=== DRY-RUN PLAN ===
Criticality: L<N>
Roster: [agents resolved from .renga.yml — or "mode: all"]

Wave 0 (context + version anchoring): agent-A, agent-B
Wave 1 (design/build): agent-C ‖ agent-D ‖ agent-E
Wave 2 (review): agent-F → agent-G (fix loop)

Acceptance criteria (per wave):
- Wave 1: [criteria]
- Wave 2: [criteria]

Open questions (must be resolved before dispatch):
1. ...
2. ...

→ Validate this plan to trigger dispatch.
```

### Anti-pattern (ERR-028)

**Seiji producing product content in plan-only mode = governance incident.**

The dry-run output is an **agentique delegation plan**, not a product document. If Seiji produces UX proposals, architecture choices, code snippets, or detailed technical recommendations directly — it has violated this rule and overstepped its role as orchestrator.
