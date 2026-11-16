# --- DNK-MRH-HEADER ---
# mrh_id: "chrome_extension_polaris_dual_theme.md"
# purpose: "Shopify Polaris 2.0 & Helix Dual-Theme Specification for Chrome Extensions."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-01"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Shopify Polaris 2.0 & Helix Dual-Theme Design Pattern for Chrome Extensions

This specification defines the exact design tokens, CSS variables, and layout patterns for building extension UIs matching the **DNK Notebook+** and **Shopify Polaris 2.0** visual language.

---

## 1. CSS Custom Properties & Color Tokens

```css
:root {
  /* Common Geometry */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Light Theme: Shopify Polaris Snow Canvas */
:root[data-theme="light"] {
  --bg-app: #f1f2f4;
  --bg-surface: #ffffff;
  --bg-surface-secondary: #f6f6f7;
  --bg-surface-hover: #edeeef;
  
  --border-subtle: #e3e5e8;
  --border-base: #c9cccf;
  --border-strong: #8c9196;
  
  --text-primary: #202223;
  --text-secondary: #6d7175;
  --text-subdued: #8c9196;
  
  --color-accent: #008060;        /* Shopify Emerald */
  --color-accent-hover: #006e52;
  --color-accent-subtle: #e3f1df;
  
  --grid-dot: rgba(0, 0, 0, 0.05);
  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.05), 0 0 0 1px var(--border-subtle);
  --shadow-modal: 0 20px 40px rgba(0, 0, 0, 0.12), 0 0 0 1px var(--border-subtle);
}

/* Dark Theme: Helix Matte Obsidian */
:root[data-theme="dark"] {
  --bg-app: #0d0e10;
  --bg-surface: #16181b;
  --bg-surface-secondary: #1d2024;
  --bg-surface-hover: #25282d;
  
  --border-subtle: #26292e;
  --border-base: #33383f;
  --border-strong: #4a515a;
  
  --text-primary: #f0f2f5;
  --text-secondary: #9da3ae;
  --text-subdued: #636b78;
  
  --color-accent: #30cd90;        /* Vivid Neon Emerald */
  --color-accent-hover: #26af7a;
  --color-accent-subtle: rgba(48, 205, 144, 0.12);
  
  --grid-dot: rgba(255, 255, 255, 0.04);
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.4), 0 0 0 1px var(--border-subtle);
  --shadow-modal: 0 24px 48px rgba(0, 0, 0, 0.7), 0 0 0 1px var(--border-subtle);
}
```

---

## 2. Micro-Dot Matrix Canvas

Apply subtle tactical dot-grid patterning to page backgrounds:

```css
body {
  background-color: var(--bg-app);
  background-image: radial-gradient(var(--grid-dot) 1px, transparent 1px);
  background-size: 16px 16px;
  color: var(--text-primary);
  font-family: var(--font-family);
  margin: 0;
  padding: 0;
}
```

---

## 3. Reactive Theme Synchronization

To keep `popup`, `sidepanel`, and `options` synchronized in real time when the user clicks the theme toggle button:

```javascript
// In popup.js, sidepanel.js, options.js
async function initTheme() {
  const res = await chrome.storage.local.get(['theme']);
  applyTheme(res.theme || 'dark');
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) {
    btn.innerHTML = theme === 'dark' ? SUN_SVG : MOON_SVG;
    btn.title = theme === 'dark' ? 'Перемкнути на світлу тему' : 'Перемкнути на темну тему';
  }
}

// React instantly to changes made across tabs or panels
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.theme) {
    applyTheme(changes.theme.newValue);
  }
});

// Toggle handler
document.getElementById('theme-toggle-btn')?.addEventListener('click', async () => {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  await chrome.storage.local.set({ theme: next });
});
```

---

## 4. Modal Dialogs with Blur Backdrop

For release logs, quick notes, and confirmation prompts:

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(12px) saturate(140%);
  -webkit-backdrop-filter: blur(12px) saturate(140%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-fast);
}

.modal-backdrop.is-open {
  opacity: 1;
  pointer-events: auto;
}

.modal-container {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  width: 90%;
  max-width: 640px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

---

## 5. Pure SVG Vector Icon Library (`common/icons.js`) & Anti-Emoji Invariant

Unicode emojis (⚡, 💡, 🤖, ⏱️, ✈️, 🔍, 🎙️) produce severe cross-platform rendering inconsistencies (macOS Apple Color Emoji vs Windows Segoe UI Emoji vs Linux Noto), misalign line heights, and do not inherit CSS `currentColor`.

### Central Icon Factory (`common/icons.js`)
All UI icons must be defined in a reusable `window.DNK_ICONS` catalog returning clean SVG strings:

```javascript
// common/icons.js
(function () {
  function svg(content, size = 16, className = '') {
    return `<svg width="${size}" height="${size}" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="dnk-icon ${className}">${content}</svg>`;
  }

  window.DNK_ICONS = {
    task: (s = 16, c = '') => svg('<polygon points="11 2 4 11 10 11 9 18 16 9 10 9 11 2" />', s, c),
    idea: (s = 16, c = '') => svg('<path d="M10 2a6 6 0 0 0-6 6c0 2.2 1.2 4.1 3 5.1V15a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-1.9c1.8-1 3-2.9 3-5.1a6 6 0 0 0-6-6z" fill="none"/><line x1="8" y1="18" x2="12" y2="18"/>', s, c),
    search: (s = 16, c = '') => svg('<circle cx="8.5" cy="8.5" r="5" stroke-width="1.8"/><line x1="12.5" y1="12.5" x2="17.5" y2="17.5" stroke-width="2"/>', s, c),
    check: (s = 16, c = '') => svg('<polyline points="4 10 8 14 16 6" stroke-width="2.2" />', s, c),
    trash: (s = 16, c = '') => svg('<path d="M3 5h14"/><path d="M8 5V3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2"/><path d="M15 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5"/>', s, c)
  };
})();
```

### Invariant Rules
1. **Zero Raw Emojis in DOM**: Buttons, badges, empty states, and toast notifications use `DNK_ICONS.<name>()`.
2. **`currentColor` Inheritance**: SVG strokes/fills must adapt automatically to the active theme's `--text-primary` or `--color-accent`.

---

## 6. Master Vector Icon (`icons/icon.svg`) & Headless Rasterizer

Keep a single master vector SVG (`icons/icon.svg`) with standard dimensions (e.g. 128x128 with squircle background).

Generate standard Chrome Web Store PNG sizes (16, 32, 48, 128) deterministically using Playwright in headless mode (`scripts/build_extension_icons.js`):

```javascript
// scripts/build_extension_icons.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SIZES = [16, 32, 48, 128];
const SVG_PATH = path.resolve(__dirname, '../icons/icon.svg');
const OUT_DIR = path.resolve(__dirname, '../icons');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const svgContent = fs.readFileSync(SVG_PATH, 'utf8');

  for (const size of SIZES) {
    const html = `<!DOCTYPE html><html><body style="margin:0;padding:0;background:transparent;display:flex;align-items:center;justify-content:center;width:${size}px;height:${size}px;">
      <div style="width:${size}px;height:${size}px;">${svgContent}</div>
    </body></html>`;
    await page.setContent(html);
    await page.setViewportSize({ width: size, height: size });
    const outPath = path.join(OUT_DIR, `icon${size}.png`);
    await page.screenshot({ path: outPath, omitBackground: true });
    console.log(`Generated: ${outPath} (${size}x${size})`);
  }
  await browser.close();
})();
```

```
