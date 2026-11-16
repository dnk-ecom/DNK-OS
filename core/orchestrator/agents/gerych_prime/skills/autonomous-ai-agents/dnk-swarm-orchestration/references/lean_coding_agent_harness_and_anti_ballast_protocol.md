# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/lean_coding_agent_harness_and_anti_ballast_protocol.md"
# purpose: "Architecture protocol for building lean, zero-ballast CLI coding agents without upstream chat/monolith bloat."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-18"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# ⚡ Lean Coding Agent Harness & Anti-Ballast Protocol

## 1. Problem Statement: Upstream Runtime Ballast
Large agent frameworks (such as upstream Hermes Agent in `core/hermes_agent/` with >16,000 files) bundle comprehensive omnichannel features:
- Multi-platform chat bridges: WhatsApp, Slack, Telegram, Discord, Signal, iMessage.
- Heavy frontends: Desktop GUI, Web-UI, Canvas/Excalidraw, audio/speech transcription, multi-language localization.

**Impact on Terminal Coding Agents**:
- `sys.path` pollution and namespace collisions (e.g. `import plugins` collisions with pytest).
- Bloated standing system context (>40,000 tokens) due to unused tool schemas and middleware.
- Massive disk footprint and slow interpreter spin-up.

---

## 2. Solution: The Thin Harness Architecture (`core/harness/`)
Per `docs/DIRECTORY_MAP.yaml` and `docs/notes/MY TASKS/0. Питання Архітектури/Журнал/180926 - План Капкан.md`:
1. **Quarantined Donor Library**: `core/hermes_agent` is treated as an isolated donor repository; no direct dependencies or wildcard imports into development runtimes.
2. **Strict Code Budget (≤ 1,500 LOC total)**:
   - `core/harness/runtime.py` (< 400 LOC): Async loop: `Task -> Context Synthesis -> LLM -> Tool Dispatch -> Execution -> Gate Check`.
   - `core/harness/state.py` (< 300 LOC): Immutable TaskDNA DAG state without conversational chat logs.
   - `core/harness/tools.py` (< 400 LOC): JIT FastMCP dispatcher exposing strictly 5 developer tools: `read_file`, `write_file`, `patch`, `terminal`, `search_files`.
   - `core/harness/gate.py` (< 400 LOC): Fail-closed quality gate enforcing `scripts/verify_all.sh` (AST anti-tautology, type-check, pytest exit code 0).

---

## 3. SOTA Ingested Patterns for Lean CLI Agents

| Repository / Pattern | Key Architecture Insight | Ingestion Reference |
| :--- | :--- | :--- |
| **`affaan-m/ECC`** | Pure terminal CLI developer workflows; pre/post hook gates; zero chat ballast. | `docs/tech/sota_assimilation/SOTA_ECC_ASSIMILATION.md` |
| **`justrach/codegraff` (graff)** | High-speed agentic coding harness in Zig/Python; FastMCP-first; DGM code evolution loop. | `docs/tech/sota_assimilation/SOTA_CODEGRAFF_ASSIMILATION.md` |
| **`gastownhall/beads` (bd)** | AI-native task runner for coding agents; lazy tool schema loading; 80-100 byte task models; CAS lease fencing. | `docs/tech/sota_assimilation/beads_audit.md` |
| **`herdrdev/herdr`** | Lightweight runtime on Rust for coding agents in sandboxed terminal environments. | `docs/tech/sota_assimilation/SOTA_HERDR_ASSIMILATION.md` |
| **`eaglhuang/AI-Atomic-Framework`** | 5D CID task identity; 7-stage lifecycle; SHA256-anchored closure proof for concurrent coding agents. | `docs/tech/sota_assimilation/SOTA_AI-ATOMIC-FRAMEWORK_ASSIMILATION.md` |
| **`Agno`** | High-velocity agent framework without chat-app ballast; lightweight memory & JIT toolsets. | `docs/tech/sota_assimilation/agno_agi.md` |

---

## 4. Operational Invariants for Pure Terminal Swarms
1. **Context Ceiling**: Initial system prompt + tool schemas must stay ≤ 6,000 tokens (JIT-Tooling).
2. **Tool Minimal Whitelist**: Developers only get file I/O, search, and terminal execution. External MCPs (Notion, Chrome DevTools, DBs) must be unmounted unless specifically requested.
3. **No Conversational Hallucinations**: Status `completed` requires deterministic execution proof (exit code 0).
