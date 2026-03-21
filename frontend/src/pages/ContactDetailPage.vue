<template>
  <div>
    <div v-if="loading">Loading…</div>

    <div v-else-if="!contact">
      <p>Contact not found.</p>
      <button type="button" @click="router.push('/contacts')">Back to Contacts</button>
    </div>

    <div v-else>
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
          <h1>{{ contact.name }}</h1>
          <span style="font-size: 0.85em; background: #eee; padding: 2px 8px; border-radius: 4px;">
            {{ contact.context_tag }}
          </span>
        </div>
        <div style="display: flex; gap: 8px;">
          <button type="button" @click="router.push(`/contacts/${contact.id}/edit`)">Edit</button>
          <button type="button" @click="confirmDelete">Delete</button>
        </div>
      </div>

      <div v-if="contact.organisation" style="margin-top: 8px; color: #555;">
        {{ contact.organisation }}
      </div>

      <div style="margin-top: 16px;">
        <strong>Added</strong>
        <span style="margin-left: 8px;">{{ formatDate(contact.created_at) }}</span>
        <span
          v-if="contact.created_lat != null && contact.created_lng != null"
          style="margin-left: 8px; font-size: 0.85em; color: #888;"
        >
          ({{ contact.created_lat.toFixed(4) }}, {{ contact.created_lng.toFixed(4) }})
        </span>
      </div>

      <div v-if="phones.length > 0" style="margin-top: 16px;">
        <strong>Phone Numbers</strong>
        <ul style="margin: 4px 0 0 0; padding-left: 20px;">
          <li v-for="phone in phones" :key="phone.id">
            <a :href="`tel:${phone.number}`">{{ phone.number }}</a>
          </li>
        </ul>
      </div>

      <div v-if="emails.length > 0" style="margin-top: 16px;">
        <strong>Email Addresses</strong>
        <ul style="margin: 4px 0 0 0; padding-left: 20px;">
          <li v-for="email in emails" :key="email.id">
            <a :href="`mailto:${email.address}`">{{ email.address }}</a>
          </li>
        </ul>
      </div>

      <div style="margin-top: 32px;">
        <h2>Interactions</h2>
        <AddInteractionForm :contact-id="id" style="margin-bottom: 16px;" />
        <InteractionFeed :contact-id="id" />
      </div>

      <div style="margin-top: 32px;">
        <h2>Edit History</h2>
        <HistoryPanel :history="history" />
      </div>

      <div v-if="showDeleteConfirm" role="dialog" aria-modal="true" aria-labelledby="delete-dialog-title" style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100;">
        <div style="background: #fff; padding: 24px; border-radius: 8px; max-width: 400px; width: 90%;">
          <h2 id="delete-dialog-title" style="margin-top: 0;">Delete Contact?</h2>
          <p>
            This will permanently delete all contact data including history and interactions.
            This cannot be undone.
          </p>
          <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px;">
            <button type="button" @click="showDeleteConfirm = false">Cancel</button>
            <button type="button" :disabled="isDeleting" @click="handleDelete" style="color: red;">
              {{ isDeleting ? 'Deleting…' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { db } from '@/services/db'
import type { Contact, ContactPhone, ContactEmail, ContactHistoryEntry } from '@/services/db'
import { useContactStore } from '@/stores/contacts'
import HistoryPanel from '@/components/HistoryPanel.vue'
import InteractionFeed from '@/components/InteractionFeed.vue'
import AddInteractionForm from '@/components/AddInteractionForm.vue'

const route = useRoute()
const router = useRouter()
const contactStore = useContactStore()

const id = route.params.id as string

const loading = ref(true)
const contact = ref<Contact | null>(null)
const phones = ref<ContactPhone[]>([])
const emails = ref<ContactEmail[]>([])
const history = ref<ContactHistoryEntry[]>([])

const showDeleteConfirm = ref(false)
const isDeleting = ref(false)

onMounted(async () => {
  await loadContact()
})

async function loadContact() {
  loading.value = true
  try {
    const [c, p, e, h] = await Promise.all([
      db.contacts.get(id),
      db.contact_phones.where('contact_id').equals(id).toArray(),
      db.contact_emails.where('contact_id').equals(id).toArray(),
      db.contact_history.where('contact_id').equals(id).toArray(),
    ])
    contact.value = c ?? null
    phones.value = p
    emails.value = e
    history.value = h
  } finally {
    loading.value = false
  }
}

function formatDate(isoString: string): string {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
}

function confirmDelete() {
  showDeleteConfirm.value = true
}

async function handleDelete() {
  isDeleting.value = true
  try {
    await contactStore.deleteContact(id)
    await router.push('/contacts')
  } finally {
    isDeleting.value = false
    showDeleteConfirm.value = false
  }
}
</script>
