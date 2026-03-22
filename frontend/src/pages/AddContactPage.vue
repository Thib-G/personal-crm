<template>
  <div class="page">
    <h1>Add Contact</h1>

    <form @submit.prevent="handleSubmit" class="form">
      <div class="field">
        <label for="name">Name <span aria-hidden="true">*</span></label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          placeholder="Full name"
          autocomplete="off"
          class="input"
        />
        <span v-if="errors.name" role="alert" class="error">{{ errors.name }}</span>
      </div>

      <div class="field">
        <label for="context_tag">Context</label>
        <select id="context_tag" v-model="form.context_tag" class="input">
          <option value="event">Event</option>
          <option value="work">Work</option>
          <option value="personal">Personal</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="field">
        <label for="organisation">Organisation</label>
        <input
          id="organisation"
          v-model="form.organisation"
          type="text"
          placeholder="Company or organisation (optional)"
          autocomplete="off"
          class="input"
        />
      </div>

      <fieldset class="fieldset">
        <legend>Phone Numbers</legend>
        <div
          v-for="(phone, index) in form.phones"
          :key="index"
          class="dynamic-row"
        >
          <input
            v-model="phone.number"
            type="tel"
            :placeholder="`Phone ${index + 1}`"
            :aria-label="`Phone number ${index + 1}`"
            class="input input-flex"
          />
          <button type="button" class="btn-remove" @click="removePhone(index)">Remove</button>
        </div>
        <button type="button" class="btn-add" @click="addPhone">Add Phone</button>
      </fieldset>

      <fieldset class="fieldset">
        <legend>Email Addresses</legend>
        <div
          v-for="(email, index) in form.emails"
          :key="index"
          class="dynamic-row"
        >
          <input
            v-model="email.address"
            type="email"
            :placeholder="`Email ${index + 1}`"
            :aria-label="`Email address ${index + 1}`"
            class="input input-flex"
          />
          <button type="button" class="btn-remove" @click="removeEmail(index)">Remove</button>
        </div>
        <button type="button" class="btn-add" @click="addEmail">Add Email</button>
      </fieldset>

      <div class="field">
        <label for="interaction_note">First Interaction Note</label>
        <textarea
          id="interaction_note"
          v-model="form.interactionNote"
          placeholder="Optional note about how you met or context for this contact"
          rows="3"
          class="input"
        />
      </div>

      <div v-if="submitError" role="alert" class="error error-block">
        {{ submitError }}
      </div>

      <div class="form-actions">
        <button type="submit" :disabled="isSubmitting" class="btn-primary">
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

.field label {
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

.fieldset {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
}

.dynamic-row {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
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
  display: block;
  margin-top: var(--space-1);
}

.error-block {
  margin-bottom: var(--space-3);
}

.form-actions {
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

@media (min-width: 640px) {
  .field-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
  }
}
</style>
