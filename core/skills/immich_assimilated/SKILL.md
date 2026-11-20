---
name: immich_assimilated
description: "Assimilated SOTA patterns and architecture from immich-app/immich."
version: "1.0.0"
category: "research"
assimilated_at: "2026-11-05"
track: "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)"
license: "AGPL-3.0"
target_worker: "dnk_video_ai_creator"
---

# 🌐 IMMICH Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[immich-app/immich](https://github.com/immich-app/immich)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `immich-app/immich`
- **License**: `AGPL-3.0`
- **Assigned Evolution Track**: `Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)`
- **Target Swarm Worker**: `dnk_video_ai_creator`
- **Architectural Directive**: CLEAN-ROOM REVERSE ENGINEERING ONLY: Verbatim copying is forbidden. Synthesize independent MIT contracts.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `services/dnk_video/ or packages/video-audit-core/`
- **High-Level Purpose**: High performance self-hosted photo and video management solution.

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe A: Swarm Worker Task Delegation
Delegate implementation directly to **`dnk_video_ai_creator`**:
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="dnk_video_ai_creator",
    action="assimilate_adapter",
    payload={
        "technology": "immich-app/immich",
        "track": "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)",
        "action": "Implement high-performance streaming animation pipeline and real-time generation contracts."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from immich
from pydantic import BaseModel, Field

class ImmichConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Strict Clean-Room Isolation: Under no circumstances copy proprietary or copyleft code directly.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct code copying is strictly prohibited. Clean-room synthesis only.
