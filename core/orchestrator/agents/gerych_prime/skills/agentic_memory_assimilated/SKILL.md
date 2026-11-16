---
name: agentic_memory_assimilated
description: "Assimilated SOTA patterns and architecture from Verace-Pvt-Ltd/agentic-memory."
version: "1.0.0"
category: "research"
assimilated_at: "2026-10-06"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "gerych_builder"
---

# 🌐 AGENTIC-MEMORY Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[Verace-Pvt-Ltd/agentic-memory](https://github.com/Verace-Pvt-Ltd/agentic-memory)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `Verace-Pvt-Ltd/agentic-memory`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_builder`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `Python`
- **Target Component Target**: `apps/web/components/canvas/ or packages/archify/`
- **High-Level Purpose**: 6-layer persistent memory (sensory, working, episodic, semantic, long-term, procedural) with non-destructive belief revision and injection-safe context synthesis — an MCP server for Claude Code, Cursor, Antigravity, Codex CLI, and any MCP-compatible agent.

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
        "technology": "Verace-Pvt-Ltd/agentic-memory",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Implement spatial nodes, directional graph layout, and canvas serialization bridges."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from agentic-memory
from pydantic import BaseModel, Field

class AgenticMemoryConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
