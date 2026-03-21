/**
 * T040 - Unit tests for ContactListPage.vue (US2)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import ContactListPage from '../ContactListPage.vue'

vi.mock('@/services/db', () => ({
  db: {
    contacts: { orderBy: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })) },
    contact_phones: { where: vi.fn(() => ({ equals: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })) })) },
    contact_emails: { where: vi.fn(() => ({ equals: vi.fn(() => ({ toArray: vi.fn().mockResolvedValue([]) })) })) },
    outbox: { add: vi.fn() },
  },
}))

vi.mock('@/services/sync', () => ({
  syncService: { addToOutbox: vi.fn(), startSync: vi.fn() },
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
})
