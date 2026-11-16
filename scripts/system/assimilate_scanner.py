#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/assimilate_scanner.py"
# purpose: "Autonomous Library Inventory & Deep Assimilation Scanner across DNK_Vibe, DNKEcom, and packages/."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "Antigravity & Gerych & Maxim"
# --- END DNK-MRH-HEADER ---

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

AUDITS_DIR = Path("docs/notes/sota_audits")

TARGET_POOLS = {
    "Vibe R&D (UI/System)": Path("../DNK_Vibe"),
    "Shopify Themes": Path("../DNKEcom/GitHub_Shopify_Themes"),
    "Shopify Apps": Path("../DNKEcom/GitHub_Shopify_Apps"),
    "Shopify Agent Workflows": Path("../DNKEcom/Audit_Shopify_Themes_Sell_WF"),
    "Local Packages": Path("packages"),
}

def get_existing_audits() -> List[str]:
    if not AUDITS_DIR.exists():
        return []
    return [f.name.lower() for f in AUDITS_DIR.glob("*.md")]

def scan_pool(name: str, pool_path: Path, audits: List[str]) -> List[Tuple[str, bool, str]]:
    if not pool_path.exists():
        return []
    
    results = []
    for item in sorted(pool_path.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            clean_name = item.name.lower().replace("-", "_").replace(" ", "_")
            # Match against audit notes
            has_audit = any(clean_name in a or a.startswith(clean_name[:12]) for a in audits)
            results.append((item.name, has_audit, str(item)))
    return results

def main():
    parser = argparse.ArgumentParser(description="DNK OS Smart Assimilation Library Scanner")
    parser.add_argument("--pending", action="store_true", help="Show only repositories awaiting deep assimilation")
    args = parser.parse_args()

    audits = get_existing_audits()
    print("🧬 [DNK OS Smart Assimilation Scanner] Library Inventory & Mechanics Audit Status")
    print(f"📚 Registered Formal Audits in docs/notes/sota_audits/: {len(audits)}\n")

    total_repos = 0
    total_audited = 0
    total_pending = 0

    for pool_name, pool_path in TARGET_POOLS.items():
        repos = scan_pool(pool_name, pool_path, audits)
        if not repos:
            continue

        audited_count = sum(1 for _, audited, _ in repos if audited)
        pending_count = len(repos) - audited_count
        total_repos += len(repos)
        total_audited += audited_count
        total_pending += pending_count

        print(f"📦 {pool_name} ({len(repos)} repos | {audited_count} audited | {pending_count} pending):")
        for name, audited, path in repos:
            if args.pending and audited:
                continue
            icon = "✅ Audited" if audited else "⏳ Pending Deep Assimilation"
            print(f"   {icon:30} : {name}")
        print()

    print("=" * 70)
    print(f"📊 SUMMARY: Total Repos: {total_repos} | ✅ Audited: {total_audited} | ⏳ Pending: {total_pending}")
    print(f"🎯 Protocol: 'Scan First, Never Reinvent, Synthesize Sovereign Core'")

if __name__ == "__main__":
    main()
