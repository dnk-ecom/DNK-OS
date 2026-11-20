---
title: "DNK Canvas Agent (FastMCP Subagent for JSON Canvas v1.0)"
status: "Active"
version: "1.0.0"
domain: "core"
name: "dnk_canvas_agent"
description: "Use when creating, reading, updating, or connecting task nodes in JSON Canvas (.canvas) files via FastMCP."
category: "software-development"
author: "DNK-e.com Maksym & Gerych Prime"
---
> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/skills/dnk_canvas_agent/SKILL.md"
> purpose: "FastMCP subagent skill for JSON Canvas v1.0 task graph creation, mutation, and status synchronization."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-10-27"
> author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# 🎨 DNK Canvas Agent (`dnk_canvas_agent`)

The `dnk_canvas_agent` is a lightweight, headless FastMCP subagent that programmatically creates, reads, mutates, and synchronizes JSON Canvas v1.0 (`.canvas`) files across the DNK OS ecosystem.

---

## 🏛️ Architecture & Standards

- **Specification**: Complies strictly with [JSON Canvas v1.0](https://jsoncanvas.org).
- **Core Workhorse**: Pure Python 3.13 stdlib + Pydantic v2 + FastMCP.
- **Dispatch Integration**: Direct registration via `FastMCPDispatcher.register_fastmcp_server("dnk_canvas", server)`.
- **Zero-Waste Protocol**: Relative paths only (`./`, `../`), deterministic verification.

### 🎨 Color Palette Mapping
Obsidian JSON Canvas node colors:
- `"1"` (Red) — `Blocked`, `Failed`, `Error`
- `"3"` (Yellow) — `In_Progress`, `Running`
- `"4"` (Green) — `Completed`, `Done`, `Success`
- `"5"` (Cyan) — `Planned`, `Todo`
- `"6"` (Purple) — Canvas Titles, Headers, Group Annotations

---

## 🛠️ FastMCP Tool Interface

All tools can be invoked via `FastMCPDispatcher.execute_tool("dnk_canvas", tool_name, arguments)`:

| Tool Name | Arguments | Returns | Description |
| :--- | :--- | :--- | :--- |
| `create_canvas` | `file_path: str`, `title: Optional[str]` | `dict` | Initializes a `.canvas` document with optional title banner. |
| `add_task_node` | `file_path: str`, `node_id: str`, `text: str`, `status: str`, `x: int`, `y: int` | `dict` | Adds or updates a task node with status badge and color. |
| `connect_nodes` | `file_path: str`, `from_node: str`, `to_node: str`, `label: Optional[str]` | `dict` | Creates a directed edge between two existing nodes. |
| `set_node_status`| `file_path: str`, `node_id: str`, `status: str` | `dict` | Updates the status and auto-updates the color mapping. |
| `read_canvas` | `file_path: str` | `dict` | Reads all nodes and edges from target canvas. |

---

## 🚀 Usage Patterns

### Python Direct Usage
```python
from core.canvas.canvas_agent import CanvasAgent

agent = CanvasAgent()
agent.create_canvas("docs/canvas/pipeline.canvas", title="Swarm Pipeline")
agent.add_task_node("docs/canvas/pipeline.canvas", "node-1", "Build Engine", status="Completed", x=0, y=0)
agent.add_task_node("docs/canvas/pipeline.canvas", "node-2", "Run Tests", status="Planned", x=300, y=0)
agent.connect_nodes("docs/canvas/pipeline.canvas", "node-1", "node-2", label="triggers")
```

### FastMCP Dispatcher Integration
```python
from core.canvas.canvas_agent import get_fastmcp_server
from core.framework.fastmcp_dispatcher import FastMCPDispatcher

dispatcher = FastMCPDispatcher()
dispatcher.register_fastmcp_server("dnk_canvas", get_fastmcp_server())

await dispatcher.execute_tool(
    "dnk_canvas",
    "set_node_status",
    {"file_path": "docs/canvas/pipeline.canvas", "node_id": "node-2", "status": "In_Progress"},
)
```

---

## 🛡️ Pitfalls & Invariants

1. **Missing Node Edge Validation**: Always ensure both `from_node` and `to_node` exist before creating an edge. `connect_nodes` raises `ValueError` if either node is missing.
2. **Path Hygiene**: Always supply relative file paths.
3. **Line Count**: Keep this skill file under 750 lines (Skill Core-Size Ratchet).
