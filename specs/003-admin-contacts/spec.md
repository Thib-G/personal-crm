# Feature Specification: Admin Contacts Management

**Feature Branch**: `003-admin-contacts`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "add contacts details management to django admin"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Browse and Search Contacts (Priority: P1)

An administrator needs to find any contact quickly across all users. They can open the contacts management section, see a paginated list of all contacts with key fields (name, owner, organisation, context tag, creation date), and use search and filters to narrow down results.

**Why this priority**: The most fundamental administrative need is being able to find and inspect records. Without this, no other admin action is possible.

**Independent Test**: Open the admin contacts section → confirm all contacts across all users are visible → search by name → filter by context tag or owner → confirm results are accurate.

**Acceptance Scenarios**:

1. **Given** the admin is logged in, **When** they open the contacts section, **Then** they see a paginated list of all contacts with name, owner, organisation, context tag, and creation date columns.
2. **Given** the contacts list is open, **When** the admin searches by name or organisation, **Then** only matching contacts are shown.
3. **Given** the contacts list is open, **When** the admin filters by context tag or owner, **Then** only contacts matching that filter are shown.
4. **Given** soft-deleted contacts exist, **When** the admin views the list, **Then** soft-deleted contacts are visible with a clear indication that they are deleted.

---

### User Story 2 — View and Edit Full Contact Details (Priority: P2)

An administrator needs to inspect or correct a contact's full profile, including their phone numbers and email addresses, without going through the end-user application. They can open a contact record and view or edit all fields, as well as add, edit, or remove phone numbers and email addresses inline.

**Why this priority**: Being able to correct data errors (wrong phone number, duplicate entries) is the second most critical admin capability after finding the record.

**Independent Test**: Open a contact's detail page → edit the name → add a phone number inline → save → confirm changes are persisted.

**Acceptance Scenarios**:

1. **Given** the admin opens a contact record, **When** they view the detail page, **Then** they see all contact fields (name, organisation, context tag, location coordinates, timestamps) and all associated phone numbers and email addresses inline.
2. **Given** the admin edits a contact's name and saves, **When** they return to the list, **Then** the updated name is reflected immediately.
3. **Given** the admin adds a phone number inline and saves, **When** they reopen the contact, **Then** the new phone number appears.
4. **Given** the admin removes a phone number inline and saves, **When** they reopen the contact, **Then** the phone number is gone.

---

### User Story 3 — Inspect Interaction and Change History (Priority: P3)

An administrator needs to audit a contact's interaction log and field change history for data quality or support purposes. They can view all interaction entries and all recorded field changes for a given contact, read-only, directly from the contact's admin page.

**Why this priority**: Audit visibility is valuable but does not block core data management tasks. It is additive.

**Independent Test**: Open a contact with existing interactions and history → confirm interaction entries are listed inline → confirm change history records (field changed, old value, new value, timestamp) are visible.

**Acceptance Scenarios**:

1. **Given** a contact has interaction entries, **When** the admin opens that contact's detail page, **Then** all interaction entries (content, date) are visible inline in read-only mode.
2. **Given** a contact has a change history, **When** the admin opens that contact's detail page, **Then** all history records (field name, old value, new value, date) are visible inline in read-only mode.
3. **Given** an admin views interactions inline, **When** they attempt to modify an interaction, **Then** the entry is read-only and no edit controls are available.

---

### Edge Cases

- What happens when a contact has no phone numbers or emails? Inline sections display as empty (zero rows) without errors.
- What happens when a contact has hundreds of interaction entries? The inline list is limited or paginated to avoid performance issues.
- How are soft-deleted contacts handled? They must be visible to admins with a clear "deleted" indicator, but restoring them is out of scope for this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Administrators MUST be able to view a paginated list of all contacts across all users, with columns for name, owner, organisation, context tag, and creation date.
- **FR-002**: Administrators MUST be able to search contacts by name and organisation from the list view.
- **FR-003**: Administrators MUST be able to filter contacts by owner and context tag.
- **FR-004**: Soft-deleted contacts MUST appear in the admin list with a clear visual indicator distinguishing them from active contacts.
- **FR-005**: Administrators MUST be able to open a contact and view all its fields on a single detail page.
- **FR-006**: Administrators MUST be able to edit contact fields (name, organisation, context tag) and save changes from the admin detail page.
- **FR-007**: Administrators MUST be able to add, edit, and remove phone numbers inline on the contact detail page.
- **FR-008**: Administrators MUST be able to add, edit, and remove email addresses inline on the contact detail page.
- **FR-009**: Interaction entries for a contact MUST be visible inline on the contact detail page in read-only mode.
- **FR-010**: Change history records for a contact MUST be visible inline on the contact detail page in read-only mode.
- **FR-011**: Access to contacts management MUST be restricted to authenticated administrators only.

### Key Entities

- **Contact**: The primary record — name, owner, organisation, context tag, coordinates, soft-delete flag, timestamps.
- **ContactPhone**: Phone number linked to a contact; multiple allowed per contact; editable inline.
- **ContactEmail**: Email address linked to a contact; multiple allowed per contact; editable inline.
- **InteractionEntry**: A log entry recording an interaction with a contact; read-only in admin.
- **ContactHistory**: An audit record of a field change on a contact; read-only in admin.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An administrator can locate any specific contact by name in under 10 seconds from the contacts list.
- **SC-002**: An administrator can correct a contact's phone number (edit inline + save) in under 60 seconds from opening the admin.
- **SC-003**: All contact records, including soft-deleted ones, are visible to administrators with 100% accuracy (no records hidden by default filters).
- **SC-004**: Interaction entries and change history are available read-only on the contact detail page with no additional navigation steps.

## Assumptions

- Only authenticated staff/superusers have access to the admin area; no changes to the existing authentication model are required.
- Soft-deleted contacts must be visible but are not restorable via the admin in this feature (restore functionality is out of scope).
- Interaction entries are read-only in admin — creation and editing of interactions remains the responsibility of the end-user application.
- Change history is system-generated and always read-only.
- The number of phone numbers and emails per contact is small enough (< 20) that all can be displayed inline without pagination.
