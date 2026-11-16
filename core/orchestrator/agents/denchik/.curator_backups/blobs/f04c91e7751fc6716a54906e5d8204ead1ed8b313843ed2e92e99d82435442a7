<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/runtime_artifact_hygiene.md"
# purpose: "Canonical Runtime Artifact, Disk Space, Process Guard & State Hygiene Runbook."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (herich_librarian & gerych_prime)"
# --- END DNK-MRH-HEADER ---
-->

# 🧹 Runtime Artifact, Disk Space & Process Hygiene Protocol

## 1. Overview & Core Invariants

This runbook establishes strict hygiene for the Gerych Swarm runtime across local workstations and CI environments.
To eliminate disk bloat, SQLite locks, zombie processes, and accidental git tree pollution:

1. **Stateless Agent Profile Invariant**:
   - Agent profile directories (`core/orchestrator/agents/<agent>/`) must remain strictly stateless and declarative (`SOUL.md`, `agent_card.yaml`, `skills/`, `memories/`).
   - Ephemeral runtime files (`state.db`, `verification_evidence.db`, `checkpoints/`, `cache/`, `logs/`, `lsp/`) must never be written directly inside profile directories.
   - Redirect runtime artifacts to `~/.hermes/runtime/<agent>/` via environment redirects or dynamic symlinks.

2. **Single-Instance Singleton Lock**:
   - Prevent concurrent agent collisions on SQLite files (`.hermes/sessions.db`, `canvas_production_fallback.db`).
   - Check and acquire single-instance lock via `python3 scripts/system/process_guard.py --check-lock <agent_name>`.
   - Auto-reap stale/dead instances via `python3 scripts/system/process_guard.py --audit` at launch.
   - Release lock cleanly on exit via process trap.

3. **Disk Saturation Alert & Auto-Pruning Threshold (>90%)**:
   - When disk capacity exceeds 90%, execute targeted prune sequences:
     - Docker build cache: `docker builder prune -a -f`
     - Stale pytest caches: `rm -rf .pytest_cache **/test_run_* **/__pycache__`
     - Visual shell temp artifacts: `rm -rf visual_shell/open_design/.tmp/*`
     - Node build scratch: `rm -rf apps/web/.next/cache`

---

## 2. SQLite WAL & Database Maintenance

Long-running agent sessions accumulate bloated Write-Ahead Logs (`.db-wal`) and unindexed history.

### Maintenance Commands

```bash
# Checkpoint WAL journals and truncate
sqlite3 ~/.hermes/sessions.db "PRAGMA wal_checkpoint(TRUNCATE);"
sqlite3 ~/.hermes/sessions.db "VACUUM;"

# For workspace verification evidence databases:
python3 -c "
import sqlite3, os
for db_path in ['verification_evidence.db', 'state.db']:
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA wal_checkpoint(TRUNCATE);')
        conn.execute('VACUUM;')
        conn.close()
"
```

---

## 3. Docker Compose & Monorepo Submodule Hygiene

1. **Port Collision Prevention (`3000`, `8000`, `5432`, `6379`)**:
   - Before launching Docker MVP stack:

     ```bash
     lsof -Pi :3000 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
     lsof -Pi :8000 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
     ```

2. **Submodule Exclusion on `git add`**:
   - Always exclude nested unpopulated submodules:

     ```bash
     git add -A -- ':!services/dnk_shopify/DNK-e.com'
     ```

3. **Aggressive Git Garbage Collection**:
   - Run in background with timeout protection:

     ```bash
     git gc --prune=now --aggressive
     ```

---

## 4. Operational Runbook & Emergency Cleanup

| Condition | Symptom | Action Runbook |
| :--- | :--- | :--- |
| **Disk > 90%** | `No space left on device` / SQLite I/O error | Run `docker system prune -f && docker builder prune -a -f`, prune `apps/web/.next/cache`. |
| **Zombie Agent** | Session hangs / Lock held | Run `python3 scripts/system/session_sentinel.py --reap-stale` or kill stale hermes PIDs. |
| **WAL Bloat** | `.hermes/sessions.db-wal` > 500 MB | Run `PRAGMA wal_checkpoint(TRUNCATE); VACUUM;`. |
| **Git Untracked Noise** | Hundreds of test files in git status | Clean temporary artifacts via `git clean -fdn` (dry-run) then `git clean -fd`. |
