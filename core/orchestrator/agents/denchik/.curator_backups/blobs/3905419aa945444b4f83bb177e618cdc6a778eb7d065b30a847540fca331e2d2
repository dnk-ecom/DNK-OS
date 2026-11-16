# --- DNK-MRH-HEADER ---
# mrh_id: "references/deterministic_decision_draft_and_cryptographic_receipts.md"
# purpose: "Canonical Protocol for Deterministic Candidate Selection, Hard Gates, Abstention, and JEV Cryptographic Receipts."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-12"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# ⚖️ Deterministic Decision Engine & JEV Cryptographic Receipts Protocol

## 🎯 1. Overview & Architectural Motivation
In high-autonomy multi-agent swarms (DNK OS), agents frequently select between competing tools, OSS repository blueprints, architectures, and execution plans.
Unconstrained LLM picking suffers from:
1. **Sycophancy & Hallucination**: Models pick arbitrary candidates when candidates are equally mediocre or unsafe.
2. **Untracked Decisions**: No verifiable cryptographic evidence of *why* a candidate was chosen.
3. **Privilege Creep**: Unvetted tools requesting excessive capabilities bypass runtime security.

By assimilating patterns from `gbesse/jev-agent-draft`, DNK OS implements **Deterministic Decision Drafts** (`core/orchestrator/decision_draft.py`):
- **Zero-Trust Hard Gates**: Fail-closed filtering prior to any scoring.
- **5-Dimensional Weighted Scoring**: Calibrated across task fit, least privilege, evidence, maintenance, and portability.
- **Abstention Protocol**: Automatic suspension when margin between top candidates is `< 5.0%` or top score is `< 70.0`.
- **Immutable Cryptographic Receipts (`jvr_<sha256[:20]>`)**: Canonical SHA-256 signed receipts enabling machine-verifiable post-audit.

---

## 🛡️ 2. Zero-Trust Hard Gates (Step 1)
Every candidate must pass 4 hard gates before entering the scoring matrix. If any gate fails, the candidate is disqualified with an explicit reason:

1. **Permission Ceiling Gate (`max_allowed_permission`)**:
   - Compares candidate's `permission_level` against the task ceiling:
     `read_only` (0) < `scoped_write` (1) < `full_system` (2).
   - If candidate permission level > allowed ceiling -> **DISQUALIFIED**.
2. **Maintenance Horizon Gate (`max_maintenance_days`)**:
   - Rejects unmaintained repositories or dependencies older than the allowed SLA (e.g. 365 days).
3. **Evidence Requirement Gate (`require_evidence`)**:
   - When active, candidates without verifiable evidence (benchmarks, test suites, or AST audits) are **DISQUALIFIED**.
4. **Rating Integrity Gate**:
   - Every evaluated dimension score must be a valid float between `0.0` and `100.0`.

---

## 📊 3. 5D Scoring Matrix & Dimension Weights (Step 2)
Weighted scoring normalizes total points to a 0–100 scale:

$$\text{Final Score} = \left( \frac{\sum (w_i \cdot s_i)}{\sum w_i \times 100} \right) \times 100$$

Standard Dimension Suites in DNK OS:
- **`SOTA_ARCH_DIMENSIONS`** (Repository Tournaments):
  - `task_fit` (Weight 5)
  - `least_privilege` (Weight 5)
  - `evidence_quality` (Weight 4)
  - `maintenance_health` (Weight 3)
  - `portability` (Weight 2)
- **`AGENT_TOOL_DIMENSIONS`** (Dynamic Tool Selection):
  - `task_alignment` (5), `security_least_privilege` (5), `execution_speed` (4), `schema_simplicity` (3), `context_cost` (3)
- **`SWARM_WORKER_DIMENSIONS`** (Subagent Routing):
  - `domain_specialization` (5), `token_efficiency` (4), `tool_scope_fit` (4), `past_task_success` (4)

---

## 🛑 4. The Abstention Protocol (Step 3)
An agent must refuse to guess when choices are ambiguous or subpar.
- **Tie-Breaker Boundary**:
  $$\text{Margin} = \text{Score}_1 - \text{Score}_2$$
  If $\text{Margin} < 5.0\%$, the verdict is `status: "abstained"` with reason:
  `"Top candidates within 5.0% margin (Margin: X.XX%). Autonomous choice withheld to prevent arbitrary hallucination."`
- **Low-Quality Boundary**:
  If $\text{Score}_1 < 70.0$, the verdict is `status: "abstained"` with reason:
  `"Winning score X.XX is below minimum acceptable threshold (70.0)."`

When an abstention triggers, the decision escalates to HITL (Human-In-The-Loop) or triggers a secondary adversarial evaluation.

---

## 🔏 5. Cryptographic Receipt Specification (`jvr_<sha256[:20]>`)
A decision receipt is a canonical JSON document complying with schema `https://jev.dev/schemas/decision-receipt/v1`:

```json
{
  "$schema": "https://jev.dev/schemas/decision-receipt/v1",
  "receipt_id": "jvr_0dc5a8cd49753128a831",
  "timestamp": "2026-10-12T14:00:00Z",
  "subject": {
    "task_id": "TASK-001",
    "decision_context": "Select SOTA repo for headless search",
    "agent": "gerych_prime"
  },
  "policy": {
    "name": "dnk-sota-tournament-v1",
    "hard_gates": { "max_allowed_permission": "scoped_write", "max_maintenance_days": 365 },
    "weights": { "task_fit": 5, "least_privilege": 5, "evidence_quality": 4, "maintenance_health": 3, "portability": 2 },
    "abstention_thresholds": { "min_margin_percent": 5.0, "min_winning_score": 70.0 }
  },
  "ranking": [
    { "candidate_id": "cand_a", "score": 92.5, "passed_gates": true },
    { "candidate_id": "cand_b", "score": 78.0, "passed_gates": true }
  ],
  "verdict": {
    "status": "decided",
    "selected_id": "cand_a",
    "margin_percent": 14.5,
    "abstention_reason": null
  }
}
```

### Deterministic Canonicalization:
1. Serialize JSON recursively with sorted keys and no whitespace separators: `json.dumps(obj, sort_keys=True, separators=(',', ':'))`.
2. Compute `hashlib.sha256(canonical_bytes).hexdigest()[:20]`.
3. Prefix digest with `jvr_` to mint `receipt_id`.
4. Verification (`verify_decision_receipt`) strips `receipt_id`, canonicalizes the payload, recomputes the SHA-256 hash, and verifies equality in constant time.

---

## 🔄 6. Runtime Integration in DNK OS
1. **Cross-Repo Tournaments (`core/orchestrator/cross_repo_synthesizer.py`)**:
   Automatically runs `evaluate_candidates_deterministic()` on candidate clusters and attaches the generated receipt to `TournamentResult.decision_receipt`.
2. **SSOT Decision Registry (`docs/architecture/DECISION_REGISTRY_ADHD.md`)**:
   Whenever a major architectural decision is sealed, record it with:
   ```python
   from core.orchestrator.decision_draft import record_to_decision_registry
   record_to_decision_registry(receipt, registry_path="./docs/architecture/DECISION_REGISTRY_ADHD.md")
   ```
