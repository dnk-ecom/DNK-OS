---
name: rynix_studio_assimilated
description: "Assimilated SOTA patterns and architecture from Nexvyn/rynix-studio."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-18"
track: "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)"
license: "rynix-studio"
target_worker: "dnk_video_ai_creator"
---

# 🌐 RYNIX-STUDIO Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[Nexvyn/rynix-studio](https://github.com/Nexvyn/rynix-studio)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `Nexvyn/rynix-studio`
- **License**: `rynix-studio`
- **Assigned Evolution Track**: `Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)`
- **Target Swarm Worker**: `dnk_video_ai_creator`
- **Architectural Directive**: CLEAN-ROOM REVERSE ENGINEERING ONLY: Verbatim copying is forbidden. Synthesize independent MIT contracts.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `services/dnk_video/ or packages/video-audit-core/`
- **High-Level Purpose**: Real-time creative effects for images, video, and camera - entirely in your browser. Halftone, ASCII, dithering, dot grids, and 30+ more. No upload. Fully on-device.

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
        "technology": "Nexvyn/rynix-studio",
        "track": "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)",
        "action": "Implement high-performance streaming animation pipeline and real-time generation contracts."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from rynix-studio
from pydantic import BaseModel, Field

class RynixStudioConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Strict Clean-Room Isolation: Under no circumstances copy proprietary or copyleft code directly.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct code copying is strictly prohibited. Clean-room synthesis only.
