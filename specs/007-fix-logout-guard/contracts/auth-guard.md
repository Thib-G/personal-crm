# Contract: Authentication Guard Behaviour

**Feature**: 007-fix-logout-guard
**Version**: 1.0

---

## Router Guard Contract

The `beforeEach` navigation guard MUST enforce the following rules on every route change:

| Navigating to | Auth state         | Action                          |
|---------------|--------------------|---------------------------------|
| `/login`      | Authenticated      | Redirect to `/contacts`         |
| `/login`      | Not authenticated  | Allow (render login form)       |
| Any other     | Authenticated      | Allow (render protected page)   |
| Any other     | Not authenticated  | Redirect to `/login`            |

**Auth state resolution**:
1. If `authStore.user` is already populated (prior navigation), use it — no server call.
2. If `authStore.user` is null, call `checkSession()` (GET `/api/auth/me/`) to determine auth state from the server before deciding.
3. If `checkSession()` fails (network error or non-2xx response), treat as not authenticated.

---

## POST /api/auth/logout/ Contract

| Property        | Value                                         |
|-----------------|-----------------------------------------------|
| Method          | POST                                          |
| Path            | `/api/auth/logout/`                           |
| Auth required   | No — callable whether or not a session exists |
| Success status  | 200                                           |
| Success body    | `{"detail": "Logged out"}`                    |
| Side effect     | Server-side session invalidated (if present)  |

**Behaviour when no session exists**: Returns 200 `{"detail": "Logged out"}` — no error.

---

## Frontend Logout Flow Contract

After a successful `POST /api/auth/logout/` (status 200):

1. Client MUST perform a full page reload to `/login` (not an in-app navigation).
2. The page reload resets all in-memory client state.
3. On the fresh load, the router guard will call `checkSession()`, which returns 401 (session invalidated), and the user remains on the login page.

After a failed `POST /api/auth/logout/` (non-200):

1. Client MUST NOT navigate away — display an error message.
2. The user's session remains active; they are still considered logged in.
