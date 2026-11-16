#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/shopify_theme_neutralizer.py"
# purpose: "Deterministic One-Pass Clean-Room Shopify OS 2.0 Theme Neutralizer, Customizer Schema Sync, Footer Verifier & ZIP Packager."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-19"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""Deterministic One-Pass Shopify OS 2.0 Theme Neutralizer & Customizer Guard."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCHEMA_RX = re.compile(r"(\{%-?\s*schema\s*-?%\})([\s\S]*?)(\{%-?\s*endschema\s*-?%\})")
HEADER_RX = re.compile(r"^(\s*/\*[\s\S]*?\*/\s*)")

THEME_ZIP_DIRS = ("assets", "blocks", "config", "layout", "locales", "sections", "snippets", "templates")


def split_shopify_json(raw: str) -> Tuple[str, Any]:
    match = HEADER_RX.match(raw)
    if match:
        header = match.group(1)
        body = raw[match.end() :]
    else:
        header = ""
        body = raw
    return header, json.loads(body)


def load_schemas(theme_root: Path) -> Dict[Tuple[str, str], Dict[str, Any]]:
    schemas: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for folder, kind in (("sections", "section"), ("blocks", "block")):
        dir_path = theme_root / folder
        if not dir_path.is_dir():
            continue
        for fp in sorted(dir_path.glob("*.liquid")):
            raw = fp.read_text(encoding="utf-8")
            m = SCHEMA_RX.search(raw)
            if not m:
                continue
            try:
                schemas[(kind, fp.stem)] = {
                    "schema": json.loads(m.group(2)),
                    "path": fp,
                    "raw": raw,
                }
            except json.JSONDecodeError:
                continue
    return schemas


def load_valid_color_schemes(theme_root: Path) -> set[str]:
    sd_path = theme_root / "config" / "settings_data.json"
    if not sd_path.is_file():
        return {"scheme-1"}
    try:
        _, data = split_shopify_json(sd_path.read_text(encoding="utf-8"))
        schemes = set((data.get("current") or {}).get("color_schemes", {}).keys())
        return schemes or {"scheme-1"}
    except Exception:
        return {"scheme-1"}


def sync_parent_block_allowlists(
    theme_root: Path,
    schemas: Dict[Tuple[str, str], Dict[str, Any]],
    write: bool = False,
) -> List[str]:
    """Ensure every non-static block used in templates/groups is allowed in its parent schema."""
    missing_by_parent: Dict[Tuple[str, str], set[str]] = {}

    def walk(kind: str, node_type: str, node_obj: Dict[str, Any]) -> None:
        entry = schemas.get((kind, node_type))
        if not entry:
            return
        sc = entry["schema"]
        allowed = {b.get("type") for b in sc.get("blocks", []) if isinstance(b, dict)}
        local_defs = {
            b.get("type")
            for b in sc.get("blocks", [])
            if isinstance(b, dict) and ("settings" in b or "name" in b)
        }
        for bdef in (node_obj.get("blocks") or {}).values():
            if not isinstance(bdef, dict):
                continue
            btype = str(bdef.get("type") or "")
            if not btype:
                continue
            if not bdef.get("static", False):
                is_ok = (
                    btype in local_defs
                    or btype in allowed
                    or ("@theme" in allowed and not btype.startswith("_"))
                    or ("@app" in allowed and btype.startswith("shopify://apps/"))
                )
                if not is_ok:
                    missing_by_parent.setdefault((kind, node_type), set()).add(btype)
            if ("block", btype) in schemas:
                walk("block", btype, bdef)

    for folder in ("templates", "sections"):
        dir_path = theme_root / folder
        if not dir_path.is_dir():
            continue
        for fp in sorted(dir_path.glob("*.json")):
            try:
                _, data = split_shopify_json(fp.read_text(encoding="utf-8"))
            except Exception:
                continue
            for sdef in (data.get("sections") or {}).values():
                if isinstance(sdef, dict) and sdef.get("type"):
                    walk("section", str(sdef["type"]), sdef)

    messages: List[str] = []
    for (kind, node_type), missing_types in sorted(missing_by_parent.items()):
        entry = schemas[(kind, node_type)]
        sc = entry["schema"]
        blocks_arr = sc.setdefault("blocks", [])
        for bt in sorted(missing_types):
            messages.append(f"DISALLOWED_CHILD_BLOCK: {kind}:{node_type} missing '{bt}'")
            if write:
                blocks_arr.append({"type": bt})
        if write:
            raw = entry["raw"]
            new_schema_str = "\n" + json.dumps(sc, indent=2, ensure_ascii=False) + "\n"
            new_raw = SCHEMA_RX.sub(rf"\1{new_schema_str}\3", raw, count=1)
            entry["path"].write_text(new_raw, encoding="utf-8")
            entry["raw"] = new_raw
    return messages


def neutralize_and_validate_theme(theme_root: Path, write: bool = False) -> Dict[str, Any]:
    schemas = load_schemas(theme_root)
    valid_schemes = load_valid_color_schemes(theme_root)
    findings: List[str] = []
    fixes = 0

    # Step 1: Parent-child block allowlists
    block_msgs = sync_parent_block_allowlists(theme_root, schemas, write=write)
    if write:
        fixes += len(block_msgs)
    else:
        findings.extend(block_msgs)

    # Step 2: Check layout/theme.liquid and sections/footer-group.json
    layout_fp = theme_root / "layout" / "theme.liquid"
    if not layout_fp.is_file():
        findings.append("MISSING_LAYOUT: layout/theme.liquid not found")
    else:
        ltxt = layout_fp.read_text(encoding="utf-8")
        if not re.search(r"\{%-?\s*sections\s+['\"]footer-group['\"]\s*-?%\}", ltxt):
            findings.append("MISSING_FOOTER_GROUP_INCLUDE: layout/theme.liquid missing {% sections 'footer-group' %}")

    fg_fp = theme_root / "sections" / "footer-group.json"
    if not fg_fp.is_file():
        findings.append("MISSING_FOOTER_GROUP_JSON: sections/footer-group.json not found")
    else:
        hdr, fg_data = split_shopify_json(fg_fp.read_text(encoding="utf-8"))
        order = fg_data.get("order") or []
        secs = fg_data.get("sections") or {}
        active_types = [secs[sid].get("type") for sid in order if sid in secs and not secs[sid].get("disabled", False)]
        if "footer" not in active_types:
            findings.append("MISSING_ACTIVE_FOOTER: sections/footer-group.json has no active 'footer' section")
        if ("section", "footer-utilities") in schemas and "footer-utilities" not in active_types:
            if write:
                secs["footer_utilities"] = {
                    "type": "footer-utilities",
                    "blocks": {
                        "copyright": {
                            "type": "footer-copyright",
                            "settings": {"show_powered_by": False, "font_size": "0.75rem", "case": "none"},
                        },
                        "policy_list": {
                            "type": "footer-policy-list",
                            "settings": {"font_size": "0.75rem", "case": "none"},
                        },
                    },
                    "block_order": ["copyright", "policy_list"],
                    "settings": {
                        "section_width": "page-width",
                        "gap": 24,
                        "divider_thickness": 1,
                        "color_scheme": "scheme-1",
                        "padding-block-start": 20,
                        "padding-block-end": 20,
                    },
                }
                order.append("footer_utilities")
                fg_data["order"] = order
                fg_fp.write_text(hdr + json.dumps(fg_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                fixes += 1
            else:
                findings.append("MISSING_FOOTER_UTILITIES: sections/footer-group.json missing 'footer-utilities'")

    # Step 3: Validate and sanitize JSON templates & section groups
    def sanitize_node_settings(file_rel: str, kind: str, node_type: str, settings: Dict[str, Any]) -> bool:
        nonlocal fixes
        if not isinstance(settings, dict):
            return False
        entry = schemas.get((kind, node_type))
        if not entry:
            findings.append(f"{file_rel}: Missing schema for {kind}:{node_type}")
            return False
        smap = {s["id"]: s for s in entry["schema"].get("settings", []) if isinstance(s, dict) and "id" in s}
        changed = False
        for k in list(settings.keys()):
            v = settings[k]
            if isinstance(v, str) and re.match(r"^shopify://(shop_images|apps|pages|blogs|products)/", v):
                if write:
                    settings[k] = "" if v.startswith("shopify://shop_images/") else "#"
                    changed = True
                    fixes += 1
                else:
                    findings.append(f"{file_rel}: Foreign Shopify URI {k}={v!r}")
            if k not in smap:
                if write:
                    del settings[k]
                    changed = True
                    fixes += 1
                else:
                    findings.append(f"{file_rel}: Unknown setting '{k}' on {kind}:{node_type}")
                continue
            sdef = smap[k]
            st = sdef.get("type")
            if st == "color_scheme" and v not in valid_schemes:
                if write:
                    default_cs = sdef.get("default")
                    settings[k] = default_cs if default_cs in valid_schemes else "scheme-1"
                    changed = True
                    fixes += 1
                else:
                    findings.append(f"{file_rel}: Invalid color_scheme '{k}'={v!r} on {kind}:{node_type}")
            elif st == "select":
                opts = [o.get("value") for o in sdef.get("options", []) if isinstance(o, dict)]
                if v not in opts:
                    if write:
                        if k == "font" and "var(--font-body--family)" in opts:
                            settings[k] = "var(--font-body--family)"
                        elif k == "color" and "var(--color-foreground)" in opts:
                            settings[k] = "var(--color-foreground)"
                        elif sdef.get("default") in opts:
                            settings[k] = sdef.get("default")
                        elif opts:
                            settings[k] = opts[0]
                        changed = True
                        fixes += 1
                    else:
                        findings.append(f"{file_rel}: Invalid select '{k}'={v!r} on {kind}:{node_type}")
        return changed

    def walk_fix(file_rel: str, kind: str, node_type: str, node_obj: Dict[str, Any]) -> bool:
        changed = sanitize_node_settings(file_rel, kind, node_type, node_obj.get("settings"))
        for bdef in (node_obj.get("blocks") or {}).values():
            if isinstance(bdef, dict) and bdef.get("type"):
                btype = str(bdef["type"])
                if ("block", btype) in schemas:
                    if walk_fix(file_rel, "block", btype, bdef):
                        changed = True
        return changed

    checked_files = 0
    for folder in ("templates", "sections"):
        dir_path = theme_root / folder
        if not dir_path.is_dir():
            continue
        for fp in sorted(dir_path.glob("*.json")):
            checked_files += 1
            rel = f"{folder}/{fp.name}"
            hdr, data = split_shopify_json(fp.read_text(encoding="utf-8"))
            file_changed = False
            for sdef in (data.get("sections") or {}).values():
                if isinstance(sdef, dict) and sdef.get("type"):
                    if walk_fix(rel, "section", str(sdef["type"]), sdef):
                        file_changed = True
            if write and file_changed:
                fp.write_text(hdr + json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "checked_files": checked_files,
        "findings": findings,
        "fixes": fixes,
    }


def build_clean_zip(theme_root: Path, zip_path: Path) -> Tuple[int, int]:
    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in THEME_ZIP_DIRS:
            dir_path = theme_root / d
            if not dir_path.is_dir():
                continue
            for root, _, files in os.walk(dir_path):
                for f in sorted(files):
                    if f.startswith("."):
                        continue
                    fp = Path(root) / f
                    rel = fp.relative_to(theme_root)
                    zf.write(fp, str(rel))
                    file_count += 1
    return file_count, zip_path.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser(description="One-Pass Shopify OS 2.0 Theme Neutralizer & Customizer Guard")
    parser.add_argument("theme_root", type=Path, help="Path to Shopify theme directory")
    parser.add_argument("--write", action="store_true", help="Apply fixes in-place")
    parser.add_argument("--zip", type=Path, default=None, help="Optional path to output clean .zip archive")
    args = parser.parse_args()

    res = neutralize_and_validate_theme(args.theme_root, write=args.write)
    if args.zip:
        cnt, size = build_clean_zip(args.theme_root, args.zip)
        print(f"Built clean theme archive: {args.zip} ({cnt} files, {size:,} bytes)")

    if res["findings"]:
        for f in res["findings"][:25]:
            print(f"ERROR: {f}", file=sys.stderr)
        print(
            f"Shopify Theme Neutralizer: {res['checked_files']} files checked, {len(res['findings'])} errors found.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Shopify Theme Neutralizer PASS: {res['checked_files']} JSON templates/groups verified, "
        f"0 errors ({res['fixes']} fixes applied)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
