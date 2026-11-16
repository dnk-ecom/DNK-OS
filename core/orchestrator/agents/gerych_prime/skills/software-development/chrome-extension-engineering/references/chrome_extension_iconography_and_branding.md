<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/chrome-extension-engineering/references/chrome_extension_iconography_and_branding.md"
purpose: "Reference guide for Chrome Extension Manifest V3 iconography, micro-scale legibility, cranial centering, and headless Playwright rasterization."
status: "Active"
version: "1.1.0"
updated_at: "2026-10-01"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Chrome Extension Iconography & Headless Rasterization Pipeline

## 1. Icon Scaling & Micro-Scale Legibility Invariants
Chrome extensions require 4 standardized icon sizes in `manifest.json`:
- **16×16**: Favicon in `chrome://extensions/` page, context menus, and small toolbar indicators.
- **32×32**: Chrome toolbar pinned extension button on Retina/HiDPI displays.
- **48×48**: Extensions management page list (`chrome://extensions/`).
- **128×128**: Chrome Web Store installation dialog, large options headers, and permissions prompts.

### Micro-Scale Design Rules (128px Master SVG):
1. **Stroke Thickness**: In a `128×128` viewBox, minimum stroke width must be **3px to 4px**. Lines thinner than 2.5px blur into gray smear artifacts during 16×16 raster anti-aliasing.
2. **Solid Silhouettes over Outlines**: Prefer filled vector paths (`fill="#ffffff"`) over multi-line wireframes or complex mesh gradients.
3. **Squircle & Safe Margin**: A squircle container with `rx="28"` and at least `14px-18px` inner margin prevents shapes from clipping against browser UI frames.
4. **Primary Silhouette Scale**: The primary subject (profile, monogram, mascot) should occupy 65–75% of the squircle frame to remain legible at micro-sizes (16px / 32px).

---

## 2. Anatomical Human Profile & Cranial Centering Invariants

### A. Profile Vector Geometry (Facing Left-to-Right)
When creating a human profile vector icon:
- **Intellectual Cranium**: Smooth, prominent forehead dome curving into the brow (`C 28 22 42 12 60 12`).
- **Nasion & Nasal Contour**: Delicate nose bridge with a defined tip (`C 73 12 84 22 84 37 L 85 40 ... C 91 49 92 50.5 87 52.5`).
- **Speaking Lips**: Articulated, slightly parted lips to convey speech interaction (`C 85 54 84 55.5 88 57` to `87.5 57`).
- **Mandible & Cervical Spine**: Distinct chin (mental protuberance), clean jawline, and natural neck curvature flowing downward (`C 74 67.5 68 71.5 63 73 C 61 75 60 78 60 82 C 68 86 78 94 82 108`).

### B. "Cranial Centering" (AI / Monogram as Brain)
Placing an "AI", brain circuit, or monogram inside a head silhouette must **never** be centered to the full bounding box of the figure (which includes jaw and neck, erroneously pulling the center into the throat):
- **Cerebral Vault Location**: Center the glyph strictly within the **upper cranial dome** (`x ~ 45, y ~ 56` in a 128x128 viewBox).
- **Equidistant Cranial Margins**: Maintain equal spacing from the letterform edges to the frontal bone (forehead) and occipital bone (back of skull) — approx 7.5px–8px padding on all sides.
- **Negative-Space Knockout Mask**: Avoid external badges or thin outline letters. Punch the monogram directly through the solid white silhouette using an SVG `<mask>`, exposing the emerald gradient beneath.
- **Typography Calibration**: Use heavy geometric grotesque fonts (`font-weight="900"`, `font-size="22"`, `letter-spacing="1.5px"`). Generous letter spacing preserves optical counters at 16×16.

### C. Speech Waves Geometry
- **Origin**: Emanate radially from the mouth aperture (focal origin at lip opening `x=88, y=56`).
- **Curvature**: 3 clean concentric arcs facing outward:
  - Wave 1: `M 96 46 A 8 8 0 0 1 96 58`
  - Wave 2: `M 101.5 42 A 14 14 0 0 1 101.5 62`
  - Wave 3: `M 107 38 A 20 20 0 0 1 107 66`
- **Stroke**: Uniform `stroke-width="3"`, `stroke-linecap="round"`, `fill="none"`.

---

## 3. Production Master SVG Reference

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="emeraldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#008060" />
      <stop offset="100%" stop-color="#004c3f" />
    </linearGradient>

    <!-- Cranial Knockout Mask: White keeps silhouette, Black cuts out brain monogram -->
    <mask id="headCutoutMask">
      <rect width="128" height="128" fill="#ffffff" />
      <text x="45" y="56"
            font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
            font-weight="900" font-size="22" fill="#000000"
            text-anchor="middle" letter-spacing="1.5">AI</text>
    </mask>
  </defs>

  <!-- Squircle Base -->
  <rect width="128" height="128" rx="28" fill="url(#emeraldGrad)" stroke="#30cd90" stroke-opacity="0.35" stroke-width="2" />

  <!-- Human Head Profile with Brain AI Knockout -->
  <path mask="url(#headCutoutMask)" fill="#ffffff"
        d="M 18 108 C 21 95 28 88 36 83 C 35 79 34 74 34 68 C 27 67 23 62 23 55 C 23 48 26 44 30 43 C 28 22 42 12 60 12 C 73 12 84 22 84 37 L 85 40 C 89 42 92 46 93 48 C 93.5 49 93 50 91.5 50.5 C 91 49 92 50.5 87 52.5 C 85 53.5 86 54.5 89 55 C 89.5 55.5 89 56.5 87.5 57 C 85 58 84 59.5 87 60 C 88 60.5 87 61.5 85 62 C 84 62 81 63 77 63 C 74 67.5 68 71.5 63 73 C 61 75 60 78 60 82 C 68 86 78 94 82 108 Z" />

  <!-- 3 Radiating Speech Waves -->
  <path d="M 96 46 A 8 8 0 0 1 96 58 M 101.5 42 A 14 14 0 0 1 101.5 62 M 107 38 A 20 20 0 0 1 107 66"
        stroke="#ffffff" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.95" />
</svg>
```

---

## 4. Headless Playwright Rasterization (`build_extension_icons.js`)
Deterministic SVG-to-PNG rasterization using Playwright Chromium:

```javascript
#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function getPlaywright() {
  try {
    return require('playwright');
  } catch (e) {
    const defaultPlaywright = '/Users/kuzmenko.top/Library/Caches/ms-playwright-go/1.57.0/package';
    if (fs.existsSync(defaultPlaywright)) {
      return require(defaultPlaywright);
    }
    throw new Error('Playwright not found in node_modules or system cache');
  }
}

async function buildIcons(options = {}) {
  const rootDir = options.rootDir || path.resolve(__dirname, '..');
  const svgPath = path.join(rootDir, 'icons', 'icon.svg');
  const iconsDir = path.join(rootDir, 'icons');

  if (!fs.existsSync(svgPath)) {
    throw new Error(`Master SVG not found at ${svgPath}`);
  }

  const svgContent = fs.readFileSync(svgPath, 'utf8');
  const { chromium } = getPlaywright();
  const browser = await chromium.launch({ headless: true });

  const sizes = [16, 32, 48, 128];
  for (const size of sizes) {
    const page = await browser.newPage({
      viewport: { width: size, height: size },
      deviceScaleFactor: 1
    });

    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: ${size}px; height: ${size}px; background: transparent; overflow: hidden; }
    svg { width: ${size}px; height: ${size}px; display: block; }
  </style>
</head>
<body>
  ${svgContent}
</body>
</html>`;

    await page.setContent(html, { waitUntil: 'load' });
    const outputPath = path.join(iconsDir, `icon${size}.png`);
    await page.screenshot({ path: outputPath, omitBackground: true });
    
    // Maintain hyphenated duplicates if existing scripts reference them
    fs.copyFileSync(outputPath, path.join(iconsDir, `icon-${size}.png`));
    await page.close();
  }

  await browser.close();
}

if (require.main === module) {
  buildIcons().catch(err => {
    console.error(err);
    process.exit(1);
  });
}
```

---

## 5. Dual-Track Synchronization: Manifest & UI Vector Catalogs
When refreshing extension branding, update both raster assets and inline JS catalogs:

1. **Manifest V3 (`manifest.json`)**:
```json
{
  "icons": {
    "16": "icons/icon16.png",
    "32": "icons/icon32.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "action": {
    "default_icon": {
      "16": "icons/icon16.png",
      "32": "icons/icon32.png"
    }
  }
}
```

2. **Inline JavaScript Icon Catalogs (`common/icons.js`)**:
Extensions frequently render vector icons dynamically in UI headers (Popup, Sidepanel, Options) to guarantee crisp HiDPI rendering:
```javascript
export const SVG_DEFS = {
  logo: `<svg viewBox="0 0 128 128" width="100%" height="100%">
    <defs>
      <mask id="dnkLogoMask">
        <rect width="128" height="128" fill="#ffffff" />
        <text x="45" y="56" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="900" font-size="22" fill="#000000" text-anchor="middle" letter-spacing="1.5">AI</text>
      </mask>
      <linearGradient id="dnkLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#008060" />
        <stop offset="100%" stop-color="#004c3f" />
      </linearGradient>
    </defs>
    <rect width="128" height="128" rx="28" fill="url(#dnkLogoGrad)" stroke="#30cd90" stroke-opacity="0.35" stroke-width="2" />
    <path mask="url(#dnkLogoMask)" fill="#ffffff" d="M 18 108 C 21 95 28 88 36 83 C 35 79 34 74 34 68 C 27 67 23 62 23 55 C 23 48 26 44 30 43 C 28 22 42 12 60 12 C 73 12 84 22 84 37 L 85 40 C 89 42 92 46 93 48 C 93.5 49 93 50 91.5 50.5 C 91 49 92 50.5 87 52.5 C 85 53.5 86 54.5 89 55 C 89.5 55.5 89 56.5 87.5 57 C 85 58 84 59.5 87 60 C 88 60.5 87 61.5 85 62 C 84 62 81 63 77 63 C 74 67.5 68 71.5 63 73 C 61 75 60 78 60 82 C 68 86 78 94 82 108 Z" />
    <path d="M 96 46 A 8 8 0 0 1 96 58 M 101.5 42 A 14 14 0 0 1 101.5 62 M 107 38 A 20 20 0 0 1 107 66" stroke="#ffffff" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.95" />
  </svg>`
};
```
3. **Multi-Surface Verification**: Always verify both raster PNG fallbacks and dynamic vector SVG renderings across Popup, Sidepanel, and Options page headers using `vision_analyze` on live screenshots.
