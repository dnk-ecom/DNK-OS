# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/canvas_human_in_the_loop_approval_mvp.md"
# purpose: "Architecture, Model, Rules, and Testing Patterns for Canvas Human-in-the-Loop Approval MVP (CANVAS-004)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-10"
# author: "DNK-e.com Maksym / Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Canvas Human-in-the-Loop Approval MVP (CANVAS-004)

## 1. Overview
The Canvas Human-in-the-Loop Approval MVP introduces a pre-execution safety gate for destructive or high-risk state changes on the Spatial Canvas. Autonomous agents or collaborators proposing critical operations must request human approval before changes are committed to `CanvasState`.

## 2. Core Models (`core/canvas/approval.py`)

### ApprovalRequest
```python
class ApprovalRequest(BaseModel):
    request_id: str
    created_at: str
    canvas_id: str
    operation_type: str
    operation_payload: Dict[str, Any]
    requester_id: str = "gerych_prime"
    approver_id: str = "maksym"
    status: str = "pending"  # pending | approved | rejected
    reason: Optional[str] = None
```

### ApprovalHistoryEntry
```python
class ApprovalHistoryEntry(BaseModel):
    request_id: str
    decided_at: str
    approver_id: str = "maksym"
    decision: str  # approved | rejected
    reason: Optional[str] = None
    canvas_id: Optional[str] = None
    operation_type: Optional[str] = None
```

## 3. Critical Operation Rules
An operation requires approval if and only if:
1. `canvas.node.remove`: Deleting a canvas node (loss of component state or tasks).
2. `canvas.edge.remove`: Deleting a DAG connection or dependency edge.
3. `canvas.state.reset`: Total reset or wipe of canvas state.
4. `canvas.node.move`: Relocation with large coordinate displacement (>500px euclidean or component distance) or marked critical.

Non-critical operations (`canvas.node.add`, `canvas.edge.add`, `canvas.node.update`, minor moves <= 500px) do not trigger approval requirements.

## 4. CLI Workflow (`scripts/system/canvas_approval.py`)

```bash
# 1. Create a request
./.venv/bin/python3 scripts/system/canvas_approval.py request \
  --canvas-id main-canvas \
  --operation-type canvas.node.remove \
  --operation-payload '{"node_id":"plugin-001"}' \
  --requester gerych_prime

# 2. List pending requests
./.venv/bin/python3 scripts/system/canvas_approval.py list-pending

# 3. Decide on request
./.venv/bin/python3 scripts/system/canvas_approval.py decide \
  --request-id <request_id> \
  --approver maksym \
  --decision approved

# 4. View history
./.venv/bin/python3 scripts/system/canvas_approval.py history \
  --canvas-id main-canvas
```

## 5. Testing & Verification Pitfall
- **AST / Token Scanning Pitfall**: When writing static safety tests that verify no HTTP clients or external network tools are used, avoid matching bare substrings like `"requests."`. Local identifiers like `all_requests.append(...)` contain `"requests."` and cause false positive test failures.
- **Remedy**: Check for import tokens (`import requests`, `from requests`) or function invocation signatures (`requests.get`, `requests.post`) rather than naive substring matching.
- **Strict Relative Path Invariant**: Always enforce `os.path.isabs(path)` rejection on file inputs.
