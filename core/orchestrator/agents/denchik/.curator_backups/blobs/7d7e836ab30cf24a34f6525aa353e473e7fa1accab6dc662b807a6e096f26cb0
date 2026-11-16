# MRH Header Hygiene & Dual-Reader Architecture in Obsidian Vault Notes

## 1. Problem Statement & The Ghost H1 Outline Trap

In Python scripts (`.py`) and shell scripts (`.sh`), Machine-Readable Headers (MRH) use hash comments:
```python
# --- DNK-MRH-HEADER ---
# mrh_id: "core/example.py"
# ...
# --- END DNK-MRH-HEADER ---
```

However, in Markdown (`.md`) files rendered inside Obsidian:
- Any line starting with `# ` is parsed as a **Top-Level H1 Markdown Heading**.
- A raw `# --- DNK-MRH-HEADER ---` block causes Obsidian to inject a giant ghost heading into the document's **Table of Contents (TOC) / Outline Panel**.
- This breaks note navigation, distorts heading hierarchies, and clutters the visual canvas.
- Additionally, if raw `# --- DNK-MRH-HEADER ---` precedes the YAML frontmatter (`---`), CommonMark parsers fail to recognize the frontmatter as YAML metadata, treating it as unparsed body prose.

---

## 2. Canonical Dual-Reader Standard for Obsidian Markdown Notes

Every note and specification in `docs/notes/`, `specs/`, or `00_MOC_*.md` must adhere to the **ADR-003 Dual-Reader Principle**:

### 1. Frontmatter Starts at Line 1
Line 1 MUST be the opening YAML delimiter `---`. No comments, spaces, or headers may precede it:
```yaml
---
title: "DNK OS Master Map of Content (MOC)"
date: 2026-09-18
tags:
  - dnk-os
  - moc
  - architecture
  - obsidian-hub
status: "Active"
mrh_id: "00_MOC_DNK_OS.md"
purpose: "Master Map of Content (MOC) and Obsidian Knowledge Index for DNK OS Standalone App."
---
```

### 2. Full Machine-Readable MRH Block as a Collapsible Callout
Directly below the closing `---` of frontmatter, place the full 9-field MRH header wrapped inside a collapsed Obsidian callout (`> [!metadata]- ⚙️ Системні метадані...`):

```markdown
> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "00_MOC_DNK_OS.md"
> purpose: "Master Map of Content (MOC) and Obsidian Knowledge Index for DNK OS Standalone App."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-09-19"
> author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```
> > [!summary] 📋 Контекст для ШІ-агента
> > Стислий виклад інженерної ролі документа та шлюзів перевірки.
```

**Key Benefits of the Collapsible Callout**:
1. **User Focus (Dual-Optics)**: In Obsidian Reading and Live Preview modes, the header collapses into a single sleek row with an icon. It does not clutter the user's reading experience ("не кидається в очі"), but can be expanded with one click whenever needed.
2. **Zero Ghost H1 in Outline**: Because the hash `#` lines are enclosed within a fenced YAML block inside the callout, Obsidian's Markdown parser does NOT treat `# --- DNK-MRH-HEADER ---` as a top-level H1 heading. Document Outline/TOC remains 100% clean.
3. **Dual Agent & CI Parseability**: Automated scripts, AST readers, and LLM prompts can extract the YAML block and context without loss of structure.

*(Note: Legacy HTML comments `<!-- --- DNK-MRH-HEADER --- ... -->` remain supported as a fallback for pure machine-only files).*

### 3. Human Visual Layer: H1 + Abstract Callout + Visual Navigators
Directly below the MRH block:
- H1 with Document Type Icon (`# 🧭 DNK OS Master Map of Content (MOC)`)
- Callout `> [!abstract] **Призначення Документа**` summarizing the core objective.
- Interactive Dataview query or Mermaid navigation diagram for Obsidian visual canvas.

---

## 3. Verification & CI Automation

To verify that no notes in `docs/notes/` contain unescaped `# --- DNK-MRH-HEADER ---`:
```bash
grep -rn "^# --- DNK-MRH-HEADER ---" docs/notes/ specs/
```
If any matches are returned, wrap them into `<!-- --- DNK-MRH-HEADER --- ... -->` to ensure 100% Outline hygiene and zero ghost headings.
