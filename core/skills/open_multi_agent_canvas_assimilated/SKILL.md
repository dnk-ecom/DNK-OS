---
name: open_multi_agent_canvas_assimilated
description: "Assimilated SOTA patterns and architecture from CopilotKit/open-multi-agent-canvas."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-20"
track: "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)"
license: "open-multi-agent-canvas"
target_worker: "gerych_builder"
---

# 🌐 OPEN-MULTI-AGENT-CANVAS Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[CopilotKit/open-multi-agent-canvas](https://github.com/CopilotKit/open-multi-agent-canvas)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `CopilotKit/open-multi-agent-canvas`
- **License**: `open-multi-agent-canvas`
- **Assigned Evolution Track**: `Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)`
- **Target Swarm Worker**: `gerych_builder`
- **Architectural Directive**: CLEAN-ROOM REVERSE ENGINEERING ONLY: Verbatim copying is forbidden. Synthesize independent MIT contracts.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `apps/web/components/canvas/ or packages/archify/`
- **High-Level Purpose**: The open-source multi-agent chat interface that lets you manage multiple agents in one dynamic conversation and add MCP servers for deep research

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe A: Swarm Worker Task Delegation
Delegate implementation directly to **`gerych_builder`**:
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="gerych_builder",
    action="assimilate_adapter",
    payload={
        "technology": "CopilotKit/open-multi-agent-canvas",
        "track": "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)",
        "action": "Implement spatial nodes, directional graph layout, and canvas serialization bridges."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from open-multi-agent-canvas
from pydantic import BaseModel, Field

class OpenMultiAgentCanvasConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Strict Clean-Room Isolation: Under no circumstances copy proprietary or copyleft code directly.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct code copying is strictly prohibited. Clean-room synthesis only.
