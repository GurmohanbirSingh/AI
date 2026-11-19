"use client";

import { useCallback, useEffect, useState } from "react";

import {
  checkLabel,
  fetchHealth,
  fetchOperator,
  healthSummary,
  login,
  logout,
  providerMode,
  type Health,
  type Operator,
} from "@/lib/api";

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-block h-2.5 w-2.5 rounded-full ${ok ? "bg-emerald-400" : "bg-rose-400"}`}
      aria-hidden="true"
    />
  );
}

export function Dashboard() {
  const [health, setHealth] = useState<Health | null>(null);
  const [operator, setOperator] = useState<Operator | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [password, setPassword] = useState("");

  const refresh = useCallback(async () => {
    try {
      const [healthResult, operatorResult] = await Promise.all([
        fetchHealth(),
        fetchOperator().catch(() => null),
      ]);
      setHealth(healthResult);
      setOperator(operatorResult);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to reach the API");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function onLogin(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const session = await login(password);
      setOperator(session);
      setPassword("");
      await refresh();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  async function onLogout() {
    if (!operator) {
      return;
    }
    setBusy(true);
    try {
      await logout(operator.csrf_token);
      setOperator(null);
      await refresh();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Sign-out failed");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return <div className="card text-sm text-slate-400">Loading service status…</div>;
  }

  const signedIn = operator?.authenticated === true;

  return (
    <div className="grid gap-6">
      {error ? (
        <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      ) : null}

      <section className="card">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">Operator session</h2>
            <p className="mt-1 text-sm text-slate-400">
              {signedIn
                ? `Signed in as ${operator?.subject ?? "operator"}.`
                : "Sign in with the local ADMIN_PASSWORD. The health endpoint stays public."}
            </p>
          </div>
          {signedIn ? (
            <button
              type="button"
              onClick={() => void onLogout()}
              disabled={busy}
              className="rounded-lg border border-white/15 px-4 py-2 text-sm hover:border-accent/60 disabled:opacity-50"
            >
              Sign out
            </button>
          ) : null}
        </div>

        {!signedIn && health?.status ? (
          <form onSubmit={onLogin} className="mt-5 flex flex-col gap-3 sm:flex-row">
            <label className="flex-1 text-sm">
              <span className="sr-only">Operator password</span>
              <input
                type="password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="ADMIN_PASSWORD"
                className="w-full rounded-lg border border-white/15 bg-black/30 px-4 py-2 text-sm outline-none focus:border-accent"
              />
            </label>
            <button
              type="submit"
              disabled={busy || password.length === 0}
              className="rounded-lg bg-accent px-5 py-2 text-sm font-semibold text-ink disabled:opacity-50"
            >
              {busy ? "Signing in…" : "Sign in"}
            </button>
          </form>
        ) : null}

        {signedIn && operator && !operator.auth_required ? (
          <p className="mt-4 text-xs text-amber-300">
            AUTH_REQUIRED=false (local test mode). Do not use this setting for operator
            sessions.
          </p>
        ) : null}
      </section>

      {health ? (
        <>
          <section className="card">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Service connectivity</h2>
                <p className="mt-1 text-sm text-slate-400">
                  {healthSummary(health)} · API {health.version} · {health.environment}
                </p>
              </div>
              <span className="pill">
                <StatusDot ok={health.status === "ok"} />
                {health.status === "ok" ? "healthy" : "degraded"}
              </span>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              {Object.entries(health.checks).map(([name, check]) => (
                <div
                  key={name}
                  className="rounded-xl border border-white/10 bg-black/20 px-4 py-3"
                >
                  <div className="flex items-center justify-between text-sm font-medium">
                    <span className="capitalize">{name}</span>
                    <StatusDot ok={check.ok} />
                  </div>
                  <p className="mt-2 text-xs text-slate-400">{checkLabel(check)}</p>
                </div>
              ))}
            </div>
          </section>

          <div className="grid gap-6 md:grid-cols-2">
            <section className="card">
              <h2 className="text-lg font-semibold">Active provider modes</h2>
              <dl className="mt-4 space-y-3 text-sm">
                {(
                  [
                    ["LLM", health.providers.llm],
                    ["TTS", health.providers.tts],
                    ["Alignment", health.providers.alignment],
                  ] as const
                ).map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between gap-4">
                    <dt className="text-slate-400">{label}</dt>
                    <dd className="text-right font-medium">{providerMode(value)}</dd>
                  </div>
                ))}
              </dl>
            </section>

            <section className="card">
              <h2 className="text-lg font-semibold">Safety switches</h2>
              <dl className="mt-4 space-y-3 text-sm">
                {(
                  [
                    ["Dry run", health.safety.dry_run],
                    ["Uploads enabled", health.safety.upload_enabled],
                    ["Publishing enabled", health.safety.publish_enabled],
                    ["Approval required", health.safety.approval_required],
                    ["Emergency stop", health.safety.global_emergency_stop],
                  ] as const
                ).map(([label, enabled]) => (
                  <div key={label} className="flex items-center justify-between gap-4">
                    <dt className="text-slate-400">{label}</dt>
                    <dd
                      className={enabled ? "font-medium text-accent" : "font-medium text-slate-300"}
                    >
                      {enabled ? "on" : "off"}
                    </dd>
                  </div>
                ))}
              </dl>
            </section>
          </div>
        </>
      ) : (
        <section className="card text-sm text-slate-400">
          API status unavailable. Start the stack with <code>make dev</code>.
        </section>
      )}
    </div>
  );
}
