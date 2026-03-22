<template>
  <div>
    <div v-if="entries.length === 0" class="empty-state">
      No interactions yet
    </div>

    <div
      v-for="entry in entries"
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
import { ref, onUnmounted } from 'vue'
import { liveQuery } from 'dexie'
import { db } from '@/services/db'
import type { InteractionEntry } from '@/services/db'

const props = defineProps<{
  contactId: string
}>()

const entries = ref<InteractionEntry[]>([])

const sub = liveQuery(() =>
  db.interaction_entries
    .where('contact_id')
    .equals(props.contactId)
    .sortBy('created_at')
    .then((rows) => rows.reverse()),
).subscribe({
  next: (rows) => {
    entries.value = rows
  },
})

onUnmounted(() => {
  sub.unsubscribe()
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
