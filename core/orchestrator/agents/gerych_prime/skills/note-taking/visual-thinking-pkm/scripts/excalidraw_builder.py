#!/usr/bin/env python3
"""
--- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/note-taking/visual-thinking-pkm/scripts/excalidraw_builder.py"
purpose: "Reusable SOTA Excalidraw Builder implementing architecture-diagram, baoyu-infographic, and popular-web-designs standards."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-09-09"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER ---
"""

import json
import random
import string
from typing import List, Dict, Any, Optional

try:
    import lzstring
except ImportError:
    lzstring = None


def generate_id(prefix: str = "el_") -> str:
    chars = string.ascii_letters + string.digits
    return f"{prefix}{''.join(random.choice(chars) for _ in range(12))}"


class SotaExcalidrawBuilder:
    """Builder for professional, executive-grade dark-themed Excalidraw diagrams."""

    def __init__(self, bg_color: str = "#090d16"):
        self.elements: List[Dict[str, Any]] = []
        self.bg_color = bg_color

    def add_shape(
        self,
        shape_type: str,
        x: float,
        y: float,
        width: float,
        height: float,
        label: Optional[str] = None,
        bg_color: str = "transparent",
        stroke_color: str = "#334155",
        stroke_width: int = 1,
        fill_style: str = "solid",
        roundness: Optional[int] = 3,
        font_size: int = 16,
        font_family: int = 5,  # Excalifont for Cyrillic
        text_color: str = "#f8fafc",
        text_align: str = "center",
        vertical_align: str = "middle",
        stroke_style: str = "solid"
    ) -> str:
        shape_id = generate_id("shp_")
        bound_elements = []

        if label:
            text_id = generate_id("txt_")
            bound_elements.append({"id": text_id, "type": "text"})

        element = {
            "id": shape_id,
            "type": shape_type,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": bg_color,
            "fillStyle": fill_style,
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": roundness} if roundness is not None else None,
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": random.randint(100000, 999999),
            "isDeleted": False,
            "boundElements": bound_elements,
            "updated": 1725890000000,
            "link": None,
            "locked": False
        }
        self.elements.append(element)

        if label:
            text_element = {
                "id": text_id,
                "type": "text",
                "x": x + 10,
                "y": y + (height - (font_size * 1.35 * len(label.split("\n")))) / 2,
                "width": max(10.0, width - 20),
                "height": font_size * 1.35 * len(label.split("\n")),
                "angle": 0,
                "strokeColor": text_color,
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "groupIds": [],
                "frameId": None,
                "roundness": None,
                "seed": random.randint(10000, 99999),
                "version": 1,
                "versionNonce": random.randint(100000, 999999),
                "isDeleted": False,
                "boundElements": None,
                "updated": 1725890000000,
                "link": None,
                "locked": False,
                "text": label,
                "fontSize": font_size,
                "fontFamily": font_family,
                "textAlign": text_align,
                "verticalAlign": vertical_align,
                "baseline": font_size,
                "containerId": shape_id,
                "originalText": label,
                "lineHeight": 1.35
            }
            self.elements.append(text_element)

        return shape_id

    def add_arrow(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        stroke_color: str = "#06b6d4",
        stroke_width: int = 2,
        stroke_style: str = "solid",
        label: Optional[str] = None,
        font_size: int = 14
    ) -> str:
        arrow_id = generate_id("arr_")
        dx = end_x - start_x
        dy = end_y - start_y
        element = {
            "id": arrow_id,
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": abs(dx) or 1,
            "height": abs(dy) or 1,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": random.randint(100000, 999999),
            "isDeleted": False,
            "boundElements": None,
            "updated": 1725890000000,
            "link": None,
            "locked": False,
            "points": [[0, 0], [dx, dy]],
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow"
        }
        self.elements.append(element)
        return arrow_id

    def build_raw_json(self) -> Dict[str, Any]:
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {
                "gridSize": None,
                "viewBackgroundColor": self.bg_color,
                "theme": "dark",
                "currentItemFontFamily": 5
            },
            "files": {}
        }

    def build_markdown(self, markdown_header: str = "") -> str:
        raw_json = self.build_raw_json()
        json_str = json.dumps(raw_json, ensure_ascii=False)

        if lzstring is not None:
            compressed = lzstring.LZString().compressToBase64(json_str)
        else:
            compressed = ""

        text_elements_md = []
        for el in self.elements:
            if el.get("type") == "text":
                text_elements_md.append(f"{el.get('text')} ^block_{el.get('id')}")

        texts_section = "\n\n".join(text_elements_md)

        return f"""---
excalidraw-plugin: parsed
tags:
  - excalidraw
---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

{markdown_header}

# Excalidraw Data
## Text Elements
{texts_section}

## Element Data
```compressed-json
{compressed}
```
"""
