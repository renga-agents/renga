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

## Time Estimates — Forbidden

**Never** include estimates in hours, days, or weeks in any plan or DAG output. These figures are based on human work paradigms and are meaningless for AI agent execution.

If sequencing information is needed, express it as **relative ordering** only:

- ✅ "Wave 1 runs after Wave 0 is complete"
- ✅ "Wave 2 is blocking — Wave 3 cannot start without its checkpoint"
- ✅ "Agents in Wave 1 run in parallel"
- ❌ "Wave 0: 4-6 hours" — forbidden
- ❌ "Estimated duration: 3-4 weeks" — forbidden

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
Full plan: .renga/memory/scratchpad-<slug>.md

Wave 0 (label): agent-A ‖ agent-B
Wave 1 (label): agent-C ‖ agent-D ‖ agent-E
Wave 2 (label): agent-F → agent-G (fix loop)

Open questions (must be resolved before dispatch):
1. [decision name] — [why it blocks dispatch]
2. ...

→ [N] decisions to resolve before dispatch. Starting with question 1 ↓
```

> **This block is the complete plan structure.** Begin your response with it — no text before it (no skill-loading narration, no "I am classifying", no "Starting with..."). No summary or additional sections after it. No tables. Waves list agents on a single line (`agent-A ‖ agent-B ‖ agent-C`). **Acceptance criteria belong in the scratchpad** (wave plan section), not in this block — the inline block is a pointer, not a plan document.
>
> **After the block: enter interactive question resolution mode.** Do not wait for a generic "validate" response. Immediately guide the user through each open question one by one:
> - Present the question with a **1-2 line framing** (what needs to be decided and why it blocks dispatch — no technical analysis, no alternatives list)
> - Ask a **direct, focused decision question** to the user
> - Once the user answers, **log the decision to the scratchpad** and move to the next question
> - Once all blocking questions are resolved, **announce dispatch** and proceed
>
> Seiji frames the decision; it does not make it. Technical analysis of alternatives belongs to specialist agents dispatched in Wave 0.

### Anti-pattern (ERR-028)

**Seiji producing product content in plan-only mode = governance incident.**

The dry-run output is an **agentique delegation plan**, not a product document. If Seiji produces UX proposals, architecture choices, code snippets, or detailed technical recommendations directly — it has violated this rule and overstepped its role as orchestrator.

**Concrete violations (all forbidden in plan-only mode):**

- ❌ "Tech stack: Hyperledger Fabric + Rust/Go + Kafka + TimescaleDB" → tech choice — belongs to software-architect
- ❌ "Hybrid on-chain/off-chain architecture with sharding" → architecture decision — belongs to infra-architect
- ❌ "✅ Data schemas + ZK-SNARK circuit specifications (not implemented)" → deliverable preview — belongs to agents
- ❌ "12 artifact directories pre-approved: `.renga/architecture/`, ..." → file plan from technical analysis — belongs to agents
- ❌ Any table with one row per agent (regardless of column names: Task, Acceptance Criteria, Scope, Output, etc.) — a table organizing per-agent work is per-agent breakdown in disguise, whatever the headers say
- ❌ Wave tables with "Scope" and "Output" columns per agent — describes deliverables; use acceptance criteria per wave instead
- ❌ Per-agent subtask descriptions inside the plan (e.g., `[software-architect] D1.1: Define boundary between... Acceptance: architecture diagram with...`) — these are **dispatch prompts**, not plan content; they belong in DISPATCH phase agent briefs, not here
- ❌ Acceptance criteria per agent — acceptance criteria belong at the **wave level**, not broken down per agent
- ❌ Acceptance criteria in the inline block — they belong in the scratchpad wave plan; the inline block is a lean pointer, not a plan document
- ❌ Open questions that contain trade-off analysis or list technical alternatives (e.g., "CRDT: stronger consistency... OT: more mature for text...") — an open question names the decision and why it must be resolved before dispatch; the analysis belongs to specialist agents
- ❌ "Covered Lanes" or agent exclusion list inside the plan block — belongs in the scratchpad, not in the user-facing output
- ❌ A summary section listing what each wave "covers" with ✅ bullets — seiji substituting for agents
- ❌ An executive summary block after the DRY-RUN PLAN — seiji commentating on content it did not produce
- ❌ Initialization logs (trigger analysis, roster decisions, escalation) shown to the user — those belong in the scratchpad only
- ❌ The auditable exit checklist embedded in the plan-only output — it is an internal governance tool, not a user deliverable

**Litmus test**: does each item describe **who does what and what gates the dispatch**, or does it describe **what the answer will be**? If the latter → ERR-028.

**Allowed in plan-only mode:**

- ✅ `Wave 0: software-architect ‖ infra-architect ‖ security-engineer (read-only)`
- ✅ `Open question: consensus algorithm choice — irreversible architecture decision, must be resolved before Wave 1`
- ✅ `Gate: Wave 1 blocked until security-engineer validates the P0 security brief`
- ✅ Acceptance criteria per wave — **in the scratchpad wave plan**, not in the inline block
