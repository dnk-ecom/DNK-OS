# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_taskboard_canvas_sync.py"
# purpose: "Unit and integration tests for Taskboard-to-Living-Canvas Bi-directional Bridge."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from core.adapters.taskboard_canvas_bridge import (
    TaskboardCanvasBridge,
    TaskboardCanvasPayload,
)
from apps.api.routers.taskboard_canvas_router import router as taskboard_router
from fastapi import FastAPI


@pytest.fixture
def temp_taskboard_db(tmp_path: Path) -> Path:
    """Creates a temporary tasks.sqlite database for isolated testing."""
    db_file = tmp_path / "tasks.sqlite"
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE agent_tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            acceptance_criteria TEXT,
            verification_cmd TEXT,
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            subagent_role TEXT DEFAULT 'Fullstack Engineer',
            scope TEXT DEFAULT '',
            scope_size TEXT DEFAULT 'small',
            product_context TEXT DEFAULT '',
            execution_logs TEXT,
            order_index INTEGER DEFAULT 0,
            processed_by_agent INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            completed_at DATETIME
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE task_comments (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            author TEXT NOT NULL,
            comment_type TEXT NOT NULL,
            content TEXT NOT NULL,
            processed_by_agent INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE task_subtasks (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            order_index INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    # Insert 3 sample tasks
    cur.execute(
        """
        INSERT INTO agent_tasks (id, title, description, status, priority, subagent_role, order_index)
        VALUES ('task-001', 'Task 1: Architect Spec', 'Draft core specification', 'done', 'high', 'Architect', 1),
               ('task-002', 'Task 2: Build Component', 'Construct Living Canvas Node', 'in_progress', 'urgent', 'Fullstack Engineer', 2),
               ('task-003', 'Task 3: Audit Security', 'Run AST verification gate', 'todo', 'medium', 'Auditor', 3);
        """
    )
    # Insert 1 comment
    cur.execute(
        """
        INSERT INTO task_comments (id, task_id, author, comment_type, content)
        VALUES ('comment-001', 'task-002', 'antigravity', 'plan', 'Execution plan approved');
        """
    )
    # Insert subtasks for task-002
    cur.execute(
        """
        INSERT INTO task_subtasks (id, task_id, title, status, order_index)
        VALUES ('sub-001', 'task-002', 'Subtask 1', 'done', 1),
               ('sub-002', 'task-002', 'Subtask 2', 'todo', 2);
        """
    )
    conn.commit()
    conn.close()
    return db_file


def test_bridge_fetch_canvas_payload(temp_taskboard_db: Path):
    bridge = TaskboardCanvasBridge(db_path=temp_taskboard_db)
    payload = bridge.fetch_canvas_payload()

    assert isinstance(payload, TaskboardCanvasPayload)
    assert payload.total_tasks == 3
    assert payload.active_tasks == 1  # task-002 is in_progress

    # Check node 1 (done)
    node1 = next(n for n in payload.nodes if n.id == "task-001")
    assert node1.data.title == "Task 1: Architect Spec"
    assert node1.data.status == "done"
    assert node1.data.progress == 100
    assert node1.data.assignedAgent == "antigravity"
    assert node1.position["x"] == 1370.0  # Done lane

    # Check node 2 (in_progress with subtasks)
    node2 = next(n for n in payload.nodes if n.id == "task-002")
    assert node2.data.title == "Task 2: Build Component"
    assert node2.data.status == "in_progress"
    assert node2.data.progress == 50  # 1 of 2 subtasks done
    assert node2.data.commentCount == 1
    assert node2.data.subtaskCount == 2
    assert node2.data.subtasksDoneCount == 1
    assert node2.data.assignedAgent == "denchik"
    assert node2.position["x"] == 710.0  # In_progress lane

    # Check node 3 (todo)
    node3 = next(n for n in payload.nodes if n.id == "task-003")
    assert node3.data.assignedAgent == "gerych_prime"
    assert node3.position["x"] == 50.0  # Todo lane

    # Check edges
    assert len(payload.edges) == 2
    assert payload.edges[0].source == "task-001"
    assert payload.edges[0].target == "task-002"
    assert payload.edges[1].source == "task-002"
    assert payload.edges[1].target == "task-003"


def test_bridge_update_task_status(temp_taskboard_db: Path):
    bridge = TaskboardCanvasBridge(db_path=temp_taskboard_db)

    # Move task-003 from todo to in_progress
    success = bridge.update_task_status(
        task_id="task-003",
        new_status="in_progress",
        execution_logs="Started execution from canvas node drag",
    )
    assert success is True

    payload = bridge.fetch_canvas_payload()
    node3 = next(n for n in payload.nodes if n.id == "task-003")
    assert node3.data.status == "in_progress"
    assert node3.position["x"] == 710.0

    # Moving to invalid status raises ValueError
    with pytest.raises(ValueError, match="Invalid status: invalid_state"):
        bridge.update_task_status("task-003", "invalid_state")


def test_bridge_real_production_sqlite():
    real_db = Path(".agents/taskboard/tasks.sqlite")
    if not real_db.exists():
        pytest.skip("Production tasks.sqlite not found")

    bridge = TaskboardCanvasBridge(db_path=real_db)
    payload = bridge.fetch_canvas_payload()

    assert payload.total_tasks > 0
    assert len(payload.nodes) == payload.total_tasks
    assert all(n.type == "agentTask" for n in payload.nodes)


def test_fastapi_taskboard_router_integration(temp_taskboard_db: Path, monkeypatch):
    from core.adapters import taskboard_canvas_bridge

    app = FastAPI()
    app.include_router(taskboard_router)

    # Monkeypatch bridge creation to point to test sqlite
    monkeypatch.setattr(
        "apps.api.routers.taskboard_canvas_router.get_bridge",
        lambda: TaskboardCanvasBridge(db_path=temp_taskboard_db),
    )

    client = TestClient(app)

    # 1. GET /api/v1/taskboard/canvas
    res = client.get("/api/v1/taskboard/canvas")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["total_tasks"] == 3

    # 2. POST /api/v1/taskboard/node/status
    post_res = client.post(
        "/api/v1/taskboard/node/status",
        json={"task_id": "task-002", "new_status": "done"},
    )
    assert post_res.status_code == 200
    assert post_res.json()["success"] is True
    assert post_res.json()["new_status"] == "done"

    # Verify updated
    res2 = client.get("/api/v1/taskboard/canvas")
    node2 = next(n for n in res2.json()["nodes"] if n["id"] == "task-002")
    assert node2["data"]["status"] == "done"
