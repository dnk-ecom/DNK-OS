#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/cli.py"
# purpose: "Headless CLI for dnk_shopify Sovereign Brick (smol-workers & Gerych-root)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import argparse
import json
import sys
from pathlib import Path

# Ensure repository root is in sys.path
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from services.dnk_shopify.src.service import DNKShopifyService
from services.dnk_shopify.runtime.local_storefront import LocalStorefrontManager
from services.dnk_shopify.contracts.schemas import (
    CartMutation,
    CartMutationQueueSpec,
    ProposalConfigSpec,
    ClientTicketRequest,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DNK Shopify 3.0 Headless Sovereign Brick CLI (DNK Sovereign 1.0.0 Apex & Theme Blocks 2.0)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. validate
    val_p = subparsers.add_parser("validate", help="Validate Liquid template syntax")
    val_p.add_argument("target", help="File path or inline liquid string")
    val_p.add_argument("--json", action="store_true", help="Output JSON")

    # 2. list-blocks
    blocks_p = subparsers.add_parser("list-blocks", help="List Theme Blocks 2.0 components")
    blocks_p.add_argument("--theme", default=None, help="Path to theme root")
    blocks_p.add_argument("--json", action="store_true", help="Output JSON")

    # 3. check
    check_p = subparsers.add_parser("check", help="Run static theme integrity check")
    check_p.add_argument("--theme", default=None, help="Path to theme root")
    check_p.add_argument("--json", action="store_true", help="Output JSON")

    # 4. cro-audit
    cro_p = subparsers.add_parser("cro-audit", help="Audit theme conversion mechanisms")
    cro_p.add_argument("--theme", default=None, help="Path to theme root")
    cro_p.add_argument("--json", action="store_true", help="Output JSON")

    # 5. cart-calc
    cart_p = subparsers.add_parser("cart-calc", help="Calculate cart mutations and shipping bar")
    cart_p.add_argument("--subtotal", type=float, default=0.0, help="Current subtotal")
    cart_p.add_argument("--threshold", type=float, default=1000.0, help="Free shipping threshold")
    cart_p.add_argument("--add-price", type=float, default=None, help="Add item with nominal price")
    cart_p.add_argument("--json", action="store_true", help="Output JSON")

    # 6. integrity
    int_p = subparsers.add_parser("integrity", help="Run 7-Gate Anti-Regression Theme Integrity check")
    int_p.add_argument("--theme", default=None, help="Path to theme root")
    int_p.add_argument("--json", action="store_true", help="Output JSON")

    # 7. proposal
    prop_p = subparsers.add_parser("proposal", help="Generate personalized Shopify proposal & 6-stage client cockpit")
    prop_p.add_argument("--client", required=True, help="Client name")
    prop_p.add_argument("--brand", required=True, help="Brand or store name")
    prop_p.add_argument("--niche", default="custom_dtc", help="Store vertical")
    prop_p.add_argument("--tier", default="scale_1500", choices=["launch_1200", "scale_1500"], help="Package tier")
    prop_p.add_argument("--extra-batches", type=int, default=0, help="Extra 10-product batches ($50 each)")
    prop_p.add_argument("--gmc", action="store_true", help="Include Google Merchant Center ($300)")
    prop_p.add_argument("--seo", action="store_true", help="Include SEO semantics ($200)")
    prop_p.add_argument("--json", action="store_true", help="Output JSON")

    # 8. triage-ticket
    tkt_p = subparsers.add_parser("triage-ticket", help="Triage client task/revision and route to Spatial Canvas node")
    tkt_p.add_argument("--deal-id", required=True, help="Deal ID")
    tkt_p.add_argument("--client", required=True, help="Client name")
    tkt_p.add_argument("--text", required=True, help="Client question or revision text")
    tkt_p.add_argument("--used-revisions", type=int, default=0, help="Already used revisions")
    tkt_p.add_argument("--max-revisions", type=int, default=3, help="Max included revisions")
    tkt_p.add_argument("--persist", action="store_true", help="Persist ticket directly into SpatialCanvasSessionRouter")
    tkt_p.add_argument("--json", action="store_true", help="Output JSON")

    # 9. lsf-status
    lsf_stat_p = subparsers.add_parser("lsf-status", help="Query local-storefront daemon status")
    lsf_stat_p.add_argument("--port", type=int, default=9292, help="Port of running lsf daemon")
    lsf_stat_p.add_argument("--json", action="store_true", help="Output JSON")

    # 10. lsf-check
    lsf_chk_p = subparsers.add_parser("lsf-check", help="Run strict Liquid check via local-storefront")
    lsf_chk_p.add_argument("--theme", default=None, help="Path to theme directory")
    lsf_chk_p.add_argument("--fix", action="store_true", help="Rewrite markup with fixes")
    lsf_chk_p.add_argument("--json", action="store_true", help="Output JSON")

    # 11. lsf-profile
    lsf_prof_p = subparsers.add_parser("lsf-profile", help="Profile theme rendering times via local-storefront")
    lsf_prof_p.add_argument("--theme", default=None, help="Path to theme directory")
    lsf_prof_p.add_argument("--path", default="/", help="URL route to profile")
    lsf_prof_p.add_argument("--json", action="store_true", help="Output JSON")

    # 12. lsf-serve
    lsf_srv_p = subparsers.add_parser("lsf-serve", help="Start local-storefront HTTP daemon")
    lsf_srv_p.add_argument("--theme", default=None, help="Path to theme directory")
    lsf_srv_p.add_argument("--port", type=int, default=9292, help="Port to listen on")
    lsf_srv_p.add_argument("--no-live-reload", action="store_true", help="Disable WebSocket live-reload")
    lsf_srv_p.add_argument("--json", action="store_true", help="Output JSON")

    # 13. lsf-reload
    lsf_rel_p = subparsers.add_parser("lsf-reload", help="Hot-reload local-storefront data fixtures")
    lsf_rel_p.add_argument("--port", type=int, default=9292, help="Port of running lsf daemon")
    lsf_rel_p.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()
    service = DNKShopifyService()

    if args.command == "validate":
        target = args.target
        target_path = Path(target)
        if target_path.exists() and target_path.is_file():
            code = target_path.read_text(encoding="utf-8", errors="replace")
        else:
            code = target

        res = service.validate_liquid(code)
        if args.json:
            print(res.model_dump_json(indent=2))
        else:
            status = "✅ VALID" if res.valid else "❌ INVALID"
            print(f"Liquid Validation: {status}")
            print(f"Tags: {res.tags_count}, Variables: {res.variables_count}")
            if res.errors:
                print("Errors:")
                for err in res.errors:
                    print(f"  - {err}")
        sys.exit(0 if res.valid else 1)

    elif args.command == "list-blocks":
        theme_p = Path(args.theme) if args.theme else None
        blocks = service.list_theme_blocks(theme_p)
        if args.json:
            print(json.dumps([b.model_dump() for b in blocks], indent=2))
        else:
            print(f"🧱 Found {len(blocks)} Theme Blocks 2.0:")
            for b in blocks:
                priv = "🔒 Private" if b.is_private else "🌐 Public"
                schema = "📜 Schema" if b.has_schema else "No Schema"
                print(f"  • {b.block_name:<30} | {priv:<10} | {schema}")
        sys.exit(0)

    elif args.command == "check":
        theme_p = Path(args.theme) if args.theme else None
        res = service.check_theme(theme_p)
        if args.json:
            print(res.model_dump_json(indent=2))
        else:
            status = "✅ PASS" if res.is_compliant else "❌ FAIL"
            print(f"Theme Check: {status} ({res.theme_path})")
            print(f"Files: {res.total_files}, Errors: {res.errors_count}, Warnings: {res.warnings_count}")
            for v in res.violations:
                print(f"  - [{v.severity.upper()}] {v.file_path}: {v.message}")
        sys.exit(0 if res.is_compliant else 1)

    elif args.command == "cro-audit":
        theme_p = Path(args.theme) if args.theme else None
        res = service.audit_cro(theme_p)
        if args.json:
            print(res.model_dump_json(indent=2))
        else:
            print(f"🎯 CRO Conversion Readiness: {res.score}/100")
            print(f"Detected ({len(res.detected_blocks)}): {', '.join(res.detected_blocks)}")
            if res.missing_blocks:
                print(f"Missing ({len(res.missing_blocks)}): {', '.join(res.missing_blocks)}")
        sys.exit(0)

    elif args.command == "cart-calc":
        mutations = []
        if args.add_price is not None:
            mutations.append(
                CartMutation(
                    action="add",
                    variant_id="mock_variant_1",
                    quantity=1,
                    properties={"price": str(args.add_price)},
                )
            )

        spec = CartMutationQueueSpec(
            current_subtotal=args.subtotal,
            free_shipping_threshold=args.threshold,
            mutations=mutations,
        )
        res = service.calculate_cart(spec)
        if args.json:
            print(res.model_dump_json(indent=2))
        else:
            print(f"🛒 Cart Subtotal: ${res.new_subtotal:.2f}")
            print(f"Shipping Progress: {res.progress_percentage:.1f}%")
            print(f"Free Shipping Qualified: {'✅ YES' if res.free_shipping_qualified else '❌ NO'}")
            print(f"Remaining for Free Shipping: ${res.remaining_for_free_shipping:.2f}")
        sys.exit(0)

    elif args.command == "integrity":
        theme_p = Path(args.theme) if args.theme else None
        res = service.run_7gate_integrity(theme_p)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            status = "✅ PASS (100% CLEAN & PROTECTED)" if res.get("all_gates_passed") else "❌ FAIL"
            print(f"Theme 7-Gate Integrity: {status}")
            print(res.get("stdout", ""))
            if res.get("stderr"):
                print(res["stderr"])
        sys.exit(0 if res.get("all_gates_passed") else 1)

    elif args.command == "proposal":
        spec = ProposalConfigSpec(
            client_name=args.client,
            brand_name=args.brand,
            niche=args.niche,  # type: ignore[arg-type]
            package_tier=args.tier,  # type: ignore[arg-type]
            extra_products_batches=args.extra_batches,
            include_gmc_setup=args.gmc,
            include_seo_semantics=args.seo,
        )
        quote = service.generate_proposal_quote(spec)
        stages = service.initialize_client_deal_cockpit(quote)
        if args.json:
            print(
                json.dumps(
                    {"quote": quote.model_dump(), "stages": [s.model_dump() for s in stages]},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"Deal ID: {quote.deal_id} | Scope SHA-256: {quote.scope_sha256}")
            print(f"Total: ${quote.total_investment_usd} (30% Prepay: ${quote.prepayment_30_usd:.2f})")
            print(f"Annual App Savings: ${quote.annual_app_savings_usd}/yr | Payback: {quote.estimated_payback_months} mo")
        sys.exit(0)

    elif args.command == "triage-ticket":
        req = ClientTicketRequest(
            deal_id=args.deal_id,
            client_name=args.client,
            request_text=args.text,
            used_revisions_count=args.used_revisions,
            max_free_revisions=args.max_revisions,
        )
        res = service.triage_client_ticket(req, persist_to_canvas_session=args.persist)
        if args.json:
            print(res.model_dump_json(indent=2))
        else:
            print(f"[{res.ticket_id}] {res.classification} -> {res.session_id} ({res.assigned_agent})")
            print(res.action_summary_uk)
        sys.exit(0)

    elif args.command == "lsf-status":
        manager = LocalStorefrontManager(default_port=args.port)
        status = manager.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            active = status.get("active")
            print(f"LSF Daemon Status: {'🟢 ACTIVE' if active else '🔴 INACTIVE'} (Port {args.port})")
            if active and status.get("status"):
                st = status["status"]
                print(f"Theme: {st.get('theme')}")
                print(f"Templates: {', '.join(st.get('templates', []))}")
        sys.exit(0 if status.get("active") else 1)

    elif args.command == "lsf-check":
        theme_dir = args.theme or str(service.default_theme_path)
        manager = LocalStorefrontManager()
        res = manager.run_check(theme_dir, fix=args.fix)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res.get("stdout") or res.get("stderr"))
        sys.exit(0 if res.get("success") else 1)

    elif args.command == "lsf-profile":
        theme_dir = args.theme or str(service.default_theme_path)
        manager = LocalStorefrontManager()
        res = manager.run_profile(theme_dir, path=args.path)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res.get("output"))
        sys.exit(0 if res.get("success") else 1)

    elif args.command == "lsf-serve":
        theme_dir = args.theme or str(service.default_theme_path)
        manager = LocalStorefrontManager(default_port=args.port)
        res = manager.start_daemon(theme_dir, live_reload=not args.no_live_reload, port=args.port)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res.get("success"):
                print(f"🟢 LSF Daemon started successfully at {res.get('url', f'http://127.0.0.1:{args.port}')}")
            else:
                print(f"🔴 Failed to start LSF Daemon: {res.get('error')}")
        sys.exit(0 if res.get("success") else 1)

    elif args.command == "lsf-reload":
        manager = LocalStorefrontManager(default_port=args.port)
        res = manager.reload_data()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("🟢 Data reloaded successfully" if res.get("success") else f"🔴 Reload failed: {res.get('error')}")
        sys.exit(0 if res.get("success") else 1)


if __name__ == "__main__":
    main()
