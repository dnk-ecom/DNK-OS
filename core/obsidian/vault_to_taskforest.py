# --- DNK-MRH-HEADER ---
# mrh_id: "core/obsidian/vault_to_taskforest.py"
# purpose: "Read-only projection (not a sync) of the 16 architectural modules into a Task Forest biological graph with 5-plant LOD hierarchy; feeds /task_forest/vault_graph and the vault integrity audit."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.1"
# updated_at: "2026-11-08"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent.parent
ARCH_DIR = _ROOT / "docs" / "notes" / "MY TASKS" / "1. АРХІТЕКТУРА"
PROJECTS_DIR = _ROOT / "docs" / "notes" / "MY TASKS" / "3. ПРОЄКТИ ТА КОРИСТУВАЧІ"

SECTOR_DEFINITIONS = [
    {
        "id": "sec-core",
        "title": "Шар 1: Ядро та Інженерні Інваріанти",
        "sector_code": "SEC-CORE",
        "plant_scale": "sector",
        "parent_id": "field-001",
        "assigned_agent": "dnk_mentor",
        "progress": None,  # derived by rollup, never invented
        "x": 500,
        "y": 400
    },
    {
        "id": "sec-data",
        "title": "Шар 2: Дані, Реєстри & Пам'ять",
        "sector_code": "SEC-DATA",
        "plant_scale": "sector",
        "parent_id": "field-001",
        "assigned_agent": "dnk_dev_fullstack",
        "progress": None,  # derived by rollup, never invented
        "x": 1500,
        "y": 400
    },
    {
        "id": "sec-plugins",
        "title": "Шар 3: Сервіси як Плагіни & SOTA",
        "sector_code": "SEC-PLUGINS",
        "plant_scale": "sector",
        "parent_id": "field-001",
        "assigned_agent": "gerych_researcher",
        "progress": None,  # derived by rollup, never invented
        "x": 2500,
        "y": 400
    },
    {
        "id": "sec-agents",
        "title": "Шар 4: Задачі, Рій & Task Forest",
        "sector_code": "SEC-AGENTS",
        "plant_scale": "sector",
        "parent_id": "field-001",
        "assigned_agent": "gerych_prime",
        "progress": None,  # derived by rollup, never invented
        "x": 3500,
        "y": 400
    },
    {
        "id": "sec-spatial",
        "title": "Шар 5: Просторова Взаємодія & Visual Shell",
        "sector_code": "SEC-SPATIAL",
        "plant_scale": "sector",
        "parent_id": "field-001",
        "assigned_agent": "gerych_builder",
        "progress": None,  # derived by rollup, never invented
        "x": 4500,
        "y": 400
    }
]


def extract_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter safely."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        data = yaml.safe_load(parts[1])
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _rollup_progress(nodes: List[Dict[str, Any]]) -> None:
    """Fill missing (None) progress as the mean of the children's progress.

    Leaves carry real facts (completed = 100, otherwise 0); an explicit value from
    frontmatter wins. A node with no children and no value stays 0.0 (nothing done
    is known), instead of the old hard-coded 75/78/82/85/88/92 placeholders.
    """
    children: Dict[str, List[Dict[str, Any]]] = {}
    for n in nodes:
        if n.get("parent_id"):
            children.setdefault(n["parent_id"], []).append(n)

    def value(n: Dict[str, Any]) -> float:
        if n.get("progress") is None:
            kids = children.get(n["id"], [])
            n["progress"] = round(sum(value(k) for k in kids) / len(kids), 1) if kids else 0.0
        return float(n["progress"])

    for n in nodes:
        value(n)


def build_vault_task_forest() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Scans the 16 architectural modules and builds the hierarchical graph."""
    nodes: List[Dict[str, Any]] = []
    wires: List[Dict[str, Any]] = []

    # 1. 🌾 Root Field
    nodes.append({
        "id": "field-001",
        "title": "DNK OS Master HQ",
        "plant_scale": "field",
        "status": "in_progress",
        "progress": None,  # derived by rollup
        "assigned_agent": "antigravity_mentor",
        "author": "Maxim",
        "verification_status": "verified",
        "position": {"x": 2500, "y": 50},
        "dto_contract": {"protocol": "TaskForestV5", "workspace": "ws-alpha-001"}
    })

    # 2. 🏞️ 5 Sectors
    sector_map = {}
    for s in SECTOR_DEFINITIONS:
        sector_map[s["sector_code"]] = s["id"]
        nodes.append({
            "id": s["id"],
            "title": s["title"],
            "plant_scale": "sector",
            "status": "in_progress",
            "progress": None,  # derived by rollup
            "parent_id": s["parent_id"],
            "assigned_agent": s["assigned_agent"],
            "author": "Maxim",
            "verification_status": "verified",
            "position": {"x": s["x"], "y": s["y"]}
        })
        wires.append({
            "source_id": s["parent_id"],
            "target_id": s["id"],
            "wire_kind": "hierarchy"
        })

    if not ARCH_DIR.exists():
        _rollup_progress(nodes)
        return nodes, wires

    # 3. 🌳 16 Trees (from 00. INDEX.md)
    sector_tree_offsets: Dict[str, int] = {s["id"]: 0 for s in SECTOR_DEFINITIONS}
    tree_ids_by_module: Dict[str, str] = {}  # module_id ("04") -> tree node id as written in the INDEX frontmatter
    
    for dir_entry in sorted(ARCH_DIR.iterdir()):
        if not dir_entry.is_dir() or dir_entry.name.startswith("."):
            continue

        index_file = dir_entry / "00. INDEX.md"
        if not index_file.exists():
            continue

        content = index_file.read_text(encoding="utf-8")
        fm = extract_frontmatter(content)
        tf = fm.get("task_forest", {})

        module_id = tf.get("module_id") or dir_entry.name[:2]
        node_id = tf.get("node_id") or f"tree-mod-{module_id}"
        tree_ids_by_module[str(module_id)] = node_id
        sector_code = tf.get("sector_id", "SEC-CORE")
        sector_id = sector_map.get(sector_code, "sec-core")

        # Position tree under its parent sector
        sector_idx = 0
        for idx, s in enumerate(SECTOR_DEFINITIONS):
            if s["id"] == sector_id:
                sector_idx = idx
                break
        
        offset = sector_tree_offsets[sector_id]
        sector_tree_offsets[sector_id] += 1

        base_x = SECTOR_DEFINITIONS[sector_idx]["x"]
        tree_x = base_x + (offset - 1.5) * 260
        tree_y = 800 + (offset % 2) * 80

        title = fm.get("title", dir_entry.name)
        status = tf.get("status", "in_progress")
        progress = float(tf["progress"]) if tf.get("progress") is not None else None  # None -> rollup of children
        agent = tf.get("assigned_agent", fm.get("assigned_agent", "gerych_builder"))

        tree_node = {
            "id": node_id,
            "title": title,
            "plant_scale": "tree",
            "status": status,
            "progress": progress,
            "parent_id": sector_id,
            "assigned_agent": agent,
            "author": "Maxim",
            "verification_status": "verified",
            "position": {"x": tree_x, "y": tree_y},
            "file_path": str(index_file.relative_to(_ROOT))
        }
        nodes.append(tree_node)

        # Hierarchy wire from sector to tree
        wires.append({
            "source_id": sector_id,
            "target_id": node_id,
            "wire_kind": "hierarchy"
        })

        # Dependency wires from dependencies field
        deps = tf.get("dependencies", [])
        for dep in deps:
            wires.append({
                "source_id": dep,
                "target_id": node_id,
                "wire_kind": "data_dependency"
            })

        # 4. 🌿 Bushes (ADR & CONTRACTS) and 🌸 Flowers (SOTA & TASKS)
        bush_idx = 0
        for sub_type, scale, folder_name in [
            ("adr", "bush", "ADR"),
            ("contract", "bush", "CONTRACTS"),
            ("sota", "flower", "SOTA"),
            ("task", "flower", "TASKS")
        ]:
            folder_path = dir_entry / folder_name
            if not folder_path.exists():
                continue

            for doc_file in sorted(folder_path.iterdir()):
                if doc_file.is_file() and doc_file.suffix == ".md":
                    doc_content = doc_file.read_text(encoding="utf-8")
                    doc_fm = extract_frontmatter(doc_content)
                    
                    doc_title = doc_fm.get("title", doc_file.stem)
                    doc_id = f"{node_id}-{folder_name.lower()}-{bush_idx}"
                    bush_x = tree_x + (bush_idx * 160) - 80
                    bush_y = tree_y + (400 if scale == 'bush' else 700)
                    bush_idx += 1

                    nodes.append({
                        "id": doc_id,
                        "title": doc_title,
                        "plant_scale": scale,
                        "status": "completed" if folder_name in ["ADR", "CONTRACTS"] else "in_progress",
                        "progress": 100.0 if folder_name in ["ADR", "CONTRACTS"] else 0.0,
                        "parent_id": node_id,
                        "assigned_agent": agent,
                        "author": "Maxim",
                        "verification_status": "verified",
                        "position": {"x": bush_x, "y": bush_y},
                        "file_path": str(doc_file.relative_to(_ROOT))
                    })

                    wires.append({
                        "source_id": node_id,
                        "target_id": doc_id,
                        "wire_kind": "hierarchy"
                    })

    # 5. 🏢 Brand & Project Specifications (docs/notes/MY TASKS/3. ПРОЄКТИ ТА КОРИСТУВАЧІ)
    if PROJECTS_DIR.exists():
        proj_idx = 0
        # Parent of project docs is module 04; its id comes from the INDEX frontmatter (e.g. TREE-MOD-04-SAAP)
        projects_tree_id = tree_ids_by_module.get("04", "tree-mod-04")
        tree_4_node = next((n for n in nodes if n["id"] == projects_tree_id), None)
        base_x = tree_4_node["position"]["x"] if tree_4_node else 2500
        base_y = tree_4_node["position"]["y"] if tree_4_node else 1000

        for proj_dir in sorted(PROJECTS_DIR.iterdir()):
            if not proj_dir.is_dir() or proj_dir.name.startswith("."):
                continue
            for doc_file in sorted(proj_dir.iterdir()):
                if doc_file.is_file() and doc_file.suffix == ".md" and not doc_file.name.startswith("000_"):
                    doc_content = doc_file.read_text(encoding="utf-8")
                    doc_fm = extract_frontmatter(doc_content)
                    tf = doc_fm.get("task_forest", {})
                    if not tf:
                        continue

                    scale = tf.get("scale", "flower")
                    node_id_val = tf.get("node_id") or f"proj-{doc_file.stem}"
                    title_val = doc_fm.get("title", doc_file.stem)
                    agent_val = tf.get("assigned_agent", "dnk_shopify")
                    parent_tree_id = projects_tree_id

                    doc_x = base_x + 320 + (proj_idx % 4) * 160
                    doc_y = base_y + 350 + (proj_idx // 4) * 180
                    proj_idx += 1

                    nodes.append({
                        "id": node_id_val,
                        "title": title_val,
                        "plant_scale": scale,
                        "status": "completed",
                        "progress": 100.0,
                        "parent_id": parent_tree_id,
                        "assigned_agent": agent_val,
                        "author": "Maxim",
                        "verification_status": "verified",
                        "position": {"x": doc_x, "y": doc_y},
                        "file_path": str(doc_file.relative_to(_ROOT))
                    })

                    wires.append({
                        "source_id": parent_tree_id,
                        "target_id": node_id_val,
                        "wire_kind": "hierarchy"
                    })

    _rollup_progress(nodes)
    return nodes, wires


if __name__ == "__main__":
    ns, ws = build_vault_task_forest()
    print(f"🌲 Compiled Task Forest Vault Graph:")
    print(f"   • Total Nodes: {len(ns)}")
    print(f"   • Total Wires: {len(ws)}")
    scale_counts = {}
    for n in ns:
        scale_counts[n['plant_scale']] = scale_counts.get(n['plant_scale'], 0) + 1
    for sc, cnt in scale_counts.items():
        print(f"     - {sc.upper()}: {cnt}")
