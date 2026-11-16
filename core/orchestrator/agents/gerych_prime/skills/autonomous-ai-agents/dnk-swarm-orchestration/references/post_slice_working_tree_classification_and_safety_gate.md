# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/post_slice_working_tree_classification_and_safety_gate.md"
# purpose: "Reference guide for post-slice uncommitted working tree classification, multi-agent noise suppression, and slice progression safety gates."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ Post-Slice Working Tree Classification & Slice Safety Gate Protocol (WT-CLASS-001)

## 1. Context and Problem Statement
In large multi-agent monorepos (such as DNK OS), multiple concurrent agents, daemons, background test runners, and external submodules (e.g. `visual_shell/open_design/`) frequently leave files in an uncommitted or untracked state.

After committing an atomic slice (e.g. `AAB-005`), an agent cannot simply assume the working tree is either 100% clean or completely broken. A systematic classification is required before starting the next slice (`AAB-006`) to ensure:
1. No slice-critical files were forgotten (`slice_omitted`).
2. No sensitive credentials, keys, or tokens are lying unmasked in the workspace (`secret_risk`).
3. Leftover uncommitted changes do not belong to the committed slice and do not introduce breaking interface conflicts (`parallel_work`, `runtime_artifact`, `cache_or_log`).

---

## 2. Mandatory Diagnostic Commands
Immediately after the slice commit, execute read-only git probes:

```bash
git status --short
git diff --name-only
git diff --stat
git ls-files --others --exclude-standard
```

---

## 3. Standard Classification Taxonomy

For each uncommitted file or logical cluster:

```yaml
path: "<relative_path>"
state: modified | untracked | deleted
classification: <category>
recommended_action: <action>
reason: "<justification>"
```

### Classification Categories:
- **`slice_omitted`** (BLOCKER): File belongs to the slice just implemented, but was omitted from the commit.
  - *Action*: `commit_separately` or amend commit immediately before moving forward.
- **`parallel_work`** (BENIGN / ISOLATED): Files belonging to parallel workstreams, other slices, or external submodules.
  - *Action*: `commit_separately` or leave uncommitted until that workstream completes.
- **`runtime_artifact`** (BENIGN): Session checkpoints, accounting logs, temporary execution states.
  - *Action*: `add_to_gitignore` or `discard`.
- **`cache_or_log`** (BENIGN): Build artifacts, bytecode, test traces.
  - *Action*: `add_to_gitignore` or `discard`.
- **`secret_risk`** (CRITICAL BLOCKER): Contains secrets, tokens, `.env`, credentials, or private keys.
  - *Action*: `quarantine` immediately. Do NOT echo or display content in chat logs!
- **`unknown`**: Unrecognized files.
  - *Action*: `investigate`.

---

## 4. Context Budget & Token Diet Protection for Massively Dirty Working Trees
When working in repositories where submodules or external repos (e.g. `visual_shell/open_design/` with 4,000+ files) dominate `git status --short`:
- **DO NOT** output 4,000 individual YAML items in the response! This exhausts the tool/output budget and causes context compression.
- **Group high-volume directories** into aggregate blocks (e.g. `path: "visual_shell/open_design/"` with `state: modified`, `classification: parallel_work`).
- Provide individual itemized YAML entries for files in `core/`, `apps/`, `scripts/`, `docs/`, `tests/`, `telemetry/`, and `sessions/`.

---

## 5. Completion Report & Gate Verdict Contract

Every classification turn must conclude with the canonical Completion Report:

```yaml
status: COMPLETED | BLOCKED
working_tree_clean: false
files_found: <total_count>
classifications:
  slice_omitted: []
  parallel_work: [...]
  runtime_artifact: [...]
  cache_or_log: [...]
  secret_risk: []
  unknown: []
safe_to_start_next_slice: true | false
reason: "<deterministic justification>"
```

### Safety Criteria for `safe_to_start_next_slice: true`:
1. `slice_omitted` is strictly empty (`[]`).
2. `secret_risk` is strictly empty (`[]`).
3. Targeted unit tests and test suites for the current and upcoming slice pass 100% green.
4. Remaining uncommitted files have zero contract overlap with the upcoming slice.
