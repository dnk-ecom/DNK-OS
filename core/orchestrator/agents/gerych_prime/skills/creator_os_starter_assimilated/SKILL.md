---
name: creator_os_starter_assimilated
description: "Assimilated SOTA patterns and architecture from kevinbadi/creator-os-starter."
version: "1.0.0"
category: "research"
assimilated_at: "2026-10-09"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "gerych_researcher"
---

# 🌐 CREATOR-OS-STARTER Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[kevinbadi/creator-os-starter](https://github.com/kevinbadi/creator-os-starter)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `kevinbadi/creator-os-starter`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_researcher`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `core/research/ or docs/tech/specs/`
- **High-Level Purpose**: Open-source wireframe of Creator OS / Marketing OS: Next.js marketing dashboard + automation runner for creators and agencies. Bring your own keys.

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
        "technology": "kevinbadi/creator-os-starter",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Deep AST extraction, competitive architectural synthesis, and algorithmic benchmarking."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from creator-os-starter
from pydantic import BaseModel, Field

class CreatorOsStarterConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
