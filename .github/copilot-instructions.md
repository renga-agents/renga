# [Project Name] — renga agent team

> Fill in the sections marked **[TODO]** with your project's actual information.
> This file is injected by Copilot into every agent session — keep it concise.

## Project identity

**Stack**: [TODO: e.g. TypeScript · React · Node.js · PostgreSQL]
**Domain**: [TODO: e.g. SaaS analytics platform]
**Key constraints**: [TODO: e.g. GDPR compliance, multi-tenant, performance-critical API]

Structuring decisions, ADRs, and technical context: `.renga/memory/project-context.md`

## Using the agent team

- **`@seiji`** — sole entry point for all tasks. Seiji decomposes, plans, dispatches specialist agents, and synthesizes results. Specialist agents are not directly invocable — they are dispatched internally by seiji.

Config: `.renga.yml` · Roster: `.github/agents/` · Session memory: `.renga/memory/`

## Conventions

[TODO: list any project-wide conventions agents must respect, e.g.:]

- All public API endpoints require authentication and rate-limiting
- Tests must be written before implementation (TDD)
- No direct commits to `main` — all changes via PR
