# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/live_orchestrator_chat_canvas_action_bridge.md"
# purpose: "Reference architecture for live Orchestrator Chat & ReactFlow Canvas Actions Bridge."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-16"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Live Orchestrator Chat & ReactFlow Canvas Actions Bridge

## 1. Architectural Overview
The Orchestrator Chat Bridge links conversational AI (Gerych Prime) with the spatial ReactFlow/XYFlow canvas. Rather than operating purely as a disconnected sidebar text-box, the chat engine interprets spatial intents and emits structured mutations (`canvas_actions`) that execute against the Zustand `canvasStore`.

```
[ User Prompt / Spatial Focus Context ]
                    │
                    ▼
POST /api/v1/orchestrator/chat/stream (SSE)
  Payload: {
    message,
    session_id,
    target_agent,
    selected_node: { id, type, title, content, incoming_edges, outgoing_edges },
    canvas_context: { nodes, edges }
  }
                    │
                    ├────────────────────────┬────────────────────────┐
                    ▼                        ▼                        ▼
           Swarm Coordinator         Intent Parser           Canvas Action Engine
                    │                        │                        │
                    └────────────────────────┴────────────────────────┘
                                             │
                                             ▼
  Server-Sent Events (SSE) Stream:
    event: thought         ➔ "Analyzing spatial graph focus..."
    event: status          ➔ "Routed to gerych_prime..."
    event: tool_call       ➔ scones_get_memories(...)
    event: tool_result     ➔ Invariant matched
    event: canvas_mutation ➔ [ { action_type: 'add_note', ... } ]
    event: content_chunk   ➔ "Live LLM response delta..."
    event: done            ➔ Metadata & summary
                                             │
                                             ▼
            ReactFlow Canvas Execution Bridge (Zustand Store)
               ├─ applyCanvasActions(...)
               │    ├─ add_note           ➔ addThoughtDagNote(...)
               │    ├─ add_agent_task     ➔ addAgentTaskNode(...)
               │    └─ connect_wire       ➔ connectContextWire(...)
               └─ Live UI Stream Consumer (OrchestratorChatPanel)
                    ├─ Thought Accordion (collapsible reasoning)
                    ├─ Tool Call Cards (live verification feedback)
                    └─ Spatial Focus Badge with Clear Action
```

## 2. Server-Sent Events (SSE) Streaming Protocol
FastAPI SSE endpoint: `POST /api/v1/orchestrator/chat/stream`
Yields standard W3C event stream chunks formatted as `data: {...}\n\n`:
- **`thought`**: Live chain-of-thought analysis and spatial graph perception.
- **`status`**: Agent swarm routing notifications (e.g. `gerych_prime`, `dnk_shopify`).
- **`tool_call` & `tool_result`**: Subsystem executions (SCONES memory, TaskDNA DAG).
- **`canvas_mutation`**: Structured mutations payload emitted directly to the frontend while streaming.
- **`content_chunk`**: Token delta stream for sub-second first-byte latency.
- **`done`**: Final payload containing model identifier (`gemini-3.8-flash`), provider (`vertex`), and full message.

## 3. Bi-Directional Spatial Context Injection (`getSelectedNodeContext`)
In `apps/web/store/canvasStore.ts`, the store exposes `getSelectedNodeContext()`:
- Inspects currently highlighted node (`selectedNodeId`).
- Resolves upstream incoming edges and downstream outgoing dependencies.
- Extracts human-readable labels of connected nodes to construct an immediate spatial scope.
- In `OrchestratorChatPanel.tsx`, active focus renders as a prominent context chip:
  `🎯 Фокус: <Title> (<Type>) [✕]`
  Allowing the user to either prompt in the context of that specific component or dismiss focus.

## 4. Client-Side Mutation Execution (`applyCanvasActions`)
The Zustand store exposes `applyCanvasActions(actions)`:
- Maps `add_note` / `ADD_NOTE` to `addThoughtDagNote`.
- Maps `add_agent_task` / `ADD_NODE` to `addAgentTaskNode`.
- Maps `connect_wire` / `CONNECT_WIRE` to `connectContextWire`.
- Applies collision offset calculation (e.g. +320px horizontal offset relative to the focused node) so spawned nodes do not stack directly on top of existing elements.

## 5. Defensive Node Data Guard Invariant (React Flow Crash Prevention)
- Custom React Flow nodes (e.g. `AgentTaskNode`, `ThoughtDagNoteNode`) must NEVER assume node `data` properties exist or are strings.
- Example: `data.taskId.slice(0, 8)` crashes the whole React tree if `taskId` is undefined.
- Always use defensive chaining: `(data.taskId || id || 'TASK').slice(0, 8)`.
- Default initializers in `canvasStore.ts` must provide all required fields (`taskId`, `status`, `agent`, `metrics`).

## 6. Multi-Tier LLM Cascading & Timeout Resilience
1. **Tier 1 (Google Vertex AI)**: `gemini-3.8-flash` via `GeminiNativeClient` with Bearer auth.
2. **Tier 2 (NVIDIA NIM)**: `meta/llama-3.2-11b-vision-instruct` / pool keys with OpenAI SDK compatibility.
3. **Tier 3 (OpenRouter / Fallback)**: Resilient fallback.
Sync provider calls must be isolated in `asyncio.to_thread` with explicit `asyncio.wait_for(..., timeout=15.0)` caps to prevent event-loop freezing or hanging connections.

## 7. CapCut AI Design Orchestrator Cockpit Pattern (LUI Invariant)
To prevent the Orchestrator Chat from decaying into a cluttered, developer-debug terminal dump, the panel must strictly adhere to the **CapCut AI Design (`capcut.com/ai-design`)** visual standard:
1. **Dark Studio Palette (`#121214` / `#18181b`)**:
   - Deep dark background with subtle `border-white/[0.08]` borders and `rounded-2xl` containers.
   - Elimination of loud developer logs, raw JSON dumps, and heavy gray cards in the default viewport.
2. **Hero Welcoming Anchor**:
   - Prominent greeting: "Що ми створюємо сьогодні?" (`text-2xl font-bold tracking-tight text-white`).
   - Clean, guiding subtext: "Поділіться ідеєю, виділіть вузол на полотні або оберіть навичку рою для старту."
3. **Swarm Skills Pills Carousel**:
   - Distinct rounded pill buttons (`rounded-full px-3.5 py-2 text-xs font-medium border border-white/10 hover:border-white/25 bg-white/[0.04]`) with domain-specific colored icon indicators (e.g., Video AI, Architecture Spec, Shopify Liquid, Builder Task, Security Gate, SCONES Memory).
   - Clicking a pill immediately injects the corresponding prompt template or dispatches intent.
   - Foldable "Показати ще / Згорнути" toggle to avoid vertical screen cannibalization.
4. **Signature Floating Input Container**:
   - Auto-resizing textarea (`min-h-[44px] max-h-[140px]`) with Enter-to-send (Shift+Enter for newline).
   - Embedded bottom toolbar containing:
     - `+` (Quick actions / add canvas node)
     - `🧊` (Spatial graph / ThoughtDAG nodes)
     - `📖` (SCONES knowledge base retrieval)
     - `↑` (Circular contrast submit button: disabled when empty, high-contrast white with black arrow when text is present, pulsating neon ring during active SSE generation).
5. **Spatial Context Docking**:
   - When a node is selected on the canvas, display a compact docked badge directly above the input: `⚡ Фокус на полотні: <Title> (<Type>) [✕]`.
6. **Thinking & Tool Execution Accordions**:
   - Verbose chain-of-thought traces and tool execution metadata must collapse into a sleek single-line summary: `💭 N міркувань • ⚡ N інструментів [⌄]`. Expanded only on demand.
