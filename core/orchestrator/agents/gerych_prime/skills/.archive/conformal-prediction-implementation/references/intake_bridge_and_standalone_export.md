# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/conformal-prediction-implementation/references/intake_bridge_and_standalone_export.md"
# purpose: "Reference guide for System One Intake Bridge, Conformal Metadata propagation, and Standalone Export Invariant."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# System One Intake Bridge & Standalone Export Reference

## 1. Intake Bridge Architecture
In `core/orchestrator/task_triage.py`:
- `dnk_triage_task` runs `FastTriageEngine(alpha=0.10)` on entry.
- Complexity score calculation:
  $$C = F_{\text{files}} + 2 \times D_{\text{domains}} + 3 \times S_{\text{stages}}$$
- Calibrated probability margin (OOD Delta):
  $$\Delta = P_{\text{top1}} - P_{\text{top2}}$$
- When $\Delta < 0.20$ or confidence $< 0.90$, task automatically flags `escalated_to_system_two = True`.
- `TriageResult` carries:
  - `calibrated_confidence`: float in $[0.0, 1.0]$
  - `ood_delta`: margin between top two predicted choices
  - `conformal_set`: list of viable execution modes within $(1 - \alpha)$ coverage
  - `escalated_to_system_two`: boolean escalation gate

## 2. Standalone App Export Invariant
- Defined in `scripts/system/export_standalone_app.py`.
- `core/system_one` is registered in `essential_dirs` as a core engine.
- Zero-Torch Invariant: `core/system_one` MUST NOT depend on `torch`, `torchvision`, or heavy C++ binaries. Pure Python + NumPy only.
- Standalone export command:
  ```bash
  python3 scripts/export_standalone_app.py --target-dir <TARGET_DIR>
  ```
- Export validation executes in-target pytest suite verifying clean execution in isolated environment.
