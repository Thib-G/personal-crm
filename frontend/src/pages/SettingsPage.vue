<template>
  <div>
    <h1>Settings</h1>

    <div style="margin-top: 24px;">
      <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
        <input
          type="checkbox"
          :checked="settingsStore.locationTrackingEnabled"
          @change="handleLocationToggle"
          style="width: 18px; height: 18px; cursor: pointer;"
        />
        <span>Record location with contacts and interactions</span>
      </label>

      <div
        v-if="showSaved"
        style="margin-top: 8px; font-size: 0.9em; color: green;"
      >
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
