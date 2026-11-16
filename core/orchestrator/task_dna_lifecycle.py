# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/task_dna_lifecycle.py"
# purpose: "TaskDNA Lifecycle Transition Engine & Live Canvas HUD Synchronizer adhering to Anti-Poisoning Protocol"
# canonical_source: true
# alters_files: ["docs/notes/Canvas/Swarm_Live_HUD.canvas"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (dnk_dev_fullstack & gerych_prime)"
# --- END DNK-MRH-HEADER ---

"""
TaskDNA Lifecycle Engine & Live Canvas HUD.
Enforces strict 4-Phase Anti-Poisoning Gated Ingestion:
  RESEARCH_RAW -> AUDIT_GATE -> FOUNDER_APPROVAL -> LIBRARIAN_INGEST -> COMPLETED

Only authorized roles can advance tasks between phases.
Direct memory writes from untrusted agents are strictly prevented.
Automatically renders live execution state into Obsidian JSON Canvas 1.0.
"""

from __future__ import annotations

import enum
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from core.obsidian.json_canvas_builder import (
    CanvasColor,
    CanvasEdge,
    CanvasEnd,
    CanvasSide,
    GroupNode,
    JSONCanvasDocument,
    TextNode,
    generate_canvas_id,
)

logger = logging.getLogger(__name__)


class TaskDNAPhase(str, enum.Enum):
    """Phases of the Anti-Poisoning Gated Ingestion Lifecycle."""
    RESEARCH_RAW = "RESEARCH_RAW"
    AUDIT_GATE = "AUDIT_GATE"
    FOUNDER_APPROVAL = "FOUNDER_APPROVAL"
    LIBRARIAN_INGEST = "LIBRARIAN_INGEST"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class AgentRole(str, enum.Enum):
    """Swarm roles authorized to perform specific lifecycle transitions."""
    RESEARCHER = "gerych_researcher"
    AUDITOR = "gerych_auditor"
    FOUNDER = "maxim_founder"
    LIBRARIAN = "herich_librarian"
    SYSTEM = "dnk_system"


class SecurityGateResult(str, enum.Enum):
    """Audit gate outcomes."""
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    FLAGGED = "FLAGGED"


@dataclass
class AuditReport:
    """Security audit details for a TaskDNA slice."""
    auditor: str
    status: SecurityGateResult
    score: float  # 0.0 - 1.0 (1.0 = 100% clean)
    issues: List[str] = field(default_factory=list)
    tested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TaskDNASlice:
    """Atomic TaskDNA unit tracking research, code, or memory ingest item."""
    id: str
    title: str
    phase: TaskDNAPhase = TaskDNAPhase.RESEARCH_RAW
    assigned_agent: str = AgentRole.RESEARCHER.value
    content: str = ""
    source_url: Optional[str] = None
    target_vault_path: Optional[str] = None
    target_memory_topic: Optional[str] = None
    audit_report: Optional[AuditReport] = None
    founder_decision: Optional[str] = None
    founder_feedback: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["phase"] = self.phase.value
        if self.audit_report:
            data["audit_report"]["status"] = self.audit_report.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskDNASlice:
        d = dict(data)
        d["phase"] = TaskDNAPhase(d["phase"])
        if d.get("audit_report"):
            ar = d["audit_report"]
            d["audit_report"] = AuditReport(
                auditor=ar["auditor"],
                status=SecurityGateResult(ar["status"]),
                score=float(ar["score"]),
                issues=list(ar.get("issues", [])),
                tested_at=ar.get("tested_at", ""),
            )
        return cls(**d)


class LifecycleSecurityViolation(Exception):
    """Raised when an unauthorized agent attempts an illegal phase transition."""
    pass


class TaskDNALifecycleEngine:
    """
    Orchestrates TaskDNA slices across the Anti-Poisoning state machine.
    Enforces strict role permissions:
      - Only RESEARCHER or SYSTEM can create RESEARCH_RAW tasks.
      - Only AUDITOR can advance RESEARCH_RAW -> AUDIT_GATE -> FOUNDER_APPROVAL.
      - Only FOUNDER can approve/reject from FOUNDER_APPROVAL.
      - Only LIBRARIAN can ingest from FOUNDER_APPROVAL (with approved decision) -> LIBRARIAN_INGEST -> COMPLETED.
    """

    ALLOWED_TRANSITIONS: Dict[TaskDNAPhase, Set[TaskDNAPhase]] = {
        TaskDNAPhase.RESEARCH_RAW: {TaskDNAPhase.AUDIT_GATE, TaskDNAPhase.REJECTED},
        TaskDNAPhase.AUDIT_GATE: {TaskDNAPhase.FOUNDER_APPROVAL, TaskDNAPhase.REJECTED},
        TaskDNAPhase.FOUNDER_APPROVAL: {TaskDNAPhase.LIBRARIAN_INGEST, TaskDNAPhase.REJECTED},
        TaskDNAPhase.LIBRARIAN_INGEST: {TaskDNAPhase.COMPLETED, TaskDNAPhase.REJECTED},
        TaskDNAPhase.COMPLETED: set(),
        TaskDNAPhase.REJECTED: {TaskDNAPhase.RESEARCH_RAW},  # allow rework
    }

    ROLE_PERMISSIONS: Dict[TaskDNAPhase, Set[str]] = {
        TaskDNAPhase.RESEARCH_RAW: {AgentRole.RESEARCHER.value, AgentRole.SYSTEM.value, AgentRole.FOUNDER.value},
        TaskDNAPhase.AUDIT_GATE: {AgentRole.AUDITOR.value, AgentRole.SYSTEM.value},
        TaskDNAPhase.FOUNDER_APPROVAL: {AgentRole.AUDITOR.value, AgentRole.SYSTEM.value},
        TaskDNAPhase.LIBRARIAN_INGEST: {AgentRole.FOUNDER.value, AgentRole.LIBRARIAN.value, AgentRole.SYSTEM.value},
        TaskDNAPhase.COMPLETED: {AgentRole.LIBRARIAN.value, AgentRole.SYSTEM.value},
        TaskDNAPhase.REJECTED: {AgentRole.AUDITOR.value, AgentRole.FOUNDER.value, AgentRole.SYSTEM.value},
    }

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else None
        self._tasks: Dict[str, TaskDNASlice] = {}
        if self.storage_path and self.storage_path.exists():
            self.load()

    def register_task(
        self,
        title: str,
        content: str,
        task_id: Optional[str] = None,
        source_url: Optional[str] = None,
        target_vault_path: Optional[str] = None,
        target_memory_topic: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        creator_role: str = AgentRole.RESEARCHER.value,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TaskDNASlice:
        """Create a new TaskDNA slice in RESEARCH_RAW phase."""
        if creator_role not in self.ROLE_PERMISSIONS[TaskDNAPhase.RESEARCH_RAW]:
            raise LifecycleSecurityViolation(
                f"Role '{creator_role}' is not authorized to register RESEARCH_RAW tasks."
            )

        tid = task_id or f"task_{uuid.uuid4().hex[:8]}"
        slice_item = TaskDNASlice(
            id=tid,
            title=title,
            phase=TaskDNAPhase.RESEARCH_RAW,
            assigned_agent=creator_role,
            content=content,
            source_url=source_url,
            target_vault_path=target_vault_path,
            target_memory_topic=target_memory_topic,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )
        self._tasks[tid] = slice_item
        self._auto_save()
        logger.info(f"TaskDNA registered: {tid} ('{title}') by {creator_role}")
        return slice_item

    def get_task(self, task_id: str) -> Optional[TaskDNASlice]:
        return self._tasks.get(task_id)

    def list_tasks(self, phase: Optional[TaskDNAPhase] = None) -> List[TaskDNASlice]:
        tasks = list(self._tasks.values())
        if phase:
            return [t for t in tasks if t.phase == phase]
        return tasks

    def submit_for_audit(self, task_id: str, actor_role: str) -> TaskDNASlice:
        """Move task from RESEARCH_RAW to AUDIT_GATE."""
        task = self._must_get_task(task_id)
        self._validate_transition(task, TaskDNAPhase.AUDIT_GATE, actor_role)
        task.phase = TaskDNAPhase.AUDIT_GATE
        task.assigned_agent = AgentRole.AUDITOR.value
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self._auto_save()
        return task

    def record_audit_result(
        self,
        task_id: str,
        auditor_role: str,
        status: SecurityGateResult,
        score: float,
        issues: Optional[List[str]] = None,
    ) -> TaskDNASlice:
        """
        Record auditor evaluation.
        If PASSED: advances to FOUNDER_APPROVAL.
        If FAILED: marks REJECTED.
        """
        task = self._must_get_task(task_id)
        if auditor_role not in {AgentRole.AUDITOR.value, AgentRole.SYSTEM.value}:
            raise LifecycleSecurityViolation(
                f"Role '{auditor_role}' cannot record audit results. Must be '{AgentRole.AUDITOR.value}'."
            )
        if task.phase != TaskDNAPhase.AUDIT_GATE:
            raise LifecycleSecurityViolation(
                f"Task {task_id} is in phase {task.phase.value}, cannot audit."
            )

        task.audit_report = AuditReport(
            auditor=auditor_role,
            status=status,
            score=max(0.0, min(1.0, score)),
            issues=issues or [],
        )

        target_phase = (
            TaskDNAPhase.FOUNDER_APPROVAL
            if status == SecurityGateResult.PASSED
            else TaskDNAPhase.REJECTED
        )
        task.phase = target_phase
        task.assigned_agent = (
            AgentRole.FOUNDER.value
            if target_phase == TaskDNAPhase.FOUNDER_APPROVAL
            else AgentRole.RESEARCHER.value
        )
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self._auto_save()
        return task

    def founder_decision(
        self,
        task_id: str,
        approved: bool,
        feedback: str = "",
        actor_role: str = AgentRole.FOUNDER.value,
    ) -> TaskDNASlice:
        """Founder reviews task in FOUNDER_APPROVAL phase."""
        task = self._must_get_task(task_id)
        if actor_role not in {AgentRole.FOUNDER.value, AgentRole.SYSTEM.value}:
            raise LifecycleSecurityViolation(
                f"Only Founder ('{AgentRole.FOUNDER.value}') can decide approval."
            )
        if task.phase != TaskDNAPhase.FOUNDER_APPROVAL:
            raise LifecycleSecurityViolation(
                f"Task {task_id} is in phase {task.phase.value}, not pending founder approval."
            )

        task.founder_decision = "APPROVED" if approved else "REJECTED"
        task.founder_feedback = feedback

        if approved:
            task.phase = TaskDNAPhase.LIBRARIAN_INGEST
            task.assigned_agent = AgentRole.LIBRARIAN.value
        else:
            task.phase = TaskDNAPhase.REJECTED
            task.assigned_agent = AgentRole.RESEARCHER.value

        task.updated_at = datetime.now(timezone.utc).isoformat()
        self._auto_save()
        return task

    def complete_ingest(
        self,
        task_id: str,
        ingested_vault_path: Optional[str] = None,
        ingested_memory_key: Optional[str] = None,
        actor_role: str = AgentRole.LIBRARIAN.value,
    ) -> TaskDNASlice:
        """Librarian ingests approved slice into Obsidian / SCONES and completes task."""
        task = self._must_get_task(task_id)
        if actor_role not in {AgentRole.LIBRARIAN.value, AgentRole.SYSTEM.value}:
            raise LifecycleSecurityViolation(
                f"Role '{actor_role}' cannot ingest. Must be '{AgentRole.LIBRARIAN.value}'."
            )
        if task.phase != TaskDNAPhase.LIBRARIAN_INGEST:
            raise LifecycleSecurityViolation(
                f"Task {task_id} is in phase {task.phase.value}, must be LIBRARIAN_INGEST."
            )
        if task.founder_decision != "APPROVED":
            raise LifecycleSecurityViolation(
                f"Task {task_id} lacks explicit Founder Approval."
            )

        if ingested_vault_path:
            task.target_vault_path = ingested_vault_path
        if ingested_memory_key:
            task.metadata["memory_key"] = ingested_memory_key

        task.phase = TaskDNAPhase.COMPLETED
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self._auto_save()
        return task

    # -------------------------------------------------------------------------
    # Visual JSON Canvas 1.0 Live HUD Sync
    # -------------------------------------------------------------------------

    def sync_to_canvas(
        self,
        canvas_rel_path: str = "docs/notes/Canvas/Swarm_Live_HUD.canvas",
    ) -> JSONCanvasDocument:
        """
        Renders the active TaskDNA pipeline into an interactive Obsidian Canvas (v1.0).
        Columns:
          1. Research Raw (Yellow)
          2. Security Audit Gate (Cyan)
          3. Founder Approval HITL (Purple)
          4. Ingestion (Cyan)
          5. Completed (Green)
        """
        nodes: List[Any] = []
        edges: List[Any] = []

        phase_config = [
            (TaskDNAPhase.RESEARCH_RAW, "1. Research Raw (Unverified)", CanvasColor.YELLOW, 0),
            (TaskDNAPhase.AUDIT_GATE, "2. Security & Quality Gate", CanvasColor.CYAN, 460),
            (TaskDNAPhase.FOUNDER_APPROVAL, "3. Founder Approval (HITL)", CanvasColor.PURPLE, 920),
            (TaskDNAPhase.LIBRARIAN_INGEST, "4. Librarian Ingestion", CanvasColor.CYAN, 1380),
            (TaskDNAPhase.COMPLETED, "5. Permanent Vault & SCONES", CanvasColor.GREEN, 1840),
        ]

        node_id_map: Dict[str, str] = {}
        card_w = 380

        for phase, group_label, color, col_x in phase_config:
            tasks_in_phase = self.list_tasks(phase=phase)
            group_y = 0
            card_y = group_y + 80
            group_h = max(600, len(tasks_in_phase) * 260 + 120)

            group_node_id = generate_canvas_id(f"group_{phase.value}")
            nodes.append(
                GroupNode(
                    id=group_node_id,
                    label=f"{group_label} ({len(tasks_in_phase)})",
                    x=col_x,
                    y=group_y,
                    width=420,
                    height=group_h,
                    color=color,
                )
            )

            # Task Cards
            for task in tasks_in_phase:
                card_node_id = generate_canvas_id(f"card_{task.id}")
                node_id_map[task.id] = card_node_id

                audit_info = ""
                if task.audit_report:
                    audit_info = f"\n- **Audit:** `{task.audit_report.status.value}` ({task.audit_report.score:.2f})"
                founder_info = ""
                if task.founder_decision:
                    founder_info = f"\n- **Founder:** `{task.founder_decision}`"

                vault_info = f"\n- **Vault:** `[[{task.target_vault_path}]]`" if task.target_vault_path else ""

                card_text = (
                    f"### {task.title}\n"
                    f"- **ID:** `{task.id}`\n"
                    f"- **Agent:** `{task.assigned_agent}`\n"
                    f"- **Phase:** `{task.phase.value}`"
                    f"{audit_info}"
                    f"{founder_info}"
                    f"{vault_info}\n\n"
                    f"{task.content[:160]}..."
                )

                nodes.append(
                    TextNode(
                        id=card_node_id,
                        text=card_text,
                        x=col_x + 20,
                        y=card_y,
                        width=card_w,
                        height=220,
                        color=color,
                    )
                )
                card_y += 240

        # Draw dependency edges
        for task in self.list_tasks():
            src_node = node_id_map.get(task.id)
            if not src_node:
                continue
            for dep_id in task.dependencies:
                target_node = node_id_map.get(dep_id)
                if target_node:
                    edge_id = generate_canvas_id(f"edge_{dep_id}_{task.id}")
                    edges.append(
                        CanvasEdge(
                            id=edge_id,
                            from_node=target_node,
                            to_node=src_node,
                            from_side=CanvasSide.RIGHT,
                            to_side=CanvasSide.LEFT,
                            to_end=CanvasEnd.ARROW,
                            label="depends_on",
                        )
                    )

        doc = JSONCanvasDocument(nodes=nodes, edges=edges)

        # Auto-export if path is provided
        if canvas_rel_path:
            out_file = Path(canvas_rel_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(doc.to_json(indent=2))
            logger.info(f"Swarm Live HUD Canvas synced to {canvas_rel_path}")

        return doc

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    def _must_get_task(self, task_id: str) -> TaskDNASlice:
        task = self._tasks.get(task_id)
        if not task:
            raise KeyError(f"Task with id '{task_id}' not found.")
        return task

    def _validate_transition(
        self,
        task: TaskDNASlice,
        target_phase: TaskDNAPhase,
        actor_role: str,
    ) -> None:
        allowed = self.ALLOWED_TRANSITIONS.get(task.phase, set())
        if target_phase not in allowed:
            raise LifecycleSecurityViolation(
                f"Illegal phase transition from '{task.phase.value}' to '{target_phase.value}'."
            )
        permitted_roles = self.ROLE_PERMISSIONS.get(target_phase, set())
        if actor_role not in permitted_roles:
            raise LifecycleSecurityViolation(
                f"Role '{actor_role}' is not authorized to transition tasks to '{target_phase.value}'. "
                f"Allowed roles: {permitted_roles}"
            )

    def _auto_save(self) -> None:
        if not self.storage_path:
            return
        self.save()

    def save(self) -> None:
        if not self.storage_path:
            return
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {tid: t.to_dict() for tid, t in self._tasks.items()}
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> None:
        if not self.storage_path or not self.storage_path.exists():
            return
        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._tasks = {tid: TaskDNASlice.from_dict(t) for tid, t in data.items()}
