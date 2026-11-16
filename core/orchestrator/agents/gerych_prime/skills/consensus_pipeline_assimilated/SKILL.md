---
name: consensus_pipeline_assimilated
description: "Assimilated SOTA patterns and architecture from fangqian616/consensus-pipeline."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-18"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "dnk_dev_fullstack"
---

# 🌐 CONSENSUS-PIPELINE Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[fangqian616/consensus-pipeline](https://github.com/fangqian616/consensus-pipeline)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `fangqian616/consensus-pipeline`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_dev_fullstack`
- **Architectural Directive**: Direct template and component integration is authorized.

## 📁 Core Architecture & Specifications
- **Stack**: `Python`
- **Target Component Target**: `apps/api/routers/ or services/dnk_core/`
- **High-Level Purpose**: Multi-agent department framework for long-form complex tasks, fighting AI hallucination, validated on academic research. 共识管线：多智能体部门长线任务解决框架，对抗AI幻觉，以学术研究为验证场景。

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
        "technology": "fangqian616/consensus-pipeline",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Design clean Pydantic v2 schemas, REST/gRPC endpoints, and transactional repositories."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
# Clean-Room Schema derived from consensus-pipeline
from pydantic import BaseModel, Field

class ConsensusPipelineConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enables feature adapter")
    mode: str = Field(default="auto", description="Execution mode")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[LICENSE_BOUNDARY]**: Respect upstream license notices and attribution.
4. **[CLEAN-ROOM REVERSE-ENGINEERING INVARIANT]**: Direct template adoption authorized under permissive license.
