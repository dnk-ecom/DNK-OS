<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/human_intent_to_agent_execution_app_pattern.md"
purpose: "Canonical Architecture and Engineering Pattern for Standalone Agentic Applications (Human = Ideas, Agents = Executors)."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-18"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🧠 Engineering Pattern: Human Intent to Autonomous Agent Execution (DNK_OS_APP)

## 📌 Architectural Philosophy
In modern agentic applications (e.g. `DNK_OS_APP`), the user is the **Creative Director / Intent Originator**, while specialized AI agents act as **Deterministic Executors**.
To avoid brittle execution, state desynchronization, and token exhaustion, the architecture separates the visual/spatial intent layer from deterministic machine execution.

---

## 🏛️ 1. Standalone Application Topology (Diátaxis & Two-Tier Model)

```
DNK_OS_APP/
├── .obsidian/                     # Spatial PKM & Visual Notes (Excalidraw, Canvas)
├── specs/                         # SSOT Data Models & FastMCP Tool Contracts
│   ├── 01_CORE_ARCHITECTURE_SPEC.md
│   ├── 02_DATA_MODELS_PYDANTIC.md
│   └── 03_FASTMCP_PLUGIN_CONTRACTS.md
├── docs/                          # Diátaxis 4-Quadrant Knowledge Base
│   ├── architecture/              # Explanation: System design rationale
│   ├── reference/                 # Reference: Schemas, endpoints, invariants
│   ├── how-to/                    # How-To: Step-by-step developer runbooks
│   └── tutorials/                 # Tutorials: Onboarding & demo flows
├── apps/
│   ├── web/                       # Next.js 15, Tailwind, @xyflow/react, CopilotKit
│   └── api/                       # FastAPI Gateway, Split-Route Auth, SSE streams
├── core/
│   └── harness/                   # Ultra-lean runtime (<1500 LOC): runtime, state, tools, gate
└── services/                      # 3 Core Workhorses (FastMCP Services)
    ├── dnk_shopify/               # E-Commerce & Liquid AST
    ├── dnk_media/                 # FFmpeg, Remotion, YouTube Ingestion
    └── dnk_distribution/          # Marketing, Postiz, Social channels
```

---

## ⚡ 2. The 5-Stage Human-to-Agent Execution Loop

```
1. [ Human Intent / Canvas Node ]
           │
           ▼ (Spatial LOD Filtering <4k tokens)
2. [ ThoughtDAG Compiler ] ──► Compiles intent into TaskDNA DAG with Negative Scope
           │
           ▼ (FastMCP RPC Dispatch)
3. [ Thin Harness Runtime ] ──► Routes subtask to domain worker (Shopify / Media / Fullstack)
           │
           ▼ (Atomic Execution ≤25 tools)
4. [ Adversarial Quality Gate ] ──► 100% Green verification (AST, pytest, typecheck)
           │
           ▼ (OCC Structural Merge)
5. [ Generative UI / Live Canvas ] ──► Renders interactive Proposal Node for Human Approval
```

---

## 🛡️ 3. Critical Failure Modes & Engineering Mitigations

1. **State Desync & Broken UI**:
   - *Cause*: Unstructured LLM responses modifying UI state.
   - *Fix*: Strict Zod / Pydantic v2 schemas for all FastMCP tool inputs/outputs; Generative UI via CopilotKit.
2. **Context Bloat & Token Decay**:
   - *Cause*: Dumping entire project workspace into every turn.
   - *Fix*: SCONES 2-Tier Memory retrieval + LOD context pruning (<4k tokens per turn).
3. **Destructive Execution**:
   - *Cause*: Direct unchecked agent writes to user projects.
   - *Fix*: Optimistic Concurrency Control (OCC) + Proposal Nodes requiring Human-in-the-Loop (HITL) approval.
