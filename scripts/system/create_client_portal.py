#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/create_client_portal.py"
# purpose: "Scaffold isolated, secure, multi-page client portal from DNK template"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import argparse
import os
import secrets
import shutil
import string
import sys
from pathlib import Path


def generate_secure_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def scaffold_client_portal(
    client_slug: str,
    title: str | None = None,
    password: str | None = None,
    output_dir: str | None = None,
) -> Path:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    template_dir = repo_root / "packages" / "client_portal_template"

    if not template_dir.exists():
        print(f"❌ Error: Template directory not found at {template_dir}", file=sys.stderr)
        sys.exit(1)

    display_title = title or client_slug.replace("-", " ").title()
    portal_password = password or f"{client_slug.replace('-', '_')}_{generate_secure_password(6)}"

    target_dir = (
        Path(output_dir).resolve()
        if output_dir
        else repo_root / "docs" / "projects" / "dnk_ecom" / "clients" / client_slug
    )

    if target_dir.exists():
        print(f"⚠️ Target directory already exists: {target_dir}")
        print("Aborting to prevent overwriting existing client data.", file=sys.stderr)
        sys.exit(1)

    print(f"🧬 [DNK OS] Scaffolding Client Portal for: {display_title} ({client_slug})...")
    shutil.copytree(template_dir, target_dir)

    # Personalize HTML files
    replacements = {
        "DNK<span>.ecom</span> • Client Space": f"{display_title} • <span>DNK Ecom</span>",
        "Клієнтський Простір | DNK Ecom": f"{display_title} | Клієнтський Простір DNK Ecom",
        "dnk2026": portal_password,
    }

    for ext in ["*.html", "*.md", "*.json"]:
        for file_path in target_dir.rglob(ext):
            try:
                content = file_path.read_text(encoding="utf-8")
                for src, dst in replacements.items():
                    content = content.replace(src, dst)
                file_path.write_text(content, encoding="utf-8")
            except Exception as e:
                print(f"⚠️ Warning updating {file_path.name}: {e}")

    # Personalize Edge Middleware
    middleware_path = target_dir / "functions" / "_middleware.ts"
    if middleware_path.exists():
        mw_content = middleware_path.read_text(encoding="utf-8")
        mw_content = mw_content.replace('validPassword = env.CLIENT_PASSWORD || "dnk2026"', f'validPassword = env.CLIENT_PASSWORD || "{portal_password}"')
        middleware_path.write_text(mw_content, encoding="utf-8")

    print("\n✅ [SUCCESS] Client Portal Scaffolding Complete!")
    print(f"📁 Path: {target_dir}")
    print(f"🌐 Subdomain: {client_slug}.kuzmenko.top")
    print(f"🔑 Secret Password: {portal_password}")
    print(f"🔗 1-Click Direct Access URL: https://{client_slug}.kuzmenko.top/?key={portal_password}")
    print("\n🚀 Next Steps:")
    print(f"  1. In Cloudflare Pages, deploy folder: {target_dir.relative_to(repo_root)}")
    print(f"  2. In Cloudflare Pages, bind custom domain: {client_slug}.kuzmenko.top")
    print(f"  3. In Cloudflare DNS, add CNAME: {client_slug} -> <project-name>.pages.dev\n")

    return target_dir


def main():
    parser = argparse.ArgumentParser(description="Create secure isolated client portal from DNK template.")
    parser.add_argument("--client", required=True, help="Client slug (e.g., nike, adidas, craftiar)")
    parser.add_argument("--title", help="Client display title (e.g., 'Nike Ukraine')")
    parser.add_argument("--password", help="Custom password for client access (default: auto-generated)")
    parser.add_argument("--output", help="Optional custom output directory")

    args = parser.parse_args()
    scaffold_client_portal(
        client_slug=args.client,
        title=args.title,
        password=args.password,
        output_dir=args.output,
    )


if __name__ == "__main__":
    main()
