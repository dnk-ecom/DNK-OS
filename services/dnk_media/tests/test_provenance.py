# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/tests/test_provenance.py"
# purpose: "Comprehensive Unit Tests for Sovereign Media Provenance & C2PA Engine (DEC-143)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from pathlib import Path
import pytest

from services.dnk_media.src.provenance import (
    ProvenanceEngine,
    provenance_engine,
)
from services.dnk_media.src.service import (
    sign_provenance,
    verify_provenance,
    synthesize_ecommerce_alt,
)
from services.dnk_media.mcp_server import (
    media_sign_provenance,
    media_verify_provenance,
    media_synthesize_alt_text,
)

# Canonical 1x1 pixel valid PNG bytes
MINIMAL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture
def sample_png(tmp_path: Path) -> Path:
    img_file = tmp_path / "sample_banner.png"
    img_file.write_bytes(MINIMAL_PNG_BYTES)
    return img_file


def test_png_metadata_injection_and_extraction(tmp_path: Path, sample_png: Path):
    target_png = tmp_path / "injected.png"
    meta = {
        "Author": "Maksym Kuzmenko",
        "Copyright": "Copyright (c) 2026 DNK-e.com",
        "DNK-Watermark-ID": "test_sig_777",
    }

    ProvenanceEngine.inject_png_metadata(sample_png, target_png, meta)
    assert target_png.exists()
    assert target_png.stat().st_size > sample_png.stat().st_size

    extracted = ProvenanceEngine.extract_png_metadata(target_png)
    assert extracted.get("Author") == "Maksym Kuzmenko"
    assert extracted.get("Copyright") == "Copyright (c) 2026 DNK-e.com"
    assert extracted.get("DNK-Watermark-ID") == "test_sig_777"


def test_sign_and_verify_provenance_roundtrip(sample_png: Path, tmp_path: Path):
    out_file = tmp_path / "signed_product.png"
    sign_res = sign_provenance(
        image_path=str(sample_png),
        author_name="DNK Design Studio",
        author_url="https://dnk-e.com/studio",
        copyright_notice="Copyright (c) 2026 DNK",
        watermark_payload="wm_sku_1001",
        output_path=str(out_file),
    )

    assert sign_res.success is True
    assert sign_res.author == "DNK Design Studio"
    assert sign_res.format == "png"
    assert out_file.exists()
    assert sign_res.manifest_path is not None
    assert Path(sign_res.manifest_path).exists()

    # Check sidecar manifest content
    with open(sign_res.manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    assert manifest_data["claim_generator"] == "DNK_OS_Media_v2.5"
    assert len(manifest_data["assertions"]) == 3

    # Verification passes
    verify_res = verify_provenance(
        image_path=str(out_file),
        expected_author="DNK Design Studio",
    )
    assert verify_res.valid is True
    assert verify_res.detected_author == "DNK Design Studio"
    assert "matches expectation" in verify_res.message


def test_verify_provenance_author_mismatch(sample_png: Path, tmp_path: Path):
    out_file = tmp_path / "signed_art.png"
    sign_provenance(
        image_path=str(sample_png),
        author_name="Original Creator",
        output_path=str(out_file),
    )

    verify_res = verify_provenance(
        image_path=str(out_file),
        expected_author="Fraudulent Impostor",
    )
    assert verify_res.valid is False
    assert "mismatch" in verify_res.message


def test_missing_file_handling():
    with pytest.raises(FileNotFoundError):
        sign_provenance(image_path="nonexistent_media_file.png")

    res = verify_provenance(image_path="nonexistent_media_file.png")
    assert res.valid is False
    assert "File not found" in res.message


def test_fastmcp_media_provenance_tools(sample_png: Path, tmp_path: Path):
    out_file = tmp_path / "fastmcp_signed.png"
    sign_data = media_sign_provenance(
        image_path=str(sample_png),
        author_name="FastMCP Author",
        output_path=str(out_file),
    )
    assert sign_data["success"] is True
    assert sign_data["author"] == "FastMCP Author"

    verify_data = media_verify_provenance(
        image_path=str(out_file),
        expected_author="FastMCP Author",
    )
    assert verify_data["valid"] is True
    assert verify_data["detected_author"] == "FastMCP Author"


def test_multilingual_alt_text_injection_and_extraction(sample_png: Path, tmp_path: Path):
    out_file = tmp_path / "hoodie_signed.png"
    sign_res = sign_provenance(
        image_path=str(sample_png),
        author_name="DNK Apparel",
        alt_text_uk="Чоловіче оверсайз худі з бавовни графітового кольору DNK",
        alt_text_en="Men's oversized cotton hoodie in graphite black by DNK",
        seo_keywords=["hoodie", "streetwear", "dnk"],
        output_path=str(out_file),
    )
    assert sign_res.success is True
    assert sign_res.alt_text_uk == "Чоловіче оверсайз худі з бавовни графітового кольору DNK"
    assert sign_res.alt_text_en == "Men's oversized cotton hoodie in graphite black by DNK"

    # Verify PNG chunks
    extracted = ProvenanceEngine.extract_png_metadata(out_file)
    assert extracted.get("Description-UK") == "Чоловіче оверсайз худі з бавовни графітового кольору DNK"
    assert extracted.get("Description-EN") == "Men's oversized cotton hoodie in graphite black by DNK"
    assert extracted.get("Keywords") == "hoodie, streetwear, dnk"

    # Verify provenance response
    verify_res = verify_provenance(image_path=str(out_file))
    assert verify_res.valid is True
    assert verify_res.detected_alt_uk == "Чоловіче оверсайз худі з бавовни графітового кольору DNK"
    assert verify_res.detected_alt_en == "Men's oversized cotton hoodie in graphite black by DNK"


def test_synthesize_ecommerce_alt():
    uk, en = synthesize_ecommerce_alt(
        product_title="Оверсайз світшот",
        color="графітовий",
        material="тринитка пеньє",
        brand="DNK Ecom",
    )
    assert "Оверсайз світшот" in uk
    assert "з тринитка пеньє" in uk
    assert "графітовий кольору" in uk
    assert "DNK Ecom" in uk
    assert len(uk) < 140

    assert "DNK Ecom" in en
    assert "Оверсайз світшот" in en
    assert "(графітовий)" in en
    assert len(en) < 140


def test_fastmcp_synthesize_alt_tool():
    res = media_synthesize_alt_text(
        product_title="Шкіряні кросівки",
        color="білий",
        material="натуральна шкіра",
        brand="Apex",
    )
    assert "alt_text_uk" in res
    assert "alt_text_en" in res
    assert res["char_count_uk"] > 0
    assert res["char_count_en"] > 0
