<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/obsidian_visual_shell_harness/references/agent_control_rest_api.md"
# purpose: "Reference guide for Agent programmatic control of Obsidian via Local REST API and MCP."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-26"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

# 🔌 Agent Programmatic Control (REST API & MCP Bridge)

Autonomous agents in the DNK OS swarm (such as **Antigravity** and **Gerych Prime**) can programmatically observe and manipulate the running Obsidian Visual Shell without requiring GUI automation.

---

## 🔑 Authentication & Port Configuration

The server runs locally by default via the `obsidian-local-rest-api` community plugin:
- **HTTP Insecure Port**: `27123`
- **HTTPS Secure Port**: `27124`
- **Default Bearer Token**: `1dc2362c168969e165c56a216137db69788189bb9dfc5e1071d3025ded21a42f`

All API requests must include the header:
```http
Authorization: Bearer 1dc2362c168969e165c56a216137db69788189bb9dfc5e1071d3025ded21a42f
```

---

## 📡 Essential REST Endpoints

### 1. Health & Vault Status
```http
GET http://127.0.0.1:27123/
```
**Response**:
```json
{
  "status": "OK",
  "manifest": { "id": "obsidian-local-rest-api", "version": "5.1.0" },
  "versions": { "obsidian": "1.14.5", "self": "5.1.0" },
  "service": "Obsidian Local REST API",
  "authenticated": true
}
```

### 2. Querying Active File
```http
GET http://127.0.0.1:27123/active/
```
Returns the full text / raw markdown content of the note currently focused in the frontmost tab of Obsidian.

### 3. Programmatic Navigation (Open File)
```http
POST http://127.0.0.1:27123/open/{relative_path}
```
Example:
```bash
curl -s -X POST -H "Authorization: Bearer 1dc2362c168969e165c56a216137db69788189bb9dfc5e1071d3025ded21a42f" \
  "http://127.0.0.1:27123/open/docs/notes/my%20Notes.excalidraw.md"
```
Forces Obsidian's active tab to navigate to the specified note and activates its registered view renderer (`excalidraw-icon`, `markdown`, etc.).

### 4. Executing Internal Commands
```http
POST http://127.0.0.1:27123/commands/{command_id}/
```
Key Command IDs:
- `app:reload` -> Force-reloads the Electron webview, invalidating stale memory caches.
- `obsidian-excalidraw-plugin:toggle-excalidraw-view` -> Switches active tab between raw markdown and interactive whiteboard.
- `k-plex:kplex-start` -> Launches the K-Plex spatial relational navigator.
- `dataview:dataview-force-refresh-views` -> Flushes Dataview caches and re-computes all active tables.

---

## 🐍 Python Swarm Client Implementation

```python
import urllib.parse
import urllib.request
import json
from typing import Optional, Dict, Any

class ObsidianHarnessClient:
    """Headless controller for the running Obsidian Visual Shell."""

    def __init__(self, port: int = 27123, token: str = "1dc2362c168969e165c56a216137db69788189bb9dfc5e1071d3025ded21a42f"):
        self.base_url = f"http://127.0.0.1:{port}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        payload = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=payload, headers=self.headers, method=method)
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body.strip().startswith(("{", "[")) else body

    def ping(self) -> bool:
        try:
            res = self._request("GET", "/")
            return res.get("status") == "OK"
        except Exception:
            return False

    def reload_app(self) -> None:
        """Trigger instant Electron reload without save."""
        self._request("POST", "/commands/app:reload/")

    def open_document(self, relative_vault_path: str) -> None:
        """Instruct Obsidian to focus the target document."""
        encoded = urllib.parse.quote(relative_vault_path)
        self._request("POST", f"/open/{encoded}")

    def execute_command(self, command_id: str) -> None:
        self._request("POST", f"/commands/{command_id}/")
```
