---
title: "PSOD DELEGATION CONTRACT: Social Commerce OG & GEO Metadata Engine [COMPLETED]"
description: "Canonical PSOD Delegation Task: Dynamic Social OG-Card, GEO Schema.org JSON-LD & Intent-Driven Alt Engine (DEC-143 Extended)"
mrh_id: "docs/tasks/TASK_2026_11_18_MEDIA_SOCIAL_COMMERCE_OG_JSONLD.md"
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
> mrh_id: "docs/tasks/TASK_2026_11_18_MEDIA_SOCIAL_COMMERCE_OG_JSONLD.md"
> purpose: "Canonical PSOD Delegation Task: Dynamic Social OG-Card, GEO Schema.org JSON-LD & Intent-Driven Alt Engine (DEC-143 Extended)"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

<!-- --- DNK-MRH-HEADER ---
mrh_id: "docs/tasks/TASK_2026_11_18_MEDIA_SOCIAL_COMMERCE_OG_JSONLD.md"
purpose: "Canonical PSOD Delegation Task: Dynamic Social OG-Card, GEO Schema.org JSON-LD & Intent-Driven Alt Engine (DEC-143 Extended)"
canonical_source: true
alters_files:
  - "services/dnk_media/contracts/schemas.py"
  - "services/dnk_media/src/provenance.py"
  - "services/dnk_media/src/social_commerce.py"
  - "services/dnk_media/src/service.py"
  - "services/dnk_media/mcp_server.py"
  - "services/dnk_media/cli.py"
  - "services/dnk_media/tests/test_social_commerce.py"
triggers_tasks: []
status: "Completed"
version: "1.1.0"
updated_at: "2026-11-18"
author: "DNK-e.com Maksym & Antigravity"
--- END DNK-MRH-HEADER --- -->

# 📋 PSOD DELEGATION CONTRACT: Social Commerce OG & GEO Metadata Engine [COMPLETED]

### 1. Problem & Requirements (P):
- **Problem**: Raw product images lack social engagement when shared in messaging apps (Telegram, WhatsApp, iMessage, Twitter/X) and are invisible to Generative Engine Optimization (GEO) crawlers (ChatGPT Search, Perplexity, Google Lens).
- **Requirements**:
  1. **Schema.org Product + Offer JSON-LD**: Synthesize compliant JSON-LD structured data with currency, price, availability, brand, and localized descriptions.
  2. **OpenGraph & Twitter Card HTML Tags**: Generate copy-pasteable meta tags for Shopify product pages (`og:image`, `og:title`, `og:description`, `product:price:amount`, `product:price:currency`).
  3. **Intent-Driven Alt Text Synthesis**: Enhance formula to support commercial USP, price tag context, and drop edition attributes while strictly respecting W3C length ceilings (< 140 chars).
  4. **Dynamic Social OG Card Generator (1200x630)**: Provide a clean SVG/HTML/image composite builder for chat cards with Glassmorphic badge, price tag, brand watermark, and "In Stock" pill.
  5. **FastMCP & CLI Integration**: Add `media_generate_social_card`, `media_generate_jsonld`, and CLI commands `social-card`, `jsonld`.

### 2. Permitted Files Whitelist (Target Whitelist):
- `services/dnk_media/contracts/schemas.py`
- `services/dnk_media/src/provenance.py`
- `services/dnk_media/src/social_commerce.py`
- `services/dnk_media/src/service.py`
- `services/dnk_media/mcp_server.py`
- `services/dnk_media/cli.py`
- `services/dnk_media/tests/test_social_commerce.py`

### 2.1. Negative Scope & Boundaries (Anti-Scope):
- ❌ Жодних змін за межами `services/dnk_media/`.
- ❌ Заборонено додавати важкі зовнішні бібліотеки генерації зображень (Cairo, Pillow); суворе дотримання Senior Dev Solution Ladder.
- ❌ Жодних абсолютних шляхів.

### 3. Substrate & Rules (S):
- Python 3.11+ / stdlib first (DEC-057 Senior Dev Solution Ladder).
- Relative paths only (`./`, `../`). No absolute `/Users/...` in code.
- Zero-Bloat: pure Python stdlib for SVG/HTML and JSON-LD generation.
- 100% deterministic test suite.

### 4. Deterministic Verification Oracle (O):
```bash
uv run pytest services/dnk_media/tests -v
```
> 🚨 EXIT CODE MUST BE `0`. ALL TESTS MUST PASS.

**Verified Execution**:
- `uv run pytest services/dnk_media/tests -v` -> 25 passed in 1.65s (Exit Code 0).
- `uv run python -m services.dnk_media.cli social-card ...` -> Exit Code 0.
- `uv run python -m services.dnk_media.cli jsonld ...` -> Exit Code 0.

### 5. Deliverable Format (D):
- Production `social_commerce.py` module implemented and verified.
- Schema extensions in `schemas.py` (`SocialCardRequest`, `SocialCardResponse`, etc.).
- FastMCP tool registration in `mcp_server.py` (`media_generate_social_card`, `media_generate_jsonld`).
- CLI subcommands in `cli.py` (`social-card`, `jsonld`).
- 100% green test suite in `tests/test_social_commerce.py`.
