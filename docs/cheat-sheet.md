# Cheat Sheet — renga

> **Target audience**: daily users of the framework
> **Prerequisites**: basic familiarity with GitHub Copilot and the agents available in this repository
> **Last updated**: 2026-03-17
> **Estimated reading time**: 4 min

---

## The 10 Essential Agents

| Agent | When to invoke it | Example request |
| --- | --- | --- |
| `@orchestrator` | Complex, cross-domain, or ambiguous task | `Implement a push notification system` |
| `@backend-dev` | Business logic, APIs, services | `Create a POST /api/orders endpoint with validation` |
| `@frontend-dev` | UI components, React, CSS, web performance | `Create an accessible, responsive Modal component` |
| `@debugger` | Hard-to-reproduce or multi-layer bug | `The /api/users endpoint returns 500, here is the log...` |
| `@qa-engineer` | Unit tests, E2E tests, test strategy | `Write Vitest tests for PaymentService` |
| `@code-reviewer` | Maintainability review, conventions, technical debt | `Review src/services/auth.ts for quality and conventions` |
| `@security-engineer` | OWASP audit, vulnerabilities, authentication | `Audit the password reset flow` |
| `@software-architect` | Architecture choices, ADRs, trade-offs | `Monolith or microservices for our use case?` |
| `@devops-engineer` | CI/CD, Docker, deployment, pipelines | `Set up the GitHub Actions pipeline for staging` |
| `@tech-writer` | Documentation, guides, changelogs, API docs | `Write the API integration quickstart` |

---

## The 5 Task Levels (L0 to L4)

| Level | In one phrase | Agents involved | Control |
| --- | --- | --- | --- |
| **L0** | Trivial, single-file | Direct agent | None, fast-track |
| **L1** | Simple, reversible | 1-2 | Standard |
| **L2** | Multi-file | 4-6, at least 2 tracks | Intermediate checkpoint |
| **L3** | Production or security impact | 6-10, at least 3 tracks | Wider consultation |
| **L4** | Critical, irreversible | 8-15, all 4 tracks | Consensus or human validation |

---

## Essential Invocation Patterns

### Invoke a single agent

```text

@agent-name: task description

```

### Route through the orchestrator

```text

@orchestrator: task description

```

### Request consensus for a critical decision

```text

@orchestrator consensus: Should we migrate from REST to GraphQL?

```

### Ask an agent to focus on a specific file

```text

@code-reviewer: Review src/services/payment.ts

```

### Request a broad audit

```text

@orchestrator: Run a thorough security audit of the authentication module

```

---

## Choosing the Right Entry Point

```text

My task is...
│
├─ Trivial, single-file, and purely mechanical?
│  └─ → Direct agent, fast-track L0 (@frontend-dev, @backend-dev...)
│
├─ Simple and within one domain?
│  └─ → Direct agent (@debugger, @frontend-dev, @backend-dev...)
│
├─ Cross-domain or ambiguous?
│  └─ → @orchestrator
│
├─ A critical decision to arbitrate?
│  └─ → @orchestrator consensus: ...
│
└─ Not sure?
   └─ → @orchestrator

```

---

## The 4 Tracks

| Track | Domain | Key agents |
| --- | --- | --- |
| **Tech** | Code, infrastructure, quality, security | backend-dev, frontend-dev, qa-engineer, devops-engineer, security-engineer |
| **Product** | UX, specs, analytics, documentation | proxy-po, ux-ui-designer, product-manager, tech-writer |
| **Data / AI** | Data, ML, pipelines, AI ethics | data-scientist, ml-engineer, data-engineer, ai-research-scientist |
| **Governance** | Compliance, risk, architecture | security-engineer, legal-compliance, ai-ethics-governance, risk-manager |

---

## Writing a Good Request

### Formula:

```text

@agent: [Action] + [What] + [Context] + [Expected result]

```

### Good:

```text

@backend-dev: Implement a rate-limiting middleware for the API.
We use Express.js. Limit to 100 requests per minute per IP.
Return 429 with a Retry-After header.

```

### Not good:

```text

@backend-dev: Do rate limiting

```

---

## Common Pitfalls

| Pitfall | Why it is a problem | Better approach |
| --- | --- | --- |
| Routing everything through the orchestrator | Extra token cost for simple tasks | Use a direct agent for L1 tasks |
| Vague requests | The result becomes generic and less useful | Add context, constraints, and the expected output |
| Ignoring agent questions | The agent is asking for missing information for a reason | Answer the questions to improve the result |
| Manually patching output without rerunning the agent | Your manual fix may introduce inconsistencies | Ask the agent to update the result with the new context |
| Forgetting the stack | The agent has to guess technologies and conventions | State the stack explicitly, for example `NestJS + PostgreSQL` |
| Mixing multiple tasks in one request | The agent tries to solve everything at once, poorly | One request, one clear objective |

---

## The `renga.sh` CLI

Unified entry point for the framework's common operations.

```bash

./scripts/renga.sh <command>

```

| Command | Description | Typical use |
| --- | --- | --- |
| `init` | Copies `.renga.example.yml` to `.renga.yml` and creates `.copilot/memory/` | First-time setup |
| `validate` | Runs `validate_agents.py` to check all `.agent.md` files | Before each PR |
| `doctor` | Full setup diagnosis: Python, required files, JSON schema, hooks | After setup or when something breaks |
| `dashboard` | Generates `reports/dashboard.md` with a framework health overview | Reporting |
| `test` | Runs the test suite, including transpilation and prompt regression | CI/CD |

### Examples

```bash

# Initialize a new project
./scripts/renga.sh init

# Check that all agents are valid
./scripts/renga.sh validate

# Diagnose a broken local setup
./scripts/renga.sh doctor

# Validate hook definitions
python scripts/validate_hooks.py

```

### Hooks (GitHub Copilot Agent Hooks)

Hooks are shell scripts in `.github/hooks/` executed automatically by Copilot before or after specific actions.

| File | Role |
| --- | --- |
| `.github/hooks/copilotagent-pre-tool.sh` | Runs before each tool call for security and filtering |
| `.github/hooks/copilotagent-post-tool.sh` | Runs after each tool call for audit and logging |
| `.github/hooks/_local/` | Your local custom hooks, not distributed |

See [docs/hooks.md](hooks.md) for the full reference.
