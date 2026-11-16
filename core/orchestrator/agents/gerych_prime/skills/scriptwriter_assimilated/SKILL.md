---
name: scriptwriter_assimilated
description: "Assimilated SOTA patterns and architecture from unclebob/scriptwriter."
version: "1.0.0"
category: "research"
assimilated_at: "2026-10-17"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "0BSD"
target_worker: "gerych_researcher"
---

# 🌐 SCRIPTWRITER Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[unclebob/scriptwriter](https://github.com/unclebob/scriptwriter)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `unclebob/scriptwriter`
- **License**: `0BSD`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_researcher`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `core/research/ or docs/tech/specs/`
- **High-Level Purpose**: A plain screenplay editor.

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
        "technology": "unclebob/scriptwriter",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Deep AST extraction, competitive architectural synthesis, and algorithmic benchmarking."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from scriptwriter
from pydantic import BaseModel, Field

class ScriptwriterConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
