import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { liveQuery } from 'dexie'
import { db } from '@/services/db'
import type { InteractionEntry } from '@/services/db'
import { syncService } from '@/services/sync'
import { useGeolocation } from '@/composables/useGeolocation'

export const useInteractionStore = defineStore('interactions', () => {
  const entries = ref<InteractionEntry[]>([])
  const currentContactId = ref<string | null>(null)

  let subscription: { unsubscribe: () => void } | null = null

  watch(currentContactId, (contactId) => {
    if (subscription) {
      subscription.unsubscribe()
      subscription = null
    }
    if (contactId) {
      subscription = liveQuery(() =>
        db.interaction_entries
          .where('contact_id')
          .equals(contactId)
          .sortBy('created_at')
          .then((rows) => rows.reverse()),
      ).subscribe({
        next: (rows) => {
          entries.value = rows
        },
      })
    } else {
      entries.value = []
    }
  })

  function loadForContact(contactId: string): void {
    currentContactId.value = contactId
  }

  async function createInteraction(contactId: string, content: string): Promise<void> {
    const gps = await useGeolocation()
    const id = crypto.randomUUID()
    const now = new Date().toISOString()

    const entry: InteractionEntry = {
      id,
      contact_id: contactId,
      content,
      created_at: now,
      updated_at: now,
      lat: gps?.lat ?? null,
      lng: gps?.lng ?? null,
    }

    await db.interaction_entries.add(entry)

    await syncService.addToOutbox({
      entity: 'interaction_entry',
      operation: 'create',
      payload: { ...entry },
      synced: 0,
    })
  }

  return {
    entries,
    currentContactId,
    loadForContact,
    createInteraction,
  }
})
