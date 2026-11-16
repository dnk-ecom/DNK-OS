# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/saap_fastmcp_dynamic_registry_and_toolrag_protocol.md"
# purpose: "SaaP FastMCP Dynamic Registry Architecture, ServicePluginCard v1alpha2 Specification & Progressive ToolRAG Protocol."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# SaaP FastMCP Dynamic Registry & Progressive ToolRAG Protocol

## 1. Context & Architecture (Phase 3 SaaP Integration)
In Phase 3 of the DNK OS Swarm Architecture, static tool maps in agent harnesses are superseded by declarative, dynamic FastMCP service discovery:
1. **Microservice Discovery Sources (Strict Isolation)**:
   - Tool discovery scans **strictly** inside `services/dnk_*` and `packages/plugins/`.
   - Registration attempts from core directories (`apps/`, `core/`, etc.) are actively blocked as security boundary violations.
2. **Dynamic ToolRAG (Progressive Disclosure)**:
   - Core tools (`read_file`, `write_file`, `patch`, `terminal`, `search_files`) remain universal and always available.
   - Domain-specific tools (e.g. video retention audit, liquid theme validation, Slack alerts, Obsidian syncing) are indexed in `ServiceRegistry.get_fastmcp_tools_catalog()`.
   - The harness dynamically resolves active domain tools by matching task goal intent against plugin tags, tool names, and domain taxonomy, reducing initial agent context overhead by up to 60%.

---

## 2. ServicePluginCard v1alpha2 Manifest Specification
Declarative schema implemented in `core/registry/service_registry.py`:

```yaml
apiVersion: "dnk.os/v1alpha2"
kind: "ServicePluginCard"
metadata:
  service_id: "dnk_video_retention_auditor"
  name: "Video Retention Auditor"
  version: "1.0.0"
  domain: "media_analytics"
  author: "DNK OS Swarm"
  description: "Audits TikTok/Reels pacing, silence intervals, and retention hooks."
  tags: ["video", "retention", "pacing", "ffmpeg"]
spec:
  lifecycle: "active"
  transport:
    protocol: "fastmcp"
    command: "python3"
    args: ["-m", "services.dnk_video_retention_auditor.service"]
    env_passthrough: ["PYTHONPATH"]
  capabilities:
    - name: "dnk_audit_video_retention"
      description: "Analyze video pacing, visual hooks, and silence drops."
      input_schema:
        type: "object"
        properties:
          video_path: {type: "string"}
        required: ["video_path"]
  canvas_widgets:
    - node_type: "retentionAuditorNode"
      display_name: "Retention Auditor Node"
      component_path: "apps/web/src/components/canvas/RetentionAuditorNode.tsx"
  governance:
    spend_guard:
      max_cost_usd_per_run: 0.05
    circuit_breaker:
      failure_threshold: 3
```

---

## 3. Progressive Tool Catalog (ToolRAG) Integration
In `core/framework/canonical_harness_engine.py`:
- `ProgressiveToolCatalog(registry=...)`:
  - Automatically queries `ServiceRegistry.get_fastmcp_tools_catalog()` on initialization or runtime card addition.
  - Dynamically builds `domain_tool_map` and maps tools across detected service domains.
  - Evaluates `resolve_tools_for_goal(goal)`:
    - Tokenizes task goal prompt.
    - Scans intent keywords against domain names and FastMCP tool descriptions.
    - Selectively injects only relevant tool capabilities into active tool definitions.

---

## 4. Key Implementation Invariants & Pitfalls

### 4.1. Security Boundary Enforcement
- FastMCP tool discovery MUST NOT traverse beyond `services/dnk_*` and `packages/plugins/`.
- Attempting to register manifests in arbitrary paths raises an isolated security warning and returns `None`, preventing untrusted sidecars from polluting the swarm tool catalog.

### 4.2. Pre-Commit Git Hygiene Invariant
- `scripts/system/auto_precommit_guard.py` includes a strict untracked files guard.
- When creating new test files under `tests/core/` (e.g. `tests/core/test_saap_fastmcp_registry.py`), the files MUST be explicitly staged via `git add` BEFORE running pre-commit verification, otherwise check 2/8 fails with `❌ GIT HYGIENE ERROR: Found untracked test/router files!`.
