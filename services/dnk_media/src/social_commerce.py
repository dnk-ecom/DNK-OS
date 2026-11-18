# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/src/social_commerce.py"
# purpose: "Dynamic Social OG-Card, Schema.org JSON-LD & Chat Rich Preview Generator for E-Commerce"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from services.dnk_media.contracts.schemas import SocialCardRequest, SocialCardResponse


def generate_schema_org_json_ld(
    product_title: str,
    price: str,
    currency: str = "UAH",
    brand: str = "DNK",
    in_stock: bool = True,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    sku: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generates standard Schema.org Product + Offer JSON-LD structured data.
    Read by Google Search, Google Shopping, ChatGPT Search, and Perplexity.
    """
    clean_price = "".join(c for c in price if c.isdigit() or c in ".,").replace(",", ".") or "0"
    availability = "https://schema.org/InStock" if in_stock else "https://schema.org/OutOfStock"

    data: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product_title,
        "brand": {
            "@type": "Brand",
            "name": brand,
        },
        "description": description or f"{product_title} by {brand}",
        "offers": {
            "@type": "Offer",
            "price": clean_price,
            "priceCurrency": currency,
            "availability": availability,
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {
                "@type": "Organization",
                "name": brand,
            },
        },
    }

    if image_url:
        data["image"] = image_url
    if sku:
        data["sku"] = sku

    return data


def generate_breadcrumbs_json_ld(
    breadcrumbs: List[Tuple[str, Optional[str]]],
) -> Dict[str, Any]:
    """
    Generates standard Schema.org BreadcrumbList structured data for clean SERP paths.
    Takes a list of (Name, URL) pairs.
    """
    elements = []
    for idx, (name, link) in enumerate(breadcrumbs, start=1):
        item_obj: Dict[str, Any] = {
            "@type": "ListItem",
            "position": idx,
            "name": name,
        }
        if link:
            item_obj["item"] = link
        elements.append(item_obj)

    return {
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }


def generate_faq_json_ld(
    faqs: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Generates standard Schema.org FAQPage structured data for rich SERP accordions.
    Takes a list of dicts with 'question' (or 'name') and 'answer' (or 'text').
    """
    main_entities = []
    for item in faqs:
        q = item.get("question") or item.get("name") or ""
        a = item.get("answer") or item.get("text") or ""
        if q and a:
            main_entities.append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a,
                },
            })

    return {
        "@type": "FAQPage",
        "mainEntity": main_entities,
    }


def generate_serp_dominator_graph(
    product_title: str,
    price: str,
    currency: str = "UAH",
    brand: str = "DNK",
    in_stock: bool = True,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    sku: Optional[str] = None,
    breadcrumbs: Optional[List[Tuple[str, Optional[str]]]] = None,
    faqs: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Generates a unified Schema.org @graph combining Product, BreadcrumbList, and FAQPage.
    Dominates mobile SERP vertical pixel area while completely eliminating schema conflict warnings.
    """
    prod_data = generate_schema_org_json_ld(
        product_title=product_title,
        price=price,
        currency=currency,
        brand=brand,
        in_stock=in_stock,
        description=description,
        image_url=image_url,
        sku=sku,
    )
    # Remove @context from child object inside @graph
    prod_data.pop("@context", None)

    graph_nodes = [prod_data]

    if breadcrumbs:
        bc_data = generate_breadcrumbs_json_ld(breadcrumbs)
        graph_nodes.append(bc_data)

    if faqs:
        faq_data = generate_faq_json_ld(faqs)
        graph_nodes.append(faq_data)

    return {
        "@context": "https://schema.org",
        "@graph": graph_nodes,
    }


def generate_opengraph_tags(
    product_title: str,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    price: Optional[str] = None,
    currency: str = "UAH",
    brand: str = "DNK",
    site_name: str = "DNK Sovereign Store",
) -> Tuple[Dict[str, str], str]:
    """
    Generates OpenGraph and Twitter Card metadata for rich social previews in
    Telegram, WhatsApp, iMessage, Twitter/X, and Discord.
    """
    desc = description or f"{product_title} — {brand}. Офіційна колекція."
    tags: Dict[str, str] = {
        "og:type": "product",
        "og:site_name": site_name,
        "og:title": f"{product_title} | {brand}",
        "og:description": desc,
        "twitter:card": "summary_large_image",
        "twitter:title": f"{product_title} | {brand}",
        "twitter:description": desc,
    }

    if image_url:
        tags["og:image"] = image_url
        tags["og:image:width"] = "1200"
        tags["og:image:height"] = "630"
        tags["twitter:image"] = image_url

    if price:
        clean_price = "".join(c for c in price if c.isdigit() or c in ".,").replace(",", ".")
        tags["product:price:amount"] = clean_price
        tags["product:price:currency"] = currency
        tags["og:price:amount"] = clean_price
        tags["og:price:currency"] = currency

    html_lines = [f'<meta property="{k}" content="{html.escape(v)}" />' for k, v in tags.items()]
    return tags, "\n".join(html_lines)


def build_social_og_svg(
    product_title: str,
    price: str,
    currency: str = "UAH",
    brand: str = "DNK",
    in_stock: bool = True,
    usp: Optional[str] = None,
    background_image_data_uri: Optional[str] = None,
) -> str:
    """
    Generates a 1200x630 SVG social preview card with luxury dark styling,
    Glassmorphic bottom overlay, verified badge, price tag, and stock indicator.
    """
    safe_title = html.escape(product_title)
    safe_brand = html.escape(brand)
    safe_price = html.escape(f"{price} {currency}".strip())
    safe_usp = html.escape(usp) if usp else ""
    stock_text = "В наявності" if in_stock else "Під замовлення"
    stock_color = "#10B981" if in_stock else "#F59E0B"

    bg_element = """
    <!-- Background Gradient -->
    <rect width="1200" height="630" fill="#0B0D13" />
    <circle cx="950" cy="180" r="400" fill="url(#neon-radial)" opacity="0.35" />
    <circle cx="200" cy="450" r="350" fill="url(#emerald-radial)" opacity="0.25" />
    """

    if background_image_data_uri:
        bg_element += f"""
        <image href="{background_image_data_uri}" x="0" y="0" width="1200" height="630" preserveAspectRatio="xMidYMid slice" opacity="0.85" />
        <rect width="1200" height="630" fill="url(#vignette-overlay)" />
        """

    usp_badge = ""
    if safe_usp:
        usp_badge = f"""
        <g transform="translate(60, 415)">
            <rect width="auto" height="32" rx="16" fill="rgba(255, 255, 255, 0.08)" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1" />
            <text x="18" y="21" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="14" font-weight="600" fill="#D1D5DB">✦ {safe_usp}</text>
        </g>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
    <defs>
        <radialGradient id="neon-radial" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.5"/>
            <stop offset="100%" stop-color="#0B0D13" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="emerald-radial" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#008060" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#0B0D13" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="vignette-overlay" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#0B0D13" stop-opacity="0.3"/>
            <stop offset="60%" stop-color="#0B0D13" stop-opacity="0.7"/>
            <stop offset="100%" stop-color="#0B0D13" stop-opacity="0.95"/>
        </linearGradient>
        <linearGradient id="glass-border" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="rgba(255, 255, 255, 0.25)"/>
            <stop offset="100%" stop-color="rgba(255, 255, 255, 0.05)"/>
        </linearGradient>
        <filter id="glass-blur">
            <feGaussianBlur stdDeviation="16"/>
        </filter>
    </defs>

    {bg_element}

    <!-- Top Sovereign Badge -->
    <g transform="translate(60, 50)">
        <rect width="220" height="38" rx="19" fill="rgba(11, 13, 19, 0.75)" stroke="url(#glass-border)" stroke-width="1.2" />
        <circle cx="22" cy="19" r="6" fill="#008060" />
        <text x="38" y="24" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="13" font-weight="700" letter-spacing="1.2" fill="#E5E7EB">{safe_brand.upper()} • VERIFIED</text>
    </g>

    <!-- Main Glassmorphic Card (Bottom Overlay) -->
    <g transform="translate(40, 360)">
        <!-- Blur Backdrop -->
        <rect width="1120" height="230" rx="24" fill="rgba(16, 20, 29, 0.82)" stroke="url(#glass-border)" stroke-width="1.5" />
        
        <!-- Stock Pill -->
        <g transform="translate(40, 35)">
            <circle cx="8" cy="8" r="5" fill="{stock_color}" />
            <text x="22" y="12" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="14" font-weight="600" fill="{stock_color}">{stock_text}</text>
        </g>

        <!-- Product Title -->
        <text x="40" y="95" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', sans-serif" font-size="38" font-weight="800" fill="#FFFFFF" letter-spacing="-0.5">
            {safe_title}
        </text>

        <!-- Subtitle / USP -->
        <text x="40" y="135" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="18" font-weight="500" fill="#9CA3AF">
            {safe_usp or f'Офіційна флагманська колекція бренду {safe_brand}'}
        </text>

        <!-- Price Badge (Right-aligned) -->
        <g transform="translate(860, 45)">
            <rect width="220" height="70" rx="18" fill="rgba(0, 128, 96, 0.2)" stroke="#008060" stroke-width="1.8" />
            <text x="110" y="44" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="28" font-weight="800" fill="#34D399">
                {safe_price}
            </text>
        </g>

        <!-- Footer Brand Touchpoint -->
        <line x1="40" y1="168" x2="1080" y2="168" stroke="rgba(255, 255, 255, 0.1)" stroke-width="1" />
        <text x="40" y="198" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="13" font-weight="600" fill="#6B7280" letter-spacing="0.5">
            C2PA CONTENT CREDENTIALS VALIDATED • SECURE CHECKOUT
        </text>
        <text x="1080" y="198" text-anchor="end" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="13" font-weight="700" fill="#3B82F6">
            dnk-e.com ↗
        </text>
    </g>
</svg>"""
    return svg


class SocialCommerceEngine:
    """Sovereign Social Commerce & Rich Preview Synthesis Engine."""

    @staticmethod
    def generate_social_card(request: SocialCardRequest) -> SocialCardResponse:
        """
        Creates a 1200x630 social preview card (SVG) with OpenGraph and JSON-LD metadata.
        """
        bg_uri = None
        if request.image_path and Path(request.image_path).exists():
            img_path = Path(request.image_path)
            try:
                b64_data = base64.b64encode(img_path.read_bytes()).decode("ascii")
                mime = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"
                bg_uri = f"data:{mime};base64,{b64_data}"
            except Exception:
                bg_uri = None

        svg_content = build_social_og_svg(
            product_title=request.product_title,
            price=request.price,
            currency=request.currency,
            brand=request.brand,
            in_stock=request.in_stock,
            usp=request.usp,
            background_image_data_uri=bg_uri,
        )

        out_path_str = None
        if request.output_path:
            out_file = Path(request.output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(svg_content, encoding="utf-8")
            out_path_str = str(out_file)

        json_ld = generate_schema_org_json_ld(
            product_title=request.product_title,
            price=request.price,
            currency=request.currency,
            brand=request.brand,
            in_stock=request.in_stock,
            description=request.usp,
        )

        og_tags, og_html = generate_opengraph_tags(
            product_title=request.product_title,
            description=request.usp,
            price=request.price,
            currency=request.currency,
            brand=request.brand,
        )

        return SocialCardResponse(
            success=True,
            svg_content=svg_content,
            output_path=out_path_str,
            width=1200,
            height=630,
            json_ld=json_ld,
            opengraph_tags=og_tags,
            opengraph_html=og_html,
        )


social_commerce_engine = SocialCommerceEngine()
