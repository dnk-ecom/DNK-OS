# JSON Canvas 1.0 Specification, Layout Patterns & Vault Security (SSOT)

Canonical reference for `core/obsidian/json_canvas_builder.py` and JSON Canvas 1.0 (`jsoncanvas.org` / Kepano v1.0).

---

## 1. Specification (jsoncanvas.org v1.0)

Obsidian JSON Canvas files (`.canvas`) are pure JSON documents with two top-level lists: `nodes` and `edges`.

### Node Types

1. **`text`**:
   - `id`: unique string (16-hex characters `[0-9a-f]{16}`)
   - `type`: `"text"`
   - `text`: Markdown content string
   - `x`, `y`, `width`, `height`: integers
   - `color`: string `"1"` through `"6"` or `#RRGGBB` hex string

2. **`file`**:
   - `id`: unique string
   - `type`: `"file"`
   - `file`: relative path in Obsidian vault (e.g. `docs/notes/Arch.md`)
   - `subpath`: optional heading or block anchor (e.g. `#Components` or `^blockId`)

3. **`link`**:
   - `id`: unique string
   - `type`: `"link"`
   - `url`: target web URL string

4. **`group`**:
   - `id`: unique string
   - `type`: `"group"`
   - `label`: optional title string displayed in header
   - `background`: optional image path or hex color
   - `backgroundStyle`: `"cover"` | `"ratio"` | `"repeat"`

### Obsidian Color Map (Strings `"1"` to `"6"`)
- `"1"`: Red (Failed, Blocked, Error, Auditor)
- `"2"`: Orange (In Progress, Review, Builder)
- `"3"`: Yellow (Pending, Backlog, Video)
- `"4"`: Green (Completed, Verified, Shopify)
- `"5"`: Blue (Orchestrator, Prime, Fullstack)
- `"6"`: Purple (Architecture, System Boundaries, Meta, Librarian)

*Pitfall*: Canvas colors 1-6 MUST be string literals (`"1"`), not raw integers (`1`), to ensure compatibility with Obsidian Desktop and strict schema parsers.

### Edges
- `id`: unique string
- `fromNode`: string ID of source node
- `fromSide`: `"top"` | `"right"` | `"bottom"` | `"left"`
- `toNode`: string ID of target node
- `toSide`: `"top"` | `"right"` | `"bottom"` | `"left"`
- `fromEnd`: `"none"` | `"arrow"` (default `"none"`)
- `toEnd`: `"none"` | `"arrow"` (default `"arrow"`)
- `label`: optional label text

---

## 2. Layout Algorithms

1. **DAG / Topological Layout (`layout_dag`)**:
   - Groups nodes into layers based on longest-path ranking from root nodes.
   - For `LR` (left-to-right): `x = layer_idx * (col_width + h_spacing)`, `y = row_idx * (row_height + v_spacing)`.
   - Connects edges horizontally with `fromSide="right"`, `toSide="left"`.
   - For `TB` (top-to-bottom): `fromSide="bottom"`, `toSide="top"`.

2. **Pipeline Layout (`layout_pipeline`)**:
   - Sequential stages as columns, with tasks within each stage stacked vertically.
   - Automatically computes a group container around each stage using `compute_group_bounds`.

3. **Group Bounding Box (`compute_group_bounds`)**:
   - Calculates `min_x`, `min_y`, `max_x`, `max_y` across all member nodes.
   - Adds padding (e.g. 50-60px) and accounts for group label height at top.

4. **PKM Mindmap Layout (`layout_mindmap`)**:
   - Root central node at (0, 0).
   - Divides primary branches evenly across Left and Right hemispheres.
   - Left branches position at `root.x - width - spacing` with `fromSide="left"`, `toSide="right"`.
   - Right branches position at `root.x + root.width + spacing` with `fromSide="right"`, `toSide="left"`.

---

## 3. Vault Path Security & Traversal Protection

When exporting canvas documents to the Obsidian vault via `export_canvas_to_vault()`:
- Always enforce `enforce_vault_root=True` by default.
- Resolve target path: `dest_path = (canonical_root / target_path).resolve()`.
- Check `dest_path.relative_to(canonical_root.resolve())` to prevent path traversal attacks (e.g. `../../../etc/passwd.canvas`).
- Raise `ValueError("Path traversal detected")` if outside the vault root.
