# Implementation Plan: UI Layout & Styling

**Branch**: `004-ui-layout` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ui-layout/spec.md`

## Summary

Replace all inline styles across 7 Vue pages and App.vue with scoped `<style>` blocks, unified by a global CSS custom properties file (`variables.css`). Mobile-first layout (320px baseline) with breakpoints at 640px and 960px. Zero new npm dependencies.

## Technical Context

**Language/Version**: TypeScript 5 / Vue 3
**Primary Dependencies**: Vue 3 (built-in scoped styles) — no new packages
**Storage**: N/A — frontend-only, no data changes
**Testing**: Visual/manual (quickstart.md); existing Vitest tests must continue passing
**Target Platform**: Browser — mobile-first (320px+), scaling to desktop (960px+)
**Project Type**: Web SPA (frontend styling pass)
**Performance Goals**: No new JavaScript — pure CSS, no runtime overhead
**Constraints**: Zero new npm dependencies; no changes to component logic, props, or emits; existing Vitest tests must not break
**Scale/Scope**: 8 Vue files (App.vue + 7 pages); 1 new CSS file

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ✓ PASS | No data changes; no new network requests. |
| II. Simplicity Over Features | ✓ PASS | Native CSS custom properties + Vue scoped styles. Zero new dependencies. |
| III. Data Integrity | ✓ PASS | No model or API changes. |
| IV. User-Owned Data | ✓ PASS | No data structure changes. |
| V. TDD | ✓ PASS | Visual styling has no unit-testable logic. Existing Vitest tests must remain green (verified per task). |
| VI. Atomic Commits | ✓ PASS | One commit per page/component styled. |

**Gate result**: All principles pass. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/004-ui-layout/
├── plan.md         ← this file
├── research.md     ← Phase 0 output
├── quickstart.md   ← Phase 1 output
└── tasks.md        ← Phase 2 output (/speckit.tasks)
```

No `data-model.md` — no entities. No `contracts/` — no API surface.

### Source Code (repository root)

```text
frontend/src/
├── styles/
│   └── variables.css          ← NEW: CSS custom properties (colors, spacing, radius)
├── main.ts                    ← MODIFIED: import './styles/variables.css'
├── App.vue                    ← MODIFIED: scoped nav styles, remove inline styles
└── pages/
    ├── LoginPage.vue          ← MODIFIED: scoped form styles
    ├── ContactListPage.vue    ← MODIFIED: scoped list + card styles
    ├── ContactDetailPage.vue  ← MODIFIED: scoped section + modal styles
    ├── AddContactPage.vue     ← MODIFIED: scoped form styles
    ├── EditContactPage.vue    ← MODIFIED: scoped form styles
    ├── MapPage.vue            ← MODIFIED: scoped map container styles
    └── SettingsPage.vue       ← MODIFIED: scoped settings styles
```

**Structure Decision**: Single `variables.css` for shared tokens; all other styles scoped to their component.

## Architecture

### CSS custom properties (`variables.css`)

Defines the complete design token set: colors (primary, danger, success, text, border, backgrounds, tag badge), spacing scale (4px–32px), border radius (4px, 8px), and font sizes. Imported once in `main.ts` so all scoped blocks can reference `var(--color-primary)` etc.

### Breakpoint strategy (mobile-first)

```css
/* base: mobile 320px+ */
.nav { flex-wrap: wrap; }

@media (min-width: 640px) { /* tablet */ }
@media (min-width: 960px) { /* desktop — max-width container, centered */ }
```

### Per-component styling scope

| Component | Key styling work |
|-----------|-----------------|
| `App.vue` | Nav bar: flex layout, active link highlight, flex-wrap on mobile, logo/brand area |
| `LoginPage.vue` | Centered card, comfortable input sizing, prominent submit button |
| `ContactListPage.vue` | Bordered list items, name/org/tag hierarchy, badge styling, empty state |
| `ContactDetailPage.vue` | Section cards with headings, action button styles, delete modal overlay |
| `AddContactPage.vue` | Form field groups, phone/email dynamic rows, error message styling |
| `EditContactPage.vue` | Same as AddContactPage (shared visual pattern) |
| `MapPage.vue` | Viewport-relative map height (`calc(100vh - 120px)`), min-height 300px |
| `SettingsPage.vue` | Labeled toggle row, descriptive help text, consistent button style |

## Complexity Tracking

No constitution violations. Table not required.
