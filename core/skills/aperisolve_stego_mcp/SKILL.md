---
name: aperisolve_stego_mcp
description: "JIT Steganalysis & Image Forensics Suite via FastMCP (AperiSolve). Bit-plane LSB decomposition, EXIF metadata scrubbing, and anti-tampering asset verification for Shopify."
version: "1.0.0"
category: "security-forensics"
assimilated_at: "2026-11-16"
track: "Track 2: Quarantined Sidecar / FastMCP Microservice"
license: "GPL-3.0 (Quarantined in ../DNK_Vibe/AperiSolve, Clean Stdio Protocol)"
target_worker: "dnk_shopify"
status: active
domain: security-forensics
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/skills/aperisolve_stego_mcp/SKILL.md"
> purpose: "JIT Steganalysis & Image Forensics Suite via FastMCP (AperiSolve) for Shopify & Media Integrity"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-16"
> author: "Antigravity & DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# 🔍 AperiSolve Image Forensics & Steganalysis Suite (JIT FastMCP)

Assimilated from **[Zeecka/AperiSolve](https://github.com/Zeecka/AperiSolve)**.

Equips DNK OS agents (`dnk_shopify`, `dnk_media`, `gerych_auditor`) with Just-In-Time (JIT) image forensics, LSB bit-plane layer decomposition, metadata/EXIF scrubbing, and invisible digital watermark detection. Quarantined in `../DNK_Vibe/AperiSolve` and exposed as a clean FastMCP stdio microservice.

---

## 📌 Repository Intel & Legal Boundary
- **Upstream Repository**: `Zeecka/AperiSolve`
- **Quarantine Location**: `../DNK_Vibe/AperiSolve` (strictly decoupled from `DNK_HUB`)
- **License**: `GPL-3.0` (Quarantined execution; zero GPL code imported into DNK OS core)
- **Interface**: FastMCP Stdio Protocol (`uv run --directory ../DNK_Vibe/AperiSolve python -m aperisolve_mcp`)
- **SaaP Card**: `packages/plugins/dnk_aperisolve_forensics/service_manifest.yaml`
- **Python Adapter**: `packages/plugins/dnk_aperisolve_forensics/adapter.py`
- **Target Swarm Workers**: `dnk_shopify` (asset hygiene), `dnk_media` (video/image integrity), `gerych_auditor` (security gates)
- **Status**: 🟢 **ACTIVE & PRODUCTION READY**

---

## 🚀 Key Capabilities for DNK OS

1. **Shopify Asset Privacy & EXIF Scrubbing**:
   - Strips GPS tags, camera serial numbers, Photoshop creation trails, and merchant personal metadata before uploading images to Shopify CDN.
2. **Supplier Catalog Payload Auditing**:
   - Analyzes third-party supplier zip/tar archives and product images with `exiftool`, `binwalk`, `zsteg`, and `strings` to prevent malicious polyglot injections (e.g., PHP/JS payloads disguised as PNG/JPEG).
3. **Invisible Digital Watermarking Verification**:
   - Decomposes image bit-planes (RGB bit 0 through 7) to inspect LSB steganography, validating proprietary copyright marks on custom lifestyle and 3D renders.
4. **Context-Diet Multimodal Guardrails**:
   - Employs token-efficient response models: paginated tool outputs (`get_tool_output`), downscaled layer planes (`max_side=1024`), and index-only result tables (`list_results`).

---

## 🛠️ Usage Recipes

### Recipe 1: JIT FastMCP Mounting in Swarm Worker

**Goal:** Mount AperiSolve FastMCP tools on demand for a specialized security or asset audit slice without standing context bloat.

```python
# In any swarm subagent turn or orchestrator worker
from core.registry.service_registry import ServiceRegistry

registry = ServiceRegistry()
service = registry.services.get("dnk_aperisolve_forensics")

# Transport command for stdio subprocess
transport = service.transport
# command: uv run --directory ../DNK_Vibe/AperiSolve python -m aperisolve_mcp
```

### Recipe 2: Sanitize Image Metadata for Shopify CDN Upload

**Goal:** Strip all metadata and tracking artifacts before pushing lifestyle/banner images into Shopify theme assets.

```python
from pathlib import Path
from packages.plugins.dnk_aperisolve_forensics.adapter import AperiSolveAdapter

adapter = AperiSolveAdapter()
clean_path = adapter.sanitize_image_metadata(
    image_path="assets/raw_hero_photo.png",
    output_path="assets/hero_photo_clean.png"
)
```

### Recipe 3: Deep Forensics Scan on Suspect Asset via FastMCP

**Goal:** Run steganalysis over an uploaded supplier image to verify absence of concealed payloads.

1. Encode the candidate asset as base64.
2. Call FastMCP tool `analyze(file_base64=..., filename="supplier_pdp.png", deep=False)`.
3. Call `wait_until_done(hash=submission_hash)`.
4. Inspect `list_results(hash=submission_hash)` for any flagged tools or extracted archives.
5. If `has_download` is true or warnings appear, inspect with `get_tool_output(hash=submission_hash, tool="binwalk")`.
