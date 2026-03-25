# Feature Specification: Mapbox Tile Integration

**Feature Branch**: `008-mapbox-tiles`
**Created**: 2026-03-25
**Status**: Draft
**Input**: User description: "replace the default osm tiles in the map by mapbox tiles (light by default, dark and satellite) and store the mapbox key in an environment variable (for dev & prod)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Map with Mapbox Light Tiles (Priority: P1)

When a user opens the map, it displays Mapbox light-style tiles by default instead of OpenStreetMap tiles. The map looks clean, modern, and loads correctly. On high-resolution (retina/HiDPI) displays, tiles render at double resolution — sharp and crisp rather than blurry.

**Why this priority**: This is the core change — replacing OSM with Mapbox as the tile provider. All other tile styles build on this foundation. Retina support ensures the map looks high-quality on modern hardware.

**Independent Test**: Can be fully tested by opening the map on a retina display and confirming Mapbox light tiles render sharply, and on a standard display confirming correct rendering without regression.

**Acceptance Scenarios**:

1. **Given** the map is loaded, **When** no tile style is explicitly selected, **Then** Mapbox light-style tiles are displayed by default
2. **Given** the map is loaded with Mapbox light tiles, **When** the user inspects the map, **Then** no OpenStreetMap tiles are visible
3. **Given** the Mapbox API key is missing or invalid, **When** the map loads, **Then** a clear error or fallback is shown rather than a broken map
4. **Given** a user is on a high-DPI (retina) display, **When** the map loads, **Then** tiles render at high resolution — labels, roads, and borders appear sharp
5. **Given** a user is on a standard-DPI display, **When** the map loads, **Then** tiles render correctly without visual degradation

---

### User Story 2 - Switch Between Tile Styles (Priority: P2)

The user can switch between three tile styles: light (default), dark, and satellite. The switch is immediate and the selected style persists for the session.

**Why this priority**: Tile style switching is a key part of the requested feature, enabling users to pick the map view that suits their needs.

**Independent Test**: Can be fully tested by switching between light, dark, and satellite styles and confirming each renders correctly.

**Acceptance Scenarios**:

1. **Given** the map is displayed, **When** the user selects the dark style, **Then** dark Mapbox tiles replace the current tiles
2. **Given** the map is displayed, **When** the user selects the satellite style, **Then** satellite imagery tiles replace the current tiles
3. **Given** the user switched to dark or satellite, **When** they select light, **Then** Mapbox light tiles are restored

---

### User Story 3 - Mapbox API Key Configured via Environment Variable (Priority: P3)

The Mapbox API key is provided through an environment variable, allowing different keys for development and production environments without hardcoding credentials in the codebase.

**Why this priority**: Security and configurability concern — the API key must not be committed to source control. This enables safe deployment across environments.

**Independent Test**: Can be fully tested by setting the environment variable and confirming the map loads tiles; unsetting it and confirming a graceful failure.

**Acceptance Scenarios**:

1. **Given** the Mapbox API key is set in the environment, **When** the application starts, **Then** the map uses that key to load tiles
2. **Given** the Mapbox API key is absent from the environment, **When** the application starts, **Then** the map indicates a configuration error rather than failing silently
3. **Given** a different key is set in the development environment vs. production, **When** each environment runs, **Then** each uses its own key independently

---

### Edge Cases

- What happens when the Mapbox API key is valid but has exceeded its usage quota?
- How does the map behave when the user is offline and Mapbox tiles cannot be fetched?
- What happens if the user switches tile styles rapidly in succession?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The map MUST display Mapbox light-style tiles by default on initial load
- **FR-002**: The map MUST offer three tile style options: light, dark, and satellite
- **FR-003**: Users MUST be able to switch between tile styles via a control on the map
- **FR-004**: The application MUST read the Mapbox API key from an environment variable at startup
- **FR-005**: The environment variable MUST be configurable independently for development and production environments
- **FR-006**: The application MUST NOT embed the Mapbox API key in source-controlled files
- **FR-007**: When the Mapbox API key is missing, the application MUST surface a visible error rather than silently breaking
- **FR-011**: The project README MUST include a dedicated section explaining how to obtain a Mapbox token and set the `VITE_MAPBOX_TOKEN` environment variable for both development and production environments
- **FR-008**: The map MUST automatically request and display high-resolution (2x retina) tiles on devices with a high pixel density ratio
- **FR-009**: Retina tile resolution MUST apply to all three tile styles (light, dark, satellite)
- **FR-010**: Tile resolution selection MUST be automatic based on device display density — no user action or toggle required

### Key Entities

- **Tile Style**: Represents a map tile provider configuration (light, dark, satellite) with an associated Mapbox style identifier
- **Mapbox API Key**: A secret credential required to authenticate tile requests; sourced from the environment, not the codebase

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The map loads with Mapbox tiles visible within the same time it previously loaded with OSM tiles (no perceptible regression)
- **SC-002**: All three tile styles (light, dark, satellite) render correctly and switch without a page reload
- **SC-003**: The Mapbox API key is absent from all committed source files and build artifacts
- **SC-004**: Deploying to a new environment requires only setting the environment variable — no code changes needed to supply the API key
- **SC-007**: A developer unfamiliar with the project can find and follow the Mapbox setup instructions in the README without needing to read the source code
- **SC-005**: On a high-DPI screen, map labels, roads, and boundaries are visually sharp — no pixel blurriness visible at normal viewing distance
- **SC-006**: On a standard-DPI screen, the map displays correctly with no visual change or performance regression

## Clarifications

### Session 2026-03-25

- Q: Should the map use high-resolution (retina) tiles? → A: Yes — automatically use 2x retina tiles on high-DPI displays; standard tiles on standard-DPI displays
- Q: Should README include Mapbox setup instructions? → A: Yes — add a section covering how to obtain a token and set VITE_MAPBOX_TOKEN for dev and prod

## Assumptions

- The map component is already built and working with OSM tiles; this feature replaces the tile source only
- A tile style switcher UI will be added directly on the map (small control, e.g., top-right corner) — no separate settings page needed
- The environment variable name will follow the existing project convention (e.g., prefixed for the frontend build tool in use)
- The selected tile style is not persisted across sessions (session-only); it resets to light on page reload
- "Retina tiles" means 2x resolution tiles specifically; 3x or device-pixel-ratio >2 is out of scope
