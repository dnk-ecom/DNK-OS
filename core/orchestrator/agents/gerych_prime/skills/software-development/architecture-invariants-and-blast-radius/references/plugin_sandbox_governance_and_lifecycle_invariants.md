# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/architecture-invariants-and-blast-radius/references/plugin_sandbox_governance_and_lifecycle_invariants.md"
# purpose: "Declarative Sandbox-First Plugin Governance Policy & Lifecycle Invariants Architecture Protocol"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.6.0"
# updated_at: "2026-09-09"
# author: "Gerych Prime & Maxim Kuzmenko"
# --- END DNK-MRH-HEADER ---

# Sandbox-First Plugin Governance & Lifecycle Invariants

This protocol establishes the architectural rules, security boundaries, and fail-closed lifecycle transitions for extensible plugins in DNK OS.

## 1. Five-Stage Lifecycle State Machine

Plugins must progress through an explicit 5-stage lifecycle:
```text
draft ──► sandbox ──► evaluated ──► active ──► deprecated
  │          │            │           ▲
  └──────────┴────────────┴───────────┘ (Direct active jump BLOCKED)
```

- **`draft`**: Initial definition. Manifest created, minimal metadata, strictly unprivileged.
- **`sandbox`**: Isolated environment for testing. Requires explicit contract test path and isolated entrypoint.
- **`evaluated`**: Candidate stage. Contract tests and security review performed; evidence artifacts generated.
- **`active`**: Production runtime execution allowed. Requires explicit owner approval (`Maksym`), passing tests, security review, and verified license.
- **`deprecated`**: Phased-out or retired. Must document replacement plugin or retirement rationale.

## 2. Default-Deny Permission Matrix

To eliminate zero-day risks and unauthorized runtime access, uncertified stages (`draft`, `sandbox`) are subject to strict default-deny constraints:

| Permission | `draft` | `sandbox` | `evaluated` | `active` |
|---|---|---|---|---|
| `secrets` | `none` (MANDATORY) | `none` (MANDATORY) | `none` / scoped | scoped via vault |
| `git` | `none` (MANDATORY) | `none` (MANDATORY) | `none` | scoped repository |
| `database` | `none` (MANDATORY) | `none` (MANDATORY) | `none` | scoped tables |
| `external_write` | `none` (MANDATORY) | `none` (MANDATORY) | `none` | approved target |
| `filesystem` | `none` / `workspace_readonly` | `none` / `workspace_readonly` | scoped | scoped |
| `network` | `none` / `allowlist` | `none` / `allowlist` | scoped | allowlist / full |

Any violation in `draft` or `sandbox` manifests triggers immediate Pydantic validation failure.

## 3. Transition Policy & Promotion Invariants

1. **Self-Transition Guard**:
   A plugin can NEVER change its own lifecycle (`actor == plugin_id` is unconditionally rejected). Transitions must be executed by authorized system actors (`gerych_prime`, `maksym`, `governance_runner`).
2. **No Direct Jumps to Active**:
   `sandbox ➔ active` direct promotion is physically blocked. Every plugin must pass through `evaluated`.
3. **Evidence & Approval Gate for Active**:
   Promotion to `active` requires:
   - Valid `contract_test_path` pointing to existing test file.
   - Valid `security_review_path` pointing to security audit.
   - Non-empty `evidence_paths` list.
   - Explicit `approval_record` signed by `Maksym`.
4. **Origin & Provenance Rules**:
   - `internal`: `repository_url` must be null, `license_spdx: DNK-INTERNAL`.
   - `open_source`: Immutable Git commit SHA, valid repository URL, and approved SPDX license required.
   - `generated`: Provenance note documenting prompt/session required.
   - Unknown or non-compliant licenses (`unknown`, unapproved) can never enter `active`.

## 4. Verification CLI & Offline Validation Pattern

Policy engines must be decoupled from the runtime environment. Static card validation and transition checking should execute offline without spinning up containers, reading secrets, or writing databases:

```bash
# Validate card syntax, types, and default-deny invariants
./.venv/bin/python3 scripts/system/plugin_policy.py validate templates/plugin/plugin_card.yaml

# Check valid lifecycle progression
./.venv/bin/python3 scripts/system/plugin_policy.py check-transition \
  --from draft --to sandbox \
  --card templates/plugin/plugin_card.yaml

# Verify fail-closed security gates
./.venv/bin/python3 scripts/system/plugin_policy.py check-transition \
  --from sandbox --to active \
  --card templates/plugin/plugin_card.yaml  # Exits 1 (BLOCKED)
```

## 5. Local Sandbox Runner Execution Invariants (PLUGIN-002)

To demonstrate that policy is physically enforced before execution without requiring heavyweight Docker or container runtimes, the local `PluginSandboxRunner` adheres to five runtime invariants:

1. **Pre-Import Policy Gate**:
   - Validation occurs strictly **before** any plugin module or entrypoint code is imported or executed in Python.
   - If `card.lifecycle != "sandbox"` or permissions exceed sandbox bounds (e.g. `network != "none"`, `filesystem` outside `["none", "workspace_readonly"]`), runner immediately halts with status `blocked` and exit code `1`.
2. **Deterministic Execution Plan (`SandboxExecutionPlan`)**:
   - Every run generates an immutable execution plan detailing entrypoint, sanitized environment, timeout constraints, and allowed relative paths.
3. **Ephemeral Subprocess Workspace**:
   - Execution occurs in an ephemeral temporary directory (`tempfile.TemporaryDirectory`) isolated from repository source code.
   - Process runs via isolated Python subprocess with stripped environment variables (`env={}`) and strict wall-clock timeout (`max_execution_seconds: 5`).
   - Cleanup of temporary directory is guaranteed in a `finally:` block.
4. **Explicit Denial Proof Flags**:
   - Every `SandboxExecutionResult` must explicitly certify all zero-privilege security flags:
     ```python
     network_called: bool = False
     secrets_read: bool = False
     git_called: bool = False
     database_called: bool = False
     external_write_called: bool = False
     temporary_workspace_cleaned: bool = True
     policy_enforced: bool = True
     ```
   - In the event of a blocked run, timeout, or failure, these flags remain `False` to prove containment.
5. **Output Budget Hard Cap**:
   - Subprocess stdout and stderr are strictly truncated to `max_output_chars: 4000` to prevent memory exhaustion and log-flooding attacks.

## 6. Implementation & Testing Pitfalls

1. **Pytest `tmp_path` vs Universal Relative Path Invariant**:
   - Standard `tmp_path` in pytest resolves to absolute system paths (`/private/var/...` or `/tmp/...`).
   - If domain models validate `_is_relative_path` (enforcing DNK Relative Path Invariant), test fixtures must create temporary folders relative to the repository workspace (e.g. `Path("templates/plugin/fixtures/_test_tmp")`) and yield clean-up teardowns.
2. **Pydantic v2 Serialization for YAML Dumps**:
   - When dumping Pydantic models containing `Enum` fields (such as `SandboxStatus` or `EntrypointType`) into YAML via `yaml.safe_dump()`, calling `model.model_dump()` preserves Enum objects, resulting in `yaml.representer.RepresenterError`.
   - **Fix**: Always call `model.model_dump(mode="json")` before passing dictionary to `yaml.safe_dump()`.

## 7. Plugin Certification & Activation Review Protocol (PLUGIN-003)

Formal certification policy governs the promotion of plugins from `evaluated` to `active`:
```text
evaluated ────────────► [ Certification & Review Gate ] ────────────► active
             (Contract Tests + Security Review + Approver: Maksym)
```

### 1. Mandatory Invariant Gates for `evaluated → active`
Promotion requires a complete `PluginCertification` record containing:
- **Contract Tests**:
  - `test_file`: Valid relative path under `tests/plugins/<plugin_id>/`.
  - `failed: 0`, `total > 0`, `coverage_pct >= 80.0`.
- **Security Review**:
  - `reviewer != plugin_id` (Non-self-certification invariant).
  - `passed: True`.
  - If `risk_level` is `high` or `critical`, `notes` is mandatory and cannot be empty or boilerplate.
- **Activation Approval**:
  - `approver == "maksym"` (Owner-only approval invariant; system or agent actors are rejected).
  - Valid `approval_record` relative path and SHA-256 signature hash.
- **Evidence Verification**:
  - Minimum 3 evidence paths pointing to markdown files: `contract_test_evidence`, `security_review`, `activation_approval`.
  - Evidence files must be populated and verified (placeholder markers like `TBD`, `TODO`, `FILL_ME` fail verification).
- **Zero-Action Safety Invariants**:
  - Certification does not automatically run plugin code or mutate system runtime.

### 2. Verification CLI Commands
```bash
# Check evidence completion and certification validity
./.venv/bin/python3 scripts/system/plugin_certification.py check \
  --plugin-id <plugin_id> \
  --card <path_to_card.yaml> \
  --evidence-dir <path_to_evidence_dir>

# Scaffold evidence templates for review
./.venv/bin/python3 scripts/system/plugin_certification.py generate-evidence \
  --plugin-id <plugin_id> \
  --output-dir <path_to_evidence_dir>
```

### 3. Pydantic v2 Cross-Field Validation Pitfall
- Use `model_validator(mode="after")` to cross-validate entities across nested models:
  - Ensure `certified_by != plugin_id`.
  - Ensure `security_review.reviewer != plugin_id`.
  - Ensure `activation_approval.approver.lower() == "maksym"`.
- When checking relative paths across all models, enforce `not Path(p).is_absolute()` to preserve the DNK Relative Path Invariant.

## 8. GitHub Open-Source Intake Protocol (PLUGIN-004)

Standardized ingestion of open-source plugins from external GitHub repositories into the DNK OS ecosystem under strict zero-trust conditions:
```text
External GitHub Repo ──► [ Intake Validation Gate ] ──► Sandbox-Only PluginCard YAML
                           (HTTPS, 40-char SHA, SPDX,
                            Zero-Privilege Default Deny)
```

### 1. Mandatory Ingestion Invariants
- **Provenance Verification**:
  - `repository_url`: Must be a valid `https://github.com/...` URL.
  - `commit_sha`: Must be an exact 40-character hexadecimal Git commit SHA (floating branches or tags are forbidden to ensure reproducible immutability).
- **License Compliance**:
  - License must belong to the approved permissive set: `MIT`, `Apache-2.0`, `BSD-3-Clause`, `ISC`.
- **Fail-Closed Lifecycle & Permissions**:
  - Initial lifecycle is strictly forced to `sandbox`.
  - Default permissions are locked to `none` (`secrets: none`, `git: none`, `database: none`, `network: none`, `external_write: none`).
- **Path Traversal Guards**:
  - All file references must be relative paths within repository root (`not Path(p).is_absolute()` and no parent directory references `..`).

### 2. CLI Intake Commands
```bash
# Generate a validated sandbox card template from GitHub metadata
./.venv/bin/python3 scripts/system/plugin_github_intake.py generate-template \
  --plugin-id <plugin_id> \
  --name "<Plugin Name>" \
  --repo-url "https://github.com/..." \
  --commit-sha "<40_char_sha>" \
  --license-spdx "MIT" \
  --output "templates/plugin/github/<plugin_id>_card.yaml"

# Validate intake parameters against schema
./.venv/bin/python3 scripts/system/plugin_github_intake.py validate \
  --card "templates/plugin/github/<plugin_id>_card.yaml"
```

## 9. Plugin Discovery & Registry Protocol (PLUGIN-005)

A lightweight, zero-runtime discovery registry providing discovery, indexing, and CLI querying across all registered plugins without executing code:
```text
templates/plugin/*.yaml
templates/plugin/github/*_card.yaml
           │
           ▼
[ Deterministic Scanner ] ──► templates/plugin/plugins_index.json
           │
           ▼
[ Registry CLI Query Engine ] (scan | list --lifecycle/--kind | show <plugin_id>)
```

### 1. Core Discovery Invariants
- **Zero-Execution Static Analysis**:
  - Scanner inspects only declarative YAML manifests (`PluginCard`).
  - No Python modules are imported, no subprocesses spawned, no network/database/git/secret operations performed.
- **Fail-Tolerant Indexing**:
  - Unparseable files or template templates (`*.template.yaml`) are ignored during indexing rather than throwing unhandled exceptions.
  - Index maintains `plugin_id`, `name`, `version`, `kind`, `lifecycle`, `origin_type`, `license_spdx`, `card_path`, and `updated_at`.
- **Index File SSOT**:
  - Registry outputs a unified machine-readable JSON index at `templates/plugin/plugins_index.json`.

### 2. CLI Commands
```bash
# Scan plugin directories and update the JSON index
./.venv/bin/python3 scripts/system/plugin_registry.py scan

# List plugins with tabular output and optional filters
./.venv/bin/python3 scripts/system/plugin_registry.py list
./.venv/bin/python3 scripts/system/plugin_registry.py list --lifecycle sandbox
./.venv/bin/python3 scripts/system/plugin_registry.py list --kind tool

# Display raw plugin card content
./.venv/bin/python3 scripts/system/plugin_registry.py show <plugin_id>
```

### 3. Pytest Fixture Traversal Pitfall & Workspace Fix
- When testing path-checking utilities that disallow `..` traversal, standard `tmp_path` generates absolute paths under `/private/var/folders/...` (macOS) or `/tmp/...` (Linux). Calling `os.path.relpath(tmp_path, cwd)` results in `../../../../private/var/...`, which immediately triggers directory traversal violations.
- **Invariant Fix**: Test fixtures must allocate temporary test directories directly inside the repository workspace (e.g. `templates/plugin/_test_tmp_<uuid>` or `tests/plugins/_tmp_<uuid>`) and ensure cleanup in a `finally` or `yield` block.

## 10. Plugin Capability Graph Protocol (PLUGIN-006)

A deterministic capability dependency graph modeling producer-consumer relationships between plugins via declarative `capabilities.provides` and `capabilities.requires`:
```text
Plugin A (provides: [X]) ──[CapabilityEdge (X)]──► Plugin B (requires: [X])
```

### 1. Core Graph Invariants
- **Schema & Pydantic Data Contract**:
  - `CapabilityNode`: `plugin_id: str`, `capability: str`, `direction: str` ("provides" or "requires").
  - `CapabilityEdge`: `from_plugin: str`, `from_capability: str`, `to_plugin: str`, `to_capability: str`.
  - `CapabilityGraph`: `nodes: list[CapabilityNode]`, `edges: list[CapabilityEdge]`, `version: str = "0.1.0"`.
- **Deterministic Edge Construction Rules**:
  - Edge is created if and only if:
    1. `plugin_A.provides` contains capability `X`.
    2. `plugin_B.requires` contains capability `X`.
    3. `plugin_A != plugin_B` (Strict anti-self-loop invariant: plugins cannot depend on themselves).
- **Wildcard Prohibition in MVP**:
  - Capabilities must be explicit exact dot-separated identifiers (e.g. `example.read`, `shopify.liquid.render`).
  - Wildcards (`*`, `?`) are strictly forbidden during MVP to prevent unpredictable dependency explosions and implicit access grants.
- **Offline & Read-Only Safety**:
  - Graph builder operates purely on declarative manifests without activating plugins, importing entrypoints, touching secrets, connecting to networks, or querying databases.
- **CLI Commands**:
  ```bash
  # Build graph and save JSON artifact
  ./.venv/bin/python3 scripts/system/plugin_capability_graph.py build

  # Inspect ASCII table of nodes and edges
  ./.venv/bin/python3 scripts/system/plugin_capability_graph.py show

  # Query detailed dependencies for a plugin
  ./.venv/bin/python3 scripts/system/plugin_capability_graph.py deps <plugin_id>
  ```

## 11. Plugin Execution Plan Protocol (PLUGIN-007)

A deterministic capability-based planner that compiles abstract task goals into validated DAG execution plans:
```text
Task Requirements ──► [ Planner / Capability Matcher ] ──► ExecutionPlan (JSON)
                                                                 │
                                                       (Topological Order,
                                                        DAG Validation,
                                                        Acyclic Check)
```

### 1. Core Plan Invariants
- **Schema & Pydantic Data Contract**:
  - `ExecutionPlanStep`: `step_id: str`, `plugin_id: str`, `capability: str`, `payload: dict`, `depends_on: list[str] = []`.
  - `ExecutionPlan`: `plan_id: str`, `task_id: str`, `steps: list[ExecutionPlanStep]`, `version: str = "0.1.0"`.
  - `ExecutionPlanValidationResult`: `valid: bool`, `errors: list[str]`, `warnings: list[str]`.
- **DAG & Cycle Detection**:
  - Step dependencies (`depends_on`) must reference valid prior `step_id`s within the plan.
  - Dependency graph must be strictly acyclic (cycles trigger immediate validation failure).
  - Unresolved dependencies or unknown capabilities reject plan compilation.
- **Offline Safety**:
  - Compiles and validates plans purely through static metadata inspection without activating plugins or running code.

### 2. CLI Commands
```bash
# Compile execution plan from task ID and capabilities
./.venv/bin/python3 scripts/system/plugin_plan.py compile \
  --task-id <task_id> \
  --capabilities <cap1> <cap2> \
  --output templates/plugin/execution_plans/<plan_id>.json

# Validate plan schema and acyclic DAG structure
./.venv/bin/python3 scripts/system/plugin_plan.py validate \
  templates/plugin/execution_plans/<plan_id>.json
```

## 12. Plugin Execution Engine MVP Protocol (PLUGIN-008)

An isolated runtime execution engine executing validated plans sequentially via ephemeral subprocess sandbox runners:
```text
ExecutionPlan (JSON) ──► [ Execution Engine Gatekeeper ] ──► PluginSandboxRunner (Subprocess)
                                    │                                  │
                     (Zero-Trust Permission Check,              (5s Wall-clock Timeout,
                      Lifecycle Sandbox/Active Check,           Ephemeral Tempdir,
                      Local Fixtures Only)                      Deterministic run(payload))
```

### 1. Core Execution Engine Invariants
- **Schema & Pydantic Data Contract**:
  - `ExecutionRun`: `run_id: str`, `task_id: str`, `plan_path: str`, `started_at: str`, `finished_at: Optional[str]`, `status: str` (`running`, `completed`, `failed`, `blocked`).
  - `ExecutionStepResult`: `step_id: str`, `plugin_id: str`, `capability: str`, `status: str` (`running`, `completed`, `failed`, `blocked`), `output: Optional[dict]`, `error: Optional[str]`.
  - `ExecutionResult`: `run_id: str`, `task_id: str`, `status: str`, `steps: list[ExecutionStepResult]`, `total_steps: int`, `completed_steps: int`, `failed_steps: int`, `blocked_steps: int`.
- **Zero-Trust Permission Filter**:
  - Execution strictly rejects any plugin requiring elevated permissions:
    `network != "none"`, `secrets != "none"`, `git != "none"`, `database != "none"`, `external_write != "none"`.
  - Any non-"none" permission immediately blocks the step with status `blocked` without executing code.
- **Lifecycle Filter**:
  - Only plugins in lifecycle `sandbox` or `active` are permitted to execute.
  - Plugins in `draft`, `evaluated`, or `deprecated` are blocked.
- **Fixture Origin Constraint**:
  - Engine strictly restricts Python entrypoints to fixtures residing in `templates/plugin/fixtures/`.
  - External, remote, or arbitrary module execution is physically rejected.
- **Ephemeral Subprocess Sandbox Isolation**:
  - Each allowed step executes via `PluginSandboxRunner` in an isolated ephemeral workspace with stripped environment and 5s hard timeout.
- **Status Propagation**:
  - If any step is `blocked`, the overall execution status becomes `blocked` (or `failed` if an error occurs).
  - Step results and run records persist to `templates/plugin/execution_results/` and `templates/plugin/execution_runs/`.

### 2. CLI Commands
```bash
# Execute plan through sandbox engine
./.venv/bin/python3 scripts/system/plugin_execute.py run \
  templates/plugin/execution_plans/<plan_id>.json

# Inspect status and step outcomes of execution run
./.venv/bin/python3 scripts/system/plugin_execute.py status <run_id>
```

### 3. Verification & Traversal Invariants
- All plan, card, and result paths must strictly adhere to the universal relative path invariant (`not Path(p).is_absolute()` and `".." not in Path(p).parts`).

## 13. Plugin Audit Log Protocol (PLUGIN-009)

An immutable, append-only JSONL audit trail recording all lifecycle, execution, and discovery events across DNK OS plugins:
```text
Plugin Event (intake | sandbox | certification | plan | execute | lifecycle | registry)
                                │
                                ▼
                       [ AuditLogManager ] ──► templates/plugin/audit/audit_log.jsonl (mode="a")
                                │
                                ▼
                       [ Audit CLI Query Engine ] (log | show <plugin_id> | tail <limit>)
```

### 1. Core Audit Log Invariants
- **Schema & Pydantic Data Contract**:
  - `AuditEventType`: Enum of 7 strictly allowed events:
    `plugin.intake`, `plugin.sandbox_run`, `plugin.certification`, `plugin.execution_plan_create`, `plugin.execution_run`, `plugin.lifecycle_transition`, `plugin.registry_scan`.
  - `AuditActor`: Enum of authorized actors (`gerych_prime`, `maksym`, `system`).
  - `AuditEvent`: `event_id: str` (e.g. `evt-<12_hex>`), `timestamp: str` (ISO-8601 UTC), `event_type: AuditEventType`, `plugin_id: str`, `actor: AuditActor`, `details: dict = {}`.
  - `AuditLog`: `log_path: str = "templates/plugin/audit/audit_log.jsonl"`, `events: list[AuditEvent] = []`.
- **Append-Only Immutability**:
  - Log writes strictly open the target file in append mode (`open(path, "a", encoding="utf-8")`).
  - Existing lines are never overwritten, rewritten, or mutated.
  - Each entry is guaranteed to be a single-line valid JSON object ending with newline (`\n`).
- **Chronological Sorting**:
  - Retrieval methods (`get_events_by_plugin`, `tail`) guarantee chronological ordering by `timestamp` (ISO-8601 string sort).
- **Zero-Action Containment**:
  - Logging operates strictly offline: no network sockets, no secrets/vault access, no Git subprocesses, no external database connections.
  - Enforces universal relative path validation (`is_relative_to_repo` rejecting absolute paths and `..` traversal).

### 2. CLI Commands
```bash
# Append an audit event to JSONL log
./.venv/bin/python3 scripts/system/plugin_audit.py log \
  --event-type plugin.intake \
  --plugin-id github-plugin-001 \
  --actor gerych_prime \
  --details '{"repository_url":"https://github.com/example/repo"}'

# Display all audit events recorded for a specific plugin
./.venv/bin/python3 scripts/system/plugin_audit.py show \
  --plugin-id github-plugin-001

# Display the last N audit events in chronological order
./.venv/bin/python3 scripts/system/plugin_audit.py tail \
  --limit 10
```

### 3. Testing Invariant: Workspace-Relative Fixture Directories
- When validating paths in tests against relative-path validators (rejecting `..` and absolute paths), standard pytest `tmp_path` creates directories under `/private/var/...` (macOS), which cannot be converted to workspace-relative paths without `..` traversal.
- **Fixture Pattern**: Create an ephemeral directory directly inside the repository workspace (e.g. `tests/plugins/_tmp_audit_<uuid>`), execute tests, and clean up unconditionally in a `pytest.fixture(autouse=False)` teardown block.

## 14. Plugin Health & Metrics Protocol (PLUGIN-010)

A lightweight, non-invasive health evaluation and metrics aggregation layer across DNK OS plugins without executing runtime code:
```text
Plugin Cards / Index + Audit Log + Execution Runs
                     │
                     ▼
           [ PluginHealthEngine ]
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
PluginHealthStatus       SystemHealthReport
(health_score: [0, 100]) (average_health_score, lifecycle/kind distribution)
         │                       │
         └───────────┬───────────┘
                     ▼
        [ CLI: scripts/system/plugin_health.py ] (plugin | system | export)
```

### 1. Core Data Models & Metrics Contracts
- **`PluginHealthStatus`**:
  - `plugin_id: str`
  - `lifecycle: str` ("draft", "sandbox", "evaluated", "active", "deprecated")
  - `last_intake_at: Optional[str]` (ISO-8601 UTC)
  - `last_sandbox_run_at: Optional[str]`
  - `last_certification_at: Optional[str]`
  - `last_execution_at: Optional[str]`
  - `total_sandbox_runs: int = 0`
  - `total_executions: int = 0`
  - `failed_executions: int = 0`
  - `blocked_executions: int = 0`
  - `health_score: int` (Range: [0, 100])
- **`SystemHealthReport`**:
  - `generated_at: str` (ISO-8601 UTC)
  - `total_plugins: int = 0`
  - `plugins_by_lifecycle: dict[str, int]` (initialized with all 5 lifecycles)
  - `plugins_by_kind: dict[str, int]` (initialized with all 6 plugin kinds)
  - `total_executions: int = 0`
  - `total_failed_executions: int = 0`
  - `total_blocked_executions: int = 0`
  - `average_health_score: int` (Default: 100 when empty, rounded integer mean)
  - `plugins: list[PluginHealthStatus] = []`

### 2. Deterministic Health Score Calculation Formula
The health score evaluates plugin trustworthiness via additive and deductive signals clamped to `[0, 100]`:
- `+20`: Valid `PluginCard` manifest exists.
- `+20`: Green sandbox run passed (`total_sandbox_runs > 0` and last run status passed).
- `+20`: Plugin is certified (`last_certification_at` is set).
- `+20`: At least one successful execution completed (`successful_executions > 0`).
- `-20`: For each failed execution (`failed_executions`).
- `-20`: For each blocked execution (`blocked_executions`).
- Clamped: `health_score = max(0, min(100, raw_score))`.

### 3. Registry & Card Deduplication Invariant
- When scanning the workspace for registered plugins, check `templates/plugin/plugins_index.json` first as the single source of truth (SSOT).
- Only if the index is missing or empty, perform directory fallback scanning (`templates/plugin/**/*.yaml`).
- Never perform unconditional dual scans to prevent double-counting plugin instances in system metrics.

### 4. CLI Commands
```bash
# Display health metrics for an individual plugin
./.venv/bin/python3 scripts/system/plugin_health.py plugin <plugin_id>

# Display aggregated system health metrics
./.venv/bin/python3 scripts/system/plugin_health.py system

# Export JSON system health report
./.venv/bin/python3 scripts/system/plugin_health.py export \
  --output templates/plugin/metrics/health_report.json
```

### 5. Testing Invariant: Workspace-Relative Fixture Directories
- Avoid using pytest's `tmp_path` fixture when validating relative path invariants (`validate_relative_path` rejecting `os.path.isabs` and `..` traversal).
- Allocate temporary directories inside the workspace (e.g. `tests/plugins/_test_health_<uuid>`), perform assertions, and clean up in a `yield` fixture.

## 15. Hyphenated Plugin Packages & Root Hygiene Gate Invariants

When building runtime DNK OS plugins (e.g. `packages/plugins/dnk-seamless-injection`):

1. **Canonical 8-Root Directory Placement (`packages/plugins/<plugin-slug>/`)**:
   - Even if a prompt specification suggests a top-level `plugins/<slug>/` path, `scripts/system/git_hygiene_guard.py` strictly enforces the Canonical 8-Root Directory Invariant (`apps`, `core`, `services`, `packages`, `infra`, `docs`, `tests`, `scripts`).
   - Always place runtime plugin modules under `packages/plugins/<plugin-slug>/` and expose `plugin.py` (inheriting `PluginBase`) + `plugin.json` + `mcp/server.py` + `skills/<skill-name>/SKILL.md`.
   - Never leave temporary `artifacts/` directories in the repo root before running `git_hygiene_guard.py`; remove them or route test outputs to `tmp_path`.

2. **Dynamic Package Loading Without Triggering AST Import Cycle False Positives**:
   - Because plugin directory names use hyphens (`dnk-seamless-injection`), tests must register a synthetic package alias in `sys.modules` via `importlib.util.spec_from_file_location("dnk_<slug>_pkg", plugin_root / "__init__.py", submodule_search_locations=[str(plugin_root)])`.
   - **Pitfall**: Writing static `from dnk_<slug>_pkg.core... import ...` statements at the top of test files causes `scripts/verify_all.sh --affected` static AST import-resolver checks to fail with `UnresolvedModuleError` because `dnk_<slug>_pkg` does not physically exist on disk.
   - **Fix**: After registering the dynamic spec in `sys.modules`, import submodules via `importlib.import_module("dnk_<slug>_pkg.core.module")` instead of static `from ... import` statements.

3. **Pillow `Image.point()` Deprecation Guard (Python 3.12 / Pillow 10+)**:
   - Never pass a callable `lambda p: ...` to `Image.point()` in image processing pipelines (triggers `DeprecationWarning` and slows pixel mapping).
   - Always pass a precomputed 256-entry lookup table list: `lut = [255 if i >= threshold else 0 for i in range(256)]; img.point(lut)`.

