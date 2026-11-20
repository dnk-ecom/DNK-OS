<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/antigravity_operations/references/mcp_and_tool_integration.md"
# purpose: "Comprehensive reference on Google Antigravity MCP Server integration, auth, and transports."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-23"
# author: "Antigravity & Gerych Prime"
# --- END DNK-MRH-HEADER ---
-->

# Google Antigravity Model Context Protocol (MCP) Reference

The Model Context Protocol (MCP) provides open, two-way integration between Antigravity agents and external toolkits, APIs, and databases.

---

## 1. Configuration File Locations

Antigravity loads MCP servers defined under a root `mcpServers` object in `mcp_config.json`:

- **Workspace Scoped**: `<workspace-root>/.agents/mcp_config.json`
- **Global User**: `~/.gemini/config/mcp_config.json`
- **Plugin Scoped**: `plugins/<plugin_name>/mcp_config.json`

---

## 2. Configuration Schema & Properties

```json
{
  "mcpServers": {
    "local-postgres": {
      "command": "/opt/homebrew/bin/node",
      "args": ["/usr/local/lib/node_modules/@modelcontextprotocol/server-postgres/dist/index.js", "postgresql://localhost/mydb"],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      },
      "cwd": ".",
      "disabled": false,
      "disabledTools": ["destructive_query"]
    },
    "remote-refero": {
      "serverUrl": "https://api.refero.design/mcp",
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer mcp-z4X8iu8Us3j5WjCJ"
      }
    }
  }
}
```

### Property Reference

| Property | Type | Transport | Description |
| :--- | :--- | :--- | :--- |
| `command` | `string` | Stdio | Path to executable (`node`, `python3`, binary). **Mandatory** for stdio. |
| `args` | `string[]` | Stdio | Command line arguments passed to the server binary. |
| `env` | `object` | Stdio | Environment key-value pairs injected into the server process. |
| `cwd` | `string` | Stdio | Working directory where process is launched. |
| `serverUrl` | `string` | Remote | HTTP(S) endpoint for Streamable HTTP or Server-Sent Events (SSE). **Mandatory** for remote. |
| `headers` | `object` | Remote | Custom HTTP headers (API keys, authorization tokens). |
| `authProviderType` | `string` | Remote | Supports `"google_credentials"` for Google Application Default Credentials (ADC). |
| `oauth` | `object` | Remote | Manual OAuth credentials: `{"clientId": "...", "clientSecret": "..."}`. |
| `disabled` | `boolean` | Both | When `true`, temporarily deactivates the server without deleting config. |
| `disabledTools` | `string[]` | Both | List of tool names to hide/withhold from the model context. |

---

## 3. Authentication Patterns

### A. Google Application Default Credentials (ADC)

For Google Cloud endpoints (Vertex AI, Cloud Run, BigQuery MCP):

```json
{
  "mcpServers": {
    "my-gcp-service": {
      "serverUrl": "https://my-service.run.app/mcp",
      "authProviderType": "google_credentials"
    }
  }
}
```

Precondition setup:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project <PROJECT_ID>
```

### B. OAuth 2.0 (Dynamic & Manual)

- **Dynamic Client Registration (DCR)**: Antigravity automatically detects DCR-enabled endpoints without extra config.
- **Manual Credentials**: Provide `oauth: { clientId, clientSecret }`. Ensure redirect URI is configured as:
  `https://antigravity.google/oauth-callback`
- **Token Cache**: Active tokens are stored and auto-refreshed in:
  `~/.gemini/antigravity/mcp_oauth_tokens.json`

### C. Static Bearer Token / API Headers

Add direct authorization tokens in `headers`:

```json
{
  "headers": {
    "Authorization": "Bearer <YOUR_TOKEN>",
    "X-Project-ID": "dnk-ecom-2026"
  }
}
```

---

## 4. Production Pitfalls & Hardening

1. **`env: node: No such file or directory`**:
   - Cause: When Antigravity spawns an MCP process, non-interactive subshells may lack `/opt/homebrew/bin` in standard `PATH`.
   - Fix: Specify absolute binary path (e.g. `/opt/homebrew/bin/node` or `/opt/homebrew/bin/npx`) and inject explicit `"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"` in the `"env"` object.

2. **Context Window Exhaustion (Standing MCP Overhead)**:
   - Heavy servers (Notion MCP ~37k tokens, Chrome DevTools ~15k tokens) bloat the baseline system prompt.
   - Guardrail: Detach or disable heavy MCPs during core coding and refactoring sessions; mount them only for tasks requiring those services.
