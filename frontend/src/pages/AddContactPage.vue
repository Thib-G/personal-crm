<template>
  <div>
    <h1>Add Contact</h1>

    <form @submit.prevent="handleSubmit">
      <div>
        <label for="name">Name <span aria-hidden="true">*</span></label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          placeholder="Full name"
          autocomplete="off"
        />
        <span v-if="errors.name" role="alert" style="color: red;">{{ errors.name }}</span>
      </div>

      <div>
        <label for="context_tag">Context</label>
        <select id="context_tag" v-model="form.context_tag">
          <option value="event">Event</option>
          <option value="work">Work</option>
          <option value="personal">Personal</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label for="organisation">Organisation</label>
        <input
          id="organisation"
          v-model="form.organisation"
          type="text"
          placeholder="Company or organisation (optional)"
          autocomplete="off"
        />
      </div>

      <fieldset>
        <legend>Phone Numbers</legend>
        <div
          v-for="(phone, index) in form.phones"
          :key="index"
          style="display: flex; gap: 8px; margin-bottom: 4px;"
        >
          <input
            v-model="phone.number"
            type="tel"
            :placeholder="`Phone ${index + 1}`"
            :aria-label="`Phone number ${index + 1}`"
          />
          <button type="button" @click="removePhone(index)">Remove</button>
        </div>
        <button type="button" @click="addPhone">Add Phone</button>
      </fieldset>

      <fieldset>
        <legend>Email Addresses</legend>
        <div
          v-for="(email, index) in form.emails"
          :key="index"
          style="display: flex; gap: 8px; margin-bottom: 4px;"
        >
          <input
            v-model="email.address"
            type="email"
            :placeholder="`Email ${index + 1}`"
            :aria-label="`Email address ${index + 1}`"
          />
          <button type="button" @click="removeEmail(index)">Remove</button>
        </div>
        <button type="button" @click="addEmail">Add Email</button>
      </fieldset>

      <div>
        <label for="interaction_note">First Interaction Note</label>
        <textarea
          id="interaction_note"
          v-model="form.interactionNote"
          placeholder="Optional note about how you met or context for this contact"
          rows="3"
        />
      </div>

      <div v-if="submitError" role="alert" style="color: red; margin-top: 8px;">
        {{ submitError }}
      </div>

      <div style="margin-top: 16px;">
        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving…' : 'Save Contact' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useContactStore } from '@/stores/contacts'
import { useGeolocation } from '@/composables/useGeolocation'

const router = useRouter()
const contactStore = useContactStore()

const form = reactive({
  name: '',
  context_tag: 'other',
  organisation: '',
  phones: [] as Array<{ number: string }>,
  emails: [] as Array<{ address: string }>,
  interactionNote: '',
})

const errors = reactive({
  name: '',
})

const isSubmitting = ref(false)
const submitError = ref('')

function addPhone() {
  form.phones.push({ number: '' })
}

function removePhone(index: number) {
  form.phones.splice(index, 1)
}

function addEmail() {
  form.emails.push({ address: '' })
}

function removeEmail(index: number) {
  form.emails.splice(index, 1)
}

function validate(): boolean {
  errors.name = ''
  if (!form.name.trim()) {
    errors.name = 'Name is required'
    return false
  }
  return true
}

async function handleSubmit() {
  submitError.value = ''

  if (!validate()) return

  isSubmitting.value = true

  try {
    const coords = await useGeolocation()

    const contactId = crypto.randomUUID()

    const phones = form.phones
      .filter((p) => p.number.trim() !== '')
      .map((p) => ({ id: crypto.randomUUID(), number: p.number.trim() }))

    const emails = form.emails
      .filter((e) => e.address.trim() !== '')
      .map((e) => ({ id: crypto.randomUUID(), address: e.address.trim() }))

    await contactStore.createContact({
      id: contactId,
      name: form.name.trim(),
      context_tag: form.context_tag,
      organisation: form.organisation.trim() || undefined,
      created_at: new Date().toISOString(),
      created_lat: coords?.lat ?? null,
      created_lng: coords?.lng ?? null,
      phones,
      emails,
    })

    await router.push('/contacts')
  } catch (err) {
    submitError.value =
      err instanceof Error ? err.message : 'An unexpected error occurred. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
