# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/visual_shell_open_design_runtime_supervision.md"
# purpose: "Operational reference for Visual Shell (Open Design Local) daemon and web runtime supervision, Excalidraw font harmonization, and Vertex AI / Google Media OAuth integration."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-10-16"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Visual Shell (Open Design Local) Runtime Supervision, Font Harmonization & Vertex AI Integration

## 1. Architecture & Canonical Dev Stack (`tools-dev`)
In `../DNK_Vibe/Open Design Local`, the monorepo manages both the daemon and web frontend via `pnpm exec tools-dev`:
- **Daemon (`apps/daemon/`, Default Port `54301`)**: Fastify/Node backend handling CLI agents, Vertex AI / `gcloud` OAuth (`apps/daemon/src/integrations/gcloud-provider.ts`), and media providers (`apps/daemon/src/routes/media.ts`).
- **Web UI (`apps/web/`, Default Port `54330`)**: Vite + React frontend proxying `/api/*` to the daemon.

### Supervision Commands & Port Conflict Resolution
- **Check Status**: `pnpm exec tools-dev status`
- **Clean Start (Fixed Ports)**:
  If an orphaned daemon or previous `pnpm run dev:web` holds `:54330`, `tools-dev start web` may auto-increment to random ports (`54302`, `54331`). Always stop existing services and pass explicit ports:
  ```bash
  pnpm exec tools-dev stop
  pnpm exec tools-dev start web --daemon-port 54301 --web-port 54330
  pnpm exec tools-dev status
  ```
- **Health Checks**:
  - Web UI: `curl -sI http://127.0.0.1:54330/` -> `200 OK`
  - GCloud Auth Status: `curl -s http://127.0.0.1:54301/api/gcloud/status` -> `{"connected":true,...}`
  - Media Models Registry: `curl -s http://127.0.0.1:54301/api/media/models`

---

## 2. Excalidraw & Flat-Green Font Harmonization (`Inter` + `Manrope`)
To match the exact Cyrillic and Latin typography of `DNK_OS_APP` (`.obsidian/snippets/dnk-flat-green.css` and Excalidraw canvas settings) without thin/broken fallback glyphs:
1. **Static Font Assets (`apps/web/public/fonts/`)**:
   Copy variable TTF assets from `DNK_OS_APP/fonts/`:
   - `Inter.ttf` (weight `100 900`, normal)
   - `Inter-Italic.ttf` (weight `100 900`, italic)
   - `Manrope-VariableFont_wght.ttf` (weight `200 800`, normal)
2. **CSS Declarations (`apps/web/src/styles/base.css` & `tokens.css`)**:
   - Declare `@font-face` for `Inter` and `Manrope` pointing to `/fonts/...`.
   - Set `--sans: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;` and `--font-heading: "Manrope", "Inter", sans-serif;`.
3. **Runtime Font Recovery (`apps/web/src/runtime/font-recovery.ts`)**:
   - Register `Inter` in `APP_FONT_ASSETS` and `RECOVERABLE_FONTS` (replacing `Albert Sans`) so canvas/SVG measurement and preload hooks load `Inter.ttf` before first paint.

---

## 3. Vertex AI Gemini & Google Media OAuth Without Paid Locks
To enable Google Cloud Vertex AI (`gemini-2.5-pro`, `gemini-2.5-flash`) and Google Media (`Imagen 3/4`, `Veo 2/3`) in local environments using `gcloud` Application Default Credentials / OAuth without static API keys or subscription locks:
1. **Unlock Model Selectors (`apps/web/src/components/`)**:
   - In `agentModelSelection.ts`: ensure `agentModelIsSelectable` returns `true` for local/Vertex models and default `defaultAgentModelId` prioritizes Gemini.
   - In `InlineModelSwitcher.tsx` & `AvatarMenu.tsx`: include `gemini-2.5-pro` and `gemini-2.5-flash` in model rows with `locked = false` (no `is-locked` class).
   - In `modelOptions.tsx`: prioritize Gemini options first in `orderModelOptionsByAvailability`.
   - In `SettingsDialog.tsx`: wire `onSelectVertexModel` on `ModelsSection` to persist model selection immediately to config state.
2. **Enable Google Media Provider via GCloud OAuth (`apps/daemon/src/media/`)**:
   - In `apps/web/src/media/models.ts` and `apps/daemon/src/media/models.ts`: set `integrated: true` and `settingsVisible: true` on the `id: 'google'` provider.
   - In `apps/daemon/src/media/config.ts`: import `isSandboxModeEnabled` from `../sandbox-mode.js` (never `../sandbox.js`) and fall back to `await refreshVertexTokenAsync()` when `provider === 'google'` and no static API key is configured.
   - In `apps/web/src/components/SettingsDialog.tsx`: render a `Google Cloud Connected` status badge for the `google` media provider instead of requiring a manual API key input.

---

## 4. Legacy Visual Shell (`visual_shell/open_design/`) Invariants
- **Native Module ABI (`better-sqlite3`)**: Ensure `/opt/homebrew/bin` precedes `/usr/local/bin` in `PATH` so Node ABI versions match compiled binaries.
- **Turbopack Static Import Boundary**: Import `isRetryableAssistantTerminalFailure` from `../../runtime/design-delivery`, never from `../../runtime/chat-events`.
