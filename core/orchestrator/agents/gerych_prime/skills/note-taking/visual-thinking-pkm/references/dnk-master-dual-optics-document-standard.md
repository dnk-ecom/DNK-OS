# --- DNK-MRH-HEADER ---
# mrh_id: "skills/note-taking/visual-thinking-pkm/references/dnk-master-dual-optics-document-standard.md"
# purpose: "Canonical specification for DNK OS Master Documentation & Architecture Template (Dual-Optics Human ↔ Agent)."
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# DNK OS Master Documentation & Architecture Standard (Dual-Optics)

The DNK OS documentation standard bridges human-friendly cognitive ergonomics with deterministic machine-actionable structure.

## 1. Dual-Optics Philosophy

| Dimension | Human Reader (Maxim) | AI Agent Swarm (Gerych Prime) |
| :--- | :--- | :--- |
| **Primary Visual Hook** | Abstract Hero Callout, Pill Badges, Breadcrumbs | Complete YAML Frontmatter + DNK-MRH-HEADER |
| **System Invariants & MRH Header** | Sleek collapsed 1-line callout (`> [!metadata]- ⚙️ ...`), expandable on click | Unaltered YAML code block `# --- DNK-MRH-HEADER ---` without Outline ghost H1 |
| **Spatial Overview** | Interactive Excalidraw Canvas Embed (`![[canvas.excalidraw]]`) | Symmetrical Mermaid Flowchart (CLI / Headless parsing) |
| **Checklist Ergonomics** | 11 Obsidian Status Bullet States (`[ ]`, `[/]`, `[x]`, `[!]`, `[?]`, etc.) | Machine Task Contract `(TASK-ID) [P0] @agent | Scope | Criteria` |
| **Context Delivery** | Semantically colored Obsidian Callouts (`[!note]`, `[!tip]`, `[!warning]`) | Agent-targeted Callouts (`[!agent]`, `[!context]`, `[!invariant]`, `[!dag]`) |
| **Deep Technical Data** | Collapsible `<details><summary>` accordion panels | Raw AST, JSON/YAML schemas, and parser targets |
| **Hidden Machine Directives** | Invisible in Obsidian Reading View | HTML Comments: `<!-- AGENT_DIRECTIVE -->`, `<!-- DAG_NODE -->` |

## 2. Machine Task Contract Syntax for TaskDNA / Beads Task Forest

When human or agent drafts tasks to be converted into automated DAG execution, every bullet must follow this deterministic schema:

```markdown
- [ ] (TASK-<DOMAIN>-<SEQ>) [<PRIORITY>] @agent:<AGENT_ROLE> | Scope: <PATH> | Criteria: <DETERMINISTIC_PASS_CRITERIA>
```

### Fields:
- `(TASK-<DOMAIN>-<SEQ>)`: Unique identifier (e.g. `(TASK-DNK-CORE-001)`).
- `[<PRIORITY>]`: `[P0]` (Blocker/Critical), `[P1]` (Feature/High), `[P2]` (Improvement/Normal).
- `@agent:<AGENT_ROLE>`: Target worker (`gerych_builder`, `dnk_dev_fullstack`, `gerych_auditor`, `dnk_shopify`, `dnk_video_ai_creator`).
- `Scope: <PATH>`: Explicit relative file path whitelist or directory boundaries.
- `Criteria: <CRITERIA>`: Machine verifiable gate (e.g. `pytest tests/test_core.py exit 0`, `tsc --noEmit`).

## 3. Obsidian Checklist Status Matrix (11 States)

```markdown
- [ ] Todo / Unassigned
- [/] In Progress
- [x] Completed & Verified
- [-] Cancelled / Out of Scope
- [!] Urgent / Blocker
- [?] Question / Research Spike
- [>] Delegated to Subagent / Swarm
- [*] Milestone / Gate Check
- [i] Informational Context
- [b] Bookmark / Resource
- [k] Key Invariant / Non-negotiable Rule
```

## 4. Invisible Machine Comment Protocols

Agents can embed metadata without disturbing human visual flow:
```markdown
<!-- AGENT_DIRECTIVE: action="autonomous_slicing" max_turns=20 -->
<!-- DAG_NODE: id="node-01" agent="dnk_dev_fullstack" depends_on=[] status="pending" -->
<!-- SCONES_INGEST: topic="canvas_architecture" importance=0.95 -->
```

## 5. Canonical File Pairings in DNK_OS_APP

- **`Do not Delete - Example.md`** & **`Do not Delete - Example.excalidraw.md`**: Master Approved Benchmark Template for all system notes.
- **`Do not Delete - Draft.md`** & **`Do not Delete - Draft.excalidraw.md`**: Active Human Scratchpad for drafting before DAG compilation.

## 6. Collapsible MRH Metadata Callout Standard

To avoid cluttering the human reader's view ("не кидатися в очі") while providing full context for agents and preventing Ghost H1 in Obsidian's outline:

```markdown
> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/path/example.md"
> purpose: "Канонічний опис компонента."
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
> > Стислий виклад інженерної ролі документа та критеріїв перевірки.
```

- **Collapsible (`[!metadata]-`)**: Renders as a 1-line collapsed accordion by default.
- **Fenced YAML block (` ```yaml `)**: Shields the `# --- DNK-MRH-HEADER ---` from Markdown outline parsers, ensuring zero outline pollution.
- **Expandable on Click**: Gives the user immediate access to metadata without needing raw source editing.
