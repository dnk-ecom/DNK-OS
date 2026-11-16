# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/screenplay_editor_and_file_ipc_patterns.md"
# purpose: "Architecture patterns from unclebob/scriptwriter: file-based token IPC, zero-DB JSON document model, and deterministic pagination projections."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🎬 Screenplay Editor, Zero-DB Document Model & Agent File IPC Patterns

Reference patterns distilled from the audit and assimilation of `unclebob/scriptwriter` (Robert C. Martin).

---

## 1. Zero-DB Folder/JSON Document Model

Instead of an embedded SQLite database or opaque binary files, the screenplay document is a simple folder holding `script.json`.

```
my-screenplay/
├── script.json         # Single Source of Truth (SSOT)
└── .scriptwriter/
    └── refresh         # Ephemeral IPC coordination token
```

### JSON Schema Structure
The document model maps screenplay semantics directly into typed elements:
```json
{
  "title": "Project Title",
  "author": "Author Name",
  "elements": [
    { "type": "scene", "text": "INT. COFFEE SHOP - DAY" },
    { "type": "action", "text": "ALICE sits by the window, typing rapidly." },
    { "type": "character", "text": "ALICE" },
    { "type": "dialogue", "text": "The architecture is clean." },
    { "type": "transition", "text": "FADE OUT." }
  ]
}
```

### Advantages for Autonomous Agents:
- **Zero Binary Bloat**: LLMs and domain workers (`dnk_video_ai_creator`, `gerych_builder`) can read, validate, and mutate the document via standard JSON tools.
- **Git Friendly**: Line-oriented diffs and merge conflict resolution work natively.
- **Inspectability**: No proprietary schema deserializer or migration pipeline required.

---

## 2. File-System Token IPC (Agent-to-Desktop Synchronization)

To allow external agents (LLMs, Grok, cron jobs, video synthesis workers) to update the screenplay without crashing or locking the active Tauri desktop UI:

1. **External Agent Mutation**: Agent edits `script.json` directly on disk (or writes an atomic update via temp file rename).
2. **Signal Token Generation**: Agent writes a timestamp/nonce to `.scriptwriter/refresh`:
   ```bash
   echo "$(date +%s)" > my-screenplay/.scriptwriter/refresh
   ```
3. **Desktop File Watcher / Poller**:
   - Tauri/Rust backend or frontend poller observes `.scriptwriter/refresh`.
   - On change, it re-reads `script.json` and updates the active CodeMirror 6 editor buffer without desynchronizing cursor state or overwriting uncommitted user keystrokes.

---

## 3. Pure Projection Pipeline (Domain vs Presentation)

The codebase exemplifies Clean Architecture by isolating formatting rules into pure projections:

```
[ Domain Model: elements[] ]
            │
            ▼
[ Pagination Projection (54 lines/page, Courier 12pt, US Letter) ]
            │
            ├──► CodeMirror 6 Visual Viewport (DOM)
            ├──► Vector PDF Export (pdf-lib + fontkit)
            ├──► Production Schedule CSV (Scene / Character Breakdown)
            └──► Mobile Pocket PDF (390pt viewport for on-set smartphones)
```

- **Dynamic `(MORE)` and `(CONT'D)` Calculation**: Handled as pure mathematical projections during pagination rather than hardcoded text mutations in the domain model.
- **Shooting Schedule Breakdown**: Extracts distinct scenes, day/night states, locations, and cast lists automatically from the document elements.
