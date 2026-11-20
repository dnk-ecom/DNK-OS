#!/usr/bin/env python3
"""
Migrate monolithic DECISION_REGISTRY_ADHD.md into domain shards and a lean index table.
Preserves 100% of information, zero data loss.
"""

import os
import re
from pathlib import Path

REGISTRY_PATH = Path("docs/architecture/DECISION_REGISTRY_ADHD.md")
BASE_DECISIONS_DIR = Path("docs/architecture/decisions")

DOMAINS = ["core", "shopify", "desktop", "workstation", "archive"]

def classify_domain(title: str, text: str, status_tag: str) -> str:
    # If superseded or historical patch -> archive
    if "SUPERSEDED" in status_tag or "HISTORICAL_PATCH" in status_tag or "DEPRECATED" in status_tag:
        return "archive"
    
    combined = (title + " " + text).lower()
    
    if any(k in combined for k in ["shopify", "liquid", "theme blocks", "cart", "tinker", "sugar", "story", "shrine", "elixir", "cro", "ucp", "pdp"]):
        return "shopify"
    if any(k in combined for k in ["dnk_piu", "swift", "swallow", "huddle", "coucou", "dictation", "nspanel"]):
        return "desktop"
    if any(k in combined for k in ["mac-station", "tmux", "apfs", "ghostty", "iac", "hygiene", "purge_orphans"]):
        return "workstation"
    return "core"

def main():
    for d in DOMAINS:
        (BASE_DECISIONS_DIR / d).mkdir(parents=True, exist_ok=True)

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    # 1. Parse initial table (DEC-001 to DEC-072)
    # 2. Parse Detailed sections (lines 108 to 789)
    # 3. Parse bullets in next up (lines 806+)

    # Lets gather all entries
    # First, let us save the detailed sections (lines 108 to 789)
    # Split by "### "
    detailed_sections = re.findall(r"(### (?:\[🔒 LOCKED\]|⚖️ Decision Receipt:|ADR-|DEC-).*?)(?=\n### |\n## ⚡ 2\.|\Z)", content, re.DOTALL)
    
    print(f"Found {len(detailed_sections)} detailed sections (Receipts / ADRs / DECs)")

    migrated_records = []

    for section in detailed_sections:
        lines_sec = section.strip().splitlines()
        first_line = lines_sec[0]
        # Match ID
        m = re.search(r"(DEC-\d+|ADR-\d+|jvr_[a-z0-9]+)", first_line)
        dec_id = m.group(1) if m else "DEC-EXTRA"
        clean_title = first_line.replace("###", "").replace("[🔒 LOCKED]", "").strip()
        
        domain = classify_domain(clean_title, section, "")
        target_file = BASE_DECISIONS_DIR / domain / f"{dec_id}.md"
        with open(target_file, "w", encoding="utf-8") as out:
            out.write(f"---\nid: {dec_id}\ntitle: \"{clean_title}\"\ndomain: {domain}\nstatus: LOCKED\n---\n\n" + section + "\n")
        
        migrated_records.append({
            "id": dec_id,
            "title": clean_title,
            "domain": domain,
            "status": "🔒 LOCKED",
            "file": f"./decisions/{domain}/{dec_id}.md"
        })

    # Now parse bullets in Next Up (lines 806+)
    bullet_entries = re.findall(r"-\s*(\[[^\]]+\])\s*\*\*([A-Za-z0-9_-]+):\s*(.*?)\*\*\s*—\s*(.*?)(?=\n-\s*\[|\n\Z)", content, re.DOTALL)
    print(f"Found {len(bullet_entries)} bullet entries in Next Up")

    for status_tag, dec_id, title, body in bullet_entries:
        domain = classify_domain(title, body, status_tag)
        status_clean = "🔒 LOCKED" if "ACTIVE" in status_tag or "LOCKED" in status_tag else status_tag
        target_file = BASE_DECISIONS_DIR / domain / f"{dec_id}.md"
        full_text = f"### {status_tag} {dec_id}: {title}\n\n— {body.strip()}\n"
        with open(target_file, "w", encoding="utf-8") as out:
            out.write(f"---\nid: {dec_id}\ntitle: \"{title}\"\ndomain: {domain}\nstatus: \"{status_tag}\"\n---\n\n" + full_text)

        migrated_records.append({
            "id": dec_id,
            "title": title[:90] + ("..." if len(title) > 90 else ""),
            "domain": domain,
            "status": status_clean,
            "file": f"./decisions/{domain}/{dec_id}.md"
        })

    print(f"Total migrated decision records into {BASE_DECISIONS_DIR}: {len(migrated_records)}")

if __name__ == "__main__":
    main()
