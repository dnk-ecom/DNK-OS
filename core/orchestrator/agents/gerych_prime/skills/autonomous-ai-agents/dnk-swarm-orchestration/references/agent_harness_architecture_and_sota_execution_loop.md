# --- DNK-MRH-HEADER ---
# mrh_id: "references/agent_harness_architecture_and_sota_execution_loop.md"
# purpose: "SOTA Agent Harness Architecture, Canonical Engine, Swarm Join Barrier & Evaluation Loops."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-09-07"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🎛️ SOTA Agent Harness Architecture, Canonical Engine & Swarm Join Barrier

## 1. Paradigm: Model vs Harness vs Runtime
- **Model (Brain)**: Raw LLM/LMM generating thoughts and structured tool calls.
- **Harness (Conductor / Scaffolding)**: Application-level runtime turning reasoning into deterministic verified action. Enforces context budgeting, tool filtering (ToolRAG), blast radius gates, loop tracking, self-healing, and task completion.
- **Runtime (Hands / Sandbox)**: Virtualenv (`.venv`), Docker container sandbox, OS subprocesses, PTY, or Git worktrees.

## 2. Canonical Harness Implementation (`core/framework/canonical_harness_engine.py`)
```python
from core.framework.canonical_harness_engine import (
    CanonicalHarnessEngine,
    HarnessConfig,
    HarnessStatus,
    TurnRecord,
    HarnessResult,
    ProgressiveToolCatalog,
    CircuitBreakerGuard,
)
```

### Core Subsystems:
1. **Dynamic Context Engine & Progressive Tool Disclosure (ToolRAG)**:
   - `ProgressiveToolCatalog`: System starts with core baseline tools (4 tools: `read_file`, `patch`, `write_file`, `terminal`).
   - Domain-specific toolsets (e.g. `shopify`, `video`, `db`, `swarm`) are loaded dynamically based on task domain triage.
   - Eliminates 60–85% of input token overhead per turn.
2. **Circuit Breakers (`CircuitBreakerGuard`)**:
   - **Anti-Read Loop**: Blocks reading the same unmutated file > 2 times. Writing or patching the file resets the read counter.
   - **Anti-Error Loop**: Blocks execution if the exact same tool failure occurs > 3 consecutive times.
3. **Closed-Loop Self-Healing Interceptor**:
   - Intercepts tool errors before raw tracebacks enter model context.
   - Automatically queries `dnk_query_error_solutions(error_text)`.
   - Injects structured distillation advice (`[SELF-HEALING DISTILLED ADVICE]`) directly into the agent's turn ledger.
4. **Append-Only State Ledger (`HarnessSession`)**:
   - Turn-by-turn transaction log with timestamps, token usage, tool calls, results, and error metadata.
   - Guarantees complete auditability and crash recovery.
5. **Master Completion Gate**:
   - Prohibits premature model claims of completion. Requires deterministic test verification (`scripts/verify_all.sh` or targeted test suite) before state transitions to `SUCCESS`.

## 3. Dynamic Tool Catalog Integration (`core/orchestrator/lazy_tool_loader.py`)
Integrated via `LazyToolLoader.configure_progressive(goal=..., explicit_toolsets=...)`:
```python
from core.orchestrator.lazy_tool_loader import lazy_tool_loader

# Configure minimal tool footprint dynamically based on task prompt
catalog = lazy_tool_loader.configure_progressive(
    goal="Create a Shopify liquid product card and optimize styling",
    explicit_toolsets=["shopify"]
)
active_tools = lazy_tool_loader.get_active_tools()
# Only baseline + shopify tools loaded; avoids injecting 50+ tool schemas into context!
```

## 4. Swarm Join Barrier & Collision Sentinel (`core/orchestrator/swarm_coordinator.py`)
Parallel subagents executing simultaneously risk silent file overwrite races or committing failed code. `SwarmJoinBarrier` solves this at synchronization:
```python
from core.orchestrator.swarm_coordinator import SwarmJoinBarrier

barrier = SwarmJoinBarrier()
barrier_report = barrier.evaluate(tasks=tasks, worker_results=results)
# barrier_report keys:
# - join_status: "PASSED" | "COLLISION_DETECTED" | "WORKER_FAILED"
# - safe_to_commit: bool (True only if all workers succeeded and no target file overlap)
# - colliding_files: list of paths claimed by >1 worker
# - error_summary: aggregated errors from failed workers
```
Integrated automatically into `GerychSwarmCoordinator.dispatch_parallel()`. If any worker fails or file collisions are detected, `safe_to_commit` is set to `False`, blocking premature Git commits.

## 5. Evaluation & Benchmarking Harness (`core/framework/eval_harness.py`)
```python
from core.framework.eval_harness import (
    AgentEvalHarness,
    GoldenTestCase,
    EvalResult,
    SuiteSummary,
    Tier1DeterministicGrader,
    Tier2TrajectoryGrader,
    Tier3RubricGrader,
)
```

### Multi-Tier Grading Architecture:
- **Tier 1 (Deterministic)**:
  - Verifies presence and contents of expected output files.
  - Regex pattern matching on generated artifacts.
  - Execution of exit-code zero verification tests (`pytest`).
- **Tier 2 (Trajectory & Blast Radius Profiling)**:
  - Turn step-count bounds (`max_turns`).
  - Token expenditure threshold checks (`token_budget`).
  - Zero forbidden tool invocations (e.g., preventing interactive `gh auth login` or destructive shell commands).
  - Detection of hallucinated / invalid tool names.
- **Tier 3 (Rubric & Hygiene Auditing)**:
  - Mandatory DNK-MRH headers (`# --- DNK-MRH-HEADER ---`).
  - Universal Relative Path Invariant (strictly flags `/Users/...` or `/home/...`).
  - Secret & token sanitization (zero unmasked API keys/passwords).

### Golden Dataset & CI Execution (`.github/workflows/agent_eval_harness.yml`):
- 16 golden test cases in `tests/eval_datasets/` across Shopify Liquid, FastAPI Backend, Database/Architecture, and RAG/Video.
- CLI Runner:
```bash
./.venv/bin/python3 core/framework/eval_harness.py --dataset-dir tests/eval_datasets --output benchmark_report.json --fail-on-regression
```
- Automatically executes in CI on PRs affecting `core/**` and on schedule (Mondays at 04:00 UTC).

## 6. Verification & Test Suite
Targeted test suite verifying harness engine, tool loader, eval framework, and swarm join barrier:
```bash
./.venv/bin/pytest tests/framework/ tests/core/test_lazy_tool_loader.py tests/core/test_swarm_join_barrier.py
```
Output: 20 passed in 0.11s.
