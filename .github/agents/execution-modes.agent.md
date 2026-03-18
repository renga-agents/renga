---
name: execution-modes
user-invocable: false
description: "Internal non-invocable reference for execution modes: sequential, parallel, waves"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Agent execution modes

> Technical reference for the orchestrator and agents. Defines the 3 execution modes with notation, rules, and concrete examples.

---

## Overview

| Mode | Notation | When to use it | Overhead |
| --- | --- | --- | --- |
| Sequential | `A ──→ B ──→ C` | B depends on A's output | Low - linear |
| Parallel | `[A ‖ B ‖ … ‖ N] ──→ SYNTHESIS` | Independent agents | Medium - synchronization |
| Waves (Consensus) | `{A ⟳ B ⟳ C} → SYNTHESIS → VERDICT` | Critical single-stream decisions | High - multi-iteration |
| **Super-wave** | `[FT:{…} ‖ FP:{…} ‖ FD:{…} ‖ FG:{…}] → MOE_SYNTHESIS` | Cross-cutting decisions across ≥ 3 streams | Very high - cross-stream |
| **Mega-wave** | `MISSION{scope} → MOE → {4 streams} → INTEGRATION` | End-to-end strategic mission | Maximal - 4 streams + MOE |

---

## Platform constraints (VS Code Copilot Agent)

> These constraints are structural. They cannot be bypassed without a platform change.

### Actual invocation depth: 1

VS Code Copilot Agent allows the orchestrator (depth 0) to invoke a sub-agent via `runSubagent` (depth 1). But an agent invoked as a sub-agent **does not have access to the same mechanism** to invoke an additional layer.

| Level | Example | Actual invocation? |
| --- | --- | --- |
| depth 0 | orchestrator | n/a - root agent |
| depth 1 | orchestrator → backend-dev, qa-engineer, security-engineer... | **Yes** - effective `runSubagent` |
| depth 2 | backend-dev → another agent | **No** - not supported |

Consequence: the orchestrator dispatches specialist agents **directly** (depth 1). No intermediate layer can itself invoke sub-agents.

### Parallelism: real, with race condition risk

The notation `‖` expresses **logical independence** AND corresponds to **actually simultaneous execution**: VS Code Copilot Agent opens N agent sessions in parallel when `runSubagent` calls are placed in the **same tool-call block**.

Risk to manage: parallel agents **share the same workspace filesystem**. If backend-dev creates `service.ts` while qa-engineer tries to read it, qa-engineer may read an incomplete state. Mitigation: publish a file plan in the scratchpad before dispatch (see ERR-004).

### Background terminals: lifecycle is mandatory

The `run_in_terminal` tool with `isBackground: true` opens a persistent VS Code terminal and returns an `id`. That terminal **stays open indefinitely** after completion if not closed - terminals accumulate, slow down the workstation, and create confusion.

| Terminal type | ID available? | Programmatic closure | Rule |
| --- | --- | --- | --- |
| `isBackground: true` | ✅ Yes - returned by `run_in_terminal` | ✅ `kill_terminal(id)` | **Mandatory** after completion is confirmed |
| `isBackground: false` | ❌ No - shared zsh shell without ID | ❌ Not applicable | Do not attempt - shared session |

**Mandatory sequence for any background terminal**:

```text

id = run_in_terminal(cmd, isBackground=true)
output = await_terminal(id, timeout)
# ... use the output if needed
kill_terminal(id)   ← ALWAYS, even in case of error

```

**Legitimate exceptions** (background terminal kept open):

- Active development server for the entire duration of the task (example: `npm run dev` watched for successive hot reloads)
- In that case: note the `id` in the scratchpad, close it at end of task via §7 LOGGING

**Responsibility**: each agent is responsible for closing its own background terminals. The orchestrator verifies in the dispatch prompt (see §4) that the instruction is included.

---

## Sequential mode

### Notation

```text

A ──→ B ──→ C

```

### Trigger rule

Use sequential mode when **one agent's output is a required input** for the next agent. Each step waits for the orchestrator's validation before moving to the next.

### Behavior

1. The orchestrator launches agent A with the instructions and context
2. Agent A produces its output
3. The orchestrator evaluates the output (see quality control in `orchestrator.agent.md`)
4. If validated → A's output is injected as context for agent B
5. Repeat until the last step

### Error handling

- If an agent produces insufficient output -> retry with critique (max 2 retries)
- If blocked -> the orchestrator can reorganize the DAG or escalate
- The entire pipeline stops if a blocking agent fails

### Sequential examples

#### Feature development

```text

software-architect ──→ backend-dev ──→ qa-engineer

```

The architecture must be validated before development starts. The final specs must exist before tests are written.

#### API documentation

```text

api-designer ──→ backend-dev ──→ tech-writer

```

The API contract is defined first, implemented next, documented last.

#### Database migration

```text

database-engineer ──→ backend-dev ──→ qa-engineer ──→ devops-engineer

```

The migration schema is designed, the code is adapted, tests are written, then deployment is planned.

---

## Parallel mode

### Parallel notation

```text

[A ‖ B ‖ C ‖ D] ──→ SYNTHESIS

```

### Parallel trigger rule

Use parallel mode when **agents do not create write/read dependencies between each other**. The orchestrator collects all results then produces a consolidated synthesis.

> **VS Code Copilot Agent parallelism**: to trigger truly simultaneous execution, place all independent `runSubagent` calls in the **same tool-call block**. Each agent then runs in its own session. Agents share the workspace filesystem - apply the matrix below before any dispatch.

### Filesystem matrix: parallel or sequential?

| Agent profile | Writes to the workspace? | Rule |
| --- | --- | --- |
| security-engineer, legal-compliance, risk-manager, code-reviewer, architecture-reviewer, ai-ethics-governance | **No** - read-only | Safe parallel with any other agent |
| tech-writer, data-scientist (analysis), performance-engineer (audit) | **No** - read-only | Safe parallel |
| backend-dev, frontend-dev, database-engineer, data-engineer | **Yes** - distinct zones | Safe parallel **if** zones differ + file plan published in the scratchpad |
| qa-engineer mode **TDD** (wave 1) | **Yes** - test files only | Safe parallel with read-only agents; sequential **before** backend-dev |
| qa-engineer mode **TAD** (after implementation) | **Yes** - tests derived from the code | Sequential **after** the implementation agent - otherwise race condition |

### Common patterns:

```text

✅ Safe parallel
[security-engineer ‖ legal-compliance ‖ performance-engineer]   ← read-only
[backend-dev(src/api/) ‖ database-engineer(src/migrations/)]  ← distinct zones
[security-engineer ‖ qa-engineer(TDD)]                        ← QA writes tests, SecEng reads

❌ Race condition → make sequential
[backend-dev ‖ qa-engineer(TAD)]  ← qa-engineer would read incomplete code
[backend-dev ‖ code-reviewer]     ← code-reviewer would read incomplete code

✅ Mandatory TDD (feature with new code)
qa-engineer(red) ──→ backend-dev(green) ──→ code-reviewer

```

### Fan-out rules (number of agents per wave)

> **Principle**: fan-out is not bounded by an arbitrary fixed number. The only real constraint is **filesystem safety** (race conditions). A well-structured DAG can launch 10-12 agents in parallel in the same wave without any problem.

| Type of wave | Recommended fan-out | Limiting constraint |
| --- | --- | --- |
| **Read-only** (wave 0, audits, reviews) | **No cap** - launch all relevant agents. 8-12 agents is normal | None - no writes, no race condition |
| **Writes in distinct zones** | Limited by the number of distinct filesystem zones | File plan published in the scratchpad (ERR-004) |
| **Writes in a shared zone** | 1 writing agent at a time; readers in parallel | Sequentialize only the actual write conflicts |
| **Consensus / waves** | 4-8 experts per opinion wave | Orchestrator synthesis capacity |

**Anti-pattern**: artificially limiting to 3-4 agents per wave when 8+ independent agents are available. An undersized DAG weakens coverage and quality.

### Parallel behavior

1. The orchestrator launches all agents in parallel with the same initial context
2. Each agent works independently
3. The orchestrator collects all outputs
4. Consistency check: do the recommendations contradict each other?
5. If contradiction -> trigger a consensus on the divergent points
6. Otherwise -> consolidated synthesis

### Parallel error handling

- If one parallel agent fails: the others continue, and the partial result is reported
- If the synthesis reveals contradictions: escalate to wave mode on the conflict points
- Timeout: if one agent takes significantly longer, the orchestrator can proceed without it and integrate it later

### Parallel examples

#### Massive Wave 0 - cross-cutting audit of a new feature (8 read-only agents)

```text

 ┌─ software-architect(architecture consistency, patterns)
 ├─ security-engineer(attack vectors, OWASP)
 ├─ performance-engineer(SLO impact, scalability)
 ├─ legal-compliance(GDPR implications, personal data)
 ├─ ux-ui-designer(mockups, user journey)
 ├─ accessibility-engineer(WCAG, ARIA, colors)
 ├─ api-designer(API contract, DX)
 └─ proxy-po(acceptance criteria, business value)
 ──→ Orchestrator SYNTHESIS (8 consolidated reports)

```

#### Full code review (5 read-only agents)

```text

 ┌─ code-reviewer(quality, patterns, maintainability)
 ├─ security-engineer(vulnerabilities, OWASP)
 ├─ performance-engineer(algorithmic complexity, N+1 queries)
 ├─ accessibility-engineer(WCAG, HTML semantics)
 └─ tech-writer(inline documentation quality)
 ──→ SYNTHESIS: consolidated review report

```

#### Feature launch - cross-stream (6 agents)

```text

 ┌─ tech-writer(user documentation)
 ├─ change-management(communication plan)
 ├─ go-to-market-specialist(messaging, segmentation)
 ├─ ux-writer(microcopy, onboarding)
 ├─ proxy-po(business release notes)
 └─ devops-engineer(deployment plan, rollback)
 ──→ SYNTHESIS: complete launch kit

```

#### Multi-zone implementation (4 safe parallel writers)

```text

 ┌─ backend-dev(src/api/ - endpoint + service)
 ├─ database-engineer(src/migrations/ - SQL migration)
 ├─ frontend-dev(src/components/ - UI component)
 └─ qa-engineer(tests/ - TDD red tests)
 ──→ SYNTHESIS: inter-zone consistency check

```

---

## Wave mode (Consensus)

### Wave notation

```text

{A ⟳ B ⟳ C} WAVE_1 → SYNTHESIS → {A' ⟳ B' ⟳ C'} WAVE_2 → VERDICT

```

If arbitration is needed:

```text

{A ⟳ B ⟳ C} V1 → SYNTHESIS → {A' ⟳ B' ⟳ C'} V2 → {A'' ⟳ B'' ⟳ C''} V3 → ARBITRATION → VERDICT

```

### Wave trigger rule

Use wave mode for the **critical decisions** defined in `consensus-protocol.agent.md`. This mode is the most expensive and must not be used for easily reversible decisions.

### Wave behavior

Full reference: `agents/consensus-protocol.agent.md`

1. **Wave 1** (independent): each agent produces its position without seeing the others'
2. **Intermediate synthesis**: the orchestrator identifies convergences, divergences, blind spots
3. **Wave 2** (informed): each agent sees the synthesis and can revise or maintain its position
4. **Wave 3** (if needed): final arbitration on persistent disagreement points
5. **Verdict**: documented decision with full traceability

### Convergence criteria

- Strong convergence (≥ 3/4) -> automatic decision, no additional wave
- Partial convergence (2/4) -> Wave 2 mandatory
- Disagreement after Wave 3 -> orchestrator arbitration or human escalation

### Wave example

#### Choosing a database for a catalog service

```text

Context: 50M items, 90% reads, 10% writes, full-text search required

Wave 1:
 ┌─ database-engineer→ PostgreSQL + pg_trgm + partitioning
 ├─ software-architect→ PostgreSQL + Elasticsearch sidecar
 ├─ performance-engineer→ MongoDB + Atlas Search
 └─ backend-dev→ PostgreSQL + Redis cache layer

Synthesis: Convergence 3/4 on PostgreSQL, divergence on search strategy

Wave 2:
 ┌─ database-engineer→ Maintained - pg_trgm is sufficient up to 100M
 ├─ software-architect→ Revised - pg_trgm at first, Elasticsearch if latency > 200ms
 ├─ performance-engineer→ Revised → PostgreSQL + pg_trgm, benchmark at 3 months
 └─ backend-dev→ Maintained - PostgreSQL with Redis cache for hot queries

VERDICT: PostgreSQL with pg_trgm, benchmark at 3 months, switch threshold to Elasticsearch defined
Consensus level: Strong (4/4 converge on PostgreSQL after Wave 2)

```

---

## Super-wave (Cross-stream)

Reserved for decisions that affect **simultaneously ≥ 3 streams** (tech + product + governance, etc.).

### Super-wave notation

```text

[FT:{A ⟳ B}] ‖ [FP:{C ⟳ D}] ‖ [FD:{E ⟳ F}] ‖ [FG:{G ⟳ H}]
 SUPER-WAVE_1 ──→ MOE_SYNTHESIS ──→ GLOBAL_VERDICT

```

FT = Technical stream specialists, FP = Product stream, FD = Data/AI stream, FG = Governance stream.  
The MOE dispatches specialists **directly** (depth=1) by reading the matrices in the stream profiles. There is no intermediate sub-MOE agent - the MOE coordinates the groups itself.

### Super-wave behavior

1. The MOE reads the 4 stream profiles and identifies the specialists to invoke for each dimension
2. It dispatches each specialist group directly (depth=1)
3. Each group produces a **stream synthesis** in 4 sections: Analysis / Recommendation / Risks / Prerequisites
4. The MOE integrates the 4 syntheses -> identifies cross-dependencies and cross-stream conflicts
5. If conflict -> inter-stream wave (specialists confront their syntheses)
6. **Global verdict** with coordinated execution plan

### Difference from standard wave mode

| Criterion | Waves (standard) | Super-wave |
| --- | --- | --- |
| Scope | Agents from one stream | Specialists from different streams |
| Facilitator | Main MOE | Main MOE only |
| Agents involved | 4-8 experts | 4 groups × 2-5 specialists each (12-20 agents total) |
| Typical duration | 15-45 min | 60-120 min |
| Threshold | Critical single-stream decision | Impact on ≥ 3 streams OR cross-cutting ambiguity |

### Super-wave example

#### Adopting LangGraph for AI orchestration

```text

 ┌─ Tech stream : { ml-engineer ⟳ backend-dev } - API integration and latency
 ├─ Product stream : { ai-product-manager ⟳ proxy-po } - roadmap and user stories
 ├─ Data stream : { data-scientist ⟳ mlops-engineer } - pipelines and model monitoring
 └─ Governance stream : { legal-compliance ⟳ ai-ethics-governance } - AI Act compliance
 ──→ MOE SYNTHESIS → VERDICT : "Adopt LangGraph as a pilot, AI Act compliance verified"

```

---

## Mega-wave (Complete strategic mission)

Reserved for **end-to-end missions** involving the 4 streams in coordinated phases.

### Mega-wave notation

```text

MISSION{scope}
 ──→ MOE_DECOMPOSITION
    ├── [Tech stream: N agents] ──→ TECH_DELIVERABLES
    ├── [Product stream: N agents] ──→ PRODUCT_DELIVERABLES
    ├── [Data stream: N agents] ──→ DATA_DELIVERABLES
    └── [Governance stream: N agents] ──→ GOVERNANCE_DELIVERABLES
 ──→ MOE_INTEGRATION
 ──→ FINAL_DELIVERABLE

```

### Mega-wave trigger rule

Use the mega-wave only for:

- Full product launch (strategic feature or MVP)
- Major architecture overhaul (stack migration)
- Full regulatory compliance effort (AI Act + GDPR simultaneously)
- See `.github/prompts/workflows/saas-launch-full.md` for a complete example

### Managing cross-stream dependencies

The mega-wave produces an explicit **cross-stream dependency DAG** before any execution. Blocking streams are identified and handled first. Example: governance validates before deployment starts.

---

## Combining modes

Modes can be combined in the same DAG. The orchestrator organizes the phases:

```text

software-architect ──→ [backend-dev ‖ database-engineer ‖ frontend-dev]
 ──→ {security-engineer ⟳ performance-engineer ⟳ legal-compliance} CONSENSUS
 ──→ qa-engineer ──→ devops-engineer ──→ tech-writer

```

Reading: architecture in sequential mode first, then development in parallel, then audit in consensus, then testing, deployment, and documentation in sequential mode.

---

## Choosing the mode - Decision aid

| Question | Yes → Mode | No → Mode |
| --- | --- | --- |
| Does agent B need A's output? | Sequential | Parallel |
| Is the decision irreversible or expensive to undo? | Waves | Parallel or Sequential |
| Are the agents working on the same topic with different perspectives? | Waves | Parallel |
| Are the agents working on independent topics? | Parallel | Sequential or Waves |
| Is there a risk of high-impact disagreement? | Waves | Sequential |
| Does the decision affect ≥ 3 streams simultaneously? | **Super-wave** | Waves |
| Does the mission involve all 4 streams end-to-end? | **Mega-wave** | Super-wave |
