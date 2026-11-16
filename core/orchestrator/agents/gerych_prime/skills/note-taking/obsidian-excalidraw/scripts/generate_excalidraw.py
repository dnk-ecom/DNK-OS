#!/usr/bin/env python3
"""
Generate Obsidian Excalidraw Hybrid Markdown (.excalidraw.md) files.
Supports nodes, shapes, container-bound labels, arrows, and Obsidian [[wikilinks]].
"""
import json
import random
import sys
from typing import List, Dict, Any, Optional

def make_seed() -> int:
    return random.randint(100000000, 999999999)

class ExcalidrawBuilder:
    def __init__(self, bg_color: str = "#ffffff"):
        self.elements: List[Dict[str, Any]] = []
        self.bg_color = bg_color
        self._next_id = 1

    def _gen_id(self, prefix: str = "elem") -> str:
        elem_id = f"{prefix}_{self._next_id}_{random.randint(1000, 9999)}"
        self._next_id += 1
        return elem_id

    def add_shape(
        self,
        shape_type: str,
        x: float,
        y: float,
        width: float,
        height: float,
        label: Optional[str] = None,
        link: Optional[str] = None,
        bg_color: str = "transparent",
        stroke_color: str = "#1e1e1e",
        stroke_width: int = 2,
        roundness: int = 3,
        font_size: int = 16,
    ) -> str:
        shape_id = self._gen_id(shape_type)
        bound_elements = []
        text_id = None

        if label:
            text_id = self._gen_id("txt")
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
            "fillStyle": "solid" if bg_color != "transparent" else "hachure",
            "strokeWidth": stroke_width,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": roundness} if roundness else None,
            "seed": make_seed(),
            "version": 1,
            "versionNonce": make_seed(),
            "isDeleted": False,
            "boundElements": bound_elements,
            "updated": 1750000000000,
            "link": link,
            "locked": False
        }
        self.elements.append(element)

        if label and text_id:
            text_element = {
                "id": text_id,
                "type": "text",
                "x": x + 10,
                "y": y + (height / 2) - (font_size / 2) - 4,
                "width": max(10, width - 20),
                "height": font_size + 8,
                "angle": 0,
                "strokeColor": stroke_color,
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": [],
                "frameId": None,
                "roundness": None,
                "seed": make_seed(),
                "version": 1,
                "versionNonce": make_seed(),
                "isDeleted": False,
                "boundElements": None,
                "updated": 1750000000000,
                "link": None,
                "locked": False,
                "text": label,
                "fontSize": font_size,
                "fontFamily": 1,
                "textAlign": "center",
                "verticalAlign": "middle",
                "baseline": font_size,
                "containerId": shape_id,
                "originalText": label,
                "lineHeight": 1.25,
                "autoResize": True
            }
            self.elements.append(text_element)

        return shape_id

    def add_arrow(
        self,
        from_id: str,
        to_id: str,
        label: Optional[str] = None,
        stroke_color: str = "#1e1e1e",
        stroke_width: int = 2
    ) -> str:
        from_elem = next((e for e in self.elements if e["id"] == from_id), None)
        to_elem = next((e for e in self.elements if e["id"] == to_id), None)
        if not from_elem or not to_elem:
            raise ValueError(f"Target elements {from_id} or {to_id} not found")

        start_x = from_elem["x"] + from_elem["width"]
        start_y = from_elem["y"] + (from_elem["height"] / 2)
        end_x = to_elem["x"]
        end_y = to_elem["y"] + (to_elem["height"] / 2)
        dx = end_x - start_x
        dy = end_y - start_y

        arrow_id = self._gen_id("arrow")
        arrow = {
            "id": arrow_id,
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": abs(dx),
            "height": abs(dy),
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": make_seed(),
            "version": 1,
            "versionNonce": make_seed(),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1750000000000,
            "link": None,
            "locked": False,
            "points": [[0, 0], [dx, dy]],
            "lastCommittedPoint": None,
            "startBinding": {"elementId": from_id, "focus": 0.1, "gap": 6},
            "endBinding": {"elementId": to_id, "focus": -0.1, "gap": 6},
            "startArrowhead": None,
            "endArrowhead": "arrow"
        }
        self.elements.append(arrow)

        # Update bindings on connected shapes
        if from_elem.get("boundElements") is None:
            from_elem["boundElements"] = []
        from_elem["boundElements"].append({"id": arrow_id, "type": "arrow"})
        if to_elem.get("boundElements") is None:
            to_elem["boundElements"] = []
        to_elem["boundElements"].append({"id": arrow_id, "type": "arrow"})

        return arrow_id

    def build_markdown(self) -> str:
        excalidraw_data = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
            "elements": self.elements,
            "appState": {
                "gridSize": None,
                "viewBackgroundColor": self.bg_color
            },
            "files": {}
        }
        json_str = json.dumps(excalidraw_data, indent=2, ensure_ascii=False)

        md = f"""---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

# Excalidraw Data
## Text Elements
%%
## Drawing
```json
{json_str}
```
%%
"""
        return md
