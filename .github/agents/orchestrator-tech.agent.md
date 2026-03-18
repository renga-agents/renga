---
name: orchestrator-tech
user-invocable: false
description: "Tech lane reference — non-invocable internal profile read by the orchestrator to route backend, frontend, QA, DevOps, and infrastructure specialists"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Lane Profile: Tech

**Available agents**: backend-dev, frontend-dev, fullstack-dev, mobile-dev, qa-engineer, api-designer, performance-engineer, devops-engineer, incident-commander, infra-architect, cloud-engineer, platform-engineer, observability-engineer, chaos-engineer, security-engineer, code-reviewer, software-architect, Debugger, accessibility-engineer

**Plugin agents (game-studio)**: AnimationsEngineer, GameAssetGenerator, AudioGenerator, GameDeveloper, GameBalancer — *available with the `game-studio` plugin in `_plugins/game-studio/`*

> **Usage**: This profile is **read by the orchestrator** during planning to select agents and define dispatch order. It is not invocable itself. The orchestrator dispatches the specialists directly at depth 1.

## Escalation Criteria Detected by the Orchestrator

| Situation | Orchestrator action |
| --- | --- |
| Cross-domain architecture conflict | Involve data-scientist + software-architect in sequence |
| Critical vulnerability detected | Suspend the flow, involve security-engineer + risk-manager |
| Feature impacts GDPR or the AI Act | Involve legal-compliance before delivery |
| Quality versus deadline disagreement | Involve architecture-reviewer for arbitration |

---

## Tech Dispatch Matrix

| Task | Primary agents | Parallel agents | Recommended cross-lane agents |
| --- | --- | --- | --- |
| New fullstack feature | fullstack-dev | qa-engineer, api-designer (if public API) | ux-ui-designer, accessibility-engineer, tech-writer, proxy-po if specs are missing |
| Backend-only feature | backend-dev | qa-engineer | security-engineer, tech-writer |
| Frontend-only feature | frontend-dev | accessibility-engineer, qa-engineer | ux-ui-designer, ux-writer, CreativeDirector if visual identity is involved |
| CI/CD pipeline | devops-engineer | platform-engineer | security-engineer, observability-engineer |
| Performance optimization | performance-engineer | observability-engineer | software-architect, database-engineer if queries are involved |
| Cloud deployment | cloud-engineer | infra-architect | security-engineer, finops-engineer, devops-engineer |
| Resilience testing | chaos-engineer | observability-engineer | risk-manager, software-architect |
| Public API | api-designer | backend-dev, qa-engineer | tech-writer, legal-compliance if personal data is involved, security-engineer |
| Interactive animation or game experience | AnimationsEngineer | frontend-dev, qa-engineer | CreativeDirector, ux-ui-designer, performance-engineer, accessibility-engineer |
| Debugging or investigation | Debugger | — | qa-engineer (reproduction), observability-engineer (tracing) |
| Production incident | incident-commander | Debugger, observability-engineer | devops-engineer (mitigation), security-engineer if security-related, tech-writer (communication) |
| Refactor or migration | software-architect | backend-dev, frontend-dev | code-reviewer, qa-engineer, tech-writer |

---

## Cross-Lane Signals

When a tech task should trigger agents from other lanes:

| Signal detected in the task | Lane | Agents to include |
| --- | --- | --- |
| User-visible interface | Product | ux-ui-designer, accessibility-engineer |
| New UI component without a mockup | Product | ux-ui-designer + proxy-po |
| Text or labels shown to the user | Product | ux-writer |
| Feature delivered to non-technical users | Product | change-management, tech-writer |
| Endpoint handles personal data | Governance | legal-compliance + security-engineer |
| New exposed service | Governance | security-engineer in wave 0 |
| Cloud, infrastructure, or scaling concern | Governance | finops-engineer |
| P1 or P0 production alert | Tech | incident-commander + observability-engineer + devops-engineer |
| Table creation or database migration | Data | database-engineer |
| Feature involves embeddings or ML | Data | data-scientist, ml-engineer |
| System prompt or agent workflow must change | Data | prompt-engineer |

---

## Consolidation Format Produced by the Orchestrator After Tech Dispatch

> When the orchestrator has dispatched multiple agents from the tech lane, it consolidates the outputs in this format before journaling.

```markdown

## Tech Summary — [task name]

### Agents involved
- [agent]: [mission] -> [status]

### Deliverables
- [file / decision / artifact]

### Blocking points
- [list or "None"]

### Watch points for the orchestrator
- [post-implementation risks identified]

```
