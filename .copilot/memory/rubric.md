# Scoring Rubric — Agent Performance

This file defines the scoring method used in `agent-performance.md`.

## Complexity Coefficients

Each raw score (0-5) is multiplied by the task coefficient:

| Level | Description | Coefficient |
| --- | --- | --- |
| L0 | Trivial single-file task (< 15 min) | x 0.5 |
| L1 | Simple multi-file task (< 1h) | x 1.0 |
| L2 | Coordinated complex task (< 4h) | x 1.5 |
| L3 | Multi-wave project (< 1 day) | x 2.0 |
| L4 | Extended multi-session project | x 3.0 |

**Weighted score** = Raw score x Complexity coefficient

Example: an agent scores 4/5 on an L3 task -> weighted score = 4 x 2.0 = 8.0

## Evaluation Scale (raw score 0-5)

| Score | Criterion |
| --- | --- |
| 5 | Output matches acceptance criteria on the first try, complete handoff |
| 4 | Output is compliant, with 1 minor retry or an incomplete but fixed handoff |
| 3 | Output is partially compliant, 1 substantial retry required |
| 2 | Output is non-compliant, 2 retries or partial escalation |
| 1 | Output failed, HITL escalation required |
| 0 | Circuit breaker triggered (>= 2 consecutive failures) |

## Evaluation Dimensions

For each agent, score these 3 dimensions and average them:

1. **Compliance**: Does the output meet the acceptance criteria?
2. **Completeness**: Is the handoff complete, with all required artifacts delivered?
3. **Autonomy**: Did the agent handle ambiguity without unnecessary escalation?

## Usage

The orchestrator populates `agent-performance-<slug>.md` with:

```markdown

| Agent | Task | Level | Raw Score | Weighted Score | Notes |
| --- | --- | --- | --- | --- | --- |
| backend-dev | Auth API implementation | L2 | 4/5 | 6.0 | 1 retry on tests |

```

After the session, `scripts/consolidate_memory.py` merges the results into `agent-performance.md`.
