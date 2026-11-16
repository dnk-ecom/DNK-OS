<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/plugin_capability_graph_and_execution_plan_protocol.md"
# purpose: "Plugin Capability Graph and Declarative Execution Plan Architecture Protocol"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---
-->

# 🔌 Plugin Capability Graph & Declarative Execution Plan Protocol (PLUGIN-006 / PLUGIN-007)

## 1. Architectural Purpose
Provides a deterministic, zero-execution planning and capability discovery layer for DNK OS plugins. It bridges developer/agent task requirements with certified plugin capabilities without executing code, activating plugins, or mutating runtime state.

---

## 2. Capability Graph Topology (`core/plugins/capability_graph.py`)

### Data Model
- **`CapabilityNode`**: Represents a plugin registered with a set of exported capabilities.
  ```python
  class CapabilityNode(BaseModel):
      plugin_id: str
      capabilities: list[str] = Field(default_factory=list)
      dependencies: list[str] = Field(default_factory=list)
  ```
- **`CapabilityEdge`**: Directed dependency edge between plugins (`source_plugin` depends on `target_plugin`).
- **`CapabilityGraph`**: Container holding all nodes, edges, generated timestamp, and counts.

### Key Invariant: Relative Path Enforcement
All graph I/O and persistence (`templates/plugin/capability_graph.json`) MUST use strictly relative paths. Absolute paths (`/Users/...`, `/etc/...`) and traversal patterns (`../`) are blocked fail-closed.

---

## 3. Execution Plan State Machine (`core/plugins/execution_plan.py`)

### Data Model
- **`ExecutionStep`**: Individual unit of work mapped to a required capability and resolved plugin provider.
  ```python
  class ExecutionStep(BaseModel):
      step_id: int
      plugin_id: str = ""
      capability: str
      input_schema: dict[str, Any] = Field(default_factory=dict)
      output_schema: dict[str, Any] = Field(default_factory=dict)
  ```
- **`ExecutionPlan`**: Full ordered plan for a task.
  ```python
  class ExecutionPlan(BaseModel):
      task_id: str
      description: str
      steps: list[ExecutionStep] = Field(default_factory=list)
      total_steps: int = 0
      status: PlanStatus = PlanStatus.DRAFT  # "draft" | "validated" | "blocked"
  ```

### State Transitions
```
                [ create_plan() ]
                        │
                        ▼
                     [draft]
                        │
             [ validate_plan(graph) ]
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
  All steps have                Any step missing
  valid provider                provider in graph
         │                             │
         ▼                             ▼
    [validated]                    [blocked]
```

- **`draft`**: Plan instantiated, step ordering created, initial provider assigned if present in graph.
- **`validated`**: Graph inspection confirms every step has a certified, registered plugin providing the capability.
- **`blocked`**: At least one step has `plugin_id == ""` because no plugin in the capability graph exports the capability.

---

## 4. CLI Interaction Contract (`scripts/system/plugin_execution_plan.py`)

```bash
# 1. Create a plan
./.venv/bin/python3 scripts/system/plugin_execution_plan.py create \
  --task-id <task_id> \
  --description "<description>" \
  --required-capabilities <cap1> <cap2>

# 2. Inspect plan in terminal
./.venv/bin/python3 scripts/system/plugin_execution_plan.py show <task_id>

# 3. Validate plan against capability graph
./.venv/bin/python3 scripts/system/plugin_execution_plan.py validate <task_id>
```

---

## 5. Absolute Safety & Zero-Execution Invariants
1. **No Code Execution**: Neither `capability_graph.py` nor `execution_plan.py` imports, activates, or invokes plugin code.
2. **No Network / Secrets**: No HTTP requests, external API calls, or vault secrets access.
3. **Deterministic Persistence**: Plans persist under `templates/plugin/execution_plans/<task_id>.json`.
4. **Decoupled Handoff**: Serves as input for the downstream isolated sandbox execution engine (PLUGIN-008).
