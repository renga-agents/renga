# renga — Your AI Agent Team for VS Code Copilot

**renga** installs a team of specialized AI agents into your project. Each agent has a precise role — backend developer, security expert, QA engineer, architect, and many more — and becomes available directly in VS Code Copilot when you open the project.

## Getting started

```bash
renga install    # configure your project and download agents, skills and hooks
renga list       # see what was installed
```

Your agents are now available. Open the VS Code **Chat** panel and pick an agent using `@` or the agent selector.

---

## `.renga.yml` — Your configuration file

Created at the root of your project by `renga install`, this file controls which agents are active and how the framework behaves.

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

### Installation profiles

`renga install` lets you choose a profile as a starting point:

| Profile | For what kind of project | Agents included |
|---------|--------------------------|-----------------|
| `lite` | Personal project, prototype | 9 agents: orchestrator, backend, frontend, QA, code reviewer, architect, debugger, git, tech writer |
| `standard` | Team project, production | 20 agents: everything in `lite` + security, DevOps, UX, database, API, performance, product, mobile |
| `full` | Large organization, all roles covered | 50+ agents, mode `all` |

To switch profile, edit `.renga.yml` directly — or run `renga install --profile <name>` again.

### LLM model configuration

Model settings live in the `models:` section of `.renga.yml`:

```yaml
# .renga.yml
models:
  default: "Claude Opus 4.6 (copilot)"

  # Per-agent overrides (optional)
  # overrides:
  #   orchestrator: "Claude Sonnet 4.6 (copilot)"
  #   security-engineer: "Claude Opus 4.6 (copilot)"
```

**To switch the model for all agents at once**, set `default:` then run:

```bash
renga models apply
# or just run renga update — it applies models automatically
```

**For per-agent overrides**, uncomment and fill the `overrides:` section — no need to touch individual files.

The `models:` section is optional. Without it, each agent uses the model defined in its own frontmatter.

---

## Commands

| Command | What it does |
|---------|--------------|
| `renga install` | Configure project, download agents, instructions, skills and hooks |
| `renga install --profile <name>` | Install with a specific profile (`lite`, `standard`, `full`) |
| `renga update` | Update to the latest release (preserves your local customizations) |
| `renga update --dry-run` | Check if an update is available without applying it |
| `renga list` | Show installed agents, skills and plugins |
| `renga plugin add <name>` | Install an optional plugin (e.g. `game-studio`) |
| `renga plugin remove <name>` | Uninstall a plugin |
| `renga plugin list` | List available and installed plugins |
| `renga local init <target>` | Set up a local customization folder (see below) |
| `renga models apply` | Stamp agent frontmatters with model settings from `.renga.yml` |
| `renga validate` | Check all agent files for errors (missing fields, broken references) |
| `renga doctor` | Full health check: Python version, agent count, schemas, hooks |
| `renga dashboard` | Generate a performance summary from agent memory files |
| `renga help` | Show all available commands |

---

## Plugins

Plugins add specialized agents for a specific domain. Agents are installed flat in `.github/agents/` for full Copilot compatibility.

```bash
renga plugin list               # see available and installed plugins
renga plugin add game-studio    # installs game development agents
renga plugin remove game-studio # uninstall
```

---

## Local customization

`renga local init` sets up the folder you need when you're ready to customize, without polluting your project from day one.

```bash
renga local init agents       # .github/agents/_local/        — add or override agents
renga local init skills       # .github/skills/_local/        — custom multi-step workflows
renga local init instructions # .github/instructions/_local/  — custom Copilot instructions
renga local init hooks        # .github/agents/_local/hooks/  — pre/post tool hooks
renga local init schemas      # .github/schemas/              — hook validation schemas
```

`renga update` will **never** overwrite anything inside `_local/` folders.

### CI validation

Run `renga local init hooks` in a repository with a GitHub remote to be offered automatic CI validation. If you accept, it generates `.github/workflows/agent-validate.yml` — a GitHub Actions workflow that runs `renga validate` on every push touching agent files.

---

## Keeping agents up to date

```bash
renga update            # apply the latest release
renga update --dry-run  # preview: shows current and available version, no changes applied
```

Updates overwrite managed files only. Your `_local/` customizations are always preserved.

---

For more information: [github.com/renga-agents/renga](https://github.com/renga-agents/renga)
