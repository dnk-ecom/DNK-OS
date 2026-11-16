# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/media/seamless-brand-injection/references/cellumove-monte-rebranding-recipe.md"
# purpose: "Reference recipe for multi-zone UI card text replacement and 3D apparel brand injection with zero bounding-box discoloration."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-23"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Multi-Zone Ad Creative Rebranding & 3D Apparel Injection Recipe

When rebranding composite e-commerce ad creatives (such as before/after split cards with flat UI badges + physical apparel photos):

1. **Flat UI Badges (`WITHOUT <DONOR>` / `WITH <DONOR>`)**:
   - Sample a clean vertical/horizontal strip from the badge's own solid/gradient background immediately above or beside the donor text.
   - Resize and paste the sample over the donor word bounding box.
   - Render the new brand name in matching bold sans-serif (`Arial Bold.ttf`) with matching fill color.

2. **3D Apparel Fabric Injection (`SurfaceBlender`)**:
   - Bypass destructive rectangular mask inpainting when injecting onto clean fabric.
   - Extract surface normals and displacement maps from the target ROI (`hip_bbox`).
   - Render 2x supersampled brand overlay, warp along fabric folds, and blend with matched camera sensor ISO grain only where `alpha > 0.004`.

## Reproducible Python Script

```python
import importlib.util
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

plugin_root = Path("packages/plugins/dnk-seamless-injection").resolve()
spec = importlib.util.spec_from_file_location(
    "dnk_seamless_injection_pkg",
    str(plugin_root / "__init__.py"),
    submodule_search_locations=[str(plugin_root)],
)
mod = importlib.util.module_from_spec(spec)
sys.modules["dnk_seamless_injection_pkg"] = mod
spec.loader.exec_module(mod)
from dnk_seamless_injection_pkg.core.surface_blender import SurfaceBlender

donor_path = "./tests/.tmp/seamless_injection_test/donor_real.png"
donor_img = Image.open(donor_path).convert("RGB")
result_img = donor_img.copy()

# 1. Rebrand bottom navy card: "WITH CELLUMOVE" -> "WITH MONTE"
bot_bg_sample = donor_img.crop((1000, 1040, 1465, 1060)).resize((465, 78))
result_img.paste(bot_bg_sample, (1000, 1060))
draw = ImageDraw.Draw(result_img)
font_bot = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 44)
draw.text((1004, 1072), "MONTE", fill=(255, 255, 255), font=font_bot)

# 2. Rebrand top light card: "WITHOUT CELLUMOVE" -> "WITHOUT MONTE"
top_bg_sample = donor_img.crop((1090, 535, 1445, 555)).resize((355, 72))
result_img.paste(top_bg_sample, (1090, 560))
font_top = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 40)
draw.text((1094, 574), "MONTE", fill=(52, 64, 76), font=font_top)

# 3. 3D Apparel Injection on Hip Fabric via SurfaceBlender (zero bounding-box discoloration)
hip_bbox = (255, 920, 335, 975)
blender = SurfaceBlender(displacement_strength=3.6, shading_strength=0.68, feather_sigma=1.5)
surface_maps = blender.extract_surface_maps(result_img, hip_bbox)
overlay = blender.render_brand_overlay((80, 55), brand_text="Monte", color=(220, 224, 228), opacity=215)
warped = blender.warp_and_shade_overlay(overlay, surface_maps)
result_img, donor_sig, inj_sig = blender.blend_and_harmonize_grain(result_img, warped, hip_bbox)

out_dir = Path("./tests/.tmp/cellumove_real_test")
out_dir.mkdir(parents=True, exist_ok=True)
result_img.save(out_dir / "monte_perfect_injection.png")
```
