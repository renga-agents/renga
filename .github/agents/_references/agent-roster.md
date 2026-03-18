# Agent Roster Resolution

> Referenced by: `seiji.agent.md §INITIALIZATION`

Seiji must resolve the active agent list at the start of every session before building the DAG. This file defines how to do it.

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
exclude files whose name starts with _ (profiles, references, plugins metadata)
```

Expected result: a flat list of agent names (e.g. `seiji`, `backend-dev`, `qa-engineer`, …).

### Case C — `.renga.yml` absent

No config file means the project was not bootstrapped with `renga install`. Treat as `mode: "all"` and scan `.github/agents/` as above. Log a warning in the scratchpad.

---

## Step 2 — Apply plugin agents

If `plugins:` is non-empty in `.renga.yml`, agents installed by those plugins are already present in `.github/agents/` and are included automatically by the scan (Case B) or must be added to the whitelist explicitly (Case A).

---

## Step 3 — Write the roster to the scratchpad

After resolution, log the active roster at the top of `scratchpad-<slug>.md`:

```
## Active roster (resolved YYYY-MM-DDTHH:MM)
mode: whitelist | all
agents: [seiji, backend-dev, qa-engineer, ...]
source: .renga.yml | scan
```

This makes the roster auditable and prevents Seiji from inventing agent names mid-session.

---

## Guardrails

- **Never dispatch an agent not in the resolved roster** — governance incident (ERR-027).
- **Never invent an agent name** — if a needed specialization is not covered, escalate to the human.
- **Scan is read-only** — listing `.github/agents/` filenames does NOT count against the 2-read quota (no file content is read).
