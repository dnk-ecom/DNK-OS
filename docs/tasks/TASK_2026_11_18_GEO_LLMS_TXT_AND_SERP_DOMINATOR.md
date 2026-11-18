---
title: "PSOD DELEGATION CONTRACT: E-Commerce llms.txt, Merchant Feed & SERP Dominator Engine [COMPLETED]"
description: "Canonical PSOD Delegation Task: E-Commerce llms.txt, Google Merchant XML & SERP Dominator Graph (DEC-160)"
mrh_id: "docs/tasks/TASK_2026_11_18_GEO_LLMS_TXT_AND_SERP_DOMINATOR.md"
status: Active
archetype: TASK_SPEC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - task
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/tasks/TASK_2026_11_18_GEO_LLMS_TXT_AND_SERP_DOMINATOR.md"
> purpose: "Canonical PSOD Delegation Task: E-Commerce llms.txt, Google Merchant XML & SERP Dominator Graph (DEC-160)"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📋 PSOD DELEGATION CONTRACT: E-Commerce llms.txt, Merchant Feed & SERP Dominator Engine [COMPLETED]

### 1. Problem & Requirements (P):
- **Problem**: In late 2026, AI search engines (ChatGPT Search, Perplexity, Claude, Gemini) and Google Shopping dominate customer discovery. E-commerce stores that only serve heavy HTML/JS are token-inefficient to AI crawlers, miss the Google Shopping free organic tier, and fail to maximize mobile SERP vertical pixel area.
- **Requirements**:
  1. **`/llms.txt` and `/llms-full.txt` E-Commerce Engine (`services/dnk_distribution/src/llms_txt.py`)**:
     - Conforms to standard `llmstxt.org` specification adapted for e-commerce.
     - Generates Markdown index (`# Store Name`, `> summary`, `## Core Collections / Products`, `## Policies`, `## Optional`).
     - Generates `llms-full.txt` aggregating deep product specs, materials, and care guides without HTML bloat.
  2. **Google Merchant Center XML Feed Generator (`services/dnk_distribution/src/merchant_feed.py`)**:
     - Generates valid RSS 2.0 / Google Base XML feed (`g:id`, `g:title`, `g:description`, `g:link`, `g:image_link`, `g:price`, `g:availability`, `g:brand`, `g:condition`).
     - Pure Python stdlib with zero external XML libraries.
  3. **SERP Dominator Graph Schema (`services/dnk_media/src/social_commerce.py`)**:
     - Generates `schema.org/BreadcrumbList` for breadcrumb hierarchy in SERP.
     - Generates `schema.org/FAQPage` for interactive accordion rich snippets directly on Google Search results.
     - Unifies `Product`, `Offer`, `BreadcrumbList`, and `FAQPage` under a single clean `@graph` JSON-LD schema.
  4. **C2PA PDP Storefront Trust Badge (`services/dnk_shopify/DNK_Ecom/blocks/dnk-c2pa-badge.liquid`)**:
     - Theme Block 2.0 with valid schema, Polaris Emerald styling, zero external JS dependencies, showing verified provenance.
  5. **FastMCP & CLI Integration**:
     - FastMCP tools: `distribution_generate_llms_txt`, `distribution_generate_merchant_feed`, `media_generate_serp_graph`.
     - CLI commands: `llms-txt`, `merchant-feed`.
  6. **Deterministic Verification Oracle**:
     - 100% test pass in `services/dnk_distribution/tests/test_llms_and_merchant.py` and `services/dnk_media/tests/test_social_commerce.py`.

**Verified Execution**:
- `uv run pytest services/dnk_distribution/tests -v` -> 11/11 passed (Exit Code 0).
- `uv run pytest services/dnk_media/tests -v` -> 27/27 passed (Exit Code 0).
- `just test-workhorses` -> 54/54 passed in 9.67s (Exit Code 0).
- CLI `llms-txt` & `merchant-feed` executed and verified.

### 2. Permitted Files Whitelist (Target Whitelist):
- `services/dnk_distribution/contracts/schemas.py`
- `services/dnk_distribution/src/llms_txt.py`
- `services/dnk_distribution/src/merchant_feed.py`
- `services/dnk_distribution/src/service.py`
- `services/dnk_distribution/mcp_server.py`
- `services/dnk_distribution/cli.py`
- `services/dnk_distribution/tests/test_llms_and_merchant.py`
- `services/dnk_media/src/social_commerce.py`
- `services/dnk_media/tests/test_social_commerce.py`
- `services/dnk_shopify/DNK_Ecom/blocks/dnk-c2pa-badge.liquid`

### 2.1. Negative Scope & Boundaries (Anti-Scope):
- Do NOT introduce external XML/RSS dependencies (strictly use Python stdlib `xml.etree.ElementTree`).
- Do NOT modify database schemas or add persistent tables for transient feeds.
- Do NOT alter core routing in other workhorses (`services/dnk_shopify` core app files).
- Do NOT create standalone microservice folders outside the 3 core workhorses.

### 3. Substrate & Rules (S):
- Python 3.11+ / stdlib first (Senior Dev Solution Ladder DEC-057).
- Relative paths only (`./`, `../`). No absolute `/Users/...` in code or docs.
- Machine-Readable Headers (MRH) per `DNK-STD-0075`.
- Atomic slices bounded by <= 25 tool calls.

### 4. Deterministic Verification Oracle (O):
```bash
uv run pytest services/dnk_distribution/tests -v
uv run pytest services/dnk_media/tests -v
```
> 🚨 EXIT CODE MUST BE `0`. ALL TESTS MUST PASS.

### 5. Deliverable Format (D):
- Production code and schemas in `services/dnk_distribution` and `services/dnk_media`.
- 100% test coverage with verifiable test receipts.
