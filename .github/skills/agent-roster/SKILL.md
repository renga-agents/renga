---
name: agent-roster
description: "Resolves the active agent list from .renga.yml (whitelist / all / absent) and writes the roster to the scratchpad before DAG construction."
argument-hint: "Read .renga.yml and resolve the roster for this session"
user-invocable: true
---
# Skill: Agent Roster Resolution

Seiji must resolve the active agent list at the start of every session, **before** building the DAG.

---

## Step 1 — Read `.renga.yml`

Read the `agents:` section of `.renga.yml` at the project root.

### Case A — `mode: "whitelist"`

```yaml
agents:
  mode: "whitelist"
  include:
    - seiji
    - backend-dev
    - qa-engineer
```

The active roster is exactly `include`. Do not dispatch any agent not listed there.

### Case B — `mode: "all"`

```yaml
agents:
  mode: "all"
```

`mode: "all"` means every installed agent is active. Resolve the full list by scanning `.github/agents/`:

```
list all *.agent.md files in .github/agents/ (not in subdirectories)
strip the .agent.md suffix → agent name
exclude files whose name starts with _ (profiles, references, plugin metadata)
```

Expected result: a flat list of agent names (e.g. `seiji`, `backend-dev`, `qa-engineer`, …).

### Case C — `.renga.yml` absent

No config file means the project was not bootstrapped with `renga install`. Treat as `mode: "all"` and scan `.github/agents/` as above. Log a warning in the scratchpad.

---

## Step 2 — Apply Plugin Agents

If `plugins:` is non-empty in `.renga.yml`, plugin agents are already present in `.github/agents/` and are included automatically by the scan (Case B), or must be added to the whitelist explicitly (Case A).

---

## Step 3 — Write the Roster to the Scratchpad

After resolution, log the active roster at the top of `scratchpad-<slug>.md`:

```
## Active roster (resolved YYYY-MM-DDTHH:MM)
mode: whitelist | all
agents: [seiji, backend-dev, qa-engineer, ...]
source: .renga.yml | scan
```

This makes the roster auditable and prevents seiji from inventing agent names mid-session.

---

## Step 4 — Handle Domain Gaps (User-Requested or Proactively Detected)

Apply this step **before DAG construction**, in two passes:

### Pass A — User-requested agents not in roster

Compare every role or agent persona named by the user against the resolved roster. For each unmatched role, determine whether an existing agent covers the specialization adequately.

### Pass B — Proactive domain gap detection

Even when the user names no specific agents, ask: *does this task's domain require expertise not covered by the current roster?* Examples of gaps seiji should detect proactively:

- Smart Grid / electrical systems → no electrical-engineer or SCADA-specialist in core roster
- Pharmaceutical / clinical research → no clinical-data-manager or regulatory-affairs-specialist
- IoT firmware / embedded systems → no iot-engineer or embedded-developer
- Energy markets / carbon economics → no energy-economist or carbon-analyst

If yes, treat the missing specialization as a domain gap and apply the policy below.

### Domain gap policy

| Condition | Action |
|---|---|
| Adequate coverage by an existing agent | Log the mapping in the scratchpad under `## Roster Mapping`; never silently remap without documentation |
| Genuine gap + specialization **central to the task** (blocks wave design or acceptance criteria) | Create a new `.github/agents/<name>.agent.md` — the agent becomes a full roster member for this and future sessions |
| Genuine gap + specialization **peripheral** (marginal scope, handled at the edges by a neighbor) | Log as gap in scratchpad; delegate to the closest agent with an explicit scope note |

### Dynamic agent creation

When creating a new agent file, use the standard format and naming convention (`electrical-engineer`, `iot-specialist`, `energy-economist`):

```markdown
---
name: <role-name>
filiere: <tech|data|product|governance>
user-invocable: false
description: "<one-line description of domain and scope>"
tools: ["read", "edit", "search", "web", "agent", "todo"]
model: ['Claude Haiku 4.5 (copilot)']
---
# Agent: <RoleName>

**Domain**: <domain description>
**Collaboration**: <closest existing agents>

## Identity & Posture
...
## When to Involve
...
## When Not to Involve
...
## Handoff Contract
...
```

Log all created agents under `## Dynamically Created Agents` in the scratchpad.

### Transparency rule

**Never silently remap** a user-requested role to an existing agent. Always document in the scratchpad:
- Which user-requested roles were mapped to which existing agents, and why
- Which gaps triggered dynamic creation
- Which gaps were delegated to a neighboring agent with a scope note

---

## Guardrails

- **Never dispatch an agent not in the resolved roster** — governance incident (ERR-027)
- **Never invent an agent name mid-session without creating the file** — if a specialization is not covered and dynamic creation is not appropriate, escalate to the human
- **Never silently remap** a user-requested agent — always document the mapping or gap in the scratchpad (Step 4 Transparency rule)
- **Scan is read-only** — listing `.github/agents/` filenames does NOT count against the 2-read quota (no file content is read)
