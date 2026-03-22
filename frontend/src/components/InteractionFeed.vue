<template>
  <div>
    <div v-if="interactionStore.entries.length === 0" class="empty-state">
      No interactions yet
    </div>

    <div
      v-for="entry in interactionStore.entries"
      :key="entry.id"
      class="entry"
    >
      <div class="entry-content">{{ entry.content }}</div>
      <div class="entry-meta">
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

<style scoped>
.empty-state {
  color: var(--color-text-muted);
  font-style: italic;
}

.entry {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  margin-bottom: var(--space-2);
  background: var(--color-bg);
}

.entry-content {
  white-space: pre-wrap;
  margin-bottom: var(--space-2);
  color: var(--color-text);
}

.entry-meta {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  display: flex;
  gap: var(--space-3);
  align-items: center;
}
</style>
