# 🛍️ Shopify CLI Theme Access & JSON Template Selective Sync Playbook

## Overview
When syncing, migrating, or modifying JSON templates (`templates/product*.json`, `templates/index.json`) between themes on live Shopify stores using **Shopify CLI** and **Theme Access Passwords** (`shptka_...`), follow this deterministic protocol.

---

## 1. Store Handle Resolution (Internal vs Custom Domain)
Theme Access App passwords (`shptka_...`) are bound strictly to the store's internal `.myshopify.com` domain or Admin handle, **not** to public custom domains (`domain.com`).

- **Symptom:** `shopify theme list --store customdomain.com --password shptka_...` fails with `Could not resolve store` or `Unauthorized (401)`.
- **Resolution:**
  1. Inspect the Shopify Admin URL: `https://admin.shopify.com/store/<store_handle>/...`
  2. The canonical target store is `<store_handle>.myshopify.com` (e.g. `6c1e24-9d.myshopify.com`).

---

## 2. Shopify CLI Non-Destructive Theme Operations

### A. Listing Themes
```bash
/opt/homebrew/bin/shopify theme list \
  --store <handle>.myshopify.com \
  --password <theme_access_token>
```

### B. Pulling Specific Templates (`--only` + `--nodelete`)
To avoid overwriting local files or pulling the entire multi-megabyte theme:
```bash
/opt/homebrew/bin/shopify theme pull \
  --path "./theme_dir" \
  --store <handle>.myshopify.com \
  --password <theme_access_token> \
  --theme <theme_id> \
  --only "templates/product*.json" \
  --nodelete
```

### C. Pushing Modified Single Templates
```bash
/opt/homebrew/bin/shopify theme push \
  --path "./theme_dir" \
  --store <handle>.myshopify.com \
  --password <theme_access_token> \
  --theme <theme_id> \
  --only "templates/product.target-template.json" \
  --nodelete
```

---

## 3. Robust JSON Template Parsing (Header Comment Preservation)

Shopify JSON templates frequently contain top-level banner comments:
```json
/*
 * ------------------------------------------------------------
 * IMPORTANT: The contents of this file are auto-generated.
 * ------------------------------------------------------------
 */
{
  "sections": { ... }
}
```

### Pitfall & Solution:
- **Pitfall:** `json.loads(text)` raises `JSONDecodeError` on comments.
- **Pitfall:** Running naive regex removal `re.sub(r'//.*', '', text)` will corrupt internal resource URLs such as `"shopify://apps/app-name/blocks/..."`.
- **Safe Parsing Technique:**
```python
import json

def load_shopify_template(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    # Locate the first opening brace
    brace_idx = raw_text.find("{")
    if brace_idx == -1:
        raise ValueError("Invalid JSON template: no opening brace found")
    
    header_comment = raw_text[:brace_idx]
    json_body = json.loads(raw_text[brace_idx:])
    return header_comment, json_body

def save_shopify_template(file_path: str, header_comment: str, json_body: dict):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(header_comment + json.dumps(json_body, indent=2, ensure_ascii=False))
```

---

## 4. Block Schema Verification Before Mutation
Before updating block settings (such as `direction`, `alignment`, `margin_top`, `disabled`):
1. Locate block schemas in `blocks/<block-name>.liquid` or `sections/<section-name>.liquid`.
2. Check enum options (e.g. `direction` might be `["horizontal", "vertical"]` rather than `1` or `column`).
3. To disable a block cleanly in Shopify OS 2.0 JSON, set `"disabled": true` at the block definition level in `blocks` dictionary.
4. **Range Step Divisibility Rule**: Shopify strictly validates numeric `range` settings on push (`Setting 'margin_top' must be a step in the range`). If a schema defines `min: 0, max: 45, step: 3`, passing `20` or `25` fails remotely. The value MUST be an exact multiple: `value = round(target / step) * step` (e.g. 15, 18, 21, 24).

---

## 5. Theme Block to Snippet Rendering & Variable Isolation Pitfall

### The Problem:
When refactoring monolith sections into modular Theme Blocks (Shopify OS 2.0 / Shrine 1.9+), blocks typically delegate rendering to shared snippets:
```liquid
{% assign has_margins = true %}
{% render 'countdown-timer', block: block %}
```
In Shopify Liquid, `{% render %}` has a **strictly isolated scope**:
- The snippet does **NOT** inherit variables assigned in the parent block (`has_margins` is `nil` inside the snippet).
- If the snippet guards styles with `{% if has_margins %}`, margin CSS (`margin-top: ...; margin-bottom: ...;`) is completely dropped, causing blocks to collapse vertically without margins.

### The Fix:
Always pass parent context explicitly to the snippet:
```liquid
{% render 'countdown-timer', block: block, has_margins: has_margins %}
```

### Flexbox Alignment in Horizontal Layouts:
When full-width banners (`width: 100%`) use horizontal layouts (`.countdown-wrapper--desktop-horizontal`), ensure `justify-content` respects the block's `alignment` setting:
```liquid
{% if block.settings.alignment == 'center' %}
  justify-content: center;
{% elsif block.settings.alignment == 'right' %}
  justify-content: flex-end;
{% else %}
  justify-content: flex-start;
{% endif %}
```

---

## 6. Multi-Column Responsive Block Layouts (Text with Icon Grid Behavior)

### The Problem:
Merchants frequently request blocks such as "Text with icon", trust badges, or guarantees to display in 2 columns on mobile devices instead of stacking vertically one below another.

### Inspection Checklist:
1. **Template Settings (`direction`)**:
   In Shopify OS 2.0 themes (e.g. Shrine 1.9+), check the block definition in `templates/product.*.json`:
   ```json
   "text_qiYcYM": {
     "type": "text-with-icon",
     "settings": {
       "direction": "horizontal", // Check if currently set to "vertical"
       ...
     }
   }
   ```
   If set to `"vertical"`, the block renders sequentially as a single column on all viewports. Switching to `"horizontal"` unlocks responsive column wrapping.
2. **Liquid Item Count & CSS Grid Calculation**:
   The snippet or block typically computes dynamic columns:
   ```liquid
   {%- assign item_count = 0 -%}
   {%- for i in (1..4) -%} ... {%- endfor -%}
   style="--item-count: {{ item_count }};"
   ```
   With `.product__text-container.horizontal`, it applies:
   ```css
   grid-template-columns: repeat(var(--item-count), 1fr);
   ```
   For 2 active items (e.g. "Free Shipping" and "Satisfaction Guarantee"), setting `direction: "horizontal"` natively generates a balanced 2-column layout on both mobile and desktop.
3. **Mobile CSS Breakpoint Check**:
   If `direction: "horizontal"` is already active but mobile collapses to 1 column due to `@media screen and (max-width: 749px)`, ensure `.product__text-container.horizontal` retains `grid-template-columns: repeat(2, 1fr)` or uses CSS flex with `flex: 1 1 45%` instead of `flex-direction: column`.

---

## 7. Block Type & Icon Settings Drift During Theme Template Upgrades

### The Problem:
During theme template migrations or OS 2.0 block reorganizations (e.g., Shrine / Verdo product templates), trust badge blocks may drift from `"type": "text-with-icon"` to a generic `"type": "text"`.
- **Symptom**: Feature highlights (such as "100% Waterproof", "Lifetime Warranty", "Adjustable Sizes") lose their icons, grid spacing, and custom icons (`custom_icon_1`..`4`), collapsing into unstyled text or vanishing from product pages.
- **Root Cause**: Generic `"type": "text"` blocks in Shopify OS 2.0 point to `blocks/text.liquid` which ignores icon settings (`text_1`..`4`, `icon_1`..`4`, `custom_icon_1`..`4`, `direction`, `icon_scale`).

### Resolution & Automation Workflow:
1. **Compare Backup vs Current JSON Templates**:
   Inspect backup templates (`templates/product.*.json`) for blocks containing icon parameters or custom SVG strings.
2. **Reconcile Block Types & Settings**:
   Automate JSON AST updates across all product templates:
   ```python
   # Convert block type from 'text' back to 'text-with-icon'
   block["type"] = "text-with-icon"
   # Restore missing setting keys
   block["settings"].update({
       "text_1": "<strong>100% Waterproof</strong>",
       "icon_1": "Local Shipping",
       "text_2": "<strong>Adjustable Sizes</strong>",
       "icon_2": "check_circle",
       "text_3": "<strong>Lifetime Warranty</strong>",
       "icon_3": "license",
       "text_4": "<strong>Designed in Amsterdam</strong>",
       "icon_4": "genetics",
       "direction": "horizontal",
       "width": "100%"
   })
   ```
3. **Comment-Aware Validation & Push**:
   Strip C-style header comments (`/* ... */`) before JSON parsing, validate that 100% of product templates pass `json.loads()`, and push non-destructively to the target live theme ID via Shopify CLI.

---

## 8. Customizer Ingestion & Pre-Mutation Pull Protocol

### The Problem:
Merchants and store owners frequently adjust product layouts, text copy, and theme settings directly within the Shopify Theme Customizer. If an agent applies AST mutations or pushes local files without pulling first, live Customizer changes will be permanently overwritten.

### Safe Sync Protocol:
1. **Safety Backup**:
   Always create a timestamped backup directory of the local theme folder before pulling:
   ```bash
   cp -r "CURRENT_THEME_DIR" "CURRENT_THEME_DIR_BACKUP_BEFORE_PULL"
   ```
2. **Pull Live Theme State**:
   Execute full or selective pull from the target theme ID:
   ```bash
   shopify theme pull --path "./CURRENT_THEME_DIR" --store <handle>.myshopify.com --password <token> --theme <theme_id>
   ```
3. **Verify Pulled Templates**:
   Validate that all pulled `.json` templates parse cleanly using comment-aware JSON decoders before initiating AST modifications.

---

## 9. Headless / Agentic Shopify CLI Partner Authentication via Browser Flow

### The Problem:
When operating without a direct Theme Access Password (`shptka_...`), commands like `shopify theme list --store <store>` demand interactive OAuth/partner authentication. In subshell/agent runners, standard non-interactive execution either fails immediately or hangs indefinitely.
Additionally, if an existing CLI session holds stale or incompatible credentials (e.g. `You are not authorized to edit themes... if you only have Partner staff member access`), commands fail immediately with exit code 1.

### Target Directory Pre-requisite for `theme pull`:
- **Fatal Error**: Running `shopify theme pull --path "./target-dir"` when `./target-dir` does not exist crashes with an unhandled Node.js exception: `gitInstanceFactory / insideGitDirectory / validateDirectory: in a directory that does not exist`.
- **Mandatory Guard**: Always execute `mkdir -p "./target-dir"` before invoking `shopify theme pull`.

### The Agentic Interactive Flow:
0. **Session Reset (If Stale Auth Detected)**:
   If authorization errors or Partner access warnings occur:
   ```bash
   shopify auth logout
   ```
1. **Launch in Background with PTY**:
   Execute the command with pseudo-terminal allocation:
   ```python
   terminal(command="shopify theme list --store <store>", background=True, pty=True)
   ```
2. **Submit Enter / Trigger Login**:
   Send newline `\n` to acknowledge the "Press any key to open the login page" prompt:
   ```python
   process(action="submit", data="\n", session_id=session_id)
   ```
3. **Capture Device Code & Complete Browser Auth**:
   Shopify CLI prints:
   ```text
   User verification code: ABCD-EFGH
   Opened link to start the auth process: https://accounts.shopify.com/activate-with-code?device_code=...
   ```
   Or for account selection:
   ```text
   https://accounts.shopify.com/select?rid=...
   ```
   The CLI launches the default browser, but the tab often remains in the background behind other windows.
   **Automated Tab Activation (macOS Chrome)**:
   Locate and raise the authentication tab directly to the front so the user has immediate 1-click access:
   ```bash
   osascript -e '
   tell application "Google Chrome"
       repeat with w in windows
           repeat with (i from 1 to count of tabs of w)
               set t to tab i of w
               if title of t contains "Shopify CLI" or URL of t contains "accounts.shopify.com" then
                   set active tab index of w to i
                   set index of w to 1
                   activate
                   return "Activated: " & (title of t)
               end if
           end repeat
       end repeat
   end tell'
   ```
4. **Passive Poll Completion (Zero Stdin Input)**:
   Do NOT send any keystrokes to stdin while polling. Poll `process(action="wait", session_id=session_id, timeout=60)` until the background process exits with `exit_code: 0`.
5. **Structured Querying**:
   Once authenticated, queries run headless without prompts:
   ```bash
   shopify theme list --store <store> --json
   ```
6. **Workspace Hygiene**:
   Clean up leftover local callback or activation tabs (`127.0.0.1:3080`, `activate-with-code`) in the browser.

---

## 10. Shopify Theme Store "Trial" Theme Invariant & API Access Boundary

### The Problem:
A merchant adds a commercial theme from the Shopify Theme Store (e.g. Helix, Prestige, Impulse) to test. In Shopify Admin under "Online Store -> Themes", the theme appears under **Draft themes** with a `Trial` badge and a `Buy` button.
However, running:
```bash
shopify theme list --store <store> --json
```
or querying the Shopify Admin Themes REST/GraphQL API (`/admin/api/unstable/themes.json`) **completely omits the trial theme**. It does not appear in the returned list, and running `shopify theme pull` against it is rejected.

### Root Cause & Shopify Invariant:
- **IP Protection by Design**: Shopify Theme Store strictly isolates unpurchased Trial themes from the remote Themes API to prevent unauthorized asset/Liquid downloading or redistribution before purchase.
- The theme's raw `.liquid`, assets, and schema files cannot be pulled via CLI or downloaded as a ZIP until the merchant clicks `Buy` and completes checkout.

### Alternative Inspection & Audit Protocols:
1. **Interactive Theme Customizer (UI/DOM Inspection)**:
   In the admin, click **"Edit theme"** (`admin.shopify.com/store/<handle>/themes/<theme_id>/editor`). Merchants and agents can inspect all available sections, blocks, templates, and theme settings directly in the Customizer without purchasing.
2. **Theme Store Metadata & Demo Store Extraction**:
   Inspect the official Theme Store listing (`https://themes.shopify.com/themes/<theme-slug>/presets/<preset-slug>`):
   - Retrieve full feature list, designer/vendor (e.g. ModuTheme), supported presets (e.g. Helix, Norda, Selene, Marlow, Elvara), and price.
   - Extract the live demo store domain via regex: `href=[\"\'](https://[^\"]*myshopify\.com[^\"]*)`.
3. **Storefront Asset & Web Component Reverse-Engineering Protocol**:
   To inspect the underlying section/block architecture and JavaScript runtime of any commercial theme without purchasing:
   - **Custom Elements / Web Components Discovery**:
     Extract all registered custom HTML elements from the demo storefront:
     ```python
     re.findall(r'<([a-z0-9]+-[a-z0-9\-]+)[\s>]', html)
     ```
     Reveals the full component tree: `<cart-drawer-component>`, `<bundle-product-card>`, `<free-shipping-bar>`, `<swatches-variant-picker-component>`, `<scrolling-hotspots>`, etc.
   - **Asset Pipeline Harvest**:
     Extract all JS/CSS assets loaded from `/cdn/shop/t/<id>/assets/`:
     ```python
     re.findall(r'cdn/shop/t/[0-9]+/assets/([a-zA-Z0-9_\-\.]+)', html)
     ```
     Provides direct access to core controllers (`component.js`, `section-renderer.js`, `cart.js`, `bundle-product-card.js`, `variant-picker.js`).
   - **Architectural Primitives Inspection**:
     Inspect `component.js` and `section-renderer.js` to extract:
     1. Base component class (e.g. Declarative Shadow DOM `<template shadowrootmode="open">`, reactive refs via `MutationObserver`).
     2. Event delegation pattern (e.g. declarative attributes `on:click="<component>/<method>?<query>"`).
     3. Section Rendering API & DOM morphing (e.g. URL query `?section_id=...` paired with `morph(existingEl, newEl)` for zero-flicker reactive updates).
     4. Sub-component contracts (e.g. embedded JSON schemas in `<script type="application/json" ref="variantData">`).
4. **Public Storefront Preview**:
   If the preview URL or theme ID is known from Admin URLs, preview live with `https://<store>.myshopify.com/?preview_theme_id=<theme_id>`.

---

## 11. macOS Shopify CLI Multi-Installation & Ruby Runtime Collision Guide (NPM vs Homebrew)

### The Problem:
On macOS environments where developers have multiple Shopify CLI installations (e.g. `/usr/local/bin/shopify` installed globally via npm and `/opt/homebrew/bin/shopify` installed via Homebrew):
1. **Ruby 2.6.10 System Incompatibility**:
   Older npm global builds of Shopify CLI (e.g. v3.52.0) rely on Ruby under `assets/cli-ruby`. On modern macOS (Monterey/Ventura/Sonoma/Sequoia), `/usr/bin/ruby` is deprecated Ruby 2.6.10, triggering:
   ```text
   Ruby version 2.6.10 is not supported. Make sure you have at least Ruby 2.7.5 installed on your system.
   ```
2. **Bundle Install Write Permission Trap**:
   If Homebrew Ruby (`/opt/homebrew/opt/ruby/bin`) is prepended to `PATH` to satisfy the Ruby 2.7+ requirement for the npm CLI, Bundler attempts to compile gems and write to:
   ```text
   /usr/local/lib/node_modules/@shopify/theme/node_modules/@shopify/cli-kit/assets/cli-ruby/Gemfile.lock
   ```
   Because `/usr/local/lib` is root-owned, this fails with:
   ```text
   Command failed with exit code 23: bundle install (Permission denied)
   ```
3. **Session Token Isolation Across CLI Paths**:
   Session auth tokens and OAuth credentials stored by `/usr/local/bin/shopify` do NOT propagate to `/opt/homebrew/bin/shopify`. Each CLI binary path maintains isolated configuration and keychain records.

### Deterministic Fix & Invariants:
1. **Always Target Homebrew Shopify CLI (v3.80+)**:
   Never invoke generic `shopify` if both paths exist. Explicitly use `/opt/homebrew/bin/shopify`. It operates entirely within user-accessible Homebrew prefixes and does not depend on root-owned `cli-ruby` gem directories.
2. **Headless Browser Auth Handshake for Homebrew CLI**:
   When authenticating a fresh `/opt/homebrew/bin/shopify` session:
   - Launch in background with `pty=True`:
     ```python
     terminal(command="/opt/homebrew/bin/shopify theme list --store <store>.myshopify.com", background=True, pty=True)
     ```
   - Send `\n` to acknowledge the "Press any key to open the login page" prompt.
   - Extract `User verification code: ABCD-EFGH` and open `https://accounts.shopify.com/activate-with-code?device_code=...` in the user's active browser.
   - Send a single `\n` ONLY to acknowledge the "Press any key" prompt and trigger the activation URL generation.
   - ⚠️ **Critical Polling Invariant (Zero-Stdin During Auth)**: NEVER send additional spaces, newlines, or keystrokes to stdin after the link is opened. In Shopify CLI v3.80+, any input while the CLI is awaiting OAuth callback triggers an Ink/Node.js unhandled rejection (`Unknown error` in chunk-KPFBSWRK), crashes the process, and immediately invalidates the user verification code on Shopify accounts.
   - Leave stdin completely untouched and wait passively via `process(action="wait", session_id=session_id, timeout=60)` for the user to approve the code in their browser. Once approved, the CLI finishes cleanly with exit code 0.
   - Verify authenticated state with `/opt/homebrew/bin/shopify theme list --store <store>.myshopify.com --json`.

---

## 12. Partner Staff Member Access Block & Development Store Workarounds

### The Problem:
When attempting to run `shopify theme list` or `shopify theme push` on a development store using an account authenticated via Shopify Partners as a **Partner staff member**, the CLI throws an error and exits:
```text
You are not authorized to edit themes on "<store>.myshopify.com".
You can't use Shopify CLI with development stores if you only have Partner staff member access.
If you want to use Shopify CLI to work on a development store, then you should be the store owner or create a staff account on the store.
```

### Deterministic Solutions:

#### Approach 1: Theme Access Password or Custom App Token (`--password`) — Recommended for CI/Agentic Pipelines
Both `shopify theme push` and `shopify theme list` accept an explicit `-p, --password <TOKEN>` parameter. This bypasses the interactive Partner OAuth check entirely.

1. **Option A: Shopify Theme Access App**
   - Install the official [Theme Access App](https://apps.shopify.com/theme-access).
   - Generate a Theme Access password (starts with `shptka_...`).
   - *Pitfall*: Navigating directly to `admin.shopify.com/store/<handle>/apps/theme-access` returns a 404 if the app is not yet installed on that specific development store.

2. **Option B: Store Custom App (Admin API Token)**
   - In Shopify Admin, navigate to `Settings > Apps and sales channels > Develop apps` (`admin.shopify.com/store/<handle>/settings/apps/development`).
   - Click **Allow legacy custom app development** (confirm).
   - Click **Create an app** (e.g. name `Theme CLI`).
   - Under **Configuration > Admin API integration**, select scopes:
     - `read_themes`
     - `write_themes`
   - Save and click **Install app** under **API credentials**.
   - Reveal the `Admin API access token` (starts with `shpat_...`).

3. **Deploy via CLI with Token**:
   ```bash
   shopify theme push \
     --store <handle>.myshopify.com \
     --path "<path_to_theme>" \
     --unpublished \
     --theme "<Theme_Name>" \
     --password "<shpat_... or shptka_...>"
   ```

#### Approach 2: Direct Store Owner CLI Re-Authentication
If token generation is unavailable:
1. Log out of the current Partner-linked session:
   ```bash
   shopify auth logout
   ```
2. Re-authenticate directly with the primary Store Owner or direct staff account:
   ```bash
   shopify theme list --store <handle>.myshopify.com
   ```

---

## 13. Zero-Ruby Fast-Path: Direct Asset Reading & Mutation via `@shopify/cli-kit` Session

### The Problem:
On environments where `shopify theme pull` or `shopify theme push` crashes due to Ruby runtime incompatibilities (e.g. Ruby 2.6 system deprecation, Bundler permission denied on root-owned `Gemfile.lock`, or missing native gems), full theme sync fails even though Shopify CLI authentication succeeded.

### The Fix (Zero-Ruby Node.js Admin API Bridge):
Once an agent or user completes `shopify theme list` or browser auth, `@shopify/cli-kit` persists the session token in the system keychain/session store. We can bypass Ruby and Bundler entirely by invoking Shopify Admin REST API directly via the pre-installed `@shopify/cli-kit` modules:

```javascript
// Example: Read and write theme assets headlessly in Node.js
import fs from "fs";

// Dynamically import cli-kit session and admin-api modules
const sessionModule = await import(
  "/usr/local/lib/node_modules/@shopify/cli/node_modules/@shopify/cli-kit/dist/public/node/session.js"
);
const adminApi = await import(
  "/usr/local/lib/node_modules/@shopify/cli/node_modules/@shopify/cli-kit/dist/public/node/api/admin.js"
);

const store = "<store_handle>.myshopify.com";
const themeId = "<theme_id>";

// 1. Acquire existing authenticated session (no prompts if already logged in)
const session = await sessionModule.ensureAuthenticatedThemes(store);

// 2. Fetch specific asset (e.g. blocks, snippets, or templates)
const res = await adminApi.restRequest(
  "GET",
  `/themes/${themeId}/assets`,
  session,
  undefined,
  { "asset[key]": "blocks/product_buy-buttons.liquid" }
);
const liquidContent = res.json.asset.value;

// 3. Mutate / write asset non-destructively
const writeRes = await adminApi.restRequest(
  "PUT",
  `/themes/${themeId}/assets`,
  session,
  {
    asset: {
      key: "blocks/product_buy-buttons.liquid",
      value: updatedLiquidContent
    }
  }
);
console.log("Status:", writeRes.status, "Key:", writeRes.json.asset.key);
```

### Key Advantages:
1. **Zero Ruby Dependency:** Immune to Ruby version conflicts, gem compilation issues, and root permission errors.
2. **Selective Atomic Sync:** Reads and writes only the exact file needed (<500ms) without multi-megabyte theme downloads.
3. **Automated Verification:** Allows immediate programmatic readback (`GET`) to verify deployed code in live Shopify.

---

## 14. Port 3456 / 3080 Conflict & Stale CLI Process Recovery

### The Problem:
Shopify CLI spins up a local HTTP listener on port `3456` (or `3080`) to capture the OAuth redirect token during browser login. If a background CLI session is cancelled or times out, the Node.js listener often remains alive, causing subsequent auth runs to fail with `EADDRINUSE :::3456` or silent hangs.

### Resolution:
1. Detect lingering listener:
   ```bash
   lsof -i :3456
   ```
2. Terminate stale process:
   ```bash
   kill -9 <PID>
   ```
3. Re-run auth command cleanly in background with `pty=True`.

---

## 15. macOS Dual-Chrome Instance & Off-Screen Window Trap During Shopify Admin Inspection

### The Problem:
When connecting to `https://admin.shopify.com/store/<handle>/themes` via macOS `Google Chrome`, two subtle desktop/AppleScript traps can stall inspection:
1. **Isolated Profile / Second Chrome Process Collision**:
   If a separate isolated Chrome process (`--user-data-dir=/tmp/...`) is running concurrently alongside the primary `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, `open -a "Google Chrome" <url>` or `computer_use(app="Google Chrome")` may bind to the wrong PID or an unauthenticated profile (resulting in Cloudflare Turnstile `"Трохи зачекайте…"` loops or login prompts), while AppleScript talks to the primary instance.
2. **Off-Screen / Hidden Window Bounds (`-1884, 59`)**:
   Opening a tab in an existing Chrome window whose coordinates were pushed off-screen (e.g., `bounds: -1884, 59, -372, 975` from a disconnected external monitor) causes `computer_use(action="capture", app="Google Chrome")` without an explicit `window_id` to capture whichever window is on-screen rather than the target Shopify Admin window.
3. **AppleScript JavaScript Execution Blocked**:
   `execute active tab of window 1 javascript "..."` fails with `Executing JavaScript through AppleScript is turned off` unless manually enabled in Chrome's View > Developer menu.

### Deterministic Resolution Workflow:
1. **Audit Chrome Processes & Clean Stale Isolated Instances**:
   ```bash
   ps aux | grep -i "Google Chrome" | grep -v "Helper" | grep -v "grep"
   ```
   If an isolated `--user-data-dir=/tmp/...` Chrome process is shadowing the primary instance, terminate the temporary PID so `computer_use` and `open -a "Google Chrome"` bind deterministically to the primary authenticated Chrome PID.
2. **Enumerate Exact `(pid, window_id)` via `computer_use`**:
   Call `computer_use(action="list_windows", app="Google Chrome")` to find the exact `window_id` and `pid` hosting the `Shopify` / `Themes` window (even if off-screen or behind another window).
3. **Target Exact `pid` + `window_id` with `mode="ax"`**:
   Instead of relying on AppleScript JavaScript injection, query the Accessibility tree directly:
   ```python
   computer_use(
       action="capture",
       app="Google Chrome",
       mode="ax",
       pid=primary_pid,
       window_id=shopify_window_id,
       max_elements=1000
   )
   ```
   This extracts all store metadata, active theme name, and draft themes directly from the AX tree in one background call without requiring Chrome's "Allow JavaScript from Apple Events" toggle or moving the user's windows.

---

## 16. Multi-Donor GitHub Repository Branch Topology & Shopify GitHub App Sync

### The Problem:
Shopify's native GitHub integration (**Online Store ➔ Themes ➔ Add theme ➔ Connect from GitHub**) strictly requires the root directory (`/`) of any connected branch to contain a valid Shopify theme structure (`layout/`, `config/`, `templates/`, `sections/`, `snippets/`, `assets/`). It does **not** support monorepo subdirectories.

Additionally, when managing multiple reference/donor themes alongside a production theme inside a single GitHub organization repository (e.g., `DNKShopify/DNK-e.com`), two operational hazards arise:
1. **Organization Visibility in Shopify GitHub App**: If the repository belongs to a GitHub Organization (`DNKShopify`) rather than a personal user account, it will not appear in Shopify's "Connect from GitHub" dropdown until organization access is explicitly granted in GitHub (`Settings ➔ Applications ➔ Installed GitHub Apps ➔ Shopify ➔ Configure ➔ Repository access`).
2. **Two-Way Sync Pollution on Reference Branches**: Once a branch (`donor/<theme>`) is connected to a store, every save in the Shopify Theme Customizer automatically pushes a commit authored by `Shopify` back to that branch (mutating `config/settings_data.json` and `templates/*.json`).

### Deterministic Architecture & Workflow:
1. **Orphan-Branch Topology (`1 Branch = 1 Root-Level Theme`)**:
   - `main` / `staging`: Core production and staging theme.
   - `donor/<theme-slug>-<version>` (e.g., `donor/ascendify-2.10.0`, `donor/shrine-pro-1.9.0`, `donor/dnk-ecom-sections-1.0.0`): Each donor theme lives at the root (`/`) of its own isolated branch and can be directly connected as an independent theme in Shopify Admin.
   - `donor/donor-lab` & `donor/sections-vault`: Non-theme branches (documentation, changelogs, standalone section vaults without `layout/theme.liquid`). **Never** connect these two branches in Shopify Admin.
2. **Bit-Exact ZIP-to-Branch Verification via `git ls-tree`**:
   Before connecting or re-syncing a donor branch, verify that the GitHub branch (`origin/donor/<theme>`) matches the canonical release `.zip` with zero file/byte drift:
   ```python
   # Compare git ls-tree -r -l origin/donor/<theme> against zipfile.ZipFile(zip_path).infolist()
   # Ensure diffs_vs_zip == 0 before linking in Shopify Admin.
   ```
   When updating a donor branch from a cleaned release `.zip`, mount the branch in an isolated temporary `git worktree add /tmp/wt-<theme> donor/<theme>`, sync the extracted files, commit, push, and remove the worktree so the primary working directory stays clean.
3. **Preserving Clean Donor Baselines Against Customizer Commits**:
   - Always run `git pull origin donor/<theme>` before pushing local code fixes to a connected branch.
   - To reset Customizer experiments back to the clean donor state, restore from the baseline commit: `git checkout <baseline_sha> -- config/settings_data.json templates/`.
   - Note that manually uploaded ZIP themes in Shopify Admin cannot be converted in-place to GitHub-connected themes; `Connect from GitHub` always creates a new theme slot (mind the 20-theme library cap on standard/dev stores).

---

## 17. Commercial Donor Theme DRM Sanitization & Cart Drawer Recovery (`fixParsedHtml` + `updateQuantity`)

### The Problem:
Commercial third-party Shopify themes (such as Ascendify, Shrine Pro, and derivative section packs) frequently embed multi-layer obfuscated DRM/licensing traps inside `assets/global.js` or `assets/main.js` (e.g., `validateLicense`, `checkPurchaseCode`, `window.location.href = "https://thrill-bro.com/..."`, or `document.body.innerHTML = ""`).
When stripping or stubbing these obfuscated functions, two critical regressions commonly break the Cart Drawer (`<cart-drawer>` / `<cart-items>`):
1. **No-Op `fixParsedHtml(htmlDoc)` Stub**:
   In Shrine/Ascendify architectures, `CartItems` / `CartDrawer` calls `this.fixParsedHtml(parsedState)` before extracting `.drawer__inner` or `#CartDrawer-CartItems` from the Section Rendering API response. If `fixParsedHtml` was entangled with DRM checks and replaced with a naive stub (`return htmlDoc;`) or if it returns `undefined`, DOM selectors fail to match or strip necessary inner wrappers, leaving the Cart Drawer empty or stale after add-to-cart.
2. **Truncated `updateQuantity(line, quantity, name)`**:
   If `updateQuantity` loses its `fetch(routes.cart_change_url, ...)` payload or requests the wrong section IDs (`sectionsToRender`), clicking `+`, `-`, or the trash icon spins indefinitely (`enableLoading(line)`) without updating line items, subtotal, or `cart-icon-bubble`.

### Deterministic Audit & Fix Pattern:
1. **Multi-Layer DRM Sweep (Zero External Beacons)**:
   Scan all `.js` and `.liquid` files in the theme for external licensing domains (`thrill-bro`, `shrine.io`, `license`, `atob`, hex-encoded URL arrays `\x68\x74\x74\x70`, or `new Function(...)`). Replace license verification gates with deterministic `return true;` while preserving surrounding class methods.
2. **Restore Full `updateQuantity` + `fixParsedHtml` Contract**:
   Ensure `CartItems.prototype.updateQuantity` (and any subclass override in `CartDrawerItems`) executes:
   - `this.enableLoading(line)` before the request and `this.disableLoading(line)` in `.finally()`.
   - `fetch(`${routes.cart_change_url}`, { ...fetchConfig(), body: JSON.stringify({ line, quantity, sections: this.getSectionsToRender().map((s) => s.section), sections_url: window.location.pathname }) })`.
   - Toggle `.is-empty` on both `this.classList` and `document.querySelector('cart-drawer')` when `parsedState.item_count === 0`.
   - Re-render each target selector in `this.getSectionsToRender()` (`main-cart-items`, `cart-icon-bubble`, `cart-live-region-text`, `main-cart-footer` / `cart-drawer`) using `this.getSectionInnerHTML(parsedState.sections[section.section], section.selector)`.
   - Dispatch `publish(PUB_SUB_EVENTS.cartUpdate, { source: 'cart-items', cartData: parsedState, variantId: ... })` so free-shipping bars, upsell sliders, and quantity breaks react immediately.
3. **Syntax & Archive Integrity Gate**:
   After patching `assets/main.js` or `assets/global.js`, run `node --check <file.js>` on every modified JS asset before repacking the `.zip` and syncing to the target `donor/*` GitHub branch.










