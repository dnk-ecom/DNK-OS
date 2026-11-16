---
name: harness_engineering_playbook_assimilated
description: "Assimilated SOTA patterns and architecture from flyrank-bih/harness-engineering-playbook."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-30"
track: "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)"
license: "NOASSERTION"
target_worker: "dnk_shopify"
---

# 🌐 HARNESS-ENGINEERING-PLAYBOOK Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[flyrank-bih/harness-engineering-playbook](https://github.com/flyrank-bih/harness-engineering-playbook)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `flyrank-bih/harness-engineering-playbook`
- **License**: `NOASSERTION`
- **Assigned Evolution Track**: `Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)`
- **Target Swarm Worker**: `dnk_shopify`
- **Architectural Directive**: CLEAN-ROOM REVERSE ENGINEERING ONLY: Verbatim copying is forbidden. Synthesize independent MIT contracts.

## 📁 Core Architecture & Specifications
- **Stack**: `Liquid`
- **Target Component Target**: `services/dnk_shopify/ or apps/web/components/ecom/`
- **High-Level Purpose**: A real-world harness-engineering example: the agent environment (router docs, prompts, runners, gates, evidence packs, self-tests, control panel) around a Shopify theme migration. The theme is the product; everything else is the harness.

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe A: Swarm Worker Task Delegation
Delegate implementation directly to **`dnk_shopify`**:
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="dnk_shopify",
    action="assimilate_adapter",
    payload={
        "technology": "flyrank-bih/harness-engineering-playbook",
        "track": "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)",
        "action": "Synthesize AST Liquid transformers, Shopify Functions (Wasm), and e-commerce schemas."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from harness-engineering-playbook
from pydantic import BaseModel, Field

class HarnessEngineeringPlaybookConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Strict Clean-Room Isolation: Under no circumstances copy proprietary or copyleft code directly.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct code copying is strictly prohibited. Clean-room synthesis only.
