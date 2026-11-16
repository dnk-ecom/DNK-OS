# --- DNK-MRH-HEADER ---
# mrh_id: "core/obsidian/wiki_canvas_translator.py"
# purpose: "Understand-Anything SOTA Bidirectional Translator: Karpathy LLM Wiki ⇄ Obsidian Canvas 1.0 / JSON Graph"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-21"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class WikiArticle:
    path: Path
    title: str
    tags: List[str] = field(default_factory=list)
    summary: str = ""
    outgoing_links: List[str] = field(default_factory=list)
    raw_content: str = ""


class WikiCanvasTranslator:
    """
    Bidirectional Karpathy LLM Wiki ⇄ Obsidian Canvas 1.0 translator.
    Adapted from Egonex-AI/Understand-Anything article-analyzer & graph-reviewer patterns.
    """

    WIKILINK_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
    FRONTMATTER_TAGS_PATTERN = re.compile(r"tags:\s*\[(.*?)\]", re.IGNORECASE)

    def __init__(self, dark_teal_theme: bool = True) -> None:
        self.dark_teal_theme = dark_teal_theme

    def parse_wiki_article(self, file_path: Path) -> WikiArticle:
        """Parse markdown file, extracting title, frontmatter tags, wikilinks, and brief summary."""
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()

        title = file_path.stem
        summary_lines: List[str] = []
        tags: List[str] = []

        # Extract title from first H1
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract wikilinks
        outgoing = self.WIKILINK_PATTERN.findall(text)

        # Extract tags
        for line in lines[:30]:
            if "tags:" in line:
                m = self.FRONTMATTER_TAGS_PATTERN.search(line)
                if m:
                    raw_tags = m.group(1).split(",")
                    tags.extend([t.strip().strip("'\"") for t in raw_tags if t.strip()])

        # Extract first non-header, non-frontmatter paragraph as summary
        in_frontmatter = False
        for line in lines:
            s_line = line.strip()
            if s_line == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter or not s_line or s_line.startswith("#"):
                continue
            summary_lines.append(s_line)
            if len(summary_lines) >= 3:
                break

        summary = " ".join(summary_lines)[:240]

        return WikiArticle(
            path=file_path,
            title=title,
            tags=tags,
            summary=summary,
            outgoing_links=list(dict.fromkeys(outgoing)),
            raw_content=text,
        )

    def wiki_to_canvas(
        self,
        wiki_dir: str,
        output_canvas_path: str,
        max_articles: int = 50,
    ) -> Dict[str, Any]:
        """Convert a directory of markdown wiki articles to an Obsidian Canvas 1.0 JSON graph."""
        wiki_path = Path(wiki_dir)
        if not wiki_path.exists():
            return {"nodes": [], "edges": []}

        articles: Dict[str, WikiArticle] = {}
        for md_file in sorted(wiki_path.rglob("*.md"))[:max_articles]:
            art = self.parse_wiki_article(md_file)
            articles[md_file.stem] = art

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        # 2D Grid Layout calculation
        col_count = 4
        node_width = 320
        node_height = 180
        gap_x = 80
        gap_y = 60

        for idx, (stem, art) in enumerate(articles.items()):
            row = idx // col_count
            col = idx % col_count
            x = col * (node_width + gap_x)
            y = row * (node_height + gap_y)

            tag_badge = f" `#{art.tags[0]}`" if art.tags else ""
            node_text = (
                f"### {art.title}{tag_badge}\n\n"
                f"{art.summary or 'No preview available.'}\n\n"
                f"📄 `[[{stem}]]`"
            )

            nodes.append({
                "id": stem,
                "type": "text",
                "text": node_text,
                "x": x,
                "y": y,
                "width": node_width,
                "height": node_height,
                "color": "5",  # Cyan (#35d5d5) in Obsidian Canvas
            })

        # Generate edges for wikilinks
        edge_idx = 0
        for stem, art in articles.items():
            for target_link in art.outgoing_links:
                target_stem = Path(target_link).stem
                if target_stem in articles and target_stem != stem:
                    edges.append({
                        "id": f"edge-wiki-{edge_idx}",
                        "fromNode": stem,
                        "toNode": target_stem,
                        "fromSide": "right",
                        "toSide": "left",
                        "color": "5",
                    })
                    edge_idx += 1

        canvas_data = {"nodes": nodes, "edges": edges}

        # Write output file if specified
        out = Path(output_canvas_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(canvas_data, f, indent=2, ensure_ascii=False)

        return canvas_data

    def canvas_to_wiki(self, canvas_path: str, output_wiki_dir: str) -> List[str]:
        """
        Reverse translator: converts Obsidian Canvas 1.0 JSON graph into structured Karpathy LLM Wiki articles.
        Reconstructs [[wikilinks]] based on graph edges.
        """
        canvas_file = Path(canvas_path)
        if not canvas_file.exists():
            return []

        with open(canvas_file, "r", encoding="utf-8") as f:
            canvas_data = json.load(f)

        nodes = canvas_data.get("nodes", [])
        edges = canvas_data.get("edges", [])

        # Build adjacency mapping
        outgoing_map: Dict[str, List[str]] = {n["id"]: [] for n in nodes}
        for edge in edges:
            fn = edge.get("fromNode")
            tn = edge.get("toNode")
            if fn in outgoing_map and tn:
                outgoing_map[fn].append(tn)

        out_dir = Path(output_wiki_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        for node in nodes:
            node_id = str(node.get("id", "untitled"))
            node_type = node.get("type", "text")
            raw_text = node.get("text", "")

            title_match = re.search(r"^###?\s+(.+)$", raw_text, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else node_id

            clean_filename = f"{re.sub(r'[^a-zA-Z0-9_-]', '_', node_id)}.md"
            target_path = out_dir / clean_filename

            # Format outgoing wikilinks
            links_section = ""
            targets = outgoing_map.get(node_id, [])
            if targets:
                links_list = "\n".join([f"- [[{t}]]" for t in targets])
                links_section = f"\n\n## 🔗 Related Knowledge Nodes\n{links_list}\n"

            content = (
                f"# --- DNK-MRH-HEADER ---\n"
                f'# mrh_id: "docs/notes/{clean_filename}"\n'
                f'# purpose: "Synthesized LLM Wiki article from Obsidian Canvas node {node_id}"\n'
                f'# canonical_source: false\n'
                f"# status: \"Active\"\n"
                f'# version: "1.0.0"\n'
                f"# author: \"DNK OS Karpathy Wiki Translator\"\n"
                f"# --- END DNK-MRH-HEADER ---\n\n"
                f"# {title}\n\n"
                f"{raw_text}\n"
                f"{links_section}"
            )

            target_path.write_text(content, encoding="utf-8")
            created_files.append(str(target_path))

        return created_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Bidirectional LLM Wiki ⇄ Obsidian Canvas Translator")
    parser.add_argument("--wiki-dir", default="docs/notes")
    parser.add_argument("--canvas-path", default="docs/notes/knowledge_graph.canvas")
    parser.add_argument("--direction", choices=["wiki_to_canvas", "canvas_to_wiki"], default="wiki_to_canvas")
    args = parser.parse_args()

    translator = WikiCanvasTranslator()
    if args.direction == "wiki_to_canvas":
        data = translator.wiki_to_canvas(args.wiki_dir, args.canvas_path)
        print(f"Synthesized Canvas graph with {len(data['nodes'])} nodes and {len(data['edges'])} edges at {args.canvas_path}")
    else:
        files = translator.canvas_to_wiki(args.canvas_path, args.wiki_dir)
        print(f"Generated {len(files)} markdown wiki articles in {args.wiki_dir}")


if __name__ == "__main__":
    main()
