# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/execution_engine.py"
# purpose: "Plugin Execution Engine MVP v0.1"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import glob
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml
from pydantic import BaseModel, Field

from core.plugins.execution_plan import ExecutionPlan, ExecutionStep, PluginExecutionPlanEngine
from core.plugins.models import (
    PluginCard,
    PluginLifecycle,
    SandboxExecutionPlan,
    SandboxExecutionResult,
    SandboxStatus,
)
from core.plugins.policy import PluginPolicyError, validate_plugin_card_file
from core.plugins.sandbox_runner import PluginSandboxRunner


class ExecutionRun(BaseModel):
    run_id: str
    task_id: str
    plan_path: str
    started_at: str
    finished_at: Optional[str] = None
    status: str = "running"  # running | completed | failed | blocked


class ExecutionStepResult(BaseModel):
    step_id: int
    plugin_id: str
    capability: str
    status: str  # completed | failed | blocked
    output: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ExecutionResult(BaseModel):
    run_id: str
    task_id: str
    status: str  # completed | failed | blocked
    steps: List[ExecutionStepResult] = Field(default_factory=list)
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    blocked_steps: int = 0


class EngineSandboxRunner(PluginSandboxRunner):
    """Sandbox runner tailored for Execution Engine supporting sandbox and active fixture plugins."""

    def build_plan(self, card_path: Union[str, Path]) -> SandboxExecutionPlan:
        valid, errors, card = validate_plugin_card_file(card_path)
        if not valid or card is None:
            raise PluginPolicyError(
                f"Invalid plugin card: {'; '.join(errors)}"
            )

        violations: List[str] = []
        lifecycle_str = (
            card.lifecycle.value
            if hasattr(card.lifecycle, "value")
            else str(card.lifecycle)
        )
        if lifecycle_str not in ("sandbox", "active"):
            violations.append(
                f"Lifecycle must be 'sandbox' or 'active', got '{lifecycle_str}'"
            )

        if card.permissions.network != "none":
            violations.append(
                f"Network permission must be 'none', got '{card.permissions.network}'"
            )
        if card.permissions.secrets != "none":
            violations.append(
                f"Secrets permission must be 'none', got '{card.permissions.secrets}'"
            )
        if card.permissions.git != "none":
            violations.append(
                f"Git permission must be 'none', got '{card.permissions.git}'"
            )
        if card.permissions.database != "none":
            violations.append(
                f"Database permission must be 'none', got '{card.permissions.database}'"
            )
        if card.permissions.external_write != "none":
            violations.append(
                f"External write permission must be 'none', got '{card.permissions.external_write}'"
            )

        if card.entrypoint.type != "python":
            violations.append(
                f"Entrypoint type must be 'python', got '{card.entrypoint.type}'"
            )

        ref = card.entrypoint.reference or ""
        ref_norm = ref.replace("\\", "/")
        if not (
            ref_norm.startswith("templates/plugin/fixtures/")
            or "/templates/plugin/fixtures/" in ref_norm
            or ref_norm.startswith("core/templates/plugin/fixtures/")
            or "/core/templates/plugin/fixtures/" in ref_norm
        ):
            violations.append(
                f"Entrypoint reference must reside in 'templates/plugin/fixtures/', got '{ref}'"
            )

        if violations:
            raise PluginPolicyError(
                f"Execution engine policy check failed: {'; '.join(violations)}"
            )

        fs_allowed = (
            "workspace_readonly"
            if card.permissions.filesystem != "none"
            else "none"
        )

        return SandboxExecutionPlan(
            plugin_id=card.id,
            lifecycle="sandbox",
            entrypoint_type="python",
            allowed_filesystem=fs_allowed,
            network="none",
            secrets="none",
            git="none",
            database="none",
            external_write="none",
            temporary_workspace=True,
            max_execution_seconds=5,
            max_output_chars=4000,
        )


class PluginExecutionEngine:
    """Execution Engine for executing Execution Plans through Sandbox Runner."""

    def __init__(
        self,
        plugins_root: str = "core/templates/plugin",
        runs_dir: str = "core/templates/plugin/execution_runs",
        results_dir: str = "core/templates/plugin/execution_results",
    ):
        self.assert_relative_path(plugins_root)
        self.assert_relative_path(runs_dir)
        self.assert_relative_path(results_dir)

        norm_root = os.path.normpath(plugins_root)
        if not os.path.exists(norm_root) and os.path.exists(os.path.join("core", norm_root)):
            norm_root = os.path.normpath(os.path.join("core", norm_root))
        self.plugins_root = norm_root

        norm_runs = os.path.normpath(runs_dir)
        if not os.path.exists(norm_runs) and os.path.exists(os.path.join("core", norm_runs)):
            norm_runs = os.path.normpath(os.path.join("core", norm_runs))
        self.runs_dir = norm_runs

        norm_results = os.path.normpath(results_dir)
        if not os.path.exists(norm_results) and os.path.exists(os.path.join("core", norm_results)):
            norm_results = os.path.normpath(os.path.join("core", norm_results))
        self.results_dir = norm_results

    @staticmethod
    def is_relative_path(path: Union[str, Path]) -> bool:
        """Checks whether path is strictly relative and does not escape workspace."""
        path_str = str(path).strip()
        if not path_str:
            return True
        if os.path.isabs(path_str) or path_str.startswith("/"):
            return False
        normalized = os.path.normpath(path_str)
        if normalized == ".." or normalized.startswith("../"):
            return False
        return True

    @classmethod
    def assert_relative_path(cls, path: Union[str, Path]) -> None:
        """Enforces that a path is strictly relative and within workspace."""
        if not cls.is_relative_path(path):
            raise ValueError(f"Path must be relative and within workspace, got: {path}")

    def find_plugin_card(self, plugin_id: str) -> Optional[str]:
        """Finds the relative path to a plugin card matching plugin_id."""
        if not plugin_id:
            return None

        patterns = [
            os.path.join(self.plugins_root, "*.yaml"),
            os.path.join(self.plugins_root, "**", "*.yaml"),
        ]
        if not self.plugins_root.startswith("core/"):
            patterns.extend([
                os.path.join("core", self.plugins_root, "*.yaml"),
                os.path.join("core", self.plugins_root, "**", "*.yaml"),
            ])
        scanned: set[str] = set()
        for pat in patterns:
            for filepath in glob.glob(pat, recursive=True):
                norm_path = os.path.normpath(filepath).replace("\\", "/")
                if norm_path in scanned:
                    continue
                scanned.add(norm_path)
                try:
                    with open(norm_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    if isinstance(data, dict) and data.get("id") == plugin_id:
                        return norm_path
                except Exception:
                    continue
        return None

    def execute_plan(
        self,
        plan_input: Union[ExecutionPlan, str, Path],
        inputs: Optional[Dict[Any, Any]] = None,
        save: bool = True,
    ) -> Tuple[ExecutionRun, ExecutionResult]:
        """Executes an execution plan and produces ExecutionRun and ExecutionResult."""
        plan_path_str = ""
        if isinstance(plan_input, (str, Path)):
            plan_path_str = str(plan_input)
            self.assert_relative_path(plan_path_str)
            plan_engine = PluginExecutionPlanEngine()
            plan = plan_engine.load_plan(plan_path_str)
        elif isinstance(plan_input, ExecutionPlan):
            plan = plan_input
            plan_path_str = f"templates/plugin/execution_plans/{plan.task_id}.json"
        else:
            raise TypeError(
                f"Expected ExecutionPlan, str, or Path, got {type(plan_input)}"
            )

        run_id = f"run-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        run = ExecutionRun(
            run_id=run_id,
            task_id=plan.task_id,
            plan_path=plan_path_str,
            started_at=now_iso,
            status="running",
        )

        step_results: List[ExecutionStepResult] = []
        runner = EngineSandboxRunner()

        inputs_dict: Dict[Any, Any] = inputs or {}

        for step in plan.steps:
            # 1. Check if plugin_id is assigned
            if not step.plugin_id or not step.plugin_id.strip():
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"No plugin assigned for capability '{step.capability}'",
                    )
                )
                continue

            # 2. Find plugin in Registry / plugins_root
            card_path = self.find_plugin_card(step.plugin_id)
            if not card_path:
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"Plugin '{step.plugin_id}' not found in registry",
                    )
                )
                continue

            # 3. Load & validate card rules
            valid, card_errors, card = validate_plugin_card_file(card_path)
            if not valid or card is None:
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"Invalid plugin card: {'; '.join(card_errors)}",
                    )
                )
                continue

            lifecycle_str = (
                card.lifecycle.value
                if hasattr(card.lifecycle, "value")
                else str(card.lifecycle)
            )
            if lifecycle_str not in ("sandbox", "active"):
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=(
                            f"Plugin lifecycle '{lifecycle_str}' is not allowed for execution "
                            f"(must be 'sandbox' or 'active')"
                        ),
                    )
                )
                continue

            # Check permissions
            if card.permissions.network != "none":
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"Forbidden network permission: '{card.permissions.network}' (must be 'none')",
                    )
                )
                continue

            if card.permissions.secrets != "none":
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"Forbidden secrets permission: '{card.permissions.secrets}' (must be 'none')",
                    )
                )
                continue

            if card.permissions.git != "none":
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"Forbidden git permission: '{card.permissions.git}' (must be 'none')",
                    )
                )
                continue

            if card.permissions.database != "none":
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"Forbidden database permission: '{card.permissions.database}' (must be 'none')",
                    )
                )
                continue

            if card.permissions.external_write != "none":
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"Forbidden external_write permission: '{card.permissions.external_write}' (must be 'none')",
                    )
                )
                continue

            # Check entrypoint
            if card.entrypoint.type != "python":
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=f"Plugin entrypoint type '{card.entrypoint.type}' is blocked (must be 'python')",
                    )
                )
                continue

            ref = card.entrypoint.reference or ""
            ref_norm = ref.replace("\\", "/")
            if not (
                ref_norm.startswith("templates/plugin/fixtures/")
                or "/templates/plugin/fixtures/" in ref_norm
                or ref_norm.startswith("core/templates/plugin/fixtures/")
                or "/core/templates/plugin/fixtures/" in ref_norm
            ):
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="blocked",
                        output={},
                        error=(
                            f"Engine does not execute external plugins: entrypoint "
                            f"must reside in 'templates/plugin/fixtures/', got '{ref}'"
                        ),
                    )
                )
                continue

            # 4. Prepare payload and execute via sandbox runner
            step_payload = (
                inputs_dict.get(str(step.step_id))
                or inputs_dict.get(step.step_id)
                or step.input_schema
                or {}
            )

            try:
                sb_res = runner.run(card_path, payload=step_payload)
                if sb_res.status == SandboxStatus.COMPLETED:
                    step_results.append(
                        ExecutionStepResult(
                            step_id=step.step_id,
                            plugin_id=step.plugin_id,
                            capability=step.capability,
                            status="completed",
                            output=sb_res.output,
                            error=None,
                        )
                    )
                elif sb_res.status == SandboxStatus.BLOCKED:
                    step_results.append(
                        ExecutionStepResult(
                            step_id=step.step_id,
                            plugin_id=step.plugin_id,
                            capability=step.capability,
                            status="blocked",
                            output=sb_res.output,
                            error=sb_res.reason or "Blocked by sandbox policy",
                        )
                    )
                else:
                    step_results.append(
                        ExecutionStepResult(
                            step_id=step.step_id,
                            plugin_id=step.plugin_id,
                            capability=step.capability,
                            status="failed",
                            output=sb_res.output,
                            error=sb_res.reason or "Execution failed in sandbox",
                        )
                    )
            except Exception as ex:
                step_results.append(
                    ExecutionStepResult(
                        step_id=step.step_id,
                        plugin_id=step.plugin_id,
                        capability=step.capability,
                        status="failed",
                        output={},
                        error=f"Execution error: {str(ex)}",
                    )
                )

        # 5. Compute totals & status
        total = len(step_results)
        completed = sum(1 for s in step_results if s.status == "completed")
        failed = sum(1 for s in step_results if s.status == "failed")
        blocked = sum(1 for s in step_results if s.status == "blocked")

        if blocked > 0:
            final_status = "blocked"
        elif failed > 0:
            final_status = "failed"
        else:
            final_status = "completed"

        finish_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        run.finished_at = finish_iso
        run.status = final_status

        result = ExecutionResult(
            run_id=run_id,
            task_id=plan.task_id,
            status=final_status,
            steps=step_results,
            total_steps=total,
            completed_steps=completed,
            failed_steps=failed,
            blocked_steps=blocked,
        )

        if save:
            self.save_run(run)
            self.save_result(result)

        return run, result

    def save_run(
        self, run: ExecutionRun, path: Optional[Union[str, Path]] = None
    ) -> str:
        """Saves ExecutionRun to disk."""
        target_path = (
            str(path)
            if path
            else os.path.join(self.runs_dir, f"{run.run_id}.json")
        )
        self.assert_relative_path(target_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(run.model_dump_json(indent=2) + "\n")
        return target_path

    def load_run(self, run_id: str) -> Optional[ExecutionRun]:
        """Loads ExecutionRun by run_id."""
        target_path = os.path.join(self.runs_dir, f"{run_id}.json")
        self.assert_relative_path(target_path)
        if not os.path.exists(target_path):
            if os.path.exists(os.path.join("core", target_path)):
                target_path = os.path.join("core", target_path)
            elif target_path.startswith("core/") and os.path.exists(target_path[5:]):
                target_path = target_path[5:]
            else:
                return None
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ExecutionRun.model_validate(data)

    def save_result(
        self, result: ExecutionResult, path: Optional[Union[str, Path]] = None
    ) -> str:
        """Saves ExecutionResult to disk."""
        target_path = (
            str(path)
            if path
            else os.path.join(self.results_dir, f"{result.run_id}.json")
        )
        self.assert_relative_path(target_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2) + "\n")
        return target_path

    def load_result(self, run_id: str) -> Optional[ExecutionResult]:
        """Loads ExecutionResult by run_id."""
        target_path = os.path.join(self.results_dir, f"{run_id}.json")
        self.assert_relative_path(target_path)
        if not os.path.exists(target_path):
            if os.path.exists(os.path.join("core", target_path)):
                target_path = os.path.join("core", target_path)
            elif target_path.startswith("core/") and os.path.exists(target_path[5:]):
                target_path = target_path[5:]
            else:
                return None
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ExecutionResult.model_validate(data)
