# UI Contract: SyncNowButton

**Component**: `frontend/src/components/SyncNowButton.vue`
**Feature**: 006-fix-sync-ui-refresh

---

## State Matrix

| `syncStatus` | Button enabled | Visual appearance | Click behaviour |
|--------------|---------------|-------------------|-----------------|
| `synced` | ✅ Yes | Normal, clickable | Calls `syncNow()` immediately |
| `syncing` | ❌ No | Disabled / spinner | No-op (click ignored) |
| `error` | ✅ Yes | Normal, clickable | Calls `syncNow()` to retry |
| `offline` | ❌ No | Disabled / muted | No-op (click ignored) |

---

## Props

None. The component reads `syncStatus` directly from the sync service (shared singleton).

---

## Emits

None. Side effect is calling `syncService.syncNow()`.

---

## Accessibility

- Button element (`<button type="button">`) — not a `<div>` or `<span>`.
- `aria-label="Sync now"` always present.
- `disabled` attribute set when button is non-interactive (syncing or offline).
- Disabled state must be visually distinguishable (opacity or muted colour).

---

## Test Scenarios

1. When `syncStatus === 'synced'`, button is enabled and clicking calls `syncNow()`.
2. When `syncStatus === 'syncing'`, button has `disabled` attribute and clicking does not call `syncNow()`.
3. When `syncStatus === 'offline'`, button has `disabled` attribute.
4. When `syncStatus === 'error'`, button is enabled and clicking calls `syncNow()`.
