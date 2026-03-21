import { defineStore } from 'pinia'
import { ref } from 'vue'
import { db } from '@/services/db'
import type { InteractionEntry } from '@/services/db'
import { syncService } from '@/services/sync'
import { useGeolocation } from '@/composables/useGeolocation'

export const useInteractionStore = defineStore('interactions', () => {
  const entries = ref<InteractionEntry[]>([])
  const currentContactId = ref<string | null>(null)

  async function loadForContact(contactId: string): Promise<void> {
    const rows = await db.interaction_entries
      .where('contact_id')
      .equals(contactId)
      .sortBy('created_at')
    entries.value = rows.reverse()
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

    await loadForContact(contactId)
  }

  return {
    entries,
    currentContactId,
    loadForContact,
    createInteraction,
  }
})
