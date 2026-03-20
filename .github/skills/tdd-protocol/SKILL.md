---
name: tdd-protocol
description: "TDD wave protocol — wave 1 (qa-engineer writes failing tests only), wave 2 (backend/frontend-dev implements to green), wave 3 (code-reviewer reviews). Defines ERR-007 forbidden files, inline mocking rules, and mandatory red commit between waves."
argument-hint: "Describe the feature, endpoint, or module to test"
user-invocable: false
---
# Skill: TDD Protocol

TDD is the **default mode** for all new feature development. qa-engineer is dispatched **before** the implementation developer as soon as the task creates new code.

---

## Wave 1 — qa-engineer alone

- Write all tests from the DTO, Zod schema, endpoint/interface spec, and prompt instructions
- Tests **must be in a `red` state** at the end of this wave (0/N passing) — this is correct and expected

### Files allowed in wave 1

- `*.spec.ts` (tests) — **primary objective**
- Test infrastructure: `package.json`, `tsconfig.json`, `vitest.config.ts`, `vitest.setup.ts` — only if absent from the project
- **Pure** interfaces and types (without logic) if the contract has not yet been defined by software-architect/api-designer

### Files STRICTLY forbidden in wave 1 (ERR-007 — main cause of TDD failure cycles)

Production files (business logic, infrastructure, routing, persistence) — regardless of framework — are STRICTLY forbidden in wave 1. Only test files and pure interfaces/types are allowed.

_NestJS example_: DTOs, services, controllers, repositories, modules, pipes, guards, decorators, entities, filters

The only exception used to be "empty stubs to compile" — **this exception is removed** because it is systematically abused.

### Mandatory mocking rule (anti ERR-007)

Dependencies in specs must be **mocked inline** with `vi.fn()` / `vi.mock()` / `createMock()`. Never use a real import to an implementation file.

```typescript

// ✅ CORRECT — inline mock, no implementation file created
const mockService = {
  create: vi.fn().mockResolvedValue({ id: 'uuid', status: 'pending' }),
};
const controller = new NotificationsController(mockService as any);

// ❌ FORBIDDEN — real import that forces file creation
import { NotificationsService } from './notifications.service';

```

If a type is required for the mock, define a type/interface **inside the spec file** or in a pure interface file.

### Mandatory commit after wave 1 (before dispatch to backend-dev)

```
test(<scope>): add failing tests (TDD red)
```

This commit must exist on the feat/ branch **before** wave 2 starts. Without this commit, the red→green cycle is not traceable in git history.

Publish in the scratchpad: list of created test files + what each validates.

---

## Wave 2 — backend-dev / frontend-dev

- Implement only what is needed to make the tests go `green`
- Any code not covered by a wave 1 test is unrequested code

---

## Wave 3 — code-reviewer

- Review the full test + implementation set

---

## What qa-engineer does NOT do in TDD mode

- Read implementation files before writing tests (that turns TDD into TAD)
- Adapt tests to code that is already written
- Write tests that pass immediately in wave 1 (if everything is green, the tests are not guiding the design)

---

## Allowed sources for tests in wave 1

- DTO / Zod schema
- Endpoint spec (method, path, expected payload/response)
- TypeScript interface or type if already defined
- Explicit prompt instructions
- **security-engineer brief if available**: its P0 constraints (IDOR, data sourcing, auth, scopes) are part of the endpoint contract — tests **must** validate them and thereby force the correct implementation in wave 2
  - Example: if security-engineer says `userId` must come from JWT `sub`, write tests so the controller reads `request.user.sub`, **not** `body.userId`
  - If security-engineer is not available in the context: state in the scratchpad that security constraints are unknown — do not invent them
