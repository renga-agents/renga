# Architecture Overview — renga

> **Target audience**: developers and maintainers who want the mental model behind the framework
> **Prerequisites**: read [getting-started.md](getting-started.md)
> **Last updated**: 2026-03-17
> **Estimated reading time**: 6 min

---

## Table of Contents

- [Why renga Uses Teams Instead of One Prompt](#why-renga-uses-teams-instead-of-one-prompt)
- [The Core Structure](#the-core-structure)
- [What the Orchestrator Does](#what-the-orchestrator-does)
- [The Four Lanes](#the-four-lanes)
- [Why This Matters](#why-this-matters)

---

## Why renga Uses Teams Instead of One Prompt

Most AI coding setups improve a single assistant with more context and more rules.
renga takes a different route: it treats software work as a coordination problem.

Instead of asking one agent to be architect, developer, reviewer, tester, writer, and security lead at the same time, renga separates those roles and defines how they hand work to one another.

---

## The Core Structure

```text

                          +-------------------+
                          |   orchestrator    |
                          |  planning/control |
                          +---------+---------+
                                    |
             +----------------------+------+----------------------+
             |                      |                             |
      +------+-------+      +-------+------+              +------+-------+
      |   tech lane  |      | product lane |              | governance   |
      +------+-------+      +-------+------+              +------+-------+
             |                      |                             |
      backend-dev            product-manager              security-engineer
      frontend-dev           ux-ui-designer               legal-compliance
      qa-engineer            tech-writer                  risk-manager
      debugger               proxy-po                     architecture-reviewer
             |
      +------+-------+
      | data/AI lane |
      +--------------+

```

The framework ships with 52 core agents:

- 46 invocable agents for direct work
- 6 internal references used by the orchestrator for routing and governance

---

## What the Orchestrator Does

The orchestrator is not the best coder in the system. Its job is to make the system coherent.

It does five things:

1. Classifies the task from L0 to L4.
2. Chooses the execution mode: direct, sequential, parallel, or waves.
3. Dispatches the right specialists.
4. Checks output quality and missing constraints.
5. Records important decisions and escalations.

This is the main difference between renga and prompt collections such as Cursor Rules or a single CLAUDE.md file.

---

## The Four Lanes

| Lane | Scope | Examples |
| --- | --- | --- |
| Tech | Delivery, architecture, debugging, testing, deployment | backend-dev, frontend-dev, qa-engineer, devops-engineer |
| Product | Discovery, UX, roadmap, documentation | product-manager, proxy-po, ux-ui-designer, tech-writer |
| Data/AI | Data pipelines, ML, experimentation, MLOps | data-engineer, data-scientist, ml-engineer, mlops-engineer |
| Governance | Security, compliance, risk, AI ethics | security-engineer, legal-compliance, risk-manager, ai-ethics-governance |

This separation keeps decisions explicit. If a task touches architecture, security, and product, those viewpoints are brought in on purpose instead of being implied by one generic prompt.

---

## Why This Matters

The design gives you three practical benefits:

- Better specialization: each agent optimizes for one domain.
- Better control: governance and review can be triggered automatically.
- Better scaling: you can start with Lite and activate more coverage only when the project needs it.

For the operational side of that choice, see [complexity-profiles.md](complexity-profiles.md).
