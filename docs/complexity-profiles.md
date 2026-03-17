# Complexity Profiles

> **Target audience**: developers and tech leads adapting the framework to their project
> **Prerequisites**: read [getting-started.md](getting-started.md)
> **Last updated**: 2026-03-17
> **Estimated reading time**: 8 min
>
> **Goal**: adapt the number of active agents to the size and needs of your project.
> renga ships with 52 core agents (46 invocable + 6 internal references) plus optional plugins.
> Most projects do not need all of them enabled at once.

---

## Table of Contents

- [Overview](#overview)
- [Lite Profile](#lite-profile)
- [Standard Profile](#standard-profile)
- [Full Profile](#full-profile)
- [How to Choose](#how-to-choose)
- [`.renga.yml` Configuration](#rengayml-configuration)

---

## Overview

| Profile | Active agents | Typical use case | Typical team |
| --- | --- | --- | --- |
| **Lite** | 8 | Small solo project or prototype | 1 developer |
| **Standard** | 20 | Structured project, small team | 2-5 developers |
| **Full** | 52 core agents | Enterprise project, strong governance needs | 5+ developers, multi-team |

---

## Lite Profile

> **8 agents**: the essentials for a solo developer or a fast prototype.

### Lite use cases

- Personal project, side project, MVP
- Technical prototype that must be validated quickly
- Solo developer comfortable with architecture and baseline security

### Lite included agents

| Agent | Role |
| --- | --- |
| `backend-dev` | APIs, services, business logic |
| `frontend-dev` | UI, React components, pages |
| `qa-engineer` | Tests, coverage, quality |
| `code-reviewer` | Code review, maintainability |
| `software-architect` | Architecture, technical decisions |
| `debugger` | Bug diagnosis and resolution |
| `git-expert` | Git workflow, branches, conflicts |
| `tech-writer` | Documentation, README, guides |

### Agents not included and acceptable trade-offs

- No `security-engineer`: baseline security is handled by the architect and developer
- No `devops-engineer`: deployment stays manual or minimally automated
- No `orchestrator`: direct invocation via `@agent-name`
- No `database-engineer`: developers manage schema changes through the ORM

### Lite `.renga.yml` example

```yaml

# Lite profile — 8 agents for solo projects and prototypes
agents:
  include:
    - backend-dev
    - frontend-dev
    - qa-engineer
    - code-reviewer
    - software-architect
    - debugger
    - git-expert
    - tech-writer

model:
  default: "Claude Opus 4.6 (copilot)"

```

---

## Standard Profile

> **20 agents**: for a structured team with stronger quality, security, and operations needs.

### Standard use cases

- Production SaaS project with 2-5 developers
- Need for security review, performance work, and automated deployment
- Product with real users and stronger quality expectations

### Standard included agents

All **Lite** agents, plus:

| Agent | Added role |
| --- | --- |
| `orchestrator` | Planning, decomposition, dispatch |
| `security-engineer` | Security reviews and vulnerability analysis |
| `database-engineer` | Schema, migrations, DB performance |
| `devops-engineer` | CI/CD, pipelines, deployment |
| `ux-ui-designer` | Mockups, design system, UX |
| `api-designer` | API contracts and specifications |
| `performance-engineer` | Optimization, profiling, benchmarks |
| `product-manager` | Product vision, prioritization, specs |
| `prompt-engineer` | System prompts, evaluation, agent tuning |
| `platform-engineer` | Internal tooling, DX, platform concerns |
| `fullstack-dev` | Cross-stack feature implementation |
| `mobile-dev` | Mobile applications, mostly React Native |

### Standard `.renga.yml` example

```yaml

# Standard profile — 20 agents for 2-5 developer teams
agents:
  include:
    # --- Core (Lite) ---
    - backend-dev
    - frontend-dev
    - qa-engineer
    - code-reviewer
    - software-architect
    - debugger
    - git-expert
    - tech-writer
    # --- Standard additions ---
    - orchestrator
    - security-engineer
    - database-engineer
    - devops-engineer
    - ux-ui-designer
    - api-designer
    - performance-engineer
    - product-manager
    - prompt-engineer
    - platform-engineer
    - fullstack-dev
    - mobile-dev

model:
  default: "Claude Opus 4.6 (copilot)"

```

---

## Full Profile

> **52 core agents**: complete coverage for large projects with governance, compliance, and specialization needs.

### Full use cases

- Enterprise project with governance, compliance, and audit requirements
- Multi-disciplinary team spanning engineering, data, ML, product, security, and compliance
- Need for exhaustive coverage: AI, observability, chaos engineering, FinOps, legal review

### Full included agents

All **Standard** agents, plus:

| Agent | Added role |
| --- | --- |
| `accessibility-engineer` | WCAG compliance and accessibility audits |
| `ai-ethics-governance` | AI governance, bias, compliance |
| `ai-product-manager` | AI and ML product strategy |
| `ai-research-scientist` | Advanced ML research and experimentation |
| `animations-engineer` | Animations, canvas, WebGL, shaders |
| `architecture-reviewer` | Cross-cutting architecture review |
| `audio-generator` | Audio generation and sound design |
| `business-analyst` | Business analysis, process mapping, KPIs |
| `change-management` | Adoption and organizational change |
| `chaos-engineer` | Resilience and chaos testing |
| `cloud-engineer` | Cloud services and IaC |
| `creative-director` | Brand and art direction |
| `data-engineer` | Data pipelines, ETL, lakehouse |
| `data-scientist` | Analysis, modeling, statistics |
| `finops-engineer` | Cloud cost control |
| `game-asset-generator` | Game assets, sprites, textures |
| `go-to-market-specialist` | Launch and go-to-market strategy |
| `incident-commander` | Incident coordination and postmortems |
| `infra-architect` | Infrastructure and network architecture |
| `legal-compliance` | Legal and regulatory compliance |
| `ml-engineer` | ML models, training, deployment |
| `mlops-engineer` | ML pipelines and model monitoring |
| `observability-engineer` | Monitoring, alerting, SLI/SLO |
| `product-analytics` | Product analytics, metrics, A/B tests |
| `product-strategist` | Long-term product strategy |
| `project-controller` | Project tracking, budget, planning |
| `proxy-po` | Proxy Product Owner |
| `risk-manager` | Risk management |
| `scrum-master` | Agile facilitation |
| `ux-writer` | UX writing and microcopy |

### Internal references (always included, not invocable)

| Reference | Role |
| --- | --- |
| `consensus-protocol` | Inter-agent consensus protocol |
| `execution-modes` | Execution modes such as standard and dry-run |
| `orchestrator-data` | Data lane reference for the orchestrator |
| `orchestrator-governance` | Governance lane reference for the orchestrator |
| `orchestrator-product` | Product lane reference for the orchestrator |
| `orchestrator-tech` | Tech lane reference for the orchestrator |

### Full `.renga.yml` example

```yaml

# Full profile — all agents active
# Explicit listing is not required if no filtering is applied.
agents:
  include: "*"

model:
  default: "Claude Opus 4.6 (copilot)"

```

---

## How to Choose

```text

Solo project or prototype?
  └─ YES → Lite
  └─ NO → Team of 5 developers or fewer, without major ML/data/compliance needs?
              └─ YES → Standard
              └─ NO → Full

```

### Signals to move up one profile

| From | To | Signals |
| --- | --- | --- |
| Lite | Standard | First production users, need for CI/CD, explicit security review requests |
| Standard | Full | Dedicated data or ML work, legal requirements such as GDPR or SOC2, multiple teams |

### Customization

Profiles are starting points. Add or remove agents based on your actual needs.

```yaml

# Standard + observability, without mobile
agents:
  include:
    # ... standard agents ...
    - observability-engineer
    # mobile-dev removed

```

---

## `.renga.yml` Configuration

Each profile includes a `model.default` entry that points to the centralized configuration in `.github/agents/_config/models.yml`.
See [docs/agent-format.md](agent-format.md) for the full configuration reference.
