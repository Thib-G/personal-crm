import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const locationTrackingEnabled = ref<boolean>(true)

  async function load(): Promise<void> {
    try {
      const response = await fetch('/api/settings/privacy/')
      if (response.ok) {
        const data = (await response.json()) as { location_tracking_enabled: boolean }
        locationTrackingEnabled.value = data.location_tracking_enabled
      } else {
        locationTrackingEnabled.value = true
      }
    } catch {
      locationTrackingEnabled.value = true
    }
  }

  async function update(enabled: boolean): Promise<void> {
    const response = await fetch('/api/settings/privacy/', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ location_tracking_enabled: enabled }),
    })

    if (!response.ok) {
      throw new Error('Failed to update privacy settings')
    }

    locationTrackingEnabled.value = enabled
  }

  return { locationTrackingEnabled, load, update }
})
