<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/antigravity_operations/references/rules_and_workflows.md"
# purpose: "Comprehensive reference on Google Antigravity Rules & Workflows hierarchy, triggers, and budgets."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-23"
# author: "Antigravity & Gerych Prime"
# --- END DNK-MRH-HEADER ---
-->

# Google Antigravity Rules & Workflows Reference

This reference covers the complete specification and best practices for creating, scoping, and managing **Rules** in Google Antigravity across the App, IDE, and CLI.

---

## 1. Hierarchy & Discovery Locations

Antigravity discovers rules by traversing the directory hierarchy from the current working directory (CWD) up to the repository root, merging them with global rules:

```text
Discovery Precedence (Highest to Lowest):
1. Directory-Specific Rules: Nearest AGENTS.md / GEMINI.md in subdirectory
2. Workspace Rules: <workspace-root>/.agents/rules/*.md, <workspace-root>/AGENTS.md
3. Inherited Configurations: Declared in <workspace-root>/.agents/rules.json
4. Global Discovery: ~/.gemini/config/rules/*.md, ~/.gemini/AGENTS.md
5. Built-in Agent System Rules
```

### File Locations by Surface

- **Workspace Project**: `<workspace-root>/.agents/rules/*.md`, `<workspace-root>/AGENTS.md`, or `GEMINI.md`.
- **Global User**: `~/.gemini/config/rules/*.md`, `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`.
- **CLI Global**: `~/.gemini/antigravity-cli/rules/*.md`.

---

## 2. YAML Frontmatter Specification

Standalone `AGENTS.md` and `GEMINI.md` files apply unconditionally to their directory tree without frontmatter. Rules placed inside `.agents/rules/*.md` or `~/.gemini/config/rules/*.md` MUST define valid YAML frontmatter.

```yaml
---
trigger: model_decision       # Required: model_decision | always_on | glob | manual
description: "..."            # Required for model_decision; recommended for all rules
globs: "*.ts, *.tsx"          # Required for glob (singular `glob:` also accepted)
---
```

### Frontmatter Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `trigger` | `string` | **Yes** | Controls activation mechanism (`model_decision`, `always_on`, `glob`, `manual`). Case-sensitive: do NOT use camelCase `alwaysOn` or `modelDecision`. |
| `description` | `string` | **Required** for `model_decision` | Concise description injected into the agent prompt index for semantic activation, or used as fallback pointer if token limits are exceeded. |
| `globs` (or `glob`) | `string` | **Required** for `glob` | Comma-separated glob patterns (e.g., `"*.py, tests/**/*.py"`). Must be quoted if starting with `*`. |

---

## 3. Activation Modes

### A. `model_decision` (Progressive Disclosure)

Best for detailed domain guides, architectural patterns, and testing protocols.

- **Upfront Overhead**: Only rule file path and `description` are injected into context index (~30 tokens).
- **Activation**: Agent fetches full rule body on-demand when the user prompt or current task matches the description.

### B. `always_on` (Unconditional Scope)

Best for core invariants, coding formatting standards, and safety boundaries.

- **Upfront Overhead**: Injected in full into every conversation turn.
- **Guideline**: Keep concise. Prefer root `AGENTS.md` for team-wide invariants.

### C. `glob` (File Pattern Scoped)

Activates automatically whenever the agent reads, edits, or inspects files matching the specified globs.

```yaml
---
trigger: glob
globs: "*.liquid, snippets/**/*.liquid"
description: "Liquid AST, Shopify Sections, and schema sanitization invariants."
---
```

### D. `manual` (Explicit Mention)

Antigravity never injects these rules automatically. The rule activates only when explicitly `@mentioned` in chat (e.g., `@release_checklist.md`). Ideal for release checklists, security audits, and destructive operation protocols.

---

## 4. File Include Syntaxes (`@` Directives)

Rules support two `@` syntaxes for referencing external files:

1. **`@[label](path)` (Direct Inline Splice)**:
   - Inlines target file contents directly into the rule before prompt evaluation and size checks.
   - Resolves relative to the rule file.
   - Automatically strips YAML frontmatter from the target file before splicing.

   ```markdown
   Follow our shared API standards:
   @[API Standards](../docs/api-standards.md)
   ```

2. **`@filename` (Canonical Path Rewrite)**:
   - Does NOT inline contents.
   - Rewrites to a canonical workspace path (`@/workspace/path`) giving the agent an unambiguous file pointer.

---

## 5. Token Budgets & Size Limits

To prevent rules from consuming excessive context:

1. **24 KB (24,000 bytes) Per-File Ceiling**: Any single rule file exceeding 24 KB (after expanding includes) is truncated by Antigravity.
2. **20,000-Token Aggregate Rules Budget**: All active `always_on` and global rules share a 20k token pool. If exceeded, Antigravity automatically demotes the largest rules to lightweight pointers (`- <path>: <description>`) for on-demand retrieval.

---

## 6. Sharing Rules Across Projects (`rules.json`)

To share rules or inherit from monorepo packages, place `.agents/rules.json` in your workspace root:

```json
{
  "inherits": [
    { "path": "../shared-config/.agents/rules.json" }
  ],
  "entries": [
    {
      "path": "../shared-rules",
      "exclude": ["legacy/", "deprecated_rules.md"]
    },
    {
      "path": "rules",
      "include_only": ["backend/*.md"]
    }
  ]
}
```
