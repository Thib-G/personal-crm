# Quickstart: Sync Status Indicator

**Branch**: `002-sync-status-indicator` | **Date**: 2026-03-21

---

## Verification Steps

### 1. Run the frontend unit tests

```bash
cd frontend
npm run test
```

All `SyncStatusIcon.spec.ts` tests must pass.

### 2. Start the dev stack

```bash
docker compose -f docker-compose.dev.yml up
```

Open `http://localhost:5173` and log in.

### 3. Verify all four states visually

| State | How to trigger | Expected icon |
|---|---|---|
| `synced` | Wait for a sync cycle to complete with no errors | Static ✓ (green) |
| `syncing` | Watch during the 30-second sync interval; or add a contact to trigger a push | Spinning ↻ animation |
| `error` | Stop the backend container (`docker stop <backend>`) and wait for next sync | ⚠ error icon (red/amber) |
| `offline` | Toggle off Wi-Fi / network in the browser DevTools (Network → Offline) | Grey ✗ offline icon |

### 4. Verify tooltips

Hover over (desktop) or tap (mobile) the icon in each state. Confirm the tooltip text matches:

| State | Expected tooltip |
|---|---|
| `synced` | "All data synced" |
| `syncing` | "Syncing…" |
| `error` | "Sync failed — will retry" |
| `offline` | "Offline — sync paused" |

### 5. Verify auto-recovery

1. Trigger the `error` state (stop backend container).
2. Restart the backend container.
3. Wait up to 30 seconds for the next sync cycle.
4. Confirm the icon returns to `synced` automatically.

### 6. Verify offline → online transition

1. Set browser to Offline mode.
2. Confirm icon shows `offline`.
3. Re-enable network.
4. Confirm icon transitions: `offline` → `syncing` → `synced` (or `error` if backend unreachable).
