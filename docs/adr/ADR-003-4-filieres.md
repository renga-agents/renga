# ADR-003: Organization into Four Business Lanes

**Date**: 2026-03-16
**Status**: Accepted
**Decision makers**: Founding team

## Context

The framework includes 60+ agents spanning domains from backend engineering to legal, AI, and product management.

> *Note: the number of agents has evolved since this ADR was written. See the [agent catalog](../../.github/agents/README.md) for the current count.* The central orchestrator cannot know every domain deeply enough to route work optimally on its own. The framework needs an intermediate structure that groups agents by business capability and makes routing easier.

## Decision

Organize agents into **four business lanes**, each guided by a lane orchestrator profile:

| Lane | Orchestrator | Scope |
| --- | --- | --- |
| **Technical** | `orchestrator-tech` | Architecture, backend, frontend, mobile, infra, DevOps, security, performance, databases |
| **Product** | `orchestrator-product` | Product management, UX/UI, analytics, strategy, go-to-market |
| **Data & AI** | `orchestrator-data` | Data engineering, data science, ML, MLOps, AI ethics |
| **Governance** | `orchestrator-governance` | Quality, compliance, risk, change management, FinOps |

The central orchestrator dispatches to the appropriate lane orchestrator, which knows its domain specialists and refines the dispatch.

## Consequences

### Positive

- **Exhaustive coverage**: every business domain has an identified owner
- **Faster dispatch**: the main orchestrator chooses among four lanes instead of 60+ agents
- **Contextual expertise**: each lane orchestrator understands dependencies within its domain
- **Conway's Law alignment**: the structure mirrors the major competence domains of a tech organization

### Negative

- **Shotgun surgery risk**: adding a fifth lane requires changing the orchestrator, creating a new lane orchestrator, and redistributing agents
- **Cross-cutting tasks**: some work spans multiple lanes, such as a database migration with product impact, and therefore requires coordination by the main orchestrator
- **Overhead**: for small teams using 5 to 10 agents, the lane structure can be oversized

### Risks

- **Structural rigidity** if the number of lanes is hardcoded, mitigated by the plugin system (see [ADR-006](ADR-006-plugin-system.md)) and by plugin auto-discovery through the `filiere` frontmatter field

## Alternatives Considered

### Flat list (all agents at the same level)

The orchestrator dispatches directly among 60+ agents. Rejected: too much cognitive load on the main orchestrator, frequent routing mistakes, and no business-domain grouping.

### By technical stack (Node, Python, Go, etc.)

Group by language or framework. Rejected: too granular, does not cover non-technical agents such as product, legal, or UX, and creates artificial boundaries for fullstack work.

### By project phase (analysis -> design -> build -> test -> deploy)

Group by lifecycle phase. Rejected: too rigid, since most tasks do not follow a linear pipeline. A bug fix often touches analysis, code, and tests at the same time.
