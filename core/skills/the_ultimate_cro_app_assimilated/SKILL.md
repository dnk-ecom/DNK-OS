---
name: the_ultimate_cro_app_assimilated
description: "Assimilated SOTA patterns, 4-way A/B testing, Scheduled Offers, and Shopify Functions architecture from Omar92953/the-ultimate-cro-app."
version: "2.0.0"
category: "research"
assimilated_at: "2026-11-15"
track: "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)"
license: "the-ultimate-cro-app"
target_worker: "dnk_shopify"
---

# 🌐 THE-ULTIMATE-CRO-APP Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[Omar92953/the-ultimate-cro-app](https://github.com/Omar92953/the-ultimate-cro-app)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `Omar92953/the-ultimate-cro-app`
- **Active Commit**: `6c6bb3fd2a929ed75c82be2cc53659e2a1010a2f` (Nov 15, 2026)
- **License**: `UNLICENSED` (Proprietary)
- **Assigned Evolution Track**: `Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)`
- **Target Swarm Worker**: `dnk_shopify`
- **Architectural Directive**: CLEAN-ROOM REVERSE ENGINEERING ONLY: Verbatim copying is forbidden. Synthesize independent MIT contracts.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript` / React Router v7 / Polaris Web Components / Prisma (Supabase Postgres + RLS)
- **Target Component Target**: `services/dnk_shopify/` & `DNKEcom/dnk_apex_theme/`
- **High-Level Purpose**: Fullstack Shopify CRO App: Scheduled offers, 4-way A/B testing, Cart Transform bundles, Wasm discount engine, Post-Purchase Checkout UI, and MCP server.

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
        "technology": "Omar92953/the-ultimate-cro-app",
        "track": "Track 2: Clean-Room Reverse Engineering (Restrictive/Copyleft)",
        "action": "Implement Scheduled Offers, 4-way A/B engine, and Cart Validation step guards."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from the-ultimate-cro-app
from pydantic import BaseModel, Field

class TheUltimateCroAppConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Strict Clean-Room Isolation: Under no circumstances copy proprietary or copyleft code directly.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct code copying is strictly prohibited. Clean-room synthesis only.
