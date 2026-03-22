# Tasks: UI Layout & Styling

**Input**: Design documents from `/specs/004-ui-layout/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · quickstart.md ✅

**Tests**: No automated tests — this is a pure visual/CSS feature. Verification is by visual inspection per quickstart.md. Existing Vitest tests must remain green after each task.

**Organization**: Tasks are grouped by user story. The foundational task (CSS variables file) must be completed first. All page-level styling tasks are then independent of each other [P].

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1–US4)

---

## Phase 1: Foundational — Design Tokens & Global Import

**Purpose**: Create the shared CSS custom properties file and wire it into the app. Every subsequent task depends on this.

- [X] T001 Create `frontend/src/styles/variables.css` with all CSS custom properties: colors (`--color-primary: #3b82f6`, `--color-primary-dark: #2563eb`, `--color-danger: #ef4444`, `--color-success: #22c55e`, `--color-text: #111827`, `--color-text-muted: #6b7280`, `--color-border: #e5e7eb`, `--color-bg: #ffffff`, `--color-bg-muted: #f9fafb`, `--color-tag-bg: #eff6ff`, `--color-tag-text: #1d4ed8`), spacing (`--space-1: 4px` through `--space-8: 32px`), radius (`--radius-sm: 4px`, `--radius-md: 8px`), and font sizes (`--font-size-sm` through `--font-size-xl`)
- [X] T002 Add `import './styles/variables.css'` to `frontend/src/main.ts` (depends on T001)

**Checkpoint**: Open the app — no visual change yet, but CSS variables are available globally.

---

## Phase 2: User Story 1 — Navigation Bar (Priority: P1) 🎯 MVP

**Goal**: The navigation bar is polished, shows an active-page highlight, and wraps gracefully on mobile instead of overflowing.

**Independent Test**: Open the app at 375px and 1280px viewport widths. Confirm nav items are accessible at both sizes, the active link is highlighted, and there is no horizontal scroll.

- [X] T003 [US1] Replace all inline styles in `frontend/src/App.vue` with a `<style scoped>` block: style the nav bar with flexbox, `flex-wrap: wrap`, `padding: var(--space-2) var(--space-4)`, `border-bottom: 1px solid var(--color-border)`, `background: var(--color-bg)`; style nav links with `color: var(--color-text-muted)`, hover `color: var(--color-primary)`; add `.router-link-active` style with `color: var(--color-primary)` and `font-weight: 600`; style the logout button with `margin-left: auto`, `color: var(--color-text-muted)`, `background: none`, `border: none`, `cursor: pointer`; add `@media (min-width: 960px)` rule for a max-width content wrapper

**Checkpoint**: Nav bar styled. Active link highlighted. Wraps on mobile. Run `npm run test` in frontend — all Vitest tests pass.

---

## Phase 3: User Story 2 — Contacts List & Contact Detail (Priority: P2)

**Goal**: The contacts list has visually separated rows with clear hierarchy. The contact detail page has named, visually distinct sections.

**Independent Test**: Open the contacts list and a contact detail page. Confirm rows are separated, name is prominent, tags are styled, and the detail page has clear section headings.

- [X] T004 [P] [US2] Replace all inline styles in `frontend/src/pages/ContactListPage.vue` with a `<style scoped>` block: add a page header style with `display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4)`; style each contact list item as a card with `border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); margin-bottom: var(--space-2); background: var(--color-bg)`; make the contact name `font-weight: 600; color: var(--color-text)`; make organisation and context tag use `font-size: var(--font-size-sm); color: var(--color-text-muted)`; style context tag badge with `background: var(--color-tag-bg); color: var(--color-tag-text); border-radius: var(--radius-sm); padding: 2px var(--space-1)`; add empty-state style; add `@media (min-width: 960px)` max-width container

- [X] T005 [P] [US2] Replace all inline styles in `frontend/src/pages/ContactDetailPage.vue` with a `<style scoped>` block: add a page header area with flex layout for name + actions; style each content section (phones, emails, interactions, history) as a card with `border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: var(--space-4); margin-bottom: var(--space-4)`; style section headings with `font-size: var(--font-size-lg); font-weight: 600; margin-bottom: var(--space-3)`; style the Edit button as primary (`background: var(--color-primary); color: white; border-radius: var(--radius-sm); padding: var(--space-2) var(--space-4)`) and Delete button as danger (`background: var(--color-danger); color: white`); style the delete confirmation modal overlay with `position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center`; add mobile-first responsive layout

**Checkpoint**: Contacts list shows styled card rows. Detail page has named section cards. Run Vitest — all tests pass.

---

## Phase 4: User Story 3 — Forms: Login, Add Contact, Edit Contact (Priority: P3)

**Goal**: Login form is centered. Add/Edit contact forms have clear field groupings, styled error messages, and a prominent submit button.

**Independent Test**: Open login, add contact, and edit contact pages at 375px and 960px. Confirm forms are centered/comfortable, errors are visually distinct, and submit is prominent.

- [X] T006 [P] [US3] Replace all inline styles in `frontend/src/pages/LoginPage.vue` with a `<style scoped>` block: center the form with `max-width: 360px; margin: var(--space-8) auto; padding: 0 var(--space-4)`; add a card container (`background: var(--color-bg); border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: var(--space-6)`); style inputs with `width: 100%; padding: var(--space-2) var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-sm); font-size: var(--font-size-base)`; style the submit button as primary full-width; add error message style with `color: var(--color-danger); font-size: var(--font-size-sm)`

- [X] T007 [P] [US3] Replace all inline styles in `frontend/src/pages/AddContactPage.vue` with a `<style scoped>` block: add form layout with `max-width: 600px; margin: 0 auto; padding: var(--space-4)`; style fieldsets with `border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: var(--space-4); margin-bottom: var(--space-4)`; style dynamic phone/email rows as flex rows with a remove button; style error messages with `color: var(--color-danger); font-size: var(--font-size-sm)`; style the submit button as primary; add `@media (min-width: 640px)` two-column layout for form fields

- [X] T008 [P] [US3] Replace all inline styles in `frontend/src/pages/EditContactPage.vue` with a `<style scoped>` block using the same patterns as AddContactPage.vue (same form structure — consistent visual treatment)

**Checkpoint**: Login, Add, Edit pages styled. Error messages visually distinct. Run Vitest — all tests pass.

---

## Phase 5: User Story 4 — Map and Settings Pages (Priority: P4)

**Goal**: Map fills available viewport height. Settings page presents the privacy toggle clearly.

**Independent Test**: Open map at 375px and 1280px — map fills meaningful height without overflow. Open settings — toggle is clearly labeled.

- [X] T009 [P] [US4] Replace all inline styles in `frontend/src/pages/MapPage.vue` with a `<style scoped>` block: replace the fixed `height: 400px` map container with `height: calc(100vh - 120px); min-height: 300px; width: 100%`; add a page heading style; keep Leaflet CSS imports unchanged

- [X] T010 [P] [US4] Replace all inline styles in `frontend/src/pages/SettingsPage.vue` with a `<style scoped>` block: add page layout with `max-width: 600px; margin: 0 auto; padding: var(--space-4)`; style the privacy toggle row as a flex container with label text and description; style the checkbox as a larger touch target (`width: 20px; height: 20px`); add a save/status feedback style using `color: var(--color-success)`

**Checkpoint**: Map fills viewport appropriately. Settings page readable. Run Vitest — all tests pass.

---

## Phase 6: Polish & Validation

- [X] T011 Run `npm run test` in `frontend/` to confirm all existing Vitest tests still pass after all styling changes
- [X] T013 Style `frontend/src/components/AddInteractionForm.vue`: textarea with border/padding/focus ring, primary submit button
- [X] T014 Style `frontend/src/components/InteractionFeed.vue`: entry cards with border/radius, muted metadata row, empty state
- [X] T015 Style "Add Contact" button in `frontend/src/pages/ContactListPage.vue` as primary
- [X] T016 Add sans-serif font stack and `box-sizing` reset to `frontend/src/styles/variables.css`
- [X] T012 Run quickstart.md validation: test all 4 scenarios at 375px, 640px, and 1280px viewports; confirm no horizontal scroll, no functional regressions, sync icon colors match design tokens

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — must complete first (T001 → T002)
- **Phase 2–5 (User Stories)**: All depend on Phase 1 (T002 must be done before any page task)
- **Within US phases**: Tasks marked [P] operate on different files and can run in parallel
- **Phase 6 (Polish)**: Depends on all user story phases

### User Story Dependencies

- **US1 (P1)**: Depends on foundational only — no inter-story dependencies
- **US2 (P2)**: Depends on foundational only — parallel with US1
- **US3 (P3)**: Depends on foundational only — parallel with US1 and US2
- **US4 (P4)**: Depends on foundational only — parallel with all above

### Parallel Opportunities

Once T001 + T002 are done, T003–T010 can all run in parallel (each targets a different file):

```
T003  App.vue           (US1)
T004  ContactListPage   (US2)
T005  ContactDetailPage (US2)
T006  LoginPage         (US3)
T007  AddContactPage    (US3)
T008  EditContactPage   (US3)
T009  MapPage           (US4)
T010  SettingsPage      (US4)
```

---

## Implementation Strategy

### MVP (US1 only — navigation shell)

1. Complete T001 + T002 (design tokens)
2. Complete T003 (App.vue nav)
3. **STOP and VALIDATE**: App looks polished on all pages without touching page content

### Full Feature

4. Complete T004–T005 (contacts list + detail) — highest-value content pages
5. Complete T006–T008 (forms)
6. Complete T009–T010 (map + settings)
7. Complete T011–T012 (validation)

---

## Notes

- Do NOT change any `<script>` or `<template>` logic — only add/replace `<style scoped>` blocks and remove inline `style="..."` attributes.
- Always use `var(--token-name)` from `variables.css` rather than hard-coded values.
- Mobile-first: base styles = mobile (320px+), enhance with `@media (min-width: 640px)` and `@media (min-width: 960px)`.
- Run `npm run test` after each phase to confirm no Vitest regressions.
