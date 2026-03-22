# Feature Specification: Add README with Installation & Deployment Documentation

**Feature Branch**: `005-add-readme-docs`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "Add a readme to the repo with instructions on how to install the application (both local dev and production on server), and how to configure the proxypass on the web server"

## Clarifications

### Session 2026-03-22

- Q: Should the reverse proxy section use a single blanket `ProxyPass /` rule or path-specific rules, and should the README explain that the production container serves both the SPA and API from a single port? → A: Keep a single `ProxyPass /` rule and add an explanation paragraph clarifying that in production the Docker image bundles the compiled Vue SPA inside Django (served as static files), so a single proxy to port 8000 already serves `/` (frontend), `/api/` (API), and `/admin` (Django admin) from the same domain. Port 5173 is development-only and does not exist in production.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New Developer Sets Up Local Environment (Priority: P1)

A developer who has just cloned the repository needs to get a fully functioning local development environment running. They should be able to follow the README from top to bottom and have the application running locally with hot-reload for both the frontend and backend, without needing to ask anyone for help.

**Why this priority**: This is the most frequent use case and directly impacts contributor onboarding. A developer cannot contribute without a working local environment.

**Independent Test**: Can be tested by a developer with no prior knowledge of the project following only the README instructions and verifying the application is accessible in their browser.

**Acceptance Scenarios**:

1. **Given** a developer has cloned the repo and has Docker installed, **When** they follow the local dev setup instructions in the README, **Then** both the backend (port 8000) and frontend (port 5173) are accessible and functional in their browser.
2. **Given** a developer follows the README, **When** they make a code change to the frontend or backend, **Then** the change is reflected without a full restart (hot-reload works as expected).
3. **Given** a developer who needs to reset their environment, **When** they follow the teardown/reset instructions, **Then** they can cleanly remove and re-create the environment.

---

### User Story 2 - System Administrator Deploys to Production Server (Priority: P2)

A sysadmin or developer deploying the application to a production server needs clear, step-by-step instructions covering environment configuration, Docker image build, container startup, and data persistence. They must end up with a running, stable production instance.

**Why this priority**: Production deployment is less frequent but higher stakes. Incorrect production setup can lead to data loss or security exposure.

**Independent Test**: Can be tested by following only the production deployment section of the README on a clean server and verifying the application is accessible and data persists across container restarts.

**Acceptance Scenarios**:

1. **Given** a server with Docker installed and the repo cloned, **When** the sysadmin follows the production deployment instructions (including required environment variables), **Then** the application starts and is accessible on port 8000 (bound to localhost).
2. **Given** the production container is running, **When** the container is restarted, **Then** all previously stored data is preserved via the mounted data volume.
3. **Given** a sysadmin configuring the environment, **When** they reference the README for required environment variables, **Then** they find a complete list with descriptions and example values (SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DATABASE_PATH).

---

### User Story 3 - Sysadmin Configures Web Server Reverse Proxy (Priority: P3)

A sysadmin needs to configure a web server (e.g., Apache or Nginx) to proxy public traffic to the application running on localhost:8000. The README must provide a working configuration example they can adapt.

**Why this priority**: Without the reverse proxy configuration, the production application is not publicly accessible over standard HTTP/HTTPS ports.

**Independent Test**: Can be tested by following the proxy configuration section of the README and verifying the application is accessible via the server's public domain name over HTTP/HTTPS.

**Acceptance Scenarios**:

1. **Given** the application container is running on port 8000, **When** the sysadmin applies the proxypass configuration from the README to their web server, **Then** the application is accessible via the server's domain name on standard ports.
2. **Given** the proxypass configuration is applied, **When** a user navigates to the public URL, **Then** all requests (including API calls and static assets) are correctly forwarded to the application.
3. **Given** a sysadmin configuring HTTPS, **When** they reference the README, **Then** they find guidance on configuring the CSRF trusted origins environment variable to match their domain.

---

### Edge Cases

- What happens when a developer skips required environment variables in production? The README must clearly mark which variables are required vs. optional and what the consequences of missing them are.
- What if the developer's port 8000 or 5173 is already in use? The README should note port requirements upfront.
- What if the sysadmin is running Apache instead of Nginx (or vice versa)? The README includes configuration examples for both Nginx and Apache, so sysadmins can follow the relevant section for their setup.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The README MUST include a prerequisites section listing software requirements (e.g., Docker, Docker Compose) and minimum version requirements for both local dev and production setups.
- **FR-002**: The README MUST include a local development setup section with step-by-step commands to clone, configure, and start the application using the development Docker Compose configuration.
- **FR-003**: The README MUST include a production deployment section with step-by-step instructions to build the production image, configure required environment variables, and start the application container.
- **FR-004**: The README MUST document all required and optional environment variables with their purpose, accepted values, and a safe example value.
- **FR-005**: The README MUST include a web server reverse proxy configuration section with a ready-to-use configuration example for at least one web server. The section MUST explain that the production Docker image bundles the compiled frontend SPA inside the Django container, so a single proxy rule to port 8000 serves the frontend from `/`, the API from `/api/`, and the admin panel from `/admin` — no path-splitting is needed. Port 5173 (Vite dev server) does not exist in production.
- **FR-006**: The README MUST explain how to configure the CSRF trusted origins variable to match the public-facing domain when deployed behind a reverse proxy.
- **FR-007**: The README MUST include instructions for verifying that the application is running correctly after each setup phase (local dev, production, proxy).
- **FR-008**: The README MUST include a section explaining how data is persisted and where the data directory is located.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer with no prior knowledge of the project can follow the README to get a working local development environment in under 15 minutes.
- **SC-002**: A sysadmin can deploy the application to a production server by following only the README, without needing external assistance.
- **SC-003**: 100% of required environment variables are documented with example values in the README.
- **SC-004**: The README covers all three setup phases: local development, production deployment, and reverse proxy configuration, each independently verifiable.
- **SC-005**: A new contributor reading the README can identify the correct setup path (dev vs. production) within the first 30 seconds of reading.

## Assumptions

- The primary deployment target is a Linux server running Docker.
- The web server reverse proxy section covers both Nginx and Apache with separate configuration examples for each.
- The README will be written in Markdown and placed at the root of the repository as `README.md`.
- HTTPS/TLS termination is handled at the web server level, not the application container.
- The reader has basic familiarity with a terminal and Docker concepts.
- The data directory (`./data`) is a host-mounted volume for persistence; no external database is required.
