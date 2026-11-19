# ShortsFactory AI

A local-first, niche-agnostic AI-assisted YouTube Shorts production system. The first pilot is GTA 6 / gaming commentary, with original scripts, source evidence, rights-cleared assets, human review, and private-first publishing.

## Authoritative documents

1. [`SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md`](SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md) — product specification and 14 sequential implementation phases (Phase 0–13).
2. [`AGENTS.md`](AGENTS.md) — shared persistent instructions for Antigravity, OpenCode, Codex, and other agents.
3. [`docs/MULTI_AGENT_DEVELOPMENT_PROTOCOL.md`](docs/MULTI_AGENT_DEVELOPMENT_PROTOCOL.md) — sequential agent ownership, handoff, Git workflow, Codex review points, and test evidence.
4. [`docs/phase-status.md`](docs/phase-status.md) — current acceptance-gate ledger.
5. [`docs/agent-handoff.md`](docs/agent-handoff.md) — current handoff record/template.

## First steps

This repository starter kit does not contain application code yet. Begin with Phase 0 only. Do not scaffold the application until the repository audit and Phase 0 gate have passed.

```bash
git status --short --branch
```

Then open the repository in Antigravity or start OpenCode from the repository root. Both should load the root `AGENTS.md`. Antigravity also supports workspace rules through `AGENTS.md`; OpenCode loads project `AGENTS.md` instructions. Codex should be given the same file and blueprint when it performs a review.

## Development model

Antigravity implements first. When its usage is unavailable, it writes a handoff and OpenCode continues from the same working tree. Codex is reserved for independent milestone audits. Only one agent may edit the shared checkout at a time. See `docs/MULTI_AGENT_DEVELOPMENT_PROTOCOL.md`.

## Safety defaults

The first release is dry-run and human-approved. Public publishing is disabled. Never commit secrets, API keys, OAuth credentials, media, or private rights documents. Never download or repost creator videos without a proper rights basis.
