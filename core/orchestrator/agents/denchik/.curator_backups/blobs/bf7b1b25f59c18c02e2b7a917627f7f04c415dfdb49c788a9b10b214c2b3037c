# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/sovereign_reverse_engineering_and_native_subsystem_assimilation_protocol.md"
# purpose: "Protocol for clean-room reverse engineering and native integration of external cognitive platforms into DNK OS instead of subordinate cloud federation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-21"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🏛️ Sovereign Reverse Engineering & Native Subsystem Assimilation Protocol

## 1. Core Principle: Sovereignty over Subordination
When evaluating or integrating external multi-agent architectures (e.g. Orbit Agents, OpenBot, Manus, AutoCanvas):
- **NEVER** subordinate DNK OS as an ephemeral satellite, worker, or client trapped inside a third-party proprietary cloud or external orchestrator.
- **ALWAYS** perform clean-room architectural reverse engineering:
  1. Deconstruct the external system's core capabilities, schemas, protocols, and tool contracts.
  2. Map these abstractions into sovereign, native DNK OS engines (`core/stores/`, `core/memory/`, `core/orchestrator/`, `core/action_bus/`).
  3. Implement native implementations that run locally under `$HUB_ROOT` with zero external platform lock-in.

---

## 2. Deconstruction & Mapping Matrix (Ex: Orbit Agents)

| External Capability | Orbit MCP Signature | Native DNK OS Engine | Architectural Role |
| :--- | :--- | :--- | :--- |
| **Presence & Lifecycle** | `orbit_heartbeat`, `orbit_ready`, `orbit_declare` | `core/orchestrator/swarm_mesh.py` + `ActionBus` | In-memory agent state, heartbeat pings, dynamic working memory, session manifests. |
| **3-Tier Vault Storage** | `orbit_result`, `orbit_get_result`, `orbit_search`, `orbit_file_*` | `core/stores/knowledge_store.py` + `core/action_bus/artifact_store.py` | 3 Trust levels (`EXPLORATORY`, `CONCLUSION`, `AUTHORITATIVE`), vector/FTS search, and Obsidian Vault sync. |
| **Knowledge Intercept** | `orbit_knowledge_propose`, Inbox approval flow | `core/action_bus/hitl_bridge.py` + `core/canvas/approval.py` | Human-In-The-Loop gate. Agents propose knowledge; only human approval elevates it to canonical L3 SCONES memory. |
| **Reactive Trackers** | `orbit_table_write`, `orbit_table_get`, `orbit_table_list` | `core/stores/tracker_engine.py` | In-place tabular mutations by `table_ref` with OCC (Optimistic Concurrency Control) instead of chat-feed spam. |
| **Operator Inbox & Decisions** | `orbit_decide`, operator dashboard | `core/canvas/approval.py` + `apps/api/` | Unified review queue for proposals, execution milestones, and human interventions. |
| **Unified Tool Gateway** | `orbit_toolbox` (list/describe/call) | `core/framework/fastmcp_dispatcher.py` | On-demand JIT tool dispatch without bloating initial agent context budgets. |

---

## 3. Implementation Workflow & Guardrails
1. **Target File Whitelist**: Every native reverse-engineered module must reside in sanctioned directories (`core/`, `services/`, `apps/api/`). Creating new root or external bridge packages without an accepted ADR is forbidden.
2. **Deterministic Verification**: Verify each native subsystem with unit and contract tests in `tests/core/` ensuring 100% green status via `bash scripts/verify_all.sh`.
3. **No Phantom Cloud Dependencies**: Native engines must function fully offline or with configured local/GCP providers, requiring no subscription or API key to the assimilated platform.
