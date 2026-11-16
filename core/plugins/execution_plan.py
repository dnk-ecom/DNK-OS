# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/execution_plan.py"
# purpose: "DNK OS Plugin Execution Plan Engine MVP v0.1"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


def is_relative_path(path: Optional[str]) -> bool:
    """Check if a path is strictly relative and contains no unsafe escapes."""
    if not path or not isinstance(path, str):
        return False
    if os.path.isabs(path):
        return False
    if path.startswith("/") or path.startswith("\\") or path.startswith("~"):
        return False
    norm = os.path.normpath(path)
    if norm == ".." or norm.startswith("../") or norm.startswith("..\\"):
        return False
    return True


class ExecutionStep(BaseModel):
    """Single step in an execution plan representing a plugin capability invocation."""

    step_id: int
    plugin_id: str = ""
    capability: str = ""
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("step_id")
    @classmethod
    def check_step_id(cls, v: int) -> int:
        if v < 1:
            raise ValueError(f"step_id must be >= 1, got {v}")
        return v


class ExecutionPlan(BaseModel):
    """Complete execution plan for a DNK OS task based on plugin capability graph."""

    schema_version: str = "dnk-execution-plan/v1.0"
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    task_id: str
    description: str = ""
    steps: List[ExecutionStep] = Field(default_factory=list)
    total_steps: int = 0
    status: str = "draft"  # draft | validated | blocked

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"draft", "validated", "blocked"}
        if v not in allowed:
            raise ValueError(f"Status '{v}' is not allowed. Must be one of: {allowed}")
        return v

    @model_validator(mode="after")
    def sync_total_steps(self) -> "ExecutionPlan":
        if self.total_steps == 0 and len(self.steps) > 0:
            self.total_steps = len(self.steps)
        elif len(self.steps) == 0:
            self.total_steps = 0
        return self


class PluginExecutionPlanEngine:
    """Engine for building, managing, and validating plugin execution plans."""

    def __init__(
        self,
        graph_path: str = "templates/plugin/capability_graph.json",
        plans_dir: str = "templates/plugin/execution_plans",
        index_path: str = "templates/plugin/plugins_index.json",
    ):
        if not is_relative_path(graph_path):
            raise ValueError(f"Graph path must be relative: {graph_path}")
        if not is_relative_path(plans_dir):
            raise ValueError(f"Plans directory must be relative: {plans_dir}")
        if not is_relative_path(index_path):
            raise ValueError(f"Index path must be relative: {index_path}")

        norm_graph = os.path.normpath(graph_path)
        if not os.path.exists(norm_graph) and os.path.exists(os.path.join("core", norm_graph)):
            norm_graph = os.path.normpath(os.path.join("core", norm_graph))
        self.graph_path = norm_graph

        norm_plans = os.path.normpath(plans_dir)
        if not os.path.exists(norm_plans) and os.path.exists(os.path.join("core", norm_plans)):
            norm_plans = os.path.normpath(os.path.join("core", norm_plans))
        self.plans_dir = norm_plans

        norm_index = os.path.normpath(index_path)
        if not os.path.exists(norm_index) and os.path.exists(os.path.join("core", norm_index)):
            norm_index = os.path.normpath(os.path.join("core", norm_index))
        self.index_path = norm_index

    def load_capability_graph(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Load capability graph data from JSON file."""
        target_path = path or self.graph_path
        if not is_relative_path(target_path):
            raise ValueError(f"Capability graph path must be relative: {target_path}")

        if not os.path.exists(target_path) and os.path.exists(os.path.join("core", target_path)):
            target_path = os.path.normpath(os.path.join("core", target_path))

        if not os.path.exists(target_path):
            return {"schema_version": "dnk-capability-graph/v1.0", "nodes": [], "edges": []}

        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_providers_for_capability(
        self, capability: str, graph_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Find plugin IDs that provide the given capability."""
        if not capability or not isinstance(capability, str):
            return []
        target_cap = capability.strip()
        providers: List[str] = []

        # 1. Try reading directly from plugin cards via index if available
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
                for entry in index_data.get("entries", []):
                    card_path = entry.get("card_path")
                    if card_path and is_relative_path(card_path) and os.path.exists(card_path):
                        with open(card_path, "r", encoding="utf-8") as cf:
                            card = yaml.safe_load(cf) or {}
                        caps = card.get("capabilities", {})
                        if isinstance(caps, dict):
                            provided = caps.get("provides") or []
                            if target_cap in provided:
                                pid = card.get("id") or card.get("plugin_id")
                                if pid and pid not in providers:
                                    providers.append(pid)
            except Exception:
                pass

        if providers:
            return sorted(providers)

        # 2. Fall back to capability graph data
        data = graph_data if graph_data is not None else self.load_capability_graph()
        # Look in edges where from_capability == target_cap
        for edge in data.get("edges", []):
            if edge.get("from_capability") == target_cap:
                fp = edge.get("from_plugin")
                if fp and fp not in providers:
                    providers.append(fp)

        # Look in nodes
        if not providers:
            for node in data.get("nodes", []):
                if node.get("capability") == target_cap:
                    pid = node.get("plugin_id")
                    if pid and pid not in providers:
                        providers.append(pid)

        return sorted(providers)

    def create_plan(
        self,
        task_id: str,
        description: str,
        required_capabilities: List[str],
        graph_data: Optional[Dict[str, Any]] = None,
    ) -> ExecutionPlan:
        """Create a new execution plan in 'draft' status with steps for each capability."""
        if not task_id or not isinstance(task_id, str):
            raise ValueError("task_id must be a non-empty string")

        steps: List[ExecutionStep] = []
        data = graph_data if graph_data is not None else self.load_capability_graph()

        for idx, cap in enumerate(required_capabilities, start=1):
            cap_clean = cap.strip() if isinstance(cap, str) else ""
            providers = self.get_providers_for_capability(cap_clean, data)
            plugin_id = providers[0] if providers else ""
            step = ExecutionStep(
                step_id=idx,
                plugin_id=plugin_id,
                capability=cap_clean,
                input_schema={},
                output_schema={},
            )
            steps.append(step)

        plan = ExecutionPlan(
            task_id=task_id.strip(),
            description=description.strip() if description else "",
            steps=steps,
            total_steps=len(steps),
            status="draft",
        )
        return plan

    def validate_plan(
        self,
        plan: ExecutionPlan,
        graph_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Validate execution plan steps against capability providers.

        Sets and returns status:
          - 'validated': all steps have valid plugin providers
          - 'blocked': one or more steps have no provider
        """
        data = graph_data if graph_data is not None else self.load_capability_graph()

        if not plan.steps:
            # Plan with empty steps: validated by default or stays draft?
            # A plan with 0 steps has no missing providers.
            plan.status = "validated"
            return "validated"

        all_valid = True
        for step in plan.steps:
            providers = self.get_providers_for_capability(step.capability, data)
            if not step.plugin_id or step.plugin_id == "":
                # Try auto-assigning if provider exists now
                if providers:
                    step.plugin_id = providers[0]
                else:
                    all_valid = False
            else:
                if step.plugin_id not in providers:
                    all_valid = False

        plan.status = "validated" if all_valid else "blocked"
        return plan.status

    def resolve_plan_path(self, task_id_or_path: str) -> str:
        """Resolve a task_id or relative file path to a verified relative path."""
        if not is_relative_path(task_id_or_path):
            raise ValueError(f"Path or task_id must be relative: {task_id_or_path}")

        candidate = task_id_or_path if (task_id_or_path.endswith(".json") or os.path.isfile(task_id_or_path)) else os.path.join(self.plans_dir, f"{task_id_or_path}.json")
        if not os.path.exists(candidate) and os.path.exists(os.path.join("core", candidate)):
            return os.path.normpath(os.path.join("core", candidate))
        return candidate

    def save_plan(self, plan: ExecutionPlan, output_path: Optional[str] = None) -> str:
        """Save execution plan as JSON to disk using strictly relative path."""
        target_path = output_path or self.resolve_plan_path(plan.task_id)
        if not is_relative_path(target_path):
            raise ValueError(f"Output path must be relative: {target_path}")

        parent_dir = os.path.dirname(target_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(plan.model_dump_json(indent=2) + "\n")

        return target_path

    def load_plan(self, task_id_or_path: str) -> ExecutionPlan:
        """Load execution plan from file using task_id or relative path."""
        target_path = self.resolve_plan_path(task_id_or_path)
        if not is_relative_path(target_path):
            raise ValueError(f"Plan path must be relative: {target_path}")

        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Execution plan not found: {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ExecutionPlan.model_validate(data)
