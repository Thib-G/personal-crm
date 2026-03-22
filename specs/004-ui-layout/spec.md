# Feature Specification: UI Layout & Styling

**Feature Branch**: `004-ui-layout`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "improve layout using css based styling"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Consistent Navigation and Global Shell (Priority: P1)

The user opens the app on any page and immediately sees a polished, consistent navigation bar. The navigation clearly identifies the app, shows the available sections, and the sync status icon and logout button are visually distinct from the navigation links.

**Why this priority**: The navigation bar appears on every page. It is the most impactful surface to improve — a polished shell makes the entire app feel more cohesive regardless of which page the user is on.

**Independent Test**: Open the app on any page (Contacts, Map, Settings) → confirm the navigation bar looks consistent, readable, and visually organized across all pages.

**Acceptance Scenarios**:

1. **Given** the user is on any page, **When** they look at the navigation, **Then** the navigation links, sync icon, and logout button are clearly separated and easy to distinguish.
2. **Given** the user navigates between pages, **When** they observe the navigation bar, **Then** the active page link is visually highlighted to indicate current location.
3. **Given** the user is on any page, **When** they view the page on a mobile screen or a desktop browser, **Then** the content does not overflow, require horizontal scrolling, or appear cut off at any viewport width.

---

### User Story 2 — Readable Contacts List and Contact Detail (Priority: P2)

The user browses their contacts and opens a contact record. The list is scannable with clear visual separation between entries. The contact detail page organizes information into distinct sections (personal info, phones, emails, interactions, history) that are easy to navigate without scrolling through a wall of unstyled text.

**Why this priority**: Contacts are the core of the app. Making the list and detail pages legible is the highest-value content improvement after the navigation shell.

**Independent Test**: Open the contacts list → confirm entries are visually separated and readable → click a contact → confirm the detail page has clear visual sections for each type of information.

**Acceptance Scenarios**:

1. **Given** the contacts list has multiple entries, **When** the user scans the list, **Then** each contact is clearly delimited and key information (name, organisation, context tag) is easy to read at a glance.
2. **Given** the user opens a contact detail page, **When** they view the page, **Then** the contact's phones, emails, interactions, and history each appear as visually distinct sections with clear headings.
3. **Given** the user is on the contact detail page, **When** they look for actions (edit, delete, add interaction), **Then** the action buttons are visually prominent and easy to identify.
4. **Given** a contact has a context tag badge, **When** the user views the contact, **Then** the badge is styled consistently with a visible background and readable text.

---

### User Story 3 — Polished Forms: Login, Add/Edit Contact (Priority: P3)

The user logs in or creates/edits a contact. The forms feel clean and structured: inputs are clearly labeled, error messages are visible, and the submit action is obvious. The login page is centered and welcoming rather than raw HTML.

**Why this priority**: Forms are used less frequently than browsing but are critical interaction points. Poor form layout causes errors and frustration. This comes after content readability.

**Independent Test**: Open the login page → confirm the form is centered and readable → open the Add Contact page → confirm the form has clear field groupings and a visible submit button.

**Acceptance Scenarios**:

1. **Given** the user opens the login page, **When** they view it, **Then** the form is centered on the page with comfortable spacing and a visible submit button.
2. **Given** the user opens the Add Contact or Edit Contact form, **When** they view the form, **Then** related fields (phones, emails) are grouped visually and adding/removing entries is clearly indicated.
3. **Given** the user submits a form with validation errors, **When** the errors appear, **Then** error messages are visually distinct (e.g., different color or icon) and positioned near the relevant field.

---

### User Story 4 — Map and Settings Pages (Priority: P4)

The map page and settings page match the visual style of the rest of the app. The map takes up appropriate space and is not constrained by an arbitrary fixed height. The settings page presents options clearly without feeling like a bare checkbox.

**Why this priority**: These pages are used less frequently but should not feel visually inconsistent with the rest of the app. They are the lowest priority since their core functionality is unaffected by current styling.

**Independent Test**: Open the Map page → confirm the map is appropriately sized and visually integrated with the page → open the Settings page → confirm the privacy toggle is clearly labeled and styled consistently.

**Acceptance Scenarios**:

1. **Given** the user opens the Map page, **When** they view it, **Then** the map fills the available content area without being cut off or leaving excessive empty space.
2. **Given** the user opens the Settings page, **When** they view the privacy toggle, **Then** the option is clearly labeled with a description and the control is easy to interact with.

---

### Edge Cases

- What happens when a contact's name is very long? Text should truncate or wrap gracefully without breaking the list layout.
- What happens on a narrow mobile screen (320px–480px wide)? All content must remain usable and readable without horizontal scrolling.
- What happens when the contacts list is empty? The empty state should be clearly communicated rather than displaying a blank area.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The navigation bar MUST display a visually distinct active state for the currently selected page.
- **FR-002**: Each page MUST have a consistent visual structure: a page heading, a content area, and clearly styled action controls.
- **FR-003**: The contacts list MUST display each contact as a visually separated row with clear hierarchy (name prominent, secondary info smaller).
- **FR-004**: The contact detail page MUST organize content into named sections (contact info, phones, emails, interactions, history), each visually distinct from the others.
- **FR-005**: All interactive controls (buttons, links) MUST be visually distinguishable from non-interactive content through consistent styling.
- **FR-006**: Error messages and status feedback MUST be visually distinct from regular content (different color or weight).
- **FR-007**: The login form MUST be visually centered and comfortable to use on a standard desktop browser.
- **FR-008**: The map MUST fill the available content area without relying on a fixed pixel height.
- **FR-009**: All pages MUST maintain visual consistency — same fonts, spacing rhythm, and color palette throughout the app.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every page of the app has a visible `<style>` section with named classes — no page relies solely on per-element inline styles for layout or spacing.
- **SC-002**: A first-time visitor can identify the navigation structure, the current page, and the primary action on each page within 5 seconds of opening it.
- **SC-003**: All 4 user stories can be independently verified by visual inspection with no functional regressions — all existing features continue to work after styling is applied.
- **SC-004**: The contacts list, contact detail, and form pages read as visually cohesive — a consistent color palette, spacing scale, and typographic hierarchy are applied across all pages.

## Assumptions

- Mobile-first: layouts are designed for small screens (≥ 320px) as the baseline and scale up gracefully to desktop (≥ 960px). Touch targets must be comfortably tappable on mobile.
- Dark mode is out of scope.
- The existing functional behavior of all pages is preserved exactly — this feature touches only visual presentation, not logic.
- A neutral, clean aesthetic is assumed (no strong brand color palette specified); colors will be drawn from a simple gray/blue palette.
- The map's external library styling (Leaflet) is not modified; only the surrounding page layout is improved.
