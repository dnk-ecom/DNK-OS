# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/session_retrieval_and_prefix_resolution_protocol.md"
# purpose: "Protocol for robust session retrieval, timestamp prefix resolution, and full session dump in DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🔍 Session Retrieval & Timestamp Prefix Resolution Protocol

## 1. Problem Statement & Root Cause
When restoring or inspecting past sessions by a user prompt containing:
- Timestamp prefix alone: e.g. `[20261010_235004]`
- Task title + timestamp: e.g. `[20261010_235004] Пошук правильного рішення в ситуації`

Calling `session_search(query="20261010_235004")` directly returns **0 results**.
**Root Cause**: The underlying `session_search` tool uses SQLite FTS5 over the `messages` content table. Unless the literal string `20261010_235004` appears in the conversation dialogue text, FTS5 cannot locate the session. Furthermore, session IDs in Hermes follow the pattern `<timestamp>_<random_hex>` (e.g. `20261010_235004_6412f7`), so exact ID match fails when given only a prefix.

## 2. Deterministic Resolution Procedure

To resolve and restore any session with 100% accuracy:

### Step 1: Resolve Full Session ID
Run a targeted lookup in either:
1. **Task Evolution Catalog**:
   Search `.scones/task_evolution_catalog.json` for the timestamp prefix or title:
   ```python
   # Locate entry by timestamp prefix or task name
   search_files(path=".scones/task_evolution_catalog.json", pattern="20261010_235004")
   ```
2. **Hermes Agent State Database**:
   Query `./core/orchestrator/agents/gerych_prime/state.db`:
   ```bash
   python3 -c "
   import sqlite3
   conn = sqlite3.connect('./core/orchestrator/agents/gerych_prime/state.db')
   cur = conn.cursor()
   cur.execute(\"SELECT id, title, started_at, message_count FROM sessions WHERE id LIKE '20261010_235004%' OR title LIKE '%Пошук%' ORDER BY started_at DESC\")
   for row in cur.fetchall():
       print(row)
   "
   ```

### Step 2: Hydrate Session via Tool
Once the full canonical session ID (e.g. `20261010_235004_6412f7`) is resolved:
```python
session_search(session_id="20261010_235004_6412f7")
```
Or query messages directly from `./core/orchestrator/agents/gerych_prime/state.db` if deep raw extraction or specific ID slicing is required:
```sql
SELECT id, role, content FROM messages WHERE session_id = '20261010_235004_6412f7' ORDER BY id ASC;
```

## 3. High-Frequency Traps & Invariants
- **Never guess full session IDs**: Suffixes are pseudo-random hex (e.g. `_6412f7`). Always resolve from DB/catalog.
- **`sessions` table schema**: In `./core/orchestrator/agents/gerych_prime/state.db`, the timestamp column is `started_at`, NOT `created_at`.
- **FTS5 search vs Metadata**: For concept/topic queries, use keywords from the title/goal (`query="Пошук правильного рішення"`), not technical IDs.
