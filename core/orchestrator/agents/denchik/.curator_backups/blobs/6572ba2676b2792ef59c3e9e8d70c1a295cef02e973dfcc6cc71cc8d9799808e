# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/architecture-invariants-and-blast-radius/references/verifiable_evidence_gate_and_anti_status_laundering_protocol.md"
# purpose: "Verifiable Evidence Gate and Anti-Status Laundering Protocol for Subagent Validation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ Verifiable Evidence Gate & Anti-Status Laundering Protocol

## 1. Problem: Delegated Status Laundering
Autonomous coding subagents emit self-reports claiming success (e.g., `"status": "completed"`, `"summary": "Successfully updated files and all tests pass"`). Without physical evidence gates, these self-reports can mask failures:
- Target files were never touched or modified.
- Tests were never actually executed or failed with exit code != 0.
- Worker process crashed, yet emitted `"status": "completed"`.
- Future turns or upstream orchestrators accept these false claims as verified facts ("Status Laundering").

## 2. Operating Invariants

### Invariant 1: Split Authority (Zero-Trust Worker)
Subagents are strictly unverified workers; they are physically forbidden from grading or certifying their own work.
Any worker status `"completed"` is treated as `UNVERIFIED_CLAIM` until verified by `VerifiableEvidenceGate`.

### Invariant 2: Pre/Post SHA-256 Fingerprinting
Before launching any worker:
1. Orchestrator computes initial SHA-256 hashes for all declared `target_files`.
2. Upon task termination, `VerifiableEvidenceGate` recalculates SHA-256 hashes.
3. If `require_mutation=True` and target files are untouched (`old_hash == new_hash`), the claim is rejected with `LaunderingFlag.TARGET_FILES_UNTOUCHED`.

### Invariant 3: Empirical Test Logs Required
Claims of "tests passed" are rejected unless backed by:
- Non-empty raw test runner stdout/stderr logs (`[RAW]`).
- Clean exit code 0 from the runner.
- Absence triggers `LaunderingFlag.TEST_PASS_CLAIM_WITHOUT_RAW_LOGS`.

### Invariant 4: Stale Verdict Invalidation
- `is_verdict_stale(result, current_hashes)` checks whether target files were modified after the verification timestamp.
- If changed, the verdict is flagged as `STALE`, mandating a re-audit.

### Invariant 5: Root Directory Hygiene Check Before Action
Per user guidance ("все по черзі, аналізувати кореневу директорію"), always verify the Canonical 8-Root directories (`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`) before initiating multi-step tasks.
