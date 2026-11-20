---
name: codespring_assimilated
description: "Assimilated SOTA patterns, 4 Core Values, and visual planning lifecycle from CodeSpring."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-10"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "gerych_builder"
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/codespring_assimilated/SKILL.md"
purpose: "Assimilated CodeSpring Architecture, 4 Core Values, Mindmap-to-Code Pipeline, and 5-Question Audit Gate"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-10"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🌐 CodeSpring Assimilation Index & Recipes

Meta-index and practical implementation patterns assimilated from **[CodeSpring](https://codespring.app)** (`CodeSpringApp/codespring-skills`).

## 📌 Repository Intel & Legal Boundary
- **Platform**: `https://codespring.app/docs`
- **Repository**: `CodeSpringApp/codespring-skills`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Workers**: `gerych_prime`, `gerych_builder`, `gerych_auditor`
- **Obsidian Reference**: `docs/notes/145_codespring_sota_assimilation_and_four_core_values.md`

## 📁 4 Core Values of CodeSpring
1. **Context-First Architecture ("Tag first, then ask")**:
   - The map is the shared memory between human and AI agent.
   - Queries are scoped to specific nodes rather than scanning the entire repo.
2. **Structural Decomposition & Mockup-Before-PRD**:
   - Node hierarchy: `Project ➔ Feature ➔ Sub-feature ➔ Bridge ➔ Notes & PRDs ➔ Tasks`.
   - Critical invariant: Generate clickable/visual UI mockups *before* writing PRDs to eliminate hallucinated specifications.
3. **Continuous Traceability & Resync Protocol**:
   - Code changes trigger AST drift detection against the map and PRDs (`cs-build-resync-codebase`).
   - Every commit traces back to a task, node, and PRD requirement.
4. **Autonomous Execution with Guardrails**:
   - Scouts scan external repos/trends and convert findings directly into Canvas feature cards.
   - Code changes must pass the 5-Question Codebase Audit before merging.

---

## 🧪 Quick Recipes

### Recipe 1: 5-Question Codebase Audit Gate (`gerych_auditor`)
```python
def verify_5_question_audit(
    does_what_needed: bool,
    zero_fake_data: bool,
    architecture_allows_goals: bool,
    scalable_foundation: bool,
    stable_runtime: bool,
) -> dict:
    """
    CodeSpring 5-Question Codebase Audit Gate:
    1. Does the app do what it actually needs to do?
    2. Is it getting things wrong, or presenting made-up figures as fact?
    3. Does the current architecture allow it to do what it needs to do?
    4. Can we build on it scalably?
    5. Can users use it without it breaking?
    """
    criteria = {
        "does_what_needed": does_what_needed,
        "zero_fake_data": zero_fake_data,
        "architecture_allows_goals": architecture_allows_goals,
        "scalable_foundation": scalable_foundation,
        "stable_runtime": stable_runtime,
    }
    all_passed = all(criteria.values())
    return {
        "passed": all_passed,
        "action": "PROCEED_TO_MERGE" if all_passed else "BLOCK_AND_REFACTOR",
        "failed_criteria": [k for k, v in criteria.items() if not v],
    }
```

### Recipe 2: Context-Tagging Subgraph Builder ("Tag First, Then Ask")
```python
def extract_node_subgraph_context(node_id: str, graph: dict) -> dict:
    """
    Given an active selected node, builds a lightweight bounded context
    without dumping the full graph or repo into the prompt.
    """
    target = graph.get("nodes", {}).get(node_id)
    if not target:
        return {"error": "Node not found"}
    
    # Collect immediate parents and direct children
    parent_ids = [e["source"] for e in graph.get("edges", []) if e["target"] == node_id]
    child_ids = [e["target"] for e in graph.get("edges", []) if e["source"] == node_id]
    
    return {
        "focus_node": {
            "id": target["id"],
            "type": target["type"],
            "label": target.get("label"),
            "data": target.get("data", {}),
        },
        "parents": [graph["nodes"].get(pid, {}).get("label") for pid in parent_ids],
        "children": [graph["nodes"].get(cid, {}).get("label") for cid in child_ids],
        "scope_boundary": "STRICT_LOCAL_SUBGRAPH",
    }
```

### Recipe 3: Mockup-First Validation Pipeline
```python
def validate_mockup_before_prd(has_visual_mockup: bool, user_approved_mockup: bool) -> dict:
    """
    Invariant: PRDs must not be generated until visual representation
    is created and validated.
    """
    if not has_visual_mockup:
        return {
            "status": "BLOCKED",
            "next_step": "DISPATCH_GERYCH_BUILDER_FOR_MOCKUP",
            "message": "Visual mockup required before PRD generation.",
        }
    if not user_approved_mockup:
        return {
            "status": "WAITING_APPROVAL",
            "next_step": "AWAIT_HUMAN_MOCKUP_SIGN_OFF",
            "message": "Human approval required for UI mockup.",
        }
    return {
        "status": "READY_FOR_PRD",
        "next_step": "GENERATE_TRI_PARTITE_PRD",
    }
```
