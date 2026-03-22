# Feature Specification: Fix Logout — Protected Routes Remain Accessible After Logout

**Feature Branch**: `007-fix-logout-guard`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "fix security bug with login: when i click on logout, it redirects to the /login page, but if i go to / or /contacts, i'm still logged"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Protected Routes Redirect to Login When Unauthenticated (Priority: P1)

After a user logs out, any attempt to navigate to a protected page (such as the contacts list, contact detail, map, or settings) must redirect them to the login page rather than showing the protected content.

**Why this priority**: This is a security vulnerability. A user who has logged out expects their session to be fully terminated. Allowing access to protected pages post-logout exposes personal data and undermines the purpose of the authentication system.

**Independent Test**: Log out, then manually type `/contacts` in the browser address bar. The app must redirect to `/login` and not display any contact data.

**Acceptance Scenarios**:

1. **Given** a user is logged out, **When** they navigate directly to `/contacts`, **Then** they are immediately redirected to the login page without seeing any contact data.
2. **Given** a user is logged out, **When** they navigate directly to `/`, **Then** they are redirected to the login page.
3. **Given** a user is logged out, **When** they use the browser back button to return to a previously visited protected page, **Then** they are redirected to the login page.
4. **Given** a user is logged out, **When** they navigate to any protected route (map, settings, contact detail), **Then** they are redirected to the login page.

---

### User Story 2 - Login Page Redirects Authenticated Users Away (Priority: P2)

A user who is already logged in should not be able to access the login page — they should be automatically sent to the contacts list.

**Why this priority**: Prevents confusion and double-login attempts. Lower priority than the security fix but important for a consistent user experience.

**Independent Test**: While logged in, manually navigate to `/login`. The app should redirect to `/contacts` without showing the login form.

**Acceptance Scenarios**:

1. **Given** a user is already authenticated, **When** they navigate to `/login`, **Then** they are redirected to `/contacts`.
2. **Given** an unauthenticated user tries to access a protected page, **When** they successfully log in, **Then** they are redirected to `/contacts`.

---

### Edge Cases

- What happens when the session expires server-side mid-use? The user should be redirected to login on their next navigation.
- What if the user's session cookie is cleared externally? Navigating to any protected route should redirect to login.
- What happens if the auth check itself fails (network error)? The user should be redirected to login rather than being granted access.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST prevent access to all protected routes when no valid session exists.
- **FR-002**: The system MUST redirect unauthenticated users to the login page when they attempt to access any protected route.
- **FR-003**: The system MUST verify authentication state before rendering any protected page — not only on initial app load, but on every navigation.
- **FR-004**: The system MUST redirect authenticated users away from the login page to the main application view.
- **FR-005**: After logout, the system MUST ensure navigating to any protected route triggers a redirect to the login page without displaying any protected content, even momentarily.
- **FR-006**: If the auth verification request fails due to a network or server error, the system MUST treat the user as unauthenticated and redirect to login.

### Key Entities

- **Session**: Represents the authenticated state of a user. Determines whether a route is accessible. Can be valid, expired, or absent.
- **Protected Route**: Any application page that requires an authenticated session (contacts list, contact detail, map, settings).
- **Public Route**: Pages accessible without authentication (login page only).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of protected routes redirect unauthenticated users to the login page — no protected content is ever rendered without a valid session.
- **SC-002**: After logout, navigating to any protected route redirects to the login page within 1 second.
- **SC-003**: Authenticated users visiting the login page are redirected to the main view with no visible flash of the login form.
- **SC-004**: No regression in existing login/logout flows — authenticated users can still access all protected routes normally.

## Assumptions

- The application has a server-side session check endpoint that can be called on each navigation to verify whether the session is still valid.
- All routes except `/login` are considered protected.
- No "remember me" or token refresh logic is in scope — this fix addresses only the missing route guard.
