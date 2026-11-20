---
name: chrome-extension-standard
description: "Production standard and governance rules for developing, auditing, testing, and publishing Chrome Extensions (Manifest V3) based on Google Chrome Developers official AI guidance, CHROMEWEBSTORE.md compliance, and DevTools MCP automation."
metadata:
  tags: "Chrome Extension, Manifest V3, Chrome Web Store, AI Agent, DevTools MCP"
  category: "browser-extensions"
---

# 🚀 Chrome Extension Development & CWS Standard (Google AI Guidelines)

> **Source**: [Build extensions with coding agents (developer.chrome.com)](https://developer.chrome.com/docs/extensions/ai/build-with-ai) & [DNK OS Extension Protocol](../../MY_LIFE_WORK/DNK_Vibe/DNK_Chrome_Plugins/).  
> **Mandatory Policy**: This skill applies to all agent sessions creating, refactoring, or preparing Chrome extensions for publication.

---

## 🔒 1. Mandatory Invariant: CHROMEWEBSTORE.md

Whenever an agent creates, modifies, or adds permissions to a Chrome extension (`manifest.json`), the agent **MUST** maintain a dedicated `CHROMEWEBSTORE.md` file in the extension repository root.

### File Structure Requirements:
1. **Metadata**: Extension Name, Short Name, Version, Primary/Secondary Category.
2. **Single Purpose Statement**: Explicitly defined single-purpose value proposition per Google CWS policy (`CWS-POL-001`).
3. **Permissions Justification Matrix**: Granular technical reason and user benefit for **every** permission declared in `manifest.json`:
   - `storage`: Local preferences, offline cache (no remote sync).
   - `activeTab`: Explicit user-triggered action on current page.
   - `tabs`: Window discovery, duplicate tab prevention.
   - `cookies`: Target-domain session auth (e.g. Google profile matching).
   - `debugger`: Automated canvas/studio interaction (requires high-risk audit explanation).
   - `scripting`: Dynamic content extraction parsers.
4. **Data Safety & Privacy**: Confirmation of local-first processing, zero external data selling, and zero remote code execution (`script-src 'self'`).
5. **Reviewer Step-by-Step Testing Guide**: Clear instructions for the Google Web Store review team to test every declared permission.

---

## 🏷️ 2. Mandatory Invariant: Canonical SemVer & Changelog Standard (SSOT)

> **Golden Benchmark**: `DNK Notebook+` (`0.1.0` ➔ `0.1.1` ➔ ... ➔ `0.1.6`).  
> **Reference Document**: `docs/guides/EXTENSION_VERSIONING_AND_CHANGELOG_STANDARD.md`.

Whenever an agent bumps a version or modifies an extension, the agent **MUST** follow strict SemVer and simultaneously update all 5 touchpoints:
1. **No Version Skipping**: Incremental PATCH progression (`0.1.0` ➔ `0.1.1` ➔ ... ➔ `0.1.6`). Never skip numbers (e.g. `0.1.0` ➔ `0.5.0` is strictly forbidden).
2. **`manifest.json`**: Declare BOTH `"version": "0.1.x"` and `"version_name": "0.1.x (YYYY-MM-DD)"`.
3. **Popup Header (`popup/popup.html`)**: Clean static version badge `<span class="version-badge">v0.1.x · DD.MM.YYYY</span>`. Zero dynamic clocks inside the version badge.
4. **App Settings / About Page (`app/app.html`)**:
   - Badge `<span class="settings-card-badge">v0.1.x Active SSOT</span>`.
   - Text `<span class="about-version">Версія: <strong>v0.1.x</strong> · Оновлено: <strong>DD.MM.YYYY</strong></span>`.
   - **Changelog Modal (`#changelog-modal`)**:
     - Modern W3C `inert` attribute when hidden (`<div id="changelog-modal" class="changelog-modal-backdrop hidden" inert>`).
     - Native HTML5 `<details class="changelog-row" name="changelog-accordion" open>` for latest release with `.cl-badge-latest`, `.cl-date`, `.cl-tag` ("Поточна" / "LATEST").
     - Semantic sections: `Додано:` (`.icon-added`), `Покращено:` (`.icon-improved`), `Виправлено:` (`.icon-fixed`).
     - All previous versions preserved in sequential collapsed `<details>` rows.
5. **Documentation & CWS Metadata (`CHROMEWEBSTORE.md`, `CHANGELOG.md`, `README.md`)**:
   - `CHROMEWEBSTORE.md` metadata table: `| **Version** | 0.1.x | 0.1.x |`.
   - MRH headers in all files: `version: "0.1.x"`, `updated_at: "YYYY-MM-DD"`.
   - `CHANGELOG.md` entry: `## [0.1.x] — YYYY-MM-DD` per Keep a Changelog.

---

## 🛠️ 3. DevTools MCP Automation Setup

To enable autonomous extension testing, installation, and inspection directly inside agent sessions:

```json
{
  "mcpServers": {
    "chrome-devtools-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--categoryExtensions",
        "--autoConnect"
      ]
    }
  }
}
```

### Key Flags:
* **`--categoryExtensions`**: Unlocks extension management tools (`install_extension`, `reload_extension`, `inspect_surface` for popup/sidepanel/serviceworker).
* **`--autoConnect`**: Connects to the developer's active Chrome profile via `chrome://inspect/#remote-debugging`. Preserves Google login cookies and user state without requiring mock credentials.

---

## 🧠 4. Chrome Built-in AI (Prompt API / Gemini Nano) Guidelines

When integrating AI features directly into extensions:
1. **Local-First Zero Cost**: Use `ai.languageModel` for fast, private, offline summarization and rewriting.
2. **Capabilities Gate**: Never assume model presence. Always check:
   ```javascript
   const capabilities = await ai.languageModel.capabilities();
   if (capabilities.available === 'readily') {
     // use Gemini Nano
   } else if (capabilities.available === 'after-download') {
     // monitor download progress
   } else {
     // fallback to cloud API or direct passthrough
   }
   ```
3. **Progressive Enhancement**: Built-in AI MUST be an optional enhancement, never a hard single point of failure.

---

## 🛡️ 5. Quality & Pre-Commit Checklist

Before opening a PR or submitting to Chrome Web Store:
- [ ] `manifest.json` uses Manifest V3. No `manifest_version: 2`.
- [ ] No remote scripts loaded via CDN (`eval`, external `.js` forbidden).
- [ ] All permissions in `manifest.json` are documented in `CHROMEWEBSTORE.md`.
- [ ] Dual-Theme verified (Dark and Light modes tested).
- [ ] Automated headless test suite passes (`node scripts/verify_*.js` exits with code 0).
- [ ] Dangerous permissions (`debugger`, `<all_urls>`) isolated or minimized.
