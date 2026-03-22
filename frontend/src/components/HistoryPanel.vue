<template>
  <div>
    <div v-if="history.length === 0" class="empty-state">
      No edit history yet
    </div>

    <div v-else class="table-wrapper">
      <table class="history-table">
        <thead>
          <tr>
            <th>Field</th>
            <th>From</th>
            <th>To</th>
            <th>Date</th>
            <th>Location</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="h in history" :key="h.id">
            <td>{{ h.field_name }}</td>
            <td class="muted">{{ h.old_value ?? '—' }}</td>
            <td>{{ h.new_value ?? '—' }}</td>
            <td class="nowrap">{{ formatDate(h.changed_at) }}</td>
            <td class="nowrap">{{ formatLocation(h) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ContactHistoryEntry } from '@/services/db'

defineProps<{
  history: ContactHistoryEntry[]
}>()

function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleString()
}

function formatLocation(h: ContactHistoryEntry): string {
  if (h.lat != null && h.lng != null) {
    return `📍 ${h.lat.toFixed(4)}, ${h.lng.toFixed(4)}`
  }
  return '—'
}
</script>

<style scoped>
.empty-state {
  color: var(--color-text-muted);
  font-style: italic;
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
  min-width: 400px;
}

.history-table th {
  text-align: left;
  padding: var(--space-1) var(--space-2);
  border-bottom: 2px solid var(--color-border);
  color: var(--color-text-muted);
}

.history-table td {
  padding: var(--space-1) var(--space-2);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.muted {
  color: var(--color-text-muted);
}

.nowrap {
  white-space: nowrap;
}
</style>
