---
name: mirofish_assimilated
description: "Assimilated SOTA patterns and architecture from 666ghj/MiroFish."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-13"
track: "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)"
license: "AGPL-3.0"
target_worker: "gerych_builder"
---
<!--
--- DNK-MRH-HEADER ---
mrh_id: "core/skills/mirofish_assimilated/SKILL.md"
purpose: "Assimilated SOTA patterns and architecture from 666ghj/MiroFish."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-13"
author: "Gerych Prime & Antigravity"
--- END DNK-MRH-HEADER ---
-->

# 🌐 MIROFISH Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[666ghj/MiroFish](https://github.com/666ghj/MiroFish)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `666ghj/MiroFish`
- **License**: `AGPL-3.0`
- **Assigned Evolution Track**: `Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)`
- **Target Swarm Worker**: `gerych_builder`
- **Architectural Directive**: CLEAN-ROOM REVERSE ENGINEERING ONLY: Verbatim copying is forbidden. Synthesize independent MIT contracts.

## 📁 Core Architecture & Specifications
- **Stack**: `Python`
- **Target Component Target**: `apps/web/components/canvas/ or packages/archify/`
- **High-Level Purpose**: A Simple and Universal Swarm Intelligence Engine, Predicting Anything. 简洁通用的群体智能引擎，预测万物

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
        "technology": "666ghj/MiroFish",
        "track": "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)",
        "action": "Implement spatial nodes, directional graph layout, and canvas serialization bridges."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from MiroFish
from pydantic import BaseModel, Field

class MirofishConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Strict Clean-Room Isolation: Under no circumstances copy proprietary or copyleft code directly.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct code copying is strictly prohibited. Clean-room synthesis only.
