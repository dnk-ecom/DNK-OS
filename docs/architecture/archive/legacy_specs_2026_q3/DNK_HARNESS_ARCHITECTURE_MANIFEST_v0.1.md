---
title: "Dnk Harness Architecture Manifest V0.1"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_HARNESS_ARCHITECTURE_MANIFEST_v0.1.md"
> purpose: "Document: Dnk Harness Architecture Manifest V0.1"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/DNK_HARNESS_ARCHITECTURE_MANIFEST_v0.1.md"
> # purpose: "Canonical architecture manifest defining DNK OS as an Agentic Harness with Spatial Canvas Control Plane and formal separation of Kernel, Profile, Plugins, Adapters, and UI."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "0.1.0"
> # updated_at: "2026-09-08"
> # author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ DNK Harness Architecture Manifest v0.1

> **Status:** Active / Specification v0.1  
> **Target Release:** DNK OS MVP Architecture (MVR)  
> **Author:** Maksym Kuzmenko (Founder) & Gerych Prime (Chief Builder)  

---

## 1. Purpose and Non-Goals

### 1.1 Purpose
DNK OS is defined canonically as an **Agentic Harness with a Spatial Canvas Control Plane**. Its mission is to transform foundation models (Google Gemini, Claude, DeepSeek, Local LLMs) into autonomous, production-grade business engines by wrapping intelligence in deterministic execution loops, zero-bloat headless capability plugins, and an infinite node-based visual control workspace.

This manifest establishes formal boundaries, contracts, and lifecycle invariants across five architectural layers to guarantee:
- Absolute isolation between core orchestration logic and domain-specific capabilities.
- Strict prevention of dependency sprawl and system bloat.
- Universal evidence-based verification for every capability.
- Multi-provider model agnosticism without lock-in.

### 1.2 Non-Goals
- **Not a Monolithic Framework:** DNK OS does not bundle third-party tools as in-tree dependencies. It assimilates capabilities headlessly.
- **Not a Mere Chat Interface:** DNK OS rejects text-only chat as the primary OS interface; the primary surface is the reactive Spatial Canvas.
- **Not an Unbounded Agent Runtime:** The harness enforces hard limits (MASE: ≤25 tool calls/slice, circuit breakers, strict capability gates).
- **Not a Synthetic Benchmark Platform:** We do not claim synthetic benchmark superiority without empirical execution evidence.

---

## 2. Canonical Terminology

| Term | Definition |
|---|---|
| **Harness Kernel** | The minimal, ultra-reliable core engine responsible for lifecycle loops, state persistence, token governance, security gates, and deterministic scheduling. It has zero domain-specific business logic. |
| **Gerych Profile** | The sovereign agent identity, behavioral configuration, system instincts, linguistic rules (Ukrainian dialogue / English artifacts), and tool access manifests configured in `core/orchestrator/agents/gerych_prime/`. |
| **Capability Plugin** | An isolated, lightweight operational unit (tool or micro-adapter) that implements a specific capability without dragging monolithic dependencies into the kernel. |
| **Domain Service** | A dedicated, autonomous micro-service (`services/dnk_*`) possessing a formal `service_manifest.yaml` (DNK Service Card), exposing MCP tools or REST contracts. |
| **Model Adapter** | A unified provider interface abstracting LLM inference calls across Google Vertex AI (Gemini), Anthropic Claude, DeepSeek, OpenAI, or local runtimes (llama.cpp/vLLM). |
| **Spatial Canvas Control Plane** | The visual, infinite node-based workspace (`apps/web/`) functioning as the human-in-the-loop and human-on-the-loop cockpit for DAG visualization, node manipulation, and state inspection. |
| **AAB (Agentic Action Bridge)** | The bidirectional transactional bridge translating agent actions into TaskDNA DAG mutations, Canvas visual state changes, and audited tool executions. |

---

## 3. Five-Layer Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LAYER 5: SPATIAL CANVAS CONTROL PLANE                           │
│  Infinite Node Canvas (apps/web) │ Reactive Node Descriptors │ Live Telemetry & HUD   │
│  Human-in-the-Loop Cockpit       │ OCC Visual State Graph    │ Approval Gate UI       │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Bidirectional WebSocket / SSE (AAB Events)
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                        LAYER 4: CAPABILITY PLUGINS & DOMAIN SERVICES                   │
│  Domain Services (services/dnk_*)  │ Headless Tool Adapters │ Subagent Sandboxes      │
│  AAB Bridge (core/aab)             │ Model Context Protocol │ SpendGuard Rate Limits  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Governed Tool Invocations & Sandboxed RPC
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                        LAYER 3: GERYCH PROFILE & SWARM ORCHESTRATION                   │
│  Gerych Prime Identity (SOUL.md)   │ 14 Swarm Agent Roles   │ Cognitive Topologies    │
│  TaskDNA DAG Planner               │ MASE Bound (≤25 Tools) │ Self-Healing Distiller  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Lifecycle Events & Context Windows
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                        LAYER 2: HARNESS KERNEL (State & Execution)                     │
│  Canonical Harness Engine          │ Execution Broker       │ SCONES Memory Engine    │
│  OCC 3-Way Graph Merger            │ Atomic State Store     │ Master Quality Gate     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Normalized Prompt / Inference Stream
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                        LAYER 1: MODEL PROVIDER ADAPTERS                                │
│  Vertex AI (Gemini 2.0 / Imagen 3) │ Anthropic Claude 3.5/3.7│ DeepSeek R1 / V3       │
│  OpenAI / Hermes Core Gateway      │ Local Adapters (vLLM)   │ Streaming Tool Callers │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Kernel Responsibilities and Explicit Non-Responsibilities

### 4.1 Kernel Responsibilities
1. **Agent Lifecycle Management:** Start, checkpoint, pause, resume, and terminate agent loops deterministically.
2. **Context & Token Economy:** Track usage, enforce SpendGuard limits, perform AST-aware context compaction, and manage prompt cache boundaries.
3. **Memory & State Persistence:** Maintain episodic and long-term memory via SCONES, with append-only transaction logs.
4. **Concurrency & Conflict Resolution:** Provide Optimistic Concurrency Control (OCC) for multi-agent and user graph mutations.
5. **Quality Gates & Security:** Gate all commits and tool side-effects through capability checks and test verifications.

### 4.2 Explicit Kernel Non-Responsibilities
1. **No Direct UI Rendering:** The kernel emits state mutations and telemetry; it never generates HTML, DOM, or CSS.
2. **No Domain Business Logic:** Liquid template compiling, CAD rendering, video encoding, and SEO copywriting belong strictly in Plugins and Domain Services.
3. **No Direct External Monolithic Dependencies:** The kernel must remain lightweight (<150MB venv), never importing heavyweight frameworks (e.g. PyTorch, Electron, heavy CAD engines) directly into core.
4. **No Direct Unauthenticated Shell Execution:** All terminal operations must be mediated through sandboxed execution brokers with blast-radius boundaries.

---

## 5. Plugin Contract and Lifecycle

Capability Plugins adhere to a deterministic 5-stage lifecycle state machine:

```
[ DRAFT ] ──► [ SANDBOX ] ──► [ EVALUATED ] ──► [ ACTIVE ] ──► [ DEPRECATED ]
```

1. **DRAFT:** Initial specification, AST extraction, or wrapper design. No execution permissions.
2. **SANDBOX:** Plugin runs in an isolated process (`core/orchestrator/subagent_sandbox.py`) with mocked filesystem and network boundaries.
3. **EVALUATED:** Passes contract tests (`test_service_card_contract.py`) and evaluation harness suites (`core/framework/eval_harness.py`).
4. **ACTIVE:** Registered in `core/service_registry.py` and exposed to Gerych Swarm workers via FastMCP or Lazy Tool Loader.
5. **DEPRECATED:** Maintained for backwards compatibility; superseded by higher-velocity plugins; scheduled for retirement.

### Plugin Technical Contract:
- **Manifest:** Must provide `service_manifest.yaml` (or plugin schema) with metadata, dependencies, and blast-radius score.
- **Interface:** Expose either FastMCP tools or clean async Python callables.
- **Zero-Waste:** Execution runtime memory footprint must not leak; external dependencies must be isolated or serverless.

---

## 6. Model Provider Abstraction

DNK OS treats all language and multimodal models as interchangeable adapters:

```python
class ModelAdapter(Protocol):
    async def generate_response(
        self, 
        prompt_stream: PromptStream, 
        tools: List[ToolDefinition],
        temperature: float = 0.2
    ) -> ModelResponse: ...
```

- **Google Vertex AI Adapter (Primary Cloud Native):**
  - Powers Gemini 2.0 Flash / Pro (reasoning, 2M context window) and Imagen 3 (photorealistic asset generation).
  - Production path: Zero local GPU requirement; low latency; high token efficiency.
- **Anthropic Claude Adapter:**
  - Specialized for deep adversarial code audit and complex refactoring workflows.
- **DeepSeek Adapter:**
  - Cost-efficient deep reasoning and algorithmic extraction.
- **Local Runtime Adapter (vLLM / llama.cpp):**
  - Offline / air-gapped sovereign execution for sensitive customer data or dedicated appliance hardware (Omarchy Box).

---

## 7. Canvas Control-Plane Contract

The Spatial Canvas Control Plane (`apps/web`) is the visual representation of the harness state:

### 7.1 What it Visualizes
- **TaskDAG Topology:** Active nodes, dependencies, bottlenecks, and execution states (Pending, Running, Succeeded, Failed).
- **Service Cards & Live Previews:** Real-time rendered previews (Liquid storefronts, 3D glTF models, generated social posts).
- **Swarm Agent Telemetry:** Live worker status, token spend, current slice budget, and latency.

### 7.2 What it May Control Directly
- **Graph Topology:** Create, drag, connect, or delete task nodes.
- **Execution Triggers:** Manually trigger execution of selected slices or entire subgraphs.
- **Parameter Tuning:** Inspect and edit prompt parameters, style variables, or service configurations.

### 7.3 What Requires Explicit User Approval
- **Irreversible Operations:** Publishing production Shopify themes, executing external financial transactions, dropping database collections, pushing to remote production git repositories.
- **High-Cost Pipelines:** Bulk video rendering or high-volume multi-agent crawls exceeding predefined spend limits ($5.00+).

---

## 8. Security and Governance

DNK OS implements multi-layered defense-in-depth:
1. **Capability Gate:** Tools are masked until dynamically triaged (`core/orchestrator/lazy_tool_loader.py`). Workers only receive permissions relevant to their assigned slice.
2. **Blast Radius Isolation:** Subagents run in isolated worktrees (`core/orchestrator/swarm_worktree.py`) preventing unintended file corruption.
3. **Pre-Tool Hook Guardrails:** Prevents anti-read loops (≥3 unmutated reads), enforces relative path invariants, and blocks unverified commits.
4. **Adversarial Audit Gate:** 2-Agent competitive evaluation (`gerych_auditor` vs `gerych_builder`) before production promotion.

---

## 9. Quality and Evaluation

Every capability and code mutation must satisfy the **Master Quality Gate**:
1. **Deterministic Unit & Integration Tests:** 100% pass rate on `bash scripts/verify_all.sh` prior to commit.
2. **Eval Harness Verification:** Automated verification of agent reasoning trajectories via `core/framework/eval_harness.py`.
3. **Evidence Artifacts:** Generation of cryptographically auditable run reports (`generate_evidence.py`).
4. **Human Review Gate:** Formal approval step on the Spatial Canvas for all critical-tier decisions.

---

## 10. Mapping to Existing Proven DNK OS Components

| Manifest Role | Existing Codebase Path | Verification / Test Evidence | Status |
|---|---|---|---|
| **Harness Engine** | `core/framework/canonical_harness_engine.py` | `tests/framework/test_canonical_harness.py` | **PROVEN** |
| **Evaluation Harness** | `core/framework/eval_harness.py` | `tests/framework/test_eval_harness.py` | **PROVEN** |
| **Execution Broker** | `core/framework/execution_broker.py` | `tests/verification/test_e2e_omni_pipeline.py` | **PROVEN** |
| **AAB TaskDNA Bridge** | `core/aab/taskdna_bridge.py` | `tests/aab/test_aab_taskdna_bridge.py` | **PROVEN** |
| **AAB Execution Adapter**| `core/aab/execution_task_adapter.py` | `tests/aab/test_execution_task_adapter.py` | **PROVEN** |
| **AAB Registry** | `core/aab/registry.py` | `tests/aab/test_aab_registry.py` | **PROVEN** |
| **SCONES Memory** | `core/scones_memory.py` | `tests/core/test_scones_middleware_hook.py` | **PROVEN** |
| **OCC 3-Way Merger** | `core/occ_merge.py` | `tests/verification/test_sqlite_wal_concurrency.py` | **PROVEN** |
| **Subagent Sandbox** | `core/orchestrator/subagent_sandbox.py` | `tests/verification/test_subagent_sandbox.py` | **PROVEN** |
| **Service Registry** | `core/service_registry.py` | `tests/contracts/test_service_card_contract.py` | **PROVEN** |
| **Canvas Transpiler** | `core/shopify_liquid/canvas_to_liquid_transpiler.py` | `tests/verification/test_canvas_to_liquid_transpiler.py` | **PROVEN** |
| **Spatial Canvas Control**| `core/orchestrator/visual_canvas_control.py` | `apps/web/src/` (Manual UI tests) | **PARTIAL** |
| **Model Adapter Layer** | `core/orchestrator/gemini_self_heal.py` | `tests/core/test_gemini_self_heal.py` | **PARTIAL** |
| **Plugin 5-Stage Machine**| `docs/specs/DNK_HARNESS_ARCHITECTURE_MANIFEST_v0.1.md` | Manifest Specification v0.1 | **DESIGN** |

---

## 11. Migration Implications

### 11.1 What Belongs in MVR (Minimum Viable Release)
- Canonical Harness Engine + Execution Broker (`core/framework/`).
- AAB & TaskDNA Bridge (`core/aab/`).
- SCONES Memory Engine & Lazy Tool Loader (`core/`).
- Vertex AI Gemini/Imagen Provider Integration.
- Basic Canvas Control Plane for TaskDAG visualization and node inspection.

### 11.2 What Remains a Plugin / Domain Service
- Shopify Liquid Engineering (`core/shopify_liquid/` & `services/dnk_shopify/`).
- Video AI Creator / Remotion (`dnk_video_ai_creator`).
- CAD / 3D Asset Generators (`services/dnk_cad/`).
- Social Media Multi-Channel Auto-Posters.

### 11.3 What is Deferred
- Local Edge Quantization (4-bit vLLM on local GPU appliances).
- Omarchy Turnkey Physical Box deployment (remains Tier 3 hardware option).
- Autonomous financial trading & unsupervised billing settlement.

---

## 12. Decisions Required from Maksym

1. **Model Gateway Default Routing:** Confirm Google Cloud Vertex AI (Gemini 2.0 Flash for reasoning, Gemini 2.0 Pro for synthesis, Imagen 3 for visuals) as the hardcoded default for all MVR capability plugins.
2. **Canvas State Synchronization Protocol:** Formally approve WebSocket + Server-Sent Events (SSE) with OCC 3-way merge as the canonical sync protocol between Kernel and Canvas UI.
3. **Plugin Strictness Policy:** Approve whether non-compliant plugins (missing `service_manifest.yaml` or blast-radius score) should be hard-rejected at boot or loaded in quarantined sandbox mode.
