---
name: ecc_assimilated
description: "Assimilated SOTA patterns and architecture from affaan-m/ECC."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-15"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "dnk_dev_fullstack"
---

# 🌐 ECC Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[affaan-m/ECC](https://github.com/affaan-m/ECC)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `affaan-m/ECC`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_dev_fullstack`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `JavaScript`
- **Target Component Target**: `apps/api/routers/ or services/dnk_core/`
- **High-Level Purpose**: The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond.

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
        "technology": "affaan-m/ECC",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Design clean Pydantic v2 schemas, REST/gRPC endpoints, and transactional repositories."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from ECC
from pydantic import BaseModel, Field

class EccConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
