---
name: tributary_assimilated
description: "Assimilated SOTA patterns and architecture from ximing/tributary."
version: "1.0.0"
category: "research"
assimilated_at: "2026-10-13"
track: "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)"
license: "tributary"
target_worker: "gerych_researcher"
---

# 🌐 TRIBUTARY Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[ximing/tributary](https://github.com/ximing/tributary)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `ximing/tributary`
- **License**: `tributary`
- **Assigned Evolution Track**: `Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)`
- **Target Swarm Worker**: `gerych_researcher`
- **Architectural Directive**: CLEAN-ROOM REVERSE ENGINEERING ONLY: Verbatim copying is forbidden. Synthesize independent MIT contracts.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `core/research/ or docs/tech/specs/`
- **High-Level Purpose**: 给会分叉的问题用的非线性脑图对话。每张卡片是一个问题，连线标出它从哪一句长出来。可以顺着往下问，也可以在旁边另开一条，不需要的枝可以收起。

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe A: Swarm Worker Task Delegation
Delegate implementation directly to **`gerych_researcher`**:
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="gerych_researcher",
    action="assimilate_adapter",
    payload={
        "technology": "ximing/tributary",
        "track": "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)",
        "action": "Deep AST extraction, competitive architectural synthesis, and algorithmic benchmarking."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from tributary
from pydantic import BaseModel, Field

class TributaryConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Strict Clean-Room Isolation: Under no circumstances copy proprietary or copyleft code directly.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct code copying is strictly prohibited. Clean-room synthesis only.
