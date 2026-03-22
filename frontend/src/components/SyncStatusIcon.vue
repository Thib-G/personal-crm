<template>
  <span
    :class="['sync-icon', `sync-${syncStatus}`, { 'sync-spinning': syncStatus === 'syncing' }]"
    :title="tooltip"
    aria-label="Sync status"
  >{{ icon }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { syncStatus } from '@/services/sync'

const icon = computed(() => {
  switch (syncStatus.value) {
    case 'synced':  return '✓'
    case 'syncing': return '↻'
    case 'error':   return '⚠'
    case 'offline': return '✗'
  }
})

const tooltip = computed(() => {
  switch (syncStatus.value) {
    case 'synced':  return 'All data synced'
    case 'syncing': return 'Syncing…'
    case 'error':   return 'Sync failed — will retry'
    case 'offline': return 'Offline — sync paused'
  }
})
</script>

<style scoped>
.sync-icon {
  display: inline-block;
  font-size: 0.9em;
  cursor: default;
  user-select: none;
}

.sync-synced  { color: #22c55e; }
.sync-syncing { color: #3b82f6; }
.sync-error   { color: #ef4444; }
.sync-offline { color: #9ca3af; }

.sync-spinning {
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
</style>
