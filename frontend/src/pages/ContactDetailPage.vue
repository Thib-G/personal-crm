<template>
  <div class="page">
    <div v-if="loading">Loading…</div>

    <div v-else-if="!contact">
      <p>Contact not found.</p>
      <button type="button" @click="router.push('/contacts')">Back to Contacts</button>
    </div>

    <div v-else>
      <div class="page-header">
        <div>
          <h1>{{ contact.name }}</h1>
          <span class="context-tag">{{ contact.context_tag }}</span>
        </div>
        <div class="header-actions">
          <button type="button" class="btn-primary" @click="router.push(`/contacts/${contact.id}/edit`)">Edit</button>
          <button type="button" class="btn-danger" @click="confirmDelete">Delete</button>
        </div>
      </div>

      <div v-if="contact.organisation" class="organisation">
        {{ contact.organisation }}
      </div>

      <div class="added-row">
        <strong>Added</strong>
        <span class="added-date">{{ formatDate(contact.created_at) }}</span>
        <span
          v-if="contact.created_lat != null && contact.created_lng != null"
          class="added-coords"
        >
          ({{ contact.created_lat.toFixed(4) }}, {{ contact.created_lng.toFixed(4) }})
        </span>
      </div>

      <div v-if="phones.length > 0" class="section-card">
        <h2 class="section-heading">Phone Numbers</h2>
        <ul class="section-list">
          <li v-for="phone in phones" :key="phone.id">
            <a :href="`tel:${phone.number}`">{{ phone.number }}</a>
          </li>
        </ul>
      </div>

      <div v-if="emails.length > 0" class="section-card">
        <h2 class="section-heading">Email Addresses</h2>
        <ul class="section-list">
          <li v-for="email in emails" :key="email.id">
            <a :href="`mailto:${email.address}`">{{ email.address }}</a>
          </li>
        </ul>
      </div>

      <div class="section-card">
        <h2 class="section-heading">Interactions</h2>
        <AddInteractionForm :contact-id="id" class="interaction-form" />
        <InteractionFeed :contact-id="id" />
      </div>

      <div class="section-card">
        <h2 class="section-heading">Edit History</h2>
        <HistoryPanel :history="history" />
      </div>

      <div v-if="showDeleteConfirm" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="delete-dialog-title">
        <div class="modal-box">
          <h2 id="delete-dialog-title" class="modal-title">Delete Contact?</h2>
          <p>
            This will permanently delete all contact data including history and interactions.
            This cannot be undone.
          </p>
          <div class="modal-actions">
            <button type="button" @click="showDeleteConfirm = false">Cancel</button>
            <button type="button" class="btn-danger" :disabled="isDeleting" @click="handleDelete">
              {{ isDeleting ? 'Deleting…' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { liveQuery } from 'dexie'
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

const subContact = liveQuery(() => db.contacts.get(id)).subscribe({
  next: (c) => {
    contact.value = c ?? null
    loading.value = false
  },
})

const subPhones = liveQuery(() =>
  db.contact_phones.where('contact_id').equals(id).toArray(),
).subscribe({ next: (p) => { phones.value = p } })

const subEmails = liveQuery(() =>
  db.contact_emails.where('contact_id').equals(id).toArray(),
).subscribe({ next: (e) => { emails.value = e } })

const subHistory = liveQuery(() =>
  db.contact_history.where('contact_id').equals(id).toArray(),
).subscribe({ next: (h) => { history.value = h } })

onUnmounted(() => {
  subContact.unsubscribe()
  subPhones.unsubscribe()
  subEmails.unsubscribe()
  subHistory.unsubscribe()
})

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

<style scoped>
.page {
  padding: var(--space-4);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.page-header h1 {
  margin: 0 0 var(--space-1) 0;
}

.context-tag {
  font-size: var(--font-size-sm);
  background: var(--color-tag-bg);
  color: var(--color-tag-text);
  padding: 2px var(--space-2);
  border-radius: var(--radius-sm);
}

.header-actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  cursor: pointer;
  font-size: var(--font-size-base);
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

.btn-danger {
  background: var(--color-danger);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  cursor: pointer;
  font-size: var(--font-size-base);
}

.organisation {
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.added-row {
  margin-bottom: var(--space-4);
  color: var(--color-text);
}

.added-date {
  margin-left: var(--space-2);
}

.added-coords {
  margin-left: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.section-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
}

.section-heading {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin: 0 0 var(--space-3) 0;
}

.section-list {
  margin: 0;
  padding-left: var(--space-4);
}

.interaction-form {
  margin-bottom: var(--space-4);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-box {
  background: var(--color-bg);
  padding: var(--space-6);
  border-radius: var(--radius-md);
  max-width: 400px;
  width: 90%;
}

.modal-title {
  margin-top: 0;
}

.modal-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
  margin-top: var(--space-4);
}

@media (min-width: 960px) {
  .page {
    max-width: 960px;
    margin: 0 auto;
  }
}
</style>
