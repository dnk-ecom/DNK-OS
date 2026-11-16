<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/shopify_helix_4gates_and_fleet_worktree_patterns.md"
purpose: "Condensed SOTA architectural patterns from Shopify Helix (4 Hard Gates), Fleet Engineering (Git Worktrees), and DNK OS CONTRACT-015-E Standard."
canonical_source: true
status: "Active"
version: "1.1.0"
updated_at: "2026-09-28"
author: "DNK-e.com Maksym & Gerych"
--- END DNK-MRH-HEADER -->

# 🛡️ Shopify Helix 4 Hard Gates, Fleet Worktree Patterns & DNK OS Standard

Distilled from real-world large-scale multi-agent deployments (Shopify 300-screen mobile rebuild & Fleet Swarm Engineering) and codified into DNK OS `CONTRACT-015-E`.

---

## 1. Shopify Helix 4 Hard Gates Protocol

### The Core Problem: Rules vs Gates
- **Rules in Prompts are Advice**: LLMs suffer from attention entropy and forget prompt rules during long runs.
- **Gates are Physical Barriers**: Execution is blocked by pre-exit hooks (e.g. Exit Code 2 interceptor) until concrete criteria pass.

### The 4 Progressive Quality Gates
```
Checkpoint Planned (TaskDNA Slice)
        │
        ▼
[Gate 1: Behavior Gate (TDD)]  ──► Failing tests written FIRST; 100% Green required
        │
        ▼
[Gate 2: UI Spatial Gate]      ──► Vision model (Gemini) checks layout, spacing, tokens
        │
        ▼
[Gate 3: Adversarial Gate]     ──► Auditor (Critic) ⚔️ vs Fixer (Builder) loop
        │
        ▼
[Gate 4: HITL & Learnings]     ──► Human review; feedback saved to persistent learnings
```

1. **Gate 1: Behavior Gate (TDD & Non-browser tests)**
   - Subagent plans and authors failing tests before code is touched.
   - Code builder runs until unit/integration tests are 100% green.
   - No UI clicking required for backend/logic validation.

2. **Gate 2: UI Spatial Gate**
   - Employs models with superior spatial awareness (e.g. Gemini 2.5/Flash/Pro).
   - Compares rendered screenshots against design specifications (spacing, font scale, tokens).

3. **Gate 3: Adversarial Gate (Auditor vs Fixer)**
   - Two specialized roles: `Auditor` (assumes code is defective, scans AST/security/anti-tautology) and `Fixer` (remediates findings).
   - Gate passes only upon explicit approval from the Auditor.

4. **Gate 4: Human-in-the-Loop & Learnings File**
   - Operator tests the final checkpoint.
   - Any operator feedback or correction is immediately committed to a persistent `learnings` file (`docs/notes/` or SCONES memory) that all future subagents load at Step 0.

---

## 2. Fleet Swarm Engineering & Concurrency Isolation

### Mitigating Multi-Agent File & Git Collisions
When running multiple coding agents concurrently (`dnk_swarm_parallel`), independent workers will collide if they share a single working tree or git branch.

```
                  ┌───► Agent 1 (Backend)  ──► .worktrees/wt-backend (branch: feature/api)
Orchestrator ─────┼───► Agent 2 (Shopify)  ──► .worktrees/wt-shopify (branch: feature/liquid)
(Supervisor)      └───► Agent 3 (Auditor)  ──► .worktrees/wt-auditor (read-only audit)
```

1. **Git Worktree Isolation**:
   - Each worker runs in its own worktree directory (`git worktree add -b <branch> <path>`).
   - Prevents branch conflicts, uncommitted git index corruption, and simultaneous write clobbering.
   - Upon subtask completion, worktree diffs are validated and merged back via OCC 3-way merge into the main feature branch before cleanup (`git worktree remove`).

2. **Compressed Handoff Documents vs Chat Dumps**:
   - **Never dump raw chat logs**: Handing off full conversational history burns context and slows reasoning.
   - **Handoff Artifacts**: Compress task status into a lightweight Markdown handoff pointing to specific file paths, test commands, and boundary contracts.

3. **Strict File Ownership Matrix**:
   - Explicit `target_files` whitelist assigned per worker.
   - Worker A is strictly read-only on Worker B's domain files.

---

## 3. Hermes Context Diet (Skill Retriever Pattern)
- When an agent environment contains 90+ skills, transmitting every skill description on every message costs 3,000–5,000 standing tokens.
- **Skill Retriever Pattern**: Semantic embedding matcher / FTS5 index filters the top-K (3–5) relevant skills for the active task prompt, drastically reducing standing context (keeping baseline overhead $\le 6\,000$ tokens at Step 0) and preventing attention rot.
- **Level-of-Detail (LOD)**: Load introductory slices first; subagents retrieve detailed `references/` or `templates/` on-demand via `skill_view(name, file_path=...)`.

---

## 4. Canonical DNK OS Implementation (CONTRACT-015-E)

The 4 Hard Gates are codified as an inviolable standard in:
`docs/notes/MY TASKS/1. АРХІТЕКТУРА/15. Контроль якості та Самозцілення/CONTRACTS/CONTRACT-015-E 4 Hard Gates Feature Development Standard.md`

| Hard Gate | Trigger & Enforcement Point | Blocking Criteria |
|-----------|-----------------------------|-------------------|
| **Gate 1: Pre-Execution Gate** | Step 0 before code mutation | Missing `Target File Whitelist`, missing `Negative Scope`, unbudgeted tool calls (>25), missing `dnk_triage_task`. Status `TURN_DOWN_WORK` if violated. |
| **Gate 2: Tool Execution Gate** | Synchronous during tool loop | Hook intercept (`hermes_pre_tool_hook.py`): $\ge 3$ repeated reads of unmutated files, absolute paths (`/Users/...`), mutating commands on non-whitelisted paths. |
| **Gate 3: Post-Execution Gate** | Prior to commit/reporting | Deterministic machine verification: `scripts/verify_all.sh` (exit code 0), `scripts/system/anti_tautology_gate.py` (AST checks), `markdown_schema_gate.py`. |
| **Gate 4: Commit & Promotion Gate** | Completion handoff | Automated atomic commit (`git commit`), clean git status, zero post-task conversational interrogation (machine proof is final). |

---

## 5. Clean-Room Reverse Engineering Enforcer (`helix_re_gate_runner.py`)

Based on the forensic post-mortem of Gerych Session `20261018_095122_a5a4e1` and `20261018_103147_7a2bc7`, Clean-Room Reverse Engineering tasks use `scripts/system/helix_re_gate_runner.py` (with `Exit Code 2` blocking) and skill `helix-reverse-engineering-workflow`:
- **Pre-Flight (`preflight`)**: Detects `/password` locks on Shopify dev previews and verifies live daemon sockets (`background=True, notify_on_complete=False`).
- **Spec Kit (`init-spec`)**: Generates `01_design_tokens_and_spatial_spec.md`, `02_data_contracts_and_state_machine.md`, and `03_feature_graph_task_dna.json` (`<= 350 LOC` per slice).
- **Gate 1 (`gate1`)**: Runs TDD suites plus Liquid tag balance, `{% schema %}` JSON validation, and `templates/*.json` -> `sections/<type>.liquid` verification.
- **Gate 2 (`gate2` / `generate-composite`)**: Eliminates `canvas.toBlob()` async download races via `Promise.all` and enforces the full-route Desktop (`1440x900`) + Mobile (`390x844`) viewport matrix.
- **Gate 3 & Gate 4 (`gate3` / `gate4`)**: Runs Adversarial Critic anti-mock/anti-tautology checks and appends distilled lessons to `learnings.md` under a 15,000-character context budget ratchet.
