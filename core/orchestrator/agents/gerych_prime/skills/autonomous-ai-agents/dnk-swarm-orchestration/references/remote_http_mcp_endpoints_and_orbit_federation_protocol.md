# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/remote_http_mcp_endpoints_and_orbit_federation_protocol.md"
# purpose: "Protocol for remote HTTP/SSE MCP endpoints, Cloudflare WAF headers, and LLM-MCP compute decoupling (GCP credits vs remote tools)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-21"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🌐 Remote HTTP/SSE MCP Endpoints & Orbit Federation Protocol

## 1. Decoupled Compute & Tooling Model (SSOT)
When connecting Hermes Agent / Gerych to remote external MCP servers (such as Orbit Agents `mcp.orbitagents.xyz`):
- **LLM Reasoning & Tokens**: Handled entirely by the configured local provider (e.g. Google Cloud Vertex AI, Gemini 2.5/Flash). All prompt evaluation, code generation, and tool routing consume the developer's Google Cloud credits/quotas.
- **Remote MCP Execution**: The remote MCP server functions strictly as an RPC provider (tool catalog, database writes, search, external CRM integrations, webhooks). The remote server does not incur LLM inference costs for the agent's cognition unless an internal tool triggers third-party paid APIs (e.g., Apollo lead scrapers).

---

## 2. Remote HTTP Transport & Cloudflare WAF Bypass
Public or cloud-hosted MCP endpoints frequently sit behind Cloudflare or similar reverse-proxy WAFs.

### Common Pitfall: Python `urllib` 403 Forbidden
Calling remote endpoints with bare `urllib.request` or default `python-requests` headers triggers Cloudflare bot challenges (HTTP 403).

### Mandatory Headers Invariant:
When probing or connecting to remote JSON-RPC HTTP MCP endpoints:
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/event-stream, */*",
    "Content-Type": "application/json",
}
```
*Note on HTTP 406*: Streamable HTTP endpoints (e.g. Orbit) require `Accept: application/json, text/event-stream`. Omitting `text/event-stream` triggers `HTTP 406 Not Acceptable`.

### Protocol Validation:
1. **GET Request**: Returns endpoint status: `{"ok": true, "server": "<name>"}`
2. **POST JSON-RPC**: Method discovery via `tools/list`:
   ```json
   {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
   ```

---

## 3. Hermes MCP Dynamic Registration & Dual Config Sync
To bind a remote HTTP/SSE MCP endpoint into the Hermes runtime:

```bash
hermes mcp add <server_name> --url <endpoint_url>
```

### Multi-Profile Config Resolution Gotcha:
Hermes uses `hermes_cli.config.get_config_path()` which resolves to the active agent profile (`core/orchestrator/agents/<profile>/config.yaml`) when running in a workspace/sub-agent environment, or `~/.hermes/config.yaml` when global. Always mirror remote MCP server definitions to both active profile and `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  <server_name>:
    url: "<endpoint_url>"
```

---

## 4. Orbit Federation & Gateway Execution Protocol

### Step 1: Heartbeat-First Announcement (`orbit_heartbeat`)
Every new session must begin with a structured identity announcement:
```json
{
  "name": "orbit_heartbeat",
  "arguments": {
    "agent": {
      "id": "hermes-gerych-prime",
      "name": "Gerych Prime",
      "provider": "google",
      "surface": "gemini",
      "model_family": "gemini-2.5"
    },
    "status": "running",
    "context": "Hermes Agent running on Google Cloud Vertex AI"
  }
}
```
Returns: `agent_id`, `session_id`, `known_projects`, and connected `toolbox`.

### Step 2: Unified External Tool Gateway (`orbit_toolbox`)
External capabilities (Apollo, Apify, PredictLeads, image generation, web scrapers) are not registered as standalone root MCP tools. They are routed via `orbit_toolbox`:
1. `{"action": "list"}` — Discover available tools.
2. `{"action": "describe", "tool": "<name>"}` — Inspect parameter schema.
3. `{"action": "call", "tool": "<name>", "arguments": {...}}` — Execute RPC call.
