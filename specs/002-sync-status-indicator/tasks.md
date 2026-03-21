# Tasks: Sync Status Indicator

**Input**: Design documents from `/specs/002-sync-status-indicator/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · quickstart.md ✅

**Tests**: TDD is **MANDATORY** per Constitution Principle V. Test tasks appear before implementation tasks in every user story phase. Tests MUST fail before implementation begins.

**Organization**: Tasks are grouped by user story. No setup or foundational phase is needed — all tooling, dependencies, and project structure are in place from feature 001.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase (different files, no shared dependencies)
- **[Story]**: User story this task belongs to (US1–US2)

---

## Phase 2: User Story 1 — See Current Sync State at a Glance (Priority: P1) 🎯 MVP

**Goal**: The navigation bar shows a reactive icon that reflects the current sync state (`synced`, `syncing`, `error`, `offline`) and transitions automatically as sync lifecycle events fire.

**Independent Test**: Open the app → observe the icon during a sync cycle → confirm it animates during sync, settles to ✓ on success, shows ⚠ after a backend failure, and shows ✗ immediately when DevTools network is set to Offline.

### Tests (write FIRST — must FAIL before implementation)

- [X] T001 [P] [US1] Write Vitest unit tests for `SyncStatusIcon.vue` in `frontend/src/components/tests/SyncStatusIcon.spec.ts`: mount component with each of the 4 `syncStatus` values (`synced`, `syncing`, `error`, `offline`) and assert the correct icon character is rendered; assert the `syncing` state element has the CSS animation class; assert non-syncing states do NOT have the animation class

### Implementation

- [X] T002 [P] [US1] Export `SyncStatus` type (`'synced' | 'syncing' | 'error' | 'offline'`) and `syncStatus` reactive ref (initial value: `navigator.onLine ? 'synced' : 'offline'`) from `frontend/src/services/sync.ts`
- [X] T003 [US1] Add `window.addEventListener('offline', () => { syncStatus.value = 'offline' })` to `SyncService.startSync()` in `frontend/src/services/sync.ts` (depends on T002)
- [X] T004 [US1] Update `SyncService.syncCycle()` in `frontend/src/services/sync.ts`: set `syncStatus.value = 'syncing'` at the start (guard: skip if already `'offline'`); set `'synced'` on successful completion; set `'error'` (or `'offline'` if `!navigator.onLine`) in the catch block (depends on T003)
- [X] T005 [US1] Create `frontend/src/components/SyncStatusIcon.vue`: reads `syncStatus` from `sync.ts`; renders a `<span>` with the correct Unicode icon per state (✓ synced, ↻ syncing, ⚠ error, ✗ offline); applies `@keyframes spin` CSS animation to the span when state is `'syncing'`; applies a per-state colour class (green / blue / red / grey) (depends on T002)
- [X] T006 [US1] Import `SyncStatusIcon` and add `<SyncStatusIcon />` between the Settings `<router-link>` and the Logout `<button>` in `frontend/src/App.vue` (depends on T005)

**Checkpoint**: Run `npm run test` → T001 tests pass. Open app → nav bar shows the sync icon. Icon spins during a sync cycle and settles to ✓. Toggling DevTools to Offline immediately shows ✗.

---

## Phase 3: User Story 2 — Understand What the Icon Means (Priority: P2)

**Goal**: Each icon state exposes a human-readable tooltip via the browser-native `title` attribute, accessible on hover (desktop) and long-press (mobile).

**Independent Test**: With the app open in each of the 4 states, hover over the icon and confirm the correct tooltip text appears with no additional interaction.

### Tests (write FIRST — must FAIL before implementation)

- [X] T007 [US2] Add tooltip assertions to `frontend/src/components/tests/SyncStatusIcon.spec.ts`: for each of the 4 states, assert the rendered element has the correct `title` attribute value — `'synced'` → `"All data synced"`, `'syncing'` → `"Syncing…"`, `'error'` → `"Sync failed — will retry"`, `'offline'` → `"Offline — sync paused"` (depends on T001; tests must fail before T008)

### Implementation

- [X] T008 [US2] Add `title` attribute to the `<span>` in `frontend/src/components/SyncStatusIcon.vue`, bound to a computed string that returns the correct tooltip text for each state (depends on T005)

**Checkpoint**: Run `npm run test` → all tests including T007 pass. Hover over the icon in each state → correct tooltip text visible.

---

## Phase 4: Polish & Validation

- [ ] T009 Run `quickstart.md` validation end-to-end: verify all 4 visual states, all 4 tooltips, auto-recovery from error state, and offline → syncing → synced transition via DevTools network toggle

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 2 (US1)**: No external dependencies — starts immediately
- **Phase 3 (US2)**: Depends on Phase 2 (SyncStatusIcon.vue must exist before tooltip tests can be written and run)
- **Phase 4 (Polish)**: Depends on Phases 2 and 3

### User Story Dependencies

- **US1 (P1)**: Independent — can start immediately
- **US2 (P2)**: Depends on US1 (tooltip is added to the component created in US1)

### Within Each User Story

1. Write tests → confirm they FAIL (Red)
2. Implement reactive state / component
3. Confirm tests PASS (Green)
4. Commit (one commit per task per Constitution Principle VI)

---

## Parallel Opportunities

### Phase 2

T001 (write tests) and T002 (add syncStatus to sync.ts) operate on different files and can run in parallel:

```
T001: frontend/src/components/tests/SyncStatusIcon.spec.ts
T002: frontend/src/services/sync.ts
```

T003 and T004 must be sequential (both modify `sync.ts`; T004 depends on T003).
T005 (create component) can start as soon as T002 is complete.
T006 (update App.vue) must wait for T005.

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 2: US1 (T001–T006)
2. **STOP and VALIDATE**: all 4 icon states visible, animation correct, offline detection working
3. Ship — the icon is useful even without tooltips

### Full Feature

4. Complete Phase 3: US2 (T007–T008) — adds tooltips
5. Complete Phase 4: Polish (T009) — end-to-end validation

---

## Notes

- TDD is non-negotiable per Constitution Principle V. T001 and T007 must be written and failing before their corresponding implementation tasks begin.
- Each task = one atomic commit per Constitution Principle VI.
- `[P]` tasks in the same phase operate on different files with no shared dependencies.
- No new npm packages: icons use Unicode characters; animation uses CSS `@keyframes`. Adding an icon library would violate Constitution Principle II (Simplicity Over Features).
- The `syncStatus` ref is exported from `sync.ts` (not a Pinia store) — see research.md Decision 1.
