# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/jev_agent_draft_and_decision_receipt_patterns.md"
# purpose: "Assimilated patterns from gbesse/jev-agent-draft: Least Privilege Agent/MCP drafting, Hard Gates, Abstention Protocol, and Cryptographic Decision Receipts."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ Jev Agent Draft & Decision Receipt SOTA Patterns (gbesse/jev-agent-draft)

## 📌 Executive Overview
`gbesse/jev-agent-draft` introduces a deterministic, zero-dependency mechanism to select agents, tools, and MCP servers under the **Principle of Least Privilege**, backed by a cryptographic **Decision Receipt** (`https://jev.dev/schemas/decision-receipt/v1`).

Key innovation: **The Abstention Protocol** — instead of guessing between mediocre or closely tied options, the engine explicitly refuses to select (`status: "abstained"`), detailing the exact evidence deficit needed to break the tie.

---

## ⚙️ Core Architecture & Pipeline

```
[Candidate Shortlist (2..32)]
            │
            ▼
   [Stage 1: Hard Gates] ─────────(Fails any gate)────────► Disqualified
            │
            ▼ (Passes all gates)
   [Stage 2: 5-Dimension Weighted Scoring] ──► Score: 0..100
            │
            ▼
   [Stage 3: Confidence & Margin Gate]
            │
            ├─► Margin < 5% OR Score < 70 ──► status: "abstained" (requires evidence)
            │
            ▼ (Clear Leader)
   [Stage 4: Cryptographic Decision Receipt] ──► status: "selected" + jvr_<sha256>
```

---

## 🚪 Stage 1: 4 Deterministic Hard Gates

Before any weighted scoring occurs, candidates must pass all 4 non-negotiable gates:
1. **Permission Ceiling (`allowedPermissions`):**
   - Any candidate requesting permissions outside the declared policy is immediately disqualified.
   - Example: An agent tasked with `code_audit` requesting `repository:write` fails immediately.
2. **Maintenance Age (`maxMaintenanceAgeDays`):**
   - Repositories unmaintained beyond the threshold (e.g. 180 days) are rejected.
3. **Evidence Presence (`evidence`):**
   - Every rating must link to verifiable benchmark URLs, test suites, or live metrics. No uncited subjective claims.
4. **Rating Integrity:**
   - All 5 dimensions must carry valid values in the range `0..100`.

---

## 📊 Stage 2: 5-Dimension Weighted Scoring

Weights reflect operational risk and utility:
$$\text{Score} = \frac{5 \cdot \text{task\_fit} + 5 \cdot \text{permission\_minimality} + 4 \cdot \text{evidence\_quality} + 3 \cdot \text{maintenance} + 2 \cdot \text{portability}}{19}$$

- **Task Fit (Weight 5):** Direct alignment with task requirements.
- **Permission Minimality (Weight 5):** Least privilege; penalty for unnecessary scopes.
- **Evidence Quality (Weight 4):** Rigor of external proof and reproducible benchmarks.
- **Maintenance (Weight 3):** Release cadence, commit frequency, issue resolution velocity.
- **Portability (Weight 2):** Ease of migration across runtimes (Node, Python, CLI, Docker).

---

## 🛑 Stage 3: Margin & Abstention Protocol

To prevent hallucinated pseudo-decisions between nearly identical candidates:
```typescript
const MIN_CONFIDENCE = 70;
const MIN_MARGIN = 5.0; // Leader must lead by >= 5.0 points

if (leader.score < MIN_CONFIDENCE) {
  return { status: "abstained", reason: "low_confidence", leader, runner_up };
}
if ((leader.score - runnerUp.score) < MIN_MARGIN) {
  return { 
    status: "abstained", 
    reason: "tie_margin_deficit", 
    margin: leader.score - runnerUp.score,
    required_evidence: ["targeted_benchmark", "security_audit"] 
  };
}
```

---

## 🔏 Stage 4: Cryptographic Decision Receipt (`jvr_*`)

Decisions are rendered tamper-evident via canonical JSON serialization and SHA-256 digest:
```python
import hashlib, json

def canonicalize(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))

payload = {
    "policy": policy_dict,
    "selected": leader_dict,
    "evaluated_candidates": candidates_list,
    "timestamp": iso_timestamp
}

digest = hashlib.sha256(canonicalize(payload).encode('utf-8')).hexdigest()
receipt_id = f"jvr_{digest[:20]}"
```

This receipt ID is recorded directly into `docs/architecture/DECISION_REGISTRY_ADHD.md` to permanently seal architectural choices against discussion amnesia.
