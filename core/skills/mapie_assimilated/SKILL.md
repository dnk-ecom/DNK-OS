---
name: mapie_assimilated
description: "Assimilated SOTA patterns and architecture from scikit-learn-contrib/mapie."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-18"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "BSD-3-Clause"
target_worker: "dnk_dev_fullstack"
---

# 🌐 MAPIE Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[scikit-learn-contrib/mapie](https://github.com/scikit-learn-contrib/mapie)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `scikit-learn-contrib/mapie`
- **License**: `BSD-3-Clause`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_dev_fullstack`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `Jupyter Notebook`
- **Target Component Target**: `apps/api/routers/ or services/dnk_core/`
- **High-Level Purpose**: A scikit-learn-compatible library for estimating prediction intervals and controlling risks, based on conformal predictions.

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe A: Swarm Worker Task Delegation
Delegate implementation directly to **`dnk_dev_fullstack`**:
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="dnk_dev_fullstack",
    action="assimilate_adapter",
    payload={
        "technology": "scikit-learn-contrib/mapie",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Design clean Pydantic v2 schemas, REST/gRPC endpoints, and transactional repositories."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from mapie
from pydantic import BaseModel, Field

class MapieConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
