# Research: Fix Logout — Route Guard and Session Invalidation

**Branch**: `007-fix-logout-guard`
**Date**: 2026-03-22

---

## Decision 1: Logout endpoint auth requirement

**Decision**: Remove the inherited `auth=django_auth` from the logout endpoint by explicitly setting `auth=None`.

**Rationale**: The logout endpoint currently inherits the global `auth=django_auth` requirement. If the Ninja auth check fails for any reason (e.g., session cookie not sent, expired session), the endpoint returns 401 and `django.contrib.auth.logout()` is never called. Setting `auth=None` makes logout always callable — calling it with no active session is harmless (Django's `logout()` is a no-op when the user is not authenticated), and it removes a silent failure mode.

**Alternatives considered**:
- Keep `auth=django_auth` and handle 401 on the frontend: fragile — any auth issue would still prevent logout from working.
- Add explicit CSRF handling: unnecessary, Django-Ninja defaults to `csrf=False` for API endpoints.

---

## Decision 2: Frontend state reset after logout

**Decision**: After a successful logout API call, perform a full page reload via `window.location.href = '/login'` instead of an in-app `router.push('/login')`.

**Rationale**: An in-app navigation after logout preserves all Pinia store state in memory. When the router guard runs for a subsequent protected-route navigation, `authStore.user` is null and `checkSession()` is called. If the server session was not properly invalidated, `checkSession()` re-authenticates the user transparently. A full page reload resets all client-side state (Pinia stores, component state) and forces a fresh session verification on the next navigation. This is the standard pattern for SPA logout.

**Alternatives considered**:
- Clear all Pinia stores manually on logout: brittle — every new store must be remembered and explicitly cleared.
- Add a `isLoggedOut` flag to the auth store: the flag would survive in-app navigation but not a page reload, creating inconsistent behavior.
- Always call `checkSession()` on every navigation (skip the `if (!authStore.user)` check): would work but adds one server round-trip to every navigation, degrading perceived performance.

---

## Decision 3: Router guard — redirect authenticated users away from `/login`

**Decision**: Update the `beforeEach` guard to check whether the user is already authenticated before serving the login page, and redirect to `/contacts` if so.

**Rationale**: Currently the guard returns `true` for any navigation to `/login` without checking auth state. An already-logged-in user who types `/login` in the address bar (or is redirected there by stale bookmarks) sees the login page. This is confusing and could enable duplicate logins. The fix adds an authenticated-user redirect to `/login` using the same guard, keeping the logic in one place.

**Alternatives considered**:
- Handle this in `LoginPage.vue` with `onMounted`: works but scatters auth logic across files; the router is the canonical place for navigation guards.

---

## Decision 4: No changes to `checkSession()` logic

**Decision**: The `checkSession()` function in `auth.ts` is correct as-is and does not need changes.

**Rationale**: It already handles the 401 case correctly (sets `user.value = null`). The bug is upstream (server session not invalidated + stale Pinia state), not in `checkSession()` itself.

---

## Files Changed

| File | Change |
|------|--------|
| `backend/users/router.py` | Add `auth=None` to the logout endpoint |
| `frontend/src/pages/LoginPage.vue` | Replace `router.push('/login')` with `window.location.href = '/login'` after logout |
| `frontend/src/router/index.ts` | Fix guard: redirect authenticated users away from `/login`; consolidate guard logic |
| `backend/users/tests/test_auth_contract.py` | Add/update tests for the logout endpoint (no-auth case, session invalidation) |
| `frontend/src/pages/tests/LoginPage.spec.ts` | Add test for the post-logout navigation behavior (new file if not exists) |
