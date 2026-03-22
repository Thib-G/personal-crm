/**
 * T001 / T007 - Unit tests for SyncStatusIcon.vue (US1 + US2)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import SyncStatusIcon from '@/components/SyncStatusIcon.vue'

const mockSyncStatus = vi.hoisted(() => ({
  value: 'synced' as 'synced' | 'syncing' | 'error' | 'offline',
}))

vi.mock('@/services/sync', () => ({
  syncStatus: mockSyncStatus,
  syncService: { addToOutbox: vi.fn(), startSync: vi.fn(), syncNow: vi.fn() },
}))

describe('SyncStatusIcon — icon rendering (US1)', () => {
  beforeEach(() => {
    mockSyncStatus.value = 'synced'
  })

  it('renders ✓ icon in synced state', () => {
    mockSyncStatus.value = 'synced'
    const wrapper = mount(SyncStatusIcon)
    expect(wrapper.text()).toContain('✓')
    expect(wrapper.find('.sync-spinning').exists()).toBe(false)
  })

  it('renders ↻ icon with spin class in syncing state', () => {
    mockSyncStatus.value = 'syncing'
    const wrapper = mount(SyncStatusIcon)
    expect(wrapper.text()).toContain('↻')
    expect(wrapper.find('.sync-spinning').exists()).toBe(true)
  })

  it('renders ⚠ icon in error state', () => {
    mockSyncStatus.value = 'error'
    const wrapper = mount(SyncStatusIcon)
    expect(wrapper.text()).toContain('⚠')
    expect(wrapper.find('.sync-spinning').exists()).toBe(false)
  })

  it('renders ✗ icon in offline state', () => {
    mockSyncStatus.value = 'offline'
    const wrapper = mount(SyncStatusIcon)
    expect(wrapper.text()).toContain('✗')
    expect(wrapper.find('.sync-spinning').exists()).toBe(false)
  })
})

describe('SyncStatusIcon — tooltip text (US2)', () => {
  it('shows "All data synced" title in synced state', () => {
    mockSyncStatus.value = 'synced'
    const wrapper = mount(SyncStatusIcon)
    expect(wrapper.find('span').attributes('title')).toBe('All data synced')
  })

  it('shows "Syncing…" title in syncing state', () => {
    mockSyncStatus.value = 'syncing'
    const wrapper = mount(SyncStatusIcon)
    expect(wrapper.find('span').attributes('title')).toBe('Syncing…')
  })

  it('shows "Sync failed — will retry" title in error state', () => {
    mockSyncStatus.value = 'error'
    const wrapper = mount(SyncStatusIcon)
    expect(wrapper.find('span').attributes('title')).toBe('Sync failed — will retry')
  })

  it('shows "Offline — sync paused" title in offline state', () => {
    mockSyncStatus.value = 'offline'
    const wrapper = mount(SyncStatusIcon)
    expect(wrapper.find('span').attributes('title')).toBe('Offline — sync paused')
  })
})
