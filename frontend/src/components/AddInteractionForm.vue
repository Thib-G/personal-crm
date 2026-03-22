<template>
  <div>
    <form @submit.prevent="handleSubmit">
      <div class="field">
        <textarea
          v-model="content"
          rows="3"
          placeholder="What happened?"
          class="textarea"
        ></textarea>
        <div v-if="validationError" class="error">
          {{ validationError }}
        </div>
      </div>

      <div v-if="errorMessage" class="error error-block">
        {{ errorMessage }}
      </div>

      <button type="submit" :disabled="submitting" class="btn-primary">
        {{ submitting ? 'Adding…' : 'Add Interaction' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useInteractionStore } from '@/stores/interactions'

const props = defineProps<{
  contactId: string
}>()

const interactionStore = useInteractionStore()

const content = ref('')
const validationError = ref('')
const errorMessage = ref('')
const submitting = ref(false)

async function handleSubmit() {
  validationError.value = ''
  errorMessage.value = ''

  if (!content.value.trim()) {
    validationError.value = 'Interaction text is required'
    return
  }

  submitting.value = true
  try {
    await interactionStore.createInteraction(props.contactId, content.value.trim())
    content.value = ''
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Failed to add interaction. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.field {
  margin-bottom: var(--space-2);
}

.textarea {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.error {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin-top: var(--space-1);
}

.error-block {
  margin-bottom: var(--space-2);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
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
</style>
