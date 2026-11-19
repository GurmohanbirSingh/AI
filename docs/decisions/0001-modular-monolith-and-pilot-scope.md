# ADR 0001 — Modular monolith, local-first providers and one approved pilot

- **Status:** Accepted
- **Date:** 2026-11-19
- **Context:** ShortsFactory AI must ship a rights-conscious YouTube Shorts pipeline
  without paid API commitments, while remaining niche-agnostic for later channels.

## Decision

1. **Modular monolith.** One FastAPI application, one worker and one web app share a
   PostgreSQL database and Redis queue. Modules (`topic_discovery`, `research`,
   `script_generation`, `rights_management`, `asset_library`, `voice`, `rendering`,
   `quality_control`, `publishing`, `analytics`, `orchestration`) are separate packages
   with explicit interfaces, not separate network services.
2. **$0-paid-API, local-first providers.** LLM, TTS, alignment and asset providers
   default to deterministic mocks during tests and local open-weight runtimes
   (Ollama, Kokoro/WhisperX once licence-reviewed) in development. External paid APIs
   are opt-in adapters, never silent fallbacks.
3. **One pilot channel, human approval.** The first release produces for a single GTA 6
   pilot channel with `ip_policy_mode = strict_third_party_ip`. Every episode requires
   operator approval; uploads and publishing remain disabled by default. Rights
   clearance for underlying game/film/music IP is never inferred from credit,
   permission to record, or an AI fair-use opinion.

## Consequences

- Simpler local operation and debugging than microservices; one Compose stack.
- Module boundaries must be enforced by review and tests because they are in-process.
- Provider adapters require mock implementations so phase gates can run offline.
- Scaling to multiple channels changes data and quotas, not the architecture.
- Multi-channel, multi-niche operation remains a later phase (Phase 12); the pilot is
  intentionally narrow.
