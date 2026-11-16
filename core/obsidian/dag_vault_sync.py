# --- DNK-MRH-HEADER ---
# mrh_id: "core/obsidian/dag_vault_sync.py"
# purpose: "Canonical Obsidian note <-> ThoughtDAG v2 node sync (one implementation replacing task_forest_sync and the import engine of obsidian_sync_engine; vault_to_taskforest stays a separate read-only projection)."
# canonical_source: true
# alters_files: [".data/thoughtdag_v2/*"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-08"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Canon vault sync (untangle D1.3a).

Reads both legacy note dialects (Task Forest: ``type``/``stage``/``dependencies``; Node Tasks:
``node_type``/``stage``/``status``/``progress``/``upstream_dependencies``, checkbox acceptance
criteria, canvas position marker) into ``ThoughtNode`` + ``DEPENDENCY`` wires, and renders nodes
back to the same frontmatter keys, so existing notes keep working unchanged.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from core.canvas.node_canvas_core import CycleDetectedError
from core.domain.dag_converters import _priority, kind_scale_for_type
from core.domain.dag_models import (
    NodeKind,
    NodeStatus,
    TaskSpec,
    ThoughtNode,
    Wire,
    WireType,
    normalize_status,
)

_EPHEMERAL_TAGS = {"micro_step", "dialogue_turn", "ephemeral", "chat_step"}
_SKIP_NAMES = {"readme.md", "index.md"}


# --- parsing ---------------------------------------------------------------------------------


def _split_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Frontmatter + body. Skips leading DNK-MRH headers (comment or HTML form); when the YAML is
    malformed, recovers `key: value` lines heuristically instead of dropping the note."""
    clean: List[str] = []
    in_mrh = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# --- DNK-MRH-HEADER ---") or stripped.startswith("<!-- --- DNK-MRH-HEADER ---"):
            in_mrh = True
            continue
        if in_mrh:
            if stripped.endswith("--- END DNK-MRH-HEADER ---") or stripped.endswith("--- END DNK-MRH-HEADER -->"):
                in_mrh = False
            continue
        clean.append(line)

    start = end = None
    for idx, line in enumerate(clean):
        if line.strip() == "---":
            if start is None:
                start = idx
            else:
                end = idx
                break
    if start is None or end is None:
        return {}, "\n".join(clean)

    yaml_text = "\n".join(clean[start + 1:end])
    body = "\n".join(clean[end + 1:])
    try:
        data = yaml.safe_load(yaml_text) or {}
        if isinstance(data, dict):
            return data, body
    except yaml.YAMLError:
        pass
    recovered: Dict[str, Any] = {}
    for yline in yaml_text.splitlines():
        m = re.match(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$", yline.strip())
        if m:
            v = m.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            recovered[m.group(1)] = v
    return recovered, body


def _wikilinks(raw: Any) -> List[str]:
    """Normalise `[[a|alias]]`, `[[a#h]]`, plain strings and comma lists to a de-duplicated id list."""
    items: List[str] = []
    if isinstance(raw, str):
        items = [x for x in re.split(r"[,\n]", raw) if x.strip()]
    elif isinstance(raw, (list, tuple)):
        items = [str(x) for x in raw]
    out: List[str] = []
    for item in items:
        m = re.search(r"\[\[(.*?)\]\]", item)
        token = (m.group(1) if m else item).split("|")[0].split("#")[0].strip()
        if token and token.lower() != "none" and token not in out:
            out.append(token)
    return out


def parse_note(path: Path) -> Optional[Tuple[ThoughtNode, List[str]]]:
    """Parse one note into (node, dependency tokens). Tokens are ids or titles, resolved on import.
    Returns None for non-notes, index/readme/`000_*` notes and notes without frontmatter."""
    path = Path(path)
    if not path.is_file() or path.suffix.lower() != ".md":
        return None
    if path.name.startswith("000_") or path.name.lower() in _SKIP_NAMES:
        return None
    text = path.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    if not fm:
        return None

    node_id = str(fm.get("id") or fm.get("node_id") or path.stem).strip()
    if not node_id:
        return None

    title = fm.get("title")
    if not title:
        h1 = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
        title = h1.group(1).strip() if h1 else node_id.replace("-", " ").replace("_", " ").title()

    legacy_type = str(fm.get("node_type") or fm.get("type") or "task").strip().lower()
    kind, scale = kind_scale_for_type(legacy_type)

    raw_status = fm.get("status") or fm.get("stage") or "ready"
    status = normalize_status(raw_status)

    if "progress" in fm:
        try:
            progress = max(0.0, min(1.0, float(fm["progress"]) / 100.0))
        except (TypeError, ValueError):
            progress = 0.0
    else:
        progress = 1.0 if status is NodeStatus.DONE else 0.0

    tags_raw = fm.get("tags", [])
    if isinstance(tags_raw, str):
        tags = [t.strip().lstrip("#") for t in tags_raw.split(",") if t.strip()]
    else:
        tags = [str(t).strip().lstrip("#") for t in (tags_raw or []) if str(t).strip()]

    criteria = [c.strip() for _, c in re.findall(r"^-\s*\[([ xX])\]\s*(.+)$", body, flags=re.MULTILINE)]
    for item in fm.get("acceptance_criteria") or []:
        if str(item).strip() and str(item).strip() not in criteria:
            criteria.append(str(item).strip())

    deps = _wikilinks(fm.get("dependencies") or fm.get("depends_on") or fm.get("upstream_dependencies"))
    for token in _wikilinks(re.findall(r"from\s+(\[\[.*?\]\])", body, flags=re.IGNORECASE)):
        if token not in deps:
            deps.append(token)

    desc = ""
    m = re.search(r"###?\s+(?:Description|Опис)\s*\n+(.*?)(?=\n###?|\Z)", body, flags=re.DOTALL | re.IGNORECASE)
    if m:
        # legacy notes have no heading after the description: drop checkbox / "from [[x]]" lines
        desc = "\n".join(
            ln for ln in m.group(1).splitlines()
            if not re.match(r"^\s*-\s*\[[ xX]\]", ln) and not re.search(r"\bfrom\s+\[\[", ln)
        ).strip()
        if desc == "_No description provided._":
            desc = ""
    elif fm.get("description"):
        desc = str(fm["description"]).strip()

    position = None
    pos_fm = fm.get("position")
    if isinstance(pos_fm, dict):
        position = {"x": float(pos_fm.get("x", 0.0)), "y": float(pos_fm.get("y", 0.0))}
    else:
        pm = re.search(r">\s*Node Position on Canvas:\s*`x=([0-9.-]+),\s*y=([0-9.-]+)`", body)
        if pm:
            position = {"x": float(pm.group(1)), "y": float(pm.group(2))}

    agent = fm.get("assigned_agent")
    agent = None if str(agent or "").strip().lower() in ("", "none", "null") else str(agent).strip()

    meta: Dict[str, Any] = {
        "legacy_node_type": legacy_type,
        "legacy_stage": str(fm.get("stage") or ""),
        "legacy_status": str(fm.get("status") or ""),
        "source_note": path.name,
    }
    tm = re.search(r"\*\*Module\*\*:\s*`([^`]+)`", body)
    module = fm.get("target_module") or (tm.group(1) if tm else None)
    if module and str(module).strip().lower() not in ("none", "null"):
        meta["target_module"] = str(module)
    files_raw = fm.get("target_files")
    if isinstance(files_raw, (list, tuple)):
        files = [str(f) for f in files_raw]
    else:
        files = []
        sec = re.search(r"###?\s+Target Module & Files\s*\n(.*?)(?=\n###?\s|\Z)", body, flags=re.DOTALL)
        if sec:
            files = re.findall(r"^\s*-\s*`([^`]+)`", sec.group(1), flags=re.MULTILINE)
    if files:
        meta["target_files"] = files
    if isinstance(fm.get("metadata"), dict):
        meta.update(fm["metadata"])

    node = ThoughtNode(
        id=node_id,
        kind=kind,
        title=str(title).strip(),
        content=desc,
        project_id=str(fm["project_id"]).strip() if fm.get("project_id") else None,
        status=status.value,
        metadata=meta,
        assigned_agent=agent,
        tags=tags,
        scale=scale,
        progress=progress,
        priority=_priority(fm.get("priority")),
        spec=TaskSpec(goal=desc, acceptance_criteria=criteria) if (desc or criteria) else None,
        position=position,
        created_at=str(fm["created_at"]) if fm.get("created_at") else None,
        updated_at=str(fm["updated_at"]) if fm.get("updated_at") else None,
    )
    return node, deps


# --- rendering -------------------------------------------------------------------------------


def _filename(node: ThoughtNode) -> str:
    clean = re.sub(r'[\\/*?:"<>|]', "", node.title or node.id).strip().replace(" ", "_")
    return (clean or node.id) + ".md"


def render_note(node: ThoughtNode, dependency_ids: List[str], titles: Optional[Dict[str, str]] = None) -> str:
    """Render a node as a note readable by `parse_note` (and by the legacy engines)."""
    titles = titles or {}
    legacy_type = (node.metadata or {}).get("legacy_node_type") or (
        node.scale.name.lower() if node.scale else node.kind.value
    )
    fm: Dict[str, Any] = {
        "id": node.id,
        "type": str(legacy_type),
        "title": node.title,
        "stage": (node.metadata or {}).get("legacy_stage") or node.status,
        "status": node.status,
        "priority": getattr(node.priority, "value", str(node.priority)),
        "progress": round(float(node.progress) * 100.0, 1),
        "tags": list(node.tags),
        "dependencies": list(dependency_ids),
    }
    if node.project_id:
        fm["project_id"] = node.project_id
    if node.assigned_agent:
        fm["assigned_agent"] = node.assigned_agent
    if node.position:
        fm["position"] = {"x": node.position["x"], "y": node.position["y"]}
    if node.created_at:
        fm["created_at"] = str(node.created_at)
    if node.updated_at:
        fm["updated_at"] = str(node.updated_at)

    mrh = (
        "<!-- --- DNK-MRH-HEADER ---\n"
        f'# mrh_id: "{_filename(node)}"\n'
        f'# purpose: "Obsidian representation of ThoughtDAG node {node.id}"\n'
        "# canonical_source: false\n# alters_files: []\n# triggers_tasks: []\n"
        '# status: "Active"\n# version: "1.0.0"\n'
        f'# updated_at: "{datetime.now().strftime("%Y-%m-%d")}"\n'
        '# author: "DNK Vault Sync"\n--- END DNK-MRH-HEADER -->\n'
    )
    dep_md = "\n".join(f"- [[{titles.get(d, d)}]]" for d in dependency_ids) or "- None"
    criteria = node.spec.acceptance_criteria if node.spec else []
    ac_md = "".join(f"- [ ] {c}\n" for c in criteria)
    return (
        f"---\n{yaml.dump(fm, sort_keys=False, allow_unicode=True)}---\n{mrh}\n"
        f"# {node.title or 'Untitled Node'}\n\n"
        f"## Description\n\n{node.content or '_No description provided._'}\n\n"
        + (f"## Acceptance Criteria\n\n{ac_md}\n" if ac_md else "")
        + f"## Dependencies\n\n{dep_md}\n"
    )


# --- vault <-> store -------------------------------------------------------------------------


_IGNORED_DIRS = {"archive", "trash", ".obsidian", "templates"}


def _merge_node(old: ThoughtNode, new: ThoughtNode, now: str) -> ThoughtNode:
    """Field-wise update of an existing node from a note: unset note fields never erase data,
    acceptance criteria are a union (existing items are kept)."""
    meta = dict(old.metadata or {})
    for key in ("legacy_node_type", "legacy_stage", "legacy_status", "source_note", "target_module", "target_files"):
        if key in new.metadata:
            meta[key] = new.metadata[key]
    old_ac = list(old.spec.acceptance_criteria) if old.spec else []
    new_ac = list(new.spec.acceptance_criteria) if new.spec else []
    merged_ac = old_ac + [c for c in new_ac if c not in old_ac]
    goal = new.content or (old.spec.goal if old.spec else "")
    update: Dict[str, Any] = {
        "title": new.title, "kind": new.kind, "scale": new.scale, "status": new.status, "progress": new.progress,
        "priority": new.priority, "metadata": meta, "updated_at": now,
        "spec": TaskSpec(goal=goal, acceptance_criteria=merged_ac) if (goal or merged_ac) else old.spec,
    }
    if new.content:
        update["content"] = new.content
    if new.assigned_agent:
        update["assigned_agent"] = new.assigned_agent
    if new.tags:
        update["tags"] = new.tags
    if new.position and (new.position.get("x") or new.position.get("y")):
        update["position"] = new.position
    return old.model_copy(update=update)


def import_vault(
    store: Any,
    vault_dir: Path,
    *,
    recursive: bool = False,
    merge_existing: bool = False,
    stub_unresolved: bool = False,
    project_id: Optional[str] = None,
    default_agent: Optional[str] = None,
    default_module: Optional[str] = None,
    edge_label: Optional[str] = None,
    edge_id_fmt: str = "dep_{src}_{dst}",
) -> Dict[str, Any]:
    """Upsert every note of `vault_dir` into the ThoughtDAGStore; dependency tokens are resolved by
    id first, then by title. Edges that would create a cycle or point nowhere are counted, not raised.

    merge_existing: update known nodes field-wise (note never erases data, criteria are unioned)
    instead of replacing them. stub_unresolved: a dependency that matches nothing becomes an
    `unresolved_prerequisite` idea node (anti-dangling guard). project_id: ignore notes of other projects."""
    vault_dir = Path(vault_dir)
    stats: Dict[str, Any] = {"scanned": 0, "imported": 0, "updated": 0, "wires_added": 0, "unresolved": 0,
                             "cycles_skipped": 0, "skipped": 0, "stubs": 0}
    if not vault_dir.exists():
        return stats

    if recursive:
        files = sorted(f for f in vault_dir.rglob("*.md")
                       if not any(part.lower() in _IGNORED_DIRS for part in f.relative_to(vault_dir).parts))
    else:
        files = sorted(vault_dir.glob("*.md"))

    parsed: List[Tuple[ThoughtNode, List[str]]] = []
    for md in files:
        result = parse_note(md)
        if result is None:
            stats["skipped"] += 1
            continue
        if project_id and (result[0].project_id or "dnk_core") != project_id:
            continue
        parsed.append(result)
    stats["scanned"] = len(parsed)
    now = datetime.now(timezone.utc).isoformat()

    def apply(core: Any) -> None:
        graph = core.graph
        for node, _ in parsed:
            old = graph.nodes.get(node.id)
            if old is not None:
                stats["updated"] += 1
                graph.nodes[node.id] = _merge_node(old, node, now) if merge_existing else node
                continue
            stats["imported"] += 1
            meta = dict(node.metadata)
            if default_module and "target_module" not in meta:
                meta["target_module"] = default_module
            graph.nodes[node.id] = node.model_copy(update={
                "assigned_agent": node.assigned_agent or default_agent, "metadata": meta,
                "created_at": node.created_at or now, "updated_at": node.updated_at or now,
            })

        by_title = {n.title: n.id for n in graph.nodes.values()}
        existing = {(w.from_node, w.to_node) for w in graph.wires}
        for node, deps in parsed:
            for token in deps:
                dep_id = token if token in graph.nodes else by_title.get(token)
                if dep_id is None and stub_unresolved and token != node.id:
                    host = graph.nodes.get(node.id)
                    hx = (host.position or {}).get("x", 0.0) if host else 0.0
                    hy = (host.position or {}).get("y", 0.0) if host else 0.0
                    graph.nodes[token] = ThoughtNode(
                        id=token, kind=NodeKind.IDEA, title=f"Unresolved Prerequisite: {token}",
                        content=f"Auto-generated stub placeholder from dangling Obsidian wikilink in [[{node.id}]].",
                        project_id=host.project_id if host else None, status="backlog", priority=_priority("low"),
                        assigned_agent="herich_librarian", tags=["unresolved_prerequisite", "obsidian_stub"],
                        metadata={"legacy_node_type": "idea", "legacy_stage": "ideation", "legacy_status": "backlog",
                                  "target_module": default_module or "core"},
                        position={"x": hx - 280.0, "y": hy}, created_at=now, updated_at=now,
                    )
                    by_title[graph.nodes[token].title] = token
                    stats["imported"] += 1
                    stats["stubs"] += 1
                    dep_id = token
                if dep_id is None or dep_id == node.id:
                    stats["unresolved"] += 1
                    continue
                if (dep_id, node.id) in existing:
                    continue
                try:
                    core.add_edge(dep_id, node.id, wire_type=WireType.DEPENDENCY, label=edge_label,
                                  edge_id=edge_id_fmt.format(src=dep_id, dst=node.id),
                                  metadata={"legacy_relation": "depends_on"})
                except CycleDetectedError:
                    stats["cycles_skipped"] += 1
                    continue
                existing.add((dep_id, node.id))
                stats["wires_added"] += 1

    store.update(apply)
    return stats


def export_vault(core: Any, vault_dir: Path, skip_ephemeral: bool = True) -> int:
    """Write one note per node. Ephemeral nodes (micro steps, dialogue turns) are skipped to avoid
    note explosion, as the Task Forest sync did."""
    vault_dir = Path(vault_dir)
    vault_dir.mkdir(parents=True, exist_ok=True)
    graph = core.graph
    titles = {n.id: n.title for n in graph.nodes.values()}
    deps: Dict[str, List[str]] = {}
    for w in graph.wires:
        if w.wire_type == WireType.DEPENDENCY and not w.validates:
            deps.setdefault(w.to_node, []).append(w.from_node)

    count = 0
    for node in graph.nodes.values():
        if skip_ephemeral and (
            (node.metadata or {}).get("ephemeral") or _EPHEMERAL_TAGS.intersection(node.tags)
        ):
            continue
        (vault_dir / _filename(node)).write_text(render_note(node, deps.get(node.id, []), titles), encoding="utf-8")
        count += 1
    return count
