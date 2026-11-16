# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/github_intake.py"
# purpose: "Minimal GitHub Open Source Plugin Intake Model, Validation & Card Generator v0.1"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import string
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import yaml
from pydantic import BaseModel, Field, model_validator


KNOWN_SPDX_LICENSES = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-only",
    "GPL-3.0-or-later",
    "LGPL-2.1-only",
    "LGPL-2.1-or-later",
    "LGPL-3.0-only",
    "LGPL-3.0-or-later",
    "AGPL-3.0-only",
    "AGPL-3.0-or-later",
    "MPL-2.0",
    "Unlicense",
    "CC0-1.0",
    "0BSD",
    "EPL-2.0",
    "Artistic-2.0",
    "BSL-1.0",
    "Zlib",
    "Python-2.0",
}

DEFAULT_DENY_PERMISSIONS = {
    "filesystem": "none",
    "network": "none",
    "secrets": "none",
    "git": "none",
    "database": "none",
    "external_write": "none",
}

VALID_PLUGIN_KINDS = {
    "tool",
    "memory",
    "agent",
    "service_adapter",
    "ui_node",
    "workflow",
}


def is_relative_path(path_str: Optional[str]) -> bool:
    """Validates that a path is relative and does not traverse outside root."""
    if not path_str:
        return True
    cleaned = str(path_str).strip()
    if (
        cleaned.startswith("/")
        or cleaned.startswith("~")
        or cleaned.startswith("\\")
    ):
        return False
    if len(cleaned) > 1 and cleaned[1] == ":":
        return False
    # Avoid directory traversal attempts
    parts = Path(cleaned).parts
    if ".." in parts:
        return False
    return True


class GitHubIntakeModel(BaseModel):
    """Pydantic model for GitHub open-source plugin intake."""

    repository_url: str
    commit_sha: str
    license_spdx: str
    plugin_id: str
    plugin_name: str
    plugin_kind: str = "tool"
    entrypoint_reference: Optional[str] = None
    generated_card_path: Optional[str] = None
    lifecycle: str = "sandbox"
    permissions: Optional[Dict[str, str]] = None

    @model_validator(mode="after")
    def validate_intake_rules(self) -> "GitHubIntakeModel":
        # 1. repository_url must start with https://
        if not self.repository_url or not self.repository_url.strip().startswith("https://"):
            raise ValueError(
                f"repository_url must start with 'https://', got: '{self.repository_url}'"
            )

        # 2. commit_sha length and hex validation (6 to 64 chars)
        sha = self.commit_sha.strip() if self.commit_sha else ""
        if len(sha) < 6 or len(sha) > 64 or not all(c in string.hexdigits for c in sha):
            raise ValueError(
                f"commit_sha must be a valid hex string of length between 6 and 64, got: '{self.commit_sha}'"
            )

        # 3. Known SPDX license validation
        spdx = self.license_spdx.strip() if self.license_spdx else ""
        if spdx not in KNOWN_SPDX_LICENSES:
            raise ValueError(
                f"Unknown or unsupported license_spdx: '{self.license_spdx}'. Must be a recognized SPDX identifier (e.g. MIT, Apache-2.0)."
            )

        # 4. Lifecycle must be strictly 'sandbox'
        if self.lifecycle.strip().lower() != "sandbox":
            raise ValueError(
                f"GitHub intake strictly enforces lifecycle='sandbox', got: '{self.lifecycle}'"
            )

        # 5. Plugin kind validation
        if self.plugin_kind.strip().lower() not in VALID_PLUGIN_KINDS:
            raise ValueError(
                f"Invalid plugin_kind: '{self.plugin_kind}'. Allowed: {sorted(list(VALID_PLUGIN_KINDS))}"
            )

        # 6. Permissions default-deny enforcement
        if self.permissions:
            for k, v in self.permissions.items():
                if v != "none":
                    raise ValueError(
                        f"Permissions violation: Intake permissions must be strictly 'none' (default-deny), got '{k}: {v}'"
                    )

        # 7. Path hygiene - relative paths only
        if self.generated_card_path and not is_relative_path(self.generated_card_path):
            raise ValueError(
                f"generated_card_path must be a relative path: '{self.generated_card_path}'"
            )
        if self.entrypoint_reference and not is_relative_path(self.entrypoint_reference):
            raise ValueError(
                f"entrypoint_reference must be a relative path: '{self.entrypoint_reference}'"
            )

        # Set computed defaults if unset
        clean_id = self.plugin_id.strip().replace("-", "_")
        if not self.entrypoint_reference:
            self.entrypoint_reference = f"plugins/{clean_id}:Plugin"
        if not self.generated_card_path:
            self.generated_card_path = f"templates/plugin/github/{clean_id}_card.yaml"

        return self


def build_plugin_card_dict(intake: GitHubIntakeModel) -> Dict[str, Any]:
    """Builds a canonical Plugin Card dictionary conforming to schema v1.0."""
    return {
        "schema_version": "dnk-plugin/v1.0",
        "id": intake.plugin_id,
        "name": intake.plugin_name,
        "version": "0.1.0",
        "kind": intake.plugin_kind,
        "lifecycle": "sandbox",
        "origin": {
            "type": "open_source",
            "repository_url": intake.repository_url,
            "commit_sha": intake.commit_sha,
            "license_spdx": intake.license_spdx,
            "assimilation_track": "open_source",
            "provenance_note": "Imported via plugin_github_intake.py",
        },
        "entrypoint": {
            "type": "python",
            "reference": intake.entrypoint_reference,
        },
        "capabilities": {
            "provides": [],
            "requires": [],
        },
        "permissions": dict(DEFAULT_DENY_PERMISSIONS),
        "governance": {
            "owner": "gerych_prime",
            "risk_level": "low",
            "approval_required_for_activation": True,
            "sandbox_profile": "default-deny",
            "evidence_paths": [],
            "contract_test_path": None,
            "security_review_path": None,
        },
        "compatibility": {
            "harness_api_version": "v0.1",
            "required_core_capabilities": [],
            "conflicts_with": [],
        },
    }


def validate_github_plugin_card(
    card_path_or_dict: Union[str, Path, Dict[str, Any]]
) -> Tuple[bool, List[str]]:
    """Validates an open-source plugin card for intake rules and schema completeness."""
    errors: List[str] = []

    data: Dict[str, Any]
    if isinstance(card_path_or_dict, (str, Path)):
        path_str = str(card_path_or_dict)
        if not is_relative_path(path_str):
            return False, [f"Card path must be a relative path, got: '{path_str}'"]
        p = Path(path_str)
        if not p.exists() and (Path("core") / p).exists():
            p = Path("core") / p
        if not p.exists():
            return False, [f"Card file does not exist: '{path_str}'"]
        try:
            with open(p, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if not isinstance(loaded, dict):
                    return False, [f"Card file does not contain a valid YAML object: '{path_str}'"]
                data = loaded
        except Exception as ex:
            return False, [f"Failed to parse YAML card from '{path_str}': {ex}"]
    elif isinstance(card_path_or_dict, dict):
        data = card_path_or_dict
    else:
        return False, ["Input must be a file path or dictionary"]

    # 1. Schema version
    if data.get("schema_version") != "dnk-plugin/v1.0":
        errors.append(f"Invalid schema_version: expected 'dnk-plugin/v1.0', got '{data.get('schema_version')}'")

    # 2. Basic fields
    for field in ["id", "name", "version", "kind", "lifecycle"]:
        if not data.get(field):
            errors.append(f"Missing required field: '{field}'")

    # 3. Lifecycle invariant: must be sandbox
    lifecycle = str(data.get("lifecycle", "")).strip().lower()
    if lifecycle != "sandbox":
        errors.append(f"Card lifecycle must be 'sandbox', got: '{data.get('lifecycle')}'")

    # 4. Kind validation
    kind = str(data.get("kind", "")).strip().lower()
    if kind not in VALID_PLUGIN_KINDS:
        errors.append(f"Invalid kind: '{data.get('kind')}'. Allowed: {sorted(list(VALID_PLUGIN_KINDS))}")

    # 5. Origin validation
    origin = data.get("origin")
    if not isinstance(origin, dict):
        errors.append("Missing or invalid 'origin' section")
    else:
        if origin.get("type") != "open_source":
            errors.append(f"Origin type must be 'open_source' for GitHub intake, got: '{origin.get('type')}'")
        repo_url = origin.get("repository_url")
        if not repo_url or not str(repo_url).startswith("https://"):
            errors.append(f"Origin repository_url must start with 'https://', got: '{repo_url}'")
        sha = str(origin.get("commit_sha", "")).strip()
        if len(sha) < 6 or len(sha) > 64 or not all(c in string.hexdigits for c in sha):
            errors.append(f"Origin commit_sha must be a hex string of length 6..64, got: '{sha}'")
        spdx = str(origin.get("license_spdx", "")).strip()
        if spdx not in KNOWN_SPDX_LICENSES:
            errors.append(f"Unknown or unsupported license_spdx: '{spdx}'. Must be in known SPDX list.")
        prov = origin.get("provenance_note")
        if prov and not is_relative_path(prov):
            errors.append(f"Origin provenance_note must be a relative path: '{prov}'")

    # 6. Entrypoint validation
    entrypoint = data.get("entrypoint")
    if not isinstance(entrypoint, dict):
        errors.append("Missing or invalid 'entrypoint' section")
    else:
        ref = entrypoint.get("reference")
        if not ref:
            errors.append("Entrypoint reference cannot be empty")
        elif not is_relative_path(ref):
            errors.append(f"Entrypoint reference must be a relative path: '{ref}'")

    # 7. Permissions validation: strictly default-deny
    permissions = data.get("permissions")
    if not isinstance(permissions, dict):
        errors.append("Missing or invalid 'permissions' section")
    else:
        for perm_name in ["filesystem", "network", "secrets", "git", "database", "external_write"]:
            val = permissions.get(perm_name)
            if val != "none":
                errors.append(
                    f"Permissions violation: Intake cards must strictly use default-deny ('none') permissions. Found '{perm_name}: {val}'"
                )

    # 8. Governance validation
    governance = data.get("governance")
    if not isinstance(governance, dict):
        errors.append("Missing or invalid 'governance' section")
    else:
        if not governance.get("owner"):
            errors.append("Governance owner must not be empty")
        if governance.get("sandbox_profile") != "default-deny":
            errors.append(f"Governance sandbox_profile must be 'default-deny', got: '{governance.get('sandbox_profile')}'")
        if governance.get("approval_required_for_activation") is not True:
            errors.append("Governance approval_required_for_activation must be true")
        for ep in governance.get("evidence_paths", []):
            if not is_relative_path(ep):
                errors.append(f"evidence_path must be a relative path: '{ep}'")
        ctp = governance.get("contract_test_path")
        if ctp and not is_relative_path(ctp):
            errors.append(f"contract_test_path must be a relative path: '{ctp}'")
        srp = governance.get("security_review_path")
        if srp and not is_relative_path(srp):
            errors.append(f"security_review_path must be a relative path: '{srp}'")

    # 9. Compatibility validation
    compatibility = data.get("compatibility")
    if not isinstance(compatibility, dict):
        errors.append("Missing or invalid 'compatibility' section")
    else:
        if not compatibility.get("harness_api_version"):
            errors.append("Compatibility harness_api_version must not be empty")

    return (len(errors) == 0, errors)


def generate_github_plugin_card(
    intake: GitHubIntakeModel, output_path: Optional[str] = None
) -> str:
    """Validates intake, builds PluginCard, verifies schema, and writes YAML to destination."""
    target_path_str = (
        output_path
        or intake.generated_card_path
        or f"templates/plugin/github/{intake.plugin_id}_card.yaml"
    )

    if not is_relative_path(target_path_str):
        raise ValueError(f"Output path must be strictly relative, got: '{target_path_str}'")

    target_path = Path(target_path_str)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    card_dict = build_plugin_card_dict(intake)

    # Validate generated card against intake rules
    is_valid, errors = validate_github_plugin_card(card_dict)
    if not is_valid:
        raise ValueError(f"Generated card failed validation: {'; '.join(errors)}")

    # Format header and YAML
    mrh_header = (
        f"# --- DNK-MRH-HEADER ---\n"
        f'# mrh_id: "{target_path_str}"\n'
        f'# purpose: "Open Source Plugin Card imported from GitHub ({intake.plugin_id})"\n'
        f"# canonical_source: true\n"
        f"# alters_files: []\n"
        f"# triggers_tasks: []\n"
        f'# status: "Draft"\n'
        f'# version: "0.1.0"\n'
        f'# updated_at: "2026-09-09"\n'
        f'# author: "DNK-e.com Maksym"\n'
        f"# --- END DNK-MRH-HEADER ---\n\n"
    )

    yaml_content = yaml.dump(card_dict, sort_keys=False, default_flow_style=False)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(mrh_header + yaml_content)

    return target_path_str
