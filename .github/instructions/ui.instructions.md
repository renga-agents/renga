---
applyTo: "**/*.tsx,**/*.jsx,**/*.css,**/components/**,**/app/**"
---

# UI Conventions — Design System, Motion & Craft

> Philosophy: beauty lies in **precision**. Every pixel, every animation curve, every transition conveys intent. A well-designed product does not need to explain its interface.
>
> This file covers the **visual** and the **motion**. The file `ux.instructions.md` covers **behaviors** and **flows**.

---

## Design principles

### 1. Zero noise

- Every visible element serves a purpose — remove everything else
- Empty space is not waste, it is **breathing room**
- Fewer borders, shadows, and colors mean more clarity
- If removing an element changes nothing, remove it

### 2. Relentless hierarchy

- **Only one** element visually dominates each viewport
- Minimum size contrast ratio: 1.25× between typographic levels
- The eye should follow a natural path: title -> subtitle -> content -> action
- Avoid visual competition between equally important elements

### 3. Systemic consistency

- Every design decision is a **token**: color, spacing, radius, shadow, duration, curve
- If a value is not a token, it should not exist
- A component behaves **identically** in all contexts
- Variations are **intentional** and documented as variants, not exceptions

### 4. Obsessive craft

- Pixel-perfect alignment on a strict grid
- Use optical corrections when geometry lies
- Keep margins, paddings, and radii consistent everywhere
- Invisible details make products memorable

---

## Typographic system

### Modular scale

Use a ratio-based scale (1.25 — Major Third recommended):

```css

fontSize: {
  'display-2xl': ['4.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '700' }],
  'display-xl':  ['3.75rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '700' }],
  'display-lg':  ['3rem', { lineHeight: '1.15', letterSpacing: '-0.02em', fontWeight: '700' }],
  'display-md':  ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '600' }],
  'display-sm':  ['1.875rem', { lineHeight: '1.25', letterSpacing: '-0.01em', fontWeight: '600' }],
  'heading':     ['1.5rem', { lineHeight: '1.3', fontWeight: '600' }],
  'subheading':  ['1.25rem', { lineHeight: '1.4', fontWeight: '500' }],
  'body-lg':     ['1.125rem', { lineHeight: '1.6' }],
  'body':        ['1rem', { lineHeight: '1.6' }],
  'body-sm':     ['0.875rem', { lineHeight: '1.5' }],
  'caption':     ['0.75rem', { lineHeight: '1.4', letterSpacing: '0.01em' }],
}

```

### Typographic rules

- **Max 2 fonts** across the product — usually one UI sans-serif and one optional display font
- `next/font` is mandatory
- Line-height: 1.1-1.2 for titles, 1.5-1.6 for body text
- Negative letter-spacing for large titles, neutral/slightly positive for small text
- Keep body text measure around 50-75 characters — `max-w-prose` is usually the right ceiling
- Use clear weight contrast between titles and body, ideally at least two weight levels apart

---

## Color system

### Token structure

```css

colors: {
  /* Primitive scale — never used directly in components */
  gray: { 50: '...', 100: '...', 950: '...' },
  blue: { 50: '...', 100: '...', 950: '...' },

  /* Semantic tokens — the only values components should consume */
  background: {
    DEFAULT: 'var(--color-bg)',
    secondary: 'var(--color-bg-secondary)',
    tertiary: 'var(--color-bg-tertiary)',
    inverse: 'var(--color-bg-inverse)',
  },
  foreground: {
    DEFAULT: 'var(--color-fg)',
    secondary: 'var(--color-fg-secondary)',
    muted: 'var(--color-fg-muted)',
    inverse: 'var(--color-fg-inverse)',
  },
  border: {
    DEFAULT: 'var(--color-border)',
    strong: 'var(--color-border-strong)',
  },
  accent: {
    DEFAULT: 'var(--color-accent)',
    hover: 'var(--color-accent-hover)',
    foreground: 'var(--color-accent-fg)',
  },
  destructive: {
    DEFAULT: 'var(--color-destructive)',
    foreground: 'var(--color-destructive-fg)',
  },
  success: {
    DEFAULT: 'var(--color-success)',
    foreground: 'var(--color-success-fg)',
  },
}

```

### Color rules

- **Never** hardcode a color in a component — always use semantic tokens
- Support dark mode through CSS custom properties
- Use at most **3 colors** per view plus neutrals
- Meet WCAG AA contrast
- Keep consistent meaning for semantic colors
- Never rely on color alone to communicate meaning

---

## Spacing system

### 4px base scale

| Token | Value | Usage |
| --- | --- | --- |
| `0.5` (2px) | Micro | Optical adjustments |
| `1` (4px) | XS | Inline spacing, tight gaps |
| `2` (8px) | SM | Compact padding, default gaps |
| `3` (12px) | MD | Button padding, form spacing |
| `4` (16px) | LG | Card padding, internal sectioning |
| `6` (24px) | XL | Spacing between related sections |
| `8` (32px) | 2XL | Spacing between sections |
| `12` (48px) | 3XL | Spacing between major groups |
| `16` (64px) | 4XL | Page margins, hero sections |
| `24` (96px) | 5XL | Large section separators |

### Spacing rules

- **Always** use Tailwind tokens
- Keep internal spacing consistent inside a component
- Keep external spacing consistent between elements of the same type
- Related elements stay close; distinct groups are separated
- Group spacing should be at least 2× intra-group spacing
- Avoid arbitrary values such as `p-[13px]` unless there is a compelling optical reason documented in the component

---

## Border Radius & Shadows

### Radius tokens

```css

borderRadius: {
  'none': '0',
  'sm': '0.25rem',
  'md': '0.5rem',
  'lg': '0.75rem',
  'xl': '1rem',
  '2xl': '1.5rem',
  'full': '9999px',
}

```

### Shadow tokens

```css

boxShadow: {
  'xs': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  'sm': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
}

```

### Rules

- Use only one radius level per local context
- Nested radius should be visually coherent
- Reserve shadows for elevated elements only
- Prefer subtle borders for standard surfaces
- Reduce or replace shadows in dark mode
- Avoid mixing neighboring elements with `rounded-md` and `rounded-lg` unless the difference is part of a deliberate hierarchy

---

## Iconography

- Use one icon system only
- Default size: 16px inline, 20px in buttons, 24px standalone
- Keep stroke width consistent
- Use icon + label for primary actions
- Add `aria-hidden="true"` when decorative
- Add `aria-label` for icon-only buttons

---

## Motion Design — Principles

### Animation as language

- Animations are **never decorative**
- They communicate:
  relationship, feedback, continuity, and hierarchy

### Disney's 12 principles applied to UI

| Principle | UI application |
| --- | --- |
| **Squash & Stretch** | Buttons compress on click, modals expand |
| **Anticipation** | Micro-movement before an action |
| **Staging** | Only one animated element should dominate attention |
| **Follow Through** | Avoid abrupt stops — allow subtle overshoot |
| **Ease In/Out** | Never linear motion for standard transitions |
| **Arcs** | Favor natural curves over rigid straight paths |
| **Secondary Action** | Linked elements animate together coherently |

### Easing curves — tokens

```css

transitionTimingFunction: {
  'ease-out-expo': 'cubic-bezier(0.16, 1, 0.3, 1)',
  'ease-in-expo': 'cubic-bezier(0.7, 0, 0.84, 0)',
  'ease-in-out-expo': 'cubic-bezier(0.87, 0, 0.13, 1)',
  'ease-out-back': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
  'ease-out-quint': 'cubic-bezier(0.22, 1, 0.36, 1)',
  'ease-micro': 'cubic-bezier(0.25, 0.1, 0.25, 1)',
}

```

### Durations — tokens

```css

transitionDuration: {
  '75': '75ms',
  '150': '150ms',
  '200': '200ms',
  '300': '300ms',
  '500': '500ms',
  '700': '700ms',
  '1000': '1000ms',
}

```

### Fundamental rule

- Entrances: `ease-out`
- Exits: `ease-in`
- Internal transitions: `ease-in-out`
- Never use `linear` except for progress bars or infinite spinners

---

## Micro-interactions — In-page animations

### Hover & Focus

```tsx

// ✅ Button feedback pattern — layered hover, active, and focus states
<button className={cn(
  "relative px-4 py-2.5 rounded-lg font-medium",
  "bg-accent text-accent-foreground",
  "transition-all duration-150 ease-micro",
  "hover:brightness-110 hover:scale-[1.02] hover:shadow-md",
  "active:scale-[0.98] active:shadow-sm active:duration-75",
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2",
)}>
  {children}
</button>

```

### Scroll Reveal — Intersection Observer

```tsx

'use client'
import { useRef, useEffect, useState } from 'react'

export function RevealOnScroll({
  children,
  delay = 0,
  direction = 'up',
}: {
  children: React.ReactNode
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right'
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setIsVisible(true) },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' },
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  const transforms = {
    up: 'translate-y-8',
    down: '-translate-y-8',
    left: 'translate-x-8',
    right: '-translate-x-8',
  }

  return (
    <div
      ref={ref}
      className={cn(
        'transition-all duration-700 ease-out-expo',
        isVisible ? 'opacity-100 translate-x-0 translate-y-0' : `opacity-0 ${transforms[direction]}`,
      )}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}

```

### Stagger — Sequential orchestration

```tsx

// ✅ List with stagger — each item appears just after the previous one
export function StaggeredList({ items }: { items: Item[] }) {
  return (
    <ul>
      {items.map((item, i) => (
        <RevealOnScroll key={item.id} delay={i * 80} direction="up">
          <li>{item.name}</li>
        </RevealOnScroll>
      ))}
    </ul>
  )
}

```

Recommended stagger delays:

- Lists: 60-100ms
- Grids: 40-60ms
- Maximum total sequence: 800ms

### Number Counters

```tsx

'use client'
import { useEffect, useState } from 'react'

export function AnimatedCounter({ value, duration = 1000 }: { value: number; duration?: number }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    const start = performance.now()
    const step = (now: number) => {
      const progress = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.round(eased * value))
      if (progress < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [value, duration])

  return <span>{count.toLocaleString()}</span>
}

```

### Toast / Notification Entry

```css

/* Notification — slide in from top + fade */
@keyframes slide-in-from-top {
  from {
    opacity: 0;
    transform: translateY(-100%) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes slide-out-to-top {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(-100%) scale(0.95);
  }
}

.toast-enter { animation: slide-in-from-top 500ms ease-out-expo forwards; }
.toast-exit { animation: slide-out-to-top 300ms ease-in-expo forwards; }

```

### Skeleton Shimmer

```css

/* Shimmer effect for loading states */
@keyframes shimmer {
  from { background-position: -200% 0; }
  to { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 0%,
    var(--color-bg-tertiary) 50%,
    var(--color-bg-secondary) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-md);
}

```

---

## Page Transitions — Navigation between pages

### View Transitions API

```tsx

// Enable native View Transitions support
const nextConfig = {
  viewTransition: true,
}

```

```css

/* Exit transition — current page fades away */
::view-transition-old(root) {
  animation: fade-out 200ms ease-in forwards;
}

/* Entry transition — new page fades in */
::view-transition-new(root) {
  animation: fade-in 300ms ease-out-expo forwards;
}

@keyframes fade-out {
  to { opacity: 0; transform: scale(0.98); }
}

@keyframes fade-in {
  from { opacity: 0; transform: scale(1.02); }
  to { opacity: 1; transform: scale(1); }
}

```

### Named transitions — shared elements

```tsx

// Product list card
export function ProductCard({ product }: { product: Product }) {
  return (
    <Link href={`/products/${product.id}`}>
      <div style={{ viewTransitionName: `product-${product.id}` }}>
        <Image src={product.image} alt={product.name} />
        <h3>{product.name}</h3>
      </div>
    </Link>
  )
}

// Product detail page — same viewTransitionName means shared-element morphing
export default function ProductPage({ product }: { product: Product }) {
  return (
    <div style={{ viewTransitionName: `product-${product.id}` }}>
      <Image src={product.image} alt={product.name} />
      <h1>{product.name}</h1>
    </div>
  )
}

```

```css

/* Named transition styles for shared elements */
::view-transition-old(product-*) {
  animation: morph-out 300ms ease-in-out-expo forwards;
}
::view-transition-new(product-*) {
  animation: morph-in 300ms ease-in-out-expo forwards;
}

```

### Directional transitions — slide

```css

/* Side-slide transitions for forward/back navigation */
@keyframes slide-out-left {
  to { opacity: 0; transform: translateX(-5%); }
}
@keyframes slide-in-right {
  from { opacity: 0; transform: translateX(5%); }
}

.navigate-forward::view-transition-old(root) {
  animation: slide-out-left 250ms ease-in forwards;
}
.navigate-forward::view-transition-new(root) {
  animation: slide-in-right 350ms ease-out-expo forwards;
}

```

### Layout transitions with `<Activity>`

```tsx

'use client'
import { Activity } from 'react'

function TabContent({ activeTab }: { activeTab: string }) {
  return (
    <div className="relative overflow-hidden">
      {tabs.map(tab => (
        <Activity key={tab.id} mode={activeTab === tab.id ? 'visible' : 'hidden'}>
          <div className={cn(
            'transition-all duration-500 ease-out-expo',
            activeTab === tab.id
              ? 'opacity-100 translate-y-0'
              : 'opacity-0 translate-y-4 pointer-events-none',
          )}>
            <tab.Component />
          </div>
        </Activity>
      ))}
    </div>
  )
}

```

This pattern gives you visual continuity **and** preserves state instead of tearing down and remounting panels.

### Intercepting Routes — Modal

```tsx

export default function ProductModal({ params }: { params: Promise<{ id: string }> }) {
  return (
    <>
      {/* Backdrop with fade-in */}
      <div className="fixed inset-0 bg-black/50 animate-in fade-in duration-300 z-40" />
      {/* Modal with slide-up */}
      <div className={cn(
        "fixed inset-x-4 bottom-0 top-20 md:inset-auto md:top-1/2 md:left-1/2",
        "md:-translate-x-1/2 md:-translate-y-1/2 md:max-w-2xl md:w-full",
        "bg-background rounded-t-2xl md:rounded-2xl shadow-2xl",
        "animate-in slide-in-from-bottom-4 duration-500 ease-out-expo",
        "z-50",
      )}>
        <ProductDetail id={(await params).id} />
      </div>
    </>
  )
}

```

---

## Complex animations — Scroll-driven & Orchestration

### Scroll-linked animations

```css

.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--color-accent);
  transform-origin: left;
  animation: progress-grow auto linear;
  animation-timeline: scroll(root);
}

@keyframes progress-grow {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

```

### Light parallax

```css

.parallax-container {
  perspective: 1px;
  overflow-y: auto;
  height: 100vh;
}
.parallax-bg {
  transform: translateZ(-1px) scale(2);
}
.parallax-content {
  transform: translateZ(0);
}

```

### Sequential orchestration — Hero section

```tsx

export function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      <div className="animate-in fade-in slide-in-from-bottom-2 duration-500 delay-0">
        <Badge>New</Badge>
      </div>
      <h1 className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-150">
        Build something extraordinary
      </h1>
      <p className="animate-in fade-in slide-in-from-bottom-3 duration-700 delay-300">
        The platform for ambitious teams.
      </p>
      <div className="animate-in fade-in slide-in-from-bottom-2 duration-500 delay-500">
        <Button size="lg">Get Started</Button>
      </div>
      <div className="animate-in fade-in zoom-in-95 duration-1000 delay-700">
        <Image src="/hero.png" alt="Dashboard" />
      </div>
    </section>
  )
}

```

Orchestration rules:

- First element: delay 0
- Increment: 100-200ms between elements
- Total duration: max 1.5s
- Later elements may settle more slowly

---

## Reduced Motion — Mandatory accessibility

```css

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

```

```tsx

'use client'
import { useEffect, useState } from 'react'

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false)
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReduced(mq.matches)
    const handler = (e: MediaQueryListEvent) => setReduced(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])
  return reduced
}

```

### Rules

- **Always** include `@media (prefers-reduced-motion: reduce)`
- Keep only minimal motion for essential animations
- Remove decorative motion
- Preserve state/layout changes without movement when possible
- Essential motion such as loading spinners or transient notifications can remain, but prefer fade-only behavior

---

## Images & Media

- `next/image` is mandatory
- Define aspect ratios on all image containers
- Use blur placeholders above the fold
- Set the `sizes` prop on fluid images
- Background videos must be muted and inline
- Avoid autoplay with audio; background video should be `muted autoPlay playsInline`

---

## Dark Mode

```tsx

<html className={theme === 'dark' ? 'dark' : ''}>

:root {
  --color-bg: theme('colors.white');
  --color-fg: theme('colors.gray.950');
  --color-border: theme('colors.gray.200');
}
.dark {
  --color-bg: theme('colors.gray.950');
  --color-fg: theme('colors.gray.50');
  --color-border: theme('colors.gray.800');
}

```

### Dark mode rules

- Semantic tokens change, components do not
- Never hardcode dark classes inside components when tokens can solve it
- Reduce brightness of text and images appropriately
- Replace invisible shadows with borders when needed
- Pure white text on dark backgrounds is usually too harsh; softer near-white tokens are preferable

---

## Visual anti-patterns

| Forbidden | Correct |
| --- | --- |
| Hardcoded colors (`bg-blue-500`) | Semantic tokens (`bg-accent`) |
| Arbitrary values (`p-[13px]`) | Spacing tokens (`p-3`) |
| `linear` timing function | `ease-out-expo` for entrances |
| Animation > 1s on micro-interactions | 150-300ms |
| Costly JavaScript parallax | CSS scroll-linked or lightweight effects |
| Layout shift during loading | Fixed-size skeletons + aspect ratio |
| Text on image without overlay | Gradient overlay or semi-transparent backing |
| More than 2 fonts | 1 UI font + 1 display font max |
| `!important` for styling | Correct specificity via Tailwind |
| Ignoring `prefers-reduced-motion` | Mandatory media query |
| Shadows on surface elements | Subtle borders |
| Inconsistent radii | One radius per component level |
