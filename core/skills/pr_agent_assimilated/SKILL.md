---
name: pr_agent_assimilated
description: "Assimilated SOTA patterns and architecture from The-PR-Agent/pr-agent."
version: "1.1.0"
category: "research"
assimilated_at: "2026-09-10"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "gerych_auditor"
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/pr_agent_assimilated/SKILL.md"
purpose: "Assimilated PR-Agent Architecture, Patch Processing, Comment Dedup, and Review State Machine"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.1.0"
updated_at: "2026-09-10"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🌐 PR-AGENT Assimilation Index & Recipes

Meta-index and practical implementation patterns assimilated from **[The-PR-Agent/pr-agent](https://github.com/The-PR-Agent/pr-agent)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `The-PR-Agent/pr-agent`
- **License**: `MIT` (Commercial safe)
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_auditor` / `gerych_researcher`
- **Obsidian Reference**: `docs/notes/143_pr_agent_sota_assimilation_audit.md`

## 📁 Key Assimilated Architectural Patterns
1. **Hunk-Only Diff Extraction**: Очищення сирого git diff від заголовків файлів з збереженням контексту рядків.
2. **Dynamic Token Budgeting**: Розбиття дифу на фрагменти за важливістю (код -> конфіги -> тести -> документація).
3. **Inline Comment Fingerprinting & State Machine**: Хешування зауважень рев'ю для уникнення дублювання при повторних комітах та автоматичного закриття виправлених зауважень.
4. **1-Click GitHub Suggestions**: Форматування пропозицій виправлення безпосередньо у форматі GitHub markdown suggestions.

## 🧪 Quick Recipes

### Recipe 1: Hunk-Only Patch Processing (Zero Bloat)
```python
import re

RE_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[ ]?(.*)")

def to_hunk_only_patch(patch_str: str) -> str:
    """Drop unified-diff file metadata before the first hunk."""
    lines = patch_str.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("@@"):
            return "".join(lines[i:])
    return ""
```

### Recipe 2: Review Finding Fingerprint & Reconciliation
```python
import hashlib

def generate_finding_fingerprint(file_path: str, line_no: int, issue_type: str) -> str:
    raw = f"{file_path}:{line_no}:{issue_type}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]

def reconcile_findings(previous_findings: set, current_findings: set) -> dict:
    resolved = previous_findings - current_findings
    persistent = previous_findings & current_findings
    new_issues = current_findings - previous_findings
    return {
        "resolved": list(resolved),
        "persistent": list(persistent),
        "new": list(new_issues)
    }
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Завжди використовувати відносні шляхи (`./`, `../`).
2. **[MRH_HEADER_INVARIANT]**: Будь-які адаптери повинні містити валідний заголовок DNK-MRH.
3. **[TOKEN_BUDGET]**: Великі diff'и обов'язково розбивати на зважені чанки з пріоритетом коду.
