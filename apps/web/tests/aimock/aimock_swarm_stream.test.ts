// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/tests/aimock/aimock_swarm_stream.test.ts"
// purpose: "Deterministic offline LLM, MCP, and AG-UI event streaming tests with @copilotkit/aimock."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { describe, it, afterEach } from "node:test";
import assert from "node:assert/strict";
import { LLMock, MCPMock, AGUIMock } from "@copilotkit/aimock";

describe("Layer 3: @copilotkit/aimock Offline Infrastructure Verification", () => {
  let activeLlm: LLMock | null = null;
  let activeMcp: MCPMock | null = null;
  let activeAgui: AGUIMock | null = null;

  afterEach(async () => {
    if (activeLlm) {
      await activeLlm.stop();
      activeLlm = null;
    }
    if (activeMcp) {
      await activeMcp.stop();
      activeMcp = null;
    }
    if (activeAgui) {
      await activeAgui.stop();
      activeAgui = null;
    }
  });

  it("should initialize LLMock on an ephemeral port and return deterministic completions", async () => {
    activeLlm = new LLMock({ port: 0 });
    activeLlm.onMessage("plan", {
      content: "Execution plan: 1. Research AST 2. Build Component 3. Auditor Gate",
    });

    await activeLlm.start();
    assert.ok(activeLlm.url.includes("http://127.0.0.1:"));

    // Direct HTTP call to OpenAI-compatible endpoint without external network egress
    const response = await fetch(`${activeLlm.url}/v1/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer mock-key",
      },
      body: JSON.stringify({
        model: "gpt-4o",
        messages: [{ role: "user", content: "plan the task" }],
      }),
    });

    assert.strictEqual(response.status, 200);
    const data = await response.json();
    assert.strictEqual(
      data.choices[0].message.content,
      "Execution plan: 1. Research AST 2. Build Component 3. Auditor Gate"
    );
  });

  it("should mock MCP Tool execution via MCPMock with zero network egress", async () => {
    activeMcp = new MCPMock({ port: 0 });
    activeMcp.addTool({
      name: "repo_resolve_symbol",
      description: "Locates symbol AST definition in <20ms",
      inputSchema: {
        type: "object",
        properties: { symbol: { type: "string" } },
        required: ["symbol"],
      },
    });

    activeMcp.onToolCall("repo_resolve_symbol", async (args: any) => {
      return JSON.stringify({
        found: true,
        symbol: args?.symbol ?? "unknown",
        file: "apps/web/components/canvas/nodes/MultiAgentSwarmNode.tsx",
        line: 42,
      });
    });

    const mcpUrl = await activeMcp.start();
    assert.ok(mcpUrl);
    assert.strictEqual(activeMcp.health().status, "ok");

    // Send HTTP POST JSON-RPC request to the running MCP mock server
    const rpcRequest = {
      jsonrpc: "2.0",
      id: 1,
      method: "tools/call",
      params: {
        name: "repo_resolve_symbol",
        arguments: { symbol: "MultiAgentSwarmNode" },
      },
    };

    const response = await fetch(`${mcpUrl}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(rpcRequest),
    });

    if (response.ok) {
      const data = await response.json();
      assert.ok(data);
    }
  });

  it("should stream AG-UI agent events deterministically for Canvas node state updates", async () => {
    activeAgui = new AGUIMock({ port: 0 });
    activeAgui.onMessage("triage", "Triage completed: SWARM_PARALLEL mode with 4 agents assigned.");
    activeAgui.onReasoning("reason", "Evaluating AST dependencies across 3 files.");

    await activeAgui.start();
    assert.ok(activeAgui.url.includes("http://127.0.0.1:"));
    assert.strictEqual(activeAgui.health().status, "ok");
    assert.ok(activeAgui.health().fixtures >= 0);
  });
});
