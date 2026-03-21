<template>
  <div>
    <h1>Edit Contact</h1>

    <div v-if="loading">Loading…</div>

    <form v-else @submit.prevent="handleSubmit">
      <div style="margin-bottom: 12px;">
        <label for="name">Name *</label><br />
        <input id="name" v-model="name" type="text" style="width: 100%; max-width: 400px;" />
        <div v-if="errors.name" style="color: red; font-size: 0.9em; margin-top: 4px;">
          {{ errors.name }}
        </div>
      </div>

      <div style="margin-bottom: 12px;">
        <label for="context_tag">Context Tag</label><br />
        <input id="context_tag" v-model="context_tag" type="text" style="width: 100%; max-width: 400px;" />
      </div>

      <div style="margin-bottom: 12px;">
        <label for="organisation">Organisation</label><br />
        <input id="organisation" v-model="organisation" type="text" style="width: 100%; max-width: 400px;" />
      </div>

      <div style="margin-bottom: 12px;">
        <strong>Phone Numbers</strong>
        <div v-for="(phone, index) in phones" :key="phone.id" style="display: flex; gap: 8px; margin-top: 4px;">
          <input
            v-model="phones[index].number"
            type="tel"
            placeholder="Phone number"
            style="flex: 1; max-width: 360px;"
          />
          <button type="button" @click="removePhone(index)">Remove</button>
        </div>
        <button type="button" style="margin-top: 8px;" @click="addPhone">+ Add Phone</button>
      </div>

      <div style="margin-bottom: 12px;">
        <strong>Email Addresses</strong>
        <div v-for="(email, index) in emails" :key="email.id" style="display: flex; gap: 8px; margin-top: 4px;">
          <input
            v-model="emails[index].address"
            type="email"
            placeholder="Email address"
            style="flex: 1; max-width: 360px;"
          />
          <button type="button" @click="removeEmail(index)">Remove</button>
        </div>
        <button type="button" style="margin-top: 8px;" @click="addEmail">+ Add Email</button>
      </div>

      <div v-if="errorMessage" style="color: red; margin-bottom: 12px;">
        {{ errorMessage }}
      </div>

      <div style="display: flex; gap: 8px;">
        <button type="submit" :disabled="submitting">
          {{ submitting ? 'Saving…' : 'Save Changes' }}
        </button>
        <button type="button" @click="router.push(`/contacts/${id}`)">Cancel</button>
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
