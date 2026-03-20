# CLAUDE.md — renga project context

## What this project is

**renga** is a Bash CLI that installs a team of specialized AI agents (`.agent.md` files) into any project for use with VS Code GitHub Copilot. Users run `renga install` once; agents appear in Copilot via `@agent-name`.

The CLI lives in `scripts/renga.sh` (source) and `dist/renga` (compiled artifact, gitignored). `install.sh` installs the CLI system-wide from a GitHub Release tarball.

---

## Repository structure

```text
scripts/
  renga.sh              # CLI source — edit this, never dist/renga directly
  build_dist.py         # Packages dist/ from .github/agents, hooks, skills, etc.
  validate_agents.py    # Validates .agent.md frontmatter and cross-references
  generate_dashboard.py # Generates a Markdown performance dashboard (reads .renga/memory/)
  consolidate_memory.py # Consolidates per-session memory files into master files
  validate_hooks.py     # Validates .hooks.json files
  agent_parser.py       # Shared parser for Markdown tables (used by dashboard)

.github/
  agents/               # The 51 core agent files (*.agent.md)
    _profiles/          # Tool profiles (advisory/technical), filière definitions
    _references/        # ONE remaining file: replicate-models.md (game-studio only)
    _plugins/           # Plugin metadata only (agents.md per plugin)
    plugins/            # Plugin agent source files (NOT installed directly)
  hooks/                # .hooks.json files + scripts/
  instructions/         # Copilot instructions files
  skills/               # SKILL.md files (15 skills — see §Skills architecture below)
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

Plugin agents go directly in `.github/agents/` (not in a subdirectory) for Copilot discovery compatibility. Metadata (list of agent filenames) is stored in `.github/agents/_plugins/<name>/agents.md`.

### Schemas are optional

`schemas/` is NOT created by default. Use `renga local init schemas` to copy schemas from the share dir. `renga doctor` treats missing schemas as informational (not an error).

### Models config in .renga.yml

Model settings live in the `models:` section of `.renga.yml`, not in a separate `_config/models.yml`. `renga models apply` stamps frontmatters from there.

### Share directory

Installed scripts and schemas are cached in `${XDG_DATA_HOME:-$HOME/.local/share}/renga/`. The compiled CLI reads from there at runtime (`$RENGA_SHARE_DIR`).

### Skills over references

**Copilot loads skills natively** (listed in agent `skills:` frontmatter) without a file read. `_references/` files require an explicit file read which agents can miss or duplicate. All operational knowledge for seiji has been migrated to skills (v1.0.23-24). `_references/` now contains only `replicate-models.md`.

---

## Skills architecture (`.github/skills/`)

15 skills total. Seiji declares orchestration skills; specialized agents declare domain-specific skills.

| Skill | Content | ERR rules | Declared by |
| --- | --- | --- | --- |
| `task-decomposition` | L0-L4 classification, acceptance criteria, dry-run gate | ERR-014, ERR-024, ERR-020, ERR-028 | seiji, qa-engineer, software-architect |
| `dag-patterns` | 3 full DAG examples (fullstack, auth, ML) | ERR-004, ERR-015 | seiji, software-architect, architecture-reviewer |
| `auto-triggers` | Trigger table, escalation table, circuit breaker, ERR-020 | ERR-016, ERR-017, ERR-020 | seiji, security-engineer, incident-commander |
| `worktree-lifecycle` | Creation, zoning, multi-MOE, closure, rollback | ERR-013 | seiji, git-expert, devops-engineer |
| `handoff-protocol` | Handoff block format, standard chains (Product/Analytics/Incident) | — (pointers to other skills) | seiji, git-expert, code-reviewer |
| `commit-discipline` | Coherent batches, asset/source separation, multiline, wave cadence, file plan | ERR-001, ERR-004, ERR-005, ERR-015, ERR-018 | seiji |
| `quality-control` | Report verification, review loop, browser validation, retrospective | ERR-019, ERR-021, ERR-022, ERR-023, ERR-025 | seiji |
| `dispatch-protocol` | QA scope, security brief, wave 0 constraints, coverage floors, multi-track catalog | ERR-007, ERR-008, ERR-013, ERR-014, ERR-024, ERR-026 | seiji |
| `hooks-catalog` | Active hooks table, allowlist, protected paths | — | seiji |
| `agent-roster` | Roster resolution from `.renga.yml` (whitelist/all/absent), scratchpad logging | ERR-027 | seiji |
| `working-memory` | `.renga/` structure, read/write conventions, file naming, retention rules | — | seiji, devops-engineer, database-engineer, infra-architect, scrum-master, qa-engineer |
| `tdd-protocol` | TDD wave protocol (wave 1/2/3), ERR-007 forbidden files, mocking rules, mandatory red commit | ERR-007 | qa-engineer, backend-dev |
| `code-review-protocol` | 6-step review process (overview→security→correctness→maintainability→performance→tests), 🔴/🟡/🟢 verdict | — | code-reviewer, security-engineer, architecture-reviewer |
| `execution-modes` | 5 execution modes (sequential, parallel, waves, super-wave, mega-wave), platform constraints, filesystem safety matrix, fan-out rules | — | seiji |
| `consensus-protocol` | Multi-wave consensus protocol, trigger thresholds, participation format, convergence criteria, cross-stream arbitration, super-wave flow | — | seiji |

Note: some ERR rules appear in multiple skills (from different angles, e.g. ERR-014 in both task-decomposition and dispatch-protocol). This is intentional — the skill that *applies* the rule embeds it.

---

## Seiji (lead orchestrator agent)

`seiji.agent.md` is the entry point for all L1+ tasks. Key behaviors:

- **Self-config loading (mandatory)**: every subagent prompt seiji dispatches MUST begin with `"Start by reading your configuration file at .github/agents/<agent-name>.agent.md..."` — governance incident if omitted (ERR-026)
- **Agent roster**: resolved at session start via skill `agent-roster`. Reads `.renga.yml` agents.mode (whitelist/all/absent). Written to scratchpad before DAG construction.
- **Context window discipline**: seiji never reads source code directly. Max 2 file reads per task (outside memory). Skills are loaded natively — no read quota cost.
- **Report persistence (ERR-025)**: each subagent writes its own full report to `.renga/reports/<slug>/wave-<N>-<agent-name>.md` and returns only a structured summary to seiji (verdict + top-3 P0 + file path).

---

## `.renga/` directory (agent working memory)

Created by `renga install` in the user's project. **Not to be confused with `.github/`** which is the framework source.

```text
.renga/
  memory/
    scratchpad.md              # Session index (seiji)
    scratchpad-<slug>.md       # Active session scratchpad (deleted on closure)
    project-context.md         # Stack, constraints, structuring decisions
    agent-performance[-<slug>].md  # Agent scoring
    error-patterns[-<slug>].md     # Error patterns
    prompt-improvements.md     # Prompt improvement changelog
    rubric.md                  # Scoring rubric for retrospectives
    vps-access.md              # (project-specific) SSH/infra access details
  reports/
    .current-session           # Active session UUID (persisted for hook scripts)
    <slug>/
      index.md                 # Wave/agent report index
      wave-<N>-<agent>.md      # Individual agent reports
      tool-audit.jsonl         # Hook: tool usage log
      quality.jsonl            # Hook: agent stop events
      session.log              # Hook: session start/end
      errors.jsonl             # Hook: error events
```

**Where `.renga/` is referenced**:

- CLI: `renga.sh` (creates, adds to .gitignore)
- Hooks: 5 scripts in `.github/hooks/scripts/` (write reports at runtime)
- Agents: seiji (11 refs), devops-engineer, database-engineer, infra-architect, scrum-master
- Skills: worktree-lifecycle, quality-control
- Scripts: consolidate_memory.py, generate_dashboard.py
- Tests: test_hook_scripts.sh, PTEST-019.yml
- Instructions: deployment.instructions.md

**SESSION_ID persistence**: hook scripts are separate subprocesses — env vars don't survive between them. SESSION_ID is written to `.renga/reports/.current-session` by `session-init.sh` and read by all other hook scripts.

**Debug mode**: create `.hook-debug` (empty file) at project root to dump raw hook payloads to `/tmp/renga-hook-debug.log`.

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

**SSH push**: if push is rejected, run `ssh-add ~/.ssh/github_rsa` first (remote is SSH: `github.com:renga-agents/renga.git`).

---

## Bash constraints

The CLI must work on **Bash 3.2** (macOS default). Avoid:

- `mapfile` / `readarray` — use `while read` loops instead
- `declare -A` (associative arrays) — not reliably available in Bash 3.2
- `${var,,}` / `${var^^}` — use `tr` or `python3` for case conversion

Use `python3` for anything complex (YAML parsing, JSON, regex substitution). Python 3.9+ is the minimum.

---

## Profiles (lite / standard / full)

Defined in `write_profile_config()` (line ~154 in `scripts/renga.sh`). The lite profile whitelist includes `seiji` (formerly `orchestrator`) — if it's missing, seiji won't be active on lite installs.

---

## validate_agents.py gotchas

- `repo_root` must be derived from `--agents-dir` (passed as `agents_dir.parent.parent`), NOT from `Path(__file__).parent.parent` — the script runs from the share dir, not the project.
- `validate_config_waivers(root_dir)` takes an explicit `root_dir: Path` parameter.
- Agent name from filename: use `f.name.replace('.agent.md', '')`, NOT `f.stem` (stem gives `orchestrator.agent`, not `orchestrator`).
- `user-invocable: false` is parsed as the string `'false'`, not the bool `False`. Check with `str(val).lower() != "false"`.
- Exit codes: 0=OK, 1=warnings (non-fatal), 2=errors. CI uses `|| { rc=$?; [ $rc -le 1 ] || exit $rc; }` to tolerate exit code 1.

---

## CI workflow gotchas

- `set -e` causes the step to exit immediately on a non-zero exit code — `cmd; rc=$?` never reaches `rc=$?` because the step dies on `cmd`. Use `cmd || { rc=$?; ...; }` instead.
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
user-invocable: true   # false for filière orchestrators (orchestrator-tech, etc.)
skills: [skill-name]   # optional — skills loaded natively by Copilot
agents: ["*"]          # optional — declares sub-agent access; ["*"] = all agents
---
# Agent: AgentName
...
## Collaboration / Handoff
...
```

Required frontmatter fields: `name`, `description`. All user-invocable agents need a Collaboration/Handoff section. The `agents: ["*"]` wildcard in seiji's frontmatter declares that seiji can delegate to any agent — this is a Copilot convention for orchestrators.

---

## .renga.lock

Stores `version`, `installed_at`, `agents_installed`, `plugins`. Used by `cmd_update` to know the currently installed version. Somewhat redundant with `framework_version` in `.renga.yml` but also serves as a sentinel that `renga install` has been run.

---

## Pending architectural work

- **Rename `.renga/` → `.renga/`**: ~65 occurrences across ~14 files. Feasible in one session. Requires a migration step in `renga.sh` (detect and rename existing `.renga/` directory). See §`.renga/` for the full file list.
