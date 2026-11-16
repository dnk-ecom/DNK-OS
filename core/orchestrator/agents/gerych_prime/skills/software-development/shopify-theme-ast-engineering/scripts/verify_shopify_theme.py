#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/verify_shopify_theme.py"
# purpose: "Deterministic verification script for Shopify themes: BOM audit, schema trailing commas, post-schema text, and JSON template validation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-08"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import os
import re
import sys
import json
from pathlib import Path

def audit_theme(theme_dir: Path) -> int:
    theme_dir = Path(theme_dir).resolve()
    if not theme_dir.is_dir():
        print(f"ERROR: {theme_dir} is not a valid directory.")
        return 1

    errors = []
    warnings = []

    print(f"🔍 Auditing Shopify Theme at: {theme_dir}")

    # 1. UTF-8 BOM Audit in JSON files
    for root, _, files in os.walk(theme_dir):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() == ".json":
                try:
                    with open(p, "rb") as fp:
                        raw = fp.read(4)
                        if raw.startswith(b"\xef\xbb\xbf"):
                            errors.append(f"UTF-8 BOM detected in {p.relative_to(theme_dir)}")
                except Exception as e:
                    errors.append(f"Failed to read {p.relative_to(theme_dir)}: {e}")

    # 2. JSON Syntax Validation (templates & config)
    for folder in ["templates", "config", "locales"]:
        target_folder = theme_dir / folder
        if target_folder.is_dir():
            for p in target_folder.glob("*.json"):
                try:
                    with open(p, "r", encoding="utf-8-sig") as fp:
                        json.load(fp)
                except Exception as e:
                    errors.append(f"Invalid JSON in {p.relative_to(theme_dir)}: {e}")

    # 3. Sections Audit: {% schema %} trailing commas and post-schema text
    sections_dir = theme_dir / "sections"
    if sections_dir.is_dir():
        for p in sections_dir.glob("*.liquid"):
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                schema_match = re.search(r"\{%\s*schema\s*%\}(.*?)\{%\s*endschema\s*%\}", content, re.DOTALL)
                if schema_match:
                    schema_raw = schema_match.group(1).strip()
                    # Check for trailing commas before } or ]
                    if re.search(r",\s*[}\]]", schema_raw):
                        errors.append(f"Trailing comma in {{% schema %}} of {p.relative_to(theme_dir)}")
                    try:
                        json.loads(schema_raw)
                    except Exception as e:
                        errors.append(f"Invalid JSON in {{% schema %}} of {p.relative_to(theme_dir)}: {e}")

                    # Check for content after {% endschema %}
                    after_schema = content[schema_match.end():].strip()
                    if after_schema:
                        # Non-empty content after endschema
                        errors.append(f"Illegal content detected after {{% endschema %}} in {p.relative_to(theme_dir)}")
            except Exception as e:
                errors.append(f"Error inspecting {p.relative_to(theme_dir)}: {e}")

    # 4. Product Gallery Scoping Check
    main_product = sections_dir / "main-product.liquid"
    if main_product.is_file():
        content = main_product.read_text(encoding="utf-8", errors="ignore")
        if "product-media-gallery" in content:
            # Check if section variable is passed
            if not re.search(r"render\s+['\"]product-media-gallery['\"][^%]*\bsection\b", content):
                warnings.append("main-product.liquid renders 'product-media-gallery' without passing 'section'. This may cause product gallery rendering failures.")

    print(f"\n📊 Audit Results for {theme_dir.name}:")
    if warnings:
        print(f"⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
        return 1
    else:
        print("✅ Theme Audit Passed: 0 fatal syntax or schema errors detected.")
        return 0

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(audit_theme(Path(target)))
