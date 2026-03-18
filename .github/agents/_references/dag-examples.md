# Typical DAG Examples — Orchestrator Reference

> These examples illustrate how to build multi-agent DAGs for different kinds of tasks.
> They serve as reusable planning models.

---

## Example 1 — Fullstack Feature (L2, 12 agents, 3 lanes)

`@orchestrator: Add a POST /api/v1/notifications endpoint with real-time WebSocket support`

```text

Wave 0 (parallel — 8 read-only agents):
 [software-architect ‖ api-designer ‖ proxy-po ‖ legal-compliance
  ‖ security-engineer ‖ ux-ui-designer ‖ performance-engineer ‖ accessibility-engineer]
           ↓
⚠️ Summary: extract P0 constraints from security-engineer + acceptance criteria from proxy-po
           ↓
Wave 1 (safe parallel — separate write zones):
 [qa-engineer(tests/ — TDD red) ‖ database-engineer(migrations/) ‖ risk-manager]
           ↓
⚠️ CHECKPOINT: mandatory TDD red commit before wave 2
           ↓
Wave 2 (sequential — depends on wave 1 tests):
 backend-dev(src/api/) ──→ frontend-dev(src/components/)
           ↓
Wave 3 (safe parallel):
 [code-reviewer ‖ tech-writer ‖ observability-engineer ‖ devops-engineer ‖ accessibility-engineer(re-check)]

```text

**Agents involved**: 12 agents across 3 lanes (Tech, Product, Governance)
**Excluded agents with rationale**: mobile-dev (no mobile), ml-engineer (no AI), finops-engineer (no cloud impact), GameAssetGenerator (out of scope)

---

## Example 2 — Authentication System Refactor (L3, 15 agents, 4 lanes)

`@orchestrator: Migrate from NextAuth v5 CredentialsProvider to multi-provider OAuth2/OIDC`

```text

Wave 0 (parallel — 10 read-only agents, cross-lane):
 [software-architect ‖ security-engineer ‖ legal-compliance ‖ risk-manager
  ‖ api-designer ‖ proxy-po ‖ ux-ui-designer ‖ accessibility-engineer
  ‖ performance-engineer ‖ architecture-reviewer]
           ↓
⚠️ Cross-lane summary: target architecture + GDPR constraints + UX journey
           ↓
Wave 1 (safe parallel — separate zones):
 [qa-engineer(tests/ — TDD red) ‖ database-engineer(migrations/) ‖ ux-writer(microcopy)]
           ↓
Wave 2 (sequential):
 backend-dev(src/auth/) ──→ frontend-dev(src/components/login/)
           ↓
Wave 3 (parallel — review + documentation):
 [code-reviewer ‖ security-engineer(re-audit) ‖ tech-writer ‖ devops-engineer ‖ change-management]

```

**Agents involved**: 15 agents across 4 lanes (Tech, Product, Governance, Data)

---

## Example 3 — Production ML Pipeline (L3, 11 agents, 3 lanes)

`@orchestrator: Put a product recommendation pipeline with embeddings into production`

```

Wave 0 (parallel — 8 read-only agents):
 [ai-research-scientist ‖ software-architect ‖ security-engineer ‖ legal-compliance
  ‖ ai-ethics-governance ‖ ai-product-manager ‖ performance-engineer ‖ risk-manager]
           ↓
Wave 1 (safe parallel — separate zones):
 [data-scientist(features/) ‖ database-engineer(migrations/ — pgvector) ‖ ml-engineer(models/)]
           ↓
Wave 2 (sequential):
 mlops-engineer(infra ML) ──→ devops-engineer(CI/CD pipeline) ──→ observability-engineer(monitoring)
           ↓
Wave 3 (parallel — review):
 [code-reviewer ‖ ai-ethics-governance(model card) ‖ tech-writer]

```

**Agents involved**: 11 agents across 3 lanes (Tech, Data/AI, Governance)

---

## Common Pattern

All DAGs follow this pattern:

| Wave | Role | Typical agents |
| --- | --- | --- |
| **Wave 0** | Framing, constraints, architecture | software-architect, security-engineer, api-designer, proxy-po, legal-compliance, ux-ui-designer |
| **Wave 1** | Tests (TDD red), migrations, complementary specifications | qa-engineer, database-engineer, risk-manager, ux-writer |
| **Wave 2** | Implementation | backend-dev, frontend-dev, ml-engineer, data-scientist |
| **Wave 3** | Review, documentation, observability | code-reviewer, tech-writer, devops-engineer, observability-engineer |

**Checkpoints**:

- P0 summary between wave 0 and wave 1, including injected security constraints (ERR-008)
- TDD red commit between wave 1 and wave 2 (ERR-015)
- Review-to-fix loop in wave 3 until Approve (ERR-019)
