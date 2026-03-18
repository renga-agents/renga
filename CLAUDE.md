# CLAUDE.md — renga project context

## What this project is

**renga** is a Bash CLI that installs a team of specialized AI agents (`.agent.md` files) into any project for use with VS Code GitHub Copilot. Users run `renga install` once; agents appear in Copilot via `@agent-name`.

The CLI lives in `scripts/renga.sh` (source) and `dist/renga` (compiled artifact, gitignored). `install.sh` installs the CLI system-wide from a GitHub Release tarball.

---

## Repository structure

```
scripts/
  renga.sh              # CLI source — edit this, never dist/renga directly
  build_dist.py         # Packages dist/ from .github/agents, hooks, skills, etc.
  validate_agents.py    # Validates .agent.md frontmatter and cross-references
  generate_dashboard.py # Generates a Markdown performance dashboard
  validate_hooks.py     # Validates .hooks.json files
  agent_parser.py       # Shared parser for Markdown tables (used by dashboard)

.github/
  agents/               # The 52 core agent files (*.agent.md)
    _profiles/          # Handoff protocol, filière definitions
    _references/        # Reference docs agents can cite
    _plugins/           # Plugin metadata only (agents.txt per plugin)
    plugins/            # Plugin agent source files (NOT installed directly)
  hooks/                # .hooks.json files + scripts/
  instructions/         # Copilot instructions files
  skills/               # SKILL.md files (multi-step workflows)
  workflows/
    ci.yml              # Runs pytest + validate_agents on every push/PR
    release.yml         # Triggered by v* tag: builds dist, creates GitHub Release

tests/                  # pytest test suite (207+ tests)
schemas/                # JSON schemas (optional, not installed by default)
install.sh              # System-wide CLI installer (curl | sh)
.renga.example.yml      # Profile template copied to .renga.yml on renga install
```

---

## Key architecture decisions

### Single onboarding command
`renga install` is the only onboarding command. `renga init` was removed. `renga install` creates `.renga.yml`, installs agents/hooks/skills, and optionally installs plugins interactively.

### Plugin flat install
Plugin agents go directly in `.github/agents/` (not in a subdirectory) for Copilot discovery compatibility. Metadata (list of agent filenames) is stored in `.github/agents/_plugins/<name>/agents.txt`.

### Schemas are optional
`schemas/` is NOT created by default. Use `renga local init schemas` to copy schemas from the share dir. `renga doctor` treats missing schemas as informational (not an error).

### Models config in .renga.yml
Model settings live in the `models:` section of `.renga.yml`, not in a separate `_config/models.yml`. `renga models apply` stamps frontmatters from there.

### Share directory
Installed scripts and schemas are cached in `${XDG_DATA_HOME:-$HOME/.local/share}/renga/`. The compiled CLI reads from there at runtime (`$RENGA_SHARE_DIR`).

---

## Key variables (scripts/renga.sh)

```bash
ROOT_DIR="$(pwd)"                                    # project being managed
RENGA_DIR="$ROOT_DIR/.github/agents"
INSTRUCTIONS_DIR="$ROOT_DIR/.github/instructions"
SKILLS_DIR="$ROOT_DIR/.github/skills"
HOOKS_DIR="$ROOT_DIR/.github/hooks"
LOCK_FILE="$ROOT_DIR/.renga.lock"
CONFIG_FILE="$ROOT_DIR/.renga.yml"
RENGA_SHARE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/renga"
```

---

## Build & release process

```bash
# 1. Make changes to scripts/renga.sh and/or scripts/*.py
# 2. Build the compiled CLI
bash scripts/renga.sh build          # or: python3 scripts/build_dist.py
# 3. Commit
git add scripts/ && git commit -m "..."
# 4. Tag and push (triggers GitHub Actions release workflow)
git tag vX.Y.Z && git push origin main --tags
```

The release workflow (`release.yml`) runs `build_dist.py`, creates a tarball + SHA256 checksum, and uploads both as GitHub Release assets. `install.sh` verifies the checksum before installing.

**`dist/` is gitignored** — never commit it directly.

---

## Bash constraints

The CLI must work on **Bash 3.2** (macOS default). Avoid:
- `mapfile` / `readarray` — use `while read` loops instead
- `declare -A` (associative arrays) — not reliably available in Bash 3.2
- `${var,,}` / `${var^^}` — use `tr` or `python3` for case conversion

Use `python3` for anything complex (YAML parsing, JSON, regex substitution). Python 3.9+ is the minimum.

---

## Profiles (lite / standard / full)

Defined in `write_profile_config()` (line ~154 in `scripts/renga.sh`). The lite profile whitelist includes `orchestrator` — if it's missing, orchestrator won't be active on lite installs.

---

## validate_agents.py gotchas

- `repo_root` must be derived from `--agents-dir` (passed as `agents_dir.parent.parent`), NOT from `Path(__file__).parent.parent` — the script runs from the share dir, not the project.
- `validate_config_waivers(root_dir)` takes an explicit `root_dir: Path` parameter.
- Agent name from filename: use `f.name.replace('.agent.md', '')`, NOT `f.stem` (stem gives `orchestrator.agent`, not `orchestrator`).
- `user-invocable: false` is parsed as the string `'false'`, not the bool `False`. Check with `str(val).lower() != "false"`.
- Exit codes: 0=OK, 1=warnings (non-fatal), 2=errors. CI uses `|| { rc=$?; [ $rc -le 1 ] || exit $rc; }` to tolerate exit code 1.

---

## CI workflow gotchas

- `set -e` is active in GitHub Actions shell steps. If a command exits non-zero, the step dies immediately — `cmd; rc=$?` does NOT work. Use `cmd || { rc=$?; ...; }` instead.
- CI installs `pytest` and `pyyaml` explicitly (`pip install pytest pyyaml`).
- `validate_agents.py` is called directly from the repo (not from share dir) in CI — `--agents-dir .github/agents` is not passed, so `repo_root` falls back to `Path(__file__).parent.parent` = repo root. This is correct for CI.

---

## Test suite

```bash
python -m pytest tests/ -v          # run all tests
python -m pytest tests/test_validate_agents.py -v   # specific file
```

Tests live in `tests/`. Dependencies: `pytest`, `pyyaml`. No other external packages.

When changing string output of `generate_dashboard.py`, update assertions in `tests/test_generate_dashboard.py`. When changing `validate_agents.py` function signatures, update `tests/test_validate_agents.py`.

---

## Agent file format

```markdown
---
name: agent-name
description: "One-line description"
tools: ["execute", "read", "edit", "search"]
filiere: tech          # tech | data | product | governance
model: "Claude Sonnet 4.6 (copilot)"
user-invocable: true   # false for meta-agents (consensus-protocol, execution-modes)
---
# Agent: AgentName
...
## Collaboration / Handoff
...
```

Required frontmatter fields: `name`, `description`. All user-invocable agents need a Collaboration/Handoff section.

---

## Git / SSH

The repo remote is `github.com:renga-agents/renga.git` (SSH). If push is rejected due to workflow scope with HTTPS, use `ssh-add ~/.ssh/github_rsa` to load the SSH key, then push via the SSH remote.

---

## .renga.lock

Stores `version`, `installed_at`, `agents_installed`, `plugins`. Used by `cmd_update` to know the currently installed version. Somewhat redundant with `framework_version` in `.renga.yml` but also serves as a sentinel that `renga install` has been run.
