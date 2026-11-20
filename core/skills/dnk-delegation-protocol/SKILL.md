---
title: "Canonical PSOD Delegation Protocol"
name: "dnk-delegation-protocol"
description: "Canonical SOTA 2026 PSOD (Problem, Substrate, Oracle, Deliverable) Delegation Protocol for 100% first-pass execution rate across Antigravity, Gerych, and Denchik subagents."
mrh_id: "core/skills/dnk-delegation-protocol/SKILL.md"
status: Active
version: "1.0.0"
updated: 2026-11-18
category: "orchestration"
assimilated_at: "2026-11-16"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/skills/dnk-delegation-protocol/SKILL.md"
> purpose: "Canonical SOTA 2026 PSOD (Problem, Substrate, Oracle, Deliverable) Delegation Protocol for 100% first-pass execution rate across Antigravity, Gerych, and Denchik subagents."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📋 Canonical PSOD Delegation Protocol (100% First-Pass Yield)

> **Core Invariant**: *"A task without a deterministic Verification Oracle is a request for hallucination. No raw execution log = NOT PASS."*

---

## 🏛️ 1. The PSOD Contract (Problem, Substrate, Oracle, Deliverable)

When delegating any task to a subagent, worker swarm, or Gerych CLI, the prompt or dispatch payload MUST strictly follow the 4-part PSOD structure:

```yaml
# 📋 PSOD DELEGATION SPECIFICATION
P (Problem & Scope):
  - Objective: Clear statement of the functional requirement or defect.
  - Target Whitelist: Explicit list of relative file paths allowed for modification.
    (Any modification outside this whitelist triggers WHITELIST_VIOLATION).

S (Substrate & Constraints):
  - Runtime: Use ~/.dnk_runtime/venv (Python 3.14/3.12 via uv).
  - Package Management: Use pnpm for node packages (APFS Hardlink Store).
  - Code Standard: Zero hardcoded absolute paths, Pydantic v2 typing, GEMINI.md hygiene.

O (Verification Oracle):
  - Deterministic Command: The exact terminal command that proves task completion.
    Example: `uv run pytest tests/core/test_cart.py`
  - Expected Exit Code: 0 (Strict).
  - Evidence Rule: Worker must capture and return raw terminal stdout/stderr.

D (Deliverable Format):
  - Compact summary of modified lines (git diff --stat).
  - Raw evidence log showing Oracle Command execution with exit code 0.
```

---

## 🛠️ 2. Subagent & Swarm Tooling Matrix

Choose the execution channel based on task nature:

| Workload Type | Execution Primitive | Isolation Strategy | Verification Gate |
| :--- | :--- | :--- | :--- |
| **Research / Exploration** | `invoke_subagent(TypeName="research")` | Read-only sandbox (zero mutation risk) | Markdown synthesis with file links |
| **Feature / Bugfix Code** | `swarm(action="add", workspace="share")` | APFS Copy-on-Write git worktree | Local test suite + git diff audit |
| **Long Autonomous Job** | `gerych -w -q "..."` | Hermes background worktree (`-w`) | Exit code 0 + `learn` skill creation |
| **Multi-Module Staged Work** | `run_workflow(Script=...)` | Python pipeline (parallel fanout + fanin) | `FanInAggregator` 4-Gate check |

---

## 🚫 3. Anti-Habits Blocked by this Protocol

1. **Phantom Done**: Claiming completion without executing the test.  
   *Interception*: `DelegationVerifier` inspects session command history; rejects completion if `oracle_command` is missing.
2. **Drive-By Refactor**: Editing files outside the designated scope.  
   *Interception*: `target_whitelist` filters `git status --porcelain`; rejects with `WHITELIST_VIOLATION`.
3. **Green-Washing**: Masking errors via `|| true` or deleting broken tests.  
   *Interception*: `hermes_pre_tool_hook.py` blocks test tampering and forced error suppression.

---

## 💻 4. Python API Usage

```python
from core.orchestrator.delegation_packet import (
    DelegationPacket,
    DelegationVerifier,
    DelegationStatus,
)

# 1. Create packet
packet = DelegationPacket(
    packet_id="DEL-20261116-01",
    title="Refactor Cart Mutation Queue",
    problem="Ensure CartMutationQueue handles concurrent checkout requests safely.",
    target_whitelist=["services/dnk_shopify/runtime/cart_queue.py"],
    oracle_command="uv run pytest services/dnk_shopify/tests/test_cart_queue.py",
    expected_exit_code=0
)

# 2. Render prompt brief for subagent
brief = packet.render_prompt_brief()

# 3. Verify execution after agent turn
verdict = DelegationVerifier.verify(
    packet=packet,
    executed_commands=["uv run pytest services/dnk_shopify/tests/test_cart_queue.py"],
    exit_codes=[0],
    modified_files=["services/dnk_shopify/runtime/cart_queue.py"]
)

assert verdict.passed is True
```
