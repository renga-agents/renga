---
applyTo: "**/*.tsx,**/*.jsx,**/app/**,**/components/**"
---

# UX Conventions — User Experience Design

<!-- Next.js App Router is the project standard. Pages Router (pages/) is not supported. -->

> Philosophy: **every interaction must reduce the user's cognitive load**. The interface must never surprise, frustrate, or make users think unnecessarily.
>
> This file covers **behaviors** and **flows**. The file `ui.instructions.md` covers **visual design** and **animations**.

---

## Fundamental UX Laws

### Hick's Law — Reduce Choices

- The more options there are, the slower the decision
- **Max 5-7 items** in a menu or choice list
- Group logically beyond 7 options (categories, sections)
- Progressive disclosure: show the essentials, reveal the rest on demand
- By default, pre-select the most common choice

### Fitts's Law — Size & Distance

- Important elements are **large and close** to the action context
- Primary CTA: the largest visible button, seen first
- Destructive actions: smaller, farther away, with confirmation
- Touch targets: minimum **44×44px** (Apple HIG) / **48×48dp** (Material)
- Screen corners and edges are strategic positions on desktop

### Jakob's Law — Familiar Patterns

- Users spend most of their time on **other** sites
- Adopt patterns users already know
- Logo in the top-left -> go home
- Cart in the top-right
- Main navigation at the top or in a left sidebar
- Innovation belongs in the **content**, not in the **navigation**

### Miller's Law — Memory Capacity

- Working memory holds about **7 ± 2** items
- Group information into chunks
- Never require users to remember information from one page to another
- Show context: breadcrumbs, current wizard step, selection summary

### Tesler's Law — Conservation of Complexity

- Complexity cannot be removed, only **moved**
- Move complexity **toward the system**, not toward the user
- Smart defaults reduce decision fatigue
- Use autocomplete, suggestions, and automatic detection where appropriate

---

## Information Hierarchy

### Visual Priority

1. **Title / Main question** — what the user came for
2. **Primary action** — what the user can do
3. **Supporting content** — complementary information
4. **Secondary navigation** — access to other sections
5. **Footer / Metadata** — legal information, secondary links

### Reading Patterns

- **F-pattern** for text-heavy pages
- **Z-pattern** for landing and marketing pages
- Place critical information in the **top-left** for LTR reading
- Users **scan** before they read; use headings, bullets, and bold text

---

## Forms — Reduce Friction

### Golden Rules

- **Fewer fields = more conversions**
- One field per piece of information
- Put labels **above** fields
- Placeholders do not replace labels
- Autofocus the first field when appropriate
- Use native HTML input types
- Add `autocomplete` to identity and address fields

### Validation

- **Inline validation** with immediate feedback below the field
- Error messages must be constructive and actionable
- Use color + icon + text together
- Do not clear invalid fields automatically
- Validate on blur, not every keystroke
- Show success feedback too

### Submit Buttons

- Use specific labels: "Create my account" instead of "Submit"
- Disable during submission and show a spinner or progress state
- Show a visual success confirmation before redirecting
- On error, scroll to the first invalid field automatically

---

## Navigation & Wayfinding

### The User Must Always Know

1. **Where they are** — title, breadcrumbs, active tab
2. **Where they came from** — back button and preserved history
3. **Where they can go** — clear and visible navigation
4. **What they did** — confirmations and action history
5. **What they can do** — visible CTA and clear action states

### Navigation Rules

- **Back button always works**
- **URL reflects state** — filters, pagination, and tabs live in the URL when meaningful
- **Deep linking** — every meaningful state has a shareable URL
- Use breadcrumbs for hierarchies deeper than two levels
- Keep the main navigation accessible everywhere

---

## Feedback & States

### Every User Action Must Have Feedback

| Action | Immediate feedback | Final feedback |
| --- | --- | --- |
| Button click | Pressed state + loading | Success/error toast |
| Form submission | Disabled button + spinner | Confirmation + redirect |
| Deletion | Confirmation dialog | "Item deleted" toast + undo |
| Page load | Skeleton / shimmer | Content displayed |
| Network error | Error state with retry | Automatic recovery |
| Long action (> 2s) | Progress bar or spinner | Completion notification |

### Perceived Response Time

- **< 100ms**: instant
- **100ms - 1s**: pressed state + transition
- **1s - 10s**: spinner + explanatory text
- **> 10s**: progress bar + estimate

### Micro-interactions

- Provide visual or haptic feedback on interaction
- Animate transitions between idle, loading, success, and error states
- Keep intermediate states visible long enough to be understood

---

## Error Handling — UX

### Principles

- **Prevent** rather than correct
- **Forgive** with undo, auto-save, and confirmation for destructive actions
- **Explain** in human language, not technical jargon
- **Resolve** with a next step: retry, support, docs

### Error Messages

```

❌ "Error 500: Internal Server Error"
❌ "An error occurred"

✅ "Unable to save your document. Check your connection and try again."
✅ "This password is too short. Use at least 12 characters."

```

### Empty State Pattern

- Never leave a blank page
- Use an illustration, title, description, and CTA
- Example: "You don't have any projects yet. Create your first project ->"

---

## Responsive & Mobile-first

### Mobile-first Means Prioritization

- Designing for mobile first forces content prioritization
- If it does not fit on mobile, it may not be necessary
- Keep touch spacing >= 8px between interactive elements
- Never rely on hover-only interactions
- Hamburger menus are acceptable on mobile, not as the default on desktop

### Standard Breakpoints

| Breakpoint | Label | Usage |
| --- | --- | --- |
| 0 - 639px | Mobile | Single-column layout |
| 640px - 767px | `sm` | Typography adjustments |
| 768px - 1023px | `md` | Two-column layout, sidebar appears |
| 1024px - 1279px | `lg` | Full layout |
| 1280px+ | `xl` | Centered content, max-width |

---

## Accessibility — UX Principles

> Technical accessibility (ARIA, semantic HTML) lives in `react.instructions.md`.
> This file focuses on **inclusive design**.

- Maintain sufficient contrast: WCAG AA minimum
- Use at least 16px for body text, never below 12px
- Do not rely on color alone
- Keep focus visible on every interactive element
- Make reading order match visual order
- Respect `prefers-reduced-motion`
- Provide text alternatives for non-text content
- Use clear, accessible language

---

## Perceived Performance

Perceived **performance** matters more than measured **performance**:

- Use skeletons to show structure before data loads
- Show content progressively: text, then media, then interactions
- Use optimistic UI when the action is low-risk
- Prefetch likely next pages or resources when appropriate
- Keep feedback under 100ms when possible

---

## Onboarding & First-time Experience

- Avoid blocking tutorial modals
- Prefer contextual learning and progressive guidance
- Use educational empty states to drive the first action
- Offer presets and templates
- Use progressive profiling instead of asking everything upfront

---

## Microcopy — Principles

- **Concise**: "Save" not "Click here to save your project"
- **Active**: "Create an account" not "Account creation"
- **Human**: "Oops, something went wrong" not "Processing error"
- **Consistent**: use the same term for the same concept everywhere
- **Positive**: "Remember me" not "Do not sign me out"
- **Inclusive**: avoid unnecessary gendering; prefer neutral wording
