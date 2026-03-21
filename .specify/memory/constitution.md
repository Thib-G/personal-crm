<!--
Sync Impact Report
==================
Version change: 1.2.0 → 1.3.0 (Technology & Stack Constraints: full stack defined — Django-Ninja, Vue 3 + TS, Apache2/Debian 13)
Modified principles: N/A (initial document)
Added sections:
  - Core Principles (5 principles)
  - Technology & Stack Constraints
  - Development Workflow
  - Governance
Removed sections: N/A
Templates checked:
  ✅ .specify/templates/plan-template.md — Constitution Check section is dynamic; no update needed
  ✅ .specify/templates/spec-template.md — generic structure; aligned with principles
  ✅ .specify/templates/tasks-template.md — task structure aligns with TDD and story-first principles
  ✅ .specify/templates/checklist-template.md — no constitution references; no update needed
  ✅ .specify/templates/agent-file-template.md — no constitution references; no update needed
Deferred TODOs: none
-->

# Personal CRM Constitution

## Core Principles

### I. Privacy-First (NON-NEGOTIABLE)

All personal contact data MUST be treated as sensitive. The system MUST:
- Store data locally or in user-controlled storage only; no third-party data sharing without
  explicit user consent
- Never transmit contact information to external services unless user-initiated
- Provide clear data boundaries: what is stored, where, and who can access it

**Rationale**: A personal CRM holds relationship data—names, notes, communications history—that
is inherently private. Privacy violations erode user trust irreversibly.

### II. Simplicity Over Features

The system MUST favor simple, focused solutions:
- Every feature MUST solve a real, demonstrated user need before being added
- YAGNI (You Aren't Gonna Need It): no speculative features or premature abstractions
- Complexity MUST be explicitly justified in the plan's Complexity Tracking table before
  implementation begins

**Rationale**: Personal tools bloat into unusable products when built for imagined future needs.
Simplicity keeps the tool useful and maintainable by a single developer.

### III. Data Integrity (NON-NEGOTIABLE)

Contact and relationship data MUST remain consistent and reliable:
- No silent data loss: all write failures MUST surface as visible errors
- Schema migrations MUST be reversible or include a documented rollback path
- Exports MUST produce complete, re-importable snapshots of all user data

**Rationale**: Losing or corrupting contact data is a critical failure mode. Users depend on
the CRM to remember what they cannot.

### IV. User-Owned Data

The user MUST retain full ownership and portability of their data:
- All data MUST be exportable in an open, documented format (e.g., CSV, JSON)
- No proprietary lock-in formats
- Delete operations MUST be complete: no hidden retention of deleted records

**Rationale**: Personal tools must not create dependency traps. Users must be able to leave,
migrate, or back up their data at any time without friction.

### V. Test-Driven Development

TDD is MANDATORY for all feature implementation:
- Tests MUST be written and reviewed before implementation begins
- The Red-Green-Refactor cycle MUST be followed: tests fail first, then implementation makes
  them pass, then refactor
- Integration tests MUST cover all critical data paths (create, read, update, delete) for
  core entities

**Rationale**: A CRM without reliable tests risks silent regressions that corrupt or lose user
data—directly violating the Data Integrity principle.

### VI. Atomic Commits

Every discrete change MUST be captured as an individual git commit:
- Each commit MUST represent one logical unit of work (one task, one fix, one decision)
- Commits MUST NOT bundle unrelated changes; squashing separate concerns is prohibited
- Commit messages MUST describe the intent of the change, not just what files were touched
- Work-in-progress MUST be committed incrementally, not as a single bulk commit at the end

**Rationale**: Individual commits make the full history of decisions visible and reversible.
A CRM evolves over years; a clear commit trail is the only reliable record of why things
are the way they are.

## Technology & Stack Constraints

The application MUST conform to the following non-negotiable platform decisions:

**Platform**: Web application, accessed via browser. No native desktop or mobile clients.

**Backend**: Python with Django and Django-Ninja for the REST API layer. Django's built-in ORM,
auth, and admin are preferred over third-party replacements.

**Frontend**: Vue 3 with TypeScript. The frontend is a SPA served as static assets; it
communicates with the backend exclusively via the Django-Ninja API.

**Authentication**: Username/password login screen backed by Django's authentication system.
Sessions MUST be server-side (Django session framework). No third-party OAuth at this stage.

**Storage**: SQLite via Django's ORM. Django migrations are the sole mechanism for schema
changes; hand-written SQL is prohibited. A migration to PostgreSQL requires an explicit
constitution amendment.

**Deployment**: Fully containerized via Docker. The entire stack MUST be runnable with a single
`docker compose up` command on a fresh Linux host. No host-level dependencies beyond Docker.
Recommended service split: one container for the Django app (gunicorn), one for the Vue static
asset build step (build-time only, not a runtime service).

**Reverse proxy**: Apache2 virtual host on the host Debian 13 machine (outside Docker) handles
TLS termination and proxies to the Django container. The app MUST NOT assume it is the root
process handling TLS.

**Target host**: A single cheap VPS (e.g., 1 vCPU, 512 MB–1 GB RAM, Linux). Constraints:
- The full stack at idle MUST consume less than 256 MB RAM
- Container images MUST be built for `linux/amd64`
- No managed cloud services required at runtime

**Scale**: Single user for the foreseeable future. Multi-tenancy MUST NOT be designed in
speculatively; it would add complexity that violates Principle II.

**Dependencies**: Minimize third-party libraries. Each added dependency MUST justify its
inclusion against the lightweight constraint.

## Development Workflow

- All features begin with a spec (`/speckit.specify`) before any code is written
- Implementation plans (`/speckit.plan`) MUST pass the Constitution Check before proceeding
- Pull requests MUST reference the feature spec and include passing tests
- No feature is considered complete until it satisfies all acceptance scenarios in its spec
- Breaking changes to data schemas MUST include a migration task in the feature's `tasks.md`

## Governance

This constitution supersedes all other development practices. Amendments require:
1. A documented rationale for the change
2. A version bump following semantic versioning:
   - **MAJOR**: Principle removed, redefined, or made incompatible with prior interpretation
   - **MINOR**: New principle or section added, or existing guidance materially expanded
   - **PATCH**: Clarifications, wording corrections, typo fixes
3. Updates to all dependent templates if the amendment changes mandatory sections or task types
4. Review of all in-progress feature specs for compliance impact

All PRs and reviews MUST verify compliance with the six Core Principles above. Use
`.specify/memory/constitution.md` as the authoritative reference during planning and review.

**Version**: 1.3.0 | **Ratified**: 2026-03-20 | **Last Amended**: 2026-03-20
