# Operations Runbook (Phase 1 scaffold)

## Start and stop

```bash
make env      # creates .env from .env.example if missing
make dev      # build and start postgres, redis, api, worker, web
make logs     # follow logs
make down     # stop containers; PostgreSQL/Redis volumes are preserved
```

`make reset` is destructive: it asks for the literal confirmation
`delete-local-data` before running `docker compose down -v`.

## Health

- API: <http://localhost:8000/api/health> (public, structured JSON)
- API docs: <http://localhost:8000/api/docs>
- Dashboard: <http://localhost:3000> (sign in with `ADMIN_PASSWORD`)

`/api/health` reports `status: ok` only when PostgreSQL and Redis respond. A degraded
response is still HTTP 200 so the dashboard can render partial connectivity; inspect
`checks.database` and `checks.queue`.

## Common failures

| Symptom | Check |
|---|---|
| API exits on startup | `.env` missing or invalid; the error names the field but never prints secret values. |
| `database: ConnectionError` | `docker compose ps postgres`; confirm `DATABASE_URL` host is `postgres` inside Compose. |
| `queue: ConnectionError` | `docker compose ps redis`; confirm `REDIS_URL`. |
| Dashboard shows "API status unavailable" | API container unhealthy; `docker compose logs api`. |
| Login always fails | `ADMIN_PASSWORD` in `.env` differs from what you typed; restart API after editing `.env`. |
| Port already in use | Change the published port in `docker-compose.yml`; do not run two stacks at once. |

## Logs and evidence

- Keep `make verify` output with the phase evidence. It includes the live smoke test.
- Do not include `.env`, cookies, tokens or private media in logs or commits.
- Phase 2 adds migrations and the pilot seed; `make migrate` and `make seed-pilot`
  currently print an explanatory notice and change nothing.
