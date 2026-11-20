# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_shopify_daily_pulse.py"
# purpose: "Deterministic unit tests for Shopify Developer Changelog Pulse Engine and FastMCP tool."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from pathlib import Path
import pytest
from scripts.shopify.shopify_daily_pulse import parse_and_filter_updates, generate_pulse_report
from core.kernel import FastMCPKernel, create_fastmcp_server


MOCK_SHOPIFY_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Shopify developer changelog</title>
    <item>
      <title>Liquid templates composition preview with block and partial tags</title>
      <description>&lt;p&gt;Liquid-first composition model with new block and partial tags.&lt;/p&gt;</description>
      <link>https://shopify.dev/changelog/liquid-first-preview</link>
      <pubDate>Fri, 13 Nov 2026 12:00:00 +0000</pubDate>
      <category>Developer Preview</category>
    </item>
    <item>
      <title>Unrelated Tax API change for POS</title>
      <description>&lt;p&gt;Updated tax rates for POS hardware terminal.&lt;/p&gt;</description>
      <link>https://shopify.dev/changelog/tax-pos</link>
      <pubDate>Thu, 12 Nov 2026 12:00:00 +0000</pubDate>
      <category>POS</category>
    </item>
    <item>
      <title>Checkout Function cart.deliverableLine cost modeling</title>
      <description>&lt;p&gt;Cart delivery cost modeling in checkout functions.&lt;/p&gt;</description>
      <link>https://shopify.dev/changelog/checkout-function-cart</link>
      <pubDate>Wed, 11 Nov 2026 12:00:00 +0000</pubDate>
      <category>API</category>
    </item>
  </channel>
</rss>
"""


def test_parse_and_filter_updates():
    updates = parse_and_filter_updates(MOCK_SHOPIFY_RSS, limit=10)
    assert len(updates) == 2  # The POS item is filtered out
    assert updates[0]["title"] == "Liquid templates composition preview with block and partial tags"
    assert "liquid" in updates[0]["matched_topics"]
    assert "block" in updates[0]["matched_topics"]
    assert updates[1]["title"] == "Checkout Function cart.deliverableLine cost modeling"
    assert "cart" in updates[1]["matched_topics"]


def test_generate_pulse_report(tmp_path: Path):
    updates = parse_and_filter_updates(MOCK_SHOPIFY_RSS, limit=5)
    report_file = tmp_path / "SHOPIFY_TEST_PULSE.md"
    generate_pulse_report(updates, report_file)
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Liquid templates composition preview" in content
    assert "DNK-MRH-HEADER" in content


@pytest.mark.asyncio
async def test_fastmcp_audit_shopify_platform_pulse():
    kernel = FastMCPKernel()
    server = create_fastmcp_server(kernel=kernel)
    tool = server._tool_manager.get_tool("audit_shopify_platform_pulse")
    assert tool is not None

    # Call with a small limit
    res_str = tool.fn(limit=2)
    res = json.loads(res_str)
    assert res["success"] is True
    assert "updates" in res
    assert len(res["updates"]) <= 2
