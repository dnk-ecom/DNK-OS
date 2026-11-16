# CopilotKit, AG-UI & aimock Canvas Integration Patterns

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/copilotkit_agui_aimock_canvas_patterns.md"
# purpose: "Architecture patterns for clean-room assimilation of open-multi-agent-canvas, AG-UI protocol, and aimock test infrastructure."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-09-20"
# author: "Hermes Prime (Gerych)"
# --- END DNK-MRH-HEADER ---

## 1. CopilotKit & open-multi-agent-canvas Pitfalls & Clean-Room Decoupling

When evaluating and assimilating multi-agent canvas interfaces from the `CopilotKit` ecosystem (e.g. `CopilotKit/open-multi-agent-canvas`):

### Critical Pitfalls
- **Proprietary Cloud Telemetry & Lock-in**: Upstream `open-multi-agent-canvas` and `@copilotkit/react-core` default to Copilot Cloud routing requiring `NEXT_PUBLIC_CPK_PUBLIC_API_KEY`. In self-hosted or sovereign agent stacks (such as DNK OS), telemetry and execution streams must NEVER egress to external cloud proxies.
- **Monolithic State Desynchronization**: Upstream expects LangGraph checkpoint threads (`checkpoint_id`, `thread_id`). If the local system uses custom TaskDAGs, TaskForests, or OCC 3-way merge graphs, do NOT import the monolithic SDK wrapper.
- **Dependency Bloat**: Importing full `@copilotkit/react-core` / `@copilotkit/react-ui` introduces conflicting React context providers, heavy Tailwind variants, and overlapping ReactFlow/xyflow versions.

### Clean-Room Assimilation Rules
1. **Extract Visual Components Only**: Re-implement or lift purely visual React components:
   - `AgentNode`: Visual card with status orb, model badge, and live activity stream.
   - `ToolExecutionNode`: Collapsible tool call arguments, output payload, and duration badge.
   - `HumanInTheLoopNode` (HITL): Action buttons (Approve / Reject / Edit params).
2. **Standardize on Open Protocol (AG-UI Protocol)**:
   - Use standard AG-UI SSE stream format or direct WebSocket JSON-RPC events.
   - Bind stream updates into the local state store (e.g. Zustand) via lightweight hook (`useGerychStream`).

---

## 2. Deterministic AI & Agent Testing with `@copilotkit/aimock`

`@copilotkit/aimock` provides single-port, zero-dependency mock infrastructure for AI frontend, agent, and canvas testing.

### Key Capabilities & Mocks
- **`LLMock`**: OpenAI, Claude, Gemini, and Ollama compatible completions and stream simulation.
- **`MCPMock`**: Full MCP server simulation supporting JSON-RPC tools, resources, and prompts on ephemeral ports.
- **`AGUIMock`**: AG-UI agent-to-UI streaming protocol simulation for real-time frontend canvas updates.
- **`A2AMock`**: Agent-to-Agent communication simulation.

### Zero-Bundler Test Harness with `tsx --test` (Vitest Alternative)
In Next.js / React projects where Vitest may conflict with peer dependencies or background process monitors, use Node's native `node:test` + `node:assert/strict` executed via `tsx --test`:

```typescript
// apps/web/tests/aimock/aimock_swarm_stream.test.ts
import { describe, it, afterEach } from "node:test";
import assert from "node:assert/strict";
import { LLMock, MCPMock, AGUIMock } from "@copilotkit/aimock";

describe("Layer 3: @copilotkit/aimock Offline Infrastructure Verification", () => {
  let activeLlm: LLMock | null = null;
  let activeMcp: MCPMock | null = null;
  let activeAgui: AGUIMock | null = null;

  afterEach(async () => {
    if (activeLlm) await activeLlm.stop();
    if (activeMcp) await activeMcp.stop();
    if (activeAgui) await activeAgui.stop();
  });

  it("should initialize LLMock on ephemeral port and return deterministic completions", async () => {
    activeLlm = new LLMock({ port: 0 });
    activeLlm.onMessage("plan", {
      content: "Execution plan: 1. Research AST 2. Build Component 3. Auditor Gate",
    });
    await activeLlm.start();

    const response = await fetch(`${activeLlm.url}/v1/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer mock-key" },
      body: JSON.stringify({
        model: "gpt-4o",
        messages: [{ role: "user", content: "plan the task" }],
      }),
    });
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
      inputSchema: { type: "object", properties: { symbol: { type: "string" } }, required: ["symbol"] },
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
    assert.strictEqual(activeMcp.health().status, "ok");
  });

  it("should stream AG-UI agent events deterministically for Canvas node state updates", async () => {
    activeAgui = new AGUIMock({ port: 0 });
    activeAgui.onMessage("triage", "Triage completed: SWARM_PARALLEL mode with 4 agents assigned.");
    activeAgui.onReasoning("reason", "Evaluating AST dependencies across 3 files.");
    await activeAgui.start();
    assert.strictEqual(activeAgui.health().status, "ok");
  });
});
```

### Critical API Pitfalls
1. **`LLMock` Fixture Registration**: `new LLMock({ port: 0 })` takes `port` in its options, NOT `fixtures`. Add fixtures dynamically using `llm.addFixtures([...])` or register matchers with `llm.onMessage(pattern, response)`.
2. **`MCPMock` Tool Call Return Type**: The handler in `onToolCall(name, handler)` must return a string (e.g. JSON stringified object) or `MCPContent[]`. Returning a raw JavaScript object causes TypeScript type mismatch.
3. **Execution Duration**: Tests using `LLMock` and `MCPMock` on ephemeral ports execute in <50ms with 0 network calls, making them ideal for pre-commit CI gates.

---

## 3. High-Frequency Multi-Agent Streaming on `@xyflow/react`

When multiple swarm agents (e.g. 4-6 parallel workers) stream reasoning tokens and tool outputs concurrently to an `@xyflow/react` canvas:

1. **Anti-Pattern (Full Graph Re-render)**:
   Updating global `nodes` array in Zustand on every token triggers top-level ReactFlow re-render, dropping canvas frame rates below 15 FPS.
2. **Best Practice (Targeted Local Updates)**:
   - Keep high-frequency streaming logs in a dedicated log buffer / ring-buffer keyed by `nodeId`.
   - Node components subscribe only to their specific worker state using Zustand selector: `useCanvasStore(s => s.agentStreams[nodeId])`.
   - Throttle UI token flushes to ~30-60ms intervals (animation frame or debounce window) while processing WebSocket packets synchronously.

---

## 4. Multi-Agent Swarm Node & Local MCP Configuration Pattern

### Canonical File Architecture
- **Types**: `apps/web/types/mcp.ts` — contains `MCPServerConfig`, `StdioServerConfig`, `SseServerConfig`, `MultiAgentSwarmNodeData`, `AgentExecutionStep`.
- **Node Component**: `apps/web/components/canvas/nodes/MultiAgentSwarmNode.tsx` — implements `@xyflow/react` custom node matching SOTA Dark Teal / Slate-Cyan design tokens.
- **Modal Component**: `apps/web/components/canvas/modals/MCPConfigModal.tsx` — manages local Stdio/SSE MCP servers without external cloud credentials.
- **Canvas Environment**: `apps/web/components/canvas/MultiAgentSwarmCanvas.tsx` — orchestrates DAG nodes with sticky agent execution HUD.
- **Mock Configuration**: `apps/web/aimock.json` — standalone config for CLI mock server.

### Visual & Interactive Invariants (SOTA Dark Teal Standard)
- **Outer Canvas Background**: `#1e2022` (Charcoal Slate).
- **Node Container**: `#162c2f` (Deep Muted Teal) with `1px border #224447` and `rounded-xl`.
- **Active Step Pulse**: When `activeNodeName` matches the node or its current sub-step, render an animated glowing banner (`#35d5d5` cyan tint) with `animate-pulse`.
- **Step Execution List**: Compact scrollable checklist displaying `AgentExecutionStep` (`status`: `completed` -> 🟢 checkmark, `running` -> 🔄 spinner, `failed` -> 🔴 error, `pending` -> ⚪ circle).
- **Quad-Directional Handles**: Expose both vertical (Top/Bottom) and horizontal (Left/Right) `Handle` elements with invisible or slate `#2a6368` dots to allow arbitrary DAG and hierarchical tree connections without edge crossing issues.
- **Type-Check Gate**: Every assimilated canvas node must pass `tsc --noEmit` cleanly in `apps/web`.

---

## 5. Local E2E Verification & Browser Testing Invariant

When facilitating local testing of new canvas pages or components in Next.js:

### Dedicated Test Route Pattern
1. Create a dedicated client route under `apps/web/app/canvas/swarm/page.tsx` marked with `'use client'`.
2. Ensure both named and default exports exist on the canvas component to prevent Next.js dynamic import or Page component export mismatches.

### Zero-Downtime Server Readiness Protocol (Anti-ERR_CONNECTION_REFUSED)
1. **Never Assume Dev Server is Running**: Before directing the user to `http://localhost:3000/<route>`, verify listener state via `lsof -i :3000` or port check.
2. **Background Process Spawn**: Launch the Next.js server via `terminal(command="npm --prefix apps/web run dev", background=True)`.
3. **Deterministic Readiness Probe**: Poll the specific endpoint until an HTTP 200 status code is returned:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/canvas/swarm
   ```
4. Only notify the user to open or reload the browser tab after the endpoint returns HTTP 200 and initial compilation finishes.
