# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/beads-task-forest-integration/references/lightweight_harness_and_thoughtdag_blueprint.md"
# purpose: "Architecture Blueprint for Lightweight Task Forest Agent Harness & ThoughtDAG Execution Engine"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-18"
# author: "Gerych Prime & Maksym"
# --- END DNK-MRH-HEADER ---

# 🧬 Lightweight Agent Harness & ThoughtDAG Blueprint

## 🎯 Architectural Context
Standard agent frameworks (LangGraph, CrewAI, AutoGen) and monolithic coding agent runtimes (Hermes, OpenCode) impose heavy prompt overhead (~5,000–8,000 standing tokens) and state-store complexity (SQLite locks, multi-profile gateways, visual DOM trees).

To achieve 10x execution speed and deterministic reliability, DNK OS partitions the execution into:
1. **Deterministic DAG Orchestrator** (Task Forest / ThoughtDAG in Pure Python / NetworkX).
2. **Stateless Micro-Workers** (Lightweight runtime with JIT tool whitelisting and ≤ 400 token system prompts).
3. **Pluggable Execution Adapters** (`backend="micro_worker"` vs `backend="hermes_headless"`).

---

## 🏛️ SOTA Architectural Patterns Assimilated

| Donor Repository | Core Pattern | Role in DNK OS Harness |
| :--- | :--- | :--- |
| `chenxiachan/thoughtdag` | **Context-as-Wires DAG** | Context flows strictly along graph edges rather than bloating a global conversation history. |
| `deepseek-ai/deepseek-harness` | **Microkernel IoC Engine** | Decouples task execution lifecycle from tool and UI plugins. |
| `affaan-m/ECC` | **Subprocess Sandboxing & JIT Tooling** | Isolates workers per task slice with strict token budgets and memory fences. |
| `coleam00/Archon` | **Deterministic Contract Validation** | Machine-verifiable artifact gating between parent and child nodes. |
| `langchain-ai/deepagents` | **DeltaChannel & BackendProtocol** | Message delta reduction ($O(N)$ growth) and unified workspace abstractions (Git Worktree vs Local). |

---

## ⚙️ Core Components & Schemas

### 1. Task Node Data Model (`TaskForestNode`)
```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class TaskForestNode:
    id: str
    goal: str
    target_files: List[str]
    required_tools: List[str]
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending | in_progress | completed | failed
    result: Optional[Dict[str, Any]] = None
    execution_backend: str = "micro_worker"  # micro_worker | hermes_headless
```

### 2. Dual Execution Adapter Interface
```python
class TaskExecutionAdapter:
    async def execute(self, node: TaskForestNode, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class MicroWorkerAdapter(TaskExecutionAdapter):
    """Direct model API calls with minimal toolset (read_file, patch, terminal)."""
    async def execute(self, node: TaskForestNode, context: Dict[str, Any]) -> Dict[str, Any]:
        # Minimal system prompt (<=400 tokens)
        # JIT tools loaded specifically for node.required_tools
        pass

class HermesHeadlessAdapter(TaskExecutionAdapter):
    """Fallback headless runner using `hermes -z` CLI."""
    async def execute(self, node: TaskForestNode, context: Dict[str, Any]) -> Dict[str, Any]:
        # hermes -z --ignore-rules -t file,terminal -m <model> "<prompt>"
        pass
```

---

### 3. Workspace Backend Protocol (`BackendProtocol`)
```python
from typing import Protocol

class BackendProtocol(Protocol):
    """Abstract interface for workspace environments (Local, Worktree, Sandbox)."""
    async def read_file(self, path: str) -> str: ...
    async def write_file(self, path: str, content: str) -> None: ...
    async def execute_command(self, cmd: str) -> str: ...
```

---

## 🛡️ Key Invariants & Guardrails
1. **Context Isolation**: Child nodes only receive upstream output explicitly wired to their dependency edges.
2. **DeltaChannel Compression**: Checkpoints store message deltas rather than accumulating full history, bounding storage growth to $O(N)$.
3. **Quality Gate Seal**: A node is marked `completed` only when deterministic verification (`scripts/verify_all.sh` or targeted `pytest`) exits with `0`.
4. **Budget Hard-Cap**: Max 15 tool calls per micro-worker turn to eliminate context entropy and infinite retry loops.
