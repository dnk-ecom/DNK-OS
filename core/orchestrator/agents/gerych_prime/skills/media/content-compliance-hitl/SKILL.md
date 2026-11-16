---
name: content-compliance-hitl
description: Use when validating content tone of voice, FTC rules, and managing dual Telegram/Web HITL approval gates.
category: media
---

# Content Brand Compliance & Human-In-The-Loop (HITL) Gate

## Overview
This skill operationalizes **Phase 3** of the 2026 Autonomous Content Intelligence Engine. It bridges automated creative generation (from `gerych_researcher` and `dnk_video_ai_creator`) with strict **Brand Safety & Compliance Gates** (inspired by Microsoft Content Generation Solution Accelerator) and an interactive **Human-in-the-Loop (HITL) Review Inbox** with dual Web Canvas & Telegram inline actions (inspired by LangChain Social Media Agent).

## Core Architecture
1. **Brand Compliance Engine (`services/dnk_content_intelligence/brand_compliance.py`)**:
   - Deterministic policy verification for:
     - Banned words / sensitive brand terms.
     - Unsubstantiated medical/health claims (FDA/FTC guard).
     - Deceptive financial or income guarantees ("make $10k overnight").
     - Competitor slander and aggressive profanity.
     - Mandatory FTC disclosure validation (`#ad`, `#sponsored`, `#partner`) for promotional media.
     - Punctuation & excitement score gating.
2. **Dual-Channel HITL Gate (`services/dnk_content_intelligence/hitl_gate.py`)**:
   - Queues content drafts (`PENDING_APPROVAL`, `REVISION_REQUESTED`, `APPROVED`, `REJECTED`).
   - Generates interactive Telegram inline button cards (`[✅ Схвалити]`, `[✏️ Редагувати]`, `[❌ Відхилити]`).
   - Supports direct webhook callbacks from Telegram Bot APIs.
3. **FastAPI Endpoints (`apps/api/routers/hitl_content_router.py`)**:
   - `POST /api/v1/content/compliance/check`
   - `POST /api/v1/content/hitl/submit`
   - `GET /api/v1/content/hitl/inbox`
   - `POST /api/v1/content/hitl/{request_id}/decision`
   - `POST /api/v1/content/hitl/telegram/callback`

## Python Usage Recipe

```python
from services.dnk_content_intelligence.brand_compliance import BrandComplianceEngine, DEFAULT_REBURN_PROFILE
from services.dnk_content_intelligence.hitl_gate import ContentHITLGate, ContentDraftCreate, ContentType

compliance_engine = BrandComplianceEngine(default_profile=DEFAULT_REBURN_PROFILE)
gate = ContentHITLGate(compliance_engine=compliance_engine)

# 1. Submit a generated creative draft
draft = gate.submit_draft(
    ContentDraftCreate(
        title="Reburn Pre-Workout Launch Reel",
        caption="Stop wasting energy on generic powders. Reburn fuels elite focus. #ad #fitness",
        content_type=ContentType.VIDEO_SHORT,
        target_platforms=["tiktok", "instagram_reels", "youtube_shorts"],
        media_url="assets/ugc/reburn_hero_short.mp4",
        is_promotional=True,
    )
)

print(f"Draft Status: {draft.status} (Compliant: {draft.compliance_report.is_compliant})")

# 2. Generate Telegram Card for Founder Review
tg_card = gate.format_telegram_approval_message(draft)
print(tg_card["chat_text"])

# 3. Simulate Founder Approving via Telegram Button
callback_result = gate.process_telegram_callback(f"content_approve:{draft.request_id}", user_id="Maxim")
print("Approval Result:", callback_result["status"])
```
