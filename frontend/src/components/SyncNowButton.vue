<template>
  <button
    type="button"
    aria-label="Sync now"
    :disabled="isDisabled"
    class="sync-now-btn"
    @click="syncService.syncNow()"
  >
    Sync
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { syncStatus, syncService } from '@/services/sync'

const isDisabled = computed(() => syncStatus.value === 'syncing' || syncStatus.value === 'offline')
</script>

<style scoped>
.sync-now-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 2px var(--space-2);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.sync-now-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
