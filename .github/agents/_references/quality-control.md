# Quality Control — Orchestrator

> This file is the reference source for quality control, report verification, output evaluation, and the pre-synthesis checklist.
> Referenced from `orchestrator.agent.md`, section §5 Quality Control.

---

## Report Verification (ERR-025)

Each subagent creates its own report file and returns a structured summary with verdict, findings, top 3 P0 items, and path. After receipt:

1. Verify that the file exists
2. Update `.copilot/reports/<slug>/index.md`
3. Evaluate the verdict: `BLOCKING` or at least 1 critical issue means read the full report, `RISKS` means assess P0 items, `OK` means the summary is sufficient
4. Update the status: `Accepted` / `Rejected` / `Retry N`

**Fallback**: if the file is missing, recreate it from the summary and note the issue in `error-patterns.md`

---

## Output Evaluation

- **Satisfactory** -> accept and move to the next step
- **Insufficient** -> send back with precise criticism. Maximum 2 retries, then record it in `error-patterns.md` and choose an alternative approach
- **Review loop (ERR-019)**: cycle CodeReviewer -> DevAgent fix -> re-review until Approve with 0 P0 items. Maximum 3 iterations, then human escalation
- **Disagreement** -> consensus via `consensus-protocol.agent.md`
- **Blocker** -> human escalation with a structured summary
- **Browser validation (ERR-021)**: every interactive deliverable MUST be validated with Playwright before closure

---

## Retrospective — Mandatory Quality Step

> The retrospective is a quality step, not an option. An empty dashboard indicates missed retrospectives.

The orchestrator MUST run a retrospective at the end of every L2+ task. See `orchestrator.agent.md §8`. Minimum checklist:

- Each dispatched agent scored through `.copilot/memory/rubric.md`, including raw and weighted score
- `agent-performance-<slug>.md` updated before closing the session
- `python scripts/generate_dashboard.py` run after `consolidate_memory.py` to refresh the dashboard

---

## Auditable Exit Checklist

> Authoritative checklist: `orchestrator.agent.md §Auditable Exit Checklist`
> This section intentionally does not duplicate the checklist. Refer to the orchestrator for the up-to-date version.
