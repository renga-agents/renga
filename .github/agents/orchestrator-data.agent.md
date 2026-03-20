---
name: orchestrator-data
user-invocable: false
description: "Data/AI lane reference — non-invocable internal profile read by the orchestrator to route data science, ML, MLOps, and data engineering specialists"
tools: ["read"]
model: "Claude Haiku 4.5 (copilot)"
---
# Lane Profile: Data/AI

**Available agents**: data-scientist, ml-engineer, mlops-engineer, data-engineer, ai-research-scientist, ai-product-manager, database-engineer, prompt-engineer

> **Usage**: This profile is **read by seiji** during planning to select agents and define dispatch order. It is not invocable itself. Seiji dispatches the specialists directly at depth 1. It also carries the project-level Data/AI conventions.

## Escalation Criteria Detected by Seiji

| Situation | Seiji action |
| --- | --- |
| Personal-data violation detected | Immediate stop, involve legal-compliance + risk-manager |
| Model bias detected | Involve ai-ethics-governance first |
| Production data infrastructure failure | Involve mlops-engineer + devops-engineer |
| Feature engineering blocked by missing data | Direct seiji arbitration on prioritization |

---

## Data/AI Dispatch Matrix

| Task | Sequential agents | Parallel agents | Recommended cross-lane agents |
| --- | --- | --- | --- |
| ETL pipeline | data-engineer | database-engineer (schema) | security-engineer (sensitive data), legal-compliance (GDPR) |
| Data exploration | data-scientist | data-engineer (data quality) | legal-compliance (personal data), risk-manager |
| Model training | ml-engineer | data-scientist (features) | ai-ethics-governance (bias), performance-engineer (latency) |
| ML production rollout | mlops-engineer | ml-engineer (packaging), observability-engineer (monitoring) | devops-engineer (CI/CD), ai-ethics-governance (model card), security-engineer |
| AI architecture research | ai-research-scientist | ml-engineer (feasibility) | software-architect, performance-engineer |
| AI product strategy | ai-product-manager | data-scientist (metrics) | product-strategist (roadmap), proxy-po (stories) |
| Adoption analysis for a data/AI feature | data-scientist | product-analytics (product reading) | product-manager, data-engineer (tracking) |
| Vector database optimization | database-engineer | data-engineer | performance-engineer (benchmarks), software-architect |
| System or agent prompt design/optimization | prompt-engineer | ml-engineer (model context) | qa-engineer (test suites), security-engineer (injection) |
| Prompt quality evaluation with PromptFoo or RAGAS | prompt-engineer | qa-engineer (test suites) | ai-ethics-governance (bias), tech-writer (documentation) |
| LLM red teaming and robustness audit | prompt-engineer | security-engineer (injection), ml-engineer | ai-ethics-governance, risk-manager |

---

## Cross-Lane Signals

When a Data/AI task should trigger agents from other lanes:

| Signal detected in the task | Lane | Agents to include |
| --- | --- | --- |
| Model deployed to production | Governance | ai-ethics-governance (model card) + risk-manager |
| Personal data in the pipeline | Governance | legal-compliance + security-engineer |
| API or endpoint needed to serve the model | Tech | api-designer + backend-dev + devops-engineer |
| ML monitoring dashboard | Tech | frontend-dev + observability-engineer |
| User-visible scoring or recommendation | Product | ux-ui-designer + proxy-po |
| Feature requires adoption KPIs or funnel analysis | Product | product-analytics + product-manager |
| Expensive data pipeline using GPU or storage | Governance | finops-engineer |
| System prompt exposed to end users | Governance | security-engineer (injection) |

---

## Project Data/AI Conventions

- Every ML experiment is tracked in MLflow or an equivalent tool
- Every deployed model has a **model card** managed with ai-ethics-governance
- Sensitive data never travels in plaintext inside prompts
- Embeddings are stored in `agent_memory.observations` through pgvector according to the project's relevant internal ADR

---

## Consolidation Format Produced by Seiji After Data/AI Dispatch

> When seiji has dispatched multiple agents from the Data/AI lane, it consolidates the outputs in this format before journaling.

```markdown

## Data/AI Summary — [task name]

### Agents involved
- [agent]: [mission] -> [status]

### Key metrics
- [metric]: [value] vs [baseline]

### Produced artifacts
- [model / pipeline / dataset / report]

### Ethics and compliance alerts
- [list or "None"]

```
