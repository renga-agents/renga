---
applyTo: "**/*.tsx,**/*.jsx,**/next.config.*,**/app/**,**/components/**"
---

# React 19.2 & Next.js 16 Conventions

> Philosophy: **server-first**. Everything that can run on the server MUST run on the server. The client only receives the strictly necessary interactivity.
>
> **Prerequisites**: Node.js >= 20.9 (LTS), TypeScript >= 5.1

---

## Server-first architecture

### Golden rule: RSC by default

- Every component is a **React Server Component** unless proven otherwise
- `'use client'` only for: event handlers, stateful React hooks, browser APIs
- Push `'use client'` as low as possible in the tree — never on an entire layout or page
- **Islands** pattern: wrap only the interactive subtree in a Client Component

```tsx

// ✅ Good — minimal client isolation
// app/dashboard/page.tsx (Server Component)
export default async function DashboardPage() {
  const stats = await getStats()
  return (
    <main>
      <h1>Dashboard</h1>
      <StatsDisplay stats={stats} />
      <InteractiveChart data={stats} />
    </main>
  )
}

```

### When to use what

| Need | Solution | Environment |
| --- | --- | --- |
| Display data | RSC with direct `async/await` | Server |
| Mutation (create, update, delete) | Server Action (`'use server'`) | Server |
| Form with navigation | `<Form>` from `next/form` | Server + Client |
| Form with feedback | `useActionState()` + Server Action | Client -> Server |
| Optimistic update | `useOptimistic()` | Client |
| UI interactivity (toggle, modal, tabs) | `'use client'` + `useState` | Client |
| Client-side data fetching (rare) | `use()` with Promise passed from RSC | Client |
| Webhook / external API | Route Handler (`app/api/`) | Server |
| Post-response task (logging, analytics) | `after()` from `next/server` | Server |
| Force dynamic rendering | `connection()` from `next/server` | Server |
| Hide/restore UI without destroying state | `<Activity mode="hidden">` | Client |
| Isolate non-reactive logic inside an Effect | `useEffectEvent()` | Client |
| Request/response middleware (rewrites, auth) | `proxy.ts` | Server |

---

## Next.js 16 — App Router

### File conventions

- App Router **only** — no Pages Router
- Strictly follow the hierarchy: `layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx`, `template.tsx`
- `loading.tsx` for instant loading states
- `error.tsx` with mandatory `'use client'`
- `default.tsx` is **mandatory** for all Parallel Routes slots

### Metadata & SEO

- Async `generateMetadata()` for dynamic SEO
- Static `metadata` export when data is fixed
- OpenGraph images via `opengraph-image.tsx`

### Route Handlers

- `app/api/` only for webhooks and third-party APIs consumed by external clients
- Never use a Route Handler for internal data fetching — use RSC
- Never use a Route Handler for internal mutations — use Server Actions

### Proxy (replaces Middleware)

```ts

// proxy.ts
import { type NextRequest, NextResponse } from 'next/server'

export default function proxy(request: NextRequest) {
  // Runs on the Node.js runtime, not on Edge like the old middleware.ts model
  if (!request.cookies.get('session')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
}

```

- `middleware.ts` is **deprecated** — migrate to `proxy.ts`
- `proxy.ts` runs on **Node.js**
- The default exported function is named `proxy`

### Turbopack — default bundler

- `next dev` and `next build` use **Turbopack by default** in v16
- No need for `--turbopack`
- To switch back to webpack: `next dev --webpack` / `next build --webpack`
- File System Cache is enabled by default in dev

### Async APIs — mandatory

The following APIs are **all asynchronous** in v16. Synchronous access is gone:

```tsx

const { slug } = await params
const { q } = await searchParams
const cookieStore = await cookies()
const headersList = await headers()
const draft = await draftMode()

```

> In v15, synchronous access still existed in deprecated mode. In v16, it is removed. Codemod: `npx @next/codemod@latest upgrade`

---

## Cache — Next.js 16 Model

> Everything is **dynamic by default**. Cache is **entirely opt-in** via the `'use cache'` directive.

### The 4 cache layers

| Layer | Scope | Default behavior | Note |
| --- | --- | --- | --- |
| **Request Memoization** | Per render pass | Auto-deduplicates identical `fetch()` GET/HEAD calls | Unchanged |
| **Data Cache** | Persistent (server) | `fetch()` is **not cached** by default | Opt-in via `'use cache'` |
| **Full Route Cache** | Build-time | Static routes cached at build; dynamic routes not cached | Opt-in via `'use cache'` |
| **Router Cache** | Client (navigation) | Dynamic pages **not cached**; layouts = 5min | — |

### Enabling cache — `cacheComponents`

```ts

import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
}
export default nextConfig

```

> When `cacheComponents` is enabled, Route Segment Config options such as `dynamic`, `revalidate`, and `fetchCache` are effectively superseded. Prefer `'use cache'` + `cacheLife()` + `cacheTag()` exclusively.
>
> The old `experimental.dynamicIO` and `experimental.ppr` flags from v15 are removed in v16 and replaced by `cacheComponents`.

### `'use cache'` directive

```tsx

'use cache'
import { cacheLife, cacheTag } from 'next/cache'

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  cacheLife('hours')
  cacheTag(`product-${id}`)

  const product = await getProduct(id)
  return <ProductDisplay product={product} />
}

```

### `'use cache'` variants

| Directive | Usage | When to use it |
| --- | --- | --- |
| `'use cache'` | Standard cache | Default — public data |
| `'use cache: private'` | Allows `cookies()` and `headers()` | Personalized content |
| `'use cache: remote'` | External cache handler | Multi-instance cache sharing |

### Application levels

| Level | Example | Effect |
| --- | --- | --- |
| Whole file | `'use cache'` at the top of the file | All exports in the file are cached |
| Component | `'use cache'` inside the component body | This specific component is cached |
| Function | `'use cache'` inside a utility function | The function result is cached |

### Custom cache profiles

```ts

const nextConfig: NextConfig = {
  cacheComponents: true,
  cacheLife: {
    'product-detail': {
      stale: 300,
      revalidate: 60,
      expire: 3600,
    },
  },
}

```

```tsx

'use cache'
import { cacheLife } from 'next/cache'

export async function ProductDetail({ id }: { id: string }) {
  cacheLife('product-detail')
  // ...
}

```

### Cache invalidation

```ts

'use server'
import { revalidateTag, revalidatePath } from 'next/cache'

export async function updateProduct(formData: FormData) {
  await db.product.update()
  revalidateTag('product-123')
  revalidatePath('/products')
}

```

### Cache handlers — external storage

```ts

const nextConfig: NextConfig = {
  cacheComponents: true,
  cacheHandlers: {
    remote: require.resolve('./cache-handler-redis'),
  },
}

```

### `connection()` — force dynamic rendering

```ts

import { connection } from 'next/server'

export default async function Page() {
  await connection()
  const data = await fetchLiveData()
  return <LiveDashboard data={data} />
}

```

This replaces `unstable_noStore()`, which is removed.

### Route Segment Config (legacy, without `cacheComponents`)

If `cacheComponents` is **not** enabled, these options still exist but should be treated as legacy:

```ts

export const dynamic = 'auto' | 'force-dynamic' | 'error' | 'force-static'
export const revalidate = false | 0 | number
export const dynamicParams = true | false
export const fetchCache = 'auto' | 'default-cache' | 'force-cache' | 'force-no-store'
export const runtime = 'nodejs' | 'edge'
export const preferredRegion = 'auto' | 'global' | 'home' | string | string[]
export const maxDuration = number

```

> Recommendation: enable `cacheComponents: true` and rely on `'use cache'`, `cacheLife()`, and `cacheTag()`.

---

## Server Actions & Mutations

### Conventions

- Dedicated file with `'use server'` at the top
- One actions file per business domain
- HTTP method: **POST** only
- Progressive enhancement: works without client-side JavaScript

### Standard pattern

```ts

'use server'

import { revalidateTag } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createProduct(prevState: ActionState, formData: FormData) {
  const validated = productSchema.safeParse(Object.fromEntries(formData))
  if (!validated.success) {
    return { errors: validated.error.flatten().fieldErrors }
  }

  const product = await db.product.create({ data: validated.data })
  revalidateTag('products')
  redirect(`/products/${product.id}`)
}

```

### New revalidation APIs

```ts

'use server'
import { revalidateTag, revalidatePath, refresh, updateTag } from 'next/cache'

revalidateTag('products')
revalidatePath('/products')
refresh()
updateTag('product-123')

```

### Server Actions security

- **Always** validate inputs on the server
- **Always** verify authentication and authorization
- Closures over sensitive values are automatically encrypted, but do not rely on that as your primary design. Pass data explicitly through `FormData` or typed arguments.
- Treat Server Actions like public POST endpoints
- Configure `serverActions.allowedOrigins` in production

### Execution model

- Server Actions are **serialized per client** — one at a time
- Use `after()` for non-blocking post-response work such as analytics, logging, or notifications

### `after()` — post-response tasks

```ts

import { after } from 'next/server'

export default async function Page() {
  const data = await getData()
  after(() => {
    analyticsTrack('page_view', { page: 'dashboard' })
  })
  return <Dashboard data={data} />
}

```

- Stable since v15.1.0
- Usable in Server Components, Server Actions, and Route Handlers
- `cookies()` and `headers()` cannot be called inside the `after()` callback itself; read them before

---

## React 19.2 — Hooks & Patterns

### `use()` — reading promises and contexts

```tsx

import { use } from 'react'

function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  // Unlike most hooks, use() can be called in conditionals and loops
  const user = use(userPromise)
  const theme = use(ThemeContext)
  return <div className={theme}>{user.name}</div>
}

```

### `useActionState()` — forms with Server Actions

```tsx

'use client'
import { useActionState } from 'react'
import { createProduct } from '@/actions/product.actions'

export function CreateProductForm() {
  const [state, dispatch, isPending] = useActionState(createProduct, { errors: {} })

  return (
    <form action={dispatch}>
      <input name="title" />
      {state.errors?.title && <p>{state.errors.title}</p>}
      <SubmitButton isPending={isPending} />
    </form>
  )
}

```

> This replaces `useFormState` from React 18. It returns `[state, dispatch, isPending]`.

### `useOptimistic()` — optimistic updates

```tsx

'use client'
import { useOptimistic } from 'react'

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimistic] = useOptimistic(
    todos,
    (current, newTodo: Todo) => [...current, newTodo],
  )

  async function addTodo(formData: FormData) {
    const todo = { id: crypto.randomUUID(), title: formData.get('title') as string }
    addOptimistic(todo)
    await createTodoAction(formData)
  }

  return (
    <form action={addTodo}>
      <ul>{optimisticTodos.map(t => <li key={t.id}>{t.title}</li>)}</ul>
      <input name="title" />
      <button type="submit">Add</button>
    </form>
  )
}

```

### `useFormStatus()` — submission state

```tsx

'use client'
import { useFormStatus } from 'react-dom'  // import from react-dom, not react

export function SubmitButton({ label = 'Save' }: { label?: string }) {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending} aria-disabled={pending}>
      {pending ? 'Saving...' : label}
    </button>
  )
}

```

`useFormStatus()` must be used in a descendant of the `<form>`, not in the same component that renders the form element itself.

### `useEffectEvent()` — non-reactive logic inside Effects

```tsx

'use client'
import { useEffect, useEffectEvent } from 'react'

function ChatRoom({ roomId, theme }: { roomId: string; theme: string }) {
  // Isolate logic that reads reactive values without adding them to the effect dependencies
  const onConnected = useEffectEvent(() => {
    showNotification('Connected!', theme)
  })

  useEffect(() => {
    const conn = createConnection(roomId)
    conn.on('connected', () => onConnected())
    conn.connect()
    return () => conn.disconnect()
  }, [roomId])
}

```

- Stable since React 19.2
- Do not include the returned callback in the dependency array
- Do not call it during render; use it only from effects and event handlers
- Keep `eslint-plugin-react-hooks` updated so the rule understands the pattern

### `<Activity>` — state preservation with hide/show

```tsx

'use client'
import { Activity } from 'react'

function TabContainer({ activeTab }: { activeTab: string }) {
  return (
    <>
      <Activity mode={activeTab === 'home' ? 'visible' : 'hidden'}>
        <HomePage />
      </Activity>
      <Activity mode={activeTab === 'settings' ? 'visible' : 'hidden'}>
        <SettingsPage />
      </Activity>
    </>
  )
}

```

- `mode="hidden"`: applies `display: none`, cleans up effects, **preserves state**
- `mode="visible"`: restores the UI and re-runs effects
- Useful for tabs, preserved navigation state, and pre-rendered views

### React 19.2 rules

- No `useEffect` for data fetching
- No manual `useMemo`/`useCallback` if React Compiler is enabled
- `ref` is a regular prop
- Context providers can be rendered directly as `<MyContext>` in modern React patterns; avoid legacy verbosity when the codebase already supports it
- Use `useEffectEvent()` to isolate non-reactive logic
- Use `<Activity>` for preserved hidden UI

---

## React Compiler (1.0)

```ts

const nextConfig: NextConfig = {
  reactCompiler: true,
}

```

- Removes the need for manual `useMemo()`, `useCallback()`, `React.memo()`
- Per-component opt-in: `'use memo'`
- Opt-out: `'use no memo'`
- Keep `eslint-plugin-react-hooks` aligned with the React Compiler version when the project uses compiler rules

---

## `<Form>` — next/form

```tsx

import Form from 'next/form'

<Form action="/search" prefetch>
  <input name="q" />
  <button type="submit">Search</button>
</Form>

<Form action={createProduct}>
  <input name="title" />
  <button type="submit">Create</button>
</Form>

```

| Prop | `action` = URL (GET) | `action` = Server Action (POST) |
| --- | --- | --- |
| `replace` | Replaces the history entry | Ignored |
| `scroll` | Scroll to top after navigation | Ignored |
| `prefetch` | Prefetches the target page | N/A |

- Prefer `<Form>` from `next/form` over a plain native `<form>` when you want Next.js navigation benefits
- GET navigation keeps shared layouts mounted and avoids a full page reload
- It still degrades gracefully to normal form behavior without JavaScript

---

## Streaming & Suspense

### Streaming SSR

- `loading.tsx`: automatic loading state
- Streaming returns an **HTTP 200** — content is sent progressively
- Enables fast TTFB with an immediate static shell
- Suspense boundaries are revealed in batches

### Granular Suspense

```tsx

import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <main>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel />
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />
      </Suspense>
    </main>
  )
}

```

- Separate Suspense boundaries stream independently
- Use skeletons sized like the final content
- There is no waterfall when independent async components sit behind separate boundaries

### Parallel Routes

- `@slot` folders for independent layout sections
- Each slot has its own `loading.tsx` and `error.tsx`
- `default.tsx` is mandatory

### Intercepting Routes

- `(.)`, `(..)`, `(..)(..)`, `(...)` for modal or preview navigation interception

---

## Components

### Conventions

- One component per file
- Props typed with `interface` — no `React.FC`
- Props destructured in the function signature
- Composition over inheritance
- Separate Server and Client components
- Named exports only, except Next.js file conventions such as `page.tsx`, `layout.tsx`, `loading.tsx`, and similar

### Recommended hierarchy

```text

components/
  ui/
    button.tsx
    card.tsx
    skeleton.tsx
  features/
    product-card.tsx
    cart-drawer.tsx

```

---

## TailwindCSS

- TailwindCSS for all styling
- Use `cn()` for conditional classes
- Tokens in `tailwind.config.ts`
- Mobile-first responsive design
- UI variants through props, not classes passed around manually
- Avoid arbitrary values such as `text-[13px]` when a token can express the same intent

---

## State

| State type | Solution | Where |
| --- | --- | --- |
| URL (filters, pagination, search) | `searchParams`, route params, `useSearchParams()` | Server + Client |
| Server data | Direct RSC `async/await` | Server |
| Mutations | Server Actions + revalidation | Server |
| Local UI | `useState` | Client |
| Shared UI | Zustand | Client |
| Forms | `useActionState()` + Server Action | Client -> Server |
| Optimistic UI | `useOptimistic()` | Client |
| Preserved tab/view state | `<Activity mode>` | Client |

- Do not introduce Redux by default; it is usually too much ceremony for this stack
- Do not use React Query for server-rendered data that RSC already handles well
- React Query only makes sense when the client genuinely needs polling, realtime, or cache control beyond the server model

---

## Performance

### Images & Fonts

- `next/image` is mandatory
- `next/font` is mandatory
- Use automatic WebP/AVIF via `next/image`

### Code splitting

- Automatic per route with App Router
- `React.lazy()` only for heavy client-only components
- Use `next/dynamic` with `ssr: false` when needed

### Prefetching

- `<Link>` prefetches visible routes
- `<Form action="/path" prefetch>` prefetches GET destinations
- Turbopack file system cache speeds up rebuilds in dev and is enabled by default in recent v16 releases

---

## Accessibility

- Use semantic HTML
- Label all inputs
- Add alt text to images
- Keep focus visible
- Add `aria-disabled` when needed
- Provide skip links
- Test periodically with a screen reader
- Avoid clickable `<div>` patterns when a semantic `<button>` or `<a>` exists

---

## `next.config.ts` — v16 options reference

```ts

import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
  reactCompiler: true,
  turbopack: {},
  cacheHandlers: {
    remote: require.resolve('./cache-handler-redis'),
  },
  cacheLife: {
    short: { stale: 60, revalidate: 30, expire: 300 },
    long: { stale: 3600, revalidate: 900, expire: 86400 },
  },
  experimental: {
    staleTimes: { dynamic: 0, static: 300 },
  },
}
export default nextConfig

```

### Removed options in v16

| Removed | Replacement |
| --- | --- |
| `experimental.ppr` | `cacheComponents: true` |
| `experimental.dynamicIO` | `cacheComponents: true` |
| `experimental.reactCompiler` | `reactCompiler: true` |
| `experimental.turbopack` | `turbopack: {}` |
| `serverRuntimeConfig` / `publicRuntimeConfig` | `.env` files |
| AMP (`useAmp`, `config.amp`) | Removed with no replacement |
| `next lint` | ESLint / Biome directly |

---

## Summary: server vs client decision tree

```text

Does the component need:
├── Async data (DB, API)?
│   └── -> Server Component (RSC) with async/await
├── Mutation (create/update/delete)?
│   └── -> Server Action ('use server')
├── Event handlers (onClick, onChange)?
│   └── -> 'use client' — isolate minimally
├── Stateful hooks (useState, useReducer)?
│   └── -> 'use client' — isolate minimally
├── Browser APIs (localStorage, geolocation)?
│   └── -> 'use client' — isolate minimally
├── Preserve state between hide/show?
│   └── -> <Activity mode="visible|hidden">
├── Non-reactive logic inside an Effect?
│   └── -> useEffectEvent()
└── None of the above?
    └── -> Server Component (default, add nothing)

```
