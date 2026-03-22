# Quickstart & Validation: UI Layout & Styling

**Feature**: 004-ui-layout
**Date**: 2026-03-21

---

## Prerequisites

- Dev stack running: `docker compose -f docker-compose.dev.yml up`
- Browser DevTools available for viewport simulation
- At least one contact with phones, emails, and an interaction exists in the database

---

## Scenario 1: Navigation bar (US1)

**Desktop (≥ 960px)**
1. Open `http://localhost:5173/contacts`.
2. **Verify**: Nav bar has clear visual separation between links (Contacts, Map, Settings), the sync icon, and the Logout button.
3. **Verify**: The "Contacts" link is visually highlighted (different color or weight) as the active page.
4. Navigate to `/map` and `/settings`.
5. **Verify**: Active link updates correctly on each page.

**Mobile (375px)**
1. Open DevTools → set viewport to 375×812 (iPhone).
2. **Verify**: Nav items remain accessible (either on one line or wrapping to a second line). No horizontal scroll.
3. **Verify**: All nav items are tappable (min 44px touch target height).

---

## Scenario 2: Contacts list and contact detail (US2)

**Contacts list**
1. Open `/contacts`.
2. **Verify**: Each contact row is clearly separated from the next (border, spacing, or background contrast).
3. **Verify**: Contact name is visually prominent (larger or bolder); organisation and context tag are secondary.
4. **Verify**: Context tag badge has a styled background (not plain text).
5. At 375px viewport: **Verify** the list is readable with no horizontal overflow.

**Contact detail**
1. Click on any contact.
2. **Verify**: Page has distinct named sections (phones, emails, interactions, history) with visible headings.
3. **Verify**: Edit and Delete buttons are visually prominent.
4. At 375px viewport: **Verify** sections stack vertically and remain readable.

---

## Scenario 3: Forms — Login, Add Contact, Edit Contact (US3)

**Login**
1. Log out and open `/login`.
2. **Verify**: Form is horizontally centered with comfortable padding.
3. **Verify**: Submit button is visually prominent.
4. At 375px: **Verify** form fills the screen width appropriately.

**Add Contact**
1. Open `/contacts/add`.
2. **Verify**: Form fields are labeled and vertically spaced.
3. **Verify**: Phone/email add buttons are visually distinct from the submit button.
4. Submit with an empty name field.
5. **Verify**: Error message is styled distinctly (red text or badge).

---

## Scenario 4: Map and Settings (US4)

**Map**
1. Open `/map`.
2. **Verify**: Map fills the available page area. On desktop it should be tall enough to be useful (not a thin strip). On mobile it should not push the page into scrolling unnecessarily.
3. **Verify**: No fixed pixel overflow at 375px viewport.

**Settings**
1. Open `/settings`.
2. **Verify**: The privacy toggle is clearly labeled with explanatory text.
3. **Verify**: The toggle control is styled consistently with the rest of the app (not a bare unstyled checkbox).

---

## Cross-cutting checks

- Open every page in DevTools at 375px, 640px, and 1280px. No page should require horizontal scrolling at any width.
- Confirm all existing interactions still work: adding a contact, editing, deleting, syncing, map markers, settings toggle.
- Check the sync icon colors still match the design tokens (blue for syncing, green for synced, red for error, grey for offline).
