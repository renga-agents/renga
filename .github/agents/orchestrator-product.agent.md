---
name: orchestrator-product
user-invocable: false
description: "Product lane reference — non-invocable internal profile read by the orchestrator to route product, UX/UI, business, analytics, and GTM specialists"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Lane Profile: Product

**Available agents**: ProxyPO, ProductManager, ProductAnalytics, ProductStrategist, UXUIDesigner, UXWriter, GoToMarketSpecialist, ScrumMaster, TechWriter, BusinessAnalyst, ChangeManagement

**Plugin agents (game-studio)**: CreativeDirector, LevelDesigner, NarrativeDesigner, GameProducer — *available with the `game-studio` plugin in `_plugins/game-studio/`*

> **Usage**: This profile is **read by the orchestrator** during planning to select agents and define dispatch order. It is not invocable itself. The orchestrator dispatches the specialists directly at depth 1.

## Escalation Criteria Detected by the Orchestrator

| Situation | Orchestrator action |
| --- | --- |
| De-prioritization decision with business impact above two weeks | Direct orchestrator arbitration |
| Disagreement between ProductStrategist and ProxyPO on priority | Involve ArchitectureReviewer or trigger consensus |
| Feature impacts GDPR or the AI Act | Involve LegalCompliance from the governance lane |
| Technical feasibility estimate required | Involve BackendDev or SoftwareArchitect |

---

## Product Dispatch Matrix

| Task | Primary agents | Secondary agents | Recommended cross-lane agents |
| --- | --- | --- | --- |
| MVP definition for a feature | ProductManager | ProxyPO (stories), ProductStrategist (vision), UXUIDesigner (wireframes) | SoftwareArchitect (feasibility), SecurityEngineer (personal data) |
| Cross-functional feature steering | ProductManager | ProxyPO (backlog), UXUIDesigner (journey), TechWriter (delivery) | BackendDev/FrontendDev, QAEngineer, GoToMarketSpecialist |
| Adoption or funnel analysis | ProductAnalytics | ProductManager (context), ProductStrategist (roadmap reading) | DataScientist (advanced analysis), DataEngineer (tracking), GoToMarketSpecialist |
| Visual identity or brand design | CreativeDirector | UXUIDesigner (system rollout), UXWriter (brand voice) | FrontendDev (implementation), AnimationsEngineer (motion design) |
| Creative brief for campaign or launch | CreativeDirector | GoToMarketSpecialist (messaging), UXWriter (copywriting) | TechWriter (assets), ChangeManagement |
| Product visual-consistency audit | CreativeDirector | UXUIDesigner (components), AnimationsEngineer (motion) | AccessibilityEngineer (WCAG), PerformanceEngineer (asset weight) |
| Feature launch and go-to-market | GoToMarketSpecialist | ProductManager (readiness), UXWriter (copywriting), TechWriter (release notes) | DevOpsEngineer (deployment), ChangeManagement, ProductAnalytics |
| Product retrospective | ScrumMaster | ProxyPO (backlog adjustment) | ProjectController (budget), ArchitectureReviewer |
| User documentation | TechWriter | UXWriter (microcopy) | AccessibilityEngineer (accessible docs), FrontendDev (screenshots) |
| Business process analysis | BusinessAnalyst | ProxyPO (backlog impact) | SoftwareArchitect (translation into architecture), DataEngineer (pipelines) |
| Change management | ChangeManagement | ScrumMaster, TechWriter | ProxyPO, LegalCompliance if GDPR is involved |
| OKR and roadmap strategy | ProductStrategist | ProductAnalytics (metrics), ProxyPO (stories translation) | SoftwareArchitect (feasibility), FinOpsEngineer (budget) |

---

## Cross-Lane Signals

When a product task should trigger agents from other lanes:

| Signal detected in the task | Lane | Agents to include |
| --- | --- | --- |
| Feature requires an API or code implementation | Tech | SoftwareArchitect + BackendDev/FrontendDev |
| Story involves personal data | Governance | LegalCompliance + SecurityEngineer |
| Feature includes scoring, AI, or recommendation logic | Data | AIProductManager + MLEngineer |
| UX redesign impacts accessibility | Governance | AccessibilityEngineer |
| Launch impacts cloud budget | Governance | FinOpsEngineer |
| Change affects CI/CD | Tech | DevOpsEngineer |
| Feature must be steered across multiple teams | Product | ProductManager |
| Decision relies on adoption, funnel, or retention signals | Product | ProductAnalytics |
| Prompt or agent workflow must change | Data | PromptEngineer |

---

## Consolidation Format Produced by the Orchestrator After Product Dispatch

> When the orchestrator has dispatched multiple agents from the product lane, it consolidates the outputs in this format before journaling.

```markdown

## Product Summary — [task name]

### Agents involved
- [agent]: [mission] -> [status]

### Product decisions
- [decision]: [justification]

### User stories / acceptance criteria
- [as a ...] [I want ...] [so that ...]

### Required coordination points with Tech or Governance
- [point or "None"]

```
