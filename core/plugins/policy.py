# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/policy.py"
# purpose: "Policy evaluation and lifecycle transition engine for DNK OS Plugin Cards"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import yaml
from pydantic import ValidationError

from core.plugins.models import (
    PluginCard,
    PluginLifecycle,
    EntrypointType,
    OriginType,
    _is_relative_path,
)


class PluginPolicyError(Exception):
    """Base exception for plugin governance policy violations."""
    pass


def validate_plugin_card_data(data: Dict[str, Any]) -> Tuple[bool, List[str], Optional[PluginCard]]:
    """
    Validates raw dictionary representation of a plugin card against schema and invariants.
    Returns: (is_valid, list_of_errors, validated_card)
    """
    errors: List[str] = []
    try:
        card = PluginCard.model_validate(data)
        return True, [], card
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(p) for p in err.get("loc", []))
            msg = err.get("msg", "Validation error")
            errors.append(f"[{loc}] {msg}")
        return False, errors, None
    except Exception as ex:
        errors.append(f"Unexpected validation error: {str(ex)}")
        return False, errors, None


def validate_plugin_card_file(file_path: str | Path) -> Tuple[bool, List[str], Optional[PluginCard]]:
    """
    Loads and validates a plugin card YAML file.
    Ensures relative path usage and enforces schema/governance invariants.
    """
    path_str = str(file_path)
    if not _is_relative_path(path_str):
        return False, [f"Card file path must be relative, got: {path_str}"], None

    p = Path(file_path)
    if not p.exists():
        if (Path("core") / p).exists():
            p = Path("core") / p
        else:
            return False, [f"Plugin card file does not exist: {file_path}"], None

    try:
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
            data = yaml.safe_load(content)
    except Exception as ex:
        return False, [f"Failed to parse YAML file {file_path}: {str(ex)}"], None

    if not isinstance(data, dict):
        return False, [f"Root of YAML file {file_path} must be a mapping/dict"], None

    return validate_plugin_card_data(data)


def check_lifecycle_transition(
    card: PluginCard,
    from_stage: str,
    to_stage: str,
    actor: Optional[str] = None,
    strict_current_stage: bool = False,
) -> Tuple[bool, List[str]]:
    """
    Verifies whether a lifecycle transition is permitted under Sandbox-First Governance.
    Evaluates policy requirements for transitioning from `from_stage` to `to_stage`.
    Returns: (is_allowed, list_of_reasons_or_violations)
    """
    violations: List[str] = []
    from_stage_clean = from_stage.strip().lower()
    to_stage_clean = to_stage.strip().lower()

    # Rule 1: Actor restriction - plugin cannot self-transition
    if actor is not None:
        actor_clean = actor.strip().lower()
        if actor_clean in [card.id.strip().lower(), "plugin", "self"]:
            violations.append(
                f"Self-transition forbidden: Plugin '{card.id}' cannot transition its own lifecycle state."
            )
            return False, violations

    # Rule 2: Current lifecycle consistency (if strict checking requested)
    if strict_current_stage and card.lifecycle.value.lower() != from_stage_clean:
        violations.append(
            f"State mismatch: Card lifecycle is '{card.lifecycle.value}', but requested from_stage is '{from_stage}'."
        )
        return False, violations

    # Rule 3: Valid target stage
    try:
        target_lifecycle = PluginLifecycle(to_stage_clean)
    except ValueError:
        violations.append(f"Invalid target lifecycle: '{to_stage}'.")
        return False, violations

    if from_stage_clean == to_stage_clean:
        violations.append(f"No-op transition: Plugin is already in '{to_stage_clean}' state.")
        return False, violations

    # Rule 4: Deprecation transitions (allowed from any active/evaluated/sandbox/draft state)
    if target_lifecycle == PluginLifecycle.DEPRECATED:
        if not card.governance.deprecation_reason or not card.governance.deprecation_reason.strip():
            violations.append(
                "Transition to 'deprecated' requires a documented 'deprecation_reason' in governance."
            )
        return (len(violations) == 0), violations

    # Rule 5: State-specific forward transitions
    if from_stage_clean == "draft" and to_stage_clean == "sandbox":
        # Requires isolated entrypoint & contract test path
        if not card.governance.contract_test_path or not card.governance.contract_test_path.strip():
            violations.append(
                "Transition 'draft -> sandbox' requires a designated 'contract_test_path'."
            )
        if not card.entrypoint.reference or not card.entrypoint.reference.strip():
            violations.append(
                "Transition 'draft -> sandbox' requires an isolated entrypoint reference."
            )
        # Sandbox permissions must be default-deny
        if card.permissions.secrets != "none":
            violations.append("Sandbox requires permissions.secrets == 'none'")
        if card.permissions.git != "none":
            violations.append("Sandbox requires permissions.git == 'none'")
        if card.permissions.database != "none":
            violations.append("Sandbox requires permissions.database == 'none'")
        if card.permissions.external_write != "none":
            violations.append("Sandbox requires permissions.external_write == 'none'")

    elif from_stage_clean == "sandbox" and to_stage_clean == "evaluated":
        # Requires contract test path, security review path, and evidence
        if not card.governance.contract_test_path or not card.governance.contract_test_path.strip():
            violations.append("Transition 'sandbox -> evaluated' requires contract_test_path.")
        if not card.governance.security_review_path or not card.governance.security_review_path.strip():
            violations.append("Transition 'sandbox -> evaluated' requires security_review_path.")
        if not card.governance.evidence_paths:
            violations.append(
                "Transition 'sandbox -> evaluated' requires at least one artifact in evidence_paths."
            )

    elif from_stage_clean in ["evaluated", "sandbox"] and to_stage_clean == "active":
        # Active transition requirements:
        # Check evidence
        if not card.governance.evidence_paths:
            violations.append(
                f"Transition '{from_stage_clean} -> active' requires evidence artifacts in evidence_paths."
            )
        # Check security review
        if not card.governance.security_review_path or not card.governance.security_review_path.strip():
            violations.append(
                f"Transition '{from_stage_clean} -> active' requires a completed security review (security_review_path)."
            )
        # Check contract test
        if not card.governance.contract_test_path or not card.governance.contract_test_path.strip():
            violations.append(
                f"Transition '{from_stage_clean} -> active' requires verified contract tests (contract_test_path)."
            )
        # Check explicit Maksym approval
        if not card.governance.approval_record:
            violations.append(
                f"Transition '{from_stage_clean} -> active' requires an explicit approval record."
            )
        elif "maksym" not in card.governance.approval_record.approved_by.strip().lower():
            violations.append(
                f"Transition '{from_stage_clean} -> active' requires approval specifically by Maksym (found: {card.governance.approval_record.approved_by})."
            )
        # Check owner
        if not card.governance.owner or not card.governance.owner.strip():
            violations.append(
                f"Transition '{from_stage_clean} -> active' requires a registered owner."
            )
        # Check license
        if card.origin.license_spdx.strip().lower() in ["unknown", "none", ""]:
            violations.append(
                f"Transition '{from_stage_clean} -> active' strictly prohibits unknown/unverified license."
            )
        # Check permission expansion
        has_elevated_perms = any(
            [
                card.permissions.secrets != "none",
                card.permissions.git != "none",
                card.permissions.database != "none",
                card.permissions.external_write != "none",
            ]
        )
        if has_elevated_perms and not card.governance.approval_record:
            violations.append(
                "Elevated permissions require an explicit approval policy record."
            )

    else:
        violations.append(
            f"Illegal lifecycle transition: '{from_stage_clean}' -> '{to_stage_clean}' is not a permitted path."
        )

    return (len(violations) == 0), violations


def validate_sandbox_policy(card: PluginCard) -> Tuple[bool, List[str]]:
    """
    Validates that a plugin card satisfies all policy requirements for sandbox execution.
    Requirements:
    - lifecycle == "sandbox"
    - entrypoint.type == "python"
    - permissions.network == "none"
    - permissions.secrets == "none"
    - permissions.git == "none"
    - permissions.database == "none"
    - permissions.external_write == "none"
    - permissions.filesystem in ["none", "workspace_readonly"]
    """
    violations: List[str] = []
    if card.lifecycle != PluginLifecycle.SANDBOX:
        violations.append(f"Lifecycle must be 'sandbox', got '{card.lifecycle.value}'")
    if card.entrypoint.type != EntrypointType.PYTHON:
        violations.append(f"Entrypoint type must be 'python', got '{card.entrypoint.type.value}'")
    if card.permissions.network != "none":
        violations.append(f"Sandbox policy prohibits network access (must be 'none', got '{card.permissions.network}')")
    if card.permissions.secrets != "none":
        violations.append(f"Sandbox policy prohibits secrets access (must be 'none', got '{card.permissions.secrets}')")
    if card.permissions.git != "none":
        violations.append(f"Sandbox policy prohibits git access (must be 'none', got '{card.permissions.git}')")
    if card.permissions.database != "none":
        violations.append(f"Sandbox policy prohibits database access (must be 'none', got '{card.permissions.database}')")
    if card.permissions.external_write != "none":
        violations.append(f"Sandbox policy prohibits external write access (must be 'none', got '{card.permissions.external_write}')")
    if card.permissions.filesystem not in ["none", "workspace_readonly"]:
        violations.append(f"Sandbox policy only permits 'none' or 'workspace_readonly' filesystem access, got '{card.permissions.filesystem}'")
    return (len(violations) == 0), violations
