---
name: consensus-protocol
user-invocable: false
description: "Internal non-invocable reference for the multi-wave consensus protocol for critical decisions"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Multi-wave consensus protocol

> Shared reference for all agents to participate in a consensus-based decision process.
> Invocation: `@orchestrator consensus: <question to decide>`

---

## Fundamental principle

Multi-wave consensus is an **iterative challenge** mechanism designed for high-impact decisions. Each agent produces its position independently, then confronts it with the others across successive cycles until convergence or arbitration.

The goal is not unanimity but an **informed and traceable decision**, with minority positions documented for future vigilance.

---

## Trigger thresholds

Wave mode is triggered **automatically** by the orchestrator in the following situations:

### Mandatory triggers

1. **Irreversible architectural choices** - primary database, structuring framework, production AI model, deployment infrastructure
2. **Critical security decisions** - authentication mechanism, encryption strategy, sensitive data exposure, secret management
3. **Regulatory decisions** - interpretation of the AI Act (risk classification), GDPR edge cases (legal basis, transfers outside the EU), OSS license choices with obligations
4. **Disagreement between 2 or more agents** - on a high-impact point identified by the orchestrator
5. **High rollback cost** - any choice whose rollback is estimated at > 2 person-weeks

### Manual trigger

- By the user: `@orchestrator consensus: <question>`
- By an agent that believes its decision should be challenged: explicit mention in its output

---

## Consensus flow

### Wave 1 - Independent positions

Each agent produces its answer **without seeing the others' answers**. This is the phase of maximum perspective diversity.

```text

 ┌─ Agent_A→ Position A
 ├─ Agent_B→ Position B
 ├─ Agent_C→ Position C
 └─ Agent_D→ Position D

```

The orchestrator collects the 4 positions and produces an **intermediate synthesis** identifying:

- Convergence points (shared recommendations)
- Divergence points (disagreements to resolve)
- Blind spots (aspects not covered by any agent)

### Wave 2 - Informed challenge

Each agent receives the intermediate synthesis and can:

- **Maintain** its position with stronger argumentation
- **Revise** its position by justifying the change
- **Enrich** it with new arguments inspired by the other positions

```text

 ┌─ Agent_A'→ Position A' (maintained or revised)
 ├─ Agent_B'→ Position B' (maintained or revised)
 ├─ Agent_C'→ Position C' (maintained or revised)
 └─ Agent_D'→ Position D' (maintained or revised)

```

**Obligation**: any agent that maintains a divergence must explicitly argue why the opposing arguments do not convince it.

### Wave 3 - Arbitration (if needed)

Triggered only if convergence is insufficient after Wave 2. The orchestrator:

1. Identifies the persistent disagreement points
2. Requests from each divergent agent one **final argument** in a maximum of 3 lines
3. Decides with explicit justification, or escalates to a human if the disagreement concerns a high-impact irreversible point

**Stopping criterion**: consensus ends after Wave 3, whatever happens. Analysis paralysis is a greater risk than an imperfect decision.

---

## Participation format for a wave

Each agent **MUST** structure its response in this exact format:

```markdown

## Position [AGENT_NAME][VARIANT] - Wave [N]

**Recommendation** : [one decisive sentence - no "it depends"]

**Confidence** : [High / Medium / Low] - [one-line justification]

**Arguments** :
 1. [main argument with data, metrics, or verifiable references]
 2. [secondary argument with project-specific context]
 3. [additional argument if relevant - max 4 arguments]

**Risks if not selected** :
 - [concrete consequence #1 with estimated impact]
 - [concrete consequence #2 if applicable]

**Revision conditions** : [what would make me change my mind - explicit triggering factors]

**Divergence from previous wave** : [Maintained / Revised - why]
← this section is mandatory starting from Wave 2

```

### Formatting rules

- The recommendation is **always decisive**: "Use PostgreSQL" and not "PostgreSQL or MongoDB depending on the case"
- The confidence level is **always justified**: "High - 3 similar projects succeeded with this stack"
- Arguments are **factual**: metrics, benchmarks, feedback, official documentation
- Risks are **concrete**: estimated cost, schedule impact, compromised functionality

---

## Convergence criteria

| Situation | Result | Action |
| --- | --- | --- |
| ≥ 3/4 agents converge on the same recommendation | **Strong convergence** | Automatic decision - no additional wave |
| 2/4 agents converge | **Partial convergence** | Wave 2 mandatory |
| < 2/4 agents converge | **Divergence** | Wave 2, then Wave 3 if still < 3/4 |
| After Wave 3, still < 3/4 | **Persistent disagreement** | Orchestrator arbitration or human escalation |

### Criteria for human escalation (vs orchestrator arbitration)

The orchestrator **must** escalate to a human if:

- The decision is irreversible AND both sides' arguments have High confidence
- The disagreement concerns a regulatory topic (AI Act, GDPR) - the orchestrator has no authority
- The financial impact exceeds an estimated 10,000 EUR
- The security risk is classified as critical by the security-engineer

---

## Final output - Consensus verdict

The orchestrator **must** produce this format after every consensus:

```markdown

## CONSENSUS VERDICT - [TOPIC]

**Date** : [DATE]
**Selected decision** : [what is decided, in 1-2 clear sentences]

**Consensus level** : [Strong / Partial / Arbitration]
- Strong: ≥ 3/4 converging agents
- Partial: 2/4 converging, decision after Wave 2
- Arbitration: orchestrator decision after Wave 3

**Agents in agreement** :
- [Agent1][Variant] - [one-line position summary]
- [Agent2][Variant] - [one-line position summary]

**Agents in disagreement** :
- [Agent3][Variant] - [position maintained for traceability]
 → Associated watchpoint: [what must be monitored]

**Arbitration justification** : [if applicable - why this position wins]

**Watchpoints** :
- [risk raised by the minority that must be actively monitored]
- [condition that could invalidate this decision in the future]

**ADR Reference** : [link to the generated ADR if architectural decision]
**Log** : decision recorded in `.github/logs/decisions-<slug>.md` (index updated in `decisions.md`)

```

---

## Notation in DAGs

Wave mode uses the following notation in workflows:

```text

{A ⟳ B ⟳ C} WAVE_1 → SYNTHESIS → {A' ⟳ B' ⟳ C'} WAVE_2 → VERDICT

```

If arbitration is needed after Wave 3:

```text

{A ⟳ B ⟳ C} V1 → SYNTHESIS → {A' ⟳ B' ⟳ C'} V2 → {A'' ⟳ B'' ⟳ C''} V3 → ARBITRATION → VERDICT

```

---

## Anti-patterns to avoid

1. **Soft consensus** - "We agree that it depends" -> FORBIDDEN. Each agent must decide.
2. **Social conformity** - An agent that changes its mind without a new argument in Wave 2 must justify it or receive a score of 2.
3. **Analysis paralysis** - Maximum 3 waves. After that, decide and move forward.
4. **False consensus** - If agents converge on a solution without considering alternatives, the orchestrator challenges them by requesting counter-arguments.
5. **Systematic escalation** - Human escalation is the last resort, not the default mode. The orchestrator must arbitrate in 80%+ of cases.

---

## Cross-stream consensus

When the disagreement opposes agents from **two different streams** (example: security-engineer vs product-manager), the standard 3-wave protocol is not enough: the evaluation criteria diverge fundamentally and none of the conflicting agents has authority over the other's domain.

> This protocol covers conflicts involving **exactly 2 streams**. For conflicts affecting ≥ 3 streams simultaneously, see the [Super-wave](#super-wave---cross-stream-cross-disciplinary-consensus) section.

### Specific process

1. **Identify the streams in conflict** - explicitly name the two opposing streams and the agents representing them.
2. **Appoint one spokesperson per stream** - the corresponding stream orchestrator (example: `orchestrator-governance`, `orchestrator-product`) consolidates its stream's position into one decisive recommendation.
3. **Vote of the relevant stream orchestrators** - each stream orchestrator decides whether it is impacted and votes. Simple majority of the voting orchestrators.
4. **In case of a tie** - mandatory HITL escalation. The orchestrator does not decide alone.
5. **Document the decision** in `.github/logs/decisions-<slug>.md` with the arguments of both sides, including the losing position.

### Fundamental rule

> An unresolved disagreement must **never** be ignored by default. The orchestrator must either conclude the consensus or escalate to a human.

### Veto rights by stream

Some conflicts grant veto power to a stream regardless of the majority vote:

| Stream | Veto right | Triggering condition |
| --- | --- | --- |
| Governance | Blocking veto | P0 security risk or confirmed regulatory violation |
| Tech | Blocking veto | Irreversible technical debt estimated at > 4 weeks |
| Product | Blocking veto | User value regression on a P0 metric |
| Data | Blocking veto | Irreversible data corruption or data loss |

A veto must be **justified in writing** in the consensus verdict. An unjustified veto is void.

### Examples of cross-stream conflicts

| Conflict | Streams | Recommended resolution |
| --- | --- | --- |
| security-engineer vs product-manager (risky feature) | Governance vs Product | Stream orchestrator vote - governance has P0 veto right |
| data-scientist vs backend-dev (ML architecture) | Data vs Tech | Vote + software-architect arbitration in case of tie |
| legal-compliance vs GTMSpecialist (launch) | Governance vs Product | Mandatory HITL escalation |
| frontend-dev vs UXDesigner (UX technical tradeoff) | Tech vs Product | Stream orchestrator vote - escalate in case of tie |

---

## Super-wave - Cross-stream Cross-disciplinary Consensus

Triggered by the main MOE when the decision affects **≥ 3 streams simultaneously**. The MOE dispatches specialists from each stream directly, reading the matrices in the stream profiles (`orchestrator-{tech,product,data,governance}.agent.md`).

### Triggers

| Situation | Streams involved |
| --- | --- |
| Choice of production AI stack | Tech + Data + Governance |
| New shared data model | Tech + Data + Product |
| Feature with regulatory + UX impact | Product + Governance + Tech |
| Global infrastructure migration | Tech + Data + FinOps (Governance) |

### Flow

```text

Inter-stream wave 1:
 ┌─ Tech stream (specialists selected via tech profile) → Technical stream synthesis
 ├─ Product stream (specialists selected via product profile) → Product stream synthesis
 ├─ Data stream (specialists selected via data profile) → Data/AI stream synthesis
 └─ Governance stream (specialists selected via governance profile) → Governance stream synthesis

Main MOE → Meta-synthesis (convergences, inter-stream conflicts, dependencies)

Inter-stream wave 2 (if conflict):
 Specialists from each stream answer specifically to the identified conflicts

MOE verdict: decision with execution plan coordinated by stream

```

### Stream synthesis format

```markdown

## [STREAM] Synthesis - Super-wave [TOPIC]

**Stream position** : [decisive recommendation in 1 sentence]

**Prerequisites from my stream** :
1. [non-negotiable prerequisite #1]
2. [non-negotiable prerequisite #2]

**Dependencies on other streams** :
- From [Stream X] : [what I need]

**Risk if ignored** : [concrete consequence if my stream is not consulted]

```

### Super-wave arbitration

If streams still diverge after Inter-stream Wave 2, the main MOE arbitrates by applying:

1. Priority: Governance > Tech > Data > Product on compliance/security questions
2. Priority: Product > Tech > Data > Governance on user value questions
3. Human escalation if Governance ↔ Product conflict on an irreversible decision

---

## Example requests triggering consensus

1. `@orchestrator consensus: PostgreSQL vs MongoDB for the catalog service, 50M items, 90% reads / 10% writes`
2. `@orchestrator consensus: OAuth2 + OIDC authentication vs session-based for the public app`
3. `@orchestrator consensus: EU AI Act classification of the product recommendation system`
4. `@orchestrator consensus: Monorepo vs polyrepo for the 4 microservices in the order domain`
