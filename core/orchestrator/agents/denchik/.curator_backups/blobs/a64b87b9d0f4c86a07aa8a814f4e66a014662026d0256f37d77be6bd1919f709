# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/stateless_agent_runtime_and_disk_hygiene.md"
# purpose: "Reference architecture for stateless agent profiles, runtime state isolation, and disk hygiene."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🧹 Stateless Agent Profiles & Runtime State Isolation Protocol

## 1. Context & Motivation
When orchestrating multi-agent systems (e.g., 14 specialized swarm workers under Hermes/DNK OS), each agent directory (`core/orchestrator/agents/<agent_name>/`) acts as an agent profile.
Over operational cycles, agents generate heavy runtime artifacts:
- SQLite databases (`state.db`, `verification_evidence.db`) containing hundreds of message histories, embeddings, and telemetry (often 200MB - 1.5GB per agent).
- Language Server Protocol caches (`lsp/` pyright/ruff/typescript ASTs).
- Execution snapshots and rollback dumps (`checkpoints/`, `sandboxes/`, `pastes/`).
- Session transcripts, logs, and cached tool outputs (`cache/`, `logs/`, `terminal-sessions/`).

Without strict isolation, agent directories accumulate gigabytes of ephemeral ballast, leading to:
1. Slow git operations, accidental git tracking of binaries/DBs, and git index pollution.
2. Degraded static analysis and code search indexing across the monorepo.
3. Breaking the architectural invariant that **agent configurations (`SOUL.md`, `agent_card.yaml`, `skills/`, `memories/`) must be declarative, deterministic, and stateless**.

---

## 2. Stateless Agent Architecture Invariant
Agent directories in the repository MUST only contain version-controlled declarative metadata:
- `SOUL.md`: Persona, mission, system instructions, and tool constraints.
- `agent_card.yaml`: Agent capabilities, default models, temperature, and toolsets.
- `skills/`: Reusable procedural memory packages.
- `memories/`: Curated, human-verified L1 declarative knowledge (`MEMORY.md`).

All mutable, high-frequency, or ephemeral runtime artifacts MUST be isolated to:
`~/.hermes/runtime/<agent_name>/` or `.runtime_cache/<agent_name>/`.

---

## 3. Dynamic Launcher Isolation (`scripts/system/gerych.sh`)
The canonical launcher automatically sets up isolated external runtime directories and provisions symlinks inside the agent directory if the runner expects in-tree paths:

```bash
# Ensure runtime caches (lsp, checkpoints, cache, logs) are isolated to ~/.hermes/runtime
RUNTIME_AGENT_DIR="$HOME/.hermes/runtime/$TARGET_AGENT"
mkdir -p "$RUNTIME_AGENT_DIR/lsp" "$RUNTIME_AGENT_DIR/checkpoints" "$RUNTIME_AGENT_DIR/cache" "$RUNTIME_AGENT_DIR/logs"
for rdir in lsp checkpoints cache logs; do
    if [ ! -e "$HERMES_HOME/$rdir" ]; then
        ln -s "$RUNTIME_AGENT_DIR/$rdir" "$HERMES_HOME/$rdir" 2>/dev/null || true
    fi
done
```

---

## 4. Git Trailing Slash Invariant (`.gitignore`)
### ⚠️ Critical Gitignore Pitfall
In `.gitignore` syntax:
- A pattern ending in `/` (e.g., `core/orchestrator/agents/**/cache/`) matches **only real directories**.
- If `cache` is a **symlink** pointing to a directory, git treats it as a symbolic link (file object), NOT a directory! The rule `cache/` will silently fail to match, causing `cache` to appear as an untracked file (`?? cache`) in `git status`.

### Correct Specification:
Always provide patterns matching both the directory and the symlink name:
```gitignore
# Match both symlinks and direct folders
core/orchestrator/agents/**/checkpoints
core/orchestrator/agents/**/checkpoints/
core/orchestrator/agents/**/lsp
core/orchestrator/agents/**/lsp/
core/orchestrator/agents/**/bin
core/orchestrator/agents/**/bin/
core/orchestrator/agents/**/cache
core/orchestrator/agents/**/cache/
core/orchestrator/agents/**/logs
core/orchestrator/agents/**/logs/
core/orchestrator/agents/**/state.db*
core/orchestrator/agents/**/verification_evidence.db*
```

---

## 5. Agent State DB Compaction & FTS5 Trigram Rebuild Invariant
### ⚠️ The FTS5 Trigram Shadow Table Trap
In SQLite databases powering Hermes / Agent state with full-text search (`messages_fts`, `messages_fts_trigram`), deleting records (`DELETE FROM messages WHERE ...`) removes raw rows, but **DOES NOT reclaim inverted index shadow tables** (`messages_fts_trigram_data`, `messages_fts_trigram_idx`, `messages_fts_trigram_config`), which account for >65% of the total database bloat (often 800+ MB out of 1.3 GB!).
Running plain `DELETE` + `VACUUM` leaves hundreds of megabytes in stale trigram shards.

### Mandatory Rebuild Sequence:
To physically reclaim disk pages:
```python
import sqlite3

def compact_agent_state_db(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # 1. Rebuild FTS tables to compact inverted indexes
    cur.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild');")
    cur.execute("INSERT INTO messages_fts_trigram(messages_fts_trigram) VALUES('rebuild');")
    conn.commit()
    # 2. Checkpoint WAL and vacuum
    cur.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    cur.execute("VACUUM;")
    # 3. Verify database integrity
    cur.execute("PRAGMA integrity_check;")
    status = cur.fetchone()[0]
    assert status == "ok", f"Corrupted SQLite DB after vacuum: {status}"
    conn.close()
```

---

## 6. Zero-Loss Cold Archival Protocol (`.data/session_archives/`)
Never delete agent session history outright. Inactive sessions older than the retention cutoff (e.g. 7 days) must be exported to compressed JSONL files before deletion:
1. **Archive Path**: `.data/session_archives/<session_id>.jsonl.gz`.
2. **Payload Structure**:
   - First line: Session header metadata (id, title, timestamps, model, system prompt, profile).
   - Subsequent lines: Chronological message items (id, role, content, tool_calls, created_at).
3. **Active Session Protection**: Sessions with `active == 1` or `ended_at IS NULL` MUST NEVER be archived or deleted, regardless of age.
4. **Pre-Mutation Cryptographic Backup**: Always take a snapshot `state.db.bak.<timestamp>` with calculated SHA-256 before in-place mutation.
5. **Operational Verification**: Validate system queries post-pruning via `scripts/system/auto_session_auditor.py --latest`.
