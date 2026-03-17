---
name: orchestrator-governance
user-invocable: false
description: "Governance lane reference — non-invocable internal profile read by the orchestrator to route security, compliance, risk, AI ethics, and FinOps specialists"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Lane Profile: Governance

**Available agents**: SecurityEngineer, LegalCompliance, AIEthicsGovernance, RiskManager, FinOpsEngineer, ChangeManagement, ArchitectureReviewer, AccessibilityEngineer, ProjectController

> **Usage**: This profile is **read by the orchestrator** during planning. It is not invocable itself. It defines the proactive mandatory triggers and veto criteria that the orchestrator applies directly.

## Proactive Triggers Applied During Planning

| Event detected in the task | Orchestrator action |
| --- | --- |
| Feature involving personal data (`userId`, `email`, `phone`, `ip`, `address`, communication content, session identifier) | Involve LegalCompliance (DPIA) + SecurityEngineer |
| AI model moved to production | Involve AIEthicsGovernance (model card) + RiskManager |
| Cloud budget overrun above 20% | Involve FinOpsEngineer |
| Major architecture change | Involve ArchitectureReviewer + SecurityEngineer |
| Public-facing UI or UX feature | Involve AccessibilityEngineer (WCAG audit) |

## Blocking Alerts and Vetoes Applied by the Orchestrator

| Alert | Priority | Immediate orchestrator action |
| --- | --- | --- |
| Critical CVE in a dependency | P0 | Block merge, involve SecurityEngineer, patch in under 4 hours |
| Personal-data leak | P0 | Full stop, involve LegalCompliance, CNIL notification in under 72 hours |
| AI Act non-compliance detected | P1 | Suspend feature, involve LegalCompliance + AIEthicsGovernance, remediate in under 48 hours |
| Risk score above the critical threshold | P1 | Involve RiskManager, trigger multi-agent consensus if impact exceeds two weeks |

---

## Governance Dispatch Matrix

| Task | Primary agents | Secondary agents | Recommended cross-lane agents |
| --- | --- | --- | --- |
| Application security audit | SecurityEngineer | ArchitectureReviewer | BackendDev (fixes), QAEngineer (tests for the fixes), CodeReviewer |
| DPIA for personal data | LegalCompliance | RiskManager | BackendDev (protection implementation), DatabaseEngineer (anonymization) |
| Model card and AI red teaming | AIEthicsGovernance | RiskManager | MLEngineer (model adjustments), PromptEngineer (robustness), DataScientist (bias metrics) |
| FinOps audit | FinOpsEngineer | — | CloudEngineer (rightsizing), DevOpsEngineer (CI optimization), InfraArchitect |
| Cross-cutting architecture review | ArchitectureReviewer | SecurityEngineer | SoftwareArchitect, PerformanceEngineer, DatabaseEngineer |
| Accessibility compliance (RGAA/WCAG) | AccessibilityEngineer | — | FrontendDev (fixes), UXUIDesigner (journey redesign) |
| Change-management plan | ChangeManagement | ScrumMaster (via orchestrator) | ProxyPO, TechWriter (training material), ProductStrategist |
| Global risk mapping | RiskManager | LegalCompliance, AIEthicsGovernance | SoftwareArchitect, DevOpsEngineer, ProjectController |

---

## Cross-Lane Signals

When a governance task should trigger agents from other lanes:

| Signal detected in the task | Lane | Agents to include |
| --- | --- | --- |
| Audit identifies vulnerabilities that must be fixed | Tech | BackendDev/FrontendDev + QAEngineer |
| DPIA reveals data that must be anonymized | Data | DatabaseEngineer + DataEngineer |
| Accessibility non-compliance detected | Tech + Product | FrontendDev + UXUIDesigner |
| Model card reveals bias that must be corrected | Data | MLEngineer + DataScientist |
| FinOps audit recommends rightsizing | Tech | CloudEngineer + DevOpsEngineer |
| Risk requires a roadmap change | Product | ProductStrategist + ProxyPO |

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
