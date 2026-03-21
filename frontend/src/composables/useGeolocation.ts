import { useSettingsStore } from '../stores/settings'

let hasWarnedPermissionDenied = false

export async function useGeolocation(): Promise<{ lat: number; lng: number } | null> {
  const settingsStore = useSettingsStore()

  if (!settingsStore.locationTrackingEnabled) {
    return null
  }

  if (!navigator.geolocation) {
    return null
  }

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        })
      },
      (error: GeolocationPositionError) => {
        if (error.code === GeolocationPositionError.PERMISSION_DENIED) {
          if (!hasWarnedPermissionDenied) {
            console.warn(
              'Geolocation permission denied. Location will not be recorded.',
            )
            hasWarnedPermissionDenied = true
          }
        }
        resolve(null)
      },
    )
  })
}
