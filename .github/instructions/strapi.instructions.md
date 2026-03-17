---
description: "Use when modifying Strapi CMS code, content types, extensions, plugins, or GraphQL schema. Covers Strapi v5 specifics, Dockerfile build, and production deployment pitfalls."
applyTo: "**/src/api/**,**/src/extensions/**,**/config/**"
---
# Strapi v5 — Development Guidelines

## Critical: Production Build

Strapi production mode loads from `dist/`, NOT `src/`. After modifying files in:

- `src/api/` → already copied by Dockerfile
- `src/components/` → already copied by Dockerfile
- `src/extensions/` → already copied by Dockerfile

**If you create a new top-level directory under `src/` that must be available at runtime,
add `cp -r src/<dir> dist/src/<dir>` in the Dockerfile after `RUN pnpm build`.**

## Extensions

When customizing Strapi extensions under `src/extensions/`:

- Override controllers/services via `strapi-server.js` or `strapi-server.ts`
- Use `strapi.db.connection` (Knex) for raw SQL when the ORM is insufficient
- Always test extensions against `dist/` build — `pnpm build && pnpm start`

## GraphQL

- Default pagination limit is **10** — always specify `pagination: { limit: N }` for lists
- Group fragments and queries in dedicated files under the frontend project

## Content

Rich text fields may store HTML with editor-specific classes.
Ensure the frontend renderer handles these classes (e.g., `rehypeRaw` for raw HTML).
