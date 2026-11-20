# --- DNK-MRH-HEADER ---
# mrh_id: "core/adapters/taskboard_canvas_bridge.py"
# purpose: "Bi-directional bridge synchronizing .agents/taskboard/tasks.sqlite with Living XYFlow v12 Canvas nodes and edges."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class CanvasTaskNodeData(BaseModel):
    title: str
    description: str
    status: str
    priority: str
    assignedAgent: str = "denchik"
    progress: int = 0
    commentCount: int = 0
    subtaskCount: int = 0
    subtasksDoneCount: int = 0
    verificationCmd: Optional[str] = None
    scope: Optional[str] = None
    scopeSize: Optional[str] = "small"


class CanvasNode(BaseModel):
    id: str
    type: str = "agentTask"
    position: Dict[str, float]
    data: CanvasTaskNodeData


class CanvasEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str = "smoothstep"
    animated: bool = False
    style: Dict[str, Any] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)


class TaskboardCanvasPayload(BaseModel):
    nodes: List[CanvasNode]
    edges: List[CanvasEdge]
    total_tasks: int
    active_tasks: int


class TaskboardCanvasBridge:
    """
    Bridges SQLite agent_tasks into Living XYFlow Canvas nodes, and updates
    task state back into the taskboard SQLite database.
    """

    LANE_X_POSITIONS = {
        "todo": 50.0,
        "planned": 380.0,
        "in_progress": 710.0,
        "verification": 1040.0,
        "done": 1370.0,
        "failed": 1700.0,
    }

    ROLE_TO_AGENT = {
        "fullstack engineer": "denchik",
        "denchik": "denchik",
        "chief architect": "antigravity",
        "architect": "antigravity",
        "auditor": "gerych_prime",
        "gerych": "gerych_prime",
        "goldfish": "goldfish",
        "strategist": "antigravity",
    }

    STATUS_PROGRESS = {
        "todo": 0,
        "planned": 25,
        "in_progress": 60,
        "verification": 90,
        "done": 100,
        "failed": 0,
    }

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            self.db_path = Path(".agents/taskboard/tasks.sqlite")
        else:
            self.db_path = Path(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        if not self.db_path.exists():
            raise FileNotFoundError(f"Taskboard database not found: {self.db_path}")
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def fetch_canvas_payload(self) -> TaskboardCanvasPayload:
        """
        Reads tasks and generates XYFlow v12 nodes and edges.
        """
        conn = self._get_connection()
        try:
            tasks_cursor = conn.execute(
                """
                SELECT id, title, description, status, priority, subagent_role,
                       scope, scope_size, verification_cmd, order_index
                FROM agent_tasks
                ORDER BY order_index ASC, created_at ASC
                """
            )
            tasks = tasks_cursor.fetchall()

            # Pre-fetch counts
            comment_counts = dict(
                conn.execute(
                    "SELECT task_id, COUNT(*) as c FROM task_comments GROUP BY task_id"
                ).fetchall()
            )
            subtask_stats = conn.execute(
                """
                SELECT task_id,
                       COUNT(*) as total,
                       SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done_cnt
                FROM task_subtasks
                GROUP BY task_id
                """
            ).fetchall()
            subtasks_map = {row["task_id"]: (row["total"], row["done_cnt"]) for row in subtask_stats}

        finally:
            conn.close()

        nodes: List[CanvasNode] = []
        edges: List[CanvasEdge] = []
        lane_counters: Dict[str, int] = {k: 0 for k in self.LANE_X_POSITIONS}

        prev_node_id: Optional[str] = None
        active_count = 0

        for task in tasks:
            status = task["status"] or "todo"
            if status in ("in_progress", "verification"):
                active_count += 1

            x = self.LANE_X_POSITIONS.get(status, 50.0)
            row_idx = lane_counters.get(status, 0)
            y = 80.0 + (row_idx * 190.0)
            lane_counters[status] = row_idx + 1

            role_raw = (task["subagent_role"] or "").strip().lower()
            assigned_agent = self.ROLE_TO_AGENT.get(role_raw, "denchik")

            # Progress calculation
            sub_total, sub_done = subtasks_map.get(task["id"], (0, 0))
            if sub_total > 0:
                progress = int((sub_done / sub_total) * 100)
            else:
                progress = self.STATUS_PROGRESS.get(status, 0)

            node_data = CanvasTaskNodeData(
                title=task["title"],
                description=task["description"] or "",
                status=status,
                priority=task["priority"] or "medium",
                assignedAgent=assigned_agent,
                progress=progress,
                commentCount=comment_counts.get(task["id"], 0),
                subtaskCount=sub_total,
                subtasksDoneCount=sub_done,
                verificationCmd=task["verification_cmd"],
                scope=task["scope"],
                scopeSize=task["scope_size"] or "small",
            )

            nodes.append(
                CanvasNode(
                    id=task["id"],
                    type="agentTask",
                    position={"x": x, "y": y},
                    data=node_data,
                )
            )

            # Sequential flow edge
            if prev_node_id is not None:
                edge_id = f"edge_{prev_node_id}_{task['id']}"
                wire_type = "DIFF" if status == "in_progress" else "CONTEXT"
                color = "#10b981" if wire_type == "DIFF" else "#06b6d4"
                edges.append(
                    CanvasEdge(
                        id=edge_id,
                        source=prev_node_id,
                        target=task["id"],
                        type="smoothstep",
                        animated=(status == "in_progress"),
                        style={"stroke": color, "strokeWidth": 2},
                        data={"wireType": wire_type},
                    )
                )

            prev_node_id = task["id"]

        return TaskboardCanvasPayload(
            nodes=nodes,
            edges=edges,
            total_tasks=len(tasks),
            active_tasks=active_count,
        )

    def update_task_status(
        self,
        task_id: str,
        new_status: str,
        execution_logs: Optional[str] = None,
    ) -> bool:
        """
        Updates task status in SQLite tasks table.
        """
        valid_statuses = {"todo", "planned", "in_progress", "verification", "done", "failed"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {valid_statuses}")

        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE agent_tasks
                SET status = ?,
                    execution_logs = COALESCE(?, execution_logs),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (new_status, execution_logs, task_id),
            )
            conn.commit()
            updated = cur.rowcount > 0
        finally:
            conn.close()

        return updated
