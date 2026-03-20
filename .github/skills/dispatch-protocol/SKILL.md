---
name: dispatch-protocol
description: "Governs wave construction and agent dispatch: file plan, TDD sequencing, wave 0 constraints, multi-agent coverage, and multi-track scan."
argument-hint: "Describe the task or DAG to dispatch"
user-invocable: true
---
# Skill: Dispatch Protocol

Authoritative source for wave construction rules, agent assignment constraints, and coverage requirements.

---

## File Plan Before Parallel Dispatch (ERR-004)

If several agents will operate on the same file tree, publish the canonical file list in the scratchpad — with path + owning agent — **before** dispatch. Each agent creates only the files assigned to them.

→ Full rule and example: skill `commit-discipline` §File Plan

---

## QA Engineer Scope — Wave 1 (ERR-007)

Before moving to wave 2, verify the files created by qa-engineer. Only the following are allowed in wave 1 (TDD red):
- `*.spec.ts`, test infrastructure (`package.json`, `vitest.config.ts`, `tsconfig.json`)
- Pure interfaces / contracts

**Forbidden in wave 1**: services, controllers, repositories, DTOs, modules, guards, decorators, entities, filters.

**On violation**: remove those files from the commit, annotate the scratchpad, then start wave 2. If qa-engineer writes the implementation, TDD loses its meaning — the tests are no longer red.

---

## Security Brief: security-engineer → qa-engineer (ERR-008)

If security-engineer is in wave 0 and qa-engineer is in wave 1, include the following verbatim in the qa-engineer prompt, **before** the source material:

> `P0 security constraints extracted from the security-engineer report (wave 0) that your tests must honor: [summary of P0 points — expected sourcing of sensitive data (e.g. userId from JWT sub, not from request body), required auth, scopes]. These constraints are part of the endpoint contract — your tests must validate them and guide the implementation design. If you do not test them, backend-dev will not implement them.`

**Mandatory sequencing**: security-engineer must be in wave 0 if qa-engineer is scheduled. Running both in parallel is forbidden.

---

## Wave 0 Agents: Read-Only, No File Creation (ERR-013)

Read-only wave 0 agents (security-engineer, code-reviewer, software-architect, api-designer, proxy-po, legal-compliance, etc.) **must not create files**. Their artifacts (OpenAPI specs, ADR drafts, schemas) must be included in the text returned by `runSubagent`.

Seiji decides whether those artifacts become actual files and assigns that work to an implementation agent in wave 2.

**Why**: wave 0 agents do not have the worktree path and read from the main workspace. Files created by wave 0 agents land in the root workspace, not the worktree, and pollute the main branch.

---

## Mandatory Multi-Agent Coverage (ERR-014)

For any `L2+` task, identify **all** agent profiles affected — not only the main implementation agent.

**Method**:
1. List the facets: architecture, implementation, UX, tests, review, documentation, security, etc.
2. Assign at least one specialist to each non-trivial facet
3. Include complementary profiles that challenge or enrich the main work

**Coverage floors**:

| Level | Min agents | Min tracks |
|---|---|---|
| L1 | 1-2 | No formal minimum |
| L2 | **4-6** | **2 tracks** |
| L3 | **6-10** | **3 tracks** |
| L4 | **8-15** | **4 tracks** + consensus or escalation |

These are **floors**, not ceilings. A well-structured 15-agent DAG is better than an overloaded 4-agent one.

**Systematic quality agents**: code-reviewer and/or tech-writer in the final wave for any task producing code or documentation.

**Warning signs**:
- "This agent can do everything alone" → DAG is undersized
- "Too many agents, too expensive" → the problem is prompt or structure, not agent count
- Same 5-6 agents on 3 consecutive tasks → rescan the full catalog

---

## Mandatory Multi-Track Catalog Scan (ERR-024)

Before building the DAG, seiji **must** mentally scan the 4 tracks and evaluate every agent.

**Required output**: an `included/excluded` list with a one-word justification for each exclusion → in the scratchpad.

**Cross-track rule**: if an `L2+` task activates agents from only **1 single track**, that is an anomaly and must be explicitly justified.

**Quick catalog checklist**:

```
TECHNICAL TRACK (18 core agents):
│ backend-dev          — API, business logic, services
│ frontend-dev         — UI, components, CSS, web performance
│ fullstack-dev        — end-to-end feature, integration
│ mobile-dev           — React Native, Flutter, mobile apps
│ qa-engineer          — tests, TDD, coverage, test strategy
│ code-reviewer        — code review, maintainability, patterns
│ Debugger             — bug investigation, root cause, reproduction
│ api-designer         — API contracts, OpenAPI, DX
│ software-architect   — patterns, ADR, domain decomposition
│ performance-engineer — profiling, SLO/SLI, load
│ devops-engineer      — CI/CD, containers, pipelines
│ incident-commander   — incident management, crisis coordination
│ infra-architect      — IaC, network topology, VPS
│ cloud-engineer       — cloud, provisioning, HA/DR
│ platform-engineer    — internal DX, self-service, abstractions
│ observability-engineer — OTel, tracing, alerting, dashboards
│ chaos-engineer       — resilience, failure injection
│ security-engineer    — OWASP, hardening, audit (primary: GOVERNANCE)

PRODUCT TRACK (11 core agents):
│ proxy-po             — user stories, backlog, acceptance criteria
│ product-manager      — cross-functional steering, MVP, feature roadmap
│ product-analytics    — adoption, funnel, retention, metrics
│ product-strategist   — vision, OKRs, roadmap, product-market fit
│ ux-ui-designer       — mockups, journeys, design system
│ ux-writer            — microcopy, onboarding, tone of voice
│ go-to-market-specialist — pricing, launch, segmentation
│ scrum-master         — facilitation, velocity, continuous improvement
│ tech-writer          — technical and user documentation
│ business-analyst     — business processes, BPMN, gap analysis
│ change-management    — change management (primary: GOVERNANCE)

DATA/AI TRACK (8 core agents):
│ data-scientist       — analysis, modeling, feature engineering
│ ml-engineer          — training, optimization, model deployment
│ mlops-engineer       — ML pipeline, model serving, monitoring
│ data-engineer        — ETL/ELT, data quality, data pipelines
│ ai-research-scientist — state of the art, experimentation
│ ai-product-manager   — AI product strategy, AI roadmap
│ database-engineer    — modeling, optimization, DB migrations
│ prompt-engineer      — system prompts, evaluation, red teaming

GOVERNANCE TRACK (8 core agents):
│ security-engineer    — OWASP, hardening, audit (secondary: TECHNICAL)
│ legal-compliance     — GDPR, AI Act, OSS licenses, Terms of Service
│ ai-ethics-governance — bias, XAI, AI red teaming, model cards
│ risk-manager         — risk mapping, DPIA, contingency
│ finops-engineer      — cloud costs, budgeting, rightsizing
│ architecture-reviewer — cross-functional review, consistency, tech debt
│ accessibility-engineer — WCAG, ARIA, RGAA (secondary: TECHNICAL)
│ project-controller   — PMO, budget tracking, dependencies

OUT-OF-TRACK (1 core agent):
│ git-expert           — Git strategy, conflicts, workflows

PLUGIN AGENTS — game-studio (9 agents):
│ AnimationsEngineer   — WebGL, Three.js, GSAP, canvas, shaders
│ GameAssetGenerator   — visual assets (Replicate)
│ AudioGenerator       — audio assets (Replicate)
│ GameDeveloper        — game logic, game loop, physics
│ GameBalancer         — balancing, difficulty curves
│ CreativeDirector     — art direction, visual identity
│ LevelDesigner        — level design, progression
│ NarrativeDesigner    — narrative, dialogue, worldbuilding
│ GameProducer         — game production, planning, milestones

DUAL AFFILIATIONS:
│ security-engineer      — primary: GOVERNANCE, secondary: TECHNICAL
│ accessibility-engineer — primary: GOVERNANCE, secondary: TECHNICAL
│ change-management      — primary: GOVERNANCE, secondary: PRODUCT
```

For each excluded agent, note a one-word justification: `mobile-dev — out of scope`.

---

## Self-Config Loading in Subagent Prompts (ERR-026)

Every subagent prompt dispatched by seiji **must** begin with:

> `"Start by reading your configuration file at .github/agents/<agent-name>.agent.md. Apply your tools, constraints, and specialization from that file throughout this task."`

**Never dispatch a bare prompt** without this prefix. If an agent ignores its config, it will not apply its governance rules, tools constraints, or domain specialization — this is a governance incident (ERR-026).

**Template**:

```
Start by reading your configuration file at .github/agents/<agent-name>.agent.md. Apply your tools, constraints, and specialization from that file throughout this task.

[actual task prompt here]
```
