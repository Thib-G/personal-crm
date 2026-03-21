# Feature Specification: Sync Status Indicator

**Feature Branch**: `002-sync-status-indicator`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "as the app syncs asynchronously, add an icon showing the sync status between the frontend and backend"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See Current Sync State at a Glance (Priority: P1)

The user is browsing or editing contacts while the app silently syncs data with the backend in the background. They want to know at any time whether their local changes have reached the server — without needing to check logs or guess. A small status icon in the navigation bar reflects the current sync state: idle (all synced), in progress (sync running), or failed (last sync encountered an error).

**Why this priority**: This is the core value of the feature. Without a visible sync state, the user cannot trust whether their data is saved on the server. Trust in data persistence is critical for a personal CRM.

**Independent Test**: Can be fully tested by observing the icon change from idle → in-progress → idle as a sync cycle completes, with no backend interaction needed for the visual states.

**Acceptance Scenarios**:

1. **Given** the app is open and all local changes have been successfully synced, **When** the user looks at the navigation bar, **Then** they see a "synced" icon indicating data is up to date.
2. **Given** a sync cycle is actively running, **When** the user looks at the navigation bar, **Then** they see an animated "syncing" icon indicating data transfer is in progress.
3. **Given** the most recent sync attempt failed (network error, server error), **When** the user looks at the navigation bar, **Then** they see an "error" icon indicating the sync did not succeed.
4. **Given** the user is offline, **When** the user looks at the navigation bar, **Then** they see an indicator that the device has no connectivity and sync is paused.

---

### User Story 2 - Understand What the Icon Means (Priority: P2)

A user sees the sync icon but is unsure what each state means. They hover over (desktop) or tap (mobile) the icon to get a short tooltip or label that explains the current state in plain language.

**Why this priority**: The icon alone may not be self-explanatory to all users. A tooltip prevents confusion without adding visual clutter.

**Independent Test**: Can be fully tested by hovering or tapping the icon in each state and verifying the correct human-readable description appears.

**Acceptance Scenarios**:

1. **Given** the sync icon is in the "synced" state, **When** the user hovers or taps the icon, **Then** a tooltip reads "All data synced" (or equivalent clear language).
2. **Given** the sync icon is in the "syncing" state, **When** the user hovers or taps the icon, **Then** a tooltip reads "Syncing…" (or equivalent).
3. **Given** the sync icon is in the "error" state, **When** the user hovers or taps the icon, **Then** a tooltip reads "Sync failed — will retry" (or equivalent).
4. **Given** the sync icon is in the "offline" state, **When** the user hovers or taps the icon, **Then** a tooltip reads "Offline — sync paused" (or equivalent).

---

### Edge Cases

- What happens if the sync state changes while the tooltip is visible? (Tooltip should update to reflect the new state.)
- What if the app has never completed a sync cycle yet (first launch)? (Treat as "syncing" on first cycle, then transition to the result state.)
- What if connectivity is restored while the icon shows "offline"? (Icon transitions automatically to "syncing" then "synced" or "error" without user action.)
- What if a sync error is transient and the next automatic retry succeeds? (Icon returns to "synced" — no persistent error state after recovery.)
- What if the user has no unsynced local changes? (Icon shows "synced" since there is nothing to push; pull still happens but the icon does not enter "error" state unless it fails.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The app MUST display a persistent sync status icon in the navigation bar, visible on all authenticated pages except the login screen.
- **FR-002**: The icon MUST reflect four distinct states: **synced** (idle, no pending changes or last sync succeeded), **syncing** (a sync cycle is currently in progress), **error** (the most recent sync cycle failed), and **offline** (the device has no network connectivity).
- **FR-003**: The icon MUST transition automatically whenever the sync state changes, with no user action required.
- **FR-004**: The icon in the "syncing" state MUST be visually animated to convey active data transfer.
- **FR-005**: Each icon state MUST expose a short human-readable label accessible via hover tooltip on desktop and tap on mobile.
- **FR-006**: The icon MUST transition from "error" back to "synced" automatically if a subsequent sync cycle succeeds.
- **FR-007**: The icon MUST transition from "offline" to "syncing" automatically when network connectivity is restored.
- **FR-008**: The icon MUST transition to "offline" automatically when the device loses network connectivity.

### Key Entities

- **SyncStatus**: The current state of the background sync process. Four possible values: `synced`, `syncing`, `error`, `offline`. Driven by sync cycle lifecycle events (started, succeeded, failed) and network connectivity events (online, offline).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The sync status icon is visible on every authenticated page of the app (excluding login) with no additional user action.
- **SC-002**: The icon reflects a state change (e.g., idle → syncing) within 500ms of the underlying sync event occurring.
- **SC-003**: The "offline" state is reflected within 2 seconds of the device losing network connectivity.
- **SC-004**: The tooltip or label text unambiguously describes the current state; user comprehension is verifiable via usability check with no external reference needed.
- **SC-005**: The addition of the icon does not break or reflow the existing navigation bar layout on mobile or desktop viewports.

## Assumptions

- **Single global state**: The indicator reflects one global sync state — not per-record or per-entity granularity. One icon, not separate indicators per contact.
- **Placement in existing nav bar**: The icon is added to the existing top navigation bar alongside the current nav links, consistent with the app's existing layout.
- **No manual sync trigger**: This feature adds status visibility only; it does not introduce a "sync now" button. Manual triggering is out of scope.
- **Automatic retry**: The sync service retries on failure automatically. The icon reflects that retries are in progress; no user-initiated action is required.
- **Offline detection via browser events**: Offline/online state is determined using standard browser connectivity events, consistent with how the existing sync service already monitors connectivity.
- **No backend changes required**: This feature is entirely frontend — it reflects the state of the existing sync service and requires no new API endpoints or backend modifications.
