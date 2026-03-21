<template>
  <div>
    <div v-if="history.length === 0" style="color: #888; font-style: italic;">
      No edit history yet
    </div>

    <table v-else style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
      <thead>
        <tr>
          <th style="text-align: left; padding: 6px 8px; border-bottom: 2px solid #ddd;">Field</th>
          <th style="text-align: left; padding: 6px 8px; border-bottom: 2px solid #ddd;">From</th>
          <th style="text-align: left; padding: 6px 8px; border-bottom: 2px solid #ddd;">To</th>
          <th style="text-align: left; padding: 6px 8px; border-bottom: 2px solid #ddd;">Date</th>
          <th style="text-align: left; padding: 6px 8px; border-bottom: 2px solid #ddd;">Location</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="h in history" :key="h.id" style="border-bottom: 1px solid #eee;">
          <td style="padding: 6px 8px;">{{ h.field_name }}</td>
          <td style="padding: 6px 8px; color: #888;">{{ h.old_value ?? '—' }}</td>
          <td style="padding: 6px 8px;">{{ h.new_value ?? '—' }}</td>
          <td style="padding: 6px 8px; white-space: nowrap;">{{ formatDate(h.changed_at) }}</td>
          <td style="padding: 6px 8px; white-space: nowrap;">{{ formatLocation(h) }}</td>
        </tr>
      </tbody>
    </table>
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
