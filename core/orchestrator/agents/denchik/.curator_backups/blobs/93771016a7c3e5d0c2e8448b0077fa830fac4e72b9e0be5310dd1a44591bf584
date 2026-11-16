<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/architecture-invariants-and-blast-radius/references/clean_room_repo_reset_and_agent_interconnection_protocol.md"
# purpose: "Protocol for Clean-Room Repository Reset, Orphan Branch Scaffolding & Agent Interconnection Contracts."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

# Clean-Room Repository Reset & Agent Interconnection Protocol

Use when resetting a polluted, legacy, or historical repository to a pristine clean-room state while establishing standardized multi-agent governance contracts and inter-repo communication topologies.

---

## 🎯 1. Discovery & Safety Gate
Before any destructive wipe or remote branch reset:
1. **Remote Introspection**:
   - Check remote branches: `gh api repos/:owner/:repo/branches`
   - Check tags: `gh api repos/:owner/:repo/tags`
   - Check active PRs: `gh pr list --repo :owner/:repo --state all`
   - Confirm target repo identity via `git remote -v`.
2. **Explicit Founder Confirmation**:
   - Destructive wipes and force-pushes require explicit human consent. Never perform destructive git actions autonomously without unambiguous user confirmation ("підтверджую").

---

## 🧹 2. Purge & Orphan Branch Initialization
1. **Purge Tracked Files**:
   ```bash
   git rm -rf .
   ```
2. **Remove Host & OS Noise**:
   ```bash
   rm -f .DS_Store
   ```
3. **Initialize Clean Orphan Branch**:
   ```bash
   git checkout --orphan clean_main
   ```
   *Rationale*: Eliminates ancestral commit graphs, bloated binary packfiles, and accidental leaks from previous legacy snapshots.

---

## 🏗️ 3. Sovereign Agent Contract Suite Scaffolding
Every clean-room repository in the DNK agent ecosystem MUST scaffold 5 canonical governance artifacts:

1. **`README.md` (Ecosystem Overview & Topology)**:
   - Contains Machine-Readable Header (MRH).
   - Explains the repository's role in the multi-repo ecosystem (`DNK_HUB`, `DNK-OS`, `DNK-Shopify-AI-Builder`, `Claude_Code_DNK`, `DNK_Researcher`).
   - Quickstart commands adhering strictly to `uv` and `pnpm`.

2. **`AGENTS.md` (Autonomous Swarm Governance)**:
   - Declares agent roles (Antigravity as Architect/Mentor, Denchik as Master Builder).
   - Zero-Waste High-Velocity Protocol (MASE slices ≤ 25 tool calls, context diet < 20k tokens).
   - Senior Dev Solution Ladder (DEC-057) & Package Manager SSOT (`uv`, `pnpm`, relative paths `./`).
   - Epistemic armor, banned sycophancy, and deterministic machine verification (`exit code 0`).

3. **`CLAUDE.md` (IDE / Claude Code Workspace Rules)**:
   - Target build, test, and lint commands (`uv run pytest`, `uv run ruff check`).
   - Python 3.12+ type annotations, async-first I/O, Pydantic v2 schemas.

4. **`docs/architecture/INTERCONNECTION_ARCHITECTURE.md` (Inter-Repo Topology & IPC)**:
   - Physical layout across `MY_LIFE_WORK/`.
   - Data flow patterns: Knowledge SSOT (`DNK_HUB`) -> Coordination (`DNK-OS`) -> Domain Workhorses.
   - SCONES memory sharing protocol (`scones_memory.db`).

5. **`core/contracts.py` & `tests/test_contracts.py` (Typed Machine IPC)**:
   - Typed Pydantic v2 models: `KernelTaskRequest`, `KernelTriageReceipt`, `KernelDecisionReceipt`, `KernelCompletionReceipt`.
   - Unit tests covering positive paths, invalid inputs, and validation gates with real assertions.
   - Configure `pyproject.toml` with `pythonpath = ["."]`.

---

## 🧪 4. Deterministic TDD Verification Gate
Run test suite before staging or committing:
```bash
uv run pytest
rm -rf .pytest_cache
```
Mandatory criteria:
- 100% tests pass (`exit code 0`).
- Zero fake, tautological, or empty assertions.
- Working tree clean of temporary test caches.

---

## 🚀 5. Commit & Force-Push Safety Barrier
1. **Commit Root State**:
   ```bash
   git add -A
   git commit -m "feat(init): clean DNK-OS architecture & agent interconnection contracts"
   ```
2. **Rebind Branch Pointer**:
   ```bash
   git branch -D main && git branch -m main
   ```
3. **Handle Force-Push Intercepts Gracefully**:
   - Executing `git push -f origin main` will typically trigger agent runtime destructive command interceptors (Smart Approval / Safety Gate timeout).
   - **Crucial Rule**: When a force-push is blocked by the runtime safety guard:
     - DO NOT retry the command in an automated loop.
     - DO NOT attempt alternative destructive workarounds (e.g. `git push --delete`, gh api deletion).
     - STOP immediately, report the verified local clean commit SHA, and request explicit single-word confirmation ("так" or "пуш") from the user.
