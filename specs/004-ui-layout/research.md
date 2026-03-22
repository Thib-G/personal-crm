# Research: UI Layout & Styling

**Feature**: 004-ui-layout
**Date**: 2026-03-21

---

## Decision 1: Global design tokens via CSS custom properties

**Decision**: Create `frontend/src/styles/variables.css` defining CSS custom properties for colors, spacing scale, border radius, and font sizes. Import it once in `frontend/src/main.ts`.

**Rationale**: CSS custom properties (`:root { --color-primary: … }`) give consistent values across all components without any build-time tooling. Any scoped `<style>` block in any Vue component can reference `var(--color-primary)` without imports. This is the standard way to share a design system without a CSS framework — zero new dependencies, aligns with Principle II.

**Alternatives considered**:
- Tailwind CSS: rejected — adds a significant dependency and build-time requirement, violates Principle II.
- SCSS variables: rejected — requires `sass` package (another dependency) and import plumbing in every file.
- Repeating values inline: rejected — the existing approach; leads to inconsistency across pages (different shades of grey on different pages).

---

## Decision 2: Scoped `<style>` block per Vue component

**Decision**: Each Vue page/component gets its own `<style scoped>` block. No shared component stylesheet (beyond the global tokens in Decision 1).

**Rationale**: Vue's scoped styles are the idiomatic approach — they prevent class name collisions, co-locate styles with templates, and require no extra tooling. Since each page has distinct layout needs (the map page is different from the contact list), per-component scoping is the right granularity.

**Alternatives considered**:
- Single global CSS file with all classes: works but creates a large file with many unused selectors per page, harder to maintain.
- CSS Modules: slightly more overhead (`:class="$style.foo"` syntax), no advantage over scoped at this scale.

---

## Decision 3: Mobile-first with two breakpoints

**Decision**: Base styles target 320px (mobile). One breakpoint at `@media (min-width: 640px)` for tablet/small desktop, one at `@media (min-width: 960px)` for wide desktop.

**Rationale**: Mobile-first means writing less override code — start with the constrained layout and progressively enhance. Two breakpoints are sufficient for this app's content (contacts list, forms, map); more would add complexity without benefit.

**Breakpoint mapping**:
- `< 640px`: single-column, stacked navigation, full-width inputs
- `640px – 959px`: wider content areas, more comfortable spacing
- `≥ 960px`: max-width content container centered, comfortable reading width

---

## Decision 4: Navigation on small screens — flex-wrap (no hamburger)

**Decision**: The navigation bar uses `flex-wrap: wrap` so links stack onto a second line on very small screens. No hamburger menu.

**Rationale**: The nav has only 3 links + sync icon + logout — 5 items. A hamburger menu adds significant JavaScript complexity for little benefit at this scale. Flex-wrap gives usable navigation on all screen sizes with pure CSS. Per Principle II, the simplest solution wins.

**Alternatives considered**:
- Hamburger/drawer menu: more polished on mobile but requires state management and transition logic — out of scope for a pure styling pass.
- Horizontal scroll: rejected — hidden content is worse UX than wrapping.

---

## Decision 5: Design token values

**Decision**: Use a neutral blue/gray palette with the following tokens:

```
--color-primary:     #3b82f6   (blue-500 — buttons, links, active states)
--color-primary-dark:#2563eb   (blue-600 — hover state)
--color-danger:      #ef4444   (red-500 — delete, errors)
--color-success:     #22c55e   (green-500 — sync synced, success messages)
--color-text:        #111827   (gray-900 — body text)
--color-text-muted:  #6b7280   (gray-500 — secondary text)
--color-border:      #e5e7eb   (gray-200 — borders, dividers)
--color-bg:          #ffffff   (page background)
--color-bg-muted:    #f9fafb   (gray-50 — subtle section backgrounds)
--color-tag-bg:      #eff6ff   (blue-50 — context tag badge background)
--color-tag-text:    #1d4ed8   (blue-700 — context tag badge text)

--space-1:  4px
--space-2:  8px
--space-3:  12px
--space-4:  16px
--space-6:  24px
--space-8:  32px

--radius-sm: 4px
--radius-md: 8px

--font-size-sm:   0.875rem
--font-size-base: 1rem
--font-size-lg:   1.125rem
--font-size-xl:   1.25rem
```

**Rationale**: These values mirror the existing sync icon colors (reusing `#3b82f6`, `#ef4444`, `#22c55e`) for consistency. The palette is minimal — 11 semantic colors, 6 spacing steps, 2 radii — enough to cover all design needs without over-engineering.

---

## Decision 6: No new npm packages

**Decision**: This feature adds zero new npm dependencies.

**Rationale**: CSS custom properties and `<style scoped>` are native browser and Vue features. No package additions needed. Aligns with constitution Technology & Stack Constraints (minimize dependencies).

---

## Decision 7: Map height — viewport-relative units

**Decision**: Replace the fixed `height: 400px` on the map container with `height: calc(100vh - 120px)` (approximate nav + padding offset), capped with a `min-height: 300px`.

**Rationale**: On mobile, 400px is proportionally very tall and leaves no room below the fold. Viewport-relative height ensures the map fills meaningful screen real estate on all device sizes without overflow. The `120px` offset accounts for the navigation bar height.
