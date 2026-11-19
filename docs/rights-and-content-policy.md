# Rights and Content Policy (working baseline)

This is a working summary of **Part A** of `SHORTSFACTORY_CODEX_BLUEPRINT_v1.2.md`.
The blueprint and verified platform terms remain authoritative. No automated test in
this repository can replace operator rights review.

## Non-negotiables

- Never download or re-upload another creator's YouTube or social video. Feed metadata
  does not grant media rights.
- Credit, creator permission for a recording, or an AI fair-use opinion does **not**
  clear underlying game, film, music or other third-party IP.
- Unknown, expired, disputed, test-fixture or non-commercial-only assets must be
  blocked by the backend rights gate, not merely hidden in the UI.
- Do not present synthetic voice or imagery as real. Disclose synthetic media in
  YouTube metadata when required.
- The first release is dry-run, human-approved, private-first and non-public.

## Publishing boundaries

- Automated tests must mock uploads. No public upload in any automated test.
- A live upload requires explicit operator approval, private visibility and recorded
  evidence in `docs/phase-status.md`.
- YouTube quota values must be re-verified in Google Cloud Console before launch.

## Data handling

- Never commit `.env`, OAuth files, tokens, API keys, private rights documents or
  generated media.
- Keep private rights evidence in a configurable protected storage path.

## Pilot

The first pilot channel uses `ip_policy_mode = strict_third_party_ip`. Original scripts,
source evidence, rights-cleared assets and programmatic graphics are required; the
pilot does not rely on reused footage.
