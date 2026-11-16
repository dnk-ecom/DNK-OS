# --- DNK-MRH-HEADER ---
# mrh_id: "sota-repository-assimilation/references/sota_code_review_triad_unified_e2e_pipeline.md"
# purpose: "Architecture, contracts, and execution invariants for the unified SOTA Code Review Triad (PR-Agent + Alibaba OCR + pr-af)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# SOTA Code Review Triad: Unified E2E Pipeline (PR-Agent + Alibaba OCR + Agent-Field pr-af)

## 📌 Architecture Overview

The DNK OS SOTA Review Triad unifies three world-class autonomous review systems into an end-to-end, deterministic, zero-hallucination pipeline:

```
                          ┌────────────────────────┐
                          │   Unified Git Diff     │
                          └───────────┬────────────┘
                                      │
            ┌─────────────────────────┴────────────────────────┐
            ▼                                                  ▼
┌───────────────────────┐                          ┌────────────────────────┐
│ 1. The-PR-Agent       │                          │ 2. Agent-Field pr-af   │
│ - Hunk-only extraction│                          │ - BlastRadiusEngine    │
│ - Token budgeting     │                          │ - AST Impact Graph     │
│ - File priority weight│                          │ - Risk Multiplier      │
└───────────┬───────────┘                          └───────────┬────────────┘
            │                                                  │
            └─────────────────────────┬────────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ 3. Alibaba Open-Code-Rev  │
                        │ - Rule sniffer (Python/TS)│
                        │ - Token-budgeted packet   │
                        │ - Algorithmic relocation  │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ 4. pr-af Adversary Gate   │
                        │ - Refutes nitpicks/style  │
                        │ - Validates guard clauses │
                        │ - Confirms verified bugs  │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ 5. Audit State Machine    │
                        │ - Multi-commit lifecycle  │
                        │ - Deterministic Score 0-100│
                        │ - Pass/Block Gate Verdict │
                        └───────────────────────────┘
```

---

## ⚙️ Core Components & Invariants

### 1. `core/orchestrator/git_diff_engine.py` (The-PR-Agent Pillar 1)
- **Dual-mode Diff Parser**: Handles standard `diff --git a/... b/...` headers as well as traditional unified diffs starting directly with `--- a/...` and `+++ b/...`.
- **Hunk-Only Extraction**: Strips unmutated boilerplate lines, isolating modified hunks with minimal surrounding context.
- **Priority Weighting**: Ranks files by critical extensions (`.py`, `.ts`, `.rs` > `.json`, `.md`), ensuring token budgets prioritize security-critical business logic.

### 2. `core/orchestrator/blast_radius.py` (pr-af Pillar 2)
- **AST / Regex Dependency Graph**: Scans Python AST imports and TypeScript/JavaScript ES6 imports to build a directed graph of affected modules.
- **Deterministic Risk Scoring**:
  - Classifies risk into `low` (1.0x penalty), `medium` (1.2x penalty), `high` (1.5x penalty), `critical` (2.0x penalty).
  - Flags blast radius if critical modules (e.g. `core/auth`, `core/crypto`, `core/database`) depend on the mutated files.

### 3. `core/orchestrator/ocr_delegation.py` (Alibaba OCR Pillar 3)
- **Context-Enriched Packet (`OCRDelegationPacket`)**: Pre-computes file contents, diff hunks, blast radius risk level, and critical dependents before dispatching to review agents.
- **Algorithmic Comment Relocation**: Matches multi-line code windows to compute line drift across subsequent commits, preventing stale GitHub review comments.

### 4. `core/orchestrator/adversary_challenge.py` (pr-af Devil's Advocate Pillar 4)
- **Polymorphic Finding Duck Typing**: Handles both `ReviewFinding` dataclasses and external/agent finding objects via `getattr` (`line_number` or `line_start`, `severity` string or enum).
- **Automated Refutation**:
  - Refutes style and formatting nitpicks unless explicitly requested.
  - Inspects upstream code slices for guard clauses (`if var is None: raise ...` or `try ... except ...`), automatically dismissing false-positive "unhandled exception" warnings.
  - Confirms legitimate security, race condition, or logic defects.

### 5. `core/orchestrator/audit_state_machine.py` (Deterministic Reconciler Pillar 5)
- **Mathematical Health Scoring**:
  $$\text{Score} = \max\left(0, 100 - \sum (\text{severity\_penalty} \times \text{risk\_multiplier})\right)$$
- **Refuted Findings Telemetry**: Refuted findings are recorded in `challenged_findings` metadata for transparent audit trails, but their penalty is strictly 0, avoiding score deflation.
- **Fail-Closed Blocking Gate**: Any unresolved `critical` or `high` finding blocks commit promotion (`AuditStatus.BLOCKED`).

---

## 🚀 Usage Recipes

### 1. Single-Function Triad Review
```python
from core.orchestrator.pr_agent_adapter import review_pull_request_diff

result = review_pull_request_diff(
    diff_content=raw_unified_diff,
    commit_hash="abc1234",
    filter_adversary=True,
    calculate_blast=True,
    repo_root="."
)

print(f"Health Score: {result['health_score']}/100")
print(f"Gate Verdict: {result['gate_verdict']}")
print(f"Blast Risk: {result['blast_report']['risk_level']}")
print(f"Adversary Refuted: {result['adversary_stats']['refuted_count']}")
```

### 2. Multi-Agent Delegation with Context-Enriched Packet
```python
from core.orchestrator.ocr_delegation import OCRDelegationRouter
from core.orchestrator.audit_state_machine import AuditStateMachine
from core.orchestrator.adversary_challenge import AdversaryGate
from core.orchestrator.blast_radius import BlastRadiusEngine

router = OCRDelegationRouter(
    state_machine=AuditStateMachine(),
    adversary_gate=AdversaryGate(),
    blast_engine=BlastRadiusEngine()
)

packet = router.create_context_enriched_packet(
    commit_hash="c0ffee1",
    files_changed=["core/auth.py"],
    file_contents={"core/auth.py": "def login(): pass"},
    diff_hunks={"core/auth.py": "@@ -1 +1 @@\n+def login(): pass"}
)

# Ingest agent findings through Adversary Gate & State Machine
reconciliation = router.ingest_findings(packet, agent_findings, filter_adversary=True)
```

---

## 🧪 Verification Commands

To verify the complete Triad pipeline and backward compatibility:
```bash
./.venv/bin/pytest tests/core/test_review_triad_e2e.py -v
./.venv/bin/pytest tests/core/test_pr_agent_assimilation.py tests/core/test_open_code_review_assimilation.py tests/core/test_pr_af_assimilation.py -v
```
