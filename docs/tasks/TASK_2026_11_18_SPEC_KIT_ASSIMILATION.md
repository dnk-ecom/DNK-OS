---
title: "PSOD Task: Assimilation of google/spec-kit"
description: "Autonomous builder task for distilling google/spec-kit into core."
mrh_id: "docs/tasks/TASK_2026_11_18_SPEC_KIT_ASSIMILATION.md"
status: Active
archetype: TASK_SPEC
version: "1.0.0"
updated: 2026-11-18
tags:
  - task
  - sota
  - denchik
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/tasks/TASK_2026_11_18_SPEC_KIT_ASSIMILATION.md"
> purpose: "Autonomous builder task for distilling google/spec-kit into core."
> canonical_source: true
> alters_files:
>   - "core/**"
>   - "docs/architecture/DECISION_REGISTRY_ADHD.md"
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📋 PSOD DELEGATION CONTRACT: Assimilation of google/spec-kit

### 1. Problem & Context (P):
- **Donor Benchmark**: `google/spec-kit`
- **Reference Spec**: `[spec_kit.md](docs/tech/sota_assimilation/spec_kit.md)`
- **Objective**: Cleanroom extraction of architectural diamonds into `core` adhering to Senior Dev Solution Ladder (DEC-057).

### 2. Permitted Files Whitelist (Target Whitelist):
- `core/**`
- `core/kernel_mcp.py`
- `tests/core/**`
- `docs/architecture/DECISION_REGISTRY_ADHD.md`

### 2.1. Negative Scope & Anti-Scope:
- Заборонено змінювати файли поза межами Target Whitelist.
- Заборонено інсталювати сторонні важкі залежності.
- Заборонено змінювати інваріанти вузької талії ядра (< 400 LOC).

### 3. Substrate & Rules (S):
- Python 3.12+ / Pydantic v2.
- Relative paths only (`./`, `../`).
- Narrow waist microkernel invariant preservation.

### 4. Deterministic Verification Oracle (O):
```bash
uv run pytest tests/core -v
bash scripts/verify_all.sh
```
> 🚨 EXIT CODE MUST BE `0`. TESTS MUST PASS.

### 5. Deliverable Format (D):
- Production-grade service implementation in `core`.
- FastMCP tool registration in `core/kernel_mcp.py`.
- 100% green tests in canonical quality gate.
