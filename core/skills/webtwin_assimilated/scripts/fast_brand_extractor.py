"""
--- DNK-MRH-HEADER ---
mrh_id: "core/skills/webtwin_assimilated/scripts/fast_brand_extractor.py"
purpose: "Zero-dependency brand asset and product extractor using Python standard library"
canonical_source: true
status: "Active"
version: "1.1.0"
updated_at: "2026-10-31"
author: "Denchik Master Builder & Antigravity"
--- END DNK-MRH-HEADER ---
"""

import html
from html.parser import HTMLParser
import json
import re
from typing import Any, Dict, List
import urllib.parse
import urllib.request


class FastMetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.meta_tags: List[Dict[str, str]] = []
        self.styles: List[str] = []
        self.in_style = False
        self.current_style = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.meta_tags.append(attr_dict)
        elif tag == "style":
            self.in_style = True
            self.current_style = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "style":
            self.in_style = False
            self.styles.append(" ".join(self.current_style))

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_style:
            self.current_style.append(data)


def extract_shopify_catalog(store_url: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Extract products directly from any Shopify store using standard /products.json fast-path."""
    clean_url = store_url.rstrip("/")
    target_endpoint = f"{clean_url}/products.json?limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(target_endpoint, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("products", [])
    except Exception:
        return []
    return []


def extract_brand_palette(target_url: str) -> Dict[str, Any]:
    """Pure stdlib extraction of brand assets, meta tags, and color cues."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(target_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_html = response.read().decode("utf-8", errors="ignore")
    except Exception as err:
        return {"error": str(err), "url": target_url}

    parser = FastMetaParser()
    parser.feed(raw_html)

    # Resolve title
    title = parser.title.strip()

    # Resolve metadata
    description = ""
    og_image = ""
    for meta in parser.meta_tags:
        name = meta.get("name", "").lower()
        prop = meta.get("property", "").lower()
        content = meta.get("content", "")
        if name == "description" or prop == "og:description":
            description = content
        elif prop == "og:image":
            og_image = urllib.parse.urljoin(target_url, content)

    # Extract colors
    all_styles = " ".join(parser.styles)
    hex_colors = list(set(re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", all_styles)))[:10]

    return {
        "url": target_url,
        "title": html.unescape(title),
        "description": html.unescape(description),
        "og_image": og_image,
        "sample_colors": hex_colors,
        "is_shopify": bool("/cdn.shopify.com" in raw_html or "Shopify.theme" in raw_html),
    }


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://shopify.com"
    res = extract_brand_palette(url)
    print(json.dumps(res, indent=2))
