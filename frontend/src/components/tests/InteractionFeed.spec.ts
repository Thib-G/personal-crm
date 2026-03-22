/**
 * InteractionFeed tests — liveQuery reactivity (T008)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import InteractionFeed from '@/components/InteractionFeed.vue'

type LiveQueryNext = (val: any) => void
let liveQuerySubscriber: LiveQueryNext | null = null

vi.mock('dexie', async (importOriginal) => {
  const actual = await importOriginal<typeof import('dexie')>()
  return {
    ...actual,
    liveQuery: vi.fn((fn: () => any) => ({
      subscribe: vi.fn(({ next }: { next: LiveQueryNext }) => {
        liveQuerySubscriber = next
        fn().then(next).catch(() => {})
        return { unsubscribe: vi.fn() }
      }),
    })),
  }
})

vi.mock('@/services/db', () => ({
  db: {
    interaction_entries: {
      where: vi.fn(() => ({
        equals: vi.fn(() => ({
          sortBy: vi.fn().mockResolvedValue([]),
        })),
      })),
    },
    outbox: { add: vi.fn() },
  },
}))

vi.mock('@/services/sync', () => ({
  syncStatus: { value: 'synced' },
  syncService: { addToOutbox: vi.fn(), startSync: vi.fn(), syncNow: vi.fn() },
}))

beforeEach(() => {
  setActivePinia(createPinia())
  liveQuerySubscriber = null
})

describe('InteractionFeed liveQuery reactivity', () => {
  it('shows empty state when no entries', async () => {
    const wrapper = mount(InteractionFeed, {
      global: { plugins: [createPinia()] },
      props: { contactId: 'contact-1' },
    })
    await new Promise((r) => setTimeout(r, 50))
    expect(wrapper.text()).toContain('No interactions')
  })

  it('renders entries emitted by liveQuery', async () => {
    const wrapper = mount(InteractionFeed, {
      global: { plugins: [createPinia()] },
      props: { contactId: 'contact-1' },
    })

    // Wait for the initial fn().then(next) microtask to resolve before pushing test data
    await new Promise((r) => setTimeout(r, 10))

    if (liveQuerySubscriber) {
      liveQuerySubscriber([
        {
          id: 'entry-1',
          contact_id: 'contact-1',
          content: 'Called to discuss project',
          created_at: '2026-01-01T10:00:00Z',
          updated_at: '2026-01-01T10:00:00Z',
          lat: null,
          lng: null,
        },
      ])
    }

    await new Promise((r) => setTimeout(r, 50))
    expect(wrapper.text()).toContain('Called to discuss project')
  })
})
