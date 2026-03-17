# ADR-008: Copilot Agent Hooks

**Date**: 2026-03-17
**Status**: Accepted
**Decision makers**: Founding team

## Context

Today, the renga framework relies on **textual instructions** (`.instructions.md`, `.agent.md`, skills) to guide agent behavior. This is effective for conveying conventions and preferences, but it has a fundamental limitation: **nothing programmatic prevents an agent from violating a rule**.

Examples of concrete gaps:

- An agent can execute `rm -rf /` or `git push --force`; saying "do not do that" is not a technical safeguard
- Worktree zoning, where an agent must only edit files in its assigned area, depends entirely on LLM self-discipline
- There is no audit trail of tools invoked during a session, which weakens incident traceability
- Quality checks such as linting, tests, and handoff validation remain textual expectations instead of automatic gates

GitHub Copilot now supports **hooks**: shell commands executed at key points in the agent lifecycle. Hooks are configured through JSON files under `.github/hooks/` and cover eight events: `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `agentStop`, `subagentStop`, and `errorOccurred`.

The `preToolUse` hook is especially important because it can **approve or reject** a tool invocation before execution, turning textual guidance into programmatic enforcement.

**Forces in tension**:

| Force | Direction |
| --- | --- |
| Security | Block dangerous commands and boundary overreach through enforcement, not suggestion |
| Traceability | Keep an audit trail of every tool invocation without logging sensitive data |
| Portability | Hooks are Copilot-specific, while the framework also supports Cursor and Claude Code (see [ADR-004](ADR-004-copilot-runtime.md)) |
| Simplicity | Add a subsystem without making onboarding heavier or slowing development |
| Customization | Let users add their own hooks without losing managed updates |
| Performance | Every `preToolUse` hook adds synchronous overhead, so latency must stay negligible |

## Decision

Introduce a **Copilot hooks** system organized around four functional domains, using a hybrid managed and user-owned distribution model.

### D1: Hybrid distribution (managed + user-owned)

The framework adopts a **two-layer** model, similar to the plugin system (see [ADR-006](ADR-006-plugin-system.md)):

- **Managed hooks**: `.github/hooks/*.hooks.json` and `.github/hooks/scripts/*.sh`, distributed by `renga install` and overwritten by `renga update`; these are the framework's core hooks
- **User-owned hooks**: `.github/agents/_local/hooks/`, created by the user and never touched by the CLI; they allow project-specific hooks or overrides for managed behavior
- **Resolution**: managed hooks load first, then `_local/hooks/` entries are merged in or override matching filenames

This model guarantees that:

1. `renga update` does not destroy a user's custom hooks
2. users receive framework improvements without manual intervention
3. override is possible without forking or editing distributed files

### D2: Anonymized logging for `userPromptSubmitted`

The `userPromptSubmitted` hook logs a **SHA-256 hash of the prompt**, never the raw prompt itself. This makes it possible to:

- detect repeated patterns, because the same hash means the same prompt
- correlate sessions without exposing user content
- comply with privacy and data-protection expectations

The raw prompt is **never** written to disk or sent to an external service.

### D3: Hooks are repo-level only

Hooks are defined at the **repository level** under `.github/hooks/`, not in the frontmatter of individual agents. No new `hooks` field is added to the `.agent.md` schema.

Rationale:

- Copilot hooks are natively repo-level; a per-agent field would require a custom preprocessor that generates JSON files, adding complexity without meaningful benefit
- Governance concerns such as security, audit, and quality apply uniformly across agents; fine-grained zoning remains inside the scripts themselves, for example `pre-tool-worktree.sh`
- A single configuration point makes the project's security posture easier to audit

### D4: No hook transpilation

Hooks are **specific to GitHub Copilot** and are not transpiled to Cursor (`.mdc`) or Claude Code (`CLAUDE.md`). This follows [ADR-004](ADR-004-copilot-runtime.md), which already accepts major feature loss outside Copilot.

The transpilation scripts `port_to_cursor.py` and `port_to_claude_code.py` add comments documenting this limitation in their respective outputs. Cursor and Claude Code have their own hook mechanisms, so future mapping remains possible, but parity is not a short-term goal.

### D5: One hook set for all Copilot runtimes

The same hooks apply identically to:

- **VS Code** in interactive agent mode
- **Copilot CLI** in terminal usage
- **Coding agent** in GitHub Actions and CI

There is no runtime-specific variant. Scripts must be idempotent and must not rely on runtime-specific features such as interactive UI.

### D6: Bash only

Hook scripts are written in **Bash**, compatible with `#!/usr/bin/env bash`. There is no native PowerShell or Windows-specific implementation.

Rationale: the framework targets macOS and Linux developers using VS Code on Unix-like systems. Windows remains workable through WSL2 and its Bash environment.

### Hook architecture

```text

.github/hooks/
├── security.hooks.json          ← preToolUse: policy enforcement
├── audit.hooks.json             ← postToolUse + session lifecycle: traceability
├── governance.hooks.json        ← preToolUse: worktree / zoning
├── quality.hooks.json           ← agentStop / subagentStop: verification
└── scripts/
    ├── pre-tool-security.sh     ← blocks dangerous commands (rm -rf, chmod 777, curl | sh, ...)
    ├── pre-tool-worktree.sh     ← verifies that the agent stays within its file zone
    ├── post-tool-audit.sh       ← structured log for each tool invocation (JSON lines)
    ├── session-init.sh          ← initializes the scratchpad and agent environment
    ├── session-cleanup.sh       ← archives session logs and cleans temporary files
    ├── quality-check.sh         ← lint, unit tests, and handoff validation
    └── error-tracker.sh         ← captures recurring error patterns

```

### Hook-to-domain mapping

| Hook event | JSON file | Script | Behavior |
| --- | --- | --- | --- |
| `preToolUse` | `security.hooks.json` | `pre-tool-security.sh` | Inspects the targeted command or file. Returns `approve` or `reject` with a reason. Blocks `rm -rf`, `git push --force`, `chmod 777`, `curl` pipes, and writes outside the allowed zone. |
| `preToolUse` | `governance.hooks.json` | `pre-tool-worktree.sh` | Verifies that the tool targets a file inside the agent's allowed zone, based on the active worktree and lane conventions. |
| `postToolUse` | `audit.hooks.json` | `post-tool-audit.sh` | Writes JSON lines to `.copilot/logs/audit-YYYY-MM-DD.jsonl` with timestamp, tool, sanitized args, truncated result, and source agent. |
| `sessionStart` | `audit.hooks.json` | `session-init.sh` | Creates the session scratchpad, loads project environment variables, and writes a session-start entry to the audit log. |
| `sessionEnd` | `audit.hooks.json` | `session-cleanup.sh` | Archives the scratchpad, compresses session logs, and cleans `.copilot/tmp/` temporary files. |
| `agentStop` | `quality.hooks.json` | `quality-check.sh` | Verifies that the agent produced a valid handoff and that tests and lint checks pass. |
| `subagentStop` | `quality.hooks.json` | `quality-check.sh` | Same checks as `agentStop`, adapted to subagent context. |
| `errorOccurred` | `audit.hooks.json` | `error-tracker.sh` | Captures the error in the audit log and detects recurring patterns. |
| `userPromptSubmitted` | `audit.hooks.json` | `post-tool-audit.sh` | Logs only the SHA-256 prompt hash, as defined in D2. |

### Audit log format

Logs are written as JSON Lines under `.copilot/logs/`:

```jsonl

{"ts":"2026-03-17T14:32:01Z","event":"tool_use","tool":"run_in_terminal","agent":"backend-dev","args_hash":"a1b2c3","status":"approved","hook":"pre-tool-security"}
{"ts":"2026-03-17T14:32:02Z","event":"tool_use","tool":"run_in_terminal","agent":"backend-dev","duration_ms":1200,"exit_code":0,"hook":"post-tool-audit"}
{"ts":"2026-03-17T14:32:05Z","event":"session_start","agent":"orchestrator","scratchpad": ".copilot/memory/scratchpad-xyz.md"}
{"ts":"2026-03-17T14:35:00Z","event":"prompt_submitted","prompt_hash":"e3b0c44298fc1c14...","agent":"orchestrator"}

```

### Script interface contract

Each script receives hook data on **stdin** as JSON serialized by Copilot and returns:

- **Exit code 0**: success, or `approve` for `preToolUse`
- **Exit code 1**: failure, or `reject` for `preToolUse`
- **stdout**: optional message shown to the agent, such as a rejection reason or warning
- **stderr**: reserved for debug logs and not forwarded to the agent

Scripts must:

- finish in **under 5 seconds** to satisfy Copilot timeouts
- be idempotent and avoid cumulative side effects
- avoid network dependencies such as HTTP requests
- sanitize all JSON input before processing, to reduce tool-argument injection risk

## Consequences

### Positive

- **Programmatic enforcement**: governance rules for security, zoning, and quality become automatic gates instead of textual suggestions
- **Automatic audit trail**: every session produces structured logs usable for debugging, postmortems, and compliance
- **Defensive security layer**: `preToolUse` hooks provide a technical barrier against dangerous commands regardless of model behavior
- **Multi-agent consistency**: the same rules apply uniformly to all agents without depending on prompt quality
- **Automatic distribution**: managed hooks are installed and updated by the CLI
- **Low-friction customization**: `_local/hooks/` lets users adapt behavior without editing managed files

### Negative

- **Copilot dependency**: hooks only work on GitHub Copilot; Cursor and Claude Code do not benefit from them
- **Synchronous overhead**: every `preToolUse` hook adds a shell call before tool execution, with measurable impact if scripts grow too slow
- **New subsystem**: four JSON files plus seven Bash scripts must be maintained, tested, and documented
- **Possible false positives**: overly strict heuristics in `pre-tool-security.sh` may block legitimate commands and require tuning
- **Debug complexity**: when a hook rejects an action, the rejection message must be clear enough for the agent to recover productively

### Risks

- **Copilot hooks API changes without backward compatibility**, mitigated by script versioning and JSON schema validation in `schemas/hooks.schema.json`
- **LLM circumvention**: a creative agent may try to reformulate a dangerous command to bypass a filter, mitigated by allowlist strategies for critical cases
- **Performance degradation** during long sessions if audit scripts accumulate too much I/O, mitigated by log rotation and append-only writes

## Alternatives Considered

### Hooks in `.agent.md` frontmatter (per agent)

Add a `hooks` field to every agent's YAML frontmatter. Rejected:

- the Copilot `.agent.md` format does not support such a field, so a custom preprocessor would be required
- governance concerns such as security and audit are cross-cutting and should apply uniformly
- 54+ agents times multiple hooks would create a configuration explosion

### User-owned hooks only

Require users to create and maintain all hooks manually. Rejected:

- every framework user would have to rebuild the same security and audit hooks
- there would be no guaranteed security baseline for a project with no custom hooks
- governance improvements would require manual synchronization for every project

### Managed hooks only

Ship hooks but prevent users from modifying or extending them. Rejected:

- this blocks project-specific customization
- it creates frustration when a managed hook produces false positives
- it violates the extensibility principle documented in [ADR-006](ADR-006-plugin-system.md)

### Transpile hooks to Cursor and Claude Code

Map Copilot hooks onto equivalent mechanisms in other platforms. Rejected:

- hook APIs are incompatible across platforms
- the transpilation effort is not justified given Copilot's role as the primary runtime
- Bash scripts would need platform-specific adaptations
- the decision is reversible if parity becomes a future priority

### PowerShell for Windows compatibility

Write hooks in PowerShell, or maintain Bash and PowerShell versions. Rejected:

- the framework currently targets macOS and Linux
- WSL2 already provides a viable Bash path for Windows users
- dual script maintenance would double testing and maintenance cost

## Relationships

- **Extends [ADR-004](ADR-004-copilot-runtime.md)**: hooks leverage a native GitHub Copilot capability and reinforce the choice of Copilot as the primary runtime
- **Completes [ADR-006](ADR-006-plugin-system.md)**: the hybrid managed and user-owned distribution model mirrors the two-layer plugin pattern
- **Reinforces [ADR-002](ADR-002-filesystem-as-state.md)**: audit logs and session scratchpads remain local filesystem artifacts
- **Operationalizes [ADR-001](ADR-001-hub-and-spoke.md)**: quality hooks on `agentStop` and `subagentStop` formalize the feedback loop between spoke agents and the hub orchestrator
