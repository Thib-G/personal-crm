import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'

// Hoist mock factories so they are available when vi.mock() runs
const { mockTileLayerFn, mockMapFn } = vi.hoisted(() => {
  const tileLayerInstance = {
    addTo: vi.fn().mockReturnThis(),
    remove: vi.fn(),
  }
  const mockTileLayerFn = vi.fn(() => tileLayerInstance)

  const mapInstance = {
    setView: vi.fn().mockReturnThis(),
    addLayer: vi.fn(),
    removeLayer: vi.fn(),
    fitBounds: vi.fn(),
    remove: vi.fn(),
  }
  const mockMapFn = vi.fn(() => mapInstance)

  return { mockTileLayerFn, mockMapFn }
})

vi.mock('leaflet', () => ({
  default: {
    map: mockMapFn,
    tileLayer: mockTileLayerFn,
    markerClusterGroup: vi.fn(() => ({ addLayer: vi.fn() })),
    marker: vi.fn(() => ({
      bindPopup: vi.fn().mockReturnThis(),
      on: vi.fn(),
    })),
    popup: vi.fn(() => ({
      setContent: vi.fn().mockReturnThis(),
      getElement: vi.fn(() => null),
    })),
    latLngBounds: vi.fn(() => ({})),
    Icon: {
      Default: {
        prototype: {},
        mergeOptions: vi.fn(),
      },
    },
  },
}))

vi.mock('leaflet/dist/leaflet.css', () => ({}))
vi.mock('leaflet.markercluster', () => ({}))
vi.mock('leaflet.markercluster/dist/MarkerCluster.css', () => ({}))
vi.mock('leaflet.markercluster/dist/MarkerCluster.Default.css', () => ({}))
vi.mock('leaflet/dist/images/marker-icon-2x.png', () => ({ default: '' }))
vi.mock('leaflet/dist/images/marker-icon.png', () => ({ default: '' }))
vi.mock('leaflet/dist/images/marker-shadow.png', () => ({ default: '' }))

import MapPage from '../MapPage.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: '/map', component: MapPage }],
})

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue([]),
    }),
  )
  vi.clearAllMocks()
})

afterEach(() => {
  vi.unstubAllEnvs()
  vi.unstubAllGlobals()
})

// ─── T002: Token guard ────────────────────────────────────────────────────────

describe('T002: token guard', () => {
  it('shows error containing "VITE_MAPBOX_TOKEN" when token is empty', async () => {
    vi.stubEnv('VITE_MAPBOX_TOKEN', '')
    const wrapper = mount(MapPage, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('VITE_MAPBOX_TOKEN')
  })

  it('does not initialise the map when token is empty', async () => {
    vi.stubEnv('VITE_MAPBOX_TOKEN', '')
    mount(MapPage, { global: { plugins: [router] } })
    await flushPromises()
    expect(mockMapFn).not.toHaveBeenCalled()
  })
})

// ─── T003: Mapbox light tile URL + detectRetina ───────────────────────────────

describe('T003: Mapbox light tiles', () => {
  it('calls L.tileLayer with a URL containing "light-v11" and "@2x" when token is set', async () => {
    vi.stubEnv('VITE_MAPBOX_TOKEN', 'pk.test-token')
    mount(MapPage, { global: { plugins: [router] } })
    await flushPromises()
    expect(mockTileLayerFn).toHaveBeenCalledWith(
      expect.stringContaining('light-v11'),
      expect.any(Object),
    )
    expect(mockTileLayerFn).toHaveBeenCalledWith(
      expect.stringContaining('@2x'),
      expect.any(Object),
    )
  })

  it('passes tileSize: 512 and zoomOffset: -1 to L.tileLayer', async () => {
    vi.stubEnv('VITE_MAPBOX_TOKEN', 'pk.test-token')
    mount(MapPage, { global: { plugins: [router] } })
    await flushPromises()
    expect(mockTileLayerFn).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ tileSize: 512, zoomOffset: -1 }),
    )
  })

  it('embeds the token in the tile URL', async () => {
    vi.stubEnv('VITE_MAPBOX_TOKEN', 'pk.test-token')
    mount(MapPage, { global: { plugins: [router] } })
    await flushPromises()
    const url = (mockTileLayerFn.mock.calls[0] as unknown[])?.[0] as string
    expect(url).toContain('pk.test-token')
  })
})

// ─── T006: Tile style switcher ────────────────────────────────────────────────

describe('T006: tile style switcher', () => {
  it('switches to dark-v11 tiles when the Dark button is clicked', async () => {
    vi.stubEnv('VITE_MAPBOX_TOKEN', 'pk.test-token')
    const wrapper = mount(MapPage, { global: { plugins: [router] } })
    await flushPromises()
    vi.clearAllMocks()

    const darkBtn = wrapper.findAll('.tile-btn').find((b) => b.text() === 'Dark')
    await darkBtn!.trigger('click')

    expect(mockTileLayerFn).toHaveBeenCalledWith(
      expect.stringContaining('dark-v11'),
      expect.objectContaining({ tileSize: 512 }),
    )
  })

  it('switches to satellite-streets-v12 tiles when the Satellite button is clicked', async () => {
    vi.stubEnv('VITE_MAPBOX_TOKEN', 'pk.test-token')
    const wrapper = mount(MapPage, { global: { plugins: [router] } })
    await flushPromises()
    vi.clearAllMocks()

    const satelliteBtn = wrapper.findAll('.tile-btn').find((b) => b.text() === 'Satellite')
    await satelliteBtn!.trigger('click')

    expect(mockTileLayerFn).toHaveBeenCalledWith(
      expect.stringContaining('satellite-streets-v12'),
      expect.objectContaining({ tileSize: 512 }),
    )
  })

  it('sets "active" class on the clicked style button and removes it from others', async () => {
    vi.stubEnv('VITE_MAPBOX_TOKEN', 'pk.test-token')
    const wrapper = mount(MapPage, { global: { plugins: [router] } })
    await flushPromises()

    const lightBtn = wrapper.findAll('.tile-btn').find((b) => b.text() === 'Light')!
    const darkBtn = wrapper.findAll('.tile-btn').find((b) => b.text() === 'Dark')!

    await darkBtn.trigger('click')

    expect(darkBtn.classes()).toContain('active')
    expect(lightBtn.classes()).not.toContain('active')
  })
})
