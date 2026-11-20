---
title: "Video Tracking Guide"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "packages/plugins/dnk-seamless-injection/skills/seamless-media-injection/references/video_tracking_guide.md"
> purpose: "Document: Video Tracking Guide"
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
mrh_id: "packages/plugins/dnk-seamless-injection/skills/seamless-media-injection/references/video_tracking_guide.md"
purpose: "Deformable surface tracking, optical flow stabilization, and motion blur matching specification."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-10-22"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Video Tracking & Temporal Stability Guide

## 1. Deformable Mesh Tracking (CoTracker3 Architecture)
- Initialize a dense $N \ge 500$ point grid (e.g., $25 \times 20 = 500$ vertices) over the target garment zone (waistband, thigh, or compression panel).
- Track vertex trajectories $\mathbf{P}_t = \{(x_{i,t}, y_{i,t})\}_{i=1}^N$ across frames $t \in [0, T-1]$, including local scale/stretch tensors as the fabric compresses and extends during walking or turning.

## 2. Temporal Flow Stabilization (Zero-Jitter Guarantee)
Frame-independent logo placement causes high-frequency temporal jitter.
- Apply bidirectional exponential moving average (EMA) / Savitzky-Golay temporal filtering over trajectory velocities:
  $$\tilde{\mathbf{P}}_t = \lambda \mathbf{P}_t + \frac{1 - \lambda}{2}(\mathbf{P}_{t-1} + \mathbf{P}_{t+1})$$
- Frame-to-frame acceleration jitter $\max_t \|\Delta^2 \tilde{\mathbf{P}}_t\|$ must remain below `0.15 px/frame^2` at 60fps.

## 3. Directional Motion Blur Matching
When instantaneous optical flow speed $v = \sqrt{v_x^2 + v_y^2}$ exceeds `1.5 px/frame`:
- Construct a directional line convolution kernel $K(v_x, v_y)$ aligned with angle $\theta = \text{atan2}(v_y, v_x)$ and length $L = \text{clamp}(\lfloor v \rfloor, 1, 15)$.
- Convolve the warped brand overlay prior to grain synthesis so motion blur matches the camera shutter speed of the donor footage.
