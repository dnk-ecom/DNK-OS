# 🛡️ Crash-Isolated Worker Supervisor & Replay Journal Patterns

<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/sota-repository-assimilation/references/clifpad_crash_isolated_worker_and_replay_journal_patterns.md"
purpose: "SOTA architectural patterns extracted from hewigovens/clifpad for crash-isolated agent execution and journal replay."
status: "Active"
version: "1.0.0"
updated_at: "2026-11-02"
author: "DNK-e.com Maksym & Denchik"
--- END DNK-MRH-HEADER --- -->

## 1. Architectural Motivation & Problem Statement
When AI agents generate dynamic low-level code (e.g. JIT compilation, C ABI calls, Cranelift IR, or unsafe memory manipulations), subtle model errors like dereferencing invalid addresses, stack overflow, or dividing by zero trigger fatal hardware traps (`SIGSEGV`, `SIGBUS`, `SIGILL`).
In standard stdio MCP servers or embedded runtimes, a single fatal signal kills the entire host server process, terminating agent communication and losing session context.

## 2. The Worker-Supervisor & Replay Journal Architecture
As demonstrated in `hewigovens/clifpad` (Rust 1.95+, Cranelift JIT):
```
[ AI Agent / Orchestrator ]
            │ (JSON-RPC / stdio MCP)
            ▼
┌────────────────────────────────────────────────────────┐
│  Host MCP Supervisor Process                           │
│  • Holds state journal (definitions, memory allocations)│
│  • Manages Worker Child Subprocess via IPC pipes       │
│  • Intercepts exit signals (SIGSEGV, SIGBUS, SIGILL)   │
└──────────────────────────┬─────────────────────────────┘
                           │ IPC Stdio (JSON-RPC)
                           ▼
┌────────────────────────────────────────────────────────┐
│  Ephemeral Worker Child Process                        │
│  • Executes volatile/JIT code                          │
│  • Catches hardware traps or dies on signal            │
│  • 3.4ms respawn time on crash                         │
└────────────────────────────────────────────────────────┘
```

### Core Invariants & Mechanics
1. **Durable In-Memory Replay Journal**:
   - The Supervisor records every successful state-altering command (function definitions, memory buffers, global variables) in an append-only journal (`Vec<JournalEntry>`).
2. **Deterministic Crash Interception**:
   - The child worker runs the dangerous code. If a trap or signal occurs, the Supervisor captures the exit code, signal name, and last stderr output.
3. **Sub-4ms Fast-Respawn & Replay**:
   - The Supervisor spawns a fresh worker instance immediately (`Child::spawn`), sequentially replays all journal entries, and brings the worker back to the exact pre-crash state.
4. **Structured Error Feedback to LLM**:
   - Instead of breaking the pipe, the tool call returns a structured failure:
     `{"status": "crashed", "signal": "SIGSEGV", "diagnostic": "bad pointer dereference at 0x0", "journal_replayed_entries": 4}`.
   - The agent receives actionable diagnostic feedback and fixes the generated code in the next turn.

## 3. Cranelift IR vs. High-Level FastMCP Python Evaluation
- **Cranelift IR (CLIF)**:
  - *Pros*: Sub-2ms compilation directly to native machine code; zero link step; precise cycle/instruction benchmarks.
  - *Cons*: Strict SSA-form without immediates creates severe cognitive friction for LLMs; high rate of verifier errors; lack of rich standard library (strings, JSON, I/O).
- **DNK OS Decision**:
  - Keep Cranelift out of core dependencies.
  - For 85%+ of low-level data and bitwise manipulation, use `execute_code` (FastMCP Python) with `ctypes`, `struct`, and `numpy`.
  - Adopt the **Supervisor + Replay Journal** pattern inside `core/harness/process_supervisor.py` for isolating volatile child processes and dynamic plugin execution.
