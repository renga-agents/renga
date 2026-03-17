# Automatic Triggers — Orchestrator

> This file is the reference source for automatic triggers, human escalation, criticality levels, and the L0 fast track.
> Referenced from `orchestrator.agent.md`, sections §1 Initialization and §2 Decomposition.

---

## Automatic Triggers (Non-Negotiable)

| Detected condition | Added agents | Mode |
| --- | --- | --- |
| Personal data **being changed**: creation, modification, exposure, or transmission of `userId`, `email`, `phone`, `ip`, or `address` to new storage or a third party. _Read-only internal display does not trigger this, except for sensitive data such as health, finance, biometrics, or third-party exposure._ | LegalCompliance + RiskManager | parallel |
| New AI processing, scoring, or automated decision-making | AIEthicsGovernance | sequential (before deployment) |
| Hosting or country change | LegalCompliance + RiskManager | parallel |
| AI model deployment or modification | AIEthicsGovernance + MLOpsEngineer | parallel |
| Delivery affecting non-technical users | ChangeManagement | sequential (before release) |
| Cloud architecture or sizing decision | FinOpsEngineer | parallel (with CloudEngineer) |
| New exposure surface (endpoint, auth, third-party integration) | SecurityEngineer | **wave 0** if QAEngineer is planned (ERR-008) |
| New endpoint or public API contract | APIDesigner + SoftwareArchitect | wave 0 |
| New module without a product spec | ProxyPO | wave 0 |
| New table or database migration | DatabaseEngineer | parallel wave 1 |
| New service or SLO change | ObservabilityEngineer | parallel |
| Added or modified code using a third-party library, not simple reading of existing code | context7 MCP | before generation |
| Critical validation MCP tool unavailable (ERR-017) | Orchestrator: notify the user and propose either waiting or explicitly accepting the risk | **blocking** |
| Hook `preToolUse` DENY (`pre-tool-security.sh` exit 1) | Any agent - tool blocked by the Copilot runtime, non-bypassable | Automatic |

> **Note**: `preToolUse` hooks act as a runtime safety net. They operate in defense-in-depth with `.instructions.md` files and the automatic triggers above. A DENY hook is **final**: the Copilot runtime blocks the tool with no agent override possible.

> **Proportionality principle**: automatic triggering must remain proportional to the **actual risk**, defined by mutation × exposure × sensitivity, not by the mere presence of an identifier in code. Reading a `userId` to display a profile does not carry the same risk as sending an `email` to a third-party service or storing a `phone` in a new table. The orchestrator evaluates the **effective risk** before involving compliance agents. In a SaaS codebase where nearly every file touches a `userId`, this principle prevents LegalCompliance from triggering on every trivial task.

---

## Automatic Human Escalation

| Trigger | Reason |
| --- | --- |
| Potentially exposed secret | Security incident |
| Sensitive or regulated personal data | Legal risk |
| Irreversible decision, rollback > 2 person-weeks | Strategic risk |
| SecurityEngineer ↔ LegalCompliance disagreement | Cross-functional risk |
| High-risk or ambiguous AI system in production | Stronger governance |
| Unexpected budget impact | Financial risk |
| Framework choice with viable alternatives, migration > 1 person-week (ERR-016) | Irreversible architecture |
| Critical validation tool unavailable (ERR-017) | Delivery without validation |

---

## Circuit Breaker — Failing Agents

| Situation | Trigger | Action |
| --- | --- | --- |
| Dispatched agent fails 2 consecutive times, non-compliant output, timeout, or error | Automatic | Human escalation + log in `error-patterns-<slug>.md`. Do not retry a third time. |
| Agent produces contradictory outputs across two retries | Automatic | Escalate to consensus if at least 2 agents are available to vote, otherwise HITL |
| No agent from the required lane can take the task | Automatic | Mandatory HITL escalation — do not continue without expertise |

> **ERR-031** — Circuit breaker: an agent cannot be retried more than 2 times on the same subtask. Beyond that, HITL escalation is mandatory.

---

## Criticality Levels

| Level | Definition | Rule |
| --- | --- | --- |
| `L0` | Trivial, single-file, purely mechanical | Fast track — direct agent, no DAG or logging |
| `L1` | Local, reversible, no external impact | Simple execution + standard control |
| `L2` | Multi-file or multi-agent, moderate rollback cost | Mandatory intermediate checkpoint |
| `L3` | Production, security, compliance, data, cost, or architecture impact | Broader consultation + stronger logging |
| `L4` | Critical or irreversible decision | Consensus or mandatory human escalation |

---

## L0 Fast Track — Bypass the Orchestrator

Trivial tasks do not justify the full orchestrator cycle. L0 fast track lets the user invoke a specialist directly without planning, DAG construction, or logging.

### L0 Criteria (All Required)

- **Single-file** task, only 1 file modified
- **Immediately reversible**, `undo` or `git checkout`
- **No external impact**, no migration, deployment, or public API
- **No architecture decision**, no pattern, library, or structural choice
- **No sensitive data**, no PII, secrets, or credentials
- No **multi-agent coordination** required

### Bypass

The user calls the specialist directly:

```

@frontend-dev: fix the header padding (24px -> 16px)
@backend-dev: rename the `tmp` variable to `userCount` in src/services/stats.ts
@tech-writer: add a JSDoc comment to the `parseConfig` function

```

The orchestrator is not involved. The agent acts alone within its own scope.

### Limitations

| What is skipped in L0 | Why that is acceptable |
| --- | --- |
| Logging in `decisions.md` | No decision involved — purely mechanical action |
| DAG construction | No dependency — one atomic action |
| Multi-agent dispatch | No coordination required |
| Worktree isolation | Single-file, reversible impact |

### L0 Examples

- Reformat a file, prettier or indentation
- Rename a local variable
- Add a comment or a type annotation
- Fix a typo in a label or error message
- Read a file to answer a question
- Modify a CSS value, color, spacing, or size

### When It Is NOT L0

If any of the following criteria is present, reclassify to `L1+` and route through the orchestrator:

- Modifies multiple files
- Impacts an API contract or shared interface
- Touches authentication, permissions, or personal data
- Requires choosing between multiple approaches
- Introduces or removes a dependency
