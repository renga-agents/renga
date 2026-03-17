---
name: dag-patterns
description: "Builds a multi-agent DAG organized in waves (reading -> TDD -> implementation -> review) with a file plan and checkpoints."
argument-hint: "Describe the feature or task for which to build the DAG"
user-invocable: true

# Skill: Multi-Agent DAG Patterns

This skill guides the construction of DAGs (Directed Acyclic Graphs) to orchestrate agents in sequential and parallel waves.

---

## Common Pattern

All DAGs follow this pattern:

| Wave | Role | Typical agents |
| --- | --- | --- |
| **Wave 0** | Framing, constraints, architecture | SoftwareArchitect, SecurityEngineer, APIDesigner, ProxyPO, LegalCompliance, UXUIDesigner |
| **Wave 1** | Tests (TDD red), migrations, specifications | QAEngineer, DatabaseEngineer, RiskManager, UXWriter |
| **Wave 2** | Implementation | BackendDev, FrontendDev, MLEngineer, DataScientist |
| **Wave 3** | Review, documentation, observability | CodeReviewer, TechWriter, DevOpsEngineer, ObservabilityEngineer |

---

## Mandatory Checkpoints

- **P0 summary** between wave 0 and wave 1: extract security constraints (ERR-008) + acceptance criteria
- **TDD red commit** between wave 1 and wave 2: red tests must exist before implementation (ERR-015)
- **Review->fix loop** in wave 3 until Approve (ERR-019)

---

## File Plan (ERR-004)

If dispatch runs in parallel on the same tree, publish the list (path + owner) in the scratchpad BEFORE dispatch.

---

## Default TDD

QAEngineer (wave 1, red tests) -> BackendDev/FrontendDev (wave 2, green).

**Never parallelize** QAEngineer (TDD) and BackendDev.

---

## Parallelism Rules

- Put all independent `runSubagent` calls in the same tool-call block
- Check the filesystem matrix before parallel dispatch
- Use uncapped fan-out: launch all independent agents in parallel

---

## Example 1: Fullstack Feature (L2)

```

Wave 0 (parallel, read-only):
 [SoftwareArchitect ‖ APIDesigner ‖ ProxyPO ‖ SecurityEngineer
  ‖ UXUIDesigner ‖ PerformanceEngineer ‖ AccessibilityEngineer]
           ↓
⚠️ Summary: P0 constraints + acceptance criteria
           ↓
Wave 1 (safe parallel, separate write zones):
 [QAEngineer(tests/) ‖ DatabaseEngineer(migrations/)]
           ↓
⚠️ CHECKPOINT: TDD red commit
           ↓
Wave 2 (sequential):
 BackendDev(src/api/) ──→ FrontendDev(src/components/)
           ↓
Wave 3 (safe parallel):
 [CodeReviewer ‖ TechWriter ‖ ObservabilityEngineer ‖ DevOpsEngineer]

```

---

## Example 2: Auth Refactor (L3)

```

Wave 0 (parallel, 10 read-only agents, cross-lane):
 [SoftwareArchitect ‖ SecurityEngineer ‖ LegalCompliance ‖ RiskManager
  ‖ APIDesigner ‖ ProxyPO ‖ UXUIDesigner ‖ AccessibilityEngineer
  ‖ PerformanceEngineer ‖ ArchitectureReviewer]
           ↓
Wave 1 (safe parallel):
 [QAEngineer(tests/) ‖ DatabaseEngineer(migrations/) ‖ UXWriter(microcopy)]
           ↓
Wave 2 (sequential):
 BackendDev(src/auth/) ──→ FrontendDev(src/components/login/)
           ↓
Wave 3 (parallel):
 [CodeReviewer ‖ SecurityEngineer(re-audit) ‖ TechWriter ‖ DevOpsEngineer]

```

---

## Example 3: ML Pipeline (L3)

```

Wave 0 (parallel, read-only):
 [AIResearchScientist ‖ SoftwareArchitect ‖ SecurityEngineer
  ‖ AIEthicsGovernance ‖ AIProductManager ‖ PerformanceEngineer]
           ↓
Wave 1 (safe parallel):
 [DataScientist(features/) ‖ DatabaseEngineer(migrations/) ‖ MLEngineer(models/)]
           ↓
Wave 2 (sequential):
 MLOpsEngineer(infra ML) ──→ DevOpsEngineer(CI/CD) ──→ ObservabilityEngineer
           ↓
Wave 3 (parallel):
 [CodeReviewer ‖ AIEthicsGovernance(model card) ‖ TechWriter]

```

---

## Commit Cadence by Wave (ERR-015)

- **Format**: `<type>(<scope>): wave N - <description>`
- Read-only waves do not generate commits
- If wave N is not committed, wave N+1 cannot start
- A single catch-all commit grouping several waves is a governance incident

---

## Expected Output Format

```

=== PLANNED DAG ===
Criticality: L<N>
Wave 0: [Agent1, Agent2] - parallel (read-only)
Wave 1: [Agent3, Agent4] - safe parallel (separate zones)
Wave 2: [Agent5 -> Agent6] - sequential
Wave 3: [Agent7 ‖ Agent8] - parallel
Dependencies: Agent5 -> {Agent3, Agent4}
Impacted files: [list with owner]
Agents involved: N / Waves: M

```
