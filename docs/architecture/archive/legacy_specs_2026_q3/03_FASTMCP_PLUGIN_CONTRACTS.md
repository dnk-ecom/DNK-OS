---
title: "03 Fastmcp Plugin Contracts"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/03_FASTMCP_PLUGIN_CONTRACTS.md"
> purpose: "Document: 03 Fastmcp Plugin Contracts"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/03_FASTMCP_PLUGIN_CONTRACTS.md"
> # purpose: "Canonical FastMCP Plugin Contracts, Manifests, and LOD Context Extraction Protocol for DNK OS Core Workhorses."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.0.0"
> # updated_at: "2026-09-20"
> # author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# 🔌 03 FastMCP Plugin Contracts & Manifest Specification

## 1. Overview & System Philosophy
DNK OS utilizes the **Model Context Protocol (MCP)**, specifically lightweight Python **FastMCP** servers, to connect reasoning LLM agents with deterministic functional domain capabilities.

Per the architectural tenet **"ЛЮДИНА — ІДЕЇ, АГЕНТИ — ВИКОНАВЦІ"** and the **Anti-Proliferation Invariant (ADR-004)**, arbitrary ad-hoc microservices are strictly prohibited. All domain capabilities are consolidated into the **3 Core Workhorses**:
1. `services/dnk_media` — Creative generation, visual styling, Remotion kinetic video, and canvas annotations.
2. `services/dnk_commerce` — Shopify Liquid OS 2.0 AST generation, product inventory syncing, and checkout extensions.
3. `services/dnk_distribution` — Multi-channel marketing syndication, social post formatting, newsletter dispatch, and SEO metadata.

---

## 2. FastMCP Manifest Schema (`PluginManifest`)

Every plugin workhorse registers a canonical manifest that dictates:
- Entrypoints and runtime transport (`stdio` or `sse`).
- Declarative tool schemas (`PluginToolSpec`).
- **Required Context Slices** (`required_context_fields`), informing the `LODContextExtractor` which subset of `BrandDNA` or `UserProfile` to load.
- Strict token ceiling (`token_budget_limit: 1500 tokens`).

### JSON Schema Specification
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PluginManifest",
  "type": "object",
  "required": ["plugin_id", "name", "entrypoint", "transport", "tools", "required_context_fields", "token_budget_limit"],
  "properties": {
    "plugin_id": {
      "type": "string",
      "pattern": "^dnk_[a-z0-9_]+$",
      "description": "Unique plugin identifier e.g. dnk_media"
    },
    "name": {
      "type": "string",
      "description": "Human-readable plugin title"
    },
    "version": {
      "type": "string",
      "default": "1.0.0"
    },
    "entrypoint": {
      "type": "string",
      "description": "Python module import path e.g. services.dnk_media.server:app"
    },
    "transport": {
      "type": "string",
      "enum": ["stdio", "sse"],
      "default": "stdio"
    },
    "capabilities": {
      "type": "array",
      "items": { "type": "string" }
    },
    "tools": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "description", "input_schema"],
        "properties": {
          "name": { "type": "string" },
          "description": { "type": "string" },
          "input_schema": { "type": "object" },
          "output_schema": { "type": "object" }
        }
      }
    },
    "required_context_fields": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Context slice targets: 'brand_dna.visual_style', 'brand_dna.negative_constraints', etc."
    },
    "token_budget_limit": {
      "type": "integer",
      "default": 1500,
      "minimum": 100,
      "maximum": 4000
    }
  }
}
```

---

## 3. The 3 Canonical Core Workhorse Manifests

### 3.1. `dnk_media` (Media & Creative Studio)
- **Plugin ID**: `dnk_media`
- **Entrypoint**: `services.dnk_media.server:app`
- **Transport**: `stdio`
- **Required Context Fields**:
  - `brand_dna.visual_style` (Palette, typography, moodboard tags)
  - `brand_dna.negative_constraints` (Mandatory safety & aesthetic prohibitions)
  - `brand_dna.mission` (Brand context)
- **Tools**:
  - `generate_product_visual(prompt: str, aspect_ratio: str, style_preset: str)`
  - `render_motion_canvas(title: str, duration_seconds: int)`

### 3.2. `dnk_commerce` (Shopify & E-Commerce Engine)
- **Plugin ID**: `dnk_commerce`
- **Entrypoint**: `services.dnk_commerce.server:app`
- **Transport**: `stdio`
- **Required Context Fields**:
  - `brand_dna.mission` (Brand value proposition)
  - `brand_dna.target_audience` (Customer demographics)
  - `brand_dna.tone_of_voice` (Product copywriting guidelines)
  - `brand_dna.negative_constraints` (Forbidden claims or terms)
- **Tools**:
  - `transpile_liquid_template(section_name: str, blocks: list)`
  - `sync_product_catalog(catalog_csv_path: str)`

### 3.3. `dnk_distribution` (Multi-Channel Syndication)
- **Plugin ID**: `dnk_distribution`
- **Entrypoint**: `services.dnk_distribution.server:app`
- **Transport**: `stdio`
- **Required Context Fields**:
  - `brand_dna.tone_of_voice` (Communication style)
  - `brand_dna.target_audience` (Audience segmentation)
  - `brand_dna.negative_constraints` (Forbidden wording or topics)
  - `user.communication_style` (Language code, conciseness)
- **Tools**:
  - `format_social_post(raw_text: str, channel: str)`

---

## 4. Level-of-Detail (LOD) Context Slicing Protocol

To eliminate context rot and preserve fast response latencies (<2s), DNK OS enforces **LOD Context Slicing** via `core.harness.lod_context.LODContextExtractor`:

1. **JIT Slicing**: When an agent executes a tool on a plugin, the harness queries the plugin manifest's `required_context_fields`.
2. **Context Projection**: Only the declared fields are extracted from `ProjectWorkspace` and `UserProfile`.
3. **Negative Constraints Invariant**: `brand_dna.negative_constraints` are **always included**, regardless of whether the plugin explicitly listed them. Safety and brand guardrails can never be omitted.
4. **Token Ceiling Guard**: If total serialized context exceeds `token_budget_limit` (default: 1,500 tokens), non-critical lists and long descriptions are systematically truncated with an explicit warning, while preserving core brand identities and negative constraints.

---

## 5. Verification & Testing
LOD context extraction and plugin manifest compliance are verified via:
- Unit tests: `tests/core/test_lod_context.py`
- Master Quality Gate: `bash scripts/verify_all.sh`
