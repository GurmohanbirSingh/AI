# Phase Status

**Product specification:** `SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md`
**Current phase:** Phase 1 — Project scaffold, developer environment and health checks
**Overall status:** PASS  
**Last updated:** 2026-11-19T23:40:42+05:30 (IST), OpenCode

## Phase gate ledger

| Phase | Name | Status | Evidence |
|---|---|---|---|
| 0 | Repository audit, requirements baseline and execution rules | PASS | Baseline recorded; missing `docs/architecture.md`, `docs/implementation-plan.md` and ADR 0001 were added during the Phase 1 session (see note below). |
| 1 | Project scaffold, developer environment and health checks | PASS | Compose stack boots; 18 API tests and 7 web tests pass; live smoke test covers health, auth, CSRF, proxy, worker and web. |
| 2 | Database, migrations, core domain and API skeleton | NOT_STARTED | — |
| 3 | Topic discovery and trend-signal ingestion | NOT_STARTED | — |
| 4 | Research packets and evidence-grounded script generation | NOT_STARTED | — |
| 5 | Rights ledger and publication eligibility gate | NOT_STARTED | — |
| 6 | Asset library, programmatic graphics, scene planning and visual selection | NOT_STARTED | — |
| 7 | Local-first AI voice and word-level caption alignment | NOT_STARTED | — |
| 8 | Video rendering, loudness normalisation, captions and thumbnail generation | NOT_STARTED | — |
| 9 | Editorial studio, review dashboard, auth and approval workflow | NOT_STARTED | — |
| 10 | YouTube OAuth, private upload, disclosure metadata and scheduling controls | NOT_STARTED | — |
| 11 | Analytics ingestion and learning loop | NOT_STARTED | — |
| 12 | Multi-channel, multi-niche orchestration, budgets and safe scaling | NOT_STARTED | — |
| 13 | Production hardening and release readiness | NOT_STARTED | — |

## Evidence log

### 2026-11-19 — Phase 1 (OpenCode)

**Baseline inspected before editing:** branch `phase/1-project-scaffold`, HEAD
`2fc6c51` (“phase 0 Check”), untracked `backend/app/__init__.py` (left untouched and
not committed), no application code. Environment: Python 3.13.1, Node v23.5.0, npm
10.9.2, Docker 29.9.3 with a reachable daemon, Compose v5.7.1. `ffmpeg`/`ffprobe` and
`uv` are not installed; no local PostgreSQL/Redis clients.

**Files created or changed**

- Root: `.env.example`, `.gitignore`, `Makefile`, `docker-compose.yml`, `README.md`
- `apps/api/`: Dockerfile, `.dockerignore`, `pyproject.toml`, `requirements.txt`,
  `requirements-dev.txt`, `app/` (config, auth, health service, API routes, schemas,
  worker, app factory), `tests/` (config, health, auth, worker)
- `apps/web/`: Dockerfile, `.dockerignore`, `package.json`, `package-lock.json`,
  Next.js App Router shell, Tailwind config, `lib/api.ts`, `components/Dashboard.tsx`,
  Vitest tests
- `scripts/`: `check_env_example.py`, `check_safety_defaults.py`, `smoke_phase1.sh`
- Docs: `docs/architecture.md`, `docs/implementation-plan.md`,
  `docs/rights-and-content-policy.md`, `docs/operations-runbook.md`,
  `docs/decisions/0001-modular-monolith-and-pilot-scope.md`,
  `docs/decisions/0002-queue-and-lockfile-choices.md`, this file,
  `docs/agent-handoff.md`
- Phase 0 remediation: the three missing Phase 0 documents above were added during this
  session. The Phase 0 implementation commit did not include them, despite the previous
  status header claiming PASS. No application behaviour was changed for Phase 0.

**Commands and results**

| Command | Result |
|---|---|
| `python3 scripts/check_env_example.py` | PASS — placeholders only, required keys present, safe defaults verified |
| `python3 scripts/check_safety_defaults.py` | PASS — dry run, uploads off, publishing off, approvals on, paid caps 0 |
| `docker compose config -q` | Exit 0 |
| `docker compose up -d --build --wait` (via smoke) | All five services reached `healthy` |
| `bash scripts/smoke_phase1.sh` | PASS — public health `status=ok`; DB and queue checks true; anonymous dashboard 401; login via Next proxy 200; authenticated dashboard 200; web shell renders; logout without CSRF 403 and with CSRF 204 |
| `docker compose run --rm --no-deps api pytest` | 18 passed, 1 warning (Starlette/anyio deprecation), 0 failed, 0 skipped |
| `docker compose run --rm --no-deps web npm test` | 7 passed, 0 failed |
| `docker compose run --rm --no-deps api ruff check .` | All checks passed |
| `docker compose run --rm --no-deps api ruff format --check .` | 22 files already formatted |
| `docker compose run --rm --no-deps api mypy app` | Success, no issues in 17 source files |
| `npm run typecheck` (host, prior to image build) | Success |
| `npm run lint` (host) | No ESLint warnings or errors (`next lint` deprecation note only) |
| `npm run build` (host) | Production build completed |
| `make verify` | PASS end to end (env checks, Compose config, lint, typecheck, both suites, live smoke) |
| `.env` / dummy token ignore check | PASS — `.env`, `dummy.env`, `dummy.token` ignored; `.env.example` not ignored |

**External services mocked versus live-verified**

- No paid API, LLM, TTS, stock, YouTube or OAuth call was made or configured.
- Provider modes report `mock`; the worker only pings local Redis.
- PostgreSQL and Redis were genuinely started and verified locally in Docker.
- Dashboard and API were genuinely served on `localhost:3000` and `localhost:8000`.
- Docker daemon was reachable, so container boot was verified rather than marked
  `BLOCKED_EXTERNAL_SETUP`.
- `ffmpeg` is not installed; irrelevant to Phase 1 and deferred to Phase 8.
- Ollama/Kokoro/Piper/WhisperX were not installed or tested; deferred to Phase 7.

**Remaining limitations**

- `make migrate` and `make seed-pilot` print an explanatory notice; migrations and the
  pilot seed arrive in Phase 2.
- The API image installs dev dependencies for local testing. Production hardening is
  Phase 13.
- `next lint` is deprecated and must be migrated to the ESLint CLI before Next.js 16.
- The untracked `backend/app/__init__.py` is user/previous work and was deliberately left
  unchanged.
- The dashboard uses build-time Next.js rewrites, so changing the API target requires a
  web image rebuild (documented in the Dockerfile).

**Gate decision:** `PASS` for Phase 1.

### 2026-11-20 — Phase 1 audit follow-up (Codex)

- Updated `scripts/smoke_phase1.sh` to store the login response in a unique temporary
  file and remove it with the cookie jar on exit. Updated
  `docs/audits/phase-01-codex-review.md` to record the finding as resolved.
- `bash scripts/smoke_phase1.sh` — PASS (exit 0); all five Compose services healthy;
  health endpoint, unauthenticated dashboard rejection, login through the web proxy,
  authenticated dashboard, web shell, and CSRF logout checks succeeded.
- Initial sandbox attempt failed before starting the stack with Docker socket permission
  denied; the same command was rerun with approved Docker access and passed.
- No other test suites were rerun. Docker Compose services were live locally; paid APIs,
  OAuth, YouTube, and external model providers were not contacted.
