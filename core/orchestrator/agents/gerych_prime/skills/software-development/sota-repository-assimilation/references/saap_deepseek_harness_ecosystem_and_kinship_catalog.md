# --- DNK-MRH-HEADER ---
# mrh_id: "skills_sota_saap_deepseek_harness_ecosystem"
# purpose: "Reference catalog and assimilation recipes for DeepSeek Harness (dsh) ecosystem, Cordis IoC, and Services as Agent Plugins (SaaP)"
# author: "Gerych Prime & Maksym"
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-15"
# --- END DNK-MRH-HEADER ---

# Services as Agent Plugins (SaaP) & DeepSeek Harness Ecosystem Kinship Catalog

## 1. Ideological Kinship Matrix: DNK OS Harness v5.0 vs DeepSeek Harness

The architectural convergence between DNK OS Agent Harness v5.0 and DeepSeek Harness (`dsh`) is grounded in 4 foundational pillars:

| Pillar | DeepSeek Harness (`dsh`) Implementation | DNK OS Harness v5.0 Target Architecture |
|---|---|---|
| **Microkernel & Inversion of Control** | Cordis IoC runtime (`ctx`). No privileged core loop. Plugins contribute typed services and reversible effects. | Ultra-thin core (`core/orchestrator/`). Core provides only Event Bus, Tool Dispatcher, Security Gates, and Memory sync. |
| **Services as Agent Plugins (SaaP)** | Every capability (shell, terminal, browser, git, fs) is an isolated package under `packages/*`. | Domain services (`services/dnk_*`) decoupled into standalone FastMCP plugins with Pydantic JSON-schema contracts. |
| **Agent as Declarative Preset** | Profiles (`web`, `headless`, `sdk`, `acp`) composed of layered bundles (`dsh-base` + extensions) configured via YAML patches. | Swarm worker roles (`gerych_builder`, `dnk_shopify`, `gerych_auditor`) declared as plugin bundles + permission policies. |
| **Spatiotemporal Event Lifecycle** | Append-only Session Events, live Agent Events (`agent/*`), and Seam Capability Events (`tools/*`, `fs/*`). | Event Bus with monotonic guards, pre-tool circuit breakers, and audit verification ledgers. |

---

## 2. Catalog Repositories: High-Kinship Internal Baseline

Curated from the DNK Repository Catalog (`.data/repo_catalog/catalog.db` & `docs/notes/112 SOTA Repository Catalog.md`):

### 1. `deepseek-ai/deepseek-harness` (Canonical Baseline)
- **Role**: Reference Cordis-based Agent Harness architecture.
- **Topology**: 40+ modular packages (`acp`, `compaction`, `guard`, `mcp`, `sandbox`, `workflow`, `workspace`).
- **Assimilation Target**: Package layout, profiles/bundles layering, reversible effect hooks (`ctx.effect`), and Programmatic Tool Calling (PTC).

### 2. `bytedance/deer-flow` (SuperAgent Long-Horizon Harness)
- **Role**: Multi-hour autonomous execution framework with sandboxes, subagents, and memory.
- **Kinship**: Aligns with Mandatory Atomic Slice Execution (MASE) and multi-agent coordination.
- **Assimilation Target**: Subagent sandboxing and execution checkpointing.

### 3. `agentplugins/agent-plugins-spec` (Open Plugin Specification)
- **Role**: Formal specification for autonomous AI agent plugins.
- **Kinship**: Standardized interface for SaaP plugins.
- **Assimilation Target**: Unified manifest declaring tools, permissions, and lifecycle hooks (`on_load`, `on_unload`, `on_turn`).

### 4. `coleam00/Archon` (Deterministic Coding Harness)
- **Role**: Open-source harness builder for reproducible AI coding workflows.
- **Kinship**: Zero-guessing and test-driven verification loops.
- **Assimilation Target**: Plan-Work-Review deterministic cycle templates.

### 5. `affaan-m/ECC` (Agent Harness Performance Optimization)
- **Role**: Performance engineering for agentic loops (skills, instincts, memory, security).
- **Kinship**: SCONES cognitive state and Pre-Tool circuit breakers.
- **Assimilation Target**: Behavioral instincts triggering immediate fallback upon error detection.

---

## 3. GitHub SOTA Discoveries: DeepSeek Harness & SaaP Ecosystem

Live discoveries identified via GitHub search across `topic:deepseek-harness-plugin` and Cordis agent architectures:

### 1. `bowenliang123/dsh-context` (Context Evolution & Token Compaction)
- **URL**: `https://github.com/bowenliang123/dsh-context`
- **Focus**: Context token breakdown, compaction visualization, pruning trajectories.
- **Assimilation Target**: Context diet HUD inside DNK OS Visual Shell to monitor plugin token consumption.

### 2. `toolclub/dsh-agent-team-gui` (Multi-Agent Team Orchestration)
- **URL**: `https://github.com/toolclub/dsh-agent-team-gui`
- **Focus**: Dynamic lead planning, DAG task decomposition, per-agent isolated toolkits, Run Center.
- **Assimilation Target**: Graphical execution panel for `dnk_decompose_task_dna` and `dnk_swarm_parallel`.

### 3. `chenxiachan/thoughtdag` (Infinite Canvas Thought Graph)
- **URL**: `https://github.com/chenxiachan/thoughtdag`
- **Focus**: Infinite canvas transforming conversational turns into DAG nodes where edges carry context.
- **Assimilation Target**: Context wiring algorithms for DNK Visual Canvas / TaskForest (`packages/domains/canvas`).

### 4. `dream-num/dsh-univer-office` (Collaborative Multi-Agent Office SDK)
- **URL**: `https://github.com/dream-num/dsh-univer-office`
- **Focus**: Univer SDK (sheets, docs, canvas, tables) with isolated agent worktrees.
- **Assimilation Target**: Concurrent artifact generation with OCC structural merge for multi-agent workflows.

### 5. `agentrq/agentrq` (Human-in-the-Loop Realtime Task Manager)
- **URL**: `https://github.com/agentrq/agentrq`
- **Focus**: Realtime HITL approval gate with ACP (Agent Client Protocol) compatibility.
- **Assimilation Target**: Pre-execution confirmation modals for `gerych_auditor` and high-blast-radius tools.

### 6. `fangqian616/consensus-pipeline` (Multi-Agent Consensus Departments)
- **URL**: `https://github.com/fangqian616/consensus-pipeline`
- **Focus**: Multi-department consensus pipeline mitigating hallucinations via structured debate.
- **Assimilation Target**: Adversarial Review enhancement (Red Team Auditor vs Blue Team Builder).

---

## 4. Phased SaaP Assimilation Workflow ("Все по черзі")

1. **Phase 1: Plugin Base Contract (`DNKPluginBase`)**
   - Define lifecycle: `initialize(ctx)`, `register_tools()`, `register_routes()`, `teardown()`.
   - Embed FastMCP protocol and permission manifests.
2. **Phase 2: Service Migration to SaaP**
   - Wrap `services/dnk_shopify` as the pilot plugin.
   - Decouple domain logic from root runtime into `packages/domains/`.
3. **Phase 3: Visual Shell & Context HUD Integration**
   - Port context breakdown patterns from `dsh-context` into the Visual Shell console.
   - Connect TaskDNA DAG view based on `toolclub/dsh-agent-team-gui` and `thoughtdag`.
