# Profile: Technical

> This profile applies to technical implementation agents (dev, infra, data, ML).
> These agents can read and write code and run commands.

## Allowed Tools

```yaml

tools: ["execute", "read", "edit", "search", "web", "agent", "todo", "io.github.chromedevtools/chrome-devtools-mcp/*", "io.github.upstash/context7/*"]

```

## Agents Using This Profile

- AccessibilityEngineer
- AIResearchScientist
- APIDesigner
- ArchitectureReviewer
- BackendDev
- CloudEngineer
- ChaosEngineer
- CodeReviewer
- DatabaseEngineer
- DataEngineer
- DataScientist
- Debugger
- DevOpsEngineer
- FrontendDev
- FullstackDev
- GitExpert
- InfraArchitect
- MLEngineer
- MLOpsEngineer
- MobileDev
- ObservabilityEngineer
- PerformanceEngineer
- PlatformEngineer
- PromptEngineer _(extended technical profile: has `context7` for LLM API verification)_
- QAEngineer
- SecurityEngineer
- SoftwareArchitect

## Rationale

These agents produce and modify code:

- **`execute`**: to run builds, tests, lints, and shell commands
- **`edit`**: to create and modify files
- **`context7/*`**: **required** before generating any third-party code - verifies current APIs
