---
name: cognitive-memory-engineering
description: "Use when designing agent memory stores, decay, or pruning."
version: "1.0.0"
author: "Denchik & DNK OS"
license: "MIT"
metadata:
  hermes:
    tags: [memory, cognitive-architecture, sqlite-wal, lock-safety, decay-pruning, testing]
    related_skills: [architecture-invariants-and-blast-radius]
---

# Cognitive Memory Engineering

Engineering robust, long-term cognitive memory stores for autonomous agents, covering concurrency, exponential knowledge decay, utility receipts, and deterministic verification.

## When to Use
- Implementing or modifying persistent agent memory stores (SCONES, SQLite WAL backends, vector indexes).
- Designing active memory decay, utility reinforcement, half-life retention algorithms, or dead-fact pruning.
- Debugging thread deadlocks or timeouts during nested memory operations and automated pytest runs.
- Writing unit and integration tests that verify time-dependent memory eviction without monkeypatching system clocks.

## Core Architectural Invariants

### 1. Re-entrant Locking for Nested Memory Stores (`threading.RLock`)
When a primary memory store (e.g. SQLite observation logger) synchronously delegates to a nested sub-engine (vitality monitor, semantic indexer, vector cache):
- **Never use `threading.Lock()`**: If the outer store acquires a lock during a write and calls the nested sub-engine which also acquires the store lock, a non-reentrant mutex deadlocks the calling thread. In automated test runners, this presents as indefinite hangs and timeout exits (e.g., 180s exit code 124).
- **Enforce `threading.RLock()`**: Both outer stores and delegated helper engines must use `threading.RLock()`. Re-entrant locks permit the same thread to acquire the lock multiple times recursively without blocking.

```python
import threading
from typing import Optional, Any

class MemorySubEngine:
    def __init__(self, store: Optional[Any] = None):
        self.store = store
        # Inherit store RLock or initialize a new re-entrant lock
        self._lock = store._lock if store is not None else threading.RLock()
```

### 2. Deterministic Time Injection for Half-Life Decay & Pruning
When implementing exponential time-based memory decay:
$$V(t) = V_0 \cdot 2^{-\frac{\Delta t}{t_{1/2}}}$$

- **Interface Contract**: Never hardcode unparameterized `time.time()` inside decay calculation, query filtering, or pruning routines.
- **Pass Optional `now`**: Expose `now: Optional[float] = None` across all public query, decay calculation, and pruning methods:
```python
def calculate_decay(self, fact_id: str, half_life_days: float = 14.0, now: Optional[float] = None) -> float:
    current_time = time.time() if now is None else float(now)
    # compute decay deterministically...
```
- **Forwarding**: Ensure wrapper methods (such as `store.query_memories(..., now=None)` and `store.prune_dead_facts(..., now=None)`) propagate `now` down to the decay engine. This allows unit tests and simulations to jump forward arbitrarily (e.g., 14, 28, 60 days) without monkeypatching system time.

### 3. Privacy-Preserving Vitality Receipts
Tracking memory utility boosts during agent tasks must not leak sensitive prompt payloads into long-term audit logs:
- Compute a SHA-256 digest of the task context:
```python
import hashlib
task_hash = hashlib.sha256(raw_task.encode("utf-8")).hexdigest()
```
- Store the hash alongside delta utility and timestamp in an append-only receipts log table.

### 4. Working-Tree Diff Overlay (`Baseline ⊕ Diff Overlay`)
For repo-anchored agent code memory, never rebuild full AST indexes on uncommitted edits:
- Snapshot immutable baseline AST symbols at commit `HEAD`.
- Inspect uncommitted changes via `git status --porcelain`.
- On-the-fly parse only modified/added files (`< 2ms`).
- Merge as `Effective = (Baseline - Deleted) ⊕ Fresh-Parse(Diff)`.

### 5. Deterministic FTS5 / BM25 with AST Locus Scoping (`GIT_NATIVE_GRAPH_MEMORY`)
Prefer SQLite FTS5 with BM25 ranking and AST locus filters over heavy local neural embeddings:
- Memory footprint stays `< 15MB` RSS vs hundreds of MBs for neural models.
- Zero semantic drift on exact symbol names and class identifiers.
- Combine free-text BM25 ranking with AST symbol and file locus filters for instant recall.

### 6. Anchor Verification for SKILL.md, ADRs & Durable Facts
Prevent dead-file and drifted-symbol decay in persistent memory and docs:
- Audit memory facts and markdown documentation against physical disk paths and live AST signatures.
- Classify references as `VERIFIED`, `STALE` (symbol renamed/missing), or `BROKEN` (file missing).
- Execute automated anchor verification (`scripts/system/verify_scones_anchors.py --skills`) in pre-commit gates.

### 7. Elephant-Goldfish Dual-Horizon Retention (`DEC-038`)
Decouple deep-horizon specification memory from zero-context adversarial review:
- **Elephant**: High-density invariant memory (SCONES FTS5, ADRs, baseline code). Formulates drafts and preserves system continuity.
- **Goldfish**: Ephemeral working context. Zero cross-session contamination; conducts un-sycophantic reviews across 4 orthogonal lenses (Zoom Out, Comprehension, Design Critic, Readiness).

### 8. Recursive Agent Harnessing & Experience Reflector (`Harness²`)
Scale agent capability around frozen model weights through systematic harness recursion:
- **Task-Level Recursion (Propose–Probe–Compose)**: Contrastive evaluation of prompts, memory configurations, and tool policies on deterministic probes.
- **Harnessing-Level Recursion (Experience Reflector)**: Extract verified lessons from tool failures and commit traces into durable SCONES `evidence_facts`.

### 9. Topic & Category Taxonomy Ingestion in Recall Matching
When implementing lexical or substring recall matching across structured memory stores (e.g., SCONES lessons and memory providers):
- **Never omit taxonomy keys**: In stores where memories hold structured classification metadata (`topic`, `category`, `tags`), search text concatenation must explicitly include taxonomy metadata alongside body content:
  ```python
  cat = item.get("category", "") or item.get("topic", "")
  search_text = f"{cat} {item.get('rule', '')} {item.get('observation', '')}".lower()
  ```
- **Silent Miss Pitfall**: If recall matching queries only inspect `rule` and `observation` text, agents querying memories by exact category/topic identifiers (e.g. `SOVEREIGN_JIT_AGENT_PARADIGM`, `DENCHIK_FULL_MASTERY_CERTIFIED`) encounter silent misses (`[]`) despite the memory existing in physical storage.

### 10. Programmatic SCONES Ingest Contract (`SCONESMemoryEngine.add_memory`)
When recording durable agent findings directly in RAM via `execute_code`:
- **Canonical Method Contract**: Do not call `engine.remember(...)` (a conversational alias). The physical method on `core.memory.scones_memory.SCONESMemoryEngine` is `add_memory`:
  ```python
  from core.memory.scones_memory import SCONESMemoryEngine

  engine = SCONESMemoryEngine()
  record = engine.add_memory(
      topic="topic_identifier",
      content="Durable architectural fact or benchmark result.",
      importance=1.0,
      metadata={"artifacts": ["docs/..."]}
  )
  ```
- **Retrieval Invariants**: Query via `engine.get_memories(topic=...)` for exact topic retrieval or `engine.search_bm25(query=..., limit=5)` for lexical keyword search over FTS5.

## Verification Checklist
1. **Concurrency**: Verify nested store method calls within a single thread do not deadlock under `RLock`.
2. **Formula Accuracy**: Confirm at $t = t_{1/2}$, vitality equals exactly $0.5 \times V_0$.
3. **Eviction Gate**: Ensure pruned dead facts are removed from both the vitality index and the primary storage tables.
4. **Overlay Correctness**: Uncommitted file modifications overwrite baseline symbols immediately; deleted files are purged from effective graph.
5. **Anchor Integrity**: Run anchor audits to verify 0 `BROKEN` references across active skill and ADR files.
6. **Dual-Horizon Cleanliness**: Ensure Goldfish review agents are spawned with zero conversational baggage or prior debate rationalizations.

## Supporting References
- `references/scones_vitality_and_lock_invariants.md`: Detailed anti-pattern analysis, mathematical decay contracts, and privacy-preserving receipt schemas.
- `references/git_native_overlay_and_anchor_verification.md`: Working-tree diff overlay architecture, SQLite FTS5 BM25 locus scoping, and anchor verification engine contracts.
- `references/elephant_goldfish_and_recursive_harnessing_patterns.md`: Deep synthesis of Google EGM dual-horizon retention, Harness² 8-component recursion, and entire-graph AST blast radius.
