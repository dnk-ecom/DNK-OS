---
name: conformal-prediction-implementation
description: "Use when implementing Conformal Prediction (CP-Router) & FBE uncertainty calibration for System One."
version: 1.0.0
author: DNK-e.com Maksym
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [conformal-prediction, fbe, system-one, calibration, uncertainty, routing]
    related_skills: ["dnk-triage-task", "architecture-invariants-and-blast-radius", "test-driven-development"]
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/conformal-prediction-implementation/SKILL.md"
purpose: "Conformal Prediction & FBE uncertainty quantification and calibration for System One."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.1"
updated_at: "2026-09-17"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

# Conformal Prediction Implementation for System One

## When to Use
Use when implementing uncertainty quantification in System One modules to enable mathematically guaranteed confidence intervals, entropy gating, and adaptive calibration.

## Key Changes Made

### core/system_one/calibrator.py
- Added `compute_conformal_prediction_set()` function for set-based uncertainty quantification
- Implemented FBE (Frequentist Bayesian Estimation) for dynamic probability calibration
- Added entropy-based anomaly detection using binary entropy thresholds
- Enhanced `ChoiceAnswer` class with conformal_alpha parameter for set size control

### core/system_one/escalator.py
- Added conformal prediction validation layer in decision escalation
- Integrated FBE calibration into confidence scoring
- Added entropy-based filtering for ambiguous decisions

### core/system_one/triage.py
- Implemented `FastTriageEngine` and `fast_triage` sub-millisecond classifier using $C = F + 2D + 3S$.
- Integrated `compute_conformal_prediction_set()` with $\alpha=0.10$ for set-based triage decisions.
- Added OOD circuit breaker: escalates to `SWARM_SEQUENTIAL` when top margin $\Delta = P_{\text{top1}} - P_{\text{top2}} < 0.20$ or confidence $< 0.90$.
- Invariant: non-phased atomic tasks must evaluate $S_{\text{stages}} = 0$ ($s_{\text{effective}} = \max(0, s)$) so $F=1, D=0$ resolves to $C=1 \le 3$ (`SOLO`).

### core/orchestrator/task_triage.py (Intake Bridge)
- Wired `FastTriageEngine` directly into `dnk_triage_task` intake handler.
- Propagates calibrated metadata on `TriageResult`: `calibrated_confidence`, `ood_delta`, `conformal_set`, `escalated_to_system_two`.
- Standalone app export verified under `scripts/system/export_standalone_app.py` preserving Zero-Torch Invariant.

### core/system_one/__init__.py
- Added imports for new CP-related functions
- Maintained backward compatibility with existing APIs

## Verification Steps

1. **Unit Tests**:
   - Verify `compute_conformal_prediction_set()` returns valid sets
   - Check entropy calculations match expected values
   - Verify FBE calibration converges to true probabilities

2. **Integration Tests**:
   - Run system with synthetic data showing CP set size variations
   - Verify FBE calibration improves with more data samples

3. **System Validation**:
   - Verify `compute_conformal_prediction_set()` handles edge cases:
     - Empty probability distributions
     - Single-class predictions
     - High-entropy scenarios

## Pitfalls to Avoid

- Never set conformal_alpha > 1.0 (invalid confidence level)
- Ensure probability distributions sum to 1.0 before CP calculation
- Avoid high binary entropy (>0.85) in decision-making
- Maintain proper probability normalization after FBE updates

## References
- [AAAI 2026: CP-Router Paper](https://arxiv.org/abs/2601.01234)
- [LMSYS RouteLLM Documentation](https://lmsys.org/)
- [Conformal Prediction Tutorial](https://www.cs.columbia.edu/~jgonzalv/cp_tutorial.pdf)
- Supporting reference: `references/intake_bridge_and_standalone_export.md` for intake bridge details and standalone export invariants.