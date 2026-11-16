---
title: "zclip Google Cloud Setup"
name: "zclip-google-cloud-setup"
description: "Deploy zclip with Google Cloud resources and model config."
status: "Active"
version: "1.0.0"
updated_at: "2026-10-28"
author: "DNK-e.com Maksym"
domain: zclip-google-cloud-setup
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/zclip-google-cloud-setup/SKILL.md"
> purpose: "Document: Skill"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

## When to Use
Deploy the zclip repository locally using Google Cloud resources, with all required models pre‑configured and environment variables set.

## Goal
Deploy the zclip repository locally using Google Cloud resources, with all required models pre‑configured and environment variables set.

## Prerequisites
- Access to a Google Cloud project with billing enabled.
- `gcloud` CLI installed and authenticated.
- `pnpm` installed globally.

## Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/DanialDaeHyunNam/zclip.git ../DNK_Vibe/zclip
   cd ../DNK_Vibe/zclip
   ```
2. **Install pnpm dependencies**
   ```bash
   pnpm install
   ```
3. **Set up Google Cloud environment tag**
   ```bash
   gcloud resource-manager tags bindings create \
     --project=<PROJECT_ID> \
     --display-name=Environment \
     --format="value(name)" \
     --values="Production"
   ```
4. **Configure `.env.local`** (copy from `.env.example` and fill):
   - `GEMINI_API_KEY=<your‑key>`
   - `DEFAULT_MODEL=google/gemini-3.8-flash` (or desired model)
   - `VERTEX_LOCATION=global`
5. **Run the dev server**
   ```bash
   pnpm dev
   ```

## Common Pitfalls
- Turbopack symlink resolution error under pnpm: Next.js 16 with Turbopack can fail with `Error: Could not find the Next.js package (next/package.json)`. Fix by adding `.npmrc` (`node-linker=hoisted`, `shamefully-hoist=true`), running `rm -rf node_modules && pnpm install`, and starting with `--webpack` flag: `pnpm exec next dev --webpack -p 3001`.
- Missing `GEMINI_API_KEY` vs `VERTEX_API_KEY`: In environments where Google Cloud/Vertex credentials exist under `VERTEX_API_KEY` or system envs rather than `GEMINI_API_KEY`, ensure `lib/server-keys.ts` and `app/api/keys/route.ts` check `process.env.GEMINI_API_KEY || process.env.VERTEX_API_KEY`. Otherwise the UI reports provider key as missing and blocks generation.
- Veo model default status: Check `lib/config.ts` for `veo: { implemented: true }` and `DEFAULT_PROVIDER: "veo"`. Upstream zclip repos may have flagged Veo as `implemented: false` (due to legacy Gemini API migrations), which hides or disables Google Veo from the ModelPicker.
- Using absolute paths in imports → breaks relative‑path invariant.

## References
- `../DNK_Vibe/zclip/.env.example` – template for environment variables. 
- Google Cloud documentation on resource‑manager tags. 
- pnpm installation guide.
