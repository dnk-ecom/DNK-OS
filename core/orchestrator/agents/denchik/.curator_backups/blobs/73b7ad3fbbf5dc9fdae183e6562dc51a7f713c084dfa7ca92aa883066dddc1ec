# --- DNK-MRH-HEADER ---
# mrh_id: "sota_assimilation_references_hermes_v0227_threshold_monorepo_assimilation"
# purpose: "Technical Reference for NousResearch/hermes-agent v0.22.7 (The Threshold Release) Assimilation & Local Patch Protection"
# author: "DNK-e.com Maksym & Denchik"
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-04"
# --- END DNK-MRH-HEADER ---

# 🧬 Technical Reference: Hermes Agent v0.22.7 Assimilation & Local Patch Protection

This reference documents the architectural changes in **Hermes Agent v0.22.7** (and the major **v0.22.0 Threshold Release**), critical pitfalls discovered during audit, and guidelines for assimilation into the DNK OS monorepo.

---

## 📌 Upstream Release Milestones
- **Baseline**: `v0.21.0` (The Pantheon Release, August 31, 2026).
- **Major Milestone**: `v0.22.0` (The Threshold Release, October 14, 2026).
- **Current Stable**: `v0.22.7` (November 3, 2026).

---

## 🏗️ Architectural Evolution (v0.21.0 → v0.22.7)

### 1. Modular State & SQLite Concurrency (`state.db`)
- **Legacy Monolith**: `hermes_state.py` handled all session, chat, cron, usage, and locks in a single file, prone to SQLite database lock contention and deadlocks under concurrent subagent access.
- **v0.22.x Architecture**: Split into 35 granular modules:
  - `hermes_state_wal.py`: Write-Ahead-Logging configuration and checkpointing.
  - `hermes_state_lockguard.py` & `hermes_state_lockowners.py`: Granular file-level and table-level concurrency guards.
  - `hermes_state_mutation_*.py`: Isolated mutation operations (`compress`, `reset`, `retirement`, `branch`).
  - Session auto-pruning (default: 90 days retention), safe VACUUM execution.

### 2. Context Compaction & Token Accounting
- **Legacy**: Heuristic string length calculation (`len(transcript) / 4`), leading to premature compaction or summary failure overriding transcript history.
- **v0.22.x Fix**:
  - Compaction calculations use verified API usage metrics returned directly by model providers.
  - Protected tail slice reserved (20% of context window) to preserve immediate operational state.
  - Fail-safe rollback: if summarization fails or is rejected, original transcript is preserved intact.

### 3. Turn Liveness Watchdog (`agent.turn_liveness.timeout_s`)
- Prevents infinite hangs caused by network stream stalls or unhandled generator errors.
- Default timeout: 600 seconds. If an LLM turn produces no progress, the watchdog terminates the turn gracefully, logs telemetry, and returns control to the agent cycle.

### 4. Lazy Tool Loading (`tool_search`)
- Eliminates standing context bloat: instead of registering 30+ tools directly into the system prompt (~13,367 tokens), rarely used tools are cataloged into a dynamic search index, reducing baseline overhead to ~6,883 tokens (~50% reduction).

### 5. Pluggable Delegation & Subagent Resilience
- Subagents (`delegate_task`) support live output streaming, image input attachments, and graceful abort via `/stop`.
- Independent process isolation: failure or crash of a child subagent returns structured error telemetry without crashing the parent session.

---

## 🚫 CRITICAL PITFALLS & LOCAL PATCH PRESERVATION

### 1. The `vertex_adapter.py` OAuth Token Refresh Invariant
- **The Bug**: Google Vertex AI application default credentials (ADC) expire after 3600 seconds (1 hour). In long-running autonomous sessions (> 50 turns), API calls begin failing with `401 Unauthorized` mid-compaction.
- **DNK OS Custom Patch**: DNK OS maintains an explicit patch in `vertex_adapter.py` that refreshes OAuth tokens proactively at 3000 seconds.
- **Assimilation Rule**: Upstream releases DO NOT include this proactive refresh. Any assimilation into `core/hermes_agent` MUST verify and re-apply the `vertex_adapter.py` token refresh patch before promoting the runtime.

### 2. Tool Renames and Alias Mapping
- In v0.22.x, several internal tool modules and CLI hooks were renamed:
  - `todo` → `todo_list`
  - `cronjob` → `cronjob_manage`
  - `process` → `process_manage`
- Although backward-compatibility aliases exist in `tools/`, automated pre-tool hooks (`hermes_pre_tool_hook.py`) and regex interceptors must account for both naming conventions.

### 3. Upstream Release Churn & Canary Gate
- Upstream experienced rapid-fire releases (7 releases in 3 weeks: v0.22.1 was released from an incorrect commit, and v0.22.2 immediately patched broken session deletion).
- **Rule**: Never update `core/hermes_agent` directly in production. Deploy to `core/hermes_agent_staging/`, run the 7 Canary Scenarios (C1–C7), and confirm rollback SLA (< 2.0s) before switching symlinks.

### 4. Zero Unauthorized Root Directory Invariant
- Never clone upstream repositories or test builds into the `DNK_HUB` repository root.
- All external clones and third-party codebases MUST reside exclusively in `../DNK_Vibe/`.
