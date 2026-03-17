# Getting Started — renga

> **Target audience**: developers discovering the framework
> **Prerequisites**: VS Code installed, GitHub Copilot enabled, this repository available locally
> **Last updated**: 2026-03-17
> **Estimated reading time**: 12 min

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Optional MCP Setup](#optional-mcp-setup)
- [Your First Task in 5 Minutes](#your-first-task-in-5-minutes)
- [Understanding Task Levels](#understanding-task-levels)
- [Direct Mode (Without the Orchestrator)](#direct-mode-without-the-orchestrator)
- [Dry-Run Mode (Preview the Plan)](#dry-run-mode-preview-the-plan)
- [Examples by Task Type](#examples-by-task-type)
- [How to Write a Good Request](#how-to-write-a-good-request)
- [FAQ](#faq)
- [Creating and Using Skills](#creating-and-using-skills)
- [Next Steps](#next-steps)

---

## Prerequisites

You only need three things:

1. **VS Code** with the **GitHub Copilot** extension installed and active.
2. **A Copilot subscription**: Individual, Business, or Enterprise. Agent mode is required.
3. **The renga CLI** installed in your project: `curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh`, then `renga init && renga install` from your project root.

That is all. No server to run. No extra runtime dependency to install.

> [!TIP]
> `renga install` automatically installs the Copilot Agent Hooks, which provide guardrails for security, audit, and worktree governance. See [docs/hooks.md](hooks.md).
> For editor setup, optional MCP servers, and VS Code configuration, see [ide-setup.md](ide-setup.md).

---

## Optional MCP Setup

renga agents can use MCP servers (Model Context Protocol) to access live external tools such as framework documentation, browser automation, SQL diagnostics, or GitHub repository data.

> [!IMPORTANT]
> MCP servers are optional. Install only the ones required by the agents you activate. If you mainly use `@debugger` and `@backend-dev`, you usually need far fewer tools than a full QA or browser-testing workflow.

### The 5 MCP servers used most often in this framework

| MCP server | Purpose | Typical agents |
| --- | --- | --- |
| `context7` | Current framework and library documentation | most technical agents |
| `chrome-devtools` | DOM, network, performance, and accessibility inspection | debugger, frontend-dev, performance-engineer |
| `playwright` | Browser automation, screenshots, E2E verification | frontend-dev, qa-engineer, accessibility-engineer |
| `postgresql` | Read-only SQL diagnostics and schema inspection | database-engineer, backend-dev, data-engineer |
| `github` | PRs, issues, commits, and repository context | git-expert, code-reviewer, tech-writer |

If you need configuration examples, secrets handling guidance, or official links for those servers, use [ide-setup.md](ide-setup.md) as the detailed reference.

---

## Your First Task in 5 Minutes

This is the shortest path to value. Do not start with optional MCP servers unless you already know you need them.

### Step 1 — Open your project in VS Code

Open your project folder in VS Code. Copilot automatically discovers the agent files installed in `.github/agents/`.

### Step 2 — Open Copilot Chat and select the orchestrator

1. Open **Copilot Chat**.
2. Use the mode selector at the top of the chat.
3. Select **`@orchestrator`**.

If you do not see the agents, make sure the repository root is the workspace root in VS Code and that `.github/agents/` is present there.

> [!TIP]
> If you want the fastest first run, call a Lite agent directly such as `@backend-dev` or `@debugger`.

### Step 3 — Describe a concrete task

For example:

```text

Add a GET /api/health route that returns { status: 'ok' }

```

You do not need to explain how. Just state what you want.

### Step 4 — Observe the workflow

The orchestrator will:

1. Analyze your request and classify it.
2. Plan the work and select the right agents.
3. Dispatch tasks to the relevant specialists.
4. Check the quality of each output.
5. Return a consolidated result.

You see the process in chat. At the end, you get code, tests, and the relevant documentation path.

> [!TIP]
> For small tasks such as a typo fix or a variable rename, invoke the specialist directly instead of using the orchestrator.

---

## Understanding Task Levels

The orchestrator classifies each task from L0 to L4. That classification determines how many agents are involved and how much control is applied.

| Level | Meaning | Example | What happens |
| --- | --- | --- | --- |
| **L0** | Trivial, single-file, mechanical | Fix a typo, rename a variable | Direct agent, no orchestrator |
| **L1** | Local, reversible, low risk | Fix a CSS issue, rename a file | 1-2 agents, quick execution |
| **L2** | Multi-file or cross-domain | Add an API endpoint with tests | 4-6 agents, at least 2 tracks |
| **L3** | Production, security, or architecture impact | Rework authentication | 6-10 agents, broader consultation |
| **L4** | Critical or irreversible | Migrate a production database | 8-15 agents, consensus or human validation |

> [!NOTE]
> You do not need to choose the level yourself. The orchestrator does that automatically. If a task is riskier than it may look, say so explicitly.

---

## Direct Mode (Without the Orchestrator)

For focused tasks in one domain, call the specialist directly. This is faster and cheaper in context usage.

### Syntax:

```text

@agent-name: task description

```

### Examples:

```text

@debugger: The /api/users endpoint returns 500 since this morning. Here is the error log: [...]

@frontend-dev: Create a responsive Card component with title, image, and CTA button

@code-reviewer: Review this file and flag maintainability issues

```

### When to use direct mode vs. the orchestrator

| Situation | Recommended mode |
| --- | --- |
| Trivial single-file action | Direct agent, fast-track L0 |
| Isolated bug in one file | `@debugger` directly |
| New feature touching multiple domains | `@orchestrator` |
| Need the plan before execution | `@orchestrator` with `dry-run` |
| Architecture question | `@software-architect` directly |
| Refactor with security impact | `@orchestrator` |
| Documentation work | `@tech-writer` directly |

---

## Dry-Run Mode (Preview the Plan)

If you want to inspect the execution plan before launching a complex task, use **dry-run** mode.

### How to enable it

Add `dry-run` or `plan only` to your request:

```text

@orchestrator: dry-run — Refactor the authentication system to support OAuth2

```

Other accepted prompts include `show me the plan`, `preview`, or `without executing`.

### What happens

The orchestrator performs analysis, decomposition, and planning, then stops and shows the planned DAG:

```text

=== PLANNED DAG (dry-run) ===
Criticality: L3
Wave 0: [SecurityEngineer (audit), SoftwareArchitect (design)] — parallel
Wave 1: [QAEngineer (red tests)] — depends on Wave 0
Wave 2: [BackendDev (implementation)] — depends on Wave 1
Wave 3: [CodeReviewer || TechWriter] — parallel
Agents involved: 5 / Waves: 4

```

No file is modified. No agent is actually dispatched beyond planning.

### After the dry-run

You can:

- Approve: `Go`, `OK`, `Execute`
- Adjust: `Add a PerformanceEngineer in wave 3`
- Cancel: `Cancel`

> [!TIP]
> Dry-run mode is especially useful for L3 and L4 tasks involving security, production, or architecture changes.

---

## Examples by Task Type

### Fix a bug

```text

@debugger: The call to /api/orders returns an empty array even though the database contains data.
Here is the SQL query: SELECT * FROM orders WHERE user_id = $1

```

### Implement a new feature

```text

@orchestrator: Add an email notification system when an order changes status.
The statuses are pending, confirmed, shipped, and delivered.

```

The orchestrator will usually involve backend work for the business logic, QA for tests, and documentation or security review if user-facing communication or personal data is involved.

### Run a code review

```text

@code-reviewer: Review src/services/payment.ts and src/controllers/checkout.ts.
Check error handling, conventions, and security risks.

```

### Ask an architecture question

```text

@software-architect: We are choosing between microservices and a modular monolith
for a marketplace API. We have 3 developers, 10k users, and expect 10x growth in 18 months.

```

Expect an opinionated recommendation with trade-offs, not a flat list of neutral options.

### Run a security audit

```text

@orchestrator: Audit the registration and login flow.
Authentication uses email and password with token-based password reset.

```

For tasks like this, the orchestrator can pull in `security-engineer` automatically and may also involve compliance-oriented roles if personal data handling becomes central.

---

## How to Write a Good Request

The quality of the output depends directly on the quality of the request.

### What works well

| Practice | Example |
| --- | --- |
| Be concrete | `Add a POST /api/users endpoint that validates email and password` |
| Provide context | `We use NestJS with TypeORM and PostgreSQL` |
| State the expected result | `Return 201 with the created user, or 400 with validation details` |
| Mention constraints | `No extra dependency` or `Must stay compatible with the current CI` |
| Flag risk explicitly | `Warning: this service handles payment data` |

### What does not work well

| Anti-pattern | Why it is a problem |
| --- | --- |
| `Do the backend` | Too vague |
| `Fix all bugs` | No clear scope |
| `Do it like usual` | The agent does not know your implicit habits |
| `It is urgent, go faster` | Urgency does not replace missing scope |

### Effective formula

```text

@agent: [Action] + [What] + [Context / Constraints] + [Expected result]

```

### Full example:

```text

@orchestrator: Implement Redis caching for /api/products responses.
We use NestJS. TTL must be configurable via environment variable.
Paginated responses must not be cached.
The cache must be invalidated when a product changes.

```

---

## FAQ

### I cannot see the agents in Copilot's mode selector

Make sure `.github/agents/` exists at the root of the VS Code workspace you opened. If you opened a subfolder, Copilot will not detect the agent files.

### Is the orchestrator mandatory?

No. For a simple and targeted task, call the specialist directly. The orchestrator is useful when the task needs coordination across multiple domains.

### Does it cost more tokens?

Yes, the orchestrator uses more context because it plans, dispatches, and controls the flow. For L1 work the difference is small. For L3-L4 work the added cost is usually worth the guardrails.

### Can I create my own agents?

Yes. Create `my-agent.agent.md` in `.github/agents/` and follow the existing format.

### What happens if two agents disagree?

The orchestrator detects contradictions and arbitrates them. For critical decisions, it can trigger a consensus flow or escalate to you for validation.

### Do agents modify my files directly?

Yes, technical agents such as `backend-dev` and `frontend-dev` can read and edit files in your workspace. Advisory agents such as `legal-compliance` or `business-analyst` are read-only by design. Git remains your safety net.

### Can I use renga on an existing project?

Yes. The recommended integration path is Git subtree for versioned updates. See [distribution.md](distribution.md) for the full workflow.

If you need the shortest possible path, you can also copy `.github/agents/` and the relevant files from `.github/instructions/` into an existing project manually. That is simpler to start with, but it does not give you an upgrade path.

Keep only the instruction files that match your stack. The agents adapt to the workspace they are invoked in; they do not require a greenfield repository.

---

## Creating and Using Skills

**Skills** are reusable knowledge packs that agents load on demand. The framework includes five of them: `task-decomposition`, `dag-patterns`, `auto-triggers`, `worktree-lifecycle`, and `handoff-protocol`.

### Create a skill manually

Create a folder in `.github/skills/` with a `SKILL.md` file:

```text

.github/skills/my-skill/SKILL.md

```

Minimal `SKILL.md` example:

```yaml

---
name: my-skill
description: "Short description of what the skill does"
argument-hint: "Describe the context for this skill"
user-invocable: true
---
# Skill: My Skill

Detailed instructions the agent follows when the skill is activated.

```

### Reference a skill from an agent

Add the skill name in the agent frontmatter:

```yaml

---
name: my-agent
skills:
  - my-skill
---
```

See [docs/agent-format.md](agent-format.md#skills) for the full format.

---

## Next Steps

| Goal | Resource |
| --- | --- |
| Integrate the framework into an existing project | [Distribution and installation](distribution.md) |
| Browse all available agents | [Agent directory](../.github/agents/README.md) |
| Memorize the main commands | [Cheat sheet](cheat-sheet.md) |
| Configure VS Code and MCP tools | [IDE setup](ide-setup.md) |
| Understand coding rules by technology | [Instructions by technology](../.github/instructions/) |
| Review agent profiles | [Agent profiles](../.github/agents/_profiles/) |
