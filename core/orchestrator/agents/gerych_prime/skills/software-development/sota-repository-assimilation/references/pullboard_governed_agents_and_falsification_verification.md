---
title: "Pullboard Governed Agents And Falsification Verification"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/pullboard_governed_agents_and_falsification_verification.md"
> purpose: "Document: Pullboard Governed Agents And Falsification Verification"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/pullboard_governed_agents_and_falsification_verification.md"
> purpose: "Document: Pullboard Governed Agents And Falsification Verification"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# Pullboard: Governed Multi-Agent Development & Falsification Verification Patterns

Assimilated patterns and architectural analysis from `pullboard-dev/pullboard` (MIT, author Corey Olson): local-first autonomous development orchestrator enforcing spec-driven contracts, git worktree isolation, and adversarial verification before merge.

---

## 1. Core Architecture & Primitives

### 1.1 Zero-External-Dependency Runtime
Pullboard runs on Node.js >= 22.13 with 0 runtime npm packages by leveraging modern Node built-ins:
- `node:sqlite`: In-process relational storage for state, queues, lanes, and shouts.
- `node:fs`, `node:path`, `node:crypto`: Local filesystem mutations, SHA-256 evidence hashing, and git hook templates.
- `node:child_process`: Git CLI and test runner invocation.
- `node:http`: Local UI and Relay pairing server.

### 1.2 Git Common Directory SQLite (`.git/pullboard.sqlite`)
Instead of polluting the working tree with state files, Pullboard anchors its database in `.git/` (specifically `git rev-parse --git-common-dir`).
- **Invariant**: Multiple git worktrees automatically share the exact same SQLite database.
- **Benefit**: Zero git status pollution, zero risk of committing agent orchestration state to repository history, instant cross-worktree atomic transactions.

### 1.3 Coordinator vs. Worker Worktrees
- **Coordinator**: Owns the main working checkout, handles human interaction (Shouts), task decomposition, and merge decisions.
- **Builders**: Work in isolated git worktrees (`pullboard worktree <lane>`). Files modified outside their assigned directory lane are rejected by commit hooks.
- **Verifier**: Separate worktree operating in detached HEAD (`git switch --detach refs/pullboard/items/...`) executing gate validation.

---

## 2. Governance & Gating Contracts

### 2.1 SPEC.md Gated Requirement Rows
Requirements follow a strict single-line machine-parsable format:
```markdown
- G1.2 [approved, must] Same file twice is a no-op. | gate: npm test
- B2.1 [draft, aim] Exponential backoff on rate limits. | gate: pytest tests/test_backoff.py
```
- Status lifecycle: `draft` -> `approved` -> `pending` -> `retired` / `wont`.
- **Power Invariant**: Builder agents may only propose `draft`. Only the human operator (or designated Coordinator) can transition a requirement to `approved`.
- **Gate Invariant**: Only requirements marked `approved` block work item merge.

### 2.2 DOCTRINE.md Engineering House Rules
A flat, numbered invariant file (`C1..C12`, `W1..W4`, `T1..T12`) enforcing non-negotiable coding standards:
- `C1`: Zero external dependencies without explicit sign-off.
- `C9`: Max 1,500 lines per file (triggers automated refactoring/splitting).
- `W1`: Concrete numbers over vague adjectives in commit messages and reports.
- `T11`: Proof must be recorded before completion claims.

### 2.3 Adversarial Double-Check Invariant (Builder != Verifier)
An agent is structurally forbidden from certifying its own code:
1. Builder finishes code and test suite, pushes ref to `refs/pullboard/items/<item-id>`.
2. Verifier checks out exact commit in isolated lane.
3. **Falsification Pass ("Break it and watch it fail")**:
   - Verifier runs gate: verifies green.
   - Verifier intentionally mutates or reverts the implementation slice to verify the gate turns red.
   - Verifier restores commit and verifies green again.
   - This eliminates fake, tautological, or mock-heavy assertions.
4. Verifier issues structured verdict.

### 2.4 Typed Rejection Taxonomy
Failed verification emits standardized machine codes rather than unstructured prose:
- `TEST_FAILURE`: Automated gate command exited with non-zero code.
- `BEHAVIOR_MISMATCH`: Code runs, but violates explicit `SPEC.md` condition.
- `INSUFFICIENT_EVIDENCE`: Missing targeted test or reproduction artifact.
- `STALE_HEAD`: Upstream main moved, rebasing required.
- `OTHER`: Environmental or configuration issue.

---

## 3. Critical Risks & Boundary Conditions (Epistemic Armor)

1. **Experimental Node `node:sqlite` Fragility**:
   Coupling to Node 22.13+ limits portability across environments running LTS Node 20 or custom runtimes.
2. **Worktree Disk Bloat & Git Lock Contention**:
   Spawning multiple concurrent worktrees in monorepos duplicates build caches and virtual environments, causing disk exhaustion and `index.lock` collisions.
3. **Throughput & Token Cost Halving**:
   Requiring an independent second agent and full checkout/falsification cycle for every atomic commit doubles API spend and latency. Must be gated by risk tiers (`light` vs. `strong`).

---

## 4. DNK OS Clean-Room Assimilation Recipes

In DNK OS, we assimilate the governance logic without adopting external Node CLI daemons:

### 4.1 Task Specification Acceptance Criteria
Map `SPEC.md` gating directly into `docs/tasks/TASK-*.md`:
```markdown
### Acceptance Criteria (Gated)
- [G1] [approved, must] Anti-tautology AST check passes with 0 violations | gate: uv run python3 scripts/system/anti_tautology_guard.py --affected
- [G2] [approved, must] Unit regression suite passes | gate: uv run pytest tests/core/test_example.py
```

### 4.2 Super-Builder Protocol Phase 3 Falsification Pass
When acting as Verifier/Auditor (`gerych_auditor` or pre-commit gate):
1. Invert the assertion or remove the fix.
2. Confirm test failure (`exit code != 0`).
3. Restore fix and verify green (`exit code 0`).
4. Log machine receipt in `docs/audit/RECEIPT-*`.

### 4.3 Swarm Ephemeral Coordination
Store multi-agent locks and work queues in `.git/dnk_swarm.db` rather than in tracked repository files, guaranteeing zero working-tree noise.
