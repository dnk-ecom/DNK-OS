#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/scripts/audit_commercial_theme_zip.py"
# purpose: "One-shot deterministic forensic auditor for commercial Shopify theme ZIP archives (OS 2.0 & Theme Blocks 2.0)."
# canonical_source: true
# status: "Active"
# version: "1.1.0"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""One-shot forensic audit script for commercial Shopify theme ZIP archives.

Usage:
    python3 audit_commercial_theme_zip.py <path_to_theme.zip>
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter

CANONICAL_SHOPIFY_DIRS = {
    "assets",
    "blocks",
    "config",
    "layout",
    "locales",
    "sections",
    "snippets",
    "templates",
}


def strip_json_comments(text: str, strip_trailing_commas: bool = False) -> str:
    """String-aware C-style comment and optional trailing-comma stripper for JSON."""
    out = []
    i = 0
    n = len(text)
    in_str = False
    esc = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
        else:
            if ch == '"':
                in_str = True
                out.append(ch)
                i += 1
            elif ch == "/" and i + 1 < n and text[i + 1] == "*":
                i += 2
                while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i += 2
            elif ch == "/" and i + 1 < n and text[i + 1] == "/":
                i += 2
                while i < n and text[i] not in "\r\n":
                    i += 1
            else:
                out.append(ch)
                i += 1
    res = "".join(out)
    if strip_trailing_commas:
        res = re.sub(r",\s*([}\]])", r"\1", res)
    return res


def audit_zip(zip_path: str) -> int:
    with zipfile.ZipFile(zip_path, "r") as z:
        files = [f for f in z.namelist() if not f.endswith("/")]
        print(f"=== THEME ZIP FORENSIC AUDIT: {zip_path} ({len(files)} files) ===")

        top_dirs = Counter(f.split("/")[0] if "/" in f else "ROOT" for f in files)
        invalid_dirs = set(top_dirs.keys()) - CANONICAL_SHOPIFY_DIRS
        print("1. Directory Structure:", dict(sorted(top_dirs.items())))
        if invalid_dirs:
            print(f"   [!] Non-standard root entries detected (Shopify upload blocker): {sorted(invalid_dirs)}")

        json_raw_valid = 0
        json_commented = 0
        json_trailing_comma = []
        json_broken = []

        for f in sorted(files):
            if f.endswith(".json"):
                raw = z.read(f).decode("utf-8", errors="replace").lstrip("\ufeff")
                try:
                    json.loads(raw)
                    json_raw_valid += 1
                except Exception:
                    try:
                        json.loads(strip_json_comments(raw, False))
                        json_commented += 1
                    except Exception:
                        try:
                            json.loads(strip_json_comments(raw, True))
                            json_trailing_comma.append(f)
                        except Exception as e:
                            json_broken.append((f, str(e)))

        print(
            f"2. JSON RFC 8259 Status: raw_valid={json_raw_valid}, "
            f"comment_headers={json_commented}, trailing_comma={len(json_trailing_comma)}, "
            f"broken={len(json_broken)}"
        )
        for f in json_trailing_comma:
            print(f"   - Trailing comma in JSON: {f}")
        for f, err in json_broken:
            print(f"   - Broken JSON: {f}: {err}")

        schema_trailing = []
        for f in sorted(files):
            if f.endswith(".liquid"):
                txt = z.read(f).decode("utf-8", errors="replace")
                m = re.search(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", txt, re.S)
                if m:
                    raw_s = m.group(1).strip()
                    try:
                        json.loads(raw_s)
                    except Exception:
                        try:
                            json.loads(strip_json_comments(raw_s, True))
                            schema_trailing.append(f)
                        except Exception as e:
                            print(f"   - Broken Liquid Schema in {f}: {e}")
        print(f"3. Liquid {{% schema %}} trailing commas: {len(schema_trailing)} files")

        drm_patterns = {
            "atob_btoa": re.compile(r"\b(atob|btoa)\s*\("),
            "fromCharCode": re.compile(r"String\.fromCharCode"),
            "supabase_firebase": re.compile(r"supabase|firebase|verify-activation", re.I),
            "drm_globals": re.compile(
                r"__te_d|__su|__ru|__tu|__sd|__stArmed|showHydrationFallback|"
                r"coun_viriality|ririality|validateDomainAccess|handleUnauthorizedAccess|"
                r"initThemeLicenseCheck|POST_LINK_INT|internationalAccessAccept|popupTimer"
            ),
            "string_concat_dom_wipe": re.compile(
                r"['\"]bod['\"]\s*\+\s*['\"]y['\"]|['\"]inne['\"]\s*\+\s*['\"]rH['\"]"
            ),
            "dropship_backdoors": re.compile(r"cjdropshipping|zippyhound|pod3\.js|cjpod", re.I),
            "external_cdn": re.compile(
                r"https?://(?:cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com|fonts\.googleapis\.com|cdn\d*\.iconfinder\.com)[^\s\"')<>]*",
                re.I,
            ),
            "foreign_shopify_store_files": re.compile(
                r"(?:https?:)?//cdn\.shopify\.com/s/files/1/\d{4}/\d{4}/\d{4}/[^\s\"')<>]*",
                re.I,
            ),
            "vendor_traces": re.compile(
                r"halothemes|lumintheme|groupthought|envato\.market|themeforest\.net|t\.me/",
                re.I,
            ),
        }

        print("4. DRM, External CDN & Vendor Leak Scan:")
        for label, pat in drm_patterns.items():
            hits = []
            for f in sorted(files):
                if f.endswith((".liquid", ".js", ".css", ".json", ".ts")):
                    txt = z.read(f).decode("utf-8", errors="replace")
                    matches = pat.findall(txt)
                    if matches:
                        hits.append((f, len(matches)))
            print(f"   - {label}: {len(hits)} files {hits[:8]}")

        locales = [f for f in files if f.startswith("locales/") and f.endswith(".json")]
        storefront_langs = {
            f.split("/")[-1].replace(".default.json", "").replace(".json", "")
            for f in locales
            if not f.endswith(".schema.json")
        }
        schema_langs = {
            f.split("/")[-1].replace(".default.schema.json", "").replace(".schema.json", "")
            for f in locales
            if f.endswith(".schema.json")
        }
        print(
            f"5. Locales: total={len(locales)}, uk_present={'uk' in storefront_langs and 'uk' in schema_langs}, "
            f"missing_storefront={sorted(schema_langs - storefront_langs)}, "
            f"missing_schema={sorted(storefront_langs - schema_langs)}"
        )

        # 6. JavaScript Syntax Gate (node --check on all .js and {% javascript %} blocks)
        js_errors = []
        if shutil.which("node"):
            with tempfile.TemporaryDirectory() as tmpdir:
                for f in sorted(files):
                    if f.endswith(".js"):
                        tmp_js = os.path.join(tmpdir, "check.js")
                        with open(tmp_js, "wb") as out_f:
                            out_f.write(z.read(f))
                        res = subprocess.run(["node", "--check", tmp_js], capture_output=True, text=True)
                        if res.returncode != 0:
                            js_errors.append((f, res.stderr.strip().splitlines()[0] if res.stderr else "SyntaxError"))
                    elif f.endswith(".liquid"):
                        txt = z.read(f).decode("utf-8", errors="replace")
                        for idx, m in enumerate(
                            re.finditer(r"\{%-?\s*javascript\s*-?%\}(.*?)\{%-?\s*endjavascript\s*-?%\}", txt, re.S)
                        ):
                            tmp_js = os.path.join(tmpdir, f"liquid_{idx}.js")
                            with open(tmp_js, "w", encoding="utf-8") as out_f:
                                out_f.write(m.group(1))
                            res = subprocess.run(["node", "--check", tmp_js], capture_output=True, text=True)
                            if res.returncode != 0:
                                js_errors.append(
                                    (f"{f}#javascript[{idx}]", res.stderr.strip().splitlines()[0] if res.stderr else "SyntaxError")
                                )
        print(f"6. JavaScript Syntax (node --check): {len(js_errors)} errors")
        for f, err in js_errors:
            print(f"   - JS Syntax Error in {f}: {err}")

        # 7. CustomElements Registration & Guard Audit
        defined_elements = set()
        unguarded_defines = []
        for f in sorted(files):
            if f.endswith((".js", ".liquid")):
                txt = z.read(f).decode("utf-8", errors="replace")
                for m in re.finditer(r"customElements\.define\(\s*['\"]([^'\"]+)['\"]", txt):
                    tag = m.group(1)
                    defined_elements.add(tag)
                    start_ctx = max(0, m.start() - 1200)
                    ctx = txt[start_ctx : m.start()]
                    if f"customElements.get('{tag}')" not in ctx and f'customElements.get("{tag}")' not in ctx:
                        unguarded_defines.append((f, tag))
        print(
            f"7. CustomElements Registry: {len(defined_elements)} defined, "
            f"unguarded_defines={len(unguarded_defines)}"
        )

        # 8. <side-drawer> Structural Integrity Gate
        drawer_issues = []
        for f in sorted(files):
            if f.endswith(".liquid"):
                txt = z.read(f).decode("utf-8", errors="replace")
                for m in re.finditer(r"<side-drawer\b[^>]*>(.*?)</side-drawer>", txt, re.S):
                    block = m.group(0)
                    missing = []
                    if 'id="Drawer-Overlay-' not in block:
                        missing.append("Drawer-Overlay-id")
                    if "data-drawer-content" not in block:
                        missing.append("data-drawer-content")
                    if "data-drawer-direction" not in block:
                        missing.append("data-drawer-direction")
                    if missing:
                        drawer_issues.append((f, missing))
        print(f"8. <side-drawer> Structural Integrity: {len(drawer_issues)} incomplete drawers")
        for f, missing in drawer_issues:
            print(f"   - Incomplete <side-drawer> in {f}: missing {missing}")
    return 1 if (invalid_dirs or json_broken or js_errors or drawer_issues) else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 audit_commercial_theme_zip.py <path_to_theme.zip>")
        sys.exit(1)
    sys.exit(audit_zip(sys.argv[1]))
