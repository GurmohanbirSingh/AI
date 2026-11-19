# ShortsFactory AI

A local-first, niche-agnostic AI-assisted YouTube Shorts production system. The first
pilot is GTA 6 / gaming commentary, with original scripts, source evidence,
rights-cleared assets, human review, and private-first publishing.

**Current status:** Phase 1 scaffold. The repository starts a local Compose stack with
PostgreSQL, Redis, the FastAPI API, a worker, and the Next.js dashboard. There are no
domain tables or media features yet; those begin in Phase 2.

## Authoritative documents

1. [`SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md`](SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md) — product specification and phases 0–13.
2. [`AGENTS.md`](AGENTS.md) — shared instructions for coding agents.
3. [`docs/MULTI_AGENT_DEVELOPMENT_PROTOCOL.md`](docs/MULTI_AGENT_DEVELOPMENT_PROTOCOL.md) — ownership, handoff and Git rules.
4. [`docs/architecture.md`](docs/architecture.md) — architecture summary.
5. [`docs/implementation-plan.md`](docs/implementation-plan.md) — phase gates.
6. [`docs/phase-status.md`](docs/phase-status.md) — live acceptance-gate ledger and evidence.
7. [`docs/agent-handoff.md`](docs/agent-handoff.md) — current handoff record.

## Requirements

| Tool | Version used | Notes |
|---|---|---|
| Docker Engine | 24+ | Docker Desktop on Windows/macOS; Compose v2 (`docker compose`). |
| Python | 3.12+ | Only needed for optional host-side checks; the container pins 3.12. |
| Node.js | 22+ | Only needed if you run the web app outside Docker. |
| FFmpeg/ffprobe | not installed yet | Required from Phase 8. Not part of the Phase 1 image. |

No paid API key is required to start the stack. Defaults use deterministic mock
providers and make no external calls.

## Quick start (Linux, Docker Engine)

1. Install Docker Engine and the Compose plugin, then verify:

   ```bash
   docker --version
   docker compose version
   docker info
   ```

2. Clone the repository and create local configuration:

   ```bash
   git clone <repository-url> shortsfactory
   cd shortsfactory
   cp .env.example .env
   ```

   Edit `.env` and replace `ADMIN_PASSWORD` and `SESSION_SECRET`. Generate a secret
   with `openssl rand -base64 32`. Never commit `.env`.

3. Start the stack:

   ```bash
   make dev
   ```

4. Open <http://localhost:3000>, sign in with `ADMIN_PASSWORD`, and confirm the
   dashboard shows API, PostgreSQL and Redis as healthy.

API health is public at <http://localhost:8000/api/health>; interactive docs are at
<http://localhost:8000/api/docs>.

## Quick start (Windows, Docker Desktop)

1. Install Docker Desktop with the WSL 2 backend, start it, and confirm
   `docker compose version` works in PowerShell or a WSL shell.
2. Clone the repository inside your Linux filesystem (`~/shortsfactory`) for acceptable
   bind-mount performance. Running it under `C:\` works but is slower.
3. Copy `.env.example` to `.env` (`Copy-Item .env.example .env`), then change
   `ADMIN_PASSWORD` and `SESSION_SECRET` using a text editor.
4. If you use `make`, run it from WSL. Without `make`, use the equivalent commands:

   ```bash
   docker compose up -d --build
   docker compose ps
   docker compose logs -f --tail=100
   docker compose down
   ```

5. Open <http://localhost:3000> and sign in.

## Standard command contract

| Command | Purpose |
|---|---|
| `make dev` | Build and start PostgreSQL, Redis, API, worker and web. |
| `make down` | Stop services. Volumes are **not** deleted. |
| `make logs` | Follow logs. |
| `make migrate` | Apply migrations (prints a notice until Phase 2 adds Alembic). |
| `make seed-pilot` | Seed the GTA 6 pilot channel (implemented in Phase 2). |
| `make test-api` | Run Python tests in the API image. |
| `make test-web` | Run web unit tests in the web image. |
| `make lint` | Ruff check/format check and Next.js ESLint. |
| `make typecheck` | mypy (API) and `tsc --noEmit` (web). |
| `make verify` | Env checks, Compose config, lint, typecheck, both test suites and a live smoke test. |
| `make dry-run` | Assert no-upload, no-paid-API safety defaults. Nothing is rendered or uploaded. |
| `make reset` | **Destructive.** Deletes local volumes after typed confirmation. |

Without Docker you can run parts of the toolchain directly:

```bash
cd apps/api && python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest && ruff check . && mypy app

cd apps/web && npm ci && npm test && npm run typecheck && npm run lint && npm run build
```

Do not create `apps/api/.venv` while using `make test-api`: the Compose API service
mounts `apps/api` at `/app`, so a Linux venv would shadow the container packages.
Create host-side venvs under `/tmp` (or skip them) when using Docker.

## Operator authentication

- `AUTH_REQUIRED=true` (default): `/api/dashboard` and all later operational routes need
  a signed HTTP-only session cookie. `/api/health` stays public.
- Login: `POST /api/auth/login` with `{"password": "..."}`; the API sets `sf_session`
  (HTTP-only) and `sf_csrf` (readable).
- Mutations must send `X-CSRF-Token` with the token returned by login or `/api/auth/me`.
- `AUTH_REQUIRED=false` exists for automated tests only and logs a visible warning in
  the dashboard. Never use it for a real operator session.
- `COOKIE_SECURE=true` is required when `APP_ENV=production`; local HTTP development
  uses `false`.

## Environment variables

`.env.example` is the source of truth and contains placeholders only. Key ranges:

| Variable | Default | Notes |
|---|---|---|
| `APP_ENV` | `development` | `development`, `test` or `production`. |
| `AUTH_REQUIRED` | `true` | Boolean. Tests may disable. |
| `ADMIN_PASSWORD` | placeholder | At least 1 character; change locally. Placeholder is rejected in production. |
| `SESSION_SECRET` | placeholder | At least 16 characters; use 32+ random bytes. Placeholder is rejected in production. |
| `SESSION_MAX_AGE_SECONDS` | `43200` | Positive integer; 12 hours. |
| `COOKIE_SECURE` | `false` | Must be `true` in production. |
| `DATABASE_URL` | `postgresql+psycopg://...` | SQLAlchemy-style URL; health checks convert it for psycopg. |
| `REDIS_URL` | `redis://redis:6379/0` | Queue broker. |
| `MEDIA_ROOT`, `TEMP_ROOT` | `/app/data/media`, `/app/data/temp` | Container paths mounted from `./data`. |
| `LLM_PROVIDER` | `mock` | `mock`, `ollama` or `openrouter`; `openrouter` requires a key. |
| `TTS_PROVIDER` | `mock` | `mock`, `kokoro`, `piper` or `api` (adapters arrive in Phase 7). |
| `ALIGNMENT_PROVIDER` | `mock` | `mock`, `whisperx` or `faster-whisper` (Phase 7). |
| `DRY_RUN` | `true` | Safety default; do not enable uploads while true. |
| `UPLOAD_ENABLED` | `false` | Requires `DRY_RUN=false` and `APPROVAL_REQUIRED=true`. |
| `PUBLISH_ENABLED` | `false` | Requires uploads enabled. |
| `APPROVAL_REQUIRED` | `true` | Human approval gate. |
| `GLOBAL_EMERGENCY_STOP` | `false` | Set true to halt automated work. |
| `MAX_DAILY_LLM_COST` | `0` | USD per day; `0` means no paid spend permitted. |
| `MAX_DAILY_TTS_COST` | `0` | USD per day. |
| `MAX_DAILY_UPLOADS` | `0` | Upload count per day. |
| `YOUTUBE_*` | empty | Not used until Phase 10. Verify quotas in Google Cloud Console. |

Invalid settings fail startup with the field name and reason. Secret values are never
echoed in the error.

## Optional local AI tooling (not required for Phase 1)

These are documented now, but no adapter calls them until Phase 7. Review every runtime,
model and voice licence before commercial use.

- **Ollama** (free local LLM): install from <https://ollama.com>, run
  `ollama pull qwen2.5:7b`, then set `LLM_PROVIDER=ollama`. From inside Docker the host
  is reached at `http://host.docker.internal:11434`; on Linux add
  `extra_hosts: ["host.docker.internal:host-gateway"]` to the API service if needed.
- **Kokoro** (preferred TTS candidate): `kokoro-onnx` runtime and Apache-2.0 model
  weights must be verified per release, along with voice packs and phonemizer licences.
- **Piper**: the maintained engine is GPL-3.0-or-later and voices have separate
  model-card terms; do not assume it is commercial-safe without review.
- **WhisperX** for word-level forced alignment of known transcripts; CPU-only is
  supported but benchmark runtime before relying on it.
- Do **not** add `edge-tts` or reverse-engineered speech endpoints.

## Troubleshooting

See [`docs/operations-runbook.md`](docs/operations-runbook.md). The most common issue is
a missing `.env`; `make env` creates one from the example.

## Safety

Dry-run, no uploads, no public publishing and human approval are the defaults. Never
commit secrets, OAuth files, tokens, media or private rights documents. Never publish a
public video or download another creator's media without a documented rights basis.
