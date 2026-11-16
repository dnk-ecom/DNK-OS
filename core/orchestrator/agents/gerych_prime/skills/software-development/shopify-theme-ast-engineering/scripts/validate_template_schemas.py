#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/scripts/validate_template_schemas.py"
# purpose: "Deterministic validator and fixer for Shopify OS 2.0 & Horizon JSON templates/config against section AND block schemas (range bounds, select option allowlists, comment headers, and foreign media stripping) to prevent silent index.json/product.json ZIP drops."
# status: "Active"
# version: "2.0.0"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import argparse
import json
import re
import sys
from pathlib import Path


def strip_json_comments(raw: str) -> tuple[str, bool]:
    """Strip C-style /* ... */ and line // comments outside of JSON strings."""
    pattern = re.compile(r'"(?:\\.|[^"\\])*"|(/\*[\s\S]*?\*/|//[^\r\n]*)')
    changed = False

    def repl(match):
        nonlocal changed
        if match.group(1) is not None:
            changed = True
            return ""
        return match.group(0)

    cleaned = pattern.sub(repl, raw).strip()
    return cleaned, changed


def extract_schemas(theme_dir: Path) -> dict[str, dict]:
    """Extract schema settings definitions from both sections/*.liquid and blocks/*.liquid."""
    schemas: dict[str, dict] = {}
    schema_re = re.compile(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", re.DOTALL)

    for folder in ("sections", "blocks"):
        d = theme_dir / folder
        if not d.exists():
            continue
        for liquid_file in d.glob("*.liquid"):
            try:
                content = liquid_file.read_text(encoding="utf-8")
                match = schema_re.search(content)
                if not match:
                    continue
                schema_json = json.loads(match.group(1).strip())
                settings_map = {}
                for s in schema_json.get("settings", []):
                    if isinstance(s, dict) and "id" in s:
                        settings_map[s["id"]] = s
                local_blocks = {}
                for b in schema_json.get("blocks", []):
                    if isinstance(b, dict) and "type" in b and "settings" in b:
                        b_map = {}
                        for s in b.get("settings", []):
                            if isinstance(s, dict) and "id" in s:
                                b_map[s["id"]] = s
                        local_blocks[b["type"]] = b_map
                schemas[f"{folder}:{liquid_file.stem}"] = {
                    "settings": settings_map,
                    "local_blocks": local_blocks,
                }
            except Exception:
                continue
    return schemas


def validate_and_fix_settings(
    settings_dict: dict,
    schema_settings: dict,
    context_label: str,
    fix: bool,
    strip_external_media: bool,
    file_issues: list[str],
) -> bool:
    changed = False
    if not isinstance(settings_dict, dict):
        return False

    for k, v in list(settings_dict.items()):
        # 1. Optional external media & foreign handle stripping
        if strip_external_media and isinstance(v, str):
            if v.startswith("shopify://shop_images/") or v.startswith("shopify://files/videos/"):
                file_issues.append(f"{context_label}: foreign media '{k}={v}'")
                if fix:
                    if v.startswith("shopify://files/videos/"):
                        del settings_dict[k]
                        idx_suffix = k.replace("video", "")
                        mt_key = f"media_type{idx_suffix}"
                        if settings_dict.get(mt_key) == "video":
                            settings_dict[mt_key] = "image"
                    else:
                        del settings_dict[k]
                    changed = True
                continue

        # 2. Stale template IDs in scroll_id
        if k == "scroll_id" and isinstance(v, str) and re.search(r"template--\d+__", v):
            file_issues.append(f"{context_label}: stale template ID in scroll_id '{v}'")
            if fix:
                settings_dict[k] = re.sub(r"template--\d+__", "", v)
                changed = True

        s_def = schema_settings.get(k)
        if not s_def:
            continue

        s_type = s_def.get("type")
        if s_type == "range" and isinstance(v, (int, float)):
            s_min = s_def.get("min")
            s_max = s_def.get("max")
            if s_max is not None and v > s_max:
                file_issues.append(f"{context_label}: range '{k}={v}' > max {s_max}")
                if fix:
                    settings_dict[k] = s_max
                    changed = True
            elif s_min is not None and v < s_min:
                file_issues.append(f"{context_label}: range '{k}={v}' < min {s_min}")
                if fix:
                    settings_dict[k] = s_min
                    changed = True

        elif s_type == "select" and isinstance(v, str):
            options = [opt.get("value") for opt in s_def.get("options", []) if isinstance(opt, dict)]
            if options and v not in options:
                default_val = s_def.get("default", options[0])
                if default_val not in options:
                    default_val = options[0]
                file_issues.append(
                    f"{context_label}: invalid select '{k}={v}' (allowed: {options}, default: {default_val})"
                )
                if fix:
                    settings_dict[k] = default_val
                    changed = True

    return changed


def walk_blocks_recursive(
    blocks_dict: dict,
    parent_local_blocks: dict,
    schemas: dict,
    context_prefix: str,
    fix: bool,
    strip_external_media: bool,
    file_issues: list[str],
) -> bool:
    changed = False
    if not isinstance(blocks_dict, dict):
        return False

    for b_id, b_data in blocks_dict.items():
        if not isinstance(b_data, dict):
            continue
        b_type = b_data.get("type", "")
        b_settings = b_data.get("settings", {})

        schema_settings = {}
        next_local_blocks = {}
        if b_type in parent_local_blocks:
            schema_settings = parent_local_blocks[b_type]
        elif f"blocks:{b_type}" in schemas:
            schema_settings = schemas[f"blocks:{b_type}"]["settings"]
            next_local_blocks = schemas[f"blocks:{b_type}"]["local_blocks"]

        if validate_and_fix_settings(
            b_settings,
            schema_settings,
            f"{context_prefix} > block '{b_id}' ({b_type})",
            fix,
            strip_external_media,
            file_issues,
        ):
            changed = True

        if isinstance(b_data.get("blocks"), dict):
            if walk_blocks_recursive(
                b_data["blocks"],
                next_local_blocks,
                schemas,
                f"{context_prefix} > block '{b_id}'",
                fix,
                strip_external_media,
                file_issues,
            ):
                changed = True

    return changed


def validate_templates(theme_dir: Path, fix: bool = False, strip_external_media: bool = False) -> int:
    schemas = extract_schemas(theme_dir)
    target_files: list[Path] = []
    for folder in ("templates", "sections", "config", "locales"):
        d = theme_dir / folder
        if d.exists():
            target_files.extend(sorted(d.rglob("*.json")))

    total_issues = 0
    fixed_files = 0

    for json_file in target_files:
        raw = json_file.read_text(encoding="utf-8")
        file_changed = False
        file_issues: list[str] = []

        cleaned_raw, had_comments = strip_json_comments(raw)
        if had_comments:
            file_issues.append("C-style comment header/inline comment detected (breaks strict Shopify JSON parser)")
            if fix:
                raw = cleaned_raw
                file_changed = True

        try:
            data = json.loads(cleaned_raw if had_comments else raw)
        except Exception as e:
            file_issues.append(f"Malformed JSON: {e}")
            total_issues += len(file_issues)
            print(f"[{json_file.relative_to(theme_dir)}] {len(file_issues)} issue(s):")
            for issue in file_issues:
                print(f"  - {issue}")
            continue

        # Determine sections dictionary (templates/*.json, sections/*.json, or config/settings_data.json)
        sections_containers = []
        if isinstance(data, dict):
            if isinstance(data.get("sections"), dict):
                sections_containers.append(data["sections"])
            if isinstance(data.get("current"), dict) and isinstance(data["current"].get("sections"), dict):
                sections_containers.append(data["current"]["sections"])

        for sections in sections_containers:
            for sec_key, sec_data in sections.items():
                if not isinstance(sec_data, dict):
                    continue
                sec_type = sec_data.get("type", "")
                sec_settings = sec_data.get("settings", {})
                sec_schema = schemas.get(f"sections:{sec_type}", {"settings": {}, "local_blocks": {}})

                if validate_and_fix_settings(
                    sec_settings,
                    sec_schema["settings"],
                    f"Section '{sec_key}' ({sec_type})",
                    fix,
                    strip_external_media,
                    file_issues,
                ):
                    file_changed = True

                if isinstance(sec_data.get("blocks"), dict):
                    if walk_blocks_recursive(
                        sec_data["blocks"],
                        sec_schema["local_blocks"],
                        schemas,
                        f"Section '{sec_key}'",
                        fix,
                        strip_external_media,
                        file_issues,
                    ):
                        file_changed = True

        if file_issues:
            total_issues += len(file_issues)
            print(f"[{json_file.relative_to(theme_dir)}] {len(file_issues)} issue(s):")
            for issue in file_issues:
                print(f"  - {issue}")

        if fix and file_changed:
            json_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            fixed_files += 1

    print(f"\nAudit complete: {total_issues} issue(s) found across theme JSON files.")
    if fix:
        print(f"Fixed {fixed_files} JSON file(s).")

    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate Shopify OS 2.0 & Horizon JSON files against section and block schemas."
    )
    parser.add_argument("--theme-dir", default=".", help="Path to Shopify theme root directory")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically strip comments, clamp range bounds, and fix invalid select option values",
    )
    parser.add_argument(
        "--strip-external-media",
        action="store_true",
        help="Strip foreign shopify://shop_images/ and shopify://files/videos/ bindings and switch video media_type to image",
    )
    args = parser.parse_args()

    sys.exit(validate_templates(Path(args.theme_dir), fix=args.fix, strip_external_media=args.strip_external_media))
