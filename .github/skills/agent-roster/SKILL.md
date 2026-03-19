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

For each deliverable in the task, apply this test:

> **"If I dispatch an existing agent on this deliverable, can it produce output that meets the domain-specific standards, certifications, or regulatory frameworks named — without needing to learn that domain from scratch?"**

If the answer is **no** for any deliverable → domain gap.

#### Hard test: certification / standard coverage

Scan the task description for any domain-specific standard, certification, or regulatory body (e.g. IEC 60880, DO-178C, IAEA NSS-17, FDA 21 CFR Part 11, ISO 26262, ASME, IMO, AS9100). For each one: verify that at least one existing agent has that standard listed as a core competency. If none does → **domain gap, regardless of how close a generic agent looks**.

#### False mapping anti-patterns — never make these mappings

These are the most common incorrect remappings. Each one produces an agent that can name the standard but cannot actually apply it:

| Requested specialization | Wrong mapping | Why it is wrong |
|---|---|---|
| Nuclear safety engineer (IEC 60880, SIL4, PSA) | `security-engineer` | security-engineer is cybersecurity; it cannot perform probabilistic safety assessment or reactor protection certification |
| Nuclear / ICS cybersecurity (IAEA NSS-17, IEC 62443 nuclear) | `security-engineer` | security-engineer covers IT/web security; nuclear ICS security requires reactor domain knowledge on top |
| Software qualification (IEC 60880, DO-178C, IEC 62138) | `qa-engineer` | qa-engineer performs software testing; qualification to safety standards requires independent V&V and specific certification methodology |
| Probabilistic safety assessment / HAZOP | `risk-manager` | risk-manager handles project and business risk; PSA and HAZOP require nuclear/chemical process engineering |
| Medical device regulatory (FDA 21 CFR, MDR, ISO 13485) | `legal-compliance` | legal-compliance covers GDPR/HIPAA/contracts; medical device regulation requires clinical and engineering domain knowledge |
| Avionics / DO-178C | `devops-engineer` | devops-engineer handles CI/CD; avionics certification requires dedicated safety lifecycle (PSAC, SDP, SVP) |
| Marine classification (IMO, DNV-GL) | `infra-architect` | infra-architect handles cloud/network topology; maritime classification requires hull, propulsion, and stability engineering |

#### Domain examples (non-exhaustive)

- Nuclear I&C / reactor protection → no `nuclear-safety-engineer`, no `isc-qualification-specialist`
- Safety-critical software (IEC 61508 / DO-178C / ISO 26262) → no `functional-safety-engineer`
- Medical devices (FDA, MDR, ISO 13485) → no `medical-device-engineer`, no `regulatory-affairs-specialist`
- Pharmaceutical manufacturing (GMP, FDA process validation) → no `process-validation-engineer`
- Avionics / aerospace (DO-178C, ARP4754A) → no `avionics-engineer`
- Maritime / naval (IMO, DNV-GL, SOLAS) → no `naval-architect`
- Smart Grid / electrical systems → no `electrical-engineer`, no `scada-specialist`
- IoT firmware / embedded → no `embedded-engineer`
- Energy markets / carbon economics → no `energy-economist`

If yes to any gap above, treat the missing specialization as a domain gap and apply the policy below.

### Domain gap policy

| Condition | Action |
|---|---|
| Adequate coverage by an existing agent | Log the mapping in the scratchpad under `## Roster Mapping`; never silently remap without documentation |
| Genuine gap + specialization **central to the task** (blocks wave design or acceptance criteria) | In **plan-only mode**: write a stub to the scratchpad and add a **Wave Init** to the DAG. In **dispatch mode**: create the file at the start of Wave Init, before any other wave is dispatched. |
| Genuine gap + specialization **peripheral** (marginal scope, handled at the edges by a neighbor) | Log as gap in scratchpad; delegate to the closest agent with an explicit scope note |

### Wave Init — agent bootstrapping

When one or more central domain gaps are detected, **prepend a Wave Init to the DAG** before Wave 0:

```
Wave Init (Agent bootstrapping — N files to create): seiji
Wave 0    (Architecture & Governance): electrical-engineer ‖ software-architect ‖ …
```

Wave Init is a **seiji-only wave** that runs at the very start of dispatch:
1. Seiji creates each missing `.agent.md` file using the template below
2. The new agents are added to the active roster
3. Wave 0 is then dispatched with the full roster available

> **Why not plan-only?** Generating complete agent files during plan-only wastes tokens on agents whose plan may never be approved and whose scope may shift when open questions are resolved. The stub in the scratchpad is sufficient to build the DAG and evaluate the plan. File creation is deferred to Wave Init, which runs only when the user confirms dispatch.

### Dynamic agent creation

When creating a new agent file, use the standard format and naming convention (`electrical-engineer`, `iot-specialist`, `energy-economist`).

> ❌ **Placeholder text (`...`) is never acceptable.** Every section must be filled with domain-specific content at the same level of detail as existing agents in `.github/agents/`. Use your knowledge of the domain to write substantive content.

**Required sections and minimum content per section:**

```markdown
---
name: <role-name>
filiere: <tech|data|product|governance>
user-invocable: false
description: "<one-line description — domain + scope>"
tools: ["read", "edit", "search", "web", "agent", "todo"]
model: ['Claude Haiku 4.5 (copilot)']
---
# Agent: <RoleName>

**Domain**: <domain — 1 sentence>
**Collaboration**: <list closest existing agents with their interaction point>

---

## Identity & Posture

<!-- 2-3 sentences: who this agent is, what optimization lens they use, what they will never compromise on.
     Example: "The electrical-engineer is a senior power systems engineer with 15+ years in grid operations.
     They reason in terms of protection, stability, and fault isolation. They never accept an architecture
     proposal without a load flow analysis to back it." -->

## Core Competencies

<!-- 6-10 bullet points — specific skills, standards, tools, methodologies relevant to the domain.
     Example for electrical-engineer:
     - **Power systems**: load flow, fault analysis, short-circuit calculations, protection coordination
     - **SCADA/ICS**: IEC 61850, DNP3, Modbus, OPC-UA, real-time control latency constraints
     - **Grid standards**: IEC 62443 (cybersecurity), IEC 61968/61970 (CIM data model), ENTSO-E grid codes
     - **Renewables integration**: intermittency, ramp rates, inertia, synthetic frequency response -->

## Reference Stack

<!-- Table: 5-8 rows. Domain tools, standards, or frameworks this agent relies on.
| Domain | Standard / Tool | Rationale |
| --- | --- | --- |
| Grid communication | IEC 61850 | … |
-->

## Workflow

<!-- 5-6 numbered steps — the reasoning process this agent follows for any task in its domain.
     Example: 1. Assess requirements … 2. Model the system … 3. Validate constraints … -->

## When to Involve

<!-- 3-5 specific, concrete conditions. Not vague ("when needed") but actionable ("when a new
     substation must be integrated into the dispatch model and protection relay coordination is required").
     -->

## When Not to Involve

<!-- 3-5 exclusions with explicit redirections.
     Example: "For software API design without electrical constraints → api-designer" -->

---

## Behavioral Rules

<!-- 5-8 Always/Never rules grounded in domain risk.
     - **Always** verify protection coordination before any topology change
     - **Never** approve a control scheme without a failure mode analysis -->

## Delivery Checklist

<!-- 4-6 checkboxes — verifiable outputs the agent must produce before handoff.
     - ☐ Load flow analysis completed and validated
     - ☐ Protection relay settings reviewed -->

---

## Handoff Contract

### Primary handoff to `<agent-A>`, `<agent-B>`

- **Fixed decisions**: <what is settled and must not be reopened>
- **Open questions**: <what downstream agents still need to resolve>
- **Artifacts to pick up**: <specific files, diagrams, specs produced>
- **Expected next action**: <what the receiving agent does with this output>

### Expected return handoff

- <what this agent expects back from downstream agents>
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
