# --- DNK-MRH-HEADER ---
# mrh_id: "references/proven_repo_recipes.md"
# purpose: "Proven local prototype recipes from Open Design Local, Tributary, ThoughtDAG, Creator OS Starter, and Hermes Desktop."
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym & Gerych Builder"
# --- END DNK-MRH-HEADER ---

# Proven Local Prototype Recipes (`../DNK_Vibe/`)

## 1. Open Design Local (`../DNK_Vibe/Open Design Local`)
- **Stack**: Next.js 16 (Turbopack) + Fastify/Node Daemon (`@open-design/daemon` v0.25.0) + `better-sqlite3` + `tools-dev` Sidecar Manager.
- **Registered Ports**:
  - Daemon API: `127.0.0.1:54301` (`OD_PORT=54301`)
  - Web UI: `127.0.0.1:54330` (`OD_WEB_PORT=54330`)
- **Google Cloud / Vertex AI Integration**:
  - Uses `@ai-sdk/openai-compatible` against `https://aiplatform.googleapis.com/v1beta1/projects/{projectId}/locations/global/endpoints/openapi`.
  - Passes OAuth2 Bearer token from `gcloud auth print-access-token` (`infobukstr@gmail.com`) via `Authorization: Bearer {env:OPEN_DESIGN_BYOK_API_KEY}`.
  - Exposes 11 Gemini models (`google/gemini-2.5-flash`, `google/gemini-2.5-pro`, `google/gemini-4-argon`, etc.).
- **Bundled Agent Binary (`byok-opencode`)**:
  - Resolved via `RUNTIME_PROJECT_ROOT` in `apps/daemon/src/runtimes/executables.ts` pointing to `node_modules/.pnpm/@powerformer+vela-cli-darwin-arm64@*/.../bin/libexec/opencode/opencode`.
  - Never use `__dirname` in ES modules.
- **Canonical Launch Command**:
  ```bash
  pnpm tools-dev start web --daemon-port 54301 --web-port 54330
  ```

## 2. Tributary (`../DNK_Vibe/tributary`)
- **Stack**: React/Vite Infinite Canvas + Fastify API + PostgreSQL (`LISTEN/NOTIFY` + SSE).
- **Registered Ports**:
  - Web UI: `127.0.0.1:5180` (`strictPort: true`)
  - Fastify Server: `127.0.0.1:8787`
- **Localization & Theme**:
  - Swept all hardcoded Chinese (`zh-CN`) strings from `apps/web/src`, `apps/server/src`, and `packages/domain/src` to English/Ukrainian while keeping `LEGACY_ALIASES` for existing DB provider keys.
  - Replaced calligraphy center mark (`支`) with universal `GitBranch` SVG.
  - Styled with ADR-008 Dual-Theme (`#0d0e10` Matte Obsidian & `#30cd90` Emerald / `#f1f2f4` Snow Canvas).
- **Database Isolation**:
  - Dedicated PostgreSQL database `tributary_dev` on `127.0.0.1:5432` with automatic `ensureSchema()` on startup.

## 3. ThoughtDAG (`../DNK_Vibe/thoughtdag`)
- **Stack**: Vite React Canvas + Express Backend.
- **Registered Ports**:
  - API: `127.0.0.1:54120` (`.env` `PORT=54120`)
  - Web UI: `127.0.0.1:54121` (`vite.config.ts` `port: 54121, strictPort: true`, proxy `/api` -> `http://127.0.0.1:54120`)

## 4. Creator OS Starter (`../DNK_Vibe/creator-os-starter`)
- **Stack**: Next.js App Router + Laya AI Sidecar.
- **Registered Ports**:
  - Next.js Web UI: `127.0.0.1:54130` (`package.json` `next dev -p 54130`)
  - Laya Sidecar: `127.0.0.1:54131` (`scripts/dev-local.mjs` `LAYA_PORT=54131`)

## 5. Hermes Agent Desktop (`../DNK_Vibe/Hermes-Agent-Desktop`)
- **Stack**: Tauri v2 + Vite Frontend + WebSocket Bridge.
- **Registered Ports**:
  - Vite UI: `127.0.0.1:5174`
  - Bridge: `127.0.0.1:5175`
