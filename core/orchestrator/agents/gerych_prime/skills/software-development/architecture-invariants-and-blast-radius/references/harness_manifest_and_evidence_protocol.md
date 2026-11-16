# Harness Architecture Manifest & Evidence Audit Protocol

## Overview
This protocol defines the strict procedure for drafting canonical Agentic Harness architecture specifications and empirical evidence audits without mutating runtime code or introducing unsubstantiated claims.

---

## 1. Five-Layer Harness Taxonomy
When specifying or refactoring an agentic harness, strictly separate concerns across 5 discrete layers:

1. **Layer 1: Model Provider Adapters**
   - Pure abstraction interface (`ModelAdapter` protocol) for foundation models.
   - Decoupled from provider APIs (Vertex AI / Gemini, Claude, DeepSeek, Local vLLM/llama.cpp).
   - Zero business or state logic.

2. **Layer 2: Harness Kernel**
   - Lifecycle loops, transaction orchestration, memory management (SCONES), OCC 3-way graph merging, SpendGuard token governance.
   - Explicit non-responsibilities: NO UI rendering, NO domain-specific business rules, NO heavy in-tree third-party frameworks.

3. **Layer 3: Sovereign Agent Profile & Swarm Orchestration**
   - Agent identity (`SOUL.md`), linguistic contracts (UA dialogue / EN artifacts), behavioral instincts.
   - Mandatory Atomic Slice Execution (MASE: ≤25 tool calls/slice).
   - Swarm topology routing (14 specialized agent roles).

4. **Layer 4: Capability Plugins & Domain Services**
   - Headless assimilated tools, FastMCP endpoints, isolated subagent sandboxes.
   - Formal service card (`service_manifest.yaml`) defining metadata, blast radius, token limits, and contracts.
   - Deterministic 5-stage lifecycle state machine: `draft` ──► `sandbox` ──► `evaluated` ──► `active` ──► `deprecated`.

5. **Layer 5: Spatial Canvas Control Plane**
   - Interactive infinite node workspace (`apps/web/`).
   - Human-in-the-loop / on-the-loop cockpit.
   - Visualizes TaskDAG, telemetry HUD, reactive node previews, and gates irreversible actions via explicit user approvals.

---

## 2. Invariant: Strict Non-Goals Guardrail
During architecture manifest authoring:
- **No Runtime Code Modifications:** Do NOT touch production files in `apps/`, `core/`, or `services/`.
- **No Plugin Creation or Scaffolding:** Do NOT generate stub plugins during a spec task.
- **No Module Relocations:** Do NOT move or refactor directory trees.
- **No Benchmark Superiority Claims:** Reject marketing hype and claims of speed/accuracy superiority unless backed by reproducible test artifacts.

---

## 3. The Tri-Artifact Delivery Pattern
Every architecture manifest task must produce three synchronized deliverables:

| Deliverable | Standard Location | Content & Purpose |
|---|---|---|
| **1. Specification** | `docs/specs/<NAME>_MANIFEST_vX.Y.md` | Formal canonical specification, layers, contracts, lifecycles, and security gates. |
| **2. Executive Note** | `docs/notes/<ID>_<name>.md` | Founder-level synthesis in Obsidian vault format (YAML frontmatter, MRH header, visual diagrams, actionable choices). |
| **3. Evidence Audit** | `docs/audit/<NAME>_evidence.json` | Machine-readable JSON tracking every capability claim with verified file and test paths. |

---

## 4. Evidence Classification Rule (Zero Hallucination)
Every claim of an implemented feature must be categorized under one of three statuses:

- `PROVEN`: Verified by existing source code AND matching automated tests with 100% pass rate.
  - Requires: `source_path`, `evidence_path` (test file).
- `PARTIAL`: Core backend engine or prototype exists, but UI integration or multi-provider coverage is incomplete.
  - Requires: `source_path`, `evidence_path`, explanatory notes.
- `DESIGN`: Documented specification, interface, or target state machine not yet implemented in code.
  - Requires: `source_path` pointing to spec.

---

## 5. Completion Report Schema
At task completion, emit a machine-readable YAML block:
```yaml
status: COMPLETED | PARTIAL | BLOCKED
files_created:
  - path/to/spec.md
  - path/to/note.md
  - path/to/evidence.json
runtime_changed: false
aab_changed: false
claims:
  proven: [...]
  partial: [...]
  design_only: [...]
decisions_required_from_maksym: [...]
commit: "<sha>"
```

---

## 6. Checksum Integrity & Pre-Commit Whitespace Hygiene
When producing evidence audits containing cryptographic checksums (e.g. SHA-256 in `*_evidence.json`):

1. **Whitespace Normalization First**:
   - Markdown documents frequently accumulate trailing whitespace (e.g., double spaces for line breaks), triggering errors in `git diff --check` and git pre-commit hooks.
   - Run trailing whitespace cleanup and ensure single EOF newline across all deliverables *before* calculating cryptographic hashes.

2. **Atomic Checksum Recalculation**:
   - Generate SHA-256 hashes strictly after formatting is finalized. Any subsequent edit, newline adjustment, or lint fix invalidates the hashes and causes evidence verification tests to fail.
   - Verify SHA-256 hashes via test runner (`pytest tests/integration/test_*_evidence.py`).

3. **Staged Diff Gate**:
   - Always run `git diff --cached --check` immediately before committing. Ensure exit code 0 (no whitespace errors or unmerged boundaries).

