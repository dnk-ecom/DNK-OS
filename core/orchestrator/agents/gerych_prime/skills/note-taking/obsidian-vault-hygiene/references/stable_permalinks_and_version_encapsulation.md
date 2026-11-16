# Stable Functional Permalinks & Internalized Versioning (Preserving [[Wikilinks]])

## 1. Problem Statement: The Version-in-Filename Anti-Pattern

When developers or agents include versions or dates in markdown file names:
❌ `Order Processing Pipeline v2.1.md`
❌ `Architecture_Spec_2026_09_Final.md`

Every subsequent update forces a file rename (`v2.1` -> `v2.2`). This triggers a systemic cascading failure:
1. **Broken [[Wikilinks]]**: All inbound wikilinks (`[[Order Processing Pipeline v2.1]]`) across 20+ vault notes become instant dead links.
2. **Knowledge Graph Fracture**: Obsidian Graph View, MOCs, and Task Forest DAG dependencies lose their relational edges.
3. **SCONES Index De-synchronization**: Cognitive embeddings and retrieval vectors point to non-existent historical files.
4. **Git Tree Churn**: Git treats renames as deletes + creates if diff heuristics fail, breaking `git blame` and history tracing.
5. **Context Window Bloat**: AI agents waste round trips and token budget searching for "which version is the latest one".

---

## 2. Canonical Rule: Stable Functional Entity Naming

**Golden Rule**: *A file name is an immutable functional permalink. It represents WHAT the entity is, never what iteration it is currently on.*

### Comparison Matrix

| Aspect | ❌ Anti-Pattern (Version in Name) | ✅ Golden Standard (Stable Permalink) |
| :--- | :--- | :--- |
| **File Name** | `014 Shopify AST Transpiler v2.md` | `014 Shopify AST Transpiler.md` |
| **Inbound Links** | `[[014 Shopify AST Transpiler v2]]` (Breaks on v3) | `[[014 Shopify AST Transpiler]]` (Never breaks) |
| **Where Version Lives** | In the file path / title | Inside YAML frontmatter + MRH header |
| **Where Iterations Live** | Scattered across duplicate `.md` files | In Git history and internal `# Changelog` |
| **Agent Discovery** | High ambiguity, searches directory for "latest" | Deterministic exact path resolution |

---

## 3. Internalized Versioning Protocol

All versioning must be encapsulated strictly **INSIDE** the document metadata:

### 1. YAML Frontmatter (Line 1)
```yaml
---
title: "DNK OS Architecture & Documentation Standard"
aliases:
  - "DNK-DOC-STANDARD"
  - "Doc Standard"
version: "2.3.0"
updated: 2026-09-19
status: active
---
```

### 2. Collapsed MRH Header Callout
```markdown
> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/specs/014_shopify_ast_transpiler.md"
> purpose: "Shopify OS 2.0 AST mutations & Canvas-to-Liquid transpiler."
> canonical_source: true
> alters_files: ["services/dnk_shopify/"]
> triggers_tasks: ["TASK-SHOPIFY-AST-001"]
> status: "Active"
> version: "2.3.0"
> updated_at: "2026-09-19"
> author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```
```

### 3. Visual Badge Bar (For Human Readers)
```html
<div align="center">
  <span>Статус: Active</span>
  <span>Версія: 2.3.0</span>
  <span>Оновлено: 2026-09-19</span>
</div>
```

---

## 5. Active Draft.md RFC Protocol & Approved Status Progression

When collaborating between Founder (Maxim) and AI Agents via Obsidian drafts:

1. **Working Draft Phase (`status: draft`)**:
   - New proposals, specifications, and architecture ideas start in a stable draft file (e.g., `Do not Delete - Draft.md`).
   - The file acts as an interactive scratchpad for human review, Obsidian Canvas visual mapping, and refinement.
   - Permalink remains unchanged (`Draft.md`) while `version: "1.0.0"` and `status: draft` reflect in-progress status.

2. **Collapsed Metadata & Clean Outline**:
   - MRH headers are enclosed inside collapsed callouts (`> [!metadata]- ⚙️ ...`) to eliminate "Ghost H1" headings in the Obsidian Outline view.

3. **Approval & Promotion (`status: approved`)**:
   - Once reviewed and approved by the Founder, status updates to `status: approved` and version bumps to `v2.0.0`.
   - The approved draft serves as the canonical spec (SSOT) from which sub-specs and `task_forest` DAG trees are derived.

---

## 4. The 3-Audience Dual-Optics Alignment

1. **For Developers & Git**:
   - Deterministic paths for CI test suites, scripts, and pre-commit hooks.
   - Clean linear git diffs without artificial file churn.
2. **For AI Agents (Swarm & SCONES)**:
   - Instant resolution via `search_files` or `dnk_resolve_symbol` without crawling directory listings.
   - Aliases in YAML allow resolving legacy or informal mentions to the canonical file.
3. **For Humans (Founder / Obsidian / ADHD UX)**:
   - Clean, uncluttered file tree in the Obsidian file explorer.
   - High-contrast visual badges at the top of the note immediately communicate the active version.
   - Zero anxiety about creating dead links when writing `[[...]]`.
