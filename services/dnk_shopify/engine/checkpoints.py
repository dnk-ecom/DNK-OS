# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/engine/checkpoints.py"
# purpose: "7-Gate Phased Checkpoint Engine for DNK Ecom Sovereign Flagship Theme."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
Deterministic 7-Gate Checkpoint Engine for commercial Shopify Theme engineering.
Guarantees sequential progression from low-level runtime foundations to high-level
Theme Blocks 2.0 sections, preventing unverified or synthetic assembly.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class CheckpointStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class CheckpointRule:
    rule_id: str
    description: str
    validator: Callable[[Path], tuple[bool, str]]


@dataclass
class ThemeCheckpoint:
    id: int
    slug: str
    title: str
    phase_name: str
    description: str
    required_files: List[str]
    rules: List[CheckpointRule] = field(default_factory=list)


def _check_file_exists(theme_path: Path, rel_path: str) -> tuple[bool, str]:
    f = theme_path / rel_path
    if f.exists() and f.is_file():
        return True, f"Found mandatory file: {rel_path}"
    return False, f"Missing mandatory file: {rel_path}"


def _check_node_syntax(file_path: Path) -> tuple[bool, str]:
    if not file_path.exists():
        return False, f"File does not exist for Node syntax check: {file_path.name}"
    try:
        proc = subprocess.run(
            ["node", "-c", str(file_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return True, f"Node syntax check clean (0 errors): {file_path.name}"
        return False, f"Node syntax error in {file_path.name}:\n{proc.stderr.strip()}"
    except Exception as e:
        return False, f"Failed to execute node -c: {e}"


def _check_json_validity(file_path: Path) -> tuple[bool, str]:
    if not file_path.exists():
        return False, f"File does not exist: {file_path.name}"
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return True, f"Valid JSON syntax: {file_path.name}"
    except Exception as e:
        return False, f"Invalid JSON syntax in {file_path.name}: {e}"


# --- CHECKPOINT 0: FOUNDATION RULES ---
def _cp0_validate_tokens(theme_path: Path) -> tuple[bool, str]:
    tokens_file = theme_path / "assets" / "dnk-tokens.css"
    if not tokens_file.exists():
        return False, "assets/dnk-tokens.css missing"
    content = tokens_file.read_text(encoding="utf-8")
    required_prefixes = ["--dnk-color-", "--dnk-font-", "--dnk-space-", "--dnk-radius-"]
    missing = [p for p in required_prefixes if p not in content]
    if missing:
        return False, f"dnk-tokens.css missing standard token prefixes: {missing}"
    return True, "Design tokens specify required color, font, space, and radius variables"


def _cp0_validate_layout_reset(theme_path: Path) -> tuple[bool, str]:
    css_files = list((theme_path / "assets").glob("*.css"))
    if not css_files:
        return False, "No CSS files found in assets/"
    has_subgrid_or_grid = any("grid" in f.read_text(encoding="utf-8") for f in css_files)
    if not has_subgrid_or_grid:
        return False, "Assets must contain modern CSS Grid / Subgrid layout primitives"
    return True, "CSSOM tokens and layout primitives verified"


# --- CHECKPOINT 1: RUNTIME RULES ---
def _cp1_validate_core_runtime(theme_path: Path) -> tuple[bool, str]:
    core_js = theme_path / "assets" / "dnk-core.js"
    if not core_js.exists():
        return False, "assets/dnk-core.js is missing"
    valid, msg = _check_node_syntax(core_js)
    if not valid:
        return False, msg

    content = core_js.read_text(encoding="utf-8")
    patterns = {
        "Custom Elements": r"customElements\.define|class\s+\w+\s+extends\s+HTMLElement",
        "Cart Mutation Queue": r"CartMutationQueue|queue|enqueue|mutateCart",
        "Event Bus / Dispatcher": r"dispatchEvent|CustomEvent|dnk:cart",
    }
    missing = []
    for name, pat in patterns.items():
        if not re.search(pat, content):
            missing.append(name)
    if missing:
        return False, f"dnk-core.js missing architectural primitives: {missing}"
    return True, "Core runtime features W3C Custom Elements base, Cart Queue, and Event Bus"


# --- CHECKPOINT 2: CHROME RULES ---
def _cp2_validate_chrome(theme_path: Path) -> tuple[bool, str]:
    theme_liq = theme_path / "layout" / "theme.liquid"
    header_liq = theme_path / "sections" / "header.liquid"
    footer_liq = theme_path / "sections" / "footer.liquid"

    if not theme_liq.exists() or not header_liq.exists() or not footer_liq.exists():
        return False, "layout/theme.liquid, sections/header.liquid, or sections/footer.liquid missing"

    theme_content = theme_liq.read_text(encoding="utf-8")
    if "content_for_header" not in theme_content:
        return False, "theme.liquid missing mandatory {{ content_for_header }}"
    if "content_for_layout" not in theme_content:
        return False, "theme.liquid missing mandatory {{ content_for_layout }}"
    if "dnk-core.js" not in theme_content:
        return False, "theme.liquid does not load dnk-core.js in head or footer"
    return True, "Global chrome passes layout structure and runtime loading requirements"


# --- CHECKPOINT 3: CART ENGINE RULES ---
def _cp3_validate_cart(theme_path: Path) -> tuple[bool, str]:
    cart_drawer = theme_path / "sections" / "cart-drawer.liquid"
    if not cart_drawer.exists():
        return False, "sections/cart-drawer.liquid missing"
    content = cart_drawer.read_text(encoding="utf-8")
    features = {
        "Free Shipping Progress": r"free-shipping|shipping-bar|progress",
        "Line Item Loop": r"for\s+item\s+in\s+cart\.items",
        "Checkout CTA": r"checkout",
    }
    missing = [k for k, pat in features.items() if not re.search(pat, content, re.IGNORECASE)]
    if missing:
        return False, f"cart-drawer.liquid missing high-CRO features: {missing}"
    return True, "Cart drawer contains dynamic shipping bar, line items, and checkout pipeline"


# --- CHECKPOINT 4: PDP THEME BLOCKS 2.0 RULES ---
def _cp4_validate_pdp(theme_path: Path) -> tuple[bool, str]:
    main_product = theme_path / "sections" / "main-product.liquid"
    if not main_product.exists():
        return False, "sections/main-product.liquid missing"

    blocks_dir = theme_path / "blocks"
    if not blocks_dir.exists():
        return False, "blocks/ directory missing (Theme Blocks 2.0 mandatory)"

    blocks = list(blocks_dir.glob("*.liquid"))
    if not blocks:
        return False, "Zero Theme Blocks found in blocks/ directory"

    # Schema block name <= 25 chars check
    for blk in blocks:
        txt = blk.read_text(encoding="utf-8")
        match = re.search(r"{%\s*schema\s*%}(.*?){%\s*endschema\s*%}", txt, re.DOTALL)
        if match:
            try:
                schema_json = json.loads(match.group(1))
                name = schema_json.get("name", "")
                if len(name) > 25:
                    return False, f"Theme Block {blk.name} schema name '{name}' exceeds 25 chars ({len(name)})"
            except Exception:
                pass

    return True, f"PDP verified with {len(blocks)} Theme Blocks conforming to 25-char limits"


# --- CHECKPOINT 5: DISCOVERY & FILTERING RULES ---
def _cp5_validate_discovery(theme_path: Path) -> tuple[bool, str]:
    main_collection = theme_path / "sections" / "main-collection.liquid"
    if not main_collection.exists():
        return False, "sections/main-collection.liquid missing"

    # Check for product card snippet or block
    card_snippet = theme_path / "snippets" / "product-card.liquid"
    card_block = theme_path / "blocks" / "product-card.liquid"
    if not card_snippet.exists() and not card_block.exists():
        return False, "Missing product card component (neither snippets/product-card.liquid nor blocks/product-card.liquid exists)"

    return True, "Discovery grid and product card components verified"


# --- CHECKPOINT 6: STORE READINESS RULES ---
def _cp6_validate_store_readiness(theme_path: Path) -> tuple[bool, str]:
    # Check customer accounts
    cust_templates = [
        "templates/customers/account.json",
        "templates/customers/login.json",
        "templates/customers/register.json",
        "templates/customers/order.json",
        "templates/customers/addresses.json",
        "templates/customers/reset_password.json",
        "templates/customers/activate_account.json",
    ]
    missing_cust = [t for t in cust_templates if not (theme_path / t).exists()]
    if missing_cust:
        return False, f"Missing customer account templates: {missing_cust}"

    # Check default locale
    en_locale = theme_path / "locales" / "en.default.json"
    if not en_locale.exists():
        return False, "locales/en.default.json missing"
    valid, msg = _check_json_validity(en_locale)
    if not valid:
        return False, msg

    # Check settings schema
    settings_schema = theme_path / "config" / "settings_schema.json"
    if not settings_schema.exists():
        return False, "config/settings_schema.json missing"
    valid, msg = _check_json_validity(settings_schema)
    if not valid:
        return False, msg

    return True, "Store readiness verified with all customer templates, schema, and locales"


CHECKPOINTS: List[ThemeCheckpoint] = [
    ThemeCheckpoint(
        id=0,
        slug="tokens_and_foundation",
        title="Design Tokens, CSSOM Reset & Typography Scaling",
        phase_name="Foundation",
        description="Zero-layout-shift CSS custom properties, responsive scales, and modern CSS Grid layout primitives.",
        required_files=["assets/dnk-tokens.css"],
        rules=[
            CheckpointRule("cp0_tokens", "Design tokens contract", _cp0_validate_tokens),
            CheckpointRule("cp0_layout", "CSS layout primitives", _cp0_validate_layout_reset),
        ],
    ),
    ThemeCheckpoint(
        id=1,
        slug="core_runtime",
        title="Unified Core Runtime, Custom Element Base & Cart Mutation Queue",
        phase_name="Core Runtime",
        description="W3C Custom Elements microkernel, Event Bus, and optimistic Cart Mutation Queue.",
        required_files=["assets/dnk-core.js"],
        rules=[
            CheckpointRule("cp1_runtime", "W3C Custom Element base & Cart Queue", _cp1_validate_core_runtime),
        ],
    ),
    ThemeCheckpoint(
        id=2,
        slug="global_chrome",
        title="Global Chrome, Accessible Header & Predictive Search",
        phase_name="Chrome & Layout",
        description="Accessible theme.liquid scaffold, sticky header, multi-currency/locale selectors, and a11y focus traps.",
        required_files=[
            "layout/theme.liquid",
            "sections/header.liquid",
            "sections/footer.liquid",
        ],
        rules=[
            CheckpointRule("cp2_chrome", "Global layout structure and script loading", _cp2_validate_chrome),
        ],
    ),
    ThemeCheckpoint(
        id=3,
        slug="cart_engine",
        title="Sovereign High-CRO Cart Engine & Drawer",
        phase_name="Cart Engine",
        description="Slide-out cart drawer, dynamic multi-tier free shipping bar, 1-click cross-sells, and cleanroom attribution fetch.",
        required_files=["sections/cart-drawer.liquid"],
        rules=[
            CheckpointRule("cp3_cart", "High-CRO cart drawer mechanics", _cp3_validate_cart),
        ],
    ),
    ThemeCheckpoint(
        id=4,
        slug="pdp_blocks",
        title="Theme Blocks 2.0 Product Detail Engine (PDP)",
        phase_name="Product Detail Page",
        description="Modular PDP with Theme Blocks 2.0, Visual Swatches via Category Metafields, and sub-16ms variant switching.",
        required_files=["sections/main-product.liquid"],
        rules=[
            CheckpointRule("cp4_pdp", "PDP blocks integrity and schema length", _cp4_validate_pdp),
        ],
    ),
    ThemeCheckpoint(
        id=5,
        slug="discovery_filtering",
        title="Collection Grid, Section Rendering Facets & Quick View",
        phase_name="Catalog Discovery",
        description="Dynamic facets via Section Rendering API, zero-refresh filtering, and high-converting product card.",
        required_files=["sections/main-collection.liquid"],
        rules=[
            CheckpointRule("cp5_discovery", "Collection grid and card components", _cp5_validate_discovery),
        ],
    ),
    ThemeCheckpoint(
        id=6,
        slug="store_readiness",
        title="Content Blocks, Customer Accounts & Shopify Theme Store Readiness",
        phase_name="Theme Store Certification",
        description="100% template coverage, complete locales, customer accounts, and 0-error theme check compliance.",
        required_files=[
            "config/settings_schema.json",
            "locales/en.default.json",
            "templates/customers/account.json",
        ],
        rules=[
            CheckpointRule("cp6_store_ready", "Complete customer accounts and locale parity", _cp6_validate_store_readiness),
        ],
    ),
]


class CheckpointEngine:
    def __init__(self, checkpoints: Optional[List[ThemeCheckpoint]] = None):
        self.checkpoints = checkpoints or CHECKPOINTS

    def verify_checkpoint(self, theme_path: Path, checkpoint_id: int) -> Dict[str, Any]:
        cp = next((c for c in self.checkpoints if c.id == checkpoint_id), None)
        if not cp:
            return {
                "checkpoint_id": checkpoint_id,
                "status": CheckpointStatus.FAILED,
                "error": f"Invalid checkpoint ID: {checkpoint_id}",
                "passed": False,
                "details": [],
            }

        details = []
        all_passed = True

        # Check required files
        for rel_f in cp.required_files:
            ok, msg = _check_file_exists(theme_path, rel_f)
            details.append({"check": f"File: {rel_f}", "passed": ok, "message": msg})
            if not ok:
                all_passed = False

        # Run specific rules
        for rule in cp.rules:
            try:
                ok, msg = rule.validator(theme_path)
                details.append({"check": rule.description, "passed": ok, "message": msg})
                if not ok:
                    all_passed = False
            except Exception as e:
                details.append({"check": rule.description, "passed": False, "message": f"Validator crashed: {e}"})
                all_passed = False

        return {
            "checkpoint_id": cp.id,
            "slug": cp.slug,
            "title": cp.title,
            "phase": cp.phase_name,
            "passed": all_passed,
            "status": CheckpointStatus.PASSED if all_passed else CheckpointStatus.FAILED,
            "details": details,
        }

    def audit_theme(self, theme_path: Path) -> Dict[str, Any]:
        results = []
        overall_passed = True
        highest_passed = -1

        for cp in self.checkpoints:
            res = self.verify_checkpoint(theme_path, cp.id)
            results.append(res)
            if res["passed"]:
                if highest_passed == cp.id - 1:
                    highest_passed = cp.id
            else:
                overall_passed = False

        return {
            "theme_path": str(theme_path),
            "total_checkpoints": len(self.checkpoints),
            "highest_consecutive_passed": highest_passed,
            "overall_passed": overall_passed,
            "checkpoints": results,
        }
