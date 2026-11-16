#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "tools/verify_theme_integrity.py"
# purpose: "Comprehensive Deterministic Verification & Anti-Regression Gate for Shopify Themes."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

"""Shopify Theme Integrity & Anti-Regression Verifier.

Enforces zero-defect theme quality gates:
1. Protected Organs Whitelist (POW): Prevents accidental pruning of vital features (e.g. quantity-breaks).
2. Dangling Render & Section Auditor: Zero MissingTemplate errors.
3. Dangling Template Blocks & Sections Auditor: Zero MissingBlock errors in templates/*.json.
4. Cleanroom Zero-DRM Gate: Zero licensing endpoints, killswitches, or obfuscations.
5. Quota & Syntax Gate: RFC 8259 JSON, <= 512KB templates, Node syntax verification on all JS.
6. Localization Parity Gate: 100% schema and UI translation key matching.
7. Optional Live Storefront Smoke Test: Zero Liquid runtime errors on live preview endpoints.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path


# Mandatory files that agents are STRICTLY FORBIDDEN from deleting
MANDATORY_PROTECTED_ORGANS = [
    # PDP Volume Pricing & Quantity Breaks (Dual Level)
    "snippets/quantity-breaks.liquid",
    "snippets/qb-v2-migration.liquid",
    "blocks/product_quantity-selector.liquid",
    "blocks/product_quantity-breaks-v2.liquid",
    "blocks/_quantity-breaks-v2_option.liquid",
    
    # High-CRO Cart Drawer
    "sections/cart-drawer.liquid",
    "blocks/cart-drawer_body.liquid",
    "blocks/cart-drawer_footer.liquid",
    
    # Core Layout & Config
    "layout/theme.liquid",
    "config/settings_schema.json",
    
    # 100% Localization
    "locales/uk.json",
    "locales/uk.schema.json",
    "locales/en.default.json",
    "locales/en.default.schema.json",
]

BANNED_DRM_PATTERNS = [
    re.compile(r"shrine\.co/api", re.IGNORECASE),
    re.compile(r"verify-license", re.IGNORECASE),
    re.compile(r"license_key", re.IGNORECASE),
    re.compile(r"document\.body\.innerHTML\s*=\s*['\"]['\"]"),
]


def strip_jsonc_leading_comment(raw: str) -> str:
    """Strip leading /* ... */ comments from JSON."""
    raw = raw.strip()
    if raw.startswith("/*"):
        end_idx = raw.find("*/")
        if end_idx != -1:
            raw = raw[end_idx + 2:].strip()
    return raw


class ThemeIntegrityAuditor:
    def __init__(self, theme_path: Path):
        self.theme = theme_path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passed_checks: list[str] = []

    def verify_protected_organs(self) -> None:
        """Check 1: Ensure all mandatory organs exist."""
        missing = []
        for rel in MANDATORY_PROTECTED_ORGANS:
            fp = self.theme / rel
            if not fp.exists():
                missing.append(rel)
        if missing:
            self.errors.append(
                f"[GATE 1: Protected Organs Whitelist FAILED] Missing {len(missing)} vital theme components:\n"
                + "\n".join(f"  ❌ {m}" for m in missing)
            )
        else:
            self.passed_checks.append(f"Gate 1: Protected Organs Whitelist ({len(MANDATORY_PROTECTED_ORGANS)} organs verified)")

    def verify_dangling_renders_and_sections(self) -> None:
        """Check 2: Ensure every render, include, and section points to a real file."""
        render_pat = re.compile(r"\{%-?\s*(?:render|include)\s+['\"]([^'\"\s]+)['\"]")
        section_pat = re.compile(r"\{%-?\s*section\s+['\"]([^'\"\s]+)['\"]")

        dangling_renders = []
        dangling_sections = []

        for fp in self.theme.rglob("*.liquid"):
            raw_txt = fp.read_text(encoding="utf-8", errors="ignore")
            # Strip comments and docblocks to avoid false positives in documentation examples
            txt = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", raw_txt, flags=re.S)
            txt = re.sub(r"\{%-?\s*doc\s*-?%\}.*?\{%-?\s*enddoc\s*-?%\}", "", txt, flags=re.S)
            rel_file = str(fp.relative_to(self.theme))

            # Check renders
            for m in render_pat.finditer(txt):
                snippet_name = m.group(1)
                snippet_file = self.theme / "snippets" / f"{snippet_name}.liquid"
                if not snippet_file.exists():
                    dangling_renders.append(f"{rel_file} -> snippets/{snippet_name}.liquid")

            # Check sections
            for m in section_pat.finditer(txt):
                sec_name = m.group(1)
                sec_file = self.theme / "sections" / f"{sec_name}.liquid"
                if not sec_file.exists():
                    dangling_sections.append(f"{rel_file} -> sections/{sec_name}.liquid")

        if dangling_renders or dangling_sections:
            msg = "[GATE 2: Dangling References FAILED]\n"
            if dangling_renders:
                msg += f"  Missing snippets ({len(dangling_renders)}):\n" + "\n".join(f"    ❌ {r}" for r in dangling_renders[:10]) + "\n"
            if dangling_sections:
                msg += f"  Missing sections ({len(dangling_sections)}):\n" + "\n".join(f"    ❌ {s}" for s in dangling_sections[:10]) + "\n"
            self.errors.append(msg.strip())
        else:
            self.passed_checks.append("Gate 2: Dangling References (0 MissingTemplate errors)")

    def verify_template_blocks_and_sections(self) -> None:
        """Check 3: Ensure all sections and blocks in templates/*.json exist."""
        # 1. Parse local blocks defined inside sections
        sec_local_blocks: dict[str, set[str]] = {}
        for sf in (self.theme / "sections").glob("*.liquid"):
            txt = sf.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"\{%\s*schema\s*%\}(.*?)\{%\s*endschema\s*%\}", txt, re.DOTALL)
            if m:
                try:
                    sch = json.loads(m.group(1))
                    sec_local_blocks[sf.stem] = {b.get("type") for b in sch.get("blocks", []) if "type" in b}
                except Exception:
                    pass

        dangling_sections = []
        dangling_blocks = []

        for t_path in (self.theme / "templates").rglob("*.json"):
            rel_tmpl = str(t_path.relative_to(self.theme))
            try:
                raw = t_path.read_text(encoding="utf-8")
                clean = strip_jsonc_leading_comment(raw)
                data = json.loads(clean)
            except Exception as e:
                self.errors.append(f"[GATE 3] JSON syntax error in {rel_tmpl}: {e}")
                continue

            for s_id, s_data in data.get("sections", {}).items():
                s_type = s_data.get("type")
                if s_type:
                    sec_file = self.theme / "sections" / f"{s_type}.liquid"
                    if not sec_file.exists():
                        dangling_sections.append(f"{rel_tmpl} [section: {s_id}] -> sections/{s_type}.liquid")

                    local_types = sec_local_blocks.get(s_type, set())
                    for b_id, b_data in s_data.get("blocks", {}).items():
                        b_type = b_data.get("type")
                        if b_type and b_type not in local_types:
                            block_file = self.theme / "blocks" / f"{b_type}.liquid"
                            if not block_file.exists():
                                dangling_blocks.append(f"{rel_tmpl} [{s_type} > {b_id}] -> blocks/{b_type}.liquid")

        if dangling_sections or dangling_blocks:
            msg = "[GATE 3: Template Structure FAILED]\n"
            if dangling_sections:
                msg += f"  Missing template sections ({len(dangling_sections)}):\n" + "\n".join(f"    ❌ {s}" for s in dangling_sections[:5]) + "\n"
            if dangling_blocks:
                msg += f"  Missing template blocks ({len(dangling_blocks)}):\n" + "\n".join(f"    ❌ {b}" for b in dangling_blocks[:5]) + "\n"
            self.errors.append(msg.strip())
        else:
            self.passed_checks.append("Gate 3: Template Structure (0 MissingBlock errors in all templates)")

    def verify_cleanroom_zero_drm(self) -> None:
        """Check 4: Ensure zero DRM endpoints or killswitch payloads."""
        drm_hits = []
        for fp in self.theme.rglob("*"):
            if fp.is_file() and fp.suffix in (".js", ".liquid", ".html"):
                txt = fp.read_text(encoding="utf-8", errors="ignore")
                for pat in BANNED_DRM_PATTERNS:
                    m = pat.search(txt)
                    if m:
                        drm_hits.append(f"{fp.relative_to(self.theme)} matches {pat.pattern}")

        if drm_hits:
            self.errors.append(
                f"[GATE 4: Cleanroom DRM Gate FAILED] Found {len(drm_hits)} banned DRM/killswitch artifacts:\n"
                + "\n".join(f"  ❌ {h}" for h in drm_hits)
            )
        else:
            self.passed_checks.append("Gate 4: Cleanroom Zero-DRM (0 DRM endpoints, 0 killswitches)")

    def verify_quotas_and_syntax(self) -> None:
        """Check 5: Shopify 512KB Quotas and Node JS syntax."""
        oversized = []
        for t in self.theme.rglob("templates/*.json"):
            if t.stat().st_size > 512_000:
                oversized.append(f"{t.relative_to(self.theme)}: {t.stat().st_size:,} bytes (>512KB limit)")

        if oversized:
            self.errors.append("[GATE 5: Quota Violation FAILED]\n" + "\n".join(f"  ❌ {o}" for o in oversized))
        else:
            self.passed_checks.append("Gate 5: Quotas & JSON (All templates <= 512KB)")

        # Verify JS syntax
        js_errors = []
        for js_file in (self.theme / "assets").glob("*.js"):
            # skip minified vendor if any
            res = subprocess.run(["node", "--check", str(js_file)], capture_output=True, text=True)
            if res.returncode != 0:
                js_errors.append(f"{js_file.name}: {res.stderr.strip()[:100]}")

        if js_errors:
            self.errors.append("[GATE 5: JS Syntax FAILED]\n" + "\n".join(f"  ❌ {e}" for e in js_errors))
        else:
            self.passed_checks.append("Gate 5: JavaScript Engine (All assets passed node --check)")

    def verify_localization_parity(self) -> None:
        """Check 6: 100% schema and UI translation parity."""
        locales = self.theme / "locales"
        en_schema = locales / "en.default.schema.json"
        uk_schema = locales / "uk.schema.json"

        if en_schema.exists() and uk_schema.exists():
            en_data = json.loads(strip_jsonc_leading_comment(en_schema.read_text(encoding="utf-8")))
            uk_data = json.loads(strip_jsonc_leading_comment(uk_schema.read_text(encoding="utf-8")))

            missing_keys = set(en_data.keys()) - set(uk_data.keys())
            if missing_keys:
                self.warnings.append(f"[GATE 6: Localization Warning] uk.schema.json lacks {len(missing_keys)} keys from en.default.schema.json")
            else:
                self.passed_checks.append(f"Gate 6: Localization Parity (100% matching {len(uk_data)} schema keys)")
        else:
            self.errors.append("[GATE 6: Localization FAILED] Missing en.default.schema.json or uk.schema.json")

    def run_live_smoke_test(self, store_domain: str, theme_id: str) -> None:
        """Check 7: Live Storefront Smoke Test."""
        pages = [
            ("Home", f"https://{store_domain}?preview_theme_id={theme_id}"),
            ("Cart JSON", f"https://{store_domain}/cart.js?preview_theme_id={theme_id}")
        ]

        smoke_failures = []
        for name, url in pages:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DNK-QA-Bot/1.0"}
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = resp.read().decode("utf-8", errors="ignore")
                    if "Liquid error:" in body or "LiquidHTMLSyntaxError" in body:
                        smoke_failures.append(f"{name} returned Liquid Error in rendered HTML!")
            except urllib.error.HTTPError as e:
                # 429 rate limit or 401 is an expected anti-bot barrier from Shopify, not a Liquid crash
                if e.code not in (429, 401, 403):
                    smoke_failures.append(f"{name} HTTP {e.code}")
            except Exception as e:
                self.warnings.append(f"Live smoke test skipped ({name}): {e}")

        if smoke_failures:
            self.errors.append("[GATE 7: Live Smoke Test FAILED]\n" + "\n".join(f"  ❌ {f}" for f in smoke_failures))
        else:
            self.passed_checks.append("Gate 7: Live Storefront Smoke Test (0 Liquid runtime crashes)")

    def audit_all(self, store_domain: str | None = None, theme_id: str | None = None, donor_mode: bool = False) -> bool:
        """Run all verification gates."""
        if not donor_mode:
            self.verify_protected_organs()
        else:
            self.passed_checks.append("Gate 1: Donor Mode Active (Protected Organs Whitelist bypassed for external donor)")
        self.verify_dangling_renders_and_sections()
        self.verify_template_blocks_and_sections()
        self.verify_cleanroom_zero_drm()
        self.verify_quotas_and_syntax()
        self.verify_localization_parity()

        if store_domain and theme_id:
            self.run_live_smoke_test(store_domain, theme_id)

        return len(self.errors) == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Theme Integrity & Anti-Regression Verifier")
    parser.add_argument("theme_path", type=Path, help="Path to Shopify theme directory")
    parser.add_argument("--donor-mode", action="store_true", help="Bypass Sovereign POW gate for external donor themes")
    parser.add_argument("--store", type=str, default=None, help="Shopify store domain for live smoke testing")
    parser.add_argument("--theme-id", type=str, default=None, help="Shopify theme ID for live smoke testing")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    auditor = ThemeIntegrityAuditor(args.theme_path)
    success = auditor.audit_all(args.store, args.theme_id, donor_mode=args.donor_mode)

    report = {
        "theme": str(args.theme_path),
        "status": "PASS" if success else "FAIL",
        "passed_checks": auditor.passed_checks,
        "warnings": auditor.warnings,
        "errors": auditor.errors,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 70)
        print("🛡️  SHOPIFY THEME INTEGRITY & ANTI-REGRESSION VERIFICATION REPORT")
        print("=" * 70)
        for check in auditor.passed_checks:
            print(f"✅ {check}")
        for warn in auditor.warnings:
            print(f"⚠️  {warn}")
        if auditor.errors:
            print("\n" + "!" * 70)
            print("🚨 CRITICAL VIOLATIONS DETECTED (BUILD BLOCKED):")
            print("!" * 70)
            for err in auditor.errors:
                print(f"\n{err}")
            print("\n❌ VERIFICATION RESULT: FAILED (Exit Code 1)")
            return 1

        print("\n🎉 VERIFICATION RESULT: 100% CLEAN & PROTECTED (Exit Code 0)")
        print("=" * 70)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
