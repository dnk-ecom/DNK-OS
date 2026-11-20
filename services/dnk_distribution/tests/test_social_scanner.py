# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/tests/test_social_scanner.py"
# purpose: "Comprehensive Unit & Contract Tests for Social Scanner Engine"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import pytest
from unittest.mock import patch, MagicMock
from services.dnk_distribution.src.social_scanner import (
    SocialMediaScanner,
    SocialScanResult,
    social_scanner,
)
from services.dnk_distribution.src.social_feedback import SocialPlatform
from services.dnk_distribution.src.service import scan_social_content
from services.dnk_distribution.contracts.schemas import SocialScanRequest, SocialScanResponse
from services.dnk_distribution.mcp_server import mcp


def test_platform_detection():
    scanner = SocialMediaScanner()
    assert scanner.detect_platform("https://vt.tiktok.com/ZSpvdyVRv/") == SocialPlatform.TIKTOK
    assert scanner.detect_platform("https://www.tiktok.com/@user/photo/12345") == SocialPlatform.TIKTOK
    assert scanner.detect_platform("https://reddit.com/r/ClaudeCode/comments/xyz/") == SocialPlatform.REDDIT
    assert scanner.detect_platform("https://youtube.com/shorts/abcde") == SocialPlatform.YOUTUBE
    assert scanner.detect_platform("https://x.com/tech_lead/status/987654") == SocialPlatform.TWITTER


def test_classify_and_distill_domains():
    scanner = SocialMediaScanner()

    # DNK OS Dev rule
    diamonds_dev = scanner.classify_and_distill(
        text_corpus="Before changing anything list every file you'll need. Never write code without supervisor.",
        title="What is your best CLAUDE.md line?",
    )
    categories_dev = [d.category for d in diamonds_dev]
    assert "dnk_os_dev" in categories_dev

    # Marketing & SMM
    diamonds_smm = scanner.classify_and_distill(
        text_corpus="Use this 3-second hook to make your Reels go viral on FYP with high retention.",
        title="SMM Secret for 2026",
    )
    categories_smm = [d.category for d in diamonds_smm]
    assert "marketing_smm" in categories_smm

    # Site builder
    diamonds_site = scanner.classify_and_distill(
        text_corpus="Double your Shopify store conversion rate with this CRO theme block and fast checkout.",
        title="E-Commerce Storefront Secrets",
    )
    categories_site = [d.category for d in diamonds_site]
    assert "site_builder" in categories_site

    # Idea radar
    diamonds_idea = scanner.classify_and_distill(
        text_corpus="Found an untapped microsaas problem for niche creators to automate workflows.",
        title="Micro-SaaS Opportunity",
    )
    categories_idea = [d.category for d in diamonds_idea]
    assert "idea_radar" in categories_idea


def test_scan_tiktok_fallback_extraction():
    scanner = SocialMediaScanner()
    test_url = "https://www.tiktok.com/@dide89355/photo/7706105451372416289"

    # Test offline fallback parsing
    with patch("urllib.request.urlopen", side_effect=Exception("Network sandbox")):
        res = scanner.scan(test_url)
        assert res.platform == SocialPlatform.TIKTOK
        assert res.author == "@dide89355"
        assert res.content_type == "carousel_slides"
        assert len(res.diamonds) > 0


def test_contract_schemas_serialization():
    req = SocialScanRequest(url="https://reddit.com/r/ClaudeCode/comments/1/")
    assert req.url.startswith("https://")

    sample_result = SocialScanResult(
        url="https://vt.tiktok.com/ZSpvdyVRv/",
        resolved_url="https://www.tiktok.com/@dide89355/photo/7706105451372416289",
        platform=SocialPlatform.TIKTOK,
        author="@dide89355",
        title="#claude #askreddit #xyzcba #fyp #viral",
        content_type="carousel_slides",
        media_count=13,
        media_urls=["https://example.com/slide1.jpg"],
        suggested_action="Assimilate instruction diamonds into AGENTS.md",
    )

    resp = SocialScanResponse(success=True, data=sample_result)
    dumped = resp.model_dump()
    assert dumped["success"] is True
    assert dumped["data"]["media_count"] == 13
    assert dumped["data"]["author"] == "@dide89355"


def test_mcp_tool_registration():
    # Verify tool is registered on FastMCP instance
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "distribution_scan_social_content" in tool_names
