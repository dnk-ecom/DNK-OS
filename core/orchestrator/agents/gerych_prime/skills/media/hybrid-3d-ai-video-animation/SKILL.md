---
name: hybrid-3d-ai-video-animation
description: Use for 2D-to-3D Blender extrusion and Veo 3.1 animation.
version: 1.0.0
author: DNK-e.com Maksym & Gerych Prime
license: MIT
metadata:
  hermes:
    tags: [blender, veo, vertex-ai, 3d-animation, logo-animation, keyframes, vfx]
    related_skills: [blender_skills_assimilated, comfyui]
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/media/hybrid-3d-ai-video-animation/SKILL.md"
purpose: "Class-level workflow for 2D-to-3D contour extrusion in headless Blender and hybrid First-to-Last Frame VFX animation via Vertex AI Veo 3.1."
status: "Active"
version: "1.0.0"
updated_at: "2026-10-24"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Hybrid 3D + AI Video Animation Pipeline (`hybrid-3d-ai-video-animation`)

## When to Use
Use this skill whenever the user asks to:
- Convert a 2D raster logo or silhouette (`.png`, `.jpg`) into an extruded, beveled 3D model (`.blend`, `.glb`) in headless Blender without external tracing libraries.
- Split multi-part 2D/3D logos into independent 3D islands (e.g., stationary perch/letter vs. animated character/emblem).
- Create cinematic VFX logo or product animations (fire, living creatures, smoke, fluid morphs) that lock 100% accurately onto exact 3D brand geometry using Blender keyframes + Google Cloud Vertex AI Veo (`veo-3.1-generate-001`).

## 1. Zero-Dependency 2D-to-3D Contour Extrusion in Headless Blender
Blender's embedded Python (`bpy` + `numpy`) does not bundle `Pillow`, `opencv`, or `potrace`. Always load raster images directly through `bpy.data.images.load`:

1. **Pixel Extraction (`bpy.data.images` + `numpy`)**:
   ```python
   img = bpy.data.images.load(filepath)
   w, h = img.size
   pixels = np.array(img.pixels[:], dtype=np.float32).reshape((h, w, img.channels))
   ```
   - `bpy.data.images` orders rows bottom-to-top (`y = 0` is bottom), matching Blender's `+Z` vertical axis (`z = y / scale`).
2. **Directed Boundary Graph & Loop Tracing**:
   - Create a binary foreground mask (e.g. `(r - 0.5*(g + b)) > 0.25` for red-on-black logos or `alpha > 0.5` for transparent PNGs).
   - Extract horizontal and vertical pixel transitions between `1` and `0` as directed edges so the foreground stays on the left.
   - Trace closed vertex loops (`len(loop) >= 80` to discard noise), apply 3–4 passes of Laplacian smoothing (`0.25*prev + 0.5*curr + 0.25*next`), and subsample (`step=4`).
3. **Separate Islands vs. Unified Curve**:
   - **Unified 3D Logo**: Add all loops as `POLY` splines inside a single `bpy.data.curves.new(name, type='CURVE')` with `dimensions = '2D'` and `fill_mode = 'BOTH'`. Blender automatically subtracts inner holes.
   - **Split Elements for Animation**: Create a separate Curve object per loop (`Loop 0` = right element, `Loop 1` = left element), set `extrude` and `bevel_depth`, and convert each to `MESH` (`bpy.ops.object.convert(target='MESH')`).

## 2. Hybrid Blender Keyframes + Vertex AI Veo 3.1 (`First-to-Last Frame`)
Pure procedural Blender smoke/fire (`Mantaflow`) cannot synthesize living organic motion (e.g., a fiery bird with flapping wings and glowing head feathers landing and solidifying into metal), while pure text-to-video hallucinates brand logos. Combine both:

1. **Render Pixel-Locked 16:9 (`1920x1080`) Start & End Keyframes in Blender**:
   - Position a `50mm` camera at `Y = -8.2` with a `TRACK_TO` constraint aimed at the logo center so the full height has `>= 15%` top and bottom margin.
   - **Frame 1 (`frame_01_start_perch.png`)**: Hide the dynamic 3D element (`hide_render = True`) and render only the stationary 3D element (`R` perch) lit by warm orange rim lighting from the incoming flight direction.
   - **Frame 2 (`frame_02_end_logo.png`)**: Unhide all 3D elements (`hide_render = False`) from the **identical camera** so the stationary element stays pixel-locked and the completed 3D logo is revealed.
   - Inspect both PNGs with `vision_analyze` to verify zero framing cutoffs before calling Vertex AI.

2. **Call Vertex AI `veo-3.1-generate-001` (`predictLongRunning`)**:
   - Obtain token via `gcloud auth print-access-token` and resolve active project via `gcloud config get-value project`.
   - POST to `https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/veo-3.1-generate-001:predictLongRunning`:
     ```json
     {
       "instances": [{
         "prompt": "Narrative transition from Frame 1 to Frame 2...",
         "image": {"bytesBase64Encoded": "<b64_frame_1>", "mimeType": "image/png"},
         "lastFrame": {"bytesBase64Encoded": "<b64_frame_2>", "mimeType": "image/png"}
       }],
       "parameters": {
         "aspectRatio": "16:9",
         "sampleCount": 1,
         "durationSeconds": 8,
         "enhancePrompt": true,
         "generateAudio": true,
         "resolution": "1080p",
         "personGeneration": "allow_adult"
       }
     }
     ```
   - Poll `:fetchPredictOperation` with `{"operationName": op_name}` every 10s (~90–120s) and decode `response.videos[0].bytesBase64Encoded` to `.mp4`.

3. **Post-Generation Visual Verification**:
   - Extract a `2x2` contact sheet (`ffmpeg -y -i video.mp4 -vf "fps=0.5,scale=960:540,tile=2x2" -frames:v 1 contact_sheet.jpg`) and inspect with `vision_analyze` to confirm every story beat.

## 3. Pitfalls & Blender 5.x Notes
- **Blender 5.2+ `use_nodes` Deprecation**: `Material.use_nodes` and `World.use_nodes` are `True` by default in Blender 5.x and slated for removal in Blender 6.0; avoid redundant assignments when `mat.node_tree` already exists.
- **16:9 Vertical Framing Trap**: A `75mm+` focal length at close distance (`Y = -6.0`) fits `1:1` square renders but clips the top and bottom of tall vertical logos in `16:9` (`1920x1080`). Always switch to `50mm` at `Y = -8.2` for `16:9` keyframes.
- **Avoid Rendering Rigid 3D Meshes in Frame 1 for Organic Subjects**: If the user wants a living creature (e.g., a fiery phoenix) to fly in and transform into a 3D emblem, leave the creature's 3D mesh hidden in Frame 1 so Veo generates a living creature flying in rather than sliding a rigid 3D block.
