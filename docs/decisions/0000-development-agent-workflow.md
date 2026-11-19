# ADR 0000 — Development agent workflow

- **Status:** Accepted for initial repository setup
- **Decision:** Use Antigravity and OpenCode sequentially for implementation, Codex primarily for independent milestone reviews, the local terminal for test execution, and GitHub for durable checkpoints.
- **Reason:** Preserve limited agent usage for implementation while maintaining independent review and reproducible test evidence.
- **Guardrails:** One writer at a time; mandatory handoff records; phase-gated implementation; no public uploads or paid services without explicit approval.
- **Revisit when:** Agent quotas, product scope, repository contributors, or tool capabilities materially change.
