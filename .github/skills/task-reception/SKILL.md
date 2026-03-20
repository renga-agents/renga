---
name: task-reception
description: "Pre-execution coherence gate: verifies task framing before any execution. Returns a TASK CHALLENGE to seiji if the task is incoherent, out of scope, or has unachievable criteria."
argument-hint: "Not invocable standalone — loaded by agents at the start of each dispatched task."
user-invocable: false
---

# Skill: Task Reception

This skill defines the pre-execution gate that every declaring agent runs **after reading its configuration file (ERR-026) and before any file reads, tool calls, or task execution**. Its purpose: surface incoherence early rather than propagate it silently through execution.

An agent that executes a structurally broken task is not a compliant agent — it is a silent failure amplifier. The gate is not an obstacle; it is the agent asserting its domain expertise.

---

## When to run the gate

**Run when**: the task arrived via seiji dispatch (prompt begins with `"Start by reading your configuration file at .github/agents/..."`).

**Skip when**: direct user invocation (`@agent-name` in chat), L0 fast-track, or re-dispatch after a previously returned TASK CHALLENGE — on re-dispatch, proceed directly.

---

## The 3-point coherence check

Evaluate each point from the task prompt and your domain expertise alone — no file reads required for this check.

| # | Check | Hard failure condition |
|---|-------|-----------------------|
| SCOPE | Is this task within my declared domain? | A significant portion of the required work falls outside my expertise, and no other agent is named to cover it. |
| CRITERIA | Are the acceptance criteria achievable and verifiable? | Criteria are contradictory, require decisions that seiji should have resolved before dispatching, or describe outputs that cannot be verified with the available inputs. |
| CONTEXT | Does the transmitted context make sense? | A factual contradiction exists, a prerequisite that seiji explicitly owns is missing, or a stated constraint makes success structurally impossible. |

---

## Decision logic

**All 3 pass** → proceed silently. No output about the gate. Begin the task.

**Minor issue** (ambiguity resolvable by a reasonable assumption, incomplete information that can be inferred from context) → proceed, state the assumption explicitly in your output at the start of the response, then continue.

**Hard failure in any check** → return a `TASK CHALLENGE` block before any execution. Stop after returning it — do not execute.

---

## TASK CHALLENGE format

```
=== TASK CHALLENGE ===
Agent: <agent-name>
Check: [SCOPE | CRITERIA | CONTEXT]
Observation: <one sentence — the specific incoherence detected>
Impact: <one sentence — why this would cause execution to fail or produce unreliable output>
Proposal: <one sentence — what adjustment or clarification is needed to proceed>
```

After returning the block: stop. Do not attempt execution. Seiji receives the challenge, arbitrates, and re-dispatches with a corrected brief or escalates to the user.

---

## Anti-patterns (do not do these)

- ❌ Challenge a task because you would have framed it differently — if the task is structurally valid, execute it as specified
- ❌ Issue a TASK CHALLENGE for ambiguity that a reasonable domain assumption resolves — state the assumption and proceed
- ❌ Issue a TASK CHALLENGE because the task is large, difficult, or requires extensive work
- ❌ List multiple challenges in one block — identify the single most blocking issue and return one block
- ❌ Re-challenge after seiji has re-dispatched a corrected brief — on re-dispatch, proceed unconditionally
- ❌ Use the gate to negotiate task scope in your favor — it exists to catch structural incoherence, not to optimize your workload
