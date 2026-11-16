---
name: freellmapi_assimilated
description: "Assimilated SOTA patterns and architecture from tashfeenahmed/freellmapi."
version: "1.0.0"
category: "research"
assimilated_at: "2026-10-24"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "dnk_dev_fullstack"
---

# 🌐 FREELLMAPI Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `tashfeenahmed/freellmapi`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_dev_fullstack`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `apps/api/routers/ or services/dnk_core/`
- **High-Level Purpose**: 7.4 billion tokens per month. 34 free LLM providers. 635 free model endpoints. All behind one /v1 endpoint, plus any custom OpenAI-compatible endpoint. Smart routing, automatic failover, encrypted keys. Personal experimentation only.

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
        "technology": "tashfeenahmed/freellmapi",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Design clean Pydantic v2 schemas, REST/gRPC endpoints, and transactional repositories."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from freellmapi
from pydantic import BaseModel, Field

class FreellmapiConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
