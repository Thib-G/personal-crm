/**
 * T007 — Router guard tests (US2 + auth-guard.md contract)
 *
 * Verifies the full guard truth table from contracts/auth-guard.md:
 *
 * | Navigating to | Auth state    | Expected action              |
 * |---------------|---------------|------------------------------|
 * | /login        | Authenticated | Redirect to /contacts        |
 * | /login        | Not authed    | Allow (render login)         |
 * | Other route   | Authenticated | Allow                        |
 * | Other route   | Not authed    | Redirect to /login           |
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const mockCheckSession = vi.fn()
const mockUser = vi.hoisted(() => ({ value: null as { id: number; username: string } | null }))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    get user() { return mockUser.value },
    checkSession: mockCheckSession,
  }),
}))

// Import router AFTER mocks are set up
const { default: router } = await import('@/router/index')

beforeEach(() => {
  setActivePinia(createPinia())
  mockUser.value = null
  mockCheckSession.mockReset()
  mockCheckSession.mockResolvedValue(undefined)
})

describe('Router guard — auth-guard.md contract', () => {
  it('redirects authenticated user away from /login to /contacts', async () => {
    mockUser.value = { id: 1, username: 'alice' }
    const result = await router.resolve('/login')
    // Navigate and capture the resolved location
    await router.push('/contacts') // reset position
    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('contacts')
  })

  it('allows unauthenticated user to access /login', async () => {
    mockUser.value = null
    mockCheckSession.mockImplementation(() => {
      // session check fails, user stays null
      return Promise.resolve()
    })
    await router.push('/contacts') // reset
    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('redirects unauthenticated user away from /contacts to /login', async () => {
    mockUser.value = null
    mockCheckSession.mockImplementation(() => Promise.resolve())
    await router.push('/login') // reset
    await router.push('/contacts')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('does not call checkSession again when user is already set', async () => {
    mockUser.value = { id: 1, username: 'alice' }
    await router.push('/login') // reset
    await router.push('/contacts')
    expect(mockCheckSession).not.toHaveBeenCalled()
    expect(router.currentRoute.value.name).toBe('contacts')
  })
})
