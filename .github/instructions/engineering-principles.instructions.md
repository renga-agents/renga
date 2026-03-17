---
applyTo: "**/*.ts,**/*.tsx,**/*.py,**/*.go"
---

# Software Engineering Principles

> These principles apply to **all** code produced, regardless of language or framework.
> They are not dogma; they allow for justified exceptions. But any exception must be **explicit and documented**.

---

## SOLID

### S — Single Responsibility Principle (SRP)

- A class, module, or function = **one single reason to change**
- If the description of a component contains "and", it is probably doing too many things
- Separate: orchestration, business logic, persistence, presentation, validation

```typescript

// ❌ A class that does everything
class UserService {
  async createUser(data) { /* validation + insertion + email + logging */ }
}

// ✅ Separate responsibilities
class UserValidator { validate(data: UserInput): ValidatedUser }
class UserRepository { create(user: ValidatedUser): Promise<User> }
class WelcomeEmailSender { send(user: User): Promise<void> }
class UserService { /* orchestrates the 3 above */ }

```

### O — Open/Closed Principle (OCP)

- Open for extension, closed for modification
- Adding behavior should **never** require changing existing code
- Patterns: Strategy, Plugin, Event-driven, Decorator

```typescript

// ❌ Switch/if that grows with every new type
function calculateDiscount(type: string, price: number) {
  if (type === "student") return price * 0.8
  if (type === "senior") return price * 0.85
}

// ✅ Extensible through Strategy
interface DiscountStrategy { apply(price: number): number }
const strategies: Record<string, DiscountStrategy> = { student: ..., senior: ... }
function calculateDiscount(type: string, price: number) {
  return strategies[type]?.apply(price) ?? price
}

```

### L — Liskov Substitution Principle (LSP)

- A subtype must be substitutable for its parent type **without breaking behavior**
- If a subclass throws an unexpected exception or ignores a contract, it violates LSP
- Prefer composition over inheritance when LSP is hard to preserve

### I — Interface Segregation Principle (ISP)

- No "kitchen sink" interfaces; use multiple **small, specific interfaces**
- A consumer should not depend on methods it does not use

```typescript

// ❌ Interface too broad
interface Repository<T> {
  findAll(): Promise<T[]>
  findById(id: string): Promise<T | null>
  create(data: Partial<T>): Promise<T>
  update(id: string, data: Partial<T>): Promise<T>
  delete(id: string): Promise<void>
  aggregate(pipeline: any): Promise<any>
  bulkInsert(items: T[]): Promise<void>
}

// ✅ Split interfaces
interface Readable<T> { findAll(): Promise<T[]>; findById(id: string): Promise<T | null> }
interface Writable<T> { create(data: Partial<T>): Promise<T>; update(id: string, data: Partial<T>): Promise<T> }
interface Deletable { delete(id: string): Promise<void> }

```

### D — Dependency Inversion Principle (DIP)

- Depend on **abstractions**, not concrete implementations
- High-level modules do not depend on low-level modules; both depend on abstractions
- Use dependency injection systematically (constructor, parameter, IoC container)

```typescript

// ❌ Direct coupling
class OrderService {
  private stripe = new StripePayment()
}

// ✅ Injection through abstraction
class OrderService {
  constructor(private payment: PaymentGateway) {}
}

```

---

## DRY — Don't Repeat Yourself

- **Duplicated knowledge** = DRY violation. **Similar code** is not necessarily a DRY violation.
- Two identical code blocks that change for **different reasons** should not be merged
- Extract only when the code is duplicated AND changes for the same reasons
- Do not extract prematurely; wait for **three occurrences** before factoring (Rule of Three)

```

// ❌ DRY applied badly — premature abstraction
// Merging user validation and product validation into a "GenericValidator"
// -> They will diverge quickly

// ✅ DRY applied correctly
// Extract a utility function when the SAME pattern repeats 3+ times
// with the SAME semantics and the SAME reasons to change

```

---

## KISS — Keep It Simple, Stupid

- The simplest solution that works is the best one
- No design patterns "just in case"; YAGNI comes first
- If a junior developer cannot understand the code in 5 minutes, it is probably too complex
- Prefer explicit over implicit: no magic, no hidden conventions
- A clear `if/else` is better than a sophisticated pattern used only once

### Signs of excessive complexity

- Indentation depth > 3 -> extract sub-functions
- Function > 30 lines -> probably too long
- More than 4 parameters -> use a configuration object
- Method chain > 3 levels -> use a named intermediate variable

---

## YAGNI — You Aren't Gonna Need It

- **Never** implement functionality "that might be useful later"
- Build only what is needed **right now**
- Premature abstractions are worse than duplication
- If a pattern is not necessary yet, do not introduce it
- Corollary: delete dead code; code that is never executed is noise

```typescript

// ❌ YAGNI violation — over-engineering
interface EventBus<T extends BaseEvent> {
  publish<E extends T>(event: E): Promise<void>
  subscribe<E extends T>(type: string, handler: Handler<E>): Unsubscribe
}

// ✅ Simple and sufficient
async function notifyUserCreated(user: User): Promise<void> {
  await sendWelcomeEmail(user)
}

```

---

## Law of Demeter (Principle of Least Knowledge)

- An object should talk only to its **immediate neighbors**
- Avoid chains like `a.getB().getC().doSomething()`
- A module should not know another module's internal structure

```typescript

// ❌ Train wreck — knowledge of internal structure
const city = order.getCustomer().getAddress().getCity()

// ✅ Ask, do not dig through internals
const city = order.getDeliveryCity()

```

---

## Clean Code — Cross-Cutting Conventions

### Naming

- Use **intention-revealing** names: `getActiveUsers()` not `getData()`
- Use **pronounceable and searchable** names: `createdAt` not `crtdAt`
- No type prefixes: `IUserService` -> `UserService`
- Use affirmative booleans: `isActive`, `hasPermission`, `canEdit`
- Functions are verbs: `calculateTotal()`, `fetchUser()`, `validateInput()`
- Classes are nouns: `UserRepository`, `PaymentGateway`, `OrderValidator`

### Functions

- Keep functions **small** and focused on one thing
- Prefer 0-2 parameters; 3 maximum; beyond that use a config object
- Avoid side effects in functions named like getters
- Use guard clauses early to validate preconditions
- Avoid flag parameters: `render(isAdmin)` -> `renderAdmin()` and `renderUser()`

### Comments

- Code should be **self-documenting**; comments explain the **why**, not the what
- Use documentation comments on public APIs
- Remove outdated comments
- No commented-out code; Git is the history

### Error handling

- Use **exceptions**, not magic return codes
- Catch specific cases; never use empty `catch` blocks
- Fail fast and surface errors early
- Never swallow an error silently; log it at minimum
- Errors are **first-class citizens**: type them, document them, test them

```typescript

// ❌ Silent error
try { await save(data) } catch (e) { /* ignore */ }

// ✅ Explicit handling
try {
  await save(data)
} catch (error) {
  if (error instanceof ConflictError) {
    return { conflict: true, existing: error.existingRecord }
  }
  throw error
}

```

### Code structure

- Order inside a file: types/interfaces -> constants -> exported functions -> internal functions
- Group imports by origin: stdlib -> third-party -> internal, then sort alphabetically
- Keep related functions close together in the file
- Remove dead code and dead branches

---

## Composition over Inheritance

- Prefer **composition** and mixins over class inheritance
- Inheritance creates strong coupling and makes refactoring harder
- Use at most **one level** of inheritance; beyond that, rethink the design
- In TypeScript, prefer interfaces + composition to `extends`
- In Python, prefer Protocols + composition to multiple inheritance

---

## Fail Fast

- Validate inputs **at the boundary** of the system (API, CLI, event handler)
- Never propagate invalid data into internal layers
- Use assertions in development and validations in production
- If a state is supposed to be impossible, raise an explicit error

---

## Separation of Concerns

- Each layer has **one role** and ignores the details of the neighboring layers
- Typical architecture: `Controller/Router -> Service -> Repository -> Database`
- The business layer must never depend on a web framework
- The persistence layer should not know about HTTP

---

## Immutability by Default

- Prefer **immutable** data: `const`, `readonly`, `frozen`, `Readonly<T>`
- Keep mutations **explicit** and localized
- Shared objects across modules should always be immutable
- Prefer creating new instances over mutating existing ones

```typescript

// ❌ In-place mutation
function addTag(product: Product, tag: string) {
  product.tags.push(tag)
}

// ✅ New instance
function addTag(product: Product, tag: string): Product {
  return { ...product, tags: [...product.tags, tag] }
}

```

---

## When to Break These Principles

These principles allow for **documented exceptions**:

| Situation | Acceptable exception | Obligation |
| --- | --- | --- |
| Rapid prototyping (spike) | SOLID, DRY | Add comment `// SPIKE: to refactor before merge` |
| Critical hotfix in production | YAGNI, Clean Code | Create a technical debt ticket immediately |
| Proven performance-critical path | KISS, immutability | Document before/after benchmarks |
| Third-party library imposing a pattern | DIP, ISP | Wrap it behind an adapter |
| Generated code (ORM, API client) | All | Do not edit generated code; override it instead |
