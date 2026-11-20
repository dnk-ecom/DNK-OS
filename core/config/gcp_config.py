# --- DNK-MRH-HEADER ---
# mrh_id: "core/config/gcp_config.py"
# purpose: "Canonical SSOT configuration provider for Google Cloud and Vertex AI settings."
# canonical_source: true
# alters_files: [".dnk_active_project.env"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
import re
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_REGION = "global"

class GCPConfigurationError(RuntimeError):
    """Raised when GCP credentials or active project cannot be resolved."""
    pass


def find_ssot_env_file() -> Optional[Path]:
    """Search for canonical .dnk_active_project.env or ~/.hermes/.env."""
    current_dir = Path(__file__).resolve().parent
    candidates = [
        current_dir.parent.parent / ".dnk_active_project.env",
        Path.cwd() / ".dnk_active_project.env",
        Path.cwd().parent / ".dnk_active_project.env",
        Path.home() / ".hermes" / ".env",
        Path.home() / ".hermes" / ".dnk_active_project.env",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def load_dnk_active_env(force_reload: bool = False) -> Dict[str, str]:
    """
    Loads active GCP project credentials from SSOT .dnk_active_project.env into os.environ.
    Returns parsed dictionary of key-value pairs.
    """
    env_path = find_ssot_env_file()
    config: Dict[str, str] = {}

    if env_path and env_path.is_file():
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    key = k.strip()
                    val = v.strip().strip("\"'")
                    config[key] = val
                    if force_reload or key not in os.environ:
                        os.environ[key] = val
        except Exception as e:
            logger.warning(f"Failed to read SSOT env file at {env_path}: {e}")

    # Fallback to gcloud CLI if environment variables are missing
    if "GOOGLE_CLOUD_PROJECT" not in os.environ and "VERTEX_PROJECT_ID" not in os.environ:
        try:
            proj = subprocess.check_output(
                ["gcloud", "config", "get-value", "project"],
                stderr=subprocess.DEVNULL,
                timeout=3
            ).decode().strip()
            if proj:
                os.environ["GOOGLE_CLOUD_PROJECT"] = proj
                os.environ["VERTEX_PROJECT_ID"] = proj
                config["GOOGLE_CLOUD_PROJECT"] = proj
                config["VERTEX_PROJECT_ID"] = proj
        except Exception:
            pass

    if "GCP_ACTIVE_ACCOUNT" not in os.environ:
        try:
            acc = subprocess.check_output(
                ["gcloud", "config", "get-value", "account"],
                stderr=subprocess.DEVNULL,
                timeout=3
            ).decode().strip()
            if acc:
                os.environ["GCP_ACTIVE_ACCOUNT"] = acc
                config["GCP_ACTIVE_ACCOUNT"] = acc
        except Exception:
            pass

    if "VERTEX_REGION" not in os.environ:
        os.environ["VERTEX_REGION"] = config.get("VERTEX_REGION", DEFAULT_REGION)
        config["VERTEX_REGION"] = os.environ["VERTEX_REGION"]

    # Ensure VERTEX_BASE_URL is generated if missing
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("VERTEX_PROJECT_ID")
    region = os.environ.get("VERTEX_REGION", DEFAULT_REGION)
    if project:
        computed_url = f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/{region}/publishers/google"
        if "VERTEX_BASE_URL" not in os.environ:
            os.environ["VERTEX_BASE_URL"] = computed_url
            config["VERTEX_BASE_URL"] = computed_url

    return config


def get_active_gcp_project() -> str:
    """Returns active Google Cloud Project ID from SSOT or raises GCPConfigurationError."""
    load_dnk_active_env()
    project = (
        os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("VERTEX_PROJECT_ID")
        or os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
    )
    if not project:
        raise GCPConfigurationError(
            "No active Google Cloud Project ID configured. "
            "Please run: ./scripts/switch_gcp_account.sh <EMAIL> <PROJECT_ID> [REGION]"
        )
    return project.strip()


def get_active_gcp_account() -> str:
    """Returns active Google Cloud Account email from SSOT or raises GCPConfigurationError."""
    load_dnk_active_env()
    account = os.environ.get("GCP_ACTIVE_ACCOUNT")
    if not account:
        raise GCPConfigurationError(
            "No active Google Cloud Account configured. "
            "Please run: ./scripts/switch_gcp_account.sh <EMAIL> <PROJECT_ID> [REGION]"
        )
    return account.strip()


def get_active_vertex_region() -> str:
    """Returns active Vertex AI Region from SSOT (default: 'global')."""
    load_dnk_active_env()
    return os.environ.get("VERTEX_REGION", DEFAULT_REGION).strip()


def get_active_vertex_base_url() -> str:
    """Returns active Vertex AI Base URL for Gemini models."""
    load_dnk_active_env()
    base_url = os.environ.get("VERTEX_BASE_URL")
    if base_url:
        return base_url.strip()

    project = get_active_gcp_project()
    region = get_active_vertex_region()
    return f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/{region}/publishers/google"


def get_gcp_project_pool() -> List[Dict[str, str]]:
    """
    Returns available project pool. If a pool configuration file exists, reads it;
    otherwise returns the currently active project dynamically.
    """
    pool_file = Path(__file__).resolve().parent.parent.parent / "infra" / "config" / "gcp_pool.json"
    if pool_file.is_file():
        try:
            import json
            return json.loads(pool_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Error loading GCP pool from {pool_file}: {e}")

    # Fallback to single active project dynamically (zero hardcoded strings!)
    return [{
        "account": get_active_gcp_account(),
        "project": get_active_gcp_project(),
        "region": get_active_vertex_region(),
    }]
