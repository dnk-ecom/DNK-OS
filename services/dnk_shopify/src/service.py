# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/src/service.py"
# purpose: "Pure business logic for dnk_shopify Sovereign Brick (Workhorse #1)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from services.dnk_shopify.contracts.schemas import (
    ThemeBlockMeta,
    ThemeCheckViolation,
    ThemeCheckResult,
    CartMutation,
    CartMutationQueueSpec,
    CartCalculationResult,
    CROBlockSpec,
    CROAuditResult,
    LiquidValidationResult,
    ProposalConfigSpec,
    ProposalQuoteResult,
    ClientArtifactRecord,
    ClientStageSpec,
    ClientTicketRequest,
    ClientTicketTriageResult,
)

logger = logging.getLogger("dnk.services.shopify")

BLOCK_TAG_PAIRS = {
    "if": "endif",
    "unless": "endunless",
    "for": "endfor",
    "case": "endcase",
    "tablerow": "endtablerow",
    "form": "endform",
    "paginate": "endpaginate",
    "raw": "endraw",
    "comment": "endcomment",
    "schema": "endschema",
    "javascript": "endjavascript",
    "stylesheet": "endstylesheet",
    "capture": "endcapture",
    "doc": "enddoc",
    "style": "endstyle",
}

INLINE_TAGS = {"else", "elsif", "when", "break", "continue", "cycle", "include", "render", "section", "sections", "content_for"}

CANONICAL_CRO_REQUIREMENTS = [
    CROBlockSpec(
        block_id="cro_buy_buttons",
        title="Direct Conversion Buy Buttons",
        category="conversion",
        canonical_filename="_product-main-buy-buttons.liquid",
    ),
    CROBlockSpec(
        block_id="cro_cart_drawer",
        title="High-Converting AJAX Cart Drawer",
        category="conversion",
        canonical_filename="cart-drawer.liquid",
    ),
    CROBlockSpec(
        block_id="cro_quantity_breaks",
        title="Dual-Level Quantity Breaks v2",
        category="average_order_value",
        canonical_filename="product_quantity-breaks-v2.liquid",
    ),
    CROBlockSpec(
        block_id="cro_free_shipping",
        title="Dynamic Free Shipping Rewards Bar",
        category="average_order_value",
        canonical_filename="cart-progress-bar.liquid",
    ),
    CROBlockSpec(
        block_id="cro_trust_badges",
        title="Trust & Security Badges",
        category="trust",
        canonical_filename="_product-main-trust-badges.liquid",
    ),
    CROBlockSpec(
        block_id="cro_product_rating",
        title="Customer Rating & Social Proof",
        category="social_proof",
        canonical_filename="_product-main-rating.liquid",
    ),
]


class DNKShopifyService:
    """Pure in-process service engine for Shopify OS 2.0 / Theme Blocks 2.0 operations."""

    def __init__(self, default_theme_path: Optional[Path] = None):
        if default_theme_path:
            self.default_theme_path = Path(default_theme_path)
        else:
            # 1. Local self-contained working copy of DNK Sovereign 1.0.0 Apex
            local_apex = Path(__file__).resolve().parent.parent / "DNK_Sovereign_Apex"
            # 2. Canonical Git Bare Mirror worktree
            git_mirrow_main = (
                Path(__file__).resolve().parent.parent.parent.parent.parent
                / "DNKEcom"
                / "DNK-Ecom_git_mirrow"
                / "main"
            )
            # Prioritize the canonical Git Bare Mirror worktree over local snapshot
            if git_mirrow_main.exists():
                self.default_theme_path = git_mirrow_main
            elif local_apex.exists():
                self.default_theme_path = local_apex
            else:
                self.default_theme_path = git_mirrow_main

    def validate_liquid(self, code: str) -> LiquidValidationResult:
        """
        Syntactic audit of Liquid template code ensuring balanced tags,
        valid {% schema %} JSON, and balanced variable interpolations.
        """
        errors: List[str] = []
        stack: List[tuple[str, int]] = []  # (tag_name, line_number)

        # Count variables {{ ... }}
        var_matches = list(re.finditer(r"\{\{(.*?)\}\}", code, re.DOTALL))
        variables_count = len(var_matches)

        # Check for unclosed {{
        open_vars = len(re.findall(r"\{\{(?!\})", code))
        close_vars = len(re.findall(r"(?<!\{)\}\}", code))
        if open_vars != close_vars:
            errors.append(f"Unbalanced variable braces: {open_vars} opened, {close_vars} closed.")

        # Match tags {% ... %}
        tag_pattern = re.compile(r"\{%-?\s*([a-zA-Z0-9_]+)(.*?)-?%\}", re.DOTALL)
        tags = list(tag_pattern.finditer(code))
        tags_count = len(tags)

        # Check {% schema %} JSON block specifically
        schema_match = re.search(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", code, re.DOTALL)
        if schema_match:
            schema_json_raw = schema_match.group(1).strip()
            if schema_json_raw:
                try:
                    json.loads(schema_json_raw)
                except json.JSONDecodeError as jde:
                    errors.append(f"Invalid JSON inside {{% schema %}}: {jde.msg} (line {jde.lineno})")

        # Track block tags
        for match in tags:
            tag_name = match.group(1).lower()
            start_pos = match.start()
            line_no = code.count("\n", 0, start_pos) + 1

            if tag_name in BLOCK_TAG_PAIRS:
                stack.append((tag_name, line_no))
            elif tag_name.startswith("end"):
                expected_open = tag_name[3:]
                if not stack:
                    errors.append(f"Unexpected closing tag '{tag_name}' at line {line_no} with no matching open tag.")
                else:
                    last_open, last_line = stack.pop()
                    expected_end = BLOCK_TAG_PAIRS.get(last_open)
                    if expected_end != tag_name:
                        errors.append(
                            f"Mismatched tag at line {line_no}: expected '{expected_end}' for '{last_open}' opened at line {last_line}, got '{tag_name}'."
                        )

        # Report any unclosed tags
        while stack:
            unclosed_tag, line_no = stack.pop()
            expected_end = BLOCK_TAG_PAIRS.get(unclosed_tag)
            errors.append(f"Unclosed tag '{unclosed_tag}' opened at line {line_no} (missing '{expected_end}').")

        return LiquidValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            tags_count=tags_count,
            variables_count=variables_count,
        )

    def list_theme_blocks(self, theme_path: Optional[Path] = None) -> List[ThemeBlockMeta]:
        """Scans the theme's blocks/ directory and parses Theme Block 2.0 metadata."""
        target_dir = theme_path or self.default_theme_path
        blocks_dir = target_dir / "blocks"
        if not blocks_dir.exists() or not blocks_dir.is_dir():
            return []

        results: List[ThemeBlockMeta] = []
        for file in sorted(blocks_dir.glob("*.liquid")):
            rel_path = str(file.relative_to(target_dir))
            is_private = file.name.startswith("_")
            content = file.read_text(encoding="utf-8", errors="replace")

            has_schema = False
            schema_name = None
            presets: List[str] = []

            schema_match = re.search(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", content, re.DOTALL)
            if schema_match:
                has_schema = True
                try:
                    s_data = json.loads(schema_match.group(1).strip())
                    schema_name = s_data.get("name")
                    raw_presets = s_data.get("presets", [])
                    presets = [p.get("name", "Default") for p in raw_presets if isinstance(p, dict)]
                except Exception:
                    pass

            results.append(
                ThemeBlockMeta(
                    block_name=file.name,
                    is_private=is_private,
                    file_path=rel_path,
                    has_schema=has_schema,
                    schema_name=schema_name,
                    target_presets=presets,
                )
            )

        return results

    def check_theme(self, theme_path: Optional[Path] = None) -> ThemeCheckResult:
        """Runs in-process static validation of theme directory structure and mandatory assets."""
        target_dir = theme_path or self.default_theme_path
        if not target_dir.exists() or not target_dir.is_dir():
            return ThemeCheckResult(
                theme_path=str(target_dir),
                total_files=0,
                errors_count=1,
                warnings_count=0,
                violations=[
                    ThemeCheckViolation(
                        file_path=str(target_dir),
                        line=0,
                        severity="error",
                        rule_id="ThemeDirectoryMissing",
                        message=f"Theme directory '{target_dir}' does not exist.",
                    )
                ],
                is_compliant=False,
            )

        violations: List[ThemeCheckViolation] = []
        mandatory_dirs = ["layout", "templates", "sections", "snippets", "config", "locales", "blocks"]

        for d in mandatory_dirs:
            if not (target_dir / d).is_dir():
                violations.append(
                    ThemeCheckViolation(
                        file_path=d,
                        line=0,
                        severity="error",
                        rule_id="RequiredDirectoryMissing",
                        message=f"Mandatory theme folder '{d}/' is missing.",
                    )
                )

        theme_liquid = target_dir / "layout" / "theme.liquid"
        if not theme_liquid.exists():
            violations.append(
                ThemeCheckViolation(
                    file_path="layout/theme.liquid",
                    line=0,
                    severity="error",
                    rule_id="ThemeLiquidMissing",
                    message="Critical root layout 'layout/theme.liquid' is missing.",
                )
            )

        settings_schema = target_dir / "config" / "settings_schema.json"
        if settings_schema.exists():
            try:
                json.loads(settings_schema.read_text(encoding="utf-8", errors="replace"))
            except Exception as e:
                violations.append(
                    ThemeCheckViolation(
                        file_path="config/settings_schema.json",
                        line=0,
                        severity="error",
                        rule_id="InvalidSettingsSchemaJson",
                        message=f"Malformed settings_schema.json: {e}",
                    )
                )

        # Count evaluated files
        all_files = list(target_dir.rglob("*.liquid")) + list(target_dir.rglob("*.json"))
        total_files = len(all_files)

        errors_count = sum(1 for v in violations if v.severity == "error")
        warnings_count = sum(1 for v in violations if v.severity == "warning")

        return ThemeCheckResult(
            theme_path=str(target_dir),
            total_files=total_files,
            errors_count=errors_count,
            warnings_count=warnings_count,
            violations=violations,
            is_compliant=(errors_count == 0),
        )

    def calculate_cart(self, spec: CartMutationQueueSpec) -> CartCalculationResult:
        """
        Pure deterministic computation of cart mutations, updating subtotal,
        remaining free shipping threshold, and progress percentage.
        """
        subtotal = spec.current_subtotal
        item_count = 0

        # Simulate mutation processing
        for m in spec.mutations:
            if m.action == "add":
                item_count += m.quantity
                # Assume default nominal delta if properties contain price
                nominal_price = float(m.properties.get("price", 25.0))
                subtotal += nominal_price * m.quantity
            elif m.action == "remove":
                item_count = max(0, item_count - m.quantity)
                nominal_price = float(m.properties.get("price", 25.0))
                subtotal = max(0.0, subtotal - (nominal_price * m.quantity))
            elif m.action == "clear":
                subtotal = 0.0
                item_count = 0

        subtotal = round(subtotal, 2)
        remaining = max(0.0, round(spec.free_shipping_threshold - subtotal, 2))
        progress = 100.0 if spec.free_shipping_threshold <= 0 else min(100.0, round((subtotal / spec.free_shipping_threshold) * 100.0, 1))
        qualified = subtotal >= spec.free_shipping_threshold

        return CartCalculationResult(
            new_subtotal=subtotal,
            remaining_for_free_shipping=remaining,
            progress_percentage=progress,
            free_shipping_qualified=qualified,
            item_count=item_count,
        )

    def audit_cro(self, theme_path: Optional[Path] = None) -> CROAuditResult:
        """Audits theme against canonical CRO conversion mechanisms."""
        target_dir = theme_path or self.default_theme_path
        blocks_dir = target_dir / "blocks"
        sections_dir = target_dir / "sections"
        snippets_dir = target_dir / "snippets"

        available_files = set()
        if blocks_dir.exists():
            available_files.update(f.name for f in blocks_dir.glob("*.liquid"))
        if sections_dir.exists():
            available_files.update(f.name for f in sections_dir.glob("*.liquid"))
        if snippets_dir.exists():
            available_files.update(f.name for f in snippets_dir.glob("*.liquid"))

        detected: List[str] = []
        missing: List[str] = []
        recommendations: List[str] = []

        for req in CANONICAL_CRO_REQUIREMENTS:
            name = req.canonical_filename
            # Match direct filename, private version, or stripped version
            if (
                name in available_files
                or f"_{name}" in available_files
                or name.lstrip("_") in available_files
            ):
                detected.append(req.title)
            else:
                missing.append(req.title)
                recommendations.append(
                    f"Integrate {req.title} ({req.canonical_filename}) to lift conversion in category: {req.category}."
                )

        score = int((len(detected) / max(1, len(CANONICAL_CRO_REQUIREMENTS))) * 100)

        return CROAuditResult(
            theme_path=str(target_dir),
            score=score,
            detected_blocks=detected,
            missing_blocks=missing,
            recommendations=recommendations,
        )

    def run_7gate_integrity(self, theme_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Executes the mandatory 7-Gate Anti-Regression Theme Integrity Gate
        (tools/verify_theme_integrity.py) of DNK Sovereign 1.0.0 Apex.
        """
        target_dir = theme_path or self.default_theme_path
        script_path = target_dir / "tools" / "verify_theme_integrity.py"

        if not script_path.exists():
            script_path = (
                Path(__file__).resolve().parent.parent
                / "DNK_Sovereign_Apex"
                / "tools"
                / "verify_theme_integrity.py"
            )

        if not script_path.exists():
            return {
                "success": False,
                "error": f"Integrity script not found at: {script_path}",
                "exit_code": 1,
            }

        import subprocess
        import sys
        proc = subprocess.run(
            [sys.executable, str(script_path), str(target_dir)],
            capture_output=True,
            text=True,
            check=False,
        )

        return {
            "success": proc.returncode == 0,
            "theme_path": str(target_dir),
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "all_gates_passed": proc.returncode == 0 and "100% CLEAN & PROTECTED" in proc.stdout,
        }

    def generate_proposal_quote(self, spec: ProposalConfigSpec) -> ProposalQuoteResult:
        """
        Generates a deterministic personalized proposal quote, App-Tax savings ROI calculation,
        niche-specific CRO molecule matrix, and 64-char SHA-256 contract scope seal.
        """
        base_price = 1200 if spec.package_tier == "launch_1200" else 1500
        included_products = 15 if spec.package_tier == "launch_1200" else 20
        included_languages = 1 if spec.package_tier == "launch_1200" else 2
        included_revisions = 2 if spec.package_tier == "launch_1200" else 3

        addons_total = (
            (spec.extra_products_batches * 50)
            + (300 if spec.include_gmc_setup else 0)
            + (200 if spec.include_seo_semantics else 0)
        )
        total_investment = base_price + addons_total
        prepayment_30 = round(total_investment * 0.30, 2)
        completion_70 = round(total_investment - prepayment_30, 2)

        # Native DNK Sovereign Apex blocks replace paid third-party Shopify subscriptions:
        # Launch ($1200): Cart Drawer Upsell ($39/mo) + Sticky ATC & Trust ($19/mo)
        #   + Free Shipping Bar ($15/mo) + Reviews Layout ($29/mo) + Delivery Estimator ($24/mo) = $126/mo ($1512/yr)
        # Scale ($1500): adds Quantity Breaks v2 Bundles ($39/mo) + Multi-Currency/Geo ($29/mo)
        #   + Email Abandonment Flows ($45/mo) = $239/mo ($2868/yr)
        monthly_app_savings = 126 if spec.package_tier == "launch_1200" else 239
        annual_app_savings = monthly_app_savings * 12

        # Estimated monthly revenue lift from CRO blocks (conservative 12% AOV + conversion delta)
        monthly_cro_lift = spec.monthly_orders_estimate * spec.average_order_value_usd * 0.08
        monthly_total_benefit = max(float(monthly_app_savings), monthly_app_savings + monthly_cro_lift)
        payback_months = round(total_investment / monthly_total_benefit, 1)

        base_molecules = [
            "_product-main-buy-buttons.liquid",
            "cart-drawer.liquid",
            "cart-progress-bar.liquid",
            "_product-main-trust-badges.liquid",
            "_product-main-rating.liquid",
            "tinker-dnk-delivery-estimator.liquid",
        ]
        if spec.package_tier == "scale_1500":
            base_molecules.extend(
                [
                    "product_quantity-breaks-v2.liquid",
                    "cart-drawer_body.liquid",
                    "product-recommendations.liquid",
                ]
            )

        niche_matrices: Dict[str, List[Dict[str, str]]] = {
            "fashion_apparel": [
                {
                    "insight": "Страх не вгадати з розміром та складність повернення",
                    "dnk_molecule": "Size Guide Drawer + Trust Guarantee Badges (_product-main-trust-badges.liquid)",
                    "expected_kpi_lift": "-22% відмов на PDP, +14% Add-to-Cart",
                },
                {
                    "insight": "Низький середній чек при покупці базової речі",
                    "dnk_molecule": "Dual-Level Quantity Breaks v2 (product_quantity-breaks-v2.liquid: 1x / 2+1 / 3+2)",
                    "expected_kpi_lift": "+28% AOV без платних бандл-аппок",
                },
            ],
            "beauty_cosmetics": [
                {
                    "insight": "Сумніви у складі та реальному ефекті засобу до/після",
                    "dnk_molecule": "Before/After Slider + Verified Video Reviews (_product-main-rating.liquid)",
                    "expected_kpi_lift": "+19% конверсії з холодного трафіку Meta Ads",
                },
                {
                    "insight": "Висока вартість залучення клієнта (CAC) при покупці 1 флакона",
                    "dnk_molecule": "Routine Bundle Builder + Free Gift Tier in Cart Drawer (cart-progress-bar.liquid)",
                    "expected_kpi_lift": "+34% AOV та повторні замовлення",
                },
            ],
            "home_decor_lighting": [
                {
                    "insight": "Побоювання пошкодження при доставці та невідомі терміни",
                    "dnk_molecule": "Dynamic Geo Delivery Estimator (tinker-dnk-delivery-estimator.liquid)",
                    "expected_kpi_lift": "+16% завершених чекаутів",
                },
                {
                    "insight": "Покупка комплекту світильників/декору в кілька кімнат",
                    "dnk_molecule": "Tiered Room Multipack (product_quantity-breaks-v2.liquid)",
                    "expected_kpi_lift": "+31% середнього чеку",
                },
            ],
            "electronics_accessories": [
                {
                    "insight": "Питання сумісності пристроїв та гарантійної заміни",
                    "dnk_molecule": "Spec Comparison Matrix + Instant Warranty Seal (_product-main-trust-badges.liquid)",
                    "expected_kpi_lift": "+18% конверсії карток товару",
                },
                {
                    "insight": "Втрата супутніх аксесуарів (кабелі, чохли, захист)",
                    "dnk_molecule": "1-Click In-Cart Upsell Queue (cart-drawer.liquid + CartMutationQueue)",
                    "expected_kpi_lift": "+24% доходу з кожного кошика",
                },
            ],
            "kids_educational": [
                {
                    "insight": "Безпека матеріалів (еко-сертифікація) та відповідність віку дитини",
                    "dnk_molecule": "Age-Filter Badges + Eco Certification Block (_product-main-trust-badges.liquid)",
                    "expected_kpi_lift": "+21% довіри батьків на першому екрані",
                },
                {
                    "insight": "Покупка на подарунок із фіксованою датою доставки",
                    "dnk_molecule": "Gift Wrap Toggle + Exact Delivery Date Estimator (tinker-dnk-delivery-estimator.liquid)",
                    "expected_kpi_lift": "+25% AOV у подарунковий сезон",
                },
            ],
            "custom_dtc": [
                {
                    "insight": "Повільне завантаження шаблонів та конфлікти сторонніх аппок у кошику",
                    "dnk_molecule": "DNK Sovereign Apex Core + CartMutationQueue (AsyncMutex FIFO)",
                    "expected_kpi_lift": "95+ Mobile PageSpeed, 0% втрачених транзакцій",
                },
                {
                    "insight": "Низька окупність платного трафіку на стандартній картці товару",
                    "dnk_molecule": "Full CRO Buy-Box Stack (product_quantity-breaks-v2.liquid + cart-progress-bar.liquid)",
                    "expected_kpi_lift": "+25% AOV та економія до $2,868/рік на підписках",
                },
            ],
        }

        slug = re.sub(r"[^a-z0-9]+", "-", spec.brand_name.lower()).strip("-") or "client"
        deal_id = f"deal-{slug}-{spec.package_tier}"

        canonical_payload = json.dumps(
            {
                "deal_id": deal_id,
                "client_name": spec.client_name,
                "brand_name": spec.brand_name,
                "niche": spec.niche,
                "package_tier": spec.package_tier,
                "total_investment_usd": total_investment,
                "included_products": included_products + (spec.extra_products_batches * 10),
                "included_languages": included_languages,
                "included_revisions": included_revisions,
                "include_gmc_setup": spec.include_gmc_setup,
                "include_seo_semantics": spec.include_seo_semantics,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        scope_sha256 = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

        return ProposalQuoteResult(
            deal_id=deal_id,
            client_name=spec.client_name,
            brand_name=spec.brand_name,
            niche=spec.niche,
            package_tier=spec.package_tier,
            base_price_usd=base_price,
            addons_total_usd=addons_total,
            total_investment_usd=total_investment,
            prepayment_30_usd=prepayment_30,
            completion_70_usd=completion_70,
            delivery_business_days=14,
            included_products_count=included_products + (spec.extra_products_batches * 10),
            included_languages_count=included_languages,
            included_revision_rounds=included_revisions,
            annual_app_savings_usd=annual_app_savings,
            estimated_payback_months=payback_months,
            recommended_molecules=base_molecules,
            niche_pain_to_molecule_matrix=niche_matrices.get(spec.niche, niche_matrices["custom_dtc"]),
            scope_sha256=scope_sha256,
        )

    def initialize_client_deal_cockpit(
        self, quote: ProposalQuoteResult, client_assets_ready: bool = True
    ) -> List[ClientStageSpec]:
        """
        Initializes the 6-Stage Client Execution Dashboard (DEC-010) bound to
        docs/canvas/shopify_vibe_pipeline.canvas with verifiable SHA-256 artifact slots.
        Automatically pauses Stage 1 SLA if client_assets_ready is False.
        """
        def _hash_artifact(stage_num: int, rel_path: str) -> str:
            raw = f"{quote.deal_id}:{quote.scope_sha256}:stage{stage_num}:{rel_path}"
            return hashlib.sha256(raw.encode("utf-8")).hexdigest()

        stage1_status = "completed" if client_assets_ready else "waiting_client_assets"
        stage2_status = "in_progress" if client_assets_ready else "pending"

        stages = [
            ClientStageSpec(
                stage_number=1,
                stage_id="stage_01_onboarding_competitors",
                title_uk="Етап 1. Онбординг, ДНК бренду та аналіз 7 конкурентів",
                canvas_node_id="node_competitors",
                assigned_agent="strategist_prime",
                status=stage1_status,
                sla_days="Дні 1-2",
                deliverables=[
                    "Матриця 7 DTC-конкурентів ніші (оффери, AOV, бандли)",
                    "Зафіксований бриф та доступи до Shopify Collaborator",
                ],
                artifacts=[
                    ClientArtifactRecord(
                        artifact_id="art_competitor_matrix",
                        stage_number=1,
                        canvas_node_id="node_competitors",
                        title="Матриця конкурентів та оферів (JSON/MD)",
                        relative_path="./artifacts/shopify/competitor_matrix.json",
                        sha256_receipt=_hash_artifact(1, "./artifacts/shopify/competitor_matrix.json"),
                        status="ready_for_review" if client_assets_ready else "locked",
                    )
                ],
            ),
            ClientStageSpec(
                stage_number=2,
                stage_id="stage_02_cro_funnel_architecture",
                title_uk="Етап 2. CRO-архітектура воронки та прототип головних сторінок",
                canvas_node_id="node_cro_audit",
                assigned_agent="dnk_shopify",
                status=stage2_status,
                sla_days="Дні 3-4",
                deliverables=[
                    "Специфікація конверсійної воронки (PDP, Cart Drawer, Upsell Tiers)",
                    "2 варіанти структури Theme Blocks 2.0 на погодження",
                ],
                artifacts=[
                    ClientArtifactRecord(
                        artifact_id="art_cro_funnel_spec",
                        stage_number=2,
                        canvas_node_id="node_cro_audit",
                        title="Специфікація CRO-воронки та Buy-Box",
                        relative_path="./artifacts/shopify/cro_funnel_spec.md",
                        sha256_receipt=_hash_artifact(2, "./artifacts/shopify/cro_funnel_spec.md"),
                        status="in_progress" if client_assets_ready else "locked",
                    )
                ],
            ),
            ClientStageSpec(
                stage_number=3,
                stage_id="stage_03_brand_dna_tokens",
                title_uk="Етап 3. Дизайн-система, фірмові кольори та типографіка",
                canvas_node_id="node_brand_dna",
                assigned_agent="denchik",
                status="pending",
                sla_days="Дні 5-6",
                deliverables=[
                    "Ін'єкція палітри, шрифтів та дизайн-токенів (--dnk-*)",
                    "Адаптивна мобільна сітка (Mobile-First UX)",
                ],
                artifacts=[
                    ClientArtifactRecord(
                        artifact_id="art_brand_tokens",
                        stage_number=3,
                        canvas_node_id="node_brand_dna",
                        title="Паспорт дизайн-токенів теми",
                        relative_path="./artifacts/shopify/brand_tokens.json",
                        sha256_receipt=_hash_artifact(3, "./artifacts/shopify/brand_tokens.json"),
                        status="locked",
                    )
                ],
            ),
            ClientStageSpec(
                stage_number=4,
                stage_id="stage_04_molecular_liquid_assembly",
                title_uk="Етап 4. Збірка блоків DNK Sovereign Apex та каталогу товарів",
                canvas_node_id="node_liquid_blocks",
                assigned_agent="dnk_shopify",
                status="pending",
                sla_days="Дні 7-10",
                deliverables=[
                    f"Імпорт та оформлення до {quote.included_products_count} товарів і колекцій",
                    f"Монтаж {len(quote.recommended_molecules)} CRO-молекул (Quantity Breaks, Cart Drawer, Trust)",
                ],
                artifacts=[
                    ClientArtifactRecord(
                        artifact_id="art_theme_integrity_7gate",
                        stage_number=4,
                        canvas_node_id="node_liquid_blocks",
                        title="Сертифікат 7-Gate Theme Integrity (0 помилок)",
                        relative_path="./artifacts/shopify/theme_7gate_receipt.json",
                        sha256_receipt=_hash_artifact(4, "./artifacts/shopify/theme_7gate_receipt.json"),
                        status="locked",
                    )
                ],
            ),
            ClientStageSpec(
                stage_number=5,
                stage_id="stage_05_copywriting_payments_policies",
                title_uk="Етап 5. Продаючий PDP-копірайтинг, платіжки та юридичні політики",
                canvas_node_id="node_pdp_copywriting",
                assigned_agent="strategist_prime",
                status="pending",
                sla_days="Дні 11-12",
                deliverables=[
                    f"Локалізація ({quote.included_languages_count} мови) та вичитка текстів без AI-slop",
                    "Налаштування Shopify Payments / Stripe / PayPal та політик (Refund, Privacy, Shipping, ToS)",
                ],
                artifacts=[
                    ClientArtifactRecord(
                        artifact_id="art_pdp_copy_pack",
                        stage_number=5,
                        canvas_node_id="node_pdp_copywriting",
                        title="Пакет текстів PDP та юридичних сторінок",
                        relative_path="./artifacts/shopify/pdp_copy_verified.md",
                        sha256_receipt=_hash_artifact(5, "./artifacts/shopify/pdp_copy_verified.md"),
                        status="locked",
                    )
                ],
            ),
            ClientStageSpec(
                stage_number=6,
                stage_id="stage_06_qa_handover_launch",
                title_uk="Етап 6. Фінальний QA-аудит, відеоінструкції та запуск у продакшн",
                canvas_node_id="node_liquid_blocks",
                assigned_agent="gerych_prime",
                status="pending",
                sla_days="Дні 13-14",
                deliverables=[
                    "Передача доступів власника, відеоуроки керування замовленнями та Customizer",
                    "1 місяць гарантійної технічної підтримки після релізу",
                ],
                artifacts=[
                    ClientArtifactRecord(
                        artifact_id="art_handover_playbook",
                        stage_number=6,
                        canvas_node_id="node_liquid_blocks",
                        title="Відеоінструкції та чекліст запуску магазину",
                        relative_path="./artifacts/shopify/store_handover_bundle.json",
                        sha256_receipt=_hash_artifact(6, "./artifacts/shopify/store_handover_bundle.json"),
                        status="locked",
                    )
                ],
            ),
        ]
        return stages

    def triage_client_ticket(
        self,
        req: ClientTicketRequest,
        persist_to_canvas_session: bool = False,
        canvas_path: Optional[Path] = None,
    ) -> ClientTicketTriageResult:
        """
        Deterministic Scope Guard and Spatial Canvas Router for client questions and revisions.
        Protects against infinite revision loops and routes validated tasks directly into
        SpatialCanvasSessionRouter (session_id = node:shopify_vibe_pipeline:{target_node_id}).
        """
        text_lower = req.request_text.lower().strip()

        out_of_scope_keywords = [
            "1c",
            "1с",
            "erp",
            "кастомний додаток",
            "custom app",
            "мобільний додаток",
            "ios app",
            "3d",
            "ar ",
            "magento",
            "woocommerce міграція",
            "crm інтеграція",
            "ai чат-бот",
            "більше 50 товарів",
        ]
        question_markers = [
            "?",
            "як ",
            "коли ",
            "підкажіть",
            "чи можна",
            "де знайти",
            "скільки часу",
            "how ",
            "when ",
            "what ",
        ]

        is_out_of_scope_kw = any(kw in text_lower for kw in out_of_scope_keywords)
        quota_exhausted = req.used_revisions_count >= req.max_free_revisions
        is_question = any(m in text_lower for m in question_markers) and not is_out_of_scope_kw

        # Route to appropriate Spatial Canvas node and sovereign agent
        if req.preferred_node_id in {
            "node_competitors",
            "node_cro_audit",
            "node_brand_dna",
            "node_liquid_blocks",
            "node_pdp_copywriting",
        }:
            target_node = req.preferred_node_id
        elif any(k in text_lower for k in ["колір", "шрифт", "лого", "стиль", "відступ", "банер", "color", "font"]):
            target_node = "node_brand_dna"
        elif any(k in text_lower for k in ["текст", "опис", "заголовок", "переклад", "політик", "faq", "copy"]):
            target_node = "node_pdp_copywriting"
        elif any(k in text_lower for k in ["конкурент", "ніш", "позиціонуван", " цін", "ринок"]):
            target_node = "node_competitors"
        elif any(k in text_lower for k in ["воронк", "конверс", "бейдж", "довір", "гарант", "cro"]):
            target_node = "node_cro_audit"
        else:
            target_node = "node_liquid_blocks"

        node_agent_map = {
            "node_competitors": "strategist_prime",
            "node_cro_audit": "dnk_shopify",
            "node_brand_dna": "denchik",
            "node_liquid_blocks": "dnk_shopify",
            "node_pdp_copywriting": "strategist_prime",
        }
        assigned_agent = node_agent_map.get(target_node, "dnk_shopify")
        session_id = f"node:shopify_vibe_pipeline:{target_node}"

        if is_out_of_scope_kw or (quota_exhausted and not is_question):
            classification = "out_of_scope_upsell"
            gate_state = "upsell_quote_required"
            remaining = max(0, req.max_free_revisions - req.used_revisions_count)
            upsell_usd = 250 if is_out_of_scope_kw else 75
            reason = (
                "Запит виходить за межі базового договору (нова зовнішня інтеграція/модуль)"
                if is_out_of_scope_kw
                else f"Вичерпано ліміт безкоштовних ітерацій ({req.max_free_revisions}/{req.max_free_revisions})"
            )
            summary_uk = (
                f"Scope Guard: {reason}. Сформовано додатковий тікет на погодження (+${upsell_usd}) "
                f"перед запуском агента {assigned_agent} у вузлі {target_node}."
            )
        elif is_question:
            classification = "question"
            gate_state = "auto_answered"
            remaining = max(0, req.max_free_revisions - req.used_revisions_count)
            upsell_usd = 0
            summary_uk = (
                f"Консультаційний запит скеровано до {assigned_agent} ({session_id}). "
                f"Квота безкоштовних правок не списується (доступно: {remaining})."
            )
        else:
            classification = "in_scope_revision"
            gate_state = "awaiting_founder_triage"
            remaining = max(0, req.max_free_revisions - (req.used_revisions_count + 1))
            upsell_usd = 0
            summary_uk = (
                f"Правка в межах договору прийнята у чергу вузла {target_node} (агент: {assigned_agent}). "
                f"Статус: очікує 1-клік підтвердження фаундера. Залишок правок у пакеті: {remaining}."
            )

        canonical_ticket = json.dumps(
            {
                "deal_id": req.deal_id,
                "client_name": req.client_name,
                "request_text": req.request_text,
                "classification": classification,
                "target_canvas_node_id": target_node,
                "assigned_agent": assigned_agent,
                "gate_state": gate_state,
                "remaining_free_revisions": remaining,
                "upsell_estimate_usd": upsell_usd,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        audit_hash = hashlib.sha256(canonical_ticket.encode("utf-8")).hexdigest()
        ticket_id = f"TKT-{audit_hash[:8].upper()}"

        if persist_to_canvas_session:
            from core.canvas.session_router import SpatialCanvasSessionRouter

            router = SpatialCanvasSessionRouter()
            router.get_or_create_session(
                canvas_id="shopify_vibe_pipeline",
                node_id=target_node,
                agent_role=assigned_agent,
            )
            router.post_message(
                session_id=session_id,
                role="user",
                content=f"[{ticket_id} | {classification.upper()} | {req.client_name}]: {req.request_text}",
                meta={
                    "ticket_id": ticket_id,
                    "deal_id": req.deal_id,
                    "classification": classification,
                    "gate_state": gate_state,
                    "audit_hash": audit_hash,
                },
            )

        return ClientTicketTriageResult(
            ticket_id=ticket_id,
            deal_id=req.deal_id,
            classification=classification,
            target_canvas_node_id=target_node,
            assigned_agent=assigned_agent,
            session_id=session_id,
            gate_state=gate_state,
            remaining_free_revisions=remaining,
            upsell_estimate_usd=upsell_usd,
            action_summary_uk=summary_uk,
            audit_hash=audit_hash,
        )

