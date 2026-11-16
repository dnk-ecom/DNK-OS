# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/dag_algorithms.py"
# purpose: "Canon graph algorithms on ThoughtDAG v2: blocked/ready, progress rollup, transitions, CPM, statistics, auto-layout (ported from NodeTaskGraphEngine)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""Pure functions over ThoughtDAGGraph (v2). Progress is 0..1."""

from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple

from core.domain.dag_models import (
    NodeKind,
    NodeStatus,
    Scale,
    ThoughtDAGGraph,
    ThoughtNode,
    Wire,
    WireType,
    normalize_status,
)


def _status(node: ThoughtNode) -> NodeStatus:
    return normalize_status(node.status)


def _is_done(node: ThoughtNode) -> bool:
    return _status(node) is NodeStatus.DONE


def _precedence_wires(graph: ThoughtDAGGraph) -> List[Wire]:
    """Wires that express 'source must precede target' (DEPENDENCY + spawned-from CONTEXT)."""
    out = []
    for w in graph.wires:
        if w.from_node not in graph.nodes or w.to_node not in graph.nodes or w.validates:
            continue  # 'validates' gates completion only, it does not order/start-block
        if w.wire_type is WireType.DEPENDENCY or (
            w.wire_type is WireType.CONTEXT and w.metadata.get("legacy_relation") == "spawns_from"
        ):
            out.append(w)
    return out


def topological_order(graph: ThoughtDAGGraph, include_parent: bool = False) -> List[str]:
    """Kahn order over precedence wires; nodes left in cycles are appended at the end."""
    adj: Dict[str, List[str]] = {n: [] for n in graph.nodes}
    indeg = {n: 0 for n in graph.nodes}
    edges = [(w.from_node, w.to_node) for w in _precedence_wires(graph)]
    if include_parent:
        edges += [(n.parent_id, n.id) for n in graph.nodes.values() if n.parent_id in graph.nodes]
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque(sorted(n for n in graph.nodes if indeg[n] == 0))
    order: List[str] = []
    while q:
        c = q.popleft()
        order.append(c)
        for nx in adj[c]:
            indeg[nx] -= 1
            if indeg[nx] == 0:
                q.append(nx)
    order += [n for n in graph.nodes if n not in set(order)]
    return order


def recompute_blocked(graph: ThoughtDAGGraph) -> Dict[str, List[str]]:
    """Returns {node_id: [incomplete prerequisite ids]}; flips READY<->BLOCKED accordingly."""
    prereqs: Dict[str, List[str]] = defaultdict(list)
    for w in _precedence_wires(graph):
        prereqs[w.to_node].append(w.from_node)
    result: Dict[str, List[str]] = {}
    for nid, node in graph.nodes.items():
        blockers = [p for p in prereqs.get(nid, []) if not _is_done(graph.nodes[p]) and graph.nodes[p].progress < 1.0]
        result[nid] = blockers
        st = _status(node)
        if blockers and st is NodeStatus.READY:
            node.status = NodeStatus.BLOCKED.value
        elif not blockers and st is NodeStatus.BLOCKED:
            node.status = NodeStatus.READY.value
    return result


def ready_nodes(graph: ThoughtDAGGraph) -> List[str]:
    blocked = recompute_blocked(graph)
    return [n for n, node in graph.nodes.items() if _status(node) is NodeStatus.READY and not blocked[n]]


def rollup_progress(graph: ThoughtDAGGraph) -> None:
    """Weighted bottom-up progress over parent_id; a parent at 100% becomes DONE (unless cancelled)."""
    children: Dict[str, List[str]] = defaultdict(list)
    for n in graph.nodes.values():
        if n.parent_id in graph.nodes and n.parent_id != n.id:
            children[n.parent_id].append(n.id)

    depth_cache: Dict[str, int] = {}

    def depth(nid: str, seen: Tuple[str, ...] = ()) -> int:
        if nid in depth_cache:
            return depth_cache[nid]
        p = graph.nodes[nid].parent_id
        d = 0 if (p not in graph.nodes or p in seen or p == nid) else 1 + depth(p, seen + (nid,))
        depth_cache[nid] = d
        return d

    for pid in sorted(children, key=lambda x: depth(x), reverse=True):
        kids = [graph.nodes[c] for c in children[pid]]
        total_w = sum(k.weight for k in kids)
        parent = graph.nodes[pid]
        parent.progress = round(
            (sum(k.progress * k.weight for k in kids) / total_w) if total_w > 0 else sum(k.progress for k in kids) / len(kids),
            4,
        )
        if parent.progress >= 1.0 and _status(parent) is not NodeStatus.CANCELLED:
            parent.status = NodeStatus.DONE.value


def can_transition(
    graph: ThoughtDAGGraph, node_id: str, target: NodeStatus, force: bool = False
) -> Tuple[bool, str]:
    if force:
        return True, "Forced transition approved"
    node = graph.nodes[node_id]
    if target in (NodeStatus.READY, NodeStatus.IN_PROGRESS):
        blockers = recompute_blocked(graph).get(node_id, [])
        if blockers:
            names = ", ".join(graph.nodes[b].title for b in blockers)
            return False, f"Node is blocked by incomplete prerequisite tasks: {names}"
    if target is NodeStatus.DONE:
        for w in graph.wires:
            if w.to_node == node_id and w.validates:
                gate = graph.nodes.get(w.from_node)
                if gate and not _is_done(gate):
                    return False, f"Verification gate '{gate.title}' must be completed first."
    return True, "Transition allowed"


_P_HOURS = {"critical": 8.0, "high": 5.0, "medium": 3.0, "low": 1.0}


def _duration(node: ThoughtNode) -> float:
    if _is_done(node):
        return 0.0
    base = _P_HOURS.get(str(getattr(node.priority, "value", node.priority)).lower(), 3.0)
    if node.scale is Scale.TREE:
        base = max(base, 10.0)
    elif node.kind is NodeKind.GATE:
        base = 1.0
    rem = max(0.0, 1.0 - node.progress)
    return max(0.5, round(base * rem, 1)) if rem > 0 else 0.0


def critical_path(graph: ThoughtDAGGraph) -> Dict[str, Any]:
    if not graph.nodes:
        return {"critical_path_node_ids": [], "critical_edge_ids": [], "total_duration_hours": 0.0,
                "bottlenecks": [], "node_metrics": {}}
    dur = {n: _duration(node) for n, node in graph.nodes.items()}
    preds: Dict[str, List[str]] = defaultdict(list)
    succs: Dict[str, List[str]] = defaultdict(list)
    edge_ids: Dict[Tuple[str, str], str] = {}
    for w in _precedence_wires(graph):
        preds[w.to_node].append(w.from_node)
        succs[w.from_node].append(w.to_node)
        edge_ids[(w.from_node, w.to_node)] = w.id
    order = topological_order(graph)
    es: Dict[str, float] = {}
    ef: Dict[str, float] = {}
    for n in order:
        es[n] = max((ef.get(p, 0.0) for p in preds[n]), default=0.0)
        ef[n] = round(es[n] + dur[n], 2)
    total = max(ef.values())
    lf: Dict[str, float] = {}
    ls: Dict[str, float] = {}
    for n in reversed(order):
        lf[n] = min((ls.get(s, total) for s in succs[n]), default=total)
        ls[n] = round(lf[n] - dur[n], 2)
    metrics: Dict[str, Dict[str, Any]] = {}
    crit: List[str] = []
    for n in order:
        slack = round(ls[n] - es[n], 2)
        is_crit = abs(slack) < 0.05 and dur[n] > 0
        metrics[n] = {"duration_hours": dur[n], "early_start": es[n], "early_finish": ef[n],
                      "late_start": ls[n], "late_finish": lf[n], "slack": slack, "is_critical": is_crit}
        if is_crit:
            crit.append(n)
    crit_edges = [eid for (u, v), eid in edge_ids.items()
                  if u in crit and v in crit and abs(ef[u] - es[v]) < 0.05]
    bottlenecks = [
        {"node_id": n, "title": graph.nodes[n].title, "assigned_agent": graph.nodes[n].assigned_agent,
         "blocking_count": len(succs[n]), "duration_hours": metrics[n]["duration_hours"],
         "priority": getattr(graph.nodes[n].priority, "value", graph.nodes[n].priority)}
        for n in crit if succs[n] or metrics[n]["duration_hours"] >= 5.0
    ]
    bottlenecks.sort(key=lambda b: (b["blocking_count"], b["duration_hours"]), reverse=True)
    return {"critical_path_node_ids": crit, "critical_edge_ids": crit_edges,
            "total_duration_hours": round(total, 1), "bottlenecks": bottlenecks, "node_metrics": metrics}


def statistics(graph: ThoughtDAGGraph) -> Dict[str, Any]:
    nodes = list(graph.nodes.values())
    blocked = recompute_blocked(graph)
    by_scale: Dict[str, int] = defaultdict(int)
    by_kind: Dict[str, int] = defaultdict(int)
    by_status: Dict[str, int] = defaultdict(int)
    workload: Dict[str, int] = defaultdict(int)
    for n in nodes:
        by_kind[n.kind.value] += 1
        by_scale[n.scale.value if n.scale else "none"] += 1
        by_status[_status(n).value] += 1
        if not _is_done(n):
            workload[n.assigned_agent or "unassigned"] += 1
    total = len(nodes)
    return {
        "total_nodes": total,
        "blocked_count": sum(1 for b in blocked.values() if b),
        "by_kind": dict(by_kind),
        "by_scale": dict(by_scale),
        "by_status": dict(by_status),
        "agent_workload": dict(workload),
        "overall_progress": round(sum(n.progress for n in nodes) / total, 4) if total else 0.0,
    }


def auto_layout(graph: ThoughtDAGGraph, h_pitch: float = 440.0, v_pitch: float = 280.0,
                base_x: float = 60.0, base_y: float = 80.0) -> Dict[str, Dict[str, float]]:
    """Level-based layered layout; writes node.position and returns {id: {x, y}}."""
    ids = set(graph.nodes)
    if not ids:
        return {}
    adj: Dict[str, List[str]] = {n: [] for n in ids}
    indeg = {n: 0 for n in ids}
    edges = [(w.from_node, w.to_node) for w in _precedence_wires(graph)]
    edges += [(n.parent_id, n.id) for n in graph.nodes.values() if n.parent_id in ids]
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    depth: Dict[str, int] = {}
    q = deque(sorted(n for n in ids if indeg[n] == 0))
    for n in q:
        depth[n] = 0
    seen = set(q)
    while q:
        c = q.popleft()
        for nx in adj[c]:
            depth[nx] = max(depth.get(nx, 0), depth[c] + 1)
            indeg[nx] -= 1
            if indeg[nx] <= 0 and nx not in seen:
                seen.add(nx)
                q.append(nx)
    for n in ids:
        if n not in depth:
            node = graph.nodes[n]
            depth[n] = 3 if node.kind is NodeKind.GATE else (0 if node.kind is NodeKind.IDEA or node.scale is Scale.TREE else 1)
    levels: Dict[int, List[str]] = defaultdict(list)
    for n, d in depth.items():
        levels[d].append(n)
    rank = {NodeKind.IDEA: 0, NodeKind.GATE: 4}
    out: Dict[str, Dict[str, float]] = {}
    for d, nids in sorted(levels.items()):
        nids.sort(key=lambda n: (rank.get(graph.nodes[n].kind, 2), graph.nodes[n].title))
        for i, n in enumerate(nids):
            pos = {"x": base_x + d * h_pitch, "y": base_y + i * v_pitch}
            graph.nodes[n].position = pos
            out[n] = pos
    return out
