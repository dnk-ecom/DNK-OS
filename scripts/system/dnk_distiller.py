#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/dnk_distiller.py"
# purpose: "DNK Knowledge Distiller & Pruning Engine: Scan DNK_HUB for inspiration, verify temporal freshness against today, consolidate similar modules into clean DNK_OS, and prune deprecated files."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "Antigravity & Gerych & Maxim"
# --- END DNK-MRH-HEADER ---

import argparse
from datetime import datetime
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

def get_current_execution_date() -> datetime:
    """Dynamic real-time timestamp when the agent executes the task."""
    return datetime.now()

SEARCH_ROOTS = [
    Path("docs"),
    Path("core"),
    Path("services"),
    Path("apps"),
]

def extract_date_from_file(file_path: Path) -> Tuple[datetime, str]:
    """Extract updated_at from MRH header, frontmatter, or file mtime."""
    date_str = None
    date_source = "mtime"

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")[:3000]
        # Look for updated_at or updated in YAML / MRH
        m = re.search(r"updated_at:\s*[\"']?(\d{4}-\d{2}-\d{2})[\"']?", content)
        if not m:
            m = re.search(r"updated:\s*[\"']?(\d{4}-\d{2}-\d{2})[\"']?", content)
        if not m:
            m = re.search(r"date:\s*[\"']?(\d{4}-\d{2}-\d{2})[\"']?", content)

        if m:
            date_str = m.group(1)
            date_source = "mrh_header"
    except Exception:
        pass

    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d"), date_source
        except ValueError:
            pass

    # Fallback to filesystem modification time
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime), "mtime"

def assess_freshness(doc_date: datetime, current_date: Optional[datetime] = None) -> Tuple[str, str, int]:
    """Calculate age in days relative to the agent's real execution date (Agentic 3x Velocity Standard)."""
    now = current_date or get_current_execution_date()
    delta = (now - doc_date).days
    if delta < 0:
        delta = 0

    # 3x Velocity Thresholds: 10 days, 30 days
    if delta <= 10:
        return "🟢 FRESH", "Актуально (менше 10 днів)", delta
    elif delta <= 30:
        return "🟡 MATURE", "Потребує звірки з останніми версіями SDK/API (10-30 днів)", delta
    else:
        return "🔴 LEGACY", "Високий ризик застарілих API та патернів (>30 днів)", delta

def search_knowledge_pool(query: str, max_results: int = 25, current_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Scan DNK_HUB documents and source files for matching query."""
    matches = []
    q_lower = query.lower()
    now = current_date or get_current_execution_date()

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.name.startswith("."):
                continue
            if p.suffix not in [".md", ".py", ".yaml", ".json", ".ts", ".tsx", ".liquid"]:
                continue

            name_lower = p.name.lower()
            rel_path = str(p)

            # Match on filename or read sample
            if q_lower in name_lower or q_lower in rel_path.lower():
                doc_date, source = extract_date_from_file(p)
                icon, label, age_days = assess_freshness(doc_date, current_date=now)
                matches.append({
                    "path": rel_path,
                    "name": p.name,
                    "date": doc_date.strftime("%Y-%m-%d"),
                    "source": source,
                    "status_icon": icon,
                    "status_label": label,
                    "age_days": age_days,
                })

            if len(matches) >= max_results:
                break
        if len(matches) >= max_results:
            break

    # Sort: newest first
    matches.sort(key=lambda x: x["age_days"])
    return matches

def main():
    parser = argparse.ArgumentParser(description="DNK Knowledge Distiller & Dynamic Temporal Freshness Evaluator")
    parser.add_argument("query", help="Keyword or domain topic to search in DNK_HUB (e.g. 'shopify', 'canvas', 'auth')")
    parser.add_argument("--limit", type=int, default=20, help="Maximum results to return")
    parser.add_argument("--date", help="Optional override for execution date (YYYY-MM-DD), defaults to real-time now()")
    args = parser.parse_args()

    exec_date = datetime.strptime(args.date, "%Y-%m-%d") if args.date else get_current_execution_date()

    print(f"🔍 [DNK Knowledge Distiller] Пошук напрацювань у DNK_HUB за темою: '{args.query}'")
    print(f"📅 Дата реалізації агентом (Live Execution Date): {exec_date.strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = search_knowledge_pool(args.query, max_results=args.limit, current_date=exec_date)

    if not results:
        print("Нічого не знайдено.")
        return

    print(f"Знайдено {len(results)} відповідних документів/файлів:\n")
    print(f"{'Статус':<12} | {'Дата':<10} | {'Вік (днів)':<10} | {'Файл / Шлях'}")
    print("-" * 80)

    for r in results:
        print(f"{r['status_icon']:<12} | {r['date']:<10} | {r['age_days']:<10} | {r['path']}")

    print("\n" + "=" * 80)
    print("💡 Рекомендація з дистиляції (Стандарт швидкості Agentic 3x):")
    print("1. Згрупуйте схожі рішення в єдиний суверенний модуль у ../DNK_OS/.")
    print("2. Для файлів 🔴 LEGACY (>30 днів): обов'язково перевірте зміни в офіційних API перед перенесенням.")
    print("3. Після успішної верифікації в DNK_OS: позначте старі файли у DNK_HUB як застарілі або видаліть для очищення.")

if __name__ == "__main__":
    main()
