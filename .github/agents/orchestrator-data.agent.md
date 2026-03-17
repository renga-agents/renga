---
name: orchestrator-data
user-invocable: false
description: "Data/AI lane reference — non-invocable internal profile read by the orchestrator to route data science, ML, MLOps, and data engineering specialists"
tools: ["read"]
model: ['Claude Opus 4.6 (copilot)']
---
# Lane Profile: Data/AI

**Available agents**: DataScientist, MLEngineer, MLOpsEngineer, DataEngineer, AIResearchScientist, AIProductManager, DatabaseEngineer, PromptEngineer

> **Usage**: This profile is **read by the orchestrator** during planning to select agents and define dispatch order. It is not invocable itself. The orchestrator dispatches the specialists directly at depth 1. It also carries the project-level Data/AI conventions.

## Escalation Criteria Detected by the Orchestrator

| Situation | Orchestrator action |
| --- | --- |
| Personal-data violation detected | Immediate stop, involve LegalCompliance + RiskManager |
| Model bias detected | Involve AIEthicsGovernance first |
| Production data infrastructure failure | Involve MLOpsEngineer + DevOpsEngineer |
| Feature engineering blocked by missing data | Direct orchestrator arbitration on prioritization |

---

## Data/AI Dispatch Matrix

| Task | Sequential agents | Parallel agents | Recommended cross-lane agents |
| --- | --- | --- | --- |
| ETL pipeline | DataEngineer | DatabaseEngineer (schema) | SecurityEngineer (sensitive data), LegalCompliance (GDPR) |
| Data exploration | DataScientist | DataEngineer (data quality) | LegalCompliance (personal data), RiskManager |
| Model training | MLEngineer | DataScientist (features) | AIEthicsGovernance (bias), PerformanceEngineer (latency) |
| ML production rollout | MLOpsEngineer | MLEngineer (packaging), ObservabilityEngineer (monitoring) | DevOpsEngineer (CI/CD), AIEthicsGovernance (model card), SecurityEngineer |
| AI architecture research | AIResearchScientist | MLEngineer (feasibility) | SoftwareArchitect, PerformanceEngineer |
| AI product strategy | AIProductManager | DataScientist (metrics) | ProductStrategist (roadmap), ProxyPO (stories) |
| Adoption analysis for a data/AI feature | DataScientist | ProductAnalytics (product reading) | ProductManager, DataEngineer (tracking) |
| Vector database optimization | DatabaseEngineer | DataEngineer | PerformanceEngineer (benchmarks), SoftwareArchitect |
| System or agent prompt design/optimization | PromptEngineer | MLEngineer (model context) | QAEngineer (test suites), SecurityEngineer (injection) |
| Prompt quality evaluation with PromptFoo or RAGAS | PromptEngineer | QAEngineer (test suites) | AIEthicsGovernance (bias), TechWriter (documentation) |
| LLM red teaming and robustness audit | PromptEngineer | SecurityEngineer (injection), MLEngineer | AIEthicsGovernance, RiskManager |

---

## Cross-Lane Signals

When a Data/AI task should trigger agents from other lanes:

| Signal detected in the task | Lane | Agents to include |
| --- | --- | --- |
| Model deployed to production | Governance | AIEthicsGovernance (model card) + RiskManager |
| Personal data in the pipeline | Governance | LegalCompliance + SecurityEngineer |
| API or endpoint needed to serve the model | Tech | APIDesigner + BackendDev + DevOpsEngineer |
| ML monitoring dashboard | Tech | FrontendDev + ObservabilityEngineer |
| User-visible scoring or recommendation | Product | UXUIDesigner + ProxyPO |
| Feature requires adoption KPIs or funnel analysis | Product | ProductAnalytics + ProductManager |
| Expensive data pipeline using GPU or storage | Governance | FinOpsEngineer |
| System prompt exposed to end users | Governance | SecurityEngineer (injection) |

---

## Project Data/AI Conventions

- Every ML experiment is tracked in MLflow or an equivalent tool
- Every deployed model has a **model card** managed with AIEthicsGovernance
- Sensitive data never travels in plaintext inside prompts
- Embeddings are stored in `agent_memory.observations` through pgvector according to the project's relevant internal ADR

---

## Consolidation Format Produced by the Orchestrator After Data/AI Dispatch

> When the orchestrator has dispatched multiple agents from the Data/AI lane, it consolidates the outputs in this format before journaling.

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
