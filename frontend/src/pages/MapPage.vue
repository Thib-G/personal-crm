<template>
  <div class="page">
    <h1>Map</h1>

    <div v-if="noData" class="no-data">
      No location data yet. Add contacts or interactions with GPS enabled.
    </div>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <div class="map-wrapper">
      <div ref="mapContainer" class="map-container"></div>
      <div class="tile-switcher">
        <button
          v-for="style in TILE_STYLES"
          :key="style.id"
          :class="['tile-btn', { active: activeTileStyleId === style.id }]"
          @click="setTileStyle(style.id)"
        >
          {{ style.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
})

const TILE_STYLES = [
  { id: 'light' as const, label: 'Light', styleId: 'mapbox/light-v11' },
  { id: 'dark' as const, label: 'Dark', styleId: 'mapbox/dark-v11' },
  { id: 'satellite' as const, label: 'Satellite', styleId: 'mapbox/satellite-streets-v12' },
]

type TileStyleId = (typeof TILE_STYLES)[number]['id']

const MAPBOX_ATTRIBUTION =
  '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> ' +
  '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'

function buildTileUrl(styleId: string, token: string): string {
  return `https://api.mapbox.com/styles/v1/${styleId}/tiles/{z}/{x}/{y}@2x?access_token=${token}`
}

const router = useRouter()

const mapContainer = ref<HTMLDivElement | null>(null)
const noData = ref(false)
const errorMessage = ref('')
const activeTileStyleId = ref<TileStyleId>('light')

let mapInstance: L.Map | null = null
let currentTileLayer: L.TileLayer | null = null

interface MapPin {
  type: string
  id: string
  contact_id: string
  contact_name: string
  lat: number
  lng: number
  label: string
  timestamp: string
}

function setTileStyle(id: TileStyleId) {
  const style = TILE_STYLES.find((s) => s.id === id)
  if (!style || !mapInstance) return
  const token = import.meta.env.VITE_MAPBOX_TOKEN
  if (currentTileLayer) mapInstance.removeLayer(currentTileLayer)
  currentTileLayer = L.tileLayer(buildTileUrl(style.styleId, token), {
    tileSize: 512,
    zoomOffset: -1,
    maxZoom: 22,
    attribution: MAPBOX_ATTRIBUTION,
  }).addTo(mapInstance)
  activeTileStyleId.value = id
}

onMounted(async () => {
  const token = import.meta.env.VITE_MAPBOX_TOKEN
  if (!token) {
    errorMessage.value = 'Map tiles unavailable: VITE_MAPBOX_TOKEN is not configured.'
    return
  }

  let pins: MapPin[] = []

  try {
    const resp = await fetch('/api/contacts/map/pins/')
    if (!resp.ok) {
      errorMessage.value = `Failed to load map data (${resp.status})`
      return
    }
    pins = await resp.json()
  } catch {
    errorMessage.value = 'Failed to load map data. Please try again.'
    return
  }

  if (pins.length === 0) {
    noData.value = true
  }

  if (!mapContainer.value) return

  mapInstance = L.map(mapContainer.value).setView([20, 0], 2)

  currentTileLayer = L.tileLayer(buildTileUrl('mapbox/light-v11', token), {
    tileSize: 512,
    zoomOffset: -1,
    maxZoom: 22,
    attribution: MAPBOX_ATTRIBUTION,
  }).addTo(mapInstance)

  if (pins.length > 0) {
    const clusterGroup = (L as any).markerClusterGroup()

    for (const pin of pins) {
      const popup = L.popup().setContent(
        `<strong>${pin.contact_name}</strong><br />${pin.label}<br /><a href="#" class="popup-contact-link" style="font-size:0.85em;">View contact</a>`,
      )
      const marker = L.marker([pin.lat, pin.lng]).bindPopup(popup)
      marker.on('popupopen', () => {
        const link = popup.getElement()?.querySelector('.popup-contact-link')
        if (link) {
          link.addEventListener(
            'click',
            (e) => {
              e.preventDefault()
              router.push('/contacts/' + pin.contact_id)
            },
            { once: true },
          )
        }
      })
      clusterGroup.addLayer(marker)
    }

    mapInstance.addLayer(clusterGroup)

    const bounds = L.latLngBounds(pins.map((p) => [p.lat, p.lng] as [number, number]))
    mapInstance.fitBounds(bounds, { padding: [40, 40] })
  }
})

onUnmounted(() => {
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }
})
</script>

<style scoped>
.page {
  padding: var(--space-4);
}

.page h1 {
  margin-top: 0;
  margin-bottom: var(--space-3);
}

.no-data {
  color: var(--color-text-muted);
  font-style: italic;
  margin-bottom: var(--space-4);
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--space-4);
}

.map-wrapper {
  position: relative;
}

.map-container {
  height: calc(100vh - 160px);
  min-height: 300px;
  width: 100%;
  border-radius: var(--radius-md);
}

.tile-switcher {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  display: flex;
  gap: 2px;
}

.tile-btn {
  padding: 4px 8px;
  font-size: 0.75rem;
  background: white;
  border: 1px solid #ccc;
  border-radius: var(--radius-sm, 4px);
  cursor: pointer;
  line-height: 1.4;
}

.tile-btn:hover {
  background: #f5f5f5;
}

.tile-btn.active {
  background: #333;
  color: white;
  border-color: #333;
}
</style>
