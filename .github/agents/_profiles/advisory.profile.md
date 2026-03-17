# Profile: Advisory

> This profile applies to advisory, facilitation, compliance, and strategy agents.
> These agents do not modify code and do not run commands.

## Allowed Tools

```yaml

tools: ["read", "search", "web", "agent", "todo"]

```

## Agents Using This Profile

- AIEthicsGovernance
- AIProductManager
- BusinessAnalyst
- ChangeManagement
- FinOpsEngineer
- GoToMarketSpecialist
- IncidentCommander
- LegalCompliance
- ProductAnalytics
- ProductManager
- ProductStrategist
- ProjectController
- ProxyPO
- RiskManager
- ScrumMaster
- TechWriter
- UXUIDesigner _(extended advisory profile: has `chrome-devtools` and `context7` for render inspection, without `execute` or `edit`)_
- UXWriter

## Rationale

These agents operate in read-only and advisory mode:

- **No `execute`**: they do not run terminal commands
- **No `edit`**: they do not directly modify code files
- **`read` + `search`**: they can read the codebase to understand context
- **`web`**: for regulatory, competitive, or technical research
- **`github/*`**: to read issues, PRs, and history
