---
title: "Supoclip Shorts Recipe"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/gcp-vertex-multimodal-integration/references/supoclip_shorts_recipe.md"
> purpose: "Document: Supoclip Shorts Recipe"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# 🎬 Supoclip AI Shorts & Google Cloud Vertex AI Integration Recipe

## Overview
How to wire `supoclip` (AI Shorts / Reels / TikTok video clipping engine) to Google Cloud Vertex AI using `pydantic-ai` and active ADC credentials instead of third-party API keys (OpenAI / Groq).

---

## 🔧 1. Vertex AI Adapter for `pydantic-ai` (`gcp_vertex_adapter.py`)

In modern `pydantic-ai` (>= 0.1.0 / 1.0+), Google Vertex integration is configured via `GoogleProvider`:

```python
import os
from pathlib import Path
import certifi
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

def ensure_ssl_environment():
    \"\"\"Fix stale/missing SSL_CERT_FILE in virtualenvs causing TLS failures.\"\"\"
    ssl_cert = os.environ.get("SSL_CERT_FILE")
    if not ssl_cert or not Path(ssl_cert).exists():
        os.environ["SSL_CERT_FILE"] = certifi.where()

def get_vertex_model(model_name: str = "gemini-3.1-pro-preview") -> GoogleModel:
    ensure_ssl_environment()
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("CLOUDSDK_CORE_PROJECT")
    # For Gemini 3 reasoning & flagship models, use global or us-central1
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

    provider = GoogleProvider(
        vertexai=True,
        project=project,
        location=location,
    )
    return GoogleModel(model_name, provider=provider)
```

---

## ⚙️ 2. Environment Configuration (`backend/.env`)

```ini
# Primary reasoning LLM for viral segment extraction
LLM=google-vertex:gemini-3.1-pro-preview
RERANK_LLM=google-vertex:gemini-3.1-pro-preview

# Speed alternative for rapid batching
# LLM=google-vertex:gemini-3-flash-preview

GOOGLE_CLOUD_PROJECT=project-2826e39f-abdc-4c1d-8b5
GOOGLE_CLOUD_LOCATION=global
```

---

## 🎯 3. Verification Command

Verify that Vertex AI returns structured `TranscriptAnalysis` with segments, virality score, and hooks:
```bash
uv run python -c "
import asyncio
from src.ai import get_most_relevant_parts_by_transcript
from src.config import get_config

async def test():
    cfg = get_config()
    print(f'Active LLM: {cfg.llm}')
    res = await get_most_relevant_parts_by_transcript('test transcript...')
    print(f'Segments extracted: {len(res.most_relevant_segments)}')

asyncio.run(test())
"
```
