---
name: orchestrator-governance
user-invocable: false
description: "Governance lane reference — non-invocable internal profile read by the orchestrator to route security, compliance, risk, AI ethics, and FinOps specialists"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Lane Profile: Governance

**Available agents**: security-engineer, legal-compliance, ai-ethics-governance, risk-manager, finops-engineer, change-management, architecture-reviewer, accessibility-engineer, project-controller

> **Usage**: This profile is **read by the orchestrator** during planning. It is not invocable itself. It defines the proactive mandatory triggers and veto criteria that the orchestrator applies directly.

## Proactive Triggers Applied During Planning

| Event detected in the task | Orchestrator action |
| --- | --- |
| Feature involving personal data (`userId`, `email`, `phone`, `ip`, `address`, communication content, session identifier) | Involve legal-compliance (DPIA) + security-engineer |
| AI model moved to production | Involve ai-ethics-governance (model card) + risk-manager |
| Cloud budget overrun above 20% | Involve finops-engineer |
| Major architecture change | Involve architecture-reviewer + security-engineer |
| Public-facing UI or UX feature | Involve accessibility-engineer (WCAG audit) |

## Blocking Alerts and Vetoes Applied by the Orchestrator

| Alert | Priority | Immediate orchestrator action |
| --- | --- | --- |
| Critical CVE in a dependency | P0 | Block merge, involve security-engineer, patch in under 4 hours |
| Personal-data leak | P0 | Full stop, involve legal-compliance, CNIL notification in under 72 hours |
| AI Act non-compliance detected | P1 | Suspend feature, involve legal-compliance + ai-ethics-governance, remediate in under 48 hours |
| Risk score above the critical threshold | P1 | Involve risk-manager, trigger multi-agent consensus if impact exceeds two weeks |

---

## Governance Dispatch Matrix

| Task | Primary agents | Secondary agents | Recommended cross-lane agents |
| --- | --- | --- | --- |
| Application security audit | security-engineer | architecture-reviewer | backend-dev (fixes), qa-engineer (tests for the fixes), code-reviewer |
| DPIA for personal data | legal-compliance | risk-manager | backend-dev (protection implementation), database-engineer (anonymization) |
| Model card and AI red teaming | ai-ethics-governance | risk-manager | ml-engineer (model adjustments), prompt-engineer (robustness), data-scientist (bias metrics) |
| FinOps audit | finops-engineer | — | cloud-engineer (rightsizing), devops-engineer (CI optimization), infra-architect |
| Cross-cutting architecture review | architecture-reviewer | security-engineer | software-architect, performance-engineer, database-engineer |
| Accessibility compliance (RGAA/WCAG) | accessibility-engineer | — | frontend-dev (fixes), ux-ui-designer (journey redesign) |
| Change-management plan | change-management | scrum-master (via orchestrator) | proxy-po, tech-writer (training material), product-strategist |
| Global risk mapping | risk-manager | legal-compliance, ai-ethics-governance | software-architect, devops-engineer, project-controller |

---

## Cross-Lane Signals

When a governance task should trigger agents from other lanes:

| Signal detected in the task | Lane | Agents to include |
| --- | --- | --- |
| Audit identifies vulnerabilities that must be fixed | Tech | backend-dev/frontend-dev + qa-engineer |
| DPIA reveals data that must be anonymized | Data | database-engineer + data-engineer |
| Accessibility non-compliance detected | Tech + Product | frontend-dev + ux-ui-designer |
| Model card reveals bias that must be corrected | Data | ml-engineer + data-scientist |
| FinOps audit recommends rightsizing | Tech | cloud-engineer + devops-engineer |
| Risk requires a roadmap change | Product | product-strategist + proxy-po |

---

## Veto Protocol Applied by the Orchestrator

When a blocking alert is detected, the orchestrator:

1. Writes a formal justification with the violated standard, regulatory article, or referenced CVE
2. Blocks the affected merge or deployment
3. Creates a GitHub issue with the `governance-blocker` label
4. Proposes a remediation path with an estimated timeline through the relevant agent
5. Re-validates after correction before lifting the block

---

## Consolidation Format Produced by the Orchestrator After Governance Dispatch

> When the orchestrator has dispatched multiple agents from the governance lane, it consolidates the outputs in this format before journaling. Each invoked agent must have produced its Analysis / Recommendation / Alternatives / Risks block.

```markdown

## Governance Summary — [task name]

### Agents involved
- [agent]: [mission] -> [status]

### Identified risks
| Risk | Probability | Impact | Treatment |
| --- | --- | --- | --- |
| [risk] | [P1-P4] | [I1-I4] | [accepted / mitigated / avoided] |

### Compliance
- GDPR: [compliant / action required]
- AI Act: [compliant / action required / N/A]
- WCAG: [AA reached / gaps identified]

### Issued vetoes
- [list or "None"]

### Required actions before deployment
- [list or "None"]

```
