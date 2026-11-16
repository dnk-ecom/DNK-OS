# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/smol_worker_harness_and_sandbox_isolation_protocol.md"
# purpose: "Smol-Worker Harness, Sandbox Isolation, and Deterministic Acceptance Gate Protocol for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-25"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🏎️ Smol-Worker Harness & Sandbox Isolation Protocol

## 1. Overview & Architectural Role
Smol-Workers are lightweight, domain-scoped, isolated execution harnesses designed for fast Tier-2/SLM models (e.g., Gemini Flash, Qwen 2.5 Coder, DeepSeek-Coder).
Instead of overloading Gerych Prime (Hermes Orchestrator) with sequential, monolithic code editing and repetitive test-fixing turns, Gerych decomposes objectives via **TaskDNA DAG** and dispatches leaf tasks to standalone Smol-Workers.

---

## 2. Core Harness Invariants & Constraints

| Parameter | Smol-Worker Specification | Gerych Prime (Orchestrator) |
|---|---|---|
| **Target Models** | Fast SLM / Flash (Gemini 2.5/3.8 Flash, Qwen-Coder) | Tier-1 Frontier (Gemini Pro, Claude 3.7 Sonnet) |
| **Tool Budget** | **Strict Hard Cap: 15 tools** per atomic slice | Up to 25 tools per slice, global orchestration |
| **Tool Surface** | **4 Flat Tools**: `read`, `patch`, `search`, `run` | Full Swarm & FastMCP Toolset (100+ tools) |
| **Standing Context** | **≤ 800 tokens** (minimal system prompt, no heavy MCPs) | Dynamic LOD context & standing memory |
| **Workspace Scope** | `Target File Whitelist` + `Negative Scope` enforced | Full monorepo visibility |

---

## 3. Host-Managed State & Speculative Compaction (Patterns from Smolcoder)

1. **Host-Managed Plan (Out-of-Context State)**:
   - The task checklist, current slice ID, and step dependencies live in the host process memory (`TaskForestNode` / TaskDNA DAG), NOT in the model's chat history.
   - Compaction or context pruning never degrades the global objective.
2. **Speculative Background Compaction**:
   - During long execution runs (e.g. `pytest`, `cargo test`, `npm run build`), the harness triggers background context summarization when history exceeds 60% of context budget, freeing up inference slots when execution finishes.
3. **Periodic 24/15-Tool Circuit Breaker**:
   - If a worker performs repetitive edits without passing tests, the harness forces an immediate compiler/test check to supply fresh error feedback before tool budget exhaustion.

---

## 4. Sandbox Isolation & Concurrency Safety

To prevent git merge collisions when multiple Smol-Workers execute concurrently:
1. **Isolated Git Worktrees**:
   - Each worker runs in an ephemeral git worktree (`git worktree add .worktrees/worker-<slice_id> -b feature/worker-<slice_id>`).
2. **OCC 3-Way Structural Merge**:
   - On slice completion, changes are merged back into the primary feature branch using Optimistic Concurrency Control (`dnk_workspace_occ_merge`).

---

## 5. Caller-Owned Acceptance & Adversarial Gate

```
[ Gerych Prime ] ──► TaskDNA DAG ──► [ Smol-Worker ]
                                           │
                                     (15-step loop)
                                           │
                                           ▼
                                [ --verify Acceptance Gate ]
                                           │
                            (exit code 0 + Evidence JSON)
                                           │
                                           ▼
                                [ gerych_auditor ]
                            (Adversarial Diff Review)
                                           │
                                           ▼
                             [ Commit to TaskForest DAG ]
```

1. **Caller-Owned Verification (`--verify`)**:
   - The worker cannot mark a task `completed` by verbal assertion.
   - The host executes the caller-supplied verification command (`pytest tests/slice_test.py` or `npm test`).
2. **Adversarial Audit Gate**:
   - Before merging the diff, `gerych_auditor` checks AST modifications to ensure the worker did not mock away tests or introduce security vulnerabilities.
