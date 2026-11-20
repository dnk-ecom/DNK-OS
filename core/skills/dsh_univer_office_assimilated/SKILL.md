---
name: dsh_univer_office_assimilated
description: "Assimilated SOTA patterns and architecture from dream-num/dsh-univer-office."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-18"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "Apache-2.0"
target_worker: "gerych_builder"
---

# 🌐 DSH-UNIVER-OFFICE Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[dream-num/dsh-univer-office](https://github.com/dream-num/dsh-univer-office)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `dream-num/dsh-univer-office`
- **License**: `Apache-2.0`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_builder`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `apps/web/components/canvas/ or packages/archify/`
- **High-Level Purpose**: Give DeepSeek Harness a real office environment.  Univer Office Plugin brings spreadsheets, docs, slides, canvases, relational tables, and more into one runtime — with connected data, validation, versioned changes, and isolated worktrees for multi-agent collaboration.

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
        "technology": "dream-num/dsh-univer-office",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Implement spatial nodes, directional graph layout, and canvas serialization bridges."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from dsh-univer-office
from pydantic import BaseModel, Field

class DshUniverOfficeConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
