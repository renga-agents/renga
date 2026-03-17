# ERR Rules Catalog — Orchestrator

> This file is the exhaustive reference for all ERR-xxx rules used by the orchestrator.
> Each rule is identified, described, and accompanied by examples or safeguards.

---

## ERR-001 — Commit reference verification

**Rule**: Before each commit, reread the message body and ensure the DEC/ERR references point to the **current** decision set, not a previous session.

**Why**: Copy-pasting commit messages across sessions introduces dead references that pollute the decision log and make Git history inconsistent.

**Safeguard**: Manually verify that each `DEC-xxx` and `ERR-xxx` in the message matches an entry in the active session's `decisions-<slug>.md` file, identified by the slug.

---

## ERR-004 — File plan before parallel dispatch

**Rule**: If several agents will operate on the same tree, publish the list of canonical files in the scratchpad, with path + owning agent, **before** dispatch. Each agent creates only the files assigned to them.

**Why**: Without a file plan, two agents can create the same file in parallel, causing write conflicts and data loss.

**Example**:

```markdown

## File plan — wave 2
| File | Owning agent |
|---|---|
| src/api/notifications.controller.ts | BackendDev |
| src/api/notifications.service.ts | BackendDev |
| migrations/20260307_add_notifications.sql | DatabaseEngineer |
| tests/notifications.spec.ts | QAEngineer (wave 1) |

```

---

## ERR-005 — Multiline commit message convention

**Rule**: Any commit whose message exceeds 1 line must use `git commit -F /tmp/commit_msg.txt` by writing the message with `create_file` first, then committing by reference. **Never** use `git commit -m "..."` with multiline content.

**Why**: The VS Code Copilot terminal enters `dquote>` mode for multiline messages passed through `-m`, and the command is lost.

**Best practice**:

```bash

# 1. Write the message into a temporary file
create_file /tmp/commit_msg.txt "feat(notifications): add WebSocket support

- Add notification controller and service
- Wire up WebSocket gateway
- Refs: DEC-042, ERR-008"

# 2. Commit by reference
git commit -F /tmp/commit_msg.txt

```

---

## ERR-007 — Validate QAEngineer scope before wave 2

**Rule**: Before moving to wave 2, verify the files created by QAEngineer. Only `*.spec.ts`, test infrastructure files such as `package.json`, `vitest.config.ts`, `tsconfig.json`, and pure interfaces are allowed.

**Forbidden files in wave 1 (TDD red)**: services, controllers, repositories, DTOs, modules, guards, decorators, entities, filters.

**Action on violation**: Remove those files from the commit and annotate the scratchpad before starting wave 2. QAEngineer must create only **tests** and **interfaces/contracts**, never the implementation.

**Why**: If QAEngineer writes the implementation, BackendDev in wave 2 will either face a conflict or overwrite it, and TDD loses its meaning because the tests are no longer red once the implementation already exists.

---

## ERR-008 — SecurityEngineer → QAEngineer brief

**Rule**: If SecurityEngineer is in wave 0 and QAEngineer is in wave 1, include the following text in the QAEngineer prompt, word for word, before the source material:

> `P0 security constraints extracted from the SecurityEngineer report (wave 0) that your tests must honor: [summary of P0 points: expected sourcing of sensitive data (e.g. userId from JWT sub, not from request body), required auth, scopes]. These constraints are part of the endpoint contract — your tests must validate them and guide the implementation design. If you do not test them, BackendDev will not implement them.`

**Why**: Without this brief, QAEngineer writes purely functional tests and ignores security constraints. BackendDev therefore does not implement them because in TDD, no test means no implementation. The result is a functional but vulnerable endpoint.

**Mandatory sequencing**: SecurityEngineer must be in **wave 0** if QAEngineer is scheduled. Running both in parallel is forbidden because the security brief must exist before the tests are written.

---

## ERR-013 — Wave 0 agents: read-only, no file creation

**Rule**: Read-only agents in wave 0 such as SecurityEngineer, CodeReviewer, SoftwareArchitect, APIDesigner, ProxyPO, LegalCompliance, and others **must not create files**. Their artifacts such as `openapi.yaml`, ADR drafts, schemas, and so on must be included directly in the text returned by `runSubagent`.

**Materialization**: The orchestrator decides whether those artifacts should become actual files and, if so, assigns that work to an implementation agent in wave 2.

**Why**: Wave 0 agents do not have the worktree path and read from the main workspace. If they create files, those files land in the root workspace instead of the worktree and pollute the main branch.

---

## ERR-014 — Mandatory multi-agent coverage

**Rule**: For any `L2+` task, the orchestrator must identify **all** agent profiles affected by the request, not only the main implementation agent.

**Anti-pattern**: The reflex of having one agent do everything degrades quality, neutralizes cross-review, and contradicts the purpose of an agent team.

**Method**:

1. List the facets of the task: architecture, implementation, rendering/animations, UX, tests, review, documentation, security, and so on.
2. Assign at least one specialist agent to each non-trivial facet.
3. Include complementary profiles that challenge or enrich the main work.

**Coverage floors**:

| Level | Minimum agents | Minimum tracks |
| --- | --- | --- |
| `L1` | 1-2 | No formal minimum |
| `L2` | **4-6** | **2 tracks** |
| `L3` | **6-10** | **3 tracks** |
| `L4` | **8-15** | **4 tracks** + consensus or escalation |

These minimums are **floors**, not ceilings. A well-structured 15-agent DAG is better than an overloaded 4-agent DAG.

**Systematic quality agents**: CodeReviewer and/or TechWriter in the final wave for any task that produces code or documentation.

**Warning signs**:

- “This agent can do everything alone” → the DAG is undersized
- “Too many subagents, too expensive in tokens” → the problem is the prompt or the structure, not the number of experts
- The same 5-6 agents on 3 consecutive tasks → rescan the full catalog

---

## ERR-015 — Commit checkpoint between every wave

**Rule**: Every wave that produces artifacts such as created, modified, or deleted files **must** be followed by a commit before moving to the next wave.

**Format**: `<type>(<scope>): wave N — <description>`

**Exception**: Read-only waves, typically wave 0, do not generate their own commit.

**Safeguard**: If wave N is not committed, wave N+1 cannot start. This rule complements the TDD red checkpoint. In a TDD DAG, the red commit **is** the wave 1 commit.

**Why**: A single catch-all commit that groups multiple waves prevents granular rollback by wave and makes the diff unreadable. This is a **governance incident**.

---

## ERR-016 — HITL escalation for framework/engine selection

**Rule**: When several frameworks, engines, paradigms, or stacks are viable and involve significant trade-offs in performance, extensibility, learning curve, or ecosystem, the orchestrator escalates to a human **before** wave 0.

**Process**:

1. SoftwareArchitect produces a comparison matrix
2. The human decides. SoftwareArchitect **does not decide**
3. Any task where the technology choice defines the nature of the deliverable is automatically classified at least `L3`

**Escalation criterion**: The migration cost exceeds one person-week if the wrong choice is made.

**Why**: A framework choice is an irreversible architecture decision. Business context, team preferences, and budget constraints go beyond what agents can infer.

---

## ERR-017 — Silent workaround forbidden

**Rule**: If an MCP tool planned in the validation DAG such as Playwright, Chrome DevTools, PostgreSQL, a linter, or a build tool is unavailable, the orchestrator must:

1. Notify the user
2. Propose either waiting for resolution or explicitly accepting the risk
3. **Never** work around it silently

**What is forbidden**: Silently replacing a browser test with a static import check, or an E2E test with a code review.

**Why**: A silent workaround of a validation tool for an interactive deliverable such as a game, UI, form, or API is a **governance incident**. The deliverable is declared validated when it is not.

---

## ERR-018 — Separate binary assets and source files

**Rule**: Always separate **binary assets** such as images, audio, sprites, and fonts from **source files** such as code, tests, and configuration into distinct commits.

**Why**: Assets have a heavy Git footprint and low reversibility. Mixing them with logic changes prevents targeted rollback and disproportionately bloats diffs.

**Example**:

```bash

# ✅ Correct: 2 separate commits
git commit -m "feat(game): add player sprite sheet"  # assets only
git commit -m "feat(game): add player animation logic"  # code only

# ❌ Incorrect: 1 mixed commit
git commit -m "feat(game): add player with sprites and animation"

```

---

## ERR-019 — Cyclical review→fix loop

**Rule**: The review wave does not end after a single pass. The `CodeReviewer → DevAgent fix → CodeReviewer re-review` cycle repeats until CodeReviewer issues an **Approve** verdict with zero P0/blocking issues.

**Limits**:

- Maximum **3 iterations** of the cycle
- If the cycle has not converged after 3 iterations, escalate to a human
- **Never** declare a task complete while P0 issues remain open

---

## ERR-020 — Mandatory agents for visual/interactive deliverables

**Rule**: For any deliverable such as a video game, interactive animation, complex dashboard, or highly visual UI classified as L3+:

**Mandatory agents**:

- CreativeDirector for art direction
- UXUIDesigner for UI consistency
- PerformanceEngineer for frame rate and memory

**Recommended agents**:

- AccessibilityEngineer if the audience is broad
- FrontendDev for cross-browser compatibility

**Additional requirement**: The DAG must include at least one wave dedicated to **visual review** using annotated screenshots, graphic consistency checks, and polish.

---

## ERR-021 — Mandatory browser validation

**Rule**: Any interactive deliverable such as a game, UI, form, or web application must be validated with Playwright or an equivalent tool before being declared complete.

**Validation checklist**:

1. Start the application and verify it boots with no console errors
2. Reproduce the main user scenarios such as navigation, interactions, and inputs
3. Capture screenshots at key steps as visual proof
4. Verify there are no JavaScript errors in the console

**Without this validation, the task cannot be closed.** A deliverable declared “done” without browser testing is a governance incident.

---

## ERR-022 — Mandatory user validation before merge

**Rule**: **Never** merge into the main branch without the user's **explicit** approval.

**Process**:

1. The orchestrator presents a structured summary of fixed bugs, passed tests, screenshots, and commits
2. The orchestrator waits for the user's written confirmation
3. Only after confirmation is the merge allowed

### An unauthorized merge is a non-negotiable governance incident

---

## ERR-023 — Squash merge forbidden by default

**Rule**: Never use `git merge --squash` unless the user explicitly asks for it.

**Why**: Squash merge destroys the granular per-wave commit history and prevents partial rollback. Use `git merge --no-ff feat/<slug>` by default.

---

## ERR-024 — Mandatory multi-track catalog scan

**Rule**: Before building the DAG, the orchestrator **must** mentally scan the 4 tracks and evaluate every agent.

**Required output**: An `included/excluded` list with a one-word justification for each exclusion. This trace goes into the scratchpad.

**Cross-track rule**: If an `L2+` task activates agents from only **1 single track**, that is an anomaly and must be explicitly justified in the scratchpad.

**Quick catalog checklist** to scan before every DAG:

```text

TECHNICAL TRACK (18 core agents):
│ BackendDev         — API, business logic, services
│ FrontendDev        — UI, components, CSS, web performance
│ FullstackDev       — end-to-end feature, integration
│ MobileDev          — React Native, Flutter, mobile apps
│ QAEngineer         — tests, TDD, coverage, test strategy
│ CodeReviewer       — code review, maintainability, patterns
│ Debugger           — bug investigation, root cause, reproduction
│ APIDesigner        — API contracts, OpenAPI, DX
│ SoftwareArchitect  — patterns, ADR, domain decomposition
│ PerformanceEngineer— profiling, SLO/SLI, load
│ DevOpsEngineer     — CI/CD, containers, pipelines
│ IncidentCommander  — incident management, crisis coordination
│ InfraArchitect     — IaC, network topology, VPS
│ CloudEngineer      — cloud, provisioning, HA/DR
│ PlatformEngineer   — internal DX, self-service, abstractions
│ ObservabilityEngineer— OTel, tracing, alerting, dashboards
│ ChaosEngineer      — resilience, failure injection
│ SecurityEngineer   — OWASP, hardening, audit (primary: GOVERNANCE)

PRODUCT TRACK (11 core agents):
│ ProxyPO            — user stories, backlog, acceptance criteria
│ ProductManager     — cross-functional steering, MVP, feature roadmap
│ ProductAnalytics   — adoption, funnel, retention, metrics
│ ProductStrategist  — vision, OKRs, roadmap, product-market fit
│ UXUIDesigner       — mockups, journeys, design system
│ UXWriter           — microcopy, onboarding, tone of voice
│ GoToMarketSpecialist— pricing, launch, segmentation
│ ScrumMaster        — facilitation, velocity, continuous improvement
│ TechWriter         — technical and user documentation
│ BusinessAnalyst    — business processes, BPMN, gap analysis
│ ChangeManagement   — change management (primary: GOVERNANCE)

DATA/AI TRACK (8 core agents):
│ DataScientist      — analysis, modeling, feature engineering
│ MLEngineer         — training, optimization, model deployment
│ MLOpsEngineer      — ML pipeline, model serving, monitoring
│ DataEngineer       — ETL/ELT, data quality, data pipelines
│ AIResearchScientist— state of the art, experimentation
│ AIProductManager   — AI product strategy, AI roadmap
│ DatabaseEngineer   — modeling, optimization, DB migrations
│ PromptEngineer     — system prompts, evaluation, red teaming

GOVERNANCE TRACK (8 core agents):
│ SecurityEngineer   — OWASP, hardening, audit (secondary: TECHNICAL)
│ LegalCompliance    — GDPR, AI Act, OSS licenses, Terms of Service
│ AIEthicsGovernance — bias, XAI, AI red teaming, model cards
│ RiskManager        — risk mapping, DPIA, contingency
│ FinOpsEngineer     — cloud costs, budgeting, rightsizing
│ ArchitectureReviewer— cross-functional review, consistency, tech debt
│ AccessibilityEngineer— WCAG, ARIA, RGAA (secondary: TECHNICAL)
│ ProjectController  — PMO, budget tracking, dependencies

OUT-OF-TRACK AGENTS (1 core agent):
│ GitExpert          — Git strategy, conflicts, workflows

PLUGIN AGENTS — game-studio (9 agents, under _plugins/game-studio/):
│ AnimationsEngineer — WebGL, Three.js, GSAP, canvas, shaders, games
│ GameAssetGenerator — visual assets for games (Replicate)
│ AudioGenerator     — audio assets for games (Replicate)
│ GameDeveloper      — game logic, game loop, physics
│ GameBalancer       — balancing, difficulty curves
│ CreativeDirector   — art direction, visual identity
│ LevelDesigner      — level design, progression, environments
│ NarrativeDesigner  — narrative, dialogue, worldbuilding
│ GameProducer       — game production, planning, milestones

DUAL AFFILIATIONS:
│ SecurityEngineer      — primary: GOVERNANCE, secondary: TECHNICAL
│ AccessibilityEngineer — primary: GOVERNANCE, secondary: TECHNICAL
│ ChangeManagement      — primary: GOVERNANCE, secondary: PRODUCT

```

For each agent **excluded** from the DAG, note a one-word justification such as `MobileDev — out of scope` or `FinOpsEngineer — no cloud`. For detailed matrices and recommended combinations, consult the track profiles: `orchestrator-tech.agent.md`, `orchestrator-product.agent.md`, `orchestrator-data.agent.md`, and `orchestrator-governance.agent.md`.

---

## ERR-025 — Mandatory file persistence for subagent reports

**Rule**: Include the following instruction in the prompt of **every sub-agent**, word for word, replacing the variables as needed:

> `Persist your report: write your full report (analysis, recommendations, artifacts, handoff block) to the file <report_path>. Use create_file to create this file. Your report must begin with this header:`
>
> ```text
>
> # Report <agent-name> — Wave <N>
> **Session** : <slug>
> **Date** : <YYYY-MM-DD>
> **Mission** : <mission_summary>
> ---
>
> ```
>
> `After the content of your report, add your usual handoff block.`
> `At the end of your mission, return ONLY:`
> `1. Verdict: [OK / RISKS / BLOCKING]`
> `2. Findings by severity: [N critical, N major, N minor]`
> `3. Top 3 P0 recommendations (3 lines max)`
> `4. Report file path: <report_path>`
> `Do NOT return the full contents of your analysis — it is in the file.`

**Path pattern**: `.copilot/reports/<slug>/wave-<N>-<agent-name>.md`

**Why**: The `runSubagent` response is injected in full into the orchestrator context window. A 200-line report consumes context budget unnecessarily. The structured summary with verdict, findings, and P0 recommendations gives the orchestrator enough information to evaluate and decide when to read the full report.

**Inter-wave referencing**: To inject a report from a previous wave into the prompt of a later-wave agent, reference the **file path**, never copy the report contents into the prompt. Example:

> `Read the full report in .copilot/reports/<slug>/wave-0-security-engineer.md for the detailed context of your security constraints.`

**Post-dispatch verification**:

1. Verify that the report file exists at the specified path
2. Update the index at `.copilot/reports/<slug>/index.md`
3. Evaluate quality based on the structured summary
4. Update the status in the index

**Fallback**: If the sub-agent did not create the file:

- Create the file from the summary received, with degraded but traceable content
- Note the incident in `.copilot/memory/error-patterns.md`

**Context gain**: On a 10-agent audit, this saves roughly 90% of the context otherwise consumed by full responses.

---
