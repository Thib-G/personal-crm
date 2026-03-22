/**
 * SyncNowButton tests — all 4 state contract scenarios (T010)
 * Contract: specs/006-fix-sync-ui-refresh/contracts/sync-now-button.md
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import SyncNowButton from '@/components/SyncNowButton.vue'

const mockSyncStatus = vi.hoisted(() => ({
  value: 'synced' as 'synced' | 'syncing' | 'error' | 'offline',
}))

const mockSyncNow = vi.hoisted(() => vi.fn())

vi.mock('@/services/sync', () => ({
  syncStatus: mockSyncStatus,
  syncService: {
    addToOutbox: vi.fn(),
    startSync: vi.fn(),
    syncNow: mockSyncNow,
  },
}))

beforeEach(() => {
  mockSyncStatus.value = 'synced'
  mockSyncNow.mockClear()
})

describe('SyncNowButton — state contract', () => {
  it('is enabled and calls syncNow() when status is synced', async () => {
    mockSyncStatus.value = 'synced'
    const wrapper = mount(SyncNowButton)
    const btn = wrapper.find('button')
    expect(btn.attributes('disabled')).toBeUndefined()
    await btn.trigger('click')
    expect(mockSyncNow).toHaveBeenCalledOnce()
  })

  it('is disabled and does NOT call syncNow() when status is syncing', async () => {
    mockSyncStatus.value = 'syncing'
    const wrapper = mount(SyncNowButton)
    const btn = wrapper.find('button')
    expect(btn.attributes('disabled')).toBeDefined()
    await btn.trigger('click')
    expect(mockSyncNow).not.toHaveBeenCalled()
  })

  it('is disabled when status is offline', async () => {
    mockSyncStatus.value = 'offline'
    const wrapper = mount(SyncNowButton)
    const btn = wrapper.find('button')
    expect(btn.attributes('disabled')).toBeDefined()
    await btn.trigger('click')
    expect(mockSyncNow).not.toHaveBeenCalled()
  })

  it('is enabled and calls syncNow() when status is error', async () => {
    mockSyncStatus.value = 'error'
    const wrapper = mount(SyncNowButton)
    const btn = wrapper.find('button')
    expect(btn.attributes('disabled')).toBeUndefined()
    await btn.trigger('click')
    expect(mockSyncNow).toHaveBeenCalledOnce()
  })

  it('has aria-label="Sync now"', () => {
    const wrapper = mount(SyncNowButton)
    expect(wrapper.find('button').attributes('aria-label')).toBe('Sync now')
  })
})
