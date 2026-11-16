# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/skills_assimilated/references/diagnosing_bugs.md"
# purpose: "Reference guide for deterministic 5-phase bug diagnosis in DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🐞 Deterministic Bug Diagnosis Loop

Assimilated from `mattpocock/skills/engineering/diagnosing-bugs`.

## 0. Redaction & Safety
- **Always redact secrets**: API keys, tokens, auth headers must be replaced with `<REDACTED>`.
- Do not run state-mutating commands on production data during diagnosis.

## 1. Phase 1: Build the Feedback Loop (The "Red" State)
- **Do not touch the implementation yet.**
- First, write a standalone, reproducible test script or pytest case that reproduces the failure deterministically.
- Run it and observe the failure (Red). If you cannot reproduce the bug reliably, you cannot know if you have fixed it.

## 2. Phase 2: Minimise the Reproduction
- Strip all irrelevant context, mock data, and auxiliary calls.
- Reduce the input payload and steps to the bare minimum that still triggers the error.
- Smaller repros reveal the underlying invariant violation instantly.

## 3. Phase 3: Hypothesise & Instrument
- Formulate **one concrete, falsifiable hypothesis** at a time:
  - *"Function X receives None because caller Y didn't validate field Z."*
- Instrument with deterministic assertions or targeted debug prints.
- Run the feedback loop. Check if the evidence confirms or refutes the hypothesis.
- If refuted, revert the instrumentation and formulate the next hypothesis. **Never guess in a loop.**

## 4. Phase 4: Apply Root-Cause Fix
- Fix the problem at its architectural root, not by adding a band-aid `if x is None: return` at the crash site.
- Ensure the fix preserves existing invariants and does not break sibling flows.

## 5. Phase 5: Verify & Lock Regression Test
- Run the reproduction test created in Phase 1 -> confirm it is now **Green**.
- Run the full suite (`bash scripts/verify_all.sh` or targeted pytest).
- Keep the test in the codebase as a permanent regression guard.
