#!/usr/bin/env python3
"""
Generate a clean, high-speed, compact DECISION_REGISTRY_ADHD.md index.
"""

from pathlib import Path
import re

DEC_DIR = Path("docs/architecture/decisions")
OUTPUT_FILE = Path("docs/architecture/DECISION_REGISTRY_ADHD.md")

DOMAIN_METADATA = {
    "shopify": ("🛍️ 1. Shopify E-Commerce & Themes", "Теми, Theme Blocks 2.0, Liquid, Cart, No-App CRO, UCP, LocalStorefront"),
    "core": ("🧠 2. Core Microkernel & Architecture", "FastMCP, SCONES пам\x27ять, Task Forest DAG, Sentinel, Quarantine, EGM, In-RAM Code Mode"),
    "desktop": ("💻 3. macOS Desktop Shell (DNK_Piu)", "Swift, NSPanel, транскрипція Vertex AI, swallow micro-transformations, HUD"),
    "workstation": ("⚙️ 4. Workstation IaC & Runtime", "mac-station, tmux, APFS clonefile, Ghostty, Python 3.14, pnpm CAS"),
    "archive": ("🗄️ 5. Архів та Історичні Патчі", "Застарілі (SUPERSEDED) та одноразові історичні патчі")
}

def extract_meta(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Try frontmatter
    id_match = re.search(r"^id:\s*(.*)$", text, re.MULTILINE)
    dec_id = id_match.group(1).strip() if id_match else file_path.stem
    
    title_match = re.search(r"^title:\s*\"?(.*?)\"?$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem
    
    # Clean up title
    title = re.sub(r"^(###\s*(\[[^\]]+\]\s*)?(DEC-\d+|ADR-\d+):\s*)", "", title).strip()
    title = title.replace("[🔒 LOCKED]", "").strip()
    if len(title) > 95:
        title = title[:92] + "..."
    
    status_match = re.search(r"^status:\s*\"?(.*?)\"?$", text, re.MULTILINE)
    status = status_match.group(1).strip() if status_match else "🔒 LOCKED"
    if "ACTIVE" in status or "LOCKED" in status:
        status = "🔒 LOCKED"
    elif "SUPERSEDED" in status:
        status = "⚠️ SUPERSEDED"
    elif "HISTORICAL" in status:
        status = "🗄️ HISTORICAL"

    return dec_id, title, status

def main():
    lines = [
        "---",
        'title: "ADHD VIBE-CODER DECISION REGISTRY (SSOT)"',
        'description: "Canonical ADHD Decision Registry & SOTA Architecture Index for DNK OS."',
        'mrh_id: "docs/architecture/DECISION_REGISTRY_ADHD.md"',
        "status: Active",
        "archetype: GENERAL_DOC",
        'version: "3.0.0"',
        "updated: 2026-11-18",
        "tags:",
        "  - dnk-os",
        "  - architecture",
        "  - sota-2026",
        "---",
        "",
        "> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)",
        "> ```yaml",
        "> # --- DNK-MRH-HEADER ---",
        '> mrh_id: "docs/architecture/DECISION_REGISTRY_ADHD.md"',
        '> purpose: "Canonical ADHD Decision Registry & SOTA Architecture Index for DNK OS."',
        "> canonical_source: true",
        "> alters_files: []",
        "> triggers_tasks: []",
        '> status: "Active"',
        '> version: "3.0.0"',
        '> updated_at: "2026-11-18"',
        '> author: "DNK-e.com Maksym & Antigravity"',
        "> # --- END DNK-MRH-HEADER ---",
        "> ```",
        "",
        "# ⚡ ADHD VIBE-CODER DECISION REGISTRY (SSOT)",
        "",
        "> **Залізне Правило (Zero Discussion Amnesia):** Будь-яке рішення зі статусом `[🔒 LOCKED]` **ЗАБОРОНЕНО обговорювати заново**. Агент зчитує індекс, бере задачу та видає виключно лаконічний ADHD-результат (до 1 екрана). Детальні специфікації кожного рішення зберігаються у відповідних доменних шардах `./decisions/<domain>/`.",
        "",
        "---",
        ""
    ]

    for domain in ["shopify", "core", "desktop", "workstation", "archive"]:
        d_dir = DEC_DIR / domain
        if not d_dir.exists():
            continue
        
        section_title, desc = DOMAIN_METADATA.get(domain, (domain.title(), ""))
        lines.append(f"## {section_title}")
        lines.append(f"> *{desc}*")
        lines.append("")
        lines.append("| ID | Технічне Рішення (Core Verdict) | Статус | Специфікація (LOD) |")
        lines.append("| :--- | :--- | :---: | :---: |")

        files = sorted(list(d_dir.glob("*.md")), key=lambda p: p.stem)
        for f in files:
            dec_id, title, status = extract_meta(f)
            rel_link = f"[Деталі](./decisions/{domain}/{f.name})"
            lines.append(f"| **{dec_id}** | {title} | {status} | {rel_link} |")
        
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.extend([
        "## ⚡ ПОТОЧНИЙ ФОКУС & ЧЕРГА ДІЙ (ACTIVE SPRINT)",
        "",
        "- [x] **DEC-158**: Затверджено 3-рівневу Бібліотеку Джерел (Shopify Dev, Донори, W3C) та Людино-Машинний Тандем.",
        "- [x] **SOTA Sharding**: Рефакторинг `DECISION_REGISTRY_ADHD.md` у 5 доменних шардів (Core, Shopify, Desktop, Workstation, Archive).",
        "- [ ] **Фаза 2 (MVP Shopify Theme)**: Denchik переносить `Cart Drawer v2` (Shrine Pro) та `12-col Canvas` (Sugar) у гілку `mvp`.",
        "- [ ] **Fast Verification**: Прогін `uv run python3 services/dnk_shopify/cli.py check` та верифікація в `LocalStorefront` (1.2 мс).",
        ""
    ])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))
    
    print(f"✅ Generated clean {OUTPUT_FILE} ({len(lines)} lines)")

if __name__ == "__main__":
    main()
