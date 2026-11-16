# Uncle Bob's SwarmForge Architecture & Swarm Topology Patterns

<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/unclebob_swarm_forge_and_swarm_topologies.md"
purpose: "Condensed architecture reference and DNK OS adaptation patterns from unclebob/swarm-forge."
status: "Active"
version: "1.0.0"
updated_at: "2026-10-17"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

## 1. Executive Summary & Core Purpose

`unclebob/swarm-forge` (by Robert C. Martin / Uncle Bob) implements an agent swarm orchestrator structured around strict Clean Architecture, Test-Driven Development (TDD), and multi-agent workflow isolation.

Rather than running LLMs in a single shared directory or context window (which leads to race conditions, file collisions, and context bloat), SwarmForge isolates agents in dedicated Git worktrees and coordinates work through a file-based handoff daemon.

## 2. Core Architectural Pillars

### A. Git Worktree Isolation (`.worktrees/<role>`)
- Each swarm role operates in an isolated Git worktree linked to a separate tmux window.
- Agents never touch uncommitted changes from another role.
- State passing occurs strictly via Git commits and metadata manifests.

### B. Daemon-Driven Handoff Transport (`handoffd`)
- Replaces raw tmux / shell injection with a deterministic filesystem queue:
  ```text
  .swarmforge/handoffs/
    outbox/
      tmp/
    sent/
    failed/
    inbox/
      new/
      in_process/
      completed/
  ```
- Priority & Sequence Filename Convention:
  `<priority>_<timestamp>_<sequence>_from_<sender>_to_<recipients>.handoff`
- Structured Git Handoff Manifest:
  ```yaml
  type: git_handoff
  to: <target_role>
  priority: 00
  task: <task_identifier>
  commit: <sender_worktree_head_sha>
  artifacts: [...]
  ```

### C. Engineering Constitution (`constitution.prompt`)
- **TDD First**: Every behavioral change must begin with an executable spec/test.
- **Metric Gates**:
  - **CRAP Score**: Combines cyclomatic complexity and code coverage. High-CRAP methods fail verification.
  - **Mutation Score**: Code changes are mutated (via `mutate4go`, `clj-mutate`, `mutate4java`); if mutated bugs pass existing tests, the suite fails.
  - **DRY Analysis**: Duplication detection gates code review.
- **Single Responsibility & Blast Radius**: Automatic split recommendation if a file exceeds 100 change sites or multiple reasons to change.

## 3. Topology Comparison Across 9 Branches

| Branch | Architecture / Pipeline | Key Mechanics & Workflow |
|---|---|---|
| `main` | Core Engine & Constitution | Shared Babashka (`.bb`) scripts, attention dashboard, base constitutional articles (`engineering`, `workflow`, `handoffs`). |
| `two-pack` | Micro Dev/Refactor Dyad | `coder` -> `cleaner`. Fast turnaround; cleaner uses `back-one` to feed cleaned AST back to coder. |
| `four-pack` | Standard Agile Pipeline | `specifier` -> `coder` -> `refactorer` -> `architect`. Clear Gherkin spec handoff and `back-all` reverse merge. |
| `six-pack` | Industrial Quality Factory | `specifier` -> `coder` -> `cleaner` -> `architect` -> `hardener` -> `QA`. Late stages run in batch mode (`hardener` runs mutation sweeps; `QA` runs full acceptance/UI suites). |
| `adversaries` | Red vs Blue Consensus Loop | `coder` <-> `reviewer`. Iterative adversarial battle until formal review sign-off. |
| `project-manager`| Multi-Project Hub | Host `lieutenant` provisions and tracks multiple isolated project packs under `projects/<name>/`. |
| `lieutenant` | Hierarchical Single Forge | Central planner agent coordinates task decomposition into local worker packs. |
| `squad` | Dynamic Ephemeral Workers | `squad-leader` + `troubleshooter` spawn on-demand ephemeral workers per story and tear them down on merge. |
| `sprint-module-squad` | Sprint-Oriented Modular Swarm | Modular architectural boundary enforcement managed by `squadd` daemon across sprint backlogs. |

## 4. DNK OS Swarm Adaptation Mapping

1. **Parallel Worker File Isolation**:
   - In `dnk_swarm_parallel`, assign distinct Git worktrees or isolated subpaths for `gerych_builder`, `gerych_auditor`, and `dnk_dev_fullstack` to prevent concurrent write collisions.
2. **Standardized Task Handoff Format**:
   - Adopt the `git_handoff` header format (`task`, `commit_sha`, `artifacts`, `priority`) for Swarm Event logs in DNK OS.
3. **Adversarial Gate Synthesis**:
   - Enrich `dnk_run_adversarial_review` with the `adversaries` review contract and `six-pack` hardener mutation checks.
