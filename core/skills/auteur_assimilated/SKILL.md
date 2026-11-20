---
name: auteur_assimilated
description: "Assimilated SOTA patterns and architecture from agiwhitelist/auteur."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-18"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "gerych_researcher"
---

# 🌐 AUTEUR Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[agiwhitelist/auteur](https://github.com/agiwhitelist/auteur)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `agiwhitelist/auteur`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_researcher`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `JavaScript`
- **Target Component Target**: `core/research/ or docs/tech/specs/`
- **High-Level Purpose**: The Claude Code skill that directs a website like a film. Commit-sheet, generated assets, build, and an executable anti-slop linter that gates every ship.

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
        "technology": "agiwhitelist/auteur",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Deep AST extraction, competitive architectural synthesis, and algorithmic benchmarking."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from auteur
from pydantic import BaseModel, Field

class AuteurConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
