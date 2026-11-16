# SCONES Vitality Engine & Re-entrant Locking Invariants (DEC-045)

## Overview
When engineering cognitive agentic memory stores with active knowledge degradation (exponential half-life decay, utility reinforcement, and pruning), two systemic architectural failure modes frequently arise:

1. **Lock Deadlock on Recursive Calls** (`threading.Lock` vs `threading.RLock`).
2. **Untestable Time-Decay Functions** lacking deterministic simulated time injection.

---

## 1. Re-entrant Locking Invariant (`threading.RLock`)
### The Anti-Pattern
A parent memory store (e.g. `SconesMemoryStore`) acquires its internal mutex:
```python
with self._lock:
    cursor.execute("INSERT INTO observations ...")
    # Sub-engine invoked while parent lock is held:
    self.vitality.track_access(fact_id)
```
If `SconesVitalityEngine` shares `store._lock` or uses the same lock, and `_lock = threading.Lock()`, Python halts indefinitely on re-acquiring the same unreleased lock in the same thread. Pytest hangs and hits timeout (e.g. 180s exit 124).

### The Invariant
Store-engine hierarchies MUST use `threading.RLock()` across all participating layers:
```python
self._lock = store._lock if store is not None else threading.RLock()
```
`RLock` permits the owning thread to acquire the lock multiple times recursively without blocking, guaranteeing deadlock-free synchronous hooks.

---

## 2. Deterministic Time Injection for Half-Life Decay
### Exponential Decay Formula
$$V(t) = V_0 \cdot 2^{-\frac{\Delta t}{t_{1/2}}}$$
Where:
- $V_0$: Initial or reinforced vitality score.
- $\Delta t$: Elapsed seconds $(now - t_{last})$.
- $t_{1/2}$: Half-life duration in seconds (e.g., 14 days = $14 \times 86400$).

### The Interface Contract
Never call `time.time()` directly inside the mathematical core without a fallback override:
```python
def calculate_decay(self, fact_id: str, half_life_days: float = 14.0, now: Optional[float] = None) -> float:
    current_time = time.time() if now is None else float(now)
    ...
```
Furthermore, propagate `now: Optional[float] = None` up to:
- `query_memories(..., min_vitality=0.1, now=None)`
- `prune_dead_facts(..., min_vitality=0.1, now=None)`

This allows tests and batch simulations to advance time arbitrarily (e.g. 14, 28, 60 days) with machine proof and zero monkeypatching.

---

## 3. Privacy-Preserving Vitality Receipts
Audit logs for memory access utility (`scones_vitality_logs`) must record access utility boosts without leaking sensitive user prompts. Hash the task identifier using SHA-256:
```python
task_hash = hashlib.sha256(raw_task.encode("utf-8")).hexdigest()
```
