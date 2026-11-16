#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "_Shopify_Theme_DEV_Workflow/companion/companion_distiller.py"
# purpose: "Recursive Donor Distiller, Apex Taxonomy Graph Builder & Molecular Grafter for DNK Sovereign Theme"
# canonical_source: true
# alters_files: [
#   "_Shopify_Theme_DEV_Workflow/companion/APEX_TAXONOMY_GRAPH.json",
#   "_Shopify_Theme_DEV_Workflow/companion/GOLDEN_MOLECULES_INDEX.json"
# ]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

"""Shopify Theme Companion Recursive Distiller.

Scans all worktrees in DNK-Ecom_git_mirrow, builds an AST connectivity graph,
detects Theme Blocks 2.0 compliance, flags DRM/trackers, scores each component
on the 100-point Apex Quality Scale, generates APEX_TAXONOMY_GRAPH.json and
GOLDEN_MOLECULES_INDEX.json, and executes cleanroom molecular grafting into
the target commercial theme.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class ComponentMeta:
    donor: str
    component_type: str  # section, block, snippet, asset
    rel_path: str
    abs_path: str
    size_bytes: int
    has_blocks_2_0: bool = False
    has_custom_elements: bool = False
    custom_elements: List[str] = field(default_factory=list)
    rendered_snippets: List[str] = field(default_factory=list)
    required_assets: List[str] = field(default_factory=list)
    drm_flags: List[str] = field(default_factory=list)
    framework_flags: List[str] = field(default_factory=list)
    has_schema: bool = False
    supports_app_blocks: bool = False
    has_i18n_keys: bool = False
    apex_score: int = 0
    commercial_role: str = ""
    graft_ready: bool = False


class CompanionDistiller:
    """Recursive AST scanner and distillation factory for theme donors."""

    DRM_PATTERNS = [
        ("ECDSA Watchdog", re.compile(r"head-bootstrap\.js", re.I)),
        ("Shopify.shop Lock", re.compile(r"Shopify\.shop\s*===|\.shop\.permanent_domain", re.I)),
        ("Screen Freeze", re.compile(r"\.sw-fr|freeze-screen", re.I)),
        ("Remote Verify API", re.compile(r"/api/verify|\.herokuapp\.com/license", re.I)),
        ("Facebook Pixel", re.compile(r"fbq\(", re.I)),
        ("TikTok Pixel", re.compile(r"ttq\.", re.I)),
        ("Google Tag", re.compile(r"gtag\(", re.I)),
        ("External CDN", re.compile(r"cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com", re.I)),
    ]

    FRAMEWORK_PATTERNS = [
        ("jQuery", re.compile(r"\$\(|jQuery\(", re.I)),
        ("Alpine.js", re.compile(r"x-data|x-bind|x-init", re.I)),
        ("React/Vue", re.compile(r"React\.createElement|vue\.js|__vue__", re.I)),
    ]

    def __init__(self, mirror_dir: Path, target_dir: Path, companion_dir: Path):
        self.mirror_dir = mirror_dir
        self.target_dir = target_dir
        self.companion_dir = companion_dir
        self.components: Dict[str, ComponentMeta] = {}
        self.taxonomy_graph: Dict[str, Any] = {}
        self.golden_index: List[Dict[str, Any]] = []

    def scan_worktrees(self) -> None:
        """Scan all donor worktrees in DNK-Ecom_git_mirrow."""
        if not self.mirror_dir.exists():
            raise FileNotFoundError(f"Mirror directory not found: {self.mirror_dir}")

        donors = [d for d in self.mirror_dir.iterdir() if d.is_dir() and d.name != ".bare"]

        for donor_path in sorted(donors):
            donor_name = donor_path.name
            self._scan_donor(donor_name, donor_path)

        # Also scan Elixir audit repository if available
        elixir_dir = Path("/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNKEcom/Audit_Shopify_Themes_Sell_WF/Elixir_Theme_Ecosystem_Audit")
        if elixir_dir.exists():
            # If sections or blocks exist, scan them under 'elixir'
            self._scan_donor("elixir", elixir_dir)

        # Also scan sterilized vaults from _Shopify_Theme_Audit_Workflow/distilled_vault
        vault_dir = Path(__file__).parent.parent.parent / "_Shopify_Theme_Audit_Workflow" / "distilled_vault"
        if vault_dir.exists():
            for v_path in vault_dir.iterdir():
                if v_path.is_dir():
                    self._scan_donor(f"vault-{v_path.name}", v_path)

        self._build_apex_taxonomy()

    def _scan_donor(self, donor_name: str, base_path: Path) -> None:
        folders = [
            ("sections", "section", "*.liquid"),
            ("blocks", "block", "*.liquid"),
            ("snippets", "snippet", "*.liquid"),
            ("assets", "asset", "*.*")
        ]

        for folder_name, comp_type, glob_pat in folders:
            folder = base_path / folder_name
            if not folder.exists():
                continue

            for file_path in folder.glob(glob_pat):
                if file_path.is_file():
                    self._analyze_file(donor_name, comp_type, file_path)

    def _analyze_file(self, donor_name: str, comp_type: str, file_path: Path) -> None:
        rel_path = f"{file_path.parent.name}/{file_path.name}"
        key = f"{donor_name}::{rel_path}"
        size_bytes = file_path.stat().st_size

        meta = ComponentMeta(
            donor=donor_name,
            component_type=comp_type,
            rel_path=rel_path,
            abs_path=str(file_path),
            size_bytes=size_bytes
        )

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            self.components[key] = meta
            return

        # Check Theme Blocks 2.0 directive
        if "content_for 'blocks'" in content or 'content_for "blocks"' in content:
            meta.has_blocks_2_0 = True

        # Check custom elements
        custom_elements = re.findall(r"customElements\.define\(['\"]([a-z0-9-]+)['\"]", content)
        tag_matches = re.findall(r"<([a-z0-9]+-[a-z0-9-]+)[\s>]", content)
        all_ce = sorted(list(set(custom_elements + tag_matches)))
        if all_ce:
            meta.has_custom_elements = True
            meta.custom_elements = all_ce

        # Check rendered snippets
        renders = re.findall(r"\{%-?\s*(?:render|include)\s+['\"]([a-zA-Z0-9_-]+)['\"]", content)
        meta.rendered_snippets = sorted(list(set(renders)))

        # Check required assets
        assets = re.findall(r"['\"]([a-zA-Z0-9_-]+\.(?:css|js))['\"]\s*\|\s*asset_url", content)
        meta.required_assets = sorted(list(set(assets)))

        # Check DRM flags
        for name, pat in self.DRM_PATTERNS:
            if pat.search(content):
                meta.drm_flags.append(name)

        # Check Framework flags
        for name, pat in self.FRAMEWORK_PATTERNS:
            if pat.search(content):
                meta.framework_flags.append(name)

        # Check Schema
        schema_m = re.search(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", content, re.S)
        if schema_m:
            meta.has_schema = True
            raw_schema = schema_m.group(1).strip()
            # Clean trailing commas
            cleaned_schema = re.sub(r",\s*([}\]])", r"\1", raw_schema)
            try:
                schema_json = json.loads(cleaned_schema)
                if isinstance(schema_json.get("blocks"), list):
                    if any(b.get("type") == "@app" for b in schema_json["blocks"] if isinstance(b, dict)):
                        meta.supports_app_blocks = True
            except Exception:
                pass

        # Check i18n
        if re.search(r"\|\s*t\b", content) or '"t:' in content:
            meta.has_i18n_keys = True

        # Compute Apex Score (0 - 100)
        score = 0
        # 1. Architectural Purity (up to 25 pts)
        if not meta.framework_flags:
            score += 15
        if meta.has_custom_elements:
            score += 10

        # 2. Theme Blocks 2.0 Readiness (up to 25 pts)
        if meta.has_blocks_2_0:
            score += 15
        if meta.supports_app_blocks:
            score += 10
        elif comp_type in ("snippet", "asset") and not meta.framework_flags:
            score += 10

        # 3. Cleanroom & Compliance (up to 25 pts)
        if not meta.drm_flags:
            score += 15
        if meta.has_i18n_keys:
            score += 5
        if meta.size_bytes <= 25_600:
            score += 5

        # 4. Commercial & CRO Value (up to 25 pts)
        high_value_keywords = [
            "cart", "drawer", "upsell", "progress", "quantity", "volume",
            "bundle", "quiz", "lookbook", "comparison", "columns", "media-sizes",
            "tier", "sticky", "scratch", "timeline"
        ]
        if any(kw in file_path.name.lower() for kw in high_value_keywords):
            score += 25
        else:
            score += 10

        meta.apex_score = min(100, score)
        meta.commercial_role = self._assign_commercial_role(file_path.name, donor_name)
        meta.graft_ready = (not meta.drm_flags) and (meta.apex_score >= 65)

        self.components[key] = meta

    def _assign_commercial_role(self, filename: str, donor: str) -> str:
        fn = filename.lower()
        if "cart" in fn or "drawer" in fn:
            return "High-CRO AJAX Cart Drawer & Rewards Engine"
        if "quantity" in fn or "bundle" in fn or "volume" in fn:
            return "D2C Tiered Pricing & Bundle Booster"
        if "column" in fn or "grid" in fn:
            return "Universal 12-Column Theme Blocks 2.0 Canvas"
        if "media-sizes" in fn or "image" in fn:
            return "Core Web Vitals Dynamic LCP Sizing Optimizer"
        if "lookbook" in fn or "pin" in fn:
            return "Editorial Storytelling & Interactive Hotspot Pinning"
        if "comparison" in fn:
            return "Advertorial Comparison Table ('Us vs Competitors')"
        if "timeline" in fn or "story" in fn:
            return "Brand Narrative & Chronological Scroller"
        if "header" in fn or "footer" in fn:
            return "Canonical Navigation & Foundation Frame"
        return "Specialized Theme Element"

    def _build_apex_taxonomy(self) -> None:
        """Build connectivity graph and Top-30 golden molecules index."""
        donors_summary: Dict[str, Any] = {}
        for key, meta in self.components.items():
            d = meta.donor
            if d not in donors_summary:
                donors_summary[d] = {
                    "total_files": 0,
                    "blocks_count": 0,
                    "sections_count": 0,
                    "snippets_count": 0,
                    "assets_count": 0,
                    "theme_blocks_2_0_count": 0,
                    "cleanroom_clean": True,
                    "avg_apex_score": 0.0,
                    "scores": []
                }
            s = donors_summary[d]
            s["total_files"] += 1
            if meta.component_type == "block":
                s["blocks_count"] += 1
            elif meta.component_type == "section":
                s["sections_count"] += 1
            elif meta.component_type == "snippet":
                s["snippets_count"] += 1
            elif meta.component_type == "asset":
                s["assets_count"] += 1

            if meta.has_blocks_2_0:
                s["theme_blocks_2_0_count"] += 1
            if meta.drm_flags:
                s["cleanroom_clean"] = False
            s["scores"].append(meta.apex_score)

        for d, s in donors_summary.items():
            if s["scores"]:
                s["avg_apex_score"] = round(sum(s["scores"]) / len(s["scores"]), 1)
            del s["scores"]

        self.taxonomy_graph = {
            "meta": {
                "generated_at": "2026-11-12",
                "total_scanned_components": len(self.components),
                "donors_count": len(donors_summary)
            },
            "donors": donors_summary,
            "components": {k: asdict(v) for k, v in self.components.items()}
        }

        # Filter and rank Top Golden Molecules (Cleanroom Ready, High Apex Score)
        sorted_candidates = sorted(
            [m for m in self.components.values() if m.graft_ready and m.component_type in ("section", "block", "snippet", "asset")],
            key=lambda x: (x.apex_score, -x.size_bytes),
            reverse=True
        )

        # Deduplicate by destination filename to get diverse top 30 molecules
        seen_filenames: Set[str] = set()
        golden: List[Dict[str, Any]] = []

        for c in sorted_candidates:
            fn = Path(c.rel_path).name
            if fn in seen_filenames:
                continue
            seen_filenames.add(fn)
            golden.append({
                "rank": len(golden) + 1,
                "donor": c.donor,
                "type": c.component_type,
                "rel_path": c.rel_path,
                "destination_rel_path": self._compute_target_rel_path(c),
                "apex_score": c.apex_score,
                "commercial_role": c.commercial_role,
                "size_kb": round(c.size_bytes / 1024, 2),
                "blocks_2_0": c.has_blocks_2_0,
                "custom_elements": c.custom_elements,
                "rendered_snippets": c.rendered_snippets
            })
            if len(golden) >= 60:
                break

        self.golden_index = golden

    def _compute_target_rel_path(self, comp: ComponentMeta) -> str:
        fn = Path(comp.rel_path).name
        # Normalize component file name if needed
        clean_fn = re.sub(r"^(?:sugar-|shrine-|story-|elixir-|casaio-|lumin-)", "dnk-", fn)
        return f"{comp.component_type}s/{clean_fn}"

    def write_graph_and_index(self) -> None:
        """Write APEX_TAXONOMY_GRAPH.json and GOLDEN_MOLECULES_INDEX.json."""
        self.companion_dir.mkdir(parents=True, exist_ok=True)
        graph_file = self.companion_dir / "APEX_TAXONOMY_GRAPH.json"
        index_file = self.companion_dir / "GOLDEN_MOLECULES_INDEX.json"

        graph_file.write_text(json.dumps(self.taxonomy_graph, indent=2, ensure_ascii=False), encoding="utf-8")
        index_file.write_text(json.dumps(self.golden_index, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"✅ APEX Taxonomy Graph written: {graph_file} ({len(self.components)} components)")
        print(f"✅ Golden Molecules Index written: {index_file} ({len(self.golden_index)} ranked molecules)")

    def graft_top_molecules(self, top_n: int = 25) -> Dict[str, Any]:
        """Execute Cleanroom grafting of top N golden molecules into target theme."""
        print(f"\n🚀 Initiating Cleanroom Grafting of Top-{top_n} Golden Molecules into: {self.target_dir}")
        self.target_dir.mkdir(parents=True, exist_ok=True)

        for d in ["assets", "blocks", "config", "layout", "locales", "sections", "snippets", "templates"]:
            (self.target_dir / d).mkdir(parents=True, exist_ok=True)

        # 1. Synthesize foundational tokens & core JS
        self._synthesize_dnk_tokens()
        self._synthesize_dnk_core_js()
        self._synthesize_base_layout()
        self._synthesize_locales()

        grafted_log = []
        molecules_to_graft = self.golden_index[:top_n]

        for mol in molecules_to_graft:
            src = Path(self.components[f"{mol['donor']}::{mol['rel_path']}"].abs_path)
            dest_rel = mol["destination_rel_path"]
            dest = self.target_dir / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)

            if src.suffix in (".liquid", ".css", ".js"):
                raw_code = src.read_text(encoding="utf-8", errors="ignore")
                # Normalize namespaces to dnk-
                norm_code = re.sub(r"\b(?:sugar|shrine|story|elixir)-", "dnk-", raw_code)
                norm_code = re.sub(r"--(?:sugar|shrine|story|elixir)-", "--dnk-", norm_code)
                norm_code = re.sub(r"data-(?:sugar|shrine|story)-animating", "data-dnk-animating", norm_code)

                # Schema normalization
                if src.suffix == ".liquid":
                    norm_code = self._sanitize_liquid_schema(norm_code)

                dest.write_text(norm_code, encoding="utf-8")
            else:
                shutil.copy2(src, dest)

            grafted_log.append({
                "rank": mol["rank"],
                "role": mol["commercial_role"],
                "source": f"{mol['donor']}::{mol['rel_path']}",
                "dest": dest_rel,
                "apex_score": mol["apex_score"]
            })

        print(f"✅ Successfully grafted {len(grafted_log)} golden molecules.")
        return {
            "target_dir": str(self.target_dir),
            "grafted_count": len(grafted_log),
            "molecules": grafted_log
        }

    def _sanitize_liquid_schema(self, code: str) -> str:
        schema_re = re.compile(r"(\{%-?\s*schema\s*-?%\})(.*?)(\{%-?\s*endschema\s*-?%\})", re.S)
        m = schema_re.search(code)
        if not m:
            return code

        raw = m.group(2).strip()
        cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
        try:
            parsed = json.loads(cleaned)
            # Ensure @app block support
            if isinstance(parsed.get("blocks"), list) and len(parsed["blocks"]) > 0:
                has_app = any(b.get("type") == "@app" for b in parsed["blocks"] if isinstance(b, dict))
                if not has_app:
                    parsed["blocks"].append({"type": "@app"})
            re_encoded = json.dumps(parsed, indent=2, ensure_ascii=False)
            return code[:m.start(2)] + "\n" + re_encoded + "\n" + code[m.end(2):]
        except Exception:
            return code

    def _synthesize_dnk_tokens(self) -> None:
        css = """/* --- DNK-MRH-HEADER ---
mrh_id: "assets/dnk-tokens.css"
purpose: "Fluid Typography, Design Tokens and Dynamic Color Schemes for DNK Sovereign Theme"
canonical_source: true
--- END DNK-MRH-HEADER --- */

:root {
  --dnk-color-brand-primary: #0F172A;
  --dnk-color-brand-accent: #2563EB;
  --dnk-color-success: #16A34A;
  --dnk-color-danger: #DC2626;

  --dnk-bg-canvas: #FFFFFF;
  --dnk-bg-surface: #F8FAFC;
  --dnk-border-subtle: rgba(15, 23, 42, 0.08);
  --dnk-text-main: #0F172A;
  --dnk-text-muted: rgba(15, 23, 42, 0.65);

  --dnk-text-xs: clamp(0.75rem, 0.7rem + 0.2vw, 0.8125rem);
  --dnk-text-sm: clamp(0.8125rem, 0.76rem + 0.25vw, 0.875rem);
  --dnk-text-base: clamp(0.9375rem, 0.88rem + 0.3vw, 1rem);
  --dnk-text-lg: clamp(1.125rem, 1.02rem + 0.5vw, 1.25rem);
  --dnk-text-xl: clamp(1.375rem, 1.22rem + 0.75vw, 1.625rem);
  --dnk-text-2xl: clamp(1.75rem, 1.5rem + 1.25vw, 2.25rem);
  --dnk-text-display: clamp(2.25rem, 1.8rem + 2.25vw, 3.5rem);

  --dnk-radius-sm: 4px;
  --dnk-radius-md: 8px;
  --dnk-radius-lg: 12px;
  --dnk-radius-pill: 9999px;

  --dnk-page-width: 1400px;
  --dnk-gutter: clamp(1rem, 0.8rem + 1vw, 2rem);
  --dnk-grid-gap: clamp(1rem, 0.9rem + 0.5vw, 1.5rem);

  --dnk-ease: cubic-bezier(0.16, 1, 0.3, 1);
  --dnk-dur-fast: 150ms;
  --dnk-dur-base: 250ms;
}
"""
        (self.target_dir / "assets" / "dnk-tokens.css").write_text(css, encoding="utf-8")

    def _synthesize_dnk_core_js(self) -> None:
        js = """/**
 * DNK Sovereign Theme Core Engine (Cleanroom Vanilla ES6+)
 * W3C Custom Elements, Zero External Frameworks, 60fps Animation Markers
 */

class DNKCartState {
  static async getCart() {
    const res = await fetch(`${window.Shopify?.routes?.root || '/'}cart.js`);
    return await res.json();
  }

  static async updateQuantity(lineKey, quantity) {
    const res = await fetch(`${window.Shopify?.routes?.root || '/'}cart/change.js`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: lineKey, quantity })
    });
    const cart = await res.json();
    document.dispatchEvent(new CustomEvent('dnk:cart:updated', { detail: { cart } }));
    return cart;
  }
}

class DNKCartDrawer extends HTMLElement {
  connectedCallback() {
    this.closeBtn = this.querySelector('.dnk-cart-drawer__close');
    this.overlay = this.querySelector('.dnk-cart-drawer__overlay');
    this.boundClose = () => this.close();
    if (this.closeBtn) this.closeBtn.addEventListener('click', this.boundClose);
    if (this.overlay) this.overlay.addEventListener('click', this.boundClose);
  }

  disconnectedCallback() {
    if (this.closeBtn) this.closeBtn.removeEventListener('click', this.boundClose);
    if (this.overlay) this.overlay.removeEventListener('click', this.boundClose);
  }

  open() {
    this.setAttribute('data-dnk-animating', '');
    this.setAttribute('open', '');
    document.body.classList.add('dnk-scroll-locked');
    setTimeout(() => this.removeAttribute('data-dnk-animating'), 300);
  }

  close() {
    this.setAttribute('data-dnk-animating', '');
    this.removeAttribute('open');
    document.body.classList.remove('dnk-scroll-locked');
    setTimeout(() => this.removeAttribute('data-dnk-animating'), 300);
  }
}
if (!customElements.get('dnk-cart-drawer')) {
  customElements.define('dnk-cart-drawer', DNKCartDrawer);
}
"""
        core_file = self.target_dir / "assets" / "dnk-core.js"
        core_file.write_text(js, encoding="utf-8")
        subprocess.run(["node", "--check", str(core_file)], check=True)

    def _synthesize_base_layout(self) -> None:
        layout_liquid = """<!doctype html>
<html class="no-js" lang="{{ request.locale.iso_code }}">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link rel="canonical" href="{{ canonical_url }}">
    <link rel="preconnect" href="https://cdn.shopify.com" crossorigin>

    <title>{{ page_title }}</title>
    {% if page_description %}
      <meta name="description" content="{{ page_description | escape }}">
    {% endif %}

    {{ 'dnk-tokens.css' | asset_url | stylesheet_tag }}
    <style>
      :root {
        {% if settings.brand_primary %}--dnk-color-brand-primary: {{ settings.brand_primary }};{% endif %}
        {% if settings.brand_accent %}--dnk-color-brand-accent: {{ settings.brand_accent }};{% endif %}
        {% if settings.page_width %}--dnk-page-width: {{ settings.page_width }}px;{% endif %}
        {% if settings.corner_radius %}
          --dnk-radius-sm: {{ settings.corner_radius | times: 0.5 | round }}px;
          --dnk-radius-md: {{ settings.corner_radius }}px;
          --dnk-radius-lg: {{ settings.corner_radius | times: 1.5 | round }}px;
        {% endif %}
      }
    </style>

    {{ content_for_header }}
    
    <script src="{{ 'dnk-core.js' | asset_url }}" defer></script>
  </head>
  <body class="dnk-theme-sovereign template-{{ request.page_type | handle }}">
    <a class="dnk-skip-to-content" href="#MainContent">
      {{ 'accessibility.skip_to_text' | t }}
    </a>

    {% sections 'header-group' %}

    <main id="MainContent" class="dnk-main-canvas" role="main" tabindex="-1">
      {{ content_for_layout }}
    </main>

    {% sections 'footer-group' %}
  </body>
</html>
"""
        (self.target_dir / "layout" / "theme.liquid").write_text(layout_liquid, encoding="utf-8")

    def _synthesize_locales(self) -> None:
        en_default = {
            "accessibility": {
                "skip_to_text": "Skip to content",
                "close": "Close"
            },
            "general": {
                "cart": {
                    "title": "Your Cart",
                    "empty": "Your cart is empty",
                    "checkout": "Check out"
                }
            }
        }
        uk = {
            "accessibility": {
                "skip_to_text": "Перейти до вмісту",
                "close": "Закрити"
            },
            "general": {
                "cart": {
                    "title": "Ваш кошик",
                    "empty": "Ваш кошик порожній",
                    "checkout": "Оформити замовлення"
                }
            }
        }
        (self.target_dir / "locales" / "en.default.json").write_text(json.dumps(en_default, indent=2, ensure_ascii=False), encoding="utf-8")
        (self.target_dir / "locales" / "uk.json").write_text(json.dumps(uk, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Shopify Theme Companion Distiller")
    parser.add_argument("--mirror-dir", type=Path, default=Path("/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNKEcom/DNK-Ecom_git_mirrow"), help="Path to donor worktrees")
    parser.add_argument("--target-dir", type=Path, default=Path("/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/themes/dnk-sovereign"), help="Target theme output directory")
    parser.add_argument("--companion-dir", type=Path, default=Path(__file__).parent, help="Companion directory")
    parser.add_argument("--scan", action="store_true", help="Scan donor worktrees and update APEX graph and golden index")
    parser.add_argument("--graft-top", type=int, default=0, help="Graft top N golden molecules into target theme")
    parser.add_argument("--validate", action="store_true", help="Validate target theme quotas and syntax")
    args = parser.parse_args()

    distiller = CompanionDistiller(args.mirror_dir, args.target_dir, args.companion_dir)

    print("🔍 Scanning donor worktrees across DNK-Ecom_git_mirrow...")
    distiller.scan_worktrees()
    distiller.write_graph_and_index()

    if args.graft_top > 0:
        distiller.graft_top_molecules(args.graft_top)

    if args.validate:
        print("\n🛡️ Validating Target Theme against Platform Quota Guards...")
        templates = list(args.target_dir.rglob("templates/*.json"))
        oversized = [str(t) for t in templates if t.stat().st_size > 512_000]
        if oversized:
            print(f"❌ FAILED: Oversized templates detected (>512KB): {oversized}")
            return 1
        print("✅ 512KB Template Quota Guard: PASS")

        js_files = list(args.target_dir.rglob("assets/*.js"))
        for jf in js_files:
            try:
                subprocess.run(["node", "--check", str(jf)], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ JS Syntax Error in {jf}: {e.stderr.decode()}")
                return 1
        print("✅ Node.js Syntax Check on Assets: PASS")
        print(f"✅ Target theme validation successful at: {args.target_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
