# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/architecture-invariants-and-blast-radius/references/read_only_mentor_and_working_tree_debt_triage.md"
# purpose: "Canonical protocol for Read-Only Mentor Audits, Working Tree Debt Triage, and Epistemic Architecture Critique in DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-01"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Read-Only Mentor Audits & Working Tree Debt Triage Protocol

## 1. Trigger Conditions
- User explicitly requests mentor mode ("виступай як ментор", "проаналізуй архітектуру").
- User enforces strict zero-write barrier ("нічого не змінюй ні строчки коду", "read-only audit").
- A complex monorepo has accumulated substantial uncommitted changes (>50 files) across multiple domains.

## 2. Invariants & Rules of Engagement

### Invariant 1: Zero Code Mutation & Zero Noise
- Strictly forbid calling `write_file`, `patch`, or running mutate/compile commands that generate cache files (`__pycache__`, `.pytest_cache`, `.next`).
- Do NOT run heavy precommit test suites (`bash scripts/verify_all.sh`) during read-only audits.
- Collect all structural facts via non-mutating shell queries or high-speed Python inspection scripts in a single turn.

### Invariant 2: 1-Turn Topographical Telemetry
Execute a unified inspection script to extract:
1. **Branch & Remote Divergence**: `git branch --show-current`, ahead/behind commit counts.
2. **Working Tree Breakdown**: Distribution of modified/untracked files grouped by top-level root.
3. **Canonical 8-Root Directory Invariant**: Verify presence of only `apps/`, `core/`, `docs/`, `infra/`, `packages/`, `scripts/`, `services/`, `tests/`.
4. **Recent Git Trajectory**: Last 5–10 commit messages to identify active feature streams.
5. **Active Focus Alignment**: Inspect canonical task journals (e.g. `docs/notes/MY TASKS/.../!!! TASK NOW.md`).

### Invariant 3: 5-Vector Developer Critique Framework
Every architectural audit must evaluate the system across:
1. **Boundary Conditions & Worker Isolation**: Swarm concurrency, thread safety, process isolation (e.g. Git Worktrees for concurrent subagents).
2. **Context Diet & Attention Entropy**: Baseline standing overhead (System Prompt + MCP schemas), Level-of-Detail (LOD), JIT tool loading (Skill Retriever).
3. **Maintainability & Technical Debt**: Accumulation of uncommitted files, deprecated shims, orphaned architectural journals vs running code.
4. **Security Attack Vectors & Split-Route Gates**: Protection of mutating endpoints (`POST`, `PUT`, `DELETE`), token hygiene, zero hardcoded credentials.
5. **Computational Efficiency & Dual SSOT Synchronization**: Single Source of Truth for shared state (e.g. Canvas UI vs FastAPI backend, unidirectional data flow, OCC merge).

### Invariant 4: Mandatory Dissent & 3 Flaws Rule
Always surface the 3 most dangerous failure modes:
1. **Working Tree Freeze**: Inability to safely branch, stash, or rebase due to excessive uncommitted files.
2. **Attention Entropy**: Context bloat causing LLMs to drop constraints and hallucinate.
3. **Feature Sprawl / Premature Optimization**: Multiple parallel unverified initiatives diluting focus from MVP core workhorses.

## 3. Action-First Stabilization Roadmap
Present concrete, non-disruptive remediation steps:
1. **Logical Commit Partitioning**: Group untracked/modified files into focused atomic commits without touching code (Docs/Vault sync, Skills sync, UI/Canvas checkpoint).
2. **Backlog Pruning & Priority Lock**: Re-anchor active work to the top 1–3 priorities in `TASK NOW.md`.
3. **Phase-2 Transition**: Only enter Phase 2 (Code Synthesis) after establishing clean git hygiene and explicit task whitelists.
