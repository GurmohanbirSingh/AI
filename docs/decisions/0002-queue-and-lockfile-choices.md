# ADR 0002 — Queue library, Python packaging and lockfiles

- **Status:** Accepted
- **Date:** 2026-11-19
- **Context:** Phase 1 requires a reproducible Python environment, pinned lockfiles and
  exactly one background-job system. The execution environment does not have `uv`
  installed, and the blueprint allows an equivalent committed lockfile.
- **Decision:**
  1. Use **RQ on Redis** for background jobs. It is small, synchronous, easy to observe
     and matches the modular-monolith design. Do not add Celery, Dramatiq, Arq or a
     second queue system later without a superseding ADR.
  2. Use **pinned `requirements.txt` / `requirements-dev.txt`** with exact versions and
     the repository `package-lock.json` for the web app. Pinning is committed; container
     builds install exactly those versions. `uv` may be adopted later via a new ADR if
     it improves reproducibility without changing runtime behaviour.
  3. Run Python 3.12 inside the API/worker container. Local development may use a newer
     interpreter for unit tests, but the documented runtime is the container image.
- **Consequences:**
  - No GPU or paid service is required for Phase 1.
  - Dependency updates are deliberate edits to pinned files, not floating ranges.
  - Phase 2 must add the durable `jobs` table before RQ jobs are enqueued.
