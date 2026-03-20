---
name: code-review-protocol
description: "Structured code review protocol — 6-step sequential process (overview, security, correctness, maintainability, performance, tests) with 🔴 Blocking / 🟡 Important / 🟢 Suggestion severity classification. Use for any PR or code submission review."
argument-hint: "Describe the PR, module, or code submission to review"
user-invocable: false
---
# Skill: Code Review Protocol

For every PR or code submission, follow this reasoning process **in order**:

---

## Review Steps

1. **Overview** — PR size, functional scope, impacted files, business context
2. **Security** — Exposed secrets, injections, auth and authz failures, vulnerable dependencies
3. **Correctness** — Business logic, edge cases, error handling. Does the code do what it claims?
4. **Maintainability** — Naming, coupling, duplication, readability. Will it still make sense in six months?
5. **Performance** — N+1 queries, memory allocation, unnecessary re-renders, algorithmic complexity
6. **Tests** — Happy path, error path, edge cases. Missing tests is blocking except for pure documentation changes

---

## Verdict Classification

After completing all 6 steps, classify the result:

- 🔴 **Blocking**: must be fixed before merge
- 🟡 **Important**: should be fixed, merge may still be possible with justification
- 🟢 **Suggestion**: optional improvement

Every finding must include its severity category and a concrete corrective suggestion for any 🔴 Blocking issue.
