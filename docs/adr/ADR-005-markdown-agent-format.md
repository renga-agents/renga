# ADR-005: Narrative Markdown as the Agent Definition Language

**Date**: 2026-03-16
**Status**: Accepted
**Decision makers**: Founding team

## Context

The framework must define the behavior of 60+ agents: identity, capabilities, rules, workflow, checklists, and handoff protocols.

> *Note: the number of agents has evolved since this ADR was written. See the [agent catalog](../../.github/agents/README.md) for the current count.* The definition format must be readable by LLMs, which interpret the instructions, and by humans, who create and maintain the agents. It must be expressive enough to encode complex behavior while remaining accessible to non-developers.

## Decision

Adopt a hybrid **YAML frontmatter + narrative Markdown** format in `.agent.md` files:

- **YAML frontmatter** between `---`: structured metadata such as name, description, allowed tools, model, and flags (`plugin`, `filiere`, `overrides`), validated through a JSON schema
- **Markdown body**: natural-language narrative instructions covering identity, capabilities, behavioral rules, workflow, checklist, and handoff contract, structured using conventional sections such as `## Identity & Posture` and `## Behavioral Rules`

The frontmatter is validated by `schemas/agent.schema.json`, and `scripts/validate_agents.py` checks structural compliance.

## Consequences

### Positive

- **Accessible**: editable by product managers, tech leads, or architects without requiring development skills
- **Expressive**: narrative Markdown can encode behavioral nuance such as posture, deliberate bias, or escalation conditions that pure JSON/YAML cannot express well
- **Versionable**: Git diffs stay readable and code review works naturally for behavior changes
- **Toolable**: YAML frontmatter enables automatic validation, catalogs, and dashboards through scripts such as `scripts/generate_dashboard.py`
- **Extensible**: adding a new Markdown section does not require schema migration

### Negative

- **Verbose**: a complete agent definition is often 150 to 300 lines, versus 30 to 50 lines for a JSON equivalent
- **Narrative content is not fully validated**: the JSON schema validates only the frontmatter, so contradictory or incoherent Markdown instructions may go unnoticed
- **Fragile parsing**: scripts that extract data from the body depend on formatting conventions that cannot be enforced strictly

### Risks

- **Format drift**: agents may gradually diverge from section conventions, mitigated by `validate_agents.py` and prompt regression tests under `tests/prompt-regression/`
- **Interpretation ambiguity** by LLMs, mitigated by explicit imperative wording such as `Always`, `Never`, and `When in doubt`, plus concrete examples in each agent

## Alternatives Considered

### Pure JSON/YAML

Keep the entire definition as structured data. Rejected: insufficient expressive power for behavioral instructions, poor readability beyond 50 lines, and a higher barrier for non-developers.

### Custom DSL (domain-specific language)

Create a dedicated agent language such as `WHEN condition THEN action`. Rejected: learning curve, custom tooling cost, and no existing ecosystem.

### Programmatic definitions (Python/TypeScript)

Define agents in code using classes or functions. Rejected: high barrier to entry, requires an execution runtime, and produces less readable diffs for behavior changes.

### Existing framework formats (CrewAI, AutoGen)

Reuse CrewAI or AutoGen YAML formats. Rejected: vendor lock-in, formats optimized for programmatic execution rather than human readability, and no native Copilot support.
