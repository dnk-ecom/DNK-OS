---
name: dnk-local-prototype-launcher
description: "Use to build and launch local repos in ../DNK_Vibe/."
category: software-development
version: "1.0.0"
author: "DNK-e.com Maksym"
license: "MIT"
metadata:
  hermes:
    tags: ["local-prototype", "launcher", "port-registry", "vertex-ai", "localization", "dnk-vibe", "gerych-builder"]
    related_skills: ["sota-repository-assimilation", "open-design-local-dev", "dnk-swarm-orchestration"]
    references:
      - "references/proven_repo_recipes.md"
---

# 🚀 DNK Local Prototype Builder & Launcher (`dnk-local-prototype-launcher`)

## When to Use
Invoke this skill immediately whenever the user gives the command **"запустити локально"**, **"launch locally"**, **"підніми локальний прототип"**, or asks to build and run any cloned open-source repository inside `../DNK_Vibe/<repo>`.

This skill turns **`gerych_builder`** into a specialized **Local Prototype Runtime Synthesizer** that uses proven blueprints from already implemented repositories (`Open Design Local`, `Tributary`, `ThoughtDAG`, `Creator OS Starter`, `Hermes Desktop`) to assemble, configure, localize, theme, wire to Google Cloud / Vertex AI, and launch working prototypes in seconds without breaking existing running services.

---

## ⚡ 1. The 6-Stage Autonomous Prototype Synthesis Pipeline

### Stage 1: Automated Inspection & SSOT Port Reservation
Before starting any process, run the deterministic prototype builder CLI:
```bash
python3 ./scripts/system/dnk_local_prototype_builder.py --repo "../DNK_Vibe/<RepoName>" --action inspect
```
- **SSOT Registry**: Reads `./core/registry/port_registry.yaml` (`ADR-092`).
- **Auto-Allocation**: If the repository is not yet registered, automatically allocates a dedicated conflict-free port pair in the `54160–54999` range (e.g. `web: 54160`, `api: 54161`) and saves it to `./core/registry/port_registry.yaml`.
- **Forbidden Ports**: Never allow a `../DNK_Vibe/` repository to bind `3000`, `5173`, `8000`, `8001`, `8002`, or `8003` (reserved for `DNK_HUB` Core).
- **Port Enforcement Rules**:
  - **Vite (`vite.config.ts`)**: Set `server: { host: '127.0.0.1', port: <WEB_PORT>, strictPort: true }`.
  - **Next.js (`package.json`)**: Pass explicit `-p <WEB_PORT> --hostname 127.0.0.1` and configure `/api/:path*` rewrites in `next.config.ts` to point to `http://127.0.0.1:<API_PORT>/api/:path*`.
  - **Daemon / Fastify / Express**: Bind `127.0.0.1:<API_PORT>` and add `<WEB_PORT>` to CORS `allowedBrowserPorts` / `trustedWebOriginPort`.

### Stage 2: Language & Localization Gate (Zero-Chinese UI Invariant)
The user operates in **English (🇬🇧)** and **Ukrainian (🇺🇦)** and does not read Chinese.
1. Inspect the `Zero-Chinese UI` field from `dnk_local_prototype_builder.py`.
2. If `cjk_files_count > 0`:
   - Audit UI entry points (`apps/web/src`, `components/`, `pages/`), server validation routes, and system prompts.
   - Replace hardcoded CJK strings (`[\u4e00-\u9fff]`) with English (`en`) or Ukrainian (`uk`) equivalents.
   - If the app has an i18n provider, force the default locale to `'en'` or `'uk'` (never `'zh'` or `'zh-CN'`).
   - Preserve a `LEGACY_ALIASES` map in backend provider configs if existing SQLite/Postgres records reference localized provider names.
   - Replace hardcoded calligraphy glyphs in canvas logos with clean Lucide SVG icons (`GitBranch`, `Sparkles`, `Layers`).

### Stage 3: DNK Design System & Dual-Theme Alignment (ADR-008)
Inject and align visual styling with the canonical DNK OS aesthetics:
```bash
python3 ./scripts/system/dnk_local_prototype_builder.py --repo "../DNK_Vibe/<RepoName>" --action prepare --inject-theme
```
- **DNK_Bookmarks Dual-Theme Standard (ADR-008)**:
  - **Dark Mode (Matte Obsidian & Emerald)**: `--dnk-bg: #0d0e10`, `--dnk-surface: #16181b`, `--dnk-surface-hover: #1e2125`, `--dnk-border: rgba(255, 255, 255, 0.08)`, `--dnk-accent: #30cd90`, `--dnk-text-primary: #f6f6f7`.
  - **Light Mode (Snow Canvas)**: `--dnk-bg: #f1f2f4`, `--dnk-surface: #ffffff`, `--dnk-border: #e3e5e8`, `--dnk-accent: #008060`, `--dnk-text-primary: #202223`.
- **Dark Teal Spatial Canvas Standard**:
  - Canvas `#1e2022`, Fill `#162c2f`, Header `#112224`, Border `#224447`, Accent `#35d5d5`, Active Orb `#22c55e`, Text `#d4d8db`.
- **Spatial Canvas Backdrop**: `radial-gradient(var(--dnk-grid-dot) 1px, transparent 1px)` with `background-size: 16px 16px`.

### Stage 4: Google Cloud Account, Vertex AI & Sidecar Wiring
Every local AI prototype must work out-of-the-box with Maxim's active Google Cloud / Vertex AI credentials without requiring manual paid third-party keys:
1. **Verify Active GCloud Session**:
   - Account: `infobukstr@gmail.com` (`gcloud auth print-access-token`).
   - Supported Vertex Models: `google/gemini-2.5-flash`, `google/gemini-2.5-pro`, `google/gemini-4-argon`.
2. **Vertex AI OpenAI-Compatible Routing (No Header Conflict)**:
   - Route Vertex AI calls via `@ai-sdk/openai-compatible` (or standard OpenAI client) against:
     `https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/global/endpoints/openapi`
   - Pass `Authorization: Bearer <GCLOUD_TOKEN>`. **Never** combine `x-goog-api-key` with OAuth2 Bearer tokens on `aiplatform.googleapis.com` (prevents HTTP 401 `API keys are not supported`).
3. **Sidecar & Agent Binary Resolution (`opencode`, `laya`, `claude-code`)**:
   - In ES Modules (`"type": "module"`), resolve bundled binaries via `RUNTIME_PROJECT_ROOT` or `import.meta.url` — **never** use `__dirname` (which throws `ReferenceError` at runtime).
   - Map HTTP `429 Too Many Requests` to `RATE_LIMITED` instead of `AGENT_AUTH_REQUIRED`.

### Stage 5: Native Addon ABI & Database Isolation
1. **Node.js ABI Compatibility**:
   - Run under Node v24 (`v24.13.0`). If the project uses native C++ addons (`better-sqlite3`, `sharp`, `node-pty`), verify the binary loads cleanly (`node -e "require('better-sqlite3')"`). If ABI mismatch (`NODE_MODULE_VERSION 115 vs 137`) occurs, run `pnpm rebuild <addon>`.
2. **Database Isolation**:
   - **PostgreSQL**: Use the local dev Postgres on `127.0.0.1:5432` and create an isolated database `<repo_slug>_dev` (`CREATE DATABASE <repo_slug>_dev;`).
   - **SQLite**: Keep database files inside the repo's local state directory (`.od/app.sqlite` or `./data/local.db`) and clear stale failed auth states if needed.

### Stage 6: Background Launch & Live Runtime Verification Gate
1. **Clean Stale Orphans on Assigned Ports Only**:
   - Check `lsof -iTCP:<WEB_PORT> -iTCP:<API_PORT> -sTCP:LISTEN -P -n`. Never kill processes on ports belonging to other repositories!
2. **Start Prototype via Official Orchestrator or Background Process**:
   - For `Open Design Local`: `pnpm tools-dev start web --daemon-port 54301 --web-port 54330`
   - For standard monorepos: launch via `terminal(background=true)` on the registered ports.
3. **Mandatory Live Verification**:
   ```bash
   python3 ./scripts/system/dnk_local_prototype_builder.py --repo "../DNK_Vibe/<RepoName>" --action verify
   ```
   Confirm `listening=True` and `HTTP 200 OK` on both Web UI and API `/api/health` before reporting completion.

---

## 📚 2. Reference Recipes from Implemented Projects
Load `skill_view(name="dnk-local-prototype-launcher", file_path="references/proven_repo_recipes.md")` for concrete configurations of:
- **Open Design Local** (`54301` Daemon / `54330` Next.js 16 + `tools-dev` + `byok-opencode` + Vertex AI)
- **Tributary** (`8787` Fastify + `5180` Vite + Postgres `tributary_dev` + EN/UK localization + ADR-008 Dual-Theme)
- **ThoughtDAG** (`54120` Express API + `54121` Vite `strictPort: true`)
- **Creator OS Starter** (`54130` Next.js + `54131` Laya Sidecar)
