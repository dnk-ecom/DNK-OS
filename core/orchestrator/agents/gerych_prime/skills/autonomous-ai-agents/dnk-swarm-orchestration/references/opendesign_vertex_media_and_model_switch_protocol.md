# --- DNK-MRH-HEADER ---
# mrh_id: "references/opendesign_vertex_media_and_model_switch_protocol.md"
# purpose: "Architecture & Integration runbook for OpenDesign / Open Design Local: Vertex AI dynamic model switcher & media provider activation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-15"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🎨 OpenDesign Local: Vertex AI & Google Media Provider Architecture

## 📌 Context & Problem Definition
In standalone applications using the OpenDesign harness (`apps/web`, `apps/daemon`, `packages/contracts`):
1. The UI default agent configuration (`agentId: 'amr'`) points to proprietary Vela/AMR cloud models which are locked without paid subscriptions.
2. Google Cloud / Vertex AI integration exists (`apps/daemon/src/integrations/gcloud-provider.ts` and `apps/web/src/components/ModelsSection.tsx`) with verified `user` ADC / OAuth access, but models are isolated inside the settings tab.
3. The main workspace model selector (`InlineModelSwitcher.tsx`) filters models strictly against `currentAgentModels` (AMR/Claude presets), leaving Vertex models unselectable from the workspace bar.
4. Media generation (`apps/web/src/media/models.ts` and `apps/daemon/src/media/models.ts`) marks Google (`imagen-4`, `imagen-3`, `veo-3`, `veo-2`, `lyria-2`) with `integrated: false`, preventing image and video generation through the user's active Vertex credentials.

---

## 🛠️ Canonical Architecture Patterns

### 1. Dual-Path Model Provider Switcher
To unlock Vertex AI in the main workspace:
- Check `gcloudStatus.connected` in `apps/web/src/components/InlineModelSwitcher.tsx`.
- When GCP is active, inject a `Google Cloud (Vertex AI)` option group into `compactModelRows` and `inlineAgentModelOptions`.
- Ensure selecting a Vertex model updates execution configuration:
  ```ts
  cfg.apiProtocol = 'google';
  cfg.model = vertexModelId;
  cfg.customBaseUrl = `https://${region}-aiplatform.googleapis.com/v1/projects/${projectId}/locations/${region}/publishers/google/models`;
  ```

### 2. Zero-Key Media Provider Inheritance
Media providers should not demand an external API key when gcloud is already authenticated:
- In `apps/web/src/media/models.ts`:
  Set `integrated: true` and `settingsVisible: true` for `id: 'google'`.
- In `apps/daemon/src/media/config.ts` & `apps/daemon/src/media/index.ts`:
  Resolve credentials dynamically via `gcloud-provider.ts`:
  ```ts
  const token = await getActiveGCloudAccessToken();
  // Pass Bearer token directly into Vertex AI REST endpoints for Imagen / Veo
  ```

### 3. Verification Protocol
- Run TypeScript compile check without emitting:
  ```bash
  cd "../DNK_Vibe/Open Design Local/apps/web" && npx tsc --noEmit
  cd "../DNK_Vibe/Open Design Local/apps/daemon" && npx tsc --noEmit
  ```
- Verify live state by checking `/api/gcloud/status` and validating model list response.
