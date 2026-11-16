# TUI Layout Patterns & Code Recipes

## 1. Responsive 2-Column Dashboard with Column Isolation & Explicit Width Budget

This pattern isolates columns into separate `rich.console.Group` objects and sets explicit column widths so that content in one column never truncates or alters line spacing of the other:

```python
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

def render_responsive_dashboard(console: Console, title: str, left_items: list[str], right_items: list[str]):
    width = console.width or 85

    # Fixed width of left hero block (e.g. 46-char ASCII logo)
    left_w = 46

    # Dynamic panel and column padding based on terminal width breakpoints
    panel_padding = 0 if width < 88 else 1
    col_padding = 1 if width < 92 else 2

    # Calculate exact remaining width budget for right column:
    # 2 chars for outer Panel borders, panel_padding * 2, col_padding, left_w
    max_right_w = max(24, width - (left_w + col_padding + (panel_padding * 2) + 2))

    # Standard / wide layout: 2 columns via 1-row Table.grid with EXPLICIT widths
    grid = Table.grid(padding=(0, col_padding))
    grid.add_column("left", justify="left", no_wrap=True, width=left_w)
    grid.add_column("right", justify="left", no_wrap=True, width=max_right_w)

    left_group = Group(*left_items)
    right_group = Group(*right_items)

    grid.add_row(left_group, right_group)
    console.print(Panel(grid, title=title, padding=(0, panel_padding)))
```

## 2. Strict Single-Line Item Truncation

Prevent accidental multi-line expansion of list items in narrow terminals:

```python
from rich.text import Text

def format_telemetry_item(label: str, description: str, max_width: int) -> Text:
    """Formats label and description on a single line, truncating if necessary."""
    line = f"{label} — {description}"
    return Text(line, no_wrap=True, overflow="ellipsis")
```

## 3. Safe Terminal String Length Measurement

Calculating cell width without being fooled by ANSI sequences or emojis:

```python
from rich.text import Text

def get_visible_cell_len(markup_or_ansi_text: str) -> int:
    """Returns actual character cells occupied on the terminal grid."""
    return Text.from_markup(markup_or_ansi_text).cell_len


## 4. Dual-Mode Responsive Banner & Breakpoint Fallback Pattern

Handle both wide and compact / split-pane modes gracefully without falling back to an unstyled default:

```python
import shutil
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

def show_adaptive_banner(console: Console, skin_name: str, dynamic_meta: dict):
    term_width = shutil.get_terminal_size().columns or 80
    min_full_width = 74  # Tuned lower bound when right column truncates cleanly

    if term_width < min_full_width:
        # Compact mode: single-line or minimal 2-line branded status
        banner = Panel(
            Text(f"[{dynamic_meta.get('system_name', 'CORE')}] "
                 f"{dynamic_meta.get('agents_count', 0)} agents · "
                 f"{dynamic_meta.get('skills_count', 0)} skills · "
                 f"{dynamic_meta.get('mcp_count', 0)} MCP",
                 justify="center"),
            border_style="cyan"
        )
        console.print(banner)
        return

    # Standard full 2-column layout
    render_responsive_dashboard(console, dynamic_meta["title"], dynamic_meta["left"], dynamic_meta["right"])
```

```
