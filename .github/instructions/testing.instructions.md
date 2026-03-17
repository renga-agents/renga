---
applyTo: "**/*.spec.ts,**/*.test.ts,**/*.spec.tsx,**/*.test.tsx,**/tests/**,**/e2e/**,**/__tests__/**,**/playwright/**"
---

# Testing Conventions

## Vitest (unit and integration tests)

- Use Vitest as the test runner; do not use Jest
- Keep test files colocated with the source: `module.service.spec.ts` next to `module.service.ts`
- Use the AAA pattern: Arrange -> Act -> Assert, with one block per section
- Use one `describe` per tested unit and one `it` per behavior
- Test naming: `it('should <expected behavior> when <condition>')`

## Rules

- Keep tests deterministic; avoid dependencies on time, randomness, or execution order
- Do not put conditional logic in tests (`if/else`)
- Keep mocks minimal; mock I/O (DB, HTTP, filesystem), not business logic
- Prefer one primary assertion per test; add more only when strongly related
- Do not merge with `test.skip`; skipped tests must be fixed or removed
- Do not use `sleep()`; use `waitFor()`, `vi.useFakeTimers()`, or event-driven patterns

## Playwright (E2E tests)

- Use the Page Object Model for recurring UI interactions
- Use resilient selectors: `data-testid`, `role`, `text`; never CSS classes or generated IDs
- Keep tests independent so each test can run on its own
- Naming: `<feature>.spec.ts` under `e2e/`
- Assertions: `expect(locator).toBeVisible()`, `toHaveText()`; avoid `wait` + `assert`
- Capture screenshots for critical visual tests

## Structure

```

src/
  modules/
    users/
      users.service.ts
      users.service.spec.ts     ← colocated unit test
      users.controller.spec.ts  ← colocated integration test
e2e/
  auth.spec.ts                  ← E2E test
  dashboard.spec.ts

```

## Coverage

- Minimum 80% coverage on services and business logic
- Controllers and resolvers should have integration tests, not unit tests
- Do not set coverage targets on config files, types, or DTOs
- Measure coverage by branches, not lines
