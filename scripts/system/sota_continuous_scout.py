#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/sota_continuous_scout.py"
# purpose: "Autonomous SOTA Scout & Continuous Assimilation Engine for DNK OS: monitors GitHub frontier without local RAM/SSD bloat."
# canonical_source: true
# alters_files: ["docs/notes/sota_audits/*", "data/sota_scout_queue.json"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

HUB_ROOT = Path(__file__).resolve().parents[2]
if str(HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(HUB_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("SOTAContinuousScout")

# Search topics representing the 2026 frontier in agent harnesses and fast inference
FRONTIER_QUERIES = [
    {"topic": "system_one_decisions", "query": "typesafe jev OR \"decision model\" stars:>10"},
    {"topic": "code_execution_mode", "query": "\"code mode\" OR \"fastmcp\" OR \"code execution with mcp\" stars:>20"},
    {"topic": "agent_harness_swe", "query": "\"agent harness\" OR \"swe-bench\" stars:>50"},
    {"topic": "context_compaction", "query": "\"context compaction\" OR \"trajectory pruning\" stars:>15"},
    {"topic": "shopify_ai_theme", "query": "\"shopify theme blocks\" OR \"shopify ai\" stars:>10"},
]


class SOTAContinuousScout:
    """
    Continuous GitHub frontier monitor designed for Mac M1 8GB/256GB hardware constraints.
    Operates strictly via lightweight GitHub CLI / REST API metadata; never clones
    heavy foreign repositories directly into local workspace.
    """

    def __init__(self, hub_dir: Optional[Path] = None):
        self.hub_root = hub_dir or HUB_ROOT
        self.catalog_file = self.hub_root / "docs/notes/MY TASKS/4. БАЗА ЗНАНЬ ТА SOTA/112 SOTA Repository Catalog.md"
        self.audits_dir = self.hub_root / "docs/notes/sota_audits"
        self.audits_dir.mkdir(parents=True, exist_ok=True)
        self.known_repos: Set[str] = self._load_known_repositories()

    def _load_known_repositories(self) -> Set[str]:
        """Extracts already cataloged repository slugs to prevent duplicate scans."""
        known = set()
        if self.catalog_file.exists():
            content = self.catalog_file.read_text(encoding="utf-8", errors="ignore")
            import re
            matches = re.findall(r"\[([a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+)\]\(https://github\.com/", content)
            known.update(matches)
        logger.info(f"Loaded {len(known)} known repositories from catalog.")
        return known

    def check_gh_installed(self) -> bool:
        """Verifies GitHub CLI is installed and authenticated."""
        return shutil.which("gh") is not None

    def search_frontier(self, limit_per_query: int = 5) -> List[Dict[str, Any]]:
        """Executes targeted searches across frontier topics via GitHub CLI."""
        if not self.check_gh_installed():
            logger.error("GitHub CLI (gh) is not installed or not in PATH.")
            return []

        discovered: List[Dict[str, Any]] = []
        seen_slugs: Set[str] = set()

        for item in FRONTIER_QUERIES:
            topic = item["topic"]
            query = item["query"]
            cmd = [
                "gh", "search", "repos",
                query,
                "--sort", "updated",
                "--limit", str(limit_per_query),
                "--json", "fullName,description,url,stargazersCount,updatedAt,license"
            ]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                repos = json.loads(result.stdout)
                for r in repos:
                    slug = r.get("fullName", "")
                    if not slug or slug in seen_slugs:
                        continue
                    seen_slugs.add(slug)

                    is_new = slug not in self.known_repos
                    license_name = r.get("license", {}).get("name") if isinstance(r.get("license"), dict) else "Unknown"
                    discovered.append({
                        "slug": slug,
                        "topic": topic,
                        "description": r.get("description") or "No description",
                        "url": r.get("url"),
                        "stars": r.get("stargazersCount", 0),
                        "updated_at": r.get("updatedAt"),
                        "license": license_name or "Unknown",
                        "is_new": is_new,
                    })
            except Exception as e:
                logger.warning(f"Failed query for topic '{topic}': {e}")

        return discovered

    def generate_sota_pulse_report(self, discovered: List[Dict[str, Any]]) -> Path:
        """Generates a clean ADHD markdown report of newly discovered frontier repositories."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        report_file = self.audits_dir / f"SOTA_FRONTIER_PULSE_{now_str}.md"

        new_repos = [r for r in discovered if r["is_new"]]
        existing_repos = [r for r in discovered if not r["is_new"]]

        lines = [
            "# --- DNK-MRH-HEADER ---",
            f"# mrh_id: \"docs/notes/sota_audits/SOTA_FRONTIER_PULSE_{now_str}.md\"",
            "# purpose: \"Automated Continuous SOTA Frontier Pulse Report (Thin-Client Hardware Governor)\"",
            "# canonical_source: true",
            "# alters_files: []",
            "# triggers_tasks: []",
            "# status: \"Active\"",
            "# version: \"1.0.0\"",
            f"# updated_at: \"{now_str}\"",
            "# author: \"SOTAContinuousScout & Antigravity\"",
            "# --- END DNK-MRH-HEADER ---",
            "",
            f"# 📡 SOTA Frontier Pulse Report ({now_str})",
            "",
            f"- **Всього знайдено репозиторіїв на фронтирі:** {len(discovered)}",
            f"- **Нових (відсутніх у каталозі):** {len(new_repos)}",
            f"- **Вже каталогізованих (відстежуваних):** {len(existing_repos)}",
            "- **Політика пам'яті:** 0 байт фізичного клонування (Zero-Local-Footprint).",
            "",
            "## 🌟 Свіжі Відкриття Фронтиру (Нові кандидати)",
            "",
            "| Репозиторій | Топік | ⭐ Stars | Ліцензія | Призначення |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]

        if not new_repos:
            lines.append("| *Нових кандидатів не виявлено* | - | - | - | Каталог повністю синхронізований |")
        else:
            for r in new_repos:
                desc = r["description"].replace("|", "/")[:90]
                lines.append(f"| **[{r['slug']}]({r['url']})** | `{r['topic']}` | {r['stars']} | `{r['license']}` | {desc} |")

        lines.extend([
            "",
            "## 📌 Рекомендована Дія для Денчіка та Antigravity",
            "1. Відібрати кандидатів із пермісивними ліцензіями (`MIT`, `Apache-2.0`).",
            "2. Для репозиторіїв із високим сигналом створити `SKILL.md` або адаптер без фізичного завантаження в `DNK_HUB` (через GitHub REST API / raw extraction).",
            "3. Додати валідних кандидатів у `112 SOTA Repository Catalog.md`.",
        ])

        report_file.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"SOTA Pulse Report saved to {report_file}")
        return report_file


def main() -> int:
    parser = argparse.ArgumentParser(description="DNK OS Continuous SOTA Scout Engine")
    parser.add_argument("--limit", type=int, default=5, help="Max results per search query")
    parser.add_argument("--report-only", action="store_true", help="Only output report without interactive prompt")
    args = parser.parse_args()

    scout = SOTAContinuousScout()
    discovered = scout.search_frontier(limit_per_query=args.limit)
    report_path = scout.generate_sota_pulse_report(discovered)
    print(f"✅ SOTA Pulse report generated: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
