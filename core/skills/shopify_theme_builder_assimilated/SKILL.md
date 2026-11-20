---
name: shopify_theme_builder_assimilated
description: "Assimilated SOTA patterns and architecture from moVictor99/shopify-theme-builder."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-29"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "dnk_shopify"
---

# 🌐 SHOPIFY-THEME-BUILDER Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[moVictor99/shopify-theme-builder](https://github.com/moVictor99/shopify-theme-builder)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `moVictor99/shopify-theme-builder`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_shopify`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `Liquid`
- **Target Component Target**: `services/dnk_shopify/ or apps/web/components/ecom/`
- **High-Level Purpose**: Interview-first skill that builds complete, theme-editor-controllable Online Store 2.0 Shopify themes (token-driven, theme-check clean, bilingual/RTL). Works with Claude, Codex, Cursor, Windsurf.

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
        "technology": "moVictor99/shopify-theme-builder",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Synthesize AST Liquid transformers, Shopify Functions (Wasm), and e-commerce schemas."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from shopify-theme-builder
from pydantic import BaseModel, Field

class ShopifyThemeBuilderConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
