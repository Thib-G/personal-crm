# Feature Specification: Fix Sync — UI Does Not Reflect Data Changes Without Page Reload

**Feature Branch**: `006-fix-sync-ui-refresh`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "Fix sync: UI does not reflect data changes without a full page reload"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Contact List Stays Current After Sync (Priority: P1)

A user has the contact list open in their browser. The background sync cycle runs and pulls new or updated contacts from the server. Without any action from the user, the contact list updates to show the latest data.

**Why this priority**: The contact list is the primary view. If it requires a manual refresh to show current data, the sync mechanism provides no practical benefit for the most-used screen.

**Independent Test**: Open the contact list, trigger a server-side data change, wait for the next sync cycle — the list updates within 30 seconds without any user interaction.

**Acceptance Scenarios**:

1. **Given** the contact list is displayed, **When** the sync cycle pulls a new contact from the server, **Then** the new contact appears in the list automatically without a page reload.
2. **Given** the contact list is displayed, **When** the sync cycle pulls an update to an existing contact (e.g., name change), **Then** the updated contact data is shown automatically.
3. **Given** the contact list is displayed, **When** the sync cycle processes a deleted contact, **Then** the deleted contact disappears from the list automatically.
4. **Given** the user creates a contact in another browser tab or device, **When** the sync cycle completes, **Then** the new contact appears in the list on the current tab without a reload.

---

### User Story 2 - Contact Detail View Stays Current After Sync (Priority: P2)

A user is viewing a contact's detail page. A sync cycle runs and pulls updated data for that contact. The contact detail page updates automatically without requiring navigation away and back.

**Why this priority**: A user reviewing or referencing a contact's details should always see current information. Stale data on the detail page can cause errors or confusion during follow-up actions.

**Independent Test**: Open a contact detail page, trigger an update to that contact via another session, wait for the sync cycle — the detail page reflects the change automatically.

**Acceptance Scenarios**:

1. **Given** a contact detail page is open, **When** the sync cycle pulls an updated field for that contact (e.g., organisation name), **Then** the updated value is displayed without a page reload.
2. **Given** a contact detail page is open, **When** the sync cycle pulls a new phone number or email for that contact, **Then** the new contact detail appears automatically.

---

### User Story 3 - Interaction Feed Stays Current After Sync (Priority: P3)

A user is viewing the interaction history for a contact. A sync cycle runs and pulls new interaction entries for that contact. The feed updates to show the new entries without requiring a page reload.

**Why this priority**: The interaction feed is the key relationship-tracking view. Stale interactions give an inaccurate picture of recent activity.

**Independent Test**: Open an interaction feed for a contact, add an interaction entry via another session, wait for the sync cycle — the new entry appears in the feed automatically.

**Acceptance Scenarios**:

1. **Given** the interaction feed for a contact is displayed, **When** the sync cycle pulls a new interaction entry for that contact, **Then** the new entry appears in the feed automatically.
2. **Given** the interaction feed is displayed, **When** the user adds a new interaction entry locally, **Then** the entry appears in the feed immediately (without waiting for the sync cycle).

---

### User Story 4 - User Manually Triggers a Sync (Priority: P2)

A user wants to immediately pull the latest data from the server without waiting for the next automatic sync cycle. A "Sync Now" button is always accessible and triggers a full sync on demand.

**Why this priority**: The automatic sync cycle runs every 30 seconds. A user who just made changes on another device should be able to get fresh data immediately rather than waiting.

**Independent Test**: Click the Sync Now button while offline and while online — verify correct behaviour in both states independently.

**Acceptance Scenarios**:

1. **Given** the user is online, **When** they click the Sync Now button, **Then** a sync cycle starts immediately and the sync status indicator reflects the in-progress state.
2. **Given** a manual sync has completed, **When** new data was available on the server, **Then** all open views update to reflect the pulled data.
3. **Given** the user is offline, **When** they click the Sync Now button, **Then** the button communicates that sync is unavailable (e.g., disabled or shows offline state) and no error is thrown.
4. **Given** a sync is already in progress (manual or automatic), **When** the user clicks Sync Now, **Then** a second concurrent sync is not started — the button is disabled or ignored until the current cycle completes.

---

### Edge Cases

- What if a sync update arrives for a contact the user is currently editing? The in-progress edit must not be discarded or overwritten — the UI should not disrupt an active editing session.
- What if the sync cycle writes a change to a contact that has been deleted locally but not yet synced? The locally deleted contact should not reappear.
- What if the same contact is updated by two sync cycles in quick succession? The final displayed state must reflect the latest write with no visual flicker or duplicate entries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The contact list MUST update automatically when new, updated, or deleted contact data is written to local storage by the sync cycle, without requiring user interaction.
- **FR-002**: The contact detail view MUST update automatically when data for the currently displayed contact is modified in local storage.
- **FR-003**: The interaction feed MUST update automatically when new interaction entries for the current contact are written to local storage.
- **FR-004**: Automatic UI updates MUST NOT disrupt or discard an in-progress edit by the user.
- **FR-005**: Locally created or modified data MUST appear in the UI immediately upon being saved to local storage, without waiting for the sync cycle.
- **FR-006**: The UI MUST NOT require a full page reload or manual navigation to reflect any data change that has been written to local storage.
- **FR-007**: A "Sync Now" button MUST be permanently accessible from the main UI (not buried in settings) and MUST trigger an immediate sync cycle when clicked.
- **FR-008**: The Sync Now button MUST be disabled while a sync cycle is already in progress (whether manual or automatic) to prevent concurrent syncs.
- **FR-009**: The Sync Now button MUST be visually disabled or indicate unavailability when the user is offline, and clicking it offline MUST NOT produce an unhandled error.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Data changes written to local storage by the sync cycle are reflected in all open views within 2 seconds, without any user action.
- **SC-002**: 100% of data-displaying views (contact list, contact detail, interaction feed) update reactively — no view requires a page reload to show current local data.
- **SC-003**: Locally created or edited data appears in the UI instantly (under 200ms) after being saved.
- **SC-004**: No in-progress edit is lost or interrupted by an automatic UI update from a concurrent sync cycle.
- **SC-005**: The Sync Now button is reachable within 1 click from any data view.
- **SC-006**: Clicking Sync Now while online produces visible feedback (sync indicator changes state) within 500ms.

## Assumptions

- The local storage layer already contains the correct data after each sync cycle completes. The bug is in the UI layer not observing those writes, not in the sync logic itself.
- The fix applies to data already in local storage. Network latency or sync cycle frequency (currently every 30 seconds) is out of scope.
- Map view (if it displays contact pin data) is out of scope for this fix unless it shares the same data layer as the contact list.
- The fix must not break the existing optimistic local-write path (user creates/edits → data saved immediately → appears immediately).
