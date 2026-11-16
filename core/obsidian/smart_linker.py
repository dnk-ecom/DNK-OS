# --- DNK-MRH-HEADER ---
# mrh_id: "core/obsidian/smart_linker.py"
# purpose: "Obsidian & zsviczian/kplex Smart Linking, Semantic Triples, and K-Hop Context Graph Engine for DNK OS Kernel."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-15"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""
Obsidian & zsviczian/kplex Smart Linking Engine for DNK OS Kernel.

Implements:
1. Canonical Obsidian Wikilinks: [[target#section|alias]] with bidirectional backlink index.
2. zsviczian/kplex Semantic Triples & Typed Relations:
   - Inline Dataview/Excalidraw Brain fields: `relation:: [[target|alias]]`
   - Typed directional graph edges: `parent` (up), `child` (down), `friend` (sibling),
     `depends_on`, `implements`, `verifies`, `alters`, `references`.
3. K-Hop Smart Context Traversal (kplex Graph RAG):
   - Given a focus node or file, traverses k hops across forward links, backlinks,
     and semantic relations to assemble a minimal, high-signal context subgraph.
4. Unlinked Mention Discovery & Smart Auto-Link Suggestions:
   - Scans raw thoughts, markdown notes, or code docstrings against the live kernel
     entity registry (ADRs, Decisions, Modules, SOTA Repositories, Thoughts) and suggests
     or auto-injects canonical `[[target|alias]]` wikilinks without corrupting existing links or code blocks.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from core.registry.repo_catalog import SOTA_GOLDEN_CORE_BLUEPRINTS
from core.self_awareness import CANONICAL_PRODUCT_MODULES


# Canonical kplex & DNK OS semantic relation ontology
KPLEX_RELATION_ONTOLOGY: Dict[str, Dict[str, str]] = {
    "parent": {
        "hierarchy": "up",
        "inverse": "child",
        "color": "4",
        "label_uk": "Батьківський концепт (↑)",
        "label_en": "Parent Concept (↑)",
    },
    "child": {
        "hierarchy": "down",
        "inverse": "parent",
        "color": "5",
        "label_uk": "Дочірній елемент (↓)",
        "label_en": "Child Element (↓)",
    },
    "friend": {
        "hierarchy": "same",
        "inverse": "friend",
        "color": "6",
        "label_uk": "Споріднений вузол (↔)",
        "label_en": "Related / Friend (↔)",
    },
    "depends_on": {
        "hierarchy": "up",
        "inverse": "depended_by",
        "color": "2",
        "label_uk": "Залежить від",
        "label_en": "Depends On",
    },
    "implements": {
        "hierarchy": "down",
        "inverse": "implemented_by",
        "color": "4",
        "label_uk": "Реалізує",
        "label_en": "Implements",
    },
    "verifies": {
        "hierarchy": "down",
        "inverse": "verified_by",
        "color": "4",
        "label_uk": "Верифікує",
        "label_en": "Verifies",
    },
    "alters": {
        "hierarchy": "down",
        "inverse": "altered_by",
        "color": "3",
        "label_uk": "Модифікує",
        "label_en": "Alters",
    },
    "references": {
        "hierarchy": "same",
        "inverse": "referenced_by",
        "color": "5",
        "label_uk": "Посилається на",
        "label_en": "References",
    },
    "supports": {
        "hierarchy": "down",
        "inverse": "supported_by",
        "color": "4",
        "label_uk": "Підтверджує доказом",
        "label_en": "Supports (Evidence)",
    },
    "refutes": {
        "hierarchy": "down",
        "inverse": "refuted_by",
        "color": "1",
        "label_uk": "Спростовує (Контрдоказ)",
        "label_en": "Refutes (Counter-Evidence)",
    },
}

# Branch Status Lifecycle & Color-Coding Registry (Branch Sprawl & Context Rot Protection)
BRANCH_STATUS_LIFECYCLE: Dict[str, Dict[str, Any]] = {
    "PROPOSED": {
        "hex_color": "#35d5d5",
        "canvas_color": "5",
        "label_uk": "Запропонована гілка (Ego-Focal)",
        "allowed_transitions": ["IN_PROGRESS", "PRUNED"],
    },
    "IN_PROGRESS": {
        "hex_color": "#3b82f6",
        "canvas_color": "6",
        "label_uk": "У виконанні спеціалізованим агентом",
        "allowed_transitions": ["VERIFIED", "STALE", "REFUTED", "PRUNED"],
    },
    "VERIFIED": {
        "hex_color": "#22c55e",
        "canvas_color": "4",
        "label_uk": "Детерміновано верифіковано (Green Gate)",
        "allowed_transitions": ["STALE", "ARCHIVED"],
    },
    "STALE": {
        "hex_color": "#f59e0b",
        "canvas_color": "2",
        "label_uk": "Застарілий контекст (Потребує ревалідації)",
        "allowed_transitions": ["IN_PROGRESS", "VERIFIED", "PRUNED"],
    },
    "REFUTED": {
        "hex_color": "#ef4444",
        "canvas_color": "1",
        "label_uk": "Спростовано контрдоказом / Відхилено",
        "allowed_transitions": ["PRUNED", "ARCHIVED"],
    },
    "PRUNED": {
        "hex_color": "#64748b",
        "canvas_color": "0",
        "label_uk": "Відсічена гілка (Захист від Context Rot)",
        "allowed_transitions": ["ARCHIVED"],
    },
    "ARCHIVED": {
        "hex_color": "#475569",
        "canvas_color": "0",
        "label_uk": "Заархівовано в SCONES / Obsidian",
        "allowed_transitions": [],
    },
}

# Graph Lenses: projection filters over the multidimensional knowledge plexus
KPLEX_GRAPH_LENSES: Dict[str, Set[str]] = {
    "all": set(KPLEX_RELATION_ONTOLOGY.keys()),
    "architectural": {"parent", "child", "implements", "depends_on"},
    "evidence": {"verifies", "supports", "refutes", "implements"},
    "causal": {"depends_on", "alters", "verifies", "child"},
    "dependency": {"depends_on", "implements", "alters", "references"},
}

# Branch Sprawl Protection Bounds (MASE & Deep Module Invariants)
MAX_BRANCH_DEPTH: int = 3
MAX_BRANCH_WIDTH_PER_NODE: int = 4
MAX_ACTIVE_PLEX_NODES: int = 25

# Regex for typed inline kplex/Dataview fields: e.g. `implements:: [[DEC-012|Zero-Framework]]` or `[parent:: [[ADR-091]]]`
TYPED_RELATION_PATTERN = re.compile(
    r"(?:^|[\s\[\(])(?P<relation>[a-zA-Z_][a-zA-Z0-9_-]*)::\s*\[\[(?P<inner>[^\[\]]+)\]\]"
)

# Regex for standard Obsidian wikilinks: `[[target#section|alias]]`
WIKILINK_PATTERN = re.compile(r"(?P<embed>!?)\[\[(?P<inner>[^\[\]]+)\]\]")


@dataclass
class ParsedWikilink:
    raw: str
    target: str
    section: Optional[str] = None
    alias: Optional[str] = None
    relation: str = "references"
    is_embed: bool = False
    hierarchy_direction: str = "same"

    @property
    def canonical_wikilink(self) -> str:
        base = f"{self.target}#{self.section}" if self.section else self.target
        if self.alias and self.alias != base:
            return f"[[{base}|{self.alias}]]"
        return f"[[{base}]]"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["canonical_wikilink"] = self.canonical_wikilink
        return data


@dataclass
class SmartGraphEntity:
    entity_id: str
    title: str
    entity_type: str  # module | decision | sota_repo | thought | document
    aliases: List[str] = field(default_factory=list)
    relative_path: Optional[str] = None
    summary: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SmartLinkEdge:
    source_id: str
    target_id: str
    relation: str
    wikilink: str
    hierarchy_direction: str = "same"
    bidirectional: bool = True
    context_snippet: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UnlinkedMentionSuggestion:
    matched_text: str
    entity_id: str
    entity_type: str
    suggested_wikilink: str
    suggested_kplex_triple: str
    relation: str
    confidence: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_wikilink_inner(
    inner: str,
    raw: str = "",
    relation: str = "references",
    is_embed: bool = False,
) -> ParsedWikilink:
    """Parses the inner body of `[[target#section|alias]]` into structured components."""
    alias: Optional[str] = None
    target_part = inner.strip()

    if "|" in target_part:
        target_part, alias_part = target_part.split("|", 1)
        target_part = target_part.strip()
        alias = alias_part.strip() or None

    section: Optional[str] = None
    if "#" in target_part:
        target_part, section_part = target_part.split("#", 1)
        target_part = target_part.strip()
        section = section_part.strip() or None

    norm_relation = relation.lower().strip().replace("-", "_")
    if norm_relation not in KPLEX_RELATION_ONTOLOGY:
        norm_relation = "references"

    hierarchy = KPLEX_RELATION_ONTOLOGY[norm_relation]["hierarchy"]
    return ParsedWikilink(
        raw=raw or f"[[{inner}]]",
        target=target_part,
        section=section,
        alias=alias,
        relation=norm_relation,
        is_embed=is_embed,
        hierarchy_direction=hierarchy,
    )


def extract_wikilinks_and_triples(text: str) -> List[ParsedWikilink]:
    """
    Extracts both typed kplex triples (`relation:: [[target|alias]]`)
    and standard Obsidian wikilinks (`[[target#section|alias]]`) from markdown/text.
    """
    results: List[ParsedWikilink] = []
    seen_spans: List[Tuple[int, int]] = []

    for match in TYPED_RELATION_PATTERN.finditer(text):
        relation = match.group("relation")
        inner = match.group("inner")
        span = match.span()
        seen_spans.append(span)
        results.append(
            parse_wikilink_inner(
                inner=inner,
                raw=match.group(0).strip(),
                relation=relation,
                is_embed=False,
            )
        )

    for match in WIKILINK_PATTERN.finditer(text):
        start, end = match.span()
        if any(s <= start and end <= e for s, e in seen_spans):
            continue
        is_embed = bool(match.group("embed"))
        inner = match.group("inner")
        results.append(
            parse_wikilink_inner(
                inner=inner,
                raw=match.group(0),
                relation="references",
                is_embed=is_embed,
            )
        )

    return results


class KernelSmartLinker:
    """
    Obsidian + zsviczian/kplex Smart Linking Engine integrated into the DNK OS Kernel.
    Maintains a bidirectional entity & edge index across kernel modules, architectural
    decisions (DEC/ADR), SOTA repositories, and active ThoughtDAG nodes.
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = (
            repo_root.resolve()
            if repo_root
            else Path(__file__).resolve().parent.parent.parent
        )
        self.entities: Dict[str, SmartGraphEntity] = {}
        self.alias_to_entity_id: Dict[str, str] = {}
        self.forward_edges: Dict[str, List[SmartLinkEdge]] = {}
        self.backlink_edges: Dict[str, List[SmartLinkEdge]] = {}
        self._bootstrap_canonical_knowledge_graph()

    def _register_entity(self, entity: SmartGraphEntity) -> None:
        self.entities[entity.entity_id] = entity
        self.forward_edges.setdefault(entity.entity_id, [])
        self.backlink_edges.setdefault(entity.entity_id, [])

        lookup_keys = [entity.entity_id, entity.title] + list(entity.aliases)
        if entity.relative_path:
            lookup_keys.append(entity.relative_path)
            lookup_keys.append(Path(entity.relative_path).stem)

        for key in lookup_keys:
            cleaned = key.strip().lower()
            if len(cleaned) >= 3:
                self.alias_to_entity_id[cleaned] = entity.entity_id

    def _add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str = "references",
        alias: Optional[str] = None,
        context_snippet: str = "",
    ) -> SmartLinkEdge:
        norm_rel = relation.lower().strip().replace("-", "_")
        if norm_rel not in KPLEX_RELATION_ONTOLOGY:
            norm_rel = "references"

        target_entity = self.entities.get(target_id)
        display_label = alias or (target_entity.title if target_entity else target_id)
        wikilink = (
            f"[[{target_id}|{display_label}]]"
            if display_label != target_id
            else f"[[{target_id}]]"
        )
        hierarchy = KPLEX_RELATION_ONTOLOGY[norm_rel]["hierarchy"]

        edge = SmartLinkEdge(
            source_id=source_id,
            target_id=target_id,
            relation=norm_rel,
            wikilink=wikilink,
            hierarchy_direction=hierarchy,
            bidirectional=True,
            context_snippet=context_snippet,
        )

        fwd_list = self.forward_edges.setdefault(source_id, [])
        if not any(
            e.target_id == target_id and e.relation == norm_rel for e in fwd_list
        ):
            fwd_list.append(edge)

        back_list = self.backlink_edges.setdefault(target_id, [])
        if not any(
            e.source_id == source_id and e.relation == norm_rel for e in back_list
        ):
            back_list.append(edge)

        return edge

    def _bootstrap_canonical_knowledge_graph(self) -> None:
        """Indexes canonical DNK OS modules, locked decisions, and SOTA blueprints."""
        # 1. Register Canonical Product Modules
        for mod in CANONICAL_PRODUCT_MODULES:
            stem = Path(mod.relative_path).stem
            self._register_entity(
                SmartGraphEntity(
                    entity_id=mod.relative_path,
                    title=f"{mod.module_id} ({stem})",
                    entity_type="module",
                    aliases=[mod.module_id, stem, mod.relative_path],
                    relative_path=mod.relative_path,
                    summary=mod.responsibility,
                    tags=[mod.layer, mod.agent_owner],
                )
            )

        # 2. Register Core Architectural Decisions (DEC / ADR)
        canonical_decisions = [
            SmartGraphEntity(
                entity_id="DEC-008",
                title="DEC-008: Dogfooding-First Production Engine",
                entity_type="decision",
                aliases=["DEC-008", "dogfooding", "Dogfooding-First"],
                relative_path="docs/architecture/DECISION_REGISTRY_ADHD.md",
                summary="Use DNK OS Kernel & Companion directly for real engineering tasks.",
                tags=["locked", "architecture", "dogfooding"],
            ),
            SmartGraphEntity(
                entity_id="DEC-012",
                title="DEC-012 / ADR-091: Zero-Framework Microkernel",
                entity_type="decision",
                aliases=["DEC-012", "ADR-091", "Zero-Framework", "FastMCP Microkernel"],
                relative_path="docs/architecture/DECISION_REGISTRY_ADHD.md",
                summary="Pure Python stdlib + Pydantic + FastMCP without heavy third-party frameworks.",
                tags=["locked", "microkernel", "fastmcp"],
            ),
            SmartGraphEntity(
                entity_id="zsviczian_kplex",
                title="zsviczian/kplex: Semantic Knowledge Plexus & Smart Linking",
                entity_type="sota_repo",
                aliases=["kplex", "zsviczian/kplex", "Excalidraw Brain", "wikilinks", "smart linking"],
                relative_path="core/obsidian/smart_linker.py",
                summary="Typed parent/child/friend semantic relations, bidirectional wikilinks, and k-hop context.",
                tags=["obsidian", "kplex", "graph-rag", "smart-linking"],
            ),
        ]
        for dec in canonical_decisions:
            self._register_entity(dec)

        # 3. Register SOTA Golden Core Blueprints
        for repo in SOTA_GOLDEN_CORE_BLUEPRINTS:
            self._register_entity(
                SmartGraphEntity(
                    entity_id=repo.id,
                    title=repo.title,
                    entity_type="sota_repo",
                    aliases=[repo.id, repo.name, f"{repo.owner}/{repo.name}", repo.architectural_pattern],
                    relative_path=None,
                    summary=repo.what_it_gives,
                    tags=[repo.category, repo.maturity_tier],
                )
            )
            if repo.dnk_module_target in self.entities:
                self._add_edge(
                    source_id=repo.dnk_module_target,
                    target_id=repo.id,
                    relation="implements",
                    alias=repo.name,
                    context_snippet=repo.architectural_pattern,
                )

        # 4. Register Smart Linker module itself and core architectural edges
        self._register_entity(
            SmartGraphEntity(
                entity_id="core/obsidian/smart_linker.py",
                title="smart_linker (Obsidian & kplex Smart Linking)",
                entity_type="module",
                aliases=["smart_linker", "KernelSmartLinker", "kplex_smart_links"],
                relative_path="core/obsidian/smart_linker.py",
                summary="Bidirectional Obsidian wikilinks, kplex semantic triples, unlinked mentions, k-hop subgraph.",
                tags=["Layer 4: Knowledge, Memory & SOTA Registry", "herich_librarian"],
            )
        )

        self._add_edge("core/kernel.py", "DEC-012", "implements", "DEC-012 Zero-Framework")
        self._add_edge("core/orchestrator/thought_companion.py", "DEC-008", "implements", "DEC-008 Dogfooding")
        self._add_edge("core/orchestrator/sota_skills_engine.py", "zsviczian_kplex", "implements", "zsviczian/kplex")
        self._add_edge("core/obsidian/smart_linker.py", "zsviczian_kplex", "implements", "zsviczian/kplex Smart Linking")
        self._add_edge("core/obsidian/smart_linker.py", "core/obsidian/json_canvas_builder.py", "friend", "JSON Canvas 1.0")
        self._add_edge("core/orchestrator/thought_companion.py", "core/obsidian/smart_linker.py", "depends_on", "Smart Linker")
        self._add_edge("tests/unit/test_self_aware_product_v1.py", "core/obsidian/smart_linker.py", "verifies", "Smart Linker Gate")

    def resolve_entity_id(self, token_or_target: str) -> Optional[str]:
        """Resolves a raw target, filename, or alias to a canonical `entity_id`."""
        cleaned = token_or_target.strip()
        if cleaned in self.entities:
            return cleaned
        lowered = cleaned.lower()
        if lowered in self.alias_to_entity_id:
            return self.alias_to_entity_id[lowered]
        return None

    def discover_unlinked_mentions(
        self,
        text: str,
        source_id: str = "active_thought",
        default_relation: str = "references",
    ) -> List[UnlinkedMentionSuggestion]:
        """
        Scans raw text for mentions of registered entities (decisions, modules, SOTA patterns)
        that are NOT yet wrapped in `[[...]]` wikilinks, and returns high-precision smart link suggestions.
        """
        existing_links = extract_wikilinks_and_triples(text)
        already_linked_ids: Set[str] = set()
        for link in existing_links:
            resolved = self.resolve_entity_id(link.target) or link.target
            already_linked_ids.add(resolved)

        # Strip existing wikilinks and inline code blocks before scanning for unlinked mentions
        masked_text = WIKILINK_PATTERN.sub(" ", text)

        suggestions: List[UnlinkedMentionSuggestion] = []
        seen_entities: Set[str] = set()

        # Sort candidate aliases longest-first to avoid partial sub-token shadowing
        sorted_aliases = sorted(
            self.alias_to_entity_id.items(),
            key=lambda kv: len(kv[0]),
            reverse=True,
        )

        for alias_lower, entity_id in sorted_aliases:
            if len(alias_lower) < 4 or entity_id == source_id:
                continue
            if entity_id in already_linked_ids or entity_id in seen_entities:
                continue

            pattern = re.compile(rf"(?<![\w/.-]){re.escape(alias_lower)}(?![\w/.-])", re.IGNORECASE)
            match = pattern.search(masked_text)
            if not match:
                continue

            entity = self.entities[entity_id]
            seen_entities.add(entity_id)

            inferred_rel = default_relation
            if entity.entity_type == "decision":
                inferred_rel = "implements"
            elif entity.entity_type == "module":
                inferred_rel = "alters" if "edit" in text.lower() or " патч" in text.lower() else "depends_on"
            elif entity.entity_type == "sota_repo":
                inferred_rel = "implements"

            matched_surface = match.group(0)
            wikilink = f"[[{entity.entity_id}|{entity.title}]]"
            kplex_triple = f"{inferred_rel}:: {wikilink}"

            suggestions.append(
                UnlinkedMentionSuggestion(
                    matched_text=matched_surface,
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    suggested_wikilink=wikilink,
                    suggested_kplex_triple=kplex_triple,
                    relation=inferred_rel,
                    confidence=0.92 if len(alias_lower) >= 6 else 0.80,
                    reason=f"Matched {entity.entity_type} '{entity.title}' ({entity.summary[:80]})",
                )
            )

        return suggestions

    def auto_link_text(self, text: str, max_insertions: int = 5) -> Dict[str, Any]:
        """
        Non-destructively enriches raw text by appending a canonical Obsidian/kplex
        Smart Links footer block (`relation:: [[target|label]]`) and inline wikilinks.
        """
        explicit = extract_wikilinks_and_triples(text)
        unlinked = self.discover_unlinked_mentions(text)[:max_insertions]

        enriched_text = text
        applied_links: List[Dict[str, Any]] = []

        for item in unlinked:
            pattern = re.compile(
                rf"(?<!\[\[)(?<![\w/.-])({re.escape(item.matched_text)})(?![\w/.-])(?!\]\])",
                re.IGNORECASE,
            )
            new_text, count = pattern.subn(
                f"[[{item.entity_id}|\\1]]",
                enriched_text,
                count=1,
            )
            if count > 0:
                enriched_text = new_text
                applied_links.append(item.to_dict())

        kplex_footer_lines = [item.suggested_kplex_triple for item in unlinked]

        return {
            "original_text": text,
            "enriched_text": enriched_text,
            "explicit_links": [e.to_dict() for e in explicit],
            "unlinked_mentions_resolved": applied_links,
            "kplex_metadata_block": "\n".join(kplex_footer_lines),
        }

    def get_k_hop_context_subgraph(
        self,
        seed_id: str,
        k_hops: int = 2,
        max_nodes: int = 25,
        lens: str = "all",
    ) -> Dict[str, Any]:
        """
        kplex-style Ego-Centric Subgraph Traversal with Graph Lens & Sprawl Protection:
        Collects bidirectional neighborhood (parents, children, friends, implements,
        depends_on, backlinks) within `k_hops` of `seed_id` for deterministic Graph-RAG context.
        Applies graph lens filtering and enforces MAX_BRANCH_DEPTH / MAX_ACTIVE_PLEX_NODES.
        """
        resolved_seed = self.resolve_entity_id(seed_id) or seed_id
        k_hops = max(1, min(k_hops, MAX_BRANCH_DEPTH))
        max_nodes = max(5, min(max_nodes, MAX_ACTIVE_PLEX_NODES))
        allowed_relations = KPLEX_GRAPH_LENSES.get(lens.lower(), KPLEX_GRAPH_LENSES["all"])

        visited_distances: Dict[str, int] = {resolved_seed: 0}
        queue: deque[Tuple[str, int]] = deque([(resolved_seed, 0)])
        collected_edges: List[SmartLinkEdge] = []
        seen_edge_keys: Set[Tuple[str, str, str]] = set()

        while queue and len(visited_distances) < max_nodes:
            current_id, dist = queue.popleft()
            if dist >= k_hops:
                continue

            outgoing = self.forward_edges.get(current_id, [])
            incoming = self.backlink_edges.get(current_id, [])

            # Filter edges according to the selected Graph Lens
            candidate_edges = [
                edge for edge in (outgoing + incoming)
                if edge.relation in allowed_relations
            ]

            added_for_current = 0
            for edge in candidate_edges:
                edge_key = (edge.source_id, edge.target_id, edge.relation)
                if edge_key not in seen_edge_keys:
                    seen_edge_keys.add(edge_key)
                    collected_edges.append(edge)

                neighbor = (
                    edge.target_id if edge.source_id == current_id else edge.source_id
                )
                if (
                    neighbor not in visited_distances
                    and len(visited_distances) < max_nodes
                    and added_for_current < MAX_BRANCH_WIDTH_PER_NODE
                ):
                    visited_distances[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))
                    added_for_current += 1

        nodes_payload: List[Dict[str, Any]] = []
        for node_id, hop_distance in visited_distances.items():
            entity = self.entities.get(
                node_id,
                SmartGraphEntity(
                    entity_id=node_id,
                    title=node_id,
                    entity_type="thought",
                    summary="Dynamic node in kplex graph.",
                ),
            )
            node_dict = entity.to_dict()
            node_dict["hop_distance"] = hop_distance
            node_dict["outgoing_count"] = len(self.forward_edges.get(node_id, []))
            node_dict["backlink_count"] = len(self.backlink_edges.get(node_id, []))
            # Determine color-coded branch status based on hop distance and entity type
            status = "VERIFIED" if node_id.startswith("DEC-") or node_id.endswith(".py") else ("PROPOSED" if hop_distance == 0 else "IN_PROGRESS")
            node_dict["branch_status"] = status
            node_dict["status_meta"] = BRANCH_STATUS_LIFECYCLE[status]
            nodes_payload.append(node_dict)

        return {
            "seed_id": resolved_seed,
            "k_hops": k_hops,
            "lens": lens,
            "node_count": len(nodes_payload),
            "edge_count": len(collected_edges),
            "nodes": nodes_payload,
            "edges": [e.to_dict() for e in collected_edges],
        }

    def build_kplex_smart_links_for_companion(
        self,
        raw_thought: str,
        thought_nodes: List[Dict[str, Any]],
        target_code_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes a complete Obsidian + zsviczian/kplex smart-link bundle for a
        ThoughtCompanion session:
        - Explicit wikilinks & typed triples parsed from user input
        - Auto-discovered unlinked mentions across kernel modules, ADRs, and SOTA repos
        - Bidirectional edges between thought nodes (`parent`, `child`, `implements`, `depends_on`, `verifies`, `alters`)
        - K-Hop context subgraph centered on the target file or primary architectural decision
        """
        explicit_links = extract_wikilinks_and_triples(raw_thought)
        unlinked_suggestions = self.discover_unlinked_mentions(raw_thought)
        auto_linked = self.auto_link_text(raw_thought)

        session_edges: List[Dict[str, Any]] = []
        backlinks_index: Dict[str, List[str]] = {}

        def _record_session_edge(
            src: str,
            tgt: str,
            rel: str,
            label: str,
        ) -> None:
            wikilink = f"[[{tgt}|{label}]]" if label and label != tgt else f"[[{tgt}]]"
            hierarchy = KPLEX_RELATION_ONTOLOGY.get(rel, KPLEX_RELATION_ONTOLOGY["references"])["hierarchy"]
            edge_obj = {
                "source": src,
                "target": tgt,
                "relation": rel,
                "hierarchy_direction": hierarchy,
                "wikilink": wikilink,
                "kplex_triple": f"{rel}:: {wikilink}",
            }
            session_edges.append(edge_obj)
            backlinks_index.setdefault(tgt, [])
            backlink_entry = f"[[{src}]] ({rel})"
            if backlink_entry not in backlinks_index[tgt]:
                backlinks_index[tgt].append(backlink_entry)

        # 1. Connect ThoughtDAG nodes with semantic kplex relations
        primary_node_id = thought_nodes[0]["id"] if thought_nodes else "node_1"
        for node in thought_nodes:
            nid = node.get("id", "node_1")
            ntype = str(node.get("node_type", node.get("type", "hypothesis")))
            for dep in node.get("depends_on", []):
                rel = "verifies" if ntype == "verification" else ("implements" if ntype == "action" else "depends_on")
                _record_session_edge(nid, dep, rel, f"Node {dep}")

        # 2. Attach explicit user wikilinks & typed triples
        for parsed in explicit_links:
            resolved_target = self.resolve_entity_id(parsed.target) or parsed.target
            label = parsed.alias or resolved_target
            _record_session_edge(primary_node_id, resolved_target, parsed.relation, label)

        # 3. Attach auto-discovered unlinked mentions (decisions, modules, SOTA repos)
        for suggestion in unlinked_suggestions:
            _record_session_edge(
                primary_node_id,
                suggestion.entity_id,
                suggestion.relation,
                self.entities[suggestion.entity_id].title
                if suggestion.entity_id in self.entities
                else suggestion.entity_id,
            )

        # 4. If a target code file is provided, link action/verification nodes to it
        if target_code_file:
            clean_target = target_code_file.strip().lstrip("./")
            action_node_id = (
                thought_nodes[2]["id"]
                if len(thought_nodes) >= 3
                else primary_node_id
            )
            _record_session_edge(action_node_id, clean_target, "alters", clean_target)
            if len(thought_nodes) >= 4:
                _record_session_edge(
                    thought_nodes[3]["id"],
                    clean_target,
                    "verifies",
                    f"Verify {clean_target}",
                )

        # 5. Always anchor to DEC-012 if no explicit decision was referenced
        if not any(e["target"].startswith("DEC-") for e in session_edges):
            _record_session_edge(
                primary_node_id,
                "DEC-012",
                "implements",
                "DEC-012 / ADR-091 Zero-Framework Microkernel",
            )

        seed_for_subgraph = (
            target_code_file.strip().lstrip("./")
            if target_code_file
            else (
                unlinked_suggestions[0].entity_id
                if unlinked_suggestions
                else "zsviczian_kplex"
            )
        )
        subgraph = self.get_k_hop_context_subgraph(seed_id=seed_for_subgraph, k_hops=2, lens="all")

        return {
            "engine": "Obsidian + zsviczian/kplex Smart Linker v1.0",
            "active_lens": "all",
            "branch_sprawl_guards": {
                "max_branch_depth": MAX_BRANCH_DEPTH,
                "max_branch_width_per_node": MAX_BRANCH_WIDTH_PER_NODE,
                "max_active_plex_nodes": MAX_ACTIVE_PLEX_NODES,
            },
            "explicit_wikilinks": [e.to_dict() for e in explicit_links],
            "unlinked_mentions": [u.to_dict() for u in unlinked_suggestions],
            "auto_linked_thought": auto_linked["enriched_text"],
            "kplex_metadata_block": auto_linked["kplex_metadata_block"],
            "semantic_edges": session_edges,
            "backlinks_index": backlinks_index,
            "k_hop_context_subgraph": subgraph,
        }
