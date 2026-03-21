# Data Model: Sync Status Indicator

**Branch**: `002-sync-status-indicator` | **Date**: 2026-03-21

---

## Note

This feature introduces no new persistent entities (no database tables, no IndexedDB tables, no API schemas). The only "model" is a transient reactive state value held in memory.

---

## SyncStatus — State Machine

**Type**: `'synced' | 'syncing' | 'error' | 'offline'`

**Owner**: `sync.ts` (exported reactive ref, mutated only by `SyncService`)

### States

| State | Meaning | Visual |
|---|---|---|
| `synced` | All local changes pushed; last sync succeeded | Static ✓ icon (green) |
| `syncing` | A sync cycle is currently running | Spinning/animated ↻ icon |
| `error` | Last sync cycle failed (network or server error) | Static ✗ or ⚠ icon (red/amber) |
| `offline` | Browser reports no network connectivity | Static ✗ icon (grey) |

### Transitions

```
[initial] ──────────────────────────────→ synced  (if navigator.onLine, no unsynced items)
[initial] ──────────────────────────────→ syncing (on first syncCycle start)
[initial] ──────────────────────────────→ offline (if !navigator.onLine at startup)

synced  ──── syncCycle starts ─────────→ syncing
synced  ──── window 'offline' ─────────→ offline

syncing ──── syncCycle succeeds ────────→ synced
syncing ──── syncCycle fails ───────────→ error
syncing ──── window 'offline' ─────────→ offline

error   ──── syncCycle starts ─────────→ syncing
error   ──── window 'offline' ─────────→ offline

offline ──── window 'online' ──────────→ syncing  (triggers syncCycle)
```

### Rules

- The `offline` state is set immediately on the `window 'offline'` event and overrides any other state.
- Returning to `online` always transitions through `syncing` (a cycle runs immediately) before settling at `synced` or `error`.
- The status starts as `synced` if `navigator.onLine` is true on first load, `offline` otherwise. It immediately transitions to `syncing` when the first cycle starts.
