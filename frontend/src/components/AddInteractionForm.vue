<template>
  <div>
    <form @submit.prevent="handleSubmit">
      <div style="margin-bottom: 8px;">
        <textarea
          v-model="content"
          rows="3"
          placeholder="What happened?"
          style="width: 100%; max-width: 500px; resize: vertical;"
        ></textarea>
        <div v-if="validationError" style="color: red; font-size: 0.9em; margin-top: 4px;">
          {{ validationError }}
        </div>
      </div>

      <div v-if="errorMessage" style="color: red; margin-bottom: 8px;">
        {{ errorMessage }}
      </div>

      <button type="submit" :disabled="submitting">
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
