---
description: "Task list for 007-fix-logout-guard"
---

# Tasks: Fix Logout — Route Guard and Session Invalidation

**Input**: Design documents from `/specs/007-fix-logout-guard/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, contracts/ ✅

**Tests**: TDD is MANDATORY per constitution. Test tasks appear before their corresponding implementation tasks. Tests must be written first and must fail before implementation begins.

**Organization**: US1 (protected routes block unauthenticated access) and US2 (login page redirects authenticated users) share the same guard file but are independently testable. The backend fix is a prerequisite for US1 to be fully verifiable end-to-end.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

No new packages or project structure changes required. All files already exist.

- [x] T001 Read and understand the current router guard in `frontend/src/router/index.ts` and the auth store in `frontend/src/stores/auth.ts` to confirm the exact failure mode before making changes

**Checkpoint**: Root cause confirmed — guard calls `checkSession()` after logout, which re-authenticates from a still-valid server session because the backend logout endpoint's inherited `auth=django_auth` can silently fail.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fix the backend so the server session is reliably invalidated on logout. US1 cannot be considered fully fixed end-to-end until this is complete.

**⚠️ CRITICAL**: The frontend fix alone (hard redirect) prevents re-authentication on subsequent SPAnavigations, but does not close the window where the server session remains alive. Fix the backend first.

### Tests for Phase 2

> **Write this test FIRST — it must FAIL before T003 is implemented**

- [x] T002 Write a failing backend test in `backend/users/tests/test_auth_contract.py` that asserts: `POST /api/auth/logout/` called WITHOUT an active session still returns 200 (not 401) — confirm the current behaviour returns 401 (test fails), then implement the fix

### Implementation for Phase 2

- [x] T003 Add `auth=None` to the logout endpoint in `backend/users/router.py` so it is callable regardless of whether a session exists: change `@router.post("/logout/")` to `@router.post("/logout/", auth=None)` — Django's `logout()` is a safe no-op when called with no active session

**Checkpoint**: `POST /api/auth/logout/` now returns 200 whether or not a session cookie is present. T002 test passes.

---

## Phase 3: User Story 1 — Protected Routes Redirect to Login When Unauthenticated (Priority: P1) 🎯 MVP

**Goal**: After logout, navigating to any protected route sends the user to `/login` with no protected content shown — even across in-app navigations within the same SPA session.

**Independent Test**: Log out, then navigate in-app to `/contacts`. The guard must redirect to `/login` without rendering any contact data.

### Tests for User Story 1

> **Write these tests FIRST — they must FAIL before T005–T006 are implemented**

- [x] T004 Write failing tests covering the guard's post-logout behaviour: create or update `frontend/src/pages/tests/LoginPage.spec.ts` with tests that assert: (a) after `authStore.logout()` is called, navigating to `/contacts` triggers a redirect to `/login`; (b) the logout function calls `window.location.href` (not `router.push`) — mock `window.location` in the test to capture this

### Implementation for User Story 1

- [x] T005 [US1] Update `frontend/src/stores/auth.ts` `logout()` function to check the response status of the logout fetch and throw an error if the API call fails (prevents silent session retention when the server call fails): `if (!response.ok) throw new Error('Logout failed')`
- [x] T006 [US1] Update `frontend/src/App.vue` `handleLogout()` to use `window.location.href = '/login'` instead of `router.push('/login')` after a successful logout — this triggers a full page reload, clearing all Pinia state and forcing a fresh session check on the next navigation; add error handling to show a message if logout fails

**Checkpoint**: After logout, navigating to any protected route (including via browser address bar or in-app link) redirects to login. T004 tests pass.

---

## Phase 4: User Story 2 — Login Page Redirects Authenticated Users Away (Priority: P2)

**Goal**: An already-authenticated user who navigates to `/login` is immediately redirected to `/contacts` without seeing the login form.

**Independent Test**: While logged in, navigate to `/login`. The app must redirect to `/contacts` without rendering the login form.

### Tests for User Story 2

> **Write this test FIRST — it must FAIL before T008 is implemented**

- [x] T007 [US2] Write a failing test in `frontend/src/router/tests/router.spec.ts` (create file if it does not exist) that asserts: when `authStore.user` is set (authenticated) and the guard runs for a navigation to `/login`, the guard returns `{ name: 'contacts' }` instead of `true`

### Implementation for User Story 2

- [x] T008 [US2] Update the `beforeEach` guard in `frontend/src/router/index.ts` to redirect authenticated users away from `/login`: after resolving auth state (calling `checkSession()` if needed), if `authStore.user` is set AND `to.name === 'login'`, return `{ name: 'contacts' }`; consolidate the guard logic per the contract in `contracts/auth-guard.md`

**Checkpoint**: Authenticated users visiting `/login` are redirected to `/contacts`. T007 test passes. The complete guard truth table from the contract is satisfied.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T009 [P] Run the full backend test suite (`cd backend && pytest`) and confirm all tests pass with no regressions — specifically verify `test_auth_contract.py` and any existing auth tests
- [x] T010 [P] Run the full frontend test suite (`cd frontend && npm run test`) and confirm all tests pass with no regressions — verify T004 and T007 pass and no existing tests are broken

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — the backend fix is a prerequisite for a fully closed security hole
- **US1 (Phase 3)**: Depends on Phase 2 — the frontend hard-redirect fix works independently but the backend fix should be in place first
- **US2 (Phase 4)**: Independent of US1 — can be implemented in parallel with Phase 3 since it touches a different part of the guard
- **Polish (Phase 5)**: Depends on all phases above

### User Story Dependencies

- **US1 (P1)**: Requires Phase 2 complete (backend fix)
- **US2 (P2)**: Independent — only touches `router/index.ts`; can proceed after Phase 1

### Within Each User Story

- Tests MUST be written and FAIL before implementation begins (constitution V)
- Backend fix (T003) before frontend logout fix (T005–T006) for end-to-end correctness

### Parallel Opportunities

- T007 (US2 test) and T004 (US1 test) can be written in parallel after Phase 1 — different files
- T008 (US2 impl) and T005–T006 (US1 impl) can be worked in parallel — T008 touches only `router/index.ts`, T005–T006 touch `auth.ts` and `App.vue`
- T009 and T010 (Polish) can run in parallel — different test suites

---

## Parallel Example: Writing Tests First

```bash
# After T001 (setup read), write all failing tests in parallel:
T002: backend/users/tests/test_auth_contract.py   # logout-without-session returns 200
T004: frontend/src/pages/tests/LoginPage.spec.ts  # hard-redirect after logout
T007: frontend/src/router/tests/router.spec.ts    # guard redirects auth users from /login
```

---

## Implementation Strategy

### MVP First (User Story 1 — security fix)

1. T001 — Confirm the failure mode
2. T002 — Write failing backend test
3. T003 — Fix backend logout endpoint
4. T004 — Write failing frontend logout test
5. T005–T006 — Fix frontend logout (auth store + App.vue)
6. **STOP AND VALIDATE**: Log out, navigate to `/contacts`, confirm redirect to `/login` ✅

### Incremental Delivery

1. T001–T003 → Backend session reliably invalidated
2. T004–T006 → Frontend hard-reloads on logout, US1 fully closed
3. T007–T008 → US2 login-page redirect for authenticated users
4. T009–T010 → Full test suite green

---

## Notes

- The `window.location.href = '/login'` approach (T006) is intentional: it resets ALL in-memory state, which is the only reliable way to prevent stale Pinia stores from bypassing the guard on subsequent in-app navigations.
- `auth=None` on the logout endpoint (T003) is safe: `django.contrib.auth.logout()` is a no-op when no session is active.
- The guard consolidation in T008 must satisfy the full truth table in `contracts/auth-guard.md` — not just the US2 redirect case.
