# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/tests/test_social_commerce.py"
# purpose: "Unit Tests for Dynamic Social OG-Card, Schema.org JSON-LD & Rich Previews"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from pathlib import Path
import pytest

from services.dnk_media.src.social_commerce import (
    generate_schema_org_json_ld,
    generate_opengraph_tags,
    build_social_og_svg,
    generate_breadcrumbs_json_ld,
    generate_faq_json_ld,
    generate_serp_dominator_graph,
    social_commerce_engine,
)
from services.dnk_media.src.service import (
    generate_social_card,
    sign_provenance,
)
from services.dnk_media.mcp_server import (
    media_generate_social_card,
    media_generate_jsonld,
    media_generate_serp_graph,
    media_sign_provenance,
)

MINIMAL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture
def sample_png(tmp_path: Path) -> Path:
    img = tmp_path / "product_photo.png"
    img.write_bytes(MINIMAL_PNG_BYTES)
    return img


def test_generate_schema_org_json_ld():
    data = generate_schema_org_json_ld(
        product_title="Оверсайз худі DNK Heavyweight",
        price="2 450.00 ₴",
        currency="UAH",
        brand="DNK",
        in_stock=True,
        description="Преміальний трикотаж пеньє 450г/м²",
        image_url="https://dnk-e.com/cdn/hoodie.jpg",
        sku="DNK-HD-01",
    )
    assert data["@context"] == "https://schema.org"
    assert data["@type"] == "Product"
    assert data["name"] == "Оверсайз худі DNK Heavyweight"
    assert data["brand"]["name"] == "DNK"
    assert data["image"] == "https://dnk-e.com/cdn/hoodie.jpg"
    assert data["sku"] == "DNK-HD-01"
    offers = data["offers"]
    assert offers["@type"] == "Offer"
    assert offers["price"] == "2450.00"
    assert offers["priceCurrency"] == "UAH"
    assert offers["availability"] == "https://schema.org/InStock"


def test_generate_schema_org_json_ld_out_of_stock():
    data = generate_schema_org_json_ld(
        product_title="Лімітований дроп",
        price="3000",
        currency="UAH",
        in_stock=False,
    )
    assert data["offers"]["availability"] == "https://schema.org/OutOfStock"
    assert data["offers"]["price"] == "3000"


def test_generate_opengraph_tags():
    tags, html_meta = generate_opengraph_tags(
        product_title="Чорне оверсайз худі",
        description="100% бавовна, розроблено в Україні",
        image_url="https://dnk-e.com/og/hoodie.svg",
        price="2 400",
        currency="UAH",
        brand="DNK",
    )
    assert tags["og:type"] == "product"
    assert tags["og:title"] == "Чорне оверсайз худі | DNK"
    assert tags["og:image:width"] == "1200"
    assert tags["og:image:height"] == "630"
    assert tags["twitter:card"] == "summary_large_image"
    assert tags["product:price:amount"] == "2400"
    assert tags["product:price:currency"] == "UAH"
    assert '<meta property="og:title"' in html_meta
    assert '<meta property="product:price:amount"' in html_meta


def test_build_social_og_svg():
    svg = build_social_og_svg(
        product_title="Штани карго Military Black",
        price="1 890",
        currency="UAH",
        brand="DNK",
        in_stock=True,
        usp="Ріп-стоп тканина з водовідштовхувальним DWR покриттям",
    )
    assert 'viewBox="0 0 1200 630"' in svg
    assert 'width="1200"' in svg
    assert 'height="630"' in svg
    assert "Штани карго Military Black" in svg
    assert "1 890 UAH" in svg
    assert "DNK • VERIFIED" in svg
    assert "В наявності" in svg
    assert "C2PA CONTENT CREDENTIALS VALIDATED" in svg


def test_social_commerce_engine_generate_social_card(tmp_path: Path, sample_png: Path):
    out_svg = tmp_path / "card.svg"
    card = generate_social_card(
        product_title="Кепка Tactical DNK",
        price="850",
        currency="UAH",
        brand="DNK",
        in_stock=True,
        usp="Анатомічна посадка",
        image_path=str(sample_png),
        output_path=str(out_svg),
    )
    assert card.success is True
    assert card.width == 1200
    assert card.height == 630
    assert out_svg.exists()
    assert out_svg.stat().st_size > 500
    assert card.json_ld["name"] == "Кепка Tactical DNK"
    assert card.opengraph_tags["og:type"] == "product"


def test_fastmcp_social_tools(sample_png: Path):
    card_dict = media_generate_social_card(
        product_title="Рюкзак Modular 30L",
        price="3 200",
        currency="UAH",
        brand="DNK",
        usp="Кордура 1000D",
        image_path=str(sample_png),
    )
    assert card_dict["success"] is True
    assert card_dict["width"] == 1200
    assert "Рюкзак Modular 30L" in card_dict["svg_content"]
    assert card_dict["json_ld"]["brand"]["name"] == "DNK"

    jsonld_dict = media_generate_jsonld(
        product_title="Футболка Heavy 260g",
        price="950",
        currency="UAH",
        brand="DNK",
        sku="TSH-01",
    )
    assert jsonld_dict["@type"] == "Product"
    assert jsonld_dict["name"] == "Футболка Heavy 260g"
    assert jsonld_dict["offers"]["price"] == "950"


def test_provenance_signing_with_commercial_metadata(tmp_path: Path, sample_png: Path):
    out_png = tmp_path / "commercial_signed.png"
    res = sign_provenance(
        image_path=str(sample_png),
        author_name="DNK-e.com",
        alt_text_uk="Чорне оверсайз худі з капюшоном",
        alt_text_en="Black oversized hoodie with hood",
        seo_keywords=["худі", "оверсайз", "тринитка"],
        price="2 400",
        currency="UAH",
        usp="Преміальна бавовна 450г/м²",
        output_path=str(out_png),
    )
    assert res.success is True
    assert res.json_ld is not None
    assert res.json_ld["offers"]["price"] == "2400"
    assert res.opengraph_tags is not None
    assert res.opengraph_tags["product:price:amount"] == "2400"


def test_generate_breadcrumbs_and_faq_json_ld():
    breadcrumbs = [
        ("Головна", "https://dnk-e.com"),
        ("Одяг", "https://dnk-e.com/collections/apparel"),
        ("Худі DNK", None),
    ]
    bc_data = generate_breadcrumbs_json_ld(breadcrumbs)
    assert bc_data["@type"] == "BreadcrumbList"
    assert len(bc_data["itemListElement"]) == 3
    assert bc_data["itemListElement"][0]["name"] == "Головна"
    assert bc_data["itemListElement"][0]["position"] == 1
    assert bc_data["itemListElement"][0]["item"] == "https://dnk-e.com"
    assert "item" not in bc_data["itemListElement"][2]

    faqs = [
        {"question": "Як підібрати розмір?", "answer": "Орієнтуйтеся на таблицю розмірів у картці товару."},
        {"question": "Скільки триває доставка?", "answer": "1-2 дні по Україні."},
    ]
    faq_data = generate_faq_json_ld(faqs)
    assert faq_data["@type"] == "FAQPage"
    assert len(faq_data["mainEntity"]) == 2
    assert faq_data["mainEntity"][0]["name"] == "Як підібрати розмір?"
    assert faq_data["mainEntity"][0]["acceptedAnswer"]["text"] == "Орієнтуйтеся на таблицю розмірів у картці товару."


def test_generate_serp_dominator_graph_and_mcp_tool():
    breadcrumbs = [
        ("Головна", "https://dnk-e.com"),
        ("Худі", "https://dnk-e.com/collections/hoodies"),
    ]
    faqs = [
        {"question": "Чи сідає тканина після прання?", "answer": "Ні, тринитка пеньє проходить попередню усадку."}
    ]
    graph = generate_serp_dominator_graph(
        product_title="Оверсайз худі",
        price="2 400",
        currency="UAH",
        brand="DNK",
        breadcrumbs=breadcrumbs,
        faqs=faqs,
    )
    assert graph["@context"] == "https://schema.org"
    assert "@graph" in graph
    types = [node["@type"] for node in graph["@graph"]]
    assert "Product" in types
    assert "BreadcrumbList" in types
    assert "FAQPage" in types

    # Test FastMCP Tool
    mcp_res = media_generate_serp_graph(
        product_title="Оверсайз худі",
        price="2 400",
        currency="UAH",
        brand="DNK",
        breadcrumbs=[["Головна", "https://dnk-e.com"], ["Худі", "https://dnk-e.com/collections/hoodies"]],
        faqs=faqs,
    )
    assert mcp_res["@context"] == "https://schema.org"
    assert len(mcp_res["@graph"]) == 3

