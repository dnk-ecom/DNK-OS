---
name: excalidraw_diagram_assimilated
description: "Assimilated SOTA patterns and architecture from alxmax/excalidraw-diagram."
version: "1.0.0"
category: "research"
assimilated_at: "2026-10-08"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "gerych_builder"
---

# 🌐 EXCALIDRAW-DIAGRAM Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[alxmax/excalidraw-diagram](https://github.com/alxmax/excalidraw-diagram)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `alxmax/excalidraw-diagram`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_builder`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `Python`
- **Target Component Target**: `apps/web/components/canvas/ or packages/archify/`
- **High-Level Purpose**: Claude Code skill: describe a system, get an editable Excalidraw scene + self-contained HTML viewer. Stdlib-only Python builder with layout gates; no npm, no API key.

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
        "technology": "alxmax/excalidraw-diagram",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Implement spatial nodes, directional graph layout, and canvas serialization bridges."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from excalidraw-diagram
from pydantic import BaseModel, Field

class ExcalidrawDiagramConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
