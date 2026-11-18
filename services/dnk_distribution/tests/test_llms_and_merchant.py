# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/tests/test_llms_and_merchant.py"
# purpose: "Unit Tests for E-Commerce llms.txt & Google Merchant Feed Generators"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from pathlib import Path
import pytest

from services.dnk_distribution.src.llms_txt import (
    StoreProfile,
    CatalogItem,
    PolicyItem,
    llms_txt_engine,
)
from services.dnk_distribution.src.merchant_feed import (
    generate_google_merchant_xml,
    export_merchant_feed,
)
from services.dnk_distribution.src.service import (
    generate_llms_bundle,
    generate_merchant_feed,
)
from services.dnk_distribution.contracts.schemas import (
    LlmsTxtRequest,
    MerchantFeedRequest,
)
from services.dnk_distribution.mcp_server import (
    distribution_generate_llms_txt,
    distribution_generate_merchant_feed,
)


@pytest.fixture
def sample_catalog():
    profile = StoreProfile(
        name="DNK Test Store",
        tagline="Sovereign High-Performance Apparel",
        base_url="https://test.dnk-e.com",
        currency="UAH",
    )
    products = [
        CatalogItem(
            title="Оверсайз худі Heavyweight",
            handle="oversize-hoodie",
            price="2 450",
            currency="UAH",
            description="Щільна бавовна пеньє 450г/м²",
            sku="DNK-01",
            in_stock=True,
            collection="Худі",
            material="100% бавовна",
            care_instructions="30°C делікатне прання",
        ),
        CatalogItem(
            title="Карго штани Tactical",
            handle="cargo-tactical",
            price="1 800",
            currency="UAH",
            description="Ріп-стоп тканина з водовідштовхувальним покриттям",
            sku="DNK-02",
            in_stock=False,
            collection="Штани",
        ),
    ]
    return profile, products


def test_llms_txt_engine_structure(sample_catalog):
    profile, products = sample_catalog
    txt = llms_txt_engine.generate_llms_txt(profile, products)

    assert "# DNK Test Store" in txt
    assert "> Sovereign High-Performance Apparel" in txt
    assert "## Core Collections & Products" in txt
    assert "### Худі" in txt
    assert "- [Оверсайз худі Heavyweight](https://test.dnk-e.com/products/oversize-hoodie): 2 450 UAH" in txt
    assert "(В наявності)" in txt
    assert "(Під замовлення)" in txt
    assert "## Customer Policies & Support" in txt
    assert "## Optional" in txt


def test_llms_full_txt_engine_structure(sample_catalog):
    profile, products = sample_catalog
    full_txt = llms_txt_engine.generate_llms_full_txt(profile, products)

    assert "# DNK Test Store — Full Knowledge Base" in full_txt
    assert "### Оверсайз худі Heavyweight" in full_txt
    assert "- **Артикул (SKU)**: DNK-01" in full_txt
    assert "- **Склад матеріалу**: 100% бавовна" in full_txt
    assert "- **Правила догляду**: 30°C делікатне прання" in full_txt


def test_llms_export_bundle(tmp_path: Path, sample_catalog):
    profile, products = sample_catalog
    exported = llms_txt_engine.export_bundle(tmp_path, profile, products)

    assert Path(exported["llms_txt"]).exists()
    assert Path(exported["llms_full_txt"]).exists()
    assert Path(exported["llms_txt"]).stat().st_size > 100


def test_google_merchant_xml_structure(sample_catalog):
    profile, products = sample_catalog
    xml_feed = generate_google_merchant_xml(profile, products)

    assert '<?xml version="1.0" encoding="UTF-8"?>' in xml_feed
    assert '<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">' in xml_feed
    assert "<g:id>DNK-01</g:id>" in xml_feed
    assert "<g:title>Оверсайз худі Heavyweight</g:title>" in xml_feed
    assert "<g:price>2450.00 UAH</g:price>" in xml_feed
    assert "<g:availability>in_stock</g:availability>" in xml_feed
    assert "<g:availability>out_of_stock</g:availability>" in xml_feed
    assert "<g:condition>new</g:condition>" in xml_feed


def test_fastmcp_distribution_llms_and_merchant():
    products_payload = [
        {
            "title": "Кепка Tactical",
            "handle": "cap-tactical",
            "price": "750",
            "description": "Анатомічна кепка",
            "sku": "CP-01",
        }
    ]
    res_llms = distribution_generate_llms_txt(
        store_name="DNK Brand",
        products=products_payload,
    )
    assert res_llms["success"] is True
    assert "# DNK Brand" in res_llms["llms_txt"]
    assert "Кепка Tactical" in res_llms["llms_txt"]

    res_feed = distribution_generate_merchant_feed(
        store_name="DNK Brand",
        products=products_payload,
    )
    assert res_feed["success"] is True
    assert "<g:id>CP-01</g:id>" in res_feed["xml_content"]
    assert "<g:price>750.00 UAH</g:price>" in res_feed["xml_content"]
