#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/audit_all_docs_compliance.py"
# purpose: "Full Repository Documentation Compliance Matrix & Scorecard Generator (Triple-Optics & Schema Gate)."
# canonical_source: true
# alters_files: ["docs/audit/DOCUMENTATION_COMPLIANCE_MATRIX.md"]
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import argparse
import glob
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dnk_md_triple_optics import audit_markdown_path, TripleOpticsResult  # noqa: E402
from markdown_schema_gate import MarkdownSchemaAuditor, MarkdownViolation  # noqa: E402

EXCLUDE_PATTERNS = [
    "archive/", "/archive/", "node_modules/", ".git/", "dist/",
    "build/", ".next/", "cache/", ".gemini/", ".worktrees/"
]

def is_excluded(path_str: str) -> bool:
    normalized = path_str.replace("\\", "/")
    return any(p in normalized for p in EXCLUDE_PATTERNS)

def classify_zone(rel_path: str) -> str:
    """
    Classifies a markdown file into one of three architectural zones per ADR-095:
    - ZONE_1_KNOWLEDGE_BASE: docs/** (Triple-Optics mandatory)
    - ZONE_2_REPO_CONTEXT: repository & app READMEs, AGENTS.md (Lightweight Markdown)
    - ZONE_3_AGENT_OR_VENDOR_EXEMPT: SOUL.md, prompts, vendor packages (Zero-Bloat Exempt)
    """
    norm = rel_path.replace("\\", "/")
    
    # Zone 3: Agent Prompts, System Prompts, Vendor & Archive (Zero-Bloat Exempt)
    if "core/orchestrator/agents/" in norm or norm.endswith("SOUL.md") or "PROMPT" in norm:
        return "ZONE_3_AGENT_OR_VENDOR_EXEMPT"
    if norm.startswith("packages/archify/") or "THIRD_PARTY" in norm or norm.endswith("LICENSE.md"):
        return "ZONE_3_AGENT_OR_VENDOR_EXEMPT"
    if "docs/archive/" in norm or "archive/" in norm or "docs/architecture/decisions/" in norm:
        return "ZONE_3_AGENT_OR_VENDOR_EXEMPT"

    # Zone 1: Knowledge Base (docs/**)
    if norm.startswith("docs/"):
        return "ZONE_1_KNOWLEDGE_BASE"

    # Zone 2: Repo Context & Component Guides (Root or Module Readmes / Directives)
    if norm.endswith("README.md") or norm.endswith("AGENTS.md") or norm.endswith("DOMAIN_RULES.md"):
        return "ZONE_2_REPO_CONTEXT"

    # Default to Zone 2 for other code-adjacent markdown files
    return "ZONE_2_REPO_CONTEXT"

def run_audit(root_dir: str, generate_matrix_path: str = None) -> Tuple[int, int, List[dict]]:
    root = Path(root_dir).resolve()
    schema_auditor = MarkdownSchemaAuditor(repo_root=root)
    all_md = [
        p for p in root.rglob("*.md")
        if not is_excluded(str(p.relative_to(root)))
    ]

    total = len(all_md)
    compliant_count = 0
    records = []

    for path in sorted(all_md):
        rel_path = str(path.relative_to(root)).replace("\\", "/")
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            content = ""

        zone = classify_zone(rel_path)
        archetype = schema_auditor.detect_archetype(rel_path, content)
        structural_errs = []
        semantic_errs = []

        if zone == "ZONE_1_KNOWLEDGE_BASE":
            # Zone 1: Strict Triple-Optics & Schema Gate
            triple_rep = audit_markdown_path(str(path))
            if not triple_rep.is_compliant:
                structural_errs = triple_rep.reasons()

            if not "templates/" in rel_path and not rel_path.endswith("_template.md"):
                try:
                    schema_violations = schema_auditor.audit_file(path)
                    semantic_errs = [
                        f"{v.violation_type}: {v.description}"
                        for v in schema_violations
                        if v.violation_type != "TRIPLE_OPTICS_VIOLATION"
                    ]
                except Exception as e:
                    semantic_errs.append(f"GATE_EXCEPTION: {str(e)}")

        elif zone == "ZONE_2_REPO_CONTEXT":
            # Zone 2: Lightweight Markdown (Check for H1 title and path hygiene only)
            triple_rep = audit_markdown_path(str(path))
            if triple_rep.absolute_path_leaks:
                structural_errs.append(f"Absolute path leaks detected: {', '.join(triple_rep.absolute_path_leaks)}")
            if not re.search(r"^#\s+.+", content, re.MULTILINE):
                structural_errs.append("Missing top-level H1 (#) title")

        elif zone == "ZONE_3_AGENT_OR_VENDOR_EXEMPT":
            # Zone 3: Strictly Exempt (Zero-Bloat Invariant)
            # Only ensure no accidental absolute path leaks
            triple_rep = audit_markdown_path(str(path))
            if triple_rep.absolute_path_leaks:
                structural_errs.append(f"Absolute path leaks detected: {', '.join(triple_rep.absolute_path_leaks)}")

        is_ok = (len(structural_errs) == 0 and len(semantic_errs) == 0)
        if is_ok:
            compliant_count += 1

        records.append({
            "path": rel_path,
            "zone": zone,
            "status": "COMPLIANT" if is_ok else "NON_COMPLIANT",
            "structural_errors": structural_errs,
            "semantic_errors": semantic_errs,
            "archetype": archetype
        })

    if generate_matrix_path:
        out_file = root / generate_matrix_path
        out_file.parent.mkdir(parents=True, exist_ok=True)
        generate_markdown_report(out_file, total, compliant_count, records)

    return total, compliant_count, records

def generate_markdown_report(out_path: Path, total: int, compliant: int, records: List[dict]):
    pct = (compliant / total * 100.0) if total > 0 else 0.0
    non_compliant = total - compliant

    structural_count = sum(1 for r in records if r["structural_errors"] and not r["semantic_errors"])
    semantic_count = sum(1 for r in records if r["semantic_errors"])
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    z1_total = sum(1 for r in records if r["zone"] == "ZONE_1_KNOWLEDGE_BASE")
    z1_ok = sum(1 for r in records if r["zone"] == "ZONE_1_KNOWLEDGE_BASE" and r["status"] == "COMPLIANT")
    z2_total = sum(1 for r in records if r["zone"] == "ZONE_2_REPO_CONTEXT")
    z2_ok = sum(1 for r in records if r["zone"] == "ZONE_2_REPO_CONTEXT" and r["status"] == "COMPLIANT")
    z3_total = sum(1 for r in records if r["zone"] == "ZONE_3_AGENT_OR_VENDOR_EXEMPT")
    z3_ok = sum(1 for r in records if r["zone"] == "ZONE_3_AGENT_OR_VENDOR_EXEMPT" and r["status"] == "COMPLIANT")

    lines = [
        "---",
        'title: "DNK OS Documentation Compliance Matrix & Scorecard"',
        'description: "Automated Repository-wide Markdown Triple-Zone and Schema Gate Compliance Ledger (ADR-095)."',
        'mrh_id: "docs/audit/DOCUMENTATION_COMPLIANCE_MATRIX.md"',
        "status: Active",
        "archetype: GENERAL_DOC",
        'version: "2.0.0"',
        f"updated: {datetime.now().strftime('%Y-%m-%d')}",
        "tags:",
        "  - dnk-os",
        "  - audit",
        "  - documentation",
        "---",
        "",
        "> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)",
        "> ```yaml",
        "> # --- DNK-MRH-HEADER ---",
        '> mrh_id: "docs/audit/DOCUMENTATION_COMPLIANCE_MATRIX.md"',
        '> purpose: "Automated Repository-wide Markdown Triple-Zone and Schema Gate Compliance Ledger (ADR-095)."',
        "> canonical_source: true",
        "> alters_files: []",
        "> triggers_tasks: []",
        '> status: "Active"',
        '> version: "2.0.0"',
        f'> updated_at: "{datetime.now().strftime("%Y-%m-%d")}"',
        '> author: "DNK-e.com Maksym & Antigravity"',
        "> # --- END DNK-MRH-HEADER ---",
        "> ```",
        "",
        "# 📊 DNK OS Documentation Compliance Matrix & Scorecard (ADR-095)",
        "",
        f"> **Дата аудиту:** `{timestamp}`  ",
        f"> **Загальний стан відповідності:** `{compliant}/{total}` (**{pct:.1f}%**)  ",
        f"> **Потребують виправлення:** `{non_compliant}` (Структурні: `{structural_count}`, Семантичні: `{semantic_count}`)  ",
        "",
        "### 🗺️ Розподіл за архітектурними зонами (ADR-095):",
        f"- **Зона 1: База Знань (`docs/**`)**: `{z1_ok}/{z1_total}` (Обов'язковий Triple-Optics FumaDocs + Obsidian + Schema Gate)",
        f"- **Зона 2: Репозитарний Контекст (`README.md`, `AGENTS.md`)**: `{z2_ok}/{z2_total}` (Легкий GitHub Markdown)",
        f"- **Зона 3: Системні Промпти & Вендор (`SOUL.md`, `packages/archify/`)**: `{z3_ok}/{z3_total}` (Строгий Zero-Bloat Exempt)",
        "",
        "## 🎯 Стандарти верифікації",
        "1. **Зона 1 (FumaDocs / Nextra + Obsidian)**: Рядок 1 — обов'язковий YAML блок з 8 ключами, за яким слідує `> [!metadata]- ⚙️...` та Schema Gate перевірки.",
        "2. **Зона 2 (GitHub Navigation)**: Чистий Markdown з валідним H1 та обов'язковою відсутністю абсолютних шляхів `/Users/...`.",
        "3. **Зона 3 (Zero-Bloat Invariant)**: Промпти та сторонній код звільнені від надлишкових веб-метаданих задля економії токенів і збереження контексту.",
        "",
        "## ❌ Документи, що потребують виправлення",
        "",
        "| Статус | Зона | Файл | Архетип | Необхідні виправлення |",
        "| :---: | :---: | :--- | :--- | :--- |"
    ]

    for r in records:
        if r["status"] == "NON_COMPLIANT":
            all_errs = []
            if r["structural_errors"]:
                all_errs.append("**Структурні:** " + "; ".join(r["structural_errors"][:3]))
            if r["semantic_errors"]:
                all_errs.append("**Семантичні:** " + "; ".join(r["semantic_errors"][:3]))
            err_str = "<br>".join(all_errs)
            lines.append(f"| ❌ | `{r['zone']}` | `{r['path']}` | `{r['archetype']}` | {err_str} |")

    lines.extend([
        "",
        "## ✅ Документи, що відповідають стандарту",
        "",
        "| Статус | Зона | Файл | Архетип |",
        "| :---: | :---: | :--- | :--- |"
    ])

    for r in records:
        if r["status"] == "COMPLIANT":
            lines.append(f"| ✅ | `{r['zone']}` | `{r['path']}` | `{r['archetype']}` |")

    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Audit documentation compliance across DNK OS.")
    parser.add_argument("--root", default=".", help="Root directory to scan.")
    parser.add_argument("--report", default="docs/audit/DOCUMENTATION_COMPLIANCE_MATRIX.md", help="Output Markdown matrix path.")
    parser.add_argument("--check", action="store_true", help="Exit with code 1 if any non-compliant files exist.")
    args = parser.parse_args()

    print("================================================================================")
    print("🛡️  DNK OS DOCUMENTATION COMPLIANCE AUDITOR & SCORECARD GENERATOR")
    print("================================================================================")
    total, compliant, records = run_audit(args.root, args.report)
    non_compliant = total - compliant
    pct = (compliant / total * 100.0) if total > 0 else 0.0

    print(f"📁 Всього проскановано .md файлів: {total}")
    print(f"✅ Повністю відповідають (Compliant): {compliant} ({pct:.1f}%)")
    print(f"❌ Потребують виправлення (Non-Compliant): {non_compliant}")
    if args.report:
        print(f"📄 Звіт збережено у: {args.report}")
    print("================================================================================")

    if args.check and non_compliant > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
