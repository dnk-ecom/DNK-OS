# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/scroll_craft_scrollytelling_and_headless_verification_patterns.md"
# purpose: "Patterns and architectural lessons harvested from nateherkai/scroll-craft: scrollytelling runtimes, dense-GOP scrubbing, headless visual verification, and anti-template grammars."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-25"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Scroll-Craft Scrollytelling, Media Scrubbing & Headless Verification Patterns

Harvested from `nateherkai/scroll-craft` (v0.3.1, MIT, 4.0k ⭐). Key patterns applicable to `services/dnk_media`, `services/dnk_shopify`, `gerych_builder`, and `gerych_auditor`.

---

## 1. Dense-GOP Video Scrubbing Pipeline (`encode.sh`)

Standard web video puts a keyframe (I-frame) every 2–5 seconds. While fine for passive playback, seeking via mousewheel forces the browser decoder to traverse backwards from the previous keyframe on every tick, causing heavy CPU lag and sluggish scrub feel.

### Production Encoding Invariant
- **Desktop**: 1080p (`scale=-2:1080`), GOP 8 (`-g 8 -keyint_min 8`), `-sc_threshold 0`, preset slow, CRF 20 (or 22–23 for noisy/grainy footage), Lanczos scaling (`format=yuv420p`), `-an` (strip audio to prevent autoplay blocking and save weight).
- **Mobile**: 720p (`scale=-2:720`), GOP 4 (`-g 4 -keyint_min 4`), CRF 24.
- **FastStart**: `-movflags +faststart` to place moov atom at beginning of file.
- **Blob Loading**: Load scrub clips via `fetch() -> blob:` URLs so the browser seeks locally without requiring HTTP byte-range server roundtrips.

---

## 2. Headless Mechanical Quality Gate (`shoot.mjs` & `sheet.png`)

Static unit tests and single-viewport screenshots cannot validate scrollytelling pages where bugs live between scroll intervals.

### Automated Detection Checks
1. **Dead Scroll Detector**: Samples DOM and render metrics across $N$ positions per act. If 2+ consecutive scroll positions advance without any clip progress, cue transition, rail travel, or clip-path change, trigger a Dead Scroll failure (wasted user effort).
2. **Frozen Clip Detector**: Detects when a pinned stage is translating in viewport (sliding up/down) while video `currentTime` remains stationary. Scrub time must be mapped across the stage's *entire on-screen life* (including entry/exit slides), not just the pinned dwell.
3. **Composited Per-Frame Contrast Gate**: Measures WCAG contrast ratio between text lines and the composited video/canvas backdrop across the brightest and darkest frames that travel under the copy.
4. **Decoder Codec Invariant**: Headless Playwright runs MUST use installed Google Chrome (`executablePath`), NOT bare Chromium. Bundled Chromium lacks proprietary H.264 decoders and silently passes against fallback posters without decoding scrub video.

---

## 3. Anti-Convergence Page Grammars & Emotion Curves (`feel.md`, `uniqueness.md`)

AI-generated web experiences notoriously converge into identical generic designs (cards, 01/06 counters, purple gradients, claymation dioramas).

### Structural Invariants
- **8 Mutually Exclusive Grammars**:
  - *Filmic One-Shot*: Unbroken linear arc, forbids visible chapter counters or multi-entry chrome.
  - *Chaptered Editorial*: Segmented reading, requires index markers and explicit pause points.
  - *Live Surface, Continuous World, Typographic Poster, Gallery, Split Stage, Rhythmic Cutlist*.
  - *The Forbid Rule*: Each grammar explicitly defines what elements it **forbids**. A page must never quietly drift back to the filmic default.
- **Emotion Curve Before Act List**:
  - Author the feeling curve in the brief first: `[Act] -> [Target Emotion] -> [On-screen Visual Cause]`.
  - Peak-End Rule: Exactly 1 engineered emotional peak per page with maximum scroll real estate and silence/rest before it. Adjacent acts with identical emotional tone are rejected as filler.
- **Fingerprint Gate**:
  - Every new generated landing page must differ from previously generated projects on $\ge 4$ of 6 dimensions: Grammar, Navigation model, Hero composition, Act sequence, Close mechanism, Signature interaction move.

---

## 4. Engine Architecture & Performance Pitfalls (Lessons for Gerych Builder)

1. **Idle rAF Drain**: Do not run a persistent `requestAnimationFrame` loop when no playhead is moving or when scroll is idle. Stop the loop and wake it on `scroll`, `resize`, or video state change.
2. **Forced Synchronous Layout**: Never read `scrollHeight` or `getBoundingClientRect()` after mutating inline CSS properties (`--sc-p`, `transform`, `opacity`) within the same frame. Read metrics once, cache them, and update via `ResizeObserver`.
3. **Local Server Dotfile Hygiene**: Static test servers must explicitly reject requests for hidden dotfiles (`.env`, `.git`) and verify resolved symlink targets against the root directory before piping streams.
