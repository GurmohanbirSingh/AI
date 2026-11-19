export type CheckStatus = "ok" | "error";

export interface ServiceCheck {
  ok: boolean;
  status: CheckStatus;
  latency_ms: number;
  detail: string;
}

export interface Providers {
  llm: string;
  tts: string;
  alignment: string;
}

export interface Safety {
  dry_run: boolean;
  upload_enabled: boolean;
  publish_enabled: boolean;
  approval_required: boolean;
  global_emergency_stop: boolean;
}

export interface Health {
  status: "ok" | "degraded";
  service: string;
  version: string;
  environment: string;
  checked_at: string;
  checks: Record<string, ServiceCheck>;
  providers: Providers;
  safety: Safety;
}

export interface Operator {
  authenticated: boolean;
  subject: string;
  csrf_token: string;
  auth_required: boolean;
}

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    return typeof body.detail === "string" ? body.detail : `HTTP ${response.status}`;
  } catch {
    return `HTTP ${response.status}`;
  }
}

export async function fetchHealth(): Promise<Health> {
  const response = await fetch("/api/health", { credentials: "include", cache: "no-store" });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as Health;
}

export async function fetchOperator(): Promise<Operator | null> {
  const response = await fetch("/api/auth/me", {
    credentials: "include",
    cache: "no-store",
  });
  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as Operator;
}

export async function login(password: string): Promise<Operator> {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as Operator;
}

export async function logout(csrfToken: string): Promise<void> {
  const response = await fetch("/api/auth/logout", {
    method: "POST",
    credentials: "include",
    headers: { "X-CSRF-Token": csrfToken },
  });
  if (!response.ok && response.status !== 401) {
    throw new Error(await readError(response));
  }
}

export function healthSummary(health: Health): string {
  return health.status === "ok" ? "All core services healthy" : "One or more services degraded";
}

export function checkLabel(check: ServiceCheck | undefined): string {
  if (!check) {
    return "not reported";
  }
  return check.ok ? `ok (${check.latency_ms} ms)` : `error${check.detail ? `: ${check.detail}` : ""}`;
}

export function providerMode(value: string): string {
  switch (value) {
    case "mock":
      return "mock (deterministic, offline)";
    case "ollama":
      return "local Ollama";
    case "openrouter":
      return "OpenRouter (external)";
    case "kokoro":
      return "local Kokoro TTS";
    case "piper":
      return "local Piper TTS";
    case "whisperx":
      return "local WhisperX alignment";
    case "faster-whisper":
      return "faster-whisper (ASR estimates)";
    case "api":
      return "external TTS API";
    default:
      return value;
  }
}
