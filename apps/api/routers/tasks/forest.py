# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/tasks/forest.py"
# purpose: "FastAPI REST router for Task Forest 5-Plant Scale Engine (Field -> Sector -> Tree -> Bush -> Flower) with Bottom-Up Rollup, CONTRACT-009 Decomposer & Dependency Wires."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import functools
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from core.task_forest.dependencies import DependencyGraph
from core.obsidian.vault_to_taskforest import build_vault_task_forest

router = APIRouter(prefix="/api/v3/task_forest", tags=["Task Forest Spatial Engine"])

PLANT_ICONS = {
    "field": "🌾",
    "sector": "🏞️",
    "tree": "🌳",
    "bush": "🌿",
    "flower": "🌸"
}

PLANT_HIERARCHY_LEVELS = ["field", "sector", "tree", "bush", "flower"]


class PlantScale(str, Enum):
    FIELD = "field"       # 🌾 Поле / Проєкт
    SECTOR = "sector"     # 🏞️ Сектор
    TREE = "tree"         # 🌳 Глобальна задача / Дерево
    BUSH = "bush"         # 🌿 Підзадача / Кущ
    FLOWER = "flower"     # 🌸 Атомарна дія / Квітка


class NodeStatus(str, Enum):
    BLOCKED = "blocked"           # Чекає завершення батьківських нод
    READY = "ready"               # Розблоковано, готове до виконання
    IN_PROGRESS = "in_progress"   # Агент чи людина працює
    VERIFYING = "verifying"       # Проходить перевірку якості / тест
    DONE = "done"                 # Успішно завершено 🟢
    COMPLETED = "completed"       # Синонім done
    TODO = "todo"                 # У беклозі
    FAILED = "failed"             # Помилка виконання


class TaskForestNode(BaseModel):
    id: str
    title: str
    plant_scale: str = Field(..., description="field | sector | tree | bush | flower")
    status: str = Field(default="todo", description="todo | pending | in_progress | completed | cancelled | ready | blocked | done")
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    parent_id: Optional[str] = None
    assigned_agent: Optional[str] = None
    author: Optional[str] = "Maxim"
    weight: float = 1.0
    git_diff: Optional[str] = None
    dto_contract: Optional[Dict[str, Any]] = None
    verification_status: Optional[str] = "verified"
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    children: List["TaskForestNode"] = Field(default_factory=list)


class TaskDependencyWire(BaseModel):
    source_id: str = Field(..., description="ID ноди, результат якої потрібен")
    target_id: str = Field(..., description="ID ноди, яка залежить від source")
    wire_kind: str = Field(default="data_dependency", description="'data_dependency' | 'temporal_order'")


class DecomposeTaskRequest(BaseModel):
    global_goal: str = Field(..., description="Людський опис глобальної мети")
    project_id: str = Field(default="ws-alpha-001", description="ID проєкту (контекст бренду)")
    suggested_skills: Optional[List[str]] = Field(default_factory=list)


class DecomposeTaskResponse(BaseModel):
    status: str = "success"
    tree_id: str
    nodes: Dict[str, Any] = Field(..., description="Словник створених нод (Tree, Bush, Flower)")
    wires: List[TaskDependencyWire] = Field(..., description="Зв'язки залежностей")
    initial_ready_node_ids: List[str] = Field(..., description="Список нод, які можна виконувати першими")


class ResolveSubtaskRequest(BaseModel):
    node_id: str
    status: str = Field(default="completed", description="completed | done | failed")
    progress: float = 100.0
    evidence_payload: Optional[Dict[str, Any]] = None


class ResolveSubtaskResponse(BaseModel):
    status: str = "success"
    node_id: str
    node_status: str
    new_parent_progress: float = Field(..., description="Оновлений прогрес батьківської задачі (Bottom-Up Rollup)")
    unlocked_nodes: List[str] = Field(default_factory=list, description="Ноди, які щойно розблокувалися")
    is_tree_completed: bool = Field(default=False, description="Чи завершено всю глобальну задачу на 100%")


class MutateNodeRequest(BaseModel):
    node_id: Optional[str] = Field(default=None, description="Existing node ID to mutate, or omit to create new node")
    parent_id: Optional[str] = Field(default=None, description="Parent node ID if creating new flower/bush")
    title: Optional[str] = None
    plant_scale: Optional[str] = Field(default="flower", description="field | sector | tree | bush | flower")
    status: Optional[str] = Field(default=None, description="todo | pending | in_progress | completed | cancelled | ready | blocked | done")
    progress: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    assigned_agent: Optional[str] = None
    author: Optional[str] = None
    git_diff: Optional[str] = None
    dto_contract: Optional[Dict[str, Any]] = None
    verification_status: Optional[str] = None


class EvolutionHistoryItem(BaseModel):
    event_id: str
    timestamp: str
    node_id: str
    node_title: str
    plant_scale: str
    mutation_type: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    previous_progress: Optional[float] = None
    new_progress: Optional[float] = None
    overall_field_progress: float
    description: str


logger = logging.getLogger(__name__)

HISTORY_LIMIT = 500


def _spatial_canon_path() -> Path:
    """Canonical ThoughtDAG v2 file of the spatial Task Forest landscape (separate graph from core TaskForest)."""
    return Path(os.environ.get("DNK_TASK_FOREST_SPATIAL_FILE") or ".data/thoughtdag_v2/task_forest_spatial.json")


def _persisting(fn):
    """Persist the landscape after a mutating store operation (best effort, never breaks the API)."""
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        result = fn(self, *args, **kwargs)
        self._persist()
        return result
    return wrapper


class TaskForestStore:
    """Thread-safe state store for Task Forest with Bottom-Up Rollup & CONTRACT-009 DAG Wires.
    Persisted in the canonical ThoughtDAG v2 store (untangle D1.4d); history lives in a sidecar file."""

    def __init__(self, canon_file: Optional[Path] = None):
        self._canon_file = Path(canon_file) if canon_file else _spatial_canon_path()
        self._nodes: Dict[str, TaskForestNode] = {}
        self._history: List[EvolutionHistoryItem] = []
        self._wires: List[TaskDependencyWire] = []
        self._dep_graph = DependencyGraph()
        if not self._restore():
            self._init_default_forest()

    @property
    def _history_file(self) -> Path:
        return self._canon_file.with_name(self._canon_file.stem + ".history.json")

    def _canon_store(self) -> Any:
        from core.canvas.dag_store import ThoughtDAGStore

        return ThoughtDAGStore(self._canon_file, graph_id="task_forest_spatial")

    def _persist(self) -> None:
        try:
            from core.domain.dag_converters import forest_to_thoughtdag

            graph = forest_to_thoughtdag(self._nodes.values(), self._wires, graph_id="task_forest_spatial")

            def _replace(core: Any) -> None:
                graph.project_id = core.graph.project_id or graph.project_id
                core.graph = graph

            self._canon_store().update(_replace)
            payload = json.dumps([h.model_dump() for h in self._history[:HISTORY_LIMIT]], ensure_ascii=False)
            tmp = self._history_file.with_suffix(".tmp")
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, self._history_file)
        except Exception as exc:  # shortcut: persistence is best-effort, trigger: D1.5 hardening
            logger.warning("task forest landscape persist failed: %s", exc)

    def _restore(self) -> bool:
        if not self._canon_file.exists():
            return False
        try:
            from core.domain.dag_converters import thoughtdag_to_forest_dicts

            nodes, wires = thoughtdag_to_forest_dicts(self._canon_store().load().graph)
            if not nodes:
                return False
            self._nodes = {d["id"]: TaskForestNode(**d) for d in nodes}
            self._wires = [TaskDependencyWire(**w) for w in wires]
            self._dep_graph = DependencyGraph()
            for w in self._wires:
                self._dep_graph.add_dependency(w.target_id, w.source_id)
            self._history = []
            if self._history_file.exists():
                self._history = [EvolutionHistoryItem(**h) for h in json.loads(self._history_file.read_text(encoding="utf-8"))]
            return True
        except Exception as exc:
            logger.warning("task forest landscape restore failed (%s); seeding baseline", exc)
            return False

    def _init_default_forest(self):
        self._nodes.clear()
        self._history.clear()
        self._wires.clear()
        self._dep_graph = DependencyGraph()

        # 1. 🌾 Field (Root)
        root_field = TaskForestNode(
            id="field-001",
            title="DNK_HUB Master HQ",
            plant_scale="field",
            status="in_progress",
            progress=88.0,
            assigned_agent="antigravity_mentor",
            author="Maxim",
            verification_status="verified",
            dto_contract={"protocol": "TaskForestV5", "workspace": "ws-alpha-001"}
        )

        # 2. 🏞️ Sector
        sector_canvas = TaskForestNode(
            id="sector-001",
            title="Spatial Studio & Infinite Canvas",
            plant_scale="sector",
            status="in_progress",
            progress=88.0,
            parent_id="field-001",
            assigned_agent="gerych_builder",
            author="Maxim",
            verification_status="verified"
        )

        # 3. 🌳 Trees
        # Tree 1: Google Stitch Canvas & Play Prototyper (100% 🟢)
        tree_stitch = TaskForestNode(
            id="tree-001",
            title="Google Stitch Canvas & Play Prototyper",
            plant_scale="tree",
            status="completed",
            progress=100.0,
            parent_id="sector-001",
            assigned_agent="gerych_builder",
            verification_status="verified",
            git_diff="feat(stitch): interactive DAG screen rendering & play prototype runtime"
        )
        bush_stitch_1 = TaskForestNode(
            id="bush-001",
            title="Screen DAG Orchestrator",
            plant_scale="bush",
            status="completed",
            progress=100.0,
            parent_id="tree-001",
            assigned_agent="gerych_builder"
        )
        flw_stitch_1 = TaskForestNode(
            id="flw-001",
            title="Interactive Canvas Screen Nodes",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-001",
            assigned_agent="gerych_builder"
        )
        flw_stitch_2 = TaskForestNode(
            id="flw-002",
            title="WebSocket Sync & Collaborative State",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-001",
            assigned_agent="gerych_builder"
        )

        # Tree 2: Shopify OS 2.0 Live AST Sandbox (100% 🟢)
        tree_shopify = TaskForestNode(
            id="tree-002",
            title="Shopify OS 2.0 Live AST Sandbox",
            plant_scale="tree",
            status="completed",
            progress=100.0,
            parent_id="sector-001",
            assigned_agent="dnk_shopify",
            verification_status="verified",
            git_diff="feat(shopify): AST Liquid compiler, schema generator & theme live push"
        )
        bush_shopify_1 = TaskForestNode(
            id="bush-002",
            title="Liquid AST Transpiler",
            plant_scale="bush",
            status="completed",
            progress=100.0,
            parent_id="tree-002",
            assigned_agent="dnk_shopify"
        )
        flw_shopify_1 = TaskForestNode(
            id="flw-003",
            title="Canvas to Shopify Theme Transpiler",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-002",
            assigned_agent="dnk_shopify"
        )
        flw_shopify_2 = TaskForestNode(
            id="flw-004",
            title="Liquid Syntax & Variable Linting",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-002",
            assigned_agent="dnk_shopify"
        )

        # Tree 3: DuckDB Lakehouse AI Analyst (100% 🟢)
        tree_lakehouse = TaskForestNode(
            id="tree-003",
            title="DuckDB Lakehouse AI Analyst",
            plant_scale="tree",
            status="completed",
            progress=100.0,
            parent_id="sector-001",
            assigned_agent="dnk_dev_fullstack",
            verification_status="verified",
            git_diff="feat(lakehouse): DuckDB analytical schemas, NL2SQL query engine & dynamic charts"
        )
        bush_lakehouse_1 = TaskForestNode(
            id="bush-003",
            title="Lakehouse BI NL2SQL Engine",
            plant_scale="bush",
            status="completed",
            progress=100.0,
            parent_id="tree-003",
            assigned_agent="dnk_dev_fullstack"
        )
        flw_lakehouse_1 = TaskForestNode(
            id="flw-005",
            title="In-Memory DuckDB Analytical Schema",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-003",
            assigned_agent="dnk_dev_fullstack"
        )
        flw_lakehouse_2 = TaskForestNode(
            id="flw-006",
            title="Multi-Agent DAG Query Dispatcher",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-003",
            assigned_agent="dnk_dev_fullstack"
        )

        # Tree 4: Task Forest Spatial HQ (In Progress 🟡 - 40%)
        tree_forest = TaskForestNode(
            id="tree-004",
            title="Task Forest Spatial HQ",
            plant_scale="tree",
            status="in_progress",
            progress=40.0,
            parent_id="sector-001",
            assigned_agent="gerych_prime",
            verification_status="pending",
            git_diff="feat(task_forest): 5-plant scale taxonomy, bottom-up rollup & timeline history"
        )
        bush_forest_1 = TaskForestNode(
            id="bush-004",
            title="5-Plant Scale Taxonomy Engine",
            plant_scale="bush",
            status="in_progress",
            progress=40.0,
            parent_id="tree-004",
            assigned_agent="gerych_prime"
        )
        flw_forest_1 = TaskForestNode(
            id="flw-007",
            title="Bottom-Up Recursive Rollup Logic",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-004",
            assigned_agent="gerych_prime"
        )
        flw_forest_2 = TaskForestNode(
            id="flw-008",
            title="Spatial Canvas Drawer UI & Inspector",
            plant_scale="flower",
            status="todo",
            progress=0.0,
            parent_id="bush-004",
            assigned_agent="gerych_builder"
        )
        flw_forest_3 = TaskForestNode(
            id="flw-009",
            title="Genetic Scrubber & Timeline History",
            plant_scale="flower",
            status="todo",
            progress=0.0,
            parent_id="bush-004",
            assigned_agent="gerych_builder"
        )
        flw_forest_4 = TaskForestNode(
            id="flw-010",
            title="FastAPI REST Mutation Endpoints",
            plant_scale="flower",
            status="in_progress",
            progress=60.0,
            parent_id="bush-004",
            assigned_agent="gerych_prime"
        )

        # Tree 5: CapCut Kinetic Video Timeline (Ready ⚪ - 100%)
        tree_timeline = TaskForestNode(
            id="tree-005",
            title="CapCut Kinetic Video Timeline",
            plant_scale="tree",
            status="ready",
            progress=100.0,
            parent_id="sector-001",
            assigned_agent="dnk_video_ai_creator",
            verification_status="verified",
            git_diff="feat(video): multi-track kinetic timeline, audio waveforms & Remotion render"
        )
        bush_timeline_1 = TaskForestNode(
            id="bush-005",
            title="Kinetic Motion & Audio Reactive Tracks",
            plant_scale="bush",
            status="completed",
            progress=100.0,
            parent_id="tree-005",
            assigned_agent="dnk_video_ai_creator"
        )
        flw_timeline_1 = TaskForestNode(
            id="flw-011",
            title="Audio Waveform Keyframe Engine",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-005",
            assigned_agent="dnk_video_ai_creator"
        )
        flw_timeline_2 = TaskForestNode(
            id="flw-012",
            title="Headless Remotion Video Renderer",
            plant_scale="flower",
            status="completed",
            progress=100.0,
            parent_id="bush-005",
            assigned_agent="dnk_video_ai_creator"
        )

        all_init_nodes = [
            root_field, sector_canvas,
            tree_stitch, bush_stitch_1, flw_stitch_1, flw_stitch_2,
            tree_shopify, bush_shopify_1, flw_shopify_1, flw_shopify_2,
            tree_lakehouse, bush_lakehouse_1, flw_lakehouse_1, flw_lakehouse_2,
            tree_forest, bush_forest_1, flw_forest_1, flw_forest_2, flw_forest_3, flw_forest_4,
            tree_timeline, bush_timeline_1, flw_timeline_1, flw_timeline_2
        ]

        for n in all_init_nodes:
            self._nodes[n.id] = n

        # Initial history baseline
        self._history.append(
            EvolutionHistoryItem(
                event_id="evt-genesis-001",
                timestamp=datetime.now(timezone.utc).isoformat(),
                node_id="field-001",
                node_title="DNK_HUB Master HQ",
                plant_scale="field",
                mutation_type="genesis",
                previous_status=None,
                new_status="in_progress",
                previous_progress=None,
                new_progress=88.0,
                overall_field_progress=88.0,
                description="Initial Task Forest Genesis baseline established."
            )
        )

        # Run bottom-up rollup to ensure mathematically consistent tree
        self._recalculate_all_rollup()
        self._persist()

    def _get_children(self, parent_id: str) -> List[TaskForestNode]:
        return [n for n in self._nodes.values() if n.parent_id == parent_id]

    def _recalculate_all_rollup(self) -> float:
        """Recursive bottom-up rollup starting from leaf nodes to root."""
        # Find root field
        roots = [n for n in self._nodes.values() if n.parent_id is None]
        if not roots:
            return 0.0

        for root in roots:
            self._rollup_node(root)

        root_field = self._nodes.get("field-001")
        return root_field.progress if root_field else 0.0

    def _rollup_node(self, node: TaskForestNode) -> float:
        children = self._get_children(node.id)
        if not children:
            # Leaf node calculation
            if node.status == "completed":
                node.progress = 100.0
            elif node.status in ("todo", "cancelled"):
                node.progress = 0.0
            elif node.status in ("in_progress", "pending"):
                # preserve explicit progress
                pass
            return node.progress

        child_progresses = [self._rollup_node(child) for child in children]
        avg_progress = round(sum(child_progresses) / len(child_progresses), 2)
        node.progress = avg_progress

        if avg_progress >= 100.0:
            node.status = "completed"
        elif avg_progress <= 0.0 and node.status not in ("cancelled", "ready"):
            node.status = "todo"
        elif node.status != "ready":
            node.status = "in_progress"

        return node.progress

    def recalculate_cascade(self, starting_node_id: str) -> None:
        """Recalculate progress up the ancestor chain: Node -> Bush -> Tree -> Sector -> Field."""
        curr_id = starting_node_id
        while curr_id:
            curr = self._nodes.get(curr_id)
            if not curr:
                break
            children = self._get_children(curr.id)
            if children:
                avg = round(sum(c.progress for c in children) / len(children), 2)
                curr.progress = avg
                if avg >= 100.0:
                    curr.status = "completed"
                elif avg <= 0.0 and curr.status not in ("cancelled", "ready"):
                    curr.status = "todo"
                elif curr.status != "ready":
                    curr.status = "in_progress"
            curr_id = curr.parent_id

    def build_tree_graph(self) -> TaskForestNode:
        """Returns deep nested tree graph for frontend consumption."""
        self._recalculate_all_rollup()
        root = self._nodes.get("field-001")
        if not root:
            raise HTTPException(status_code=404, detail="Root field node not found")

        def _assemble(n: TaskForestNode) -> TaskForestNode:
            c_nodes = self._get_children(n.id)
            return TaskForestNode(
                id=n.id,
                title=n.title,
                plant_scale=n.plant_scale,
                status=n.status,
                progress=n.progress,
                parent_id=n.parent_id,
                assigned_agent=n.assigned_agent,
                author=n.author,
                weight=n.weight,
                git_diff=n.git_diff,
                dto_contract=n.dto_contract,
                verification_status=n.verification_status,
                updated_at=n.updated_at,
                children=[_assemble(c) for c in c_nodes]
            )

        return _assemble(root)

    @_persisting
    def mutate_node(self, req: MutateNodeRequest) -> Dict[str, Any]:
        prev_status = None
        prev_progress = None
        mutation_type = "create"

        if req.node_id and req.node_id in self._nodes:
            # Update existing node
            node = self._nodes[req.node_id]
            prev_status = node.status
            prev_progress = node.progress
            mutation_type = "update"

            if req.title is not None:
                node.title = req.title
            if req.status is not None:
                node.status = req.status
                if req.status == "completed":
                    node.progress = 100.0
                elif req.status in ("todo", "cancelled"):
                    node.progress = 0.0
            if req.progress is not None:
                node.progress = req.progress
            if req.assigned_agent is not None:
                node.assigned_agent = req.assigned_agent
            if req.author is not None:
                node.author = req.author
            if req.git_diff is not None:
                node.git_diff = req.git_diff
            if req.dto_contract is not None:
                node.dto_contract = req.dto_contract
            if req.verification_status is not None:
                node.verification_status = req.verification_status

            node.updated_at = datetime.now(timezone.utc).isoformat()
            target_node = node
        else:
            # Create new node
            new_id = req.node_id or f"flw-{int(time.time() * 1000) % 1000000:06d}"
            target_node = TaskForestNode(
                id=new_id,
                title=req.title or "New Task Flower",
                plant_scale=req.plant_scale or "flower",
                status=req.status or "todo",
                progress=100.0 if req.status == "completed" else (req.progress or 0.0),
                parent_id=req.parent_id or "bush-004",
                assigned_agent=req.assigned_agent or "gerych_builder",
                author=req.author or "Maxim",
                git_diff=req.git_diff or "feat(task): new atomic task created on spatial canvas",
                dto_contract=req.dto_contract,
                verification_status=req.verification_status or "verified"
            )
            self._nodes[new_id] = target_node

        # Recalculate rollup cascade
        if target_node.parent_id:
            self.recalculate_cascade(target_node.parent_id)
        else:
            self._recalculate_all_rollup()

        root = self._nodes.get("field-001")
        overall = root.progress if root else 0.0

        # Append evolution history entry
        evt_id = f"evt-{int(time.time() * 1000)}"
        history_item = EvolutionHistoryItem(
            event_id=evt_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            node_id=target_node.id,
            node_title=target_node.title,
            plant_scale=target_node.plant_scale,
            mutation_type=mutation_type,
            previous_status=prev_status,
            new_status=target_node.status,
            previous_progress=prev_progress,
            new_progress=target_node.progress,
            overall_field_progress=overall,
            description=f"Node '{target_node.title}' mutated: status={target_node.status}, progress={target_node.progress}%"
        )
        self._history.insert(0, history_item)

        return {
            "status": "success",
            "mutation_type": mutation_type,
            "node": target_node.model_dump(),
            "overall_field_progress": overall,
            "event_id": evt_id
        }

    @_persisting
    def decompose_goal(self, req: DecomposeTaskRequest) -> Dict[str, Any]:
        """CONTRACT-009: Decomposes a high-level goal into connected Tree -> Bush -> Flower DAG nodes."""
        ts = int(time.time() * 1000)
        tree_id = f"tree-dec-{ts % 1000000:06d}"
        
        # Determine main builder agent based on skills
        builder_agent = "dnk_dev_fullstack"
        if req.suggested_skills:
            if any("shopify" in s.lower() for s in req.suggested_skills):
                builder_agent = "dnk_shopify"
            elif any("video" in s.lower() for s in req.suggested_skills):
                builder_agent = "dnk_video_ai_creator"

        # 1. 🌳 Create Tree Node
        tree_node = TaskForestNode(
            id=tree_id,
            title=req.global_goal,
            plant_scale="tree",
            status="ready",
            progress=0.0,
            parent_id="sector-001",
            assigned_agent="antigravity_mentor",
            author="Maxim",
            verification_status="in_review",
            dto_contract={
                "project_id": req.project_id,
                "suggested_skills": req.suggested_skills,
                "goal": req.global_goal
            }
        )
        self._nodes[tree_id] = tree_node

        # 2. 🌿 Create 3 Bushes (Phases)
        bush_arch_id = f"bush-{tree_id}-arch"
        bush_arch = TaskForestNode(
            id=bush_arch_id,
            title="Фаза 1: Архітектура та DTO Контракти",
            plant_scale="bush",
            status="ready",
            progress=0.0,
            parent_id=tree_id,
            assigned_agent="antigravity_mentor"
        )
        self._nodes[bush_arch_id] = bush_arch

        bush_exec_id = f"bush-{tree_id}-exec"
        bush_exec = TaskForestNode(
            id=bush_exec_id,
            title="Фаза 2: Fullstack Розробка та Інтеграція",
            plant_scale="bush",
            status="blocked",
            progress=0.0,
            parent_id=tree_id,
            assigned_agent=builder_agent
        )
        self._nodes[bush_exec_id] = bush_exec

        bush_audit_id = f"bush-{tree_id}-audit"
        bush_audit = TaskForestNode(
            id=bush_audit_id,
            title="Фаза 3: Верифікація та Gate Контролю Якості",
            plant_scale="bush",
            status="blocked",
            progress=0.0,
            parent_id=tree_id,
            assigned_agent="gerych_auditor"
        )
        self._nodes[bush_audit_id] = bush_audit

        # 3. 🌸 Create Flowers (Atomic Tasks)
        # Phase 1 Flowers:
        flw_spec_id = f"flw-{tree_id}-01"
        flw_spec = TaskForestNode(
            id=flw_spec_id,
            title=f"Специфікація DTO, Pre-Mortem та Інваріантів: {req.global_goal[:35]}",
            plant_scale="flower",
            status="ready",
            progress=0.0,
            parent_id=bush_arch_id,
            assigned_agent="antigravity_mentor",
            dto_contract={
                "pre_mortem_required": True,
                "mandatory_dissent": ["failure_mode_1", "failure_mode_2", "failure_mode_3"]
            }
        )
        self._nodes[flw_spec_id] = flw_spec

        flw_dag_id = f"flw-{tree_id}-02"
        flw_dag = TaskForestNode(
            id=flw_dag_id,
            title="Побудова графу залежностей (TaskDNA DAG)",
            plant_scale="flower",
            status="blocked",
            progress=0.0,
            parent_id=bush_arch_id,
            assigned_agent="gerych_researcher"
        )
        self._nodes[flw_dag_id] = flw_dag

        # Phase 2 Flowers:
        flw_core_id = f"flw-{tree_id}-03"
        flw_core = TaskForestNode(
            id=flw_core_id,
            title="Реалізація логіки модуля / Core Engine",
            plant_scale="flower",
            status="blocked",
            progress=0.0,
            parent_id=bush_exec_id,
            assigned_agent=builder_agent
        )
        self._nodes[flw_core_id] = flw_core

        flw_ui_id = f"flw-{tree_id}-04"
        flw_ui = TaskForestNode(
            id=flw_ui_id,
            title="Підключення Visual Shell & API Роутера",
            plant_scale="flower",
            status="blocked",
            progress=0.0,
            parent_id=bush_exec_id,
            assigned_agent=builder_agent
        )
        self._nodes[flw_ui_id] = flw_ui

        # Phase 3 Flowers:
        flw_test_id = f"flw-{tree_id}-05"
        flw_test = TaskForestNode(
            id=flw_test_id,
            title="Створення Pytest & Інтеграційних тестів",
            plant_scale="flower",
            status="blocked",
            progress=0.0,
            parent_id=bush_audit_id,
            assigned_agent="gerych_auditor"
        )
        self._nodes[flw_test_id] = flw_test

        flw_gate_id = f"flw-{tree_id}-06"
        flw_gate = TaskForestNode(
            id=flw_gate_id,
            title="Adversarial Pre-Commit Gate (Auditor vs Builder)",
            plant_scale="flower",
            status="blocked",
            progress=0.0,
            parent_id=bush_audit_id,
            assigned_agent="gerych_auditor"
        )
        self._nodes[flw_gate_id] = flw_gate

        # 4. ⚡ Wires (Prerequisite dependencies: target depends on source)
        created_wires = [
            TaskDependencyWire(source_id=flw_spec_id, target_id=flw_dag_id),
            TaskDependencyWire(source_id=flw_dag_id, target_id=flw_core_id),
            TaskDependencyWire(source_id=flw_core_id, target_id=flw_ui_id),
            TaskDependencyWire(source_id=flw_ui_id, target_id=flw_test_id),
            TaskDependencyWire(source_id=flw_test_id, target_id=flw_gate_id),
        ]
        for w in created_wires:
            self._wires.append(w)
            self._dep_graph.add_dependency(w.target_id, w.source_id)

        # Recalculate rollup
        self.recalculate_cascade(tree_id)

        initial_ready = [flw_spec_id]
        created_nodes = {
            n_id: self._nodes[n_id].model_dump()
            for n_id in [
                tree_id,
                bush_arch_id, bush_exec_id, bush_audit_id,
                flw_spec_id, flw_dag_id, flw_core_id, flw_ui_id, flw_test_id, flw_gate_id
            ]
        }

        # Evolution history
        evt_id = f"evt-{int(time.time() * 1000)}"
        root = self._nodes.get("field-001")
        overall = root.progress if root else 0.0
        self._history.insert(0, EvolutionHistoryItem(
            event_id=evt_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            node_id=tree_id,
            node_title=tree_node.title,
            plant_scale="tree",
            mutation_type="decompose",
            new_status="ready",
            new_progress=0.0,
            overall_field_progress=overall,
            description=f"CONTRACT-009: Task Decomposed into DAG tree '{tree_node.title}' with {len(created_wires)} wires"
        ))

        return {
            "status": "success",
            "tree_id": tree_id,
            "nodes": created_nodes,
            "wires": [w.model_dump() for w in created_wires],
            "initial_ready_node_ids": initial_ready
        }

    @_persisting
    def resolve_subtask(self, req: ResolveSubtaskRequest) -> Dict[str, Any]:
        """CONTRACT-009: Resolves an atomic subtask, rolls up progress bottom-up, and unlocks dependent nodes."""
        node = self._nodes.get(req.node_id)
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {req.node_id} not found")

        prev_status = node.status
        node.status = "completed" if req.status in ("completed", "done") else req.status
        node.progress = req.progress
        if req.evidence_payload:
            if not node.dto_contract:
                node.dto_contract = {}
            node.dto_contract["evidence"] = req.evidence_payload
        node.updated_at = datetime.now(timezone.utc).isoformat()

        # Recalculate rollup cascade up hierarchy
        if node.parent_id:
            self.recalculate_cascade(node.parent_id)
        else:
            self._recalculate_all_rollup()

        # Check unlocked nodes via DependencyGraph
        unlocked_nodes: List[str] = []
        if node.status in ("completed", "done"):
            dependents = self._dep_graph.get_dependents(node.id)
            for dep_id in dependents:
                dep_node = self._nodes.get(dep_id)
                if not dep_node:
                    continue
                prereqs = self._dep_graph.get_dependencies(dep_id)
                all_done = all(
                    self._nodes.get(p) and self._nodes[p].status in ("completed", "done")
                    for p in prereqs
                )
                if all_done and dep_node.status in ("blocked", "todo"):
                    dep_node.status = "ready"
                    if dep_node.parent_id and self._nodes.get(dep_node.parent_id):
                        parent = self._nodes[dep_node.parent_id]
                        if parent.status == "blocked":
                            parent.status = "ready"
                    unlocked_nodes.append(dep_id)

        # Check if parent Tree is completed
        parent_tree = None
        curr = node
        while curr and curr.plant_scale != "tree":
            curr = self._nodes.get(curr.parent_id) if curr.parent_id else None
        if curr and curr.plant_scale == "tree":
            parent_tree = curr

        is_tree_completed = bool(parent_tree and parent_tree.progress >= 100.0)
        parent_node = self._nodes.get(node.parent_id) if node.parent_id else None
        parent_progress = parent_node.progress if parent_node else node.progress

        # CONTRACT-010 / DEC-019: Hook bidirectional sync back to Docs Portal and Obsidian
        try:
            from apps.api.routers.docs_portal import sync_taskforest_resolution_to_portal
            sync_taskforest_resolution_to_portal(
                node_id=node.id,
                status=node.status,
                progress=node.progress,
                evidence_payload=req.evidence_payload,
            )
        except Exception:
            pass

        root = self._nodes.get("field-001")
        overall = root.progress if root else 0.0

        evt_id = f"evt-{int(time.time() * 1000)}"
        self._history.insert(0, EvolutionHistoryItem(
            event_id=evt_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            node_id=node.id,
            node_title=node.title,
            plant_scale=node.plant_scale,
            mutation_type="resolve",
            previous_status=prev_status,
            new_status=node.status,
            previous_progress=None,
            new_progress=node.progress,
            overall_field_progress=overall,
            description=f"CONTRACT-009: Resolved '{node.title}': unlocked {len(unlocked_nodes)} nodes, tree_done={is_tree_completed}"
        ))

        return {
            "status": "success",
            "node_id": node.id,
            "node_status": node.status,
            "new_parent_progress": parent_progress,
            "unlocked_nodes": unlocked_nodes,
            "is_tree_completed": is_tree_completed
        }


# Global in-memory singleton store
_task_forest_store = TaskForestStore()


@router.get("/graph", response_model=Dict[str, Any])
def get_task_forest_graph():
    """
    Returns full Task Forest graph with Bottom-Up Rollup calculations across all 5 plant levels,
    including active dependency wires.
    Levels: 🌾 Field -> 🏞️ Sector -> 🌳 Tree -> 🌿 Bush -> 🌸 Flower
    """
    tree_root = _task_forest_store.build_tree_graph()
    nodes_flat = {k: v.model_dump() for k, v in _task_forest_store._nodes.items()}
    
    scale_counts = {scale: 0 for scale in PLANT_HIERARCHY_LEVELS}
    for n in _task_forest_store._nodes.values():
        if n.plant_scale in scale_counts:
            scale_counts[n.plant_scale] += 1

    return {
        "status": "success",
        "taxonomy": PLANT_HIERARCHY_LEVELS,
        "plant_icons": PLANT_ICONS,
        "overall_progress": tree_root.progress,
        "root_field": tree_root.model_dump(),
        "total_nodes": len(nodes_flat),
        "scale_counts": scale_counts,
        "nodes": nodes_flat,
        "wires": [w.model_dump() for w in _task_forest_store._wires]
    }


@router.get("/dag", response_model=Dict[str, Any])
def get_task_forest_canon_dag():
    """Canon ThoughtDAG v2 view of the Task Forest (graph, stats, CPM, ready set)."""
    from core.domain.dag_converters import dag_view, forest_to_thoughtdag

    graph = forest_to_thoughtdag(_task_forest_store._nodes.values(), _task_forest_store._wires)
    return {"status": "success", **dag_view(graph)}


@router.get("/vault_graph", response_model=Dict[str, Any])
def get_vault_task_forest_graph():
    """
    Returns compiled Task Forest graph directly parsed from the 16 architectural modules in the Obsidian Vault.
    Contains: 🌾 1 Root Field, 🏞️ 5 Sectors, 🌳 16 Module Trees, 🌿 Bushes (ADRs/CONTRACTS), 🌸 Flowers (SOTA/TASKS).
    """
    nodes, wires = build_vault_task_forest()
    nodes_flat = {n["id"]: n for n in nodes}
    scale_counts = {scale: 0 for scale in PLANT_HIERARCHY_LEVELS}
    for n in nodes:
        sc = n.get("plant_scale")
        if sc in scale_counts:
            scale_counts[sc] += 1

    root_field = next((n for n in nodes if n["plant_scale"] == "field"), None)
    overall_progress = root_field["progress"] if root_field else 88.0

    return {
        "status": "success",
        "taxonomy": PLANT_HIERARCHY_LEVELS,
        "plant_icons": PLANT_ICONS,
        "overall_progress": overall_progress,
        "root_field": root_field,
        "total_nodes": len(nodes),
        "scale_counts": scale_counts,
        "nodes": nodes_flat,
        "wires": wires
    }


@router.post("/node/mutate", response_model=Dict[str, Any])
def mutate_task_forest_node(req: MutateNodeRequest):
    """
    Mutate existing task node or spawn a new flower node with automatic bottom-up cascade.
    """
    res = _task_forest_store.mutate_node(req)
    return res


@router.post("/decompose", response_model=Dict[str, Any])
def decompose_task_forest_goal(req: DecomposeTaskRequest):
    """
    CONTRACT-009: Decompose high-level goal into connected subtask nodes with automatic dependency wires.
    """
    return _task_forest_store.decompose_goal(req)


@router.post("/resolve", response_model=Dict[str, Any])
def resolve_task_forest_subtask(req: ResolveSubtaskRequest):
    """
    CONTRACT-009: Resolve a subtask, trigger bottom-up rollup recalculation, and unlock dependent nodes.
    """
    return _task_forest_store.resolve_subtask(req)


@router.get("/evolution_history", response_model=Dict[str, Any])
def get_task_forest_evolution_history(limit: int = Query(default=50, ge=1, le=500)):
    """
    Returns task mutation history for the Canvas Timeline Scrubber.
    """
    history_slice = _task_forest_store._history[:limit]
    return {
        "status": "success",
        "total_events": len(_task_forest_store._history),
        "events": [h.model_dump() for h in history_slice]
    }


@router.post("/reset", response_model=Dict[str, Any])
def reset_task_forest_baseline():
    """Resets the task forest to the canonical initial baseline."""
    _task_forest_store._init_default_forest()
    return {
        "status": "success",
        "message": "Task forest reset to canonical baseline (88.0% Field Progress)."
    }
