# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/models.py"
# purpose: "Pydantic models and declarative validation for DNK OS Plugin Card v1.0"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

from enum import Enum
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, model_validator


class PluginKind(str, Enum):
    TOOL = "tool"
    MEMORY = "memory"
    AGENT = "agent"
    SERVICE_ADAPTER = "service_adapter"
    UI_NODE = "ui_node"
    WORKFLOW = "workflow"


class PluginLifecycle(str, Enum):
    DRAFT = "draft"
    SANDBOX = "sandbox"
    EVALUATED = "evaluated"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class OriginType(str, Enum):
    INTERNAL = "internal"
    OPEN_SOURCE = "open_source"
    VENDOR = "vendor"
    GENERATED = "generated"


class EntrypointType(str, Enum):
    PYTHON = "python"
    MCP = "mcp"
    HTTP = "http"
    CONTAINER = "container"
    FRONTEND = "frontend"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def _is_relative_path(path_str: Optional[str]) -> bool:
    if not path_str:
        return True
    cleaned = path_str.strip()
    if cleaned.startswith("/") or cleaned.startswith("~") or cleaned.startswith("\\"):
        return False
    # Check for drive letter on Windows (e.g., C:)
    if len(cleaned) > 1 and cleaned[1] == ":":
        return False
    return True


class OriginInfo(BaseModel):
    type: OriginType
    repository_url: Optional[str] = None
    commit_sha: Optional[str] = None
    license_spdx: str
    assimilation_track: Optional[str] = None
    provenance_note: Optional[str] = None

    @model_validator(mode="after")
    def validate_origin(self) -> "OriginInfo":
        if self.provenance_note and not _is_relative_path(self.provenance_note):
            raise ValueError(f"provenance_note must be a relative path: {self.provenance_note}")

        if self.type == OriginType.INTERNAL:
            if self.repository_url is not None and self.repository_url.strip() != "":
                raise ValueError("Internal origin must have repository_url set to null")
            if not (self.license_spdx == "DNK-INTERNAL" or self.license_spdx.startswith("DNK-")):
                raise ValueError(
                    f"Internal origin requires DNK-INTERNAL or DNK-* license, got: {self.license_spdx}"
                )

        elif self.type == OriginType.OPEN_SOURCE:
            if not self.repository_url or not self.repository_url.strip():
                raise ValueError("open_source origin requires repository_url")
            if not self.commit_sha or not self.commit_sha.strip():
                raise ValueError("open_source origin requires commit_sha")
            if not self.license_spdx or self.license_spdx.strip().lower() in ["unknown", "none", ""]:
                raise ValueError("open_source origin requires a valid SPDX license identifier")

        elif self.type == OriginType.GENERATED:
            if not self.provenance_note or not self.provenance_note.strip():
                raise ValueError("generated origin requires provenance_note")

        elif self.type == OriginType.VENDOR:
            if not self.license_spdx or not self.license_spdx.strip():
                raise ValueError("vendor origin requires license_spdx or agreement reference")

        return self


class EntrypointInfo(BaseModel):
    type: EntrypointType
    reference: str

    @model_validator(mode="after")
    def validate_entrypoint(self) -> "EntrypointInfo":
        if not self.reference or not self.reference.strip():
            raise ValueError("Entrypoint reference cannot be empty")
        if not _is_relative_path(self.reference):
            raise ValueError(f"Entrypoint reference must be a relative path: {self.reference}")
        return self


class CapabilitiesInfo(BaseModel):
    provides: List[str] = Field(default_factory=list)
    requires: List[str] = Field(default_factory=list)


class PermissionsInfo(BaseModel):
    filesystem: Literal["none", "workspace_readonly", "allowlist"] = "none"
    network: Literal["none", "allowlist"] = "none"
    secrets: Literal["none", "allowlist"] = "none"
    git: Literal["none", "allowlist"] = "none"
    database: Literal["none", "allowlist"] = "none"
    external_write: Literal["none", "allowlist"] = "none"


class ApprovalRecord(BaseModel):
    approved_by: str
    approval_date: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_approval(self) -> "ApprovalRecord":
        if not self.approved_by or not self.approved_by.strip():
            raise ValueError("Approval record must include approved_by")
        return self


class GovernanceInfo(BaseModel):
    owner: str
    risk_level: RiskLevel = RiskLevel.LOW
    approval_required_for_activation: bool = True
    sandbox_profile: str = "default-deny"
    evidence_paths: List[str] = Field(default_factory=list)
    contract_test_path: Optional[str] = None
    security_review_path: Optional[str] = None
    approval_record: Optional[ApprovalRecord] = None
    deprecation_reason: Optional[str] = None

    @model_validator(mode="after")
    def validate_paths(self) -> "GovernanceInfo":
        for ep in self.evidence_paths:
            if not _is_relative_path(ep):
                raise ValueError(f"evidence_path must be a relative path: {ep}")
        if self.contract_test_path and not _is_relative_path(self.contract_test_path):
            raise ValueError(f"contract_test_path must be a relative path: {self.contract_test_path}")
        if self.security_review_path and not _is_relative_path(self.security_review_path):
            raise ValueError(f"security_review_path must be a relative path: {self.security_review_path}")
        return self


class CompatibilityInfo(BaseModel):
    harness_api_version: str = "v0.1"
    required_core_capabilities: List[str] = Field(default_factory=list)
    conflicts_with: List[str] = Field(default_factory=list)


class PluginCard(BaseModel):
    schema_version: Literal["dnk-plugin/v1.0"] = "dnk-plugin/v1.0"
    id: str
    name: str
    version: str
    kind: PluginKind
    lifecycle: PluginLifecycle
    origin: OriginInfo
    entrypoint: EntrypointInfo
    capabilities: CapabilitiesInfo
    permissions: PermissionsInfo
    governance: GovernanceInfo
    compatibility: CompatibilityInfo

    @model_validator(mode="after")
    def validate_card_invariants(self) -> "PluginCard":
        # 1. Default-deny invariants for draft and sandbox
        if self.lifecycle in [PluginLifecycle.DRAFT, PluginLifecycle.SANDBOX]:
            if self.permissions.secrets != "none":
                raise ValueError(
                    f"Permissions violation: lifecycle '{self.lifecycle.value}' prohibits secrets access (must be 'none', got '{self.permissions.secrets}')"
                )
            if self.permissions.git != "none":
                raise ValueError(
                    f"Permissions violation: lifecycle '{self.lifecycle.value}' prohibits git write access (must be 'none', got '{self.permissions.git}')"
                )
            if self.permissions.database != "none":
                raise ValueError(
                    f"Permissions violation: lifecycle '{self.lifecycle.value}' prohibits direct database access (must be 'none', got '{self.permissions.database}')"
                )
            if self.permissions.external_write != "none":
                raise ValueError(
                    f"Permissions violation: lifecycle '{self.lifecycle.value}' prohibits external write access (must be 'none', got '{self.permissions.external_write}')"
                )
            if self.permissions.network not in ["none", "allowlist"]:
                raise ValueError(
                    f"Permissions violation: lifecycle '{self.lifecycle.value}' network must be 'none' or 'allowlist', got '{self.permissions.network}'"
                )
            if self.permissions.filesystem not in ["none", "workspace_readonly"]:
                raise ValueError(
                    f"Permissions violation: lifecycle '{self.lifecycle.value}' filesystem must be 'none' or 'workspace_readonly', got '{self.permissions.filesystem}'"
                )

        # 2. Lifecycle minimum requirements
        if self.lifecycle == PluginLifecycle.SANDBOX:
            if not self.governance.contract_test_path:
                raise ValueError("Lifecycle 'sandbox' requires a non-null contract_test_path")

        elif self.lifecycle == PluginLifecycle.EVALUATED:
            if not self.governance.contract_test_path:
                raise ValueError("Lifecycle 'evaluated' requires contract_test_path")
            if not self.governance.security_review_path:
                raise ValueError("Lifecycle 'evaluated' requires security_review_path")
            if not self.governance.evidence_paths:
                raise ValueError("Lifecycle 'evaluated' requires non-empty evidence_paths")

        elif self.lifecycle == PluginLifecycle.ACTIVE:
            if not self.governance.contract_test_path:
                raise ValueError("Lifecycle 'active' requires contract_test_path")
            if not self.governance.security_review_path:
                raise ValueError("Lifecycle 'active' requires security_review_path")
            if not self.governance.evidence_paths:
                raise ValueError("Lifecycle 'active' requires non-empty evidence_paths")
            if not self.governance.owner or not self.governance.owner.strip():
                raise ValueError("Lifecycle 'active' requires a registered owner")
            if self.origin.license_spdx.strip().lower() in ["unknown", "none", ""]:
                raise ValueError("Lifecycle 'active' strictly prohibits unknown or missing license")
            if not self.governance.approval_record:
                raise ValueError("Lifecycle 'active' requires an explicit approval_record")
            if "maksym" not in self.governance.approval_record.approved_by.strip().lower():
                raise ValueError(
                    f"Lifecycle 'active' requires explicit approval by Maksym, got: {self.governance.approval_record.approved_by}"
                )

        elif self.lifecycle == PluginLifecycle.DEPRECATED:
            if not self.governance.deprecation_reason or not self.governance.deprecation_reason.strip():
                raise ValueError("Lifecycle 'deprecated' requires a deprecation_reason")

        return self


class SandboxStatus(str, Enum):
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


class SandboxExecutionPlan(BaseModel):
    plugin_id: str
    lifecycle: Literal["sandbox"] = "sandbox"
    entrypoint_type: Literal["python"] = "python"
    allowed_filesystem: Literal["none", "workspace_readonly"] = "workspace_readonly"
    network: Literal["none"] = "none"
    secrets: Literal["none"] = "none"
    git: Literal["none"] = "none"
    database: Literal["none"] = "none"
    external_write: Literal["none"] = "none"
    temporary_workspace: bool = True
    max_execution_seconds: int = 5
    max_output_chars: int = 4000


class SandboxExecutionResult(BaseModel):
    plugin_id: str
    status: SandboxStatus
    reason: str = ""
    output: Dict[str, Any] = Field(default_factory=dict)
    execution_seconds: float = 0.0
    policy_enforced: bool = True
    network_called: bool = False
    secrets_read: bool = False
    git_called: bool = False
    database_called: bool = False
    external_write_called: bool = False
