---
applyTo: "**/*.sql,**/migrations/**,**/seeds/**,**/prisma/**,**/drizzle/**"
---

# Database Conventions

## PostgreSQL

- Use PostgreSQL as the primary database
- Use snake_case naming for tables, columns, indexes, and constraints
- Use plural table names (`users`, `notifications`, `orders`)
- Primary key: `id` (prefer UUID v7, or BIGSERIAL when performance is critical)
- Timestamps: `created_at` and `updated_at` on every table, with a trigger for `updated_at`
- Use soft deletes via `deleted_at` (nullable timestamp); avoid hard deletes except for temporary data

## Migrations

- One migration per logical change; avoid catch-all migrations
- Every migration must be reversible (UP + DOWN)
- Naming: `YYYYMMDDHHMMSS_description_snake_case.sql`
- Do not `DROP COLUMN` in production without a prior read-compatible migration (expand-contract pattern)
- Test migrations against a production dump before applying them

## Queries

- Do not use `SELECT *`; list columns explicitly
- Add indexes on columns used in `WHERE`, `JOIN`, and `ORDER BY`
- Run `EXPLAIN ANALYZE` for queries impacting more than 1000 rows
- Use cursor-based pagination for large lists; avoid `OFFSET`
- Use explicit transactions for multi-table writes

## Security

- Use parameterized queries only; never concatenate SQL strings
- Use Row Level Security (RLS) for multi-tenant data
- Use a DB user with minimal privileges; never run the application as superuser
- Never store sensitive data in plain text; use application-level encryption for critical PII

## Modeling

- Target at least 3NF; denormalize only with documented performance justification
- Use foreign keys with explicit `ON DELETE` behavior (`RESTRICT` by default)
- Use CHECK constraints for business invariants
- Use PostgreSQL enum types (`CREATE TYPE`) for finite value sets
