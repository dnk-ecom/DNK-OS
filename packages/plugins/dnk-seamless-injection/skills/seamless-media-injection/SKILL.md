---
name: seamless-media-injection
description: "Use when injecting brand logos, text, or 3D graphics into donor photos or videos with 100% photorealism, zero-trace texture inpainting, displacement warping, grain harmonization, and temporal flow consistency."
version: 1.0.0
author: DNK System Architecture
category: media
tags: [inpainting, sam2, lama, cotracker3, photorealism, grain-matching, shopify-cdn]
status: active
domain: seamless-media-injection
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "packages/plugins/dnk-seamless-injection/skills/seamless-media-injection/SKILL.md"
> purpose: "Operational guide for Zero-Trace Seamless Visual Injection Engine in DNK OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-10-22"
> author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# Zero-Trace Seamless Visual Injection Engine (`dnk-seamless-injection`)

## Overview
The **Zero-Trace Seamless Visual Injection Engine** (`packages/plugins/dnk-seamless-injection`) replaces donor logos, text boxes, or visual artifacts in high-resolution photos and 60fps videos while preserving fabric folds, lighting gradients, sensor ISO grain, and temporal optical flow.

## When to Trigger
- Replacing a donor logo or watermark on compression sportswear/leggings (e.g., **Monte** brand injection).
- Embedding brand typography or graphics onto curved, textured, or moving 3D surfaces.
- Verifying photorealism quality gates (`LPIPS < 0.04`, `Edge Gradient Consistency > 0.98`, `Zero-Residual OCR`) before syncing media to Shopify CDN.

## 5-Layer Mathematical Injection Pipeline

1. **Stage 1 — Subpixel Segmentation (`core/segmenter.py`)**:
   - Grounding DINO + SAM 2 wrapper (with deterministic multi-channel color/contrast + morphological fallback) generates a binary mask with **1.5–2.0px Gaussian feathering**, isolating donor text/logos without clipping anatomical lines or fabric seams.
2. **Stage 2 — Clean Texture Inpainting (`core/inpainter.py`)**:
   - Fast Fourier Convolution (LaMa) wrapper reconstructs periodic 3D compression fabric ribs and skin gradients across the masked region without blurring.
3. **Stage 3 — Surface & Lighting Extraction (`core/surface_blender.py`)**:
   - Extracts **Luminance Displacement Map** (high-frequency micro-folds and seams) and **Shading & Ambient Occlusion Map** (low-frequency directional illumination).
4. **Stage 4 — Deformable Geometric & Photometric Warp (`core/surface_blender.py`)**:
   - Warps the injected logo/text vector along fabric displacement vectors:
     $$I_{\text{warped}}(x, y) = I_{\text{logo}}\bigl(x + \alpha_x \nabla_x D(x,y),\; y + \alpha_y \nabla_y D(x,y)\bigr)$$
   - Modulates luminance with the extracted shading map and performs Poisson-like feathered alpha-gradient blending.
5. **Stage 5 — Spectral Sensor Grain Harmonization (`core/surface_blender.py`)**:
   - Measures per-channel RGB noise standard deviation ($\sigma_R, \sigma_G, \sigma_B$) in the surrounding unmasked ring and synthesizes matching correlated Gaussian sensor grain over the injected pixels.

## Video Pipeline (`core/video_tracker.py`)
- **Deformable Mesh Tracking (CoTracker3)**: Tracks a 500+ point grid across dynamic garment deformation.
- **Temporal Flow Consistency (RAFT Optical Flow + Savitzky-Golay / EMA Filter)**: Eliminates frame-to-frame jitter.
- **Motion Blur Matching**: Convolves the injected asset with a directional motion-blur kernel proportional to instantaneous pixel velocity $(v_x, v_y)$.

## MCP Tools (`mcp/server.py`)
Invoke directly via FastMCP or Python API:
1. `inject_brand_photo(image_path, brand_text, target_prompt, output_path, ...)`
2. `inject_brand_video(video_path, brand_text, target_prompt, output_path, fps, ...)`
3. `inspect_photorealism_metrics(original_path, injected_path, mask_bbox, donor_text, target_brand)`

## Mandatory Quality Gates
No asset is synced via `core/shopify_syncer.py` unless all three gates pass:
- `lpips_score < 0.04`
- `edge_gradient_consistency > 0.98`
- `donor_ocr_matches == 0` and `target_brand_readable == True`

## Detailed References (LOD)
- Photorealism math & quality thresholds: `references/photorealism_rules.md`
- Video mesh tracking & temporal smoothing: `references/video_tracking_guide.md`
