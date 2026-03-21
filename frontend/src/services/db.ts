import Dexie, { type Table } from 'dexie'

export interface Contact {
  id: string
  name: string
  context_tag: 'event' | 'work' | 'personal' | 'other'
  organisation: string | null
  created_at: string
  updated_at: string
  created_lat: number | null
  created_lng: number | null
  is_deleted: boolean
}

export interface ContactPhone {
  id: string
  contact_id: string
  number: string
  updated_at: string
}

export interface ContactEmail {
  id: string
  contact_id: string
  address: string
  updated_at: string
}

export interface InteractionEntry {
  id: string
  contact_id: string
  content: string
  created_at: string
  updated_at: string
  lat: number | null
  lng: number | null
}

export interface ContactHistoryEntry {
  id: string
  contact_id: string
  field_name: string
  old_value: string | null
  new_value: string
  changed_at: string
  lat: number | null
  lng: number | null
}

export interface OutboxEntry {
  _seq?: number
  entity: 'contact' | 'contact_phone' | 'contact_email' | 'interaction_entry'
  operation: 'create' | 'update' | 'delete'
  payload: object
  synced: 0 | 1
  created_at: string
}

export interface PrivacySettings {
  id: string
  location_tracking_enabled: boolean
  updated_at: string
}

class PersonalCRMDatabase extends Dexie {
  contacts!: Table<Contact, string>
  contact_phones!: Table<ContactPhone, string>
  contact_emails!: Table<ContactEmail, string>
  interaction_entries!: Table<InteractionEntry, string>
  contact_history!: Table<ContactHistoryEntry, string>
  privacy_settings!: Table<PrivacySettings, string>
  outbox!: Table<OutboxEntry, number>

  constructor() {
    super('PersonalCRM')

    this.version(1).stores({
      contacts: '&id, name, context_tag, updated_at, is_deleted',
      contact_phones: '&id, contact_id, updated_at',
      contact_emails: '&id, contact_id, updated_at',
      interaction_entries: '&id, contact_id, created_at, updated_at',
      contact_history: '&id, contact_id, changed_at',
      privacy_settings: '&id',
      outbox: '++_seq, entity, operation, synced, created_at',
    })
  }
}

export const db = new PersonalCRMDatabase()
