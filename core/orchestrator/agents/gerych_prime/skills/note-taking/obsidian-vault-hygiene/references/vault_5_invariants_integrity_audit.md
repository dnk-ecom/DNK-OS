<!-- --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/note-taking/obsidian-vault-hygiene/references/vault_5_invariants_integrity_audit.md"
# purpose: "Reference guide for the 5-Invariant Vault Integrity and Linkage Audit."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-17"
# author: "Antigravity & Gerych Prime"
# --- END DNK-MRH-HEADER -->

# 5-Invariant Obsidian Vault Integrity & Linkage Audit

When auditing or standardizing an Obsidian markdown vault (especially after migrations, refactoring, or restructuring), verify against the 5 canonical invariants:

---

## The 5 Vault Invariants

### 1. Invariant 1: Zero Broken Wikilinks Gate
- All `[[target]]`, `[[target|alias]]`, `[[target#heading]]`, and `![[embedded]]` links must resolve.
- **Resolution Order**:
  1. Direct file path relative to current note's directory.
  2. Direct file path relative to vault root (`docs/notes/`).
  3. Basename lookup across all `.md`, `.canvas`, and `.excalidraw.md` files in the vault.
  4. Repository root fallback for code references (e.g. `[[apps/...]]`, `[[core/...]]`, `[[scripts/...]]`).
- **Code Block Sanitization**: Strip out fenced code blocks (` ```...``` `) and inline code spans (` `...` `) before scanning so sample syntax is not treated as active links.
- **Code References**: Prefer wrapping code file paths in backticks (`` `apps/api/routers/example.py` ``) rather than wikilinks unless intentionally linking across the workspace graph.
- **Service Consolidation Traps**: When consolidating services (e.g. migrating `dnk_store_studio` into `dnk_shopify`), always sweep `docs/notes/` for old service paths in code wikilinks and update them to prevent broken link failures.

### 2. Invariant 2: Zero Active Orphans Gate
- Every active specification file in domain modules (`MY TASKS/` subfolders: `ADR/`, `CONTRACTS/`, `SOTA/`, `TASKS/`) must be linked in its module's `00. INDEX.md`.
- Active specifications must be registered as nodes in `core/obsidian/vault_to_taskforest.py` or indexed in the Task Forest.
- Cold archive notes (`docs/notes/ARCHIVE/`) are exempt from active graph linking.

### 3. Invariant 3: Clean Root Invariant
- The vault root directory (`docs/notes/`) must contain only canonical subdirectories (`.obsidian/`, `MY TASKS/`, `ARCHIVE/`, `tasks_and_ideas/`, `Canvas/`, etc.) and strictly ONE sanctioned master index entry note: `000_DNK_HUB_NOTES_INDEX.md`.
- Stray `.md` files or temporary audit/task files in the vault root break Invariant 3 and the `test_no_root_markdown_files` hygiene gate. Ad-hoc notes must be filed into the appropriate module or archived in `ARCHIVE/`.

### 4. Invariant 4: 100% Migration Reconciliation Gate
- Master migration registries (e.g. `РЕЄСТР_МІГРАЦІЇ.md`) must account for every single file in the vault.
- Every file must have an explicit status: Active (`🟢`), Frozen Cold Storage (`❄️`), or Migrated.
- No dangling or undetermined states (`🟡`) are permitted.

### 5. Invariant 5: Single Vault SSOT
- The vault configuration (`.obsidian/app.json`, `.obsidian/community-plugins.json`, etc.) must be valid and synchronized with the workspace.
- The vault serves as the Single Source of Truth for human-agent cognitive alignment.

---

## Automated Verification Recipe

Run the integrity scanner:
```bash
PYTHONPATH=. .venv/bin/python3 scripts/system/audit_notes_vault_integrity.py --json docs/audit/VAULT_INTEGRITY_AUDIT.json -v
```
