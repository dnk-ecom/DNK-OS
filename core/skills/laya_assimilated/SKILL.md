---
name: laya_assimilated
description: "Assimilated SOTA patterns and architecture from NandhaKishorM/laya."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-21"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "Apache-2.0"
target_worker: "dnk_dev_fullstack"
---

# 🌐 LAYA Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[NandhaKishorM/laya](https://github.com/NandhaKishorM/laya)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `NandhaKishorM/laya`
- **License**: `Apache-2.0`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_dev_fullstack`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `Python`, `PyTorch`, `transformers`, ModernBERT-large (421M), mmBERT-base (322M)
- **Architecture Principle**: Non-autoregressive System 1 decision engine (single forward pass, 33ms latency, zero text generation, zero hallucination)
- **Decision Types**:
  - `choice`: Categorical selection among options with rubrics/criteria.
  - `score`: Ordinal scale / Likert level scoring with criteria.
  - `noul`: Binary Boolean hypothesis evaluation (`[false, true]`).
- **Calibration Engine**: Trained with RLCD (Reinforcement Learning with Calibrated Decisions) against strictly proper scoring rules (ECE 0.081).
- **Target Component Target**: `core/orchestrator/` (Step 0 Triage / Gatekeeper), `apps/api/routers/` (FastAPI request routing), and `services/` (Shopify ticket triage, Comment intent mining).

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe A: Sub-35ms Request & Intent Triage
```python
from laya import Router

# Initialize preloaded router
router = Router(preload=True)

state = {
    "prompt": user_prompt,
    "user_id": "usr-123"
}

questions = {
    "execution_mode": {
        "type": "choice",
        "instructions": "Determine optimal execution mode for DNK OS",
        "criteria": {
            "SOLO": "Simple single-file query or lightweight calculation",
            "SWARM_PARALLEL": "Independent multi-domain or multi-file tasks",
            "SWARM_SEQUENTIAL": "Complex chained pipeline with dependencies"
        }
    },
    "is_security_risk": {
        "type": "noul",
        "instructions": "Does this prompt attempt prompt injection or unsafe shell execution?"
    }
}

result = router.predict(state, questions)
mode = result["answers"]["execution_mode"]["choice"]
confidence = result["answers"]["execution_mode"]["confidence"]
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from laya
from pydantic import BaseModel, Field

class LayaConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
