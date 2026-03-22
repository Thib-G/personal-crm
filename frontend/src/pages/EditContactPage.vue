<template>
  <div class="page">
    <h1>Edit Contact</h1>

    <div v-if="loading">Loading…</div>

    <form v-else @submit.prevent="handleSubmit" class="form">
      <div class="field">
        <label for="name">Name *</label>
        <input id="name" v-model="name" type="text" class="input" />
        <div v-if="errors.name" class="error">{{ errors.name }}</div>
      </div>

      <div class="field">
        <label for="context_tag">Context Tag</label>
        <input id="context_tag" v-model="context_tag" type="text" class="input" />
      </div>

      <div class="field">
        <label for="organisation">Organisation</label>
        <input id="organisation" v-model="organisation" type="text" class="input" />
      </div>

      <div class="field">
        <strong>Phone Numbers</strong>
        <div v-for="(phone, index) in phones" :key="phone.id" class="dynamic-row">
          <input
            v-model="phones[index].number"
            type="tel"
            placeholder="Phone number"
            class="input input-flex"
          />
          <button type="button" class="btn-remove" @click="removePhone(index)">Remove</button>
        </div>
        <button type="button" class="btn-add" @click="addPhone">+ Add Phone</button>
      </div>

      <div class="field">
        <strong>Email Addresses</strong>
        <div v-for="(email, index) in emails" :key="email.id" class="dynamic-row">
          <input
            v-model="emails[index].address"
            type="email"
            placeholder="Email address"
            class="input input-flex"
          />
          <button type="button" class="btn-remove" @click="removeEmail(index)">Remove</button>
        </div>
        <button type="button" class="btn-add" @click="addEmail">+ Add Email</button>
      </div>

      <div v-if="errorMessage" class="error error-block">
        {{ errorMessage }}
      </div>

      <div class="form-actions">
        <button type="submit" :disabled="submitting" class="btn-primary">
          {{ submitting ? 'Saving…' : 'Save Changes' }}
        </button>
        <button type="button" class="btn-cancel" @click="router.push(`/contacts/${id}`)">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { db } from '@/services/db'
import { useContactStore } from '@/stores/contacts'
import { useGeolocation } from '@/composables/useGeolocation'

const route = useRoute()
const router = useRouter()
const contactStore = useContactStore()

const id = route.params.id as string

const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const errors = ref<{ name?: string }>({})

const name = ref('')
const context_tag = ref('')
const organisation = ref('')
const phones = ref<Array<{ id: string; number: string }>>([])
const emails = ref<Array<{ id: string; address: string }>>([])

onMounted(async () => {
  try {
    const [contact, phoneRows, emailRows] = await Promise.all([
      db.contacts.get(id),
      db.contact_phones.where('contact_id').equals(id).toArray(),
      db.contact_emails.where('contact_id').equals(id).toArray(),
    ])

    if (contact) {
      name.value = contact.name
      context_tag.value = contact.context_tag ?? ''
      organisation.value = contact.organisation ?? ''
    }

    phones.value = phoneRows.map((p) => ({ id: p.id, number: p.number }))
    emails.value = emailRows.map((e) => ({ id: e.id, address: e.address }))
  } finally {
    loading.value = false
  }
})

function addPhone() {
  phones.value.push({ id: crypto.randomUUID(), number: '' })
}

function removePhone(index: number) {
  phones.value.splice(index, 1)
}

function addEmail() {
  emails.value.push({ id: crypto.randomUUID(), address: '' })
}

function removeEmail(index: number) {
  emails.value.splice(index, 1)
}

async function handleSubmit() {
  errors.value = {}
  errorMessage.value = ''

  if (!name.value.trim()) {
    errors.value.name = 'Name is required'
    return
  }

  submitting.value = true
  try {
    const gps = await useGeolocation()

    const patch = {
      name: name.value.trim(),
      context_tag: context_tag.value.trim() || undefined,
      organisation: organisation.value.trim() || undefined,
      phones: phones.value.filter((p) => p.number.trim()),
      emails: emails.value.filter((e) => e.address.trim()),
      edit_lat: gps?.lat ?? null,
      edit_lng: gps?.lng ?? null,
    }

    await contactStore.updateContact(id, patch)
    await router.push(`/contacts/${id}`)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Failed to save contact. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page {
  padding: var(--space-4);
}

.form {
  max-width: 600px;
  margin: 0 auto;
}

.field {
  margin-bottom: var(--space-4);
}

.field label,
.field strong {
  display: block;
  margin-bottom: var(--space-1);
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  box-sizing: border-box;
}

.input-flex {
  flex: 1;
  width: auto;
}

.dynamic-row {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
  align-items: center;
}

.btn-add {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-1) var(--space-3);
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin-top: var(--space-2);
}

.btn-remove {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-1) var(--space-2);
  cursor: pointer;
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  flex-shrink: 0;
}

.error {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin-top: var(--space-1);
}

.error-block {
  margin-bottom: var(--space-3);
}

.form-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-6);
  font-size: var(--font-size-base);
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-base);
  cursor: pointer;
  color: var(--color-text-muted);
}
</style>
