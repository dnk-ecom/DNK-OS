#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/dnk_browser.py"
# purpose: "Two-Tier Lightweight Web Engine for DNK OS: Tier 1 (Crawl4AI/Trafilatura) + Tier 2 (Camoufox Stealth)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
DNK OS Two-Tier Web Engine (DEC-072):
- Tier 1: Fast, zero-GPU Markdown/text extraction via Trafilatura / Crawl4AI (~50MB RAM).
- Tier 2: Anti-detect headless browser via Camoufox (Gecko-based, ~200MB RAM, passes Cloudflare).
- Rule: Categorically bans full Retina pixel-based CUA on 8GB machines to prevent swap thrashing.
"""

import sys
import argparse
import urllib.request
import urllib.error


from html.parser import HTMLParser
import re


class _SimpleHTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.in_ignored = False
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg", "header_code"):
            self.in_ignored = True
        elif tag == "title":
            self.in_title = True
        elif tag in ("h1", "h2", "h3", "h4", "p", "li", "tr"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg", "header_code"):
            self.in_ignored = False
        elif tag == "title":
            self.in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "p", "li", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()
        elif not self.in_ignored:
            cleaned = data.strip()
            if cleaned:
                self.parts.append(cleaned + " ")

    def get_markdown(self) -> str:
        text = "".join(self.parts)
        clean = re.sub(r"\n\s*\n+", "\n\n", text).strip()
        prefix = f"# {self.title}\n\n" if self.title else ""
        return prefix + clean


def _get_ssl_context():
    import ssl
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(cafile=certifi.where())
    except Exception:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _fetch_raw_url(url: str, timeout: int = 15) -> tuple:
    """Fetches raw HTML via urllib with full browser headers and HTTP/2 curl fallback for rate limits/Cloudflare."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,uk;q=0.8",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=_get_ssl_context()) as resp:
            return resp.read().decode("utf-8", errors="replace"), resp.geturl()
    except Exception as e:
        # Transparent fallback to macOS system curl (HTTP/2 + modern TLS handshake)
        import subprocess
        cmd = [
            "curl", "-sL", "--max-time", str(timeout),
            "-A", headers["User-Agent"],
            "-H", f"Accept: {headers['Accept']}",
            "-H", f"Accept-Language: {headers['Accept-Language']}",
            url
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout:
            return res.stdout, url
        raise e


def fetch_markdown(url: str, timeout: int = 15) -> str:
    """Tier 1: Extract clean Markdown/text from a URL (<10MB RAM, 0 GPU, standard library)."""
    try:
        raw_html, _ = _fetch_raw_url(url, timeout=timeout)
        # Try trafilatura if installed
        try:
            import trafilatura
            result = trafilatura.extract(
                raw_html,
                include_links=True,
                include_images=False,
                include_tables=True,
                output_format="txt",
            )
            if result:
                return result
        except ImportError:
            pass

        parser = _SimpleHTMLTextExtractor()
        parser.feed(raw_html)
        extracted = parser.get_markdown()
        return extracted or "No main text content extracted."
    except Exception as e:
        return f"Error extracting markdown from {url}: {e}"


def run_stealth_browser(url: str, headless: bool = True, wait_sec: int = 2) -> dict:
    """Tier 2: Interactive stealth browser via Camoufox (~200MB RAM, bypasses anti-bot)."""
    try:
        from camoufox.sync_api import Camoufox

        with Camoufox(headless=headless, humanize=True) as browser:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if wait_sec > 0:
                page.wait_for_timeout(wait_sec * 1000)

            title = page.title()
            content = page.content()
            return {
                "success": True,
                "url": page.url,
                "title": title,
                "html_length": len(content),
                "content": content,
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_shopify_intel(html_raw: str, resolved_url: str = "") -> dict:
    """
    Tier 1 High-Speed Shopify Intelligence Extractor (<50ms, 0 GPU, 0 subprocesses).
    Extracts:
    - JSON-LD schemas (Product, Offers, Reviews, Organization)
    - Cleaned Shopify section names and detected CRO blocks
    - Theme metadata (Theme name, theme ID, currency, page type)
    - CSS brand tokens (Palette, Typography vars)
    - Cleanroom status
    """
    import json
    import re

    is_shopify = (
        "cdn.shopify.com" in html_raw
        or "Shopify.theme" in html_raw
        or "myshopify.com" in html_raw
        or "shopify-section-" in html_raw
    )

    # 1. JSON-LD parsing
    json_ld_blocks = re.findall(
        r'<script[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>(.*?)</script>',
        html_raw,
        re.DOTALL | re.IGNORECASE,
    )
    product_data = None
    structured_schemas = []

    for block in json_ld_blocks:
        try:
            data = json.loads(block.strip())
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                schema_type = item.get("@type", "Unknown")
                structured_schemas.append(schema_type)
                if schema_type == "Product" and not product_data:
                    offers = item.get("offers", {})
                    if isinstance(offers, list) and offers:
                        offers = offers[0]
                    product_data = {
                        "name": item.get("name"),
                        "description": (item.get("description") or "")[:300],
                        "brand": item.get("brand", {}).get("name") if isinstance(item.get("brand"), dict) else item.get("brand"),
                        "sku": item.get("sku"),
                        "price": offers.get("price") if isinstance(offers, dict) else None,
                        "currency": offers.get("priceCurrency") if isinstance(offers, dict) else None,
                        "availability": offers.get("availability") if isinstance(offers, dict) else None,
                        "rating": item.get("aggregateRating", {}).get("ratingValue") if isinstance(item.get("aggregateRating"), dict) else None,
                        "review_count": item.get("aggregateRating", {}).get("reviewCount") if isinstance(item.get("aggregateRating"), dict) else None,
                    }
        except Exception:
            continue

    # 2. Section and CRO block detection
    raw_sections = re.findall(r'id=[\"\']shopify-section-([^\"\']+)[\"\']', html_raw, re.IGNORECASE)
    cleaned_sections = []
    for s in raw_sections:
        clean = re.sub(r'^(sections|template)--[0-9]+__', '', s)
        clean = re.sub(r'_[A-Za-z0-9]{5,}$', '', clean)
        if clean and clean not in cleaned_sections:
            cleaned_sections.append(clean)

    # Known CRO Block heuristics
    cro_block_patterns = {
        "cart_drawer": [r"cart-drawer", r"ajax-cart", r"mini-cart"],
        "floating_buy_bar": [r"floating-cart", r"sticky-cart", r"sticky-buy", r"quick-buy"],
        "quantity_breaks": [r"volume-discount", r"quantity-break", r"bundle-picker", r"tiered-pricing"],
        "countdown_timer": [r"countdown", r"urgency-bar", r"timer"],
        "social_proof_reviews": [r"reviews", r"as-seen-on", r"testimonials", r"ugc-video"],
        "before_after_slider": [r"before-after", r"comparison-slider"],
        "quiz_funnel": [r"quiz", r"survey", r"diagnostic"],
        "trust_badges": [r"trust-badges", r"guarantee", r"payment-icons"],
    }
    detected_cro_blocks = []
    html_lower = html_raw.lower()
    for block_name, patterns in cro_block_patterns.items():
        if any(re.search(pat, html_lower) for pat in patterns):
            detected_cro_blocks.append(block_name)

    # 3. Theme metadata & analytics
    theme_match = (
        re.search(r'\"theme_name\":\s*\"([^\"]+)\"', html_raw)
        or re.search(r'Shopify\.theme\s*=\s*{[^}]*name:\s*\"([^\"]+)\"', html_raw)
    )
    theme_name = theme_match.group(1) if theme_match else ("Shopify Custom/Detected" if is_shopify else "Non-Shopify")

    theme_id_match = re.search(r'Shopify\.theme\s*=\s*{[^}]*id:\s*([0-9]+)', html_raw)
    theme_id = theme_id_match.group(1) if theme_id_match else None

    # Currency
    currency_match = re.search(r'\"currency\":\s*\"([A-Z]{3})\"', html_raw) or re.search(r'Shopify\.currency\s*=\s*{[^}]*active:\s*\"([A-Z]{3})\"', html_raw)
    currency = currency_match.group(1) if currency_match else "USD"

    # 4. Design tokens extraction
    css_vars = re.findall(r'(--[a-zA-Z0-9_-]+)\s*:\s*([^;}{]+);', html_raw)
    palette = {}
    font_tokens = {}
    for var_name, var_val in css_vars:
        var_name_clean = var_name.strip()
        var_val_clean = var_val.strip()
        if "color" in var_name_clean.lower() or "bg" in var_name_clean.lower() or "accent" in var_name_clean.lower():
            if len(palette) < 12 and var_name_clean not in palette:
                palette[var_name_clean] = var_val_clean
        elif "font" in var_name_clean.lower():
            if len(font_tokens) < 6 and var_name_clean not in font_tokens:
                font_tokens[var_name_clean] = var_val_clean

    return {
        "is_shopify": is_shopify,
        "theme_name": theme_name,
        "theme_id": theme_id,
        "active_currency": currency,
        "product_data": product_data,
        "structured_schemas_found": sorted(list(set(structured_schemas))),
        "sections_detected": cleaned_sections,
        "cro_blocks_detected": detected_cro_blocks,
        "design_tokens_preview": {
            "total_css_vars": len(css_vars),
            "key_colors": palette,
            "fonts": font_tokens,
        },
    }


def audit_site_unit(url: str, use_stealth: bool = False, timeout: int = 15) -> dict:
    """
    Unified Site Unit Auditor (DEC-072 / DEC-137):
    Analyzes an e-commerce / web page unit (e.g. sugarthe.me, PDP, landing page).
    Extracts:
    - Page identity & title
    - Platform detection (Shopify / WooCommerce / Custom)
    - Cleanroom status (DRM tokens, tracker domains like ipwho.is, sugarwords.ai)
    - Theme Blocks 2.0 / Section counts
    - Clean text & value propositions
    """
    import json
    import re
    import time

    start_t = time.time()
    html_raw = ""
    resolved_url = url
    title = ""

    if use_stealth:
        res = run_stealth_browser(url, headless=True, wait_sec=2)
        if res.get("success"):
            resolved_url = res.get("url", url)
            title = res.get("title", "")
            html_raw = res.get("content", "")
        else:
            return {"success": False, "error": res.get("error", "Stealth browser failed"), "url": url}
    else:
        try:
            html_raw, resolved_url = _fetch_raw_url(url, timeout=timeout)
        except Exception as e:
            return {"success": False, "error": str(e), "url": url}

    # Extract text & markdown from obtained html_raw
    try:
        import trafilatura
        extracted = trafilatura.extract(
            html_raw,
            include_links=False,
            include_images=False,
            output_format="txt",
        )
        text_content = extracted or ""
    except Exception:
        text_content = ""

    if not text_content and html_raw:
        parser = _SimpleHTMLTextExtractor()
        parser.feed(html_raw)
        text_content = parser.get_markdown() or "No main text content extracted."
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", html_raw, re.IGNORECASE | re.DOTALL)
        title = m.group(1).strip() if m else ""

    # Extract Shopify intelligence (<50ms AST & regex)
    shopify_intel = extract_shopify_intel(html_raw, resolved_url)
    is_shopify = shopify_intel.get("is_shopify", False)
    theme_name = shopify_intel.get("theme_name", "Non-Shopify")

    # Cleanroom & DRM audit
    drm_indicators = ["ipwho.is", "sugarwords.ai", "license_key", "drm_token", "piracy_check"]
    detected_drm = [ind for ind in drm_indicators if ind in html_raw.lower()]

    section_count = len(shopify_intel.get("sections_detected", []))
    theme_block_count = len(re.findall(r'data-block-id=[\"\']', html_raw, re.IGNORECASE))

    elapsed = round(time.time() - start_t, 2)

    return {
        "success": True,
        "url": resolved_url,
        "title": title,
        "platform": "Shopify" if is_shopify else "Web/Other",
        "theme_name": theme_name,
        "cleanroom_audit": {
            "is_clean": len(detected_drm) == 0,
            "detected_trackers_or_drm": detected_drm,
        },
        "structure": {
            "shopify_sections_detected": section_count,
            "theme_blocks_detected": theme_block_count,
            "html_bytes": len(html_raw),
        },
        "shopify_intel": shopify_intel if is_shopify else None,
        "summary_text": text_content[:1500] if text_content else "",
        "execution_time_sec": elapsed,
    }


def main():
    parser = argparse.ArgumentParser(description="DNK OS Two-Tier Web Engine (DEC-072)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # fetch command (Tier 1)
    fetch_parser = subparsers.add_parser("fetch", help="Tier 1: Fast text/markdown extraction (<50MB RAM)")
    fetch_parser.add_argument("url", help="Target URL to extract content from")

    # stealth command (Tier 2)
    stealth_parser = subparsers.add_parser("stealth", help="Tier 2: Headless anti-detect browser via Camoufox (~200MB RAM)")
    stealth_parser.add_argument("url", help="Target URL to navigate with stealth")
    stealth_parser.add_argument("--headed", action="store_true", help="Launch in visible GUI window instead of headless")
    stealth_parser.add_argument("--wait", type=int, default=2, help="Seconds to wait after load")

    # audit-unit command (Unified Site Unit Analyzer)
    audit_parser = subparsers.add_parser("audit-unit", help="Unified Site Unit Audit (Cleanroom, DRM, Shopify, Content in <2s)")
    audit_parser.add_argument("url", help="Target URL to audit")
    audit_parser.add_argument("--stealth", action="store_true", help="Use Camoufox stealth browser for dynamic JS redirects")

    # shopify command (Deep Shopify Store Extractor)
    shopify_parser = subparsers.add_parser("shopify", help="Extract instant Shopify metadata, JSON-LD, sections and design tokens (<0.5s)")
    shopify_parser.add_argument("url", help="Shopify store or PDP URL")
    shopify_parser.add_argument("--json", action="store_true", help="Output raw JSON instead of ADHD terminal report")
    shopify_parser.add_argument("--stealth", action="store_true", help="Use stealth mode if Cloudflare is present")

    args = parser.parse_args()

    if args.command == "fetch":
        md = fetch_markdown(args.url)
        print(md)
    elif args.command == "stealth":
        res = run_stealth_browser(args.url, headless=not args.headed, wait_sec=args.wait)
        import json
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.command == "audit-unit":
        res = audit_site_unit(args.url, use_stealth=args.stealth)
        import json
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.command == "shopify":
        import json
        res = audit_site_unit(args.url, use_stealth=args.stealth)
        intel = res.get("shopify_intel")
        if args.json or not intel:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 60)
            print(f"🛍️ SHOPIFY INTEL: {res.get('title')} ({res.get('url')})")
            print("=" * 60)
            print(f"• Platform / Theme: {res.get('platform')} | {intel.get('theme_name')}")
            print(f"• Active Currency:  {intel.get('active_currency')}")
            prod = intel.get("product_data")
            if prod:
                print(f"• Product Name:     {prod.get('name')}")
                print(f"• Price / Avail:    {prod.get('currency')} {prod.get('price')} ({prod.get('availability', '').split('/')[-1]})")
                if prod.get('rating'):
                    print(f"• Rating / Reviews: ⭐ {prod.get('rating')} ({prod.get('review_count')} reviews)")
            print(f"• Sections Count:   {len(intel.get('sections_detected', []))}")
            if intel.get('sections_detected'):
                print(f"  Sections sample:  {', '.join(intel.get('sections_detected')[:8])}")
            if intel.get('cro_blocks_detected'):
                print(f"• CRO Blocks:       {', '.join(intel.get('cro_blocks_detected'))}")
            palette = intel.get("design_tokens_preview", {}).get("key_colors", {})
            if palette:
                print(f"• Key CSS Palette:  {', '.join(f'{k}: {v}' for k, v in list(palette.items())[:4])}")
            print(f"• Execution Time:   {res.get('execution_time_sec')}s (0 GPU, < 10MB RAM)")
            print("=" * 60)


if __name__ == "__main__":
    main()
