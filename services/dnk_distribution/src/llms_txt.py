# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/src/llms_txt.py"
# purpose: "E-Commerce llms.txt & llms-full.txt Generation Engine for GEO & AI Agents"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StoreProfile(BaseModel):
    name: str = Field(default="DNK Sovereign Store", description="Store or brand name")
    tagline: str = Field(default="Sovereign Apparel & Premium Streetwear", description="Short brand summary")
    base_url: str = Field(default="https://dnk-e.com", description="Store root URL")
    currency: str = Field(default="UAH", description="Primary currency")
    shipping_info: str = Field(default="Доставка по Україні (Нова Пошта 1-2 дні). Міжнародна доставка по всьому світу.", description="Shipping summary")
    return_policy: str = Field(default="14 днів гарантованого повернення та обміну згідно із законодавством.", description="Return policy summary")


class CatalogItem(BaseModel):
    title: str
    handle: str
    price: str
    currency: str = "UAH"
    description: str
    sku: Optional[str] = None
    in_stock: bool = True
    collection: Optional[str] = "Featured"
    material: Optional[str] = None
    care_instructions: Optional[str] = None
    url: Optional[str] = None


class PolicyItem(BaseModel):
    title: str
    url: str
    summary: str


class LlmsTxtEngine:
    """Sovereign Engine generating llmstxt.org compliant index files for AI crawlers."""

    @staticmethod
    def generate_llms_txt(
        profile: StoreProfile,
        products: List[CatalogItem],
        policies: Optional[List[PolicyItem]] = None,
        optional_links: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Builds a concise, token-optimized llms.txt file.
        Provides AI agents (ChatGPT Search, Perplexity, Claude) with an explicit map of the store.
        """
        lines = [
            f"# {profile.name}",
            f"> {profile.tagline}",
            f"> Валюта: {profile.currency} | Доставка: {profile.shipping_info} | Повернення: {profile.return_policy}",
            "",
            "## Core Collections & Products",
        ]

        # Group by collection
        by_col: Dict[str, List[CatalogItem]] = {}
        for p in products:
            col = p.collection or "Catalog"
            by_col.setdefault(col, []).append(p)

        for col_name, items in by_col.items():
            lines.append(f"### {col_name}")
            for item in items:
                link = item.url or f"{profile.base_url.rstrip('/')}/products/{item.handle}"
                stock = "В наявності" if item.in_stock else "Під замовлення"
                desc = item.description.replace("\n", " ").strip()
                if len(desc) > 120:
                    desc = desc[:117] + "..."
                lines.append(f"- [{item.title}]({link}): {item.price} {item.currency} — {desc} ({stock})")
            lines.append("")

        lines.append("## Customer Policies & Support")
        default_policies = policies or [
            PolicyItem(
                title="Доставка та Оплата",
                url=f"{profile.base_url.rstrip('/')}/pages/shipping",
                summary="Умови доставки Новою Поштою та міжнародними поштовими операторами.",
            ),
            PolicyItem(
                title="Повернення та Обмін",
                url=f"{profile.base_url.rstrip('/')}/pages/returns",
                summary="14-денний термін обміну та повернення коштів без ускладнень.",
            ),
            PolicyItem(
                title="Розмірна Сітка",
                url=f"{profile.base_url.rstrip('/')}/pages/size-guide",
                summary="Таблиця вимірів європейських та оверсайз лекал DNK.",
            ),
        ]

        for pol in default_policies:
            lines.append(f"- [{pol.title}]({pol.url}): {pol.summary}")
        lines.append("")

        lines.append("## Optional")
        opts = optional_links or [
            {"title": "Про Бренд DNK", "url": f"{profile.base_url.rstrip('/')}/pages/about", "desc": "Філософія суверенного виробництва та матеріали преміум-класу."},
            {"title": "C2PA Автентичність", "url": f"{profile.base_url.rstrip('/')}/pages/provenance", "desc": "Криптографічна верифікація оригінальності виробів."},
        ]
        for opt in opts:
            lines.append(f"- [{opt['title']}]({opt['url']}): {opt.get('desc', '')}")

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def generate_llms_full_txt(
        profile: StoreProfile,
        products: List[CatalogItem],
        policies: Optional[List[PolicyItem]] = None,
    ) -> str:
        """
        Builds a comprehensive llms-full.txt file containing deep technical and
        product specifications for LLM reasoning and shopping comparisons.
        """
        lines = [
            f"# {profile.name} — Full Knowledge Base & Product Catalog",
            f"> {profile.tagline}",
            f"> Base URL: {profile.base_url} | Primary Currency: {profile.currency}",
            "",
            "## Store Policies & Terms",
            f"- **Доставка**: {profile.shipping_info}",
            f"- **Повернення**: {profile.return_policy}",
            "",
            "## Comprehensive Product Catalog",
            "",
        ]

        for p in products:
            link = p.url or f"{profile.base_url.rstrip('/')}/products/{p.handle}"
            stock_str = "В наявності" if p.in_stock else "Під замовлення"
            lines.append(f"### {p.title}")
            lines.append(f"- **URL**: {link}")
            lines.append(f"- **Ціна**: {p.price} {p.currency}")
            lines.append(f"- **Статус**: {stock_str}")
            if p.sku:
                lines.append(f"- **Артикул (SKU)**: {p.sku}")
            if p.material:
                lines.append(f"- **Склад матеріалу**: {p.material}")
            if p.care_instructions:
                lines.append(f"- **Правила догляду**: {p.care_instructions}")
            lines.append(f"- **Опис**: {p.description}")
            lines.append("")

        return "\n".join(lines).strip() + "\n"

    @classmethod
    def export_bundle(
        cls,
        output_dir: Path,
        profile: StoreProfile,
        products: List[CatalogItem],
        policies: Optional[List[PolicyItem]] = None,
    ) -> Dict[str, str]:
        """Writes both llms.txt and llms-full.txt into destination directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        txt_path = output_dir / "llms.txt"
        full_path = output_dir / "llms-full.txt"

        txt_content = cls.generate_llms_txt(profile, products, policies)
        full_content = cls.generate_llms_full_txt(profile, products, policies)

        txt_path.write_text(txt_content, encoding="utf-8")
        full_path.write_text(full_content, encoding="utf-8")

        return {
            "llms_txt": str(txt_path),
            "llms_full_txt": str(full_path),
        }


llms_txt_engine = LlmsTxtEngine()
