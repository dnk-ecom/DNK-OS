---
title: "Spa Cad Reverse Engineering And Bundle Harvest"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/spa_cad_reverse_engineering_and_bundle_harvest.md"
> purpose: "Document: Spa Cad Reverse Engineering And Bundle Harvest"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/denchik/skills/software-development/sota-repository-assimilation/references/spa_cad_reverse_engineering_and_bundle_harvest.md"
# purpose: "Zero-Browser Fast-Path for SPA CAD & WebGL constructors: In-Memory AST, Entity Catalogs, and Geometry Extraction."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-30"
# author: "DNK-e.com Maksym & Denchik Prime"
# --- END DNK-MRH-HEADER ---

# ⚡ Zero-Browser Fast-Path: SPA CAD & WebGL Constructor In-Memory Reverse Engineering

## 1. Context & Motivation
When reverse-engineering modern browser-based CAD and WebGL constructors (such as BloomsEye Studio, Planner5D, or Canva-style builders), attempting to scrape interactive canvases via headless browser automation (Playwright/Puppeteer/CDP) is slow, fragile, and misses deep model contracts. Modern SPAs (Vite/Webpack/Rollup) bundle data models, entity catalogs, and geometry schemas directly into preloaded JavaScript chunks.

## 2. In-Memory Bundle Harvesting Pipeline (Execution in < 3s)
Rather than executing headless browsers:
1. **Entry HTML Harvest**:
   - Fetch target entry point (`/`, `/online`, `/editor`) using lightweight HTTP `curl` or `urllib`.
   - Extract `<script type="module" src="...">` and `<link rel="modulepreload" ...>` hashes.
2. **Chunk Discovery & Classification**:
   - `catalog-data-*.js`: Entity databases, taxonomies, dimensions, tags, pricing, and asset maps.
   - `index-*.js`: React/Vue/Svelte router state machine, CAD canvas interaction handlers, and geometry math.
   - `vendor-*.js`: Runtime dependencies (Three.js, Zod, Supabase, Tailwind, PixiJS).
   - `*Worker*.js`: WebWorkers handling heavy computation (e.g., depth map estimation, geometry triangulation).
3. **In-Memory AST / Regex Slicing (`execute_code`)**:
   - Load chunk text into Python memory without burning LLM context window.
   - Extract entity record schemas (e.g., botanical flora, furniture objects, CAD layers).
   - Extract exact CDN asset maps (`slug -> .webp / .svg / .glb / .gltf`).
   - Extract spatial geometry primitives: coordinate schemas (`{x, z}` planar coordinates, `y` elevation), polygon smoothing algorithms, footprint area calculations.

## 3. Concrete Case: BloomsEye Studio Architectural Proof
- **Catalog Density**: 2,610 distinct plant varieties across 11 taxonomic categories (`Tree`, `Conifer`, `Shrub`, `Perennial`, `Grass`, `Fern`, etc.).
- **Asset Schema**: Direct key-value mapping table linking slugs to 5,216 WebP high-resolution imagery and dimensions.
- **Parametric Geometry**:
  - `shape: { kind: "polygon", points: [...] }` (smooth B-splines) or `{ kind: "rect", origin, width, depth }`.
  - Dynamic surface types (`mulch`, `lawn`, `gravel`, `soil`, `hardscape`).
  - Three.js procedural crown shader with 4-season transitions (`bloom`, `foliage` hex codes).
