# Research: Fix Sync — UI Reactivity

**Feature**: 006-fix-sync-ui-refresh | **Date**: 2026-03-22

All decisions derived from reading the existing codebase. No external research required.

---

## Decision 1: Reactive mechanism — `liveQuery` vs polling vs event bus

**Decision**: Use `dexie`'s built-in `liveQuery()` observable.

**Rationale**: `liveQuery` is already available (Dexie is installed). It uses IndexedDB's native change-detection and re-runs the wrapped query only when the specific tables it reads from are written to. This is zero-cost when idle and precise — it does not re-run for unrelated table writes. No new packages, no polling interval, no manual event wiring.

**Alternatives considered**:
- **Polling**: call `loadContacts()` on a setInterval — rejected. Wastes resources, adds latency up to the poll interval, and could cause race conditions with the sync cycle.
- **Custom event bus**: sync service emits an event after each pull, stores listen and reload — rejected. Requires stores to know about the sync service; creates coupling; still falls back to full reload rather than fine-grained reactivity.
- **VueUse `useObservable`**: thin wrapper around RxJS that bridges Dexie's observable to Vue — rejected. Adds `@vueuse/rxjs` dependency unnecessarily since the subscribe/unsubscribe pattern is trivial to implement directly.

---

## Decision 2: Where to own the `liveQuery` subscription — store vs composable vs component

**Decision**: Contacts and interactions subscriptions live in their respective Pinia stores. ContactDetail subscriptions live directly in the page component.

**Rationale**:
- The contacts store is already the shared owner of `contacts` state used by `ContactListPage`. Migrating the subscription there keeps the interface unchanged for consumers.
- The interactions store already owns `entries` and `currentContactId`. The `liveQuery` subscription there replaces `loadForContact()` cleanly.
- `ContactDetailPage` reads contact/phones/emails/history that are not shared with other components. Keeping the subscriptions local to the page avoids polluting the store with page-specific data. It also allows clean `onUnmounted` teardown scoped to the page lifecycle.

---

## Decision 3: `liveQuery` subscription teardown

**Decision**: Store subscriptions are long-lived (store lifetime). Page component subscriptions are torn down in `onUnmounted`.

**Rationale**: Pinia stores are singletons that persist for the app lifetime. The contacts `liveQuery` subscription should stay active so the contact list is always fresh when navigated back to. Page components are mounted/unmounted on navigation — their subscriptions must be cleaned up to avoid memory leaks and stale callbacks after the component is destroyed.

For the interactions store, when `currentContactId` changes (navigating to a different contact detail page), the old subscription must be unsubscribed and a new one started for the new ID.

---

## Decision 4: Handling the `loading` state in ContactDetailPage

**Decision**: Set `loading.value = false` on the first emission of the contact `liveQuery` subscription, regardless of whether the contact was found.

**Rationale**: The existing `loading` flag guards the template from rendering before data is available. With `liveQuery`, the first emission arrives asynchronously (typically within one microtask). Setting `loading = false` on first emission preserves the existing loading UX with no behaviour change.

---

## Decision 5: Sync Now button placement

**Decision**: Add `SyncNowButton.vue` to the global nav in `App.vue`, immediately adjacent to `SyncStatusIcon`.

**Rationale**: The nav bar is the only UI element visible on all pages (except login). Placing the button there satisfies SC-005 ("reachable within 1 click from any data view"). Extending the existing `SyncStatusIcon` was considered but rejected — the icon is a pure display component; mixing interactive behaviour into it would violate the single-responsibility principle and complicate its tests.

---

## Decision 6: Preventing concurrent syncs

**Decision**: Track an `isSyncing` boolean flag in `SyncService` (or derive it from `syncStatus.value === 'syncing'`). The Sync Now button is disabled when this flag is true.

**Rationale**: `syncStatus` already transitions to `'syncing'` at the start of `syncCycle()` and back to `'synced'`/`'error'`/`'offline'` when it completes. Reading `syncStatus.value === 'syncing'` is sufficient to prevent concurrent syncs without any new state.

---

## Summary

| Unknown | Resolved | Decision |
|---------|----------|----------|
| Reactive mechanism | ✅ | `liveQuery` (Dexie built-in) |
| Subscription ownership | ✅ | Stores for shared state; page for page-local state |
| Teardown strategy | ✅ | Store = long-lived; page = `onUnmounted` |
| Loading state | ✅ | False on first liveQuery emission |
| Button placement | ✅ | Global nav, next to SyncStatusIcon |
| Concurrent sync prevention | ✅ | Derive from `syncStatus === 'syncing'` |
