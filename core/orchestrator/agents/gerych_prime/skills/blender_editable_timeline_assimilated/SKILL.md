---
name: blender_editable_timeline_assimilated
description: "Assimilated SOTA patterns and architecture from CatsMansion/blender-editable-timeline."
version: "1.0.0"
category: "research"
assimilated_at: "2026-10-25"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "dnk_video_ai_creator"
---

# 🌐 BLENDER-EDITABLE-TIMELINE Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[CatsMansion/blender-editable-timeline](https://github.com/CatsMansion/blender-editable-timeline)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `CatsMansion/blender-editable-timeline`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_video_ai_creator`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `Python`
- **Target Component Target**: `services/dnk_video/ or packages/video-audit-core/`
- **High-Level Purpose**: Agent skill: hand a client a Blender video timeline they can edit themselves - native TEXT strips instead of baked-in captions, documented channel plan, silent VSE channel-push avoidance, sequencer_scene and view_transform fixes, seam-free same-colour compositing, and a backup scheme that survives an overwrite save.

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
        "technology": "CatsMansion/blender-editable-timeline",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Implement high-performance streaming animation pipeline and real-time generation contracts."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from blender-editable-timeline
from pydantic import BaseModel, Field

class BlenderEditableTimelineConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
