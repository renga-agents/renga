---
name: orchestrator-tech
user-invocable: false
description: "Tech lane reference — non-invocable internal profile read by the orchestrator to route backend, frontend, QA, DevOps, and infrastructure specialists"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Lane Profile: Tech

**Available agents**: BackendDev, FrontendDev, FullstackDev, MobileDev, QAEngineer, APIDesigner, PerformanceEngineer, DevOpsEngineer, IncidentCommander, InfraArchitect, CloudEngineer, PlatformEngineer, ObservabilityEngineer, ChaosEngineer, SecurityEngineer, CodeReviewer, SoftwareArchitect, Debugger, AccessibilityEngineer

**Plugin agents (game-studio)**: AnimationsEngineer, GameAssetGenerator, AudioGenerator, GameDeveloper, GameBalancer — *available with the `game-studio` plugin in `_plugins/game-studio/`*

> **Usage**: This profile is **read by the orchestrator** during planning to select agents and define dispatch order. It is not invocable itself. The orchestrator dispatches the specialists directly at depth 1.

## Escalation Criteria Detected by the Orchestrator

| Situation | Orchestrator action |
| --- | --- |
| Cross-domain architecture conflict | Involve DataScientist + SoftwareArchitect in sequence |
| Critical vulnerability detected | Suspend the flow, involve SecurityEngineer + RiskManager |
| Feature impacts GDPR or the AI Act | Involve LegalCompliance before delivery |
| Quality versus deadline disagreement | Involve ArchitectureReviewer for arbitration |

---

## Tech Dispatch Matrix

| Task | Primary agents | Parallel agents | Recommended cross-lane agents |
| --- | --- | --- | --- |
| New fullstack feature | FullstackDev | QAEngineer, APIDesigner (if public API) | UXUIDesigner, AccessibilityEngineer, TechWriter, ProxyPO if specs are missing |
| Backend-only feature | BackendDev | QAEngineer | SecurityEngineer, TechWriter |
| Frontend-only feature | FrontendDev | AccessibilityEngineer, QAEngineer | UXUIDesigner, UXWriter, CreativeDirector if visual identity is involved |
| CI/CD pipeline | DevOpsEngineer | PlatformEngineer | SecurityEngineer, ObservabilityEngineer |
| Performance optimization | PerformanceEngineer | ObservabilityEngineer | SoftwareArchitect, DatabaseEngineer if queries are involved |
| Cloud deployment | CloudEngineer | InfraArchitect | SecurityEngineer, FinOpsEngineer, DevOpsEngineer |
| Resilience testing | ChaosEngineer | ObservabilityEngineer | RiskManager, SoftwareArchitect |
| Public API | APIDesigner | BackendDev, QAEngineer | TechWriter, LegalCompliance if personal data is involved, SecurityEngineer |
| Interactive animation or game experience | AnimationsEngineer | FrontendDev, QAEngineer | CreativeDirector, UXUIDesigner, PerformanceEngineer, AccessibilityEngineer |
| Debugging or investigation | Debugger | — | QAEngineer (reproduction), ObservabilityEngineer (tracing) |
| Production incident | IncidentCommander | Debugger, ObservabilityEngineer | DevOpsEngineer (mitigation), SecurityEngineer if security-related, TechWriter (communication) |
| Refactor or migration | SoftwareArchitect | BackendDev, FrontendDev | CodeReviewer, QAEngineer, TechWriter |

---

## Cross-Lane Signals

When a tech task should trigger agents from other lanes:

| Signal detected in the task | Lane | Agents to include |
| --- | --- | --- |
| User-visible interface | Product | UXUIDesigner, AccessibilityEngineer |
| New UI component without a mockup | Product | UXUIDesigner + ProxyPO |
| Text or labels shown to the user | Product | UXWriter |
| Feature delivered to non-technical users | Product | ChangeManagement, TechWriter |
| Endpoint handles personal data | Governance | LegalCompliance + SecurityEngineer |
| New exposed service | Governance | SecurityEngineer in wave 0 |
| Cloud, infrastructure, or scaling concern | Governance | FinOpsEngineer |
| P1 or P0 production alert | Tech | IncidentCommander + ObservabilityEngineer + DevOpsEngineer |
| Table creation or database migration | Data | DatabaseEngineer |
| Feature involves embeddings or ML | Data | DataScientist, MLEngineer |
| System prompt or agent workflow must change | Data | PromptEngineer |

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
