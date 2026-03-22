import { defineStore } from 'pinia'
import { ref } from 'vue'
import { liveQuery } from 'dexie'
import { db } from '@/services/db'
import type { Contact } from '@/services/db'
import { syncService } from '@/services/sync'

export type ContactPatchPayload = {
  name?: string
  context_tag?: string
  organisation?: string
  phones?: Array<{ id: string; number: string }>
  emails?: Array<{ id: string; address: string }>
  edit_lat?: number | null
  edit_lng?: number | null
}

type CreateContactPayload = {
  id: string
  name: string
  context_tag: string
  organisation?: string
  created_at: string
  created_lat?: number | null
  created_lng?: number | null
  phones: Array<{ id: string; number: string }>
  emails: Array<{ id: string; address: string }>
}

export const useContactStore = defineStore('contacts', () => {
  const contacts = ref<Contact[]>([])

  liveQuery(() =>
    db.contacts.orderBy('name').toArray().then((all) => all.filter((c) => !c.is_deleted)),
  ).subscribe({
    next: (result) => {
      contacts.value = result
    },
  })

  function loadContacts(): Promise<Contact[]> {
    return Promise.resolve(contacts.value)
  }

  async function createContact(payload: CreateContactPayload): Promise<void> {
    const now = new Date().toISOString()

    await db.contacts.put({
      id: payload.id,
      name: payload.name,
      context_tag: payload.context_tag as Contact['context_tag'],
      organisation: payload.organisation ?? null,
      created_at: payload.created_at,
      created_lat: payload.created_lat ?? null,
      created_lng: payload.created_lng ?? null,
      updated_at: now,
      is_deleted: false,
    })

    for (const phone of payload.phones) {
      await db.contact_phones.put({
        id: phone.id,
        contact_id: payload.id,
        number: phone.number,
        updated_at: now,
      })
    }

    for (const email of payload.emails) {
      await db.contact_emails.put({
        id: email.id,
        contact_id: payload.id,
        address: email.address,
        updated_at: now,
      })
    }

    await syncService.addToOutbox({
      entity: 'contact',
      operation: 'create',
      payload,
      synced: 0,
    })
  }

  async function updateContact(id: string, patch: ContactPatchPayload): Promise<void> {
    const now = new Date().toISOString()

    await db.contacts.update(id, {
      ...(patch.name !== undefined && { name: patch.name }),
      ...(patch.context_tag !== undefined && { context_tag: patch.context_tag as Contact['context_tag'] }),
      ...(patch.organisation !== undefined && { organisation: patch.organisation ?? null }),
      updated_at: now,
    })

    if (patch.phones !== undefined) {
      const existing = await db.contact_phones.where('contact_id').equals(id).toArray()
      const existingIds = existing.map((p) => p.id)
      const newIds = patch.phones.map((p) => p.id)

      for (const oldId of existingIds) {
        if (!newIds.includes(oldId)) {
          await db.contact_phones.delete(oldId)
        }
      }

      for (const phone of patch.phones) {
        await db.contact_phones.put({
          id: phone.id,
          contact_id: id,
          number: phone.number,
          updated_at: now,
        })
      }
    }

    if (patch.emails !== undefined) {
      const existing = await db.contact_emails.where('contact_id').equals(id).toArray()
      const existingIds = existing.map((e) => e.id)
      const newIds = patch.emails.map((e) => e.id)

      for (const oldId of existingIds) {
        if (!newIds.includes(oldId)) {
          await db.contact_emails.delete(oldId)
        }
      }

      for (const email of patch.emails) {
        await db.contact_emails.put({
          id: email.id,
          contact_id: id,
          address: email.address,
          updated_at: now,
        })
      }
    }

    await syncService.addToOutbox({
      entity: 'contact',
      operation: 'update',
      payload: { id, ...patch, updated_at: now },
      synced: 0,
    })
  }

  async function deleteContact(id: string): Promise<void> {
    const now = new Date().toISOString()

    await db.contacts.update(id, {
      is_deleted: true,
      updated_at: now,
    })

    await syncService.addToOutbox({
      entity: 'contact',
      operation: 'delete',
      payload: { id, deleted_at: now },
      synced: 0,
    })
  }

  return {
    contacts,
    loadContacts,
    createContact,
    updateContact,
    deleteContact,
  }
})
