# Research: Sync Status Indicator

**Branch**: `002-sync-status-indicator` | **Date**: 2026-03-21

---

## Decision 1: State Management — Reactive ref vs Pinia store

**Decision**: Export a Vue 3 reactive `ref<SyncStatus>` directly from `sync.ts` alongside the existing `SyncService` singleton.

**Rationale**: The sync status is owned and mutated exclusively by `SyncService`. A Pinia store would add a layer of indirection with no benefit — the service would still need to call `store.setStatus()`. A module-level `ref()` is reactive, readable by any component, and keeps the state co-located with the code that changes it.

**Alternatives considered**:
- *Pinia store*: More consistent with other stores in the codebase, but adds boilerplate (defineStore, actions) for a single piece of state with a single writer. Rejected per Constitution Principle II.
- *Event emitter / mitt*: Adds a dependency and requires components to manage subscriptions manually. Rejected — Vue's reactive system handles this natively.

---

## Decision 2: Offline Detection

**Decision**: Use `window.addEventListener('online' / 'offline')` and `navigator.onLine` for initial state, consistent with how `SyncService.startSync()` already handles connectivity.

**Rationale**: The existing sync service already listens to `online` events to trigger sync cycles. Extending it to also emit `offline` state is zero additional complexity. `navigator.onLine` gives the initial state on first load.

**Alternatives considered**:
- *Polling a known endpoint*: More accurate for captive-portal detection, but adds network traffic and complexity. Out of scope for a single-user personal tool.

---

## Decision 3: Icon Component — Inline in App.vue vs Separate Component

**Decision**: Create a dedicated `SyncStatusIcon.vue` component, imported and used in `App.vue`.

**Rationale**: Separating the icon into its own component makes it independently testable with Vitest + `@vue/test-utils`. Inline logic in `App.vue` would complicate existing `App.vue` tests. Component boundary also makes future icon changes (color, shape, animation) isolated.

**Alternatives considered**:
- *Inline in App.vue*: Simpler for a small feature, but mixes rendering logic with layout concerns and makes unit testing harder.

---

## Decision 4: No New npm Packages

**Decision**: Use CSS animation (`@keyframes`) for the spinning/syncing state. Use Unicode characters or simple CSS shapes for icons rather than an icon library.

**Rationale**: Constitution mandates minimising third-party dependencies. Vue's reactive system and CSS are sufficient. An icon library (heroicons, lucide) would add a dependency purely for this feature.

**Alternatives considered**:
- *lucide-vue-next*: Would provide clean SVG icons but adds a dependency for a cosmetic feature. Rejected.
- *Emoji/Unicode symbols*: Accessible without any dependency; readable on all platforms.
