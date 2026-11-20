---
name: keyper_assimilated
description: "Assimilated SOTA patterns and architecture from pinkpixel-dev/keyper."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-18"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "NOASSERTION"
target_worker: "dnk_shopify"
---

# 🌐 KEYPER Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[pinkpixel-dev/keyper](https://github.com/pinkpixel-dev/keyper)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `pinkpixel-dev/keyper`
- **License**: `NOASSERTION`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_shopify`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `TypeScript`
- **Target Component Target**: `services/dnk_shopify/ or apps/web/components/ecom/`
- **High-Level Purpose**: 🔐 A self-hosted credential manager with zero-knowledge encryption, multi-user support, and emergency recovery. Store API keys, passwords, and secrets securely with your own database. Features AES-256-GCM encryption, Argon2 key derivation, PWA support, and professional-grade security architecture.

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
        "technology": "pinkpixel-dev/keyper",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Synthesize AST Liquid transformers, Shopify Functions (Wasm), and e-commerce schemas."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from keyper
from pydantic import BaseModel, Field

class KeyperConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
