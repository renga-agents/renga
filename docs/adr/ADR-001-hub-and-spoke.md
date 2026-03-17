# ADR-001: Hub-and-Spoke Architecture with a Central Orchestrator

**Date**: 2026-03-16
**Status**: Accepted
**Decision makers**: Founding team

## Context

The renga framework coordinates 60+ specialized agents inside a VS Code workspace.

> *Note: the number of agents has evolved since this ADR was written. See the [agent catalog](../../.github/agents/README.md) for the current count.* A single user task may involve 1 to 10 agents running at the same time. The framework needs a coordination model that guarantees delivery consistency, decision traceability, and quality control, while staying within GitHub Copilot platform constraints, especially the one-level subagent invocation limit.

## Decision

Adopt a **hub-and-spoke** architecture: a single orchestrator is the entry point for every complex task. It classifies the task, plans the work, dispatches to specialized agents via `runSubagent`, and validates the resulting deliverables. Specialized agents do not invoke one another directly; depth stays limited to 1 and there is no sub-orchestration.

The orchestrator does not code, design, or audit. It reasons, plans, challenges, and arbitrates.

## Consequences

### Positive

- **Centralized coordination**: one decision point for planning and arbitration
- **Traceability**: every dispatch is logged and every deliverable is reviewed
- **Platform compatibility**: complies with the GitHub Copilot Agent mode depth=1 constraint
- **Mental simplicity**: easy for users to understand

### Negative

- **Single point of failure**: if the orchestrator reasons poorly, the entire chain is affected
- **Bottleneck risk**: everything flows through the orchestrator, including tasks that could otherwise be parallelized
- **Context budget cost**: orchestration consumes tokens that are not spent on domain work

### Risks

- **High cognitive load on the orchestrator** for L3/L4 tasks, mitigated by lane orchestrators that pre-filter dispatch
- **Users bypassing orchestration** by invoking agents directly, mitigated by the `user-invocable` flag and the documentation

## Alternatives Considered

### Peer-to-peer (agents invoke each other)

Each agent decides which collaborators to call. Rejected: without central governance, this creates a risk of invocation loops, decision conflicts, and poor traceability. It is also incompatible with the depth=1 platform constraint.

### Multi-level hierarchy (cascading orchestrators)

Orchestrator -> sub-orchestrator -> agents. Rejected: the Copilot platform does not support depth > 1, and the added coordination complexity is not justified.

### Sequential pipeline

A fixed chain of agents (analysis -> design -> code -> test -> review). Rejected: it does not fit non-linear tasks such as debugging, refactoring, or exploration, which represent most real-world use cases.
