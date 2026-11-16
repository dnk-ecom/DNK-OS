# Deterministic Multi-Label Documentation Triage & Migration Protocol

## 1. Overview & Problem Statement
When restructuring or exporting documentation from a monorepo workspace (`DNK_HUB`) to standalone applications (`DNK_OS_APP`), naive approaches fail:
- **LLM-per-file anti-pattern**: Expensive ($2–5/run), slow (3–6 minutes), suffers from taxonomy entropy (drifting tag names), and lacks topological context.
- **1-of-N Choice routers (e.g. Jev)**: Broken for multi-domain documents (e.g. docs that span both Canvas UI and Shopify e-commerce).
- **In-place mutation hazard**: Directly modifying YAML frontmatter during audit introduces dirty diffs and syntax breakage into git history.

---

## 2. Canonical Multi-Label Frontmatter Schema (CONTRACT-021)

Every markdown artifact evaluated for migration adheres to this typed schema:

```yaml
---
title: "Canvas Engine Specification"
status: Active
archetype: "dev_spec"          # dev_spec | api_contract | adr | user_guide | sop_runbook | agent_directive | sota_archive | scratchpad
domains:                       # Multi-label taxonomy
  - "canvas_ui"
  - "backend_fastapi"
utility: "core_ip"             # core_ip | reference | discard
target_app_path: "apps/web/docs/CANVAS_SPEC.md"
migration_action: "migrate"    # migrate | keep_hub_only | archive_vault | delete
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "docs/architecture/CANVAS_ENGINE_SPEC.md"
purpose: "Canvas visual engine spec and OCC sync"
canonical_source: true
status: "Active"
version: "2.0.0"
--- END DNK-MRH-HEADER -->
```

---

## 3. The 3-Tier SOTA Cascading Triage Pipeline

To triage 500+ documents in < 3 seconds with zero hallucinations and $0 token cost:

```
[Repository Markdown Corpus]
       │
       ▼ Level 1: Deterministic Graph Centrality & Git Co-Commit Mining (~75% classified, 0.2s)
       │  • In-Degree Centrality: Count incoming [[wikilinks]] and codebase string references.
       │    Nodes with >= 3 in-links = core_ip. Isolated 0-link stale nodes = discard/archive candidate.
       │  • Git Co-Commit Mining: Check `git log --name-only` for co-edits with active app paths:
       │    Co-committed with apps/web/ -> domains: ["canvas_ui"]
       │    Co-committed with services/dnk_shopify/ -> domains: ["shopify_ecom"]
       │
       ▼ Level 2: Local Quantized Embeddings (FastEmbed / ONNX) (~20% classified, 1.5s)
       │  • Vectorize doc abstract/headings against fixed domain prototype anchors.
       │  • Multi-label assignment via cosine similarity threshold (cos >= 0.65).
       │  • Fully offline, deterministic, zero API token spend.
       │
       ▼ Level 3: Bounded Batched LLM Fallback (~5% orphan tail, < 1.0s)
          • Send digest batches (20 orphan notes per prompt) to Gemini Flash / Haiku.
          • Enforce strict Pydantic JSON schema output.
```

---

## 4. Migration & Safety Invariants

1. **Read-Only Audit Phase**: Source files in `DNK_HUB` remain strictly read-only during triage. All classifications are accumulated in `migration_manifest.json`.
2. **Wikilink Integrity Gate**: Re-mapping `target_app_path` must build a path lookup table (`old_path -> new_path`) and verify/rewrite `[[wikilinks]]` or populate `aliases:` in the destination vault to prevent dead links.
3. **Automated Schema Gate**: Manifests and target headers must pass `scripts/system/markdown_schema_gate.py` with 100% compliance before physical file copying.
