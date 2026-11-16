# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/creative/blender_skills_assimilated/references/shopify_glb_checklist.md"
# purpose: "Shopify 3D GLB & Visual Match validation checklist assimilated from arjun988/blender-skills."
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-24"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Shopify 3D GLB & Reference Image Match Checklist

## 1. Scale & Transform Invariants
- [ ] Real-world physical product dimensions in meters (`1 Blender unit = 1m`).
- [ ] Object origin placed at bottom-center (`Z = 0`) so the product sits cleanly on the AR floor plane.
- [ ] All transforms applied (`Location = 0,0,0`, `Rotation = 0,0,0`, `Scale = 1,1,1`).
- [ ] Exported with `+Y Up` (`export_yup=True` in `bpy.ops.export_scene.gltf`).

## 2. Geometry & Material Budgets (Shopify `<model-viewer>`)
- [ ] File size: `<= 15 MB` target (`<= 4 MB` ideal for mobile 4G PDP load).
- [ ] Triangle count: `<= 50,000` triangles for hero e-commerce products.
- [ ] Material slots: `1–4` Principled BSDF materials (`MAT_` prefix).
- [ ] Textures: `1024x1024` or `2048x2048` max, packed ORM (Occlusion/Roughness/Metallic) where applicable.

## 3. Reference Image Convergence Loop (`reference-image-match.md`)
1. Document **Phase 0 Reference Analysis**: subject, aspect ratio, camera azimuth/elevation, key light direction, 5–8 hex palette.
2. Match `CAM_Hero` focal length (`50mm–85mm` for product studio shots).
3. Construct geometry in 3 tiers:
   - Tier 1: Primary silhouette & proportions.
   - Tier 2: Panel breaks, bevels, seams, caps.
   - Tier 3: Surface details, logos, accents.
4. Render preview (`BLENDER_EEVEE`) and compare silhouette/lighting before final GLB export.
