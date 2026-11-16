# Hermes Managed Instance Gateway & OnePersonCompany Pattern

# --- DNK-MRH-HEADER ---
# mrh_id: "references/hermes_managed_instance_gateway_and_opc_pattern.md"
# purpose: "Architecture pattern for spawning, supervising, and interacting with Hermes Agent via native Gateway API on port 8642."
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-25"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

## 📌 1. Architecture Overview
When building external dashboards, multi-agent command centers, or solopreneur platforms (such as `tashfeenahmed/OnePersonCompany`), external orchestrators often need to spawn and control **Hermes Agent** as a headless or managed subprocess.

### 🔑 Critical Hermes Port Differentiation
- **Port 8645 (`hermes proxy`)**: Proxies LLM completions to upstream providers. Does NOT run the agent loop or execute tools.
- **Port 8642 (`hermes gateway run`)**: The true **Agent Execution Door**. When enabled, it exposes an OpenAI-compatible REST server:
  - `GET /v1/models` → returns `{"data": [{"id": "hermes-agent"}]}`
  - `POST /v1/chat/completions` → directly executes the **Hermes Agent loop** (with active tools, skills, and memory). Calling this endpoint drives the agent, not just a bare LLM.

---

## ⚡ 2. Environment & Gateway Launch Recipe

To run Hermes as a managed background agent server:

```bash
# 1. Configure in $HERMES_HOME/.env or process environment
export API_SERVER_ENABLED="true"
export API_SERVER_KEY="sk-hermes-managed-internal"
export API_SERVER_HOST="127.0.0.1"
export API_SERVER_PORT="8642"

# 2. Launch Gateway process
hermes gateway run
```

### Probing Readiness
Poll `GET http://127.0.0.1:8642/v1/models` with header `Authorization: Bearer sk-hermes-managed-internal`:
- Wait until status code `200` and response contains `"id": "hermes-agent"`.
- Typical boot latency: 1.5s – 3.0s.

---

## 🔄 3. Agent Execution Protocol (OpenAI-Compatible Bridge)

To dispatch a task to the managed Hermes Agent from any backend (FastAPI, Hono, Node.js, Go):

```typescript
const response = await fetch("http://127.0.0.1:8642/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-hermes-managed-internal"
  },
  body: JSON.stringify({
    model: "hermes-agent",
    messages: [
      { role: "user", content: "Execute task: audit venture metrics and report status" }
    ],
    stream: false
  })
});
const result = await response.json();
// result.choices[0].message.content contains the completed execution output
```

---

## 🏛️ 4. Zero-Bloat Solopreneur Stack (OnePersonCompany Baseline)

For lightweight local command centers (Node 24+ SOTA):
1. **Zero-build Backend**:
   - Runtime: `node --experimental-strip-types`
   - Framework: Hono (`@hono/node-server`)
   - 0 heavyweight ORMs; pure native `node:sqlite` (`DatabaseSync`).
2. **SQLite WAL Hygiene**:
   ```sql
   PRAGMA journal_mode = WAL;
   PRAGMA synchronous = NORMAL;
   PRAGMA busy_timeout = 5000;
   ```
3. **Decoupled Roles**:
   - Chief of Staff (Task prioritization & inbox triage)
   - Growth & SEO Ops (Rank checks & automated audits)
   - Media Studio (Video script synthesis & render pipelines)
   - Autopilot / Proactive Signals (Health checks, churn signals, domain expiry)
