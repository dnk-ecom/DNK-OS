# --- DNK-MRH-HEADER ---
# mrh_id: "dnk-swarm-orchestration/references/swarmchat_at_least_once_delivery_and_role_topology_protocol.md"
# purpose: "At-Least-Once delivery with piggybacked ACK & clean-room role topologies (Builder/Tester, Owner/Helper) from swarmchat."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

# 🐝 SwarmChat At-Least-Once Delivery & Clean-Room Role Topologies

## 1. Architectural Summary

SwarmChat provides an in-memory, dependency-free agent communication server ("Slack for Agents") with zero external services. Its two primary architectural contributions to DNK OS are:
1. **At-Least-Once Delivery via Piggybacked Acknowledgment (`ack`)**: Preventing message loss when agent processes terminate, crash, or hit tool timeouts mid-turn.
2. **ProgramBench Multi-Agent Role Topologies**: Strict channel permissions and role invariants that prevent communication chatter and git conflicts across multi-agent swarms.

---

## 2. At-Least-Once Delivery: Long-Polling + Piggybacked ACK

### The Problem
Traditional naive HTTP messaging marks messages as "read" when the server writes the HTTP response body. If the agent crashes while processing the message or the TCP connection terminates prematurely, the message is permanently lost to the agent.

### The Mechanism
```
Agent Client                                           Swarm Server
     │                                                      │
     │── 1. POST /wait {peek: true, timeout: 280, ...} ────>│ (Long-polls on threading.Condition)
     │                                                      │  _pending() finds new messages
     │<─ 2. HTTP 200 {messages: [...], positions: {...}} ───│ (Disk pointer UNCHANGED!)
     │                                                      │
[Buffer in RAM: self.ack[chat] = max_seq]                    │
     │                                                      │
     │── 3. Next RPC (wait/send/download/close) ───────────>│
     │      Payload includes: {"ack": {chat_id: 42}}        │ Server executes api.confirm(ack)
     │                                                      │ -> store.mark_read(me, chat, 42)
     │<─ 4. HTTP 200 {result of next action} ───────────────│ (Read pointer committed to disk)
```

### Key Invariants
- **`peek=True` on `wait`**: The client library always requests `peek=True` behind the scenes. Messages are returned into the client's memory buffer without advancing the disk cursor.
- **Piggybacked ACK**: `client.py` attaches `params["ack"] = self.ack` to all subsequent outgoing HTTP calls. The server strips `params.pop("ack")` and commits the read marker **before** executing the new action.
- **Fail-Safe Recovery**: If the agent's LLM context exceeds budget, process gets killed, or network drops, `self.ack` was never dispatched. Upon restart, `client.wait()` re-reads the unacknowledged messages. Zero message loss.
- **Heartbeat & Gone Check**: The server's `wait` loop pulses `cond.wait(min(left, 1.0))` and checks `gone()` socket status. If the client drops, it exits immediately without modifying read positions.

---

## 3. Clean-Room Multi-Agent Topologies (`extras/programbench/`)

### Topology A: Builder vs. Tester (Adversarial Quality Gate)
- **Channel Partitioning**:
  - `#general`: High-level sync, announcements, and diff reports.
  - `#build`: Exclusive to Builders. Internal architecture discussions.
  - `#test`: Exclusive to Testers. Test suite coordination.
- **Tester Invariant (Zero Production Code Edits)**:
  Testers are structurally forbidden from modifying feature code. Their sole responsibility is running builds against the specification/reference, capturing discrepancies, creating reproducible red unit tests under `tests/`, and posting the exact CLI discrepancy into `#general`:
  `[COMMAND] -> [EXPECTED OUTPUT] -> [ACTUAL OUTPUT]`.
- **Builder Invariant (Test-Driven Synthesis)**:
  Builders do not debate requirements; they write code until all tests under `tests/` pass with exit code 0.

### Topology B: Owner vs. Helper (Single-Committer Git Model)
- **Owner Role**: The sole agent with push access to `origin/main`. Responsible for continuous build integrity.
- **Helper Role**: Operates in an isolated worktree or container without write access to `main`. Pushes candidate patches to `<agent_name>/<topic>` branches on `incoming/`.
- **Merge Flow**: Owner fetches from `incoming/`, runs adversarial checks, merges, and pushes to `main`. Eliminates git rebase conflicts across concurrent autonomous workers.

### Topology C: Pure Lead
- **Lead Invariant**: The lead agent writes **zero feature code**. Its sole task is decomposing goals into atomic slices, maintaining `TASKS.md`, dispatching workers, and evaluating PR receipts.

---

## 4. Boundary Conditions & DNK OS Skeptic Alternative

1. **GIL & Threading Overhead**: In-memory `threading.Condition` locks degrade beyond 20 concurrent long-polling agents in Python.
2. **Append-Only JSONL Drift**: Chat logs grow unbounded without compaction or retention pruning.
3. **Context Poisoning Vulnerability**: Agent messages enter sibling contexts without input sanitization; prompt injection between agents must be guarded by the orchestrator.
4. **Sovereign DNK OS Alternative**:
   Use an in-process **SQLite WAL Event Queue** (`core/memory/a2a_bus.db`) accessed via FastMCP `execute_code`. Delivers ACID transactions, sub-millisecond local latency, zero open network ports, and atomic ACK commits without an external HTTP daemon.
