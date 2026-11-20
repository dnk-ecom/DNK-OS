// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/tests/aimock/setup.ts"
// purpose: "Zero-dependency deterministic test harness using @copilotkit/aimock for isolated Vitest & CI execution."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { LLMock, MCPMock } from "@copilotkit/aimock";

export interface MockHarness {
  llm: LLMock;
  mcp?: MCPMock;
  url: string;
  stop: () => Promise<void>;
}

/**
 * Initializes an isolated in-memory LLMock server on an ephemeral port.
 * Zero network calls, zero external API keys.
 */
export async function startAIMockHarness(options?: {
  fixtures?: any[];
  port?: number;
}): Promise<MockHarness> {
  const llm = new LLMock({
    port: options?.port ?? 0,
  });

  if (options?.fixtures && options.fixtures.length > 0) {
    llm.addFixtures(options.fixtures);
  }

  await llm.start();
  const url = llm.url;

  // Intercept environment variables for SDKs
  const originalOpenAIBase = process.env.OPENAI_BASE_URL;
  const originalOpenAIKey = process.env.OPENAI_API_KEY;

  process.env.OPENAI_BASE_URL = `${url}/v1`;
  process.env.OPENAI_API_KEY = "mock-key-dnk-ci";

  const stop = async () => {
    await llm.stop();
    if (originalOpenAIBase !== undefined) {
      process.env.OPENAI_BASE_URL = originalOpenAIBase;
    } else {
      delete process.env.OPENAI_BASE_URL;
    }
    if (originalOpenAIKey !== undefined) {
      process.env.OPENAI_API_KEY = originalOpenAIKey;
    } else {
      delete process.env.OPENAI_API_KEY;
    }
  };

  return {
    llm,
    url,
    stop,
  };
}
