# --- DNK-MRH-HEADER ---
# mrh_id: "core/memory/scones_semantic_connector.py"
# purpose: "Understand-Anything SOTA Semantic Connection Generator between SCONES rules and Architecture Decision Records (ADRs)"
# canonical_source: true
# alters_files: ["docs/scones/scones_adr_semantic_graph.json"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-21"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class SemanticLink:
    source_id: str
    target_id: str
    source_type: str  # "rule" or "adr"
    target_type: str  # "rule" or "adr"
    confidence: float
    shared_concepts: List[str] = field(default_factory=list)
    relationship: str = "supports"  # "implements", "governs", "supports", "cites"


@dataclass
class SconesADRGraph:
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_rules: int = 0
    total_adrs: int = 0
    total_links: int = 0
    links: List[SemanticLink] = field(default_factory=list)
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_rules": self.total_rules,
            "total_adrs": self.total_adrs,
            "total_links": self.total_links,
            "links": [asdict(link) for link in self.links],
            "nodes": self.nodes,
        }


class SconesSemanticConnector:
    """
    Synthesizes a bidirectional semantic graph between SCONES cognitive memory rules
    and Architecture Decision Records (ADRs) using AST/keyword concept extraction.
    Inspired by Egonex-AI/Understand-Anything article-analyzer & graph-reviewer patterns.
    """

    STOPWORDS: Set[str] = {
        "the", "and", "for", "with", "that", "this", "from", "are", "not", "have",
        "was", "all", "can", "has", "but", "our", "you", "your", "they", "been",
        "для", "що", "або", "який", "яка", "яке", "які", "при", "про", "без", "під"
    }

    def __init__(
        self,
        scones_rules_dir: Optional[str] = None,
        adr_dirs: Optional[List[str]] = None,
    ) -> None:
        if scones_rules_dir is None:
            primary = Path("docs/architecture/scones")
            fallback = Path("docs/scones")
            self.scones_rules_dir = primary if primary.exists() or not fallback.exists() else fallback
        else:
            self.scones_rules_dir = Path(scones_rules_dir)
        self.adr_dirs = [Path(d) for d in (adr_dirs or [
            "docs/architecture/adr",
            "docs/architecture",
            "docs/tasks",
        ])]

    def _tokenize_text(self, text: str) -> Set[str]:
        words = re.findall(r"[a-zA-Z0-9_]{3,}", text.lower())
        return {w for w in words if w not in self.STOPWORDS}

    def load_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load all SCONES rules from json files."""
        rules: Dict[str, Dict[str, Any]] = {}
        if not self.scones_rules_dir.exists():
            return rules

        # 1. Assimilated rules
        assimilated_dir = self.scones_rules_dir / "assimilated_rules"
        if assimilated_dir.exists():
            for rule_file in assimilated_dir.glob("*.json"):
                try:
                    with open(rule_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        repo = data.get("repo", rule_file.stem)
                        for idx, rule in enumerate(data.get("rules", [])):
                            rule_id = f"rule-{rule_file.stem}-{idx}"
                            title = rule.get("pattern", rule.get("topic", rule.get("title", f"Rule {idx}")))
                            content = " ".join([
                                str(rule.get("description", "")),
                                str(rule.get("pattern", "")),
                                str(rule.get("actionable_guidance", "")),
                                str(rule.get("dnk_applicability", "")),
                            ])
                            rules[rule_id] = {
                                "id": rule_id,
                                "type": "rule",
                                "title": title,
                                "repo": repo,
                                "file": str(rule_file),
                                "tokens": self._tokenize_text(f"{title} {content}"),
                                "raw": rule,
                            }
                except Exception:
                    continue

        # 2. Domain knowledge rules
        domain_file = self.scones_rules_dir / "domain_knowledge.json"
        if domain_file.exists():
            try:
                with open(domain_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("rules", data if isinstance(data, list) else []):
                        if isinstance(item, dict):
                            rule_id = f"rule-domain-{item.get('id', len(rules))}"
                            title = item.get("topic", item.get("title", "Domain Knowledge"))
                            content = str(item.get("content", ""))
                            rules[rule_id] = {
                                "id": rule_id,
                                "type": "rule",
                                "title": title,
                                "repo": "dnk-core",
                                "file": str(domain_file),
                                "tokens": self._tokenize_text(f"{title} {content}"),
                                "raw": item,
                            }
            except Exception:
                pass

        return rules

    def load_adrs(self) -> Dict[str, Dict[str, Any]]:
        """Load ADR markdown files from designated directories."""
        adrs: Dict[str, Dict[str, Any]] = {}
        for adr_dir in self.adr_dirs:
            if not adr_dir.exists():
                continue
            for adr_path in adr_dir.rglob("*.md"):
                if "ADR" not in adr_path.name.upper():
                    continue
                try:
                    text = adr_path.read_text(encoding="utf-8", errors="ignore")
                    adr_id = adr_path.stem.replace(" ", "_")
                    first_heading = ""
                    for line in text.splitlines():
                        if line.startswith("# "):
                            first_heading = line[2:].strip()
                            break
                    title = first_heading or adr_path.stem

                    adrs[adr_id] = {
                        "id": adr_id,
                        "type": "adr",
                        "title": title,
                        "file": str(adr_path),
                        "tokens": self._tokenize_text(f"{title} {text[:3000]}"),
                    }
                except Exception:
                    continue
        return adrs

    def build_graph(self, min_shared_concepts: int = 3) -> SconesADRGraph:
        """
        Cross-reference rules and ADRs, computing semantic overlap links.
        """
        rules = self.load_rules()
        adrs = self.load_adrs()

        graph = SconesADRGraph(
            total_rules=len(rules),
            total_adrs=len(adrs),
        )

        # Register nodes
        for r_id, r_data in rules.items():
            graph.nodes[r_id] = {
                "id": r_id,
                "type": "rule",
                "title": r_data["title"],
                "file": r_data["file"],
            }
        for a_id, a_data in adrs.items():
            graph.nodes[a_id] = {
                "id": a_id,
                "type": "adr",
                "title": a_data["title"],
                "file": a_data["file"],
            }

        # Compute cross-links
        for r_id, r_data in rules.items():
            r_tokens = r_data["tokens"]
            if not r_tokens:
                continue

            for a_id, a_data in adrs.items():
                a_tokens = a_data["tokens"]
                if not a_tokens:
                    continue

                shared = r_tokens.intersection(a_tokens)
                if len(shared) >= min_shared_concepts:
                    # Jaccard / Overlap coefficient
                    overlap_coeff = len(shared) / min(len(r_tokens), len(a_tokens))
                    confidence = round(min(1.0, overlap_coeff * 1.5), 3)

                    # Determine relationship
                    rel = "supports"
                    if "invariant" in shared or "security" in shared or "gate" in shared:
                        rel = "governs"
                    elif "architecture" in shared or "pipeline" in shared:
                        rel = "implements"

                    link = SemanticLink(
                        source_id=r_id,
                        target_id=a_id,
                        source_type="rule",
                        target_type="adr",
                        confidence=confidence,
                        shared_concepts=sorted(list(shared))[:8],
                        relationship=rel,
                    )
                    graph.links.append(link)

        graph.total_links = len(graph.links)
        return graph

    def save_graph(self, output_path: str = "docs/scones/scones_adr_semantic_graph.json") -> str:
        """Compute and serialize the semantic graph to JSON."""
        graph = self.build_graph()
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(graph.to_dict(), f, indent=2, ensure_ascii=False)
        return str(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SCONES Rules ⇄ ADR Semantic Graph")
    parser.add_argument("--output", default="docs/scones/scones_adr_semantic_graph.json")
    args = parser.parse_args()

    connector = SconesSemanticConnector()
    saved = connector.save_graph(output_path=args.output)
    print(f"Successfully generated SCONES ⇄ ADR Semantic Graph: {saved}")


if __name__ == "__main__":
    main()
