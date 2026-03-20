# renga

> ### The team your AI agent is missing
>
> **Target audience**: developers, tech leads, and product teams using AI-assisted development
> **Prerequisites**: VS Code, GitHub Copilot in agent mode
> **Last updated**: 2026-03-17
> **Estimated reading time**: 5 min

English | [Français](README.fr.md)

---

## Table of Contents

- [renga](#renga)
	- [Table of Contents](#table-of-contents)
	- [Why renga](#why-renga)
		- [The problem](#the-problem)
		- [The solution](#the-solution)
		- [The shift in mindset](#the-shift-in-mindset)
		- [What this buys you](#what-this-buys-you)
	- [Architecture](#architecture)
	- [Quickstart](#quickstart)
		- [1. Install the CLI](#1-install-the-cli)
		- [2. Initialize your project](#2-initialize-your-project)
		- [3. Open Copilot Chat and start with one specialist](#3-open-copilot-chat-and-start-with-one-specialist)
	- [Lite Profile](#lite-profile)
	- [How renga Compares](#how-renga-compares)
	- [Documentation](#documentation)
	- [Governance](#governance)
	- [Repository Structure](#repository-structure)

---

## Why renga

Most AI coding setups still revolve around one assistant with more rules, more context, or a longer prompt.

renga takes a different position: software delivery is a coordination problem. The framework gives your editor a team structure instead of a single super-prompt.

### The problem

A lone coding agent can move fast, but it usually lacks four things that matter on real software work:

- coordination across specialties
- meaningful peer review before changes land
- explicit governance for security, privacy, and irreversible decisions
- real specialization instead of one generic prompt stretched across every domain

That is why the same setup often produces acceptable local code but weak system-level outcomes.

### The solution

renga organizes 52 core agents under a central orchestrator, much like a real engineering team:

- an architect frames the design before implementation
- a security specialist challenges exposed surfaces and risky flows
- a QA writes or validates tests before delivery confidence is assumed
- a product-oriented role clarifies intent when the task is under-specified
- an orchestrator plans, dispatches, and arbitrates the full sequence

That means:

- an architect for design and irreversible choices
- a developer for implementation
- a reviewer for maintainability
- a QA for tests and release confidence
- a debugger for root-cause analysis
- a writer for documentation and handoff quality

You can use direct specialist invocation for fast work, or bring in the orchestrator when the task becomes multi-file, risky, or cross-functional.

### The shift in mindset

The framework changes the operating model from “ask one agent to do everything” to “pilot a small team of specialists with explicit roles and handoffs”.

### What this buys you

| Benefit | Why it matters |
| --- | --- |
| Full lifecycle coverage | Tech, Product, Data/AI, and Governance together cover design, delivery, review, and risk |
| Quality by construction | Testing, review, security, and documentation are built into the workflow |
| Traceability | Important decisions and trade-offs do not disappear into one opaque prompt history |
| Guardrails | Sensitive tasks can trigger stronger review and governance automatically |
| Specialization | Each agent is optimized for one domain instead of approximating all of them |
| Runtime hooks | Copilot hooks add technical enforcement for audit, safety, and workspace zoning |

---

## Architecture

The orchestrator is the hub. It does not replace specialists; it coordinates them.

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

The key principle is simple: the orchestrator does not code, design, or audit for the specialists. It makes sure the right expertise appears at the right moment and that the final result is coherent.

---

## Quickstart

The fastest path is the Lite profile.

### 1. Install the CLI

```bash

curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh

```

### 2. Initialize your project

From the root of your project:

```bash

renga install
code .

```

`renga install` is the single onboarding command. It creates `.renga.yml` (defaulting to Lite profile), installs agents/hooks/skills, and optionally activates plugins. In an interactive terminal, it lets you choose between Lite, Standard, and Full profiles.

### 3. Open Copilot Chat and start with one specialist

```text

@backend-dev: Add a GET /api/health route that returns { status: 'ok' }

```

For broader tasks, switch to the orchestrator:

```text

@orchestrator: Add a GET /api/health route with tests and docs

```

If you want the fuller setup for VS Code and MCP tools, read [docs/ide-setup.md](docs/ide-setup.md).

---

## Lite Profile

Lite is the default onboarding path and the best fit for a solo project, MVP, or first evaluation.

It enables 8 core agents:

- `backend-dev`
- `frontend-dev`
- `qa-engineer`
- `code-reviewer`
- `software-architect`
- `debugger`
- `git-expert`
- `tech-writer`

This keeps the learning curve low while preserving the essential engineering loop: design, implementation, testing, review, debugging, and documentation.

See [docs/complexity-profiles.md](docs/complexity-profiles.md) for the full Lite, Standard, and Full breakdown.

---

## How renga Compares

| Capability | renga | Cursor Rules | CLAUDE.md | Aider |
| --- | --- | --- | --- | --- |
| Specialized agents | 52 core agents plus plugins | One assistant with global rules | One assistant with project context | One assistant with instructions |
| Multi-agent orchestration | Yes | No | No | No |
| Cross-review by role | Yes | No | No | No |
| Governance guardrails | Yes | Limited | Limited | Limited |
| Progressive adoption | Lite, Standard, Full | Manual | Manual | Manual |

renga is not trying to be a better prompt file. It is trying to make AI-assisted work behave more like an accountable engineering team.

---

## Documentation

Start here:

- [docs/getting-started.md](docs/getting-started.md) for the first task flow
- [docs/ide-setup.md](docs/ide-setup.md) for VS Code, Copilot, and MCP setup
- [docs/cheat-sheet.md](docs/cheat-sheet.md) for the day-to-day reference
- [docs/agent-format.md](docs/agent-format.md) for the .agent.md and skill format reference
- [docs/complexity-profiles.md](docs/complexity-profiles.md) to choose Lite, Standard, or Full
- [docs/architecture.md](docs/architecture.md) for the orchestrator and four-lane model
- [docs/distribution.md](docs/distribution.md) for install and update strategies
- [docs/plugin-system.md](docs/plugin-system.md) for bundled packs and custom plugins
- [docs/i18n-guide.md](docs/i18n-guide.md) for glossary and translation guidance
- [docs/hooks.md](docs/hooks.md) for Copilot hook behavior and guardrails

Repository internals and decision records:

- [docs/adr/README.md](docs/adr/README.md)
- [.github/agents/README.md](.github/agents/README.md)
- [.github/instructions](.github/instructions)

Contributor-facing documents:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [GOVERNANCE.md](GOVERNANCE.md)

---

## Governance

renga is being prepared as a community-first open-source project.

The current operating model is:

- BDFL-led while the framework stabilizes
- explicit contribution rules and review expectations
- progressive delegation toward Champions and then a Core Team as adoption grows

The detailed model lives in [GOVERNANCE.md](GOVERNANCE.md).

---

## Repository Structure

At a high level, the repository is organized like this:

```text

renga/
├── .github/
│   ├── agents/           # core agents, internal references, profiles, plugins
│   ├── instructions/     # technology-specific coding rules
│   └── hooks/            # Copilot runtime hooks and enforcement scripts
├── docs/                 # guides, references, ADRs
├── scripts/              # CLI and build/validation tooling
├── schemas/              # JSON schemas for validation
├── tests/                # parser, validation, transpilation, and regression tests
├── output/               # generated distributions for other runtimes
└── reports/              # generated health and dashboard outputs

```

If you want the deeper rationale behind these folders, start with [docs/architecture.md](docs/architecture.md) and [docs/adr/README.md](docs/adr/README.md).
