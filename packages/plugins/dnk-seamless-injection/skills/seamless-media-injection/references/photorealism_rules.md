---
title: "Photorealism Rules"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "packages/plugins/dnk-seamless-injection/skills/seamless-media-injection/references/photorealism_rules.md"
> purpose: "Document: Photorealism Rules"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

<!-- --- DNK-MRH-HEADER ---
mrh_id: "packages/plugins/dnk-seamless-injection/skills/seamless-media-injection/references/photorealism_rules.md"
purpose: "Mathematical rules and quality gate invariants for 100% photorealistic visual injection."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-10-22"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Photorealism Rules & Mathematical Quality Gates

## 1. Subpixel Feathering Invariant
Hard binary masks produce visible step edges ("scissor cut" artifacts) on 4K/Retina displays.
- Every segmentation mask MUST apply an isotropic Gaussian feathering kernel with $\sigma \in [1.5, 2.0]$ pixels at the boundary transition zone.
- Anatomical seams and garment edges outside the prompt bounding box must remain 100% untouched ($\alpha = 0$).

## 2. Luminance Displacement & Shading Decomposition
Given the clean inpainted background patch $B(x, y)$ in luminance space $L \in [0, 1]$:
- **Shading Map ($S$)**: Low-pass Gaussian filter $G_{\sigma_{\text{low}}}(L)$ capturing directional studio lighting, shadows, and specular highlights.
- **Displacement Map ($D$)**: High-pass residual $D(x, y) = L(x, y) - S(x, y)$ capturing micro-ribs of 3D compression fabric.
- **Coordinate Warp**:
  $$\Delta x = k_d \cdot \frac{\partial L}{\partial x}, \quad \Delta y = k_d \cdot \frac{\partial L}{\partial y}$$
- **Photometric Modulation**:
  $$C_{\text{shaded}}(x, y) = C_{\text{warped}}(x, y) \cdot \left(\gamma_{\text{base}} + (1 - \gamma_{\text{base}}) \cdot \frac{S(x, y)}{\bar{S}}\right)$$

## 3. Sensor Noise & Film Grain Synthesis
Vector graphics have zero entropy ($\sigma_{\text{noise}} = 0$), which immediately betrays synthetic compositing.
- Estimate high-frequency sensor residual $R_c = I_c - G_{\sigma=1.0}(I_c)$ for each channel $c \in \{R, G, B\}$ in the surrounding donor ring.
- Sample zero-mean Gaussian noise $N_c \sim \mathcal{N}(0, \hat{\sigma}_c^2)$ and blend into the injected region proportional to mask alpha $\alpha(x, y)$.

## 4. Quality Gate Thresholds
1. **LPIPS Perceptual Patch Distance**: `< 0.04` (strictly `< 0.05` hard ceiling) between boundary neighborhood patches.
2. **Edge Gradient Consistency**: `> 0.98` cosine/normalized gradient continuity across the mask contour.
3. **Zero-Residual OCR**: `0` matches for donor text tokens; `100%` match confidence for injected brand (`Monte`).
