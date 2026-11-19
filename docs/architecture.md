# Architecture

Derived from **Part D** of `SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md`, which remains
authoritative. This document summarises the target architecture so implementation
phases have a shared, checkable reference.

## Shape

A **modular monolith**: one FastAPI backend, one Python worker, one Next.js web app,
PostgreSQL, Redis and FFmpeg-family tooling, deployed with Docker Compose for local
development. Modules are separated by responsibility inside the API rather than as
network services.

## Runtime components

| Component | Technology | Responsibility |
|---|---|---|
| Web | Next.js App Router, TypeScript, Tailwind CSS | Operator dashboard, login, review screens (Phases 1 and 9). Calls the API through a same-origin proxy. |
| API | Python 3.12+, FastAPI, Pydantic v2 | Public health endpoint, local operator auth, domain API (Phase 2 onwards). |
| Worker | Python process, RQ on Redis | Durable background jobs with `jobs` records (Phase 2 onwards). Phase 1 only proves queue connectivity. |
| Database | PostgreSQL 16 | All domain state, audit logs, jobs and rights records. Alembic migrations from Phase 2. |
| Queue | Redis 7 | RQ broker and worker heartbeat. |
| Media | FFmpeg/ffprobe, Pillow, CairoSVG, Matplotlib | Rendering, audio normalisation, graphics (Phases 6 and 8). Not installed in the Phase 1 image. |
| Storage | Local filesystem behind a `StorageProvider` interface | `MEDIA_ROOT` and `TEMP_ROOT`, mounted as `./data` in development. |

## Service boundaries

1. `topic_discovery` — feeds, manual entry, optional metadata APIs.
2. `research` — allowlisted extraction and evidence packets.
3. `script_generation` — structured scripts from verified evidence.
4. `rights_management` — authoritative rights decisions.
5. `asset_library` — assets, hashes, graphics, optional stock adapters.
6. `voice` — TTS and caption alignment.
7. `rendering` — scene assembly, loudness, thumbnails, FFmpeg.
8. `quality_control` — video, audio, captions, evidence, rights, metadata checks.
9. `publishing` — YouTube OAuth and private upload.
10. `analytics` — metrics ingestion and cited observations.
11. `orchestration` — durable jobs, budgets, audit events.

## Provider adapters

Every external integration sits behind an interface with a deterministic `mock`
implementation. Phase 1 exposes provider **modes** only; it does not call any external
service. The default modes are `mock` for LLM, TTS and alignment.

## Safety and auth boundaries

- `/api/health` is public and returns structured connectivity, provider and safety data.
- All other operational routes require an operator session when `AUTH_REQUIRED=true`
  (the default). Mutations additionally require an `X-CSRF-Token` header.
- The session is a signed HTTP-only cookie (`sf_session`); CSRF uses a double-submit
  token mirrored in the readable `sf_csrf` cookie.
- `DRY_RUN=true`, `UPLOAD_ENABLED=false`, `PUBLISH_ENABLED=false` and
  `APPROVAL_REQUIRED=true` are enforced as defaults by `.env.example` and validated at
  startup (for example, uploads cannot be enabled while dry-run is on).

## Current-phase boundaries

Phase 1 deliberately contains no domain tables, no migrations, no topic or script
logic, and no media processing. `/api/migrate` and `make seed-pilot` are placeholders
until Phase 2. See `docs/phase-status.md` for the live gate ledger.
