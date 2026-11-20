# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/src/social_scanner.py"
# purpose: "Social Media Intelligence Scanner & Diamond Extraction Engine for dnk_distribution"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.dnk_distribution.src.social_feedback import SocialPlatform

logger = logging.getLogger("dnk.distribution.social_scanner")


class SocialScanDiamond(BaseModel):
    category: str  # dnk_os_dev | marketing_smm | site_builder | idea_radar
    headline: str
    detail: str
    actionable_directive: str


class SocialScanResult(BaseModel):
    url: str
    resolved_url: str
    platform: SocialPlatform
    author: str
    title: str
    content_type: str  # carousel_slides | video | post | thread
    media_count: int = 0
    media_urls: List[str] = Field(default_factory=list)
    extracted_text_blocks: List[str] = Field(default_factory=list)
    diamonds: List[SocialScanDiamond] = Field(default_factory=list)
    suggested_action: str
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class SocialMediaScanner:
    """
    Autonomous scanner capable of resolving and extracting intelligence from social media posts
    (TikTok carousels/videos, Reddit discussions, YouTube, Twitter) without brittle scraping blocks.
    """

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"

    def detect_platform(self, url: str) -> SocialPlatform:
        url_lower = url.lower()
        if "tiktok.com" in url_lower:
            return SocialPlatform.TIKTOK
        elif "reddit.com" in url_lower:
            return SocialPlatform.REDDIT
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return SocialPlatform.YOUTUBE
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return SocialPlatform.TWITTER
        elif "instagram.com" in url_lower:
            return SocialPlatform.INSTAGRAM
        elif "linkedin.com" in url_lower:
            return SocialPlatform.LINKEDIN
        return SocialPlatform.TIKTOK

    def resolve_redirect(self, url: str) -> str:
        """Resolves shortlinks (e.g. vt.tiktok.com) to canonical URLs."""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent}, method="HEAD")
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.geturl()
        except Exception:
            return url

    def scan_tiktok(self, canonical_url: str) -> Dict[str, Any]:
        """Fetches TikTok metadata, slides, or video URLs via clean API fallback."""
        encoded_url = urllib.parse.quote(canonical_url)
        api_url = f"https://www.tikwm.com/api/?url={encoded_url}"
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("code") == 0:
                    d = data.get("data", {})
                    author_nick = d.get("author", {}).get("nickname", "unknown")
                    author_id = d.get("author", {}).get("unique_id", "")
                    author_str = f"{author_nick} (@{author_id})" if author_id else author_nick
                    images = d.get("images", [])
                    is_carousel = bool(images)
                    media_urls = images if is_carousel else ([d.get("play", "")] if d.get("play") else [])
                    return {
                        "author": author_str,
                        "title": d.get("title", ""),
                        "content_type": "carousel_slides" if is_carousel else "video",
                        "media_urls": media_urls,
                        "raw": d,
                    }
        except Exception as e:
            logger.warning(f"TikTok scan fallback notice: {e}")

        # Fallback minimal extraction from URL structure
        match = re.search(r"@([^/]+)/(?:photo|video)/(\d+)", canonical_url)
        if match:
            return {
                "author": f"@{match.group(1)}",
                "title": f"TikTok Item {match.group(2)}",
                "content_type": "carousel_slides" if "/photo/" in canonical_url else "video",
                "media_urls": [],
                "raw": {"id": match.group(2)},
            }
        return {"author": "unknown", "title": "TikTok Post", "content_type": "post", "media_urls": [], "raw": {}}

    def scan_reddit(self, canonical_url: str) -> Dict[str, Any]:
        """Fetches Reddit thread metadata & top comments via public JSON endpoint."""
        clean_url = canonical_url.split("?")[0].rstrip("/")
        json_url = f"{clean_url}.json"
        try:
            req = urllib.request.Request(json_url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, list) and len(data) > 0:
                    post_data = data[0].get("data", {}).get("children", [{}])[0].get("data", {})
                    title = post_data.get("title", "")
                    author = post_data.get("author", "unknown")
                    selftext = post_data.get("selftext", "")
                    comments = []
                    if len(data) > 1:
                        for c in data[1].get("data", {}).get("children", []):
                            body = c.get("data", {}).get("body")
                            if body:
                                comments.append(body)
                    return {
                        "author": f"u/{author}",
                        "title": title,
                        "content_type": "thread",
                        "media_urls": [],
                        "text_blocks": [selftext] + comments[:10],
                        "raw": post_data,
                    }
        except Exception as e:
            logger.warning(f"Reddit scan error: {e}")
        return {"author": "unknown", "title": "Reddit Thread", "content_type": "thread", "media_urls": [], "raw": {}}

    def classify_and_distill(self, text_corpus: str, title: str) -> List[SocialScanDiamond]:
        """Classifies content into domain diamonds and derives actionable directives."""
        combined = f"{title} {text_corpus}".lower()
        diamonds: List[SocialScanDiamond] = []

        # 1. DNK OS Dev & Agent Governance
        if any(k in combined for k in ["claude", "claude.md", "agents.md", "prompt", "subagent", "supervisor", "llm", "audit"]):
            diamonds.append(SocialScanDiamond(
                category="dnk_os_dev",
                headline="Agentic Execution & Governance Rule",
                detail="Contains instruction-tuning, audit-first, or supervisor-subagent operational invariants.",
                actionable_directive="Integrate verified rules into docs/architecture/DECISION_REGISTRY_ADHD.md and AGENTS.md.",
            ))

        # 2. Marketing & SMM
        if any(k in combined for k in ["viral", "fyp", "hook", "smm", "retention", "marketing", "reels", "traffic"]):
            diamonds.append(SocialScanDiamond(
                category="marketing_smm",
                headline="High-Engagement Viral Pattern",
                detail="Identified viral content structure, visual pacing, or engagement retention triggers.",
                actionable_directive="Feed pattern into services/dnk_distribution (RLSF social feedback) and services/dnk_media.",
            ))

        # 3. Site Builder & E-Commerce
        if any(k in combined for k in ["shopify", "website", "landing", "pdp", "cro", "checkout", "store", "ecommerce"]):
            diamonds.append(SocialScanDiamond(
                category="site_builder",
                headline="Conversion Rate & Storefront Architecture",
                detail="Features storefront optimization, theme blocks, or conversion rate boosting strategies.",
                actionable_directive="Implement as Liquid Theme Block 2.0 in services/dnk_shopify/DNK_Ecom/blocks/.",
            ))

        # 4. Idea Radar & Micro-SaaS
        if any(k in combined for k in ["idea", "microsaas", "saas", "business", "niche", "opportunity", "problem"]):
            diamonds.append(SocialScanDiamond(
                category="idea_radar",
                headline="Commercial Niche / Micro-SaaS Opportunity",
                detail="Extracted market demand signal, unmet developer friction, or monetization wedge.",
                actionable_directive="Submit to hypokiln_assimilated and roast_room_assimilated for 12-board evaluation.",
            ))

        if not diamonds:
            diamonds.append(SocialScanDiamond(
                category="marketing_smm",
                headline="General Social Media Post",
                detail="General audience content or multimedia showcase.",
                actionable_directive="Archive in SCONES episodic memory for audience preference tracking.",
            ))
        return diamonds

    def scan(self, url: str) -> SocialScanResult:
        """Main entry point to scan any social post URL and produce structured intelligence."""
        resolved = self.resolve_redirect(url)
        platform = self.detect_platform(resolved)

        meta: Dict[str, Any] = {}
        text_blocks: List[str] = []

        if platform == SocialPlatform.TIKTOK:
            meta = self.scan_tiktok(resolved)
        elif platform == SocialPlatform.REDDIT:
            meta = self.scan_reddit(resolved)
            text_blocks = meta.get("text_blocks", [])
        else:
            meta = {"author": "unknown", "title": f"Social content from {platform.value}", "content_type": "post", "media_urls": [], "raw": {}}

        title = meta.get("title", "")
        author = meta.get("author", "unknown")
        content_type = meta.get("content_type", "post")
        media_urls = meta.get("media_urls", [])

        # Distill diamonds
        corpus = " ".join(text_blocks)
        diamonds = self.classify_and_distill(text_corpus=corpus, title=title)

        # Formulate suggested action
        primary_cat = diamonds[0].category if diamonds else "general"
        if primary_cat == "dnk_os_dev":
            suggested_action = "Assimilate instruction diamonds into AGENTS.md and execute verification via verify_all.sh."
        elif primary_cat == "marketing_smm":
            suggested_action = "Deploy viral hook to dnk_distribution social feedback loop and generate HyperFrames media."
        elif primary_cat == "site_builder":
            suggested_action = "Generate companion Shopify CRO block in services/dnk_shopify."
        else:
            suggested_action = "Stress-test hypothesis in hypokiln idea engine."

        return SocialScanResult(
            url=url,
            resolved_url=resolved,
            platform=platform,
            author=author,
            title=title,
            content_type=content_type,
            media_count=len(media_urls),
            media_urls=media_urls,
            extracted_text_blocks=text_blocks,
            diamonds=diamonds,
            suggested_action=suggested_action,
            raw_metadata=meta.get("raw", {}),
        )


social_scanner = SocialMediaScanner()
