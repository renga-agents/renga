# Task Classification and Planning — Seiji

> This file is the reference source for task decomposition, multi-agent coverage, DAG planning, and the dry-run gate.
> Referenced from `seiji.agent.md`, sections §2 Decomposition and §3 Planning.

---

## Decomposition

### Principles

- Break down into atomic subtasks with explicit acceptance criteria
- Identify dependencies, blocking vs non-blocking
- Estimate complexity, simple, medium, or complex
- Check **automatic triggers**, see `_references/auto-triggers.md`

### Multi-Agent Coverage (ERR-014)

List the facets of the task and assign at least 1 agent to each non-trivial facet.

**Minimums by level**:

| Level | Min agents | Min lanes | Notes |
| --- | --- | --- | --- |
| L2 | 4-6 | 2 | — |
| L3 | 6-10 | 3 | — |
| L4 | 8-15 | 4 | + mandatory consensus |

Full details in `_references/error-catalog.md §ERR-014`

### Catalog Scan (ERR-024)

Scan the 4 lanes and produce an include/exclude list with justification:

- **Tech** -> `orchestrator-tech.agent.md`
- **Product** -> `orchestrator-product.agent.md`
- **Data/AI** -> `orchestrator-data.agent.md`
- **Governance** -> `orchestrator-governance.agent.md`

Full checklist in `_references/error-catalog.md §ERR-024`

### Stack-Domain Consultants in Wave 0

Domain experts must be included **read-only in Wave 0** for any task touching their stack — not just in the implementation wave. They provide version anchoring and prevent `software-architect` from falling back on stale training-data versions.

| Domain trigger | Required Wave 0 consultant |
| --- | --- |
| Frontend / fullstack (React, Next.js, CSS) | `frontend-dev` |
| Mobile (iOS, Android, React Native) | `mobile-dev` |
| Data pipeline / warehouse | `data-engineer` |
| ML / AI feature | `ai-research-scientist` |
| Database schema | `database-engineer` |

> **Why Wave 0, not just Wave 2?** software-architect selects stack and versions during planning. If the domain expert only arrives in Wave 2 (implementation), version choices are already locked in the ADR and the scaffolding.

### Visual Deliverables (ERR-020)

Visual L3+ work requires CreativeDirector + ux-ui-designer + performance-engineer

---

## Planning — DAG Construction

### Assignment and Organization

- Assign each subtask to the optimal agent
- Use **direct dispatch** (depth=1, never through a sub-seiji). Lane profiles:
  - Tech -> `orchestrator-tech.agent.md` | Product -> `orchestrator-product.agent.md`
  - Data/AI -> `orchestrator-data.agent.md` | Governance -> `orchestrator-governance.agent.md`
- Organize execution as sequential, parallel, or wave-based depending on dependencies
- If the decision is critical, use consensus via `consensus-protocol.agent.md`
- **Uncapped fan-out**: run all independent agents in parallel. Details in `execution-modes.agent.md §Fan-Out Rules`

### File Plan (ERR-004)

If parallel dispatch targets the same tree, publish the list with path and owner in the scratchpad BEFORE dispatch.

### Filesystem Matrix

Check `execution-modes.agent.md §Filesystem Matrix` before parallel dispatch.

### Default TDD

qa-engineer in wave 1, red tests, then backend-dev or frontend-dev in wave 2, green implementation. Never parallelize qa-engineer and backend-dev.

### Commit Checkpoint (ERR-015)

1 commit per productive wave. Details in `_references/commit-discipline.md`.

### Typical DAG Examples

See `.github/agents/_references/dag-examples.md` for 3 full examples.

---

## Dry-Run Gate (Plan-Only)

If the user mentioned **`dry-run`**, **`plan only`**, or **`plan-only`** in the request:

1. **Display the planned DAG** in the following format:

   ```text

   === PLANNED DAG (dry-run) ===
   Criticality: L2
   Wave 0: [Agent1 (read), Agent2 (read)] — parallel
   Wave 1: [Agent3 (write)] — depends on Wave 0
   Wave 2: [Agent4 ‖ Agent5] — parallel
   Dependencies: Agent3 -> {Agent1, Agent2} | Agent4 -> Agent3
   Impacted files: [list with owner]
   Agents involved: 5 / Waves: 3

   ```

2. **Stop there** — do NOT continue to step 4 (DISPATCH). No agent is launched, no file is modified, and no worktree is created.
3. **Ask for validation** — the user can:
   - Approve: `Go`, `Execute`, `OK` -> resume at step 4 (DISPATCH)
   - Modify: adjust the plan, add or remove an agent, change wave order, modify criteria
   - Cancel: abandon the task with no trace in decision logs

> **Activation**: the user simply includes `dry-run` or `plan only` in the request. No formal syntax is required. Seiji detects those keywords semantically. Accepted synonyms include `show me the plan`, `preview`, and `without executing`.
>
> **Cost**: dry-run mode only consumes steps 1-3: initialization, decomposition, planning. No dispatch, no code reads, no file edits. Token cost remains minimal.

---

## Timeouts and SLA by Wave Type

These thresholds are **indicative**. They exist to detect blockers, not to interrupt work arbitrarily.

| Wave type | Warning threshold | Escalation threshold | Action on breach |
| --- | --- | --- | --- |
| Read-only wave, exploration or research | 10 min | 20 min | Check available MCP tools, reduce scope |
| Source-writing wave, backend-dev, frontend-dev, and similar agents | 30 min | 60 min | Check progress, split the subtask |
| Consensus wave, 3 or more agents disagreeing | 15 min | 30 min | HITL escalation if no convergence |
| Review or validation wave, qa-engineer, code-reviewer | 20 min | 40 min | Retry with a smaller scope |
| Final wave, synthesis and logging | 10 min | 20 min | HITL escalation |

> **Rule**: if a wave exceeds the escalation threshold without producing output, seiji must notify the human instead of continuing silently. Record that in the scratchpad.
