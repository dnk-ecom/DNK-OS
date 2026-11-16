#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/social-media/ecommerce-ad-funnel-cro-audit/scripts/audit_shopify_funnel.py"
# purpose: "Deterministic Shopify funnel & bundle JSON inspector for paid social CRO audits."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "Gerych Prime"
# --- END DNK-MRH-HEADER ---

import json
import re
import sys
import urllib.parse
import urllib.request


def unwrap_meta_url(url: str) -> str:
    """Unwrap l.facebook.com redirect URLs and strip tracking parameters."""
    parsed = urllib.parse.urlparse(url)
    if "facebook.com" in parsed.netloc and parsed.path == "/l.php":
        qs = urllib.parse.parse_qs(parsed.query)
        if "u" in qs:
            url = urllib.parse.unquote(qs["u"][0])
            parsed = urllib.parse.urlparse(url)
    clean_qs = {
        k: v
        for k, v in urllib.parse.parse_qs(parsed.query).items()
        if not k.startswith(("fbclid", "utm_", "_aem_"))
    }
    return urllib.parse.urlunparse(
        parsed._replace(query=urllib.parse.urlencode(clean_qs, doseq=True))
    )


def audit_shopify_url(url: str) -> dict:
    """Fetch a Shopify landing page and extract bundle JSON, DOM weight, and CRO leaks."""
    clean_url = unwrap_meta_url(url)
    req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8", errors="ignore")

    title_match = re.search(r"<title[^>]*>(.*?)</title>", raw, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""

    # Extract Kaching Bundles dealBars configuration if present
    deal_bars = []
    free_gifts = []
    m = re.search(
        r'"dealBars"\s*:\s*(\[.*?\])\s*,\s*"badgesEnabled"\s*:\s*(true|false)', raw
    )
    if m:
        try:
            bars = json.loads(m.group(1))
            for b in bars:
                deal_bars.append(
                    {
                        "title": b.get("title"),
                        "subtitle": b.get("subtitle"),
                        "quantity": b.get("quantity"),
                        "badgeText": b.get("badgeText"),
                        "selectedByDefault": b.get("selectedByDefault"),
                        "pricing": b.get("pricing"),
                    }
                )
                if b.get("freeGifts"):
                    free_gifts.extend(b.get("freeGifts"))
        except Exception:
            pass

    ratings = list(
        set(re.findall(r"\b[34]\.\d\s*(?:out of 5|stars|rating|/5)", raw, re.IGNORECASE))
    )
    uk_leaks = re.findall(
        r"\b(?:Birmingham|Southampton|London|Manchester|UK|£)\b", raw
    )
    duplicate_app_warnings = re.findall(
        r"Multiple app embed blocks detected[^<\"\n]*", raw
    )

    return {
        "url": clean_url,
        "title": title,
        "html_kb": round(len(raw.encode("utf-8")) / 1024, 1),
        "img_tag_count": len(re.findall(r"<img\b", raw, re.IGNORECASE)),
        "deal_bars": deal_bars,
        "free_gifts": free_gifts,
        "ratings_found": ratings,
        "uk_geo_leak_count": len(uk_leaks),
        "uk_geo_leak_samples": list(set(uk_leaks))[:10],
        "duplicate_app_warnings": list(set(duplicate_app_warnings)),
    }


if __name__ == "__main__":
    targets = sys.argv[1:]
    results = {u: audit_shopify_url(u) for u in targets}
    print(json.dumps(results, indent=2, ensure_ascii=False))
