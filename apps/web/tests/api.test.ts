import { describe, expect, it } from "vitest";

import {
  checkLabel,
  healthSummary,
  providerMode,
  type Health,
  type ServiceCheck,
} from "../lib/api";

const okCheck: ServiceCheck = { ok: true, status: "ok", latency_ms: 7, detail: "" };

function health(overrides: Partial<Health> = {}): Health {
  return {
    status: "ok",
    service: "shortsfactory-api",
    version: "0.1.0",
    environment: "test",
    checked_at: "2026-01-01T00:00:00Z",
    checks: { database: okCheck, queue: okCheck },
    providers: { llm: "mock", tts: "mock", alignment: "mock" },
    safety: {
      dry_run: true,
      upload_enabled: false,
      publish_enabled: false,
      approval_required: true,
      global_emergency_stop: false,
    },
    ...overrides,
  };
}

describe("health summary", () => {
  it("reports healthy status", () => {
    expect(healthSummary(health())).toBe("All core services healthy");
  });

  it("reports degraded status", () => {
    expect(healthSummary(health({ status: "degraded" }))).toBe(
      "One or more services degraded",
    );
  });
});

describe("check labels", () => {
  it("includes latency for healthy checks", () => {
    expect(checkLabel(okCheck)).toBe("ok (7 ms)");
  });

  it("includes a sanitised error detail", () => {
    expect(
      checkLabel({ ok: false, status: "error", latency_ms: 0, detail: "ConnectionError" }),
    ).toBe("error: ConnectionError");
  });

  it("handles a missing check", () => {
    expect(checkLabel(undefined)).toBe("not reported");
  });
});

describe("provider modes", () => {
  it("labels the mock and local modes", () => {
    expect(providerMode("mock")).toContain("offline");
    expect(providerMode("ollama")).toContain("local");
    expect(providerMode("whisperx")).toContain("local");
  });

  it("passes unknown values through", () => {
    expect(providerMode("custom")).toBe("custom");
  });
});
