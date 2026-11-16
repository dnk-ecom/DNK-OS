---
name: blender_skills_assimilated
description: Use for Blender 3D, Shopify GLB models, and bpy scripts.
version: 1.0.0
author: DNK-e.com Maksym & Gerych Prime
license: MIT
metadata:
  hermes:
    tags: [blender, 3d, glb, shopify, pbr, bpy, media]
    related_skills: [comfyui, sota-repository-assimilation]
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/creative/blender_skills_assimilated/SKILL.md"
purpose: "Consolidated SOTA Blender 3D & Shopify GLB pipeline assimilated from arjun988/blender-skills."
status: "Active"
version: "1.0.0"
updated_at: "2026-10-24"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Blender 3D & Shopify GLB Pipeline (`blender_skills_assimilated`)

## When to Use
Use this skill whenever the user asks to:
- Generate, inspect, optimize, or convert 3D models (`.blend`, `.glb`, `.gltf`, `.fbx`, `.obj`).
- Create 3D product models for Shopify PDP (`<model-viewer>` / AR Quick Look).
- Render 3D studio product shots or turntable animations for `dnk_media` / Remotion.
- Write or audit Blender Python (`bpy`) scripts in headless mode (`/opt/homebrew/bin/blender -b`).

## 1. DNK OS Execution Architecture (Headless-First Invariant)
Instead of relying on an unauthenticated GUI socket (`localhost:9876`), execute Blender deterministically in headless mode via `services/dnk_media/src/creation/blender_headless_engine.py` or CLI:
```bash
/opt/homebrew/bin/blender -b --factory-startup --python <script.py>
```
- **Zero Standing Overhead**: Spawns on demand, uses Apple Silicon Metal (`METAL`), exports `.glb` or `.png`, and exits cleanly.
- **Interactive Mode (Optional)**: Only use `uvx blender-mcp` if the user explicitly opens the Blender GUI for live viewport lookdev.

## 2. Universal 10-Stage Asset Pipeline (Never Skip Planning)
1. **Reference & Scale Analysis**: Establish real-world dimensions (`1 Blender unit = 1 meter`). For e-commerce products, use exact physical product dimensions in meters.
2. **Collection & Naming Setup**:
   - Collections: `COL_Reference`, `COL_Geo_Hero`, `COL_Lights`, `COL_Cameras`, `COL_Export`.
   - Prefixes: `SM_` (Static Mesh), `MAT_` (Material), `T_` (Texture), `CAM_` (Camera), `LGT_` (Light).
3. **3-Tier Geometry Construction**:
   - **Tier 1 (Primary Silhouette)**: Block out core proportions with primitives + Subdivision/Bevel modifiers.
   - **Tier 2 (Secondary Structural Breaks)**: Seams, rims, caps, bevels, recesses (never leave flat sharp boxes).
   - **Tier 3 (Tertiary Accents)**: Logos, knurling, buttons, emissive indicators.
4. **Topology & Cleanup**:
   - Merge by distance, recalculate outside normals, remove internal/non-manifold faces, apply Weighted Normals after Bevel.
5. **PBR Materials (Principled BSDF)**:
   - Metals: `Metallic = 1.0`, `Roughness = 0.15–0.45` (never `0.0` or `1.0`).
   - Dielectrics/Plastics/Ceramics: `Metallic = 0.0`, `IOR = 1.45–1.55`, `Roughness = 0.1–0.7`.
6. **Three-Point Studio Lighting & Camera**:
   - Key light (`45°` azimuth, `30–45°` elevation), Fill light (`-45°`, 30–50% intensity), Rim light (`135–160°` behind subject).
   - Camera: `50mm–85mm` focal length for product hero shots (avoids wide-angle distortion).
7. **Shopify GLB Optimization & Export**:
   - Apply all transforms (`location=0`, `rotation=0`, `scale=1`).
   - Export via `bpy.ops.export_scene.gltf(filepath=..., export_format='GLB', export_apply=True, export_yup=True)`.
8. **Deterministic Validation Gate**:
   - Verify triangle budget (`<= 50,000` tris for Shopify hero prop), material slots (`1–4`), and non-zero bounding box.

## 3. Pitfalls & Anti-Patterns
- **Never use `bpy.ops` context-dependent operators in headless mode without explicit selection** (`bpy.context.view_layer.objects.active = obj; obj.select_set(True)`). Prefer data API (`bpy.data.meshes.new`, `bmesh`) when possible.
- **Blender 4.0+/5.x Principled BSDF Socket Names**: Use `"Base Color"`, `"Metallic"`, `"Roughness"`, `"IOR"`, `"Emission Color"`, `"Emission Strength"` (note: `"Emission"` was renamed to `"Emission Color"` in Blender 4.0+).
- **Blender 4.2+/5.x EEVEE Engine Name**: Use `BLENDER_EEVEE` or `CYCLES` depending on `bpy.app.version` (in Blender 5.x, `BLENDER_EEVEE` is standard).

## 4. LOD References
Load detailed checklists with `skill_view(name='blender_skills_assimilated', file_path='references/shopify_glb_checklist.md')`.
