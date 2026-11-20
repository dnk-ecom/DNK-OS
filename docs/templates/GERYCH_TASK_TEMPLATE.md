---
title: "Gerych Bulletproof Task Specification Standard"
description: "Canonical Task Formulation & Specification Standard v3.0 for Gerych Prime and Swarm Agents."
mrh_id: "docs/templates/GERYCH_TASK_TEMPLATE.md"
status: Active
archetype: TASK_SPEC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - dnk/templates
  - dnk/task-specification
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/templates/GERYCH_TASK_TEMPLATE.md"
> purpose: "Canonical Task Formulation & Specification Standard v3.0 for Gerych Prime and Swarm Agents."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "Antigravity (Mentor & Chief Architect), Gerych Prime & DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> ```

# 📋 Gerych Bulletproof Task Specification Standard (v3.0)

> **Zero-Waste High-Velocity Protocol (ZWSP) & Mandatory Atomic Slice Execution (MASE)**
> Governs all tasks dispatched to **Gerych (Hermes Prime)** and collaborating swarm agents.
> Guarantees 100% first-pass completion, zero token waste, and eliminates tool-exhaustion loops.

---

## 🎯 1. Task Header & Metadata

- **Task ID**: `TASK-DNK-[DOMAIN]-[YYYYMMDD]-[001]` *(e.g. TASK-DNK-AAB-20260909-001)*
- **Title**: `[Short, descriptive title of the task]`
- **Domain / Bounded Context**: `[apps/visual_shell | apps/api | services/dnk_* | core/* | docs/*]`
- **Primary Executor**: `[gerych_prime | gerych_builder | dnk_dev_fullstack | dnk_shopify | dnk_video_ai_creator | gerych_auditor]`
- **Collaborating Swarm Agents**: `[e.g. gerych_researcher, dnk_scones_memory, gerych_auditor, herich_librarian]`
- **Execution Mode**: `[MUTATION (Code Modification) | READ_ONLY_AUDIT (Investigation / Analysis)]`
- **Estimated Complexity**: `[P0 Critical | P1 High | P2 Medium | P3 Low]`

---

## 🛑 2. Negative Scope & Boundaries (Anti-Scope)

Specify explicitly what is STRICTLY FORBIDDEN to touch, modify, or assume:

- ❌ **Do NOT modify**: `[e.g. data/repo_catalog/catalog.db, core/runtime, TaskDNA]`
- ❌ **Do NOT perform**: `[e.g. automatic code synthesis, mass refactoring of legacy code]`
- ❌ **Do NOT introduce**: `[e.g. external databases, new unsanctioned npm/pip dependencies]`
- ❌ **Zero Absolute Paths**: Absolute paths (`/Users/...`) are strictly forbidden. Use repo-relative paths only.
- ❌ **Zero Unauthorized Root Folders**: Creating new top-level directories in root is strictly forbidden. Files must live within `apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`.
- ❌ **Zero Unsanctioned Microservices**: Creating new directories under `services/` is strictly forbidden. All development MUST map to the 3 Core Workhorses (`services/dnk_shopify`, `services/dnk_media`, `services/dnk_distribution`) or `core/`.
- ❌ **AI Turns Down Work Enforcer**: If this task lacks an explicit Target File Whitelist or unclarified data sources, the agent MUST output `STATUS: TURN_DOWN_WORK` and refuse speculative code generation.
- ❌ **Zero Secrets / Runtime Leaks**: No credentials, API tokens, or local cache state in version control.

---

## 🗺️ 3. Targeted File Manifest (Whitelist)

Specify the EXACT list of files allowed to be created or modified. Do NOT allow unwhitelisted files.

| Action | Target Relative Path | Responsibilities / Core Symbols |
| :--- | :--- | :--- |
| `[NEW]` | `docs/schemas/example.schema.yaml` | JSON Schema Draft-07 specification |
| `[NEW]` | `core/domain/models.py` | Pydantic v2 data models |
| `[NEW]` | `core/domain/engine.py` | Core domain engine & algorithms |
| `[NEW]` | `scripts/system/example_cli.py` | Read-only CLI tool (`--json`, human format) |
| `[NEW]` | `tests/domain/test_engine.py` | Comprehensive unit & regression tests |
| `[NEW]` | `docs/notes/XXX_title.md` | Obsidian knowledge note with MRH header |
| `[NEW]` | `docs/audit/TASK_evidence.json` | Verification & quality gate evidence |

---

## ⚙️ 4. Toolchain, Environment & JIT-Tooling Preconditions

- **Python Runtime**: Python 3.12+ in project virtualenv (`./.venv/bin/python3`)
- **Pre-installed Packages**: `pydantic>=2.0`, `pyyaml`, `pytest`, `jsonschema` (verify before execution)
- **SSOT Invariant**: Pydantic models serve as code SSOT; YAML schemas serve as external exchange contracts.
- **🛠️ Sanctioned Tools & MCP Whitelist (Zero Context Bloat)**:
  * **Allowed Core Tools**: `[e.g. view_file, replace_file_content, run_command]`
  * **Sanctioned Domain MCPs**: `[e.g. NONE | shopify_mcp | github_mcp]` *(Max 1 domain MCP per worker)*
  * **Strictly Detached MCPs**: `[Notion MCP, Chrome DevTools, Postgres MCP (STRICTLY FORBIDDEN unless task targets them)]`
  * **Standing Context Budget**: Baseline prompt at Step 0 must remain ≤ 6,000 tokens.

---

## 📐 5. Interface Contracts & Algorithmic Invariants

### A. Core Class & Method Signatures
```python
class DomainRegistry:
    def load_directory(self, directory: Path) -> None: ...
    def get(self, item_id: str) -> DomainModel | None: ...
    def search(self, query: str | None = None, limit: int = 20) -> list[DomainModel]: ...
```

### B. Business Logic Invariants (Pseudocode)
```python
# Disambiguate multi-entity filtering / conflicts:
# 1. Candidate C must not be in selected set S
# 2. For every s in S: C.id not in s.conflicts_with AND s.id not in C.conflicts_with
# 3. Sort deterministically: score DESC, id ASC
```

### C. Human-Readable CLI Output Format
- Human format: `"<id> | <type> | <domain> | score: <score> | <title>"`
- Machine format: `--json` outputs clean JSON array/dict without debug noise.

---

## 🧩 6. Mandatory Atomic Slices (MASE) & Acceptance Gates

Decompose execution into discrete slices bound by ≤ 25 tool calls each. Every slice MUST include machine-verifiable Acceptance Gates (assimilated from `unlazy` SOTA anti-laziness protocol):

### 🔹 Slice 1: Contracts, Schemas & Fixtures
- **Goal**: Create YAML schema, example fixture, and Pydantic v2 models.
- **Target Files**: `docs/schemas/...`, `core/.../models.py`, `tests/.../test_schema.py`
- **Acceptance Gates**:
  - [ ] G1.1: Pydantic v2 model validates schema fixture
    CHECK: pytest tests/.../test_schema.py -k test_fixture_valid
    EXPECT: 1 passed
    CWD: .
    EVIDENCE: pending
- **Budget**: ≤ 20 tool calls.

### 🔹 Slice 2: Core Engine & Deterministic Logic
- **Goal**: Implement parsers, registries, and business logic algorithms.
- **Target Files**: `core/.../parser.py`, `core/.../registry.py`, `tests/.../test_engine.py`
- **Acceptance Gates**:
  - [ ] G2.1: Deterministic resolution executes without state regression
    CHECK: pytest tests/.../test_engine.py
    EXPECT: passed in
    CWD: .
    EVIDENCE: pending
- **Budget**: ≤ 25 tool calls.

### 🔹 Slice 3: CLI & Integration Adapters
- **Goal**: Implement CLI script with `--json` and human-readable formats.
- **Target Files**: `scripts/system/...`
- **Acceptance Gates**:
  - [ ] G3.1: CLI returns valid JSON on --json flag
    CHECK: python3 scripts/system/... --json
    EXPECT: "ok": true
    CWD: .
    EVIDENCE: pending
- **Budget**: ≤ 20 tool calls.

### 🔹 Slice 4: Evidence, Note & Quality Gate
- **Goal**: Run `verify_all.sh`, generate Evidence JSON, and write Obsidian note.
- **Target Files**: `docs/notes/XXX_note.md`, `docs/audit/..._evidence.json`
- **Acceptance Gates**:
  - [ ] G4.1: Master Quality Gate passes 100%
    CHECK: bash scripts/verify_all.sh
    EXPECT: ALL AUDITS & TESTS PASSED
    CWD: .
    EVIDENCE: pending
- **Budget**: ≤ 15 tool calls.

---

## 🛡️ 7. Verification & Quality Gate Commands

```bash
# Unit & integration tests
./.venv/bin/python -m pytest tests/[domain] -q

# CLI interface checks
./.venv/bin/python scripts/system/[tool].py validate
./.venv/bin/python scripts/system/[tool].py list

# Master quality gate
./.venv/bin/python scripts/system/root_hygiene_guard.py
bash scripts/verify_all.sh
git diff --check
```

---

## 📋 8. Required Completion Report

```yaml
status: COMPLETED | PARTIAL | BLOCKED | FAILED
scope: "[Task Name / ID]"
files_created: []
files_modified: []
tests:
  command: "./.venv/bin/pytest tests/... -q"
  passed: 0
  failed: 0
verification:
  schema_validation: PASS | FAIL
  cli_commands: PASS | FAIL
  root_hygiene_guard: PASS | FAIL
  master_quality_gate: PASS | FAIL | BASELINE_FAILURE
safety:
  negative_scope_honored: true
  zero_absolute_paths: true
  zero_unauthorized_root_folders: true
  no_runtime_db_modified: true
  secrets_exposed: false
evidence: "docs/audit/..._evidence.json"
note: "docs/notes/XXX_...md"
commit: "[git commit hash]"
remaining_risks: []
next_recommended_slice: "[Next atomic step]"
```
