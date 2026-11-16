<!-- --- DNK-MRH-HEADER ---
mrh_id: "A2A-MAILBOX-JOIN-BARRIER-001"
purpose: "Canonical Protocol for A2A Mailbox NDJSON Storage, Join Barrier Coordination & HITL Abort Handling."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-13"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

# 📬 A2A Mailbox NDJSON, Join Barrier & HITL Abort Protocol

## 1. File-Based Agent-to-Agent (A2A) Mailbox Subsystem (`SwarmLedger`)
- **Path Layout**: Each agent owns a dedicated persistent append-only inbox:
  `core/data/swarm_artifacts/mailboxes/<agent_name>/inbox.ndjson`
- **Atomic Concurrency & Thread-Safety**:
  - File writes must never perform in-place mutations.
  - New messages are appended or rewritten via atomic file swaps:
    ```python
    tmp_path = inbox_path.with_suffix(".ndjson.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        # write updated records
    os.replace(tmp_path, inbox_path)
    ```
  - Lock acquisition via `threading.Lock()` or POSIX file locks prevents inter-worker race conditions.
- **Message Schema Invariants**:
  ```json
  {
    "message_id": "msg-uuid-v4",
    "timestamp": "2026-09-13T12:00:00Z",
    "sender": "gerych_prime",
    "recipient": "gerych_builder",
    "payload": { "task_id": "...", "action": "render_canvas" },
    "ack": false
  }
  ```

## 2. Decoupled Real-Time Telemetry (`EventBroadcaster`)
- **Bounded Queues**: SSE and WebSocket clients consume from bounded async queues (`max_queue_size=200`).
- **Drop-Oldest Under Saturation**: If a downstream client lags, the oldest unread event is dropped (`queue.get_nowait()`) to guarantee zero backpressure on the agent execution loop.
- **Ring Buffer Rehydration**: The broadcaster retains a ring buffer of the last 100 system events, allowing newly connected web UI clients to immediately rehydrate active swarm state without database queries.

## 3. Swarm Join Barrier (`SwarmRouter`)
- **Modes of Execution**:
  1. `and_all`: Concurrently awaits all dispatched subagents (`asyncio.gather`), aggregating full results into an execution bundle.
  2. `or_any`: Speculative race mode. Upon first valid completion, all remaining pending tasks are immediately cancelled (`task.cancel()`) to conserve LLM tokens and execution budget.
- **SpendGuard Integration**: Barrier execution must verify remaining workspace spend tokens before spawning subagents.

## 4. Human-In-The-Loop (HITL) Bridge & Abort Protocol
- **Suspension via `asyncio.Event`**: Sensitive tools (system configuration modification, production deployments, irreversible file deletions) pause subagent execution until operator approval is received via `POST /api/v1/mvr/hitl/decide`.
- **Operator Abort API (`POST /api/v1/mvr/simulation/{id}/abort`)**:
  - Sets simulation status to `ABORTED`.
  - Cascades `SIGTERM` followed by `SIGKILL` (after a 5-second graceful window) to all child OS processes (`cgroups_v2` / `pgid`).
  - Emits `SwarmAbortedEvent` across the ActionBus.

## 5. Git Staged Commit & Git-Ignored File Safety Guard
- **Pitfall**: Attempting `git add file1 file2 ignored_file.md` aborts with exit code 1 (`fatal: pathspec did not match any files` / `The following paths are ignored by one of your .gitignore files`).
- **Invariant**:
  - Always check `git status --porcelain <files>` before constructing `git add`.
  - Never include files like `docs/plans/TASK_ACTIVE.md` (which are git-ignored local run trackers) in explicit `git add` lists without verifying git status.
  - Stage only explicitly modified tracked or intentional new files.
