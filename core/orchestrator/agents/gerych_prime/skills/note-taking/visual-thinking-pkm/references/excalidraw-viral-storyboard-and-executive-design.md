# Excalidraw Executive Design & Viral Storyboard Architecture

## 1. The Anti-Child-Drawing Invariants (Legibility & Visual Authority)

### Common Failure Modes & User Rejections
- **Microscopic Text (<14px)**: When rendered at default canvas zoom, text is illegible without aggressive manual pinch-to-zoom.
- **Rainbow Pastel Clutter**: Using 6-10 uncoordinated pastel colors across dozens of tiny shapes produces an amateurish "kindergarten drawing" effect.
- **Chaotic Asymmetry**: Random coordinates, misaligned margins, and inconsistent element heights destroy executive credibility.

### Executive Design Standards (DNK OS Standard)
1. **Dark Slate Canvas Baseline**:
   - `viewBackgroundColor: "#090d16"` (or deep dark `#121212`).
   - Cards/Containers: `backgroundColor: "#111827"` or `"#1e293b"` with subtle, controlled border strokes (`#334155` or `#475569`).
2. **Strict Color Palette Discipline (Max 4 Semantic Colors)**:
   - 🔴 **Danger / Problem / Shock**: Stroke `#ef4444`, Fill `#450a0a` (subtle dark tint).
   - 🟠 **Warning / Mechanism / Heat**: Stroke `#f97316`, Fill `#431407`.
   - 🔵 **Engineering / Technology / SOTA**: Stroke `#06b6d4` / `#38bdf8`, Fill `#083344`.
   - 🟢 **Success / Triumph / CTA**: Stroke `#10b981`, Fill `#064e3b`.
   - ⚪ **Typography**: Primary `#f8fafc`, Secondary/Labels `#94a3b8`, Highlights `#fbbf24`.
3. **Generous Human-Scale Typography Hierarchy**:
   - Canvas / Banner Header: **28–36px** (bold / prominent).
   - Frame / Card Title Badges: **20–24px**.
   - Section Subtitles / Badges: **16–18px**.
   - Body Text / Bullet Points: **14–16px** (strictly NEVER drop below 14px for body copy).
   - Font Family: **`fontFamily: 5` (Excalifont)** for native Cyrillic handwriting, or **`2` (Helvetica)** for clean UI boxes.

---

## 2. Viral Video Storyboard Layout (TikTok / Reels / Shorts)

### Canvas Geometry
- **Aspect Ratio per Card**: 9:16 vertical proportion (e.g. `width: 440–480px`, `height: 780–840px`).
- **Gutter Spacing**: `50–60px` between cards.
- **Orientation**: Horizontal progression (5 scenes side-by-side along the X-axis) with connecting transition arrows.

### The 5-Frame Viral Structure
1. **Кадр 1: Шок-Хук (0:00 - 0:04)**:
   - Visual: High-contrast shocking metric (e.g., laser pyrometer reading `+62.4 °C` into smoke chamber).
   - Core Message: Disprove conventional wisdom, break complacency ("Ти не коптиш, ти вариш!").
2. **Кадр 2: Фізика / Розтин помилки (0:04 - 0:12)**:
   - Visual: Cross-section diagram, temperature differential ($\Delta T$), dew point equation.
   - Core Message: Why conventional gear fails (acidic condensate, protein coagulation).
3. **Кадр 3: Хаос у масштабі / Тепловізор (0:12 - 0:22)**:
   - Visual: Chamber cutaway (e.g. 500 L), thermal stratification (hot upper layer vs cold floor).
   - Core Message: Irreversible product damage, financial and quality loss.
4. **Кадр 4: Інженерне рішення / Механізм Reburn (0:22 - 0:34)**:
   - Visual: Flow schematic showing cooling loops, tar separator jar, isothermal blue smoke (`+23 °C`).
   - Core Message: The proprietary mechanism that eliminates the root physical flaw.
5. **Кадр 5: Тріумф & Заклик до дії (0:34 - 0:45)**:
   - Visual: 4K macro product payoff (translucent, firm texture) + interactive CTA button.
   - Core Message: Lead magnet trigger (e.g., "Пиши 'СХЕМА' у коментарях").

### Frame Component Specification (Inside each 9:16 Card)
- **Top Header Badge**: Scene number, timestamp interval, and psychological role.
- **Visual Centerpiece Mockup**: Large schematic or illustration (min. 220–260px height).
- **Camera Movement & Lighting Box**: Shot type, focal length, color grading cues.
- **Dynamic On-Screen Text (Kinetic Typography)**: Exact text animations displayed to viewers.
- **Voiceover Script Box**: Word-for-word spoken narration in natural language.
- **SFX & Audio Design Box**: Concrete foley and music cues (whoosh, alarm beep, sizzle, bass drop).

---

## 3. Executive Comparative Matrix (Bottom Anchor)
Beneath the 5 storyboard cards, author a full-width comparative table or dual-column matrix:
- **Left Column**: The Broken / Conventional / Competitor Method (dark red palette `#ef4444`).
- **Right Column**: The Engineered SOTA Method (dark cyan/emerald palette `#10b981`).
- Provide concrete side-by-side metric rows: temperatures, humidity, yield loss, tar content, texture.
- This serves as the high-retention "Save/Screenshot this" artifact for the viewer.
