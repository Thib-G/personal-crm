# Feature Specification: Personal CRM Web Application

**Feature Branch**: `001-personal-crm`
**Created**: 2026-03-20
**Status**: Draft
**Input**: User description: "create a personal crm webapp, to keep track of the contacts i make during events, at work, in private. it should make it easy for me to add names and contact details, with an history of the modifications, and always store the gps location of the edit (depending on privacy settings of course). it should also allow me to store a small summary for me to remember the interactions. in a later version, maybe able to fetch data from public sources (linkedin for contacts, banque carrefour des entreprises for belgian companies etc.)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a New Contact (Priority: P1)

A user meets someone at an event, at work, or in their personal life, and wants to quickly capture that person's name and contact details before they forget. The user opens the app, taps "Add Contact", fills in a name, phone number or email, selects the context (event, work, personal), optionally writes a short note about the interaction, and saves. The app records the current GPS location at the time of saving (if location access is granted) and timestamps the entry.

**Why this priority**: This is the core value proposition — without the ability to add contacts, nothing else works. It must be fast and frictionless.

**Independent Test**: Can be fully tested by adding a contact and verifying it appears in the contact list with correct details, timestamp, and location data.

**Acceptance Scenarios**:

1. **Given** the user opens the app, **When** they fill in at least a name and save, **Then** the contact is created and visible in the contact list with a creation timestamp.
2. **Given** the user has granted location permission, **When** they save a contact, **Then** the contact record stores the GPS coordinates at the time of saving.
3. **Given** the user has denied location permission or location tracking is disabled in privacy settings, **When** they save a contact, **Then** the contact is saved without GPS data and no error is shown.
4. **Given** the user is adding a contact, **When** they leave the name field empty, **Then** the system prevents saving and shows a clear validation message.

---

### User Story 2 - View and Browse Contacts (Priority: P2)

A user wants to find a specific contact they added previously. They open the app, see a list or searchable directory of all their contacts, and can quickly locate someone by name, context (work/event/personal), or keyword in notes.

**Why this priority**: Retrieval is as important as entry — the app only delivers value if contacts are easy to find.

**Independent Test**: Can be fully tested by adding several contacts and verifying search/filter returns correct results.

**Acceptance Scenarios**:

1. **Given** the user has saved contacts, **When** they open the contact list, **Then** all contacts are displayed with name, context tag, and creation date visible.
2. **Given** the user types a name or keyword in the search field, **When** they submit the query, **Then** only matching contacts are shown.
3. **Given** the user selects a contact, **When** the contact detail view opens, **Then** all stored fields, the interaction summary, and the edit history are visible.

---

### User Story 3 - Edit a Contact and View History (Priority: P3)

A user learns new information about a contact (new job title, new phone number) and wants to update the record. After editing, the previous values are preserved in a history log so the user can see how the contact's details evolved over time. The GPS location and timestamp of each edit are also stored.

**Why this priority**: Contacts change over time; history provides context and prevents loss of information.

**Independent Test**: Can be fully tested by editing a contact field and verifying the history log shows both old and new values with timestamps and locations.

**Acceptance Scenarios**:

1. **Given** the user opens a contact and edits a field, **When** they save, **Then** the contact is updated and the previous value is preserved in the edit history with a timestamp.
2. **Given** the user has location access enabled, **When** they save an edit, **Then** the GPS coordinates at edit time are stored alongside the history entry.
3. **Given** the user views the edit history for a contact, **When** the history panel is open, **Then** each history entry shows the changed field, old value, new value, date/time, and location (if available).

---

### User Story 4 - Log an Interaction Entry (Priority: P3)

After meeting someone, the user wants to add a new timestamped note to remember that specific interaction: where they met, what was discussed, any follow-up action needed. Each interaction is a separate dated entry so the full history of meetings is visible as a feed on the contact's page.

**Why this priority**: The interaction log is what differentiates a CRM from a simple address book — it captures the evolving human relationship over time.

**Independent Test**: Can be fully tested by adding multiple interaction entries to a contact and verifying they all appear as a dated feed on the contact detail view.

**Acceptance Scenarios**:

1. **Given** the user opens a contact, **When** they add a new interaction entry with text and save, **Then** the entry is stored with a timestamp and appears at the top of the interaction feed.
2. **Given** the user has multiple interaction entries, **When** they view the contact detail, **Then** all entries are visible as a chronological feed (newest first), each showing its text, date, and GPS location (if available).
3. **Given** the user adds an interaction entry while location tracking is enabled, **When** they save, **Then** the entry records the current GPS coordinates.
4. **Given** the user leaves the entry text empty, **When** they attempt to save, **Then** the system prevents saving and shows a validation message.

---

### User Story 5 - Manage Privacy Settings (Priority: P4)

The user wants control over whether location data is collected. They can toggle GPS tracking on or off globally from the app's settings page, and this preference is respected for all future edits.

**Why this priority**: Location tracking is privacy-sensitive; user control is required for trust and compliance.

**Independent Test**: Can be fully tested by disabling GPS tracking in settings, adding a contact, and verifying no location is recorded.

**Acceptance Scenarios**:

1. **Given** the user opens settings and disables location tracking, **When** they subsequently add or edit a contact, **Then** no GPS data is recorded for those entries.
2. **Given** the user re-enables location tracking, **When** they add or edit a contact, **Then** GPS data is recorded again.
3. **Given** the device OS denies location permission for the app, **When** the user has location tracking enabled in app settings, **Then** the app gracefully falls back to saving without location and notifies the user once.

---

### User Story 6 - Explore Contacts on a Map (Priority: P4)

The user wants to see where they've met people or made edits, displayed as pins on a map. They can open the map view to get a geographic overview of their network — useful after events, conferences, or travel.

**Why this priority**: Adds spatial context that complements the list view; GPS is already captured, so the map is a natural extension with high value at low incremental cost.

**Independent Test**: Can be fully tested by adding contacts with GPS data and verifying they appear as pins on the map at the correct locations.

**Acceptance Scenarios**:

1. **Given** contacts or interaction entries with GPS coordinates exist, **When** the user opens the map view, **Then** each location is shown as a pin on the map.
2. **Given** the user taps a pin, **When** the pin detail opens, **Then** the associated contact name and interaction summary (or field edit context) is shown with a link to the full contact.
3. **Given** a contact has no GPS data, **When** the map view is open, **Then** that contact is not shown on the map (no error, no empty pin).
4. **Given** multiple interactions occurred at the same location, **When** the map renders, **Then** pins are clustered to avoid overlap, with the cluster count visible.

---

### Edge Cases

- What happens when a contact is saved with only a name and no other details? (Should be allowed — name is the only required field.)
- How does the system handle duplicate names (two contacts named "John Smith")? (Both are kept; no deduplication in v1.)
- What if the user loses internet connectivity while saving a contact — is data preserved locally?
- What happens if GPS coordinates are unavailable (e.g., airplane mode, indoors, no signal) while location tracking is enabled? (Save proceeds; location recorded as unavailable.)
- How does the history display when a contact has been edited many times — is there pagination?
- What if the user clears browser/app data — are contacts lost? (Out of scope for v1; assumed handled by backend persistence.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-000**: System MUST require users to authenticate (email/password or passkey) before accessing any contact data; unauthenticated requests must be rejected.
- **FR-001**: System MUST allow users to create a contact with at minimum a name field; all other fields are optional.
- **FR-002**: System MUST support the following contact fields: full name, phone number(s), email address(es), organisation/company, context tag (event / work / personal / other), and interaction summary.
- **FR-003**: System MUST automatically record the current timestamp whenever a contact is created or edited.
- **FR-004**: System MUST request device location permission and, when granted and location tracking is enabled in privacy settings, record GPS coordinates at the moment of each create or edit operation.
- **FR-005**: System MUST store an immutable history log for every contact, capturing each field change with its old value, new value, timestamp, and GPS location (if available).
- **FR-006**: System MUST allow users to view the full edit history of any contact.
- **FR-007**: System MUST provide full-text search across all contact fields (name, organisation, phone, email, context tag) and all interaction entry text; results must update as the user types.
- **FR-007b**: System MUST provide a map view that plots contacts and individual interaction entries at their recorded GPS locations; tapping a pin opens a popup showing the contact name and context label, with a "View contact" link that navigates to the contact detail page in the same tab.
- **FR-008**: System MUST allow users to add multiple timestamped interaction entries to any contact; each entry is a free-text note with a creation timestamp and optional GPS location.
- **FR-009**: System MUST provide a privacy settings screen where users can enable or disable GPS location tracking for all future edits.
- **FR-010**: System MUST respect the user's location privacy preference and never collect GPS data when the preference is disabled.
- **FR-011**: System MUST allow users to edit any field on an existing contact.
- **FR-012**: System MUST allow users to permanently delete a contact; deletion MUST be preceded by a warning explicitly stating that all associated data (field history, interaction entries) will be irreversibly removed. No data is retained after confirmed deletion.
- **FR-013**: System SHOULD support attaching multiple phone numbers or email addresses to a single contact.
- **FR-014**: System SHOULD display contacts in a sortable, browsable list (default: alphabetical by name).

### Key Entities

- **Contact**: The central record. Attributes include name, phone number(s), email address(es), organisation, context tag (event/work/personal/other), creation timestamp, creation location (optional), and last modified timestamp.
- **InteractionEntry**: A timestamped note attached to a Contact, created each time the user logs an interaction. Attributes include free-text content, creation timestamp, and GPS coordinates (nullable). Entries are immutable once saved; the full list forms the interaction feed for a contact.
- **ContactHistory**: An append-only log entry linked to a Contact, recording changes to contact fields (not interaction entries). Attributes include the field that changed, previous value, new value, timestamp of change, and GPS coordinates at time of change (nullable).
- **PrivacySettings**: User-level preferences. Attributes include location tracking enabled (boolean), defaulting to enabled subject to OS-level permission.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can add a new contact with name and at least one detail in under 60 seconds from opening the app.
- **SC-002**: A user can locate any existing contact by name search in under 10 seconds, regardless of total contact count up to 1,000 contacts.
- **SC-003**: Every contact creation and edit reliably records a timestamp; GPS coordinates are recorded in 100% of cases where location access is granted and tracking is enabled.
- **SC-004**: The edit history for any contact is fully accessible and displays all past changes with no data loss.
- **SC-005**: Disabling location tracking in settings immediately prevents any new GPS data from being captured; existing historical data is unaffected.
- **SC-006**: The app remains fully usable (add, edit, view, search contacts) when the device is offline; all local changes are automatically synced to the remote backend once connectivity is restored, with no data loss.
- **SC-007**: 90% of first-time users can add a contact and log an interaction entry without external guidance.
- **SC-008**: Search returns relevant results across all fields (including interaction entries) within 2 seconds for a library of up to 1,000 contacts.
- **SC-009**: All contacts and interaction entries with GPS data are correctly plotted on the map view; tapping any pin opens a popup with the contact name, context label, and a working "View contact" link that navigates to the contact detail page in the same tab.

## Clarifications

### Session 2026-03-21

- Q: When the user clicks the "View contact" link in the map pin popup, should it open in the same tab or a new tab? → A: Same tab — navigate within the SPA; back button returns to the map.

### Session 2026-03-20

- Q: Should the interaction summary be a single rolling text field or multiple timestamped entries per contact? → A: Multiple dated entries per contact — one note per interaction, displayed as a chronological feed.
- Q: Where is data primarily stored — local-only, local-first with backend sync, or backend-required? → A: Local-first with backend sync — app works fully offline, syncs to remote backend when online.
- Q: When a contact is deleted, what happens to all associated data? → A: Hard delete — contact, all field history, and all interaction entries permanently removed; deletion preceded by an explicit warning that the action is irreversible.
- Q: Is user authentication required in v1? → A: Yes — users must authenticate (email/password or passkey) before accessing any data; no data exposed without an authenticated session.
- Q: Which fields should search cover, and any additional views needed? → A: Full-text search across all fields including interaction entries; contacts and interaction entries also visible on a map view via their GPS coordinates.

## Assumptions

- **Single user**: This is a personal tool used by one person; no multi-user collaboration or sharing features are in scope for this version.
- **Authentication in v1**: User authentication is required in v1. Users must authenticate (email/password or passkey) before accessing any data. The app must not expose contact data or sync to the backend without an authenticated session.
- **Local-first with backend sync**: Contacts are stored locally on the device/browser so the app is fully functional offline. When connectivity is restored, local changes are synced to a remote backend. The backend is the long-term source of truth; local storage is the operational layer.
- **No external data fetching in v1**: Integration with LinkedIn, Banque Carrefour des Entreprises, or other public data sources is explicitly deferred to a future version.
- **Mobile-first but web-based**: The webapp is designed primarily for mobile browser use (where GPS is most relevant) but must also function on desktop browsers.
- **Data export**: Exporting contacts (CSV, vCard) is a desirable future feature but not required for this version.
- **History is read-only during normal use**: Past field history and interaction entries cannot be individually edited or deleted. The only way to remove history is by deleting the entire contact, which triggers a permanent hard delete of all associated data.
- **GDPR / privacy**: As this handles personal data and GPS locations, the app must operate in compliance with GDPR principles (data minimisation, user consent, right to deletion), though detailed compliance implementation is out of scope for this spec.
