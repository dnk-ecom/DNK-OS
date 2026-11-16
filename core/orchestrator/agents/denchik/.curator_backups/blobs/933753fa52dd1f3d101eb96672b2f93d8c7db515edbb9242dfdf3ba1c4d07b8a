# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/gemini_imagen_storyboard_canvas_pipeline.md"
# purpose: "Multimodal Gemini Imagen 3 & Vertical Video Storyboard Pipeline on DNK Canvas."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "Gerych Prime, DNK OS"
# --- END DNK-MRH-HEADER ---

# Multimodal Gemini Imagen 3 & Vertical Video Storyboard Pipeline on DNK Canvas

## 1. Architectural Overview & Value
In DNK OS, viral video production (TikTok, Reels, Shorts) is orchestrated as a living graph on the infinite `@xyflow/react` canvas (`apps/web/components/canvas/`).
Instead of static text scripts or siloed AI generation tools, the production pipeline connects:
1. **Strategy / Research Node (`StrategyMarkdownNode`)**: Target audience, pain points, core hook, and conversion angle.
2. **Video Storyboard Node (`VideoStoryboardNoteNode`)**: 9:16 vertical scene-by-scene storyboard (0:00-0:04 Hook, 0:04-0:12 Problem, 0:12-0:25 Solution, 0:25-0:40 Demo, 0:40-0:50 CTA) with timings, voiceover, and visual prompts.
3. **Multimodal Image Generator (`PhotoStudioNode` / Vertex AI Imagen 3)**: Programmatic generation of 9:16 photographic frames for each scene via Gemini/Imagen.
4. **Remotion Composition Engine (`VideoCreatorNode` / `RemotionPlayer`)**: Real-time assembly of video composition with animated subtitles, pan-zoom transitions, and voiceover audio.

---

## 2. Canvas DAG Topology

```
┌─────────────────────────────────┐
│      StrategyMarkdownNode       │  (Target audience: Cold smoking 500L cabinet)
│   "Чому риба вариться у диму"   │
└────────────────┬────────────────┘
                 │ [DataFlowEdge]
                 ▼
┌─────────────────────────────────┐           ┌────────────────────────────────┐
│    VideoStoryboardNoteNode      │ ◄───────► │        PhotoStudioNode         │
│   - Scene 1: Pyrometer hook     │           │   (Vertex AI Imagen 3 API:     │
│   - Scene 2: Acidic dew fillet  │           │    9:16 cinematic generation)  │
│   - Scene 3: Thermal chamber    │           └────────────────────────────────┘
│   - Scene 4: Reburn cooler      │
│   - Scene 5: Golden balyk CTA   │
└────────────────┬────────────────┘
                 │
                 ├──────────────────────────────┐
                 ▼                              ▼
┌─────────────────────────────────┐  ┌────────────────────────────────┐
│       ArchifySpatialNode        │  │        VideoCreatorNode        │
│   (Technical Excalidraw SOTA    │  │    (Remotion 9:16 Composition: │
│    vector engineering schema)   │  │     subtitles + VO + music)    │
└─────────────────────────────────┘  └────────────────────────────────┘
```

---

## 3. Vertex AI Imagen 3 API Protocol

When generating vertical frames for the storyboard:
- **Endpoint**:
  `https://aiplatform.googleapis.com/v1/projects/${VERTEX_PROJECT_ID}/locations/${VERTEX_REGION}/publishers/google/models/imagen-3.0-generate-001:predict`
- **Request Payload**:
  ```json
  {
    "instances": [
      {
        "prompt": "Macro photorealistic 9:16 shot of cold smoked salmon sliced thin on a dark walnut cutting board, translucent delicate texture, condensation droplets, soft cinematic studio side lighting, high-end culinary photography, shot on 85mm lens, f/2.8, 8k resolution."
      }
    ],
    "parameters": {
      "sampleCount": 1,
      "aspectRatio": "9:16",
      "outputMimeType": "image/jpeg",
      "personGeneration": "allow_adult"
    }
  }
  ```
- **Asset Storage & URL Resolution**:
  - Generated frames are saved to `apps/web/public/media/storyboards/<topic>/frame_01.jpg` ... `frame_05.jpg`.
  - In Next.js, these are immediately servable via `/media/storyboards/<topic>/frame_01.jpg`.

---

## 4. `VideoStoryboardNoteNode` Data Contract

In `apps/web/components/canvas/nodes/VideoStoryboardNoteNode.tsx`:
```typescript
export interface StoryboardScene {
  id: string;
  timeRange: string;      // e.g. "0:00 - 0:04"
  visualPrompt: string;   // Image generation prompt / camera instruction
  voiceover: string;      // Spoken voiceover line
  imageUrl?: string;      // Path to generated Gemini frame (/media/storyboards/...)
  soundFx?: string;       // SFX cue (laser beep, sizzle, whoosh)
  cameraAngle?: string;   // e.g. "Extreme close-up, 45-degree angle"
}
```

---

## 5. Automation Python Script Recipe (`generate_gemini_storyboard_frames.py`)

```python
import os
import json
import base64
import requests

def generate_storyboard_frame(prompt: str, output_path: str) -> str:
    project_id = os.environ.get("VERTEX_PROJECT_ID")
    region = os.environ.get("VERTEX_REGION", "us-central1")
    token = os.environ.get("VERTEX_TOKEN") or os.environ.get("VERTEX_API_KEY")
    
    url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/imagen-3.0-generate-001:predict"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "9:16",
            "outputMimeType": "image/jpeg"
        }
    }
    
    res = requests.post(url, headers=headers, json=payload, timeout=60)
    res.raise_for_status()
    data = res.json()
    
    b64_img = data["predictions"][0]["bytesBase64Encoded"]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(b64_img))
        
    return output_path


---

## 6. Prompt Engineering Invariants for 9:16 Photorealistic Storyboards
1. **Typography Separation Invariant**:
   - NEVER request text, titles, subtitles, or numbers to be rendered inside the image generation prompt by Imagen 3.
   - AI diffusion models frequently hallucinate or distort typography.
   - All text (hooks, timestamps, measurements, badges) MUST be rendered as vector DOM elements in Next.js/React Flow or as dynamic Remotion subtitle layers.
2. **Cinematography & Framing Tokens**:
   - Always specify the optical setup: lens focal length (e.g. `85mm f/2.8 macro`, `24mm wide angle`), lighting (`soft directional studio side lighting`, `cinematic backlight`), and background depth of field (`shallow depth of field, dark muted background`).
3. **Aspect Ratio Enforcement**:
   - Pass `"aspectRatio": "9:16"` in parameters to prevent letterboxing or center-crop distortion when displaying in `VideoStoryboardNoteNode`.

---

## 7. Deferred Implementation & Architecture Anchoring Pattern
When the user indicates that a concept is to be captured now and implemented later ("маємо зафіксувати ідею і реалізовувати будемо пізніше"):
1. **SSOT Architecture Note**: Author a comprehensive Markdown architectural specification under `docs/notes/` (e.g. `141_node_based_viral_storyboard_studio_with_gemini_and_canvas.md`) detailing node types, data contracts, API payloads, and phased roadmap.
2. **Knowledge Hub Linking**: Cross-link the architecture note inside the relevant domain knowledge hubs (e.g. `docs/notes/Reburn/000 Reburn Knowledge Hub.md`).
3. **Zero Partial Code Churn**: Do not scaffold unfinished UI components or broken endpoints until the active implementation phase is explicitly triggered.
```
