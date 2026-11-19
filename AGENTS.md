# ShortsFactory AI — shared agent instructions

These instructions apply to Antigravity, OpenCode, Codex, and any other coding agent working in this repository.

## Read before acting

1. Read this file completely.
2. Read `SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md` completely before implementing or reviewing product work.
3. Read `docs/MULTI_AGENT_DEVELOPMENT_PROTOCOL.md` before taking over work from another agent.
4. Read `docs/phase-status.md` and `docs/agent-handoff.md` before changing files.
5. Inspect `git status --short --branch` before every work session. Preserve all existing user changes.

## Product source of truth

- `SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md` is the product and technical specification.
- `docs/MULTI_AGENT_DEVELOPMENT_PROTOCOL.md` defines how agents share implementation, review, testing, and handoffs.
- If these documents conflict, do not guess. Record the conflict in `docs/decisions/`, explain the affected requirement, and stop before implementing the disputed behaviour.

## Mandatory phase gates

- Work on exactly one numbered phase at a time, in blueprint order (Phase 0 through Phase 13).
- Do not implement features from later phases early, even if they appear easy.
- A phase is complete only when its required tests have actually run and its acceptance criteria are satisfied.
- Record exact commands, outcomes, skipped tests, external blockers, changed files, and remaining limitations in `docs/phase-status.md`.
- `BLOCKED_EXTERNAL_SETUP` is not the same as `PASS`. Continue only where the blueprint explicitly permits offline work; keep the external dependency visible as a release blocker.
- On `FAIL`, remain in the current phase and fix the issue. Never weaken a test merely to make the gate pass.
- Never claim a test, integration, licence, or external account was verified unless it was actually checked.

## Agent responsibilities

- **Antigravity:** primary implementation agent while available.
- **OpenCode:** continuation implementation agent when Antigravity usage is unavailable, or when explicitly assigned an isolated task.
- **Codex:** independent reviewer/auditor by default. Do not use Codex for routine implementation unless the operator explicitly asks. Audits should be read-only and produce a report under `docs/audits/`.
- **Terminal/test runner:** the source of truth for executed test results. Agents may run commands, but must report the actual output and exit status.
- **GitHub:** durable source-control history and phase checkpoints. One agent at a time may modify the shared working tree.

## Handoff rules

Before handing work to another agent:

1. Stop starting new tasks.
2. Finish or safely stop running commands; do not leave a renderer, migration, or test process mutating files in the background.
3. Update `docs/agent-handoff.md` with the exact phase, task, files changed, commands run, test results, uncommitted changes, blockers, and next action.
4. Update `docs/phase-status.md` if phase status or evidence changed.
5. Record `git status --short --branch` and the current commit hash in the handoff.
6. Do not discard uncommitted changes. Do not run `git reset --hard`, `git clean -fd`, or destructive cleanup unless the operator explicitly approves it.
7. Tell the next agent whether the working tree is clean or dirty. The next agent must inspect it before editing.

The next agent must read the handoff, inspect the diff and Git status, verify the described state, and continue the same phase. It must not restart, overwrite, or assume the previous agent's work is correct without inspection.

## Git discipline

- Use one shared working tree sequentially; never let two agents edit the same checkout concurrently.
- Prefer a branch per implementation phase, e.g. `phase/0-repository-audit`, `phase/1-scaffold`.
- Commit only after the relevant tests and phase gate pass. Use a clearly labelled checkpoint commit for incomplete work only when needed to preserve a handoff; never mark it as a completed phase.
- Do not force-push, rewrite shared history, delete branches, or push secrets.
- Before every commit, inspect `git diff --check`, `git diff --stat`, and `git status`.

## Safety and security

- Keep `DRY_RUN=true`, `UPLOAD_ENABLED=false`, `PUBLISH_ENABLED=false`, `APPROVAL_REQUIRED=true` by default.
- Never make a public YouTube upload. All upload tests must be mocked. Any live upload requires explicit operator approval and must be private.
- Never download or re-upload another creator's YouTube/social video. Metadata/feed discovery does not grant media rights.
- Never treat credit, creator permission for a recording, or an AI-generated fair-use opinion as clearance for underlying game/film/music IP.
- Never allow unknown, expired, disputed, test-fixture, or non-commercial-only assets through the backend rights gate.
- Never invent facts, sources, API behaviour, test outcomes, quota availability, licences, or monetisation eligibility.
- Never commit `.env`, OAuth files, tokens, API keys, private rights documents, or generated media.
- Keep subprocess calls argument-based (`shell=False`); apply SSRF protections to fetched URLs.
- Do not add a paid service, model, API, or infrastructure dependency without recording the cost and receiving operator approval.

## Engineering rules

- Preserve existing architecture and changes; inspect before refactoring.
- Prefer the modular-monolith approach specified in the blueprint.
- Keep provider integrations behind interfaces and supply deterministic mocks.
- Make background jobs durable, bounded, observable, and idempotent where possible.
- Do not add non-working UI controls.
- Do not use Bun. Use standard Node.js/npm unless the repository's existing, documented architecture requires otherwise.
- Pin dependencies and commit lockfiles.
- Write tests with the implementation, not afterwards.
- Do not silently substitute another model/provider when a configured provider fails.

## Required end-of-session report

Every agent session that changes or reviews the repository must report:

- Current phase and status (`NOT_STARTED`, `IN_PROGRESS`, `PASS`, `FAIL`, or `BLOCKED_EXTERNAL_SETUP`).
- Files changed.
- Commands actually run and concise results.
- Tests passed/failed/skipped.
- External services mocked versus live-verified.
- Git branch, commit, and working-tree state.
- Blockers and the single next action.
