# Anahata ASI: Context Window Garbage Collector (CwGC) & Stateful Container Patterns

Architectural distillation from `anahata-os/anahata-asi` (Java 21 / NetBeans Platform ASI Container) for DNK OS context pipeline and agent execution layers.

---

## 1. Context Window Garbage Collection (CwGC)

Rather than treating LLM context as a linear append-only string or doing blind truncation, CwGC treats conversation turns like a managed heap:

### In-Band Metadata Injection
Every message and message part receives an explicit metadata header:
```text
--- Message ID: {ID} | Role: {ROLE} | From: {SENDER} | Time: {TIMESTAMP} | Tokens: {COUNT} [| PINNED/PRUNED] ---
[Part ID: {ID} | Type: {TYPE} | Tokens: {COUNT} | Turns Left: {N} [| PINNED/PRUNED]]
```
- **Time-to-Live (TTL)**: Dynamic tool outputs and scratchpad data have decremented TTLs.
- **PINNED State (Messi State)**: Core system instructions, active task specifications, and invariant gates receive the `PINNED` marker and are strictly protected against eviction.

### Semantic Ghosts (Soft Pruning)
When a message part expires or context exceeds headroom budgets:
- It is **never deleted silently** into an empty void.
- It is replaced by a lightweight **Semantic Ghost** header containing:
  1. `Pruned Reason`: E.g., `TTL_EXPIRED`, `TOKEN_BUDGET_PRESSURE`, `HISTORICAL_OBSOLETE`.
  2. `Thought Signatures`: Model reasoning signatures are preserved for coherence.
  3. `Semantic Hint`: 1-line truncated summary of what the output contained.
- **Contiguous Range Compaction**: Sequences of pruned historical messages are collapsed into range blocks:
  ```text
  --- PRUNED MESSAGE RANGES ---
  - Messages ID: 10 to 25 are PRUNED | Reasons: HISTORICAL_TOOL_OUTPUT | Thought Signatures Preserved: 12
  ```

---

## 2. In-Memory Reflection & JIT ClassLoader vs FastMCP

Anahata ASI compiles and loads Java bytecode directly into the JVM Metaspace via `javax.tools.JavaCompiler` and child-first `AgiClassLoader`:
- Allows cross-turn persistence of compiled tools and session objects.
- **DNK OS Translation**: Rather than introducing JVM complexity, DNK OS achieves this via **FastMCP Code Mode (`execute_code`)**, running in-memory Python scripts in the active virtualenv without compilation cycles or classloader leaks.

---

## 3. Human-In-The-Loop (HITL) Tool Lifecycle

Tool calls transition through explicit lifecycle states:
- `PENDING`: Staged before execution for user parameter review and mutation.
- `APPROVED` / `ALWAYS_APPROVED`: Human permission grants per tool or per session.
- `DENIED` / `MODIFIED`: Parameter overrides mid-flight.

---

## 4. Epistemic Armor & Pitfalls

1. **JVM Monolith Friction**: JVM heap (800MB-2GB), 5-12s cold start, and Maven daemon overhead make direct Java container adoption toxic for fast agentic loops.
2. **NetBeans Platform Obsolescence**: 120+ classes tied to NetBeans IDE TopComponents are irrelevant for Obsidian Canvas DAG and modern VS Code workflows.
3. **Clean-Room Assimilation Rule**: Borrow the **CwGC Semantic Ghost** protocol and metadata injection logic, implemented natively in Python / TypeScript context compactor hooks (`hermes_pre_tool_hook.py` / session compactor).
