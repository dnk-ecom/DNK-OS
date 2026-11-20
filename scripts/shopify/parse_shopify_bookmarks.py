#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/shopify/parse_shopify_bookmarks.py"
# purpose: "High-Speed Zero-Bloat Terminal Bookmark Scanner for Shopify, Themes, CRO, Agents & E-Commerce (DEC-137/DEC-152)."
# canonical_source: true
# alters_files: [
#   "docs/notes/shopify_bookmarks/shopify_bookmarks.json",
#   "docs/notes/shopify_bookmarks/SHOPIFY_BOOKMARKS_INDEX_2026-11-18.md"
# ]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
Shopify Bookmarks Intelligence Scanner:
Parses Netscape Bookmark HTML archives in RAM (<0.5s) with zero browser overhead.
Filters, scores, and categorizes bookmarks into 7 core pillars:
  1. shopify_core_and_themes (Themes, Liquid AST, Theme Blocks 2.0, CSS/Design Systems, Cart Drawers)
  2. cro_funnels_and_ux (Conversion Optimization, A/B Testing, Bundles, Upsells, VSL, PDP)
  3. ai_agents_mcp_and_automation (Shopify MCP Servers, Hermes Agent Skills, AI Site Builders, Ads Agents)
  4. store_audits_spies_and_intel (Store Scrapers, App Review Crawlers, DTC Benchmarks, SEO Audits)
  5. marketing_ads_and_tracking (Meta CAPI, TikTok Events, Klaviyo, SMM Panels, Attribution)
  6. apps_apis_and_backend_ops (Custom Apps, Shopify GraphQL API, Bulk Product Uploads, Crypto Payouts)
  7. official_portals_and_community (Partner Dashboards, Dev Changelogs, Awesome Shopify, Tutorials)
"""

import argparse
import datetime
import html.parser
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

CORE_KEYWORDS = [
    "shopify", "liquid", "polaris", "storefront", "dawn", "horizon", "cart drawer",
    "themekit", "theme-tools", "clyro", "refero", "e-commerce", "ecommerce", "dropship",
    "dropshipping", "klaviyo", "capi validator", "adspy", "scrollstash", "convertflow"
]

SECONDARY_KEYWORDS = [
    "theme", "cart", "checkout", "cro", "funnel", "upsell", "cross-sell", "pdp",
    "product upload", "landing page", "ads", "marketing", "site builder"
]

EXCLUDED_KEYWORDS = [
    "obsidian", "vscode", "sublime", "terminal theme", "gtk theme", "iterm", "zsh theme",
    "gnome", "kde", "oh-my-zsh"
]

CATEGORY_METADATA = {
    "shopify_core_and_themes": {
        "title": "Shopify Core, Liquid & Theme Engineering",
        "badge": "🎨",
        "desc": "Liquid engines, Theme Blocks 2.0, devkits, component systems (Smelt/Vue/Tailwind), AJAX Cart Drawers, Refero styles."
    },
    "cro_funnels_and_ux": {
        "title": "CRO, Funnels & Conversion UX",
        "badge": "📈",
        "desc": "Conversion Rate Optimization, A/B testing frameworks, Sticky ATC, Bundles, Upsells, VSL funnels, ScrollStash DTC."
    },
    "ai_agents_mcp_and_automation": {
        "title": "AI Agents, MCP Servers & E-Com Automation",
        "badge": "🤖",
        "desc": "Shopify MCP servers, Hermes Agent Shopify skills, Claude/Cursor e-commerce skills, Manus site builders, AI growth agents."
    },
    "store_audits_spies_and_intel": {
        "title": "Store Audits, Intelligence & Competitive Reverse-Engineering",
        "badge": "🔍",
        "desc": "UX reverse engineering (Hoverify), store scrapers, App Store review crawlers, GEO-AI (llms.txt), tech datasets."
    },
    "marketing_ads_and_tracking": {
        "title": "Marketing, Paid Ads & Event Tracking",
        "badge": "🎯",
        "desc": "Meta CAPI & TikTok Events validators, Claude Ads / AI Ads strategies, Klaviyo email retention, SMM panel automation."
    },
    "apps_apis_and_backend_ops": {
        "title": "Shopify Apps, APIs & Store Operations",
        "badge": "⚙️",
        "desc": "Shopify GraphQL & Admin APIs, ShopifySharp, bulk product uploaders, CSV data wizards, fulfillment dashboards."
    },
    "official_portals_and_community": {
        "title": "Official Shopify Portals, Changelog & Knowledge Hubs",
        "badge": "📚",
        "desc": "Shopify Partner Dashboards, Dev Changelog/Pulse, Awesome Shopify curated lists, BrandUp Factory guides."
    }
}


class BookmarkParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_folder = []
        self.bookmarks = []
        self.in_h3 = False
        self.in_a = False
        self.current_title = ""
        self.current_href = ""
        self.current_add_date = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag_lower = tag.lower()
        if tag_lower == "h3":
            self.in_h3 = True
            self.current_title = ""
        elif tag_lower == "a":
            self.in_a = True
            self.current_title = ""
            self.current_href = attrs_dict.get("href", "").strip()
            self.current_add_date = attrs_dict.get("add_date", "").strip()

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == "h3":
            self.in_h3 = False
            folder_name = self.current_title.strip()
            if folder_name:
                self.current_folder.append(folder_name)
        elif tag_lower == "dl":
            if self.current_folder:
                self.current_folder.pop()
        elif tag_lower == "a":
            self.in_a = False
            title = self.current_title.strip() or self.current_href
            folder_path = " > ".join(self.current_folder) if self.current_folder else "Root"
            if self.current_href and not self.current_href.startswith("chrome://"):
                self.bookmarks.append({
                    "title": title,
                    "href": self.current_href,
                    "folder": folder_path,
                    "add_date": self.current_add_date
                })

    def handle_data(self, data):
        if self.in_h3 or self.in_a:
            self.current_title += data


def sanitize_url(raw_url: str) -> str:
    """Removes tracking query params while preserving necessary functional params."""
    try:
        parsed = urlparse(raw_url)
        if not parsed.scheme or not parsed.netloc:
            return raw_url
        query_dict = parse_qs(parsed.query, keep_blank_values=True)
        # Drop UTM and common tracking params
        tracking_keys = {
            "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "ref", "fbclid", "gclid", "ttclid", "mc_cid", "mc_eid"
        }
        filtered_query = {k: v for k, v in query_dict.items() if k.lower() not in tracking_keys}
        new_query = urlencode(filtered_query, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    except Exception:
        return raw_url


def format_timestamp(ts_str: str) -> str:
    """Converts unix timestamp string to ISO date YYYY-MM-DD."""
    if not ts_str:
        return "Unknown"
    try:
        ts = int(ts_str)
        # Handle microsecond vs second timestamps
        if ts > 10_000_000_000:
            ts = ts // 1_000_000
        return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return "Unknown"


def classify_bookmark(b: dict) -> str:
    """Classifies a bookmark into one of the 7 core pillars."""
    url = b.get("url") or b.get("href", "")
    text = f"{b['title']} {url} {b['folder']}".lower()

    # Priority 1: AI Agents, MCP Servers & Automation
    if any(k in text for k in [
        "mcp", "hermes", "agent", "claude-ads", "ai-ads", "manus", "site builder",
        "bankr", "skill", "ouroboros", "roast", "ai coding", "chatbot", "chattermate"
    ]):
        if any(c in text for c in ["shopify", "e-commerce", "ecommerce", "store", "ad", "marketing", "retail", "seller", "commerce"]):
            return "ai_agents_mcp_and_automation"

    # Priority 2: Shopify Themes & Liquid Engineering
    if any(k in text for k in [
        "theme", "liquid", "polaris", "storefront", "dawn", "horizon", "themekit",
        "theme-tools", "smelt", "devkit", "tailwind", "cart drawer", "clyro", "style"
    ]):
        return "shopify_core_and_themes"

    # Priority 3: CRO, Funnels & Conversion UX
    if any(k in text for k in [
        "cro", "conversion", "funnel", "upsell", "cross-sell", "bundle", "checkout",
        "cart", "refero", "scrollstash", "convertflow", "vsl", "landing page"
    ]):
        return "cro_funnels_and_ux"

    # Priority 4: Audits & Intelligence
    if any(k in text for k in [
        "audit", "crawler", "scraper", "dataset", "intelligence", "spy", "geo-ai",
        "review-crawler", "builtwith", "hoverify", "reverse engineering", "seo-crawler", "data-pipeline"
    ]):
        return "store_audits_spies_and_intel"

    # Priority 5: Marketing & Paid Ads Tracking
    if any(k in text for k in [
        "ads", "advertising", "marketing", "klaviyo", "capi", "pixel", "attribution",
        "smm", "meta ads", "tiktok ads", "leadgen"
    ]):
        return "marketing_ads_and_tracking"

    # Priority 6: Apps, APIs & Backend Ops
    if any(k in text for k in [
        "product-upload", "import-export", "fulfillment", "app", "listing", "dropship",
        "dropshipping", "payout", "seller", "shopifysharp", "oauth", "graphql", "api"
    ]):
        return "apps_apis_and_backend_ops"

    # Priority 7: Official Portals & Community
    return "official_portals_and_community"


def is_relevant(b: dict) -> bool:
    """Determines if the bookmark belongs to the Shopify/E-Commerce domain."""
    url = b.get("url") or b.get("href", "")
    title = b.get("title", "")
    folder = b.get("folder", "")
    title_url = f"{title} {url}".lower()
    full_text = f"{title_url} {folder}".lower()

    # Reject non-ecommerce tools (Obsidian, VSCode, iTerm, etc.) unless title/url specifically mentions Shopify/ecom
    if any(ex in title_url for ex in EXCLUDED_KEYWORDS):
        if not ("shopify" in title_url or "e-commerce" in title_url or "ecommerce" in title_url or "liquid" in title_url):
            return False

    if any(k in full_text for k in CORE_KEYWORDS):
        return True

    if any(k in full_text for k in SECONDARY_KEYWORDS):
        if any(ctx in full_text for ctx in ["shop", "store", "ecom", "market", "sell", "retail", "dtc", "order", "product", "conversion", "ad"]):
            return True

    return False


def scan_bookmarks(html_path: str) -> list[dict]:
    """Scans and extracts all relevant Shopify & E-commerce bookmarks."""
    parser = BookmarkParser()
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        parser.feed(f.read())

    processed = []
    seen_urls = set()

    for raw in parser.bookmarks:
        clean_url = sanitize_url(raw["href"])
        if clean_url in seen_urls:
            continue
        seen_urls.add(clean_url)

        item = {
            "title": raw["title"],
            "url": clean_url,
            "folder": raw["folder"],
            "date": format_timestamp(raw["add_date"]),
            "domain": urlparse(clean_url).netloc
        }

        if is_relevant(item):
            item["category"] = classify_bookmark(item)
            processed.append(item)

    return processed


def generate_markdown(items: list[dict], total_all: int) -> str:
    """Generates a structured Master Knowledge Base in Markdown."""
    by_category = {cat: [] for cat in CATEGORY_METADATA.keys()}
    for it in items:
        cat = it.get("category", "official_portals_and_community")
        by_category.setdefault(cat, []).append(it)

    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    md = []
    md.append("---")
    md.append("title: \"Shopify & E-Commerce Bookmarks Knowledge Base\"")
    md.append("description: \"Synthesized and categorized intelligence from Maxim's browser bookmarks for Shopify theme development, CRO, and AI agents.\"")
    md.append("mrh_id: \"docs/notes/shopify_bookmarks/SHOPIFY_BOOKMARKS_INDEX_2026-11-18.md\"")
    md.append("status: \"Active\"")
    md.append("version: \"1.0.0\"")
    md.append(f"updated: {now_iso[:10]}")
    md.append("type: \"index\"")
    md.append("domain: \"shopify\"")
    md.append("author: \"DNK-e.com Maksym & Antigravity\"")
    md.append("canonical_source: true")
    md.append("---")
    md.append("")
    md.append("> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)")
    md.append("> ```yaml")
    md.append("> # --- DNK-MRH-HEADER ---")
    md.append("> mrh_id: \"docs/notes/shopify_bookmarks/SHOPIFY_BOOKMARKS_INDEX_2026-11-18.md\"")
    md.append("> purpose: \"Synthesized Master Knowledge Base for Shopify & E-Commerce Bookmarks (DEC-137/DEC-152).\"")
    md.append("> canonical_source: true")
    md.append("> alters_files: []")
    md.append("> triggers_tasks: []")
    md.append("> status: \"Active\"")
    md.append("> version: \"1.0.0\"")
    md.append(f"> updated_at: \"{now_iso[:10]}\"")
    md.append("> author: \"DNK-e.com Maksym & Antigravity\"")
    md.append("> # --- END DNK-MRH-HEADER ---")
    md.append("> ```")
    md.append("")
    md.append("# 🛍️ База Знань: Shopify, Themes, CRO & Agentic E-Commerce (Bookmarks Digest)")
    md.append("")
    md.append(f"> **Час генерації**: `{now_iso}`  ")
    md.append(f"> **Всього проскановано закладок**: `{total_all}`  ")
    md.append(f"> **Виділено цільових Shopify / E-Commerce ресурсів**: `{len(items)}`  ")
    md.append("")
    md.append("## 📊 Розподіл по категоріях")
    md.append("")
    md.append("| Категорія | Значок | Кількість | Призначення для DNK OS |")
    md.append("| :--- | :---: | :---: | :--- |")
    for cat_id, meta in CATEGORY_METADATA.items():
        count = len(by_category.get(cat_id, []))
        md.append(f"| [{meta['title']}](#{cat_id}) | {meta['badge']} | **{count}** | {meta['desc']} |")
    md.append("")
    md.append("---")
    md.append("")

    for cat_id, meta in CATEGORY_METADATA.items():
        cat_items = by_category.get(cat_id, [])
        md.append(f"<a id=\"{cat_id}\"></a>")
        md.append(f"## {meta['badge']} {meta['title']} ({len(cat_items)} ресурсів)")
        md.append(f"*{meta['desc']}*")
        md.append("")
        if not cat_items:
            md.append("_Немає ресурсів у цій категорії._\n")
            continue

        md.append("| Ресурс / Репозиторій | Домен | Папка закладок | Дата |")
        md.append("| :--- | :--- | :--- | :--- |")
        for it in sorted(cat_items, key=lambda x: x["date"], reverse=True):
            clean_title = it["title"].replace("|", "\\|").strip()
            # Clean up excessively long title strings
            if len(clean_title) > 95:
                clean_title = clean_title[:92] + "..."
            md.append(f"| [{clean_title}]({it['url']}) | `{it['domain']}` | `{it['folder']}` | {it['date']} |")
        md.append("")
        md.append("---")
        md.append("")

    return "\n".join(md)


def query_bookmarks(query: str = "", category: str = "", limit: int = 15, db_path: str = "docs/notes/shopify_bookmarks/shopify_bookmarks.json") -> dict:
    """Queries the local bookmarks database in RAM with keyword and category filtering."""
    db_file = Path(db_path)
    if not db_file.exists():
        return {"success": False, "error": f"Database file {db_path} not found. Run parse_shopify_bookmarks.py first.", "results": []}

    with open(db_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    results = []
    q_lower = query.lower().strip()
    cat_lower = category.lower().strip()

    for it in items:
        if cat_lower and it.get("category", "").lower() != cat_lower:
            continue
        if q_lower:
            haystack = f"{it.get('title', '')} {it.get('url', '')} {it.get('folder', '')}".lower()
            if q_lower not in haystack:
                continue
        results.append(it)
        if len(results) >= limit:
            break

    return {
        "success": True,
        "query": query,
        "category": category,
        "total_matched": len(results),
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description="High-Speed Bookmark Scanner for Shopify Ecosystem")
    parser.add_argument("--input", "-i", required=True, help="Path to Netscape bookmarks HTML file")
    parser.add_argument("--output-json", "-j", default="docs/notes/shopify_bookmarks/shopify_bookmarks.json", help="Path to output JSON")
    parser.add_argument("--output-md", "-m", default="docs/notes/shopify_bookmarks/SHOPIFY_BOOKMARKS_INDEX_2026-11-18.md", help="Path to output Markdown")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Scanning bookmarks file: {input_path} ({input_path.stat().st_size / 1024 / 1024:.2f} MB)...")
    
    # Get total count first
    raw_parser = BookmarkParser()
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_parser.feed(f.read())
    total_raw = len(raw_parser.bookmarks)

    # Filtered items
    items = scan_bookmarks(str(input_path))
    print(f"✅ Filtered {len(items)} high-value Shopify/E-com resources out of {total_raw} total bookmarks.")

    # Write JSON
    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "total_raw": total_raw,
            "total_extracted": len(items),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "items": items
        }, f, indent=2, ensure_ascii=False)
    print(f"💾 JSON database written to: {out_json}")

    # Write Markdown
    out_md = Path(args.output_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    md_content = generate_markdown(items, total_raw)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"📝 Markdown knowledge base written to: {out_md}")

    # Summary by Category
    categories = Counter(it["category"] for it in items)
    print("\n📊 Breakdown by Pillar:")
    for cat_id, meta in CATEGORY_METADATA.items():
        print(f"  {meta['badge']} {meta['title']}: {categories[cat_id]}")


if __name__ == "__main__":
    main()
