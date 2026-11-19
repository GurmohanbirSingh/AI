# Multi-Agent Development Protocol

**Applies to:** Antigravity, OpenCode, Codex, and the operator's local terminal.

**Project:** ShortsFactory AI  
**Canonical product spec:** `SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md`

## 1. Operating model

Use Antigravity and OpenCode as sequential implementation agents. Use Codex primarily as an independent reviewer because its available usage is more limited. Use the local terminal as the repeatable test executor and GitHub as the durable project history.

| Tool | Default role | Not its default role |
|---|---|---|
| Antigravity | Primary implementation agent until usage is unavailable | Independent final authority on its own work |
| OpenCode | Continue implementation from the saved repository state and handoff | Rebuild from scratch or overwrite Antigravity's work |
| Codex | Read-only architecture, security, policy, and test-evidence review | Routine implementation or broad rewrites |
| Local terminal | Run lint, type checks, unit/integration/e2e tests and inspect media artefacts | Infer that tests pass without executing them |
| GitHub | Store commits, branches, issues and reviewable diffs | Store secrets, media dumps, or private licence evidence |

The operator may change these assignments, but must record the change in `docs/decisions/`.

## 2. Sequential ownership — no simultaneous edits

Only one agent may have write ownership of the shared working tree at a time.

Recommended cycle:

1. Antigravity takes the current phase and implements it.
2. When it reaches a usage limit or the operator chooses to switch, Antigravity performs the handoff in Section 3.
3. OpenCode inspects the handoff, Git state, and actual diff, then continues the same phase.
4. The active implementation agent runs the phase's required tests and records the results.
5. Once the phase gate passes, commit the phase checkpoint.
6. Codex reviews the completed phase at the review checkpoints in Section 5.
7. If Codex finds defects, the implementation agent fixes them, reruns tests, and records the remediation. Codex is not permitted to silently change the implementation during a read-only audit.
8. Start the next phase only after the gate permits it.

Do not have Antigravity and OpenCode edit the same checkout concurrently. Parallel work is permitted only in separate Git worktrees/branches with explicitly disjoint file ownership and an integration plan. Avoid parallelism during the early phases.

## 3. Required handoff procedure

Before switching agents, the outgoing agent must:

- Stop taking new tasks and wait for any current write operation to finish or stop it safely.
- Update `docs/agent-handoff.md` using the template already in that file.
- Update `docs/phase-status.md` with real results and the current gate state.
- Record the current branch, HEAD commit, `git status --short`, and a concise diff summary.
- List every uncommitted file and explain whether it is complete, partial, or generated.
- Record exact commands run, exit codes, failures, skipped tests, and tests not yet run.
- Identify the next smallest actionable task.
- Never discard user work or use destructive Git commands to make the tree look clean.

The incoming agent must:

1. Read `AGENTS.md`, this protocol, the blueprint, `docs/phase-status.md`, and `docs/agent-handoff.md`.
2. Run `git status --short --branch` and `git log -1 --oneline`.
3. Inspect all changes named in the handoff using `git diff` and relevant file reads.
4. Verify that the described tests/results are plausible from the recorded output; rerun relevant tests when practical.
5. Continue the current phase. Do not silently change scope or start a later phase.
6. Replace the handoff contents at the next handoff, rather than appending stale instructions indefinitely.

A handoff is not a phase gate. Work remains `IN_PROGRESS`, `FAIL`, or `BLOCKED_EXTERNAL_SETUP` until the acceptance conditions in the blueprint are met.

## 4. Git strategy

Use the default branch (initially `main`) for the clean project baseline. Use one feature branch per phase:

- `phase/0-repository-audit`
- `phase/1-scaffold`
- `phase/2-domain-database-api`
- continue following the blueprint's phase names.

For each phase:

1. Create the branch from the latest accepted checkpoint.
2. Make changes only for that phase.
3. Run `git diff --check`, inspect `git diff --stat`, and inspect `git status`.
4. Commit only after the phase gate passes. Use a conventional commit such as `feat(phase-2): add core domain and migrations`.
5. Merge to `main` only after review and successful verification.

If an agent must hand off an incomplete phase, it may leave the work in the same local branch and working tree. Do not merge it to `main`. A checkpoint commit may be used to preserve unfinished work, but it must be clearly labelled `wip` and must not be represented as a passed phase.

Never force-push, reset shared history, or remove files to resolve an agent conflict without operator approval.

## 5. Codex review checkpoints

Codex is best spent on targeted audits after these milestones:

| Review point | Review scope |
|---|---|
| After Phase 0 | Is the repository audit accurate? Are there unresolved spec conflicts? |
| After Phase 2 | Schema integrity, migration safety, API contracts, auth boundaries, state machine and audit records |
| After Phase 4 | Evidence traceability, unsupported claims, prompt injection, script originality and provider failure behaviour |
| After Phase 5 | Rights-layer modelling, commercial rights checks, backend enforcement and bypass tests |
| After Phase 8 | FFmpeg safety, output integrity, caption alignment, loudness measurement and render manifests |
| After Phase 10 | OAuth/CSRF, secret encryption, private-only uploads, quota handling, idempotency and synthetic-media metadata |
| After Phase 11 | Analytics correctness, metric definitions and unsupported conclusions |
| After Phase 13 | Security, backup/restore, observability, release blockers and full acceptance evidence |

For each Codex audit, provide:

- The full blueprint (or explicitly identify the relevant sections, while keeping the full file available).
- `AGENTS.md` and this protocol.
- `docs/phase-status.md` and the current handoff.
- `git diff <last-accepted-commit>...HEAD` or the exact current diff.
- Relevant test logs, not just a statement that tests passed.

Ask Codex to produce a prioritised audit with file/line references, severity, reproducible reasoning, and suggested tests. Request read-only review; do not ask it to rewrite the product. Store the response as `docs/audits/phase-XX-codex-review.md`. The implementation agent owns remediation.

Codex review is an additional check, not a substitute for the blueprint's required automated tests or operator rights review.

## 6. Test and evidence rules

- Run the exact commands declared by the current phase in the blueprint and the repository's `Makefile`/README once they exist.
- Capture actual exit codes and meaningful test summaries.
- Identify skipped tests and their reasons. A suite with skipped critical tests is not automatically a pass.
- Use deterministic mocks for LLMs, TTS, stock libraries, OAuth, and YouTube in automated tests.
- Mark absent credentials, licenses, downloaded models, or Docker availability as `BLOCKED_EXTERNAL_SETUP` where appropriate.
- Never call a mocked test a live integration test.
- Media QC must inspect generated files with the actual tools (e.g. `ffprobe`); a mocked renderer test does not prove FFmpeg output is correct.
- Rights checks must be verified through backend/API tests, not only disabled UI buttons.

## 7. Usage conservation

- Do not ask every agent to reread or regenerate broad implementation plans on every session. Use the phase status and handoff to focus work.
- Antigravity/OpenCode should implement the current phase and write concise evidence as they go.
- Codex prompts should be narrow, evidence-based audits at the checkpoints above.
- Prefer local deterministic tests and local models for development; never switch to paid APIs silently.
- A usage limit is a handoff trigger, not permission to skip verification.

## 8. Global stop conditions

Stop and report rather than guessing when:

- The blueprint conflicts with existing repository behaviour or a library's verified API.
- A required commercial licence or rights-holder permission is unclear.
- A security-sensitive API behaviour cannot be verified.
- A migration risks user data or a destructive command is required.
- Required tests fail and the cause is not understood.
- A model/provider is unavailable and the fallback would incur a cost or change data handling.

Do not publish public videos, change live channel settings, or spend money. Any production-side action requires explicit operator approval.
