# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/subagent_research_schema_and_offline_mock_hygiene.md"
# purpose: "Protocol for robust subagent research schemas, Pydantic V2 URL platform inference, and deterministic offline mock fallbacks."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ Subagent Research Schema & Offline Mock Resilience Protocol

## 1. Problem Statement
When orchestrating autonomous swarm workers (such as `gerych_researcher`) executing intelligence tasks (`comment_mining`, `ad_library_teardown`, `outlier_posts`, `transcript_intelligence`):
1. **LLM Payload Drift**: Subagents often invoke endpoints passing unstructured or natural parameters (e.g. `{"url": "https://tiktok.com/@brand/video/123"}`) omitting strict enum requirements like `platform="tiktok"` or using varying keys (`url` vs `post_url`). Strict Pydantic models reject these with `ValidationError: Field required (platform)`, triggering costly repair loops.
2. **Third-Party API Fragility**: Research scraping APIs may be unauthenticated (missing `API_KEY` in local/staging environments), rate-limited, or experience network drops. Hard failures abort swarm pipelines prematurely.

## 2. Invariant Rules

### Rule 1: Pydantic V2 Pre-Validation URL Sniffing
Every research input model accepting a URL must implement `@model_validator(mode="before")`:
```python
from pydantic import BaseModel, model_validator
from enum import Enum

class SocialPlatform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"

class CommentMiningRequest(BaseModel):
    post_url: str
    platform: SocialPlatform = SocialPlatform.TIKTOK
    max_comments: int = 100

    @model_validator(mode="before")
    @classmethod
    def infer_platform_and_normalize(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize url alias
            url = data.get("post_url") or data.get("url")
            if url:
                data["post_url"] = str(url)
                if not data.get("platform"):
                    url_lower = str(url).lower()
                    if "tiktok.com" in url_lower:
                        data["platform"] = SocialPlatform.TIKTOK
                    elif "instagram.com" in url_lower:
                        data["platform"] = SocialPlatform.INSTAGRAM
                    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
                        data["platform"] = SocialPlatform.YOUTUBE
                    elif "reddit.com" in url_lower:
                        data["platform"] = SocialPlatform.REDDIT
                    elif "linkedin.com" in url_lower:
                        data["platform"] = SocialPlatform.LINKEDIN
                    elif "twitter.com" in url_lower or "x.com" in url_lower:
                        data["platform"] = SocialPlatform.TWITTER
        return data
```

### Rule 2: Deterministic Zero-Cost Offline Mock Layer
Client libraries communicating with external intelligence services (`services/dnk_content_intelligence/client.py`) must never raise uncaught connection or missing credential errors during normal swarm runs.
If `api_key` is absent or the live API fails/times out, the client must seamlessly fall back to realistic, deterministic mock telemetry:
- Complete with customer pain points, objections, and verbatim quotes.
- Correctly matching timestamps and duration metrics to avoid assertion mismatches.
- Logged clearly as `[OFFLINE MOCK FALLBACK]` for transparency.

### Rule 3: Swarm Coordinator Single-Dispatch Mapping
Swarm coordinators (`core/orchestrator/swarm_coordinator.py`) must cleanly map researcher domain actions directly into the engine:
```python
# In SwarmCoordinator:
if agent == "gerych_researcher":
    return self._execute_researcher_worker(action, payload)
```
This isolates research operations from generic shell commands and prevents tool budget exhaustion.
