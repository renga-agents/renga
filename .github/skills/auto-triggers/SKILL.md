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
| New AI processing via external API or rules-based automation (no custom model training) | AIEthicsGovernance | sequential (before deployment) |
| Hosting or country change | LegalCompliance + RiskManager | parallel |
| Custom AI model: training, fine-tuning, or deployment (includes semantic search, embeddings, NLP pipelines, recommendation engines — any custom ML pipeline, not just an API call) | AIEthicsGovernance + MLOpsEngineer | parallel |
| Delivery reaching end-users (researchers, business users, customers — anyone who is not a developer on the project, regardless of their technical expertise) | ChangeManagement | sequential (before release) |
| Cloud architecture / sizing decision | FinOpsEngineer + CloudEngineer | parallel |
| New exposure surface (endpoint, auth, third-party integration) | SecurityEngineer | wave 0 if QAEngineer is planned (ERR-008) |
| New endpoint or public API contract | APIDesigner + SoftwareArchitect | wave 0 |
| New service, major feature, or multi-phase module (L2+) without validated user stories | ProxyPO | wave 1 (after Wave 0 architecture and product decisions — translates architecture outcomes into user stories; in plan-only mode: proxy-po must appear in Wave 1 of the DAG even if story writing happens at dispatch time) |
| Multi-phase roadmap or plan with ≥ 3 waves (L3+) | ProductManager | wave 0 (parallel) — validates phase sequencing by user value, defines success metrics per phase, arbitrates scope vs engineering constraints |
| **L4 task** OR multi-wave L3+ execution with ≥ 3 agent domains | ScrumMaster | **mandatory for every L4 task** — **Wave 0** (parallel — defines DoD for all waves + phase gate criteria upfront, before agents start) ‖ **final synthesis wave** (go/no-go gate, inter-wave impediment review, retrospective). Both placements are required. Not optional. Excluding scrum-master from Wave 0 or the final synthesis wave without a scratchpad waiver = ERR-017. |
| New table or DB migration | DatabaseEngineer | parallel wave 1 |
| New service or SLO change | ObservabilityEngineer + PerformanceEngineer | parallel — ObservabilityEngineer: wave 0 or 1; PerformanceEngineer: wave 3 (load testing, SLO validation pre-release) |
| Implementation wave with agent-generated code (L2+) | CodeReviewer | wave immediately after implementation — before the release/validation wave |
| Regulated platform deployment (health, financial, biometric, or legally sensitive data — HDS, HIPAA, RGPD, PCI-DSS, etc.) | LegalCompliance + SecurityEngineer | final validation wave — mandatory pre-production sign-off before release |
| Code using a third-party library (not simply reading existing code) | — | _(tool, not agent)_ context7 MCP required before generation — verify package API and version before coding |
| Critical validation MCP tool unavailable (ERR-017) | — | _(seiji handles directly)_ escalate to user — **blocking** |
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
