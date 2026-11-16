---
name: terminal-ui-design
description: "Use when building TUIs, CLI dashboards, and banners."
version: 1.0.0
author: DNK OS Swarm
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tui, cli, rich, terminal, banners, dashboards, layout, ascii]
---

# Terminal UI Design & CLI Dashboard Engineering

A comprehensive guide for building robust, responsive, and visually clean Terminal User Interfaces (TUIs), CLI welcome banners, status dashboards, and console layouts using Python libraries like `rich`, `curses`, or `prompt_toolkit`.

## When to Use

- Designing or modifying CLI startup banners, welcome screens, or interactive dashboards.
- Constructing multi-column layouts in the terminal (side-by-side hero + telemetry).
- Diagnosing and fixing visual corruption in terminal output (broken ASCII art, orphan words, unwanted line wraps, horizontal alignment drift).
- Making CLI output responsive across diverse terminal emulator widths (80, 100, 120+ columns).

## Core Architecture Principles

### 1. Terminal Width Budgeting & Breakpoints

Never assume a widescreen terminal (>120 cols). Standard terminal windows, default tmux panes, and split IDE consoles frequently run at **80 to 90 columns**.

- **Narrow / Mobile Console (< 90 cols)**:
  - Total usable width after outer panel borders and margins is ~74–84 characters.
  - Avoid wide 2-column layouts if the left column alone takes 45–50 characters (leaving <35 characters for the right column).
  - Use a stacked (single-column) layout or a miniature/compact ASCII hero logo.
- **Standard Console (90–110 cols)**:
  - 2-column layout is viable, but right-column line items MUST enforce strict single-line bounds (truncate with `...`).
- **Widescreen (> 110 cols)**:
  - Full 2-column dashboard with expansive metrics, multi-line agent/tool descriptions, and full ASCII headers.

### 2. Column Isolation vs Row-by-Row Zipping

#### ❌ The Fatal Flaw: Row-by-Row `zip_longest`
A common anti-pattern when rendering two columns side-by-side:
```python
# ANTI-PATTERN: Row-by-row zipping into a Rich Table
for left_line, right_line in zip_longest(left_lines, right_lines, fillvalue=""):
    table.add_row(left_line, right_line)
```
**Why this breaks:**
If any line on the right wraps into 2 lines due to terminal width, Rich expands the table row height to 2.
- The left cell in that row receives an artificial blank line underneath or in the middle.
- If the left column contains multi-line ASCII art (where lines must be strictly contiguous), the ASCII art splits open with empty rows inserted between blocks.
- Telemetry headers shift out of sync vertically with their corresponding sections.

#### ✅ The Solution: Column Isolation via `rich.console.Group`
Treat each column as an independent visual entity within a 1-row container:
```python
from rich.console import Group
from rich.table import Table

# Create a 1-row grid with 2 independent columns
layout_table = Table.grid(padding=(0, 2))
layout_table.add_column("left", justify="left", no_wrap=True)
layout_table.add_column("right", justify="left", ratio=1)

# Group entire column contents independently
left_group = Group(*left_renderables)
right_group = Group(*right_renderables)

# A wrap in right_group never affects row heights or line spacing in left_group
layout_table.add_row(left_group, right_group)
```

### 3. Single-Line Invariant for Telemetry Lists

When rendering lists of tools, agents, MCP servers, or status badges:
- Wrap every item in `Text(item, no_wrap=True, overflow="ellipsis")`.
- Keep item descriptions ultra-compact (e.g. `agent — short role` rather than full paragraphs).
- Ensure section headers specify exact counts without word breaks (e.g. `🤖 Swarm Agents (14)` instead of `🤖 Swarm Agents (14 active workers registered in system)`).

### 4. Visible String Width vs ANSI Escape Length

Never compute column widths or padding using Python's `len(string)` on text containing ANSI escape sequences (e.g. `\033[38;2;...m` or Rich markup strings):
- `len("\033[31mHello\033[0m")` is 14, but its terminal display width is 5.
- Using `len()` causes misaligned tables and premature wrapping.
- Use `rich.text.Text.from_markup(text).cell_len` or `wcwidth` to measure actual terminal cell occupancy.

## Supporting References

- See `references/tui-layout-patterns.md` for complete code examples, responsive banner helpers, and Rich Layout configurations.

## Pitfalls & Defensive Rules

1. **Rich Column Auto-Shrink & Truncation of ASCII Art**:
   - Even with `Table.grid` and `no_wrap=True`, if you omit explicit `width=...` on `add_column()`, Rich will dynamically shrink BOTH columns when total desired width exceeds `console.width`.
   - Result: ASCII art in the left column gets truncated with an ellipsis (`…`).
   - Fix: Always pass explicit `width=left_w` on the fixed-width hero column, and explicitly constrain the right column `width=max_right_w` computed from the terminal budget.
2. **Terminal Emulator Hardware Wrap**:
   - If a rendered string exactly equals `console.width`, some terminals emit an automatic hardware carriage return, causing an unintended blank line. Always budget `console.width - 2` as the hard upper bound.
3. **Double Wrapping**:
   - Rich wrapping text inside an already wrapped panel border causes jagged borders and orphan characters. Always set explicit `width` or `max_width` on inner renderables.
4. **Emoji Cell Widths**:
   - Emojis (e.g. 🤖, 📚, ⚡) often occupy 2 cells in modern terminal emulators (iTerm2, Alacritty, Kitty), but some fallback fonts render them as 1 cell. Keep emoji usage in headers consistent and do not rely on character-perfect trailing whitespace after emojis.
5. **CLI Startup Breakpoints & The Split-Pane Trap**:
   - Many CLI runners (e.g. Hermes CLI) employ a hardcoded width threshold (e.g. `use_compact = term_width < 80`).
   - In IDE sidebars (VS Code), split tmux panes, or narrow terminal windows, width frequently drops into the 72–79 column range. If unhandled, the CLI bypasses the custom/dynamic banner entirely and silently falls back to a legacy default banner.
   - Defensive strategy:
     - Always brand and customize both the full banner AND the compact fallback banner (`_build_compact_banner`).
     - Tune the breakpoint down to the actual minimal viable width (e.g. 72–75 cols) when single-line truncation is active.
     - Verify startup warm-launch caches (e.g. `banner_snapshot.json`) across launcher profiles to prevent stale cache fallback.
