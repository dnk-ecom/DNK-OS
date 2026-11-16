# 🛡️ Darkroom CC-Settings: Proof Gates, Drift Fuse & Context Compaction Hook

<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "references/darkroom_cc_settings_proof_gates_and_drift_fuse.md"
# purpose: "Operational reference for proof-of-work validation, drift-fuse watchdog, and context handoff hooks from darkroomengineering/cc-settings."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-30"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

## 🎯 Architectural Mechanisms

### 1. Proof-of-Work Gate (Amdahl-Shrink Principle)
Human review attention is the ultimate bottleneck in high-velocity agentic workflows.
- **Rule**: Code is strictly forbidden from being declared "done" or marked `review-ready` without real machine proof.
- **Battery**:
  1. Static typing passes (`tsc --noEmit` or `pyright`).
  2. Unit and regression tests pass with `exit code 0` (`uv run pytest` or `pnpm test`).
  3. Linter clean (`eslint` / `ruff`).
  4. For UI mutations: visual artifact or headless DOM snapshot verified.

### 2. Drift-Fuse Watchdog (Anti-Entropy Circuit Breaker)
Agents suffering from context drift tend to explore adjacent files or over-refactor.
- **Contract**: Store the user's initial prompt as an immutable contract at Step 0.
- **Execution**: On every tool action, verify alignment against the contract and target file whitelist.
- **Trip Condition**: If 2 consecutive tool calls wander outside the negative scope or target directory, trip the fuse:
  - Halt automated multi-turn execution.
  - Emit an out-of-band warning with the deviated diff.
  - Require explicit re-alignment before proceeding.

### 3. PreCompact & SessionEnd Handoff Hooks
- Triggered right before agent context window compaction.
- Dumps:
  - Active goal and subtask progress (`todo.json`).
  - Modified files snapshot (`git status --porcelain`).
  - Active architectural decisions and uncommitted hypotheses.
- Output is injected directly into the post-compaction context header to eliminate post-compaction amnesia.

### 4. AST Codemap & Blast Radius Calculation
- Parse `git diff` hunks to extract altered AST symbol identifiers (functions, classes, exports).
- Traverse project import/call graph to compute the transitive closure of dependent modules.
- Formulate a targeted test execution matrix: run only the affected tests, reducing test suite latency by >85%.

### 5. Catalog & Memory Persistence Standards in DNK OS
- **Catalog Database**: `.data/repo_catalog/catalog.db` (table: `repositories`).
- **SCONES Memory**: `core.memory.scones_memory.SCONESMemoryEngine.add_memory(topic, content)`.
- **Vault Note**: `docs/vault/notes/<XXX>_<name>_sota_assimilation_audit.md`.
- **Tech Spec**: `docs/vault/tech/sota_assimilation/SOTA_<NAME>_ASSIMILATION.md`.
