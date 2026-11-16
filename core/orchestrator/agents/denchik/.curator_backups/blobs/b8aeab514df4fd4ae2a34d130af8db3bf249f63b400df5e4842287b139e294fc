---
title: "Sota Batch Intake And Cluster Taxonomy 2026 11"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/sota_batch_intake_and_cluster_taxonomy_2026_11.md"
> purpose: "Document: Sota Batch Intake And Cluster Taxonomy 2026 11"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧬 SOTA Batch Intake & 7-Cluster Ecosystem Taxonomy Protocol (2026-11)

## Overview & Context
This reference captures the production-tested methodology for high-velocity batch intake, GitHub REST API parallel hydration, SQLite `catalog.db` + FTS5 full-text indexing, and domain clustering across 100+ heterogeneous repositories without hitting rate limits or blowing context windows.

---

## ⚡ 1. High-Velocity Batch Intake Architecture

### Ingestion Pipeline
1. **URL Normalization & Slicing**:
   - Extract `owner/repo` from GitHub URLs.
   - Filter out organization landing pages (`github.com/orgs/...`), bare org slugs (`sanity-io`), and SaaS web application URLs (`app.flora.ai/...`, `puckeditor.com/docs/...`).
   - Map non-repo targets to their canonical open-source engine (e.g. `payloadcms/payload`, `puckeditor/puck`) or tag them as external ecosystem references.
2. **Parallel In-Memory API Hydration**:
   - Use `ThreadPoolExecutor(max_workers=10)` with Python `urllib.request`.
   - Pass `Authorization: token $GITHUB_TOKEN` from environment SSOT to achieve high throughput without 403 secondary rate limits.
   - Set request timeout to 12s with exponential retry on transient connection resets.
3. **Deterministic FTS5 Catalog Sync**:
   - Upsert records into SQLite `repositories` table.
   - Rebuild virtual table `repositories_fts USING fts5` with `tokenize = 'porter unicode61'`.
   - Update JSON SSOT snapshot `.data/repo_catalog/repositories.json`.

---

## 🧩 2. The 7-Cluster Strategic Taxonomy

| Cluster | Primary Focus & SOTA Capabilities | Assigned Swarm Agent | DNK Target Module |
| :--- | :--- | :--- | :--- |
| **1. Shopify & E-Commerce** | Theme AST generation (`shopify-theme-builder`), heuristic CRO auditing (`shopify-cro-checker`), Agentic app pipelines (`Agentic-Shopify-App-Pipeline`), visual reviews (`imagyn-reviews`). | `dnk_shopify` | `services/dnk_shopify` |
| **2. Video AI & Motion Graphics** | YouTube automated video editing & motion graphics (`sirioberati`), podcast virality hook clipping (`supoclip`, `desyn`), localized video card studios (`vibecut`, `card-news-studio`, `zclip`), voice cloning (`HuiSheng`). | `dnk_video_ai_creator` | `services/dnk_media` |
| **3. Web Scraping & Anti-Detect** | Botasaurus framework + scrapers (AliExpress, Temu, TikTok, YouTube, Amazon, Shopify, Google Trends), Browserbase bell-stack, BrightData MCP, SEO SERP crawler (`advertools`). | `dnk_dev_fullstack` | `services/dnk_distribution`, `scripts/tools` |
| **4. Visual Canvas, Wireflow & CMS** | Puck AI visual component builder (`puckeditor`), Payload CMS headless architecture (`payloadcms/payload`), Wireflow SVG node protocol (`vanila-io/wireflow`), human-agent UI protocol (`ag-ui`). | `dnk_mentor` | `core/canvas`, `apps/web` |
| **5. Multi-Agent Swarms & Skills** | Strategic simulation (`CEO-Arena`), scientific skills (`K-Dense-AI/mimeo`), context management (`squadron`, `context-forge`), dynamic skill grafting (`skill-graft`). | `dnk_mentor` | `core/orchestrator` |
| **6. Marketing & Meta Ads CRO** | Meta Ads Library scrapers & creative stack generation (`Andriy-Kulak`), multimodal creative audit with Claude Vision (`moritzkremb/jev-meta-ads-analyzer`), automated ad copy generators. | `dnk_marketing` | `services/dnk_distribution` |
| **7. RAG & Cognitive Memory** | Obsidian local vector graph (`obsidian-smart-connections`), compact in-memory RAG pipelines (`librag`, `RagBook`). | `gerych_prime` | `core/memory` |

---

## 🛡️ 3. Pitfalls & Epistemic Guardrails

1. **Botasaurus & E-Commerce Selector Rot**:
   - *Pitfall*: Public e-commerce scrapers (Temu, AliExpress, Amazon) hardcode CSS/XPath selectors that break when platforms update class names or bot defenses.
   - *Defense*: Treat scrapers as extraction recipes rather than stable APIs. Prefer official APIs, Sitemap/Robots inspection (`advertools`), or JSON-LD extraction (`<script type="application/ld+json">`) before launching headless Chrome.
2. **Heavy Node/GPU Dependencies in Video Repos**:
   - *Pitfall*: Repositories like `supoclip` or `vibecut` bundle heavy FFmpeg binaries, Next.js runtimes, and local Canvas builds that can create port collisions or high memory usage.
   - *Defense*: Apply clean-room extraction of the core algorithmic highlights (e.g. word-level timestamp heuristics, audio RMS silence trimming) into native DNK OS media services (`services/dnk_media/`), leaving heavy foreign wrappers isolated in `../DNK_Vibe/`.
3. **SQLite FTS5 Tokenizer Collision**:
   - *Pitfall*: Re-inserting into FTS5 tables without rebuilding or dropping triggers can cause duplicate matches or corrupted rank scores.
   - *Defense*: Always rebuild `repositories_fts` cleanly after batch upserts:
     ```sql
     DROP TABLE IF EXISTS repositories_fts;
     CREATE VIRTUAL TABLE repositories_fts USING fts5(..., tokenize = 'porter unicode61');
     INSERT INTO repositories_fts SELECT ... FROM repositories;
     ```
