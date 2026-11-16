# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/capability_graph.py"
# purpose: "DNK OS Plugin Capability Graph MVP Engine v0.1"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml
from pydantic import BaseModel, Field, field_validator


def is_relative_path(path: Optional[str]) -> bool:
    """Check if a path is strictly relative and contains no unsafe escapes."""
    if not path or not isinstance(path, str):
        return False
    if os.path.isabs(path):
        return False
    if path.startswith("/") or path.startswith("\\") or path.startswith("~"):
        return False
    norm = os.path.normpath(path)
    if norm == ".." or norm.startswith("../") or norm.startswith("..\\"):
        return False
    return True


def validate_capability_name(capability: str) -> str:
    """Validate capability name format. Disallow wildcards in MVP."""
    if not isinstance(capability, str) or not capability.strip():
        raise ValueError("Capability name must be a non-empty string")
    cap = capability.strip()
    if "*" in cap or "?" in cap:
        raise ValueError(f"Wildcard capability '{cap}' is forbidden in MVP")
    return cap


class CapabilityNode(BaseModel):
    """Node in the capability graph representing a capability associated with a plugin."""

    plugin_id: str
    capability: str

    @field_validator("capability")
    @classmethod
    def check_capability(cls, v: str) -> str:
        return validate_capability_name(v)


class CapabilityEdge(BaseModel):
    """Directed edge in the capability graph: from_plugin provides capability to to_plugin."""

    from_plugin: str
    from_capability: str
    to_plugin: str
    to_capability: str

    @field_validator("from_capability")
    @classmethod
    def check_from_cap(cls, v: str) -> str:
        return validate_capability_name(v)

    @field_validator("to_capability")
    @classmethod
    def check_to_cap(cls, v: str) -> str:
        return validate_capability_name(v)

    @field_validator("to_plugin")
    @classmethod
    def check_no_self_edge(cls, v: str, info: Any) -> str:
        from_p = info.data.get("from_plugin")
        if from_p and from_p == v:
            raise ValueError(f"Self-edges forbidden: '{from_p}' cannot link to itself")
        return v


class CapabilityGraph(BaseModel):
    """Complete capability graph representation."""

    schema_version: str = "dnk-capability-graph/v1.0"
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    nodes: List[CapabilityNode] = Field(default_factory=list)
    edges: List[CapabilityEdge] = Field(default_factory=list)


class PluginCapabilityGraph:
    """Engine for building, analyzing, and querying plugin capability graphs."""

    def __init__(
        self,
        index_path: str = "core/templates/plugin/plugins_index.json",
        output_path: str = "core/templates/plugin/capability_graph.json",
    ):
        if not is_relative_path(index_path):
            raise ValueError(f"Index path must be relative: {index_path}")
        if not is_relative_path(output_path):
            raise ValueError(f"Output path must be relative: {output_path}")

        norm_index = os.path.normpath(index_path)
        if not os.path.exists(norm_index) and os.path.exists(os.path.join("core", norm_index)):
            norm_index = os.path.normpath(os.path.join("core", norm_index))
        self.index_path = norm_index

        norm_output = os.path.normpath(output_path)
        if not os.path.exists(norm_output) and os.path.exists(os.path.join("core", norm_output)):
            norm_output = os.path.normpath(os.path.join("core", norm_output))
        self.output_path = norm_output

    def build_from_cards(self, cards: List[Dict[str, Any]]) -> CapabilityGraph:
        """Build CapabilityGraph in-memory from a list of parsed plugin card dictionaries."""
        raw_nodes: Set[Tuple[str, str]] = set()
        provides_map: Dict[str, List[str]] = {}
        requires_map: Dict[str, List[str]] = {}

        for card in cards:
            if not isinstance(card, dict):
                continue
            plugin_id = card.get("id") or card.get("plugin_id")
            if not plugin_id or not isinstance(plugin_id, str):
                continue

            caps = card.get("capabilities") or {}
            if not isinstance(caps, dict):
                continue

            provides = caps.get("provides") or []
            requires = caps.get("requires") or []

            if not isinstance(provides, list):
                provides = []
            if not isinstance(requires, list):
                requires = []

            for p in provides:
                if not isinstance(p, str):
                    continue
                valid_p = validate_capability_name(p)
                raw_nodes.add((plugin_id, valid_p))
                provides_map.setdefault(valid_p, []).append(plugin_id)

            for r in requires:
                if not isinstance(r, str):
                    continue
                valid_r = validate_capability_name(r)
                raw_nodes.add((plugin_id, valid_r))
                requires_map.setdefault(plugin_id, []).append(valid_r)

        # Construct sorted nodes
        nodes = [
            CapabilityNode(plugin_id=pid, capability=cap)
            for pid, cap in sorted(raw_nodes, key=lambda x: (x[0], x[1]))
        ]

        # Construct edges: from_plugin (provider) -> to_plugin (consumer)
        raw_edges: Set[Tuple[str, str, str, str]] = set()
        for consumer_id, req_caps in requires_map.items():
            for req_cap in req_caps:
                providers = provides_map.get(req_cap, [])
                for provider_id in providers:
                    if provider_id != consumer_id:
                        raw_edges.add((provider_id, req_cap, consumer_id, req_cap))

        edges = [
            CapabilityEdge(
                from_plugin=fp,
                from_capability=fc,
                to_plugin=tp,
                to_capability=tc,
            )
            for fp, fc, tp, tc in sorted(raw_edges, key=lambda x: (x[0], x[2], x[1]))
        ]

        return CapabilityGraph(nodes=nodes, edges=edges)

    def build_from_index(self, index_path: Optional[str] = None) -> CapabilityGraph:
        """Alias for build(). Build CapabilityGraph from plugins_index.json."""
        return self.build(index_path=index_path)

    def build(self, index_path: Optional[str] = None) -> CapabilityGraph:
        """Build CapabilityGraph from plugins_index.json and card files."""
        target_index = index_path or self.index_path
        if not is_relative_path(target_index):
            raise ValueError(f"Index path must be relative: {target_index}")

        if not os.path.exists(target_index) and os.path.exists(os.path.join("core", target_index)):
            target_index = os.path.normpath(os.path.join("core", target_index))

        if not os.path.exists(target_index):
            raise FileNotFoundError(f"Plugin index file not found: {target_index}")

        with open(target_index, "r", encoding="utf-8") as f:
            index_data = json.load(f)

        entries = index_data.get("entries", [])
        cards: List[Dict[str, Any]] = []

        for entry in entries:
            card_path = entry.get("card_path")
            if not card_path or not is_relative_path(card_path):
                continue
            if not os.path.exists(card_path) and os.path.exists(os.path.join("core", card_path)):
                card_path = os.path.normpath(os.path.join("core", card_path))
            if not os.path.exists(card_path):
                continue

            try:
                with open(card_path, "r", encoding="utf-8") as cf:
                    card_dict = yaml.safe_load(cf)
                    if isinstance(card_dict, dict):
                        cards.append(card_dict)
            except Exception:
                continue

        return self.build_from_cards(cards)

    def save_graph(
        self, graph: CapabilityGraph, output_path: Optional[str] = None
    ) -> str:
        """Persist CapabilityGraph to disk as formatted JSON."""
        target_output = output_path or self.output_path
        if not is_relative_path(target_output):
            raise ValueError(f"Output path must be relative: {target_output}")

        os.makedirs(os.path.dirname(target_output) or ".", exist_ok=True)
        with open(target_output, "w", encoding="utf-8") as f:
            f.write(graph.model_dump_json(indent=2))
            f.write("\n")
        return target_output

    def load_graph(self, path: Optional[str] = None) -> CapabilityGraph:
        """Load CapabilityGraph from JSON file."""
        target_path = path or self.output_path
        if not is_relative_path(target_path):
            raise ValueError(f"Path must be relative: {target_path}")

        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Capability graph file not found: {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return CapabilityGraph.model_validate(data)

    def get_dependencies(
        self,
        plugin_id: str,
        graph: Optional[CapabilityGraph] = None,
        index_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze incoming and outgoing capability dependencies for a given plugin."""
        target_graph = graph or self.load_graph()

        # Find all nodes for this plugin
        plugin_nodes = [n for n in target_graph.nodes if n.plugin_id == plugin_id]

        # Try to retrieve exact provides and requires from plugin card via index
        card_provides: List[str] = []
        card_requires: List[str] = []
        card_found = False

        target_index = index_path or self.index_path
        if is_relative_path(target_index) and os.path.exists(target_index):
            try:
                with open(target_index, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
                for entry in index_data.get("entries", []):
                    if entry.get("plugin_id") == plugin_id or entry.get("id") == plugin_id:
                        card_path = entry.get("card_path")
                        if card_path and is_relative_path(card_path) and os.path.exists(card_path):
                            with open(card_path, "r", encoding="utf-8") as cf:
                                cdata = yaml.safe_load(cf) or {}
                                caps = cdata.get("capabilities") or {}
                                card_provides = caps.get("provides") or []
                                card_requires = caps.get("requires") or []
                                card_found = True
                        break
            except Exception:
                pass

        # Incoming edges: other plugins provide capabilities that plugin_id requires
        edges_in = [e for e in target_graph.edges if e.to_plugin == plugin_id]
        # Outgoing edges: plugin_id provides capabilities to other plugins
        edges_out = [e for e in target_graph.edges if e.from_plugin == plugin_id]

        incoming_providers: Dict[str, List[str]] = {}
        for edge in edges_in:
            incoming_providers.setdefault(edge.to_capability, []).append(edge.from_plugin)

        outgoing_consumers: Dict[str, List[str]] = {}
        for edge in edges_out:
            outgoing_consumers.setdefault(edge.from_capability, []).append(edge.to_plugin)

        # If card was not found, fallback to inferred provides/requires
        if card_found:
            provides = card_provides
            requires = card_requires
        else:
            provides = sorted(
                list(
                    set(
                        [e.from_capability for e in edges_out]
                        + [n.capability for n in plugin_nodes if n.capability in outgoing_consumers]
                    )
                )
            )
            requires = sorted(
                list(
                    set(
                        [e.to_capability for e in edges_in]
                        + [n.capability for n in plugin_nodes if n.capability in incoming_providers]
                    )
                )
            )
            if not provides and not requires and plugin_nodes:
                # If only nodes exist without edges, populate provides with node capabilities
                provides = sorted(list(set(n.capability for n in plugin_nodes)))

        unresolved_requirements = [r for r in requires if r not in incoming_providers]

        return {
            "plugin_id": plugin_id,
            "provides": provides,
            "requires": requires,
            "incoming_providers": incoming_providers,
            "outgoing_consumers": outgoing_consumers,
            "edges_in": edges_in,
            "edges_out": edges_out,
            "unresolved_requirements": unresolved_requirements,
            "nodes": plugin_nodes,
        }
