# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/thoughtdag_contract_002_context_wires.md"
# purpose: "CONTRACT-002 ThoughtDAG Context Engineering, Wires & Staleness Fingerprinting reference."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-16"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# CONTRACT-002: ThoughtDAG Context Engineering & Context Wires Reference

## 1. Architectural Invariants
1. **Living ThoughtDAG Note vs Whiteboard**:
   - `ThoughtDagNoteNode` is a first-class interactive ReactFlow node (`type: 'thoughtdag_note'`).
   - It is NOT a static whiteboard shape. It possesses rich markdown editing, tag parsing (`#tag`), highlight modes (`all` vs `selective`), and reactive state propagation.
2. **Context Wire Directionality**:
   - Wires (`wire_type: 'context'`, edge type `context_wire`) connect strictly from Note to downstream Agent/Task nodes (`source: note`, `target: agent/task`).
   - Cycles are strictly prohibited: topological sort validates acyclicity before compilation.
3. **Context Scope Modes**:
   - `full`: Entire note markdown body is assembled.
   - `tag`: Only lines containing matching `#tag` tokens are extracted.
   - `highlight`: Only manually highlighted text blocks are assembled into prompt context.

## 2. Deterministic SHA-256 Staleness Detection
- **Upstream Fingerprint**: Calculated by hashing the sorted concatenation of all upstream compiled context blocks:
  ```python
  hasher = hashlib.sha256()
  for block in sorted(upstream_blocks):
      hasher.update(block.encode('utf-8'))
  fingerprint = hasher.hexdigest()
  ```
- **Staleness Flag**:
  Downstream agent nodes compare `upstream_fingerprint != last_executed_fingerprint`.
  When stale, UI displays `⚠️ STALE CONTEXT` and offers `⚡ Sync & Re-run` action.

## 3. API & Middleware Invariants
- Endpoints:
  - `POST /api/v1/thoughtdag/compile`: Assembles topological ancestor context.
  - `POST /api/v1/thoughtdag/staleness`: Checks staleness against cached fingerprint.
  - `POST /api/v1/thoughtdag/transpile/obsidian`: Converts Obsidian callout markdown to DAG notes.
  - `GET /api/v1/thoughtdag/health`: Service health and protocol verification.
- **Tenant Isolation**:
  All requests MUST supply `X-Workspace-ID: <workspace_id>` header (e.g. `ws-alpha-001`).
- **Server Lifecycle**:
  When new FastAPI routers are registered, ensure background uvicorn workers are restarted to avoid hanging reloaders or 500 errors.
