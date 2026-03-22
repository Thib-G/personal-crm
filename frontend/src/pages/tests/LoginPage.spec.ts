/**
 * T004 — Tests for logout flow: hard redirect and error handling
 * Contract: specs/007-fix-logout-guard/contracts/auth-guard.md
 *
 * These tests verify:
 * (a) authStore.logout() throws when the API returns a non-OK response
 * (b) handleLogout() in App.vue uses window.location.href (not router.push)
 *     so that a full page reload resets all client state
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import App from '@/App.vue'

// ── Mocks ──────────────────────────────────────────────────────────────────

vi.mock('@/services/sync', () => ({
  syncStatus: { value: 'synced' },
  syncService: { addToOutbox: vi.fn(), startSync: vi.fn(), syncNow: vi.fn() },
}))

vi.mock('@/components/SyncStatusIcon.vue', () => ({ default: { template: '<span/>' } }))
vi.mock('@/components/SyncNowButton.vue', () => ({ default: { template: '<button/>' } }))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
    { path: '/contacts', name: 'contacts', component: { template: '<div>Contacts</div>' } },
  ],
})

// ── Auth store logout behavior ─────────────────────────────────────────────

describe('authStore.logout() error handling', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('throws when the logout API returns a non-OK response', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 }),
    )
    const authStore = useAuthStore()
    await expect(authStore.logout()).rejects.toThrow('Logout failed')
  })

  it('resolves and clears user when the logout API returns 200', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Logged out' }), { status: 200 }),
    )
    const authStore = useAuthStore()
    authStore.$patch({ user: { id: 1, username: 'alice' } } as never)
    await authStore.logout()
    expect(authStore.user).toBeNull()
  })
})

// ── App.vue handleLogout — hard redirect contract ─────────────────────────

describe('App.vue handleLogout', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('sets window.location.href to /login after successful logout', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Logged out' }), { status: 200 }),
    )

    // Capture window.location.href assignment
    const locationSpy = vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      set href(url: string) {
        locationSpy.mock.results.push({ type: 'return', value: url } as never)
      },
    })

    // Simpler approach: replace the assign/href setter via Object.defineProperty
    let capturedHref: string | null = null
    Object.defineProperty(window, 'location', {
      value: {
        ...window.location,
        set href(url: string) { capturedHref = url },
        get href() { return 'http://localhost/' },
      },
      writable: true,
      configurable: true,
    })

    const pinia = createPinia()
    setActivePinia(pinia)
    const authStore = useAuthStore()
    authStore.$patch({ user: { id: 1, username: 'alice' } } as never)

    await router.push('/contacts')
    const wrapper = mount(App, { global: { plugins: [pinia, router] } })

    const logoutBtn = wrapper.find('.nav-logout')
    await logoutBtn.trigger('click')
    await flushPromises()

    expect(capturedHref).toBe('/login')
  })
})
