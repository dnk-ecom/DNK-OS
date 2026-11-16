# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_mixar_tool.py"
# purpose: "Native Hermes & DNK OS Dual-Surface tool for Mixar 3D & Blender Cinematography orchestration."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import glob
import json
import logging
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("DNKMixarTool")

MIXAR_HUB_DIR = Path.home() / ".mixar" / "hub"
DEFAULT_SIDECAR_PORT = 7733


def _get_live_mixar_connection() -> tuple[int, str]:
    """Retrieves port and bearer token for the running Mixar instance."""
    json_files = glob.glob(str(MIXAR_HUB_DIR / "*.json"))
    if not json_files:
        raise RuntimeError("No active Mixar instance found in ~/.mixar/hub/. Ensure /Applications/Mixar.app is running.")
    
    # Read the latest json record
    latest_file = max(json_files, key=os.path.getmtime)
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    port = data.get("port", DEFAULT_SIDECAR_PORT)
    token = data.get("token", "")
    return port, token


def _sidecar_request(method: str, path: str, body: Optional[Dict[str, Any]] = None, timeout: int = 15) -> Any:
    """Executes an authenticated HTTP request to Mixar loopback sidecar."""
    port, token = _get_live_mixar_connection()
    url = f"http://127.0.0.1:{port}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "image" in content_type:
                return resp.read()
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        raise RuntimeError(f"Mixar sidecar returned HTTP {e.code}: {err_msg}")
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with Mixar sidecar: {e}")


def dnk_mixar_status() -> str:
    """
    Checks the status and health of the active Mixar instance.
    Returns:
        JSON string with health, instance_id, scene name, and object count.
    """
    try:
        res = _sidecar_request("GET", "/health")
        return json.dumps(res, indent=2, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def dnk_mixar_get_scene() -> str:
    """
    Retrieves the full 3D scene hierarchy, object names, types, locations, and render engine.
    Returns:
        JSON string describing the scene graph and objects.
    """
    try:
        res = _sidecar_request("GET", "/scene")
        return json.dumps(res, indent=2, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def dnk_mixar_capture_viewport(output_path: str = "artifacts/mixar_viewport.png") -> str:
    """
    Captures a live high-resolution 1080p PNG screenshot of the current Mixar 3D viewport.
    Args:
        output_path: Destination file path for the screenshot PNG.
    Returns:
        JSON string confirming capture and saved image path.
    """
    try:
        img_bytes = _sidecar_request("GET", "/viewport.png", timeout=30)
        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(img_bytes)
        return json.dumps({
            "ok": True,
            "saved_to": str(dest.resolve()),
            "bytes": len(img_bytes)
        }, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def dnk_mixar_send_prompt(prompt: str) -> str:
    """
    Injects a text prompt directly into Mixar's internal chat interface (Mixie Chat).
    Args:
        prompt: Instruction or scene description to inject.
    Returns:
        JSON string confirming queue status.
    """
    try:
        res = _sidecar_request("POST", "/prompt", body={"prompt": prompt})
        return json.dumps(res, indent=2, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def dnk_mixar_export_scene(export_format: str = "glb", object_names: Optional[list] = None) -> str:
    """
    Exports the current Mixar scene or specific objects to GLB, USD, or FBX format.
    Args:
        export_format: "glb", "usd", or "fbx".
        object_names: Optional list of specific object names to export. None exports all.
    Returns:
        JSON string with export result and file path.
    """
    try:
        res = _sidecar_request("POST", "/export", body={
            "format": export_format,
            "object_names": object_names
        }, timeout=60)
        return json.dumps(res, indent=2, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)
