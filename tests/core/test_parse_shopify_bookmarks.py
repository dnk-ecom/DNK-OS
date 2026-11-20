#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_parse_shopify_bookmarks.py"
# purpose: "Unit tests for High-Speed Shopify Bookmarks Intelligence Scanner and FastMCP Query Tool (DEC-137/DEC-152)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
import pytest
from pathlib import Path
from scripts.shopify.parse_shopify_bookmarks import (
    BookmarkParser,
    sanitize_url,
    format_timestamp,
    classify_bookmark,
    is_relevant,
    scan_bookmarks,
    query_bookmarks,
)


SAMPLE_BOOKMARKS_HTML = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="1784303919">Dev tools</H3>
    <DL><p>
        <DT><H3 ADD_DATE="1784303919">Shopify</H3>
        <DL><p>
            <DT><A HREF="https://github.com/barrel/devkit?utm_source=test&ref=xyz" ADD_DATE="1720569600">barrel/devkit: Advanced Shopify themes</A>
            <DT><A HREF="https://github.com/jaynatividad1489/shopify-cart-drawer" ADD_DATE="1721260800">jaynatividad1489/shopify-cart-drawer: AJAX Cart Drawer</A>
            <DT><A HREF="https://github.com/joshhh62/shopify-cro-engine" ADD_DATE="1722470400">joshhh62/shopify-cro-engine: Prioritized CRO audits</A>
            <DT><A HREF="https://github.com/0ddlab/shopify-hermes-skill" ADD_DATE="1717027200">0ddlab/shopify-hermes-skill: Hermes agent skill for Shopify</A>
            <DT><A HREF="https://github.com/lsb11/shopify-capi-validator" ADD_DATE="1721865600">lsb11/shopify-capi-validator: Validate Meta CAPI</A>
            <DT><A HREF="https://github.com/Breadpitt1387/product-upload" ADD_DATE="1716336000">Breadpitt1387/product-upload: Shopify product uploader</A>
            <DT><A HREF="https://shopify.dev/changelog" ADD_DATE="1710000000">Shopify Developer Changelog</A>
            <DT><A HREF="https://github.com/obsidianmd/obsidian-releases" ADD_DATE="1710000000">Obsidian plugins and theme list</A>
        </DL><p>
    </DL><p>
</DL><p>
"""


def test_sanitize_url():
    raw = "https://github.com/barrel/devkit?utm_source=twitter&utm_medium=social&ref=partner&id=123"
    cleaned = sanitize_url(raw)
    assert "utm_source" not in cleaned
    assert "utm_medium" not in cleaned
    assert "ref" not in cleaned
    assert "id=123" in cleaned
    assert cleaned.startswith("https://github.com/barrel/devkit?id=123")


def test_format_timestamp():
    date_str = format_timestamp("1720569600")
    assert date_str == "2024-07-10"
    assert format_timestamp("") == "Unknown"
    assert format_timestamp("invalid") == "Unknown"


def test_relevance_and_exclusion():
    # Relevant Shopify theme
    assert is_relevant({
        "title": "Shopify Cart Drawer",
        "url": "https://github.com/test/cart",
        "folder": "Shopify"
    }) is True

    # Generic Obsidian theme (should be excluded as false positive)
    assert is_relevant({
        "title": "Obsidian plugins and theme list",
        "url": "https://github.com/obsidianmd/obsidian-releases",
        "folder": "Obsidian > Themes"
    }) is False


def test_classify_bookmark():
    # Theme Engineering
    assert classify_bookmark({
        "title": "barrel/devkit: Advanced Shopify themes",
        "url": "https://github.com/barrel/devkit",
        "folder": "Dev tools > Shopify"
    }) == "shopify_core_and_themes"

    # CRO & Funnels
    assert classify_bookmark({
        "title": "joshhh62/shopify-cro-engine: Prioritized CRO audits",
        "url": "https://github.com/joshhh62/shopify-cro-engine",
        "folder": "Dev tools > Shopify"
    }) == "cro_funnels_and_ux"

    # AI Agents & MCP
    assert classify_bookmark({
        "title": "0ddlab/shopify-hermes-skill: Hermes agent skill for Shopify",
        "url": "https://github.com/0ddlab/shopify-hermes-skill",
        "folder": "Dev tools > Shopify"
    }) == "ai_agents_mcp_and_automation"

    # Marketing & Tracking
    assert classify_bookmark({
        "title": "lsb11/shopify-capi-validator: Validate Meta CAPI",
        "url": "https://github.com/lsb11/shopify-capi-validator",
        "folder": "Dev tools > Shopify"
    }) == "marketing_ads_and_tracking"

    # Apps & Operations
    assert classify_bookmark({
        "title": "Breadpitt1387/product-upload: Shopify product uploader",
        "url": "https://github.com/Breadpitt1387/product-upload",
        "folder": "Dev tools > Shopify"
    }) == "apps_apis_and_backend_ops"

    # Official Portals
    assert classify_bookmark({
        "title": "Shopify Developer Changelog",
        "url": "https://shopify.dev/changelog",
        "folder": "Dev tools > Shopify"
    }) == "official_portals_and_community"


def test_scan_bookmarks_from_html(tmp_path: Path):
    html_file = tmp_path / "test_bookmarks.html"
    html_file.write_text(SAMPLE_BOOKMARKS_HTML, encoding="utf-8")

    items = scan_bookmarks(str(html_file))
    assert len(items) == 7  # Obsidian item excluded

    urls = [it["url"] for it in items]
    assert "https://github.com/barrel/devkit" in urls
    assert "https://github.com/obsidianmd/obsidian-releases" not in urls


def test_query_bookmarks_tool(tmp_path: Path):
    db_file = tmp_path / "test_db.json"
    dummy_data = {
        "items": [
            {
                "title": "Clyro AI Theme Builder",
                "url": "https://app.clyro.com",
                "folder": "Tools",
                "category": "ai_agents_mcp_and_automation"
            },
            {
                "title": "Shopify Cart Drawer Component",
                "url": "https://github.com/test/cart-drawer",
                "folder": "Themes",
                "category": "shopify_core_and_themes"
            }
        ]
    }
    db_file.write_text(json.dumps(dummy_data), encoding="utf-8")

    # Query all
    res = query_bookmarks(db_path=str(db_file))
    assert res["success"] is True
    assert len(res["results"]) == 2

    # Query with keyword
    res_kw = query_bookmarks(query="clyro", db_path=str(db_file))
    assert len(res_kw["results"]) == 1
    assert res_kw["results"][0]["title"] == "Clyro AI Theme Builder"

    # Query with category
    res_cat = query_bookmarks(category="shopify_core_and_themes", db_path=str(db_file))
    assert len(res_cat["results"]) == 1
    assert "Cart Drawer" in res_cat["results"][0]["title"]
