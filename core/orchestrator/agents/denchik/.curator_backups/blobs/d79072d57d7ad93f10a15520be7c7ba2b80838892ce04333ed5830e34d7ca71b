# Direct SQLite Session Recovery & Deep Context Reconstruction Protocol

When `session_search(query=...)` returns 0 hits for a known historical session ID, timestamp, or prompt keyword (common when operating across isolated agent profiles or detached state databases), use direct SQLite queries against the agent's persistent state store.

## 1. Locating the Agent State Database

In the DNK OS architecture, agent session databases are partitioned by profile/agent:
- Primary Gerych Prime store: `core/orchestrator/agents/gerych_prime/state.db`
- Generic Hermes runtime stores: `~/.hermes/profiles/<profile_name>/state.db`, `~/.hermes/state.db`

## 2. Fast Discovery & Schema Inspection

The state database maintains `sessions` and `messages` tables:

```python
import sqlite3

db_path = "core/orchestrator/agents/gerych_prime/state.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Locate session record by ID fragment or title keyword
cur.execute(
    "SELECT id, title, started_at, model, cwd FROM sessions WHERE id LIKE ? OR title LIKE ?",
    ("%20261010_160905%", "%YouTube%")
)
sessions = cur.fetchall()
# Example result: ('20261010_160905_ac0c8b', 'Аналіз відео з YouTube', 1760101745.2, 'vertex/gemini-2.5-flash', ...)
```

## 3. Extracting Context & Key Decisions

To reconstruct session progress without reading all intermediate tool noise:

```python
# 2. Extract final assistant turns and synthesized conclusions
cur.execute("""
    SELECT id, role, content 
    FROM messages 
    WHERE session_id = ? AND role = 'assistant' AND length(content) > 100 
    ORDER BY id DESC LIMIT 5
""", (session_id,))
for msg_id, role, text in cur.fetchall():
    print(f"=== Checkpoint {msg_id} ===\n{text[:500]}...\n")
```

## 4. Extracting Created & Mutated Files from Tool Calls

```python
# 3. Parse tool_calls to find exact file modifications
cur.execute("""
    SELECT json_extract(tc.value, '$.function.arguments')
    FROM messages m, json_each(m.tool_calls) tc
    WHERE m.session_id = ? AND json_extract(tc.value, '$.function.name') IN ('write_file', 'patch')
""", (session_id,))
modified_files = set(row[0] for row in cur.fetchall())
```

## 5. Correlating with Session Audit Artifacts

Always cross-reference the extracted SQLite session ID with:
1. `docs/audit/sessions/AUDIT_<session_id>.md` (contains tool counts, efficiency ratings, modified components).
2. `docs/notes/MY TASKS/` and `docs/plans/` (contains generated ADRs, journals, and architectural notes).

Present the recovered session in an ADHD format:
- **Card Header**: Session ID, Topic, Started At, Source / Repo.
- **Key Milestones**: Core decisions, architectures analyzed.
- **Artifacts Created**: Exact paths to generated ADRs, files, notes.
- **Actionable Next Steps**: 2-3 discrete forks to continue execution.

## 6. Live Runtime & Working Tree Reconciliation

When resuming an interrupted development or debugging session:
1. **Live Port & Daemon Probe**: Check whether dev servers or background gateways are still listening via `lsof -i :<ports>` before attempting to re-launch them (avoids `EADDRINUSE` port collision).
2. **Working Tree Status**: Inspect `git status` and `git diff --stat` in the active project directory (e.g., in `../DNK_Vibe/<repo>`) to reconcile disk state with the last recorded session turn.
3. **CWD State Hygiene**: When executing commands across sandboxes via `terminal(command="cd <path> && ...")`, verify and reset the session working directory back to `DNK_HUB` root (`cd $HUB_ROOT`) to prevent subsequent path drift errors.
