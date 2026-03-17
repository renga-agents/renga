---
applyTo: "**/*.ts,**/*.tsx"
---

# TypeScript Conventions

## General Rules

- Enable strict TypeScript mode (`strict: true` in tsconfig)
- Do not use `any`; use `unknown` and type guards when the type is unclear
- Prefer interfaces for objects and type aliases for unions/intersections
- Prefer `const enum` or union types over classic enums
- Use named exports only; avoid `export default`

## NestJS (backend)

- Use one module per business domain (bounded context)
- Validate DTOs with `class-validator` and `class-transformer`
- Use `HttpException` with appropriate HTTP status codes for business errors
- Use constructor injection only; never use `@Inject()` on properties
- Keep services pure and testable without infrastructure
- Keep controllers limited to validation, transformation, and delegation; no business logic
- Use the repository pattern for data access

## Patterns

- Use a `Result<T, E>` pattern for operations that can fail
- Use guard clauses at the beginning of functions
- Prefer pure functions when possible
- Default to immutability (`readonly`, `Readonly<T>`, `as const`)

## Naming

- Use camelCase for variables and functions
- Use PascalCase for classes, interfaces, types, and enums
- Use UPPER_SNAKE_CASE for constants
- Use suffixes: `.service.ts`, `.controller.ts`, `.module.ts`, `.dto.ts`, `.entity.ts`, `.spec.ts`
- Do not prefix interfaces with `I`

## Imports

- Use absolute imports via path aliases (`@/modules/...`, `@/shared/...`)
- Order imports as: 1) external libs, 2) internal modules, 3) relative imports
- Avoid circular imports

## Error Handling

- Always type errors explicitly
- Use structured JSON logging with context (correlation ID, user ID, action)
- Never catch and silently ignore errors
