---
name: auto-triggers
description: "Identifies automatic triggers for specialized agents based on conditions detected in the task (personal data, security, AI, compliance)."
argument-hint: "Describe the task or change to analyze in order to detect the required triggers"
user-invocable: true

# Skill: Automatic Triggers

This skill identifies the conditions that require automatically consulting specialized agents. These triggers are **non-negotiable** and apply as soon as the condition is detected.

---

## Automatic Trigger Table

| Detected condition | Added agents | Mode |
| --- | --- | --- |
| Personal data **being changed** (creation, modification, exposure, or transmission of `userId`, `email`, `phone`, `ip`, `address` to new storage or a third party) | LegalCompliance + RiskManager | parallel |
| Personal data **already exposed** to unauthorized parties or found in logs/external systems (breach, leak, misconfiguration) | LegalCompliance + RiskManager + SecurityEngineer | **L4 — human escalation mandatory** — GDPR 72h notification window may be running |
| New AI processing, scoring, or automated decision-making | AIEthicsGovernance | sequential (before deployment) |
| Hosting or country change | LegalCompliance + RiskManager | parallel |
| AI model deployment/modification | AIEthicsGovernance + MLOpsEngineer | parallel |
| Delivery affecting non-technical users | ChangeManagement | sequential (before release) |
| Cloud architecture / sizing decision | FinOpsEngineer | parallel (with CloudEngineer) |
| New exposure surface (endpoint, auth, third-party integration) | SecurityEngineer | wave 0 if QAEngineer is planned (ERR-008) |
| New endpoint or public API contract | APIDesigner + SoftwareArchitect | wave 0 |
| New service, major feature, or multi-phase module (L2+) without validated user stories | ProxyPO | wave 1 (after Wave 0 architecture and product decisions — translates architecture outcomes into user stories) |
| Multi-phase roadmap or plan with ≥ 3 waves (L3+) | ProductManager | wave 0 (parallel) — validates phase sequencing by user value, defines success metrics per phase, arbitrates scope vs engineering constraints |
| Multi-wave execution (L3+) with cross-functional coordination across ≥ 3 agent domains | ScrumMaster | synthesis wave — defines Definition of Done per wave, ceremony structure, inter-wave impediment escalation protocol |
| New table or DB migration | DatabaseEngineer | parallel wave 1 |
| New service or SLO change | ObservabilityEngineer | parallel |
| Code using a third-party library (not simply reading existing code) | context7 MCP | before generation |
| Critical validation MCP tool unavailable (ERR-017) | Orchestrator: notify the user | **blocking** |
| Incident response or security breach | Load skill `handoff-protocol` during PLANNING — apply the incident chain order: `IncidentCommander → ObservabilityEngineer → Debugger → DevOpsEngineer → IncidentCommander` | sequential (defines wave order) |
| Product feature requiring vision → prioritization → specs → dev | Load skill `handoff-protocol` during PLANNING — apply the product chain: `ProductStrategist → ProductManager → ProxyPO → Devs` | sequential |

---

## Triggered Agent Waiver Rule (ERR-017)

An agent that appears in the **Activated triggers** list is non-negotiable. It MUST be assigned to a wave in the DAG. The only exception is an explicit waiver, which requires:

1. A one-line justification in the scratchpad trigger analysis (why the condition does not actually apply)
2. The waiver logged under **Non-applicable triggers**, not silently omitted from the wave plan

❌ Triggering an agent in the analysis and then excluding it in the coverage verification without a scratchpad waiver = ERR-017 (silent omission).

---

## Proportionality Principle

The trigger must be proportional to the **actual risk**, defined by the combination of:

- **Mutation**: are the data being created, modified, or deleted?
- **Exposure**: are the data being transmitted to a third party or exposed publicly?
- **Sensitivity**: are they sensitive data (health, finance, biometrics)?

Reading a `userId` to display a profile is not the same as sending an `email` to a third-party service.

---

## Automatic Human Escalation

| Trigger | Reason |
| --- | --- |
| Potentially exposed secret | Security incident |
| Sensitive or regulated personal data | Legal risk |
| Irreversible decision, rollback > 2 person-weeks | Strategic risk |
| SecurityEngineer ↔ LegalCompliance disagreement | Cross-functional risk |
| High-risk or ambiguous AI system in production | Stronger governance required |
| Unexpected budget impact | Financial risk |
| Framework choice with viable alternatives, migration > 1 person-week (ERR-016) | Irreversible architecture |
| Authentication or authorization architecture (SSO provider, token strategy JWT/opaque, session store, 2FA model) with viable alternatives | Irreversible at scale — L4 candidate |
| Critical validation tool unavailable (ERR-017) | Delivery without validation |

---

## Circuit Breaker: Failing Agents

| Situation | Action |
| --- | --- |
| Agent fails 2 consecutive times | Human escalation + log. Do not retry a 3rd time. |
| Contradictory outputs across retries | Consensus (if ≥ 2 agents) or HITL escalation |
| No agent available in the required lane | HITL escalation required |

---

## Mandatory Agents for Visual/Interactive Deliverables (ERR-020)

For any deliverable classified as `L3+` (video game, interactive animation, complex dashboard, highly visual UI):

**Mandatory**: CreativeDirector (art direction) + ux-ui-designer (UI consistency) + performance-engineer (frame rate and memory)

**Recommended**: accessibility-engineer (if broad audience) + frontend-dev (cross-browser compatibility)

**Additional requirement**: the DAG must include at least one wave dedicated to **visual review** (annotated screenshots, graphic consistency checks, polish).

---

## Expected Output Format

```

=== TRIGGER ANALYSIS ===

Activated triggers:
  ✅ SecurityEngineer — new exposure surface (POST /api/v1/... endpoint)
  ✅ DatabaseEngineer — new 'notifications' table

Non-applicable triggers:
  ⏭️ LegalCompliance — no personal data mutation
  ⏭️ AIEthicsGovernance — no AI processing

Escalation required: no

```
