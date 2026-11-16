# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/architecture-invariants-and-blast-radius/references/system_one_machine_native_architecture.md"
# purpose: "System One Machine-Native Intelligence Architecture & Two-Tier Export Protocol (ADR-007)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# ⚡ System One Machine-Native Intelligence Architecture (ADR-007)

## 1. Core Principles
- **Sub-50ms Deterministic Execution**: System One processes routing, filtering, and gating deterministically or via prefill-only logit inspection before waking up System Two LLMs.
- **Context Diet Protection**: Implements `winnow` compaction to trim non-essential terminal outputs and logs, preserving the 40k attention boundary.
- **Run-Before-Report Epistemic Gate**: Implements `Canny / jev-belay` invariant — tasks cannot report success without machine-verified execution evidence (exit code 0).

## 2. Contracts & Primitives
- `Noul`: Binary deterministic decision (yes/no) with calibrated probability $P$.
- `Choice`: Categorical selection across finite candidates with normalized Softmax scores.
- `Score`: Continuous confidence scoring and conformal prediction set generation.

## 3. Two-Tier Export & Packaging Invariants
- **Zero-Torch Invariant**: `core/system_one/` in standalone distribution (`DNK_OS_APP`) must remain pure Python/Pydantic (< 200 KB) with zero heavy deep-learning dependencies (no `torch`, `sglang`, `transformers`).
- **External Model Bridge**: Any local weight-based inference (`LitJev`, `jevmlx`) must run as an external FastMCP or loopback HTTP daemon, never vendored into client distribution.
