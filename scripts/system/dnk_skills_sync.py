#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/dnk_skills_sync.py"
# purpose: "Universal Skill Registry Synchronizer across Antigravity, Hermes (Gerych), and Claude Code."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
import sys
from pathlib import Path

HOME = Path.home()
REPO_ROOT = HOME / "Kuzmenko/MY_LIFE_WORK"
DNK_HUB = REPO_ROOT / "DNK_HUB"
DNK_OS = REPO_ROOT / "DNK_OS"

# Source Directories (Ordered by priority: DNK_OS Core first)
SOURCES = [
    DNK_OS / "core/skills",
    DNK_HUB / "core/skills",
    REPO_ROOT / "DNK_Vibe/mac-station/skills",
    REPO_ROOT / "SHOPIFY/DNKShopify/DNKEcom/GitHub_Agentic_Shopify_WF/shopify-ai-toolkit/skills",
    HOME / ".agents/skills",
]

# Target Agent Harnesses
TARGETS = {
    "Antigravity IDE": HOME / ".gemini/config/skills",
    "Gerych (Hermes)": HOME / ".hermes/skills/dnk_ecosystem",
    "Claude Code": HOME / ".claude/skills",
}


def find_skills(source_dirs: list[Path]) -> dict[str, Path]:
    skills = {}
    for src in source_dirs:
        if not src.exists():
            continue
        for item in src.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skill_name = item.name
                if skill_name not in skills:
                    skills[skill_name] = item.resolve()
    return skills


def sync_skills() -> None:
    print("=" * 68)
    print("🚀 [DNK Universal Skills Substrate] Synchronizing Agent Skills...")
    print("=" * 68)

    discovered = find_skills(SOURCES)
    print(f"📦 Total unique SOTA skills discovered: {len(discovered)}")

    for harness_name, target_dir in TARGETS.items():
        target_dir.mkdir(parents=True, exist_ok=True)
        created = 0
        updated = 0
        intact = 0

        for skill_name, src_path in discovered.items():
            link_path = target_dir / skill_name
            if link_path.is_symlink():
                try:
                    current_target = link_path.resolve()
                    if current_target == src_path:
                        intact += 1
                        continue
                    else:
                        link_path.unlink()
                        link_path.symlink_to(src_path)
                        updated += 1
                except Exception:
                    link_path.unlink()
                    link_path.symlink_to(src_path)
                    updated += 1
            elif link_path.exists():
                # Don't overwrite real directories, preserve local customizations
                intact += 1
            else:
                try:
                    link_path.symlink_to(src_path)
                    created += 1
                except Exception as e:
                    print(f"⚠️ Could not link {skill_name} -> {link_path}: {e}")

        print(f"  ✨ {harness_name:16}: {created} created | {updated} updated | {intact} intact ({target_dir})")

    print("-" * 68)
    print("✅ All harnesses now share the unified DNK OS Knowledge Base (0 byte duplicates)!")
    print("=" * 68)


if __name__ == "__main__":
    sync_skills()
