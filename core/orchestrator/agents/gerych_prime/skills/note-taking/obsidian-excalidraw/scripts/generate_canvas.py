#!/usr/bin/env python3
"""
Generate Obsidian JSON Canvas (.canvas) files.
Conforms to the open JSON Canvas specification (https://jsoncanvas.org).
"""
import json
import random
from typing import List, Dict, Any, Optional

def make_id(prefix: str = "node") -> str:
    return f"{prefix}_{random.randint(100000, 999999)}"

class CanvasBuilder:
    def __init__(self):
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []

    def add_text_node(
        self,
        text: str,
        x: float,
        y: float,
        width: float = 260,
        height: float = 140,
        color: Optional[str] = None
    ) -> str:
        node_id = make_id("txt")
        node = {
            "id": node_id,
            "type": "text",
            "text": text,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        if color:
            node["color"] = color  # "1"=red, "2"=orange, "3"=yellow, "4"=green, "5"=cyan, "6"=purple
        self.nodes.append(node)
        return node_id

    def add_file_node(
        self,
        file_path: str,
        x: float,
        y: float,
        width: float = 350,
        height: float = 300,
        subpath: Optional[str] = None,
        color: Optional[str] = None
    ) -> str:
        node_id = make_id("file")
        node = {
            "id": node_id,
            "type": "file",
            "file": file_path,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        if subpath:
            node["subpath"] = subpath
        if color:
            node["color"] = color
        self.nodes.append(node)
        return node_id

    def add_group_node(
        self,
        label: str,
        x: float,
        y: float,
        width: float,
        height: float,
        color: Optional[str] = None
    ) -> str:
        node_id = make_id("group")
        node = {
            "id": node_id,
            "type": "group",
            "label": label,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        if color:
            node["color"] = color
        self.nodes.append(node)
        return node_id

    def add_edge(
        self,
        from_node: str,
        to_node: str,
        label: Optional[str] = None,
        from_side: str = "right",
        to_side: str = "left",
        color: Optional[str] = None
    ) -> str:
        edge_id = make_id("edge")
        edge = {
            "id": edge_id,
            "fromNode": from_node,
            "fromSide": from_side,
            "toNode": to_node,
            "toSide": to_side
        }
        if label:
            edge["label"] = label
        if color:
            edge["color"] = color
        self.edges.append(edge)
        return edge_id

    def build_json(self) -> str:
        data = {
            "nodes": self.nodes,
            "edges": self.edges
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
