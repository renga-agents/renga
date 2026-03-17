# Agent Output Scoring Rubric

## Evaluation Dimensions

Each subagent output is evaluated on 5 dimensions, scored from 1 to 5.

### 1. Completeness (weight: 25%)

Does the output cover all acceptance criteria defined in the prompt?

- 5: All criteria met, plus useful bonus insights
- 4: All criteria met
- 3: Most criteria met (>= 75%)
- 2: Criteria partially met (50-74%)
- 1: Most criteria missed (< 50%)

### 2. Technical Relevance (weight: 25%)

Is the output technically correct and well adapted to the context?

- 5: Correct, well adapted, and includes actionable recommendations
- 4: Correct and well adapted
- 3: Correct but partially out of context
- 2: Minor technical errors
- 1: Major technical errors

### 3. Actionability (weight: 20%)

Are the recommendations or outputs directly usable?

- 5: Immediately implementable without clarification
- 4: Implementable with minor clarifications
- 3: Requires translation or adaptation work
- 2: Too vague to act on
- 1: Not actionable

### 4. Concision (weight: 15%)

Is the output proportional to the task, without unnecessary verbosity?

- 5: Compact and information-dense
- 4: Well proportioned
- 3: Some unnecessary length
- 2: Verbose, with significant padding
- 1: Massively verbose and buried in noise

### 5. Handoff Compliance (weight: 15%)

Is the handoff block structured and usable?

- 5: Complete block with all sections and clear transitions
- 4: Present and usable
- 3: Partial but sufficient
- 2: Missing or unusable
- 1: No handoff

## Final Score Calculation

Score = (Completeness x 0.25) + (Relevance x 0.25) + (Actionability x 0.20) + (Concision x 0.15) + (Handoff x 0.15)

## Action Thresholds

| Score | Action |
| --- | --- |
| >= 4.0 | None - high-performing agent |
| 3.0 - 3.9 | Monitor - review whether the prompt can be improved |
| 2.0 - 2.9 | Alert - retry or use an alternative agent, update `error-patterns.md` |
| < 2.0 | Ban - exclude the agent from that task type, update `project-context.md` |
