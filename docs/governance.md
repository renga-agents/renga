# Team Governance

> **Audience**: developers and tech leads using renga on a shared project with at least 2 contributors
> **Prerequisite**: read [getting-started.md](getting-started.md) and understand the `.renga.yml` structure
> **Last updated**: 2026-03-17
> **Estimated reading time**: 5 min

This document describes the process for teams using renga on shared projects. Each section answers a concrete question: *how do you change framework configuration without breaking other contributors' work?*

---

## Table of Contents

- [Waivers — Disabling guardrails](#waivers--disabling-guardrails)
- [Commit rules for renga changes](#commit-rules-for-renga-changes)
- [Adding a new custom agent](#adding-a-new-custom-agent)
- [Consensus protocol](#consensus-protocol)
- [CODEOWNERS — Protecting critical paths](#codeowners--protecting-critical-paths)
- [HITL escalation — Human intervention](#hitl-escalation--human-intervention)

---

## Waivers — Disabling Guardrails

### What Is a Waiver?

A **waiver** is an explicit declaration in `.renga.yml` that disables a governance rule for a specific project. Example: disabling the mandatory SecurityEngineer brief during a prototype phase.

**A waiver is not trivial**. It removes a guardrail designed to protect the team. A silent deactivation without justification or planned review is one of the main sources of governance debt.

### Mandatory Process (4 Steps)

Any rule deactivation **must** follow these 4 steps, in order:

1. **Fill the `reason` field** in `.renga.yml` with one sentence justifying the deactivation *for this project, at this moment*
2. **Document the decision** in `.github/logs/decisions.md`, referencing the rule number, rationale, and approver
3. **Require PR approval** from a second developer, ideally enforced through `CODEOWNERS` on `.renga.yml`
4. **Set a review date**. The `expires` field is mandatory. A waiver without an expiration date must be rejected

### Correct vs Incorrect Example

```yaml

# ✅ Correctly documented waiver
waivers:
  - rule: "ERR-014"
    reason: "Solo project — reduced multi-lane coverage accepted until a second developer joins"
    expires: "2026-09-01"
    approved_by: "@lead-dev"

# ❌ Incorrect waiver — no reason, no expiration, no approver
waivers:
  - rule: "ERR-014"

```

### Periodic Review

At each sprint, the team checks:

- Waivers whose `expires` date is near or already exceeded
- Whether the rationale is still valid, for example a prototype has moved to production so the security waiver should be removed
- Whether a waiver can be removed instead of renewed

> A waiver renewed without reevaluation is a warning sign. If a rule is never applicable to the project, prefer changing the underlying governance model rather than renewing the waiver indefinitely.

---

## Commit Rules for renga Changes

Any change to framework configuration files such as `.renga.yml`, `.github/agents/`, or `.github/instructions/` should follow these 5 rules:

1. **One commit per change type**: governance, agent, instruction, and `.renga.yml` changes belong in separate commits
2. Use the **`chore(governance):` prefix** for any rule or waiver change
3. Use the **`docs(agents):` prefix** for a new agent or a change to an existing agent
4. **Commit body required** when the diff changes a waiver or a threshold. Explain why in 1 to 2 lines
5. **Do not mix** application refactoring and governance changes in the same commit

```bash

# ✅ Correct examples
git commit -m "chore(governance): add waiver ERR-014 for solo prototype phase"
git commit -m "docs(agents): add custom billing-assistant agent"

# ❌ Incorrect examples
git commit -m "fix: various changes including new agent and bug fix"

```

> For multiline commit messages, use `git commit -F /tmp/commit_msg.txt` — see the reference [commit-discipline.md](../.github/agents/_references/commit-discipline.md).

---

## Adding a New Custom Agent

To add a project-specific agent such as `billing-assistant`, follow these 3 steps.

### Step 1 — Create the Agent File

Create `.github/agents/billing-assistant.agent.md` using the standard format:

```markdown

---
name: billing-assistant
description: "Short description of what the agent does"
tools: ["read", "edit"]
---
# Billing Assistant

[Agent instructions...]

```

Use an existing agent, for example `.github/agents/backend-dev.agent.md`, as a format reference.

### Step 2 — Validate with `validate_agents.py`

```bash

python scripts/validate_agents.py

```

Fix every reported error before continuing. A clean validation is required before opening a PR.

### Step 3 — Declare It in `.renga.yml` and Document It

In `.renga.yml`, add the agent to the `agents.include` list:

```yaml

agents:
  mode: "whitelist"
  include:
    - billing-assistant  # Custom agent — see decisions.md#DEC-XXX

```

Then create an entry in `.github/logs/decisions.md`:

```markdown

## DEC-XXX — Add billing-assistant agent

**Date**: 2026-03-17
**Decision**: Create a custom agent to automate invoice processing
**Justification**: Recurring task, 3 hours per week, not covered by standard agents
**Approver**: @lead-dev

```

---

## Consensus Protocol

When a critical decision requires input from several agents, such as irreversible architecture, security, regulation, or persistent disagreement, the orchestrator can trigger a **consensus protocol**.

### Trigger

```text

@orchestrator consensus: Should we migrate from REST to GraphQL?

```

### How It Works

1. The orchestrator identifies the agents affected by the decision
2. Each agent issues a **reasoned opinion** with a recommendation, for, against, or neutral
3. The orchestrator consolidates those opinions and highlights convergences and disagreements
4. If disagreement persists, it escalates to the human user, HITL

### Typical Use Cases

- Irreversible architecture choice, monolith vs microservices
- Security decision with performance impact
- Technical arbitration with compliance implications
- Disagreement between two agents on the same question

> Complete reference: see skill `consensus-protocol` (`.github/skills/consensus-protocol/SKILL.md`)

---

## CODEOWNERS — Protecting Critical Paths

The `CODEOWNERS` file protects governance files against unreviewed changes. Any PR touching those paths **requires approval** from the designated owners.

### Recommended Protected Paths

| Path | Owner | Rationale |
| --- | --- | --- |
| `.renga.yml` | `@lead-dev` | Central configuration — one change impacts all agents |
| `.github/agents/*.agent.md` | `@lead-dev` | Changing a core agent changes framework behavior |
| `.github/agents/_config/` | `@lead-dev` | LLM model configuration |
| `.github/agents/_references/` | `@lead-dev` | Internal reference documentation |
| `.github/instructions/` | `@lead-dev` | Coding rules — global impact on generated code quality |

### Example `CODEOWNERS` File

```text

# renga governance
.renga.yml                    @lead-dev
.github/agents/                    @lead-dev
.github/instructions/              @lead-dev

```

### Why It Matters

Without `CODEOWNERS`, any contributor can:

- Disable a security guardrail by modifying an agent
- Add a waiver without approval
- Change criticality thresholds without review

`CODEOWNERS` turns those changes into **mandatory reviews**.

---

## HITL Escalation — Human Intervention

HITL escalation, Human-In-The-Loop, is triggered automatically by the orchestrator when a decision exceeds the mandate of the agents.

### When Does the Orchestrator Escalate?

| Situation | Trigger | What happens |
| --- | --- | --- |
| **L4 task** | Critical or irreversible decision | The orchestrator presents the plan and waits for approval before execution |
| **Disagreement** | Unresolved disagreement after consensus | The orchestrator presents the divergent positions and asks for arbitration |
| **Sensitive data** | Detection of personal data, secrets, or credentials | The affected agent pauses and asks for confirmation |
| **Production impact** | Database schema, infrastructure, or deployment change | The orchestrator asks for an explicit green light |
| **Out of scope** | The agent detects that the request exceeds its domain of expertise | The agent states its limits and asks for guidance |

### Escalation Format

When the orchestrator escalates, it provides:

1. **The context**: what task is in progress and why escalation is necessary
2. **The options**: possible choices and their tradeoffs
3. **Its recommendation**: what it would do if the decision were its own
4. **The question**: a closed or multiple-choice question to minimize user effort

### Resuming After Escalation

After your reply, the orchestrator resumes execution with the decision treated as a fixed constraint. The decision is logged in `.github/logs/decisions-<slug>.md`.
