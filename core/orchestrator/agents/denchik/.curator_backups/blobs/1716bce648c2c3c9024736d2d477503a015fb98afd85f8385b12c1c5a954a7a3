<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/hermes_core_audit_and_vendor_upgrade_protocol.md"
purpose: "Auditing, vendoring, and upgrading embedded Hermes Agent core within DNK OS without breaking local patches or runtime environments."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-29"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

# 🧬 Hermes Core Audit & Vendor Upgrade Protocol

## 📌 Context & Architecture
In DNK OS, Hermes Agent (`core/hermes_agent`) powers Gerych Prime and the swarm runtime.
The core is embedded directly within the unified `DNK_HUB` repository and installed in editable mode into the active runtime virtual environment (`~/.dnk_runtime/venv`).
Because `core/hermes_agent` lacks its own `.git` directory, standard upstream update commands (`hermes update --check` or `hermes update`) fail with `✗ Not a git repository`.

---

## ⚡ 1. Upstream Audit Checklist
When checking for upstream improvements from `NousResearch/hermes-agent`:
1. **Fetch Upstream Release Tags**:
   ```bash
   gh release list --repo NousResearch/hermes-agent --limit 10
   ```
2. **Inspect Specific Release Notes**:
   ```bash
   gh release view <tag> --repo NousResearch/hermes-agent
   ```
3. **Compare Commit Range**:
   ```bash
   gh api repos/NousResearch/hermes-agent/compare/<current_tag>...<target_tag> --jq '.total_commits, .commits[0:10]'
   ```

---

## 🛡️ 2. Critical Core Subsystems & Upgrade Evaluation Matrix

| Subsystem | What to Check in Upstream Diff | DNK Swarm Impact |
| :--- | :--- | :--- |
| **`delegate_task` / Subagents** | Completion groups, streaming returns, process handoff, `/stop` handling. | High: eliminates batch bottlenecks, prevents zombie subagents. |
| **`state.db` / SQLite** | POSIX lock handling, second-writer mitigations, WAL recovery, FTS5 corruption guards. | Critical: prevents session lockups and 4–20s startup hangs. |
| **Context Compression** | Commit fences during concurrent compaction, retry loops, OAuth token expiry. | Critical: eliminates 401 Unauthorized loops during long runs. |
| **FastMCP & Tooling** | Discovery concurrency caps, stdio crash isolation, browser process tree killing. | High: prevents tool registry starvation and memory leaks. |
| **Skills & Profiles** | `skills.auto_load`, multi-profile credential isolation. | High: ensures standard skills are always in context. |

---

## ⚠️ 3. Inviolable Invariant: Local Patch Preservation
DNK OS contains custom engine fixes inside `core/hermes_agent/`. NEVER perform a blind overwrite or naive git checkout of upstream files.

### Known Local Patches:
- **`core/hermes_agent/agent/vertex_adapter.py` (Commit `d7ba08e31a`)**:
  - Implements ADC OAuth bearer token expiration tracking.
  - Rejects stale tokens after 3000 seconds, forcing fresh token generation.
  - **Failure mode if overwritten**: Long-running sessions (>50 turns) hit `401 Unauthorized` during context compression, aborting the agent loop.

---

## 🚀 4. Step-by-Step Vendor Upgrade Procedure

1. **Create Dedicated Feature Branch**:
   ```bash
   git checkout -b dnk-mvp/feature/hermes-agent-v<target_version>-upgrade
   ```
2. **Inspect Local Changes**:
   ```bash
   git diff v<current_version>..HEAD core/hermes_agent/
   ```
3. **Apply Upstream Diff / Vendor Sync**:
   - Download upstream release tarball or diff:
     ```bash
     gh api repos/NousResearch/hermes-agent/tarball/v<target_version> -o /tmp/hermes_upstream.tar.gz
     ```
   - Unpack and sync to `core/hermes_agent/`, excluding custom configuration.
4. **Re-apply and Verify Local Patches**:
   - Re-check `core/hermes_agent/agent/vertex_adapter.py` token refresh logic.
5. **Sync Runtime Dependencies**:
   ```bash
   ~/.dnk_runtime/venv/bin/uv pip install -e core/hermes_agent
   ```
6. **Execute Verification Gate**:
   ```bash
   bash scripts/verify_all.sh
   # Perform live FastMCP and delegate_task sanity test
   ```
7. **Commit & Produce Signed Evidence**:
   ```bash
   python3 scripts/system/generate_evidence.py --task CORE-HERMES-UPGRADE --title "Hermes Agent v<target> Upgrade" --components core/hermes_agent
   ```
