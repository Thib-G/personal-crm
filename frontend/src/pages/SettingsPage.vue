<template>
  <div class="page">
    <h1>Settings</h1>

    <div class="settings-section">
      <div class="toggle-row">
        <label class="toggle-label" for="location-toggle">
          <input
            id="location-toggle"
            type="checkbox"
            :checked="settingsStore.locationTrackingEnabled"
            @change="handleLocationToggle"
            class="toggle-checkbox"
          />
          <div class="toggle-text">
            <span class="toggle-title">Record location with contacts and interactions</span>
            <span class="toggle-description">When enabled, your GPS coordinates are saved when you add contacts or log interactions.</span>
          </div>
        </label>
      </div>

      <div v-if="showSaved" class="saved-feedback">
        Saved
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const showSaved = ref(false)

let savedTimer: ReturnType<typeof setTimeout> | null = null

onMounted(async () => {
  await settingsStore.load()
})

async function handleLocationToggle(event: Event) {
  const newValue = (event.target as HTMLInputElement).checked
  await settingsStore.update(newValue)

  if (savedTimer) clearTimeout(savedTimer)
  showSaved.value = true
  savedTimer = setTimeout(() => {
    showSaved.value = false
  }, 2000)
}
</script>

<style scoped>
.page {
  padding: var(--space-4);
  max-width: 600px;
  margin: 0 auto;
}

.settings-section {
  margin-top: var(--space-6);
}

.toggle-row {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.toggle-label {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  cursor: pointer;
}

.toggle-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 2px;
}

.toggle-text {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.toggle-title {
  font-weight: 600;
  color: var(--color-text);
}

.toggle-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.saved-feedback {
  margin-top: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--color-success);
}
</style>
