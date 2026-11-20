---
name: iris_assimilated
description: "Assimilated SOTA patterns from brijr/iris: CDP visual feedback loop, smart page settling, IntersectionObserver lazy loading, and element bounding clip."
version: "1.0.0"
category: "software-development"
assimilated_at: "2026-09-12"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "gerych_builder"
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/iris_assimilated/SKILL.md"
purpose: "Assimilated brijr/iris CDP Visual Capture Engine, Smart Settling, Lazy-Load Step Scrolling, and Element Bounding"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-12"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🌐 BRIJR/IRIS Assimilation Index & Recipes

Meta-index and practical implementation patterns assimilated from **[brijr/iris](https://github.com/brijr/iris)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `brijr/iris`
- **License**: `MIT` (Commercial safe)
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_builder` / `dnk_dev_fullstack`
- **Obsidian Reference**: `docs/notes/149_iris_visual_feedback_and_inspection_engine.md`
- **SOTA Report**: `docs/tech/sota_assimilation/SOTA_IRIS_ASSIMILATION.md`
- **Adapter**: `core/adapters/dnk_iris_adapter.py`

---

## 📁 Key Assimilated Architectural Pillars

1. **Zero-Bloat Protocol Compliance**:
   - Zero git clone operations performed. Inspected and extracted via GitHub REST API.
   - Core Rust algorithms (`SETTLE_JS`, `SCROLL_JS`, `element_bounds_js`, presets) extracted into clean Python hexagonal adapter.
   - Zero heavy framework dependencies (no Puppeteer/Playwright Node modules).

2. **Smart Page Settling (`SETTLE_JS`)**:
   - Font loading check via `document.fonts.ready`.
   - Viewport-bounded image loading with 3s timeout.
   - Dual RAF cycle to flush browser paint pipelines.
   - Draining active CSS transitions and animations (`document.getAnimations()`).

3. **Progressive Lazy Loading Step-Scroll (`SCROLL_JS`)**:
   - Iterative viewport-height steps down the document triggering `IntersectionObserver` callbacks.
   - Smooth return to top `(0, 0)` with settling buffer.

4. **Dual Engine Execution Hierarchy**:
   - **Engine 1**: Native compiled `iris` binary (~360ms sub-second execution).
   - **Engine 2**: Autonomous Headless Chrome fallback (`/Applications/Google Chrome.app/...`), providing instant captures without external installation.

---

## 🛠️ Execution Recipes

### 1. Python Adapter Usage
```python
from core.adapters.dnk_iris_adapter import IrisVisualEngine

engine = IrisVisualEngine()
res = engine.capture(
    url="http://localhost:3000",
    output_path="tmp/screenshot.png",
    size="desktop",  # 'desktop', 'iphone', 'ipad', or '1920x1080'
    dark=True,
    selector="[data-testid='hero-card']",
    padding=16
)
print(f"Captured via {res['engine']}: {res['output_path']}")
```

### 2. CLI Fast Bridge
```bash
# Capture element in Dark Mode
python3 scripts/system/iris_inspect.py http://localhost:3000 --selector ".nav-header" --dark

# Capture iPhone responsive view
python3 scripts/system/iris_inspect.py http://localhost:3000 --size iphone --output ./tmp/iphone_preview.png
```
