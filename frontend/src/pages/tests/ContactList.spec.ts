/**
 * ContactListPage tests — includes liveQuery reactivity test (T003)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import ContactListPage from '../ContactListPage.vue'

// liveQuery mock: captures the subscriber so tests can push emissions manually
let liveQuerySubscriber: ((val: any) => void) | null = null

vi.mock('dexie', async (importOriginal) => {
  const actual = await importOriginal<typeof import('dexie')>()
  return {
    ...actual,
    liveQuery: vi.fn((fn: () => any) => ({
      subscribe: vi.fn(({ next }: { next: (val: any) => void }) => {
        liveQuerySubscriber = next
        // emit initial value
        fn().then(next).catch(() => {})
        return { unsubscribe: vi.fn() }
      }),
    })),
  }
})

vi.mock('@/services/db', () => ({
  db: {
    contacts: {
      orderBy: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })),
    },
    contact_phones: { where: vi.fn(() => ({ equals: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })) })) },
    contact_emails: { where: vi.fn(() => ({ equals: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })) })) },
    outbox: { add: vi.fn() },
  },
}))

vi.mock('@/services/sync', () => ({
  syncStatus: { value: 'synced' },
  syncService: { addToOutbox: vi.fn(), startSync: vi.fn(), syncNow: vi.fn() },
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/contacts', component: ContactListPage },
    { path: '/contacts/new', component: { template: '<div/>' } },
    { path: '/contacts/:id', component: { template: '<div/>' } },
  ],
})

beforeEach(() => {
  setActivePinia(createPinia())
  liveQuerySubscriber = null
})

describe('ContactListPage', () => {
  it('renders without error', () => {
    const wrapper = mount(ContactListPage, {
      global: { plugins: [createPinia(), router] },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('shows empty state when no contacts', async () => {
    const wrapper = mount(ContactListPage, {
      global: { plugins: [createPinia(), router] },
    })
    await new Promise((r) => setTimeout(r, 50))
    expect(wrapper.text()).toContain('No contacts')
  })

  it('renders contacts emitted by liveQuery without loadContacts() being called', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    const wrapper = mount(ContactListPage, {
      global: { plugins: [pinia, router] },
    })

    // Wait for the initial fn().then(next) microtask to resolve before pushing test data
    await new Promise((r) => setTimeout(r, 10))

    // Simulate liveQuery emitting a contact list (as the sync cycle would after a pull)
    if (liveQuerySubscriber) {
      liveQuerySubscriber([
        {
          id: 'abc-123',
          name: 'Alice Reactive',
          context_tag: 'work',
          organisation: null,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          created_lat: null,
          created_lng: null,
          is_deleted: false,
        },
      ])
    }

    await new Promise((r) => setTimeout(r, 50))
    expect(wrapper.text()).toContain('Alice Reactive')
  })
})
