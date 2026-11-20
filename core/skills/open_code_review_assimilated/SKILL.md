---
name: open_code_review_assimilated
description: "Assimilated SOTA patterns from alibaba/open-code-review: deterministic rule sniffing, precision-over-recall review, algorithmic comment relocation, and delegation packets."
version: "1.0.0"
category: "research"
assimilated_at: "2026-09-10"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "Apache-2.0"
target_worker: "gerych_auditor"
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/open_code_review_assimilated/SKILL.md"
purpose: "Assimilated Alibaba Open-Code-Review Architecture, Deterministic Sniffer, Comment Relocation, and Delegation Engine"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-10"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🌐 ALIBABA OPEN-CODE-REVIEW Assimilation Index & Recipes

Meta-index and practical implementation patterns assimilated from **[alibaba/open-code-review](https://github.com/alibaba/open-code-review)**.

## 📌 Repository Intel & Legal Boundary
- **Repository**: `alibaba/open-code-review`
- **License**: `Apache-2.0` (Commercial safe)
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `gerych_auditor` / `dnk_dev_fullstack`
- **Obsidian Reference**: `docs/notes/144_open_code_review_sota_assimilation_audit.md`
- **Reference Doc**: `core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/open_code_review_deterministic_hybrid_and_relocation_patterns.md`

## 📁 Key Assimilated Architectural Pillars

1. **Deterministic Rule Sniffer & File Filtering**:
   - Zero-waste bypass of lockfiles, vendor bundles, generated minified scripts, and binary assets.
   - Dynamic regex and extension-based matching of file-level rules (`.py`, `.ts`, `.tsx`, `.go`, `.sql`, `.github/workflows`).
2. **Golden Review Invariant (Precision Over Recall)**:
   - *"Only raise an issue when you are confident it is a real defect, and stay silent when the surrounding context is unclear — a false alarm costs more reviewer trust than a missed minor issue."*
   - Strict dichotomy: `BLOCKING` (Security vulnerabilities, resource leaks, concurrent data races, fatal logic errors) vs `NON_BLOCKING` (idiomatic style, performance micro-optimizations).
3. **Algorithmic Comment Relocation & Boundary Gate**:
   - Fixes position drift between suggested lines from LLM diff chunks and real file lines.
   - Exact window search -> file-wide normalized search -> fuzzy token similarity. Eliminates phantom comments.
4. **Fingerprinted State Machine & GitHub Suggestions**:
   - Fingerprint deduplication across multi-commit reviews via `AuditStateMachine`.
   - Native 1-click GitHub suggestions (`format_github_suggestion`).
5. **Self-Contained Delegation Engine (`OCRDelegationEngine`)**:
   - Packages diff chunks, active rule IDs, and output schema into token-budgeted `OCRDelegationPacket` for autonomous workers (`dnk_swarm_parallel`, `gerych_auditor`, `claude-code`).

## 🧪 Quick Recipes

### Recipe 1: Dynamic Rule Sniffing for Code Review
```python
from core.orchestrator.code_review_rules import CodeReviewRuleSniffer

sniffer = CodeReviewRuleSniffer()
rules = sniffer.sniff_rules_for_files(["apps/api/routers/users.py", "apps/web/src/App.tsx"])
prompt_guidelines = sniffer.generate_prompt_guidelines(rules)
# -> Returns high-signal markdown guidelines with active domain rule IDs
```

### Recipe 2: Algorithmic Comment Relocation (Zero Phantom Comments)
```python
from core.orchestrator.git_diff_engine import relocate_comment

file_code = """
def process_data(items):
    # Some new comment added here
    result = []
    for item in items:
        result.append(item)
    return result
"""

# Reviewer suggested comment at line 3 for "result = []", but line shifted
res = relocate_comment(
    file_content=file_code,
    existing_code="result = []",
    suggested_line=2,
    tolerance_window=10,
)
if res.matched:
    print(f"Comment successfully relocated to line {res.relocated_line}")
```

### Recipe 3: Generating and Ingesting an Autonomous OCR Delegation Packet
```python
from core.orchestrator.ocr_delegation import OCRDelegationEngine

engine = OCRDelegationEngine()

# 1. Prepare packet from git diff
packet = engine.prepare_packet(
    raw_diff=git_diff_text,
    commit_hash="HEAD",
    max_tokens_per_chunk=3500,
)
packet_prompt = packet.to_prompt()

# 2. Ingest subagent response with automatic relocation and gate check
result = engine.ingest_findings(
    packet=packet,
    raw_findings=subagent_json_output,
    file_contents={"core/main.py": file_text},
)

print(f"Gate Passed: {result.passed_gate} | Blocking: {result.blocking_count}")
```

## ⚠️ Pitfalls & Invariants
1. **[PRECISION_OVER_RECALL]**: Do not flood PRs with stylistic nitpicks. False alarms degrade reviewer trust.
2. **[PHANTOM_COMMENTS]**: Always anchor findings to existing code snippets via `relocate_comment` before posting.
3. **[ZERO_ABSOLUTE_PATHS]**: All file paths in findings and packets must be relative to workspace root (`./`).
4. **[BLOCKING_VS_NON_BLOCKING]**: The master gate blocks only on `BLOCKING` severity findings; `NON_BLOCKING` findings remain advisory.
