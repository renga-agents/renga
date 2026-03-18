---
name: orchestrator-product
user-invocable: false
description: "Product lane reference — non-invocable internal profile read by the orchestrator to route product, UX/UI, business, analytics, and GTM specialists"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Lane Profile: Product

**Available agents**: proxy-po, product-manager, product-analytics, product-strategist, ux-ui-designer, ux-writer, go-to-market-specialist, scrum-master, tech-writer, business-analyst, change-management

**Plugin agents (game-studio)**: CreativeDirector, LevelDesigner, NarrativeDesigner, GameProducer — *available with the `game-studio` plugin in `_plugins/game-studio/`*

> **Usage**: This profile is **read by the orchestrator** during planning to select agents and define dispatch order. It is not invocable itself. The orchestrator dispatches the specialists directly at depth 1.

## Escalation Criteria Detected by the Orchestrator

| Situation | Orchestrator action |
| --- | --- |
| De-prioritization decision with business impact above two weeks | Direct orchestrator arbitration |
| Disagreement between product-strategist and proxy-po on priority | Involve architecture-reviewer or trigger consensus |
| Feature impacts GDPR or the AI Act | Involve legal-compliance from the governance lane |
| Technical feasibility estimate required | Involve backend-dev or software-architect |

---

## Product Dispatch Matrix

| Task | Primary agents | Secondary agents | Recommended cross-lane agents |
| --- | --- | --- | --- |
| MVP definition for a feature | product-manager | proxy-po (stories), product-strategist (vision), ux-ui-designer (wireframes) | software-architect (feasibility), security-engineer (personal data) |
| Cross-functional feature steering | product-manager | proxy-po (backlog), ux-ui-designer (journey), tech-writer (delivery) | backend-dev/frontend-dev, qa-engineer, go-to-market-specialist |
| Adoption or funnel analysis | product-analytics | product-manager (context), product-strategist (roadmap reading) | data-scientist (advanced analysis), data-engineer (tracking), go-to-market-specialist |
| Visual identity or brand design | CreativeDirector | ux-ui-designer (system rollout), ux-writer (brand voice) | frontend-dev (implementation), AnimationsEngineer (motion design) |
| Creative brief for campaign or launch | CreativeDirector | go-to-market-specialist (messaging), ux-writer (copywriting) | tech-writer (assets), change-management |
| Product visual-consistency audit | CreativeDirector | ux-ui-designer (components), AnimationsEngineer (motion) | accessibility-engineer (WCAG), performance-engineer (asset weight) |
| Feature launch and go-to-market | go-to-market-specialist | product-manager (readiness), ux-writer (copywriting), tech-writer (release notes) | devops-engineer (deployment), change-management, product-analytics |
| Product retrospective | scrum-master | proxy-po (backlog adjustment) | project-controller (budget), architecture-reviewer |
| User documentation | tech-writer | ux-writer (microcopy) | accessibility-engineer (accessible docs), frontend-dev (screenshots) |
| Business process analysis | business-analyst | proxy-po (backlog impact) | software-architect (translation into architecture), data-engineer (pipelines) |
| Change management | change-management | scrum-master, tech-writer | proxy-po, legal-compliance if GDPR is involved |
| OKR and roadmap strategy | product-strategist | product-analytics (metrics), proxy-po (stories translation) | software-architect (feasibility), finops-engineer (budget) |

---

## Cross-Lane Signals

When a product task should trigger agents from other lanes:

| Signal detected in the task | Lane | Agents to include |
| --- | --- | --- |
| Feature requires an API or code implementation | Tech | software-architect + backend-dev/frontend-dev |
| Story involves personal data | Governance | legal-compliance + security-engineer |
| Feature includes scoring, AI, or recommendation logic | Data | ai-product-manager + ml-engineer |
| UX redesign impacts accessibility | Governance | accessibility-engineer |
| Launch impacts cloud budget | Governance | finops-engineer |
| Change affects CI/CD | Tech | devops-engineer |
| Feature must be steered across multiple teams | Product | product-manager |
| Decision relies on adoption, funnel, or retention signals | Product | product-analytics |
| Prompt or agent workflow must change | Data | prompt-engineer |

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
