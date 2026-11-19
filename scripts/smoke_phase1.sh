#!/usr/bin/env bash
# Phase 1 live smoke test: boots the Compose stack and verifies health, auth,
# the web proxy, and that the safety defaults are exposed correctly.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "FAIL: .env is missing. Run 'make env' first." >&2
  exit 1
fi

admin_password="$(grep -E '^ADMIN_PASSWORD=' .env | head -1 | cut -d= -f2-)"
if [ -z "${admin_password}" ]; then
  echo "FAIL: ADMIN_PASSWORD is empty in .env" >&2
  exit 1
fi

cookie_jar="$(mktemp)"
login_body="$(mktemp)"
trap 'rm -f "${cookie_jar}" "${login_body}"' EXIT

step() { echo "== $*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

step "Starting stack (build if needed) and waiting for health checks"
docker compose up -d --build --wait

step "API health endpoint is public and healthy"
health="$(curl -fsS http://localhost:8000/api/health)" || fail "API health request failed"
echo "${health}" | grep -q '"status":"ok"' || fail "API health is not ok: ${health}"
echo "${health}" | grep -q '"database":{"ok":true' ||
  fail "database check did not report ok: ${health}"
echo "${health}" | grep -q '"queue":{"ok":true' || fail "queue check did not report ok: ${health}"
echo "${health}" | grep -q '"llm":"mock"' || fail "LLM provider is not mock by default"

step "Protected route rejects unauthenticated requests"
status="$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/dashboard)"
[ "${status}" = "401" ] || fail "expected 401 for anonymous dashboard, got ${status}"

step "Login through the web proxy sets a session"
status="$(curl -s -o "${login_body}" -w '%{http_code}' \
  -c "${cookie_jar}" \
  -H 'Content-Type: application/json' \
  -d "{\"password\":\"${admin_password}\"}" \
  http://localhost:3000/api/auth/login)"
[ "${status}" = "200" ] || fail "login failed with HTTP ${status}"
csrf="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["csrf_token"])' "${login_body}")"
[ -n "${csrf}" ] || fail "login response did not include a CSRF token"

step "Authenticated session can read dashboard status through the proxy"
curl -fsS -b "${cookie_jar}" http://localhost:3000/api/dashboard |
  grep -q '"operators_authenticated":true' || fail "dashboard did not return an authenticated state"

step "Web app serves the operator shell"
curl -fsS http://localhost:3000 | grep -q 'ShortsFactory' || fail "web app did not render"

step "Logout requires CSRF and succeeds with it"
status="$(curl -s -o /dev/null -w '%{http_code}' -b "${cookie_jar}" -X POST \
  http://localhost:3000/api/auth/logout)"
[ "${status}" = "403" ] || fail "logout without CSRF expected 403, got ${status}"
status="$(curl -s -o /dev/null -w '%{http_code}' -b "${cookie_jar}" -X POST \
  -H "X-CSRF-Token: ${csrf}" http://localhost:3000/api/auth/logout)"
[ "${status}" = "204" ] || fail "logout with CSRF expected 204, got ${status}"

step "PASS: Phase 1 live smoke test"
docker compose ps
