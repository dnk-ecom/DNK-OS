# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/beads-task-forest-integration/references/dnk_os_app_agentic_spec_and_eval_architecture.md"
# purpose: "Architecture & Spec Blueprint for DNK_OS_APP Next-Gen Agentic Engineering, Evals, and Spatial Task Forest"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-22"
# author: "Gerych Prime & Maksym"
# --- END DNK-MRH-HEADER ---

# 🌐 DNK_OS_APP Next-Gen Agentic Architecture & Evals Blueprint

## 🎯 Context & Motivation
Transitioning from monorepo research (`DNK_HUB`) to the standalone production release (`DNK_OS_APP`) requires solving the **"Terminal Wall-of-Text"** cognitive bottleneck. Scoping, planning, and supervising multi-agent swarms solely through terminal logs or long chat transcripts causes cognitive exhaustion for humans and context entropy (attention degradation) for LLMs.

**The Solution**: A unified spatial PKM and execution engine combining:
1. **Interactive Node-Based Canvas** (XYFlow / React / Canvas Engine) for visual thinking, intermediate artifact inspection, and human steering.
2. **ThoughtDAG & Task Forest** for deterministic task decomposition and context-as-wires dependency management.
3. **Agent Harness & Trajectory Evals** for machine-verifiable task execution and automatic skill evolution (`best_skill.md`).
4. **Bidirectional Obsidian Integration** (YAML frontmatter + Dataview queries + `.canvas` JSON).

---

## 🏛️ SOTA Architectural Foundations (2026)

| Architectural Domain | Key Repositories / Sources | Core Pattern Assimilated |
| :--- | :--- | :--- |
| **Contract-Driven Specs** | `github/spec-kit` | Structured contracts (`specs/*.md`), machine-verifiable requirements, negative scopes. |
| **Spatial Agent Canvas** | `CopilotKit/open-multi-agent-canvas`, `CopilotKit/openbot`, `TestOrg/AutoCanvas` | 2D infinite canvas for co-working; visual streaming of intermediate thoughts and artifacts. |
| **Hierarchical Swarm** | `SenteLabs/OpenExecutive`, `JDPOLASKY/Chief-of-Staff-2` | Executive Orchestrator (Strategy) ➔ Domain Workers (Execution) with bounded scopes. |
| **Zero-Trust Guardrails** | `Affaan-M/AgentShield`, `Affaan-M/ECC` | JIT tool whitelisting, sandbox isolation, split-route security, anti-injection filters. |
| **Self-Healing & Evals** | `AgriciDaniel/agentic-habits`, `deepseek-ai/deepseek-harness`, `google/ax` | Textual optimization of skills (`best_skill.md`) on failure; deterministic trajectory logs. |
| **Context-as-Wires DAG** | `chenxiachan/thoughtdag`, `justrach/codegraff` | Explicit edge-based context passing (no global conversation bloat); branching history DAG. |

---

## ⚙️ Core Architecture Layers in DNK_OS_APP

```
+--------------------------------------------------------------------------+
|                        HUMAN-IN-THE-LOOP (HITL)                          |
|         Desktop Shell (Tauri v2 + Rust) / Visual Canvas (XYFlow)          |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                     TASK FOREST & THOUGHTDAG ENGINE                      |
|   Epics ➔ Features ➔ Tasks ➔ Atomic Slices (Topological DAG Resolution)   |
|         Bidirectional Sync: Obsidian Vault (.md / .canvas / Dataview)     |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                      AGENT HARNESS & EVALUATION GATE                     |
|  - Microkernel IoC Engine & Trajectory Logger (Google AX / DeepSeek)     |
|  - Zero-Trust Sandboxing & JIT Tooling (AgentShield / ECC)               |
|  - Deterministic Machine Verification (Anti-Mock Runtime Testing)        |
|  - Textual Skill Evolution / Self-Healing (best_skill.md distillation)    |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                      SWARM EXECUTION (FastMCP WORKERS)                   |
|     dnk_dev_fullstack  |  gerych_builder  |  dnk_shopify  |  herich_lib  |
+--------------------------------------------------------------------------+
```

---

## 📋 Mandatory Implementation Protocols

### 1. Specification Standard (`specs/`)
All new capabilities in `DNK_OS_APP` must be preceded by formal specifications in `specs/`:
- `07_AGENT_HARNESS_AND_EVALS_SPEC.md`: Trajectory recording, deterministic verification gates, automated benchmark tests.
- `08_THOUGHTDAG_AND_CANVAS_ENGINE_SPEC.md`: Canvas node schemas, wire-based context passing, undo/redo state DAG.
- `09_AGENTIC_SECURITY_AND_SANDBOX_SPEC.md`: Subprocess isolation, token-budget enforcement, permission escalation ladder.

### 2. Obsidian Task Forest Hygiene
- **YAML Frontmatter on Line 1**: Mandatory fields: `task_id`, `title`, `status`, `assigned_agent`, `priority`, `complexity_score`, `inputs`, `outputs`.
- **MRH Header Format**: Use HTML comments (`<!-- --- DNK-MRH-HEADER --- ... -->`) immediately after YAML frontmatter to maintain Obsidian property compatibility.
- **Wikilink Edges**: Express parent/child/dependency relationships as `[[Task Note]]` links for native graph navigation.

### 3. Trajectory Evals & Anti-Mock Verification
- **Anti-Mock Invariant**: Unit tests relying purely on mocks are insufficient for core agent actions. Verification requires real execution proof (FastMCP call, live HTTP status, CLI exit code 0).
- **Textual Skill Optimization**: When an agent hits execution errors, distill the root cause into `best_skill.md` or a skill `references/` note to improve future iterations without model retraining.
