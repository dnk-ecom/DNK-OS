# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/src/merchant_feed.py"
# purpose: "Google Merchant Center & Meta Catalog RSS 2.0 / XML Product Feed Generator"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import html
from pathlib import Path
from typing import List, Optional
from services.dnk_distribution.src.llms_txt import CatalogItem, StoreProfile


def generate_google_merchant_xml(
    profile: StoreProfile,
    products: List[CatalogItem],
    image_base_url: Optional[str] = None,
) -> str:
    """
    Generates a valid Google Merchant Center / Google Shopping RSS 2.0 XML feed.
    Enables free organic product listings across Google Shopping and Meta Catalog.
    """
    safe_title = html.escape(profile.name)
    safe_link = html.escape(profile.base_url)
    safe_desc = html.escape(profile.tagline)

    items_xml: List[str] = []
    for p in products:
        item_id = html.escape(p.sku or p.handle)
        item_title = html.escape(p.title)
        item_desc = html.escape(p.description)
        item_link = html.escape(p.url or f"{profile.base_url.rstrip('/')}/products/{p.handle}")
        
        # Clean price formatting (e.g. 2400.00 UAH)
        clean_num = "".join(c for c in p.price if c.isdigit() or c in ".,").replace(",", ".") or "0.00"
        if "." not in clean_num:
            clean_num = f"{clean_num}.00"
        price_str = f"{clean_num} {p.currency}"

        avail = "in_stock" if p.in_stock else "out_of_stock"
        img_url = image_base_url or f"{profile.base_url.rstrip('/')}/cdn/products/{p.handle}.jpg"

        item_xml = f"""    <item>
      <g:id>{item_id}</g:id>
      <g:title>{item_title}</g:title>
      <g:description>{item_desc}</g:description>
      <g:link>{item_link}</g:link>
      <g:image_link>{html.escape(img_url)}</g:image_link>
      <g:condition>new</g:condition>
      <g:availability>{avail}</g:availability>
      <g:price>{price_str}</g:price>
      <g:brand>{safe_title}</g:brand>
      <g:identifier_exists>no</g:identifier_exists>
    </item>"""
        items_xml.append(item_xml)

    joined_items = "\n".join(items_xml)
    xml_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
  <channel>
    <title>{safe_title}</title>
    <link>{safe_link}</link>
    <description>{safe_desc}</description>
{joined_items}
  </channel>
</rss>"""
    return xml_feed


def export_merchant_feed(
    output_path: Path,
    profile: StoreProfile,
    products: List[CatalogItem],
    image_base_url: Optional[str] = None,
) -> str:
    """Exports Google Merchant Center XML feed to a local file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    xml_content = generate_google_merchant_xml(profile, products, image_base_url)
    output_path.write_text(xml_content, encoding="utf-8")
    return str(output_path)
