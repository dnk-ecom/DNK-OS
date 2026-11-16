<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/federated_role_capsule_harness_and_astryx_ui_registry_protocol.md"
purpose: "Canonical protocol for Clean Upstream Harness upgrades, Federated Role-Capsule Swarm execution (Shopify 6-Stage Pipeline), and Agent-First UI Registry (Meta Astryx pattern)."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-10-15"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🏛️ Federated Role-Capsule Harness, Clean Upstream Upgrade & Agent-First UI Registry Protocol

## 1. Clean Upstream Engine + Isolated DNK Overlay Invariant
When evaluating external lightweight harnesses or upgrading the base Hermes Agent runtime:
- **Never migrate to a foreign monolithic harness framework** (`DEC-012` Zero-Framework Microkernel). Any agent loop is ~200 lines of Python (`pre_hook -> execute_tool -> post_hook -> call_llm`). External innovations are assimilated via `core/dna_assimilation.py` into pure Python schemas (`core/kernel/contracts.py`) or skills (`SKILL.md`).
- **Two-Layer Separation**:
  1. **Upstream Binary/CLI Layer (Upgradeable)**: LLM API transport, PTY terminal session drivers, browser CDP connectors, and base MCP client sockets. Safe to pull upstream performance and stability updates.
  2. **DNK OS Overlay Layer (Immutable / Protected inside `DNK_HUB`)**:
     - `core/orchestrator/agents/gerych_prime/SOUL.md` & root `AGENTS.md`.
     - `scripts/system/hermes_pre_tool_hook.py` (Ring 0 security, Anti-Read-Loop, MASE gates).
     - `core/kernel/contracts.py` & `core/orchestrator/control_plane.py` (`SwarmControlPlane`, `TaskNode` DAG, OCC 3-way merge).
     - `catalog.db` (3-Tier SOTA Radar), SCONES L2/L3 memory, and 55+ distilled skills.

---

## 2. Federated Role-Capsule Architecture (Single Microkernel vs. Multi-Daemon Anti-Pattern)
- **Anti-Pattern (Forbidden)**: Spawning 14 separate heavy CLI/Hermes daemon processes per specialized agent or frontend session causes 8–16 GB RAM exhaustion, 3–5s cold-start handoff latency, and split-brain graph state.
- **Canonical Architecture (Federated Role Capsules over Shared Microkernel)**:
  - **Shared Ring 0 Core (`core/kernel/`)**: Enforces global Pre-Tool Hooks, System 1 Triage (<50ms), SCONES memory access, Jev cryptographic receipts (`jvr_<digest>`), and MASE ≤25 tool bounds.
  - **Role-Specific Capsule (`AgentHarnessProfile`)**: Each specialist worker mounts an isolated manifest containing:
    1. **Sanctioned Tool Whitelist** (standing context strictly ≤ 6,000 tokens).
    2. **Domain-Scoped Skills & Few-Shot Examples** (e.g. `shopify_cro_blocks`, `shopify_theme_ast_engineering`).
    3. **Domain Validators / Post-Hooks** (e.g. `dnk_shopify_validate_liquid`, `DualTrackStoreEngine` Machine Gate).

### Parallel Shopify Store & Theme Production Pipeline (Tinker 4.2.0 / Theme Blocks 2.0)
1. **Stage 1 (Intake & Contract Lock)**: System 1 Triage produces `KernelTaskRequest` and locks `contract.json` + `dynamics.json`.
2. **Parallel Batch A (Intel + Architecture)**:
   - `gerych_researcher` (Intel): Niche CRO patterns and competitor teardowns -> `contract.json`.
   - `Architect`: Assembles JSON page wireframes (`templates/page.*.json`) using the 3 canonical Tinker shells (`_blocks`, `main-product`, `main-cart`).
3. **Parallel Batch B (`dnk_swarm_parallel` with strict `target_files` isolation)**:
   - `dnk_shopify`: Generates Dual-Ready Liquid blocks (`target_files: ["blocks/*.liquid"]`) + runs `dnk_shopify_validate_liquid`.
   - `Wordsmith`: High-conversion bilingual copy (`target_files: ["locales/*.json"]`).
   - `dnk_video_ai_creator`: Generates visual assets and 9:16 video compositions.
4. **Stage 5–6 (Machine Gate & Deploy)**: `gerych_auditor` verifies `gate.json` (`openDeltas == 0`) and `verify_all.sh` before Shopify Theme Push.

---

## 3. Agent-First UI Component Registry (Meta Astryx Reverse-Engineered Pattern)
When building the DNK OS frontend (`apps/web`) for user ideation, chat nodes, and task tracking:
- **Do NOT import raw `facebook/astryx` StyleX code**: StyleX conflicts with our canonical `Next.js + React + Tailwind CSS + shadcn/ui + @xyflow/react` stack.
- **Assimilate the Astryx Machine-Readable Component Registry Pattern**:
  - Maintain a typed UI component manifest (`apps/web/src/registry/ui-manifest.json` + Zod schemas) styled in the Dark Teal standard (`Canvas #1e2022`, `Fill #162c2f`, `Accent #35d5d5`).
  - Combine **Tree Outliner** (`tributary_assimilated` for hierarchical thoughts/ideas/tasks) with **ThoughtDAG Canvas** (`@xyflow/react` where every chat and task is an interconnected graph node via `context-builder.ts`).
  - Frontend agents never hallucinate raw HTML/CSS markup; they emit structured JSON payloads (`{ "component": "ShopifyWireframeCard" | "JevDecisionReceiptCard" | "SwarmProgressNode", "props": {...} }`) that render deterministically from the component registry.
