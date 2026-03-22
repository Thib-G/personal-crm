import { ref } from 'vue'
import { db } from './db'
import type { OutboxEntry } from './db'

export type SyncStatus = 'synced' | 'syncing' | 'error' | 'offline'
export const syncStatus = ref<SyncStatus>(
  typeof navigator !== 'undefined' && navigator.onLine ? 'synced' : 'offline'
)

interface MapPin {
  type: string
  id: string
  contact_id: string
  contact_name: string
  lat: number
  lng: number
  label: string
  timestamp: string
}

const LAST_SYNC_KEY = 'personal_crm_last_sync_at'

class SyncService {
  private intervalId: ReturnType<typeof setInterval> | null = null

  startSync(): void {
    window.addEventListener('online', () => {
      if (syncStatus.value === 'offline') syncStatus.value = 'synced'
      this.syncCycle()
    })
    window.addEventListener('offline', () => { syncStatus.value = 'offline' })
    this.syncCycle()
    this.intervalId = setInterval(() => {
      if (navigator.onLine) this.syncCycle()
    }, 30_000)
  }

  async addToOutbox(entry: Omit<OutboxEntry, '_seq' | 'created_at'>): Promise<void> {
    await db.outbox.add({ ...entry, created_at: new Date().toISOString() } as OutboxEntry)
  }

  syncNow(): Promise<void> {
    return this.syncCycle()
  }

  async syncCycle(): Promise<void> {
    if (syncStatus.value === 'offline') return
    syncStatus.value = 'syncing'

    try {
      const since = localStorage.getItem(LAST_SYNC_KEY) ?? '1970-01-01T00:00:00Z'

      // 1. Pull
      const pullResp = await fetch(`/api/sync/pull/?since=${encodeURIComponent(since)}`)
      if (pullResp.status === 401) {
        syncStatus.value = 'synced'
        return
      }
      if (pullResp.ok) {
        const pulled = await pullResp.json()
        await db.transaction('rw', [db.contacts, db.contact_phones, db.contact_emails, db.interaction_entries, db.contact_history], async () => {
          for (const c of pulled.contacts) {
            await db.contacts.put({ ...c, is_deleted: c.is_deleted ?? false })
          }
          for (const p of pulled.contact_phones) await db.contact_phones.put({ ...p, updated_at: new Date().toISOString() })
          for (const e of pulled.contact_emails) await db.contact_emails.put({ ...e, updated_at: new Date().toISOString() })
          for (const i of pulled.interaction_entries) await db.interaction_entries.put({ ...i, updated_at: i.updated_at ?? new Date().toISOString() })
          for (const h of pulled.contact_history) await db.contact_history.put(h)
          for (const t of pulled.tombstones) {
            if (t.entity === 'contact') await db.contacts.delete(t.id)
          }
        })
        localStorage.setItem(LAST_SYNC_KEY, pulled.server_time)
      }

      // 2. Push
      const unsynced = await db.outbox.where('synced').equals(0).toArray()
      if (unsynced.length === 0) {
        syncStatus.value = 'synced'
        return
      }

      const pushResp = await fetch('/api/sync/push/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ changes: unsynced.map((e) => ({ entity: e.entity, operation: e.operation, payload: e.payload })) }),
      })

      if (pushResp.ok) {
        const result = await pushResp.json()
        const appliedIds = new Set(result.applied.map((a: any) => a.id))
        await db.outbox.where('synced').equals(0).modify((entry) => {
          const id = (entry.payload as any).id
          if (appliedIds.has(id)) entry.synced = 1
        })
      }

      syncStatus.value = 'synced'
    } catch (e) {
      console.warn('[SyncService] sync cycle error:', e)
      syncStatus.value = navigator.onLine ? 'error' : 'offline'
    }
  }
}

function getCsrfToken(): string {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

export const syncService = new SyncService()
