# Profile: Handoff Protocol

> This profile defines the standard handoff contract between agents.
> Agents reference this profile instead of duplicating the handoff block.

---

## Handoff Contract: Standard Format

Each agent must structure its handoff according to this template. Only the **specific contents** (recipients, decisions, artifacts) change from one agent to another; the **structure** stays the same.

### Main Handoff

```markdown

**Main handoff to `<agent-1>`, `<agent-2>`, and `<agent-3>`**

- **Typical recipients**: [Target agents and their role in the handoff]
- **Fixed decisions**: [Validated constraints, closed choices, tradeoffs made, closed assumptions - downstream does not revisit them]
- **Open questions**: [Blind spots, unresolved dependencies, validations still required]
- **Artifacts to pick up**: [Files, schemas, tests, plans, dashboards, issues, or product recommendations]
- **Expected next action**: [What the recipient must do - continue without reinterpreting what is already decided]

```

### Secondary Handoff (Optional)

```markdown

**Secondary handoff to `<agent-x>`**

- [Raise the specific elements that do not belong to the main recipient]

```

### Expected Return Handoff

```markdown

**Expected return handoff**

- The downstream agent must confirm what they are taking over, flag what they dispute, and make any newly discovered dependency visible.

```

---

## Protocol Rules

1. **Completeness** - Do not omit any field. An empty field must be stated explicitly: `- **Open questions**: none`.
2. **Non-negotiable decisions** - "Fixed decisions" are NOT suggestions. The downstream agent applies them or escalates to a human.
3. **Traceability** - The handoff is the official record of what was transmitted. It serves as evidence in case of inter-agent dispute.
4. **Symmetry** - Every main handoff requires a return handoff. The downstream agent is obligated to respond.
5. **Specificity** - Adapt content to the real context. A generic handoff (copy-pasted without customization) is a governance violation.

---

## Concrete Example: BackendDev -> QAEngineer

```markdown

## Handoff Contract

**Main handoff to `qa-engineer`, `security-engineer`, and `code-reviewer`**

- **Fixed decisions**: API contract implemented (POST /api/v1/notifications),
  class-validator validations selected, 400/401/404/500 errors handled
- **Open questions**: load testing not covered, retry scheme still to validate
- **Artifacts to pick up**: endpoints, DTOs, services, 12 unit tests,
  Prisma migration #042, structured Pino logs
- **Expected next action**: validate non-regression, challenge
  security blind spots, decide whether the code is ready to merge

**Expected return handoff**

- `qa-engineer` confirms the actual coverage level and remaining scenarios
- `security-engineer` states whether P0 constraints are satisfied

```

---

## Usage in a `.agent.md`

Instead of duplicating the full handoff block, an agent can reference this profile:

```markdown

## Handoff Contract

> Handoff structure: see `_profiles/handoff-protocol.md`

**Main handoff to `qa-engineer` and `code-reviewer`**

- **Fixed decisions**: [specific to this agent]
- **Open questions**: [specific to this agent]
- **Artifacts to pick up**: [specific to this agent]
- **Expected next action**: [specific to this agent]

**Expected return handoff**

- [specific to this agent]

```

The profile provides the framework (rules, format, definitions); the agent provides the specific content.
