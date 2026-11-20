---
name: agent_skills_assimilated
description: "Assimilated SOTA patterns and architecture from jhonatan-oliveiradev/agent-skills."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-14"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "gerych_auditor"
---

# 🌐 AGENT-SKILLS Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[jhonatan-oliveiradev/agent-skills](https://github.com/jhonatan-oliveiradev/agent-skills)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `jhonatan-oliveiradev/agent-skills`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_auditor`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `core/security/ or scripts/audit/`
- **High-Level Purpose**: Agent Skills Studio — Curated skills and installable packs for engineering, design, security, writing and product workflows.

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe A: Swarm Worker Task Delegation
Delegate implementation directly to **`gerych_auditor`**:
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="gerych_auditor",
    action="assimilate_adapter",
    payload={
        "technology": "jhonatan-oliveiradev/agent-skills",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Construct adversarial test gates, automated SAST scan rules, and security integrity shields."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from agent-skills
from pydantic import BaseModel, Field

class AgentSkillsConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
