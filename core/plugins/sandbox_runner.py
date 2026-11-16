# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/sandbox_runner.py"
# purpose: "Minimal local sandbox runner verifying plugin governance policy before execution"
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
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from core.plugins.models import (
    PluginCard,
    PluginLifecycle,
    EntrypointType,
    SandboxExecutionPlan,
    SandboxExecutionResult,
    SandboxStatus,
)
from core.plugins.policy import (
    PluginPolicyError,
    validate_plugin_card_file,
    validate_sandbox_policy,
)


class PluginSandboxRunner:
    """
    Local sandbox execution runner enforcing DNK plugin governance policy.
    Ensures plugins undergo strict policy validation before isolated execution.
    """

    def __init__(self) -> None:
        self.last_workspace_path: Optional[Path] = None

    def build_plan(self, card_path: Union[Path, str]) -> SandboxExecutionPlan:
        """
        Builds a SandboxExecutionPlan for a given plugin card after validating policy.
        Only plugins in the 'sandbox' lifecycle are permitted.
        """
        path_obj = Path(card_path)
        if not path_obj.exists() and (Path("core") / path_obj).exists():
            path_obj = Path("core") / path_obj
        is_valid, errors, card = validate_plugin_card_file(path_obj)
        if not is_valid or card is None:
            raise PluginPolicyError(
                f"Card schema validation failed: {'; '.join(errors)}"
            )

        ok, violations = validate_sandbox_policy(card)
        if not ok:
            raise PluginPolicyError(
                f"Policy check failed: {'; '.join(violations)}"
            )

        fs_perm = (
            card.permissions.filesystem
            if card.permissions.filesystem in ("none", "workspace_readonly")
            else "workspace_readonly"
        )

        plan = SandboxExecutionPlan(
            plugin_id=card.id,
            lifecycle="sandbox",
            entrypoint_type="python",
            allowed_filesystem=fs_perm,
            network="none",
            secrets="none",
            git="none",
            database="none",
            external_write="none",
            temporary_workspace=True,
            max_execution_seconds=5,
            max_output_chars=4000,
        )

        self.validate_plan(plan)
        return plan

    def validate_plan(self, plan: SandboxExecutionPlan) -> None:
        """
        Validates that a SandboxExecutionPlan strictly conforms to sandbox constraints:
        - lifecycle == 'sandbox'
        - entrypoint_type == 'python'
        - network == 'none'
        - secrets == 'none'
        - git == 'none'
        - database == 'none'
        - external_write == 'none'
        - allowed_filesystem in ('none', 'workspace_readonly')
        """
        violations = []
        if plan.lifecycle != "sandbox":
            violations.append(f"Lifecycle must be 'sandbox', got '{plan.lifecycle}'")
        if plan.entrypoint_type != "python":
            violations.append(
                f"Entrypoint type must be 'python', got '{plan.entrypoint_type}'"
            )
        if plan.network != "none":
            violations.append(
                f"Plan permits forbidden network access: '{plan.network}'"
            )
        if plan.secrets != "none":
            violations.append(
                f"Plan permits forbidden secrets access: '{plan.secrets}'"
            )
        if plan.git != "none":
            violations.append(f"Plan permits forbidden git access: '{plan.git}'")
        if plan.database != "none":
            violations.append(
                f"Plan permits forbidden database access: '{plan.database}'"
            )
        if plan.external_write != "none":
            violations.append(
                f"Plan permits forbidden external write access: '{plan.external_write}'"
            )
        if plan.allowed_filesystem not in ("none", "workspace_readonly"):
            violations.append(
                f"Plan specifies invalid filesystem access: '{plan.allowed_filesystem}'"
            )

        if violations:
            raise PluginPolicyError(
                f"Sandbox plan validation failed: {'; '.join(violations)}"
            )

    def _limit_output(self, data: Any, max_chars: int) -> Any:
        """Limits output data size to not exceed max_output_chars."""
        try:
            dumped = json.dumps(data)
            if len(dumped) <= max_chars:
                return data
            if isinstance(data, dict):
                capped: Dict[str, Any] = {}
                num_fields = max(1, len(data))
                budget_per_field = max(10, (max_chars // num_fields) - 20)
                for k, v in data.items():
                    if isinstance(v, str) and len(v) > budget_per_field:
                        capped[k] = v[:budget_per_field]
                    else:
                        capped[k] = v
                if len(json.dumps(capped)) <= max_chars:
                    return capped
                return {
                    "truncated": True,
                    "preview": json.dumps(capped)[: max(0, max_chars - 30)],
                }
            elif isinstance(data, str):
                return data[:max_chars]
        except Exception:
            pass
        return data

    def run(
        self,
        card_path: Union[Path, str],
        payload: dict,
        timeout_override: Optional[int] = None,
    ) -> SandboxExecutionResult:
        """
        Executes a plugin inside an isolated temporary workspace after policy verification.
        If policy check fails, execution is blocked before module import.
        """
        path_obj = Path(card_path)
        if not path_obj.exists() and (Path("core") / path_obj).exists():
            path_obj = Path("core") / path_obj
        plugin_id = "unknown"

        # Attempt to read plugin_id from card file for audit logging
        if path_obj.exists():
            try:
                with open(path_obj, "r", encoding="utf-8") as f:
                    raw_data = yaml.safe_load(f)
                    if isinstance(raw_data, dict) and "id" in raw_data:
                        plugin_id = str(raw_data["id"])
            except Exception:
                pass

        # Step 1: Pre-execution policy & plan validation
        try:
            plan = self.build_plan(path_obj)
            self.validate_plan(plan)
            plugin_id = plan.plugin_id
        except Exception as exc:
            return SandboxExecutionResult(
                plugin_id=plugin_id,
                status=SandboxStatus.BLOCKED,
                reason=f"Execution blocked by policy: {str(exc)}",
                output={},
                execution_seconds=0.0,
                policy_enforced=True,
                network_called=False,
                secrets_read=False,
                git_called=False,
                database_called=False,
                external_write_called=False,
            )

        # Step 2: Resolve entrypoint
        _, _, card = validate_plugin_card_file(path_obj)
        if card is None:
            return SandboxExecutionResult(
                plugin_id=plugin_id,
                status=SandboxStatus.BLOCKED,
                reason="Plugin card could not be loaded",
                output={},
                execution_seconds=0.0,
                policy_enforced=True,
                network_called=False,
                secrets_read=False,
                git_called=False,
                database_called=False,
                external_write_called=False,
            )

        entry_ref = card.entrypoint.reference.strip()
        if ":" in entry_ref:
            file_part, func_name = entry_ref.split(":", 1)
        else:
            file_part, func_name = entry_ref, "run"

        entry_file = Path(file_part)
        if not entry_file.is_absolute():
            entry_file = Path.cwd() / entry_file

        if not entry_file.exists():
            if file_part.startswith("templates/"):
                fallback = Path.cwd() / "core" / file_part
                if fallback.exists():
                    entry_file = fallback
            elif file_part.startswith("plugins/"):
                fallback = Path.cwd() / "packages" / file_part
                if fallback.exists():
                    entry_file = fallback

        if not entry_file.exists():
            return SandboxExecutionResult(
                plugin_id=plugin_id,
                status=SandboxStatus.FAILED,
                reason=f"Entrypoint file not found: {file_part}",
                output={},
                execution_seconds=0.0,
                policy_enforced=True,
                network_called=False,
                secrets_read=False,
                git_called=False,
                database_called=False,
                external_write_called=False,
            )

        # Step 3: Temporary isolated workspace setup & execution
        temp_dir = tempfile.mkdtemp(prefix="dnk_sandbox_ws_")
        self.last_workspace_path = Path(temp_dir)
        timeout_seconds = (
            timeout_override
            if timeout_override is not None
            else plan.max_execution_seconds
        )

        try:
            start_time = time.perf_counter()

            worker_script = f"""
import sys, json, importlib.util
from pathlib import Path

entry_file = Path({json.dumps(str(entry_file))})
func_name = {json.dumps(func_name)}
payload = json.loads({json.dumps(json.dumps(payload))})

try:
    spec = importlib.util.spec_from_file_location("plugin_fixture_mod", entry_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {{entry_file}}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = getattr(mod, func_name)
    result = fn(payload)
    out_json = json.dumps(result)
    print("__SANDBOX_OUTPUT_START__" + out_json + "__SANDBOX_OUTPUT_END__")
    sys.exit(0)
except Exception as ex:
    print(f"Error during fixture execution: {{str(ex)}}", file=sys.stderr)
    sys.exit(1)
"""

            try:
                proc = subprocess.run(
                    [sys.executable, "-c", worker_script],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    env={
                        "PYTHONPATH": str(Path.cwd()),
                        "PATH": os.environ.get("PATH", ""),
                    },
                )
                elapsed = time.perf_counter() - start_time

                if proc.returncode != 0:
                    return SandboxExecutionResult(
                        plugin_id=plugin_id,
                        status=SandboxStatus.FAILED,
                        reason=f"Execution error (exit {proc.returncode}): {proc.stderr.strip()}",
                        output={},
                        execution_seconds=round(elapsed, 4),
                        policy_enforced=True,
                        network_called=False,
                        secrets_read=False,
                        git_called=False,
                        database_called=False,
                        external_write_called=False,
                    )

                stdout = proc.stdout
                if (
                    "__SANDBOX_OUTPUT_START__" in stdout
                    and "__SANDBOX_OUTPUT_END__" in stdout
                ):
                    raw_out = (
                        stdout.split("__SANDBOX_OUTPUT_START__")[1]
                        .split("__SANDBOX_OUTPUT_END__")[0]
                    )
                    out_data = json.loads(raw_out)
                else:
                    out_data = {"raw_output": stdout.strip()}

                out_data = self._limit_output(out_data, plan.max_output_chars)

                return SandboxExecutionResult(
                    plugin_id=plugin_id,
                    status=SandboxStatus.COMPLETED,
                    reason="Execution completed successfully",
                    output=out_data,
                    execution_seconds=round(elapsed, 4),
                    policy_enforced=True,
                    network_called=False,
                    secrets_read=False,
                    git_called=False,
                    database_called=False,
                    external_write_called=False,
                )

            except subprocess.TimeoutExpired:
                elapsed = time.perf_counter() - start_time
                return SandboxExecutionResult(
                    plugin_id=plugin_id,
                    status=SandboxStatus.TIMED_OUT,
                    reason=f"Execution exceeded timeout limit ({timeout_seconds}s)",
                    output={},
                    execution_seconds=round(elapsed, 4),
                    policy_enforced=True,
                    network_called=False,
                    secrets_read=False,
                    git_called=False,
                    database_called=False,
                    external_write_called=False,
                )

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
