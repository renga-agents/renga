---
description: "Use when modifying Next.js frontend code, App Router patterns, server/client components, or build config."
applyTo: "**/app/**,**/pages/**,**/next.config.*"
---
# Next.js — Development Guidelines

## App Router

- Prefer Server Components by default — add `'use client'` only when needed (hooks, event handlers, browser APIs)
- Use `loading.tsx` for Suspense boundaries at the route level
- Use `error.tsx` for error boundaries at the route level
- Colocate data fetching in Server Components — avoid client-side fetching when possible

## Env vars

- `NEXT_PUBLIC_*` — baked into client JS at build time via Docker build args
- Other vars — read at runtime via `process.env` in server components only
- Never import `process.env` in client components — use `NEXT_PUBLIC_*` prefix

## Styling

- Tailwind CSS + CSS Modules for scoped styles
- Prefer composition of utility classes over custom CSS

## Build

- Dockerfile uses multi-stage build → standalone output
- Production image: `node server.js` (no package manager in runtime)
- Set `output: 'standalone'` in `next.config.ts` for Docker deployments
