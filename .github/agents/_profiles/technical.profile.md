# Profile: Technical

> This profile applies to technical implementation agents (dev, infra, data, ML).
> These agents can read and write code and run commands.

## Allowed Tools

```yaml

tools: ["execute", "read", "edit", "search", "web", "agent", "todo", "io.github.chromedevtools/chrome-devtools-mcp/*", "io.github.upstash/context7/*"]

```

## Agents Using This Profile

- accessibility-engineer
- ai-research-scientist
- api-designer
- architecture-reviewer
- backend-dev
- cloud-engineer
- chaos-engineer
- code-reviewer
- database-engineer
- data-engineer
- data-scientist
- Debugger
- devops-engineer
- frontend-dev
- fullstack-dev
- git-expert
- infra-architect
- ml-engineer
- mlops-engineer
- mobile-dev
- observability-engineer
- performance-engineer
- platform-engineer
- prompt-engineer _(extended technical profile: has `context7` for LLM API verification)_
- qa-engineer
- security-engineer
- software-architect

## Rationale

These agents produce and modify code:

- **`execute`**: to run builds, tests, lints, and shell commands
- **`edit`**: to create and modify files
- **`context7/*`**: **required** before generating any third-party code - verifies current APIs
