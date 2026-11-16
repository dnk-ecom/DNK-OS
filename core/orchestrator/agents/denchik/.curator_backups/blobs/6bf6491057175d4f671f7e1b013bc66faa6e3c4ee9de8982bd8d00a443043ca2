# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/verifiable_evidence_gate_and_anti_status_laundering_protocol.md"
# purpose: "Verifiable Evidence Gate and Anti-Status Laundering Protocol for DNK Swarm Subagents."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ Verifiable Evidence Gate & Anti-Status Laundering Protocol (EVID-GATE-001)

## 1. Problem: Delegated Status Laundering (Self-Graded Homework)
When delegating work to autonomous subagents or external LLM workers, workers tend to emit self-reports claiming success (e.g. `"status": "completed"`, `"summary": "Successfully updated files and all tests pass"`). Without physical evidence gates, these self-reports are often hallucinations:
- Target files were never touched or modified.
- Tests were never actually executed or failed with exit code != 0.
- Worker process crashed, yet emitted `"status": "completed"`.
- Future turns accept these false claims as verified facts ("Delegated Status Laundering").

## 2. Core Operating Invariants

### Invariant 1: Split Authority (Zero-Trust Worker)
Subagents are strictly workers; they are physically forbidden from certifying their own output.
Any worker status `"completed"` is treated as `UNVERIFIED_CLAIM` until verified by `VerifiableEvidenceGate`.

### Invariant 2: Pre/Post SHA-256 Fingerprinting
Before launching any worker:
1. `prepare_subagent_environment` calculates initial SHA-256 hashes for all declared `target_files`.
2. Upon return, `VerifiableEvidenceGate` recalculates SHA-256 hashes of all `target_files`.
3. If `require_mutation=True` and target files are untouched (`old_hash == new_hash`), the claim is immediately rejected with `LaunderingFlag.TARGET_FILES_UNTOUCHED`.

### Invariant 3: Empirical Test Logs Required
No claim of "tests passed" or test suite execution is accepted without:
- Non-empty raw test runner stdout/stderr logs (`[RAW]`).
- Exit code 0 from the test runner.
- If missing, the gate triggers `LaunderingFlag.TEST_PASS_CLAIM_WITHOUT_RAW_LOGS`.

### Invariant 4: Stale Verdict Invalidation
Verdicts must be tamper-proof against downstream mutations:
- `is_verdict_stale(result, current_hashes)` checks whether any target file's SHA-256 changed after the evaluation timestamp.
- If modified, the verdict is flagged as `STALE` and a re-audit is mandated.

### Invariant 5: Root Directory Hygiene Check Before Action
Per user guidance ("все по черзі, аналізувати кореневу директорію"), always verify the Canonical 8-Root directories (`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`) before initiating multi-step tasks. Never allow temporary files or scratch directories in `$HUB_ROOT`.

## 3. Reference Implementation Architecture
```
GerychSwarmCoordinator
       │
       ├── 1. evidence_gate.create_contract(task_id, target_files, require_mutation, require_test_pass)
       │      └── Computes pre-run SHA-256 of target_files
       │
       ├── 2. prepare_subagent_environment & Subagent Execution
       │
       ├── 3. harvest_subagent_output
       │      └── Raw subprocess logs & final artifacts
       │
       └── 4. evidence_gate.evaluate(contract, result_data)
              ├── Check Process Crash (exitcode != 0)
              ├── Check Output Artifact Exists & Non-Empty
              ├── Verify File Mutation (SHA-256 changed)
              ├── Verify Raw Test Logs
              └── Final Verdict: PASS / REJECT / AUDIT_REQUIRED
```
