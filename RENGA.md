# renga — Your AI Agent Team for VS Code Copilot

**renga** installs a team of specialized AI agents into your project. Each agent has a precise role — backend developer, security expert, QA engineer, architect, and many more — and becomes available directly in VS Code Copilot when you open the project.

## Getting started

```bash
renga init       # configure your project (creates .renga.yml, folders, CI workflow)
renga install    # download the agents, skills and hooks
renga list       # see what was installed
```

Your agents are now available. Open the VS Code **Chat** panel and pick an agent using `@` or the agent selector.

---

## `.renga.yml` — Your configuration file

Created at the root of your project by `renga init`, this file controls which agents are active and how the framework behaves.

### Choosing which agents to activate

```yaml
agents:
  mode: "whitelist"   # only agents listed below are active
  include:
    - backend-dev
    - qa-engineer
    - code-reviewer
    - security-engineer
```

| Mode | Behavior |
|------|----------|
| `whitelist` | Only agents listed under `include` are active. Good for focused teams. |
| `all` | Every installed agent is available. Use `exclude` to hide unwanted ones. |

### Initialization profiles

`renga init` lets you choose a profile as a starting point:

| Profile | For what kind of project | Agents included |
|---------|--------------------------|-----------------|
| `lite` | Personal project, prototype | 8 agents: backend, frontend, QA, code reviewer, architect, debugger, git, tech writer |
| `standard` | Team project, production | 20 agents: everything in `lite` + security, DevOps, UX, database, API, performance, product, mobile |
| `full` | Large organization, all roles covered | 50+ agents, mode `all` |

To switch profile, edit `.renga.yml` directly — or delete it and run `renga init --profile <name>` again.

### LLM model configuration

The model used by all agents is defined in a single place: `.github/agents/_config/models.yml`.

```yaml
# .github/agents/_config/models.yml
default:
  model: "Claude Opus 4.6 (copilot)"
```

**To switch the model for all agents at once** — for example to a faster model during development — edit only this file. No need to touch each agent individually.

**To use a different model for one specific agent**, create an override file in `.github/agents/_local/`:

```yaml
# .github/agents/_local/orchestrator.agent.md
---
name: orchestrator
model: gpt-4o
---
```

Files in `_local/` belong to you — `renga update` will never modify or delete them.

---

## Commands

| Command | What it does |
|---------|--------------|
| `renga install` | Download agents, instructions, skills and hooks for this project |
| `renga update` | Update to the latest release (preserves your local customizations) |
| `renga update --dry-run` | Check if an update is available without applying it |
| `renga list` | Show installed agents, skills and plugins |
| `renga plugin add <name>` | Install an optional plugin (e.g. `game-studio`) |
| `renga plugin remove <name>` | Uninstall a plugin |
| `renga plugin list` | List installed plugins |
| `renga validate` | Check all agent files for errors (missing fields, broken references) |
| `renga doctor` | Full health check: Python version, agent count, schemas, hooks |
| `renga dashboard` | Generate a performance summary from agent memory files |
| `renga help` | Show all available commands |

---

## Plugins

Plugins add specialized agents for a specific domain, without polluting your main agent list.

```bash
renga plugin add game-studio    # installs 9 game development agents
renga plugin list               # see what's installed
renga plugin remove game-studio # uninstall
```

---

## Local customization

Everything inside `_local/` folders belongs to you. `renga update` will **never** overwrite it.

| Folder | Purpose |
|--------|---------|
| `.github/agents/_local/` | Add new agents or override existing ones for this project |
| `.github/instructions/_local/` | Custom Copilot instructions specific to this project |
| `.github/skills/_local/` | Custom skills (specialized multi-step agent workflows) |
| `.github/hooks/` | Custom Copilot hooks (pre/post tool execution) |

---

## Keeping agents up to date

```bash
renga update            # apply the latest release
renga update --dry-run  # preview: shows current and available version, no changes applied
```

Updates overwrite managed files only. Your `_local/` customizations are always preserved.

---

## CI validation

`renga init` generates `.github/workflows/agent-validate.yml` — a GitHub Actions workflow that runs `renga validate` on every push touching agent files. No configuration needed.

---

For more information: [github.com/renga-agents/renga](https://github.com/renga-agents/renga)
