<template>
  <div>
    <div v-if="interactionStore.entries.length === 0" style="color: #888; font-style: italic;">
      No interactions yet
    </div>

    <div
      v-for="entry in interactionStore.entries"
      :key="entry.id"
      style="border: 1px solid #ddd; border-radius: 6px; padding: 12px; margin-bottom: 10px;"
    >
      <div style="white-space: pre-wrap; margin-bottom: 6px;">{{ entry.content }}</div>
      <div style="font-size: 0.8em; color: #888; display: flex; gap: 12px; align-items: center;">
        <span>{{ formatDate(entry.created_at) }}</span>
        <span v-if="entry.lat != null && entry.lng != null">📍</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useInteractionStore } from '@/stores/interactions'

const props = defineProps<{
  contactId: string
}>()

const interactionStore = useInteractionStore()

onMounted(async () => {
  await interactionStore.loadForContact(props.contactId)
})

function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleString()
}
</script>
