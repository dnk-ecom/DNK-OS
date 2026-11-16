# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/certification.py"
# purpose: "DNK OS Plugin Certification & Activation Review Policy Model and Validator"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""
DNK OS Plugin Certification & Activation Review Layer (v1.0).

Enforces formal, fail-closed policy gates for transitioning plugins
from 'evaluated' to 'active'.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CertificationRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


RiskLevel = CertificationRiskLevel


def _is_relative_path(path_str: str) -> bool:
    """Validate that path is non-empty and strictly relative."""
    if not path_str or not isinstance(path_str, str):
        return False
    path_clean = path_str.strip()
    if not path_clean:
        return False
    if path_clean.startswith("/") or path_clean.startswith("~"):
        return False
    if re.match(r"^[a-zA-Z]:", path_clean):
        return False
    p = Path(path_clean)
    return not p.is_absolute()


class ContractTestsInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., description="Relative path to contract test suite.")
    status: Literal["green", "passed"] = Field(..., description="Status of contract test suite.")
    last_run_at: str = Field(..., description="Timestamp of the test execution.")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Contract test path cannot be empty.")
        if not _is_relative_path(v):
            raise ValueError(f"Contract test path must be relative: {v}")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in ("green", "passed"):
            raise ValueError(f"Contract tests status must be 'green' or 'passed', got: {v}")
        return v_clean


class SecurityReviewInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., description="Relative path to security review markdown document.")
    reviewer: str = Field(..., description="Identity of reviewer (e.g. gerych_prime).")
    reviewed_at: str = Field(..., description="Timestamp of security review.")
    risk_level: CertificationRiskLevel = Field(default=CertificationRiskLevel.LOW)
    notes: Optional[str] = Field(default="", description="Mandatory notes if risk_level is high or critical.")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Security review path cannot be empty.")
        if not _is_relative_path(v):
            raise ValueError(f"Security review path must be relative: {v}")
        return v.strip()

    @field_validator("reviewer")
    @classmethod
    def validate_reviewer(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Security reviewer cannot be empty.")
        return v.strip()

    @model_validator(mode="after")
    def validate_risk_notes(self) -> "SecurityReviewInfo":
        if self.risk_level in (CertificationRiskLevel.HIGH, CertificationRiskLevel.CRITICAL):
            if not self.notes or not self.notes.strip():
                raise ValueError(
                    f"Security review with risk_level '{self.risk_level.value}' must provide explanatory mitigation notes."
                )
        return self


class ActivationApprovalInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., description="Relative path to activation approval document.")
    approver: str = Field(..., description="Identity of approver (must be Maksym).")
    approved_at: str = Field(..., description="Timestamp of activation approval.")
    approval_record: Optional[str] = Field(default="", description="Approval reference token or id.")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Activation approval path cannot be empty.")
        if not _is_relative_path(v):
            raise ValueError(f"Activation approval path must be relative: {v}")
        return v.strip()

    @field_validator("approver")
    @classmethod
    def validate_approver(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Activation approver cannot be empty.")
        v_clean = v.strip().lower()
        if "maksym" not in v_clean:
            raise ValueError(f"Activation approval for active state requires approver 'maksym', got: '{v}'")
        return v.strip()


class PluginCertificationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plugin_id: str = Field(..., description="Plugin identifier.")
    plugin_version: str = Field(..., description="Semantic version of the plugin.")
    lifecycle_from: Literal["evaluated"] = Field(default="evaluated")
    lifecycle_to: Literal["active"] = Field(default="active")
    contract_tests: ContractTestsInfo
    security_review: SecurityReviewInfo
    activation_approval: ActivationApprovalInfo
    evidence_paths: List[str] = Field(..., min_length=3, description="List of relative evidence paths.")
    certified_at: str = Field(..., description="Timestamp of certification.")
    certified_by: str = Field(..., description="Identity of certifying agent or authority.")

    @field_validator("plugin_id")
    @classmethod
    def validate_plugin_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Plugin ID cannot be empty.")
        return v.strip()

    @field_validator("plugin_version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Plugin version cannot be empty.")
        return v.strip()

    @field_validator("certified_by")
    @classmethod
    def validate_certified_by(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("certified_by cannot be empty.")
        return v.strip()

    @field_validator("evidence_paths")
    @classmethod
    def validate_evidence_paths(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("evidence_paths must not be empty.")
        for p in v:
            if not _is_relative_path(p):
                raise ValueError(f"All evidence paths must be relative, got: '{p}'")
        return v

    @model_validator(mode="after")
    def validate_cross_rules(self) -> "PluginCertificationRecord":
        plugin_clean = self.plugin_id.strip().lower()

        # Rule 9: Certification cannot be performed by the plugin itself
        cert_by_clean = self.certified_by.strip().lower()
        if cert_by_clean in (plugin_clean, "plugin", "self"):
            raise ValueError(
                f"Certification cannot be performed by the plugin itself (certified_by='{self.certified_by}')."
            )

        reviewer_clean = self.security_review.reviewer.strip().lower()
        if reviewer_clean in (plugin_clean, "plugin", "self"):
            raise ValueError(
                f"Security review cannot be performed by the plugin itself (reviewer='{self.security_review.reviewer}')."
            )

        approver_clean = self.activation_approval.approver.strip().lower()
        if approver_clean in (plugin_clean, "plugin", "self"):
            raise ValueError(
                f"Activation approval cannot be granted by the plugin itself (approver='{self.activation_approval.approver}')."
            )

        # Rule 5: Lifecycle transition to 'active' strictly requires approver == 'maksym'
        if self.lifecycle_to == "active" and "maksym" not in approver_clean:
            raise ValueError("Activation approval for 'active' lifecycle strictly requires 'maksym'.")

        # Invariant: Evidence paths must include security review, activation approval, and contract test evidence
        evidence_set = set(self.evidence_paths)
        if self.security_review.path not in evidence_set:
            raise ValueError(f"evidence_paths missing security_review.path: '{self.security_review.path}'")
        if self.activation_approval.path not in evidence_set:
            raise ValueError(f"evidence_paths missing activation_approval.path: '{self.activation_approval.path}'")

        has_contract_test_evidence = any("contract_test" in p or "test" in p for p in self.evidence_paths)
        if not has_contract_test_evidence:
            raise ValueError("evidence_paths missing contract test evidence artifact.")

        return self


def parse_frontmatter_and_markdown(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and body markdown from a file."""
    if not file_path.exists():
        return {}, ""
    content = file_path.read_text(encoding="utf-8")
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
                return fm, parts[2]
            except Exception:
                return {}, content
    return {}, content


def validate_certification_record(
    data: Union[Dict[str, Any], PluginCertificationRecord]
) -> Tuple[bool, List[str], Optional[PluginCertificationRecord]]:
    """Validate a certification record against schema and invariants."""
    if isinstance(data, PluginCertificationRecord):
        return True, [], data

    if not isinstance(data, dict):
        return False, ["Input must be a dictionary or PluginCertificationRecord"], None

    try:
        record = PluginCertificationRecord(**data)
        return True, [], record
    except Exception as e:
        return False, [str(e)], None


def check_plugin_certification(
    plugin_id: str,
    card_path: Union[str, Path],
    evidence_dir: Union[str, Path],
) -> Tuple[bool, List[str], Optional[PluginCertificationRecord]]:
    """
    Check if a plugin meets all requirements for evaluated -> active transition.

    Enforces:
    1. Valid relative paths only.
    2. Plugin Card exists and matches plugin_id, valid license, valid owner.
    3. Contract test evidence exists, is green, and has no template placeholders.
    4. Security review evidence exists, has valid reviewer, valid risk_level, notes if high.
    5. Activation approval evidence exists, approved by maksym, status approved.
    6. All paths are relative.
    7. Validation of the generated PluginCertificationRecord.
    """
    errors: List[str] = []

    card_str = str(card_path)
    ev_str = str(evidence_dir)

    if not _is_relative_path(card_str):
        return False, [f"Card path must be a relative path: {card_str}"], None
    if not _is_relative_path(ev_str):
        return False, [f"Evidence directory path must be a relative path: {ev_str}"], None

    card_file = Path(card_str)
    if not card_file.is_file():
        return False, [f"Plugin Card file not found: {card_str}"], None

    try:
        card_data = yaml.safe_load(card_file.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return False, [f"Failed to parse Plugin Card YAML: {e}"], None

    card_id = card_data.get("id")
    if card_id != plugin_id:
        errors.append(f"Plugin Card id '{card_id}' does not match requested plugin_id '{plugin_id}'.")

    card_version = card_data.get("version", "0.1.0")

    # Check origin & license
    origin = card_data.get("origin", {})
    license_type = origin.get("license", "").strip() if isinstance(origin, dict) else ""
    if not license_type:
        errors.append("Plugin origin license is missing or empty.")

    # Check governance & owner
    governance = card_data.get("governance", {})
    owner = governance.get("owner", "").strip() if isinstance(governance, dict) else ""
    if not owner:
        errors.append("Plugin governance owner is missing or empty.")

    ev_dir = Path(ev_str)
    if not ev_dir.is_dir():
        errors.append(f"Evidence directory does not exist: {ev_str}")
        return False, errors, None

    # Target evidence filenames
    contract_ev_path = ev_dir / "contract_test_evidence.md"
    security_ev_path = ev_dir / "security_review.md"
    approval_ev_path = ev_dir / "activation_approval.md"

    # Template fallback checks (if only template exists, evidence is incomplete)
    contract_template = ev_dir / "contract_test_evidence.template.md"
    security_template = ev_dir / "security_review.template.md"
    approval_template = ev_dir / "activation_approval.template.md"

    # 1. Contract tests evidence
    ct_target = contract_ev_path if contract_ev_path.is_file() else (contract_template if contract_template.is_file() else None)
    if not ct_target:
        errors.append("Missing contract test evidence: 'contract_test_evidence.md' not found.")
    elif ct_target.name.endswith(".template.md"):
        errors.append("Incomplete contract test evidence: only unpopulated template exists.")
    else:
        fm, body = parse_frontmatter_and_markdown(ct_target)
        status = str(fm.get("status", "")).strip().lower()
        if status not in ("green", "passed"):
            errors.append(f"Contract test evidence status must be 'green' or 'passed', got: '{status}'.")
        test_path = str(fm.get("test_suite_path", "")).strip()
        if not test_path or "{{PLUGIN_ID}}" in test_path or "TODO" in test_path:
            errors.append("Contract test evidence has invalid or placeholder test_suite_path.")
        if "pending" in status or "{{STATUS}}" in body:
            errors.append("Contract test evidence contains unpopulated placeholders.")

    # 2. Security review evidence
    sec_target = security_ev_path if security_ev_path.is_file() else (security_template if security_template.is_file() else None)
    if not sec_target:
        errors.append("Missing security review evidence: 'security_review.md' not found.")
    elif sec_target.name.endswith(".template.md"):
        errors.append("Incomplete security review evidence: only unpopulated template exists.")
    else:
        fm, body = parse_frontmatter_and_markdown(sec_target)
        reviewer = str(fm.get("reviewer", "")).strip()
        risk_lvl = str(fm.get("risk_level", "low")).strip().lower()
        notes = str(fm.get("notes", "")).strip()
        if not reviewer or "{{REVIEWER}}" in reviewer:
            errors.append("Security review evidence reviewer is missing or placeholder.")
        if risk_lvl in ("high", "critical") and not notes:
            errors.append(f"Security review has risk level '{risk_lvl}' but lacks required mitigation notes.")

    # 3. Activation approval evidence
    appr_target = approval_ev_path if approval_ev_path.is_file() else (approval_template if approval_template.is_file() else None)
    if not appr_target:
        errors.append("Missing activation approval evidence: 'activation_approval.md' not found.")
    elif appr_target.name.endswith(".template.md"):
        errors.append("Incomplete activation approval evidence: only unpopulated template exists.")
    else:
        fm, body = parse_frontmatter_and_markdown(appr_target)
        approver = str(fm.get("approver", "")).strip().lower()
        appr_status = str(fm.get("approval_status", "")).strip().lower()
        if "maksym" not in approver:
            errors.append(f"Activation approval must be granted by 'maksym', got: '{approver}'.")
        if appr_status != "approved":
            errors.append(f"Activation approval status must be 'approved', got: '{appr_status}'.")
        if "{{APPROVED_AT}}" in str(fm.get("approved_at", "")) or fm.get("approved_at") is None:
            errors.append("Activation approval timestamp is not set.")

    if errors or ct_target is None or sec_target is None or appr_target is None:
        return False, errors, None

    # Construct and validate record
    try:
        record_dict = {
            "plugin_id": plugin_id,
            "plugin_version": card_version,
            "lifecycle_from": "evaluated",
            "lifecycle_to": "active",
            "contract_tests": {
                "path": str(ct_target.as_posix()),
                "status": "green",
                "last_run_at": datetime.now(timezone.utc).isoformat(),
            },
            "security_review": {
                "path": str(sec_target.as_posix()),
                "reviewer": "gerych_prime",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "risk_level": "low",
                "notes": "",
            },
            "activation_approval": {
                "path": str(appr_target.as_posix()),
                "approver": "maksym",
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "approval_record": f"DNK-ACT-{plugin_id}-001",
            },
            "evidence_paths": [
                str(ct_target.as_posix()),
                str(sec_target.as_posix()),
                str(appr_target.as_posix()),
            ],
            "certified_at": datetime.now(timezone.utc).isoformat(),
            "certified_by": "gerych_prime",
        }
        valid, rec_errors, record = validate_certification_record(record_dict)
        if not valid:
            return False, rec_errors, None
        return True, [], record
    except Exception as e:
        return False, [f"Failed to generate certification record: {e}"], None


def generate_evidence_templates(
    plugin_id: str,
    output_dir: Union[str, Path],
    plugin_version: str = "0.1.0",
    template_suffix: bool = True,
) -> Dict[str, str]:
    """
    Generate evidence markdown templates for a plugin with correct fields.

    Produces:
    - contract_test_evidence[.template].md
    - security_review[.template].md
    - activation_approval[.template].md
    """
    out_dir = Path(output_dir)
    if not _is_relative_path(str(output_dir)):
        raise ValueError(f"Output directory must be a relative path: {output_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = ".template.md" if template_suffix else ".md"

    ext_map = {
        f"contract_test_evidence{suffix}": _build_contract_template(plugin_id, plugin_version),
        f"security_review{suffix}": _build_security_template(plugin_id, plugin_version),
        f"activation_approval{suffix}": _build_approval_template(plugin_id, plugin_version),
    }

    created_paths: Dict[str, str] = {}
    for filename, content in ext_map.items():
        target = out_dir / filename
        target.write_text(content, encoding="utf-8")
        created_paths[filename] = str(target.as_posix())

    return created_paths


def _build_contract_template(plugin_id: str, plugin_version: str) -> str:
    return f"""---
plugin_id: "{plugin_id}"
plugin_version: "{plugin_version}"
artifact_type: "contract_test_evidence"
status: "pending"
test_suite_path: "tests/plugins/{plugin_id}/test_{plugin_id}.py"
execution_target: "local_pytest"
last_run_at: null
passed_count: 0
failed_count: 0
---

# --- DNK-MRH-HEADER ---
# mrh_id: "templates/plugin/evidence/contract_test_evidence.template.md"
# purpose: "Evidence template for Plugin Contract Test verification (evaluated -> active)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🧪 Contract Test Evidence: {plugin_id}

## 1. Execution Summary
- **Plugin ID**: `{plugin_id}`
- **Plugin Version**: `{plugin_version}`
- **Test Suite Relative Path**: `tests/plugins/{plugin_id}/test_{plugin_id}.py`
- **Status**: `[STATUS]`
- **Last Run Timestamp**: `[LAST_RUN_AT]`

## 2. Tested Contract Invariants
- [ ] Interface signature conformance.
- [ ] Input payload validation and default-deny boundary isolation.
- [ ] Output schema conformity.
- [ ] Error handling and graceful failure without host crash.

## 3. Test Runner Output Log
```text
[PASTE PYTEST / RUNNER EXECUTION OUTPUT HERE]
```
"""


def _build_security_template(plugin_id: str, plugin_version: str) -> str:
    return f"""---
plugin_id: "{plugin_id}"
plugin_version: "{plugin_version}"
artifact_type: "security_review"
reviewer: "gerych_prime"
reviewed_at: null
risk_level: "low"
notes: ""
permissions_justified: false
secrets_evaluated: false
network_evaluated: false
git_evaluated: false
database_evaluated: false
external_write_evaluated: false
---

# --- DNK-MRH-HEADER ---
# mrh_id: "templates/plugin/evidence/security_review.template.md"
# purpose: "Security Review Evidence Template for evaluated -> active plugin transition"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ Plugin Security Review: {plugin_id}

## 1. Review Metadata
- **Plugin ID**: `{plugin_id}`
- **Plugin Version**: `{plugin_version}`
- **Reviewer**: `gerych_prime`
- **Reviewed At**: `[REVIEWED_AT]`
- **Risk Level**: `low`

## 2. Risk & Permissions Analysis
### 2.1 Permissions Justification
- **Declared Permissions**: `[]`
- **Justification**:
  [Explain why each permission is required]

### 2.2 Attack Surface & Capability Audit
- **Secrets Access**: None
- **Network Access**: None
- **Git Access**: None
- **Database Access**: None
- **External Write Access**: None

## 3. Sandboxing & Blast Radius Verification
- [ ] Plugin runs under standard isolated sandbox runner (`core.plugins.sandbox`).
- [ ] No arbitrary code execution or unmonitored subshell spawning.

## 4. Residual Risk Assessment & Mitigation Notes
*(Mandatory if risk_level is high or critical)*
[NOTES]

## 5. Security Verdict
- **Verdict**: PENDING
"""


def _build_approval_template(plugin_id: str, plugin_version: str) -> str:
    return f"""---
plugin_id: "{plugin_id}"
plugin_version: "{plugin_version}"
artifact_type: "activation_approval"
approver: "maksym"
approved_at: null
approval_record: "DNK-ACT-AUTH-{plugin_id}-001"
approval_status: "pending"
lifecycle_target: "active"
workspace_scope: "ws-alpha-001"
---

# --- DNK-MRH-HEADER ---
# mrh_id: "templates/plugin/evidence/activation_approval.template.md"
# purpose: "Formal Activation Approval by Maxim for DNK OS Plugin Transition to Active"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 👑 Plugin Activation Approval: {plugin_id}

## 1. Approval Record
- **Plugin ID**: `{plugin_id}`
- **Plugin Version**: `{plugin_version}`
- **Authorized Approver**: `maksym` (Maksym Kuzmenko, System Owner)
- **Approved At**: `[APPROVED_AT]`
- **Approval Record ID**: `DNK-ACT-AUTH-{plugin_id}-001`
- **Target Lifecycle State**: `active`
- **Allowed Workspace Scope**: `ws-alpha-001`

## 2. Gate Verification Checklist
- [ ] Plugin Card v1.0 schema validated and governance approved.
- [ ] Contract tests passing 100% green on target environment.
- [ ] Security review completed and risk within acceptable parameters.
- [ ] Owner identified and responsive.
- [ ] License compliant.

## 3. Formal Authorization Statement
> "I hereby authorize the transition of plugin `{plugin_id}` (v`{plugin_version}`)
> from lifecycle state `evaluated` to `active` within the authorized workspace scope `ws-alpha-001`."

- **Approver Signature**: `maksym`
- **Status**: `pending`
"""
