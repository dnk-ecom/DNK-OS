# Obsidian Excalidraw Font Family & Compression Standards

## 1. Font Family Mapping & Vault Standards

Obsidian Excalidraw plugin (`zsviczian/obsidian-excalidraw-plugin`) maps font family integers as follows:

| Value | Font Name | Intended Usage | Vault Invariant |
| :--- | :--- | :--- | :--- |
| **`5`** | **Excalifont** | Modern hand-drawn handwriting font | **MANDATORY DEFAULT** for all DNK OS vault diagrams. Matches user reference notes (`Нотатки структури DNK OS 090926.excalidraw.md`). Full native Cyrillic support! |
| **`1`** | **Virgil** | Legacy Excalidraw hand-drawn font | Legacy only. **Pitfall**: lacks Cyrillic glyphs; in Obsidian, Ukrainian/Cyrillic characters fall back to mismatched system fonts. Do NOT use for vault diagrams. |
| **`2`** | **Helvetica / Normal** | Sans-serif clean font | UI wireframes, formal corporate cards. |
| **`3`** | **Cascadia Code** | Monospace font | Code snippets, JSON structures, Task Forest IDs (`TF-DSS-*`). |
| **`4`** | **Local Font** | Custom user-configured font | Special typography. |

### Configuration Requirements
When generating Excalidraw raw JSON or `.excalidraw.md` files:
1. Every text element MUST have `"fontFamily": 5` (unless specifically monospace code, then `3`, or clean UI cards, then `2`).
2. `appState.currentItemFontFamily` MUST be set to `5` (or `2` for clean geometric cards).

---

## 2. In-Memory Tab Caching & Live Reload Pitfall

### The Problem
The Obsidian Excalidraw plugin caches the active canvas view in memory:
```javascript
if (this.lastLoadedFile === this.file) return;
```
If an agent or script updates `.excalidraw` or `.excalidraw.md` on disk while Obsidian has that file open in a tab, **Obsidian will NOT reload the drawing automatically**. The user will still see the old diagram and assume the changes failed.

### Resolution Steps
1. **User Action**: Close the open diagram tab (`×`) and reopen it from the file tree, or press `Cmd + R` in Obsidian, or select "Reload without saving" from the Excalidraw hamburger menu.
2. **Dual File Invariant**: When both `.excalidraw` (standalone JSON) and `.excalidraw.md` (Markdown wrapper) exist, always update **both** synchronously so regardless of which file Obsidian opens, the latest scene is rendered.

---

## 3. Language & Domain Vocabulary Invariant

For Maxim and the DNK OS ecosystem:
- **Ukrainian Language SSOT**: All canvas node labels, zone headings, and cards must be in clear, structured Ukrainian (🇺🇦) using official DNK OS concepts (Task Forest, Graphify, Visual Prior, Tinker Blocks).
- Avoid raw English boilerplate placeholders.

---

## 4. Drawing Storage & Compression (`compressed-json`)

Obsidian Excalidraw stores drawing data using LZString Base64 compression by default.

### Python Compression Recipe
```python
import json
import lzstring

def compress_excalidraw(data: dict) -> str:
    raw_json_str = json.dumps(data, ensure_ascii=False)
    lz = lzstring.LZString()
    compressed_base64 = lz.compressToBase64(raw_json_str)
    return f"```compressed-json\n{compressed_base64}\n```"
```

### Full-Text Search & Obsidian Graph Integration
To ensure Obsidian Quick Switcher, Omnisearch, and Graph View can index text elements inside the compressed drawing:
1. Output all text elements above the drawing block under `## Text Elements`.
2. Format: `{clean_text} ^{element_id}`.
3. Output bidirectional links under `## Element Links`: `^{element_id}: [[Target Note]]`.

---

## 5. UI Cards & Mixed Typography Standards (Ukrainian Cyrillic + English Terms)

### Font Fallback & Mismatch Pitfall
When UI cards, slides, or canvas blocks contain mixed text (Ukrainian sentences containing English technical terms like `Google Flow`, `API`, `DNK OS`), a severe visual break occurs if the selected font lacks Cyrillic glyphs:
- **Root Cause**: Many popular Google display fonts (e.g., `Plus Jakarta Sans`) contain **0 Cyrillic codepoints** in their official releases.
- **Visual Glitch**: Applying Bold (`**text**`) or Italic (`*text*`) causes English words to render in the custom bold display font, while Ukrainian characters fall back to a generic OS font (Arial/Helvetica) with differing baseline, x-height, stroke weight, and kerning.

### The Standard Typography Pair for DNK OS Cards & Boards
To guarantee 100% monolithic styling with identical metrics across Latin and Ukrainian Cyrillic:

| Element Role | Font Family | Recommended Weights | Rationale & Glyph Coverage |
| :--- | :--- | :--- | :--- |
| **Headings, Badges, Numeric Indicators** (e.g. `АНТИПАТЕРНИ:`, badge `1`) | **`Manrope`** | SemiBold 600, Bold 700, ExtraBold 800 | Geometric, modern grotesque matching Plus Jakarta Sans aesthetics with **104 native Ukrainian Cyrillic glyphs** (І, і, Ї, ї, Є, є, Ґ, ґ). |
| **Body Text, Mixed Inline Terms, Quotes** | **`Inter`** | Regular 400, Bold 700, Italic (Variable) | Industry SSOT for UI. Identical optical metrics for Latin & Cyrillic. Bold (`Cmd+B`), Italic (`Cmd+I`), and Underline work identically on both languages without fallback jumps. |

### Font Installation & Machine Verification
System fonts should be placed in `~/Library/Fonts/` on macOS:
- `~/Library/Fonts/Manrope[wght].ttf`
- `~/Library/Fonts/Inter[opsz,wght].ttf`
- `~/Library/Fonts/Inter-Italic[opsz,wght].ttf`

### Web & App CSS Fallback Stack & Variable Font Hygiene
When embedding this standard into web applications, design canvases, or local dev tools (e.g. Open Design, Canvas editors):
- **Never rely on pure system font names alone** or non-Cyrillic web fonts (`Albert Sans`, `Plus Jakarta Sans`, or CJK fonts like `PingFang SC`, `Microsoft YaHei`) as primary sans fonts. They cause optical weight and kerning mismatch between Ukrainian and English words.
- **SSOT Font-Family Token Definition**:
  ```css
  --font-heading: "Manrope", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --serif: "Manrope", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --mono: "Cascadia Code", "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  ```
- **Local Font Asset Binding (`@font-face`)**:
  Ensure local static or variable assets (`Inter.ttf`, `Inter-Italic.ttf`, `InterVariable.woff2`) are declared with full weight range (`font-weight: 100 900; font-style: normal` and `italic`) and loaded with `font-display: swap;`.

**Automated Cyrillic Audit Snippet**:
```python
from fontTools.ttLib import TTFont

def verify_ukrainian_support(font_path: str) -> bool:
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    ua_specific = [0x0406, 0x0456, 0x0407, 0x0457, 0x0404, 0x0454, 0x0490, 0x0491] # І, і, Ї, ї, Є, є, Ґ, ґ
    return all(cp in cmap for cp in ua_specific)
```
