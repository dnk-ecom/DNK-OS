# --- DNK-MRH-HEADER ---
# mrh_id: "skills/sota-repository-assimilation/references/agent_native_dual_surface_and_hitl_dispatch_patterns.md"
# purpose: "Assimilated SOTA patterns from BuilderIO/agent-native: Dual-Surface Actions, HITL Approval Workflows, and Visual Plans Canvas."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-21"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🧬 Agent-Native SOTA Patterns (BuilderIO/agent-native)

Assimilated patterns from BuilderIO/agent-native (MIT, 5.2k+ stars):

## 1. Dual-Surface Action Pattern (`core/framework/dual_surface_actions.py`)
In traditional AI-assisted web applications, tool definitions for LLMs and UI action handlers are implemented separately.

**DNK OS Clean-Room Synthesis**:
Define the capability once via a shared declarative schema (`DualSurfaceAction` with Pydantic):
- **FastMCP Tool Layer**: Automatic registration in `FastMCPDispatcher` via `bind_to_fastmcp_dispatcher()`.
- **Frontend UI Manifest**: Exported via `/api/v1/actions/manifest` with JSON Schemas.
- **Hook Layer**: Consumed in React via `apps/web/ui/hooks/useDualSurfaceActions.ts`.
- **Zero Schema Drift**: Changes to backend `input_schema` reflect immediately in frontend validation.

```python
from pydantic import BaseModel, Field
from core.framework.dual_surface_actions import DualSurfaceAction, action_registry

class UpdatePlanSchema(BaseModel):
    node_id: str = Field(..., description="Target node ID")
    status: str = Field(..., description="pending | in_progress | completed")

class UpdatePlanAction(DualSurfaceAction):
    action_id = "update_plan_node"
    name = "Update Plan Node"
    description = "Updates node status on visual canvas"
    input_schema = UpdatePlanSchema
    is_dangerous = False

    def execute(self, payload=None, context=None, **kwargs):
        # Implementation logic
        return {"status": "updated", "node_id": payload["node_id"]}

action_registry.register(UpdatePlanAction())
```

## 2. Dispatch Control Plane & HITL Approval Queue (`core/framework/swarm_approval.py`)
State machine for human-in-the-loop (HITL) authorization:
- Sensitive operations (`is_dangerous=True`, e.g. production deployments, billing mutations, delete actions) are intercepted automatically.
- Emits an `ApprovalTicket` (`pending_approval`) with risk level (`critical`, `high`, `medium`, `low`).
- The UI renders `apps/web/components/canvas/SwarmApprovalCard.tsx` inside `HitlApprovalDrawer.tsx` with Dark Teal tokens (`#162c2f`, `#224447`, `#35d5d5`).
- Approving via `POST /api/v1/approvals/{ticket_id}/approve` unblocks execution with an approval bypass token.

## 3. Visual Plans & Canvas Layout Sync
- Seamless dual-pane workspace: conversational stream on the left, reactive visual canvas on the right.
- Real-time synchronization between Swarm Agent task execution and visual node status chips (`pending`, `running`, `done`).
- Directly maps to DNK OS `ThoughtDagNoteNode` and `HitlApprovalDrawer`.
