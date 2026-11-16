---
title: "Extraction Recipes"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/web-app-reverse-engineering/references/extraction_recipes.md"
> purpose: "Document: Extraction Recipes"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# 🔬 Production Bundle Extraction Recipes

## 1. Complete String & Injected CSS Extraction from Client JS
Modern Vite/Webpack bundles often inject hundreds of component styles encoded as template literals or quoted string arrays:

```python
import re
from pathlib import Path

def extract_all_css_from_bundle(bundle_path: Path, output_path: Path):
    text = bundle_path.read_text()
    
    # Extract both backtick template literals and quoted string CSS rules
    matches_backtick = re.findall(r'`([^`]*?\.[a-zA-Z0-9\-_]{2,30}\s*\{[^`]*?)`', text)
    matches_quoted = re.findall(r'"([^"\\]*?\.[a-zA-Z0-9\-_]{2,30}\s*\{[^"]*?)"', text)
    
    all_blocks = []
    for m in (matches_backtick + matches_quoted):
        if "{" in m and "}" in m and (";" in m or ":" in m) and len(m) > 15:
            # Clean escaped characters
            cleaned = m.replace("\\n", "\n").replace('\\"', '"').replace("\\'", "'")
            all_blocks.append(cleaned)
            
    combined = "\n\n/* --- EXTRACTED COMPONENT BLOCK --- */\n\n".join(all_blocks)
    output_path.write_text(combined)
    print(f"Extracted {len(all_blocks)} CSS blocks ({output_path.stat().st_size} bytes)")
```

## 2. Extract Shape AST & Discriminated Unions
```python
import re
from pathlib import Path

def extract_shape_contracts(bundle_path: Path):
    text = bundle_path.read_text()
    shape_kinds = set(re.findall(r'shape\.kind\s*===?\s*["\']([a-zA-Z0-9_\-]+)["\']', text))
    materials = set(re.findall(r'material\s*===?\s*["\']([a-zA-Z0-9_\-]+)["\']', text))
    print("Found shape kinds:", shape_kinds)
    print("Found materials:", materials)
    return {"shapes": shape_kinds, "materials": materials}
```

## 3. Chaikin B-Spline Curve Smoothing for Freehand & Poly Beds
To achieve smooth CAD curves without heavy external dependencies:

```typescript
export function smoothPolygon(points: { x: number; z: number }[], iterations = 2): { x: number; z: number }[] {
  if (points.length < 3) return points;
  let current = points;
  for (let it = 0; it < iterations; it++) {
    const next: { x: number; z: number }[] = [];
    const n = current.length;
    for (let i = 0; i < n; i++) {
      const p0 = current[i];
      const p1 = current[(i + 1) % n];
      // Chaikin subdivision: 75%/25% and 25%/75% points
      next.push({ x: 0.75 * p0.x + 0.25 * p1.x, z: 0.75 * p0.z + 0.25 * p1.z });
      next.push({ x: 0.25 * p0.x + 0.75 * p1.x, z: 0.25 * p0.z + 0.75 * p1.z });
    }
    current = next;
  }
  return current;
}
```

## 4. Real-Time Edge Segment Metrics (Meters)
```typescript
export function getSegmentLengths(points: { x: number; z: number }[], ppm = 40) {
  const segments = [];
  const n = points.length;
  for (let i = 0; i < n; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % n];
    const dx = p2.x - p1.x;
    const dz = p2.z - p1.z;
    const pixelDist = Math.sqrt(dx * dx + dz * dz);
    segments.push({
      p1,
      p2,
      mid: { x: (p1.x + p2.x) / 2, z: (p1.z + p2.z) / 2 },
      lengthMeters: pixelDist / ppm
    });
  }
  return segments;
}
```

## 5. Vertex AI Gemini Multimodal Diffing Call
```python
import subprocess
import urllib.request
import json
import ssl

def query_gemini_multimodal(prompt: str, image_b64: str = None) -> str:
    token = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True).stdout.strip()
    url = "https://us-central1-aiplatform.googleapis.com/v1/projects/project-2826e39f-abdc-4c1d-8b5/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent"
    
    parts = [{"text": prompt}]
    if image_b64:
        parts.append({"inline_data": {"mime_type": "image/png", "data": image_b64}})
        
    data = json.dumps({"contents": [{"role": "user", "parts": parts}]}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=ctx) as r:
        res = json.loads(r.read())
        return res["candidates"][0]["content"]["parts"][0]["text"]
```
