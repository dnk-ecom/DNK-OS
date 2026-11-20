---
name: agent_native_assimilated
description: "Assimilated SOTA patterns and architecture from BuilderIO/agent-native (Dual-Surface Actions, Approval Workflows, Visual Plans Canvas)."
version: "1.1.0"
category: "research"
assimilated_at: "2026-09-21"
track: "Track 1 & 2: Clean-Room Reverse Engineering & Pattern Synthesis"
license: "MIT"
target_worker: "gerych_researcher"
---

# 🌐 AGENT-NATIVE Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[BuilderIO/agent-native](https://github.com/BuilderIO/agent-native)**.

## 📌 Repository Intel & Scope
- **Repository**: `BuilderIO/agent-native`
- **Stars**: `⭐ 5,815+`
- **License**: `MIT`
- **Key Concepts**: Dual-Surface Actions (`defineAction`), Workspace Control Plane (`@agent-native/dispatch`), Visual Canvas Apps (`plans`).

---

## 🔬 Core Architectural Patterns

### Pattern A: Dual-Surface Actions (Agent Tool + UI Hook)
Capability defined once with shared schema, exposed simultaneously to LLM and React UI:
```typescript
// Shared Action Contract Concept
import { z } from "zod";

export const createNodeAction = {
  id: "canvas.create_node",
  schema: z.object({
    title: z.string(),
    type: z.enum(["task", "doc", "service"]),
    position: z.object({ x: z.number(), y: z.number() }),
  }),
  // Exposed to FastMCP as a tool for Gerych/Swarm Workers
  // Exposed to React as useActionMutation("canvas.create_node")
};
```

### Pattern B: Human-in-the-Loop Approval Queue (`packages/dispatch`)
Critical mutations (Shopify, deletions, payments) enter a pending approval state:
```typescript
export interface ApprovalRequest {
  id: string;
  agentId: string;
  actionId: string;
  payload: Record<string, unknown>;
  status: "pending" | "approved" | "rejected";
  createdAt: string;
  approvedBy?: string;
}
```

---

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe 1: Dispatching Research/Adaptation to Swarm
Delegate clean-room contract synthesis to `gerych_researcher`:
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="gerych_researcher",
    task_description="Extract Dual-Surface Action contract generator from agent_native_assimilated into core/fastmcp bridge.",
    workspace_id="ws-alpha-001"
)
```

### Recipe 2: Adding Approval Interceptor to Dangerous Endpoints
Apply the dispatch approval pattern before executing irreversible agent actions:
```python
async def execute_swarm_action(action_name: str, payload: dict, is_dangerous: bool = False):
    if is_dangerous:
        # Create approval request in DNK OS Visual Shell DB
        approval_id = await create_hitl_approval_ticket(action_name, payload)
        return {"status": "pending_approval", "approval_id": approval_id}
    return await run_action_direct(action_name, payload)
```

---

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[CLEAN_ROOM_INTEGRATION]**: Do not install `@agent-native/*` directly into DNK OS root. Synthesize native Python FastMCP / TypeScript React implementations.
4. **[SWARM_PARALLEL_AWARE]**: Do not degrade DNK OS multi-agent routing into a single-agent chat paradigm.
