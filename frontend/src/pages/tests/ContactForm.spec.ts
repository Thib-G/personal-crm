/**
 * T030 - Unit tests for AddContactPage.vue (US1)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import AddContactPage from '../AddContactPage.vue'

vi.mock('@/services/db', () => ({
  db: {
    contacts: { put: vi.fn() },
    contact_phones: { put: vi.fn() },
    contact_emails: { put: vi.fn() },
    outbox: { add: vi.fn() },
  },
}))

vi.mock('@/services/sync', () => ({
  syncService: { addToOutbox: vi.fn(), startSync: vi.fn(), syncNow: vi.fn() },
}))

vi.mock('@/composables/useGeolocation', () => ({
  useGeolocation: vi.fn().mockResolvedValue({ lat: 50.85, lng: 4.35 }),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/contacts', component: { template: '<div/>' } },
    { path: '/contacts/new', component: AddContactPage },
  ],
})

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('AddContactPage', () => {
  it('renders name input', () => {
    const wrapper = mount(AddContactPage, {
      global: { plugins: [createPinia(), router] },
    })
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
  })

  it('shows validation error when name is empty on submit', async () => {
    const wrapper = mount(AddContactPage, {
      global: { plugins: [createPinia(), router] },
    })
    await wrapper.find('form').trigger('submit')
    expect(wrapper.text()).toContain('Name is required')
  })
})
