/**
 * ContactDetailPage tests — liveQuery reactivity (T006)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import ContactDetailPage from '../ContactDetailPage.vue'

type LiveQueryNext = (val: any) => void
const liveQuerySubscribers: LiveQueryNext[] = []

vi.mock('dexie', async (importOriginal) => {
  const actual = await importOriginal<typeof import('dexie')>()
  return {
    ...actual,
    liveQuery: vi.fn((fn: () => any) => ({
      subscribe: vi.fn(({ next }: { next: LiveQueryNext }) => {
        liveQuerySubscribers.push(next)
        fn().then(next).catch(() => {})
        return { unsubscribe: vi.fn() }
      }),
    })),
  }
})

vi.mock('@/services/db', () => ({
  db: {
    contacts: {
      get: vi.fn().mockResolvedValue(null),
      update: vi.fn(),
      orderBy: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })),
    },
    contact_phones: { where: vi.fn(() => ({ equals: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })) })) },
    contact_emails: { where: vi.fn(() => ({ equals: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })) })) },
    contact_history: { where: vi.fn(() => ({ equals: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })) })) },
    outbox: { add: vi.fn() },
  },
}))

vi.mock('@/services/sync', () => ({
  syncStatus: { value: 'synced' },
  syncService: { addToOutbox: vi.fn(), startSync: vi.fn(), syncNow: vi.fn() },
}))

vi.mock('@/components/HistoryPanel.vue', () => ({ default: { template: '<div/>' } }))
vi.mock('@/components/InteractionFeed.vue', () => ({ default: { template: '<div/>' } }))
vi.mock('@/components/AddInteractionForm.vue', () => ({ default: { template: '<div/>' } }))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/contacts/:id', component: ContactDetailPage },
    { path: '/contacts', component: { template: '<div/>' } },
  ],
})

beforeEach(async () => {
  setActivePinia(createPinia())
  liveQuerySubscribers.length = 0
  await router.push('/contacts/test-id-1')
})

describe('ContactDetailPage liveQuery reactivity', () => {
  it('shows loading state before liveQuery emits', () => {
    const wrapper = mount(ContactDetailPage, {
      global: { plugins: [createPinia(), router] },
    })
    // Before emissions, loading should be visible
    expect(wrapper.text()).toContain('Loading')
  })

  it('displays contact name from liveQuery emission', async () => {
    const wrapper = mount(ContactDetailPage, {
      global: { plugins: [createPinia(), router] },
    })

    // Wait for initial fn().then(next) microtasks to resolve first
    await new Promise((r) => setTimeout(r, 10))

    // Emit contact data via the contact page's liveQuery (index 1, after contacts store at index 0)
    if (liveQuerySubscribers[1]) {
      liveQuerySubscribers[1]({
        id: 'test-id-1',
        name: 'Bob LiveQuery',
        context_tag: 'personal',
        organisation: 'ACME',
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
        created_lat: null,
        created_lng: null,
        is_deleted: false,
      })
    }

    await new Promise((r) => setTimeout(r, 50))
    expect(wrapper.text()).toContain('Bob LiveQuery')
  })

  it('sets loading to false after first contact emission', async () => {
    const wrapper = mount(ContactDetailPage, {
      global: { plugins: [createPinia(), router] },
    })

    await new Promise((r) => setTimeout(r, 10))

    if (liveQuerySubscribers[1]) {
      liveQuerySubscribers[1]({
        id: 'test-id-1',
        name: 'Bob LiveQuery',
        context_tag: 'personal',
        organisation: null,
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
        created_lat: null,
        created_lng: null,
        is_deleted: false,
      })
    }

    await new Promise((r) => setTimeout(r, 50))
    expect(wrapper.text()).not.toContain('Loading')
  })
})
