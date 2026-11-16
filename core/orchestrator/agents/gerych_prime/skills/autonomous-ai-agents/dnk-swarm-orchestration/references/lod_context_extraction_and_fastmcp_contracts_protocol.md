<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/lod_context_extraction_and_fastmcp_contracts_protocol.md"
purpose: "Canonical LOD Context Slicing protocol and FastMCP Plugin Contracts for DNK OS Workhorses."
status: "Active"
version: "1.1.0"
updated_at: "2026-09-20"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

# 🧬 LOD Context Extraction & FastMCP Plugin Contracts Protocol

## 1. Overview & Architecture
To eliminate standing token bloat (JIT Tooling) and maintain context efficiency across the 3 Core Workhorses (`dnk_media`, `dnk_commerce` / `dnk_shopify`, `services/dnk_distribution`), all plugin context must pass through the `LODContextExtractor` (`core/harness/lod_context.py`).

Context is generated just-in-time from the canonical Pydantic v2 identity models (`UserProfile`, `ProjectWorkspace`, `BrandDNA`).

## 2. Core Operational Invariants
1. **Strict 1,500-Token Budget Ceiling**:
   - Total rendered context injected into a specialist subagent must never exceed 1,500 tokens (approx. 6,000 characters).
   - If projected context exceeds this budget, non-critical collections (such as raw product lists, historical proposals, or secondary assets) are dynamically sliced or truncated.
2. **Inviolability of Negative Constraints**:
   - Brand negative constraints (`BrandDNA.negative_constraints`) represent legal, tone-of-voice, and compliance boundaries.
   - **MANDATORY**: `negative_constraints` are NEVER dropped or truncated, regardless of budget pressure.
3. **Strict Relative Path Invariant**:
   - All asset paths, directories, and logo locations must use workspace-relative paths (`./assets/...`, `docs/...`). Absolute paths are rejected at schema validation.
4. **Targeted Field Projection**:
   - Plugins declare their exact needs via `PluginManifest.required_context_fields` (e.g. `["brand_dna", "assets", "voice_preferences"]`).
   - The extractor slices only the requested fields rather than dumping the full monolithic workspace.
5. **FastMCP Server Initialization & Export Convention**:
   - **Parameter Quirk (FastMCP 3.x)**: FastMCP uses `instructions`, NOT `description`. Calling `FastMCP(name, description="...")` raises `TypeError: FastMCP.__init__() got an unexpected keyword argument 'description'`. Always initialize with:
     ```python
     mcp = FastMCP("dnk_service_name", instructions="...")
     ```
   - **Multi-Export SSOT**: Always export `mcp`, `server = mcp`, and `app = mcp` in `server.py` to allow dynamic loading across CLI MCP runners, `FastMCPDispatcher`, and ASGI test mounts.
   - **Zero Service Proliferation Symlink Invariant**: To satisfy AGENTS.md Rule 8 (3 Core Workhorses SSOT) when aliasing service contracts (e.g., `dnk_commerce` for `dnk_shopify`), implement the server under `services/dnk_shopify/server.py` with `mcp = FastMCP("dnk_commerce", ...)` and establish a relative symlink:
     `ln -s dnk_shopify services/dnk_commerce`.

## 3. The 3 Core Workhorses Contracts
- **`dnk_media` (`services/dnk_media/server.py`)**:
  * Focus: Video generation, kinetic typography, Remotion scripts, image assets.
  * Required fields: `brand_dna`, `assets`, `voice_preferences`.
  * Canonical Tools:
    - `generate_product_visual(prompt, aspect_ratio="1:1", style_preset="photorealistic") -> Dict`: Generates visual asset metadata with BrandDNA palette and moodboard tags.
    - `render_motion_canvas(title, duration_seconds=15) -> Dict`: 9:16 Remotion kinetic canvas (30 fps, 1080x1920) with clamped scene timelines.
- **`dnk_commerce` (`services/dnk_shopify/server.py` via symlink `services/dnk_commerce`)**:
  * Focus: Shopify Liquid themes, product sync, checkout UI extensions.
  * Required fields: `brand_dna`, `products`, `store_config`.
  * Canonical Tools:
    - `transpile_liquid_template(section_name, blocks=None) -> Dict`: Generates Shopify OS 2.0 Liquid code with validated `{% schema %}` JSON block.
    - `sync_product_catalog(catalog_csv_path) -> Dict`: Synchronizes inventory and prices according to BrandDNA margin rules.
- **`dnk_distribution` (`services/dnk_distribution/server.py`)**:
  * Focus: Multi-channel publishing, social copy formatting, email newsletters.
  * Required fields: `brand_dna`, `distribution_channels`, `voice_preferences`.
  * Canonical Tools:
    - `format_social_post(raw_text, channel) -> Dict`: Formats copy per channel rules (`twitter` <= 280 chars + tags, `telegram` header + CTA, `linkedin` bulleted insights).

## 4. Verification & Direct FastMCP Async Test Pattern
When verifying FastMCP tool execution in pytest, tools can be invoked either directly as Python functions or via FastMCP's asynchronous `call_tool`:
```python
import pytest
import json
from services.dnk_media.server import mcp

@pytest.mark.asyncio
async def test_fastmcp_call_tool():
    # Invoke via FastMCP async interface
    result = await mcp.call_tool("render_motion_canvas", {"title": "Summer Drop", "duration_seconds": 15})
    assert result is not None
    payload = json.loads(result[0].text)
    assert payload["status"] == "success"
    assert payload["aspect_ratio"] == "9:16"
```
