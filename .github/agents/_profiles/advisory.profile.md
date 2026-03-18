# Profile: Advisory

> This profile applies to advisory, facilitation, compliance, and strategy agents.
> These agents do not modify code and do not run commands.

## Allowed Tools

```yaml

tools: ["read", "search", "web", "agent", "todo"]

```

## Agents Using This Profile

- ai-ethics-governance
- ai-product-manager
- business-analyst
- change-management
- finops-engineer
- go-to-market-specialist
- incident-commander
- legal-compliance
- product-analytics
- product-manager
- product-strategist
- project-controller
- proxy-po
- risk-manager
- scrum-master
- tech-writer
- ux-ui-designer _(extended advisory profile: has `chrome-devtools` and `context7` for render inspection, without `execute` or `edit`)_
- ux-writer

## Rationale

These agents operate in read-only and advisory mode:

- **No `execute`**: they do not run terminal commands
- **No `edit`**: they do not directly modify code files
- **`read` + `search`**: they can read the codebase to understand context
- **`web`**: for regulatory, competitive, or technical research
- **`github/*`**: to read issues, PRs, and history
