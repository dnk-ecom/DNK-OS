---
name: seamless-brand-injection
description: Use when injecting brand logos onto photos or videos.
version: 1.0.0
license: MIT
author: DNK-e.com Maksym & Gerych Prime
tags: [media, image-processing, brand-injection, inpainting, surface-blending, ecommerce]
metadata:
  hermes:
    tags: [media, image-processing, brand-injection, inpainting, surface-blending, ecommerce]
    related_skills: [comfyui, video-retention-engineering]
---

# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/media/seamless-brand-injection/SKILL.md"
# purpose: "5-Stage Zero-Trace Seamless Visual Brand Injection & ROI Artifact Prevention Protocol."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-23"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Zero-Trace Seamless Visual Brand Injection (`dnk-seamless-injection`)

## When to Use

Use this skill when replacing competitor/donor watermarks, rebranding comparison cards, or injecting 3D-warped brand typography/logos (`Monte`, etc.) onto textured apparel (leggings, activewear, curved surfaces) in product images and 60fps video frames using `packages/plugins/dnk-seamless-injection/`.

## Core 5-Stage Pipeline Architecture

1. **Stage 1: Sub-Pixel Segmentation (`core/segmenter.py` — `SubpixelSegmenter`)**
   - Detects high-contrast donor logos/watermarks inside `hint_bbox` and applies `1.5–2.0px` Gaussian feathering.
   - **Critical Invariant (Additive vs. Subtractive Mode)**: When `full_binary.getbbox() is None` (no high-contrast donor watermark exists in the ROI, e.g., injecting a brand onto clean fabric), the mask MUST remain empty (`0`). Never fill a fallback `255` rectangle over `hint_bbox`, or Stage 2 will blur the entire bounding box and create a visible blurry patch around the text.
2. **Stage 2: Frequency-Selective Texture Inpainting (`core/inpainter.py` — `LaMaTextureInpainter`)**
   - Reconstructs underlying fabric weave/ribbing ONLY where the Stage 1 mask > 0. Leaves unmasked pixels 100% untouched.
3. **Stage 3: Dense 500+ Point Mesh Tracking (`core/mesh_tracker.py` — `CoTracker3MeshTracker`)**
   - Tracks non-rigid fabric deformation across video frames with sub-pixel temporal smoothing (`jitter < 0.15px`).
4. **Stage 4: 3D Normal/Displacement Warping & Shading (`core/surface_blender.py` — `SurfaceBlender`)**
   - Extracts surface normals and displacement maps from clean background fabric (`extract_surface_maps`).
   - Renders 2x supersampled brand typography (`render_brand_overlay`) using system TrueType/OpenType fonts (`Arial Bold.ttf`, `Helvetica.ttc`) before falling back to `ImageFont.load_default()`.
   - Warps glyph geometry along fabric folds and modulates pixel luminance (`warp_and_shade_overlay`).
5. **Stage 5: Photometric Alpha Blending & ISO Sensor Grain Matching (`blend_and_harmonize_grain`)**
   - Estimates RGB high-frequency camera sensor noise (`estimate_sensor_grain_sigma`) and injects matched Gaussian grain only into non-transparent glyph pixels (`alpha > 0.004`).

## Verification & CLI Usage

### 1. Run the CLI Visual Runner & Comparison Sheet Generator
```bash
.venv/bin/python packages/plugins/dnk-seamless-injection/cli_test_image.py \
  --input "./tests/.tmp/seamless_injection_test/donor_real.png" \
  --brand-text "Monte" \
  --roi "255,920,335,975" \
  --output-dir "./tests/.tmp/cellumove_real_test"
```

### 2. Mandatory Quality Gates
Every injection run must pass the three deterministic gates in `04_quality_report.json`:
- `lpips_score < 0.04` (perceptual seamlessness)
- `edge_gradient_consistency > 0.98` (zero hard boundary seams)
- `donor_ocr_matches == 0` (zero residual competitor text)

### 3. Unit & Anti-Tautology Test Suite
```bash
.venv/bin/pytest packages/plugins/dnk-seamless-injection/tests/ -v
.venv/bin/python scripts/system/anti_tautology_guard.py \
  packages/plugins/dnk-seamless-injection/tests/test_grain_matching.py \
  packages/plugins/dnk-seamless-injection/tests/test_temporal_consistency.py
```

## Pitfalls & Anti-Patterns

- **Blurry Rectangular ROI Box Artifact**: Caused by pasting a solid `255` mask over `hint_bbox` when no donor watermark is present, or applying background modification across all bbox pixels regardless of overlay `alpha`. Always gate pixel blending on `if alpha <= 0.004: keep original pixel verbatim`.
- **Pixelated Bitmap Text**: Never rely on bare `ImageFont.load_default()` without size/TrueType resolution when rendering brand overlays on high-res photos; always resolve a scalable `.ttf`/`.ttc` font at 2x supersampling (`ss = 2`).
- **UI Card Text Replacement vs. 3D Apparel Injection**: For flat UI banners/badges (e.g., `"WITHOUT CELLUMOVE"` / `"WITH CELLUMOVE"`), sample a clean adjacent strip of the card background, paste over the old word, and render crisp matched-font text. Reserve `SurfaceBlender` 3D displacement warping for curved physical fabric/product surfaces.

## References
- See `references/cellumove-monte-rebranding-recipe.md` for the complete multi-zone rebranding script (UI badge replacement + 3D hip fabric injection + 2x zoom verification sheet).
