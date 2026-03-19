# [Project Name] — renga agent team

> Fill in the sections marked **[TODO]** with your project's actual information.
> This file is injected by Copilot into every agent session — keep it concise.

## Project identity

**Stack**: [TODO: e.g. TypeScript · React · Node.js · PostgreSQL]
**Domain**: [TODO: e.g. SaaS analytics platform]
**Key constraints**: [TODO: e.g. GDPR compliance, multi-tenant, performance-critical API]

Structuring decisions, ADRs, and technical context: `.renga/memory/project-context.md`

## Using the agent team

- **`@seiji`** — entry point for any multi-file, architectural, or multi-domain task. Seiji decomposes, plans, dispatches specialist agents, and synthesizes results.
- **Specialized agents** — invoke directly for focused single-domain tasks: `@software-architect`, `@security-engineer`, `@qa-engineer`, `@devops-engineer`, etc.

Config: `.renga.yml` · Roster: `.github/agents/` · Session memory: `.renga/memory/`

## Conventions

[TODO: list any project-wide conventions agents must respect, e.g.:]

- All public API endpoints require authentication and rate-limiting
- Tests must be written before implementation (TDD)
- No direct commits to `main` — all changes via PR
