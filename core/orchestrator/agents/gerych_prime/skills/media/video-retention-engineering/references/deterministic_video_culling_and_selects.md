# Deterministic Video Culling & Selects Architecture

## Overview & The Cutdown Paradigm
Automated footage culling and "selects" generation isolates usable sub-clips from raw video footage without heavy AI inference models. It relies on deterministic computer vision mathematics across three core axes: **Focus**, **Exposure**, and **Motion**, followed by zero-reencode timeline export (FCPXML, Premiere XML, EDL, AAF).

---

## 1. Mathematical Analysis Pipeline (The 3 M's)

### A. Pre-Processing Optimization
- Downscale frames to ~960px (long side) and convert to single-channel 8-bit grayscale for real-time throughput (>120 FPS).

### B. Focus & Sharpness Analysis
- **Metric**: Local gradient energy via Laplacian Variance ($\sigma^2(\nabla^2 I)$) or Tenengrad filter (Sobel magnitude $\sum (G_x^2 + G_y^2)$).
- **Noise Discounting**: Compute sharpness over a grid (e.g. 8x8 patches). Dark shadow patches ($Y < 20$) are discounted to prevent sensor noise from mimicking high-frequency edge detail.
- **Focus Stability**: Moving-window variance filter over consecutive frames to detect autofocus "hunting" or rack-focus drift.

### C. Exposure & Dynamic Range Analysis
- **Luma Histogram**: Split luminance [0..255] into crushed shadows ($< 5$), midtones, and blown highlights ($> 250$).
- **Grading Flexibility**: Ratio of usable dynamic range before highlight/shadow clipping.
- **Inter-Frame Flicker**: Temporal variance of average luminance between frames $t$ and $t-1$ to detect light flickering.

### D. Motion Estimation & Camera vs Subject Separation
- **Feature Tracking**: Lucas-Kanade optical flow (`cv2.calcOpticalFlowPyrLK`) on Shi-Tomasi good features.
- **Camera Motion Estimation**: Fit global transformation (affine or homography) using RANSAC. The inlier consensus model represents camera movement (Static, Pan, Tilt, Dolly).
- **Subject Motion**: Outlier vectors represent moving subjects or foreground objects.
- **Instability Detection**: High angular acceleration in homography indicates camera shake or whip-pan transitions.

---

## 2. Pass/Fail Scoring & Segment Generation
1. **Frame Scoring**: Calculate weighted quality score $Q_t = w_f F_t + w_e E_t + w_m M_t$.
2. **Hard Flags**: Instant fail if frame is out-of-focus, clipped beyond threshold, or during camera whip/shake.
3. **Selects Contiguity**: Group consecutive passing frames into segments where $\text{duration} \ge \text{min\_duration}$ (e.g., 1.5s).
4. **Handles (Head/Tail Padding)**: Add configurable padding (e.g. 12-24 frames) to segment boundaries for editing flexibility.

---

## 3. Leading Open-Source Tools & Repositories

| Repository | Stars / Stack | Core Functionality |
| :--- | :--- | :--- |
| **`ceevents/video-culler`** | React + FastAPI + OpenCV | Automated wedding/event footage culler; focus scoring + smart selects duration + FCPXML/Premiere export. |
| **`WyattBlue/auto-editor`** | ~4.7k★ / Python, Nim | Motion & silence detection (`--edit motion`), zero-reencode export to DaVinci, Premiere, FCPXML, OpenTimelineIO. |
| **`murlexander/louppe-media-culler`** | Swift / macOS Native | Local high-speed media culler with keyboard shortcuts, histogram review, and batch export. |
| **`ChrisChen667788/pixcull`** | Python / PySceneDetect | Multi-axis photo & video quality scoring (sharpness, exposure) + shot boundary detection. |
| **`AcademySoftwareFoundation/OpenTimelineIO`** | ~2.0k★ / C++, Python | Standard editorial timeline interchange API for EDL, FCPXML, Premiere XML, AAF. |
| **`Breakthrough/PySceneDetect`** | ~5.2k★ / OpenCV | Scene transition and cut detection library with XML/CSV markers export. |

---

## 4. Headless Deterministic Quality Checks via FFmpeg

When running automated pipelines in headless CI or server agents, native FFmpeg filters provide deterministic frame metrics without external Python dependencies:
- **Sharpness/Blur**: `ffmpeg -i input.mp4 -vf "blurdetect=high=0.11:low=0.05" -f null -`
- **Exposure & Broadcast Range**: `ffmpeg -i input.mp4 -vf "signalstats" -f null -`
- **Freeze/Motionless Frames**: `ffmpeg -i input.mp4 -vf "freezedetect=n=0.003:d=2" -f null -`
