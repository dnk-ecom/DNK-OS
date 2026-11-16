---
name: chrome-extension-engineering
description: "Use when building Chrome Manifest V3 extensions & panels."
version: 1.0.0
author: Gerych Prime
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [chrome, extensions, manifest-v3, service-worker, sidepanel, web-speech, webhooks]
---

# Chrome Extension Engineering (Manifest V3)

Comprehensive engineering patterns, lifecycle management, and architectural invariants for developing high-performance Google Chrome extensions under Manifest V3.

## When to Use
- Building or refactoring Chrome, Brave, Arc, or Edge browser extensions using Manifest V3.
- Implementing persistent browser sidebars via the `chrome.sidePanel` API.
- Designing background task processing using ephemeral Service Workers and `chrome.alarms`.
- Integrating audio recording and voice transcription in extension popups via Web Speech API (`webkitSpeechRecognition`).
- Implementing secure outward webhook synchronization (Telegram Bot API, local LLM/Agent REST endpoints, Markdown exporters).

**Don't use for:**
- Standard web single-page apps (SPA) running purely on public HTTP origins without extension APIs.
- Legacy Manifest V2 extensions (MV2 background pages and persistent script engines are deprecated).

## Architecture & Directory Topology
A production-grade Manifest V3 extension must adhere to strict modular isolation:

```text
extension-root/
├── manifest.json              # Canonical MV3 manifest & permission boundaries
├── _locales/                  # i18n messages
│   ├── en/messages.json
│   └── uk/messages.json
├── icons/                     # 16, 32, 48, 128px PNG icon assets
├── background.js              # Ephemeral service worker (alarms, commands, sync)
├── popup/                     # Quick action popover (opened from browser bar)
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── sidepanel/                 # Persistent workspace panel (sidePanel API)
│   ├── sidepanel.html
│   ├── sidepanel.css
│   └── sidepanel.js
├── options/                   # Settings & credentials configuration page
│   ├── options.html
│   ├── options.css
│   └── options.js
└── README.md                  # Installation and keyboard shortcuts guide
```

## Core Invariants & Engineering Rules

### 1. Ephemeral Service Worker Lifecycle (Zero In-Memory State)
- Manifest V3 replaces persistent background pages with **Service Workers**.
- Service Workers are routinely terminated by the browser after ~30 seconds of inactivity.
- **Rule**: NEVER store session state, active timers, or item queues in global JavaScript variables (`let state = {...}`).
- **State SSOT**: Always persist state in `chrome.storage.local`.
- **Timers**: NEVER use long `setInterval` or `setTimeout` in `background.js` (they will be killed when the worker goes dormant). Use `chrome.alarms.create(name, { periodInMinutes: ... })` instead.

### 2. Strict Content Security Policy (CSP) Compliance
- MV3 enforces strict CSP: `script-src 'self'`.
- **Rule**: Absolutely NO inline script blocks (`<script>doSomething()</script>`).
- **Rule**: Absolutely NO inline HTML event attributes (`onclick="..."`, `onchange="..."`, `onsubmit="..."`).
- **Rule**: Absolutely NO `eval()`, `new Function()`, or dynamic remote code injection.
- All event listeners must be bound in external JS files via `element.addEventListener('click', handler)`.

### 3. Asynchronous Messaging Contract
- When sending messages from UI pages (`popup.js`, `sidepanel.js`) to `background.js`:
  ```javascript
  chrome.runtime.sendMessage({ action: 'ACTION_NAME', payload: data }, (response) => {
    if (chrome.runtime.lastError) {
      console.warn('Runtime error:', chrome.runtime.lastError.message);
      return;
    }
    // Handle response
  });
  ```
- In `background.js`, when handling messages asynchronously (e.g. performing a `fetch`), the listener **MUST return `true`** to keep the message channel open:
  ```javascript
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'ASYNC_OP') {
      executeAsync(request.payload).then((res) => sendResponse(res));
      return true; // Crucial: signals asynchronous response
    }
  });
  ```

### 4. Side Panel API & Global Behavior
- Enable opening the side panel on action click:
  ```javascript
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false })
    .catch((err) => console.error(err));
  ```
- To toggle the side panel programmatically in response to a keyboard command:
  ```javascript
  chrome.commands.onCommand.addListener(async (command) => {
    if (command === 'toggle_vibe_sidepanel') {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab?.windowId) {
        chrome.sidePanel.open({ windowId: tab.windowId });
      }
    }
  });
  ```

### 5. Web Speech API Audio Capture
- Extension popup pages possess window context and can utilize `window.webkitSpeechRecognition` or `window.SpeechRecognition`.
- Initialize recognition with proper fallback and language selection:
  ```javascript
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = 'uk-UA'; // or 'en-US'
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  ```
- Ensure visual recording indicators (pulse animations, status text) toggle smoothly on `onstart`, `onend`, and `onerror`.

### 6. Chrome Built-in AI & On-Device Prompt API
- Chrome 128+ provides local Gemini Nano via `window.ai.languageModel` in windowed contexts (Side Panel, Popup, Offscreen).
- **Rule**: Window context is mandatory (`window.ai` does NOT exist in Service Workers). If background scripts need AI, route requests to an open Side Panel or create a dedicated Offscreen Document.
- **Rule**: Always verify `(await window.ai.languageModel.capabilities()).available === 'readily'` before prompting; provide a Tier 1 deterministic regex/rule fallback.
- See `references/chrome_builtin_ai_and_bookmark_safety.md` for session creation, streaming, and error handling.

### 7. Transactional Bookmark & Tab Mutation Safety
- High-volume data extensions (tabs, bookmarks, session managers) must protect against data loss (a primary cause of 1-star reviews for tools like OneTab and Session Buddy).
- **Rule**: NEVER mutate bookmarks or session tabs without taking an automatic timestamped snapshot in `chrome.storage.local`.
- **Rule**: Never reorganize or delete bookmarks blindly — enforce a Visual Diff & Review step before writing mutations to `chrome.bookmarks`.
- See `references/chrome_builtin_ai_and_bookmark_safety.md` for snapshot rollback patterns.

### 8. Shopify Polaris / Helix Dual-Theme & Options Architecture
- Extensions adopting modern design standards (e.g. DNK Notebook+) must support seamless light/dark theme switching.
- **Tokens**: Light (Shopify Polaris Snow Canvas, `#f1f2f4`, `#ffffff`, `#008060`) and Dark (Helix Matte Obsidian, `#0d0e10`, `#16181b`, `#30cd90`).
- **Reactive Synchronization**: Listen to `chrome.storage.onChanged` in `popup.js`, `sidepanel.js`, and `options.js` so theme toggles propagate across all open extension contexts in real time.
- **Options & Modal Patterns**: Use dedicated tab navigation for settings categories (General, Integrations, Vault/Storage, About) and backdrop blur modals (`backdrop-filter: blur(12px)`) with collapsible `<details>` accordions for in-app Changelogs.
- See `references/chrome_extension_polaris_dual_theme.md` for complete CSS variable declarations and template components.

## Quick Reference & Commands
Validate and test an extension before distribution:

```bash
# 1. Check JSON syntax across manifest and locale catalogs
python3 -c 'import json, glob; [json.load(open(f)) for f in glob.glob("**/*.json", recursive=True)]'

# 2. Check JavaScript syntax using Node.js
node -c background.js popup/popup.js sidepanel/sidepanel.js options/options.js

# 3. Load into browser:
# Navigate to chrome://extensions/ -> Toggle "Developer mode" -> "Load unpacked"
```

## Pitfalls & Edge Cases
1. **Unregistered Alarms**: If `chrome.alarms.onAlarm` listener is not registered at the root of `background.js` during initial script evaluation, alarms waking up the service worker will be silently missed.
2. **Missing Storage Defaults**: Always handle `chrome.storage.local.get` returning an empty object `{}` when keys are not yet set.
3. **CORS on Webhook Endpoints**: MV3 Service Workers bypass standard web CORS when making `fetch` calls to external URLs, provided the URL pattern is declared in `host_permissions` (e.g. `https://api.telegram.org/*`, `http://127.0.0.1:*`).
4. **Windowless Contexts**: In `background.js`, `window`, `document`, and `alert()` do not exist. Use `chrome.notifications.create` for user-visible notifications.
5. **Built-in AI in Service Worker**: Calling `window.ai` in `background.js` throws `ReferenceError`. Delegate inference to `sidepanel.js` or an offscreen document.
6. **Fragile `localStorage`**: Avoid using raw `localStorage` in content scripts or popups for critical user links; OS cleanup utilities (CleanMyMac) frequently purge browser cache and unindexed storage. Always use `chrome.storage.local`.
7. **Cross-Context Theme Desync**: Toggling light/dark theme in `options.html` or `popup.html` will leave open `sidepanel.html` out-of-sync unless `chrome.storage.onChanged` is explicitly handled to update `data-theme`.
8. **Icon Micro-Scale Anti-aliasing, Cranial Centering & Dual-Track Sync**: Extension icons at 16×16 and 32×32 px anti-alias thin lines (<3px in a 128px viewBox) and external corner badges into an illegible blur. Maximize the primary silhouette (65–75% area), punch secondary monograms ("AI") directly through the silhouette using SVG masks (`<mask id="cutoutMask">`) centered optically in the cranial vault (cerebrum) rather than the lower bounding-box center. Synchronize both raster PNGs (`manifest.json`) and inline vector catalogs (`common/icons.js`) across Popup, Sidepanel, and Options headers, validating with headless Playwright and `vision_analyze` (see `references/chrome_extension_iconography_and_branding.md`).
9. **Iframe Security Headers (CSP & X-Frame-Options)**: In multi-screen previewers and responsive canvases loading external targets into `<iframe>`, browsers reject embedding via `X-Frame-Options` and CSP `frame-ancestors`. Do not attempt legacy `webRequestBlocking` in MV3; use `chrome.declarativeNetRequest.updateSessionRules` with `RuleActionType.MODIFY_HEADERS` to remove `x-frame-options` and `content-security-policy` on `sub_frame` requests scoped strictly to the viewer's `tabId`. For direct CRX3 package harvesting and unpacking from Chrome Web Store without scrapers, see `references/crx_teardown_and_declarative_net_request_iframe_rules.md`.

## Verification Checklist
- [ ] `manifest.json` conforms to Manifest V3 schema with valid permissions.
- [ ] Background service worker registers all alarm and message listeners synchronously at top-level.
- [ ] Zero inline event attributes in HTML (`grep -rn "onclick=" .` returns 0 hits).
- [ ] Web Speech API cleanly handles unsupported browsers or microphone permission denials.
- [ ] Sensitive API tokens are kept strictly in `chrome.storage.local` and never hardcoded in source.
- [ ] Dual-theme tokens (`data-theme="light"` / `data-theme="dark"`) reactive across popup, sidepanel, and options via `chrome.storage.onChanged`.
- [ ] Pure SVG Vector icons via `common/icons.js` (`currentColor` inheritance, zero platform-dependent emojis in UI).
- [ ] Icon assets generated at 16, 32, 48, 128 px from master vector `icons/icon.svg` via headless Playwright script.