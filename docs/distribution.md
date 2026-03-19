# Distribution and Installation

> **Target audience**: developers and tech leads who want to integrate renga into an existing project
> **Prerequisites**: Git ≥ 2.30, VS Code with GitHub Copilot, curl, Python ≥ 3.9
> **Last updated**: 2026-03-17
> **Estimated reading time**: 12 min

---

## Table of Contents

- [Overview](#overview)
- [CLI Installation](#cli-installation)
- [Project Initialization](#project-initialization)
- [Framework Installation](#framework-installation)
- [Updating](#updating)
- [Plugin Management](#plugin-management)
- [Custom Agents and the `_local/` Convention](#custom-agents-and-the-_local-convention)
- [File Categories](#file-categories)
- [Installed File Structure](#installed-file-structure)
- [Project Configuration](#project-configuration)
- [What Is NOT Distributed](#what-is-not-distributed)
- [FAQ](#faq)
- [Manual Method (Legacy)](#manual-method-legacy)

---

## Overview

renga is distributed as a set of Markdown and YAML files that you integrate directly into your project. No NPM package, no runtime dependency — only files that GitHub Copilot detects automatically.

The `renga` CLI automates the entire lifecycle:

```text

install CLI → init → install → update → plugin add

```

| Step | Command | What it does |
| --- | --- | --- |
| **1. CLI** | `curl … \| sh` | Installs the `renga` binary into `~/.local/bin/` |
| **2. Init** | `renga init` | Creates `.renga.yml`, `_local/`, and the CI workflow |
| **3. Install** | `renga install` | Downloads the agents from a GitHub Release and writes the lock file |
| **4. Update** | `renga update` | Updates to the latest version |
| **5. Plugins** | `renga plugin add <name>` | Adds a thematic agent pack |

---

## CLI Installation

A single one-liner:

```bash

curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh

```

The CLI is installed in `~/.local/bin/renga`. If that directory is not in your `PATH`, the script will show you the line to add to your `~/.zshrc` or `~/.bashrc`.

### Install a Specific Version

```bash

curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh -s -- --version 1.2.0

```

### Verify the Installation

```bash

renga help

```

> [!TIP]
> The CLI requires `curl` and `python3` (≥ 3.9) to work. Run `renga doctor` after installation to verify that everything is in place.

---

## Project Initialization

From the root of your project:

```bash

renga init

```

This command:

- Copies `.renga.example.yml` → `.renga.yml` (if missing — never overwritten)
- Creates the `_local/` folders in `.github/agents/` and `.github/instructions/`
- Creates `.renga/memory/` for agent session memory
- Generates the CI workflow `.github/workflows/agent-validate.yml` (if missing)

### Result

```text

my-project/
├── .github/
│   ├── agents/
│   │   └── _local/                ← Your custom agents
│   ├── instructions/
│   │   └── _local/                ← Your custom instructions
│   └── workflows/
│       └── agent-validate.yml     ← Automatic validation CI
├── .renga/
│   └── memory/                    ← Local session memory
├── .renga.yml                     ← Project configuration
└── ...

```

> [!IMPORTANT]
> `renga init` is idempotent — it creates only missing files and never overwrites an existing file. You can run it again safely.

---

## Framework Installation

```bash

renga install

```

The command downloads the latest release from `OWNER/renga` on GitHub, extracts the agents and instructions, and then writes the `.renga.lock` lock file.

### Target a Specific Version

```bash

renga install --version 2.1.0

```

### What `install` Does

1. **Downloads** the `.tar.gz` artifact from the GitHub Release
2. **Checks** for the presence of `manifest.json` in the artifact
3. **Copies agents** into `.github/agents/` (filtered by the whitelist in `.renga.yml` if configured)
4. **Copies instructions** into `.github/instructions/`
5. **Copies hooks** from `.github/hooks/` into `.github/hooks/` (if present in the release)
6. **Copies `_references/`** and the validation JSON schema
7. **Creates `_local/`** in both folders (if it does not already exist)
8. **Writes `.renga.lock`** with the installed version, the date, and the number of agents

### `.renga.lock` File

Generated automatically, it records the installation state:

```yaml

version: "2.1.0"
installed_at: "2026-03-17T14:30:00"
agents_installed: 52
plugins: []

```

> [!IMPORTANT]
> **Commit `.renga.lock`** in your repository. It lets the whole team know which framework version is installed and serves as the reference for updates.

---

## Updating

### Update to the Latest Version

```bash

renga update

```

The command checks the current version in `.renga.lock`, then reruns the installation with the latest available release.

### Check Available Updates Without Modifying Files

```bash

renga update --dry-run

```

The dry run shows the current version and the available version without downloading or modifying anything.

### Update to a Specific Version

```bash

renga update --version 2.2.0

```

### What Is Preserved During an Update

| Element | Behavior |
| --- | --- |
| `.renga.yml` | **Never touched** — user-owned file |
| `_local/` (agents and instructions) | **Never touched** — user-owned folder |
| `_plugins/` | **Never touched** — plugins installed separately |
| `.renga.lock` | **Rewritten** with the new version |
| Framework agents and instructions | **Overwritten** by the new versions |

### Recommended Frequency

| Situation | Frequency |
| --- | --- |
| Project under active development | Every 2 to 4 weeks |
| Project in maintenance mode | At each major framework release |
| After a breaking-change announcement | Immediately |

---

## Plugin Management

Plugins are thematic agent packs distributed in the `_plugins/` folder of the release.

### Add a Plugin

```bash

renga plugin add <plugin-name>

```

The plugin is downloaded from the latest release and installed into `.github/agents/_plugins/<name>/`.

### Remove a Plugin

```bash

renga plugin remove <plugin-name>

```

### List Installed Agents and Plugins

```bash

renga plugin list

```

Displays the core agents and the plugins with their respective number of agents.

> [!TIP]
> The `renga list` command also shows the same overview (core agents + installed plugins).

---

## Custom Agents and the `_local/` Convention

The `_local/` folder is the reserved area for your custom agents and instructions:

```text

.github/
├── agents/
│   ├── _local/                      ← Your custom agents
│   │   ├── my-agent.agent.md
│   │   └── my-workflow.agent.md
│   ├── orchestrator.agent.md        ← Framework agent (managed)
│   └── ...
└── instructions/
    ├── _local/                      ← Your custom instructions
    │   └── my-project.instructions.md
    ├── typescript.instructions.md   ← Framework instruction (managed)
    └── ...

```

### Non-Overwrite Guarantee

The `_local/` folders are **never touched** by `renga install` or `renga update`. The CLI creates them at initialization, then always ignores them.

Put the following in `_local/`:

- **Agents specific** to your project or team
- **Coding instructions** specific to your codebase
- Any file you do not want to lose during an update

Agents in `_local/` are detected automatically by Copilot, just like the framework agents.

→ For reusable agents across multiple projects, prefer the [plugin system](plugin-system.md).

---

## File Categories

The CLI distinguishes three categories of files — understanding this distinction avoids surprises during updates.

### Managed Files (handled by the CLI)

Framework files, downloaded and overwritten on each `install` / `update`:

| File | Location |
| --- | --- |
| Core agents | `.github/agents/*.agent.md` |
| Core instructions | `.github/instructions/*.instructions.md` |
| Internal references | `.github/agents/_references/` |
| Validation schema | `schemas/agent.schema.json` |

**Do not edit these files directly** — your changes will be lost at the next update. Use `_local/` or `.renga.yml` to customize.

### User-Owned Files (your property)

Files that the CLI creates only once (or never) and then no longer modifies:

| File | Created by | Note |
| --- | --- | --- |
| `.renga.yml` | `renga init` | Never overwritten |
| `.github/agents/_local/` | `renga init` | Never touched by update |
| `.github/instructions/_local/` | `renga init` | Never touched by update |
| `.github/agents/_plugins/` | `renga plugin add` | Never touched by update |
| `.github/workflows/agent-validate.yml` | `renga init` | Never overwritten if already present |
| `.renga/memory/` | `renga init` | Local session data |

### Lock File

| File | Role |
| --- | --- |
| `.renga.lock` | Installed version, date, number of agents, plugins. Rewritten on every `install` / `update`. Commit it to Git. |
| `manifest.json` | Present only in the release artifact — contains the build version, the list of agents, and a `hooks` section (path + sha256 of each hook). Not copied into your project. |

---

## Installed File Structure

After `renga init` + `renga install`, your project contains:

```text

my-project/
├── .github/
│   ├── agents/                          ← Framework core (managed)
│   │   ├── orchestrator.agent.md        ← Main orchestrator
│   │   ├── backend-dev.agent.md         ← Backend agent
│   │   ├── frontend-dev.agent.md        ← Frontend agent
│   │   ├── qa-engineer.agent.md         ← QA / test agent
│   │   ├── ...                          ← Core agents
│   │   ├── _config/
│   │   │   └── models.yml               ← LLM model configuration
│   │   ├── _local/                      ← Your custom agents (user-owned)
│   │   ├── _plugins/                    ← Installed plugins (user-owned)
│   │   ├── _profiles/                   ← Permission profiles (advisory, technical)
│   │   └── _references/                 ← Internal reference documents
│   ├── instructions/                    ← Coding rules by technology (managed)
│   │   ├── typescript.instructions.md
│   │   ├── react.instructions.md
│   │   ├── security.instructions.md
│   │   ├── injection-resistance.instructions.md
│   │   ├── _local/                      ← Your custom instructions (user-owned)
│   │   └── ...
│   └── workflows/
│       └── agent-validate.yml           ← Validation CI (user-owned)
├── .renga/
│   └── memory/                          ← Session memory (user-owned)
├── .renga.yml                           ← Project configuration (user-owned)
├── .renga.lock                          ← Installed version (lock)
├── schemas/
│   └── agent.schema.json                ← Validation schema (managed)
└── ...                                  ← The rest of your project

```

---

## Project Configuration

### `.renga.yml` File

Main configuration file, created by `renga init` at the root of your project. It controls which agents are active, criticality thresholds, and project conventions.

```yaml

version: "1.0"

project:
  name: "my-project"
  description: "Next.js web app with REST API, 3 developers"

agents:
  mode: "whitelist"          # "all", "whitelist", or "blacklist"
  include:
    - software-architect
    - backend-dev
    - frontend-dev
    - qa-engineer
    - code-reviewer
    - debugger
    - devops-engineer

thresholds:
  l2_min_agents: 2           # Reduce for smaller teams
  l3_min_agents: 3
  max_retries: 3

stack:
  backend: "Next.js API Routes"
  frontend: "Next.js 15 (App Router)"
  database: "PostgreSQL 16"
  test_framework: "Vitest + Playwright"

```

→ Full reference with every documented field: `.renga.example.yml` in the source repository.

### Coding Instructions

The `.github/instructions/` folder contains coding rules by technology. Keep the ones that match your stack and remove the others:

```bash

# Example: keep only TypeScript, React, and security rules
cd .github/instructions/
rm go.instructions.md python.instructions.md strapi.instructions.md animations.instructions.md

```

> [!TIP]
> The `security.instructions.md`, `injection-resistance.instructions.md`, and `engineering-principles.instructions.md` instructions are cross-cutting — keep them regardless of your stack.

---

## What Is NOT Distributed

Some folders in the renga repository are specific to developing the framework itself and should **not** be copied into your projects:

| Folder / file | Reason for exclusion |
| --- | --- |
| `.renga/memory/` | Steering memory — local data generated by agents over sessions, **specific to each project** |
| `.renga/reports/` | Audit and session reports — local data generated automatically, **specific to each project** |
| `output/` (Cursor `.mdc`, Claude Code `CLAUDE.md`) | Exports generated by the porting scripts (`scripts/port_to_cursor.py`, etc.) — this is **not** framework core |
| `.github/hooks/_local/` | Custom user hooks — never included in the distribution (`build_dist.py` excludes `_local/`) |
| `docs/` | Documentation for the framework itself — useful as reference, not required in your project |
| `scripts/` | Framework maintenance scripts (validation, dashboard generation) |
| `tests/` | Framework prompt regression tests |
| `reports/` | Framework monitoring dashboard |

> [!IMPORTANT]
> The `.renga/memory/` and `.renga/reports/` folders may eventually be created automatically by agents when they run in your project. They contain local session data. Add them to your `.gitignore` if you do not want to commit them:
>
> ```gitignore
>
> .renga/memory/
> .renga/reports/
>
> ```

---

## FAQ

### How do I update without losing my customizations?

User-owned files are never modified by the CLI:

1. **`.renga.yml`** — never overwritten by `install` or `update`.
2. **`_local/`** — never touched. Your custom agents and instructions are preserved.
3. **`_plugins/`** — never touched by `update`. Managed exclusively through `renga plugin`.

**Best practice**: do not modify managed framework files directly. Use `.renga.yml` to configure, `_local/` to extend, and plugins to reuse across projects.

### How do I install only a subset of agents?

Two approaches:

**Approach 1 — Install everything, filter via configuration** (recommended):

```yaml

# .renga.yml
agents:
  mode: "whitelist"
  include:
    - backend-dev
    - frontend-dev
    - qa-engineer
    - software-architect

```

All files are present, but only the listed agents are loaded by the orchestrator. The orchestrator and its sub-orchestrators are always active regardless of the mode.

**Approach 2 — Filter at installation time**:

If `.renga.yml` is configured in `whitelist` mode before `renga install`, only the listed agents are copied. Excluded agents are not downloaded.

### How do I know which framework version is installed?

Check `.renga.lock` at the root of your project:

```bash

cat .renga.lock

```

```yaml

version: "2.1.0"
installed_at: "2026-03-17T14:30:00"
agents_installed: 52
plugins: []

```

### How do I verify that the setup is correct?

```bash

renga doctor

```

The diagnostic checks: Python ≥ 3.9, presence of `.renga.yml`, `.agent.md` files in `.github/agents/`, validity of the JSON schema, and presence of the essential scripts.

### Agents are not detected by Copilot after installation

Copilot detects `.agent.md` files in `.github/agents/` **at the root of the workspace opened in VS Code**. Check that:

1. The `.github/agents/` folder is indeed at the workspace root (not in a subfolder).
2. You opened the **correct folder** in VS Code — if you opened a parent or child folder, the agents will not be detected.
3. The GitHub Copilot extension is active and agent mode is available.

### How do I share my custom agents with other projects?

Two options:

1. **Direct copy**: copy the `.agent.md` file from `_local/` into the `_local/` of another project.
2. **Plugin**: package your agents into a distributable plugin via the plugin system — see [plugin-system.md](plugin-system.md).

---

## Manual Method (Legacy)

> [!NOTE]
> The methods below are kept for special cases (environments without CLI access, network constraints, integration into an existing monorepo). **In all other cases, use the `renga` CLI.**

### Git Subtree

Integrates the framework directly into your project's history:

```bash

# Add the remote
git remote add renga https://github.com/OWNER/renga.git

# Import the agents, then the instructions
git subtree add --prefix=.github/agents renga main --squash
git subtree add --prefix=.github/instructions renga main --squash

# Update later
git subtree pull --prefix=.github/agents renga main --squash

```

**Advantages**: everything is in the history, transparent for the team when cloning.

**Disadvantages**: no lockfile, manual conflict handling, no managed / user-owned separation.

### Manual Copy

```bash

git clone https://github.com/OWNER/renga.git /tmp/renga
cp -r /tmp/renga/.github/agents/ .github/agents/
cp -r /tmp/renga/.github/instructions/ .github/instructions/
cp /tmp/renga/.renga.example.yml .renga.yml
rm -rf /tmp/renga

```

**Advantages**: simple, no dependency.

**Disadvantages**: no traceability of the installed version, updates are entirely manual.

### Git Submodule

```bash

git submodule add https://github.com/OWNER/renga.git .github/renga-src

```

**Advantages**: version pinned by SHA.

**Disadvantages**: each team member must run `git submodule update --init`, CI must be configured with `--recurse-submodules`, and files are not directly under `.github/agents/` (symlink or copy required).

**Recommendation**: prefer the `renga` CLI, which handles versioning, the lockfile, and file separation automatically.
