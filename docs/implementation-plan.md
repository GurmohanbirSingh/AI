# Implementation Plan

The authoritative phase list is **Part E** of `SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md`.
Work proceeds in strict order. No phase starts until the previous gate passes or is
explicitly recorded as `BLOCKED_EXTERNAL_SETUP` with offline work permitted.

| Phase | Name | Gate |
|---|---|---|
| 0 | Repository audit, requirements baseline and execution rules | A new developer can understand the repository, product boundary, architecture and phase sequence without guessing. |
| 1 | Project scaffold, developer environment and health checks | Clone, configure local variables, run documented commands, open the dashboard, sign in, see API/database/queue health with no paid credentials. |
| 2 | Database, migrations, core domain and API skeleton | Seed the pilot channel, create topics/episodes/jobs, inspect state and audit trail, reject illegal transitions. |
| 3 | Topic discovery and trend-signal ingestion | Allowlisted feeds and manual entry produce deduplicated candidate topics with evidence links; network failures are bounded and observable. |
| 4 | Research packets and evidence-grounded script generation | Every claim maps to evidence; prompt-injection and unsupported-claim cases are rejected; provider failures fall back only as specified. |
| 5 | Rights ledger and publication eligibility gate | Backend blocks assets without valid, current, commercial rights; bypass attempts fail. |
| 6 | Asset library, graphics, scene planning and visual selection | Rights-cleared assets and original graphics produce a deterministic scene plan. |
| 7 | Local-first AI voice and word-level caption alignment | Mock and local TTS produce audio; alignment emits word timings with documented accuracy. |
| 8 | Video rendering, loudness normalisation, captions and thumbnails | Render produces a valid Short meeting defined QC checks and a reproducible manifest. |
| 9 | Editorial studio, review dashboard, auth and approval workflow | Operator can review and approve/reject an episode end to end; no non-working controls. |
| 10 | YouTube OAuth, private upload, disclosure metadata and scheduling | Mocked upload tests pass; any live test is private and operator-approved. |
| 11 | Analytics ingestion and learning loop | Metrics import is cited, bounded and reproducible; conclusions are clearly labelled. |
| 12 | Multi-channel, multi-niche orchestration, budgets and safe scaling | Additional niche channels work with zero code changes and enforced caps. |
| 13 | Production hardening and release readiness | Security, backup/restore, observability and release blockers are verified and documented. |

## Cross-phase rules

- Record exact commands, exit codes, test totals, skipped tests and blockers in
  `docs/phase-status.md`.
- Only mocked uploads in automated tests. Never publish publicly without explicit
  operator approval.
- Keep `DRY_RUN=true`, `UPLOAD_ENABLED=false`, `PUBLISH_ENABLED=false` and
  `APPROVAL_REQUIRED=true` as defaults.
- Do not add paid dependencies without recorded cost and operator approval.
- Commit only after the current phase gate passes; checkpoint commits for incomplete
  work must be clearly labelled `wip`.

## Phase 0 follow-up

The Phase 0 commit did not include `docs/architecture.md`,
`docs/implementation-plan.md`, or ADR 0001. They were added during the Phase 1
scaffold session and are recorded in the Phase 1 evidence log.
