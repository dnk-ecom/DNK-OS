# --- DNK-MRH-HEADER ---
# mrh_id: "references/agentic_microkernel_ssot_contracts_and_mcp_compat.md"
# purpose: "Canonical protocol for DNK OS Agentic Microkernel SSOT contracts (ADR-091) and FastMCP compatibility."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-13"
# author: "Gerych Prime & DNK OS"
# --- END DNK-MRH-HEADER ---

# Agentic Microkernel SSOT Contracts & FastMCP Compatibility Protocol

## 1. Problem & Context
When moving from fragmented agent scripts to an integrated Agentic Operating System, agents often fall into one of two antipatterns:
1. **Blind Implementation**: Writing monolithic, untested worker logic that breaks existing services or runs out of tool budget.
2. **Planning Paralysis (Spec Bloat)**: Writing exhaustive 50-page markdown documents that never translate into executing code or machine-enforced gates.

Furthermore, dynamic MCP tool loading can encounter breaking upstream changes (e.g. `mcp>=2.0.0` breaking `FastMCP 3.4.6` low-level server APIs).

## 2. Contract-Driven Thin Slice Protocol (4 Slices)
To bridge specification and implementation without bloat:
1. **Slice 1: Baseline Hygiene & Clean Working Tree**:
   - Ensure `git status` is 100% clean.
   - Run root hygiene guard and dependency verification before introducing architectural primitives.
2. **Slice 2: Formal ADR & Pydantic SSOT Contracts**:
   - Author concise ADR (`docs/architecture/adr/ADR-091-*.md`).
   - Define typed, machine-enforced models in `core/kernel/contracts.py`:
     - `KernelTaskRequest`: Goal, task ID, required `target_files` (whitelist), and `negative_scope`.
     - `KernelTriageReceipt`: Deterministic complexity score ($C = F + 2D + 3S$), mode (`SOLO`, `SWARM_PARALLEL`, `SWARM_SEQUENTIAL`), assigned agents, parallel batches.
     - `KernelDecisionReceipt`: 3-flaws checklist, cryptographic SHA-256 integrity, margin/confidence bounds.
     - `KernelCompletionReceipt`: Deterministic gate verification (`exit_code == 0`, clean git state).
3. **Slice 3: Red-Gate Unit Verification (`tests/core/test_kernel_contract.py`)**:
   - Verify serialization/deserialization, contract bounds, and invariant violations.
   - Test suite must pass 100% Green (`exit_code == 0`) before any agent orchestration code is modified.
4. **Slice 4: Swarm Integration (MASE <= 25)**:
   - Wire contracts into `core/system_one/triage.py` and `dnk_swarm_dispatch`.

## 3. FastMCP vs MCP Upstream Compatibility Invariant
- **Failure Mode**: `FastMCP 3.4.6` relies on `request_ctx` from `mcp.server.lowlevel.server`. In `mcp>=2.0.0`, lowlevel server exports were refactored, causing `ImportError: cannot import name 'request_ctx' from 'mcp.server.lowlevel.server'` and disabling FastMCP tool discovery.
- **Resolution**:
  - Pin `mcp<2.0.0` (canonical: `mcp==1.30.0`) in virtual environment and requirements.
  - Test FastMCP server health via `pytest tests/core/test_thoughtdag_mcp.py tests/core/test_workhorse_fastmcp_servers.py`.
