#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/companion/shopify_knowledge_indexer.py"
# purpose: "Shopify Platform Knowledge Ingestion Engine: Liquid Specs, Theme Blocks 2.0, Storefront GraphQL API, and Theme Check Rules"
# canonical_source: true
# alters_files: [
#   "_Shopify_Theme_DEV_Workflow/companion/KNOWLEDGE_BASE_SHOPIFY_STANDARDS.md",
#   "_Shopify_Theme_DEV_Workflow/companion/shopify_platform_specs.json"
# ]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

"""Shopify Platform Knowledge Ingestion Engine.

Authoritative indexing and query system for:
1. Shopify Liquid Standard (Current & Deprecated syntax)
2. Theme Blocks 2.0 Nesting Architecture (content_for 'blocks')
3. Storefront GraphQL API (Cart, PDP, Buyer Identity)
4. Official Shopify Theme Check Linting Rules
5. Core Web Vitals & Cleanroom Invariants for Theme Store ($350-$420 MSRP)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


class ShopifyPlatformKnowledge:
    """Canonical knowledge base of Shopify theme engineering standards."""

    @staticmethod
    def get_liquid_specs() -> Dict[str, Any]:
        return {
            "version": "Shopify Liquid 2026 LTS",
            "deprecated_tags": [
                {"tag": "include", "replacement": "render", "reason": "include shares parent scope and harms performance; render enforces strict isolated scope."},
                {"tag": "img_url", "replacement": "image_url", "reason": "image_url provides superior responsive width/height cropping and WebP/AVIF auto-negotiation."},
                {"tag": "content_for_header", "status": "mandatory_in_theme_liquid", "rule": "Must be placed in <head> of layout/theme.liquid; never manipulated or removed."}
            ],
            "essential_tags_2026": [
                {"tag": "content_for 'blocks'", "scope": "Theme Blocks 2.0", "description": "Renders nested blocks assigned in theme customizer."},
                {"tag": "render", "scope": "Snippets", "description": "Renders snippet with isolated variable bindings: {% render 'snippet-name', prop: value %}."},
                {"tag": "javascript / stylesheet", "scope": "Bundling", "description": "Scoped asset injection evaluated by Shopify edge servers."},
                {"tag": "schema", "scope": "Settings", "description": "Must contain valid RFC 8259 JSON describing section/block customization UI."}
            ],
            "modern_filters": [
                {"filter": "image_url", "usage": "image | image_url: width: 800", "description": "Dynamic CDN image resizing with automatic format negotiation."},
                {"filter": "image_tag", "usage": "image | image_tag: loading: 'lazy', fetchpriority: 'auto', sizes: sizes", "description": "Generates semantic responsive <img> tag."},
                {"filter": "t", "usage": "'general.cart.title' | t", "description": "Internationalization lookup in locales/*.json."},
                {"filter": "json", "usage": "settings | json", "description": "Escapes Liquid object into valid JSON string."},
                {"filter": "money", "usage": "product.price | money", "description": "Formats monetary value per merchant currency settings."}
            ],
            "context_objects": [
                {"object": "closest.product", "context": "Theme Blocks 2.0", "description": "Resolves closest parent product context when a block is nested in generic containers."},
                {"object": "routes", "context": "Global Storefront", "description": "Provides localized dynamic routing URLs (e.g. routes.cart_url, routes.cart_add_url)."},
                {"object": "request.page_type", "context": "Layout / Template", "description": "Identifies active template (product, collection, cart, index, etc.)."}
            ]
        }

    @staticmethod
    def get_theme_blocks_2_0_spec() -> Dict[str, Any]:
        return {
            "title": "Theme Blocks 2.0 Architecture Specification",
            "directive": "{% content_for 'blocks' %}",
            "nesting_rules": {
                "max_nesting_depth": 8,
                "max_blocks_per_section": 25,
                "max_total_blocks_theme": 300,
                "app_block_requirement": "Every section schema.blocks array MUST include {'type': '@app'} for App Extensions compatibility."
            },
            "schema_definition_sample": {
                "name": "Custom Columns",
                "tag": "section",
                "class": "dnk-section-custom-columns",
                "blocks": [
                    {"type": "@app"},
                    {"type": "column"}
                ],
                "presets": [
                    {
                        "name": "Custom Columns",
                        "blocks": [
                            {"type": "column"},
                            {"type": "column"}
                        ]
                    }
                ]
            },
            "best_practices": [
                "Use scoped CSS classes with .dnk- prefix.",
                "Use media-sizes-scope snippet to pass calculated sizes down to nested image blocks.",
                "Avoid tight coupling: blocks should communicate via DOM CustomEvents rather than direct JavaScript references.",
                "Animate using [data-dnk-animating] attribute for 60fps transitions without style-based reflows."
            ]
        }

    @staticmethod
    def get_storefront_graphql_spec() -> Dict[str, Any]:
        return {
            "api_version": "2026-04",
            "endpoint": "/api/2026-04/graphql.json",
            "core_cart_operations": [
                {
                    "operation": "cartCreate",
                    "type": "mutation",
                    "purpose": "Initialize brand new headless or AJAX cart with optional lines and buyer identity."
                },
                {
                    "operation": "cartLinesAdd",
                    "type": "mutation",
                    "purpose": "Add merchandise variant lines with custom attributes and selling plan allocations."
                },
                {
                    "operation": "cartLinesUpdate",
                    "type": "mutation",
                    "purpose": "Update item quantities or attributes dynamically without page reload."
                },
                {
                    "operation": "cartLinesRemove",
                    "type": "mutation",
                    "purpose": "Remove lines by line IDs."
                },
                {
                    "operation": "cartDiscountCodesUpdate",
                    "type": "mutation",
                    "purpose": "Apply or remove coupon codes in real-time."
                }
            ],
            "cart_schema_invariants": [
                "Always query cost.totalAmount and cost.subtotalAmount.",
                "Always query lines.edges.node.merchandise for image, title, selectedOptions.",
                "Support merchandise.product.metafields for bundle logic."
            ]
        }

    @staticmethod
    def get_theme_check_rules() -> List[Dict[str, str]]:
        return [
            {"code": "DeprecatedTags", "severity": "error", "description": "Flag use of {% include %} instead of {% render %}."},
            {"code": "ValidSchemaName", "severity": "error", "description": "Ensure section and block schemas have valid non-empty names or t: keys."},
            {"code": "ValidHTMLTranslation", "severity": "error", "description": "Ensure HTML translations inside locales/*.json are syntactically valid."},
            {"code": "ParserBlockingScript", "severity": "error", "description": "Flag scripts in <head> missing defer, async, or type='module'."},
            {"code": "RemoteAsset", "severity": "error", "description": "Disallow loading CSS/JS from unpkg, cdn.jsdelivr.net, or external domains."},
            {"code": "ImgWidthAndHeight", "severity": "warning", "description": "Require explicit width and height attributes to avoid CLS."},
            {"code": "AssetSizeAppBlockCSS", "severity": "error", "description": "Check that individual CSS assets do not exceed 100KB uncompressed."},
            {"code": "TemplateLength", "severity": "error", "description": "Hard platform error if templates/*.json exceeds 512,000 bytes (512 KB)."}
        ]

    @staticmethod
    def get_cleanroom_drm_signatures() -> List[Dict[str, str]]:
        return [
            {"name": "ECDSA Head Bootstrap Watchdog", "signature": "head-bootstrap.js", "action": "Remove file and references in layout/theme.liquid."},
            {"name": "Domain Verification Lock", "signature": "Shopify.shop", "action": "Neutralize comparison locks; rely on Partner Dashboard billing."},
            {"name": "Freeze Overlay", "signature": ".sw-fr", "action": "Strip CSS overlay rules that blur or lock storefront."},
            {"name": "Remote Auth Ping", "signature": "/api/verify", "action": "Eliminate unauthorized network calls."},
            {"name": "Facebook Pixel Hardcode", "signature": "fbq(", "action": "Remove; delegate to Shopify Customer Events API."},
            {"name": "TikTok Pixel Hardcode", "signature": "ttq.", "action": "Remove; delegate to Shopify Customer Events API."},
            {"name": "Google Tag Manager Hardcode", "signature": "gtag(", "action": "Remove; delegate to Shopify Customer Events API."}
        ]


class ShopifyKnowledgeIndexer:
    """Generator and Query CLI for Shopify Theme Engineering Knowledge Base."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.kb_file = root_dir / "KNOWLEDGE_BASE_SHOPIFY_STANDARDS.md"
        self.json_file = root_dir / "shopify_platform_specs.json"

    def compile_full_specs(self) -> Dict[str, Any]:
        return {
            "meta": {
                "title": "Shopify Platform Technical Specification & Standards Index",
                "version": "2026.11-LTS",
                "author": "DNK-e.com Maksym & Antigravity (Chief Architect)"
            },
            "liquid": ShopifyPlatformKnowledge.get_liquid_specs(),
            "theme_blocks_2_0": ShopifyPlatformKnowledge.get_theme_blocks_2_0_spec(),
            "storefront_graphql": ShopifyPlatformKnowledge.get_storefront_graphql_spec(),
            "theme_check": ShopifyPlatformKnowledge.get_theme_check_rules(),
            "cleanroom_drm": ShopifyPlatformKnowledge.get_cleanroom_drm_signatures()
        }

    def generate_markdown(self) -> str:
        specs = self.compile_full_specs()
        md = []
        md.append("# --- DNK-MRH-HEADER ---")
        md.append(f"# mrh_id: \"_Shopify_Theme_DEV_Workflow/companion/KNOWLEDGE_BASE_SHOPIFY_STANDARDS.md\"")
        md.append(f"# purpose: \"Exhaustive Reference Knowledge Base: Shopify Platform Specs, Theme Blocks 2.0, GraphQL Storefront API & Theme Check Rules\"")
        md.append(f"# canonical_source: true")
        md.append(f"# alters_files: []")
        md.append(f"# triggers_tasks: []")
        md.append(f"# status: \"Active\"")
        md.append(f"# version: \"1.0.0\"")
        md.append(f"# updated_at: \"2026-11-12\"")
        md.append(f"# author: \"DNK-e.com Maksym & Antigravity (Chief Architect)\"")
        md.append("# --- END DNK-MRH-HEADER ---\n")

        md.append("# 📚 БАЗА ЗНАНЬ СТАНДАРТІВ ПЛАТФОРМИ SHOPIFY (2026 LTS)")
        md.append("## Для розробки комерційних тем преміум-класу ($350–$420 MSRP)\n")

        # Liquid Section
        md.append("## 💧 1. СТАНДАРТИ ТА ІНВАРІАНТИ SHOPIFY LIQUID\n")
        md.append("### 1.1. Застарілі та заборонені теги:")
        md.append("| Заборонений тег | Обов'язкова заміна | Причина та архітектурний вплив |")
        md.append("| :--- | :--- | :--- |")
        for dt in specs["liquid"]["deprecated_tags"]:
            tag_name = dt.get('tag')
            replacement = dt.get('replacement', 'N/A')
            desc = dt.get('reason', dt.get('rule', ''))
            md.append(f"| `{{% {tag_name} %}}` | `{replacement}` | {desc} |")
        md.append("\n### 1.2. Обов'язкові сучасні теги та директиви 2026:")
        md.append("| Тег | Область застосування | Опис |")
        md.append("| :--- | :--- | :--- |")
        for et in specs["liquid"]["essential_tags_2026"]:
            tag_name = et['tag']
            scope = et['scope']
            desc = et['description']
            md.append(f"| `{{% {tag_name} %}}` | **{scope}** | {desc} |")

        # Theme Blocks 2.0
        tb = specs["theme_blocks_2_0"]
        md.append("\n---\n")
        md.append("## 🧩 2. СПЕЦИФІКАЦІЯ ТА ВКЛАДЕНІСТЬ THEME BLOCKS 2.0\n")
        md.append(f"- **Ключова директива рендерингу:** `{tb['directive']}`")
        md.append(f"- **Максимальна глибина вкладеності:** {tb['nesting_rules']['max_nesting_depth']} рівнів")
        md.append(f"- **Ліміт блоків на секцію:** {tb['nesting_rules']['max_blocks_per_section']} блоків")
        md.append(f"- **Загальний ліміт блоків теми:** {tb['nesting_rules']['max_total_blocks_theme']} блоків")
        md.append(f"- **App Blocks вимога:** {tb['nesting_rules']['app_block_requirement']}\n")
        md.append("### Найкращі практики проектування блоків:")
        for bp in tb["best_practices"]:
            md.append(f"- {bp}")

        # Storefront GraphQL API
        sg = specs["storefront_graphql"]
        md.append("\n---\n")
        md.append("## ⚡ 3. STOREFRONT GRAPHQL API ДЛЯ AJAX-КОШИКА ТА КАРТОК\n")
        md.append(f"- **Версія API:** `{sg['api_version']}` | **Ендпоінт:** `{sg['endpoint']}`\n")
        md.append("### Ключові операції кошика:")
        md.append("| Операція | Тип | Призначення |")
        md.append("| :--- | :--- | :--- |")
        for op in sg["core_cart_operations"]:
            md.append(f"| `{op['operation']}` | `{op['type']}` | {op['purpose']} |")

        # Theme Check Rules
        md.append("\n---\n")
        md.append("## 🛡️ 4. ПРАВИЛА ВАЛІДАЦІЇ ТА ЛІНТИНГУ SHOPIFY THEME CHECK\n")
        md.append("| Код перевірки | Рівень | Опис правила |")
        md.append("| :--- | :--- | :--- |")
        for tc in specs["theme_check"]:
            icon = "🔴" if tc["severity"] == "error" else "🟡"
            md.append(f"| `{tc['code']}` | {icon} {tc['severity'].upper()} | {tc['description']} |")

        # Cleanroom & DRM Signatures
        md.append("\n---\n")
        md.append("## 🧹 5. СИГНАТУРИ ДЛЯ CLEANROOM-САНАЦІЇ ТА ZERO-DRM\n")
        md.append("| Назва загрози / сигнатура | Маркер у коді | Необхідна дія з санації |")
        md.append("| :--- | :--- | :--- |")
        for drm in specs["cleanroom_drm"]:
            md.append(f"| **{drm['name']}** | `{drm['signature']}` | {drm['action']} |")

        return "\n".join(md)

    def write_artifacts(self) -> None:
        specs = self.compile_full_specs()
        # 1. JSON Export
        self.json_file.write_text(json.dumps(specs, indent=2, ensure_ascii=False), encoding="utf-8")
        # 2. Markdown Reference
        md_text = self.generate_markdown()
        self.kb_file.write_text(md_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Shopify Platform Knowledge Ingestion Engine")
    parser.add_argument("--root", type=Path, default=Path(__file__).parent, help="Root directory for companion agent")
    parser.add_argument("--generate-docs", action="store_true", help="Generate KNOWLEDGE_BASE_SHOPIFY_STANDARDS.md and specs JSON")
    parser.add_argument("--query", type=str, help="Query specific topic: liquid, blocks, graphql, check, drm")
    args = parser.parse_args()

    indexer = ShopifyKnowledgeIndexer(args.root)

    if args.generate_docs or not args.query:
        indexer.write_artifacts()
        print(f"✅ Generated JSON specifications: {indexer.json_file}")
        print(f"✅ Generated Markdown knowledge base: {indexer.kb_file}")

    if args.query:
        q = args.query.lower()
        specs = indexer.compile_full_specs()
        if "liquid" in q:
            print(json.dumps(specs["liquid"], indent=2, ensure_ascii=False))
        elif "block" in q:
            print(json.dumps(specs["theme_blocks_2_0"], indent=2, ensure_ascii=False))
        elif "graph" in q or "storefront" in q:
            print(json.dumps(specs["storefront_graphql"], indent=2, ensure_ascii=False))
        elif "check" in q:
            print(json.dumps(specs["theme_check"], indent=2, ensure_ascii=False))
        elif "drm" in q:
            print(json.dumps(specs["cleanroom_drm"], indent=2, ensure_ascii=False))
        else:
            print(f"Unknown topic '{args.query}'. Options: liquid, blocks, graphql, check, drm.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
